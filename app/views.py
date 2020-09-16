from flask import Blueprint, redirect, url_for

# from flask_login import login_required

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
# @login_required
def index():
    return redirect(url_for("demo.demo"))
