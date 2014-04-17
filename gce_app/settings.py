"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module, 
           which should be kept out of version control.

"""
import logging
import os

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY


class Config(object):
    """
    Default configuration
    """
    #Production is the
    ENV_PRODUCTION = 'PRODUCTION'
    #Staging is used for testing replicating the same production environment
    ENV_STAGING = 'STAGING'
    #Done sessions cant be modified
    ENV_LOCAL = 'LOCAL'
    ENVIRONMENT_CHOICES = [
        ENV_PRODUCTION,
        ENV_STAGING,
        ENV_LOCAL,
    ]
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

    SOURCE_APP_NAME = 'ArDuX'

    OAUTH2_SCOPE = 'https://www.googleapis.com/auth/calendar'

    OAUTH_SCOPE = ('https://apps-apis.google.com/a/feeds/calendar/resource/',)

    ENDPOINTS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    EMAIL_REGEXP = "^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$"


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
            return Config.ENV_LOCAL
        elif os.environ['SERVER_SOFTWARE'].startswith('Google App Engine/'):
            #For considering an environment staging we assume the version id
            # contains -staging and the URL
            current_version_id = str(os.environ['CURRENT_VERSION_ID']) if (
                'CURRENT_VERSION_ID') in os.environ else ''
            if '-staging' in current_version_id:
                return Config.ENV_STAGING
            #If not local or staging then is production TODO: really?
            return Config.ENV_PRODUCTION
    return Config.ENV_LOCAL