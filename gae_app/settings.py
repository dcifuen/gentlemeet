"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module, 
           which should be kept out of version control.

"""

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY, OAUTH2_CLIENT_ID, \
    OAUTH2_CLIENT_SECRET


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

    OAUTH2_CLIENT_ID = OAUTH2_CLIENT_ID
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


def get_setting(key):
    """
    Get the value for a setting with the given key, since cache is shared
    between staging and production is necessary to include that in the key too
    :param key: string that represents the setting key
    :return: the value of the setting
    """
    from main import app
    return app.config[key]


