import csv
from io import TextIOWrapper
from app.database import db
from flask import current_app as app
from app.models import Subdomain, ModelType, Feature, CaseValue
from app.logger import log


def import_data_from_file(
    file_path_value,
    file_path_explaner,
    subdomain_name,
    subdomain_type,
    model_type="XGBoost",
):
    subdomain = (
        Subdomain.query.filter(Subdomain.name == subdomain_name)
        .filter(Subdomain.type == Subdomain.Type[subdomain_type])
        .first()
    )
    model = ModelType.query.filter(ModelType.name == model_type).first()
    feature_names = {feature.short_name: feature for feature in Feature.query.all()}
    with open(file_path_value, "rb") as f:
        csv_reader = csv.DictReader(TextIOWrapper(f, encoding="utf-8"), delimiter=",")
        for row in csv_reader:
            case_id = int(row[""])
            for feature_short_name in feature_names:
                if feature_short_name in row:
                    value = float(row[feature_short_name])
                    case = CaseValue(
                        case_id=case_id,
                        value=value,
                        feature=feature_names[feature_short_name],
                        subdomain=subdomain,
                        model_type=model,
                    )
                    db.session.add(case)

    with open(file_path_explaner, "rb") as f:
        csv_reader = csv.DictReader(TextIOWrapper(f, encoding="utf-8"), delimiter=",")
        for row in csv_reader:
            case_id = int(row[""])
            for feature_short_name in feature_names:
                if feature_short_name in row:
                    explainer = float(row[feature_short_name])
                    case = (
                        CaseValue.query.filter(CaseValue.case_id == case_id)
                        .filter(CaseValue.subdomain == subdomain)
                        .filter(CaseValue.model_type == model)
                        .filter(CaseValue.feature == feature_names[feature_short_name])
                        .first()
                    )
                    if case:
                        case.explainer = explainer

    db.session.commit()
    log(log.INFO, "Import successfull")
    if not app.config["TESTING"]:
        log(log.DEBUG, "Testing")
