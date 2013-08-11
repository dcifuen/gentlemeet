from ardux.helpers import OAuthHelper
from main import app
from google.appengine.api import users
from flask import redirect
from flask.views import View
from flask import helpers
from ardux.models import Client
import logging

# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

