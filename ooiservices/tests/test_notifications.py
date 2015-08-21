#!/usr/bin/env python
'''
Specific testing for Alert and Alarm Notifications (class UserEventNotifications)
'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization
from ooiservices.app.models import SystemEventDefinition, SystemEvent, UserEventNotification
import requests
import datetime as dt
import calendar

from unittest import skipIf
import os

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class NotificationsTestCase(unittest.TestCase):

    # enable verbose during development and documentation to get a list of sample
    # urls used throughout test cases. Always set to False before check in.
    verbose = False
    debug = False
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
        scope = UserScope.query.filter_by(scope_name='redmine').first()
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
        debug = self.debug
        if verbose: print '\n'
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
        # Create alerts
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 3637761438.72, 2015-04-11T17:17:18
        escalate_on = 5.0
        escalate_boundary = 10.0
        alert_time_start = 3637761438.72            # 3607761438.72, 2014-04-29T11:57:18
        alert_escalate_on = alert_time_start + escalate_on
        alert_escalate_boundary = alert_time_start + escalate_boundary
        offset = 2208988800

        # Sample loops to generate alerts, verify timestamp
        inx = 0.0
        ts_tmp = alert_time_start
        ticket_id_escalate_on = None
        ticket_id_escalate_boundary = None
        while ts_tmp <= alert_escalate_boundary + 6.0:

            ts_tmp = alert_time_start + inx
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # POST alert which uses the SystemEventDefinition id
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            system_event_definition_id = alert_definition_id
            uframe_filter_id = alert_definition['uframe_filter_id']
            event_data = {}
            event_data['uframe_event_id'] = -1
            event_data['uframe_filter_id'] = uframe_filter_id
            event_data['system_event_definition_id'] = system_event_definition_id
            event_data['event_time'] = ts_tmp  #event_time
            event_data['event_type'] = 'alert'
            event_data['event_response'] = '[Test] Alert %d' % int(inx) #event_response_message
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
            if ts_tmp == (alert_escalate_on + 1.0):
                if debug: print '\n ------ Escalate On - Issued redmine ticket...'
                if debug: print '\n ------ ticket_id: ', response_data['ticket_id']
                ticket_id_escalate_on = response_data['ticket_id']
            elif ts_tmp == (alert_escalate_boundary + 1.0):
                if debug: print '\n ------ Escalate Boundary reached..............'
                ticket_id_escalate_boundary = response_data['ticket_id']
            elif ts_tmp == (alert_escalate_boundary + 1.0):
                if debug: print '\n ------ Escalate Boundary - Reissue redmine ticket...'
                if debug: print '\n ------ ticket_id: ', response_data['ticket_id']
            elif ts_tmp > (alert_escalate_boundary + 1.0):
                if debug: print '\n ------ Update reissued redmine ticket...'
                if debug: print '\n ------ updated ticket_id: ', response_data['ticket_id']

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
            self.delete_alertfilters(list_filter_ids)
        if verbose: print '\n'


    def test_notification_routes(self):
        """
        Test routes associated with the notifications process for the alerts and alarms.
        """
        verbose = self.verbose
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
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'

        arrays = [array_CE, array_GP, array_CP]
        platforms = [CP02PMCO_WFP01_rd]
        instruments = [DOFSTK000_rd, CTDPFK000_rd, PARADK000_rd]

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Basic positive tests - array, platform, instrument w/o data (no alerts or alarms definitions yet)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alert definitions, including user_event_notifications
        alarm1 = self.create_alert_alarm_definition(ref_def=DOFSTK000_rd, event_type='alarm', uframe_filter_id=2, severity=1)
        alarm2 = self.create_alert_alarm_definition(ref_def=CTDPFK000_rd, event_type='alarm', uframe_filter_id=2, severity=2)
        alarm3 = self.create_alert_alarm_definition(ref_def=PARADK000_rd, event_type='alarm', uframe_filter_id=2, severity=3)
        alert1 = self.create_alert_alarm_definition(ref_def=DOFSTK000_rd, event_type='alert', uframe_filter_id=1, severity=1)
        alert2 = self.create_alert_alarm_definition(ref_def=CTDPFK000_rd, event_type='alert', uframe_filter_id=1, severity=2)
        alert3 = self.create_alert_alarm_definition(ref_def=PARADK000_rd, event_type='alert', uframe_filter_id=1, severity=3)

        # todo Validate alert and alarm fields after create_alert_alarm_definition

        # test /alert_alarm_definition route using request.arg array_name
        for array in arrays:
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
            response_data = json.loads(response.data)
            self.assertTrue(response_data is not None)
            self.assertTrue('id' in response_data)
            inx += 1

        # Check that some SystemEvent (s) have been created...
        url = url_for('main.get_alerts_alarms')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm' in data)
        self.assertTrue(len(data['alert_alarm']) > 0)
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
        z['active'] = True
        z['description'] = ''
        z['high_value'] = '13'
        z['low_value'] = '10'
        z['severity'] = 2
        z['stream'] = 'ctdpf_j_cspp_instrument'
        z['escalate_on'] = 5.0
        z['escalate_boundary'] = 10.0
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
        list_alertfilter_ids.append(uframe_id)

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

        # PUT invalid (nonexistent) uframe_filter_id == 37, generate 400
        alert_definition['uframe_filter_id'] = 37
        alert_definition['event_type'] = 'alarm'
        stuff = json.dumps(alert_definition)
        response = self.client.put(url_for('main.update_alert_alarm_def', id=new_definition_id), headers=headers, data=stuff)
        self.assertEquals(response.status_code, 400)

        # PUT data=None, generate 409
        response = self.client.put(url_for('main.update_alert_alarm_def', id=33371), headers=headers, data=None)
        self.assertEquals(response.status_code, 400)

        # GET invalid id=9876
        response = self.client.get(url_for('main.get_alert_alarm_def', id=9876), content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 400)

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
        for definition in definitions:
            if definition['uframe_filter_id'] > 3 and definition['uframe_filter_id'] != 2228: # not retiring filterId 1 or 2 right now
                url = url_for('main.delete_alert_alarm_definition', id=definition['id'])
                response = self.client.delete(url, headers=headers)
                self.assertEquals(response.status_code, 200)

        # Delete all alertfilter ids (where id > 3)
        self.delete_alertfilters(list_alertfilter_ids)

        if verbose: print '\n '


    def test_notification_routes_negative(self):
        """
        Test routes associated with the notifications process for the alerts and alarms.
        """
        verbose = self.verbose
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
        DOFSTK000_rd = 'CP02PMCO-WFP01-02-DOFSTK000'
        CTDPFK000_rd = 'CP02PMCO-WFP01-03-CTDPFK000'
        PARADK000_rd = 'CP02PMCO-WFP01-05-PARADK000'

        arrays = [array_CE, array_GP, array_CP]
        platforms = [CP02PMCO_WFP01_rd]
        instruments = [DOFSTK000_rd, CTDPFK000_rd, PARADK000_rd]

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alert definitions
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alert definitions (without user_event_notification(s))
        alarm1 = self.create_alert_alarm_definition_wo_notification(ref_def=DOFSTK000_rd, event_type='alarm', uframe_filter_id=2, severity=1)
        alarm2 = self.create_alert_alarm_definition_wo_notification(ref_def=CTDPFK000_rd, event_type='alarm', uframe_filter_id=2, severity=2)
        alarm3 = self.create_alert_alarm_definition_wo_notification(ref_def=PARADK000_rd, event_type='alarm', uframe_filter_id=2, severity=3)
        alert1 = self.create_alert_alarm_definition_wo_notification(ref_def=DOFSTK000_rd, event_type='alert', uframe_filter_id=1, severity=1)
        alert2 = self.create_alert_alarm_definition_wo_notification(ref_def=CTDPFK000_rd, event_type='alert', uframe_filter_id=1, severity=2)
        alert3 = self.create_alert_alarm_definition_wo_notification(ref_def=PARADK000_rd, event_type='alert', uframe_filter_id=1, severity=3)

        # test /alert_alarm_definition route using request.arg array_name
        for array in arrays:
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
        self.assertEquals(data['event_type'], 'alarm')

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
        self.assertEquals(response.status_code, 201)
        response_data = json.loads(response.data)
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
        # Create SystemEvent(s) from invalid SystemEventDefinitions (no user_event_notification)
        # Get alert_alarm_definition(s); loop through and POST new SystemEvent for each
        # todo Verify alert_alarm_def has user_event_notification!!
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

        # Test creating alarm w/o having a user_event_notification for SystemEventDefinition (test error condition)
        tmp_definition = definitions[0]

        self.assertTrue('id' in tmp_definition)
        self.assertTrue('uframe_filter_id' in tmp_definition)
        self.assertTrue('reference_designator' in tmp_definition)
        self.assertTrue('instrument_parameter' in tmp_definition)
        self.assertTrue('instrument_parameter_pdid' in tmp_definition)
        self.assertTrue('operator' in tmp_definition)
        self.assertTrue('high_value' in tmp_definition)
        self.assertTrue('low_value' in tmp_definition)
        self.assertTrue('severity' in tmp_definition)
        self.assertTrue('stream' in tmp_definition)
        self.assertTrue('escalate_on' in tmp_definition)
        self.assertTrue('escalate_boundary' in tmp_definition)
        system_event_definition_id = tmp_definition['id']
        instrument_name = tmp_definition['reference_designator']
        instrument_parameter = tmp_definition['instrument_parameter']
        operator = tmp_definition['operator']
        high_value = tmp_definition['high_value']
        low_value = tmp_definition['low_value']
        event_response_message = "Instrument: {0} condition exceeded where parameter {1} {2} {3} {4}".format(
                                        instrument_name, instrument_parameter, operator, high_value, low_value)
        event_time = 3607761438.72      # uframe sample event_time float: 3607761438.72
        event_data = {}
        event_data['uframe_event_id'] = inx * 314       # instance
        event_data['uframe_filter_id'] = tmp_definition['uframe_filter_id']
        event_data['system_event_definition_id'] = system_event_definition_id
        event_data['event_time'] = event_time
        event_data['event_type'] = tmp_definition['event_type']
        event_data['event_response'] = event_response_message
        event_data['method'] = 'telemetered'
        event_data['deployment'] = 1
        event_data['ticket_id'] = 0     # default, i.e. no ticket
        new_event = json.dumps(event_data)
        response = self.client.post(url_for('main.create_alert_alarm'), headers=headers,data=new_event)
        self.assertEquals(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertTrue('message' in response_data)
        self.assertTrue(len(response_data['message']) > 0)
        self.assertEquals(len(response_data), 2)

        # Add user_event_notifications
        notification = self.create_user_event_notification(alarm1.id)
        notification = self.create_user_event_notification(alarm2.id)
        notification = self.create_user_event_notification(alarm3.id)
        notification = self.create_user_event_notification(alert1.id)
        notification = self.create_user_event_notification(alert2.id)
        notification = self.create_user_event_notification(alert3.id)

        inx = 1
        for definition in definitions:
            #print '\n definition event_type: ', definition['event_type']
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
            #event_type = 'alarm'
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
            event_data['uframe_filter_id'] = definition['uframe_filter_id'] # definition - hardcoded for now; uframe update required
            event_data['system_event_definition_id'] = system_event_definition_id
            event_data['event_time'] = event_time
            event_data['event_type'] = definition['event_type']
            event_data['event_response'] = event_response_message
            event_data['method'] = 'telemetered'
            event_data['deployment'] = 1
            event_data['ticket_id'] = 0     # default, i.e. no ticket
            new_event = json.dumps(event_data)
            response = self.client.post(url_for('main.create_alert_alarm'), headers=headers,data=new_event)
            self.assertEquals(response.status_code, 201)
            response_data = json.loads(response.data)
            self.assertTrue(response_data is not None)
            self.assertTrue('id' in response_data)
            self.assertTrue('event_type' in response_data)
            self.assertEquals(response_data['event_type'], definition['event_type'])
            inx += 1

        # Check that some SystemEvent (s) have been created...
        url = url_for('main.get_alerts_alarms')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm' in data)
        self.assertTrue(len(data['alert_alarm']) > 0)
        if verbose:
            aa_events = data['alert_alarm']
            for event in aa_events:
                print '\n\nevent: ', event

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get alert and alarm definitions; loop through and delete definitions which have
        # uframe_filter_id values > 2  (during development).
        # Verify the corresponding alertfilter have been removed in uframe.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.get_alerts_alarms_def')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('alert_alarm_definition' in data)
        self.assertEquals(len(data['alert_alarm_definition']),7)
        self.assertTrue('alert_alarm_definition' in data)
        definitions = data['alert_alarm_definition']
        for definition in definitions:
            if definition['uframe_filter_id'] > 3 and definition['uframe_filter_id'] != 2228: # not retiring filterId 1, 2, 3 or 2228 right now
                url = url_for('main.delete_alert_alarm_definition', id=definition['id'])
                response = self.client.delete(url, headers=headers)
                if definition['id'] in list_alertfilter_ids:
                    self.assertEquals(response.status_code, 200)
                else:
                    self.assertEquals(response.status_code, 400)

        # Delete all alertfilter ids (where id > 3)
        self.delete_alertfilters(list_alertfilter_ids)
        if verbose: print '\n '

    def scrub_alertfilters(self):
        debug = False
        # ======== Only use for TEST DEVELOPMENT ===========
        # Get all alertfilter ids (where id > 3)
        list_alertfilter_ids = self.get_alertfilters()
        list_alertfilter_ids.sort()
        if debug: print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)

        # Delete all alertfilter ids (where id > 3)
        if debug: print '\n list_alertfilter_ids(%d): %s' % (len(list_alertfilter_ids), list_alertfilter_ids)
        self.delete_alertfilters(list_alertfilter_ids)
        return

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
        self.assertEquals(response.status_code, 400)
        definition = json.loads(response.data)
        self.assertTrue(definition is not None)
        self.assertTrue('alert_alarm_definition' not in definition)
        self.assertTrue('error' in definition)
        self.assertTrue(definition['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create some alert definitions (do not provide 'id' or 'uframe_filter_id' on create)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'platform_name': u'CE01ISSP-XX099', 'high_value': u'31.0', 'event_type': u'alarm',
                'stream': u'ctdpf_j_cspp_instrument', 'severity': 2, 'low_value': u'10.0', 'active': True,
                'array_name': u'CE', 'reference_designator': u'CE01ISSP-XX099-01-CTDPFJ999',
                'operator': u'GREATER', 'instrument_name': u'CE01ISSP-XX099-01-CTDPFJ999',
                'instrument_parameter': u'temperature', 'instrument_parameter_pdid': u'PD440',
                'description': 'initial', "escalate_on": 5.0, "escalate_boundary": 10.0,
                "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
                "use_log": False, "use_sms": True}
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
        self.assertEquals(response.status_code, 200)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.delete_alertfilters(list_alertfilter_ids)

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
                'description': 'initial', "escalate_on": 5.0, "escalate_boundary": 10.0,
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
                'description': 'initial', "escalate_on": 5.0, "escalate_boundary": 10.0,
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

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET /alert_alarm by id when there aren't any alerts or alarms ( {"error": "alert_alarm not found"} )
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm', id=8989), content_type=content_type)
        self.assertEquals(response.status_code, 400)
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
                'description': 'initial', "escalate_on": 5.0, "escalate_boundary": 10.0,
                "user_id": 1, "use_email": False, "use_redmine": True, "use_phone": False,
                "use_log": False, "use_sms": True}

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
        uframe_event_id = 100
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
        # Check whether ok to delete alert_alarm_definition (have alarm instance, should NOT be ok)
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
        ack_data['acknowledged'] = True
        ack_data['ack_by'] = 'admin'
        ack_data['ack_for'] = None
        ack_data['ts_acknowledged'] = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        acknowledged_event = json.dumps(ack_data)
        response = self.client.post(url_for('main.acknowledge_alert_alarm'), headers=headers, data=acknowledged_event)
        self.assertEquals(response.status_code, 409)
        response_data = json.loads(response.data)
        self.assertTrue('error' in response_data)
        self.assertTrue('message' in response_data)
        self.assertTrue(response_data['message'] is not None)
        self.assertTrue(response_data['error'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Force Acknowledge alert_alarm
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tmp_event = SystemEvent.query.get(alert_alarm_id)
        self.assertTrue(tmp_event is not None)
        try:
            tmp_event.acknowledged = True
            tmp_event.ack_by = 1
            tmp_event.ts_acknowledged = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
            db.session.add(tmp_event)
            db.session.commit()
        except:
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
        self.assertEquals(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete all uframe alertfilter ids created during test case (id > 3)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.delete_alertfilters(list_alertfilter_ids)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private test helper methods and tests
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create_user_event_notification(self, alert_alarm_definition_id):
        user_id = 1
        use_email = False
        use_redmine = True
        use_phone = False
        use_log = False
        use_sms = True
        try:
            # Create corresponding UserEventNotification when alert or alarm definition is created
            notification = UserEventNotification.insert_user_event_notification(
                                                 system_event_definition_id=alert_alarm_definition_id,
                                                 user_id=user_id,
                                                 use_email=use_email,
                                                 use_redmine=use_redmine,
                                                 use_phone=use_phone,
                                                 use_log=use_log,
                                                 use_sms=use_sms)
            return notification

        except Exception as err:
            message = 'Failed to create user_event_notification; %s' % err.message
            raise Exception(message)


    def create_alert_alarm_definition(self, ref_def, event_type, uframe_filter_id, severity):
        # Note, creates a definition in test database only, just used to exercise SystemEventDefinition class
        # but does NOT create alertfilter id in uframe. An alertfilter is created when the /alert_alarm_definition
        # route is called.
        alert_alarm_definition = None
        array_name = ref_def[0:0+2]
        platform_name = ref_def[0:0+14]
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
        if ref_def is not None:
            alert_alarm_definition = SystemEventDefinition(reference_designator=ref_def)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = ref_def
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_filter_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except:
                raise

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
            except:
                raise
        return alert_alarm_definition

    def create_alert_alarm_definition_wo_notification(self, ref_def, event_type, uframe_filter_id, severity):
        # Note, creates a definition in test database only, just used to exercise SystemEventDefinition class
        # but does NOT create alertfilter id in uframe. An alertfilter is created when the /alert_alarm_definition
        # route is called.
        alert_alarm_definition = None
        array_name = ref_def[0:0+2]
        platform_name = ref_def[0:0+14]
        instrument_parameter = 'temperature'
        instrument_parameter_pdid = 'PD100'
        operator = 'GREATER'
        high_value = '10.0'
        low_value = '1.0'
        stream = 'ctdpf_j_cspp_instrument'
        escalate_on = 5
        escalate_boundary = 10
        create_time = dt.datetime.now()
        if ref_def is not None:
            alert_alarm_definition = SystemEventDefinition(reference_designator=ref_def)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = ref_def
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_filter_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except:
                raise

        return alert_alarm_definition

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
            if id > 3 and id != 2228:
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
                if uframe_id > 3 and uframe_id != 2228:
                    list_of_alertfilter_ids.append(uframe_id)
        return list_of_alertfilter_ids
