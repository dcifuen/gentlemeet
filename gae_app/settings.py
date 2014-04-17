"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module, 
           which should be kept out of version control.

"""
import os
import constants

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY


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


def get_environment():
    """
    Returns the environment based on the OS variable, server name and app id
    :return: The current environment that the app is running on
    """
    # Auto-set settings object based on App Engine dev environ
    if 'SERVER_SOFTWARE' in os.environ:
        if os.environ['SERVER_SOFTWARE'].startswith('Dev'):
            return constants.ENV_LOCAL
        elif os.environ['SERVER_SOFTWARE'].startswith('Google App Engine/'):
            #For considering an environment staging we assume the version id
            # contains -staging and the URL
            current_version_id = str(os.environ['CURRENT_VERSION_ID']) if (
                'CURRENT_VERSION_ID') in os.environ else ''
            if '-staging' in current_version_id:
                return constants.ENV_STAGING
            #If not local or staging then is production TODO: really?
            return constants.ENV_PRODUCTION
    return constants.ENV_LOCAL