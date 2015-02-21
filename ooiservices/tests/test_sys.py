#!/usr/bin/env python
'''
Tests system utilities.

'''
__author__ = "Jim Case"

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization

test_username = 'admin'
test_password = 'test'

class SystemTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(is_test=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=False)
        Organization.insert_org()
        User.insert_user(username=test_username, password=test_password)
        UserScope.insert_scopes()

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

    def test_list_routes(self):
        # Get routes
        response = self.client.get(url_for('main.list_routes'), content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

        data = json.loads(response.data)
        self.assertIn('routes', data)