from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, HiddenField
from app.models import Subdomain, ModelType


def get_subdomain_names():
    """retrieve list of choices for SelectField
    """
    return [(s.name, s.name) for s in Subdomain.query.all()]


def get_model_type_names():
    """retrieve list of choices for SelectField
    """
    return [(m.name, m.name) for m in ModelType.query.all()]


class SubdomainChoiceForm(FlaskForm):

    subdomain_name = SelectField("Type of application subdomain:")
    subdomain_type = HiddenField()
    model_type = SelectField("Select Model Type:")
    next = SubmitField("Next")
