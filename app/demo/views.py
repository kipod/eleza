from flask import render_template, Blueprint, request, session, redirect, url_for, flash
from flask_login import login_required
from app.models import Feature, Subdomain, ModelType
from app.contoller import predictive_power, import_data_from_file_stream
from .forms import SubdomainChoiceForm


demo_blueprint = Blueprint("demo", __name__)


@demo_blueprint.route("/", methods=['GET', 'POST'])
@login_required
def demo():
    form = SubdomainChoiceForm(request.form, csrf_enabled=False)
    form.subdomains = Subdomain.query.all()
    form.models = ModelType.query.all()
    form.subdomain_id.choices = [(s.id, s.name) for s in form.subdomains]
    form.model_type.choices = [(m.name, m.name) for m in form.models]
    form.active_domain = session.get("active_domain", "general")

    if form.validate_on_submit():
        session["subdomain"] = form.subdomain_id.data
        session["model_type"] = form.model_type.data
        session["active_domain"] = form.domain.data
        bkg_file = request.files.get("bkg_file")
        if not bkg_file:
            flash("Need select background file", "warning")
            return render_template("demo.html", form=form)
        explainer_file = request.files.get("explainer_file")
        if not explainer_file:
            flash("Need select explainer file", "warning")
            return render_template("demo.html", form=form)
        user_data = import_data_from_file_stream(
            file_value=bkg_file,
            file_explainer=explainer_file,
            subdomain_id=form.subdomain_id.data,
            domain=form.domain.data,
            model_type=form.model_type.data
        )
        session["user_data_id"] = user_data.id
        if form.domain.data == Subdomain.Domain.healthcare.name:
            return redirect(url_for("demo.select_features"))
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template("demo.html", form=form)


@demo_blueprint.route("/features")
def select_features():
    features = Feature.query.all()
    subdomain = Subdomain.query.get(session.get("subdomain", None))
    pred_pow = predictive_power(subdomain, user_data_id=session.get('user_data_id'))
    return render_template(
        "select_features.html",
        features=features,
        pred_pow=pred_pow,
    )
