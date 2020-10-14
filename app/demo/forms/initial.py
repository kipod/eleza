from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField
from flask_wtf.file import FileField, FileAllowed


class InitialForm(FlaskForm):

    domain = HiddenField()
    model_file = FileField(
        "Select Model Dataset File :",
        validators=[FileAllowed(["*"], "Upload file")],
    )
    dataset_file = FileField(
        "Select Dataset File :",
        validators=[FileAllowed(["*"], "Upload file")],
    )

    next = SubmitField("Next")
