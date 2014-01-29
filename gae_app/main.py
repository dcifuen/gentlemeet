from google.appengine.api import users

from flask.app import Flask
from flask.ext.admin.base import MenuLink
#from settings import get_environment

from settings import get_environment, Config, ProductionConfig, TestingConfig

from werkzeug.debug import DebuggedApplication
from flask_admin import Admin
import logging

flask_app = Flask(__name__)
with flask_app.app_context():
    environment = get_environment()
    #Load settings from the corresponding class
    if environment == Config.ENV_PRODUCTION:
        flask_app.config.from_object(ProductionConfig)
    else:
        flask_app.config.from_object(TestingConfig)
    #If debug then enable
    if flask_app.config['DEBUG']:
        flask_app.debug = True
        app = DebuggedApplication(flask_app, evalex=True)
    app = flask_app
    from google.appengine.ext.deferred import application as deferred_app
    from ardux import admin_views
    from ardux import views
    admin_url = '/admin'

    #Build admin stuff
    admin = Admin(flask_app,
                  name='Ardux',
                  index_view=admin_views.AdminIndex(
                      url=admin_url,
                      name='Home',
                      endpoint='admin',
                  ),
    )
    admin.add_link(MenuLink(
        name='Logout',
        url=users.create_logout_url(admin_url)
    ))

    admin.add_view(admin_views.DevicesView(
        name='Devices',
        endpoint='devices',
    ))

    admin.add_view(admin_views.OAuthView(
        name='Settings',
        endpoint='oauth',
        static_url_path=True
    ))
