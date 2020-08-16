from flask import render_template, Blueprint

demo_blueprint = Blueprint("demo", __name__)


@demo_blueprint.route("/demo")
def demo():
    return render_template("demo.html")


@demo_blueprint.route("/slide_helthcare_criteries")
def slide_helthcare_criteries():
    return render_template("slide2_for_criteries/helthcare_criteres.html")
