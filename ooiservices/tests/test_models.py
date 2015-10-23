#!/usr/bin/env python
'''
unit testing for the model classes.

'''
__author__ = 'M@Campbell'

import unittest
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import Array, InstrumentDeployment, PlatformDeployment, Stream, \
StreamParameter, User, OperatorEvent, OperatorEventType, Organization

from unittest import skipIf
import os
'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=False)
        Organization.insert_org()

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
        'geo_location': None, 'reference_designator': None, 'start_date': None})

    def test_instrument_deployment(self):
        #Test the json in the object
        instrument_deployment = InstrumentDeployment()
        should_be = {
            'id' :None,
            'depth': None,
            'display_name' : None,
            'end_date' : None,
            'geo_location': None,
            'platform_deployment_id' : None,
            'reference_designator' : None,
            'start_date' : None
        }
        self.assertEquals(instrument_deployment.to_json() , should_be)
    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
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
        self.assertEquals(user.to_json(), {
            'email': None,
            'id': None,
            'user_id': None,
            'active':None,
            'first_name': None,
            'last_name' : None,
            'organization_id' : None,
            'phone_alternate' : None,
            'phone_primary' : None,
            'scopes' : [],
            'role' : None,
            'user_name': None,
            'email_opt_in': None})

    def test_operator_event_type(self):
        #Test the json in the object
        operator_event_type = OperatorEventType()
        self.assertTrue(operator_event_type.to_json() == {'id': None, 'type_name': None, 'type_description': None})

    def test_geometry(self):
        platform_deployment = PlatformDeployment()
        platform_deployment.reference_designator = 'TEST0000'
        platform_deployment.geo_location = 'POINT(-70 40)'
        db.session.add(platform_deployment)
        db.session.commit()
        pd = PlatformDeployment.query.filter(PlatformDeployment.reference_designator=='TEST0000').first()
        self.assertEquals(pd.geojson, {'coordinates': [-70, 40], 'type': 'Point'})
