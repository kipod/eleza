import json
from flask import render_template, request, session
from .blueprint import demo_blueprint
from app.models import Feature, Subdomain, CaseValue
from flask_wtf import FlaskForm
from app.demo.controller import age_range_groups


@demo_blueprint.route("/financial_explan_2_per_client/<case_id>", methods=["GET"])
def financial_explan_2_per_client(case_id):
    form = FlaskForm(request.form)
    form.case_id = case_id
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

    # age_feature = Feature.query.filter(Feature.name == "Age").first()
    # age_case_val = all_case_values_query_for_patient.filter(
    #     CaseValue.feature_id == age_feature.id
    # ).first()
    # age_case_value = int(age_case_val.value)
    # age_case_explainer = round((age_case_val.explainer * 100), 3)

    # form.age_table_row = ["", "Age", age_case_value, age_case_explainer]

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
            if feature_name == "Age" or feature_name.startswith("Number"):
                age = int(case_val.value)
                age = age_range_groups(range_groups_ages, age)
                form.table_rows += [
                    [
                        "",
                        feature_name,
                        age,
                        round(case_val.explainer * 100, 3),
                    ]
                ]
            else:
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
