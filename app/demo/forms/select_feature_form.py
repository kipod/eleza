from flask_wtf import FlaskForm
from wtforms import SubmitField


class SelectFeaturesForm(FlaskForm):
    next = SubmitField("Next")
