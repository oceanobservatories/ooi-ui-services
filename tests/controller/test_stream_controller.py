#!/usr/bin/env python
'''
tests.controller.test_stream_controller

Test for the stream controller
'''
import json
from ooiservices import app
from tests.services_test_case import ServicesTestCase

import pytest

# This test currently depends on the external connection to ERDDAP

@pytest.mark.erddap
class TestStreamController(ServicesTestCase):
    '''
    Unit tests for the stream controller
    '''

    def setUp(self):
        '''
        Creates a test table to work with as a mock model
        '''
        ServicesTestCase.setUp(self)
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_listing(self):
        '''
        Make sure that we're able to list the streams available on ERDDAP
        '''

        rv = self.app.get('/streams')
        response = json.loads(rv.data)
        response = { s['id'] : s for s in response }
        assert 'CP02PMCI_SBS01_00_000000000_cg_stc_eng_stc_unprocessed' in response

    def test_reference_designators(self):
        rv = self.app.get('/streams?reference_designator=CP02PMCO_WFP01_05_PARADK000')
        response = json.loads(rv.data)
        response = { s['id'] : s for s in response }
        assert len(response) == 4
        assert 'CP02PMCO_WFP01_05_PARADK000_parad_k__stc_imodem_instrument_unprocessed' in response
        assert 'CP02PMCI_SBS01_00_000000000_cg_stc_eng_stc_unprocessed' not in response

