#!/usr/bin/env python
'''
unit testing for the model classes.

'''
__author__ = 'M@Campbell'

import unittest
from flask import url_for
from app import create_app, db
from app.models import Array, InstrumentDeployment, PlatformDeployment, Stream, \
StreamParameter, User, UserRole, Annotation

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
        test_password = 'test'
        User.insert_user(test_password)
        UserRole.insert_roles()

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
        self.assertTrue(instrument_deployment.to_json() == {'id': None, \
        'depth': None, 'display_name': None, 'end_date': None, 'geo_location': None, \
        'platform_deployment_id': None, 'reference_designator': None, 'start_date': None})

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
        self.assertTrue(user.to_json() == {'email': None, 'id': None, \
        'pass_hash': None, 'user_id': None, 'user_name': None})

    def test_role(self):
        #Test the json in the object
        role = UserRole()
        self.assertTrue(role.to_json() == {'id': None, 'role_name': None})

    def test_annotation(self):
        annotation = Annotation()
        self.assertTrue(annotation.to_json() == {'comment': None, 'created_time': None, \
        'modified_time': None, 'reference_name': None, 'reference_pk_id': None, \
        'reference_type': None, 'title': None, 'user_id': None})

        newAnnotation = annotation.from_json({'comment': 'test', 'created_time': '2015-01-19 10:36:38', \
        'modified_time': '2015-01-19 10:36:38', 'reference_name': 'test', 'reference_pk_id': 1, \
        'reference_type': 'test', 'title': 'test', 'user_id': 1})
        db.session.add(newAnnotation)
        db.session.commit()
        self.assertTrue(db.session.query(Annotation).count() == 1L)