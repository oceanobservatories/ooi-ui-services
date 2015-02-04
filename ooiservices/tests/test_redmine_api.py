#!/usr/bin/env python
'''
Unit testing for the Redmine API

'''

from ooiservices.app import create_app
from ooiservices.app.redmine.routes import redmine_login
import unittest
from unittest import skipIf
import os
import json

'''
These tests verify the functionality of the Redmine api list.

'''

PROJECT = 'ooi-ui-api-testing'


@skipIf(not os.getenv('CI', True), 'Skip if testing from Travis CI.')
class RedmineTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        self.app_context.pop()

    def get_api_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_read_redmine_issue(self):
        rv = self.client.get('redmine/ticket/id/?id=2290')
        self.assertTrue(rv.status_code == 200)

    def test_read_redmine_issues(self):
        rv = self.client.get('redmine/ticket/?project=' + PROJECT)
        self.assertTrue(rv.status_code == 200)

    def test_create_redmine_ticket(self):
        rv = self.client.post('redmine/ticket',
                              headers=self.get_api_headers(),
                              data=json.dumps({'project': PROJECT, 'subject': 'Test Issue 2'}))
        self.assertTrue(rv.status_code == 201)

    def test_update_redmine_ticket(self):
        redmine = redmine_login()
        project = redmine.project.get(PROJECT).refresh()

        rv = self.client.post('redmine/ticket/id',
                              headers=self.get_api_headers(),
                              data=json.dumps({'resource_id': 2290, 'project_id': project.id, 'subject': 'Test Update', 'notes': 'This is a test'}))
        self.assertTrue(rv.status_code == 201)
