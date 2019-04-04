# app/listings/forms.py

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, IntegerField, DecimalField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Optional
from .. import db
from sqlalchemy import text
from ..models import comicbook
from ..models import Selling
from datetime import datetime
        

class ListingForm(FlaskForm):
    """
    Form for users to post listings
    """
    publisher= StringField('Publisher', validators=[DataRequired()])
    series = StringField('Series', validators=[DataRequired()])
    issueNum = IntegerField('Issue #', validators=[DataRequired()])
    primaryCharacter = StringField('Primary Character', validators=[DataRequired()])
    primaryVillain = StringField('Primary Villain', validators=[DataRequired()])
    genre = SelectField('Genre', choices=[('action', 'action'), ('horror', 'horror'), ('adventure', 'adventure'), ('comedy', 'comedy'), ('mystery', 'mystery'), ('scifi', 'scifi')])
    author = StringField('Primary Author', validators=[DataRequired()])
    price = DecimalField('Price ($)', places = 10, validators=[DataRequired()])
    cgc = StringField('CGC')
    submit = SubmitField('Post Listing')
    
class CheckForm(FlaskForm):
    character = StringField('Primary Character')
    villain = StringField('Primary Villain')
    series = StringField('Series')
    issueNum = IntegerField('Issue #', validators=[Optional()])
    submit = SubmitField('submit')
    reset=  SubmitField('reset')
