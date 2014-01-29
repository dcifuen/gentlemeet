import sys
import os
sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))
import SocketServer
import logging
from logging.handlers import TimedRotatingFileHandler
from threading import Thread
from flask import Flask
from flask.ext.admin.base import Admin

#SERVER = "PRODUCTION"
SERVER = "DEVELOPMENT"

class FlaskThread(Thread):
    def run(self):
        app = Flask(__name__)
        with app.app_context():
            admin_url = '/admin'
            from ardux import admin_views
            from ardux import views

            #Build admin stuff
            admin = Admin(app,
                          name='Ardux',
                          index_view=admin_views.AdminIndex(
                              url=admin_url,
                              name='Home',
                              endpoint='admin',
                          ),
            )
            app.run(host='0.0.0.0', port=8888)



class DeviceThread(Thread):
    def run(self):
        from ardux.device_handler import DeviceHandler
        HOST, PORT = "0.0.0.0", 6543
        server = SocketServer.TCPServer((HOST, PORT), DeviceHandler)
        server.serve_forever()

if __name__ == '__main__':
    threads = []
    if SERVER == 'PRODUCTION':
        log_handler = TimedRotatingFileHandler(filename='logs/console.log', when='midnight', backupCount=30)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(log_handler)
    device_thread = DeviceThread()
    flask_thread = FlaskThread()
    device_thread.start()
    flask_thread.start()
    threads.append(device_thread)
    threads.append(flask_thread)
    for t in threads:
        t.join()
