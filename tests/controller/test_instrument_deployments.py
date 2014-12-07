#!/usr/bin/env python
'''
tests.controller.test_instrument_deployment_controller

Test for the instrument deployment controller
'''
import json
from ooiservices import app
from tests.services_test_case import ServicesTestCase

class TestInstrumentDeploymentController(ServicesTestCase):
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
        rv = self.app.get('/instrument_deployments')
        response = json.loads(rv.data)

        # Rearrange the response by array_code
        response = { r['reference_designator'] : r for r in response }
        assert "CP02PMCI-WFP01-05-PARADK000" in response
        assert response["CP02PMCI-WFP01-05-PARADK000"]['display_name'] == "Photosynthetically Available Radiation"

    def test_instrument_deployment_where(self):
        rv = self.app.get('/instrument_deployments?platform_deployment_id=15')
        response = json.loads(rv.data)

        # Rearrange the response by array_code
        response = { r['reference_designator'] : r for r in response }
        assert "CP02PMCI-WFP01-03-CTDPFK000" in response
        assert response["CP02PMCI-WFP01-03-CTDPFK000"]['display_name'] == "CTD Profiler"
        
        rv = self.app.get('/instrument_deployments?id=10000')
        response = json.loads(rv.data)

        assert len(response) == 0

    def test_get(self):
        rv = self.app.get('/instrument_deployments/4')
        response = json.loads(rv.data)
        assert response['reference_designator'] == "CP02PMCI-SBS01-01-MOPAK0000"

        # Assert not found
        rv = self.app.get('/instrument_deployments/9000')
        assert rv.status_code == 204



