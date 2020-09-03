from app.models import CaseValue, Feature


def predictive_power(subdomain, user_data_id):
    result = {}
    for feature in Feature.query.all():
        all = (
            CaseValue.query.filter(CaseValue.subdomain == subdomain)
            .filter(CaseValue.feature == feature)
            .filter(CaseValue.user_data_id == user_data_id)
            .all()
        )
        count = len(all)
        if not count:
            continue
        result[feature.name] = sum([abs(case.explainer) for case in all]) / count

    # result[feature.name] = add_pred_pow(result[feature.name])
    update_values(result)
    return result


def update_values(params):
    max_val = max([v for v in params.values()])
    assert max_val > 0
    multiply = 1
    while (multiply * max_val) < 1:
        multiply *= 10
    while (multiply * max_val) > 10:
        multiply *= 0.1
    for key in params:
        params[key] *= multiply
    return params
