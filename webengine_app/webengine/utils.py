'''
Created on 21/01/2014

@author: Jorge Salcedo
'''
import json
import datetime
import calendar
import logging
from google.appengine.api.app_identity import app_identity
from webengine.models import User
import os


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj.utcoffset() is not None:
                obj = obj - obj.utcoffset()
            encoded_object = int(
                calendar.timegm(obj.timetuple()) * 1000 +
                obj.microsecond / 1000
            )
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        
        return encoded_object
        

def build_login_wrapper(func, roles=[User.ROLE_USER], *args, **kwargs):
    def check_login(self, *args, **kwargs):
        auth = self.auth
        user = auth.get_user_by_session()
        if not auth.get_user_by_session():
            self.session['after_login'] = self.request.path
            self.redirect(self.uri_for('login'))
        else:
            for role in roles:
                if role in user['roles']:
                    return func(self, *args, **kwargs)
            self.abort(401)  
    return check_login


def get_app_host(include_version=True):
    host = app_identity.get_default_version_hostname()
    server = os.environ.get('SERVER_SOFTWARE', '')
    version = os.environ.get('CURRENT_VERSION_ID', '.').split('.')[0]
    if version and include_version and not server.startswith('Dev'):
        host = '%s-dot-%s' % (version, host)
    return host



