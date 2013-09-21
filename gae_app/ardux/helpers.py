from oauth2client.client import OAuth2WebServerFlow, Credentials
from settings import OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, OAUTH2_SCOPE
import gdata
from main import app

class OAuthHelper(object):
    """ OAuth dance helper class"""
    flow = None

    def __init__(self, redirect_uri='', approval_prompt = 'auto'):

        self.flow = OAuth2WebServerFlow(client_id=OAUTH2_CLIENT_ID,
                                        client_secret=OAUTH2_CLIENT_SECRET,
                                        scope=OAUTH2_SCOPE,
                                        redirect_uri=redirect_uri,
                                        approval_prompt = approval_prompt)

    def step1_get_authorize_url(self):
        return self.flow.step1_get_authorize_url()

    def step2_exchange(self,code):
        return self.flow.step2_exchange(code)

    def get_credentials(self, credentials_json):
        return Credentials.new_from_json(credentials_json)


class CalendarResourcesHelper(object):
    def __init__(self,domain):
        self.client = gdata.calendar_resource.client.CalendarResourceClient(source=app.config['SOURCE_APP_NAME'],domain=domain)
        self.client.http_client.debug = DEBUG
        access_token = gdata.gauth.AeLoad(ACCESS_TOKEN)
        self.client.http_client.debug = False
        self.client.auth_token = gdata.gauth.OAuthHmacToken(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'],
                                                       access_token.token, access_token.token_secret,
                                                       gdata.gauth.ACCESS_TOKEN, next=None, verifier=None)


    def setup_token(self):
        access_token = gdata.gauth.AeLoad(ACCESS_TOKEN)
        self.client.http_client.debug = False
        self.client.auth_token = gdata.gauth.OAuthHmacToken(CONSUMER_KEY, CONSUMER_SECRET,
                                                       access_token.token, access_token.token_secret,
                                                       gdata.gauth.ACCESS_TOKEN, next=None, verifier=None)

    def get_all_resources(self):
        return self.client.GetResourceFeed()
