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
        response = { r['array_code'] : r for r in response }
        assert 'CP' in response

    def test_array_where(self):
        rv = self.app.get('/arrays?array_code=CP')
        response = json.loads(rv.data)

        # Rearrange the response by array_code
        response = { r['array_code'] : r for r in response }
        assert 'CP' in response

        rv = self.app.get('/arrays?array_code=OP')
        response = json.loads(rv.data)

        assert len(response) == 0

    def test_array_get(self):
        rv = self.app.get('/arrays/1')
        response = json.loads(rv.data)

        assert response['id'] == 1
        assert response['array_code'] == 'CP'

        # Assert not found
        rv = self.app.get('/arrays/9000')
        assert rv.status_code == 204