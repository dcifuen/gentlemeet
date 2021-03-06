"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module, 
           which should be kept out of version control.

"""

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY, OAUTH2_CLIENT_SECRET


class Config(object):
    """
    Default configuration
    """
    DEBUG = False
    TESTING = False
    STAGING = False
    PRODUCTION = False
    CSRF_ENABLED = True

    # Set secret keys for CSRF protection
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY

    OAUTH2_CLIENT_SECRET = OAUTH2_CLIENT_SECRET

    # Flask-Cache settings
    CACHE_TYPE = 'gaememcached'


class ProductionConfig(Config):
    """
    Overrides the default configuration
    """
    DEBUG = False
    TESTING = False
    STAGING = False
    PRODUCTION = True
    CSRF_ENABLED = True

    pass


class TestingConfig(Config):
    """
    Configuration used for development and testing
    """
    DEBUG = True
    TESTING = True
    PRODUCTION = False
    CSRF_ENABLED = False
    pass
