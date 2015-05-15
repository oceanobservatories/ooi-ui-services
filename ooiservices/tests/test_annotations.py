#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
unit testing for the annotations feature

'''
__author__ = 'M@Campbell'

import unittest
import json
from base64 import b64encode
from flask import url_for, jsonify, g
from ooiservices.app import create_app, db
from ooiservices.app.models import Annotation, User, UserScope, UserScopeLink, Organization
from datetime import datetime

'''
These tests verify the functioning of the api list.
Sample data is inserted, checked, and then removed.

'''

class AnnotationsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_username = 'admin'
        test_password = 'test'
        Organization.insert_org()
        User.insert_user(username=test_username, password=test_password)

        self.client = self.app.test_client(use_cookies=False)
        UserScope.insert_scopes()
        
        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        scope = UserScope.query.filter_by(scope_name='annotate').first()
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

    def test_annotation(self):

        headers = self.get_api_headers('admin', 'test')

        # POST /annotation
        data = {
            'reference_designator' : 'CP02PMCO-WFP01-01-VEL3DK000',
            'start_time' : '2014-04-12T1826Z',
            'end_time' : '2014-04-13T00:00Z',
            'stream_parameter_name': 'vel3d_k_temp_c',
            'stream_name':'vel3d_k_wfp_instrument',
            'description' : '僕にとって、その球が完璧だ。',
            # User is matched by authentication

        }
        response = self.client.post('/annotation', data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 201)


