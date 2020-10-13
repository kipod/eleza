import os
import pytest
from app import create_app
from app.database import db, db_fill_data
from app.contoller import generate_bkg_exp


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_PKL_FILE = os.path.join(BASE_DIR, "credit_app_explainers.pkl")
TEST_DATA_FILE = os.path.join(BASE_DIR, "cs-test_curated.csv")

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


def test_init_data(client):

    bkg_file, explainer_file, plot_file = generate_bkg_exp(
        path_to_pkl=TEST_PKL_FILE,
        path_to_data=TEST_DATA_FILE
        )
    assert bkg_file
    assert explainer_file
    assert plot_file
