import json
from flask import request, session, render_template, flash
from flask_wtf import FlaskForm
from .blueprint import demo_blueprint

from app.models import Feature, Subdomain, CaseValue
from app.demo.controller import (
    age_range_groups,
    gen_squares_code,
    prediction_score,
    predicted,
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
