import json
from flask import request, session, render_template, flash
from flask_wtf import FlaskForm
from .blueprint import demo_blueprint

from app.models import Feature, Subdomain, CaseValue
from app.demo.controller import age_range_groups


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
