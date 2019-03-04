# app/models.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

# Set up a table for many-many relationship between Selling and User
want_to_sell = db.Table('want_to_sell', db.Column('selling_id', db.Integer, db.ForeignKey('selling.id'), primary_key=True), db.Column('users_id', db.Integer, db.ForeignKey('users.id'), primary_key = True))


class User(UserMixin, db.Model):
    """
    Create a User table
    """

    # Ensures table will be named in plural and not in singular
    # as in the name of the model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    rating = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.email)


    # Set up user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    
class Selling(db.Model):
    """
    Create a Selling table
    """

    __tablename__ = 'selling'

    id = db.Column(db.Integer, primary_key=True)
    listingId = db.Column(db.Integer)
    price = db.Column(db.Float)
    date_posted = db.Column(db.String(10))
    want_to_sell = db.relationship('User', secondary=want_to_sell, lazy='subquery', 
        backref=db.backref('pages', lazy=True))

    def __repr(self):
        return '<Selling: {}>'.format(self.email)

