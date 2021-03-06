import os
import pytest
from app import create_app
from app.database import db, db_fill_data
from app.models import Subdomain, UserData
from .login import login, register


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
        db_fill_data()
        register(client)
        login(client)
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_upload_files(client):
    with open(TEST_CSV_VALUE_FILE, "rb") as bkg_f:
        with open(TEST_CSV_EXPLAINER_FILE, "rb") as exp_f:
            data = {
                "subdomain_id": Subdomain.query.filter(Subdomain.name == 'Diabetic').first().id,
                "domain": Subdomain.Domain.healthcare.name,
                "bkg_file": (bkg_f, "test_bkg.csv"),
                "explainer_file": (exp_f, "test_bkg.csv"),
                "model_type": "Model1",
            }
            response = client.post(
                "demo/",
                data=data,
                follow_redirects=False,
                content_type="multipart/form-data",
            )
            assert response.status_code == 302
    response = client.get(response.location)
    assert response.status_code == 200
    assert UserData.query.all(), "User Data presents in DB"
