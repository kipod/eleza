import csv
from io import TextIOWrapper
from app.database import db
from app.models import Subdomain, ModelType, Feature, CaseValue, UserData
from app.logger import log


def import_data_from_file_stream(
    file_value, file_explainer, subdomain_id, model_type,
):
    subdomain = Subdomain.query.filter(Subdomain.id == subdomain_id).first()
    user_data = UserData().save()
    model = ModelType.query.filter(ModelType.name == model_type).first()
    feature_names = {feature.short_name: feature for feature in Feature.query.all()}
    csv_reader = csv.DictReader(
        TextIOWrapper(file_value, encoding="utf-8"), delimiter=","
    )
    read_features = []
    try:
        for row in csv_reader:
            case_id = int(row[""])
            prediction = row["predictions"]
            for feature_short_name in feature_names:
                if feature_short_name in row:
                    if feature_names[feature_short_name] not in read_features:
                        read_features += [feature_names[feature_short_name]]
                    value = float(row[feature_short_name])
                    case = CaseValue(
                        case_id=case_id,
                        value=value,
                        feature=feature_names[feature_short_name],
                        subdomain=subdomain,
                        model_type=model,
                        user_data=user_data,
                        prediction=prediction
                    ).save(False)

        csv_reader = csv.DictReader(
            TextIOWrapper(file_explainer, encoding="utf-8"), delimiter=","
        )
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
                        .filter(CaseValue.user_data == user_data)
                        .first()
                    )
                    assert case
                    case.explainer = explainer
    except Exception:
        return

    db.session.commit()
    log(log.INFO, "Import data successfull for %s[%s]", subdomain.domain, subdomain_id)
    return user_data, read_features


def import_data_from_file(
    file_path_value, file_path_explainer, subdomain_id, model_type,
):
    with open(file_path_value, "rb") as f_value:
        with open(file_path_explainer, "rb") as f_explainer:
            return import_data_from_file_stream(
                f_value, f_explainer, subdomain_id, model_type
            )
