from flask import render_template, Blueprint, request, session, redirect, url_for, flash
from flask_login import login_required
from app.models import Feature, Subdomain, ModelType, CaseValue
from app.contoller import predictive_power, import_data_from_file_stream
from flask_wtf import FlaskForm
from .forms import (
    SubdomainChoiceForm,
    SelectFeaturesForm,
    RangeGroupsForm,
    CategoriesForm,
    FinancialSelectFeatures,
)
from .controller import (
    prediction_score,
    predicted,
    age_range_groups,
    gen_squares_code,
)


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
        user_data, read_features = import_data_from_file_stream(
            file_value=bkg_file,
            file_explainer=explainer_file,
            subdomain_id=form.subdomain_id.data,
            model_type=form.model_type.data,
        )
        session["features_in_file"] = [f.id for f in read_features]
        session["user_data_id"] = user_data.id
        if form.domain.data == Subdomain.Domain.healthcare.name:
            return redirect(url_for("demo.select_features"))
        if form.domain.data == Subdomain.Domain.financial.name:
            return redirect(url_for("demo.financial_select_features"))
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template("demo.html", form=form)


# Begin healthcare domain!
@demo_blueprint.route("/features", methods=["GET", "POST"])
def select_features():
    form = SelectFeaturesForm(request.form)
    features_in_file = session.get("features_in_file", [])
    features = Feature.query.filter(Feature.id.in_(features_in_file)).all()
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
        session["ranges_for_feature"] = {}
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
    form.feature.choices = [(v, v) for v in form.selected_features]
    form.ranges = {}
    ranges_for_feature = session.get("ranges_for_feature", {})
    for feature_name in form.selected_features:
        feature = Feature.query.filter(Feature.name == feature_name).first()
        all_values = [
            c.value
            for c in CaseValue.query.filter(CaseValue.user_data_id == user_data_id)
            .filter(CaseValue.feature == feature)
            .all()
        ]
        form.ranges[feature_name] = (round(min(all_values), 3), (max(all_values), 3))
    if form.validate_on_submit():
        if form.next.data:
            session["categories"] = {}
            return redirect(url_for("demo.categories"))
        try:
            if form.feature.data in ranges_for_feature:
                ranges_for_feature[form.feature.data] += [
                    (float(form.range_from.data), float(form.range_to.data))
                ]
            else:
                ranges_for_feature[form.feature.data] = [
                    (float(form.range_from.data), float(form.range_to.data))
                ]
            session["ranges_for_feature"] = ranges_for_feature
        except ValueError:
            flash("Invalid data", "warning")
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template(
        "range_groups.html", form=form, ranges_for_feature=ranges_for_feature
    )


@demo_blueprint.route("/categories", methods=["GET", "POST"])
def categories():
    form = CategoriesForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.categories = session.get("categories", {})
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    # ranges_for_feature = session.get("ranges_for_feature", {})
    if form.validate_on_submit():
        if form.submit.data:
            form.categories[form.category_name.data] = [
                k for k in request.form if request.form[k] == "on"
            ]
            session["categories"] = form.categories
        if form.next.data:
            session["categories"] = form.categories
            # {}
            return redirect(url_for("demo.explanations_summary"))
    elif form.is_submitted():
        flash("Invalid data", "warning")
    return render_template("categories.html", form=form)


