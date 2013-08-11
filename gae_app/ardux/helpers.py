from oauth2client.client import OAuth2WebServerFlow, Credentials
from settings import OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET, OAUTH2_SCOPE
import gdata


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