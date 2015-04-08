#!/usr/bin/env python
'''
Specific testing for Alert and Alarm
'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import SystemEventDefinition, SystemEvent
import datetime as dt

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class AlertAlarmTestCase(unittest.TestCase):

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
        else:
            instrument_deployment = InstrumentDeployment(reference_designator=instrument_reference_designator)
            instrument_deployment.reference_designator = platform_deployment_id
            db.session.add(instrument_deployment)
            db.session.commit()
        return instrument_deployment

    def create_alert_alarm_definition(self, instrument_reference_designator, priority, uframe_id):
        #valid_priority = ['alert','alarm']
        alert_alarm_definition = None
        array_name = instrument_reference_designator[0:0+2]
        platform_name = instrument_reference_designator[0:0+14]
        instrument_parameter = 'junk'
        operator = '>'
        values = '5.0'
        create_time = dt.datetime.now()
        if instrument_reference_designator == 'CP02PMCO-WFP01-02-DOFSTK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.priority = priority
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.operator = operator
            alert_alarm_definition.values = values
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_definition_id = uframe_id
            if priority == 'alarm':
                alert_alarm_definition.uframe_definition_id = uframe_id
            db.session.add(alert_alarm_definition)
            db.session.commit()
        elif alert_alarm_definition == 'CP02PMCO-WFP01-03-CTDPFK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.priority = priority
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.operator = operator
            alert_alarm_definition.values = values
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_definition_id = uframe_id
            if priority == 'alarm':
                alert_alarm_definition.uframe_definition_id = uframe_id
            db.session.add(alert_alarm_definition)
            db.session.commit()
        elif alert_alarm_definition == 'CP02PMCO-WFP01-05-PARADK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.priority = priority
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.operator = operator
            alert_alarm_definition.values = values
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_definition_id = uframe_id
            if priority == 'alarm':
                alert_alarm_definition.uframe_definition_id = uframe_id
            db.session.add(alert_alarm_definition)
            db.session.commit()
        else:
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.priority = priority
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.operator = operator
            alert_alarm_definition.values = values
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_definition_id = uframe_id
            if priority == 'alarm':
                alert_alarm_definition.uframe_definition_id = uframe_id
            db.session.add(alert_alarm_definition)
            db.session.commit()
        return alert_alarm_definition

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

    def test_alert_alarm_array_routes(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        '''
        Test array routes:
        Array:  CE
        http://localhost:4000/alert_alarm_definition?array_name=CE

        Array:  CP
        http://localhost:4000/alert_alarm_definition?array_name=CP

        Negative:
        http://localhost:4000/alert_alarm_definition?array_name=RS
        http://localhost:4000/alert_alarm_definition?array_name=

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
        platforms = []
        CP02PMCO_WFP01, CP02PMCO_SBS01, CP02PMUI_RII01 = self.create_CP_platform_deployments()
        CP02PMCO_WFP01_rd = CP02PMCO_WFP01.reference_designator
        CP02PMCO_SBS01_rd = CP02PMCO_SBS01.reference_designator
        CP02PMUI_RII01_rd = CP02PMUI_RII01.reference_designator
        # platform deployment 1
        platforms.append(CP02PMCO_WFP01_rd)
        # platform deployment 2
        platforms.append(CP02PMCO_SBS01_rd)
        # platform deployment 3
        platforms.append(CP02PMUI_RII01_rd)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Instruments
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        instruments = []
        # (platform deployment 1) instrument deployment 1
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        self.create_instrument_deployment(DOFSTK000_rd, CP02PMCO_WFP01.id)
        instruments.append(DOFSTK000_rd)
        # (platform deployment 1) instrument deployment 2
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        self.create_instrument_deployment(CTDPFK000_rd, CP02PMCO_WFP01.id)
        instruments.append(CTDPFK000_rd)
        # (platform deployment 1) instrument deployment 3
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'
        self.create_instrument_deployment(PARADK000_rd, CP02PMCO_WFP01.id)
        instruments.append(PARADK000_rd)

        '''
        # (platform deployment 2) instrument deployment 1
        MOPAK0000_rd = 'CP02PMCO-SBS01-01-MOPAK0000'
        self.create_instrument_deployment(MOPAK0000_rd, CP02PMCO_SBS01.id)
        # (platform deployment 3) instrument deployment 1
        ADCPTG000_rd = 'CP02PMUI-RII01-02-ADCPTG000'
        self.create_instrument_deployment(ADCPTG000_rd, CP02PMUI_RII01.id)
        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # End of data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Proceed with tests
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - array, platform, instrument w/o data (no alerts or alarms definitins yet)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.exercise_alert_alarm_definition_no_data(arrays, platforms, instruments)

        # Create some alert definitions
        priority = 'alert'
        uframe_id = 10100
        alert1 = self.create_alert_alarm_definition(DOFSTK000_rd, priority, uframe_id)
        uframe_id += 1
        alert2 = self.create_alert_alarm_definition(CTDPFK000_rd, priority, uframe_id)
        uframe_id += 1
        alert3 = self.create_alert_alarm_definition(PARADK000_rd, priority, uframe_id)
        uframe_id += 1
        priority = 'alarm'
        alarm1 = self.create_alert_alarm_definition(DOFSTK000_rd, priority, uframe_id)
        uframe_id += 1
        alarm2 = self.create_alert_alarm_definition(CTDPFK000_rd, priority, uframe_id)
        uframe_id += 1
        alarm3 = self.create_alert_alarm_definition(PARADK000_rd, priority, uframe_id)

        for array in arrays:
            array_code = array.array_code
            if verbose: print '\nArray: ', array_code
            url = url_for('main.get_alerts_alarms_def')
            url += '?array_name=%s' % array_code
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            if array_code == 'CP':
                self.assertTrue(len(data['alert_alarm_definition']) == 6)
            else:
                self.assertTrue(len(data['alert_alarm_definition']) == 0)

        # http://localhost:4000/alert_alarm_definition?platform_name=platform
        for platform in platforms:
            if verbose: print '\nPlatform: ', platform
            url = url_for('main.get_alerts_alarms_def')
            url += '?platform_name=%s' % platform
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            if platform == CP02PMCO_WFP01_rd:
                self.assertTrue(len(data['alert_alarm_definition']) == 6)
            else:
                self.assertTrue(len(data['alert_alarm_definition']) == 0)

        # http://localhost:4000/alert_alarm_definition?instrument_name=instrument
        # should be an alert and alarm for each instrument
        for instrument in instruments:
            if verbose: print '\nInstrument: ', instrument
            url = url_for('main.get_alerts_alarms_def')
            url += '?instrument_name=%s' % instrument
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertTrue(len(data['alert_alarm_definition']) == 2)

        # Save current value of USE_MOCK_DATA; restore after this test loop
        current_mock_value_flag = self.app.config['USE_MOCK_DATA']
        test_cases = [True, False]
        for value in test_cases:
            self.app.config['USE_MOCK_DATA'] = value
            # GET an alert_alarm_def, create new definition and POST
            url = url_for('main.get_alert_alarm_def', id=1)
            #url += '?array_name=%s' % array_code
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('reference_designator' in data)
            save_instrument_reference_designator = data['reference_designator']

            # Leveraging data from GET above, change a few things and issue POST to create new def and
            # some 'free' SystemEvent()s
            content_type = 'application/json'
            headers = self.get_api_headers('admin', 'test')
            foo = {}
            inx = 0
            for k,v in data.iteritems():
                if k != 'id':
                    foo[k] = v
                    inx += 1
            foo['active'] = True
            foo['description'] = 'some new and fancy description'
            goo = json.dumps(foo)
            response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers,data=goo)
            self.assertEquals(response.status_code, 201)

        self.app.config['USE_MOCK_DATA'] = current_mock_value_flag

        # get alert and all alert alarm defs, count should be three for this instrument, 7 for platform and array
        url = url_for('main.get_alerts_alarms_def')
        url += '?instrument_name=%s' % data['reference_designator']
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']),4)

        platform = foo['reference_designator'][0:14]
        array_code = foo['reference_designator'][0:2]

        if verbose: print '\nPlatform: ', platform
        url = url_for('main.get_alerts_alarms_def')
        url += '?platform_name=%s' % platform
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 8)

        if verbose: print '\nArray: ', array_code
        url = url_for('main.get_alerts_alarms_def')
        url += '?array_name=%s' % array_code
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 8)

        # Check that some ancillary SystemEvent (s) have been created...
        url = url_for('main.get_alerts_alarms')
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm' in data)
        if self.app.config['USE_MOCK_DATA']:
            self.assertTrue(len(data['alert_alarm']) > 0)  # turn auto generate SystemEvent == False or remove from loader
        else:
            self.assertEquals(len(data['alert_alarm']), 5)  # turn auto generate SystemEvent == False or remove from loader

        # Get alert and alarm defs, loop through and POST new SystemEvent for each
        url = url_for('main.get_alerts_alarms_def')
        url += '?instrument_name=%s' % save_instrument_reference_designator #data['reference_designator']
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']),4)
        self.assertTrue('alert_alarm_definition' in data)
        definitions = data['alert_alarm_definition']
        self.assertEquals(len(definitions),4)

        inx = 1
        for definition in definitions:
            self.assertTrue('id' in definition)
            self.assertTrue('uframe_definition_id' in definition)
            self.assertTrue('reference_designator' in definition)
            self.assertTrue('instrument_parameter' in definition)
            self.assertTrue('operator' in definition)
            self.assertTrue('values' in definition)

            system_event_definition_id = definition['id']
            event_type = 'alert'
            instrument_name = definition['reference_designator']
            instrument_parameter = definition['instrument_parameter']
            operator = definition['operator']
            values = definition['values']
            event_response_message = "Instrument: {0} boundary condition exceeded where parameter {1} {2} {3}".format(instrument_name, instrument_parameter, operator, values)
            event_time = str(dt.datetime.now())
            event_data = {}
            event_data['uframe_event_id'] = inx
            event_data['system_event_definition_id'] = system_event_definition_id
            event_data['event_time'] = event_time
            event_data['event_type'] = event_type
            event_data['event_response'] = event_response_message

            new_event = json.dumps(event_data)
            response = self.client.post(url_for('main.create_alert_alarm'), headers=headers,data=new_event)
            self.assertEquals(response.status_code, 201)
            inx += 1

        # Check that some SystemEvent (s) have been created...
        url = url_for('main.get_alerts_alarms')
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm' in data)
        self.assertTrue(len(data['alert_alarm']) > 0)  # turn auto generate SystemEvent == False
        if verbose:
            aa_events = data['alert_alarm']
            for event in aa_events:
                print '\n\nevent: ', event

        url = url_for('main.get_alert_alarm', id=1)
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)

        response = self.client.post(url_for('main.create_alert_alarm'), headers=headers,data=None)
        self.assertEquals(response.status_code, 409)

        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers,data=None)
        self.assertEquals(response.status_code, 409)

        url = url_for('main.get_alerts_alarms')
        url += '?type=Alert'
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)

        url = url_for('main.get_alerts_alarms_def')
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        if verbose:
            for d in data['alert_alarm_definition']:
                if d['id'] == 2:
                    print 'uframe_definition_id: ', d['uframe_definition_id']

        #  Force an error (400) on create definition; utilize session.rollback() in except block
        #  create alert or alarm, note w/o type checking or validation this passes db add and
        # commit, but fails on jsonify for return
        z = {}
        z['uframe_definition_id'] = 10101
        z['reference_designator'] = None #'CP10-123123'
        z['array_name'] = 'CP'
        z['platform_name'] = 'none_such_really_long_wacky_name'
        z['instrument_name'] = 'CP10-123123'
        z['instrument_parameter'] = 'param'
        z['operator'] = '>'
        z['values'] = '12'
        z['priority'] = 'foo'
        z['active'] = str(True)
        z['description'] = ''
        stuff = json.dumps(z)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers,data=stuff)
        self.assertEquals(response.status_code, 400)

        # this test verifies after the previous error (400), a rollback is issued in except block;
        # if it hasn't been then this GET would fail
        url = url_for('main.get_alerts_alarms_def')
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 8)
        # save alert definition to use in PUT below
        alert_definition = None
        for d in data['alert_alarm_definition']:
            if d['uframe_definition_id'] == 10101:
                alert_definition = d
                break

        # test PUT to update definition (use BAD data on update)
        response = self.client.get(url_for('main.get_alert_alarm_def', id=2), headers=headers)
        self.assertEquals(response.status_code, 200)

        response = self.client.get(url_for('main.get_alerts_alarms', type='alert'), headers=headers)
        self.assertEquals(response.status_code, 200)
        alerts = json.loads(response.data)
        self.assertTrue(len(alerts) > 0)

        # do PUT using alert_Definition from above, modify description field; check with GET
        alert_definition['description'] = 'this is an update!'
        good_stuff = json.dumps(alert_definition)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=10101), headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_definition['id']), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('description' in data)
        self.assertEquals("this is an update!", data['description'])

        # PUT valid uframe_definition_id but bad data, generate 400
        response = self.client.put(url_for('main.update_alert_alarm_def', id=10101), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 400)

        # PUT invalid (nonexistent) uframe_definition_id == 37, generate 404
        response = self.client.put(url_for('main.update_alert_alarm_def', id=371), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 404)

        # PUT data=None, generate 409
        response = self.client.put(url_for('main.update_alert_alarm_def', id=371), headers=headers, data=None)
        self.assertEquals(response.status_code, 409)

        # GET invalid id=9876
        response = self.client.get(url_for('main.get_alert_alarm_def', id=9876), headers=headers)
        self.assertEquals(response.status_code, 404)

        if verbose: print '\n'

    def exercise_alert_alarm_definition_no_data(self, arrays, platforms, instruments):
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - array, platform, instrument w/o data (no alerts or alarms yet)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.get_alerts_alarms_def')
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 0)

        # http://localhost:4000/alert_alarm_definition?array_name=array_code
        for array in arrays:
            array_code = array.array_code
            if verbose: print '\nArray: ', array_code
            url = url_for('main.get_alerts_alarms_def')
            url += '?array_name=%s' % array_code
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertTrue(len(data['alert_alarm_definition']) == 0)

        # http://localhost:4000/alert_alarm_definition?platform_name=platform
        for platform in platforms:
            if verbose: print '\nPlatform: ', platform
            url = url_for('main.get_alerts_alarms_def')
            url += '?platform_name=%s' % platform
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertTrue(len(data['alert_alarm_definition']) == 0)

        # http://localhost:4000/alert_alarm_definition?instrument_name=instrument
        for instrument in instruments:
            if verbose: print '\nInstrument: ', instrument
            url = url_for('main.get_alerts_alarms_def')
            url += '?instrument_name=%s' % instrument
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertTrue(len(data['alert_alarm_definition']) == 0)

        # http://localhost:4000/alert_alarm_definition?reference_designator=instrument
        for instrument in instruments:
            if verbose: print '\nReference Designator: ', instrument
            url = url_for('main.get_alerts_alarms_def')
            url += '?reference_designator=%s' % instrument
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertEquals(len(data['alert_alarm_definition']), 0)

        if verbose: print '\n'

        return


