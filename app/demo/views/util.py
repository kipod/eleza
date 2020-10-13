from flask import session, redirect, url_for
from app.contoller import import_data_from_file_stream
from app.models import Subdomain


def redirect_select_features(file_value, file_explainer, domain, subdomain_id, model_type):
    user_data, read_features = import_data_from_file_stream(
        file_value=file_value,
        file_explainer=file_explainer,
        subdomain_id=subdomain_id,
        model_type=model_type,
    )
    session["features_in_file"] = [f.id for f in read_features]
    session["user_data_id"] = user_data.id
    if domain == Subdomain.Domain.healthcare.name:
        return redirect(url_for("demo.select_features"))
    if domain == Subdomain.Domain.financial.name:
        return redirect(url_for("demo.financial_select_features"))
