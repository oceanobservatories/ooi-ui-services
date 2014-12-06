#!/usr/bin/env python
'''
tests.controller.test_table_of_contents

Test to ensure that the table of contents can be compiled using GET commands
'''
import json
from ooiservices import app
from tests.services_test_case import ServicesTestCase

class TestTableOfContents(ServicesTestCase):
    def setUp(self):
        '''
        Initializes the application
        '''
        ServicesTestCase.setUp(self)
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_toc(self):
        root = {}
        rv = self.app.get('/arrays')
        response = json.loads(rv.data)
        response = { r['array_code'] : r for r in response }
        root = response

        for array in root:
            root[array]['platforms'] = self.build_platforms(root[array]['id'])

        
        assert root['CP']['platforms']['CP04OSPM-SBS11']['instruments']['CP04OSPM-SBS11-00-ENG000000']['display_name'] == 'Engineering Data'


    def build_platforms(self, array_id):
        rv = self.app.get('/platform_deployments?array_id=%s' % array_id)
        response = json.loads(rv.data)
        response = { r['reference_designator'] : r for r in response }
        for platform in response:
            response[platform]['instruments'] = self.build_instruments(response[platform]['id'])
        return response

    def build_instruments(self, platform_id):
        rv = self.app.get('/instrument_deployments?platform_deployment_id=%s' % platform_id)
        response = json.loads(rv.data)
        response = { r['reference_designator'] : r for r in response }
        return response

        

