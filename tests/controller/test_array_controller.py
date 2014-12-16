#!/usr/bin/env python
'''
tests.controller.test_array_controller

Test for the array controller
'''
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
        rv = self.app.get('/arrays')
        response = json.loads(rv.data)

        # Rearrange the response by array_code
        response = { r['id'] : r for r in response }
        assert 'CP' in response

    def test_array_list(self):
        rv = self.app.get('/arrays')
        response = json.loads(rv.data)

        # Rearrange the response by array_code
        response = { r['id'] : r for r in response }
        assert 'CP' in response

    def test_array_get(self):
        rv = self.app.get('/arrays/CP')
        response = json.loads(rv.data)

        assert response['id'] == 'CP'

        # Assert not found
        rv = self.app.get('/arrays/9000')
        assert rv.status_code == 204