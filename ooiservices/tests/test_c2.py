#!/usr/bin/env python
'''
Specific testing for Command and Control (C2)
To determine C2 routes (for examples or coverage), set verbose to True.
To debug a specific test, set debug to True while debugging.
(Always set verbose and debug to False at check in.)
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

    # enable verbose during development and documentation to get a list of sample
    # urls used throughout test cases. Always set to False before check in.
    verbose = False
    root = 'http://localhost:4000'

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
        elif platform_reference_designator == 'CP02PMUI-RII01':
            CP02PMUI_RII01    = PlatformDeployment(reference_designator=platform_reference_designator)
            CP02PMUI_RII01.reference_designator = platform_reference_designator
            CP02PMUI_RII01.display_name = 'CP02PMUI_RII01 display_name'
            CP02PMUI_RII01.array_id = 3
            db.session.add(CP02PMUI_RII01)
            db.session.commit()
            platform_deployment = CP02PMUI_RII01
        else:
            platform_deployment = PlatformDeployment(reference_designator=platform_reference_designator)
            db.session.add(platform_deployment)
            db.session.commit()
        return platform_deployment

    def create_CP_platform_deployments(self):

        # platform deployment 1
        CP02PMCO_WFP01_rd = 'CP02PMCO-WFP01'
        CP02PMCO_WFP01 = self.create_platform_deployment(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_rd = 'CP02PMCO-SBS01'
        CP02PMCO_SBS01 = self.create_platform_deployment(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_rd = 'CP02PMUI-RII01'
        CP02PMUI_RII01 = self.create_platform_deployment(CP02PMUI_RII01_rd)

        return CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01

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
        elif instrument_reference_designator == 'CP02PMUI-RII01-02-ADCPTG000':
            ADCPTG000 = InstrumentDeployment(reference_designator=instrument_reference_designator)
            ADCPTG000.depth = 1000.0
            ADCPTG000.display_name = 'Velocity Profiler (short range)'
            ADCPTG000.end_date = dt.datetime.now()
            ADCPTG000.geo_location = 'POINT(-70 40)'
            ADCPTG000.platform_deployment_id = platform_deployment_id
            ADCPTG000.reference_designator = instrument_reference_designator
            ADCPTG000.start_date = dt.datetime.now()
            db.session.add(ADCPTG000)
            db.session.commit()
            instrument_deployment = ADCPTG000
        else:
            instrument_deployment = InstrumentDeployment(reference_designator=instrument_reference_designator)
            instrument_deployment.reference_designator = platform_deployment_id
            db.session.add(instrument_deployment)
            db.session.commit()
        return instrument_deployment

    def setup_array_data(self):
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
        return array_CE, array_GP, array_CP

    #Test C2 API routes
    def test_c2_data_setup_arrays(self):
        '''
        general test for array api route for lists
        '''
        content_type = 'application/json'

        #Create a sample data set.
        array_CE, array_GP, array_CP = self.setup_array_data()

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

    def test_c2_data_setup_all(self):

        '''
        # c2 array routes:
        http://localhost:4000/c2/array/CP/abstract
        http://localhost:4000/c2/array/CP/current_status_display
        http://localhost:4000/c2/array/CP/history
        http://localhost:4000/c2/array/CP/status_display
        http://localhost:4000/c2/array/CP/mission_display

        # c2 platform routes:
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/abstract
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/current_status_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/history
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/status_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/commands

        # c2 instrument routes:
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/streams
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/commands
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/history
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/status_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k_stc_imodem_instrument/fields

        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/commands
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/dofst_k_wfp_metadata/fields

        # c2 mission control (platform and instrument)
        [Platform] Mission
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selections
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/mission4
        return mission_plan  {"mission_plan": ["name: Mission 4"]}

        [Instrument] Mission
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selections
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selection/mission4
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/mission_does_not_exist
        return mission_plan {"mission_plan": []}
        '''
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
        #     3. platform deployment:       CP02PMUI_RII01
        #         instrument deployment(1): CP02PMUI-RII01-02-ADCPTG000
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type = 'application/json'

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - arrays
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        array_CE, array_GP, array_CP = self.setup_array_data()

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = 'CP02PMCO-WFP01'
        CP02PMCO_SBS01_rd = 'CP02PMCO-SBS01'
        CP02PMUI_RII01_rd = 'CP02PMUI-RII01'
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Total number of instruments to be created across all platforms
        number_of_instruments = 5
        platform_1_instrument_count = 3
        platform_2_instrument_count = 1
        platform_3_instrument_count = 1

        platform_1_instrument_deployments = []
        platform_2_instrument_deployments = []
        platform_3_instrument_deployments = []
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

        # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        MOPAK0000 = self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        MOPAK0000_id = MOPAK0000.id
        platform_2_instrument_deployments.append(MOPAK0000_rd)

        # (platform deployment 3) instrument deployment 1
        ADCPTG000_rd = 'CP02PMUI-RII01-02-ADCPTG000'
        ADCPTG000 = self.create_instrument_deployment(ADCPTG000_rd, CP02PMUI_RII01_id)
        ADCPTG000_id = ADCPTG000.id
        platform_3_instrument_deployments.append(ADCPTG000_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Data verification
        # Get all instrument deployments; verify 5 instruments returned
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
        # End of data setup and verification.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Now have two arrays, three platforms, each populated with instruments
        # Have list of:
        #   platform_deployments for array CP: array_CP_platforms
        #   instrument_deployments for each platform - platform_1_instrument_deployments, platform_2_instrument_deployments
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def test_c2_array_routes(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Test array routes:
        Array:  CE
        http://localhost:4000/c2/array/CE/abstract
        http://localhost:4000/c2/array/CE/current_status_display
        http://localhost:4000/c2/array/CE/history
        http://localhost:4000/c2/array/CE/status_display
        http://localhost:4000/c2/array/CE/mission_display

        Array:  GP
        http://localhost:4000/c2/array/GP/abstract
        http://localhost:4000/c2/array/GP/current_status_display
        http://localhost:4000/c2/array/GP/history
        http://localhost:4000/c2/array/GP/status_display
        http://localhost:4000/c2/array/GP/mission_display

        Array:  CP
        http://localhost:4000/c2/array/CP/abstract
        http://localhost:4000/c2/array/CP/current_status_display
        http://localhost:4000/c2/array/CP/history
        http://localhost:4000/c2/array/CP/status_display
        http://localhost:4000/c2/array/CP/mission_display

        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Start data setup.
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
        #     3. platform deployment:       CP02PMUI_RII01
        #         instrument deployment(1): CP02PMUI-RII01-02-ADCPTG000
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        array_CE, array_GP, array_CP = self.setup_array_data()
        arrays = [array_CE, array_GP, array_CP]
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        # platform deployment 1
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - array
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/arrays
        url = url_for('main.c2_get_arrays')
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('arrays' in data)
        self.assertTrue(len(data['arrays']) == len(arrays))

        # http://localhost:4000/c2/array/CP/abstract
        for array in arrays:
            array_code = array.array_code
            if verbose: print '\nArray: ', array_code
            url = url_for('main.c2_get_array_abstract', array_code=array_code)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('abstract' in data)
            self.assertTrue(len(data['abstract']) > 0)

            # http://localhost:4000/c2/array/CP/current_status_display
            url = url_for('main.c2_get_array_current_status_display', array_code=array_code)
            if verbose: print root+url
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('current_status_display' in data)
            if array_code == 'CP':
                self.assertTrue(len(data['current_status_display']) > 0)
            else:
                self.assertTrue(len(data['current_status_display']) == 0)
            # http://localhost:4000/c2/array/CP/history
            url = url_for('main.c2_get_array_history', array_code=array_code)
            if verbose: print root+url
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            # http://localhost:4000/c2/array/CP/status_display
            url = url_for('main.c2_get_array_status_display', array_code=array_code)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            # http://localhost:4000/c2/array/CP/mission_display
            url = url_for('main.c2_get_array_mission_display', array_code=array_code)
            if verbose: print root+url
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

        if verbose: print '\n'

    def test_c2_array_routes_negative(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Negative tests for array routes:

        Following tests generate error (404):
            http://localhost:4000/c2/array//abstract
            http://localhost:4000/c2/array//current_status_display
            http://localhost:4000/c2/array//history
            http://localhost:4000/c2/array//status_display
            http://localhost:4000/c2/array//mission_display

        Following tests should generate bad_request (400), with consistent error message:
            http://localhost:4000/c2/array/no_such_array/abstract
            http://localhost:4000/c2/array/no_such_array/current_status_display
            http://localhost:4000/c2/array/no_such_array/history
            http://localhost:4000/c2/array/no_such_array/status_display
            http://localhost:4000/c2/array/no_such_array/mission_display
        All tests returning bad_request (400) shall have following error:
            {
              "error": "bad request",
              "message": "unknown array (array_code: 'no_such_array')"
            }
        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Start data setup.
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
        #     3. platform deployment:       CP02PMUI_RII01
        #         instrument deployment(1): CP02PMUI-RII01-02-ADCPTG000
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type = 'application/json'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (platform deployment 1) instrument deployment 1
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        self.create_instrument_deployment(DOFSTK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 2
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        self.create_instrument_deployment(CTDPFK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 3
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'
        self.create_instrument_deployment(PARADK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        # (platform deployment 3) instrument deployment 1
        ADCPTG000_rd = 'CP02PMUI-RII01-02-ADCPTG000'
        self.create_instrument_deployment(ADCPTG000_rd, CP02PMUI_RII01_id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        error_text = "unknown array (array_code: 'no_such_array')"
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic negative tests - array
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/array/no/abstract
        array_code='NO'
        url = url_for('main.c2_get_array_abstract', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        # http://localhost:4000/c2/array//abstract
        array_code=''
        url = url_for('main.c2_get_array_abstract', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/array/CP/current_status_display
        url = url_for('main.c2_get_array_current_status_display', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/array/CP/history
        url = url_for('main.c2_get_array_history', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/array/CP/status_display
        url = url_for('main.c2_get_array_status_display', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/array/CP/mission_display
        url = url_for('main.c2_get_array_mission_display', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # Bad array_code
        array_code='no_such_array'
        url = url_for('main.c2_get_array_abstract', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/array/no_such_array/current_status_display
        url = url_for('main.c2_get_array_current_status_display', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/array/no_such_array/history
        url = url_for('main.c2_get_array_history', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/array/no_such_array/status_display
        url = url_for('main.c2_get_array_status_display', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/array/no_such_array/mission_display
        url = url_for('main.c2_get_array_mission_display', array_code=array_code)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        if verbose: print '\n'

    def test_c2_platform_routes(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Test c2 platform routes (three platforms):
        Platform:  CP02PMCO-WFP01
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/abstract
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/current_status_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/ports_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/history
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/status_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/commands
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission/instruments_list

        Platform:  CP02PMCO-SBS01
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/abstract
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/current_status_display
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/ports_display
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/history
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/status_display
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/mission_display
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/commands
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/mission/instruments_list

        Platform:  CP02PMUI-RII01
        http://localhost:4000/c2/platform/CP02PMUI-RII01/abstract
        http://localhost:4000/c2/platform/CP02PMUI-RII01/current_status_display
        http://localhost:4000/c2/platform/CP02PMUI-RII01/ports_display
        http://localhost:4000/c2/platform/CP02PMUI-RII01/history
        http://localhost:4000/c2/platform/CP02PMUI-RII01/status_display
        http://localhost:4000/c2/platform/CP02PMUI-RII01/mission_display
        http://localhost:4000/c2/platform/CP02PMUI-RII01/commands
        http://localhost:4000/c2/platform/CP02PMUI-RII01/mission/instruments_list

        '''
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Instruments (used by /ports_display)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (platform deployment 1) instrument deployment 1
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        self.create_instrument_deployment(DOFSTK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 2
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        self.create_instrument_deployment(CTDPFK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 3
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'
        self.create_instrument_deployment(PARADK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        # (platform deployment 3) instrument deployment 1
        ADCPTG000_rd = 'CP02PMUI-RII01-02-ADCPTG000'
        self.create_instrument_deployment(ADCPTG000_rd, CP02PMUI_RII01_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - platform
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for platform in array_CP_platforms:

            if verbose: print '\nPlatform: ', platform

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/abstract
            url = url_for('main.c2_get_platform_abstract', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            # http://localhost:4000/c2/platform/CP02PMCO-WFP01/current_status_display
            url = url_for('main.c2_get_platform_current_status_display', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/ports_display
            url = url_for('main.c2_get_platform_ports_display', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('ports_display' in data)
            self.assertTrue(len(data['ports_display']) > 0)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/history
            url = url_for('main.c2_get_platform_history', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/status_display
            url = url_for('main.c2_get_platform_status_display', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_display
            url = url_for('main.c2_get_platform_mission_display', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/commands
            url = url_for('main.c2_get_platform_commands', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            # http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission/instruments_list
            url = url_for('main.c2_get_platform_mission_instruments_list', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

        if verbose: print '\n'

    def test_c2_platform_routes_negative(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Test a variety of urls, all using platform='BAD':
            http://localhost:4000/c2/platform/BAD/abstract
            http://localhost:4000/c2/platform/BAD/current_status_display
            http://localhost:4000/c2/platform/BAD/history
            http://localhost:4000/c2/platform/BAD/ports_display
            http://localhost:4000/c2/platform/BAD/status_display
            http://localhost:4000/c2/platform/BAD/mission_display
            http://localhost:4000/c2/platform/BAD/commands
            http://localhost:4000/c2/platform/BAD/mission_selections
            http://localhost:4000/c2/platform/BAD/mission_selection/mission4
        All shall return error (400) with following bad_request message (consistency):
            {
              "error": "bad request",
              "message": "unknown platform_deployment (reference_designator: 'BAD')"
            }
        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        error_text = "unknown platform_deployment (reference_designator: 'BAD')"
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # basic negative tests - platform is 'BAD'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        platform = 'BAD'
        # http://localhost:4000/c2/platform/BAD/abstract
        url = url_for('main.c2_get_platform_abstract', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/current_status_display
        url = url_for('main.c2_get_platform_current_status_display', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/history
        url = url_for('main.c2_get_platform_history', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/ports_display
        url = url_for('main.c2_get_platform_ports_display', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/status_display
        url = url_for('main.c2_get_platform_status_display', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/mission_display
        url = url_for('main.c2_get_platform_mission_display', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/commands
        url = url_for('main.c2_get_platform_commands', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/mission_selections
        url = url_for('main.c2_get_platform_mission_selections', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/BAD/mission_selection/mission4
        mission_plan_store = 'mission4'
        url = url_for('main.c2_get_platform_mission_selection', reference_designator=platform, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission/instruments_list
        url = url_for('main.c2_get_platform_mission_instruments_list', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # TODO platform with invalid operational status (400)

        if verbose: print '\n'

    def test_c2_instrument_routes(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        '''
        Exercise a variety of instrument routes:
        Instrument:  CP02PMCO-WFP01-02-DOFSTK000
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/streams
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/commands
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/history
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/status_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/mission_display

        Instrument:  CP02PMCO-WFP01-03-CTDPFK000
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/streams
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/commands
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/history
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/status_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/mission_display

        Instrument:  CP02PMCO-WFP01-05-PARADK000
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/streams
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/commands
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/history
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/status_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display

        Instrument:  CP02PMCO-SBS01-01-MOPAK0000
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/streams
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/commands
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/history
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/status_display
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/mission_display

        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/dofst_k_wfp_metadata/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k_stc_imodem_instrument/fields
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/mopak_o_dcl_accel/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_instrument/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_metadata/fields

        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Start data setup.
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
        #     3. platform deployment:       CP02PMUI_RII01
        #         instrument deployment(1): CP02PMUI-RII01-02-ADCPTG000
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create multiple instrument deployments for multiple platforms
        # Total number of instruments (5) created across all platforms (3)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        platform_instruments = []
        # (platform deployment 1) instrument deployment 1
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        DOFSTK000 = self.create_instrument_deployment(DOFSTK000_rd, CP02PMCO_WFP01_id)
        platform_instruments.append(DOFSTK000_rd)
        # (platform deployment 1) instrument deployment 2
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        CTDPFK000 = self.create_instrument_deployment(CTDPFK000_rd, CP02PMCO_WFP01_id)
        platform_instruments.append(CTDPFK000_rd)
        # (platform deployment 1) instrument deployment 3
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'
        PARADK000 = self.create_instrument_deployment(PARADK000_rd, CP02PMCO_WFP01_id)
        platform_instruments.append(PARADK000_rd)
        # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        MOPAK0000 = self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        platform_instruments.append(MOPAK0000_rd)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - instrument
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for instrument in platform_instruments:
            if verbose: print '\nInstrument: ', instrument

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/abstract
            url = url_for('main.c2_get_instrument_abstract', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/ports_display
            url = url_for('main.c2_get_instrument_ports_display', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/streams
            url = url_for('main.c2_get_instrument_streams', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/commands
            url = url_for('main.c2_get_instrument_commands', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/history
            url = url_for('main.c2_get_instrument_history', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/status_display
            url = url_for('main.c2_get_instrument_status_display', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display
            url = url_for('main.c2_get_instrument_mission_display', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)

        # Field specific tests
        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k_stc_imodem_instrument/parad_k_par
        instrument = PARADK000.reference_designator
        stream_name = 'parad_k_stc_imodem_instrument'
        field_name = 'parad_k_par'
        url = url_for('main.c2_get_instrument_stream_field', reference_designator=instrument,
                      stream_name=stream_name, field_name=field_name)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        res = {}
        res = data['field']
        # verify expected attributes are present
        self.assertTrue('units' in res)
        self.assertTrue('name' in res)
        self.assertTrue('value' in res)
        self.assertTrue('type' in res)
        valid_attributes = ['units','name','value','type']
        # verify only expected (valid) attributes for field
        for k,v in res.iteritems():
            self.assertTrue(k in valid_attributes)

        #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k_stc_imodem_instrument/fields
        #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/commands
        #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/dofst_k_wfp_metadata/fields

        if verbose: print '\n'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - instrument deployment fields
        # test fields for instrument_deployment stream_name
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/dofst_k_wfp_metadata/fields
        test_data = []
        test_data.append( (DOFSTK000.reference_designator, 'dofst_k_wfp_metadata' ) )
        test_data.append( (PARADK000.reference_designator, 'parad_k_stc_imodem_instrument' ) )
        test_data.append( (MOPAK0000.reference_designator, 'mopak_o_dcl_accel' ) )
        test_data.append( (CTDPFK000.reference_designator, 'ctdpf_ckl_wfp_instrument' ) )
        test_data.append( (CTDPFK000.reference_designator, 'ctdpf_ckl_wfp_metadata' ) )
        for data in test_data:
            instrument = data[0]
            stream = data[1]
            url = url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('fields' in data)
            self.assertTrue(len(data['fields']) > 0)

        if verbose: print '\n'

    def test_c2_instrument_routes_negative(self):
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Test instrument routes, all using instrument='BAD':
            http://localhost:4000/c2/instrument/BAD/abstract
            http://localhost:4000/c2/instrument/BAD/history
            http://localhost:4000/c2/instrument/BAD/ports_display
            http://localhost:4000/c2/instrument/BAD/status_display
            http://localhost:4000/c2/instrument/BAD/mission_display
            http://localhost:4000/c2/instrument/BAD/commands
            http://localhost:4000/c2/instrument/BAD/mission_selections
            http://localhost:4000/c2/instrument/BAD/mission_selection/mission4

        All shall return error (400) with following bad_request message (tested for consistency):
            {
              "error": "bad request",
              "message": "unknown platform_deployment (reference_designator: 'BAD')"
            }

        Additional negative tests:
            http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG000/commands
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/commands
            http://localhost:4000/c2/instrument//ctdpf_ckl_wfp_metadata/fields                      (*)
            http://localhost:4000/c2/instrument/no_such_instrument/ctdpf_ckl_wfp_metadata/fields
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000//fields                 (*)
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/no_such_stream/fields
            http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG000/streams
            http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG00XX/streams
            http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG00XX/history
            http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG00XX/history
        * empty url params, 404 is returned
        '''
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (platform deployment 1) instrument deployment 1
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        DOFSTK000 = self.create_instrument_deployment(DOFSTK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 2
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        CTDPFK000 = self.create_instrument_deployment(CTDPFK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 3
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'
        PARADK000 = self.create_instrument_deployment(PARADK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        MOPAK0000 = self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        # (platform deployment 3) instrument deployment 1
        ADCPTG000_rd = 'CP02PMUI-RII01-02-ADCPTG000'
        ADCPTG000 = self.create_instrument_deployment(ADCPTG000_rd, CP02PMUI_RII01_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #  End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        error_text = "unknown instrument_deployment (reference_designator: 'BAD')"
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # basic negative tests - instrument
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        instrument = 'BAD'
        # http://localhost:4000/c2/instrument/BAD/abstract
        url = url_for('main.c2_get_instrument_abstract', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/history
        url = url_for('main.c2_get_instrument_history', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/ports_display
        url = url_for('main.c2_get_instrument_ports_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/status_display
        url = url_for('main.c2_get_instrument_status_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/mission_display
        url = url_for('main.c2_get_instrument_mission_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/commands
        url = url_for('main.c2_get_instrument_commands', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/streams
        url = url_for('main.c2_get_instrument_streams', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/mission_selections
        url = url_for('main.c2_get_instrument_mission_selections', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # http://localhost:4000/c2/instrument/BAD/mission_selection/mission4
        mission_plan_store = 'mission4'
        url = url_for('main.c2_get_instrument_mission_selection', reference_designator=instrument, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertEquals(data['message'], error_text)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic negative tests - instrument
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG000/commands
        # message: "Failed to retrieve commands for instrument (reference designator 'CP02PMUI-RII01-02-ADCPTG000')"
        instrument = ADCPTG000.reference_designator #'CP02PMUI-RII01-02-ADCPTG000'
        url = url_for('main.c2_get_instrument_commands', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/commands
        instrument = CTDPFK000.reference_designator #'CP02PMCO-WFP01-03-CTDPFK000'
        url = url_for('main.c2_get_instrument_commands', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        #  Negative tests for: /c2/instrument/reference_designator/stream_name/fields
        # http://localhost:4000/c2/instrument//ctdpf_ckl_wfp_metadata/fields
        instrument = ''
        stream = 'ctdpf_ckl_wfp_metadata'
        url = url_for('main.c2_get_instrument_fields',reference_designator=instrument, stream_name=stream)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/instrument/no_such_instrument/ctdpf_ckl_wfp_metadata/fields
        # response is (400) bad_request: "Invalid reference designator for instrument ('no_such_instrument')."
        instrument = 'no_such_instrument'
        stream = 'ctdpf_ckl_wfp_metadata'
        url = url_for('main.c2_get_instrument_fields',reference_designator=instrument, stream_name=stream)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        # http://localhost:4000/c2/instrument//ctdpf_ckl_wfp_metadata/fields
        instrument = CTDPFK000.reference_designator
        stream = ''
        url = url_for('main.c2_get_instrument_fields',reference_designator=instrument, stream_name=stream)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/no_such_stream/fields
        # response is (400) bad_request: "Invalid stream name ('no_such_stream') for instrument ('CP02PMCO-WFP01-03-CTDPFK000')"
        instrument = CTDPFK000.reference_designator
        stream = 'no_such_stream'
        url = url_for('main.c2_get_instrument_fields', reference_designator=instrument, stream_name=stream)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        # instrument - negative test (instrument does not have streams)
        # "Failed to retrieve streams for instrument (reference designator 'CP02PMUI-RII01-02-ADCPTG000')"
        # http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG000/streams
        valid_instrument_no_streams = ADCPTG000.reference_designator #'CP02PMUI-RII01-02-ADCPTG000'
        url = url_for('main.c2_get_instrument_streams', reference_designator=valid_instrument_no_streams)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        # Negative tests for invalid instrument - 400 same message for all! CHECK
        # http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG000XX/streams
        # "unknown instrument (reference_designator: 'CP02PMUI-RII01-02-ADCPTG0XXX')"
        invalid_instrument_no_streams = 'CP02PMUI-RII01-02-ADCPTG00XX'
        url = url_for('main.c2_get_instrument_streams', reference_designator=invalid_instrument_no_streams)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        if verbose: print '\n'


    def test_c2_mission_routes(self):
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Exercises a variety of routes:
            http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selections
            http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/mission4
            http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/no_such_mission_store
            http://localhost:4000/c2/platform//mission_selection/mission4
            http://localhost:4000/c2/platform//mission_selection/no_such_mission_store
            http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/
            http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/empty_mission
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selections
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selection/mission4
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selection/mission_does_not_exist
        '''
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (platform deployment 1) instrument deployment 1
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        DOFSTK000 = self.create_instrument_deployment(DOFSTK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 2
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        CTDPFK000 = self.create_instrument_deployment(CTDPFK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 1) instrument deployment 3
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'
        PARADK000 = self.create_instrument_deployment(PARADK000_rd, CP02PMCO_WFP01_id)
        # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        MOPAK0000 = self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        # (platform deployment 3) instrument deployment 1
        ADCPTG000_rd = 'CP02PMUI-RII01-02-ADCPTG000'
        ADCPTG000 = self.create_instrument_deployment(ADCPTG000_rd, CP02PMUI_RII01_id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - Mission Control
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        platform = CP02PMCO_WFP01.reference_designator

        #http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selections
        url = url_for('main.c2_get_platform_mission_selections', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        #http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/mission4
        mission_plan_store = 'mission4'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # mission - negative tests
        # http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/no_such_mission_store
        bad_mission_plan_store = 'no_such_mission_store'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=bad_mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        contents = json.loads(response.data)
        self.assertTrue(contents != None)
        self.assertTrue('mission_plan' in contents)
        self.assertTrue(contents['mission_plan'] != None)
        self.assertTrue(len(contents['mission_plan']) == 0)

        # http://localhost:4000/c2/platform//mission_selection/mission4
        empty_platform = ''
        mission_plan_store = 'mission4'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=empty_platform, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/platform//mission_selection/no_such_mission_store
        empty_platform = ''
        bad_mission_plan_store = 'no_such_mission_store'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=empty_platform, mission_plan_store=bad_mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/
        empty_mission_plan_store = ''
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=empty_mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_selection/empty_mission
        mission_plan_store = 'empty_mission'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        contents = json.loads(response.data)
        self.assertTrue(contents != None)
        self.assertTrue('mission_plan' in contents)
        self.assertTrue(contents['mission_plan'] != None)
        self.assertTrue(len(contents['mission_plan']) == 0)

        # Instruments Mission (positive)
        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display
        instrument = PARADK000.reference_designator #'CP02PMCO-WFP01-05-PARADK000'
        url = url_for('main.c2_get_instrument_mission_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selections
        url = url_for('main.c2_get_instrument_mission_selections', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selection/mission4
        mission_plan_store = 'mission4'
        url = url_for('main.c2_get_instrument_mission_selection',
                        reference_designator=instrument, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selection/mission_does_not_exist
        mission_plan_store_does_not_exist = 'mission_does_not_exist'
        url = url_for('main.c2_get_instrument_mission_selection',
                        reference_designator=instrument, mission_plan_store=mission_plan_store_does_not_exist)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        if verbose: print '\n'

    def _c2_instrument_update_field(self):
        #TODO use this test during development only since it modifies data files
        #TODO disable before check in (remove prefix test from def name)
        #TODO enable when file based data is no longer used for testing

        field_name = 'control_Int32'
        field_type = 'Int32'
        field_value = '37'
        delta = 277
        self._instrument_update_fields(field_name, field_type, field_value, delta)

        field_name = 'control_Float32'
        field_type = 'Float32'
        field_value = '0.0101010101'
        delta = 10.5
        self._instrument_update_fields(field_name, field_type, field_value, delta)

        field_name = 'control_String'
        field_type = 'String'
        field_value = 'ok'
        delta = '*'
        self._instrument_update_fields(field_name, field_type, field_value, delta)

    def _instrument_update_fields(self, const_field_name, constant_type, original_field_value, delta):
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        debug = False
        if debug: print '\n\ntest_instrument_update_fields (type=%s) (debug on)' % constant_type
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # for an instrument stream, get original field value, set to new value and check, then set back to original value
        # e.g. set field_name 'control_TYPENAME' from original_value to original_value+delta, then back to original_value
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Platform - (using platform 2 (CP02PMCO_SBS01))
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Instrument (Create instrument deployment for platform 2)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        MOPAK0000 = self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01_id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests for instrument_update route
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # set constants to be held throughout unit test; only variable is field_value
        const_instrument = MOPAK0000.reference_designator
        self.assertEquals(const_instrument, MOPAK0000_rd)
        const_stream_name = 'mopak_o_dcl_accel'
        const_command_name = 'SET'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET instrument stream original fields; save to restore values
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug: print '\nGET current field_value'
        response = self.GET_instrument_fields(verbose, const_instrument, const_stream_name)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        # check data
        self.assertTrue(len(data) > 0)
        self.assertTrue('fields' in data)
        # create a list_of_fields from response.data
        list_of_fields = data['fields']
        self.assertTrue(list_of_fields != None)
        self.assertTrue(len(list_of_fields) > 0)
        # create keyed dict for original fields (dict key='name'); save
        original_fields = self.get_fields(list_of_fields)
        # check original field name and value
        self.assertTrue(original_fields[const_field_name]['name'] == const_field_name)
        s_original_field_value = original_fields[const_field_name]['value']
        original_field_type = original_fields[const_field_name]['type']
        self.assertEquals(original_field_type, constant_type)
        try:
            if constant_type == 'Int32' or constant_type == 'Int64':
                original_field_value = int(s_original_field_value)
            elif constant_type == 'String':
                original_field_value = str(s_original_field_value)
            elif constant_type == 'Float32' or constant_type == 'Float64':
                original_field_value = float(s_original_field_value)
            else:
                raise Exception('')
        except:
            # Raise error to fail test
            if constant_type == 'Int32' or constant_type == 'Int64':
                self.assertTrue('original field value not of type Int' == 0)
            elif constant_type == 'String':
                self.assertTrue('original field value not of type String' == 0)
            elif constant_type == 'Float32' or constant_type == 'Float64':
                self.assertTrue('original field value not of type Float' == 0)
            else:
                self.assertTrue('original field value not of type specified' == 0)
        if debug:
            print 'field name:  \'%s\'' % const_field_name
            print 'field value: %r' % original_field_value
            print 'field delta: %r' % delta
            print 'field type: \'%s\'\n' % original_field_type
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # PUT new value (new_field_value=original_field_value = '*')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug: print 'PUT new field_value'
        new_field_value = original_field_value + delta
        response = self.PUT_instrument_update(verbose, const_instrument, const_stream_name, const_field_name,
                                              const_command_name, new_field_value)
        self.assertTrue(response.status_code == 200)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET to verify new value applied to field_name; verify other values remain same
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug: print 'GET verify new field_value'
        response = self.GET_instrument_fields(verbose, const_instrument, const_stream_name)
        self.assertTrue(response.status_code == 200)
        # check data
        data = json.loads(response.data)
        self.assertTrue(len(data) > 0)
        self.assertTrue('fields' in data)
        # create a new_list_of_fields from response.data
        new_list_of_fields = data['fields']
        self.assertTrue(new_list_of_fields != None)
        self.assertTrue(len(new_list_of_fields) > 0)
        # create keyed dict for new fields (dict key='name'); save
        new_fields = self.get_fields(new_list_of_fields)
        if debug:
            print 'field_name:  ', const_field_name
            print 'new_field_value: \'%r\'\n' % new_field_value
        try:
            if constant_type == 'Int32' or constant_type == 'Int64':
                new_field_value_returned = int(new_fields[const_field_name]['value'])
                self.assertTrue(new_field_value_returned == new_field_value)
            elif constant_type == 'String':
                new_field_value_returned = str(new_fields[const_field_name]['value'])
                self.assertTrue(new_field_value_returned == new_field_value)
            elif constant_type == 'Float32' or constant_type == 'Float64':
                new_field_value_returned = float(new_fields[const_field_name]['value'])
                self.assertTrue(new_field_value_returned == new_field_value)
            else:
                raise Exception('')
        except:
            # Raise error to fail test
            if constant_type == 'Int32' or constant_type == 'Int64':
                self.assertTrue('original field value not of type Int' == 0)
            elif constant_type == 'String':
                self.assertTrue('original field value not of type String' == 0)
            elif constant_type == 'Float32' or constant_type == 'Float64':
                self.assertTrue('original field value not of type Float' == 0)
            else:
                self.assertTrue('original field value not of type specified' == 0)

        self.assertTrue(new_fields[const_field_name]['name'] == const_field_name)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # PUT original field_value (field_value=original_field_value)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # verify original value applied and TODO verify other values remain same
        if debug: print 'PUT original field_value'
        response = self.PUT_instrument_update(verbose, const_instrument, const_stream_name, const_field_name,
                                              const_command_name, original_field_value)
        self.assertTrue(response.status_code == 200)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET - verify contents - should be in original state (restored_list_of_fields=original_fields)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug: print 'GET to verify back to original field_value'
        response = self.GET_instrument_fields(verbose, const_instrument, const_stream_name)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        #check data
        self.assertTrue(len(data) > 0)
        self.assertTrue('fields' in data)
        # create a restored_list_of_fields from response.data
        restored_list_of_fields = data['fields']
        self.assertTrue(list_of_fields != None)
        self.assertTrue(len(list_of_fields) > 0)
        # create keyed dict for restored fields (dict key='name')
        restored_fields = self.get_fields(restored_list_of_fields)
        try:
            if constant_type == 'Int32' or constant_type == 'Int64':
                restored_field_value = int(restored_fields[const_field_name]['value'])
            elif constant_type == 'String':
                restored_field_value = str(restored_fields[const_field_name]['value'])
            elif constant_type == 'Float32' or constant_type == 'Float64':
                restored_field_value = float(restored_fields[const_field_name]['value'])
            else:
                raise Exception()
        except:
            # Raise error to fail test
            if constant_type == 'Int32' or constant_type == 'Int64':
                self.assertTrue('original field value not of type Int' == 0)
            elif constant_type == 'String':
                self.assertTrue('original field value not of type String' == 0)
            elif constant_type == 'Float32' or constant_type == 'Float64':
                self.assertTrue('original field value not of type Float' == 0)
            else:
                self.assertTrue('original field value not of type specified' == 0)

        self.assertTrue(restored_field_value == original_field_value)
        if debug:
            print 'field_name:  ', const_field_name
            print 'field_value: %r' % restored_field_value

    # helpers
    def get_fields(self, list_of_fields):
        # for convenience, create keyed dict for original fields (key='name'), return dict
        original_fields = {}
        for item in list_of_fields:
            self.assertTrue('name' in item)
            field_name = item['name']
            if field_name not in original_fields:
                original_fields[field_name] = item
        self.assertTrue(len(original_fields) > 0)
        return original_fields

    def GET_instrument_fields(self, verbose, reference_designator, stream_name):
        '''
        data:
        {"fields": [
                    {
                      "id": 1,
                      "name": "parad_k_par",
                      "type": "Float32",
                      "units": "umol photons m-2 s-1",
                      "value": "0.27"
                    },
                    {
                      "id": 2,
                      "name": "preferred_timestamp",
                      "type": "String",
                      "units": "1",
                      "value": "internal_timestamp"
                    },...
                    ]
        '''
        root = self.root
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        url = url_for('main.c2_get_instrument_fields',reference_designator=reference_designator,stream_name=stream_name)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        return response

    def PUT_instrument_update(self, verbose, reference_designator, stream_name, field_name, command_name, field_value):
        root = self.root
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        url = url_for('main.c2_update_instrument_field_value',
                        reference_designator=reference_designator, stream_name=stream_name,
                        field_name=field_name, command_name=command_name, field_value=field_value)
        if verbose: print root+url
        response = self.client.put(url,content_type=content_type, headers=headers)
        return response