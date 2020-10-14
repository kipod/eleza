import tempfile

from flask import request, redirect, url_for, flash, session, send_file
from flask_login import login_required
from app.demo.forms import InitialForm
from app.contoller import generate_bkg_exp

from .blueprint import demo_blueprint

from app.models import Subdomain


@demo_blueprint.route("/initial", methods=["POST"])
@login_required
def initial():
    form = InitialForm(request.form)
    session["active_domain"] = form.domain.data
    if form.generate.data:
        # pressed button <<Generate>>
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
        # process files
        bkg_file = None
        explainer_file = None
        plot_file = None
        with tempfile.NamedTemporaryFile(delete=True) as data_file:
            data_file.write(dataset_file.read())
            data_file.flush()
            bkg_file, explainer_file, plot_file = generate_bkg_exp(
                file_pkl=model_file,
                file_data=data_file.name
                )
        # store path to files in the session
        session["generated_background_file"] = bkg_file
        session["generated_explainer_file"] = explainer_file
        session["generated_ploter_file"] = plot_file
        # show ploter
        session["data_generated"] = True
    else:
        # pressed button <<Next>>
        # goto financial page
        session["active_domain"] = Subdomain.Domain.financial.name

    return redirect(url_for("demo.demo"))


@demo_blueprint.route("/generated_ploter_image", methods=["GET"])
@login_required
def generated_plot():
    return send_file(session["generated_ploter_file"])
