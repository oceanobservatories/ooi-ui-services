#!/usr/bin/env python
'''
Tests for log entry API

'''

import unittest
from base64 import b64encode
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope
from ooiservices.app.models import OperatorEvent, OperatorEventType, Organization
from ooiservices.app.models import LogEntry

import json

class TestLogEntries(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        test_username = 'admin'
        test_password = 'test'
        Organization.insert_org()
        User.insert_user(username=test_username, password=test_password, email='admin@oceanobservatories.org')


        OperatorEventType.insert_operator_event_types()

        self.client = self.app.test_client(use_cookies=False)

        UserScope.insert_scopes()

        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)

        db.session.add(admin)
        db.session.commit()

        joe = User.insert_user(username='joe', password='joe', email='joe@oceanobservatories.org')
        bob = User.insert_user(username='bob', password='bob', email='bob@oceanobservatories.org')


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

    def test_get_entries(self):

        headers = self.get_api_headers('admin', 'test')

        org = Organization.query.first()
        org_id = org.id

        admin_user = User.query.first()
        org = Organization.query.first()

        log_entry = LogEntry()
        log_entry.log_entry_type = 'INFO'
        log_entry.entry_title = 'First Entry'
        log_entry.entry_description = 'This is where the description goes'
        log_entry.user_id = admin_user.id
        log_entry.organization_id = org.id
        db.session.add(log_entry)
        db.session.commit()

        # GET /log_entry
        response = self.client.get('/log_entry')
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.data)
        entry = data['log_entries'][0]
        self.assertEquals(entry['entry_title'], log_entry.entry_title)


        # GET /log_entry/:id
        response = self.client.get('/log_entry/%s' % log_entry.id)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.data)
        entry = data
        self.assertEquals(entry['entry_title'], log_entry.entry_title)


        # GET /log_entry?organization_id=:organization_id
        response = self.client.get('/log_entry?organization_id=%s' % org.id)
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.data)
        entry = data['log_entries'][0]
        self.assertEquals(entry['entry_title'], log_entry.entry_title)

        # GET /log_entry?organization_id=90 (404)
        response = self.client.get('/log_entry?organization_id=90')
        self.assertEquals(response.status_code, 204)

        # POST /log_entry
        data = {
            'log_entry_type' : 'INFO',
            'entry_title' : 'Another Entry',
            'entry_description' : "I'm Scotty P, knaw I'm sayin'",
            'organization_id' : org.id
        }
        response = self.client.post('/log_entry', data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        entry_id = data.get('id')

        # GET /log_entry/:id
        response = self.client.get('/log_entry/%s' % entry_id)
        self.assertEquals(response.status_code, 200)

        entry = json.loads(response.data)
        self.assertEquals(entry['entry_title'], data['entry_title'])


        # PUT /log_entry
        data = {
            'log_entry_type' : 'INFO',
            'entry_title' : 'Changed Entry',
            'entry_description' : "I'm Scotty P, knaw I'm sayin'",
            'organization_id' : org.id
        }
        response = self.client.put('/log_entry/%s' % entry_id, data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 200)
        entry = json.loads(response.data)

        self.assertEquals(entry['entry_title'], data['entry_title'])

        # GET /log_entry/:id
        response = self.client.get('/log_entry/%s' % entry_id)
        self.assertEquals(response.status_code, 200)

        entry = json.loads(response.data)
        self.assertEquals(entry['entry_title'], data['entry_title'])

        # DELETE /log_entry/:id
        response = self.client.delete('/log_entry/%s' % entry_id, headers=headers)
        self.assertEquals(response.status_code, 204)

        response = self.client.get('/log_entry/%s' % entry_id)
        self.assertEquals(response.status_code, 204)


    def test_authorizations(self):
        joe_headers = self.get_api_headers('joe', 'joe')
        bob_headers = self.get_api_headers('bob', 'bob')
        admin_headers = self.get_api_headers('admin', 'test')

        # POST /log_entry
        data = {
            'log_entry_type' : 'INFO',
            'entry_title' : 'Another Entry',
            'entry_description' : "I'm Scotty P, knaw I'm sayin'"
        }
        response = self.client.post('/log_entry', data=json.dumps(data), headers=joe_headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        entry_id = data['id']

        # PUT /log_entry UNAUTHORIZED
        data = {
            'log_entry_type' : 'INFO',
            'entry_title' : 'Changed Entry',
            'entry_description' : "I'm Scotty P, knaw I'm sayin'"
        }
        response = self.client.put('/log_entry/%s' % entry_id, data=json.dumps(data), headers=bob_headers)
        self.assertEquals(response.status_code, 401)
        error_message = json.loads(response.data)
        self.assertIn('Unauthorized', error_message['error'])

        # PUT /log_entry
        data = {
            'log_entry_type' : 'INFO',
            'entry_title' : 'Changed Entry',
            'entry_description' : "I'm Scotty P, knaw I'm sayin'"
        }
        response = self.client.put('/log_entry/%s' % entry_id, data=json.dumps(data), headers=admin_headers)
        self.assertEquals(response.status_code, 200)
        
        # DELETE /log_entry UNAUTHORIZED
        response = self.client.delete('/log_entry/%s' % entry_id, headers=bob_headers)
        self.assertEquals(response.status_code, 401)
        
        response = self.client.delete('/log_entry/%s' % entry_id, headers=joe_headers)
        self.assertEquals(response.status_code, 204)
