import os
# Copy this file into secrets.py and set keys, secrets and scopes.

# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here: 
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = "abcsd123"
SESSION_SECRET_KEY = 'abcd1234'

# Google APIs
GOOGLE_APP_ID = 'app id'
GOOGLE_APP_SECRET = 'app secret'

# Facebook auth apis
if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
    FACEBOOK_APP_ID = 'app id'
    FACEBOOK_APP_SECRET = 'app secret'
    FACEBOOK_APP_NAMESPACE = 'namespace'

else:
    FACEBOOK_APP_ID = 'app id'
    FACEBOOK_APP_SECRET = 'app secret'
    FACEBOOK_APP_NAMESPACE = 'namespace'

FACEBOOK_SCOPE = 'user_about_me,publish_actions,user_photos'

# https://dev.twitter.com/apps
TWITTER_CONSUMER_KEY = 'oauth1.0a consumer key'
TWITTER_CONSUMER_SECRET = 'oauth1.0a consumer secret'

# https://foursquare.com/developers/apps
FOURSQUARE_CLIENT_ID = 'client id'
FOURSQUARE_CLIENT_SECRET = 'client secret'

# config that summarizes the above

AUTH_CONFIG = {
    # OAuth 2.0 providers
    'google': (GOOGLE_APP_ID, GOOGLE_APP_SECRET,
               'https://www.googleapis.com/auth/userinfo.profile'),

    'facebook': (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET,
                 FACEBOOK_SCOPE),

    'foursquare': (FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,
                   'authorization_code'),

    # OAuth 1.0 providers don't have scopes
    'twitter': (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),

}
