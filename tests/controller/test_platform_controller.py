#!/usr/bin/env python
'''
tests.controller.test_platform_controller

Test for the platform controller

'''
__author__ = 'Matt Campbell'

import json
from ooiservices.app import app
from tests.services_test_case import ServicesTestCase

class TestPlatformController(ServicesTestCase):
    def setUp(self):
        '''
        Initializes the application
        '''
        ServicesTestCase.setUp(self)
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_listing(self):
        '''
        Test that the app context initializes successfully
        '''
        rv = self.app.get('/platforms')
        response = json.loads(rv.data)
        assert 'id' in response

    def test_empty_response(self):
        rv = self.app.get('/platforms/notreal')
        assert rv.status_code == 204