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
        base_doc = '[{"site_id": 1, "id": "1", "name": "TEST1"}, {"site_id": 2, "id": "2", "name": "TEST2"}]'
        rv = self.app.get('/platforms')
        assert base_doc == rv.data