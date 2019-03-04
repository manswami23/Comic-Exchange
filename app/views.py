# config.py

class Config(object):
    """
    common configurations
    """

    # Put any configurations here that are across all environments


class DevelopmentConfig(Config):
    """
    Development configurations

    TESTING - activates testing mode for Flask extensions
    DEBUG - activates debug mode on the app
    SQLALCHEMY_ECHO - logs SQLAlchemy errors
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}