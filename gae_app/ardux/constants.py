SOURCE_APP_NAME = 'GentleMeet'

#Environment related constants
#Production is the final environment where the app will run
ENV_PRODUCTION = 'PRODUCTION'
#Staging is used for testing replicating the same production environment
ENV_STAGING = 'STAGING'
#Done sessions cant be modified
ENV_LOCAL = 'LOCAL'
ENVIRONMENT_CHOICES = [
    ENV_PRODUCTION,
    ENV_STAGING,
    ENV_LOCAL,
]

#Formats and regexps
ENDPOINTS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

CALENDAR_DATE_TIME = "%Y-%m-%dT%H:%M:%S.%f%z"

EMAIL_REGEXP = "^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$"

#OAuth scope
OAUTH2_SCOPE = 'https://www.googleapis.com/auth/calendar ' \
               'https://apps-apis.google.com/a/feeds/calendar/resource/'

#Model constants
TYPE_PHYSICAL = 'PHYSICAL'
TYPE_WEB = 'WEB'
TYPE_CHOICES = [
    TYPE_PHYSICAL,
    TYPE_WEB,
]

STATE_REGISTERED = 'REGISTERED'
STATE_ACTIVE = 'ACTIVE'
STATE_INACTIVE = 'INACTIVE'
STATE_CHOICES = [
    STATE_REGISTERED,
    STATE_ACTIVE,
    STATE_INACTIVE,
]

TYPE_IN = 'IN'
TYPE_OUT = 'OUT'
TYPE_CHOICES = [
    TYPE_IN,
    TYPE_OUT,
]

OAUTH2_CLIENT_ID = '233923764866.apps.googleusercontent.com'