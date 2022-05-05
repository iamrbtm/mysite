from flask_wtf import FlaskForm
import email_validator, flask_login
from wtforms import (
    StringField,
    DateField,
    DecimalField,
    IntegerField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    FloatField,
    FileField,
    HiddenField,
    TextAreaField
)
from wtforms.validators import InputRequired, Email, URL, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms_sqlalchemy.orm import model_form
from website import db
from website.models import *

class Project_Form(FlaskForm):
    project_name = StringField("Project Name")
    project_description = TextAreaField("Project Name")