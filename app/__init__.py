# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()

login_manager = LoginManager()


def create_app(config_name):
    # create Flask object instance
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY='secret_key',
        #SQLALCHEMY_DATABASE_URI='mysql://super_admin:sugoi@localhost/superhero_db'
        SQLALCHEMY_DATABASE_URI='mysql://ba4f284f7d53c5:ff337ef1@us-cdbr-iron-east-03.cleardb.net/heroku_ac9d5074a62e26f'
    )
    # app = Flask(__name__, instance_relative_config=True)
    # app.config.from_object(app_config[config_name])
    # app.config.from_pyfile('config.py')

    # initialize database 
    db.init_app(app)

    # initialize login manager
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"
    migrate = Migrate(app, db)

    # test funcition
    # @app.route('/')
    # def hello_world():
    #     return 'Hello, World!'

    # initialize Boostrap
    Bootstrap(app)

    from app import models

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # import home blueprint
    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    # import auth blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
