#!/usr/bin/python
# encoding: utf-8
"""
tests.py
"""
import unittest
import base64
import datetime

from google.appengine.ext import testbed, deferred, ndb

from apis import GentleMeetApi
from constants import CHECK_IN
from models import ResourceEvent, CheckInOut


USAGE = """
Path to your sdk must be the first argument. To run type:

$ utrunner.py tests.py path/to/your/appengine/installation

Remember to set environment variable FLASK_CONF to TEST.
Loading configuration depending on the value of
environment variable allows you to add your own
testing configuration in src/ardux/settings.py

"""


class AppEngineFlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Flask apps testing. See: http://flask.pocoo.org/docs/testing/
        from ardux import app
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self._ctx = app.test_request_context()
        self._ctx.push()

        # Setups app engine test bed. See: http://code.google.com/appengine/docs/python/tools/localunittesting.html#Introducing_the_Python_Testing_Utilities
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub(root_path=".")
        self.task_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()
        if getattr(self, '_ctx') and self._ctx is not None:
            self._ctx.pop()
        del self._ctx

    def run_queue_tasks(self, queue='default'):
        api_tasks = self.task_stub.GetTasks(queue)
        while len(api_tasks) >0:
            self.task_stub.FlushQueue(queue)
            for api_task in api_tasks:
                deferred.run(base64.b64decode(api_task['body']))
            api_tasks = self.task_stub.GetTasks(queue)

    def set_current_user(self, email, user_id, is_admin=False):
        self.testbed.setup_env(
            USER_EMAIL=email or '',
            USER_ID=user_id or '',
            USER_IS_ADMIN='1' if is_admin else '0'
        )


class CheckInOutTestCase(AppEngineFlaskTestCase):

    def test_api_check_in(self):
        event_key = ResourceEvent(
            organizer='administrador@eforcers.com.co',
            original_start_date_time=datetime.datetime.now(),
            original_end_date_time=datetime.datetime.now() +
                                   datetime.timedelta(hours=3),
            summary='Test event',
            is_express=False
        ).put()

        gentlemeet_api = GentleMeetApi()
        request = gentlemeet_api.insert_training_session.remote.request_type()
        request.id = event_key.id()
        gentlemeet_api.check_in(request)
        checks = CheckInOut.query().fetch()
        self.assertEqual(1, len(checks), 'Only one check')
        self.assertEqual(checks[0].type, CHECK_IN, 'Should be check in')

        ndb.delete_multi([event_key, checks[0].key])


if __name__ == '__main__':
    unittest.main()
