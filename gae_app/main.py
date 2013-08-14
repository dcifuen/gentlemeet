from ardux.admin_views import AdminIndex
from ardux.middlewares import UsersMiddleware
from flask.app import Flask
from flask.ext.admin.base import MenuLink
from werkzeug.debug import DebuggedApplication
from flask_admin import Admin
from google.appengine.api import users
from flask import helpers
import settings


flask_app = Flask(__name__)
flask_app.config.from_object(settings)

admin = Admin(flask_app, name='ArDuX', index_view=AdminIndex(url='/admin', name='Home'), )
admin.add_link(MenuLink(name='Logout',url = users.create_logout_url('/')))
flask_app.wsgi_app = UsersMiddleware(flask_app.wsgi_app)

if flask_app.config['DEBUG']:
    flask_app.debug = True
    app = DebuggedApplication(flask_app, evalex=True)

app = flask_app

from ardux import admin_views
from ardux import views

#*********** Admin Views *****************
admin.add_view( admin_views.Devices(name = 'Devices' ,endpoint='devices', static_url_path=True))
admin.add_view( admin_views.OAuthView(name = 'Authorize' ,endpoint='oauth', static_url_path=True))

