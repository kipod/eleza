from flask import render_template, Blueprint, request, session, redirect, url_for, flash
from app.models import Feature, Subdomain
from app.contoller import predictive_power
from .forms import SubdomainChoiceForm


demo_blueprint = Blueprint("demo", __name__)


@demo_blueprint.route("/demo")
def demo():
    form = SubdomainChoiceForm(request.form)
    form.subdomain_type.data = Subdomain.Type.healthcare.name
    form.subdomains = Subdomain.query.all()
    if form.validate_on_submit():
        session["subdomain"] = form.subdomain_name.data
        session["model_type"] = form.model_type.data
        if form.subdomain_type.data == Subdomain.Type.healthcare.name:
            redirect(url_for("demo.slide_helthcare_criteries"))
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template("demo.html", form=form)


@demo_blueprint.route("/slide_helthcare_criteries")
def slide_helthcare_criteries():
    features = Feature.query.all()
    subdomain = Subdomain.query.filter(Subdomain.name == "Diabetic").first()
    pred_pow = predictive_power(subdomain)
    return render_template(
        "slide2_for_criteries/helthcare_criteres.html",
        features=features,
        pred_pow=pred_pow,
    )
