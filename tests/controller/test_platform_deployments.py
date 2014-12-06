#!/usr/bin/env python
'''
tests.controller.test_platform_deployment_controller

Test for the platform deployment controller
'''
import json
from ooiservices.app import app
from tests.services_test_case import ServicesTestCase

class TestPlatformDeploymentController(ServicesTestCase):
    def setUp(self):
        '''
        Initializes the application
        '''
        ServicesTestCase.setUp(self)
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_listing(self):
        '''
        Test that the app context initializes successfully
        mjc: we'll have a test for complex endpoints and their json output.
            For now, we just need to know that the end points are running.
        '''
        rv = self.app.get('/platform_deployments')
        response = json.loads(rv.data)

        # Rearrange the response by array_code
        response = { r['reference_designator'] : r for r in response }
        assert 'CP05MOAS-GL005' in response
        assert response["CP05MOAS-GL005"]['display_name'] == "Pioneer Mobile Coastal Glider #5"

    def test_platform_deployment_where(self):
        rv = self.app.get('/platform_deployments?array_id=1')
        response = json.loads(rv.data)

        # Rearrange the response by array_code
        response = { r['reference_designator'] : r for r in response }
        assert 'CP05MOAS-GL005' in response
        assert response["CP05MOAS-GL005"]['display_name'] == "Pioneer Mobile Coastal Glider #5"
        
        rv = self.app.get('/platform_deployments?id=10000')
        response = json.loads(rv.data)

        assert len(response) == 0

    def test_get(self):
        rv = self.app.get('/platform_deployments/5')
        response = json.loads(rv.data)
        assert response['reference_designator'] == "CP04OSPM-SBS11"

        # Assert not found
        rv = self.app.get('/platform_deployments/9000')
        assert rv.status_code == 204


