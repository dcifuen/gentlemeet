#-*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
import logging
import uuid
from ardux.models import Device

from flask import current_app as app
from flask import redirect
from flask.helpers import url_for
from flask.templating import render_template


@app.route('/')
def index():
    device = Device()
    device.name = "Casa"
    device.uuid = str(uuid.uuid4())
    logging.info("Before put")
    device.put()
    logging.info("After put")
    return redirect(url_for('admin.index'))

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

