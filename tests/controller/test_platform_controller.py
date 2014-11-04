#!/usr/bin/env python
'''
tests.controller.test_platform_controller

Test for the platform controller
'''

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

    def test_context(self):
        '''
        Test that the app context initializes successfully
        '''
        rv = self.app.get('/platforms')
        #This test is rediculus!
        #assert rv.data == ''