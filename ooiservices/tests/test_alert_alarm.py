#!/usr/bin/env python
'''
Specific testing for Alert and Alarm
'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import (url_for, current_app)
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import SystemEventDefinition, SystemEvent, UserEventNotification
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
        scope = UserScope.query.filter_by(scope_name='redmine').first()     # added
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

    def test_alert_alarm_definition_routes(self):

        verbose = self.verbose
        root = self.root
        list_alertfilter_ids = []
        if verbose: print '\n'

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        array_CE = 'CE'
        array_GP = 'GP'
        array_CP = 'CP'
        CP02PMCO_WFP01_rd = 'CP02PMCO-WFP01'
        CP02PMCO_SBS01_rd = 'CP02PMCO-SBS01'
        CP02PMUI_RII01_rd = 'CP02PMUI-RII01'
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'

        arrays = [array_CE, array_GP, array_CP]
        platforms = [CP02PMCO_WFP01_rd] #, CP02PMCO_SBS01_rd, CP02PMUI_RII01_rd]
        instruments = [DOFSTK000_rd, CTDPFK000_rd, PARADK000_rd]

        # Create some definitions
        alarm1 = self.create_alert_alarm_definition(DOFSTK000_rd, 'alarm', 2, 1)
        alarm2 = self.create_alert_alarm_definition(CTDPFK000_rd, 'alarm', 2, 2)
        alarm3 = self.create_alert_alarm_definition(PARADK000_rd, 'alarm', 2, 3)
        alert1 = self.create_alert_alarm_definition(DOFSTK000_rd, 'alert', 2, 1)
        alert2 = self.create_alert_alarm_definition(CTDPFK000_rd, 'alert', 2, 2)
        alert3 = self.create_alert_alarm_definition(PARADK000_rd, 'alert', 2, 3)

        # test /alert_alarm_definition route using request.arg array_name
        for array in arrays:
            #array_code = array.array_code
            url = url_for('main.get_alerts_alarms_def')
            url += '?array_name=%s' % array
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            if array == 'CP':
                self.assertEquals(len(data['alert_alarm_definition']), 6)
            else:
                self.assertEquals(len(data['alert_alarm_definition']), 0)

        # test /alert_alarm_definition route using request.arg platform_name
        # http://localhost:4000/alert_alarm_definition?platform_name=platform
        for platform in platforms:
            url = url_for('main.get_alerts_alarms_def')
            url += '?platform_name=%s' % platform
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            if platform == CP02PMCO_WFP01_rd:
                self.assertEquals(len(data['alert_alarm_definition']), 6)
            else:
                self.assertEquals(len(data['alert_alarm_definition']), 0)

        # test /alert_alarm_definition route using request.arg instrument_name
        # http://localhost:4000/alert_alarm_definition?instrument_name=instrument
        # should be an alert and alarm for each instrument
        for instrument in instruments:
            url = url_for('main.get_alerts_alarms_def')
            url += '?instrument_name=%s' % instrument
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertEquals(len(data['alert_alarm_definition']), 2)

        # GET an alert_alarm_def (no request.args), create new definition and POST
        url = url_for('main.get_alert_alarm_def', id=1)     #url += '?array_name=%s' % array_code
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
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
        foo['user_id'] = 1
        foo['use_email'] = False
        foo['use_redmine'] = False
        foo['use_phone'] = False
        foo['use_log'] = False
        foo['use_sms'] = False
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
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']),3)

        platform = foo['reference_designator'][0:14]
        array_code = foo['reference_designator'][0:2]

        if verbose: print '\nPlatform: ', platform
        url = url_for('main.get_alerts_alarms_def')
        url += '?platform_name=%s' % platform
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 7)

        if verbose: print '\nArray: ', array_code
        url = url_for('main.get_alerts_alarms_def')
        url += '?array_name=%s' % array_code
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']), 7)

        # Check if SystemEvent(s) have been created...should not have any at this time
        url = url_for('main.get_alerts_alarms')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm' in data)
        self.assertEquals(len(data['alert_alarm']), 0)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create SystemEvent(s) from SystemEventDefinitions
        # Get alert_alarm_definition(s); loop through and POST new SystemEvent for each
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.get_alerts_alarms_def')
        url += '?instrument_name=%s' % save_instrument_reference_designator
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
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
            self.assertTrue('escalate_on' in definition)
            self.assertTrue('escalate_boundary' in definition)
            system_event_definition_id = definition['id']
            event_type = 'alarm'
            instrument_name = definition['reference_designator']
            instrument_parameter = definition['instrument_parameter']
            operator = definition['operator']
            high_value = definition['high_value']
            low_value = definition['low_value']
            event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                            instrument_name, instrument_parameter, operator, high_value, low_value)
            event_time = 3607761438.72      # uframe sample event_time float: 3607761438.72
            event_data = {}
            event_data['uframe_event_id'] = inx * 314       # instance
            event_data['uframe_filter_id'] = 2 #inx         # definition - hardcoded for now; uframe update required
            event_data['system_event_definition_id'] = system_event_definition_id
            event_data['event_time'] = event_time
            event_data['event_type'] = event_type
            event_data['event_response'] = event_response_message
            event_data['method'] = 'telemetered'
            event_data['deployment'] = 1
            event_data['ticket_id'] = 0     # default, i.e. no ticket
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
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        #print '\n data: ', data
        self.assertTrue('alert_alarm' in data)
        self.assertTrue(len(data['alert_alarm']) > 0)

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
        z['instrument_parameter_pdid'] = 'PD440'
        z['operator'] = 'GREATER'
        z['event_type'] = 'alarm'
        z['active'] = str(True)
        z['description'] = ''
        z['high_value'] = '13'
        z['low_value'] = '10'
        z['severity'] = 2
        z['stream'] = 'ctdpf_j_cspp_instrument'
        z['escalate_on'] = 5
        z['escalate_boundary'] = 10
        z['user_id'] = 1
        z['use_email'] = False
        z['use_redmine'] = False
        z['use_phone'] = False
        z['use_log'] = False
        z['use_sms'] = False
        stuff = json.dumps(z)

        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('id' in response_data)
        self.assertTrue('escalate_on' in response_data)
        self.assertTrue('escalate_boundary' in response_data)
        self.assertTrue('uframe_filter_id' in response_data)
        uframe_id = response_data['uframe_filter_id']
        self.assertTrue(uframe_id != z['uframe_filter_id'])
        z_id = response_data['id']
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

        # PUT using alert_Definition from above, modify description field; check with GET
        update_description = 'this is an update!'
        alert_definition['description'] = update_description
        alert_definition['uframe_filter_id'] = uframe_id
        '''
        alert_definition['system_event_definition_id'] = new_definition_id
        alert_definition['user_id'] = 1
        alert_definition['use_email'] = False
        alert_definition['use_redmine'] = True
        alert_definition['use_phone'] = False
        alert_definition['use_log'] = False
        alert_definition['use_sms'] = True
        '''
        good_stuff = json.dumps(alert_definition)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=new_definition_id),headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)

        response = self.client.get(url_for('main.get_alert_alarm_def', id=new_definition_id),content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('description' in data)
        self.assertEquals(update_description, data['description'])

        # PUT valid uframe_filter_id but bad data, generate 400
        alert_definition['uframe_filter_id'] = uframe_id
        alert_definition['event_type'] = 'not_alert_or_alarm'
        stuff = json.dumps(alert_definition)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=new_definition_id), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 409)

        # PUT invalid (nonexistent) uframe_filter_id == 37, generate 404
        alert_definition['uframe_filter_id'] = 379379379
        alert_definition['event_type'] = 'alarm'
        stuff = json.dumps(alert_definition)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=new_definition_id), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 409)

        # PUT data=None, generate 409
        response = self.client.put(url_for('main.update_alert_alarm_def', id=33371), headers=headers, data=None)
        self.assertEquals(response.status_code, 404)

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
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']),8)
        self.assertTrue('alert_alarm_definition' in data)
        definitions = data['alert_alarm_definition']
        #print '\n Number of alert_alarm_definitions: ', len(definitions)

        for definition in definitions:
            if definition['uframe_filter_id'] > 3 and definition['uframe_filter_id'] != 2228:      # not retiring filterId 1 or 2 right now
                url = url_for('main.delete_alert_alarm_definition', id=definition['id'])
                response = self.client.delete(url, headers=headers)
                self.assertEquals(response.status_code, 200)

        # Delete all alertfilter ids (where id > 3)
        #if verbose: print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)

        # ======== NEVER USE THIS CODE EXCEPT FOR TEST DEVELOPMENT ===========
        #self.scrub_alertfilters()
        # ======== NEVER USE THIS CODE EXCEPT FOR TEST DEVELOPMENT ===========

        if verbose: print '\n '

    def test_create_alert_alarm_def_description(self):

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create alarm definition
        rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        definition = self.create_alert_alarm_definition(rd, 'alarm', 2, 1)

        response = self.client.get(url_for('main.get_alert_alarm_def', id=1), content_type=content_type,headers=headers)
        self.assertEquals(response.status_code, 200)

        # PUT using definition from above, description = None
        tmp = definition.to_json()
        tmp['description'] = None
        good_stuff = json.dumps(tmp)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=definition.id),headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)

        # PUT using definition from above, high_value = None and low_value = None
        tmp = definition.to_json()
        tmp['description'] = 'something'
        tmp['high_value'] = None
        tmp['low_value'] = None
        good_stuff = json.dumps(tmp)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=definition.id),headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 409)

        # PUT using definition from above, reference_designator = None
        tmp = definition.to_json()
        tmp['description'] = 'something'
        tmp['high_value'] = 10.0
        tmp['low_value'] = 5.0
        tmp['reference_designator'] = None
        good_stuff = json.dumps(tmp)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=definition.id),headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 409)

        # PUT using definition from above, reference_designator = None
        tmp = definition.to_json()
        tmp['description'] = 'something'
        tmp['high_value'] = 10.0
        tmp['low_value'] = 5.0
        tmp['reference_designator'] = rd[0:5]
        good_stuff = json.dumps(tmp)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=definition.id),headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 409)

    def test_create_alert_alarm_negative(self):

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create alarm definition
        rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        definition = self.create_alert_alarm_definition(rd, 'alarm', 2, 1)
        response = self.client.get(url_for('main.get_alert_alarm_def', id=1), content_type=content_type,headers=headers)
        self.assertEquals(response.status_code, 200)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create alarm which uses invalid uframe_filter_id
        # error: 'Insufficient data, or bad data format; Failed to retrieve SystemEventDefinition for uframe_filter_id: 10'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = definition.id
        uframe_event_id = 100
        uframe_filter_id = 10 #definition.uframe_filter_id
        instrument_name = definition.reference_designator
        instrument_parameter = definition.instrument_parameter
        operator = definition.operator
        high_value = definition.high_value
        low_value = definition.low_value
        event_response_message = "(test) Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response.data is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create alarm which uses definition active = False
        # error:
        #  'Insufficient data, or bad data format. Failed to create alert_alarm; system_event_definition (id:1) is not active.'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        definition_id = definition.id
        try:
            definition.active = False
            db.session.add(definition)
            db.session.commit()
        except:
            print '\n exception: failed to set active to False'

        definition = SystemEventDefinition.query.get(definition_id)

        event_type = 'alarm'
        system_event_definition_id = definition.id
        uframe_event_id = 100
        uframe_filter_id = definition.uframe_filter_id
        instrument_name = definition.reference_designator
        instrument_parameter = definition.instrument_parameter
        operator = definition.operator
        high_value = definition.high_value
        low_value = definition.low_value
        event_response_message = "(test) Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create alarm which uses definition retired = True
        # error:
        # 'Insufficient data, or bad data format. Failed to create alert_alarm - system_event_definition is retired. (1)'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        definition_id = definition.id
        try:
            definition.active = True
            definition.retired = True
            db.session.add(definition)
            db.session.commit()
        except:
            print '\n exception: failed to set retired to True'

        definition = SystemEventDefinition.query.get(definition_id)

        event_type = 'alarm'
        system_event_definition_id = definition.id
        uframe_event_id = 100
        uframe_filter_id = definition.uframe_filter_id
        instrument_name = definition.reference_designator
        instrument_parameter = definition.instrument_parameter
        operator = definition.operator
        high_value = definition.high_value
        low_value = definition.low_value
        event_response_message = "(test) Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Create new alarm definition
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        definition_id = definition.id
        try:
            definition.active = True
            definition.retired = False
            definition.user_id = 1
            db.session.add(definition)
            db.session.commit()
        except:
            print '\n exception: failed to set array_name to None'

        definition = SystemEventDefinition.query.get(definition_id)
        new_definition = definition.to_json()
        new_definition['array_name'] = 'RI'
        new_definition['user_id'] = 1
        new_definition['use_email'] = True
        new_definition['use_redmine'] = True
        new_definition['use_phone'] = True
        new_definition['use_log'] = True
        new_definition['use_sms'] = True
        bad_def = json.dumps(new_definition)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=bad_def)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('id' in response_data)
        new_alarm_definition_id = response_data['id']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Create new alarm instance using new definition
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        new_alert_definition = SystemEventDefinition.query.get(new_alarm_definition_id)
        try:
            new_alert_definition.event_type = 'alert'
            db.session.add(new_alert_definition)
            db.session.commit()
        except:
            print '\n failed to create new alert definition'

        event_type = 'alert'
        system_event_definition_id = new_alert_definition.id
        uframe_event_id = 100
        uframe_filter_id = new_alert_definition.uframe_filter_id
        instrument_name = new_alert_definition.reference_designator
        instrument_parameter = new_alert_definition.instrument_parameter
        operator = new_alert_definition.operator
        high_value = new_alert_definition.high_value
        low_value = new_alert_definition.low_value
        event_response_message = "(test) Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Create new alert definition
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Create new alert instance using new definition
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alert'
        system_event_definition_id = new_definition['id']
        uframe_event_id = -1
        uframe_filter_id = new_definition['uframe_filter_id']
        instrument_name = new_definition['reference_designator']
        instrument_parameter = new_definition['instrument_parameter']
        operator = new_definition['operator']
        high_value = new_definition['high_value']
        low_value = new_definition['low_value']
        event_response_message = "(test) Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        self.assertTrue('ticket_id' in response_data)



        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Create alarm which uses SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = definition.id
        uframe_event_id = 100
        uframe_filter_id = definition.uframe_filter_id
        instrument_name = definition.reference_designator
        instrument_parameter = definition.instrument_parameter
        operator = definition.operator
        high_value = definition.high_value
        low_value = definition.low_value
        event_response_message = "(test) Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        '''

    def test_user_event_notification_alarm(self):
        verbose = self.verbose
        debug = False
        if verbose: print '\n'

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Data setup. (Now have three arrays, three platforms, each populated with instruments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        reference_designator = "CE01ISSP-XX099-01-CTDPFJ999"
        # Create and alert and an alarm
        test_alarm = self.create_alert_alarm_definition(reference_designator, event_type='alarm', uframe_id=2, severity=1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=test_alarm.id), headers=headers)
        self.assertEquals(response.status_code, 200)
        alarm_definition = json.loads(response.data)
        if debug: print '\n -- alarm_definition: ', alarm_definition
        self.assertTrue(alarm_definition is not None)

        # Get user_event_notifications (1)
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get a valid uframe_event_id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://uframe-test.ooi.rutgers.edu:12577/alertalarms/inv/CE01ISSP/XX099/01-CTDPFJ999?acknowledged=false
        url = 'http://uframe-test.ooi.rutgers.edu:12577/alertalarms/inv/CE01ISSP/XX099/01-CTDPFJ999?acknowledged=false'
        uframe_url, timeout, timeout_read = self.get_uframe_info()
        response = requests.get(url, timeout=(timeout, timeout_read))
        alarms = json.loads(response.content)
        if alarms is None:
            self.assertEquals('Failed to get alarms from uframe',0)

        tmp = alarms[0]

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alarm instance which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = alarm_definition['id']
        uframe_event_id = tmp['eventId'] #100
        uframe_filter_id = alarm_definition['uframe_filter_id']
        instrument_name = alarm_definition['reference_designator']
        instrument_parameter = alarm_definition['instrument_parameter']
        operator = alarm_definition['operator']
        high_value = alarm_definition['high_value']
        low_value = alarm_definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        alarm = SystemEvent.query.get(response_data['id'])

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        notification = None
        for item in notifications:
            notification = UserEventNotification.query.get(item['id'])
            break
        try:
            db.session.delete(notification)
            db.session.commit()
        except:
            self.assertEquals('error deleting notification', 0)

        # Get user_event_notifications (0)
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 0)

        # Try to acknowledge the alarm when definition does not have a user event_notification - force error.
        # This section requires LIVE/REAL uframe 'uframe_event_id' retuned from qpid message
        ack_data = {}
        ack_data['id'] = alarm.id
        ack_data['uframe_event_id'] = alarm.uframe_event_id  # actual eventID value from qpid message
        ack_data['uframe_filter_id'] = alarm.uframe_filter_id
        ack_data['system_event_definition_id'] = alarm_definition['id'] #system_event_definition_id
        ack_data['event_type'] = alarm.event_type
        ack_data['ack_by'] = 1

        # Expect error: 'Insufficient data, or bad data format; Failed to identify user_event_notification with id: 1'
        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 409)
        response_data = json.loads(response.data)
        #print '\n response_data: ', response_data
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        '''
        self.assertTrue('acknowledged' in response_data)
        self.assertTrue('ack_by' in response_data)
        self.assertTrue('ts_acknowledged' in response_data)
        self.assertEquals(response_data['acknowledged'], True)
        self.assertEquals(response_data['ack_by'], 1)
        self.assertTrue(response_data['ts_acknowledged'] is not None)
        '''

    def test_user_event_notification_alert(self):
        """

        """
        verbose = self.verbose
        debug = False
        if verbose: print '\n'

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # # Create an alert
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        reference_designator = "CE01ISSP-XX099-01-CTDPFJ999"
        test_alert = self.create_alert_alarm_definition(reference_designator, event_type='alert', uframe_id=2, severity=1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=test_alert.id), headers=headers)
        self.assertEquals(response.status_code, 200)
        alert_definition = json.loads(response.data)
        self.assertTrue(alert_definition is not None)

        # Get user_event_notifications (1)
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 1)

        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get any valid uframe_event_id for ALARM which has not been acknowledged
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://uframe-test.ooi.rutgers.edu:12577/alertalarms/inv/CE01ISSP/XX099/01-CTDPFJ999?acknowledged=false
        url = 'http://uframe-test.ooi.rutgers.edu:12577/alertalarms/inv/CE01ISSP/XX099/01-CTDPFJ999?acknowledged=false'
        uframe_url, timeout, timeout_read = self.get_uframe_info()
        response = requests.get(url, timeout=(timeout, timeout_read))
        alarms = json.loads(response.content)
        if alarms is None:
            self.assertEquals('Failed to get alarms from uframe',0)
        '''

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alert which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alert'
        system_event_definition_id = alert_definition['id']
        uframe_filter_id = alert_definition['uframe_filter_id']
        instrument_name = alert_definition['reference_designator']
        instrument_parameter = alert_definition['instrument_parameter']
        operator = alert_definition['operator']
        high_value = alert_definition['high_value']
        low_value = alert_definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
        event_data = {}
        event_data['uframe_event_id'] = -1
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
        alert = SystemEvent.query.get(response_data['id'])

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Checkpoint: Have alert definition, verified user_event_notification exists,
        # have a uframe_event_id for uframe
        #
        # Force delete user_event_notifications (just created for alert and alarm)
        #for id in notification_ids:
        try:
            notification = UserEventNotification.query.get(notifications[0]['id'])
            db.session.delete(notification)
            db.session.commit()
        except:
            self.assertEquals('error deleting notification', 0)

        # Get user_event_notifications (should be 0)
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 0)

        # Try to acknowledge the alarm when definition does not have a user event_notification - force error.
        # This section requires LIVE/REAL uframe 'uframe_event_id' retuned from qpid message
        ack_data = {}
        ack_data['id'] = alert.id
        ack_data['uframe_event_id'] = alert.uframe_event_id  # actual eventID value from qpid message
        ack_data['uframe_filter_id'] = alert.uframe_filter_id
        ack_data['system_event_definition_id'] = alert_definition['id'] #system_event_definition_id
        ack_data['event_type'] = alert.event_type
        ack_data['ack_by'] = 1

        # Expect error: 'Insufficient data, or bad data format; Failed to identify user_event_notification with id: 1'
        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 409)
        response_data = json.loads(response.data)
        #print '\n response_data: ', response_data
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)

    def test_alarm_acknowledgement(self):
        verbose = self.verbose
        debug = False
        if verbose: print '\n'

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # # Create alert and an alarm
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        reference_designator = "CE01ISSP-XX099-01-CTDPFJ999"
        # Create and alert and an alarm
        test_alarm = self.create_alert_alarm_definition(reference_designator, event_type='alarm', uframe_id=2, severity=1)
        test_alert = self.create_alert_alarm_definition(reference_designator, event_type='alert', uframe_id=-1, severity=1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=test_alarm.id), headers=headers)
        self.assertEquals(response.status_code, 200)
        alarm_definition = json.loads(response.data)
        if debug: print '\n -- alarm_definition: ', alarm_definition
        self.assertTrue(alarm_definition is not None)

        # Get user_event_notifications (1)
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 2)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get a valid uframe_event_id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # http://uframe-test.ooi.rutgers.edu:12577/alertalarms/inv/CE01ISSP/XX099/01-CTDPFJ999?acknowledged=false
        url = 'http://uframe-test.ooi.rutgers.edu:12577/alertalarms/inv/CE01ISSP/XX099/01-CTDPFJ999?acknowledged=false'
        uframe_url, timeout, timeout_read = self.get_uframe_info()
        response = requests.get(url, timeout=(timeout, timeout_read))
        alarms = json.loads(response.content)
        if alarms is None:
            self.assertEquals('Failed to get alarms from uframe',0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alarm instance which uses an INVALID SystemEventDefinition id (expect failure)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tmp = alarms[0]
        event_type = 'alarm'
        system_event_definition_id = test_alarm.id #90909090 #alarm_definition['id']
        uframe_event_id = tmp['eventId'] #100
        uframe_filter_id = alarm_definition['uframe_filter_id']
        instrument_name = alarm_definition['reference_designator']
        instrument_parameter = alarm_definition['instrument_parameter']
        operator = alarm_definition['operator']
        high_value = alarm_definition['high_value']
        low_value = alarm_definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
        event_data = {}
        event_data['uframe_event_id'] = uframe_event_id
        event_data['uframe_filter_id'] = uframe_filter_id
        event_data['system_event_definition_id'] = test_alert.id #system_event_definition_id
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

        alarm = SystemEvent.query.get(response_data['id'])
        '''
        try:
            db.session.delete(test_alert)
            db.session.commit()
        except Exception as err:
            print '\n Unable to delete test_alert.', err.message
            self.assertEquals('Unable to delete test_alert.', 0)
        '''

        # Try to acknowledge the alarm when definition does not have a user event_notification - force error.
        # This section requires LIVE/REAL uframe 'uframe_event_id' returned from qpid message (re: ooi-ui-alerts uframe_qpid)
        ack_data = {}
        ack_data['id'] = alarm.id
        ack_data['uframe_event_id'] = alarm.uframe_event_id  # actual eventID value from qpid message
        ack_data['uframe_filter_id'] = alarm.uframe_filter_id
        ack_data['system_event_definition_id'] = alarm_definition['id'] #system_event_definition_id
        ack_data['event_type'] = alarm.event_type
        ack_data['ack_by'] = 1

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alarm instance which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
        #print '\n response_data: ', response_data
        self.assertTrue('acknowledged' in response_data)
        self.assertTrue('ack_by' in response_data)
        self.assertTrue('ts_acknowledged' in response_data)
        self.assertEquals(response_data['acknowledged'], True)
        self.assertEquals(response_data['ack_by'], 1)
        self.assertTrue(response_data['ts_acknowledged'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Expect error: 'Insufficient data, or bad data format; Failed to identify user_event_notification with id: 1'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = alarm_definition['id']
        uframe_event_id = tmp['eventId']
        uframe_filter_id = alarm_definition['uframe_filter_id']
        instrument_name = alarm_definition['reference_designator']
        instrument_parameter = alarm_definition['instrument_parameter']
        operator = alarm_definition['operator']
        high_value = alarm_definition['high_value']
        low_value = alarm_definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        alarm = SystemEvent.query.get(response_data['id'])

        # Try to acknowledge the alarm when definition does not have a user event_notification - force error.
        # This section requires LIVE/REAL uframe 'uframe_event_id' retuned from qpid message
        ack_data = {}
        ack_data['id'] = alarm.id
        ack_data['uframe_event_id'] = alarm.uframe_event_id  # actual eventID value from qpid message
        ack_data['uframe_filter_id'] = alarm.uframe_filter_id
        ack_data['system_event_definition_id'] = alarm_definition['id'] #system_event_definition_id
        ack_data['event_type'] = alarm.event_type
        ack_data['ack_by'] = 1

        # Expect error: 'Insufficient data, or bad data format; Failed to identify user_event_notification with id: 1'
        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 409)
        response_data = json.loads(response.data)
        #print '\n response_data: ', response_data
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)


    def test_SystemEventDefinitions_uframe_integration(self):
        """
        Test alert_alarm_definition integration with uframe. (exercise SystemEventDefinition class)
        """
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_alertfilter_ids = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm_definition when there aren't any
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alerts_alarms_def'), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definitions = json.loads(response.data)
        self.assertTrue(definitions is not None)
        self.assertTrue('alert_alarm_definition' in definitions)
        self.assertTrue(definitions['alert_alarm_definition'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm_definition by id when there aren't any  ( {"error": "alert_alarm_definition not found"} )
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=8989), content_type=content_type)
        self.assertEquals(response.status_code, 404)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' not in definition)
        self.assertTrue('error' in definition)
        self.assertTrue(definition['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alert definitions (do not provide 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': False,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', 'escalate_on': 5, 'escalate_boundary': 10,
                "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False, "use_log": False,
                "use_sms": True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers,data=request_data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('id' in definition)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), headers=headers)
        self.assertEquals(response.status_code, 200)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST Update to description field; this also performs uframe alertfilter update
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        updated_description = 'alertfilter updated!'
        data['description'] = updated_description
        data['uframe_filter_id'] = alert_alarm_def_uframe_id
        data['id'] = definition_id

        # Add user_event_notification fields for update
        data['user_id'] = 1
        data['use_email'] = False
        data['use_redmine'] = False
        data['use_phone'] = False
        data['use_log'] = False
        data['use_sms'] = False
        good_stuff = json.dumps(data)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=definition_id),
                                   headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET updated alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), content_type=content_type)
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
        # Check whether ok to delete alert_alarm_definition (no instances, should be ok)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.ok_to_delete_alert_alarm_definition', id=definition_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('status' in response_data)
        self.assertEquals(response_data['status'], True)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clean up by deleting ('retired') alert_alarm_def
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        #response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)


    def test_SystemEvent_uframe_integration(self):
        """
        Test alert_alarm integration with uframe. (exercise SystemEvent class)
        """
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_alertfilter_ids = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm when there aren't any
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alerts_alarms'), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        events = json.loads(response.data)
        self.assertTrue(events is not None)
        self.assertTrue('alert_alarm' in events)
        self.assertTrue(events['alert_alarm'] is not None)
        self.assertEquals(len(events['alert_alarm']), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm by id when there aren't any alerts or alarms ( {"error": "alert_alarm not found"} )
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm', id=8989), content_type=content_type)
        self.assertEquals(response.status_code, 404)
        events = json.loads(response.data)
        self.assertTrue(events is not None)
        self.assertTrue('alert_alarm' not in events)
        self.assertTrue('error' in events)
        self.assertTrue(events['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alarm definitions (no 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                'user_id': 1, 'use_email': False, 'use_redmine': True, 'use_phone': False,
                'use_log': False, 'use_sms': True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('id' in definition)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check whether ok to delete alert_alarm_definition (no instances, should be ok)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.ok_to_delete_alert_alarm_definition', id=definition_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('status' in response_data)
        self.assertEquals(response_data['status'], True)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alarm which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = definition_id
        uframe_event_id = 945
        uframe_filter_id = definition['uframe_filter_id']
        instrument_name = definition['reference_designator']
        instrument_parameter = definition['instrument_parameter']
        operator = definition['operator']
        high_value = definition['high_value']
        low_value = definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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
        # (Negative) Check whether ok to delete alert_alarm_definition (have alarm instance, should NOT be ok)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.ok_to_delete_alert_alarm_definition', id=definition_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('status' in response_data)
        self.assertEquals(response_data['status'], False)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Try to delete alert_alarm_def when alert_alarm instance not yet acknowledged.
        # response_data:
        #   {u'error': u'There are existing alert_alarm instances using this id which have not yet been acknowledged.'}
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('error' in response_data)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using non-existent alert or alarm id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = 999
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 892, 'event_type': 'alarm',
        # 'system_event_definition_id': 1, 'acknowledged': True,
        # 'uframe_event_id': 100, 'ack_by': 1, 'id': 999}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 409)        # message 'Failed to retrieve alert_alarm.'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using non-existent ack_by = None
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = None

        # sample BAD ack_data:  {'uframe_filter_id': 2388, 'event_type': 'alarm', 'system_event_definition_id': 1,
        # 'uframe_event_id': 945, 'ack_by': None, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 400)        # message 'Required value ack_by is empty or None.'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using non-existent system_event_definition_id = 999
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = 999 #system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 2436, 'event_type': 'alarm', 'system_event_definition_id': 999,
        # 'uframe_event_id': 945, 'ack_by': 1, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409) # message 'Acknowledge failed to retrieve SystemEventDefinition (id: 999)'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using bad uframe_filter_id = 1010101
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = 1010101 #uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 2436, 'event_type': 'alarm', 'system_event_definition_id': 999,
        # 'uframe_event_id': 945, 'ack_by': 1, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409) # message 'Acknowledge failed to retrieve SystemEventDefinition (id: 999)'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using bad uframe_filter_id = 1010101
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = 'blah' #event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 2436, 'event_type': 'alarm', 'system_event_definition_id': 999,
        # 'uframe_event_id': 945, 'ack_by': 1, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409) # message 'Acknowledge failed to retrieve SystemEventDefinition (id: 999)'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)


        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Acknowledge alert_alarm
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        '''
        # This section requires LIVE/REAL uframe 'uframe_event_id' retuned from qpid message
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id  # actual eventID value from qpid message
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = 1

        # sample GOOD ack_data:  {'uframe_filter_id': 892, 'event_type': 'alarm',
        # 'system_event_definition_id': 1, 'acknowledged': True,
        # 'uframe_event_id': 100, 'ack_by': 1 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue('acknowledged' in response_data)
        self.assertTrue('ack_by' in response_data)
        self.assertTrue('ts_acknowledged' in response_data)
        self.assertEquals(response_data['acknowledged'], True)
        self.assertEquals(response_data['ack_by'], 1)
        self.assertTrue(response_data['ts_acknowledged'] is not None)
        '''

        # Manual acknowledgement of alarm, requires updating SystemEvent
        # Manually set acknowledgement fields for unit test of acknowledge; can't get uframe eventId from qpid message.
        # todo Investigate uframe REST interface for alertalarm to query individual entries in
        # todo uframe alertalarm metadatabase for eventID
        # Note: when uframe performs acknowledgement of alarm, the alertfilter associated with the alarm is
        # immediately 'retired' and longer available. The ooi-ui-services does NOT retire the SystemEventDefinition
        # until the delete_alert_alarm_definition is executed. This means individual alerts and alarms can be acknowledged
        # without the alert and alarm definition being removed. MISMATCH: uframe has already removed the alert filter for
        # the definition.
        # todo Review and discuss implications to ooi-ui-services, workflow, etc.
        '''
        tmp_definition = SystemEventDefinition.query.get(system_event_definition_id)
        self.assertTrue(tmp_definition is not None)
        try:
            tmp_definition.retired = True
            tmp_definition.ts_retired = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
            db.session.add(tmp_definition)
            db.session.commit()
        except:
            print '\n Exception persisting SystemEventDefinition when do not have qpid process.'
            self.assertEquals(1,0)
        '''
        tmp_event = SystemEvent.query.get(alert_alarm_id)
        self.assertTrue(tmp_event is not None)
        try:
            tmp_event.acknowledged = True
            tmp_event.ack_by = 1
            tmp_event.ts_acknowledged = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
            db.session.add(tmp_event)
            db.session.commit()
        except:
            print '\n Exception in workaround persisting SystemEvent when do not have qpid process.'
            self.assertEquals(1,0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check whether ok to delete alert_alarm_definition (has single acknowledged instance, should be ok)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.ok_to_delete_alert_alarm_definition', id=definition_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('status' in response_data)
        self.assertEquals(response_data['status'], True)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clean up by retiring alert_alarm_def
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertEquals(len(response_data), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert_alarm_definition by id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue('retired' in definition)
        self.assertTrue('ts_retired' in definition)
        self.assertEquals(definition['retired'], True)
        self.assertTrue(definition['retired'] is not None)
        save_ts_retired = definition['ts_retired']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete alert_alarm_def (which is already retired)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertEquals(len(response_data), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert/alarm definition by id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue('retired' in definition)
        self.assertTrue('ts_retired' in definition)
        self.assertEquals(definition['retired'], True)
        self.assertTrue(definition['retired'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete non existing alert_alarm_definition ( {error': 'alert_alarm_definition not found' )
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=909090)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n filter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)

    def test_SystemEventDefinition_required_fields(self):
        """
        Test alert_alarm integration with uframe. (exercise SystemEvent class)
        """
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_alertfilter_ids = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm when there aren't any
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alerts_alarms'), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        events = json.loads(response.data)
        self.assertTrue(events is not None)
        self.assertTrue('alert_alarm' in events)
        self.assertTrue(events['alert_alarm'] is not None)
        self.assertEquals(len(events['alert_alarm']), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create some alarm definitions - missing a required field ('active')
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0',
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                'user_id': 1, 'use_email': False, 'use_redmine': True, 'use_phone': False,
                'use_log': False, 'use_sms': True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        '''
        self.assertTrue('id' in definition)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)
        '''

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create some alarm definitions - event_type is None
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': None,
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                'user_id': 1, 'use_email': False, 'use_redmine': True, 'use_phone': False,
                'use_log': False, 'use_sms': True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        '''
        self.assertTrue('id' in definition)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)
        '''

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create some alarm definitions - event_type is invalid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': 'junk',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                'user_id': 1, 'use_email': False, 'use_redmine': True, 'use_phone': False,
                'use_log': False, 'use_sms': True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        '''
        self.assertTrue('id' in definition)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)
        '''

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create some alarm definitions - operator is None
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': None, 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                'user_id': 1, 'use_email': False, 'use_redmine': True, 'use_phone': False,
                'use_log': False, 'use_sms': True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        '''
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)
        '''

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create some alarm definitions - operator is invalid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'BAD_OPERATOR', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                'user_id': 1, 'use_email': False, 'use_redmine': True, 'use_phone': False,
                'use_log': False, 'use_sms': True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 409)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        '''
        self.assertTrue('id' in definition)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)
        '''


    def test_SystemEvent_uframe_integration_negative(self):
        """
        Test alert_alarm integration with uframe. (exercise SystemEvent class with bad values.)
        """
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_alertfilter_ids = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm when there aren't any
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alerts_alarms'), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        events = json.loads(response.data)
        self.assertTrue(events is not None)
        self.assertTrue('alert_alarm' in events)
        self.assertTrue(events['alert_alarm'] is not None)
        self.assertEquals(len(events['alert_alarm']), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm by id when there aren't any alerts or alarms ( {"error": "alert_alarm not found"} )
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm', id=8989), content_type=content_type)
        self.assertEquals(response.status_code, 404)
        events = json.loads(response.data)
        self.assertTrue(events is not None)
        self.assertTrue('alert_alarm' not in events)
        self.assertTrue('error' in events)
        self.assertTrue(events['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alarm definitions (no 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                'user_id': 1, 'use_email': False, 'use_redmine': True, 'use_phone': False,
                'use_log': False, 'use_sms': True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('id' in definition)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('description' in definition)
        definition_id = definition['id']
        alert_alarm_def_uframe_id = definition['uframe_filter_id']
        list_alertfilter_ids.append(alert_alarm_def_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert/alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check whether ok to delete alert_alarm_definition (no instances, should be ok)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.ok_to_delete_alert_alarm_definition', id=definition_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('status' in response_data)
        self.assertEquals(response_data['status'], True)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alarm which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = definition_id
        uframe_event_id = 945
        uframe_filter_id = definition['uframe_filter_id']
        instrument_name = definition['reference_designator']
        instrument_parameter = definition['instrument_parameter']
        operator = definition['operator']
        high_value = definition['high_value']
        low_value = definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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

        # Bad thing to do - update alert_alarm directly to force error
        tmp_alert_alarm = SystemEvent.query.get(alert_alarm_id)
        if tmp_alert_alarm is not None:
            tmp_alert_alarm.uframe_event_id = 898989
            try:
                db.session.add(tmp_alert_alarm)
                db.session.commit()
            except:
                db.session.rollback()
                self.assertTrue('Failed to update SystemEvent with bad uframe_event_id', 'error')

        #print '\n BAD uframe_event_id: ', tmp_alert_alarm.uframe_event_id
        bad_alert_alarm_uframe_event_id = tmp_alert_alarm.uframe_event_id

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Check whether ok to delete alert_alarm_definition (have alarm instance, should NOT be ok)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.ok_to_delete_alert_alarm_definition', id=definition_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('status' in response_data)
        self.assertEquals(response_data['status'], False)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Try to delete alert_alarm_def when alert_alarm instance not yet acknowledged.
        # response_data:
        #   {u'error': u'There are existing alert_alarm instances using this id which have not yet been acknowledged.'}
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('error' in response_data)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using bad alert_alarm_id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = bad_alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 892, 'event_type': 'alarm',
        # 'system_event_definition_id': 1, 'acknowledged': True,
        # 'uframe_event_id': 100, 'ack_by': 1, 'id': 999}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        response_data = json.loads(response.data)
        #print '\n response_data: ', response_data
        self.assertEquals(response.status_code, 409)        # message 'Failed to retrieve alert_alarm.'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using non-existent ack_by = None
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = None

        # sample BAD ack_data:  {'uframe_filter_id': 2388, 'event_type': 'alarm', 'system_event_definition_id': 1,
        # 'uframe_event_id': 945, 'ack_by': None, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 400)        # message 'Required value ack_by is empty or None.'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using non-existent system_event_definition_id = 999
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = 999 #system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 2436, 'event_type': 'alarm', 'system_event_definition_id': 999,
        # 'uframe_event_id': 945, 'ack_by': 1, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409) # message 'Acknowledge failed to retrieve SystemEventDefinition (id: 999)'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using bad uframe_filter_id = 1010101
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = 1010101 #uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 2436, 'event_type': 'alarm', 'system_event_definition_id': 999,
        # 'uframe_event_id': 945, 'ack_by': 1, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409) # message 'Acknowledge failed to retrieve SystemEventDefinition (id: 999)'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Acknowledge alert_alarm using bad uframe_filter_id = 1010101
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ack_data = {}
        ack_data['id'] = alert_alarm_id
        ack_data['uframe_event_id'] = alert_alarm_uframe_event_id
        ack_data['uframe_filter_id'] = uframe_filter_id
        ack_data['system_event_definition_id'] = system_event_definition_id
        ack_data['event_type'] = 'blah' #event_type
        ack_data['ack_by'] = 1

        # sample BAD ack_data:  {'uframe_filter_id': 2436, 'event_type': 'alarm', 'system_event_definition_id': 999,
        # 'uframe_event_id': 945, 'ack_by': 1, 'id': 1}

        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        response_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409) # message 'Acknowledge failed to retrieve SystemEventDefinition (id: 999)'
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        tmp_event = SystemEvent.query.get(alert_alarm_id)
        self.assertTrue(tmp_event is not None)
        try:
            tmp_event.acknowledged = True
            tmp_event.ack_by = 1
            tmp_event.ts_acknowledged = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
            db.session.add(tmp_event)
            db.session.commit()
        except:
            print '\n Exception in workaround persisting SystemEvent when do not have qpid process.'
            self.assertEquals(1,0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check whether ok to delete alert_alarm_definition (has single acknowledged instance, should be ok)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.ok_to_delete_alert_alarm_definition', id=definition_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('status' in response_data)
        self.assertEquals(response_data['status'], True)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clean up by retiring alert_alarm_def
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertEquals(len(response_data), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert_alarm_definition by id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue('retired' in definition)
        self.assertTrue('ts_retired' in definition)
        self.assertEquals(definition['retired'], True)
        self.assertTrue(definition['retired'] is not None)
        save_ts_retired = definition['ts_retired']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete alert_alarm_def (which is already retired)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertEquals(len(response_data), 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert/alarm definition by id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue('retired' in definition)
        self.assertTrue('ts_retired' in definition)
        self.assertEquals(definition['retired'], True)
        self.assertTrue(definition['retired'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete non existing alert_alarm_definition ( {error': 'alert_alarm_definition not found' )
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.delete_alert_alarm_definition', id=909090)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n filter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)

    def test_SystemEventDefinition_operators(self):
        """
        The list of valid uframe operators for SystemEventDefinition is:
            ['GREATER', 'LESS', 'BETWEEN_EXCLUSIVE', 'OUTSIDE_EXCLUSIVE']
        """
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
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

    def test_SystemEventDefinition_update_user_notification(self):
        """
        Execute update_alert_alarm_definition with the 'update_user_event_notification' parameter set to True.
        This should update the user_event_definition when update_alert_alarm_definition is invoked.
        """
        #todo add negative test for user_event_processing, including roll back processing on failure
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        filter_ids = []
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Alarm - Valid alert_alarm_definition data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        key_list = ['use_email', 'use_redmine', 'use_phone', 'use_log', 'use_sms']
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
        }

        # - - Create alert_alarm_definition (Alarm)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=json.dumps(data))
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('uframe_filter_id' in definition)
        self.assertTrue('id' in definition)
        definition_id = definition['id']
        uframe_filter_id = definition['uframe_filter_id']
        filter_ids.append(uframe_filter_id)

        # - - Get alert_alarm_def
        url = url_for('main.get_alerts_alarms_def', id=definition_id)
        response = self.client.get(url, headers=headers, content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' in definition)
        self.assertEquals(len(definition['alert_alarm_definition']), 1)


        # - - Put update_alert_alarm_def including 'update_user_event_notification' switch
        data["update_user_event_notification"] = True
        data['uframe_filter_id'] = uframe_filter_id

        for key in key_list:
            data[key] = True
        good_stuff = json.dumps(data)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=definition_id),
                                   headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

        # - - Get user_event_notification created from create_alert_alarm_def
        url = url_for('main.get_user_event_notifications')
        response = self.client.get(url, headers=headers, content_type=content_type)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue('notifications' in response_data)
        self.assertEquals(len(response_data['notifications']), 1)
        notifications = response_data['notifications']
        for key in key_list:
            self.assertTrue(key in notifications[0])
            self.assertEquals(notifications[0][key], True)

        # - - Get alert_alarm_def (which has been updated)
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, headers=headers, content_type=content_type)
        self.assertEquals(response.status_code, 200)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' in definition)
        self.assertEquals(len(definition['alert_alarm_definition']), 1)

        # - - Clean up by retiring alert_alarm_def
        url = url_for('main.delete_alert_alarm_definition', id=definition_id)
        response = self.client.delete(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertEquals(len(response_data), 0)

        # - - Get alert_alarm_def (which has been deleted)
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
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
              "stream": "ctdpf_j_cspp_instrument",
              "escalate_on": 5,
              "escalate_boundary": 10,
              "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
              "use_log": False, "use_sms": True
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

        if verbose: print '\n '


    def test_SystemEvent_query_filter_options(self):
        """
        Test alert_alarm (SystemEvent class) query filter options provided in request.args

        Current filter options for request.args:
            'type', 'method', 'deployment', 'acknowledged', 'array_name', 'platform_name', 'instrument_name',
            'reference_designator', 'active', 'retired'
        """
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create alert_alarm_definitions and alert_alarm instances with route /create_alert_alarm.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        alarm_definition_id, alert_definition_id, filter_ids = self.create_valid_definition_and_events()

        # Configure test case items for exercising filter variables
        valid_filter_items = ['type', 'method', 'deployment', 'acknowledged',
                              'array_name', 'platform_name', 'instrument_name',
                              'reference_designator', 'active', 'retired']
        valid_filter_values = {
                                'type': ['alert', 'alarm'],
                                'method': ['telemetered', 'discovered'],
                                'deployment' : [1, 2],
                                'acknowledged' : ['true', 'false'],
                                'array_name' : ['CE', 'CP'],
                                'platform_name' : ['CE01ISSP-XX099'],
                                'instrument_name' : ['CE01ISSP-XX099-01-CTDPFJ999'],
                                'reference_designator' : ['CE01ISSP-XX099-01-CTDPFJ999'],
                                'active' : ['true', 'false'],
                                'retired' : ['true', 'false'],
                            }
        valid_filter_counts = {
                                'type': [ 1, 1],
                                'method': [ 2, 0],
                                'deployment' : [ 2, 0],
                                'acknowledged' : [ 0, 2],
                                'array_name' : [ 2, 0],
                                'platform_name' : [ 2 ],
                                'instrument_name' : [ 2 ],
                                'reference_designator' : [ 2 ],
                                'active' : [ 2, 0],
                                'retired' : [ 0, 2]
                            }
        invalid_filter_values = {
                                'type': [None, '', 'foo', 'Alert', 'Alarm'],
                                'method': [None, ''],
                                'deployment': [None, 'a', True, ''],
                                'acknowledged': [None, 'a', ''],
                                'array_name': ['CP'],
                                'platform_name': [None, '', 'no platform'],
                                'instrument_name': [None, '', 'no instrument', 'CE01ISSP-XX099-01-'],
                                'reference_designator': [None, '', 'no reference_designator','CE01ISSP-XX099-01-'],
                                'active': [None, '', 'a'],
                                'retired': [None, '', 'a']
                            }
        invalid_filter_counts = {
                                'type': [ 2, 2, 0, 0, 0, 0 ],
                                'method': [ 0, 0],
                                'deployment' : [ 2, 2, 2, 2],
                                'acknowledged' : [ 2, 2, 2],
                                'array_name' : [ 0 ],
                                'platform_name' : [ 0, 0, 0],
                                'instrument_name' : [ 0, 0, 0, 0],
                                'reference_designator' : [ 0, 0, 0, 0],
                                'active' : [ 0, 0, 2],
                                'retired' : [ 2, 2, 2]
                            }

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check each filter variable individually, expect success for all
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for key in valid_filter_items:
            inx = 0
            for value in valid_filter_values[key]:
                url = url_for('main.get_alerts_alarms')
                url += '?%s=%s' % (key, value)
                if verbose: print root+url
                response = self.client.get(url, content_type=content_type, headers=headers)
                self.assertEquals(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue('alert_alarm' in data)
                self.assertEquals(len(data['alert_alarm']), valid_filter_counts[key][inx])
                inx += 1

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check each filter variable individually, expect failure for all
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for key in valid_filter_items:
            inx = 0
            for value in invalid_filter_values[key]:
                url = url_for('main.get_alerts_alarms')
                url += '?%s=%s' % (key, value)
                if verbose: print '-- ', root+url
                response = self.client.get(url, content_type=content_type, headers=headers)
                self.assertEquals(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue('alert_alarm' in data)
                self.assertEquals(len(data['alert_alarm']), invalid_filter_counts[key][inx])
                inx += 1

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilters created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n filter_ids(%d): %s' % (len(filter_ids), filter_ids)
        self.delete_alertfilters(filter_ids)

        if verbose: print '\n'

    def test_SystemEventDefinition_query_filter_options(self):
        """
        Test alert_alarm_definition (SystemEvent class) query filter options provided in request.args
        Current filter options for request.args:
            'retired', 'array_name', 'platform_name', 'instrument_name', 'reference_designator'
        """
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        # Configure test case items for exercising filter variables
        valid_filter_items = ['array_name', 'platform_name', 'instrument_name',
                              'reference_designator', 'retired']
        valid_filter_values = {
                                'array_name' : ['CE', 'CP'],
                                'platform_name' : ['CE01ISSP-XX099'],
                                'instrument_name' : ['CE01ISSP-XX099-01-CTDPFJ999'],
                                'reference_designator' : ['CE01ISSP-XX099-01-CTDPFJ999'],
                                'retired' : ['true', 'false'],
                            }
        valid_filter_counts = {
                                'array_name' : [ 2, 0],
                                'platform_name' : [ 2 ],
                                'instrument_name' : [ 2 ],
                                'reference_designator' : [ 2 ],
                                'retired' : [ 0, 2]
                            }
        invalid_filter_values = {
                                'array_name': ['CP'],
                                'platform_name': [None, '', 'no platform'],
                                'instrument_name': [None, '', 'no instrument', 'CE01ISSP-XX099-01-'],
                                'reference_designator': [None, '', 'no reference_designator','CE01ISSP-XX099-01-'],
                                'retired': [None, '', 'a']
                            }
        invalid_filter_counts = {
                                'array_name' : [ 0 ],
                                'platform_name' : [ 0, 2, 0],
                                'instrument_name' : [ 0, 2, 0, 0],
                                'reference_designator' : [ 0, 2, 0, 0],
                                'retired' : [ 2, 2, 2]
                            }

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create alert_alarm_definitions and alert_alarm instances with route /create_alert_alarm.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        alarm_definition_id, alert_definition_id, filter_ids = self.create_valid_definition_and_events()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check each filter variable individually, expect success for all
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for key in valid_filter_items:
            inx = 0
            for value in valid_filter_values[key]:
                url = url_for('main.get_alerts_alarms_def')
                url += '?%s=%s' % (key, value)
                if verbose: print root+url
                response = self.client.get(url, content_type=content_type, headers=headers)
                self.assertEquals(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue('alert_alarm_definition' in data)
                self.assertEquals(len(data['alert_alarm_definition']), valid_filter_counts[key][inx])
                inx += 1

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check each filter variable individually, expect failure for all
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for key in valid_filter_items:
            inx = 0
            for value in invalid_filter_values[key]:
                url = url_for('main.get_alerts_alarms_def')
                url += '?%s=%s' % (key, value)
                if verbose: print '-- ', root+url
                response = self.client.get(url, content_type=content_type, headers=headers)
                self.assertEquals(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue('alert_alarm_definition' in data)
                self.assertEquals(len(data['alert_alarm_definition']), invalid_filter_counts[key][inx])
                inx += 1

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilters created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print '\n filter_ids(%d): %s' % (len(filter_ids), filter_ids)
        self.delete_alertfilters(filter_ids)

        if verbose: print '\n'

    def convert_from_utc(self, u): return dt.datetime.utcfromtimestamp(u)
    def ut(self, d): return calendar.timegm(d.timetuple())

    def test_reissue_notification_ticket(self):
        """
        Test alert routes associated with the escalation process and subsequent notifications using redmine.

        1. Create alert definition (using route) with low escalate_on and low escalate_boundary values.
        2. Create alerts (using route) until escalate_on reached, continue to escalate_boundary + 1.0.
        3. Verify two redmine tickets have been issued:
            - one when escalate_on is reached and
            - one when escalate_boundary is reached

        Use redmine to fetch tickets created.
        Cleanup: remove alertfilter created in uframe

        """
        verbose = self.verbose
        debug = False
        root = self.root
        if verbose: print '\n'

        self.scrub_alertfilters()

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_filter_ids = []

        escalate_on = 5.0
        escalate_boundary = 10.0

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create valid alert definition (escalate on 5 and escalate_boundary 10)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alert',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'salinity', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": escalate_on, "escalate_boundary": escalate_boundary,
                "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
                "use_log": False, "use_sms": True}

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
        alert_definition_id = alert_definition['id']
        alert_uframe_id = alert_definition['uframe_filter_id']
        list_filter_ids.append(alert_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create alerts
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 3637761438.72, 2015-04-11T17:17:18
        escalate_on = 5.0
        escalate_boundary = 10.0
        alert_time_start = 3637761438.72            # 3607761438.72, 2014-04-29T11:57:18
        alert_escalate_on = alert_time_start + escalate_on
        alert_escalate_boundary = alert_time_start + escalate_boundary
        offset = 2208988800
        ts_event_time = self.convert_from_utc(alert_time_start - offset)

        # Sample loops to generate alerts, verify timestamp
        inx = 0.0
        ts_tmp = alert_time_start
        ticket_id_escalate_on = None
        ticket_id_escalate_boundary = None
        while ts_tmp <= alert_escalate_boundary + 1.0:

            ts_tmp = alert_time_start + inx
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # POST alert which uses the SystemEventDefinition id
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            event_type = 'alert'
            system_event_definition_id = alert_definition_id
            uframe_filter_id = alert_definition['uframe_filter_id']
            event_data = {}
            event_data['uframe_event_id'] = -1
            event_data['uframe_filter_id'] = uframe_filter_id
            event_data['system_event_definition_id'] = system_event_definition_id
            event_data['event_time'] = ts_tmp  #event_time
            event_data['event_type'] = 'alert'
            event_data['event_response'] = 'Test alert %d' % int(inx) #event_response_message
            event_data['method'] = 'telemetered'
            event_data['deployment'] = 1
            new_event = json.dumps(event_data)
            response = self.client.post(url_for('main.create_alert_alarm'), headers=headers, data=new_event)
            self.assertEquals(response.status_code, 201)
            self.assertTrue(response.data is not None)
            response_data = json.loads(response.data)
            self.assertTrue('id' in response_data)
            self.assertTrue(response_data['id'] is not None)

            # create alert using ts_tmp
            if ts_tmp == alert_escalate_on:
                if debug: print '\n ------ Escalate On - Issued redmine ticket...'
                if debug: print '\n ------ ticket_id: ', response_data['ticket_id']
                ticket_id_escalate_on = response_data['ticket_id']
            elif ts_tmp > alert_escalate_boundary:
                if debug: print '\n ------ Escalate Boundary - Reissue redmine ticket...'
                if debug: print '\n ------ ticket_id: ', response_data['ticket_id']
                ticket_id_escalate_boundary = response_data['ticket_id']
            if debug: print '\n Created alert (%d) for %s' % (int(inx+1),
                                                     dt.datetime.strftime(self.convert_from_utc(ts_tmp - offset),
                                                                          "%Y-%m-%dT%H:%M:%S"))

            inx += 1.0

        if debug: print '\n ------ ticket_id_escalate_on: ', ticket_id_escalate_on
        if debug: print '\n ------ ticket_id_escalate_boundary: ', ticket_id_escalate_boundary

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(list_filter_ids) != 0:
            if debug: print '\n list_alertfilter_ids(%d): %s' % (len(list_filter_ids), list_filter_ids)
            self.delete_alertfilters(list_filter_ids)
        if verbose: print '\n'

    def test_z_last_test_scrub(self):

        self.scrub_alertfilters()
        #print '\n last test to execute...'

    def test_uframe_get_instrument_metadata(self):
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

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
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.uframe_get_instrument_metadata', ref='CE01ISSM-SBD17-04-VELPTA000'), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private test helper methods and tests
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create_valid_definition_and_events(self):
        """
        Create valid alert_alarm_definitions (2) and alert_alarm instances (2) to use in test cases.
        reference designator: 'CE01ISSP-XX099-01-CTDPFJ999'
        """
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        list_filter_ids = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create (1) valid alarm definition and user event_notification (no 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
                "use_log": False, "use_sms": True}

        request_data = json.dumps(data)
        response = self.client.post(url_for('main.create_alert_alarm_def'), headers=headers, data=request_data)
        self.assertEquals(response.status_code, 201)
        self.assertTrue(response is not None)
        self.assertTrue(response.data is not None)
        alarm_definition = json.loads(response.data)
        self.assertTrue(alarm_definition is not None)
        self.assertTrue('id' in alarm_definition)
        self.assertTrue('uframe_filter_id' in alarm_definition)
        self.assertTrue('description' in alarm_definition)
        alarm_definition_id = alarm_definition['id']
        alarm_uframe_id = alarm_definition['uframe_filter_id']
        list_filter_ids.append(alarm_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alarm_definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create (2) valid alert definition (no 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alert',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'salinity', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5, "escalate_boundary": 10,
                "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
                "use_log": False, "use_sms": True}

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
        alert_definition_id = alert_definition['id']
        alert_uframe_id = alert_definition['uframe_filter_id']
        list_filter_ids.append(alert_uframe_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alert definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=alert_definition_id), content_type=content_type)
        self.assertEquals(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alarm instance which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alarm'
        system_event_definition_id = alarm_definition_id
        uframe_event_id = 100
        uframe_filter_id = alarm_definition['uframe_filter_id']
        instrument_name = alarm_definition['reference_designator']
        instrument_parameter = alarm_definition['instrument_parameter']
        operator = alarm_definition['operator']
        high_value = alarm_definition['high_value']
        low_value = alarm_definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # POST alert which uses the SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_type = 'alert'
        system_event_definition_id = alert_definition_id
        uframe_event_id = 100
        uframe_filter_id = alert_definition['uframe_filter_id']
        instrument_name = alert_definition['reference_designator']
        instrument_parameter = alert_definition['instrument_parameter']
        operator = alert_definition['operator']
        high_value = alert_definition['high_value']
        low_value = alert_definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72
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

        return alarm_definition_id, alert_definition_id, list_filter_ids

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
        self.assertEquals(response.status_code, 200)
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
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertEquals(len(data['alert_alarm_definition']), 0)

        # http://localhost:4000/alert_alarm_definition?platform_name=platform
        for platform in platforms:
            if verbose: print '\nPlatform: ', platform
            url = url_for('main.get_alerts_alarms_def')
            url += '?platform_name=%s' % platform
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertEquals(len(data['alert_alarm_definition']), 0)

        # http://localhost:4000/alert_alarm_definition?instrument_name=instrument
        for instrument in instruments:
            if verbose: print '\nInstrument: ', instrument
            url = url_for('main.get_alerts_alarms_def')
            url += '?instrument_name=%s' % instrument
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertEquals(len(data['alert_alarm_definition']), 0)

        # http://localhost:4000/alert_alarm_definition?reference_designator=instrument
        for instrument in instruments:
            if verbose: print '\nReference Designator: ', instrument
            url = url_for('main.get_alerts_alarms_def')
            url += '?reference_designator=%s' % instrument
            if verbose: print root+url
            response = self.client.get(url, content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('alert_alarm_definition' in data)
            self.assertEquals(len(data['alert_alarm_definition']), 0)

        if verbose: print '\n'

        return

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
        else:
            instrument_deployment = InstrumentDeployment(reference_designator=instrument_reference_designator)
            instrument_deployment.reference_designator = platform_deployment_id
            db.session.add(instrument_deployment)
            db.session.commit()
        return instrument_deployment

    def create_alert_alarm_definition(self, instrument_reference_designator, event_type, uframe_id, severity):
        # Note, creates a definition in test database only, just used to exercise SystemEventDefinition class
        # but does NOT create alertfilter id in uframe. An alertfilter is created when the /alert_alarm_definition
        # route is called.
        headers = self.get_api_headers('admin', 'test')
        valid_event_type = ['alert','alarm']
        alert_alarm_definition = None
        array_name = instrument_reference_designator[0:0+2]
        platform_name = instrument_reference_designator[0:0+14]
        instrument_parameter = 'temperature'
        instrument_parameter_pdid = 'PD100'
        operator = 'GREATER'
        high_value = '10.0'
        low_value = '1.0'
        stream = 'ctdpf_j_cspp_instrument'
        escalate_on = 5
        escalate_boundary = 10
        user_id = 1
        use_email = False
        use_redmine = True
        use_phone = False
        use_log = False
        use_sms = True
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
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n ***  CP02PMCO-WFP01-02-DOFSTK000 **** message: ', err.message

            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-02-DOFSTK000 UserEventNotification message: \n', err.message

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
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-03-CTDPFK000 alert_alarm_definition message: \n', err.message

            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-03-CTDPFK000 UserEventNotification message: \n', err.message


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
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n *** CP02PMCO-WFP01-05-PARADK000 **** message: ', err.message

            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-05-PARADK000 UserEventNotification message: \n', err.message
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
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n *** %s **** message: %s' % (instrument_reference_designator,err.message)
            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create UserEventNotification message: \n', err.message
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
        Delete test alertfilters in uframe; development helper only to be used during controlled testing.
        """
        debug = False
        if debug: print '\n Deleting alertfilter ids: ', list_of_ids
        headers = self.get_api_headers('admin', 'test')
        uframe_url, timeout, timeout_read = self.get_uframe_info()
        for id in list_of_ids:
            if id > 3 and id != 2228: # not retiring filterId 1, 2, 3 or 2228 right now
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
                if uframe_id > 3 and uframe_id != 2228: # not retiring filterId 1, 2, 3 or 2228 right now
                    list_of_alertfilter_ids.append(uframe_id)
        return list_of_alertfilter_ids

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



