from google.appengine.api import users
from ardux.helpers import OAuthHelper
from flask.ext.admin import BaseView, expose
from flask.ext.admin.base import AdminIndexView
from settings import API_KEY, OAUTH_SCOPE, CONSUMER_SECRET
from werkzeug.routing import RequestRedirect
from flask import helpers
from ardux.models import Client
from flask import redirect, request
from gdata.docs.client import DocsClient
from gdata.gauth import AuthorizeRequestToken, AeSave, AeLoad
import logging

REQUEST_TOKEN = 'RequestToken'
ACCESS_TOKEN = 'AccessToken'

class AuthView(BaseView):
    def is_accessible(self):
        if users.is_current_user_admin():
            return True
        else:
            raise RequestRedirect(users.create_login_url(self.url))

class AdminIndex(AuthView,AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('index.html')

class AuthView(AuthView):

    client = DocsClient(source='ArDuX')

    @expose('/')
    def start_oauth2(self):
        redirect_uri = helpers.url_for('oauth.callback_oauth2', _external = True)
        domain = users.get_current_user().email().split('@')[1]
        client = Client.get_by_id(domain)
        if client:
            if client.refresh_token is None:
                oauthHelper = OAuthHelper(redirect_uri, approval_prompt = 'force')
            else:
                oauthHelper = OAuthHelper(redirect_uri)
        else:
            client = Client(id = domain)
            client.put()
            oauthHelper = OAuthHelper(redirect_uri)

        url = oauthHelper.step1_get_authorize_url()

        return redirect("%s&state=%s" % (url, domain))

    @expose('/callback/')
    def callback_oauth2(self):
        redirect_uri = helpers.url_for('oauth.callback_oauth2', _external = True)
        oauthHelper = OAuthHelper(redirect_uri)
        code = request.args.get('code', None)
        domain = users.get_current_user().email().split('@')[1]
        if code:
            credentials = oauthHelper.step2_exchange(code)
            client = Client.get_by_id(domain)
            client.credentials = credentials.to_json()
            if client.refresh_token is None:
                client.refresh_token = credentials.refresh_token
            client.put()

        return redirect(helpers.url_for('oauth.start_oauth1'))

    @expose('/oauth1/')
    def start_oauth1(self):

        oauth_callback_url = helpers.url_for('oauth.callback_oauth1', _external = True)
        logging.info("oauth_callback_url [%s]", oauth_callback_url)

        request_token = self.client.GetOAuthToken(OAUTH_SCOPE, oauth_callback_url, API_KEY,
                                             consumer_secret = CONSUMER_SECRET)

        domain = users.get_current_user().email().split('@')[1]

        AeSave(request_token, REQUEST_TOKEN)

        authorization_url = request_token.generate_authorization_url()
        return redirect(str(authorization_url))

    @expose('/oauth1/callback/')
    def callback_oauth1(self):
        saved_request_token = AeLoad(REQUEST_TOKEN)
        request_token = AuthorizeRequestToken(saved_request_token, request.url)
        access_token = self.client.GetAccessToken(request_token)
        AeSave(access_token, ACCESS_TOKEN)
        return 'Yes'
