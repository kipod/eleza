"""Database initiation"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def db_fill_data():
    from app.models import Subdomain, ModelType, Feature

    Subdomain(type=Subdomain.Type.healthcare, name="Cancer").save()
    Subdomain(type=Subdomain.Type.healthcare, name="Diabetic").save()
    Subdomain(type=Subdomain.Type.healthcare, name="Dermatology").save()
    Subdomain(type=Subdomain.Type.healthcare, name="Radiology").save()
    Subdomain(type=Subdomain.Type.healthcare, name="Pharma").save()
    Subdomain(type=Subdomain.Type.healthcare, name="Genomics").save()
    ModelType(name="XGBoost").save()
    Feature(name="Age", short_name="age").save()
    Feature(name="Number of Pregnancies", short_name="preg").save()
    Feature(name="Blood Pressure", short_name="pres").save()
    Feature(name="Skin Thickness", short_name="skin").save()
    # Feature(name="")
