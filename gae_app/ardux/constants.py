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

OAUTH2_CLIENT_ID = '233923764866.apps.googleusercontent.com'

#Model constants
TYPE_PHYSICAL = 'PHYSICAL'
TYPE_WEB = 'WEB'
DEVICE_CHOICES = [
    TYPE_PHYSICAL,
    TYPE_WEB,

]

#TODO: Refactor as Fysom states
STATE_REGISTERED = 'REGISTERED'
STATE_ACTIVE = 'ACTIVE'
STATE_INACTIVE = 'INACTIVE'
DEVICE_STATE_CHOICES = [
    STATE_REGISTERED,
    STATE_ACTIVE,
    STATE_INACTIVE,
]

STATE_SCHEDULED = 'SCHEDULED'
STATE_IN_PROGRESS = 'IN_PROGRESS'
STATE_FINISHED = 'FINISHED'
STATE_CANCELLED = 'CANCELLED'

EVENT_STATE_CHOICES = [
    STATE_SCHEDULED,
    STATE_IN_PROGRESS,
    STATE_FINISHED,
    STATE_CANCELLED,
]

CHECK_IN = 'IN'
CHECK_OUT = 'OUT'
CHECK_CHOICES = [
    CHECK_IN,
    CHECK_OUT,
]

EARLY_CHECK_IN_MINUTES = 5

QUICK_ADD_MINUTES = 30

QUICK_ADD_TITLE = 'Quick %s Meeting' % SOURCE_APP_NAME

