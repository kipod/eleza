from flask import render_template, Blueprint
from app.models import Feature, Subdomain
from app.contoller import predictive_power

demo_blueprint = Blueprint("demo", __name__)


@demo_blueprint.route("/demo")
def demo():
    return render_template("demo.html")


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
