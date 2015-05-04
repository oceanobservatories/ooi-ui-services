#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        from sqlalchemy.orm.mapper import configure_mappers
        configure_mappers()
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

    def test_entries_and_comments(self):

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

        # GET /log_entry_comment?log_entry_id=:id
        response = self.client.get('/log_entry_comment?log_entry_id=%s' % entry_id)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEquals(data['log_entry_comments'], [])

        # POST /log_entry_comment
        data = {
            'comment' : u'これもいつか過ぎ去るものです',
            'log_entry_id' : entry_id
        }
        response = self.client.post('/log_entry_comment', data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 200)
        comment = json.loads(response.data)
        self.assertEquals(comment['comment'], data['comment'])
        log_entry_comment_id = comment['id']

        # GET /log_entry_comment?log_entry_id=:id
        response = self.client.get('/log_entry_comment?log_entry_id=%s' % entry_id)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEquals(len(data['log_entry_comments']), 1)

        # PUT /log_entry_comment/:id
        data = {
            'comment' : u'This too shall pass.',
            'log_entry_id' : entry_id
        }
        response = self.client.put('/log_entry_comment/%s' % log_entry_comment_id, data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 200)

        # GET /log_entry_comment/:id
        response = self.client.get('/log_entry_comment/%s' % log_entry_comment_id)
        self.assertEquals(response.status_code, 200)
        comment = json.loads(response.data)
        self.assertEquals(comment['comment'], data['comment'])

        # DELETE /log_entry_comment/:id
        response = self.client.delete('/log_entry_comment/%s' % log_entry_comment_id, headers=headers)
        self.assertEquals(response.status_code, 204)

        # GET /log_entry_comment/:id
        response = self.client.get('/log_entry_comment/%s' % log_entry_comment_id)
        self.assertEquals(response.status_code, 204)

    def test_search(self):
        headers = self.get_api_headers('admin', 'test')
        entries = [
            {
                'log_entry_type' : 'INFO',
                'entry_title' : 'First Entry',
                'entry_description' : "This one is about the sword in the stone."
            },
            {
                'log_entry_type' : 'INFO',
                'entry_title' : 'Second Entry',
                'entry_description' : "A dragon magically appears."
            },
            {
                'log_entry_type' : 'INFO',
                'entry_title' : 'Third Entry',
                'entry_description' : "Japanese Language Lessons"
            },
            {
                'log_entry_type' : 'INFO',
                'entry_title' : 'Last Entry',
                'entry_description' : "It's the end of the world and we know it."
            }
        ]
        # POST /log_entry
        for entry in entries:
            response = self.client.post('/log_entry', data=json.dumps(entry), headers=headers)
            self.assertEquals(response.status_code, 200)

        # GET /log_entry?search=Japanese
        response = self.client.get('/log_entry?search=Japanese')
        self.assertEquals(response.status_code, 200)
        entries = json.loads(response.data)
        self.assertEquals(len(entries['log_entries']), 1)
        
        # GET /log_entry?search=dragon
        response = self.client.get('/log_entry?search=dragon')
        self.assertEquals(response.status_code, 200)
        entries = json.loads(response.data)
        self.assertEquals(len(entries['log_entries']), 1)

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
