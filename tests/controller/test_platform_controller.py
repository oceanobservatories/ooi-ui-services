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
        assert rv.data == '[{"id": "2695f343-a741-4aad-8b04-b49d1d4b6396", "name": "TEST1", "site_id": null}, {"id": "408c5200-0b73-460a-b1bc-3b8a792cff73", "name": "TEST3", "site_id": 3}, {"id": "7f4baf3e-15d3-4839-bf3c-75d27e75dbab", "name": "TEST2", "site_id": 2}, {"id": "e2f42ee0-2059-4827-a98e-24ec0c09b0b4", "name": "TEST4", "site_id": 4}]'