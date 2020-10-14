from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField


class RangeGroupsForm(FlaskForm):
    feature = SelectField("Select Feature to Bin:")
    range_from = StringField("From:")
    range_to = StringField("To:")
    submit = SubmitField("Submit")
    next = SubmitField("Next")
