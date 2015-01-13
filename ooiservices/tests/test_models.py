#!/usr/bin/env python
'''
unit testing for the model classes.

'''
__author__ = 'M.Campbell'

import unittest
from flask import url_for
from app import create_app, db
from app.models import Array, InstrumentDeployment, PlatformDeployment, Stream, \
StreamParameter, User

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_array(self):
        #Test the json in the object
        array = Array()
        self.assertTrue(array.to_json() == {'id': None, 'array_code': None, \
        'array_name': None, 'description': None, 'display_name': None, \
        'geo_location': None})

    def test_platform_deployment(self):
        #Test the json in the object
        platform_deployment = PlatformDeployment()
        self.assertTrue(platform_deployment.to_json() == {'id': None, \
        'array_id': None, 'display_name': None, 'end_date': None, \
        'geo_location': None, 'ref_designator': None, 'start_date': None})

    def test_instrument_deployment(self):
        #Test the json in the object
        instrument_deployment = InstrumentDeployment()
        self.assertTrue(instrument_deployment.to_json() == {'id': None, \
        'depth': None, 'display_name': None, 'end_date': None, 'geo_location': None, \
        'platform_deployment_id': None, 'ref_designator': None, 'start_date': None})

    def test_stream(self):
        #Test the json in the object
        stream = Stream()
        self.assertTrue(stream.to_json() == {'id': None, 'description': None, \
        'instrument_id': None, 'stream_name': None})

    def test_parameter(self):
        #Test the json in the object
        stream_param = StreamParameter()
        self.assertTrue(stream_param.to_json() == {'id': None, 'data_type': None, \
        'long_name': None, 'parameter_name': None, 'short_name': None, \
        'standard_name': None, 'units': None})

    def test_user(self):
        #Test the json in the object
        user = User()
        self.assertTrue(user.to_json() == {'email': None, 'id': None,\
        'pass_hash': None, 'user_id': None, 'username': None})