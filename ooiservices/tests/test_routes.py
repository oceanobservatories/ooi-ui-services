#!/usr/bin/env python
'''
Specific testing of routes.

'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import PlatformDeployment, InstrumentDeployment, Stream, StreamParameter, VocabNames
from ooiservices.app.models import Organization, User, UserScope
import flask.ext.whooshalchemy as whooshalchemy
import datetime as dt

app = create_app('TESTING_CONFIG')
app.config['WHOOSH_BASE'] = 'ooiservices/whoosh_index'
whooshalchemy.whoosh_index(app, PlatformDeployment)
'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_username = 'admin'
        test_password = 'test'
        Organization.insert_org()
        User.insert_user(username=test_username, password=test_password)

        self.client = self.app.test_client(use_cookies=False)

        UserScope.insert_scopes()

        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    #Test [GET] /platform_deployments - 'main.get_platform_deployments'
    def test_route_get_platform_deployments(self):

        #Create a sample data set.
        platform_ref = PlatformDeployment(reference_designator='CE01ISSM')
        db.session.add(platform_ref)
        db.session.commit()

        platform_ref2 = PlatformDeployment(reference_designator='GS05MOAS-PG002')
        db.session.add(platform_ref2)
        db.session.commit()

        content_type = 'application/json'
        response = self.client.get(url_for('main.get_platform_deployments'), content_type = content_type)
        all_data = response.data
        expected_data = json.loads(response.data)
        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_platform_deployment', id='CE01ISSM'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        response = self.client.get('/platform_deployments?array_id=3')
        self.assertTrue(response.status_code == 200)

        response = self.client.get('/platform_deployments?array_id=999')
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        no_data = {'platform_deployments': []}
        self.assertTrue(data == no_data)

        response = self.client.get('/platform_deployments?ref_id="GS05MOAS-PG002"')
        self.assertTrue(response.status_code == 200)

        # search for not existent platform; all platforms returned
        response = self.client.get('/platform_deployments?ref_id="badthing"')
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue(data == expected_data)

        response = self.client.get('/platform_deployments?search="CE01ISSM"')
        self.assertTrue(response.status_code == 200)


    # Test [GET] /parameters - 'main.get_parameters'
    def test_get_parameters(self):
        '''
        parameter(id=preferred_timestamp): {
                                              "data_type": null,
                                              "id": 1,
                                              "long_name": null,
                                              "parameter_name": "preferred_timestamp",
                                              "short_name": null,
                                              "standard_name": null,
                                              "units": null
                                            }
        '''
        content_type = 'application/json'

        #Create a sample data set
        parameter_name = StreamParameter(stream_parameter_name='preferred_timestamp')
        db.session.add(parameter_name)
        db.session.commit()

        # Get all parameters
        response = self.client.get(url_for('main.get_parameters'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        # Get parameter
        response = self.client.get(url_for('main.get_parameter', id='preferred_timestamp'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

    def test_organization(self):

        content_type = 'application/json'

        # get all organizations
        response = self.client.get('/organization', content_type=content_type)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        expectation = {u'organizations':[{u'id':1, u'organization_long_name' : None, u'organization_name' : u'RPS ASA', u'image_url':None}]}
        self.assertEquals(data, expectation)

        # Get organization by id
        response = self.client.get('/organization/1', content_type=content_type)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEquals(data, expectation['organizations'][0])

        # Get non-existant organization (bad id value); expect failure
        response = self.client.get('/organization/999', content_type=content_type)
        self.assertEquals(response.status_code, 204)


    # Test [GET] /display_name - 'main.get_display_name'
    def test_get_display_name(self):

        content_type = 'application/json'

        # Create a sample data set.
        platform_ref = VocabNames(reference_designator='CE01ISSM', level_one='Endurance', level_two='OR Inshore Surface Mooring')
        db.session.add(platform_ref)
        db.session.commit()

        platform_ref2 = VocabNames(reference_designator='CE01ISSM-MFC31', level_one='Endurance', level_two='OR Inshore Surface Mooring',
                                   level_three='Multi-Function Node')
        db.session.add(platform_ref2)
        db.session.commit()

        response = self.client.get(url_for('main.get_display_name', reference_designator='CE01ISSM-MFC31'), content_type=content_type)
        self.assertEquals(response.status_code, 200)

        response = self.client.get(url_for('main.get_display_name'), content_type=content_type)
        self.assertEquals(response.status_code, 204)

        response = self.client.get(url_for('main.get_display_name', reference_designator='GS03FLMA-RIXXX'), content_type=content_type)
        self.assertEquals(response.status_code, 204)

        response = self.client.get(url_for('main.get_display_name', reference_designator='GS03FLMA-RIXXX-BAD'), content_type=content_type)
        self.assertEquals(response.status_code, 204)
