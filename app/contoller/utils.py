from app.models import CaseValue, Feature


def predictive_power(subdomain):
    result = {}
    for feature in Feature.query.all():
        all = (
            CaseValue.query.filter(CaseValue.subdomain == subdomain)
            .filter(CaseValue.feature == feature)
            .all()
        )
        count = len(all)
        if not count:
            return {}
        result[feature.name] = sum([abs(case.explainer) for case in all]) / count
        result[feature.name] = add_pred_pow(result[feature.name])
    return result


def add_pred_pow(result_pow):
    if result_pow < 0.1:
        result_pow = result_pow * 10
    return result_pow