@demo_blueprint.route("/explanations_summary", methods=["GET", "POST"])
def explanations_summary():
    form = FlaskForm(request.form)
    categories = session.get("categories", {})
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    ranges_for_feature = session.get("ranges_for_feature", {})
    range_groups_ages = ranges_for_feature.get("Age", [])
    form.presentation_type = "Percents"
    if form.validate_on_submit():
        form.presentation_type = request.form["presentation_type"]
    elif form.is_submitted():
        flash("Invalid data", "warning")

    form.table_heads = [
        "Patient ID",
        "Age",
        f"{form.subdomain.name} Predicted",
        "Prediction or Confidence Score (Out of 100)",
    ]

    form.table_heads += [f"{name} Contribution" for name in categories]

    all_case_values_query = CaseValue.query.filter(
        CaseValue.user_data_id == session["user_data_id"]
    )
    max_patient_id = max([v.case_id for v in all_case_values_query.all()])
    form.table_rows = []
    for patient_id in range(max_patient_id + 1):
        all_case_values_query_for_patient = all_case_values_query.filter(
            CaseValue.case_id == patient_id
        )
        if not all_case_values_query_for_patient.all():
            continue
        age_feature = Feature.query.filter(Feature.name == "Age").first()
        age_case_val = all_case_values_query_for_patient.filter(
            CaseValue.feature_id == age_feature.id
        ).first()
        age = int(age_case_val.value)
        age = age_range_groups(range_groups_ages, age)
        prediction_score = int(round(age_case_val.prediction, 2) * 100)
        predicted = "No" if prediction_score < 50 else "Yes"
        prediction_score_color = "red"
        if prediction_score > 45:
            prediction_score_color = "yellow"
            if prediction_score > 70:
                prediction_score_color = "green"

        patient_id_bgcolor = "MediumSlateBlue"
        row = [
            (patient_id, patient_id_bgcolor),
            (age, None),
            (predicted, None),
            (prediction_score, prediction_score_color),
        ]
        explainers = []
        for cat_name in categories:
            sum_explainer = 0
            for feature_name in categories[cat_name]:
                feature = Feature.query.filter(Feature.name == feature_name).first()
                case_val = all_case_values_query_for_patient.filter(
                    CaseValue.feature_id == feature.id
                ).first()
                sum_explainer += case_val.explainer
            explainers += [sum_explainer]
        # if not selected percentage
        cells = None

        if form.presentation_type == "Percents":
            hundred = sum(explainers)
            values = list(
                map(lambda val: int(round(val * 100 / hundred, 0)), explainers)
            )
            max_val = max(values)
            colors = list(
                map(lambda val: ("green" if val == max_val else None), values)
            )
            cells = list(zip(values, colors))
        else:
            values = list(map(lambda val: (round(val, 4)), explainers))
            max_val = max(values)
            colors = list(
                map(lambda val: ("green" if val == max_val else None), values)
            )
            cells = list(zip(values, colors))
        row += cells
        form.table_rows += [row]

    return render_template(
        "explanations_summary.html", form=form, range_groups_ages=range_groups_ages,
    )


