#!/usr/bin/env python
'''
tests.controller.test_platform_controller

Test for the platform controller
'''
import json
from ooiservices.app import app
from tests.services_test_case import ServicesTestCase
import unittest

@unittest.skip("Shortcut isn't using the platform controller like it should")
class TestPlatformController(ServicesTestCase):
    def setUp(self):
        '''
        Initializes the application
        '''
        ServicesTestCase.setUp(self)
        app.config['TESTING'] = True
        self.app = app.test_client()
    
    def test_platform_listing(self):
        '''
        Test that the app context initializes successfully
        '''
        rv = self.app.get('/platforms')
        json.loads(rv.data) # Assert data is JSON
        with open('tests/controller/expected_platforms.json', 'r') as f:
            expected = f.read()

        assert expected == rv.data

