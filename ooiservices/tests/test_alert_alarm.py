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
import requests

from unittest import skipIf
import os

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
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

    def test_alert_alarm_routes(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
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
        uframe_id = 2
        event_type = 'alarm'
        alarm1 = self.create_alert_alarm_definition(DOFSTK000_rd, event_type, uframe_id, 1)
        alarm2 = self.create_alert_alarm_definition(CTDPFK000_rd, event_type, uframe_id, 2)
        alarm3 = self.create_alert_alarm_definition(PARADK000_rd, event_type, uframe_id, 3)
        event_type = 'alert'
        alert1 = self.create_alert_alarm_definition(DOFSTK000_rd, event_type, uframe_id, 1)
        alert2 = self.create_alert_alarm_definition(CTDPFK000_rd, event_type, uframe_id, 2)
        alert3 = self.create_alert_alarm_definition(PARADK000_rd, event_type, uframe_id, 3)
        for array in arrays:
            array_code = array.array_code
            if verbose: print '\nArray: ', array_code
            url = url_for('main.get_alerts_alarms_def')
            url += '?array_name=%s' % array_code
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
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertTrue(response.status_code == 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertTrue(len(data['alert_alarm_definition']) == 2)

        #----------------------------------------------------------------------
        save_instrument_reference_designator = None
        list_alertfilter_ids = []

        # GET an alert_alarm_def, create new definition and POST
        url = url_for('main.get_alert_alarm_def', id=1)     #url += '?array_name=%s' % array_code
        if verbose: print root+url
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('reference_designator' in data)
        save_instrument_reference_designator = data['reference_designator']

        # Leveraging data from GET above, change a few things and issue POST to create new def
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
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=goo)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response_data is not None)
        self.assertTrue('id' in response_data)
        self.assertTrue('uframe_filter_id' in response_data)
        list_alertfilter_ids.append(response_data['uframe_filter_id'])

        # get alert and all alert alarm defs, count should be three for this instrument, 7 for platform and array
        url = url_for('main.get_alerts_alarms_def')
        url += '?instrument_name=%s' % data['reference_designator']
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']),3)

        platform = foo['reference_designator'][0:14]
        array_code = foo['reference_designator'][0:2]

        if verbose: print '\nPlatform: ', platform
        url = url_for('main.get_alerts_alarms_def')
        url += '?platform_name=%s' % platform
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 7)

        if verbose: print '\nArray: ', array_code
        url = url_for('main.get_alerts_alarms_def')
        url += '?array_name=%s' % array_code
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 7)

        # Check if SystemEvent(s) have been created...
        url = url_for('main.get_alerts_alarms')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm' in data)
        self.assertEquals(len(data['alert_alarm']), 0)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create SystemEvent(s) from SystemEventDefinitions
        # Get alert and alarm definitions; loop through and POST new SystemEvent for each
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.get_alerts_alarms_def')
        url += '?instrument_name=%s' % save_instrument_reference_designator #data['reference_designator']
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 3)
        self.assertTrue('alert_alarm_definition' in data)
        definitions = data['alert_alarm_definition']
        self.assertEquals(len(definitions),3)
        inx = 1
        for definition in definitions:
            self.assertTrue('id' in definition)
            self.assertTrue('uframe_filter_id' in definition)
            self.assertTrue('reference_designator' in definition)
            self.assertTrue('instrument_parameter' in definition)
            self.assertTrue('instrument_parameter_pdid' in definition)
            self.assertTrue('operator' in definition)
            self.assertTrue('high_value' in definition)
            self.assertTrue('low_value' in definition)
            self.assertTrue('severity' in definition)
            self.assertTrue('stream' in definition)

            system_event_definition_id = definition['id']
            event_type = 'alarm'
            instrument_name = definition['reference_designator']
            instrument_parameter = definition['instrument_parameter']
            operator = definition['operator']
            high_value = definition['high_value']
            low_value = definition['low_value']
            event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                            instrument_name, instrument_parameter, operator, high_value, low_value)
            event_time = str(dt.datetime.now())
            event_data = {}
            event_data['uframe_event_id'] = inx * 314       # instance
            event_data['uframe_filter_id'] = 2 #inx         # definition - hardcoded for now; uframe update required
            event_data['system_event_definition_id'] = system_event_definition_id
            event_data['event_time'] = event_time
            event_data['event_type'] = event_type
            event_data['event_response'] = event_response_message
            event_data['method'] = 'telemetered'
            event_data['deployment'] = 1
            new_event = json.dumps(event_data)
            response = self.client.post(url_for('main.create_alert_alarm'), headers=headers,data=new_event)
            self.assertEquals(response.status_code, 201)

            # Sample response data:
            # {u'uframe_filter_id': 2,
            # u'event_response': u'Instrument: CP02PMCO-WFP01-02-DOFSTK000 condition exceeded where parameter temperature GREATER 10.0 1.0',
            # u'event_type': u'alarm', u'event_time': u'Sun, 19 Jul 2015 21:33:50 GMT', u'system_event_definition_id': 1,
            # u'method': u'telemetered', u'uframe_event_id': 314, u'deployment': 1, u'id': 1}
            response_data = json.loads(response.data)
            self.assertTrue(response_data is not None)
            self.assertTrue('id' in response_data)
            inx += 1

        # Check that some SystemEvent (s) have been created...
        url = url_for('main.get_alerts_alarms')
        response = self.client.get(url, content_type=content_type, headers=headers)
        response_data = json.loads(response.data)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm' in data)
        self.assertTrue(len(data['alert_alarm']) > 0)  # turn auto generate SystemEvent == False
        if verbose:
            aa_events = data['alert_alarm']
            for event in aa_events:
                print '\n\nevent: ', event

        url = url_for('main.get_alert_alarm', id=1)
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)

        response = self.client.post(url_for('main.create_alert_alarm'), headers=headers,data=None)
        self.assertEquals(response.status_code, 409)

        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers,data=None)
        self.assertEquals(response.status_code, 409)

        url = url_for('main.get_alerts_alarms')
        url += '?type=alert'
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)

        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        if verbose:
            for d in data['alert_alarm_definition']:
                if d['id'] == 2:
                    print 'uframe_filter_id: ', d['uframe_filter_id']

        # todo Revisit this section to rework exception handling tests for create and update.
        # Here just generating rotten test data to force errors and exercise branches in code.
        #  Force an error (400) on create definition; utilize session.rollback() in except block
        #  create alert or alarm, note w/o type checking or validation this passes db add and
        # commit, but fails on jsonify for return
        z = {}
        z['uframe_filter_id'] = 10101
        z['reference_designator'] = 'CE01ISSP-XX099-01-CTDPFJ999'
        z['array_name'] = 'CP'
        z['platform_name'] = 'CE01ISSP-XX099'
        z['instrument_name'] = 'CE01ISSP-XX099-01-CTDPFJ999'
        z['instrument_parameter'] = 'param'
        z['instrument_parameter_pdid'] = 'PD220'
        z['operator'] = 'GREATER'
        z['event_type'] = 'alarm'
        z['active'] = str(True)
        z['description'] = ''
        z['high_value'] = '13'
        z['low_value'] = '10'
        z['severity'] = 2
        z['stream'] = 'ctdpf_j_cspp_instrument'
        stuff = json.dumps(z)

        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('id' in response_data)
        self.assertTrue('uframe_filter_id' in response_data)
        uframe_id = response_data['uframe_filter_id']
        self.assertTrue(uframe_id != z['uframe_filter_id'])
        list_alertfilter_ids.append(uframe_id)

        # todo - Rework this section and previous create_alert_alarm_def. Must generate 400 after uframe alertfilter create.
        # todo - creates instance; then rollback will require deleting uframe filter created.
        # Get this back in: This test verifies after the previous error (400), a rollback is issued in except block;
        # if it hasn't been then this GET would fail.
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 8)
        # save alert definition to use in PUT below
        alert_definition = None
        for d in data['alert_alarm_definition']:
            if d['uframe_filter_id'] == uframe_id:
                alert_definition = d
                break

        new_definition_id = alert_definition['id']

        # test PUT to update definition (use BAD data on update)
        response = self.client.get(url_for('main.get_alert_alarm_def', id=2), content_type=content_type,headers=headers)
        self.assertEquals(response.status_code, 200)

        response = self.client.get(url_for('main.get_alerts_alarms', type='alert'), content_type=content_type,headers=headers)
        self.assertEquals(response.status_code, 200)
        alerts = json.loads(response.data)
        self.assertTrue(len(alerts) > 0)

        # do PUT using alert_Definition from above, modify description field; check with GET
        update_description = 'this is an update!'
        alert_definition['description'] = update_description
        alert_definition['uframe_filter_id'] = uframe_id
        good_stuff = json.dumps(alert_definition)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=new_definition_id),headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)
        response = self.client.get(url_for('main.get_alert_alarm_def', id=new_definition_id),content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('description' in data)
        self.assertEquals(update_description, data['description'])

        # PUT valid uframe_filter_id but bad data, generate 400
        response = self.client.put(url_for('main.update_alert_alarm_def', id=uframe_id), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 409)

        # PUT invalid (nonexistent) uframe_filter_id == 37, generate 404
        response = self.client.put(url_for('main.update_alert_alarm_def', id=33371), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 409)

        # PUT data=None, generate 409
        response = self.client.put(url_for('main.update_alert_alarm_def', id=33371), headers=headers, data=None)
        self.assertEquals(response.status_code, 409)

        # GET invalid id=9876
        response = self.client.get(url_for('main.get_alert_alarm_def', id=9876), content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 404)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get alert and alarm definitions; loop through and delete definitions which have
        # uframe_filter_id values > 2  (during development). Verify corresponding
        # alertfilter have been removed in uframe.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertTrue(response.status_code == 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']),8)
        self.assertTrue('alert_alarm_definition' in data)
        definitions = data['alert_alarm_definition']
        #print '\n Number of alert_alarm_definitions: ', len(definitions)

        for definition in definitions:
            if definition['uframe_filter_id'] > 2:      # not retiring filterId 1 or 2 right now
                url = url_for('main.delete_alert_alarm_definition', id=definition['id'])
                response = self.client.delete(url, headers=headers)
                #response = self.client.get(url, headers=headers)
                self.assertEquals(response.status_code, 200)


        # Delete all alertfilter ids (where id > 3)
        if verbose: print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)

        # ======== NEVER USE THIS CODE EXCEPT FOR TEST DEVELOPMENT ===========
        #self.scrub_alertfilters()

        '''
        # List all filter ids (id > 3)
        list_alertfilter_ids = self.get_alertfilters()
        #print '\n filter_ids: ', list_alertfilter_ids
        self.assertEquals(len(list_alertfilter_ids), 0)
        #print '\n filter_ids after delete: ', list_alertfilter_ids
        '''

    def scrub_alertfilters(self):
        debug = False
        # ======== NEVER USE THIS CODE EXCEPT FOR TEST DEVELOPMENT ===========
        # Get all alertfilter ids (where id > 3)
        list_alertfilter_ids = self.get_alertfilters()
        list_alertfilter_ids.sort()
        if debug: print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)

        # Delete all alertfilter ids (where id > 3)
        if debug: print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)
        return

    def test_SystemEventDefinitions_uframe_integration(self):

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_alertfilter_ids = []
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alert definitions (no 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': False,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial'}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers,data=request_data)
        #print '\n response data: ', json.loads(response.data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        alert_definition = json.loads(response.data)
        self.assertTrue(alert_definition is not None)
        self.assertTrue('id' in alert_definition)
        self.assertTrue('uframe_filter_id' in alert_definition)
        self.assertTrue('description' in alert_definition)
        alert_alarm_def_id = alert_definition['id']
        alert_alarm_def_uframe_id = alert_definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_alarm_def_id), headers=headers)
        self.assertEquals(response.status_code, 200)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST Update to description field; this also performs uframe alertfilter update
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        updated_description = 'alertfilter updated!'
        data['description'] = updated_description
        data['uframe_filter_id'] = alert_alarm_def_uframe_id
        data['id'] = alert_alarm_def_id
        good_stuff = json.dumps(data)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=alert_alarm_def_id),
                                   headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET updated alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_alarm_def_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        get_data = json.loads(response.data)
        self.assertTrue('description' in get_data)
        self.assertEquals(updated_description, get_data['description'])

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Now verify uframe reports same value for description, http://localhost:12577/alertfilters/alertfilter_id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        uframe_url, timeout, timeout_read = self.get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters', str(alert_alarm_def_uframe_id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        get_uframe_data = json.loads(response.content)
        self.assertTrue(get_uframe_data is not None)
        self.assertTrue('alertMetadata' in get_uframe_data)
        self.assertTrue('description' in get_uframe_data['alertMetadata'])
        uframe_description = get_uframe_data['alertMetadata']['description']
        self.assertTrue(uframe_description is not None)
        self.assertEquals(uframe_description, updated_description)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clean up by deleting ('retire') alert_alarm_def
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=alert_alarm_def_id)
        response = self.client.delete(url, headers=headers)
        #response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)

    def test_SystemEvents_uframe_integration(self):

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_alertfilter_ids = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alert definitions (no 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial'}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        alert_definition = json.loads(response.data)
        self.assertTrue(alert_definition is not None)
        self.assertTrue('id' in alert_definition)
        self.assertTrue('uframe_filter_id' in alert_definition)
        self.assertTrue('description' in alert_definition)
        alert_alarm_def_id = alert_definition['id']
        alert_alarm_def_uframe_id = alert_definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_alarm_def_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alarm which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = definition['id']
        uframe_event_id = 100
        uframe_filter_id = definition['uframe_filter_id']
        instrument_name = definition['reference_designator']
        instrument_parameter = definition['instrument_parameter']
        operator = definition['operator']
        high_value = definition['high_value']
        low_value = definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        event_data = {}
        event_data['uframe_event_id'] = uframe_event_id
        event_data['uframe_filter_id'] = uframe_filter_id
        event_data['system_event_definition_id'] = system_event_definition_id
        event_data['event_time'] = event_time
        event_data['event_type'] = event_type
        event_data['event_response'] = event_response_message
        event_data['method'] = 'telemetered'
        event_data['deployment'] = 1
        new_event = json.dumps(event_data)
        response = self.client.post(url_for('main.create_alert_alarm'), headers=headers, data=new_event)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue('id' in response_data)
        self.assertTrue(response_data['id'] is not None)
        alert_alarm_id = response_data['id']
        alert_alarm_uframe_event_id = response_data['uframe_event_id']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Try to delete alert_alarm_def when alert_alarm instance not yet acknowledged.
        # response_data:
        #   {u'error': u'There are existing alert_alarm instances using this id which have not yet been acknowledged.'}
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=alert_alarm_def_id)
        response = self.client.delete(url, headers=headers)
        #response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('error' in response_data)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Acknowledge alert_alarm
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['acknowledged'] = True
        ack_data['ack_by'] = 'admin'
        ack_data['ack_for'] = None
        ack_data['ts_acknowledged'] = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")

        # sample ack_data:  {'uframe_filter_id': 892, 'ack_for': None, 'event_type': 'alarm',
        # 'system_event_definition_id': 1, 'ts_acknowledged': '2015-07-21T07:51:14', 'acknowledged': True,
        # 'uframe_event_id': 100, 'ack_by': 'admin', 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue('acknowledged' in response_data)
        self.assertTrue('ack_by' in response_data)
        self.assertTrue('ack_for' in response_data)
        self.assertTrue('ts_acknowledged' in response_data)
        self.assertEquals(response_data['acknowledged'], True)
        self.assertEquals(response_data['ack_by'], 'admin')
        self.assertTrue(response_data['ts_acknowledged'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clean up by retiring alert_alarm_def
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=alert_alarm_def_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertEquals(len(response_data), 0)

        # - - GET alert_alarm_definition by id
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_alarm_def_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue('retire' in definition)
        self.assertTrue('ts_retire' in definition)
        self.assertEquals(definition['retire'], True)
        self.assertTrue(definition['retire'] is not None)
        save_ts_retire = definition['ts_retire']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete alert_alarm_def (which is already retired)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=alert_alarm_def_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertEquals(len(response_data), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_alarm_def_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue('retire' in definition)
        self.assertTrue('ts_retire' in definition)
        self.assertEquals(definition['retire'], True)
        self.assertTrue(definition['retire'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete non existing alert_alarm_definition ( {error': 'alert_alarm_definition not found'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=909090)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)

    def test_SystemEventDefinition_invalid_operators(self):

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        filter_ids = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Alarm - Valid alert_alarm_definition data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {
              "active": True,
              "array_name": "CE",
              "description": "Rule 42",
              "event_type": "alarm",
              "high_value": "31.0",
              "instrument_name": "CE01ISSP-XX099-01-CTDPFJ999",
              "instrument_parameter": "temperature",
              "instrument_parameter_pdid": "PD440",
              "low_value": "10.0",
              "operator": "GREATER",
              "platform_name": "CE01ISSP-XX099",
              "reference_designator": "CE01ISSP-XX099-01-CTDPFJ999",
              "severity": 2,
              "stream": "ctdpf_j_cspp_instrument"
        }
        # - - Create alert_alarm_definition (Alarm)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=json.dumps(data))
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('uframe_filter_id' in definition)
        filter_ids.append(definition['uframe_filter_id'])

        # - - Clean up by retiring alert_alarm_def
        url = url_for('main.delete_alert_alarm_definition', id=definition['id'])
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertEquals(len(response_data), 0)

        # - - Get alert_alarm_def
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, headers=headers, content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' in definition)
        self.assertEquals(len(definition['alert_alarm_definition']), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Alarm - Invalid alert_alarm_definition data, invalid operator
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {
              "active": True,
              "array_name": "CE",
              "description": "Rule 42",
              "event_type": "alarm",
              "high_value": "31.0",
              "instrument_name": "CE01ISSP-XX099-01-CTDPFJ999",
              "instrument_parameter": "temperature",
              "instrument_parameter_pdid": "PD440",
              "low_value": "10.0",
              "operator": "NO_SUCH_OPERATOR",
              "platform_name": "CE01ISSP-XX099",
              "reference_designator": "CE01ISSP-XX099-01-CTDPFJ999",
              "severity": 2,
              "stream": "ctdpf_j_cspp_instrument"
        }
        # - - POST create_alert_alarm_definition, receive error 'Insufficient data, or bad data format.'
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=json.dumps(data))
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)

        # - - Get alert_alarm_def
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' in definition)
        self.assertEquals(len(definition['alert_alarm_definition']), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Alert - Valid alert_alarm_definition data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {
              "active": True,
              "array_name": "CE",
              "description": "Rule 42",
              "event_type": "alert",
              "high_value": "31.0",
              "instrument_name": "CE01ISSP-XX099-01-CTDPFJ999",
              "instrument_parameter": "temperature",
              "instrument_parameter_pdid": "PD440",
              "low_value": "10.0",
              "operator": "GREATER",
              "platform_name": "CE01ISSP-XX099",
              "reference_designator": "CE01ISSP-XX099-01-CTDPFJ999",
              "severity": 2,
              "stream": "ctdpf_j_cspp_instrument"
        }
        # - - Create alert_alarm_definition (Alert)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=json.dumps(data))
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('uframe_filter_id' in definition)
        filter_ids.append(definition['uframe_filter_id'])

        # - - Get alert_alarm_def
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' in definition)
        self.assertEquals(len(definition['alert_alarm_definition']), 1)

        definition_id = definition['alert_alarm_definition'][0]['id']
        # - - Clean up by retiring alert_alarm_def
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertEquals(len(response_data), 0)

        # - - Get alert_alarm_def
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' in definition)
        self.assertEquals(len(definition['alert_alarm_definition']), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Alert - Invalid alert_alarm_definition data, invalid operator
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {
              "active": True,
              "array_name": "CE",
              "description": "Rule 42",
              "event_type": "alert",
              "high_value": "31.0",
              "instrument_name": "CE01ISSP-XX099-01-CTDPFJ999",
              "instrument_parameter": "temperature",
              "instrument_parameter_pdid": "PD440",
              "low_value": "10.0",
              "operator": "NO_SUCH_OPERATOR",
              "platform_name": "CE01ISSP-XX099",
              "reference_designator": "CE01ISSP-XX099-01-CTDPFJ999",
              "severity": 2,
              "stream": "ctdpf_j_cspp_instrument"
        }
        # - - POST create_alert_alarm_definition, receive error 'Insufficient data, or bad data format.'
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=json.dumps(data))
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)

        # - - Get alert_alarm_def
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' in definition)
        self.assertEquals(len(definition['alert_alarm_definition']), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilters created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n filter_ids(%d): %s' % (len(filter_ids), filter_ids)
        self.delete_alertfilters(filter_ids)

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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # private test helper methods
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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

    def create_alert_alarm_definition(self, instrument_reference_designator, event_type, uframe_id, severity):
        # Note, this isn't creating a definition in uframe, just used to exercise SystemEventDefinition
        #valid_priority = ['alert','alarm']
        alert_alarm_definition = None
        array_name = instrument_reference_designator[0:0+2]
        platform_name = instrument_reference_designator[0:0+14]
        instrument_parameter = 'temperature'
        instrument_parameter_pdid = 'PD100'
        operator = 'GREATER'
        high_value = '10.0'
        low_value = '1.0'
        stream = 'ctdpf_j_cspp_instrument'
        create_time = dt.datetime.now()
        if instrument_reference_designator == 'CP02PMCO-WFP01-02-DOFSTK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            db.session.add(alert_alarm_definition)
            db.session.commit()
        elif alert_alarm_definition == 'CP02PMCO-WFP01-03-CTDPFK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            db.session.add(alert_alarm_definition)
            db.session.commit()
        elif alert_alarm_definition == 'CP02PMCO-WFP01-05-PARADK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            db.session.add(alert_alarm_definition)
            db.session.commit()
        else:
            alert_alarm_definition = SystemEventDefinition(reference_designator=instrument_reference_designator)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = instrument_reference_designator
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
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

    def get_uframe_info(self):
        """ Get uframe alertalarm configuration information. (port 12577) """
        uframe_url = self.app.config['UFRAME_ALERTS_URL']
        timeout = self.app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = self.app.config['UFRAME_TIMEOUT_READ']
        return uframe_url, timeout, timeout_read

    def delete_alertfilters(self,list_of_ids):
        """
        Delete alertfilters in uframe; development helper only to be used during controlled testing.
        """
        debug = False
        if debug: print '\n Deleting alertfilter ids: ', list_of_ids
        headers = self.get_api_headers('admin', 'test')
        uframe_url, timeout, timeout_read = self.get_uframe_info()
        for id in list_of_ids:
            if id > 3:
                url = "/".join([uframe_url, 'alertfilters', str(id)])
                if debug: print '\n delete url: ', url

                response = requests.delete(url, timeout=(timeout, timeout_read), headers=headers)
                self.assertEquals(response.status_code, 200)
                get_uframe_data = json.loads(response.content)

                # Sample Delete response dictionary: {u'message': u'Delete successful.', u'id': 204, u'statusCode': u'OK'}
                self.assertTrue('message' in get_uframe_data)
                self.assertTrue('id' in get_uframe_data)
                self.assertTrue('statusCode' in get_uframe_data)
                self.assertEquals(get_uframe_data['statusCode'],'OK')
        return

    def get_alertfilters(self):
        """
        Get list of all alertfilter ids in uframe. Only to be used during development testing.
        Warning constrained to 3 < alertfilter id < 100000.
        """
        list_of_alertfilter_ids = []
        uframe_url, timeout, timeout_read = self.get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        alertfilters = json.loads(response.content)
        self.assertTrue(alertfilters is not None)
        for alertfilter in alertfilters:
            if 'eventId' in alertfilter:
                uframe_id = alertfilter['eventId']
                if uframe_id >= 3 and uframe_id < 10000:
                    list_of_alertfilter_ids.append(uframe_id)
        return list_of_alertfilter_ids

    '''
    reference_designator = 'CE01ISSP-XX099-01-CTDPFJ999'
    def make_fake_uframe_alertfilter_data(self):
        """ Make uframe input data for evaluation/test processing; works in conjunction with manual ingestion process. """
        result = {
              "@class" : "com.raytheon.uf.common.ooi.dataplugin.alert.alertfilter.AlertFilterRecord",
              "enabled" : True,
              "stream" : "ctdpf_j_cspp_instrument",
              "referenceDesignator" : {
                "node" : "XX099",
                "full" : True,
                "subsite" : "CE01ISSP",
                "sensor" : "01-CTDPFJ999"
              },
              "alertRule" : {
                "filter" : "GREATER",
                "valid" : True,
                "highVal" : 31.0,
                "errMessage" : None,
                "lowVal" : 10.0
              },
              "pdId" : "PD440",
              "eventId" : 2,
              "alertMetadata" : {
                "severity" : -2,
                "description" : "Rule 42"
              }
            }

        return result
    '''



