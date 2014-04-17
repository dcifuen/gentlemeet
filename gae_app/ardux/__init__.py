from google.appengine.api import users
from ardux.utils import CustomJSONEncoder

from flask.app import Flask
from flask.ext.admin.base import MenuLink

from settings import ProductionConfig, TestingConfig

from werkzeug.debug import DebuggedApplication
from flask_admin import Admin
import constants
import os


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

flask_app = Flask(__name__)
flask_app.json_encoder = CustomJSONEncoder
with flask_app.app_context():
    environment = get_environment()
    #Load settings from the corresponding class
    if environment == constants.ENV_PRODUCTION:
        flask_app.config.from_object(ProductionConfig)
    else:
        flask_app.config.from_object(TestingConfig)
    #If debug then enable
    if flask_app.config['DEBUG']:
        flask_app.debug = True
        app = DebuggedApplication(flask_app, evalex=True)
    app = flask_app
    from google.appengine.ext.deferred import application as deferred_app
    import admin_views
    import views

    admin_url = '/admin'

    #Build admin stuff
    admin = Admin(flask_app,
                  name='GentleMeet',
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