@demo_blueprint.route("/explanations_per_patient/<case_id>", methods=["GET", "POST"])
def explanations_per_patient(case_id):
    form = FlaskForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.categories = session.get("categories", {})
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    ranges_for_feature = session.get("ranges_for_feature", {})
    range_groups_ages = ranges_for_feature.get("Age", [])
    all_case_values_query = CaseValue.query.filter(
        CaseValue.user_data_id == session["user_data_id"]
    )
    all_case_values_query_for_patient = all_case_values_query.filter(
        CaseValue.case_id == case_id
    )
    form.presentation_type = "Proportional to the Total Confidence Score"

    if form.validate_on_submit():
        form.presentation_type = request.form["presentation_type"]
    elif form.is_submitted():
        flash("Invalid data", "warning")

    form.table_heads = []
    sum_explainer = {}
    sum_explainer_abs = {}
    for cat_name in form.categories:
        sum_explainer[cat_name] = 0
        sum_explainer_abs[cat_name] = 0
        for feature_name in form.categories[cat_name]:
            feature = Feature.query.filter(Feature.name == feature_name).first()
            case_val = all_case_values_query_for_patient.filter(
                CaseValue.feature_id == feature.id
            ).first()
            sum_explainer[cat_name] += case_val.explainer
            sum_explainer_abs[cat_name] += abs(case_val.explainer)
        form.table_heads += [[cat_name, ], "Feature Contribution"]
    form.table_rows = []
    num_of_rows = max([len(form.categories[k]) for k in form.categories])
    for cat_name in form.categories:
        row_index = 0
        for feature_name in form.categories[cat_name]:
            if len(form.table_rows) <= row_index:
                form.table_rows += [[]]
            feature = Feature.query.filter(Feature.name == feature_name).first()
            case_val = all_case_values_query_for_patient.filter(
                CaseValue.feature_id == feature.id
            ).first()
            if form.presentation_type == "Proportional to the Total Confidence Score":
                one_square_val = sum(sum_explainer_abs.values()) / 12
                square_num = int(round(abs(case_val.explainer) / one_square_val, 0))
                form.table_rows[row_index] += [[feature_name, gen_squares_code(square_num)]]
            else:
                each_category_squares = 12 / len(form.categories)
                value_of_square = int(round(100 / each_category_squares, 0))
                sum_explainer_category = sum_explainer_abs[cat_name]
                feature_explainer = int((case_val.explainer / sum_explainer_category) * 100)
                feature_squares = int(round((feature_explainer / value_of_square), 0))
                form.table_rows[row_index] += [[feature_name, gen_squares_code(feature_squares)]]
            row_index += 1
        for i in range(row_index, num_of_rows):
            if len(form.table_rows) <= i:
                form.table_rows += [[]]
            form.table_rows[i] += [["", ""]]

    explainers = sum(sum_explainer.values())
    values = list(
        map(lambda val: int(round(val * 100 / explainers, 0)), sum_explainer.values())
    )
    form.value_percent = max(values)
    for i, percent in enumerate(values):
        form.table_heads[2 * i] += [percent]

    age_feature = Feature.query.filter(Feature.name == "Age").first()
    age_case_val = all_case_values_query_for_patient.filter(
        CaseValue.feature_id == age_feature.id
    ).first()

    form.age = int(age_case_val.value)
    form.age = age_range_groups(range_groups_ages, form.age)
    form.case_id = case_id
    form.prediction_score = prediction_score(age_case_val.prediction)
    form.predicted = predicted(form.prediction_score)

    def check_is_list(val):
        return type(val) is list

    return render_template(
        "explanations_per_patient.html",
        form=form,
        check_is_list=check_is_list,
    )

# Begin financial domain!


@demo_blueprint.route("/financial_select_features", methods=["GET", "POST"])
def financial_select_features():
    form = FinancialSelectFeatures(request.form)
    features_in_file = session.get("features_in_file", [])
    features = Feature.query.filter(Feature.id.in_(features_in_file)).all()
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
        session["ranges_for_feature"] = {}
        return redirect(url_for("demo.financial_range_groups"))
    elif form.is_submitted():
        flash("Invalid data", "warning")
    return render_template(
        "financial_select_features.html", features=features, pred_pow=pred_pow, form=form,
    )


@demo_blueprint.route("/financial_range_groups", methods=["GET", "POST"])
def financial_range_groups():
    form = RangeGroupsForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    user_data_id = session["user_data_id"]
    form.feature.choices = [(v, v) for v in form.selected_features]
    form.ranges = {}
    ranges_for_feature = session.get("ranges_for_feature", {})
    for feature_name in form.selected_features:
        feature = Feature.query.filter(Feature.name == feature_name).first()
        all_values = [
            c.value
            for c in CaseValue.query.filter(CaseValue.user_data_id == user_data_id)
            .filter(CaseValue.feature == feature)
            .all()
        ]
        form.ranges[feature_name] = (round(min(all_values), 3), round(max(all_values), 3))
    if form.validate_on_submit():
        if form.next.data:
            session["categories"] = {}
            return redirect(url_for("demo.financial_categories"))
        try:
            if form.feature.data in ranges_for_feature:
                ranges_for_feature[form.feature.data] += [
                    (float(form.range_from.data), float(form.range_to.data))
                ]
            else:
                ranges_for_feature[form.feature.data] = [
                    (float(form.range_from.data), float(form.range_to.data))
                ]
            session["ranges_for_feature"] = ranges_for_feature
        except ValueError:
            flash("Invalid data", "warning")
    elif form.is_submitted():
        flash("Invalid data", "warning")

    return render_template(
        "financial_range_groups.html", form=form, ranges_for_feature=ranges_for_feature
    )


