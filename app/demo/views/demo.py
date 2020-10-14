from flask import render_template, request, session, flash
from flask_login import login_required
from app.models import Subdomain, ModelType
from app.demo.forms import (
    SubdomainChoiceForm,
    InitialForm
)

from .util import redirect_select_features
from .blueprint import demo_blueprint


@demo_blueprint.route("/", methods=["GET", "POST"])
@login_required
def demo():
    form = SubdomainChoiceForm(request.form)
    form_initial = InitialForm(request.form)
    form_initial.generated = session.get("data_generated", False)
    form.subdomains = Subdomain.query.all()
    form.models = ModelType.query.all()
    form.subdomain_id.choices = [(s.id, s.name) for s in form.subdomains]
    form.model_type.choices = [(m.name, m.name) for m in form.models]
    form.active_domain = session.get("active_domain", "initial")

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

        return redirect_select_features(
            file_value=bkg_file,
            file_explainer=explainer_file,
            domain=form.domain.data,
            subdomain_id=form.subdomain_id.data,
            model_type=form.model_type.data
        )

    elif form.is_submitted():
        session["active_domain"] = form.domain.data
        flash("Invalid data", "warning")

    return render_template("demo.html", form=form, form_initial=form_initial)
