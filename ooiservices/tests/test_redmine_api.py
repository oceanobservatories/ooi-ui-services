#!/usr/bin/env python
'''
Unit testing for the Redmine API

'''

from ooiservices.app import create_app, db
from ooiservices.app.redmine.routes import redmine_login
from ooiservices.app.models import User, UserScope, UserScopeLink
import unittest
from unittest import skipIf
import os
import json
from base64 import b64encode

'''
These tests verify the functionality of the Redmine api list.

'''

PROJECT = 'ooi-ui-api-testing'


@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class RedmineTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_username = 'admin'
        test_password = 'test'
        User.insert_user(username=test_username, password=test_password)

        self.client = self.app.test_client(use_cookies=False)

        UserScope.insert_scopes()

        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='redmine').first()
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

    def test_read_redmine_issue(self):
        rv = self.client.get('redmine/ticket/id/?id=2290',
                             headers=self.get_api_headers('admin', 'test'))
        self.assertTrue(rv.status_code == 200)

    def test_read_redmine_issues(self):
        rv = self.client.get('redmine/ticket/?project=' + PROJECT,
                             headers=self.get_api_headers('admin', 'test'))
        self.assertTrue(rv.status_code == 200)

    def test_read_redmine_users(self):
        rv = self.client.get('redmine/users/?project=' + PROJECT,
                             headers=self.get_api_headers('admin', 'test'))
        self.assertTrue(rv.status_code == 200)

    def test_create_redmine_ticket(self):
        rv = self.client.post('redmine/ticket',
                              headers=self.get_api_headers('admin', 'test'),
                              data=json.dumps({'project_id': PROJECT,
                                               'subject': 'Test Issue 2',
                                               'due_date': '2015-04-15',
                                               'description': 'Get this work done ASAP',
                                               'priority_id': 1}))
                                               # 'assigned_to_id': 1}))

        self.assertTrue(rv.status_code == 201)

    def test_update_redmine_ticket(self):
        redmine = redmine_login()
        project = redmine.project.get(PROJECT).refresh()

        rv = self.client.post('redmine/ticket/id',
                              headers=self.get_api_headers('admin', 'test'),
                              data=json.dumps({'resource_id': 2290,
                                               'project_id': project.id,
                                               'subject': 'Testing Update',
                                               'notes': 'This is simply a test'}))
        self.assertTrue(rv.status_code == 201)
