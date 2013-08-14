from google.appengine.api import users
from google.appengine.ext import ndb
from ardux.models import User

class UsersMiddleware(object):
    """WSGI middleware to create new users in DataStore
    """
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        user = users.get_current_user()
        db_user = ndb.Key(User,user.email()).get()
        if not db_user:
            db_user = User(id = user.email())
            db_user.is_admin = users.is_current_user_admin()
            db_user.put()
        return self.app(environ, start_response)