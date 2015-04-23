#!/usr/bin/env python
'''
Specific testing for Command and Control (C2)
'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
import datetime as dt

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class CommandAndControlTestCase(unittest.TestCase):

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

    def get_api_post_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
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
        elif platform_reference_designator == 'CP02PMCI-WFP01':
            CP02PMCI_WFP01    = PlatformDeployment(reference_designator=platform_reference_designator)
            CP02PMCI_WFP01.reference_designator = platform_reference_designator
            CP02PMCI_WFP01.display_name = 'CP02PMCI_WFP01 display_name'
            CP02PMCI_WFP01.array_id = 3
            db.session.add(CP02PMCI_WFP01)
            db.session.commit()
            platform_deployment = CP02PMCI_WFP01
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

        # platform deployment 4
        CP02PMCI_WFP01_rd = 'CP02PMCI-WFP01'
        CP02PMCI_WFP01 = self.create_platform_deployment(CP02PMCI_WFP01_rd)

        return CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01

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

        elif instrument_reference_designator == 'CP02TEST-SBS01-01-MOPAK0000':
            test = InstrumentDeployment(reference_designator=instrument_reference_designator)
            test.depth = 1000.0
            test.display_name = 'Test instrument'
            test.end_date = dt.datetime.now()
            test.geo_location = 'POINT(-70 40)'
            test.platform_deployment_id = platform_deployment_id
            test.reference_designator = instrument_reference_designator
            test.start_date = dt.datetime.now()
            db.session.add(test)
            db.session.commit()
            instrument_deployment = test
        elif instrument_reference_designator == 'CP02PMCI-WFP01-03-CTDPFK000':
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
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = 'CP02PMCO-WFP01'
        CP02PMCO_SBS01_rd = 'CP02PMCO-SBS01'
        CP02PMUI_RII01_rd = 'CP02PMUI-RII01'
        CP02PMCI_WFP01_rd = 'CP02PMCI-WFP01'
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # platform deployment 4
        CP02PMCI_WFP01_id = CP02PMCI_WFP01.id
        array_CP_platforms.append(CP02PMCI_WFP01_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Total number of instruments to be created across all platforms
        number_of_instruments = 6
        platform_1_instrument_count = 3
        platform_2_instrument_count = 1
        platform_3_instrument_count = 1
        platform_4_instrument_count = 1

        platform_1_instrument_deployments = []
        platform_2_instrument_deployments = []
        platform_3_instrument_deployments = []
        platform_4_instrument_deployments = []
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

        # (platform deployment 4) instrument deployment 1
        _CTDPFK000_rd = 'CP02PMCI-WFP01-03-CTDPFK000'
        _CTDPFK000 = self.create_instrument_deployment(_CTDPFK000_rd, CP02PMCI_WFP01_id)
        _CTDPFK000_id = _CTDPFK000.id
        platform_4_instrument_deployments.append(_CTDPFK000_rd)

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

        # Get instrument _CTDPFK000 (latform deployment 4)
        response = self.client.get(url_for('main.get_instrument_deployment', id=CTDPFK000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        _CTDPFK000_data = json.loads(response.data[:])
        self.assertTrue('platform_deployment_id' in _CTDPFK000_data)
        self.assertTrue(_CTDPFK000_data['platform_deployment_id'], CP02PMCI_WFP01_id)
        self.assertTrue(self._check_instrument_deployment_fields_provided(_CTDPFK000_data))
        # Verify (a) all required fields provided, todo  (b)content as expected and (c) geo_location not null

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup and verification.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Now have two arrays, four platforms, each populated with instruments
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
        http://localhost:4000/c2/array/CE/mission_display

        Array:  GP
        http://localhost:4000/c2/array/GP/abstract
        http://localhost:4000/c2/array/GP/current_status_display
        http://localhost:4000/c2/array/GP/history
        http://localhost:4000/c2/array/GP/mission_display

        Array:  CP
        http://localhost:4000/c2/array/CP/abstract
        http://localhost:4000/c2/array/CP/current_status_display
        http://localhost:4000/c2/array/CP/history
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
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        CP02PMCI_WFP01_rd = CP02PMCI_WFP01.reference_designator
        # platform deployment 1
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # platform deployment 4
        array_CP_platforms.append(CP02PMCI_WFP01_rd)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, four platforms, each populated with instruments)
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
        self.assertEquals(response.status_code, 200)
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
            self.assertEquals(response.status_code, 200)
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
                self.assertEquals(len(data['current_status_display']), 0)
            # http://localhost:4000/c2/array/CP/history
            url = url_for('main.c2_get_array_history', array_code=array_code)
            if verbose: print root+url
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)

            # http://localhost:4000/c2/array/CP/mission_display
            url = url_for('main.c2_get_array_mission_display', array_code=array_code)
            if verbose: print root+url
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)

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
            http://localhost:4000/c2/array//mission_display

        Following tests should generate bad_request (400), with consistent error message:
            http://localhost:4000/c2/array/no_such_array/abstract
            http://localhost:4000/c2/array/no_such_array/current_status_display
            http://localhost:4000/c2/array/no_such_array/history
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
        #     4. platform deployment:       CP02PMCI-WFP01
        #         instrument deployment(1): CP02PMCI-WFP01-03-CTDPFK000
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type = 'application/json'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        CP02PMCI_WFP01_rd = CP02PMCI_WFP01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # platform deployment 4
        CP02PMCI_WFP01_id = CP02PMCI_WFP01.id
        array_CP_platforms.append(CP02PMCI_WFP01_rd)

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
        # (platform deployment 4) instrument deployment 1
        _CTDPFK000_rd = 'CP02PMCI-WFP01-03-CTDPFK000'
        self.create_instrument_deployment(_CTDPFK000_rd, CP02PMCI_WFP01_id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, four platforms, each populated with instruments)
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
        Test c2 platform routes (four platforms):
        Platform:  CP02PMCO-WFP01
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/abstract
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/current_status_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/ports_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/history
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_display
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/commands
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission/instruments_list

        Platform:  CP02PMCO-SBS01
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/abstract
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/current_status_display
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/ports_display
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/history
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/mission_display
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/commands
        http://localhost:4000/c2/platform/CP02PMCO-SBS01/mission/instruments_list

        Platform:  CP02PMUI-RII01
        http://localhost:4000/c2/platform/CP02PMUI-RII01/abstract
        http://localhost:4000/c2/platform/CP02PMUI-RII01/current_status_display
        http://localhost:4000/c2/platform/CP02PMUI-RII01/ports_display
        http://localhost:4000/c2/platform/CP02PMUI-RII01/history
        http://localhost:4000/c2/platform/CP02PMUI-RII01/mission_display
        http://localhost:4000/c2/platform/CP02PMUI-RII01/commands
        http://localhost:4000/c2/platform/CP02PMUI-RII01/mission/instruments_list

        Platform:  CP02PMCI-WFP01
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/abstract
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/current_status_display
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/ports_display
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/history
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_display
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/commands
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission/instruments_list

        Manually testing RS:
        http://localhost:4000/c2/platform/RS03ASHS-ID03A/abstract
        http://localhost:4000/c2/platform/RS03ASHS-ID03A/current_status_display
        http://localhost:4000/c2/platform/RS03ASHS-ID03A/ports_display
        http://localhost:4000/c2/platform/RS03ASHS-ID03A/history
        *http://localhost:4000/c2/platform/RS03ASHS-ID03A/mission_display
        http://localhost:4000/c2/platform/RS03ASHS-ID03A/commands
        http://localhost:4000/c2/platform/RS03ASHS-ID03A/mission/instruments_list

        http://localhost:4000/c2/instrument/RS03ASHS-ID03A-06-CAMHDA301/abstract
        http://localhost:4000/c2/instrument/RS03ASHS-ID03A-06-CAMHDA301/commands
        http://localhost:4000/c2/instrument/RS03ASHS-ID03A-06-CAMHDA301/history
        http://localhost:4000/c2/instrument/RS03ASHS-ID03A-06-CAMHDA301/ports_display

        http://localhost:4000/c2/instrument/RS03ASHS-MJ03B-05-OBSSPA302/abstract
        http://localhost:4000/c2/instrument/RS03ASHS-MJ03B-05-OBSSPA302/commands
        http://localhost:4000/c2/instrument/RS03ASHS-MJ03B-05-OBSSPA302/ports_display
        '''
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        CP02PMCI_WFP01_rd = CP02PMCI_WFP01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # platform deployment 1
        CP02PMCI_WFP01_id = CP02PMCI_WFP01.id
        array_CP_platforms.append(CP02PMCI_WFP01_rd)

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
        # (platform deployment 4) instrument deployment 1
        _CTDPFK000_rd = 'CP02PMCI-WFP01-03-CTDPFK000'
        self.create_instrument_deployment(_CTDPFK000_rd, CP02PMCI_WFP01_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, four platforms, each populated with instruments)
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
            self.assertEquals(response.status_code, 200)

            # http://localhost:4000/c2/platform/CP02PMCO-WFP01/current_status_display
            url = url_for('main.c2_get_platform_current_status_display', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/ports_display
            url = url_for('main.c2_get_platform_ports_display', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('ports_display' in data)
            if platform == CP02PMCI_WFP01_rd:
                self.assertTrue(len(data['ports_display']) > 0)
            else:
                self.assertEquals(len(data['ports_display']), 0)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/history
            url = url_for('main.c2_get_platform_history', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission_display
            url = url_for('main.c2_get_platform_mission_display', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)

            #http://localhost:4000/c2/platform/CP02PMCO-WFP01/commands
            url = url_for('main.c2_get_platform_commands', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)

            # http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission/instruments_list
            url = url_for('main.c2_get_platform_mission_instruments_list', reference_designator=platform)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)

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
            http://localhost:4000/c2/platform/BAD/mission_display
            http://localhost:4000/c2/platform/BAD/commands
            http://localhost:4000/c2/platform/BAD/mission_selections
            http://localhost:4000/c2/platform/BAD/mission_selection/mission4
        All shall return error (400) with following bad_request message (consistency):
            {
              "error": "bad request",
              "message": "unknown platform_deployment ('BAD')"
            }
        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        error_text = "unknown platform_deployment ('BAD')"
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # basic negative tests - platform is 'BAD'
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        platform = 'BAD'
        # http://localhost:4000/c2/platform/BAD/abstract
        url = url_for('main.c2_get_platform_abstract', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('abstract' in data)
        self.assertEquals(len(data['abstract']), 0)

        # http://localhost:4000/c2/platform/BAD/current_status_display
        url = url_for('main.c2_get_platform_current_status_display', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('current_status_display' in data)
        self.assertEquals(len(data['current_status_display']), 0)

        # http://localhost:4000/c2/platform/BAD/history
        url = url_for('main.c2_get_platform_history', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('history' in data)
        self.assertEquals(len(data['history']), 0)

        # http://localhost:4000/c2/platform/BAD/ports_display
        url = url_for('main.c2_get_platform_ports_display', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('ports_display' in data)
        self.assertEquals(len(data['ports_display']), 0)

        # http://localhost:4000/c2/platform/BAD/mission_display
        url = url_for('main.c2_get_platform_mission_display', reference_designator=platform)
        if verbose: print root+url

        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)

        self.assertTrue('mission_display' in data)
        self.assertEquals(len(data['mission_display']), 0)

        # http://localhost:4000/c2/platform/BAD/commands
        url = url_for('main.c2_get_platform_commands', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('commands' in data)
        self.assertEquals(len(data['commands']), 0)

        # http://localhost:4000/c2/platform/BAD/mission_selections
        url = url_for('main.c2_get_platform_mission_selections', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_selections' in data)
        self.assertEquals(len(data['mission_selections']), 0)

        # http://localhost:4000/c2/platform/BAD/mission_selection/mission4
        mission_plan_store = 'mission4'
        url = url_for('main.c2_get_platform_mission_selection', reference_designator=platform, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_plan' in data)
        self.assertEquals(len(data['mission_plan']), 0)

        # http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission/instruments_list
        url = url_for('main.c2_get_platform_mission_instruments_list', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('instruments' in data)
        self.assertEquals(len(data['instruments']), 0)

        if verbose: print '\n'

    def test_c2_instrument_routes(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        debug = False
        '''
        Exercise a variety of instrument routes:
        Instrument:  CP02PMCO-WFP01-02-DOFSTK000
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/status
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/history
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/mission_display

        Instrument:  CP02PMCO-WFP01-03-CTDPFK000
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/status
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/history
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/mission_display

        Instrument:  CP02PMCO-WFP01-05-PARADK000
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/status
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/history
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display

        Instrument:  CP02PMCO-SBS01-01-MOPAK0000
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/abstract
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/status
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/history
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/mission_display

        Instrument:  CP02PMCI-WFP01-03-CTDPFK000
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/abstract
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/ports_display
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/status
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/history
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/mission_display

        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Start data setup.
        # Summary: 2 platform deployments, three instrument deployments
        # Contents:
        #     1. platform deployment:       CP02PMCO-WFP01
        #         instrument deployment(1): CP02PMCO-WFP01-02-DOFSTK000,
        #                              (2): CP02PMCO-WFP01-03-CTDPFK000
        #                              (3): CP02PMCO-WFP01-05-PARADK000
        #     2. platform deployment:       CP02PMCO-SBS01
        #         instrument deployment(1): CP02PMCO-SBS01-01-MOPAK0000
        #     3. platform deployment:       CP02PMUI_RII01
        #         instrument deployment(1): CP02PMUI-RII01-02-ADCPTG000
        #     4. platform deployment:       CP02PMCI-WFP01
        #         instrument deployment(1): CP02PMCI-WFP01-03-CTDPFK000
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        CP02PMCI_WFP01_rd = CP02PMCI_WFP01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # platform deployment 4
        CP02PMCI_WFP01_id = CP02PMCI_WFP01.id
        array_CP_platforms.append(CP02PMCI_WFP01_rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create multiple instrument deployments for multiple platforms
        # Total number of instruments (6) created across all platforms (4)
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
        # (platform deployment 4) instrument deployment 1
        _CTDPFK000_rd = 'CP02PMCI-WFP01-03-CTDPFK000'
        _CTDPFK000 = self.create_instrument_deployment(_CTDPFK000_rd, CP02PMCI_WFP01_id)
        platform_instruments.append(_CTDPFK000_rd)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, four platforms, each populated with instruments)
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

            # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/abstract
            # http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/abstract
            url = url_for('main.c2_get_instrument_abstract', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('abstract' in data)
            result = data['abstract']
            if instrument == _CTDPFK000_rd:
                self.assertTrue(result> 0)
            else:
                self.assertEquals(len(result), 0)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/ports_display
            url = url_for('main.c2_get_instrument_ports_display', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('ports_display' in data)
            result = data['ports_display']
            if instrument == _CTDPFK000_rd:
                self.assertTrue(result> 0)
            else:
                self.assertEquals(len(result), 0)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/commands
            url = url_for('main.c2_get_instrument_driver_status', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            if instrument == _CTDPFK000_rd:
                self.assertEquals(response.status_code, 200)
            else:
                self.assertEquals(response.status_code, 400)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/history
            url = url_for('main.c2_get_instrument_history', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('history' in data)
            result = data['history']
            if instrument == _CTDPFK000_rd:
                self.assertTrue(result> 0)
            else:
                self.assertEquals(len(result), 0)

            #http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display
            url = url_for('main.c2_get_instrument_mission_display', reference_designator=instrument)
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('mission_display' in data)
            result = data['mission_display']
            if instrument == _CTDPFK000_rd:
                self.assertTrue(result> 0)
            else:
                self.assertEquals(len(result), 0)

    def test_c2_instrument_routes_negative(self):
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Test instrument routes, all using instrument='BAD':
            http://localhost:4000/c2/instrument/BAD/abstract
            http://localhost:4000/c2/instrument/BAD/history
            http://localhost:4000/c2/instrument/BAD/ports_display
            http://localhost:4000/c2/instrument/BAD/mission_display
            http://localhost:4000/c2/instrument/BAD/commands
            http://localhost:4000/c2/instrument/BAD/mission_selections
            http://localhost:4000/c2/instrument/BAD/mission_selection/mission4

        Additional negative tests:
            http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG000/commands
            http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/commands
            http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG0XX/history

        Note, when empty url params, 404 is returned
        '''
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        CP02PMCI_WFP01_rd = CP02PMCI_WFP01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # platform deployment 4
        CP02PMCI_WFP01_id = CP02PMCI_WFP01.id
        array_CP_platforms.append(CP02PMCI_WFP01_rd)

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
        # (platform deployment 4) instrument deployment 1
        _CTDPFK000_rd = 'CP02PMCI-WFP01-03-CTDPFK000'
        _CTDPFK000 = self.create_instrument_deployment(_CTDPFK000_rd, CP02PMCI_WFP01_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #  End of data setup. (Now have three arrays, four platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # basic negative tests - instrument
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        instrument = 'BAD'
        # http://localhost:4000/c2/instrument/BAD/abstract
        url = url_for('main.c2_get_instrument_abstract', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('abstract' in data)
        self.assertEquals(len(data['abstract']), 0)

        # http://localhost:4000/c2/instrument/BAD/history
        url = url_for('main.c2_get_instrument_history', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('history' in data)
        self.assertEquals(len(data['history']), 0)

        # http://localhost:4000/c2/instrument/BAD/ports_display
        url = url_for('main.c2_get_instrument_ports_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('ports_display' in data)
        self.assertEquals(len(data['ports_display']), 0)

        # http://localhost:4000/c2/instrument/BAD/mission_display
        url = url_for('main.c2_get_instrument_mission_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_display' in data)
        self.assertEquals(len(data['mission_display']), 0)

        # http://localhost:4000/c2/instrument/BAD/commands
        url = url_for('main.c2_get_instrument_driver_status', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertTrue(len(data['message']) > 0)

        # http://localhost:4000/c2/instrument/BAD/mission_selections
        url = url_for('main.c2_get_instrument_mission_selections', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_selections' in data)
        self.assertEquals(len(data['mission_selections']), 0)

        # http://localhost:4000/c2/instrument/BAD/mission_selection/mission4
        mission_plan_store = 'mission4'
        url = url_for('main.c2_get_instrument_mission_selection', reference_designator=instrument, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_plan' in data)
        self.assertEquals(len(data['mission_plan']), 0)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic negative tests - instrument
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG000/commands
        # message: "Failed to retrieve commands for instrument ('CP02PMUI-RII01-02-ADCPTG000')"
        instrument = ADCPTG000.reference_designator #'CP02PMUI-RII01-02-ADCPTG000'
        url = url_for('main.c2_get_instrument_driver_status', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 400)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/commands
        instrument = CTDPFK000.reference_designator #'CP02PMCO-WFP01-03-CTDPFK000'
        url = url_for('main.c2_get_instrument_driver_status', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 400)

        # http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/status
        instrument = _CTDPFK000.reference_designator #'CP02PMCI-WFP01-03-CTDPFK000'
        url = url_for('main.c2_get_instrument_driver_status', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)

        #http://localhost:4000/c2/instrument/CP02PMUI-RII01-02-ADCPTG00XX/history
        invalid_instrument = 'CP02PMUI-RII01-02-ADCPTG0XX'
        url = url_for('main.c2_get_instrument_history', reference_designator=invalid_instrument)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('history' in data)
        self.assertEquals(len(data['history']), 0)

        if verbose: print '\n'

    def test_c2_mission_routes(self):
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Exercises a variety of routes:

        Mission Control - Platforms (positive)
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selections
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/mission4

        Mission Control - Platforms (negative)
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/no_such_mission_store
        http://localhost:4000/c2/platform//mission_selection/mission4
        http://localhost:4000/c2/platform//mission_selection/no_such_mission_store
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/
        http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/empty_mission

        Mission Control - Instruments (positive)
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/mission_display
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/mission_selection/mission4

        Mission Control - Instruments (negative)
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_display
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selections
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/mission_selection/mission4
        http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/mission_selection/mission_does_not_exist
        '''
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Setup data - Arrays and Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.setup_array_data()
        array_CP_platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01, CP02PMCI_WFP01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        CP02PMCI_WFP01_rd = CP02PMCI_WFP01.reference_designator
        # platform deployment 1
        CP02PMCO_WFP01_id = CP02PMCO_WFP01.id
        array_CP_platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        CP02PMCO_SBS01_id = CP02PMCO_SBS01.id
        array_CP_platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        CP02PMUI_RII01_id = CP02PMUI_RII01.id
        array_CP_platforms.append(CP02PMUI_RII01_rd)
        # platform deployment 4
        CP02PMCI_WFP01_id = CP02PMCI_WFP01.id
        array_CP_platforms.append(CP02PMCI_WFP01_rd)
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
        # (platform deployment 4) instrument deployment 1
        _CTDPFK000_rd = 'CP02PMCI-WFP01-03-CTDPFK000'
        _CTDPFK000 = self.create_instrument_deployment(_CTDPFK000_rd, CP02PMCI_WFP01_id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, four platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with C2 tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - Mission Control - Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n'
        if verbose: print 'Mission Control - Platforms (positive)'
        platform = CP02PMCI_WFP01.reference_designator

        #http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selections
        url = url_for('main.c2_get_platform_mission_selections', reference_designator=platform)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_selections' in data)
        result = data['mission_selections']
        self.assertTrue(result != None)
        self.assertEquals(len(result), 5)

        # http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/mission4  (POSITIVE)
        mission_plan_store_name = 'mission4'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=mission_plan_store_name)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_plan' in data)
        result = data['mission_plan']
        self.assertTrue(result != None)
        self.assertTrue(len(result) > 0)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic negative tests - Mission Control - Platforms
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/no_such_mission_store
        if verbose: print '\n'
        if verbose: print 'Mission Control - Platforms (negative)'
        bad_mission_plan_store_name = 'no_such_mission_store'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=bad_mission_plan_store_name)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        contents = json.loads(response.data)
        self.assertTrue(contents != None)
        self.assertTrue('mission_plan' in contents)
        self.assertTrue(contents['mission_plan'] != None)
        self.assertTrue(len(contents['mission_plan']) == 0)

        # http://localhost:4000/c2/platform//mission_selection/mission4
        empty_platform = ''
        mission_plan_store_name = 'mission4'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=empty_platform, mission_plan_store=mission_plan_store_name)
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

        # http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/
        empty_mission_plan_store = ''
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=empty_mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 404)

        # http://localhost:4000/c2/platform/CP02PMCI-WFP01/mission_selection/empty_mission
        mission_plan_store = 'empty_mission'
        url = url_for('main.c2_get_platform_mission_selection',
                        reference_designator=platform, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        contents = json.loads(response.data)
        self.assertTrue(contents != None)
        self.assertTrue('mission_plan' in contents)
        self.assertTrue(len(contents['mission_plan']) == 0)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - Mission Control - Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n'
        if verbose: print 'Mission Control - Instruments (positive)'
        # http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/mission_display
        instrument = _CTDPFK000.reference_designator     # 'CP02PMCI-WFP01-03-CTDPFK000'
        url = url_for('main.c2_get_instrument_mission_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        data = json.loads(response.data)
        self.assertEquals(response.status_code, 200)

        # http://localhost:4000/c2/instrument/CP02PMCI-WFP01-03-CTDPFK000/mission_selection/mission4
        mission_plan_store = 'mission4'
        instrument = _CTDPFK000.reference_designator
        url = url_for('main.c2_get_instrument_mission_selection',
                        reference_designator=instrument, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_plan' in data)
        result = data['mission_plan']
        self.assertTrue(result != None)
        self.assertTrue(len(result) > 0)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic negative tests - Mission Control - Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n'
        if verbose: print 'Mission Control - Instruments (negative)'
        # http://localhost:4000/c2/instrument/CP02PMCI-WFP01-05-PARADK000/mission_display
        instrument = PARADK000.reference_designator #'CP02PMCO-WFP01-05-PARADK000'
        url = url_for('main.c2_get_instrument_mission_display', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)

        # http://localhost:4000/c2/instrument/CP02PMCI-WFP01-05-PARADK000/mission_selections
        instrument = PARADK000.reference_designator
        url = url_for('main.c2_get_instrument_mission_selections', reference_designator=instrument)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)

        # http://localhost:4000/c2/instrument/CP02PMCI-WFP01-05-PARADK000/mission_selection/mission4
        mission_plan_store = 'mission4'
        instrument = PARADK000.reference_designator
        url = url_for('main.c2_get_instrument_mission_selection',
                        reference_designator=instrument, mission_plan_store=mission_plan_store)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission_plan' in data)
        result = data['mission_plan']
        self.assertTrue(result != None)
        self.assertEquals(len(result), 0)

        # http://localhost:4000/c2/instrument/CP02PMCI-WFP01-05-PARADK000/mission_selection/mission_does_not_exist
        mission_plan_store_does_not_exist = 'mission_does_not_exist'
        instrument = _CTDPFK000.reference_designator
        url = url_for('main.c2_get_instrument_mission_selection',
                        reference_designator=instrument, mission_plan_store=mission_plan_store_does_not_exist)
        if verbose: print root+url
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)

        if verbose: print '\n'

