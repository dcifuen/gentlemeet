import uuid
from ardux.models import ResourceDevice
import flask
from main import app
import os
import sys
from google.appengine.ext import ndb

# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.route('/_ah/warmup')
def warmup():
    sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))
    return 'Warming Up'


@app.route('/device/register', methods=['POST'])
def device_register():
    device = ResourceDevice(uuid = str(uuid.uuid1()))
    if device.uuid is None:
            device.uuid = str()
    device.put();
    return flask.jsonify(device.to_dict())


@app.route('/device/sync/{uuid}', methods=['POST'])
def device_sync(uuid):
    device = ndb.Key(uuid = uuid).get()
    device = ResourceDevice()
    return flask.jsonify(device.to_dict())