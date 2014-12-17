#!/usr/bin/env python
'''
tests.controller.test_array_controller

Test for the array controller
'''

__author__ = 'Matt Campbell'

import json
from ooiservices import app
from tests.services_test_case import ServicesTestCase

class TestArrayController(ServicesTestCase):
    def setUp(self):
        ServicesTestCase.setUp(self)
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_valid_response(self):
        '''
        Test fails when the response is not proper JSON or is improperly formatted
        '''
        rv = self.app.get('/array')
        data = json.loads(rv.data)

        assert 'id' in data[0]

    def test_invalid_response(self):
        rv = self.app.get('/array/notreal')
        assert rv.status_code == 204