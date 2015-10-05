#!/usr/bin/env python
'''

'''

__author__ = 'M@Campbell'

import unittest
import json
import os
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, UserScopeLink, Organization

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class AlfrescoBlueprintTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        db.create_all()
        test_password = 'test'
        Organization.insert_org()
        UserScope.insert_scopes()
        User.insert_user(password=test_password)

        self.client = self.app.test_client(use_cookies=False)

        # set the vars for the connection
        self.cmisUrl =  \
            'https://alfresco.oceanobservatories.org/alfresco/s/api/cmis'
        self.cmisUsername = 'ooinet'
        self.cmisPassword = '75commonLIKEbrown76'
        self.cmisId = 'c161bc66-4f7e-4a4f-b5f2-aac9fbf1d3cd'

        # cmis is tested elsewhere

        from cmislib.model import CmisClient
        client = CmisClient(self.cmisUrl, self.cmisUsername, self.cmisPassword)
        repo = client.getRepository(self.cmisId)

    def badSetUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.basedir = os.path.abspath(os.path.dirname(__file__))

        # set the vars for the connection
        self.cmisUrl = 'http://localhost/alfresco/badsetup'
        self.cmisUsername = 'admin'
        self.cmisPassword = 'admin'
        self.cmisId = 'not-correct-code'

        # cmis is tested elsewhere

        from cmislib.model import CmisClient
        client = CmisClient(self.cmisUrl, self.cmisUsername, self.cmisPassword)
        repo = client.getRepository(self.cmisId)

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

    def test_alfresco_bp(self):
        from cmislib.model import CmisClient
        client = CmisClient(self.cmisUrl, self.cmisUsername, self.cmisPassword)
        repo = client.getRepository(self.cmisId)

        from ooiservices.app import alfresco

        # test unauth
        print '\n\ttesting authenication . . .'
        response = self.client.get('/alfresco/', content_type = 'application/json')
        self.assertTrue(response.status_code == 401)

        # lets auth on the services
        headers = self.get_api_headers('admin', 'test')

        # test redirect (if no trailing slash is provided, will get redirect)
        print '\ttesting redirect . . .'
        response = self.client.get('/alfresco', headers = headers,  content_type = 'application/json')
        self.assertTrue(response.status_code == 301)

        # test redirect (if no trailing slash is provided, will get redirect)
        print '\ttesting not found . . .'
        response = self.client.get('/alfresco/notfound', headers = headers,  content_type = 'application/json')
        self.assertTrue(response.status_code == 404)

        # test root (should respond with alfresco repo informatioN)
        print '\ttesting root . . .'
        response = self.client.get('/alfresco/', headers = headers, content_type = 'application/json')
        self.assertTrue(response.status_code == 200)


