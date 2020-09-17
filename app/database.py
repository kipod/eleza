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

    Subdomain(domain=Subdomain.Domain.general, name="Type 1").save(False)
    Subdomain(domain=Subdomain.Domain.general, name="Type 2").save(False)
    Subdomain(domain=Subdomain.Domain.general, name="Type 3").save(False)
    Subdomain(domain=Subdomain.Domain.general, name="Type 4").save(False)
    Subdomain(domain=Subdomain.Domain.general, name="Type 5").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Cancer").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Diabetic").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Dermatology").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Radiology").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Pharma").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Genomics").save(False)
    Subdomain(domain=Subdomain.Domain.healthcare, name="Cardiac").save(False)
    Subdomain(domain=Subdomain.Domain.financial, name="Credit Application").save(False)
    Subdomain(domain=Subdomain.Domain.financial, name="Insurance Claims").save(False)
    Subdomain(domain=Subdomain.Domain.financial, name="Investment Portfolios").save(
        False
    )
    Subdomain(domain=Subdomain.Domain.financial, name="Financial Instruments").save(
        False
    )

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
    Feature(name="Glucose", short_name="plas").save(False)
    Feature(name="Insulin", short_name="test").save()

    Feature(name="SeriousDlqin2yrs", short_name="SeriousDlqin2yrs").save()
    Feature(
        name="Revolving Utilization of Unsecured Lines",
        short_name="RevolvingUtilizationOfUnsecuredLines",
    ).save()
    Feature(
        name="Number of times 30-59 days past due not worse",
        short_name="NumberOfTime30-59DaysPastDueNotWorse",
    ).save()
    Feature(name="Debt Ratio", short_name="DebtRatio").save()
    Feature(name="Monthly Income", short_name="MonthlyIncome").save()
    Feature(
        name="Number of Open Credit Lines And Loans",
        short_name="NumberOfOpenCreditLinesAndLoans",
    ).save()
    Feature(name="Number of times 90 days late", short_name="NumberOfTimes90DaysLate").save()
    Feature(
        name="Number Real Estate Loans or Lines", short_name="NumberRealEstateLoansOrLines"
    ).save()
    Feature(
        name="Number of times 60-89 days past due not worse",
        short_name="NumberOfTime60-89DaysPastDueNotWorse",
    ).save()
    Feature(name="Number of Dependents", short_name="NumberOfDependents").save()

    user = User(username="admin", email="simple2b.info@gmail.com")
    user.password = "ZAQ!xsw2"
    user.save()
