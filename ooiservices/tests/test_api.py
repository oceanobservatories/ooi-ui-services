#!/usr/bin/env python
'''
unit testing for the table of contents (TOC) required classes.

'''
__author__ = 'M@Campbell'

import unittest
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import Array, InstrumentDeployment, PlatformDeployment, Stream, StreamParameter
from ooiservices.app.models import Organization
import json
'''
These tests verify the functioning of the api list.
Sample data is inserted, checked, and then removed.

'''
class TOCTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_array(self):
        #Create a sample data set.
        #TODO : This will be replaced by an endpoint
        array_code = Array(array_code='CE')

        db.session.add(array_code)
        db.session.commit()

        #test the api route for lists
        response = self.client.get(url_for('main.get_arrays'), content_type='application/json')
        self.assertTrue(response.status_code == 200)
        response = self.client.get(url_for('main.get_array',id='CE'), content_type='application/json')
        self.assertTrue(response.status_code == 200)

    def test_platform_deployment(self):
        #Create a sample data set.
        #TODO : This will be replaced by an endpoint
        platform_ref = PlatformDeployment(reference_designator='CE01ISSM-LM001')

        db.session.add(platform_ref)
        db.session.commit()

        response = self.client.get(url_for('main.get_platform_deployments'), content_type='application/json')

        self.assertTrue(response.status_code == 200)

        # Run locally but not under travis due to vocabulary dependency.
        """
        response = self.client.get(url_for('main.get_platform_deployment', id='CE01ISSM-LM001'),
                                   content_type='application/json')
        self.assertTrue(response.status_code == 200)
        """

    # Run locally but not under travis due to vocabulary dependency.
    def _test_instrument_deployment(self):
        #Create a sample data set
        #TODO : This will be replaced by an endpoint

        instrument_ref = InstrumentDeployment(reference_designator = 'CE04OSSM-SBD11-01-MOPAK0000')

        db.session.add(instrument_ref)
        db.session.commit()
        instrument_id = instrument_ref.id

        response = self.client.get(url_for('main.get_instrument_deployments'), content_type='application/json')

        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_instrument_deployment', id = instrument_id),
                                   content_type='application/json')

        self.assertTrue(response.status_code == 200)


    def test_parameter(self):
        #Create a sample data set
        #TODO : This will be replaced by an endpoint
        parameter_name = StreamParameter(stream_parameter_name='preferred_timestamp')

        db.session.add(parameter_name)
        db.session.commit()

        response = self.client.get(url_for('main.get_parameters'), content_type='application/json')

        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_parameter', id='preferred_timestamp'),
                                   content_type='application/json')

        self.assertTrue(response.status_code == 200)

    def test_organization(self):
        organization = Organization()
        organization.organization_name = 'HTEST'
        organization.organization_long_name = 'Health Test'
        db.session.add(organization)
        db.session.commit()

        response = self.client.get('/organization', content_type='application/json')
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEquals(data, {'organizations': [{'id': 1, 'organization_name': 'HTEST',
                                                   'organization_long_name':'Health Test', 'image_url':None}]})

        response = self.client.get('/organization/1', content_type='application/json')
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEquals(data, {'id':1, 'organization_name': 'HTEST', 'organization_long_name': 'Health Test',
                                 'image_url': None})




