# app/auth/views.py

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user
from sqlalchemy import text
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from werkzeug.security import generate_password_hash
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        engine = db.engine
        connection = engine.connect()
        sql = text('INSERT INTO users (email, password_hash) VALUES(:x, :y)')
        connection.execute(sql, x = form.email.data, y = generate_password_hash(form.password.data))
        connection.close()
        #user = User(email = form.email.data, password = form.password.data)
        
        # Add user to the database
        #db.session.add(user)
        #db.session.commit()
        flash('Registration successful!')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log in a user through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():
        # check whether user exists in the database and whether
        # the password entered matches the password in the database
        engine = db.engine
        connection = engine.connect()
        sql = text('SELECT email, password_hash FROM users WHERE users.email = :x')
        result = connection.execute(sql, x= form.email.data)
        row = result.fetchone()
        user = User.query.filter_by(email=form.email.data).first()
        if row and user.verify_password(form.password.data):
            user = User.query.filter_by(email=form.email.data).first()
            # log in the user
            login_user(user)

            # redirect to the dashboard page after login
            connection.close()
            return redirect(url_for('home.dashboard'))
            
        # when login details are incorrect
        else:
            flash('Invalid email or password.')
            connection.close()

    # load login template
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log a user out through the logout link
    """
    logout_user()
    flash('You have successfuly logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))
