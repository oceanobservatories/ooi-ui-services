#!/usr/bin/env python
'''
unit testing for the model classes.

'''
__author__ = 'M@Campbell'

import unittest
from ooiservices.app import create_app, db
from ooiservices.app.models import Array, User, OperatorEventType, Organization

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
        self.assertTrue(array.to_json() == {'id': None, 'array_code': None,
                                            'array_name': None, 'description': None, 'display_name': None,
                                            'geo_location': None})

    def test_user(self):
        #Test the json in the object
        user = User()
        self.assertEquals(user.to_json(), {
            'email': None,
            'id': None,
            'user_id': None,
            'active':None,
            'first_name': None,
            'last_name': None,
            'organization_id': None,
            'phone_alternate': None,
            'phone_primary': None,
            'scopes': [],
            'role': None,
            'user_name': None,
            'email_opt_in': None,
            'other_organization' : None,
            'vocation' : None,
            'country' : None,
            'state' : None,
            'api_user_name' : None,
            'api_user_token' : None
            })

    def test_operator_event_type(self):
        #Test the json in the object
        operator_event_type = OperatorEventType()
        self.assertTrue(operator_event_type.to_json() == {'id': None, 'type_name': None, 'type_description': None})