@demo_blueprint.route("/financial_categories", methods=["GET", "POST"])
def financial_categories():
    form = CategoriesForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.categories = session.get("categories", {})
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    # ranges_for_feature = session.get("ranges_for_feature", {})
    if form.validate_on_submit():
        if form.submit.data:
            form.categories[form.category_name.data] = [
                k for k in request.form if request.form[k] == "on"
            ]
            session["categories"] = form.categories
        if form.next.data:
            session["categories"] = form.categories
            # {}
            return redirect(url_for("demo.financial_explan_summary"))
    elif form.is_submitted():
        flash("Invalid data", "warning")
    return render_template("financial_categories.html", form=form)

# financial_explan_summary


@demo_blueprint.route("/financial_explan_summary", methods=["GET", "POST"])
def financial_explan_summary():
    form = FlaskForm(request.form)
    categories = session.get("categories", {})
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    ranges_for_feature = session.get("ranges_for_feature", {})
    range_groups_ages = ranges_for_feature.get("Age", [])
    form.presentation_type = "Percents"
    if form.validate_on_submit():
        form.presentation_type = request.form["presentation_type"]
    elif form.is_submitted():
        flash("Invalid data", "warning")

    form.table_heads = [
        "Patient ID",
        "Age",
        f"{form.subdomain.name} Predicted",
        "Prediction or Confidence Score (Out of 100)",
    ]

    form.table_heads += [f"{name} Contribution" for name in categories]

    all_case_values_query = CaseValue.query.filter(
        CaseValue.user_data_id == session["user_data_id"]
    )
    max_patient_id = max([v.case_id for v in all_case_values_query.all()])
    form.table_rows = []
    for patient_id in range(max_patient_id + 1):
        all_case_values_query_for_patient = all_case_values_query.filter(
            CaseValue.case_id == patient_id
        )
        if not all_case_values_query_for_patient.all():
            continue
        age_feature = Feature.query.filter(Feature.name == "Age").first()
        age_case_val = all_case_values_query_for_patient.filter(
            CaseValue.feature_id == age_feature.id
        ).first()
        age = int(age_case_val.value)
        age = age_range_groups(range_groups_ages, age)
        prediction_score = int(round(age_case_val.prediction, 2) * 100)
        predicted = "No" if prediction_score < 50 else "Yes"
        prediction_score_color = "red"
        if prediction_score > 45:
            prediction_score_color = "yellow"
            if prediction_score > 70:
                prediction_score_color = "green"

        patient_id_bgcolor = "MediumSlateBlue"
        row = [
            (patient_id, patient_id_bgcolor),
            (age, None),
            (predicted, None),
            (prediction_score, prediction_score_color),
        ]
        explainers = []
        for cat_name in categories:
            sum_explainer = 0
            for feature_name in categories[cat_name]:
                feature = Feature.query.filter(Feature.name == feature_name).first()
                case_val = all_case_values_query_for_patient.filter(
                    CaseValue.feature_id == feature.id
                ).first()
                sum_explainer += case_val.explainer
            explainers += [sum_explainer]
        # if not selected percentage
        cells = None

        if form.presentation_type == "Percents":
            hundred = sum(explainers)
            values = list(
                map(lambda val: int(round(val * 100 / hundred, 0)), explainers)
            )
            max_val = max(values)
            colors = list(
                map(lambda val: ("green" if val == max_val else None), values)
            )
            cells = list(zip(values, colors))
        else:
            values = list(map(lambda val: (round(val, 4)), explainers))
            max_val = max(values)
            colors = list(
                map(lambda val: ("green" if val == max_val else None), values)
            )
            cells = list(zip(values, colors))
        row += cells
        form.table_rows += [row]

    return render_template(
        "financial_explan_summary.html", form=form, range_groups_ages=range_groups_ages,
    )


