import operator
from flask import request, session, render_template, redirect, url_for, flash
from .blueprint import demo_blueprint

from app.models import Feature, Subdomain
from app.demo.forms import FinancialSelectFeatures
from app.contoller import predictive_power


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
