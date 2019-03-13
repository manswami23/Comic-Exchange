# app/listings/__init__.py

from flask import Blueprint

listings = Blueprint('listings', __name__)

from . import views
