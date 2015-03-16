#!/usr/bin/env python
'''
Specific testing of arrays.

'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment,  Instrumentname
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

    def _check_instrument_deployment_fields_provided(self, instrument_deployment):
        # verify all data fields for an InstrumentDeployment object are [returned] in response_data
        result = False
        try:
            self.assertTrue(len(instrument_deployment) > 0, msg='\ninstrument_deployment <= 0')
            self.assertTrue('id' in instrument_deployment)
            self.assertTrue('depth' in instrument_deployment)
            self.assertTrue('geo_location' in instrument_deployment)
            self.assertTrue('display_name' in instrument_deployment)
            self.assertTrue('end_date' in instrument_deployment)
            self.assertTrue('start_date' in instrument_deployment)
            self.assertTrue('platform_deployment_id' in instrument_deployment)
            self.assertTrue('reference_designator' in instrument_deployment)
            result = True
        except Exception, err:
            print '\n _check_instrument_deployment_fields_provided: error: %s' % err.message

        return result
    def test_array(self):
        '''
        general test for array api route for lists
        '''
        content_type = 'application/json'

        #Create a sample data set.
        array_code = Array(array_code='CE')
        db.session.add(array_code)
        db.session.commit()

        response = self.client.get(url_for('main.get_arrays'), content_type=content_type )
        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_array',id='CE'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

    def create_platform_deployment(self, platform_reference_designator):
        platform_deployment = None
        if platform_reference_designator == 'CP02PMCO-WFP01':
            CP02PMCO_WFP01    = PlatformDeployment(reference_designator=platform_reference_designator)
            CP02PMCO_WFP01.reference_designator = platform_reference_designator
            CP02PMCO_WFP01.display_name = 'CP02PMCO_WFP01 display_name'
            CP02PMCO_WFP01.array_id = 3
            db.session.add(CP02PMCO_WFP01)
            db.session.commit()
            platform_deployment = CP02PMCO_WFP01
        elif platform_reference_designator == 'CP02PMCO-SBS01':
            CP02PMCO_SBS01    = PlatformDeployment(reference_designator=platform_reference_designator)
            CP02PMCO_SBS01.reference_designator = platform_reference_designator
            CP02PMCO_SBS01.display_name = 'CP02PMCO_SBS01 display_name'
            CP02PMCO_SBS01.array_id = 3
            db.session.add(CP02PMCO_SBS01)
            db.session.commit()
            platform_deployment = CP02PMCO_SBS01
        else:
            platform_deployment = PlatformDeployment(reference_designator=platform_reference_designator)
            db.session.add(platform_deployment)
            db.session.commit()
        return platform_deployment

    def create_instrument_deployment(self, instrument_reference_designator, platform_deployment_id):
        instrument_deployment = None
        if instrument_reference_designator == 'CP02PMCO-WFP01-02-DOFSTK000':
            DOFSTK000 = InstrumentDeployment(reference_designator=instrument_reference_designator)
            DOFSTK000.depth = 1000.0
            DOFSTK000.display_name = 'Dissolved Oxygen Fast Response'
            DOFSTK000.end_date = dt.datetime.now()
            DOFSTK000.geo_location = 'POINT(-70 40)'
            DOFSTK000.platform_deployment_id = platform_deployment_id
            DOFSTK000.reference_designator = instrument_reference_designator
            DOFSTK000.start_date = dt.datetime.now()
            db.session.add(DOFSTK000)
            db.session.commit()
            instrument_deployment = DOFSTK000

        elif instrument_reference_designator == 'CP02PMCO-WFP01-03-CTDPFK000':
            CTDPFK000 = InstrumentDeployment(reference_designator=instrument_reference_designator)
            CTDPFK000.depth = 1000.0
            CTDPFK000.display_name = 'CTD Profiler'
            CTDPFK000.end_date = dt.datetime.now()
            CTDPFK000.geo_location = 'POINT(-70 40)'
            CTDPFK000.platform_deployment_id = platform_deployment_id
            CTDPFK000.reference_designator = instrument_reference_designator
            CTDPFK000.start_date = dt.datetime.now()
            db.session.add(CTDPFK000)
            db.session.commit()
            instrument_deployment = CTDPFK000
        elif instrument_reference_designator == 'CP02PMCO-WFP01-05-PARADK000':
            PARADK000 = InstrumentDeployment(reference_designator=instrument_reference_designator)
            PARADK000.depth = 1000.0
            PARADK000.display_name = 'Photosynthetically Available Radiation'
            PARADK000.end_date = dt.datetime.now()
            PARADK000.geo_location = 'POINT(-70 40)'
            PARADK000.platform_deployment_id = platform_deployment_id
            PARADK000.reference_designator = instrument_reference_designator
            PARADK000.start_date = dt.datetime.now()
            db.session.add(PARADK000)
            db.session.commit()
            instrument_deployment = PARADK000
        elif instrument_reference_designator == 'CP02PMCO-SBS01-01-MOPAK0000':
            MOPAK0000 = InstrumentDeployment(reference_designator=instrument_reference_designator)
            MOPAK0000.depth = 1000.0
            MOPAK0000.display_name = '2-Wavelength Fluorometer'
            MOPAK0000.end_date = dt.datetime.now()
            MOPAK0000.geo_location = 'POINT(-70 40)'
            MOPAK0000.platform_deployment_id = platform_deployment_id
            MOPAK0000.reference_designator = instrument_reference_designator
            MOPAK0000.start_date = dt.datetime.now()
            db.session.add(MOPAK0000)
            db.session.commit()
            instrument_deployment = MOPAK0000
        else:
            instrument_deployment = InstrumentDeployment(reference_designator=instrument_reference_designator)
            instrument_deployment.reference_designator = platform_deployment_id
            db.session.add(instrument_deployment)
            db.session.commit()
        return instrument_deployment

    #Test C2 API routes
    def test_array_display_route(self):

        content_type = 'application/json'

        # Start data setup.
        # Create test data - three arrays (CE, GP, CP)
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'Coastal node array description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= 'POINT(-70 40)'
        db.session.add(array_CE)
        db.session.commit()

        array_GP = Array(array_code='GP')
        array_GP.array_name  = 'Papa'
        array_GP.description = 'Global Station Papa node array description...'
        array_GP.display_name= 'Global Station Papa'
        array_GP.geo_location= 'POINT(-70 40)'
        db.session.add(array_GP)
        db.session.commit()

        array_CP = Array(array_code='CP')
        array_CP.array_name  = 'Pioneer'
        array_CP.description = 'array description...'
        array_CP.display_name= 'Coastal Pioneer'
        array_CP.geo_location= 'POINT(-70 45)'
        db.session.add(array_CP)
        db.session.commit()

        # Check three arrays are available
        response = self.client.get(url_for('main.get_array', id='CE'), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        response = self.client.get(url_for('main.get_array', id='GP'), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        response = self.client.get(url_for('main.get_array', id='CP'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        # verify resulting fields for array are returned
        #response_data = response.data
        #self.assertTrue(self._check_array_fields_provided(response_data))

        response = self.client.get(url_for('main.get_arrays'), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('arrays' in data)
        self.assertEquals(3, len(data['arrays']))

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create a sample data set:
        # Summary: 2 platform deployments, three instrument deployments
        # Contents:
        #     1. platform deployment:       CP02PMCO-WFP01
        #         instrument deployment(1): CP02PMCO-WFP01-02-DOFSTK000,
        #                              (2): CP02PMCO-WFP01-03-CTDPFK000
        #                              (3): CP02PMCO-WFP01-05-PARADK000
        #
        #     2. platform deployment:       CP02PMCO-SBS01
        #         instrument deployment(1): CP02PMCO-SBS01-01-MOPAK0000
        #
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        array_CP_platforms = []
        # platform_deployment(s) - CP02PMCO-WFP01, CP02PMCO-SBS01
        # platform deployment 1
        CP02PMCO_WFP01_rd = 'CP02PMCO-WFP01'
        CP02PMCO_WFP01 = self.create_platform_deployment(CP02PMCO_WFP01_rd)
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)

        # platform deployment 2
        CP02PMCO_SBS01_rd = 'CP02PMCO-SBS01'
        CP02PMCO_SBS01 = self.create_platform_deployment(CP02PMCO_SBS01_rd)
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)

        # Total number of instruments to be created across all platforms
        number_of_instruments = 4
        platform_1_instrument_count = 3
        platform_2_instrument_count = 1

        platform_1_instrument_deployments = []
        platform_2_instrument_deployments = []
        # Create multiple instrument deployments for multiple platforms
        # (platform deployment 1) instrument deployment 1
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        DOFSTK000 = self.create_instrument_deployment(DOFSTK000_rd, CP02PMCO_WFP01_id)
        DOFSTK000_id = DOFSTK000.id
        platform_1_instrument_deployments.append(DOFSTK000_rd)

        # (platform deployment 1) instrument deployment 2
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        CTDPFK000 = self.create_instrument_deployment(CTDPFK000_rd, CP02PMCO_WFP01_id)
        CTDPFK000_id = CTDPFK000.id
        platform_1_instrument_deployments.append(CTDPFK000_rd)

        # (platform deployment 1) instrument deployment 3
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'
        PARADK000 = self.create_instrument_deployment(PARADK000_rd, CP02PMCO_WFP01_id)
        PARADK000_id = PARADK000.id
        platform_1_instrument_deployments.append(PARADK000_rd)

        # # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        MOPAK0000 = self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        MOPAK0000_id = MOPAK0000.id
        platform_2_instrument_deployments.append(MOPAK0000_rd)

        # Get all instrument deployments; verify 4 instruments returned
        response = self.client.get(url_for('main.get_instrument_deployments'), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        all_data = json.loads(response.data)

        # Verify four instrument deployments (total)
        self.assertIn('instrument_deployments', all_data)
        list_all_data = all_data['instrument_deployments']
        len_list_all_data = len(list_all_data)
        self.assertTrue(len_list_all_data > 0)
        self.assertEquals(len_list_all_data, number_of_instruments)

        # Platform 1 - Verify each instrument is associated with correct platform deployment id
        # Get instrument DOFSTK000
        response = self.client.get(url_for('main.get_instrument_deployment', id=DOFSTK000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        DOFSTK000_data = json.loads(response.data[:])
        self.assertTrue('platform_deployment_id' in DOFSTK000_data)
        self.assertTrue(DOFSTK000_data['platform_deployment_id'], CP02PMCO_WFP01_id)
        self.assertTrue(self._check_instrument_deployment_fields_provided(DOFSTK000_data))
        # Verify (a) all required fields provided, todo  (b)content as expected and (c) geo_location not null

        # Get instrument CTDPFK000
        response = self.client.get(url_for('main.get_instrument_deployment', id=CTDPFK000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        CTDPFK000_data = json.loads(response.data[:])
        self.assertTrue('platform_deployment_id' in CTDPFK000_data)
        self.assertTrue(CTDPFK000_data['platform_deployment_id'], CP02PMCO_WFP01_id)
        self.assertTrue(self._check_instrument_deployment_fields_provided(CTDPFK000_data))
        # Verify (a) all required fields provided, todo  (b)content as expected and (c) geo_location not null

        # Get instrument PARADK000
        response = self.client.get(url_for('main.get_instrument_deployment', id=PARADK000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        PARADK000_data = json.loads(response.data[:])
        self.assertTrue('platform_deployment_id' in PARADK000_data)
        self.assertTrue(PARADK000_data['platform_deployment_id'], CP02PMCO_WFP01_id)
        self.assertTrue(self._check_instrument_deployment_fields_provided(PARADK000_data))
        # Verify (a) all required fields provided, todo  (b)content as expected and (c) geo_location not null

        # Platform 2 - Verify each instrument is associated with correct platform deployment id
        # Get instrument MOPAK0000
        response = self.client.get(url_for('main.get_instrument_deployment', id=MOPAK0000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        MOPAK0000_data = json.loads(response.data[:])
        self.assertTrue('platform_deployment_id' in MOPAK0000_data)
        self.assertTrue(MOPAK0000_data['platform_deployment_id'], CP02PMCO_SBS01_id)
        self.assertTrue(self._check_instrument_deployment_fields_provided(PARADK000_data))
        # Verify (a) all required fields provided, todo  (b)content as expected and (c) geo_location not null

        # Verify platform deployment 1 has three instruments and are three instruments expected
        response = self.client.get('/instrument_deployment?platform_deployment_id=%s' % CP02PMCO_WFP01_id)
        self.assertTrue(response.status_code == 200)
        response_data = response.data
        self.assertTrue('instrument_deployments' in response_data)
        ins_data = json.loads(response_data)
        list_instrument_deployments_platform1 = ins_data['instrument_deployments']
        self.assertEquals(len(list_instrument_deployments_platform1), platform_1_instrument_count)
        self.assertEquals(list_instrument_deployments_platform1[0], DOFSTK000_data)
        self.assertEquals(list_instrument_deployments_platform1[1], CTDPFK000_data)
        self.assertEquals(list_instrument_deployments_platform1[2], PARADK000_data)

        # Verify platform deployment 2 has one instrument and it is the instrument expected
        response = self.client.get('/instrument_deployment?platform_deployment_id=%s' % CP02PMCO_SBS01_id)
        self.assertTrue(response.status_code == 200)
        response_data = response.data
        self.assertTrue('instrument_deployments' in response_data)
        ins_data = json.loads(response_data)
        list_instrument_deployments_platform2 = ins_data['instrument_deployments']
        self.assertEquals(len(list_instrument_deployments_platform2), platform_2_instrument_count)
        self.assertEquals(list_instrument_deployments_platform2[0], MOPAK0000_data)
        self.assertTrue(self._check_instrument_deployment_fields_provided(MOPAK0000_data))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup.
        # Now have two arrays, two platforms, each populated with instruments
        # Have list of:
        #   platform_deployments for array CP: array_CP_platforms
        #   instrument_deployments for each platform - platform_1_instrument_deployments, platform_2_instrument_deployments
        #
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Test /c2/array_display/array_code
        # http://localhost:4000/c2/array_display/CE
        array_code='CE'
        response = self.client.get(url_for('main.c2_get_array_display', array_code=array_code),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/array_display/CP
        array_code='CP'
        response = self.client.get(url_for('main.c2_get_array_display', array_code=array_code),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # Test /c2/platform_display/reference_designator
        # http://localhost:4000/c2/platform_display/CP02PMCO-WFP01
        platform = CP02PMCO_WFP01.reference_designator
        response = self.client.get(url_for('main.c2_get_platform_display', reference_designator=platform),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/platform_display/CP02PMCO-SBS01
        platform = CP02PMCO_SBS01.reference_designator
        response = self.client.get(url_for('main.c2_get_platform_display', reference_designator=platform),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # test all three instruments for platform 1
        # http://localhost:4000/c2/instrument_display/CP02PMCO-WFP01-02-DOFSTK000
        instrument = DOFSTK000.reference_designator
        response = self.client.get(url_for('main.c2_get_instrument_display', reference_designator=instrument),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument_display/CP02PMCO-WFP01-03-CTDPFK000
        instrument = CTDPFK000.reference_designator
        response = self.client.get(url_for('main.c2_get_instrument_display', reference_designator=instrument),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument_display/CP02PMCO-WFP01-05-PARADK000
        instrument = PARADK000.reference_designator
        response = self.client.get(url_for('main.c2_get_instrument_display', reference_designator=instrument),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # test single instrument for platform 2
        # http://localhost:4000/c2/instrument_display/CP02PMCO-SBS01-01-MOPAK0000
        instrument = MOPAK0000.reference_designator
        response = self.client.get(url_for('main.c2_get_instrument_display', reference_designator=instrument),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # test fields for instrument_deployment stream_name
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/dofst_k_wfp_metadata/fields
        instrument = DOFSTK000.reference_designator
        stream = 'dofst_k_wfp_metadata'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k_stc_imodem_instrument/fields
        instrument = PARADK000.reference_designator
        stream = 'parad_k_stc_imodem_instrument'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/mopak_o_dcl_accel/fields
        instrument = MOPAK0000.reference_designator
        stream = 'mopak_o_dcl_accel'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_instrument/fields
        instrument = CTDPFK000.reference_designator
        stream = 'ctdpf_ckl_wfp_instrument'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_metadata/fields
        instrument = CTDPFK000.reference_designator
        stream = 'ctdpf_ckl_wfp_metadata'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # negative test(s)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Negative tests for: /c2/array_display/array_code
        # http://localhost:4000/c2/array_display/
        array_code=''
        response = self.client.get(url_for('main.c2_get_array_display', array_code=array_code),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/array_display/no_such_array
        array_code='no_such_array'
        response = self.client.get(url_for('main.c2_get_array_display', array_code=array_code),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Negative tests for: /c2/platform_display/reference_designator
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/platform_display/
        platform = ''
        response = self.client.get(url_for('main.c2_get_platform_display', reference_designator=platform),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/platform_display/no_such_platform
        platform = 'no_such_platform'
        response = self.client.get(url_for('main.c2_get_platform_display', reference_designator=platform),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Negative tests for: /c2/instrument_display/reference_designator
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/instrument_display/
        instrument = ''
        response = self.client.get(url_for('main.c2_get_instrument_display', reference_designator=instrument),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/instrument_display/no_such_platform
        instrument = 'no_such_platform'
        response = self.client.get(url_for('main.c2_get_instrument_display', reference_designator=instrument),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        #  Negative tests for: /c2/instrument/reference_designator/stream_name/fields
        # http://localhost:4000/c2/instrument//ctdpf_ckl_wfp_metadata/fields
        instrument = ''
        stream = 'ctdpf_ckl_wfp_metadata'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/instrument/no_such_instrument/ctdpf_ckl_wfp_metadata/fields
        # response is (400) bad_request: "Invalid reference designator for instrument ('no_such_instrument')."
        instrument = 'no_such_instrument'
        stream = 'ctdpf_ckl_wfp_metadata'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        # http://localhost:4000/c2/instrument//ctdpf_ckl_wfp_metadata/fields
        instrument = CTDPFK000.reference_designator
        stream = ''
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/no_such_stream/fields
        # response is (400) bad_request: "Invalid stream name ('no_such_stream') for instrument ('CP02PMCO-WFP01-03-CTDPFK000')"
        instrument = CTDPFK000.reference_designator
        stream = 'no_such_stream'
        response = self.client.get(url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream),
                                   content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

    #TODO save for C2 PUT test development
    '''
    # Test [PUT] /arrays/<int:id> - 'main.update_array'
    def test_update_array(self):

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create array data
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= 'POINT(-70 40)'
        db.session.add(array_CE)
        db.session.commit()

        data = json.dumps({'description':'description update'})
        response = self.client.put(url_for('main.update_array', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 200)

        # fetch array and compare contents returned with expected contents
        response = self.client.get(url_for('main.get_array',id='CE'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        # verify resulting fields for array are returned
        response_data = response.data
        self.assertTrue(self._check_array_fields_provided(response_data))

        # create dictionary from string;
        dict_data = json.loads(response_data)

        expected_data = {'array_code': 'CE', 'display_name':'Coastal Endurance',
                         'description': 'description update','array_name': 'Endurance', 'id': 1,
                         'geo_location': {u'type': u'Point', u'coordinates': [-70, 40]}, }
        self.assertTrue(dict_data == expected_data)

    # Test [PUT] /arrays/<int:id> - 'main.update_array'
    def test_update_array_with_error(self):

        headers = self.get_api_headers('admin', 'test')

        # Create array with geo_locations == None
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= None
        db.session.add(array_CE)
        db.session.commit()

        data = json.dumps({'description':'update'})
        response = self.client.put(url_for('main.update_array', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 409)

    # Test [POST] /arrays/ - 'main.create_array'
    def test_create_array(self):

        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create array data
        data = {}
        data['array_code']   = 'RS'
        data['array_name']   = 'Regional Scale Node'
        data['display_name'] = 'Coastal Regional Scale Node'
        data['description']  = 'Coastal array located off Washington and Oregon coasts.'
        data["geo_location"] = 'POINT(-70 40)'

        data = json.dumps(data)
        response = self.client.post(url_for('main.create_array'), headers=headers,data=data)
        self.assertEquals(response.status_code, 201)

        response = self.client.get(url_for('main.get_array',id='RS'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

    # Test [POST] /arrays/ - 'main.create_array'
    def test_create_duplicate_array_code(self):

        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create array
        data = {}
        data['array_code']   = 'RS'
        data['array_name']   = 'Regional Scale Node'
        data['display_name'] = 'Coastal Regional Scale Node'
        data['description']  = 'Coastal array located off Washington and Oregon coasts.'
        data['geo_location'] = 'POINT(-70 40)'

        data = json.dumps(data)
        response = self.client.post(url_for('main.create_array'), headers=headers,data=data)
        self.assertEquals(response.status_code, 201)

        response = self.client.get(url_for('main.get_array',id='RS'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        response = self.client.post(url_for('main.create_array'), headers=headers,data=data)
        self.assertEquals(response.status_code, 201)

        response = self.client.get(url_for('main.get_array',id='RS'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

'''
