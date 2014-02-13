#-*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
import logging
from google.appengine.ext import deferred
from google.appengine.api import users
from ardux.tasks import sync_resources

from flask import current_app as app, abort
from flask import redirect, g
from flask.helpers import url_for
from flask.templating import render_template
from models import  User
from settings import get_setting
from ardux.models import ResourceDevice
import random
import string
import flask
import datetime

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


@app.route('/device/register', methods=['GET'])
def device_register():
    device = ResourceDevice(uuid=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(5)))
    device.put();
    return flask.jsonify(device.to_dict())


@app.route('/device/sync/<uuid>')
def device_sync(uuid):
    device = ResourceDevice.query(ResourceDevice.uuid == uuid).fetch(1)[0]
    device.last_sync = datetime.datetime.now()
    device.put()
    if device:
        return flask.jsonify(device.to_dict())
    else:
        return 'Device not found', 404


@app.route('/cron/sync/resources')
def resources_sync():
    logging.info("Scheduling sync task")
    deferred.defer(sync_resources)
    return "Scheduling sync task..."


@app.before_request
def before_request():
    if users.get_current_user():
        g.url_logout_text = 'Logout'
        g.url_logout = users.create_logout_url(url_for('admin.index'))
    else:
        g.url_logout_text = 'Login'
        g.url_logout = users.create_login_url(url_for('admin.index'))

@app.errorhandler(403)
def page_unauthorized(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_error(e):
    logging.error('500 error %s', e)
    return render_template('500.html'), 500

