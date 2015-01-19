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
from app import create_app, db
from app.models import User, UserRole, OperatorEvent, OperatorEventType

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
        User.insert_user(test_password)
        UserRole.insert_roles()

        OperatorEventType.insert_operator_event_types()
        OperatorEvent.insert_operator_event()

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

    def test_operator_event_type(self):
        operator_event_type = OperatorEventType()
        operator_event_type.insert_operator_event_types()

        event_type = OperatorEventType.query.filter_by(type_name='INFO').first()
        self.assertTrue(event_type.type_name == 'INFO')

    def test_operator_event_insert(self):
        operator_event = OperatorEvent.query.filter_by(operator_event_type_id=1).first()
        self.assertTrue(operator_event.event_title == 'This is only a test.')

    def test_get_operator_events_by_user(self):
        #Test unauthorized
        response = self.client.get(url_for('main.get_operator_events_by_user', id='1'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        #Test authorized
        response = self.client.get(url_for('main.get_operator_events_by_user', id='1'), headers=self.get_api_headers('admin', 'test'))

        self.assertTrue(response.status_code == 200)

    def test_get_operator_event_types(self):
        #Test unauthorized
        response = self.client.get(url_for('main.get_operator_event_types'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        #Test authorized
        response = self.client.get(url_for('main.get_operator_event_types'), headers=self.get_api_headers('admin', 'test'))

        self.assertTrue(response.status_code == 200)
