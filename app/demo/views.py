from flask import render_template, Blueprint, request, session, redirect, url_for, flash
from flask_login import login_required
from app.models import Feature, Subdomain, ModelType, CaseValue
from app.contoller import predictive_power, import_data_from_file_stream
from .forms import SubdomainChoiceForm, SelectFeaturesForm, RangeGroupsForm, CategoriesForm


demo_blueprint = Blueprint("demo", __name__)


@demo_blueprint.route("/", methods=["GET", "POST"])
@login_required
def demo():
    form = SubdomainChoiceForm(request.form)
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
            model_type=form.model_type.data,
        )
        session["user_data_id"] = user_data.id
        if form.domain.data == Subdomain.Domain.healthcare.name:
            return redirect(url_for("demo.select_features"))
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template("demo.html", form=form)


@demo_blueprint.route("/features", methods=["GET", "POST"])
def select_features():
    form = SelectFeaturesForm(request.form)
    features = Feature.query.all()
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    pred_pow = predictive_power(
        form.subdomain, user_data_id=session.get("user_data_id")
    )
    for k in pred_pow:
        pred_pow[k] = round(pred_pow[k], 2)
    if form.validate_on_submit():
        selected_features = []
        for name in request.form:
            if request.form[name] == "on":
                selected_features += [name]
        session["selected_features"] = selected_features
        return redirect(url_for("demo.range_groups"))
    elif form.is_submitted():
        flash("Invalid data", "warning")
    return render_template(
        "select_features.html", features=features, pred_pow=pred_pow, form=form,
    )


@demo_blueprint.route("/range_groups", methods=["GET", "POST"])
def range_groups():
    form = RangeGroupsForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    user_data_id = session["user_data_id"]
    form.ranges = {}
    for feature_name in form.selected_features:
        feature = Feature.query.filter(Feature.name == feature_name).first()
        all_values = [
            c.value
            for c in CaseValue.query.filter(CaseValue.user_data_id == user_data_id)
            .filter(CaseValue.feature == feature)
            .all()
        ]
        form.ranges[feature_name] = (min(all_values), max(all_values))

    return render_template("range_groups.html", form=form)


@demo_blueprint.route("/categories", methods=['GET', 'POST'])
def categories():
    form = CategoriesForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.categories = session.get("categories", {
        "Personal & Family History": [
            "Age",
            "Num. of Pregnancies",
        ],
        "Blood Lab Values": [
            "Glucose",
            "Insulin"
        ],
        "Clinical Measurements": [
            "Body Mass Index",
            "Skin Thickness",
            "Blood Pressure"
        ]
    })
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    if form.validate_on_submit():
        if form.submit:
            form.categories[form.category_name.data] = [k for k in request.form if request.form[k] == 'on']
    elif form.is_submitted():
        flash("Invalid data", "warning")
    return render_template(
        "categories.html",
        form=form
    )
