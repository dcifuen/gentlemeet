#-*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
import logging
import random
import string
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import deferred
import httplib2

from ardux.tasks import sync_resources
from flask import redirect, g, session, request, make_response
from flask.helpers import url_for
from flask.templating import render_template
from ardux.models import ResourceDevice
import flask
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import constants
from ardux import app


@app.route('/')
def index():
    user = users.get_current_user()
    if user:
        return redirect(url_for('admin.index'))
        #Force user to login then admin
    return redirect(users.create_login_url(url_for('admin.index')))


@app.route('/_ah/warmup')
def warmup():
    #TODO: Warmup
    return 'Warming Up...'


@app.route('/device/register', methods=['GET', 'POST'])
def device_register():
    device = ResourceDevice(uuid=''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in
        range(5)))
    device.put();
    return flask.jsonify(device.to_dict())


@app.route('/device/sync/<uuid>')
def device_sync(uuid):
    device = ResourceDevice.query(ResourceDevice.uuid == uuid).fetch(1)[0]
    device.last_sync = datetime.datetime.now()
    device.put()
    if device:
        return flask.jsonify(device.to_dict(exclude=('resource_key',)))
    else:
        return 'Device not found', 404


@app.route('/cron/sync/resources')
def resources_sync():
    logging.info("Scheduling sync task")
    deferred.defer(sync_resources)
    return "Scheduling sync task..."


@app.route('/signout')
def sign_out():
    pass


@app.route('/signin')
def sign_in():
# Create a state token to prevent request forgery.
    # Store it in the session for later validation.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for
                    x in xrange(32))
    session['state'] = state
    # Set the Client ID, Token State, and Application Name in the HTML while
    # serving it.
    return render_template('signin.html',
                           CLIENT_ID=constants.OAUTH2_CLIENT_ID,
                           STATE=state,
                           APPLICATION_NAME=constants.SOURCE_APP_NAME)


@app.route('/connect', methods=['POST'])
def connect():
    """Exchange the one-time authorization code for a token and
    store the token in the session."""
    # Ensure that the request is not a forgery and that the user sending
    # this connect request is the expected user.


    if request.args.get('state', '') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        # Normally, the state is a one-time token; however, in this example,
        # we want the user to be able to connect and disconnect
        # without reloading the page.  Thus, for demonstration, we don't
        # implement this best practice.
        # del session['state']

    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # An ID Token is a cryptographically-signed JSON object encoded in base 64.
    # Normally, it is critical that you validate an ID Token before you use it,
    # but since you are communicating directly with Google over an
    # intermediary-free HTTPS channel and using your Client Secret to
    # authenticate yourself to Google, you can be confident that the token you
    # receive really comes from Google and is valid. If your server passes the
    # ID Token to other components of your app, it is extremely important that
    # the other components validate the token before using it.
    gplus_id = credentials.id_token['sub']

    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
        # Store the access token in the session for later use.
    session['credentials'] = credentials
    session['gplus_id'] = gplus_id
    response = make_response(json.dumps('Successfully connected user.', 200))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Revoke current user's token and reset their session."""

    # Only disconnect a connected user.
    credentials = session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del session['credentials']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.before_request
def before_request():
    if users.get_current_user():
        g.url_logout_text = 'Logout'
        g.url_logout = users.create_logout_url(url_for('admin.index'))
    else:
        g.url_logout_text = 'Login'
        g.url_logout = users.create_login_url(url_for('sign_in'))


@app.errorhandler(403)
def page_unauthorized(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_error(e):
    logging.error('500 error: %s', e)
    return render_template('500.html'), 500

