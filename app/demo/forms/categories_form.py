from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField


class CategoriesForm(FlaskForm):
    category_name = StringField("Enter category name:")
    submit = SubmitField("Submit")
    next = SubmitField("Next")
