#!/usr/bin/env python
"""
Specific testing for calibration event routes

"""
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from random import randint
from flask import (url_for)
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.uframe.event_tools import (get_rd_by_asset_id, get_uframe_event)
from ooiservices.app.uframe.deployment_tools import (is_instrument)
from ooiservices.app.uframe.events_create_update import get_calibration_event_id
import datetime
from unittest import skipIf
import os

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''


@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class CruiseEventTestCase(unittest.TestCase):

    # enable verbose (during development and documentation) to get a list of
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
        scope = UserScope.query.filter_by(scope_name='redmine').first()     # added
        admin.scopes.append(scope)
        scope = UserScope.query.filter_by(scope_name='asset_manager').first()
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
    """
    def suite(self):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(self.test_calibration_events()))
        return suite

    if __name__ == "__main__":
        unittest.main()
    """
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Test cases
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test calibration events.
    def test_calibration_events(self):
        """
        Create CALIBRATION_DATA event. Only applied for instrument ('Sensor') assets.
        http://uframe-3-test.ooi.rutgers.edu:12587/asset/cal?uid=A00679, or,
        http://uframe-3-test.ooi.rutgers.edu:12587/asset?uid=A00679
        {
          "@class" : ".XCalibrationData",
          "values" : [ -1.493703E-4 ],
          "dimensions" : [ 1 ],
          "comments" : "Test entry",
          "cardinality" : 0,
          "assetUid" : "A00679",
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_a0",
          "eventStartTime" : 1443614400000
        }


        Scalar value
          "values" : [ 10.0 ],
          "dimensions" : [ 1 ],
          "cardinality" : 0,

        One dimensional array of n values
          "values" : [ 10.0, 11.0, 12.0 ... 20.0 ],   // eleven values in array
          "dimensions" : [ 11 ],
          "cardinality" : 1,

        Two dimensional array of m times n values
          "values" : [ 10.0, 11.0, 12.0, 20.0, 21.0, 22.0, 30.0, 31.0, 32.0  ],   // 3 x 3 array
          "dimensions" : [ 3, 3 ],
          "cardinality" : 2,

        http://host:12587/asset/cal/A00679

        Sample input:
            input = {
              "@class" : ".XCalibrationData",
              "values" : [ -1.493703E-4 ],
              "dimensions" : [ 1 ],
              "comments" : "Test entry",
              "cardinality" : 0,
              "assetUid" : "A00679",
              "eventType" : "CALIBRATION_DATA",
              "eventName" : "CC_a0",
              "eventStartTime" : 1443614400000
            }

        """
        debug = self.debug
        verbose = self.verbose
        event_type = 'CALIBRATION_DATA'
        if verbose: print '\n'
        #if verbose: print '\n event_types: ', event_types

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add cruise event to a mooring asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n ----------------------------------'
            print '\n Creating %s event ...' % event_type

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        have_instrument_id = False
        instrument_id = None
        instrument_uid = None
        instrument_rd = None

        count = 0
        while not have_instrument_id and count <= number_of_assets:

            count +=1
            asset_index = randint(0, (number_of_assets-1))
            #print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            if is_instrument(rd):
                if not have_instrument_id:
                    have_instrument_id = True
                    instrument_id = asset_id
                    instrument_uid = asset_uid
                    instrument_rd = rd
        if verbose:
            print '\n Note: Number of loops to get instrument asset: %d ' % count
            print '\n ----- Instrument:'
            print '\n\t instrument_id: %d' % instrument_id
            print '\n\t instrument_uid: %s' % instrument_uid
            print '\n\t instrument_rd: %s' % instrument_rd

        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Create calibration event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        input = self.create_event_data_calibration(event_type, instrument_uid, instrument_rd)
        #input['eventName'] = 'CC_a1'
        event_name = input['eventName']
        if verbose: print '\n\tCalibration create...'
        if debug: print '\n\tCalibration create input: ', input
        # Create event
        event_id, last_modified = self._create_event_type_calibration(event_type, instrument_uid, input, event_name)
        if verbose: print '\n input: ', self.dump_dict(input, debug)
        self.assertTrue(input is not None)
        self.assertTrue('assetUid' in input)
        self.assertTrue(input['assetUid'] is not None)
        if verbose:
            print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
            print '\n\tNow performing an UPDATE on event we just created...'

        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Update event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update the cruise we just created
        if verbose: print '\n\tCalibration update...'
        update_input = self.update_event_data_calibration(event_type, instrument_uid, event_id, last_modified, event_name)
        self.assertTrue(update_input is not None)
        self.assertTrue('eventId' in update_input)
        self.assertEquals(int(update_input['eventId']), event_id)
        self.assertTrue('assetUid' in update_input)
        self.assertEquals(update_input['assetUid'], instrument_uid)
        if not isinstance(update_input['eventId'], int):
            if verbose: print '\n debug -- test case -- event_id is not instance of int...'
            update_input['eventId'] = int(str(update_input['eventId']))
            self.assertTrue(isinstance(update_input['eventId'], int))
        if verbose: print '\n\tUpdated eventId: %d' % update_input['eventId']
        update_event_id = self._update_event_type_calibration(event_type, update_input, event_id,
                                                              instrument_uid, event_name)
        self.assertTrue(update_event_id is not None)
        self.assertTrue(isinstance(update_event_id, int))
        if verbose: print '\n\tUpdated eventId: %d' % update_event_id

        # Check eventId against eventId returned on update.
        if verbose: print '\n\tCalibration update - check results...'
        if debug: print '\n instrument_uid: ', instrument_uid
        if debug: print '\n event_name: ', event_name
        event_id, last_modified = self.get_calibration_event_id_last_modified(instrument_uid, event_name)
        self.assertTrue(event_id is not None)
        self.assertTrue(last_modified is not None)
        self.assertEquals(update_event_id, event_id)

        # Get calibration event, check input contents are reflected in 'updated' event.
        event = get_uframe_event(event_id)
        if debug: print '\n\tUpdated calibration data event(id: %d): %s' % (event_id, event)
        self.assertTrue(event is not None)
        input_keys = input.keys()
        update_input_keys = update_input.keys()
        event_keys = event.keys()
        self.assertTrue(len(event_keys) > len(input_keys))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Try to create same event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n (Negative) Calibration create input: ', input
        event_id, last_modified = self._create_event_type_negative(event_type, instrument_uid, input, event_name)
        if verbose:
            print '\n\t(Negative) Create eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

        if verbose: print '\n'


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_id_uid_rd(self, asset):
        """ For an asset, get id, uid and rd.
        """
        debug = False
        try:
            # Get asset_id
            self.assertTrue('id' in asset)
            asset_id = asset['id']
            self.assertTrue(asset_id is not None)
            self.assertTrue(asset_id)
            if debug: print '\n Have asset_id: %d' % asset_id

            # Get asset uid
            self.assertTrue('uid' in asset)
            asset_uid = asset['uid']
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_uid)
            if debug: print '\n Have asset_uid: %s ' % asset_uid

            # Get reference designator
            rd = get_rd_by_asset_id(asset_id)
            if debug: print '\n Have rd: %s ' % rd

            return asset_id, asset_uid, rd

        except Exception:
            print '\n exception getting asset id, uid and rd.'
            return None, None, None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create event_type
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _create_event_type_calibration(self, _event_type, uid, input, event_name):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        self.assertTrue(uid is not None)
        self.assertTrue(event_name is not None)
        # Define variables specific to event type
        if verbose: print '\n -------------- Creating new event of type %s' % _event_type
        target_event_type = _event_type
        key = target_event_type

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET event types
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test_url = url_for('uframe.get_event_type')
        response = self.client.get(test_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('event_types' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are event_types in a list
        events_by_type = results['event_types']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, list))
        if debug: print '\n -- len(events_by_type): ', len(events_by_type)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug ********\n test CREATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = url_for('uframe.create_event')
        if debug: print '\n create url: ', url
        data = json.dumps(input)
        response = self.client.post(url, headers=headers, data=data)
        if debug:
            print '\n Create calibration event -- response.status_code: ', response.status_code
            if response.status_code != 204:
                print '\n Create calibration event -- response.content: ', json.loads(response.data)
        self.assertEquals(response.status_code, 200)

        if debug: print '\n instrument_uid: ', uid
        if debug: print '\n event_name: ', event_name
        event_id, last_modified = self.get_calibration_event_id_last_modified(uid, event_name)
        self.assertTrue(event_id is not None)
        self.assertTrue(last_modified is not None)
        self.assertTrue(event_id > 0)
        return event_id, last_modified

    def get_calibration_event_id_last_modified(self, uid, event_name):
        """
        Get calibration event id from asset by event name.
        """
        debug = False
        self.assertTrue(uid is not None)
        self.assertTrue(event_name is not None)
        if debug:
            print '\n get_calibration_event_id_last_modified: uid: ', uid
            print '\n get_calibration_event_id_last_modified: event_name: ', event_name
        error_text = ' uid: ' + uid + ', event name: ' + event_name
        try:

            # Get asset by uid, retrieve eventId and name from calibration event.
            event_id = None
            last_modified = None
            try:
                event_id, last_modified = get_calibration_event_id(uid, event_name)
            except Exception as err:
                self.assetEquals('Failed to get event id for calibration', event_name + ' ' + str(err))

            if debug: print '\n Calibration event_id: %r, uid: %s, last_modified: %d' % (event_id, uid, last_modified)
            self.assertTrue(event_id is not None)
            self.assertTrue(isinstance(event_id, int))
            self.assertTrue(event_id > 0)
            self.assertTrue(last_modified is not None)
            return event_id, last_modified

        except Exception as err:
            message = 'Failed to get event id for calibration event for ' + error_text + '.' + str(err)
            self.assertEquals('Failed to get event id for calibration event for ', error_text)
            raise Exception(message)

    def _create_event_type_negative(self, _event_type, uid, input, event_name):
        """
        Create calibration event (which already exists.)
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Define variables specific to event type
        if verbose: print '\n -------------- [negative] Try to create calibration event which already exists...'
        target_event_type = _event_type
        key = target_event_type

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET event types
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test_url = url_for('uframe.get_event_type')
        response = self.client.get(test_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('event_types' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are event_types in a list
        events_by_type = results['event_types']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, list))
        if debug: print '\n -- len(events_by_type): ', len(events_by_type)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug ********\n test CREATE request_data(%d): %r' % (len(input),
                                            json.dumps(input, indent=4, sort_keys=True))

        url = url_for('uframe.create_event')
        if debug: print '\n create url: ', url
        data = json.dumps(input)
        response = self.client.post(url, headers=headers, data=data)
        if debug: print '\n Create calibration event -- response.status_code: ', response.status_code
        self.assertEquals(response.status_code, 400)

        event_id, last_modified = self.get_calibration_event_id_last_modified(uid, event_name)
        self.assertTrue(event_id is not None)
        self.assertTrue(last_modified is not None)
        return event_id, last_modified

    def request_headers(self):
        """ Headers for uframe PUT and POST. """
        return {"Content-Type": "application/json"}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Update event_type calibration. Return event_id and last_modified (timestamp)
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _update_event_type_calibration(self, _event_type, input, event_id, uid, event_name):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n **** Update %s event' % _event_type
            print '\n **** Update event_id: %r' % event_id
            print '\n **** Update input: %r' % input

        self.assertTrue('eventId' in input)
        self.assertTrue(input['eventId'] is not None)
        self.assertTrue(isinstance(input['eventId'], int))
        if debug:
            print '\n debug ********\n test update -- UPDATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = url_for('uframe.update_event', id=event_id)
        if verbose: print '\n **** Update url: ', url
        data = json.dumps(input)
        response = self.client.put(url, headers=headers, data=data)
        if debug: print '\n uframe update response.status_code: ', response.status_code
        if response.status_code != 200 and response.status_code != 204:
            if debug: print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            if debug: print '\n response_error: ', response_error

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue('event' in response_data)
        event = response_data['event']
        self.assertTrue(event is not None)
        #print '\n debug -- event: ', event
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)

        update_event_id, last_modified = self.get_calibration_event_id_last_modified(uid, event_name)
        self.assertTrue(event_id is not None)
        self.assertTrue(last_modified is not None)
        self.assertEquals(update_event_id, event_id)
        event_id = int(str(event['eventId']))
        self.assertTrue(event_id is not None)
        self.assertTrue(isinstance(event_id, int))
        self.assertTrue(event_id > 0)
        return event_id

    def get_some_assets(self):
        """
        Get assets to assist in testing events.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')
        try:
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # (Positive) GET assets
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            url = url_for('uframe.get_assets')
            if verbose: print '\n ----- url: ', url
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue('assets' in results)
            if debug: print '\n -- len(results): ', len(results)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            # Verify there are asset objects in a list
            assets = results['assets']
            self.assertTrue(assets is not None)
            self.assertTrue(isinstance(assets, list))
            if debug: print '\n -- len(assets): ', len(assets)

            return assets

        except Exception as err:
            if verbose: print '\n exception: ', str(err)
            return None

    # Data used to create different event types.
    def create_event_data(self, event_type, uid, rd):
        input = {}
        unique_num = randint(1, 1000)
        unique_float = randint(1, 1000) * 100.0
        notes = 'Create new %s event for %s, (assetUid: %s); unique number: %d' % (event_type, rd, uid, unique_num)
        if event_type == 'ACQUISITION':
            input = {
                      'purchasePrice': unique_float,
                      'purchaseDate': None,
                      'deliveryDate': None,
                      'purchasedBy': None,
                      'vendorIdentification': None,
                      'vendorPointOfContact': None,
                      'receivedFromVendorBy': None,
                      'authorizationNumber': None,
                      'authorizationForPayment': None,
                      'invoiceNumber': 'invoice number: ' + str(unique_num),
                      'eventType': 'ACQUISITION',
                      'eventName': rd,
                      'eventStartTime': None,
                      'eventStopTime': None,
                      'notes': notes,
                      'tense': 'UNKNOWN',
                      'dataSource': None,
                      'assetUid': uid
                      }

        elif event_type == 'ASSET_STATUS':
            input = {
                    'severity': 5,
                    'reason': str(unique_num),
                    'location': None,
                    'status': None,
                    'eventType': 'ASSET_STATUS',
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
                    }

        elif event_type == 'ATVENDOR':
            input = {
                    'reason': 'Broken during storm at sea.',
                    'authorizationNumber': str(unique_num),
                    'vendorIdentification': None,
                    'authorizationForPayment': None,
                    'invoiceNumber': None,
                    'vendorPointOfContact': None,
                    'sentToVendorBy': None,
                    'receivedFromVendorBy' : None,
                    'eventType': 'ATVENDOR',
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
                    }

        elif event_type == 'CRUISE_INFO':
            # Make some unique key in form: 'EE-2016-0102'
            unique_num = randint(105, 990)
            uniqueCruiseIdentifer = 'XX-2016-0' + str(unique_num)
            #'cruiseIdentifier': 'Test EE Cruise Info 2016',
            input = {
                    'uniqueCruiseIdentifier': uniqueCruiseIdentifer,
                    'shipName': 'Scarlett OHara',
                    'eventType': 'CRUISE_INFO',
                    'eventStartTime': 1453308000000,
                    'eventStopTime': 1453508700000,
                    'notes': notes,
                    'eventName': 'Test XX Cruise Info 2016',
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': None,
                    'editPhase': None
                    }

        elif event_type == 'INTEGRATION':
            unique_num = randint(1, 200)
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*2)
            input = {
                    'integrationInto': None,
                    'deploymentNumber': 3,
                    'versionNumber': 1,
                    'integratedBy': 'Engineer, RPS ASA',
                    'eventType': 'INTEGRATION',
                    'eventName':  rd,
                    'eventStartTime': eventStartTime,
                    'eventStopTime': 1405382400000,
                    'notes': notes + str(unique_num),
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
                    }

        elif event_type == 'LOCATION':
            unique_num = randint(201, 300)
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*2)
            input = {
                    'depth': 551.27,
                    'longitude': -70.77599,
                    'latitude': 40.36341,
                    'orbitRadius': 0.0,
                    'eventType': 'LOCATION',
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
                    }

        elif event_type == 'RETIREMENT':
            unique_num = randint(301, 400)
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*2)
            input = {
                    'reason': 'All done with this.' + str(unique_num),
                    'disposition': 'Unknown',
                    'retiredBy': 'Engineer at RPS ASA',
                    'eventType': 'RETIREMENT',
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'eventName': rd + str(unique_num),
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
                    }

        elif event_type == 'STORAGE':
            unique_num = randint(301, 400)
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*3)
            input = {
                    'buildingName': 'Tower' + str(unique_num),
                    'eventName': rd,
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'eventType': 'STORAGE',
                    'notes': notes,
                    'performedBy': 'Engineer, RPS ASA',
                    'physicalLocation': 'Narragansett, RI',
                    'roomIdentification': '23',
                    'shelfIdentification': 'Cube 7-27',
                    'dataSource': str(unique_num),
                    'tense': None,
                    'assetUid': uid
                    }

        elif event_type == 'UNSPECIFIED':
            unique_num = randint(401, 500)
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*2)
            input = {
                    'dataSource': str(unique_num),
                    'eventName': rd + str(unique_num),
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'eventType': 'UNSPECIFIED',
                    'notes': notes + str(unique_num),
                    'tense': 'UNKNOWN',
                    'assetUid': uid
                    }

        string_input = self.get_event_input_as_string(input)
        return uid, string_input

    def create_event_data_calibration(self, event_type, uid, rd):
        input = {}
        debug = False
        if debug: print '\n Create new %s event for %s, (assetUid: %s)' % (event_type, rd, uid)
        if event_type == 'CALIBRATION_DATA':
            #"@class" : ".XCalibrationData",
            event_name = 'CC_test_' + uid
            # 'CC_a0'
            if debug: print '\n Create new %s...' % event_type
            input = {
                      'assetUid': uid,
                      'cardinality': 0,
                      'comments': 'Test entry',
                      'dimensions': [ 1 ],
                      'eventType': 'CALIBRATION_DATA',
                      'eventName': event_name,
                      'eventStartTime': 1443614400000,
                      'values': [ -1.493703E-4 ],
                      'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                      'dataSource': 'Test data ' + str(datetime.datetime.now()),
                      'eventStopTime': None
                    }
        string_input = self.get_event_input_as_string(input)
        return string_input

    # Data used to update CALIBRATION_DATA event types.
    def update_event_data_calibration(self, event_type, uid, event_id, last_modified, event_name):
        debug = False
        if debug: print '\n debug -- update_event_data_calibration -- event_type/uid/eventId: %s/%s/%d' % (event_type, uid, event_id)
        input = {}
        if event_type == 'CALIBRATION_DATA':
            #eventName = 'CC_a0'
            unique_num = randint(1000, 2000)
            eventStartTime = 1453309000000 + 10000
            eventStopTime = eventStartTime + (unique_num*2)
            input = {
                      "@class": ".XCalibrationData",
                      "values": [ -1.493703E-4 ],
                      "dimensions": [ 1 ],
                      "comments": "Updated test entry.",
                      "cardinality": 0,
                      "eventId": event_id,
                      "assetUid": uid,
                      "eventType": event_type,
                      "eventName": event_name,
                      "eventStartTime": eventStopTime,
                      'eventStopTime': eventStopTime,
                      'lastModifiedTimestamp': last_modified,
                      'dataSource': 'Automated test data ' + str(datetime.datetime.now()),
                      'notes': 'Update calibration at ' + str(datetime.datetime.now())
                    }

        #  Make all value in dictionary type string (simulate jgrid output).
        string_input = self.get_event_input_as_unicode(input)
        return string_input

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create event_type
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _create_event_type(self, _event_type, uid, input):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')
        event_id = None
        last_modified = None

        # Define variables specific to event type
        if debug: print '\n ***************************************** start'
        if verbose: print '\n -------------- Creating new event of type %s' % _event_type
        target_event_type = _event_type
        key = target_event_type

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET event types
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test_url = url_for('uframe.get_event_type')
        response = self.client.get(test_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('event_types' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are event_types in a list
        events_by_type = results['event_types']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, list))
        if debug: print '\n -- len(events_by_type): ', len(events_by_type)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug ********\n test CREATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = url_for('uframe.create_event')
        if debug: print '\n create url: ', url
        data = json.dumps(input)
        response = self.client.post(url, headers=headers, data=data)
        if debug:
            print '\n Create event -- response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            print '\n response_data: ', response_error

        if _event_type == 'DEPLOYMENT':
            self.assertEquals(response.status_code, 400)
            if debug: print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            if debug: print '\n response_data: ', response_error
            event_id = 0
            last_modified = 0

        else:
            if _event_type != 'CALIBRATION_DATA':
                if debug: print '\n response.status_code: ', response.status_code
                if debug: print '\n response_data: ', json.loads(response.data)
                self.assertEquals(response.status_code, 200)
                self.assertTrue(response.data is not None)
                response_data = json.loads(response.data)
                self.assertTrue('event' in response_data)
                event = response_data['event']
                self.assertTrue(event is not None)
                self.assertTrue('eventId' in event)
                event_id = event['eventId']
                self.assertTrue(event_id is not None)
                #print '\n event_id: ', event_id
                self.assertTrue('lastModifiedTimestamp' in event)
                last_modified = event['lastModifiedTimestamp']
                self.assertTrue(last_modified is not None)
                #print '\n last_modified: ', last_modified

        if debug: print '\n ***************************************** exit'
        return event_id, last_modified

    def get_event_input_as_string(self, data):
        """ Take input from UI and present all values as string type. Leaves nulls.
        Handles one dict level down. Used to simulate UI data from jgrid submit.
        """
        debug = False
        try:
            if debug: print '\n debug -- get_event_input_as_string'
            string_data = data.copy()
            keys = data.keys()
            for key in keys:
                if data[key] is not None:
                    if not isinstance(data[key], dict):
                        string_data[key] = str(data[key])
                    else:
                        if debug: print '\n Field is dict: ', key
                        tmp_dict = data[key].copy()
                        for k,v in tmp_dict.iteritems():
                            if v is not None:
                                if not isinstance(v, dict):
                                    string_data[key][k] = str(v)
            return string_data

        except Exception as err:
            if debug: print '\n exception: ', str(err)
            raise

    def get_event_input_as_unicode(self, data):
        """ Take input from UI and present all values as string type. Leaves nulls.
        Handles one dict level down. Used to simulate UI data from jgrid submit.
        """
        debug = False
        try:
            if debug: print '\n debug -- get_event_input_as_unicode'
            string_data = data.copy()
            keys = data.keys()
            for key in keys:
                if data[key] is not None:
                    if not isinstance(data[key], dict):
                        string_data[key] = unicode(data[key])
                    else:
                        if debug: print '\n Field is dict: ', key
                        tmp_dict = data[key].copy()
                        for k,v in tmp_dict.iteritems():
                            if v is not None:
                                if not isinstance(v, dict):
                                    string_data[key][k] = unicode(v)
            return string_data

        except Exception as err:
            if debug: print '\n exception: ', str(err)
            raise

    def dump_dict(self, dict, debug=False):
        """
        Print dict if debug enabled.
        """
        if debug:
            print '\n --------------\n dictionary: %s' % json.dumps(dict, indent=4, sort_keys=True)