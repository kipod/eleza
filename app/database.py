"""Database initiation"""
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "init_data"
)


def db_fill_data(import_values=True):
    from app.models import Subdomain, ModelType, Feature
    from app.contoller import import_data_from_file

    Subdomain(type=Subdomain.Type.healthcare, name="Cancer").save(False)
    Subdomain(type=Subdomain.Type.healthcare, name="Diabetic").save(False)
    Subdomain(type=Subdomain.Type.healthcare, name="Dermatology").save(False)
    Subdomain(type=Subdomain.Type.healthcare, name="Radiology").save(False)
    Subdomain(type=Subdomain.Type.healthcare, name="Pharma").save(False)
    Subdomain(type=Subdomain.Type.healthcare, name="Genomics").save(False)
    ModelType(name="XGBoost").save(False)
    Feature(name="Age", short_name="age").save()
    Feature(name="Number of Pregnancies", short_name="preg").save(False)
    Feature(name="Blood Pressure", short_name="pres").save(False)
    Feature(name="Skin Thickness", short_name="skin").save(False)
    Feature(name="Body Mass Index", short_name="mass").save(False)
    Feature(name="Diabetes Family Pedigree", short_name="pedi").save()
    # Feature(name="Glucose", short_name="gluc").save()
    # Feature(name="Skin Thickness", short_name="skin").save() ??
    # TODO: others features: fill questions.txt
    # Feature(name="")

    if import_values:
        # load init data
        # Healthcare - Diabetic
        import_data_from_file(
            file_path_value=os.path.join(BASE_DIR, "diabetes_background_dataset.csv"),
            file_path_explaner=os.path.join(BASE_DIR, "diabetes_explainer_dataset.csv"),
            subdomain_name="Diabetic",
            subdomain_type=Subdomain.Type.healthcare.name,
            model_type="XGBoost",
        )
        # Financial - Credit
        import_data_from_file(
            file_path_value=os.path.join(BASE_DIR, "credit_background_dataset.csv"),
            file_path_explaner=os.path.join(BASE_DIR, "credit_explainer_dataset.csv"),
            subdomain_name="Credit",
            subdomain_type=Subdomain.Type.financial.name,
            model_type="XGBoost",
        )
