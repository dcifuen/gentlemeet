'''
Created on 16/01/2014

@author: Jorge Salcedo
'''
import logging
from webapp2_extras import securecookie
from webapp2_extras.sessions import SessionDict
from secrets import SESSION_KEY
import os
import Cookie
from settings import SESSION_ATTRIBUTES, TOKEN_CONFIG
from webengine.models import User
import time
import webapp2
from webengine.utils import get_app_host


class AuthRemoteService(object):
    def __init__(self, *args, **kwargs):
        #Dummy request for Cloudendpoints
        #TODO: Get current request from endpoint
        from webengine import WSGIWebEngine
        req = webapp2.Request.blank('/', base_url="http://%s" % get_app_host(include_version=False))
        req.app = WSGIWebEngine._instance
        WSGIWebEngine._instance.set_globals(app=WSGIWebEngine._instance, request=req)  # @UndefinedVariable
        
    @classmethod
    def get_user_from_cookie(cls):
        serializer = securecookie.SecureCookieSerializer(SESSION_KEY)
        logging.info(os.environ)
        cookie_string = os.environ.get('HTTP_COOKIE')
        if cookie_string:
            cookie = Cookie.SimpleCookie()
            cookie.load(cookie_string)
            logging.info("Cookie String: %s",cookie_string)
            logging.info("Cookie %s", cookie)
            if "auth" in cookie:
                session = cookie['auth'].value
                session_data = serializer.deserialize('auth', session)
                logging.info("Session data %s", session_data);
                session_dict = SessionDict(cls, data=session_data, new=False)
                logging.info("Session Dict: %s",session_dict)
                if session_dict:
                    session_final = dict(zip(SESSION_ATTRIBUTES, session_dict.get('_user')))
                    _user, _token = cls.validate_token(session_final.get('user_id'), session_final.get('token'),
                                                       token_ts=session_final.get('token_ts'))
                    logging.info("User: %s", _user)
                    logging.info("Token: %s", _token)
                    cls.user = _user
                    cls.token = _token
                else:
                    cls.user = None
            else:
                cls.user = None
        else:
            cls.user = None
    
    @classmethod
    def user_to_dict(cls, user):
        """Returns a dictionary based on a user object.

        Extra attributes to be retrieved must be set in this module's
        configuration.

        :param user:
            User object: an instance the custom user model.
        :returns:
            A dictionary with user data.
        """
        if not user:
            return None

        user_dict = dict((a, getattr(user, a)) for a in [])
        user_dict['user_id'] = user.get_id()
        return user_dict
    
    @classmethod
    def get_user_by_auth_token(cls, user_id, token):
        """Returns a user dict based on user_id and auth token.

        :param user_id:
            User id.
        :param token:
            Authentication token.
        :returns:
            A tuple ``(user_dict, token_timestamp)``. Both values can be None.
            The token timestamp will be None if the user is invalid or it
            is valid but the token requires renewal.
        """
        user, ts = User.get_by_auth_token(user_id, token)
        return cls.user_to_dict(user), ts

    @classmethod
    def validate_token(cls, user_id, token, token_ts=None):
        """Validates a token.

        Tokens are random strings used to authenticate temporarily. They are
        used to validate sessions or service requests.

        :param user_id:
            User id.
        :param token:
            Token to be checked.
        :param token_ts:
            Optional token timestamp used to pre-validate the token age.
        :returns:
            A tuple ``(user_dict, token)``.
        """
        now = int(time.time())
        delete = token_ts and ((now - token_ts) > TOKEN_CONFIG['token_max_age'])
        create = False

        if not delete:
            # Try to fetch the user.
            user, ts = cls.get_user_by_auth_token(user_id, token)
            if user:
                # Now validate the real timestamp.
                delete = (now - ts) > TOKEN_CONFIG['token_max_age']
                create = (now - ts) > TOKEN_CONFIG['token_new_age']

        if delete or create or not user:
            if delete or create:
                # Delete token from db.
                User.delete_auth_token(user_id, token)

                if delete:
                    user = None

            token = None

        return user, token