from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Optional

class SignUpForm(FlaskForm):
    """Form for registering"""
    username = StringField("Username", validators=[InputRequired(), Length(min=5, max=20)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=5, max=30)])
    image_url = StringField("Image_URL(Profile Pic)", validators=[Optional()])

class LoginForm(FlaskForm):
    """Form for logging in"""
    username = StringField("Username", validators=[InputRequired(), Length(min=5, max=20)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=5, max=30)])
