import os
import pytest
import tempfile
from app import create_app
from app.database import db, db_fill_data
from app.contoller import generate_bkg_exp, ParsingError


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
    bkg_file = None
    explainer_file = None
    plot_file = None
    with open(TEST_PKL_FILE, 'rb') as file_pkl:
        with open(TEST_DATA_FILE, 'rb') as file_data:
            with tempfile.NamedTemporaryFile(delete=False) as pkl_file:
                pkl_file.write(file_pkl.read())
                pkl_file.close()
                with tempfile.NamedTemporaryFile(delete=False) as data_file:
                    data_file.write(file_data.read())
                    data_file.close()
                    bkg_file, explainer_file, plot_file = generate_bkg_exp(
                        file_pkl=pkl_file.name,
                        file_data=data_file.name
                        )
    assert bkg_file
    assert explainer_file
    assert plot_file


def test_init_data_exception(client):
    bkg_file = None
    explainer_file = None
    plot_file = None
    with pytest.raises(ParsingError):
        with open(TEST_DATA_FILE, 'rb') as file_pkl:
            with open(TEST_DATA_FILE, 'rb') as file_data:
                with tempfile.NamedTemporaryFile(delete=False) as pkl_file:
                    pkl_file.write(file_pkl.read())
                    pkl_file.close()
                    with tempfile.NamedTemporaryFile(delete=False) as data_file:
                        data_file.write(file_data.read())
                        data_file.close()
                        bkg_file, explainer_file, plot_file = generate_bkg_exp(
                            file_pkl=pkl_file.name,
                            file_data=data_file.name
                            )
