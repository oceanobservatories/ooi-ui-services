#!/usr/bin/env python
'''
Specific testing of routes.

'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from ooiservices.app import create_app, db
from ooiservices.app.models import Organization, User, UserScope


app = create_app('TESTING_CONFIG')
#from flask import url_for
#import flask.ext.whooshalchemy as whooshalchemy
#import datetime as dt
#app.config['WHOOSH_BASE'] = 'ooiservices/whoosh_index'
#whooshalchemy.whoosh_index(app, PlatformDeployment)
'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
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

    def test_organization(self):

        content_type = 'application/json'

        # get all organizations
        response = self.client.get('/organization', content_type=content_type)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        expectation = {u'organizations':[{u'id':1, u'organization_long_name' : None, u'organization_name' : u'RPS ASA', u'image_url':None}]}
        self.assertEquals(data, expectation)

        # Get organization by id
        response = self.client.get('/organization/1', content_type=content_type)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEquals(data, expectation['organizations'][0])

        # Get non-existant organization (bad id value); expect failure
        response = self.client.get('/organization/999', content_type=content_type)
        self.assertEquals(response.status_code, 204)