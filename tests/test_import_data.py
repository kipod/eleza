import os
import pytest
from app import create_app
from app.database import db, db_fill_data
from app.contoller.import_data import import_data_from_file
from app.models import CaseValue


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


def test_import(client):
    CaseValue.query.delete()
    import_data_from_file(
        TEST_CSV_VALUE_FILE, TEST_CSV_EXPLAINER_FILE, "Diabetic", "healthcare",
    )
    assert len(CaseValue.query.all())
    for case in CaseValue.query.all():
        assert case.value is not None
        assert case.explainer
        assert case.subdomain
        assert case.case_id is not None
        assert case.model_type
        assert case.feature
