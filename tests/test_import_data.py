import os
import pytest
from app import create_app
from app.database import db, db_fill_data
from app.contoller.import_data import import_data_from_file
from app.models import CaseValue, Subdomain
from app.contoller.utils import predictive_power


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_CSV_VALUE_FILE = os.path.join(BASE_DIR, "diabetes_background_dataset.csv")
TEST_CSV_EXPLAINER_FILE = os.path.join(BASE_DIR, "diabetes_explainer_dataset.csv")

app = create_app(environment="testing")


@pytest.fixture
def client():
    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        db_fill_data(import_values=False)
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def import_test_data():
    TEST_SUBDOMAIN = "Diabetic"
    TEST_DOMAIN = "healthcare"
    TEST_MODEL = "Model1"
    subdomain = (
        Subdomain.query.filter(Subdomain.name == TEST_SUBDOMAIN)
        .filter(Subdomain.domain == TEST_DOMAIN)
        .first()
    )
    subdomain_id = subdomain.id

    CaseValue.query.delete()
    import_data_from_file(
        TEST_CSV_VALUE_FILE, TEST_CSV_EXPLAINER_FILE, subdomain_id, TEST_MODEL
    )


def test_import(client):
    import_test_data()
    assert len(CaseValue.query.all())
    for case in CaseValue.query.all():
        assert case.value is not None
        assert case.explainer
        assert case.subdomain
        assert case.case_id is not None
        assert case.model_type
        assert case.feature


def test_predictive_power(client):
    import_test_data()
    subdomain = (
        Subdomain.query.filter(Subdomain.name == "Diabetic")
        .filter(Subdomain.domain == Subdomain.Domain.healthcare)
        .first()
    )
    # feature = Feature.query.filter(Feature.name == "Age").first()
    # pp = predictive_power(feature=feature, subdomain=subdomain)
    all_pp = predictive_power(subdomain=subdomain, user_data_id=1)
    assert max(all_pp.values()) >= 1
    assert max(all_pp.values()) <= 10
