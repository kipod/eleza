import pytest
from app import create_app
from app.database import db, db_fill_data
from app.contoller import predictive_power
from app.models import Feature, Subdomain  # noqa F401


app = create_app(environment="testing")


@pytest.fixture
def client():
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        db_fill_data()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_predictive_power(client):
    subdomain = (
        Subdomain.query.filter(Subdomain.name == "Diabetic")
        .filter(Subdomain.domain == Subdomain.Domain.healthcare)
        .first()
    )
    # feature = Feature.query.filter(Feature.name == "Age").first()
    # pp = predictive_power(feature=feature, subdomain=subdomain)
    all_pp = predictive_power(subdomain=subdomain)

    # for pp in all_pp.values():
    #     assert pp > 0.1
    #     assert pp < 10.0