@demo_blueprint.route("/financial_explan_per_patient/<case_id>", methods=["GET", "POST"])
def financial_explan_per_patient(case_id):
    form = FlaskForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.categories = session.get("categories", {})
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    ranges_for_feature = session.get("ranges_for_feature", {})
    range_groups_ages = ranges_for_feature.get("Age", [])
    all_case_values_query = CaseValue.query.filter(
        CaseValue.user_data_id == session["user_data_id"]
    )
    all_case_values_query_for_patient = all_case_values_query.filter(
        CaseValue.case_id == case_id
    )
    form.presentation_type = "Proportional to the Total Confidence Score"

    if form.validate_on_submit():
        form.presentation_type = request.form["presentation_type"]
    elif form.is_submitted():
        flash("Invalid data", "warning")

    form.table_heads = []
    sum_explainer = {}
    sum_explainer_abs = {}
    for cat_name in form.categories:
        sum_explainer[cat_name] = 0
        sum_explainer_abs[cat_name] = 0
        for feature_name in form.categories[cat_name]:
            feature = Feature.query.filter(Feature.name == feature_name).first()
            case_val = all_case_values_query_for_patient.filter(
                CaseValue.feature_id == feature.id
            ).first()
            sum_explainer[cat_name] += case_val.explainer
            sum_explainer_abs[cat_name] += abs(case_val.explainer)
        form.table_heads += [[cat_name, ], "Feature Contribution"]
    form.table_rows = []
    num_of_rows = max([len(form.categories[k]) for k in form.categories])
    for cat_name in form.categories:
        row_index = 0
        for feature_name in form.categories[cat_name]:
            if len(form.table_rows) <= row_index:
                form.table_rows += [[]]
            feature = Feature.query.filter(Feature.name == feature_name).first()
            case_val = all_case_values_query_for_patient.filter(
                CaseValue.feature_id == feature.id
            ).first()
            if form.presentation_type == "Proportional to the Total Confidence Score":
                one_square_val = sum(sum_explainer_abs.values()) / 12
                square_num = int(round(abs(case_val.explainer) / one_square_val, 0))
                form.table_rows[row_index] += [[feature_name, gen_squares_code(square_num)]]
            else:
                each_category_squares = 12 / len(form.categories)
                value_of_square = int(round(100 / each_category_squares, 0))
                sum_explainer_category = sum_explainer_abs[cat_name]
                feature_explainer = int((case_val.explainer / sum_explainer_category) * 100)
                feature_squares = int(round((feature_explainer / value_of_square), 0))
                form.table_rows[row_index] += [[feature_name, gen_squares_code(feature_squares)]]
            row_index += 1
        for i in range(row_index, num_of_rows):
            if len(form.table_rows) <= i:
                form.table_rows += [[]]
            form.table_rows[i] += [["", ""]]

    explainers = sum(sum_explainer.values())
    values = list(
        map(lambda val: int(round(val * 100 / explainers, 0)), sum_explainer.values())
    )
    form.value_percent = max(values)
    for i, percent in enumerate(values):
        form.table_heads[2 * i] += [percent]

    age_feature = Feature.query.filter(Feature.name == "Age").first()
    age_case_val = all_case_values_query_for_patient.filter(
        CaseValue.feature_id == age_feature.id
    ).first()

    form.age = int(age_case_val.value)
    form.age = age_range_groups(range_groups_ages, form.age)
    form.case_id = case_id
    form.prediction_score = prediction_score(age_case_val.prediction)
    form.predicted = predicted(form.prediction_score)

    def check_is_list(val):
        return type(val) is list

    return render_template(
        "financial_explan_per_patient.html",
        form=form,
        check_is_list=check_is_list,
    )
