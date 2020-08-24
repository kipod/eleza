from flask import render_template, Blueprint, request, session, redirect, url_for, flash
from app.models import Feature, Subdomain, ModelType
from app.contoller import predictive_power
from .forms import SubdomainChoiceForm


demo_blueprint = Blueprint("demo", __name__)


@demo_blueprint.route("/", methods=['GET', 'POST'])
def demo():
    form = SubdomainChoiceForm(request.form, csrf_enabled=False)
    form.subdomains = Subdomain.query.all()
    form.models = ModelType.query.all()
    form.subdomain_name.choices = [(s.id, s.name) for s in form.subdomains]
    form.model_type.choices = [(m.id, m.name) for m in form.models]
    if form.validate_on_submit():
        session["subdomain"] = form.subdomain_name.data
        session["model_type"] = form.model_type.data
        bkg_file = request.files.get("bkg_file")
        if not bkg_file:
            flash("Need select background file", "warning")
            return render_template("demo.html", form=form)
        # TODO:
        ## call import_data_from_file()
        ## check bkg_fistore user_data id in the session
        if form.domain.data == Subdomain.Domain.healthcare.name:
            return redirect(url_for("demo.slide_helthcare_criteries"))
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template("demo.html", form=form)


@demo_blueprint.route("/slide_helthcare_criteries")
def slide_helthcare_criteries():
    subdomain_id = session.get("subdomain", None)
    if subdomain_id is None:
        return redirect(url_for('demo.demo'))
    features = Feature.query.all()
    subdomain = Subdomain.query.filter_by(id=int(subdomain_id)).first()
    pred_pow = predictive_power(subdomain)
    return render_template(
        "slide2_for_criteries/helthcare_criteres.html",
        features=features,
        pred_pow=pred_pow,
    )
