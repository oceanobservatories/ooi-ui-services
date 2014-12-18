#!/usr/bin/env python
'''
tests.controller.test_instrument_deployment.py

Test for the platform controller
'''

__author__ = 'Matt Campbell'

import json
from ooiservices.app import app
from tests.services_test_case import ServicesTestCase

class TestInstrumentDeplymentController(ServicesTestCase):
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
        rv = self.app.get('/instrument_deployments')
        assert rv.status_code == 200

    def test_empty_response(self):
        rv = self.app.get('/instrument_deplyments/notreal')
        assert rv.status_code == 204