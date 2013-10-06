from google.appengine.api import users
from ardux.models import Client, User
from ardux.helpers import OAuthDanceHelper
from flask.ext.admin import BaseView, expose
from flask.ext.admin.base import AdminIndexView, expose_plugview
from werkzeug.routing import RequestRedirect
import logging
from flask import abort, redirect, helpers, request
from settings import get_setting


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
        #Force user to login
        raise RequestRedirect(users.create_login_url(self.url))

class AdminIndex(AuthView, AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin_index.html')

class OAuthView(AuthView):

    def is_accessible(self):
        """
        Check that the user is an app engine admin to configure this
        :return: True if the user is admin, raise redirect otherwise
        """
        if users.is_current_user_admin():
            return True
        abort(403)

    @expose('/')
    def index(self):
        #FIXME: Common, use a template
        return '<a href="%s?type=reseller">Click me to authorize ' \
               'as ' \
               'reseller</a><br/><a href="%s?type=target">Click me to ' \
               'authorize as ' \
               'target domain</a>' % (helpers.url_for('oauth'
                                                      '.start_oauth2_dance'), helpers.url_for('oauth.start_oauth2_dance'))

    @expose('/start/')
    def start_oauth2_dance(self):
        login_hint = ''
        scope = ''
        type = request.args.get('type', None)
        client = Client.get_by_id(1)
        if not client:
            #If client does not exist then create an empty one
            client = Client(id = 1)
            client.put()
        #Get the login hint from configuration
        if type == 'reseller':
            approval_prompt = 'auto' if client.reseller_refresh_token else 'force'
            login_hint = get_setting('OAUTH2_RESELLER_DOMAIN_USER')
            scope = get_setting('OAUTH2_RESELLER_SCOPE')
        elif type == 'target':
            approval_prompt = 'auto' if client.target_refresh_token else 'force'
            login_hint = get_setting('OAUTH2_DOMAIN_USER')
            scope = get_setting('OAUTH2_DOMAIN_SCOPE')
        else:
            logging.warn('Type of domain not supported')
            abort(404)
        redirect_uri = helpers.url_for('oauth.oauth_callback',
                                        _external = True)
        oauth_helper = OAuthDanceHelper(redirect_uri, approval_prompt, scope)
        url = oauth_helper.step1_get_authorize_url()
        #TODO: Add a random token to avoid forgery
        return redirect("%s&state=%s&login_hint=%s" % (url, type, login_hint))

    @expose('/callback/')
    def oauth_callback(self):
        code = request.args.get('code', None)
        if code:
            type = request.args.get('state', None)
            redirect_uri = helpers.url_for('oauth.oauth_callback', _external = True)
            oauth_helper = OAuthDanceHelper(redirect_uri)
            credentials = oauth_helper.step2_exchange(code)
            client = Client.get_by_id(1)
            if client:
                if type == 'reseller':
                    client.reseller_credentials = credentials.to_json()
                    if credentials.refresh_token:
                        client.reseller_refresh_token = credentials.refresh_token
                    client.put()
                    return redirect(helpers.url_for('oauth.index'))
                elif type == 'target':
                    client.target_credentials = credentials.to_json()
                    if credentials.refresh_token:
                        client.target_refresh_token = credentials.refresh_token
                    client.put()
                    return redirect(helpers.url_for('oauth.index'))
                else:
                    logging.warn('Type of domain not supported')
                    abort(404)
            else:
                logging.error('No client object, aborting authorization')
                abort(500)
        else:
            logging.error('No code, no authorization')
            abort(500)
