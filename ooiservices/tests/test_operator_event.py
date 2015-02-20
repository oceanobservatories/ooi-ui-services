#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'Jim Case'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope
from ooiservices.app.models import OperatorEvent, OperatorEventType, Organization

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class OperatorEventTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(is_test=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        test_username = 'admin'
        test_password = 'test'
        User.insert_user(username=test_username, password=test_password)

        OperatorEventType.insert_operator_event_types()

        self.client = self.app.test_client(use_cookies=False)

        UserScope.insert_scopes()

        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)

        db.session.add(admin)
        db.session.commit()


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

        org = Organization(organization_name='Hello')
        org.users
        db.session.add(org)
        db.session.commit()
        org_id = org.id

        # no watches, get watch (/watch/open), expect 204 (no watches currently open)
        response = self.client.get('/watch/open', headers=headers)
        self.assertEquals(response.status_code, 204)

        response = self.client.post('/watch', headers=headers)
        self.assertEquals(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)
        watch_id = data['id']

        # Test [POST] post watch when watch already open; expect failure (405)
        response = self.client.post('/watch', headers=headers)
        self.assertEquals(response.status_code, 405)

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

        #Test [GET] /operator_event/<int:operator_event_id> - 'main.get_operator_event'
        response = self.client.get('/operator_event/1')
        self.assertEquals(response.status_code, 204)

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
        data_event_1 = response.data[:]
        self.assertIn('id', data)
        event_id = data['id']

        #Test [GET] /operator_event/<int:operator_event_id> - 'main.get_operator_event'
        response = self.client.get('/operator_event/%s' % event_id, headers=headers)
        self.assertEquals(response.status_code, 200)

        # Get events for the current watch
        response = self.client.get('/operator_event?watch_id=%s' % watch_id)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEquals(data['operator_events'][0]['id'], event_id)

        # Close the current watch
        response = self.client.put('/watch/%s' % watch_id, headers=headers, data='{}')
        self.assertEquals(response.status_code, 201)

        # watch is closed, get watch (/watch/open), expect 204 (for no watches currently open)
        response = self.client.get('/watch/open', headers=headers)
        self.assertEquals(response.status_code, 204)

        # Try to create an event with no open watches (careful with data here!!)
        response = self.client.post('/operator_event', data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 400)

        #Test [GET] /watch - 'main.get_watches'
        response = self.client.get('/watch', headers=headers)
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/watch?organization_id=%s' % org_id)
        self.assertEquals(response.status_code, 204)

        # Test [GET] non existent watch_id (999)
        response = self.client.get('/watch/999')
        self.assertEquals(response.status_code, 204)

        #Test [GET] /operator_event_type  - 'main.get_operator_event_types'
        response = self.client.get('/operator_event_type')
        self.assertEquals(response.status_code, 200)

        #Test [GET] /operator_event/<int:operator_event_id> - 'main.get_operator_event'
        response = self.client.get('/operator_event/1', headers=headers)
        self.assertEquals(response.status_code, 200)

        #Test [POST] /operator_event - 'main.post_operator_event'
        # Post operator_event with data={}
        response = self.client.post('/operator_event', data='{}', headers=headers)
        self.assertEquals(response.status_code, 400)



