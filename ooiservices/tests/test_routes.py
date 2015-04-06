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
from ooiservices.app.models import PlatformDeployment, InstrumentDeployment, Stream, StreamParameter
from ooiservices.app.models import Organization, User, UserScope
import datetime as dt

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
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


    # Test [GET] /streams  - 'main.get_streams'
    def test_stream(self):

        content_type = 'application/json'

        #Create a sample data set
        stream_name = Stream(stream_name='mopak_o_dcl_accel_unprocessed')
        db.session.add(stream_name)
        db.session.commit()

        response = self.client.get(url_for('main.get_streams'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_stream', id='mopak_o_dcl_accel_unprocessed'),
                                   content_type=content_type)
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
        self.assertEquals(data, {'organizations':[{'id':1, 'organization_name' : 'ASA'}]})

        # Get organization by id
        response = self.client.get('/organization/1', content_type=content_type)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEquals(data, {'id':1, 'organization_name' : 'ASA'})

        # Get non-existant organization (bad id value); expect failure
        response = self.client.get('/organization/999', content_type=content_type)
        self.assertEquals(response.status_code, 204)

    # Test [GET] /platformlocation - 'main.get_platform_deployment_geojson_single'
    def test_route_get_platform_deployment_geojson_single(self):

        content_type = 'application/json'

        # Issue requests when no data available
        response = self.client.get(url_for('main.get_platform_deployment_geojson_single'), content_type=content_type)
        self.assertEquals(response.status_code, 204)

        # Create a sample data set.
        platform_ref = PlatformDeployment(reference_designator='CE01ISSM')
        platform_ref.geo_location = 'POINT(-70 40)'
        db.session.add(platform_ref)
        db.session.commit()

        platform_ref2 = PlatformDeployment(reference_designator='GS05MOAS-PG002')
        platform_ref2.geo_location = 'POINT(-70 40)'
        db.session.add(platform_ref2)
        db.session.commit()

        # Get platform_deployment
        response = self.client.get(url_for('main.get_platform_deployment', id='CE01ISSM'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        '''
        curl -X GET 'http://localhost:4000/platform_deployments/GS05MOAS-PG002'
        {
          "array_id": 6,
          "display_name": "Global Southern Ocean Mobile (Open Ocean) - Profiler",
          "end_date": null,
          "geo_location": {
            "coordinates": [
              -89.6652,
              -54.0814
            ],
            "type": "Point"
          },
          "id": 203,
          "reference_designator": "GS05MOAS-PG002",
          "start_date": null
        }
        '''

        # Request all
        response = self.client.get(url_for('main.get_platform_deployment_geojson_single'), content_type=content_type)
        self.assertEquals(response.status_code, 200)

        # Request single reference_designator
        response = self.client.get(url_for('main.get_platform_deployment_geojson_single', reference_designator='CE01ISSM'), content_type=content_type)
        self.assertEquals(response.status_code, 200)

        # Request single reference_designator
        response = self.client.get(url_for('main.get_platform_deployment_geojson_single', reference_designator='NO-GOOD'), content_type=content_type)
        self.assertEquals(response.status_code, 204)

    # Test [GET] /display_name - 'main.get_display_name'
    def test_get_display_name(self):

        content_type = 'application/json'

        # Create a sample data set.
        platform_ref = PlatformDeployment(reference_designator='CE01ISSM')
        platform_ref.geo_location = 'POINT(-70 40)'
        db.session.add(platform_ref)
        db.session.commit()

        platform_ref2 = PlatformDeployment(reference_designator='GS03FLMA-RIS02')
        platform_ref2.geo_location = 'POINT(-70 40)'
        db.session.add(platform_ref2)
        db.session.commit()

        response = self.client.get(url_for('main.get_display_name', reference_designator='GS03FLMA-RIS02'), content_type=content_type)
        self.assertEquals(response.status_code, 200)

        response = self.client.get(url_for('main.get_display_name'), content_type=content_type)
        self.assertEquals(response.status_code, 204)

        response = self.client.get(url_for('main.get_display_name', reference_designator='GS03FLMA-RIXXX'), content_type=content_type)
        self.assertEquals(response.status_code, 204)

        response = self.client.get(url_for('main.get_display_name', reference_designator='GS03FLMA-RIXXX-99-ABCDEF000'),
                                   content_type=content_type)
        self.assertEquals(response.status_code, 204)

        response = self.client.get(url_for('main.get_display_name', reference_designator='GS03FLMA-RIXXX-BAD'), content_type=content_type)
        self.assertEquals(response.status_code, 204)

        # Create platform deployment for foreign key constraints when creating
        # instrument_deployment (note: using platform_deployment with actual id=203)
        GS05MOAS_PG002_rd = 'GS05MOAS-PG002'
        GS05MOAS_PG002 = PlatformDeployment(reference_designator=GS05MOAS_PG002_rd)
        db.session.add(GS05MOAS_PG002)
        db.session.commit()
        GS05MOAS_PG002_id = GS05MOAS_PG002.id
        number_of_platform_deployments = 1

        # Create instrument(s) for previously created platform deployment; required for
        # foreign keys - otherwise foreign key violation received.
        number_of_instruments = 1
        FLORDM000_rd = 'GS05MOAS-PG002-02-FLORDM000'
        FLORDM000 = InstrumentDeployment(reference_designator=FLORDM000_rd)
        FLORDM000.depth = 1000.0
        FLORDM000.display_name = '2-Wavelength Fluorometer'
        FLORDM000.end_date = dt.datetime.now()
        FLORDM000.geo_location = 'POINT(-70 40)'
        FLORDM000.platform_deployment_id = GS05MOAS_PG002_id                # actual 754
        FLORDM000.reference_designator = FLORDM000_rd
        FLORDM000.start_date = dt.datetime.now()
        db.session.add(FLORDM000)
        db.session.commit()
        response = self.client.get(url_for('main.get_display_name', reference_designator='GS05MOAS-PG002-02-FLORDM000'),
                                   content_type=content_type)
        self.assertEquals(response.status_code, 200)
