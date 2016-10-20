#!/usr/bin/env python
"""
Asset Management - Specific testing for calibration event routes and supporting functions.

"""
__author__ = 'Edna Donoughe'

import unittest
from ooiservices.tests.common_tools import (dump_dict, get_event_input_as_unicode, get_event_input_as_string)
from base64 import b64encode
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from unittest import skipIf
import os

from flask import (url_for)
from ooiservices.app.uframe.event_tools import get_rd_by_asset_id
from ooiservices.app.uframe.uframe_tools import get_uframe_event
from ooiservices.app.uframe.common_tools import is_instrument
from ooiservices.app.uframe.events_create_update import get_calibration_event_id
from random import randint
import datetime
import json


@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class CalibrationEventsTestCase(unittest.TestCase):

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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test cases
    #   test_calibration_events
    #   test_negative_create_duplicate_calibration_events
    #   test_negative_calibration_events
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test calibration events.
    def test_calibration_events(self):
        """
        Create CALIBRATION_DATA event. Only applied for instrument ('Sensor') assets.
        http://uframe-3-test.ooi.rutgers.edu:12587/asset/cal?uid=A00679, or,
        http://uframe-3-test.ooi.rutgers.edu:12587/asset?uid=A00679

        New calibration data format:
          {
              "@class" : ".XInstrument",
              "calibration" : [ {
                "@class" : ".XCalibration",
                "name" : "CC_scale_factor_volume_scatter",
                "calData" : [ {
                  "@class" : ".XCalibrationData",
                  "value" : 1.883E-6,
                  "comments" : null,
                  "eventId" : 15238,
                  "assetUid" : "A00992",
                  "eventType" : "CALIBRATION_DATA",
                  "eventName" : "CC_scale_factor_volume_scatter",
                  "eventStartTime" : 1394755200000,
                  "eventStopTime" : null,
                  "notes" : null,
                  "tense" : "UNKNOWN",
                  "dataSource" : "FLORT_Cal_Info.xlsx",
                  "lastModifiedTimestamp" : 1473180383529
                } ]
              },
          }

        Three different (basic) calibration data types:
            1. scalar,
            2. one dimensional array, and
            3. two dimensional array

        Descriptions:
        1. Scalar value
          "value" : 10.0,

        2. One dimensional array of n values
          "value" : [ 10.0, 11.0, 12.0 ... 20.0 ],   // eleven values in array

        3. Two dimensional array of m times n values
          "value" : [[10.0, 11.0, 12.0], [20.0, 21.0, 22.0], [30.0, 31.0, 32.0]],   // 3 x 3 array

        http://host:12587/asset/cal/A00679

        Sample verbose output:

            Creating CALIBRATION_DATA event ...

             Have some assets (4917)

             Note: Number of loops to get instrument asset: 4

             ----- Instrument:

                 instrument_id: 3723

                 instrument_uid: N00104

                 instrument_rd: CP02PMUO-WFP01-01-VEL3DK000

            Processing calibration data type of scalar.

                Calibration create...

                Creating new event of type CALIBRATION_DATA

                Created eventId: 34445 and lastModifiedTimestamp: 1473974539601

                Now performing an UPDATE on event we just created...

                Calibration update...

                Updated eventId: 34445

                Update CALIBRATION_DATA event, event id: 34445

                Updated eventId: 34445

                Calibration update - check results...

            Processing calibration data type of one_dimensional.

                Calibration create...

                Creating new event of type CALIBRATION_DATA

                Created eventId: 34447 and lastModifiedTimestamp: 1473974540513

                Now performing an UPDATE on event we just created...

                Calibration update...

                Updated eventId: 34447

                Update CALIBRATION_DATA event, event id: 34447

                Updated eventId: 34447

                Calibration update - check results...

            Processing calibration data type of two_dimensional.

                Calibration create...

                Creating new event of type CALIBRATION_DATA

                Created eventId: 34449 and lastModifiedTimestamp: 1473974541435

                Now performing an UPDATE on event we just created...

                Calibration update...

                Updated eventId: 34449

                Update CALIBRATION_DATA event, event id: 34449

                Updated eventId: 34449

                Calibration update - check results...
        """
        debug = self.debug
        verbose = self.verbose
        event_type = 'CALIBRATION_DATA'
        if verbose: print '\n'
        #if verbose: print '\n event_types: ', event_types

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add calibration event to an instrument asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n ----------------------------------'
            print '\n Creating %s event ...' % event_type

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))
        data_types = ['scalar', 'one_dimensional', 'two_dimensional']

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
            #if debug: print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))

            # do not touch asset id 1.
            if asset['id'] == 1:
                continue

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

        for data_type in data_types:

            if verbose: print '\nProcessing calibration data type of %s.' % data_type
            # Get data to create calibration event.
            #data_type = 'scalar'
            input = self.calibration_data_for_create(event_type, instrument_uid, instrument_rd, data_type)
            event_name = input['eventName']
            if verbose: print '\n\tCalibration create...'

            # Create calibration event.
            event_id, last_modified = self.create_calibration_event(event_type, instrument_uid, input, event_name)
            if debug:
                print '\n\tCalibration create input: '
                dump_dict(input, debug)
            self.assertTrue(input is not None)
            self.assertTrue('assetUid' in input)
            self.assertTrue(input['assetUid'] is not None)
            if verbose:
                print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
                print '\n\tNow performing an UPDATE on event we just created...'

            # Update calibration event.
            if verbose: print '\n\tCalibration update...'
            update_input = self.calibration_data_for_update(event_type, instrument_uid, event_id, last_modified, event_name)
            self.assertTrue(update_input is not None)
            self.assertTrue('eventId' in update_input)
            self.assertEquals(int(update_input['eventId']), event_id)
            self.assertTrue('assetUid' in update_input)
            self.assertEquals(update_input['assetUid'], instrument_uid)
            if not isinstance(update_input['eventId'], int):
                update_input['eventId'] = int(str(update_input['eventId']))
                self.assertTrue(isinstance(update_input['eventId'], int))
            if verbose: print '\n\tUpdated eventId: %d' % update_input['eventId']

            # Save copy of 'update' data before issuing update request.
            update_data = update_input.copy()
            if debug:
                print '\n ----- calibration event update data: '
                dump_dict(update_data, debug)

            # Update calibration event, returns event id.
            update_event_id = self.update_calibration_event(event_type, update_input, event_id, instrument_uid, event_name)
            self.assertTrue(update_event_id is not None)
            self.assertTrue(isinstance(update_event_id, int))
            if verbose: print '\n\tUpdated eventId: %d' % update_event_id

            # Check eventId against the eventId returned on update.
            if verbose: print '\n\tCalibration update - check results...'
            if debug:
                print '\n instrument_uid: ', instrument_uid
                print '\n event_name: ', event_name
            event_id, last_modified = self.get_calibration_event_id_last_modified(instrument_uid, event_name)
            self.assertTrue(event_id is not None)
            self.assertTrue(last_modified is not None)
            self.assertEquals(update_event_id, event_id)

            # Get calibration event by event id
            event = get_uframe_event(event_id)
            if debug: print '\n\tUpdated calibration data event(id: %d): %s' % (event_id, event)
            self.assertTrue(event is not None)
            if verbose:
                print '\n Updated uframe calibration data event (2d): '
                dump_dict(event, verbose)

            # Check calibration content changes are reflected in 'updated' calibration event.
            update_data_keys = update_data.keys()
            event_keys = event.keys()
            self.assertEquals(len(event_keys), len(update_data_keys))
            for key in event_keys:
                self.assertTrue(key in update_data_keys)
            for key in update_data_keys:
                if key != '@class':
                    self.assertTrue(key in event_keys)


        if verbose: print '\n'

    def test_calibration_events_two_dimensional(self):
        """
        Create CALIBRATION_DATA event. Only applied for instrument ('Sensor') assets.
        http://uframe-3-test.ooi.rutgers.edu:12587/asset/cal?uid=A00679, or,
        http://uframe-3-test.ooi.rutgers.edu:12587/asset?uid=A00679

        New calibration data format:
          {
              "@class" : ".XInstrument",
              "calibration" : [ {
                "@class" : ".XCalibration",
                "name" : "CC_scale_factor_volume_scatter",
                "calData" : [ {
                  "@class" : ".XCalibrationData",
                  "value" : 1.883E-6,
                  "comments" : null,
                  "eventId" : 15238,
                  "assetUid" : "A00992",
                  "eventType" : "CALIBRATION_DATA",
                  "eventName" : "CC_scale_factor_volume_scatter",
                  "eventStartTime" : 1394755200000,
                  "eventStopTime" : null,
                  "notes" : null,
                  "tense" : "UNKNOWN",
                  "dataSource" : "FLORT_Cal_Info.xlsx",
                  "lastModifiedTimestamp" : 1473180383529
                } ]
              },
          }

        Test two dimensional array calibration data types:

        Descriptions:

        Two dimensional array of m times n values (2 x 5, two per row, 5 rows)
          "value" : [[10.0, 11.0], [20.0, 21.0], [30.0, 31.0], [40.0, 41.0], [50.0, 51.0]],   // 2 x 5 array

        http://host:12587/asset/cal/A00679

        Sample verbose output:

            Creating CALIBRATION_DATA event ...

             Have some assets (4917)

             Note: Number of loops to get instrument asset: 4

             ----- Instrument:

                 instrument_id: 3723

                 instrument_uid: N00104

                 instrument_rd: CP02PMUO-WFP01-01-VEL3DK000

            Processing calibration data type of two_dimensional.

                Calibration create...

                Creating new event of type CALIBRATION_DATA

                Created eventId: 34449 and lastModifiedTimestamp: 1473974541435

                Now performing an UPDATE on event we just created...

                Calibration update...

                Updated eventId: 34449

                Update CALIBRATION_DATA event, event id: 34449

                Updated eventId: 34449

                Calibration update - check results...
        """
        debug = self.debug
        verbose = self.verbose
        event_type = 'CALIBRATION_DATA'
        if verbose: print '\n'
        #if verbose: print '\n event_types: ', event_types

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add calibration event to an instrument asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n ----------------------------------'
            print '\n Creating %s event ...' % event_type

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))
        data_types = ['two_dimensional']

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        have_instrument_id = False
        instrument_id = None
        instrument_uid = None
        instrument_rd = None
        two_dimensional_test_values = [[10.0, 11.0], [20.0, 21.0], [30.0, 31.0], [40.0, 41.0], [50.0, 51.0]]

        count = 0
        while not have_instrument_id and count <= number_of_assets:

            count +=1
            asset_index = randint(0, (number_of_assets-1))
            #if debug: print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))

            # do not touch asset id 1.
            if asset['id'] == 1:
                continue

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

        for data_type in data_types:

            if verbose: print '\nProcessing calibration data type of %s.' % data_type
            # Get data to create calibration event.
            input = self.calibration_data_for_create_two_dimensional(event_type, instrument_uid, instrument_rd)

            event_name = input['eventName']
            if verbose: print '\n\tCalibration create...'

            # Create calibration event.
            event_id, last_modified = self.create_calibration_event(event_type, instrument_uid, input, event_name)
            if verbose:
                print '\n\tCalibration create input: '
                dump_dict(input, verbose)
            self.assertTrue(input is not None)
            self.assertTrue('assetUid' in input)
            self.assertTrue(input['assetUid'] is not None)
            if verbose:
                print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

            # Get calibration event just created.
            # Get calibration event by event id
            uframe_event = get_uframe_event(event_id)
            if debug: print '\n\tUpdated calibration data event(id: %d):' % event_id
            self.assertTrue(uframe_event is not None)
            if verbose:
                print '\n Updated uframe calibration data event (2d): '
                dump_dict(uframe_event, verbose)

            """
            #- - - - - - - - - - - - - - - - - - - - - - - - - - -
            # todo - Add 2d special update function for this test.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - -

            if verbose:
                print '\n\tNow performing an UPDATE on event we just created...'

            # Update calibration event.
            if verbose: print '\n\tCalibration update...'
            update_input = self.calibration_data_for_update(event_type, instrument_uid, event_id, last_modified, event_name)
            self.assertTrue(update_input is not None)
            self.assertTrue('eventId' in update_input)
            self.assertEquals(int(update_input['eventId']), event_id)
            self.assertTrue('assetUid' in update_input)
            self.assertEquals(update_input['assetUid'], instrument_uid)
            if not isinstance(update_input['eventId'], int):
                update_input['eventId'] = int(str(update_input['eventId']))
                self.assertTrue(isinstance(update_input['eventId'], int))
            if verbose: print '\n\tUpdated eventId: %d' % update_input['eventId']

            # Save copy of 'update' data before issuing update request.
            update_data = update_input.copy()
            if debug:
                print '\n ----- calibration event update data: '
                dump_dict(update_data, debug)

            # Update calibration event, returns event id.
            update_event_id = self.update_calibration_event(event_type, update_input, event_id, instrument_uid, event_name)
            self.assertTrue(update_event_id is not None)
            self.assertTrue(isinstance(update_event_id, int))
            if verbose: print '\n\tUpdated eventId: %d' % update_event_id

            # Check eventId against the eventId returned on update.
            if verbose: print '\n\tCalibration update - check results...'
            if debug:
                print '\n instrument_uid: ', instrument_uid
                print '\n event_name: ', event_name
            event_id, last_modified = self.get_calibration_event_id_last_modified(instrument_uid, event_name)
            self.assertTrue(event_id is not None)
            self.assertTrue(last_modified is not None)
            self.assertEquals(update_event_id, event_id)

            # Get calibration event by event id
            event = get_uframe_event(event_id)
            if debug: print '\n\tUpdated calibration data event(id: %d): %s' % (event_id, event)
            self.assertTrue(event is not None)
            if debug:
                print '\n Update uframe event: '
                dump_dict(event, debug)

            # Check calibration content changes are reflected in 'updated' calibration event.
            update_data_keys = update_data.keys()
            event_keys = event.keys()
            self.assertEquals(len(event_keys), len(update_data_keys))
            for key in event_keys:
                self.assertTrue(key in update_data_keys)
            for key in update_data_keys:
                if key != '@class':
                    self.assertTrue(key in event_keys)
            """

        if verbose: print '\n'


    def test_negative_create_duplicate_calibration_events(self):
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

        Three different (basic) calibration data types:
            1. scalar,
            2. one dimensional array, and
            3. two dimensional array

        Descriptions:
        1. Scalar value
          "values" : [ 10.0 ],
          "dimensions" : [ 1 ],
          "cardinality" : 0,

        2. One dimensional array of n values
          "values" : [ 10.0, 11.0, 12.0 ... 20.0 ],   // eleven values in array
          "dimensions" : [ 11 ],
          "cardinality" : 1,

        3. Two dimensional array of m times n values
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
        data_types = ['scalar', 'one_dimensional', 'two_dimensional']
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add calibration event to an instrument asset.
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
            #if debug: print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))

            self.assertTrue(asset['id'] != 1)

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

        for data_type in data_types:
            if verbose: print '\nProcessing calibration data type of %s.' % data_type
            # Get data to create calibration event.
            #data_type = 'one_dimensional'
            input = self.calibration_data_for_create(event_type, instrument_uid, instrument_rd, data_type)


            event_name = input['eventName']
            if verbose: print '\n\tCalibration create...'
            if debug:
                print '\n\tCalibration create input: '
                dump_dict(input, debug)

            # Create calibration event.
            event_id, last_modified = self.create_calibration_event(event_type, instrument_uid, input, event_name)
            if verbose:
                print '\n event_id: ', event_id
                print '\n last_modified: ', last_modified
            self.assertTrue(input is not None)
            self.assertTrue('assetUid' in input)
            self.assertTrue(input['assetUid'] is not None)
            if verbose:
                print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
                print '\n\tNow performing an UPDATE on event we just created...'

            #- - - - - - - - - - - - - - - - - - - - - - - - - - -
            # (Negative) Try to create same event, expect error.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - -
            event_id, last_modified = self.negative_create_calibration_event(event_type, instrument_uid, input, event_name)

    def test_negative_calibration_events(self):
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

        Three different (basic) calibration data types:
            1. scalar,
            2. one dimensional array, and
            3. two dimensional array

        Descriptions:
        1. Scalar value
          "values" : [ 10.0 ],
          "dimensions" : [ 1 ],
          "cardinality" : 0,

        2. One dimensional array of n values
          "values" : [ 10.0, 11.0, 12.0 ... 20.0 ],   // eleven values in array
          "dimensions" : [ 11 ],
          "cardinality" : 1,

        3. Two dimensional array of m times n values
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
        headers = self.get_api_headers('admin', 'test')

        event_type = 'CALIBRATION_DATA'
        if verbose: print '\n'
        data_types = ['scalar', 'one_dimensional', 'two_dimensional']
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add calibration event to an instrument asset.
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
            #if debug: print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))

            self.assertTrue(asset['id'] != 1)

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

        for data_type in data_types:
            if verbose: print '\nProcessing bad calibration data type of %s.' % data_type
            # Get data to create calibration event.
            #data_type = 'one_dimensional'
            input = self.bad_calibration_data_for_create(event_type, instrument_uid, instrument_rd, data_type)
            event_name = input['eventName']
            if verbose: print '\n\tCalibration create...'
            if debug:
                print '\n\tCalibration create input: '
                dump_dict(input, debug)

            # Create calibration event.
            url = url_for('uframe.create_event')
            if debug: print '\n create url: ', url
            data = json.dumps(input)
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 400)
            if debug:
                print '\n Create calibration event -- response.status_code: ', response.status_code
                if response.status_code != 204:
                    print '\n Create calibration event -- response.content: ', json.loads(response.data)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Supporting functions:
    #   create_calibration_event
    #   update_calibration_event
    #   calibration_data_for_create
    #   calibration_data_for_update
    #   negative_create_calibration_event
    #   get_calibration_event_id_last_modified
    #   - - - - - - - - - -
    #   get_some_assets
    #   get_id_uid_rd
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Create calibration event.
    def create_calibration_event(self, _event_type, uid, input, event_name):
        """
        Create CALIBRATION_DATA event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        self.assertTrue(_event_type is not None)
        self.assertTrue(uid is not None)
        self.assertTrue(input is not None)
        self.assertTrue(event_name is not None)

        # Define variables specific to event type
        if verbose: print '\n\tCreating new event of type %s' % _event_type
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

        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug -- Create request_data(%d): ' % len(input)
            dump_dict(input, debug)

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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Update calibration event. Return event_id and last_modified (timestamp)
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update_calibration_event(self, _event_type, input, event_id, uid, event_name):
        """ Update calibration  event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n\tUpdate %s event, event id: %d' % (_event_type, event_id)

        self.assertTrue('eventId' in input)
        self.assertTrue(input['eventId'] is not None)
        self.assertTrue(isinstance(input['eventId'], int))
        if debug:
            print '\n test update -- UPDATE request_data: '
            dump_dict(input, debug)

        url = url_for('uframe.update_event', id=event_id)
        if debug: print '\n **** Update url: ', url
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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Get data to create calibration_data event.
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calibration_data_for_create(self, event_type, uid, rd, data_type):
        input = {}
        debug = False
        data_types = ['scalar', 'one_dimensional', 'two_dimensional']
        if debug: print '\n Create new %s event for %s, (assetUid: %s)' % (event_type, rd, uid)
        self.assertEquals(event_type, 'CALIBRATION_DATA')
        self.assertTrue(event_type is not None)
        self.assertTrue(uid is not None)
        self.assertTrue(rd is not None)
        self.assertTrue(is_instrument(rd))
        self.assertTrue(data_type in data_types)

        if event_type == 'CALIBRATION_DATA':
            #"@class" : ".XCalibrationData",
            unique_int = randint(5000, 10000)
            event_name = 'CC_test_' + uid + str(unique_int)
            # 'CC_a0'
            unique_num = randint(1000, 2000)
            if data_type == 'scalar':

                if debug: print '\n Create new %s...' % event_type
                input = {
                          'assetUid': uid,
                          'comments': 'Test entry (scalar) ' + str(unique_num),
                          'eventType': 'CALIBRATION_DATA',
                          'eventName': event_name,
                          'eventStartTime': 1443614400000,
                          'value':  42.0027,
                          'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                          'dataSource': 'Test data ' + str(datetime.datetime.now()),
                          'eventStopTime': None,
                          'tense': 'UNKNOWN'
                        }
            elif data_type == 'one_dimensional':

                if debug: print '\n Create new %s...' % event_type
                input = {
                          'assetUid': uid,
                          'comments': 'Test entry (scalar) ' + str(unique_num),
                          'eventType': 'CALIBRATION_DATA',
                          'eventName': event_name,
                          'eventStartTime': 1443614400000,
                          'value':  [-1.493703E-4, 2.0],
                          'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                          'dataSource': 'Test data ' + str(datetime.datetime.now()),
                          'eventStopTime': None,
                          'tense': 'UNKNOWN'
                        }
            elif data_type == 'two_dimensional':

                if debug: print '\n Create new %s...' % event_type
                input = {
                          'assetUid': uid,
                          'comments': 'Test entry (scalar) ' + str(unique_num),
                          'eventType': 'CALIBRATION_DATA',
                          'eventName': event_name,
                          'eventStartTime': 1443614400000,
                          'value':  [[-1.493703E-4, -2.0], [31.0, 32]],
                          'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                          'dataSource': 'Test data ' + str(datetime.datetime.now()),
                          'eventStopTime': None,
                          'tense': 'UNKNOWN'
                        }

        string_input = get_event_input_as_string(input, debug)
        self.assertTrue(input is not None)
        return string_input

    def calibration_data_for_create_two_dimensional(self, event_type, uid, rd):
        # two_dimensional_test_values
        two_dimensional_test_values =  [[10.0, 11.0], [20.0, 21.0], [30.0, 31.0], [40.0, 41.0], [50.0, 51.0]]
        debug = False
        if debug: print '\n Create new %s event for %s, (assetUid: %s)' % (event_type, rd, uid)
        self.assertEquals(event_type, 'CALIBRATION_DATA')
        self.assertTrue(event_type is not None)
        self.assertTrue(uid is not None)
        self.assertTrue(rd is not None)
        self.assertTrue(is_instrument(rd))
        self.assertEquals(event_type, 'CALIBRATION_DATA')

        #"@class" : ".XCalibrationData",
        unique_int = randint(5000, 10000)
        event_name = 'CC_test_' + uid + str(unique_int)
        # 'CC_a0'
        unique_num = randint(1000, 2000)

        if debug: print '\n Create new %s...' % event_type
        input = {
                  'assetUid': uid,
                  'comments': 'Test entry (scalar) ' + str(unique_num),
                  'eventType': 'CALIBRATION_DATA',
                  'eventName': event_name,
                  'eventStartTime': 1443644400000,
                  'value':  two_dimensional_test_values,
                  'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                  'dataSource': 'Test data ' + str(datetime.datetime.now()),
                  'eventStopTime': None,
                  'tense': 'UNKNOWN'
                }

        string_input = get_event_input_as_string(input, debug)
        self.assertTrue(input is not None)
        return string_input

    def bad_calibration_data_for_create(self, event_type, uid, rd, data_type):
        input = {}
        debug = False
        data_types = ['scalar', 'one_dimensional', 'two_dimensional']
        if debug: print '\n Create new %s event for %s, (assetUid: %s)' % (event_type, rd, uid)
        self.assertEquals(event_type, 'CALIBRATION_DATA')
        self.assertTrue(event_type is not None)
        self.assertTrue(uid is not None)
        self.assertTrue(rd is not None)
        self.assertTrue(is_instrument(rd))
        self.assertTrue(data_type in data_types)

        if event_type == 'CALIBRATION_DATA':
            #"@class" : ".XCalibrationData",
            unique_int = randint(5000, 10000)
            event_name = 'CC_test_' + uid + str(unique_int)
            # 'CC_a0'
            unique_num = randint(1000, 2000)
            if data_type == 'scalar':

                if debug: print '\n Create new %s...' % event_type
                input = {
                          'assetUid': uid,
                          'comments': 'Test entry (scalar) ' + str(unique_num),
                          'eventType': 'CALIBRATION_DATA',
                          'eventName': None,
                          'eventStartTime': 1443614400000,
                          'value':  42.0027,
                          'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                          'dataSource': 'Test data ' + str(datetime.datetime.now()),
                          'eventStopTime': None,
                          'tense': 'UNKNOWN'
                        }
            elif data_type == 'one_dimensional':

                if debug: print '\n Create new %s...' % event_type
                input = {
                          'assetUid': uid,
                          'comments': 'Test entry (scalar) ' + str(unique_num),
                          'eventType': 'CALIBRATION_DATA',
                          'eventName': None,
                          'eventStartTime': 1443614400000,
                          'value':  [-1.493703E-4, 2.0],
                          'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                          'dataSource': 'Test data ' + str(datetime.datetime.now()),
                          'eventStopTime': None,
                          'tense': 'UNKNOWN'
                        }
            elif data_type == 'two_dimensional':

                if debug: print '\n Create new %s...' % event_type
                input = {
                          'assetUid': uid,
                          'comments': 'Test entry (scalar) ' + str(unique_num),
                          'eventType': 'CALIBRATION_DATA',
                          'eventName': None,
                          'eventStartTime': 1443614400000,
                          'value':  [[-1.493703E-4, -2.0], [31.0, 32]],
                          'notes': 'Create calibration at ' + str(datetime.datetime.now()),
                          'dataSource': 'Test data ' + str(datetime.datetime.now()),
                          'eventStopTime': None,
                          'tense': 'UNKNOWN'
                        }

        string_input = get_event_input_as_string(input, debug)
        self.assertTrue(input is not None)
        return string_input


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Get data to update CALIBRATION_DATA event types.
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calibration_data_for_update(self, event_type, uid, event_id, last_modified, event_name):
        debug = self.debug
        try:
            if debug: print '\n debug -- calibration_data_for_update -- event_type/uid/eventId: %s/%s/%d' % (event_type, uid, event_id)
            self.assertTrue(event_type is not None)
            self.assertEquals(event_type, 'CALIBRATION_DATA')
            self.assertTrue(uid is not None)
            self.assertTrue(event_id is not None)
            self.assertTrue(isinstance(event_id, int))
            self.assertTrue(event_id > 0)
            self.assertTrue(last_modified is not None)
            self.assertTrue(last_modified > 0)
            self.assertTrue(event_name is not None)
            input = {}
            #eventName = 'CC_a0'
            unique_num = randint(1000, 2000)
            eventStartTime = 1453309000000 + 10000
            eventStopTime = eventStartTime + (unique_num*2)
            input = {
                      "@class": ".XCalibrationData",
                      "value": [-1.493703E-4, 3.0],
                      "comments": "Updated test entry.",
                      "eventId": event_id,
                      "assetUid": uid,
                      "eventType": event_type,
                      "eventName": event_name,
                      "eventStartTime": eventStartTime,
                      'eventStopTime': eventStopTime,
                      'lastModifiedTimestamp': last_modified,
                      'dataSource': 'Automated test data ' + str(datetime.datetime.now()),
                      'notes': 'Update calibration at ' + str(datetime.datetime.now()),
                      'tense': 'UNKNOWN'
                    }
            """
            {
            'eventStartTime': '1443614400000',
            'notes': 'Create calibration at 2016-09-15 14:05:42.756471',
            'value': '[-0.0001493703, 2.0]',
            'eventName': 'CC_test_A01247',
            'tense': 'UNKNOWN',
            'comments': 'Test entry (scalar) 1458',
            'eventType': 'CALIBRATION_DATA',
            'eventStopTime': None,
            'assetUid': 'A01247',
            'dataSource': 'Test data 2016-09-15 14:05:42.756494'
            }
            """

            #  Make all value in dictionary type string (simulate jgrid output).
            string_input = get_event_input_as_unicode(input, debug)
            self.assertTrue(input is not None)
            return string_input
        except Exception as err:
            message = str(err)
            self.assertEquals('Exception calibration_data_for_update: ', message)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create calibration event which already exists.
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def negative_create_calibration_event(self, _event_type, uid, input, event_name):
        """
        Create calibration event (which already exists.)
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Define variables specific to event type
        if verbose: print '\n\t\tNegative test creation of duplicate CALIBRATION_DATA event...'
        target_event_type = _event_type
        key = target_event_type

        # Get event types
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
        # (Negative) Create Event.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug -- Create request_data(%d): ' % len(input)
            dump_dict(input, debug)

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

    def get_calibration_event_id_last_modified(self, uid, event_name):
        """ Get calibration event id and lastModified from asset using calibration_data event name.
        """
        debug = self.debug
        self.assertTrue(uid is not None)
        self.assertTrue(event_name is not None)
        if debug:
            print '\n get_calibration_event_id_last_modified: uid: ', uid
            print '\n get_calibration_event_id_last_modified: event_name: ', event_name
        error_text = ' uid: %s, event name: %s' % (uid, event_name)
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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Get assets to assist in testing events.
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_some_assets(self):
        """ Get assets to assist in testing events.
        """
        headers = self.get_api_headers('admin', 'test')
        try:
            # Get assets.
            url = url_for('uframe.get_assets')
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue('assets' in results)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            # Verify there are assets in list.
            assets = results['assets']
            self.assertTrue(assets is not None)
            self.assertTrue(isinstance(assets, list))
            return assets

        except Exception as err:
            message = str(err)
            self.assertEquals('Exception get_some_assets: %s' % message)
            return None

    # Get id, uid and rd.
    def get_id_uid_rd(self, asset):
        """ For an asset, get id, uid and rd.
        """
        debug = self.debug
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