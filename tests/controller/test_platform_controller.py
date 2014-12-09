#!/usr/bin/env python
'''
tests.controller.test_platform_controller

Test for the platform controller
'''
import json
from ooiservices import app
from tests.services_test_case import ServicesTestCase

class TestPlatformController(ServicesTestCase):
    def setUp(self):
        ServicesTestCase.setUp(self)
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_valid_response(self):
        '''
        Test fails when the response is not proper JSON or is improperly formatted
        '''
        rv = self.app.get('/platforms')
        data = json.loads(rv.data)

        assert 'id' in data[0]
        assert 'platform_id' in data[0]
        assert 'name' in data[0]

    def test_invalid_response(self):

        rv = self.app.get('/platforms?id=notreal')
        assert rv.status_code == 204

    def test_failed_response(self):
        mock_something()

        rv = self.app.get('/platforms?id=notreal')
        assert rv.status_code == 500