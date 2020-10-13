from flask import request, redirect, url_for, flash, session
from flask_login import login_required
from app.demo.forms import InitialForm

from .blueprint import demo_blueprint


@demo_blueprint.route("/initial", methods=["POST"])
@login_required
def initial():
    form = InitialForm(request.form)
    session["active_domain"] = form.domain.data
    if not form.validate_on_submit():
        flash("Invalid data", "warning")
        return redirect(url_for("demo.demo"))
    model_file = request.files.get("model_file")
    if not model_file:
        flash("Need select model file", "warning")
        return redirect(url_for("demo.demo"))
    dataset_file = request.files.get("dataset_file")
    if not dataset_file:
        flash("Need select dataset file", "warning")
        return redirect(url_for("demo.demo"))

    return redirect(url_for("demo.demo"))
    # return redirect(url_for("demo.financial_select_features"))
