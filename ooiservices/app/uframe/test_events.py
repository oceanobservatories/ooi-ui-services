#!/usr/bin/env python
"""
Specific testing for events routes

Routes:
[GET] /events/<int:id>                          # Get event. This should not be used by UI; if needed, then discuss!
[GET] /events/types                             # Get all supported event types
[GET] /events/uid/<string:uid>                  # Get all events of all types for asset with uid
      /events/uid/<string:uid>?type=EventType   # Get all events for asset with uid, only type(s) identified
      # Example: /uframe/events/uid/A00228?type=ATVENDOR
      # Example: /uframe/events/uid/A00228?type=ATVENDOR,INTEGRATION

[POST] /events                                  # Create an event of each eventType.
[PUT]  /events/<int:id>                         # Update events of each eventType.

"""
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from random import randint
from flask import (url_for)
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_event_types)
from ooiservices.app.uframe.event_tools import (get_rd_by_asset_id, get_uframe_event)   # get_uframe_event (future test)
from ooiservices.app.uframe.deployment_tools import (is_instrument, is_platform, is_mooring)
from ooiservices.app.uframe.events_validate_fields import get_rd_from_integrationInto
from ooiservices.app.uframe.events_create_update import get_calibration_event_id
from ooiservices.app.uframe.cruise_tools import uniqueCruiseIdentifier_exists
from unittest import skipIf
import os
import requests

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''


