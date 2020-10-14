import json
import operator
from flask import render_template, request, session, redirect, url_for, flash
from flask_login import login_required
from app.models import Feature, Subdomain, ModelType, CaseValue
from app.contoller import predictive_power
from flask_wtf import FlaskForm
from app.demo.forms import (
    SubdomainChoiceForm,
    SelectFeaturesForm,
    RangeGroupsForm,
    CategoriesForm,
    FinancialSelectFeatures,
    InitialForm
)
from app.demo.controller import (
    prediction_score,
    predicted,
    age_range_groups,
    gen_squares_code,
)

from .util import redirect_select_features

from .initial import demo_blueprint


@demo_blueprint.route("/", methods=["GET", "POST"])
@login_required
def demo():
    form = SubdomainChoiceForm(request.form)
    form_initial = InitialForm(request.form)
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

        redirect_select_features(
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
    sorted_x = sorted(pred_pow.items(), key=operator.itemgetter(1), reverse=True)
    pred_pow = dict(sorted_x)
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
        "select_features.html", features=features, pred_pow=pred_pow, form=form
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
    Feature_Name_Age = "Age"
    for feature_name in form.selected_features:
        feature = Feature.query.filter(Feature.name == feature_name).first()
        all_values = [
            c.value
            for c in CaseValue.query.filter(CaseValue.user_data_id == user_data_id)
            .filter(CaseValue.feature == feature)
            .all()
        ]
        if feature_name == Feature_Name_Age:
            form.ranges[feature_name] = (
                int(min(all_values)),
                int(max(all_values)),
            )
        else:
            form.ranges[feature_name] = (
                round(min(all_values), 3),
                round(max(all_values), 3),
            )
    if form.validate_on_submit():
        if form.next.data:
            session["categories"] = "{}"
            return redirect(url_for("demo.categories"))
        try:
            min_val_of_range_from = float(form.ranges[form.feature.data][0])
            max_val_of_range_from = float(form.ranges[form.feature.data][1])
            if form.feature.data in ranges_for_feature:
                if form.feature.data == "Age":
                    if (
                        (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        )
                        or (float(form.range_from.data) < min_val_of_range_from)
                        or (float(form.range_from.data) > max_val_of_range_from)
                    ):
                        if float(form.range_from.data) < min_val_of_range_from or (
                            float(form.range_from.data) > max_val_of_range_from
                        ):
                            form.range_from.data = min_val_of_range_from
                        if (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        ):
                            form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] += [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]
                    else:
                        ranges_for_feature[form.feature.data] += [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]

                elif (
                    (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    )
                    or (float(form.range_from.data) < min_val_of_range_from)
                    or (float(form.range_from.data) > max_val_of_range_from)
                ):
                    if float(form.range_from.data) < min_val_of_range_from or (
                        float(form.range_from.data) > max_val_of_range_from
                    ):
                        form.range_from.data = min_val_of_range_from
                    if (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    ):
                        form.range_to.data = max_val_of_range_from
                    ranges_for_feature[form.feature.data] += [
                        (float(form.range_from.data), float(form.range_to.data))
                    ]
                else:
                    ranges_for_feature[form.feature.data] += [
                        (float(form.range_from.data), float(form.range_to.data))
                    ]
            else:
                if form.feature.data == "Age":
                    if (
                        (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        )
                        or (float(form.range_from.data) < min_val_of_range_from)
                        or (float(form.range_from.data) > max_val_of_range_from)
                    ):
                        if float(form.range_from.data) < min_val_of_range_from or (
                            float(form.range_from.data) > max_val_of_range_from
                        ):
                            form.range_from.data = min_val_of_range_from
                        if (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        ):
                            form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] = [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]
                    else:
                        ranges_for_feature[form.feature.data] = [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]

                elif (
                    (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    )
                    or (float(form.range_from.data) < min_val_of_range_from)
                    or (float(form.range_from.data) > max_val_of_range_from)
                ):
                    if float(form.range_from.data) < min_val_of_range_from or (
                        float(form.range_from.data) > max_val_of_range_from
                    ):
                        form.range_from.data = min_val_of_range_from
                    if (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    ):
                        form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] = [
                            (float(form.range_from.data), float(form.range_to.data))
                        ]
                    else:
                        ranges_for_feature[form.feature.data] = [
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
    form.categories = json.loads(session.get("categories", "{}"))
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    # ranges_for_feature = session.get("ranges_for_feature", {})
    if form.validate_on_submit():
        if form.submit.data:
            form.categories[form.category_name.data] = [
                k for k in request.form if request.form[k] == "on"
            ]
            session["categories"] = json.dumps(form.categories)
        if form.next.data:
            if not form.categories:
                flash("Need define at least one category", "danger")
                return render_template("categories.html", form=form)
            session["categories"] = json.dumps(form.categories)
            # {}
            return redirect(url_for("demo.explanations_summary"))
    elif form.is_submitted():
        flash("Invalid data", "warning")

    # def reversed_function(argument):
    #     return reversed(argument)

    return render_template("categories.html", form=form)


@demo_blueprint.route("/explanations_summary", methods=["GET", "POST"])
def explanations_summary():
    form = FlaskForm(request.form)
    categories = json.loads(session.get("categories", "{}"))
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
        "Prediction_or_Confidence Score (Out of 100)",
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
        prediction_score_color = "green"
        if prediction_score > 45:
            prediction_score_color = "yellow"
            if prediction_score > 70:
                prediction_score_color = "red"

        row = [
            (patient_id, None),
            (age, None),
            (predicted, None),
            (prediction_score, prediction_score_color),
        ]
        explainers = []
        explainers_abs_values = []
        for cat_name in categories:
            sum_explainer = 0
            for feature_name in categories[cat_name]:
                feature = Feature.query.filter(Feature.name == feature_name).first()
                case_val = all_case_values_query_for_patient.filter(
                    CaseValue.feature_id == feature.id
                ).first()
                sum_explainer += case_val.explainer
            explainers += [sum_explainer]
            explainers_abs_values += [abs(sum_explainer)]
        # if not selected percentage
        cells = None

        if form.presentation_type == "Percents":
            hundred = sum(explainers_abs_values)
            values = list(
                map(lambda val: int(round(val * 100 / hundred, 0)), explainers)
            )
            max_val = max(values)
            colors = list(map(lambda val: ("red" if val == max_val else None), values))
            values = map(lambda val: f"{val}%", values)
            cells = list(zip(values, colors))
        else:
            values = list(map(lambda val: (round(val, 3)), explainers))
            max_val = max(values)
            colors = list(map(lambda val: ("red" if val == max_val else None), values))
            cells = list(zip(values, colors))
        row += cells
        form.table_rows += [row]

    return render_template(
        "explanations_summary.html",
        form=form,
        range_groups_ages=range_groups_ages,
        len=len,
    )


@demo_blueprint.route("/explanations_per_patient/<case_id>", methods=["GET", "POST"])
def explanations_per_patient(case_id):
    form = FlaskForm(request.form)
    form.selected_features = session.get("selected_features", [])
    form.categories = json.loads(session.get("categories", "{}"))
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
                form.table_rows[row_index] += [
                    [feature_name, gen_squares_code(square_num)]
                ]
            else:
                each_category_squares = 12 / len(form.categories)
                value_of_square = int(round(100 / each_category_squares, 0))
                sum_explainer_category = sum_explainer_abs[cat_name]
                feature_explainer = int(
                    (case_val.explainer / sum_explainer_category) * 100
                )
                feature_squares = int(round((feature_explainer / value_of_square), 0))
                form.table_rows[row_index] += [
                    [feature_name, gen_squares_code(feature_squares)]
                ]
            row_index += 1
        for i in range(row_index, num_of_rows):
            if len(form.table_rows) <= i:
                form.table_rows += [[]]
            form.table_rows[i] += [["", ""]]
    explainers = sum((list(map(abs, sum_explainer.values()))))
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
        enumerate=enumerate,
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
    sorted_x = sorted(pred_pow.items(), key=operator.itemgetter(1), reverse=True)
    pred_pow = dict(sorted_x)
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
        "financial_select_features.html",
        features=features,
        pred_pow=pred_pow,
        form=form,
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
    Feature_Name_Age = "Age"
    for feature_name in form.selected_features:
        feature = Feature.query.filter(Feature.name == feature_name).first()
        all_values = [
            c.value
            for c in CaseValue.query.filter(CaseValue.user_data_id == user_data_id)
            .filter(CaseValue.feature == feature)
            .all()
        ]
        if feature_name == Feature_Name_Age:
            form.ranges[feature_name] = (
                int(min(all_values)),
                int(max(all_values)),
            )
        else:
            form.ranges[feature_name] = (
                round(min(all_values), 3),
                round(max(all_values), 3),
            )
    if form.validate_on_submit():
        if form.next.data:
            session["categories"] = "{}"
            return redirect(url_for("demo.financial_categories"))
        try:
            min_val_of_range_from = float(form.ranges[form.feature.data][0])
            max_val_of_range_from = float(form.ranges[form.feature.data][1])
            if form.feature.data in ranges_for_feature:
                if form.feature.data == "Age":
                    if (
                        (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        )
                        or (float(form.range_from.data) < min_val_of_range_from)
                        or (float(form.range_from.data) > max_val_of_range_from)
                    ):
                        if float(form.range_from.data) < min_val_of_range_from or (
                            float(form.range_from.data) > max_val_of_range_from
                        ):
                            form.range_from.data = min_val_of_range_from
                        if (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        ):
                            form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] += [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]
                    else:
                        ranges_for_feature[form.feature.data] += [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]

                elif (
                    (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    )
                    or (float(form.range_from.data) < min_val_of_range_from)
                    or (float(form.range_from.data) > max_val_of_range_from)
                ):
                    if float(form.range_from.data) < min_val_of_range_from or (
                        float(form.range_from.data) > max_val_of_range_from
                    ):
                        form.range_from.data = min_val_of_range_from
                    if (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    ):
                        form.range_to.data = max_val_of_range_from
                    ranges_for_feature[form.feature.data] += [
                        (float(form.range_from.data), float(form.range_to.data))
                    ]
                else:
                    ranges_for_feature[form.feature.data] += [
                        (float(form.range_from.data), float(form.range_to.data))
                    ]
            else:
                if form.feature.data == "Age":
                    if (
                        (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        )
                        or (float(form.range_from.data) < min_val_of_range_from)
                        or (float(form.range_from.data) > max_val_of_range_from)
                    ):
                        if float(form.range_from.data) < min_val_of_range_from or (
                            float(form.range_from.data) > max_val_of_range_from
                        ):
                            form.range_from.data = min_val_of_range_from
                        if (
                            min_val_of_range_from > float(form.range_to.data)
                            or float(form.range_to.data) > max_val_of_range_from
                        ):
                            form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] = [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]
                    else:
                        ranges_for_feature[form.feature.data] = [
                            (
                                (
                                    int(float(form.range_from.data)),
                                    int(float(form.range_to.data)),
                                )
                            )
                        ]

                elif (
                    (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    )
                    or (float(form.range_from.data) < min_val_of_range_from)
                    or (float(form.range_from.data) > max_val_of_range_from)
                ):
                    if float(form.range_from.data) < min_val_of_range_from or (
                        float(form.range_from.data) > max_val_of_range_from
                    ):
                        form.range_from.data = min_val_of_range_from
                    if (
                        min_val_of_range_from > float(form.range_to.data)
                        or float(form.range_to.data) > max_val_of_range_from
                    ):
                        form.range_to.data = max_val_of_range_from
                        ranges_for_feature[form.feature.data] = [
                            (float(form.range_from.data), float(form.range_to.data))
                        ]
                    else:
                        ranges_for_feature[form.feature.data] = [
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
    form.categories = json.loads(session.get("categories", "{}"))
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    # ranges_for_feature = session.get("ranges_for_feature", {})
    if form.validate_on_submit():
        if form.submit.data:
            form.categories[form.category_name.data] = [
                k for k in request.form if request.form[k] == "on"
            ]
            session["categories"] = json.dumps(form.categories)
        if form.next.data:
            if not form.categories:
                flash("Need define at least one category", "danger")
                return render_template("categories.html", form=form)
            session["categories"] = json.dumps(form.categories)
            # {}
            return redirect(url_for("demo.financial_explan_summary"))
    elif form.is_submitted():
        flash("Invalid data", "warning")
    return render_template("financial_categories.html", form=form)


# financial_explan_summary


@demo_blueprint.route("/financial_explan_summary", methods=["GET", "POST"])
def financial_explan_summary():
    form = FlaskForm(request.form)
    categories = json.loads(session.get("categories", "{}"))
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    ranges_for_feature = session.get("ranges_for_feature", {})
    range_groups_ages = ranges_for_feature.get("Age", [])
    form.presentation_type = "Percents"
    if form.validate_on_submit():
        form.presentation_type = request.form["presentation_type"]
    elif form.is_submitted():
        flash("Invalid data", "warning")

    form.table_heads = [
        "Client ID",
        "Age",
        "Risk of default",
        "Prediction_or_Confidence Score (Out of 100)",
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
        predicted = "No" if prediction_score < 10 else "Yes"
        prediction_score_color = "green"
        if prediction_score > 45:
            prediction_score_color = "yellow"
            if prediction_score > 70:
                prediction_score_color = "red"

        row = [
            (patient_id, None),
            (age, None),
            (predicted, None),
            (prediction_score, prediction_score_color),
        ]
        explainers = []
        explainers_abs_values = []
        for cat_name in categories:
            sum_explainer = 0
            for feature_name in categories[cat_name]:
                feature = Feature.query.filter(Feature.name == feature_name).first()
                case_val = all_case_values_query_for_patient.filter(
                    CaseValue.feature_id == feature.id
                ).first()
                sum_explainer += case_val.explainer
            explainers += [sum_explainer]
            explainers_abs_values += [abs(sum_explainer)]
        # if not selected percentage
        cells = None

        if form.presentation_type == "Percents":
            hundred = sum(explainers_abs_values)
            values = list(
                map(lambda val: int(round(val * 100 / hundred, 0)), explainers)
            )
            max_val = max(values)
            colors = list(map(lambda val: ("red" if val == max_val else None), values))
            values = map(lambda val: f"{val}%", values)
            cells = list(zip(values, colors))
        else:
            values = list(map(lambda val: (round(val * 100, 2)), explainers))
            max_val = max(values)
            colors = list(map(lambda val: ("red" if val == max_val else None), values))
            cells = list(zip(values, colors))
        row += cells
        form.table_rows += [row]

    return render_template(
        "financial_explan_summary.html",
        form=form,
        range_groups_ages=range_groups_ages,
        len=len,
    )


@demo_blueprint.route("/financial_explan_per_client/<case_id>", methods=["GET"])
def financial_explan_per_client(case_id):
    form = FinancialSelectFeatures(request.form)
    form.case_id = case_id
    form.selected_features = session.get("selected_features", [])
    form.categories = json.loads(session.get("categories", "{}"))
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    all_case_values_query = CaseValue.query.filter(
        CaseValue.user_data_id == session["user_data_id"]
    )
    all_case_values_query_for_patient = all_case_values_query.filter(
        CaseValue.case_id == case_id
    )

    form.table_rows = [[]]
    sum_explainers = 0
    for cat_name in form.categories:
        feature_values = []
        for feature_name in form.categories[cat_name]:
            feature = Feature.query.filter(Feature.name == feature_name).first()
            case_val = all_case_values_query_for_patient.filter(
                CaseValue.feature_id == feature.id
            ).first()
            feature_values.append(feature_name)
            feature_values.append(str(round(case_val.value, 3)))
            feature_values.append(round(case_val.explainer * 100, 3))
            sum_explainers += case_val.explainer * 100
            if len(feature_name) >= 2:
                form.table_rows += [feature_values]
                feature_values = []
    form.table_rows += [["Total", "", round(sum_explainers, 3)]]
    total_score_name_client = round(sum_explainers, 3)

    prediction_score_list = []
    max_patient_id = max([v.case_id for v in all_case_values_query.all()])
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
        prediction_score = int(round(age_case_val.prediction, 2) * 100)
        prediction_score_list += [prediction_score]
    sum_prediction_score = sum(prediction_score_list)
    average_default_score = round(sum_prediction_score / (max_patient_id + 1), 2)

    return render_template(
        "financial_explan_per_client.html",
        form=form,
        total_score_name_client=total_score_name_client,
        average_default_score=average_default_score
    )


@demo_blueprint.route("/financial_explan_2_per_client/<case_id>", methods=["GET"])
def financial_explan_2_per_client(case_id):
    form = FlaskForm(request.form)
    form.case_id = case_id
    form.categories = json.loads(session.get("categories", "{}"))
    form.subdomain = Subdomain.query.get(session.get("subdomain", None))
    all_case_values_query = CaseValue.query.filter(
        CaseValue.user_data_id == session["user_data_id"]
    )
    all_case_values_query_for_patient = all_case_values_query.filter(
        CaseValue.case_id == case_id
    )

    form.table_heads = ["Categories", "Characteristics", "Attributes", "Contributions"]
    form.table_rows = []
    total_contrib = 0
    for cat_name in form.categories:
        sub_head = [cat_name, "", "", ""]
        form.table_rows += [sub_head]
        sum_contribution = 0
        for feature_name in form.categories[cat_name]:
            feature = Feature.query.filter(Feature.name == feature_name).first()
            case_val = all_case_values_query_for_patient.filter(
                CaseValue.feature_id == feature.id
            ).first()
            form.table_rows += [
                [
                    "",
                    feature_name,
                    round(case_val.value, 3),
                    round(case_val.explainer * 100, 3),
                ]
            ]
            sum_contribution += case_val.explainer * 100
        sub_head[3] = round(sum_contribution, 3)
        total_contrib += sum_contribution
    form.table_rows += [["Total", "", "", round(total_contrib, 3)]]
    total_score_name_client = round(total_contrib, 3)

    prediction_score_list = []
    max_patient_id = max([v.case_id for v in all_case_values_query.all()])
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
        prediction_score = int(round(age_case_val.prediction, 2) * 100)
        prediction_score_list += [prediction_score]
    sum_prediction_score = sum(prediction_score_list)
    average_default_score = round(sum_prediction_score / (max_patient_id + 1), 2)

    return render_template(
        "financial_explan_2_per_client.html",
        form=form,
        total_score_name_client=total_score_name_client,
        average_default_score=average_default_score
    )
