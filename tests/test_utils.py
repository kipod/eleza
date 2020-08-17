import pytest
from app import create_app
from app.database import db, db_fill_data
from app.contoller import predictive_power
from app.models import Feature, Subdomain


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
        .filter(Subdomain.type == Subdomain.Type.healthcare)
        .first()
    )
    feature = Feature.query.filter(Feature.name == "Age").first()
    pp = predictive_power(feature=feature, subdomain=subdomain)
    assert pp > 0.09
    assert pp < 10.0