@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class EventsTestCase(unittest.TestCase):

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

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Test cases
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_events(self):
        """
        Exercise event routes:
        [GET]    /events/types           # Get all supported event types
        [GET]    /events/uid/<string:uid # Get events for asset with uid
        [GET]    /assets/<int:id>/events # Get all events for asset with asset id.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get some assets
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))
        if verbose: print '\n -- len(assets): ', len(assets)

        # Verify there asset objects which are dictionaries
        index = len(assets) - 10
        asset = assets[index]
        self.assertTrue(asset is not None)
        self.assertTrue(asset)
        self.assertTrue(isinstance(asset, dict))

        # Get asset_id
        self.assertTrue('id' in asset)
        asset_id = asset['id']
        self.assertTrue(asset_id is not None)
        self.assertTrue(asset_id)

        # Get asset uid
        self.assertTrue('uid' in asset)
        asset_uid = asset['uid']
        self.assertTrue(asset_uid is not None)
        self.assertTrue(asset_uid)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET event types (list)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_event_type')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('event_types' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are event_types in a list
        event_types = results['event_types']
        self.assertTrue(event_types is not None)
        self.assertTrue(isinstance(event_types, list))
        if debug: print '\n -- len(event_types): ', len(event_types)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get events by asset uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_events_by_uid', uid=asset_uid)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get events by bad asset uid #(returns empty dict if asset not found, status code 200)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_events_by_uid', uid='notgood')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(result)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get events by bad asset uid #(returns empty dict if asset not found, status code 200)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_events_by_uid', uid='')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 404)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get events for asset (by event_id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_asset_events', id=asset_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('events' in result)
        self.assertTrue(isinstance(result['events'], dict))
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, dict))
        self.assertTrue(len(events_by_type) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Process event types by type, validate fields
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- len(result): ', len(result)
        event_types = get_event_types()
        for event_type in events_by_type:
            if debug: print '\n debug -- Event_type: ', event_type
            self.assertTrue(event_type in event_types)
            self.assertTrue(event_type in events_by_type)
            self.assertTrue(isinstance(events_by_type[event_type], list))
            event_ids = []
            if events_by_type[event_type]:
                if debug: print '\n Have events of %s event type.' % event_type
                events = events_by_type[event_type]
                for event in events:
                    self.assertTrue(event is not None)
                    self.assertTrue(isinstance(event, dict))
                    self.assertTrue('eventId' in event)
                    self.assertTrue(event['eventId'])
                    if event['eventId'] not in event_ids:
                        event_ids.append(event['eventId'])

        # (Negative) Create events
        self.create_event_negative('{}')
        self.create_event_negative(None)

        self.update_event_negative('{}')
        self.update_event_negative(None)

        asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
        uid, input = self.create_event_data('STORAGE', asset_uid, rd)
        input['eventName'] = None
        self.create_event_negative(input)

        # Get event types (/uframe/events/types)
        url = url_for('uframe.get_event_type', id=asset_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        # Get supported event types (/uframe/events/types/supported)
        url = url_for('uframe.get_supported_event_type')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Negative test - use bad uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url = url_for('uframe.get_events_by_uid', uid='nogood')
        target_url = base_url + '?type=' + 'CRUISE_INFO'
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 400)
        #result = json.loads(response.data)

        # Get supported event types (/events/edit_phase_values)
        url = url_for('uframe.get_edit_phase_values')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        if verbose: print '\n'

    def test_create_event_types_random(self):
        """
        Create events of different types for three random assets with an asset type of mooring, platform and sensor.
        """
        verbose = self.verbose
        event_types = get_supported_event_types()

        # Cruises tested elsewhere.
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')

        # Calibration tested elsewhere.
        if 'CALIBRATION_DATA' in event_types:
            event_types.remove('CALIBRATION_DATA')

        if verbose: print '\n event_types: ', event_types

        #===============================================================================================
        # Get three assets, one for mooring, node and sensor; generate variety of event types for each.
        #===============================================================================================
        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        have_mooring_id = False
        have_platform_id = False
        have_instrument_id = False

        mooring_id = None
        mooring_uid = None
        mooring_rd = None

        platform_id = None
        platform_uid = None
        platform_rd = None

        instrument_id = None
        instrument_uid = None
        instrument_rd = None

        count = 0
        while not have_mooring_id or not have_platform_id or not have_instrument_id and count <= number_of_assets:

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
            if is_mooring(rd):
                if not have_mooring_id:
                    have_mooring_id = True
                    mooring_id = asset_id
                    mooring_uid = asset_uid
                    mooring_rd = rd

            elif is_platform(rd):
                if not have_platform_id:
                    have_platform_id = True
                    platform_id = asset_id
                    platform_uid = asset_uid
                    platform_rd = rd

            elif is_instrument(rd):
                if not have_instrument_id:
                    have_instrument_id = True
                    instrument_id = asset_id
                    instrument_uid = asset_uid
                    instrument_rd = rd
        if verbose:
            print '\n Note: Number of loops to get three items of interest: %d ' % count
            print '\n ----- Mooring:'
            print '\n\t mooring_id: %d' % mooring_id
            print '\n\t mooring_uid: %s' % mooring_uid
            print '\n\t mooring_rd: %s' % mooring_rd
            print '\n ----- Platform:'
            print '\n\t platform_id: %d' % platform_id
            print '\n\t platform_uid: %s' % platform_uid
            print '\n\t platform_rd: %s' % platform_rd
            print '\n ----- Instrument:'
            print '\n\t instrument_id: %d' % instrument_id
            print '\n\t instrument_uid: %s' % instrument_uid
            print '\n\t instrument_rd: %s' % instrument_rd

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add event(s) to a mooring asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #event_types = ['LOCATION']
        for event_type in event_types:
            if verbose: print '\n Creating %s event for mooring - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                mooring_id, mooring_uid, mooring_rd)

            # Create another
            uid, input = self.create_event_data(event_type, mooring_uid, mooring_rd)
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add event(s) to a platform asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #event_types = ['INTEGRATION']
        for event_type in event_types:
            if verbose: print '\n Creating %s event for platform - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                platform_id, platform_uid, platform_rd)

            # Create another
            uid, input = self.create_event_data(event_type, platform_uid, platform_rd)
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add event(s) to an instrument asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #event_types = ['INTEGRATION']
        for event_type in event_types:
            if verbose: print '\n Creating %s event for instrument - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                        instrument_id, instrument_uid, instrument_rd)

            # Create another
            uid, input = self.create_event_data(event_type, instrument_uid, instrument_rd)
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

            if verbose: print '\n'

    # Test cruise events.
    def test_cruise_events(self):
        """
        Create CRUISE_INFO event. [for three random assets with types of mooring, platform and sensor.]
        """
        debug = self.debug
        verbose = self.verbose
        event_type = 'CRUISE_INFO'
        if verbose: print '\n'
        #if verbose: print '\n event_types: ', event_types

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add cruise event to a mooring asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n ----------------------------------'
            print '\n Creating %s event ...' % event_type

        # Get unique cruise identifier
        cruise_id, input = self.get_cruise_by_cruise_id(None, None)
        self.assertTrue(cruise_id is not None)
        self.assertTrue(input is not None)

        # Create cruise event
        event_id, last_modified = self._create_event_type(event_type, None, input)
        if verbose:
            print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
            print '\n\tUnique cruise identifier: ', cruise_id
            print '\n\tNow performing an UPDATE on event we just created...'

        # Update the cruise we just created
        input = self.update_event_data_cruise(event_type, event_id, last_modified, cruise_id=cruise_id)
        update_event_id = self._update_event_type(event_type, input, event_id)
        if verbose: print '\n\tUpdated eventId: %d, cruise id: %s ' % (update_event_id, cruise_id)

        if verbose: print '\n'

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

        #=======================================

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
        if verbose:
            print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
            print '\n\tNow performing an UPDATE on event we just created...'

        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Update event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update the cruise we just created
        if verbose: print '\n\tCalibration update...'
        update_input = self.update_event_data_calibration(event_type, instrument_uid, event_id, last_modified, event_name)
        update_event_id = self._update_event_type_calibration(event_type, update_input, event_id,
                                                              instrument_uid, event_name)
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
        self.assertTrue(len(event_keys) > len(update_input_keys))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Try to create same event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n (Negative) Calibration create input: ', input
        event_id, last_modified = self._create_event_type_negative(event_type, instrument_uid, input, event_name)
        if verbose:
            print '\n\t(Negative) Create eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

        if verbose: print '\n'

    def test_create_event_types_numerous_regular(self):
        """
        Create events of different types for numerous assets, can configure for more than one asset.
        This test case is useful for populating large quantities of event (all types) on a uframe server. Careful.

        Routes:
        [GET]   /assets
        [GET]   /events/uid/<string:uid>
        [GET]   /events/uid/<string:uid>?type=EventType   # Example: /uframe/events/uid/A00228?type=ACQUISITION
        [PUT]   /events/<int:id>
        [POST]  /events
        """
        verbose = self.verbose
        event_types = get_supported_event_types()

        """
        if 'ACQUISITION' in event_types:
            event_types.remove('ACQUISITION')
        """
        # Remove event_type which are not supported at this time.
        #event_types.remove('DEPLOYMENT')
        event_types.remove('CALIBRATION_DATA')

        # Cruises tested elsewhere.
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')

        if verbose: print '\n event_types: ', event_types

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        count = 0
        maximum_count = 1
        while count <= number_of_assets and count < maximum_count:

            # Select an asset...Get asset_id, asset_uid, rd.
            #assets = assets.sort(reverse=True)
            asset = assets[count+20]
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            asset_type = ''
            if is_mooring(rd):
                asset_type = 'mooring'
            elif is_platform(rd):
                asset_type = 'platform'
            elif is_instrument(rd):
                asset_type = 'instrument'

            if verbose: print '\n***********************************************************************'
            message = '\n (%d) Processing %s asset...' % ((count + 1), asset_type)
            if verbose: print '\n %s' % message
            count +=1

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Add event(s) to asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Note: To test single event type, set event_types list here: event_types = ['UNSPECIFIED']
            #event_types = ['INTEGRATION']  # ['ACQUISITION'] #
            #event_types = ['CALIBRATION_DATA', 'DEPLOYMENT']
            #event_types = ['ATVENDOR']
            for event_type in event_types:
                if verbose: print '\n ----- Creating %s event - asset id/uid/rd: %d/%s/%s' % (event_type, asset_id, asset_uid, rd)

                # Create an event
                uid, input = self.create_event_data(event_type, asset_uid, rd)
                if event_type == 'DEPLOYMENT' or event_type == 'CALIBRATION_DATA':
                    input['eventType'] = event_type
                    input['assetUid'] = uid
                event_id, last_modified = self._create_event_type(event_type, uid, input)
                if verbose:
                    print '\n Created eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

                if event_type == 'CRUISE_INFO':
                    continue

                if event_type != 'DEPLOYMENT' and event_type != 'CALIBRATION_DATA':
                    if verbose: print '\n Now performing an UPDATE on event we just created...'
                    # Update the one we just created
                    uid, input = self.update_event_data(event_type, asset_uid, rd, event_id, last_modified)
                    update_event_id = self._update_event_type(event_type, input, event_id)
                    if verbose: print '\n Updated eventId: %d ' % update_event_id
                    self.assertTrue(event_id, update_event_id)

        if verbose: print '\n Note: Number of assets processed: %d ' % count
        if verbose: print '\n'

    # todo - bad fix this!!
    def test_create_event_types_numerous_requests(self):
        """
        *********************************************************************************************************
        **** Fails if login and asset_manage scope required. Requires localhost:400 services to be running. *****
        *********************************************************************************************************

        Create events of different types for numerous assets, configure for more than two assets.
        This test case is useful for populating large quantities of event (all types) on a uframe server. Careful.

        Following event types not supported and why:
        'DEPLOYMENT'           # (general)
        'CALIBRATION_DATA'     # create and update api not available
        'RECOVERY'             # OBE?

        Routes:
        [GET]   /assets
        [GET]   /events/uid/<string:uid>
        [GET]   /events/uid/<string:uid>?type=EventType   # Example: /uframe/events/uid/A00228?type=ACQUISITION
        [PUT]   /events/<int:id>
        [POST]  /events
        """
        verbose = self.verbose
        event_types = get_event_types()

        # Remove event_type which are not supported at this time.
        event_types.remove('DEPLOYMENT')
        event_types.remove('CALIBRATION_DATA')

        # Cruises tested elsewhere.
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')

        if verbose: print '\n event_types: ', event_types

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        count = 0
        maximum_count = 1
         #number_of_assets
        while count <= number_of_assets and count < maximum_count:

            # Select an asset...
            asset = assets[count+20]
            #asset = assets[count]

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            asset_type = ''
            if is_mooring(rd):
                asset_type = 'mooring'
            elif is_platform(rd):
                asset_type = 'platform'
            elif is_instrument(rd):
                asset_type = 'instrument'

            if verbose: print '\n***********************************************************************'
            message = '\n (%d) Processing %s asset...' % ((count + 1), asset_type)
            if verbose: print '\n %s' % message
            count +=1

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Add event(s) to asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Note: To test single event type, set event_types list here:
            #event_types = ['INTEGRATION']
            for event_type in event_types:
                if verbose:
                    print '\n Creating %s event - asset id/uid/rd: %d/%s/%s' % (event_type, asset_id, asset_uid, rd)

                # Create another
                uid, input = self.create_event_data(event_type, asset_uid, rd)
                event_id, last_modified = self._create_event_type_requests(event_type, uid, input)
                if verbose: print '\n (requests) Created eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

                if event_type == 'CRUISE_INFO':
                    continue

                if verbose:
                    print '\n Now performing an UPDATE on event we just created...'
                # Update the one we just created
                uid, input = self.update_event_data(event_type, asset_uid, rd, event_id, last_modified)
                update_event_id = self._update_event_type_requests(event_type, input, event_id)
                if verbose: print '\n (requests) Updated eventId: %d ' % update_event_id
                self.assertTrue(event_id, update_event_id)

        if verbose: print '\n Note: Number of assets processed: %d ' % count
        if verbose: print '\n'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create_event_negative(self, input):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        debug = False
        headers = self.get_api_headers('admin', 'test')
        url = url_for('uframe.create_event')
        if debug: print '\n create url: ', url
        data = json.dumps(input)
        response = self.client.post(url, headers=headers, data=data)
        self.assertEquals(response.status_code, 400)
        if debug: print '\n response.status_code: ', response.status_code
        response_error = json.loads(response.data)
        if debug: print '\n response_data: ', response_error

        response = self.client.post(url, headers=headers, data=None)
        self.assertEquals(response.status_code, 400)
        if debug: print '\n response.status_code: ', response.status_code
        response_error = json.loads(response.data)
        if debug: print '\n response_data: ', response_error

        response = self.client.post(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        if debug: print '\n response.status_code: ', response.status_code
        response_error = json.loads(response.data)
        if debug: print '\n response_data: ', response_error

    def update_event_negative(self, input):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        debug = False
        headers = self.get_api_headers('admin', 'test')
        url = url_for('uframe.update_event', id=20052)
        if debug: print '\n create url: ', url
        data = json.dumps(input)
        response = self.client.put(url, headers=headers, data=data)
        self.assertEquals(response.status_code, 400)
        if debug: print '\n response.status_code: ', response.status_code
        response_error = json.loads(response.data)
        if debug: print '\n response_data: ', response_error

        response = self.client.put(url, headers=headers, data=None)
        self.assertEquals(response.status_code, 400)
        if debug: print '\n response.status_code: ', response.status_code
        response_error = json.loads(response.data)
        if debug: print '\n response_data: ', response_error

        response = self.client.put(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        if debug: print '\n response.status_code: ', response.status_code
        response_error = json.loads(response.data)
        if debug: print '\n response_data: ', response_error

    def get_cruise_by_cruise_id(self, uid, rd):

        """ http://uframe-test.ooi.rutgers.edu:12587/events/cruise/inv/EE-2016-0191
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        if verbose: print '\n test -- Entered get_cruise_by_cruise_id...'

        # Make create initial cruise data.
        event_type = 'CRUISE_INFO'
        uid, input = self.create_event_data(event_type, None, None) # for cruise set uid and rd equal to None.

        # Get value for uniqueCruiseIdentifer
        cruise_id = input['uniqueCruiseIdentifier']

        # Verify uniqueCruiseIdentifer does not already exist in cruises.
        url = url_for('uframe.get_cruise_by_cruise_id', cruise_id=cruise_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        if debug: print '\n test -- response.status_code: ', response.status_code
        if response.status_code != 409:
            if debug: print '\n ************** Loop to create unique id...'
            max_count = 10
            count = 0
            while count < max_count:
                count += 1
                cruise_id = None
                if debug: print '\n test -- (%d) Get unique cruise id. '% count
                # Get a unique cruise identifier
                # Make some unique key in form: 'EE-2016-0102'
                unique_num = randint(105, 990)
                uniqueCruiseIdentifer = 'XX-2016-0' + str(unique_num)

                if not uniqueCruiseIdentifier_exists(uniqueCruiseIdentifer):
                    if debug: print '\n Have unique cruise identifier: ', uniqueCruiseIdentifer
                    cruise_id = uniqueCruiseIdentifer
                    break
                else:
                    if debug: print '\n Do not have unique cruise identifier: ', uniqueCruiseIdentifer

                """
                if debug: print '\n test -- Try uniqueCruiseIdentifier: ', uniqueCruiseIdentifer
                # Verify uniqueCruiseIdentifer does not exist in cruises
                url = url_for('uframe.get_cruise_by_cruise_id', cruise_id=uniqueCruiseIdentifer)
                if debug: print '\n ----- url: ', url
                response = self.client.get(url, headers=headers)
                if debug: print '\n test -- response.status_code: ', response.status_code
                if response.status_code == 409:
                    cruise_id = uniqueCruiseIdentifer
                    break
                """

        self.assertTrue(cruise_id is not None)
        if verbose: print '\n Unique cruise id: ', cruise_id
        input['uniqueCruiseIdentifier'] = cruise_id

        return cruise_id, input

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

    def get_events_for_an_event_type(self, event_type, uid):
        verbose = False
        headers = self.get_api_headers('admin', 'test')
        base_url = url_for('uframe.get_events_by_uid', uid=uid)
        target_url = base_url + '?type=' + event_type
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if verbose: print '\n -- fetched asset uid %s %s events: %s' % (uid, event_type, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)
        self.assertTrue(result['events'] is not None)
        some_events = result['events'][event_type]
        if verbose: print '\n Number of %s events returned: %d' % (event_type, len(some_events))

        return some_events

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

    # todo -- under test
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
            print '\n get_calibration_event_id_last_modified, uid: ', uid
            print '\n get_calibration_event_id_last_modified, event_name: ', event_name
        error_text = ' uid: ' + uid + ', event name: ' + event_name
        try:

            # Get asset by uid, retrieve eventId and name from calibration event.
            event_id = None
            last_modified = None
            try:
                event_id, last_modified = get_calibration_event_id(uid, event_name)
            except Exception as err:
                self.assetEquals('Failed to get event id for calibration', event_name + ' ' + str(err))

            if debug: print '\n Calibration event_id: %s, uid: %s, last_modified: %d' % (event_id, uid, last_modified)
            self.assertTrue(event_id is not None)
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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create event_type using requests
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _create_event_type_requests(self, _event_type, uid, input):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Define variables specific to event type
        if verbose: print '\n Creating new event of type %s' % _event_type
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

        """
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get asset with uid 'A00391.1'; get asset_id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_asset_by_uid', uid=uid), headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset (%s): %s' % (uid, result)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get events for asset with uid 'A00391.1'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url = url_for('uframe.get_events_by_uid', uid=uid)
        if verbose: print '\n Base url: ', base_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid events(%s): %s' % (uid, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)

        # Get events by type dictionary, key is event_type
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(len(events_by_type) > 0)

        # Create list of event_types returned for this asset
        event_types = events_by_type.keys()
        event_types.sort()
        self.assertTrue(len(event_types) > 0)
        if debug: print '\n Have event_types: ', event_types

        # Get all uframe supported event types
        all_event_types = get_event_types()
        self.assertTrue(isinstance(all_event_types, list))
        self.assertTrue(len(all_event_types) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Determine number of events of target event type currently available
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        target_events = []
        target_event_ids = []
        if target_event_type in event_types:
            target_events = events_by_type[target_event_type]
            if target_events:
                for event in target_events:
                    if 'event_id' in event:
                        if event['event_id']:
                            if event['event_id'] not in target_event_ids:
                                target_event_ids.append(event['event_id'])

        if debug: print '\n Number of %s events: %d' % (target_event_type, len(target_events))
        number_of_target_events = len(target_events)

        # Verify number of events by query (using type=target_event_type)
        target_url = base_url + '?type=' + key
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid %s %s events: %s' % (uid, key, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)
        self.assertTrue(result['events'] is not None)
        events = result['events']
        #if debug: print '\n debug-- result[events]: ', events
        self.assertTrue(events is not None)

        some_events = result['events'][key]
        if debug: print '\n Number of %s events returned: %d' % (key, len(some_events))
        self.assertEquals(len(some_events), number_of_target_events)
        """

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug ********\n test create (line 668) CREATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))
        url = self.root
        url += url_for('uframe.create_event')
        if debug: print '\n debug -- Requests Create url: ', url
        data = json.dumps(input)
        timeout = 5
        timeout_read = 30
        response_data = None
        #response = requests.post(url, timeout=(timeout, timeout_read), headers=self.request_headers(), data=data)
        response = requests.post(url, timeout=(timeout, timeout_read),  data=data)
        if debug: print '\n debug -- Test: Create response.status_code: ', response.status_code

        if _event_type == 'DEPLOYMENT' or _event_type == 'CALIBRATION_DATA':
            self.assertEquals(response.status_code, 400)
            if debug: print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            if debug: print '\n response_data: ', response_error
            event_id = 0
            last_modified = 0

        else:
            if response.status_code != 200:
                if debug: print '\n Failed to execute to localhost:4000 create event, status_code: ', response.status_code
                if response.content:
                    response_data = json.loads(response.content)
                    if debug: print '\n Failed Event create data from POST: %s' % response_data
                event_id = 0
                last_modified = 0
            else:
                if response.content:
                    response_data = json.loads(response.content)
                    if debug: print '\n Test: Successful Event create data from POST (json.loads(response.content)): %s' % response_data

                #print '\n response_data: ', response_data
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

            """
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Verify number of events has increased by one
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            target_url = base_url + '?type=' + key
            if verbose: print '\n target_url: ', target_url
            response = self.client.get(base_url, headers=headers)
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)
            #if debug: print '\n -- fetched asset uid %s %s events: %s' % (uid, key, result)
            self.assertTrue(result is not None)
            self.assertTrue('events' in result)
            self.assertTrue(result['events'] is not None)
            some_events = result['events'][key]
            if debug: print '\n Number of %s events returned: %d' % (key, len(some_events))
            self.assertEquals(len(some_events), number_of_target_events + 1)
            """
        return event_id, last_modified


    def request_headers(self):
        """ Headers for uframe PUT and POST. """
        return {"Content-Type": "application/json"}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Update event_type - regular
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _update_event_type(self, _event_type, input, event_id):
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

        if debug:
            print '\n debug ********\n test update (line 756) UPDATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = url_for('uframe.update_event', id=event_id)
        if verbose: print '\n **** Update url: ', url
        data = json.dumps(input)
        response = self.client.put(url, headers=headers, data=data)
        if response.status_code != 200:
            if debug: print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            if debug: print '\n response_error: ', response_error

        if _event_type == 'DEPLOYMENT' or _event_type == 'CALIBRATION_DATA':
            self.assertEquals(response.status_code, 400)
            if debug: print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            if debug: print '\n response_data: ', response_error
            event_id = 0

        else:
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
        return event_id

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

        if debug:
            print '\n debug ********\n test update (line 756) UPDATE request_data(%d): %r' % (len(input),
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
        return event_id


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Update event_type - using requests
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _update_event_type_requests(self, _event_type, input, event_id):
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

        if debug:
            print '\n debug ********\n test update (line 756) UPDATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = self.root
        url += url_for('uframe.update_event', id=event_id)
        if debug: print '\n debug -- Requests Update url: ', url

        data = json.dumps(input)
        timeout = 5
        timeout_read = 30
        response_data = None
        response = requests.put(url, timeout=(timeout, timeout_read), headers=self.request_headers(), data=data)
        if debug: print '\n debug -- Test: Update response.status_code: ', response.status_code
        if response.status_code != 200:
            if debug: print '\n Failed to execute to localhost:4000 update event, status_code: ', response.status_code
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Failed Event update data from POST: %s' % response_data
        else:
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Successful Event update data from POST: %s' % response_data

        self.assertTrue('event' in response_data)
        event = response_data['event']
        if debug: print '\n debug -- event: ', event
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)
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
                    }
        string_input = self.get_event_input_as_string(input)
        return string_input

    # Data used to update different event types.
    def update_event_data(self, event_type, uid, rd, event_id, last_modified, cruise_id=None):
        debug = False
        if debug: print '\n debug -- update_event_data -- event_type: ', event_type
        input = {}
        notes = 'Update new %s event for %s, associated with asset: %s)' % (event_type, rd, uid)
        unique_num = randint(1, 1000)
        unique_float = randint(1, 1000) * 100.0
        if event_type == 'ACQUISITION':
            input = {
                      'purchasePrice': unique_float,
                      'purchaseDate': 1398040000000,
                      'deliveryDate': 1398050000000,
                      'purchasedBy': str(unique_num),
                      'vendorIdentification': None,
                      'vendorPointOfContact': None,
                      'receivedFromVendorBy': None,
                      'authorizationNumber': None,
                      'authorizationForPayment': None,
                      'invoiceNumber': str(unique_num),
                      'eventType': 'ACQUISITION',
                      'eventName': rd,
                      'eventStartTime': 1398060000000,
                      'eventStopTime':  1398070000000,
                      'notes': str(unique_float),
                      'tense': 'UNKNOWN',
                      'dataSource': None,
                      'assetUid': uid,
                      'eventId': event_id,
                      'lastModifiedTimestamp': last_modified
                      }

        elif event_type == 'ASSET_STATUS':
            input = {
                    'severity': 4,
                    'reason': 'At operational capability; check battery power again in 5 days.',
                    'location': 'Onsite',
                    'status': 'Operational',
                    'eventType': 'ASSET_STATUS',
                    'eventStartTime': 1398039160000,
                    'eventStopTime': 1405382410000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_float),
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'ATVENDOR':
            unique_num = randint(100, 300)
            notes = 'Issues with some components used to refurbish the hardware. '
            notes += 'Issues configuring calibration to OEM specs. Please review.'
            input = {
                    'reason': 'Dial not working properly do to power issues.',
                    'authorizationNumber': '10147' + str(unique_num),
                    'vendorIdentification': 'vendor A',
                    'authorizationForPayment': None,
                    'invoiceNumber': '2016-45870',
                    'vendorPointOfContact': 'Vendor Technician',
                    'sentToVendorBy': 'Engineer',
                    'receivedFromVendorBy': 'Marine technician' + str(unique_num),
                    'eventType': 'ATVENDOR',
                    'eventStartTime': 1398039160000 + unique_num,
                    'eventStopTime': 1405382430000+ (2* unique_num),
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_float),
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'CRUISE_INFO':
            eventName = 'Updated %s event name.' % cruise_id
            unique_num = randint(301, 400)
            #cruiseIdentifier = 'Updated %s cruise identifier.' % cruise_id
            eventStartTime = 1453309000000 + 10000 + unique_num
            eventStopTime = eventStartTime + 10000 + (unique_num*2)
            notes = None
            # edit_phase is one of ['EDIT', 'STAGED', 'OPERATIONAL']
            #'cruiseIdentifier': cruiseIdentifier,
            input = {
                    'uniqueCruiseIdentifier': cruise_id,
                    'shipName': 'Scarlett OHara',
                    'eventType': 'CRUISE_INFO',
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'eventName': eventName,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_float+100.0),
                    'assetUid': None,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified,
                    'editPhase': 'OPERATIONAL'
                    }

        elif event_type == 'INTEGRATION':
            unique_num = randint(401, 500)
            notes = None
            eventStopTime = 1453309000000 + (unique_num * 2)
            integrationInto = {
                                'node': None,
                                'subsite': 'CP01CNSM',
                                'sensor': None
                              }
            integration_rd = get_rd_from_integrationInto(integrationInto)
            if debug: print '\n debug -- rd: ', rd
            input = {
                    'integrationInto': integration_rd,
                    'deploymentNumber': 1,
                    'versionNumber': 2,
                    'integratedBy': 'Engineer 5, RPS ASA' + str(unique_num),
                    'eventType': 'INTEGRATION',
                    'eventName':  rd,
                    'eventStartTime': 1471218130232,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_float+50.0),
                    'assetUid': uid,
                    'eventId': event_id,
                      'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'LOCATION':
            eventStartTime = 1398039360000 + unique_num
            eventStopTime = 1453309000000 + (unique_num * 10)

            input = {
                    'depth': 551.27,
                    'longitude': -70.8125,
                    'latitude': 40.467731,
                    'orbitRadius': 0.0,
                    'eventType': 'LOCATION',
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'RETIREMENT':
            eventStartTime = 1398039370000 + unique_num
            eventStopTime = 1453309000000 + (unique_num * 10)
            input = {
                    'reason': 'Equipment beyond repair.',
                    'disposition': 'Disposed',
                    'retiredBy': 'Engineer at RPS ASA',
                    'eventType': 'RETIREMENT',
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'STORAGE':
            eventStartTime = 1398039360000 + unique_num
            eventStopTime = 1453309000000 + (unique_num * 10)
            input = {
                    'buildingName': 'Marine Storage',
                    'eventName': rd,
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'eventType': 'STORAGE',
                    'notes': notes,
                    'performedBy': 'Engineer, RPS ASA',
                    'physicalLocation': 'URI, Narragansett, RI',
                    'roomIdentification': '55-104',
                    'shelfIdentification': '4139-03',
                    'dataSource': None,
                    'tense': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'UNSPECIFIED':
            eventStartTime = 1398039360000 + unique_num
            eventStopTime = 1453309000000 + (unique_num * 10)
            input = {
                    'dataSource': None,
                    'eventName': rd,
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'eventType': 'UNSPECIFIED',
                    'notes': notes,
                    'tense': 'UNKNOWN',
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        string_input = self.get_event_input_as_unicode(input)
        return uid, string_input

    # Data used to update CRUISE_INFO event types.
    def update_event_data_cruise(self, event_type, event_id, last_modified, cruise_id=None):
        debug = False
        if debug: print '\n debug -- update_event_data -- event_type: ', event_type
        input = {}
        notes = 'Update new %s event.' % event_type

        if event_type == 'CRUISE_INFO':
            eventName = 'Updated %s event name.' % cruise_id
            #cruiseIdentifier = 'Updated %s cruise identifier.' % cruise_id
            eventStartTime = 1453309000000 + 10000
            eventStopTime = eventStartTime + 10000
            notes = None
            # edit_phase is one of ['EDIT', 'STAGED', 'OPERATIONAL']
            #'cruiseIdentifier': cruiseIdentifier,
            input = {
                    'uniqueCruiseIdentifier': cruise_id,
                    'shipName': 'Scarlett OHara',
                    'eventType': 'CRUISE_INFO',
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'eventName': eventName,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': None,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified,
                    'editPhase': 'OPERATIONAL'
                    }

        string_input = self.get_event_input_as_unicode(input)
        return string_input

    # Data used to update CALIBRATION_DATA event types.
    def update_event_data_calibration(self, event_type, uid, event_id, last_modified, event_name):
        debug = False
        if debug: print '\n debug -- update_event_data_calibration -- event_type/uid/eventId: %s/%s/%d' % (event_type, uid, event_id)
        input = {}
        if event_type == 'CALIBRATION_DATA':
            #eventName = 'CC_a0'
            eventStartTime = 1453309000000 + 10000
            input = {
                      "@class" : ".XCalibrationData",
                      "values" : [ -1.493703E-4 ],
                      "dimensions" : [ 1 ],
                      "comments" : "Updated test entry.",
                      "cardinality" : 0,
                      "eventId": event_id,
                      "assetUid" : uid,
                      "eventType" : event_type,
                      "eventName" : event_name,
                      "eventStartTime" : eventStartTime,
                      'lastModifiedTimestamp': last_modified
                    }

        #  Make all value in dictionary type string (simulate jgrid output).
        string_input = self.get_event_input_as_unicode(input)
        return string_input

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