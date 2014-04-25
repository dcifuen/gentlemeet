from endpoints import api_config
from secrets import *

ENDPOINTS_AUTH_CONFIG = api_config.ApiAuth(allow_cookie_auth=True)

USER_ATTRS = {
    'facebook': {
        'id': lambda id: ('avatar_url',
                          'http://graph.facebook.com/{0}/picture?type=large'.format(id)),
        'name': 'name',
        'link': 'link'
    },
    'google': {
        'picture': 'avatar_url',
        'name': 'name',
        'profile': 'link'
    },
    'twitter': {
        'profile_image_url': 'avatar_url',
        'screen_name': 'name',
        'link': 'link'
    },
}


# webapp2 config
APP_CONFIG = {
    'webapp2_extras.sessions': {
        'cookie_name': '_simpleauth_sess',
        'secret_key': SESSION_KEY
    },
    'webapp2_extras.auth': {
        'user_model': 'webengine.models.User',
        'user_attributes': ['name', 'roles']

    }
}

TOKEN_CONFIG = {
    'token_max_age': 86400 * 7 * 3,
    'token_new_age': 86400,
    'token_cache_age': 3600,
}

SESSION_ATTRIBUTES = ['user_id', 'remember',
                      'token', 'token_ts', 'cache_ts', 'roles']

APPS = [
    'test'
]
