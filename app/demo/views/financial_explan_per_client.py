import json
from flask import request, session, render_template
from .blueprint import demo_blueprint

from app.models import Feature, Subdomain, CaseValue
from app.demo.forms import FinancialSelectFeatures
from app.demo.controller import age_range_groups


@demo_blueprint.route("/financial_explan_per_client/<case_id>", methods=["GET"])
def financial_explan_per_client(case_id):
    form = FinancialSelectFeatures(request.form)
    form.case_id = case_id
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

    form.table_rows = [[]]
    sum_explainers = 0

    feature_names_in_one_position = []
    for cat_name in form.categories:
        feature_values = []
        for feature_name in form.categories[cat_name]:
            feature = Feature.query.filter(Feature.name == feature_name).first()
            case_val = all_case_values_query_for_patient.filter(
                CaseValue.feature_id == feature.id
            ).first()
            if feature_name in feature_names_in_one_position:
                sum_explainers += case_val.explainer * 100
                continue
            else:
                feature_values.append(feature_name)
                if feature_name == "Age" or feature_name.startswith("Number"):
                    age = int(case_val.value)
                    age = age_range_groups(range_groups_ages, age)
                    feature_values.append(age)
                else:
                    feature_values.append(str(round(case_val.value, 3)))
                feature_values.append(round(case_val.explainer * 100, 3))
                feature_names_in_one_position += [feature_name]

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
        average_default_score=average_default_score,
    )
