# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from .. import db
from sqlalchemy import text
from ..models import User

class RegistrationForm(FlaskForm):
    """
    Form for users to create new account
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')

    # Make sure every user has a unique email
    def validate_email(self, field):
            engine = db.engine
            connection = engine.connect()
            sql = text('SELECT email From users WHERE users.email = :x')
            result = connection.execute(sql, x= field.data)
            connection.close()
            #if User.query.filter_by(email=field.data).first():
            if result.first().email:
                raise ValidationError('Email is already in use.')
        

class LoginForm(FlaskForm):
    """
    Form for users to login
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
