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
    from app.models import Subdomain, ModelType, Feature, User

    Subdomain(domain=Subdomain.Domain.healthcare, name="Cancer").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Diabetic").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Dermatology").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Radiology").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Pharma").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Genomics").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Cardiac").save(False)
    Subdomain(domain=Subdomain.Domain.financial, name="Credit").save(False)
    ModelType(name="Model1").save(False)
    ModelType(name="Model2").save(False)
    ModelType(name="Model3").save(False)
    ModelType(name="Model4").save(False)
    ModelType(name="Model5").save(False)
    Feature(name="Age", short_name="age").save()
    Feature(name="Number of Pregnancies", short_name="preg").save(False)
    Feature(name="Blood Pressure", short_name="pres").save(False)
    Feature(name="Skin Thickness", short_name="skin").save(False)
    Feature(name="Body Mass Index", short_name="mass").save(False)
    Feature(name="Diabetes Family Pedigree", short_name="pedi").save(False)
    Feature(name="Glucose", short_name="plas").save()
    Feature(name="Insulin", short_name="test").save()


    user = User(username="admin", email="simple2b.info@gmail.com")
    user.password = "ZAQ!xsw2"
    user.save()
