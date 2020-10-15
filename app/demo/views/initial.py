import tempfile

from flask import request, redirect, url_for, flash, session, send_file
from flask_login import login_required
from app.demo.forms import InitialForm
from app.contoller import generate_bkg_exp, ParsingError

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
        try:
            with tempfile.NamedTemporaryFile(delete=False) as pkl_file:
                pkl_file.write(model_file.read())
                pkl_file.close()
                with tempfile.NamedTemporaryFile(delete=False) as data_file:
                    data_file.write(dataset_file.read())
                    data_file.close()
                    bkg_file, explainer_file, plot_file = generate_bkg_exp(
                        file_pkl=pkl_file.name,
                        file_data=data_file.name
                        )
        except ParsingError as error:
            flash(str(error), "danger")
            return redirect(url_for("demo.demo"))
        # store path to files in the session
        session["generated_background_file"] = bkg_file
        session["generated_explainer_file"] = explainer_file
        session["generated_ploter_file"] = plot_file
        # show ploter
        session["data_generated"] = True
        # flash('The following files were generated successfully:', 'success')
        # flash('Background Dataset file', 'success')
        # flash('Explainer Dataset file', 'success')
    else:
        # pressed button <<Next>>
        # goto financial page
        session["active_domain"] = Subdomain.Domain.financial.name

    return redirect(url_for("demo.demo"))


@demo_blueprint.route("/generated_ploter_image", methods=["GET"])
@login_required
def generated_plot():
    return send_file(session["generated_ploter_file"])


@demo_blueprint.route("/refresh_initial")
@login_required
def refresh_initial():
    session["active_domain"] = Subdomain.Domain.initial.name
    session["generated_background_file"] = None
    session["generated_explainer_file"] = None
    session["generated_ploter_file"] = None
    session["data_generated"] = False
    return redirect(url_for("demo.demo"))
