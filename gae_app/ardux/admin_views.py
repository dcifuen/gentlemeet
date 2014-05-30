import logging

from google.appengine.api import users

from models import Client, ResourceDevice
from helpers import OAuthDanceHelper
from flask.ext.admin import BaseView, expose
from flask.ext.admin.base import AdminIndexView
from werkzeug.routing import RequestRedirect
from flask import abort, redirect, helpers, request
import constants


class AuthView(BaseView):
    def is_accessible(self):
        """
        By default check that the user is authenticated against GAE, has the
        is staff flag and belongs to the Eforcers team or a valid test domain
        :return: True if is a
        """
        user = users.get_current_user()
        if user:
            return True
        # Force user to login
        raise RequestRedirect(users.create_login_url(self.url))


class AdminIndex(AuthView, AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin_index.html')


class DevicesView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin_devices.html')

    @expose('/add/')
    def device_add(self):
        return self.render('admin_device.html', device=ResourceDevice())

    @expose('/<uuid>/')
    def device_edit(self, uuid):
        device = ResourceDevice.get_by_uuid(uuid)
        if device:
            return self.render('admin_device.html', device=device)
        else:
            abort(404)


class OAuthView(AuthView):
    def is_accessible(self):
        """
        Check that the user is an app engine admin to configure this
        :return: True if the user is admin, raise redirect otherwise
        """

        if users.get_current_user():
            return True
        else:
            redirect(users.create_login_url(request.full_path))

    @expose('/')
    def index(self):
        # FIXME: Common, use a template
        return '<a href="%s">Click me to authorize</a>' % (
        helpers.url_for('oauth.start_oauth2_dance'))

    @expose('/start/')
    def start_oauth2_dance(self):
        login_hint = ''
        scope = ''
        client = Client.get_by_id(1)
        if not client:
            # If client does not exist then create an empty one
            client = Client(id=1)
            client.installer_user = users.get_current_user().email()
            client.put()
        # Get the login hint from configuration
        approval_prompt = 'auto' if client.refresh_token else 'force'
        scope = constants.OAUTH2_SCOPE
        redirect_uri = helpers.url_for('oauth.oauth_callback',
                                       _external=True)
        oauth_helper = OAuthDanceHelper(redirect_uri, approval_prompt, scope)
        url = oauth_helper.step1_get_authorize_url()
        #TODO: Add a random token to avoid forgery
        return redirect(url)

    @expose('/callback/')
    def oauth_callback(self):
        code = request.args.get('code', None)
        if code:
            redirect_uri = helpers.url_for('oauth.oauth_callback',
                                           _external=True)
            oauth_helper = OAuthDanceHelper(redirect_uri)
            credentials = oauth_helper.step2_exchange(code)
            client = Client.get_by_id(1)
            if client:
                client.credentials = credentials.to_json()
                if credentials.refresh_token:
                    client.refresh_token = credentials.refresh_token
                client.put()
                return redirect(helpers.url_for('oauth.index'))
            else:
                logging.error('No client object, aborting authorization')
                abort(500)
        else:
            logging.error('No code, no authorization')
            abort(500)
