#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'Jim Case'

import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, OperatorEvent, OperatorEventType

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class OperatorEventTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_password = 'test'
        User.insert_user(password=test_password)

        OperatorEventType.insert_operator_event_types()

        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_operator_framework(self):
        # Create a new watch
        headers = self.get_api_headers('admin', 'test')
        response = self.client.post('/watch', headers=headers)
        self.assertEquals(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        watch_id = data['id']

        # Verify watch exists
        response = self.client.get('/watch/user', headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        watch = data['watches'][0]
        self.assertEquals(watch['id'], watch_id)

        # Get open watches
        response = self.client.get('/watch/open', headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEquals(data['id'], watch_id)

        # Create a new operator event
        data = {
            'operator_event_type_id' : 1,
            'event_title' : 'Event Title',
            'event_comment' : 'Event Comment'
        }

        # Create a new operator event
        response = self.client.get('/operator_event', headers=headers)
        self.assertEquals(response.status_code, 204)
        response = self.client.post('/operator_event', data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        event_id = data['id']

        # Get events for the current watch
        response = self.client.get('/operator_event?watch_id=%s' % watch_id)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEquals(data['operator_events'][0]['id'], event_id)

        # Close the current watch
        response = self.client.put('/watch/%s' % watch_id, headers=headers, data='{}')
        self.assertEquals(response.status_code, 201)

        # Try to create an event with no open watch
        response = self.client.post('/operator_event', data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 400)

