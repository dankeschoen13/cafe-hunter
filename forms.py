from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, URL, Length, InputRequired
from flask_ckeditor import CKEditorField
from flask_ckeditor.utils import cleanify

def safe_cleanify(value):
    if not value:
        return value
    return cleanify(value)

class AddForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=250)])
    map_url = StringField('Map URL', validators=[DataRequired(), Length(max=500), URL()])
    img_url = StringField('Image URL', validators=[DataRequired(), Length(max=500), URL()])
    location = StringField('Location', validators=[DataRequired(), Length(max=250)])
    seats = StringField('How many seats?', validators=[DataRequired(), Length(max=250)])

    has_toilet = BooleanField('Has toilet?')
    has_wifi = BooleanField('Has WiFi?')
    has_sockets = BooleanField('Has wall sockets?')
    can_take_calls = BooleanField('Can take calls?')
    
    coffee_price = StringField('Price of Coffee:', validators=[DataRequired(), Length(max=250)])
    description = CKEditorField('Description', filters=[safe_cleanify])
    submit = SubmitField('SUBMIT')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(max=250)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    name = StringField('Name', validators=[DataRequired(), Length(max=250)])
    submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(max=250)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Sign in')