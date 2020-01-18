#!/usr/bin/env python
"""
Asset Management - Specific testing for events routes

Routes:
[GET] /events/<int:id>                          # Get event. This should not be used by UI; if needed, then discuss!
[GET] /events/types                             # Get all supported event types
[GET] /events/uid/<string:uid>                  # Get all events of all types for asset with uid
      /events/uid/<string:uid>?type=EventType   # Get all events for asset with uid, only type(s) identified
      # Example: /uframe/events/uid/A00228?type=ATVENDOR
      # Example: /uframe/events/uid/A00228?type=ATVENDOR,INTEGRATION

[POST] /events                                  # Create an event of each eventType.
[PUT]  /events/<int:id>                         # Update events of each eventType.


Test the creation, read and update of the following event types:
    'ACQUISITION',
    'ASSET_STATUS',
    'ATVENDOR',
    'INTEGRATION',
    'LOCATION',
    'RETIREMENT',
    'STORAGE',
    'UNSPECIFIED'

The remaining event types are tested in separate files:
    'CALIBRATION_DATA'      test_calibration_events.py
    'CRUISE_INFO'           test_cruises.py
    'DEPLOYMENT'    Test Cases:
                    test_deployments.py             Test UI routes for deployment support.
                    test_uframe_deployments.py      Exercise direct uframe deployment endpoints to verify operation(s).
"""
__author__ = 'Edna Donoughe'

import unittest
from ooiservices.app import (create_app, db)
from ooiservices.tests.common_tools import (dump_dict, get_event_input_as_unicode, get_event_input_as_string)
from ooiservices.app.uframe.common_tools import operational_status_values, operational_status_display_values
from ooiservices.app.uframe.common_tools import (get_asset_types, get_asset_type_by_rd, get_uframe_asset_type)
from base64 import b64encode
from random import randint
from flask import (url_for)
import requests
import datetime
import json
from unittest import skipIf
import os


from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_event_types)
from ooiservices.app.uframe.deployment_tools import (is_instrument, is_platform, is_mooring)
from ooiservices.app.uframe.events_validate_fields import get_rd_from_integrationInto


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
    # Test cases:
    #   test_get_events
    #   test_create_event_types_random
    #   test_create_event_types_numerous_regular
    #   test_create_event_types_numerous_requests
    # Proposed:
    #   test_negative_create_events
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
        good_asset_uid = asset['uid']
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

        self.assertTrue(asset is not None)
        asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
        self.assertTrue(asset_uid is not None)
        self.assertTrue(rd is not None)
        uid, input = self.create_event_data('STORAGE', asset_uid, rd)
        input['eventName'] = None
        self.assertTrue(input is not None)
        uid = uid + str(datetime.datetime.now())
        event_id, last_modified = self._create_event_type('STORAGE', uid, input)

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

        # Get valid operational status values
        url = url_for('uframe.get_operational_status_values')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('operational_status_values' in result)

        # Get event tabs for asset types
        asset_types = get_asset_types()
        for asset_type in asset_types:

            url = url_for('uframe.get_event_tabs_by_asset_type', asset_type=asset_type)
            if verbose: print '\n ----- url: ', url
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)
            self.assertTrue(result is not None)
            self.assertTrue(isinstance(result, dict))
            self.assertTrue('tabs' in result)
            self.assertTrue(len(result['tabs']) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Negative test - use bad uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url = url_for('uframe.get_events_by_uid', uid='nogood')
        target_url = base_url + '?type=' + 'CRUISE_INFO'
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 400)
        #result = json.loads(response.data)

        # Get supported event types (/events/edit_phase_values).
        url = url_for('uframe.get_event_edit_phase_values')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        # Get all events for an asset uid.
        url = url_for('uframe.get_all_events_by_uid', uid=good_asset_uid)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('events' in result)
        self.assertTrue(len(result['events']) > 0)

        # Get all events for an asset uid.
        url = url_for('uframe.get_all_events_by_uid', uid='bad-uid')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        if verbose: print '\n'

    def test_create_event_types_random(self):
        """
        Create events of different types for three random assets with an asset type of mooring, platform and sensor.
        Verbose output sample:
        Processing event_types(8):
        ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

         Have some assets (4742)

         Note: Number of loops to get three items of interest: 118

         ----- Mooring:
             mooring_id: 3008
             mooring_uid: N00240
             mooring_rd: CP02PMUO

         ----- Platform:
             platform_id: 3680
             platform_uid: N00122
             platform_rd: CE01ISSP-SP001

         ----- Instrument:
             instrument_id: 758
             instrument_uid: A00616
             instrument_rd: CE01ISSM-RID16-02-FLORTD000

         -- Mooring Assets.

            Creating ACQUISITION event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32731 and lastModifiedTimestamp: 1473779975511

            Creating ASSET_STATUS event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32732 and lastModifiedTimestamp: 1473779975678

            Creating ATVENDOR event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32733 and lastModifiedTimestamp: 1473779975844

            Creating INTEGRATION event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32734 and lastModifiedTimestamp: 1473779976011

            Creating LOCATION event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32735 and lastModifiedTimestamp: 1473779976178

            Creating RETIREMENT event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32736 and lastModifiedTimestamp: 1473779976350

            Creating STORAGE event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32737 and lastModifiedTimestamp: 1473779976521

            Creating UNSPECIFIED event for mooring - asset id/uid/rd: 3008/N00240/CP02PMUO
                Created eventId: 32738 and lastModifiedTimestamp: 1473779976687

         -- Node Assets.

            Creating ACQUISITION event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32739 and lastModifiedTimestamp: 1473779976866

            Creating ASSET_STATUS event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32740 and lastModifiedTimestamp: 1473779977040

            Creating ATVENDOR event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32741 and lastModifiedTimestamp: 1473779977215

            Creating INTEGRATION event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32742 and lastModifiedTimestamp: 1473779977383

            Creating LOCATION event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32743 and lastModifiedTimestamp: 1473779977553

            Creating RETIREMENT event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32744 and lastModifiedTimestamp: 1473779977728

            Creating STORAGE event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32745 and lastModifiedTimestamp: 1473779977902

            Creating UNSPECIFIED event for platform - asset id/uid/rd: 3680/N00122/CE01ISSP-SP001
                Created eventId: 32746 and lastModifiedTimestamp: 1473779978083

         -- Sensor Assets.

            Creating ACQUISITION event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32747 and lastModifiedTimestamp: 1473779978269

            Creating ASSET_STATUS event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32748 and lastModifiedTimestamp: 1473779978433

            Creating ATVENDOR event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32749 and lastModifiedTimestamp: 1473779978600

            Creating INTEGRATION event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32750 and lastModifiedTimestamp: 1473779978773

            Creating LOCATION event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32751 and lastModifiedTimestamp: 1473779978939

            Creating RETIREMENT event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32752 and lastModifiedTimestamp: 1473779979106

            Creating STORAGE event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32753 and lastModifiedTimestamp: 1473779979262

            Creating UNSPECIFIED event for instrument - asset id/uid/rd: 758/A00616/CE01ISSM-RID16-02-FLORTD000
                Created eventId: 32754 and lastModifiedTimestamp: 1473779979427
        """
        debug = self.debug
        verbose = self.verbose
        event_types = get_supported_event_types()

        # Remove event_type value(s) which are not used in this test case.
        if 'CALIBRATION_DATA' in event_types:
            event_types.remove('CALIBRATION_DATA')
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')
        if 'DEPLOYMENT' in event_types:
            event_types.remove('DEPLOYMENT')

        if verbose: print '\n\nProcessing event_types(%d): \n%s' % (len(event_types), event_types)

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
            if debug: print 'Count: %d' % count

            asset_index = randint(0, (number_of_assets-1))
            #print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))
            start_index = randint(number_of_assets/4, number_of_assets-1)
            asset = assets[start_index]

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_id > 0)
            self.assertTrue('assetType' in asset)
            asset_type = asset['assetType']
            asset_type = get_uframe_asset_type(asset_type)
            self.assertTrue(asset_type in get_asset_types())
            if rd is not None:
                self.assertEquals(asset_type, get_asset_type_by_rd(rd))

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_id > 0)
            if rd is None:
                continue
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
            else:
                continue
        if verbose:
            print '\n Note: Number of loops to get three items of interest: %d ' % count
            print '\n ----- Mooring:'
            print '\t mooring_id: %d' % mooring_id
            print '\t mooring_uid: %s' % mooring_uid
            print '\t mooring_rd: %s' % mooring_rd
            print '\n ----- Platform:'
            print '\t platform_id: %d' % platform_id
            print '\t platform_uid: %s' % platform_uid
            print '\t platform_rd: %s' % platform_rd
            print '\n ----- Instrument:'
            print '\t instrument_id: %d' % instrument_id
            print '\t instrument_uid: %s' % instrument_uid
            print '\t instrument_rd: %s' % instrument_rd

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Mooring asset. Add event(s).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- Mooring Assets.'
        for event_type in event_types:
            if verbose: print '\n\tCreating %s event for mooring - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                mooring_id, mooring_uid, mooring_rd)
            # Create events.
            uid, input = self.create_event_data(event_type, mooring_uid, mooring_rd)
            #print '\n event_type: ', event_type
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Platform asset. Add event(s).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- Node Assets.'
        for event_type in event_types:
            #print '\n processing event_type: ', event_type
            if verbose: print '\n\tCreating %s event for platform - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                platform_id, platform_uid, platform_rd)
            # Create events.
            uid, input = self.create_event_data(event_type, platform_uid, platform_rd)
            #print '\n event_type: ', event_type
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Instrument asset. Add event(s).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- Sensor Assets.'
        for event_type in event_types:
            if verbose: print '\n\tCreating %s event for instrument - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                        instrument_id, instrument_uid, instrument_rd)
            # Create events.
            uid, input = self.create_event_data(event_type, instrument_uid, instrument_rd)
            #print '\n event_type: ', event_type
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

        if verbose: print '\n'

    def test_create_duplicate_event_types_random(self):
        """
        Create events of different types for three random assets with an asset type of mooring, platform and sensor.
        Create a duplicate (and fail) for each event type for each asset type.
        Verbose output sample:

        Processing event_types(8):
        ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

         Have some assets (5628)

         Note: Number of loops to get three items of interest: 1296

         ----- Mooring:
             mooring_id: 3011
             mooring_uid: N00242
             mooring_rd: CP03ISSM

         ----- Platform:
             platform_id: 474
             platform_uid: A00078
             platform_rd: CE05MOAS-GL311

         ----- Instrument:
             instrument_id: 3551
             instrument_uid: N00306
             instrument_rd: CE05MOAS-GL312-02-FLORTM000

         -- Mooring Assets.

            Creating ACQUISITION event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36211 and lastModifiedTimestamp: 1474229235005
                Creating duplicate event of type ACQUISITION

            Creating ASSET_STATUS event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36212 and lastModifiedTimestamp: 1474229235246
                Creating duplicate event of type ASSET_STATUS

            Creating ATVENDOR event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36213 and lastModifiedTimestamp: 1474229235505
                Creating duplicate event of type ATVENDOR

            Creating INTEGRATION event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36214 and lastModifiedTimestamp: 1474229235750
                Creating duplicate event of type INTEGRATION

            Creating LOCATION event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36215 and lastModifiedTimestamp: 1474229235994
                Creating duplicate event of type LOCATION

            Creating RETIREMENT event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36216 and lastModifiedTimestamp: 1474229236238
                Creating duplicate event of type RETIREMENT

            Creating STORAGE event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36217 and lastModifiedTimestamp: 1474229236482
                Creating duplicate event of type STORAGE

            Creating UNSPECIFIED event for mooring - asset id/uid/rd: 3011/N00242/CP03ISSM
                Created eventId: 36218 and lastModifiedTimestamp: 1474229236715
                Creating duplicate event of type UNSPECIFIED

         -- Node Assets.

            Creating ACQUISITION event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36219 and lastModifiedTimestamp: 1474229236972
                Creating duplicate event of type ACQUISITION

            Creating ASSET_STATUS event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36220 and lastModifiedTimestamp: 1474229237247
                Creating duplicate event of type ASSET_STATUS

            Creating ATVENDOR event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36221 and lastModifiedTimestamp: 1474229237511
                Creating duplicate event of type ATVENDOR

            Creating INTEGRATION event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36222 and lastModifiedTimestamp: 1474229237791
                Creating duplicate event of type INTEGRATION

            Creating LOCATION event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36223 and lastModifiedTimestamp: 1474229239097
                Creating duplicate event of type LOCATION

            Creating RETIREMENT event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36224 and lastModifiedTimestamp: 1474229239419
                Creating duplicate event of type RETIREMENT

            Creating STORAGE event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36225 and lastModifiedTimestamp: 1474229239691
                Creating duplicate event of type STORAGE

            Creating UNSPECIFIED event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 36226 and lastModifiedTimestamp: 1474229239966
                Creating duplicate event of type UNSPECIFIED

         -- Sensor Assets.

            Creating ACQUISITION event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36227 and lastModifiedTimestamp: 1474229240249
                Creating duplicate event of type ACQUISITION

            Creating ASSET_STATUS event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36228 and lastModifiedTimestamp: 1474229240549
                Creating duplicate event of type ASSET_STATUS

            Creating ATVENDOR event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36229 and lastModifiedTimestamp: 1474229240837
                Creating duplicate event of type ATVENDOR

            Creating INTEGRATION event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36230 and lastModifiedTimestamp: 1474229241124
                Creating duplicate event of type INTEGRATION

            Creating LOCATION event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36231 and lastModifiedTimestamp: 1474229241415
                Creating duplicate event of type LOCATION

            Creating RETIREMENT event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36232 and lastModifiedTimestamp: 1474229241759
                Creating duplicate event of type RETIREMENT

            Creating STORAGE event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36233 and lastModifiedTimestamp: 1474229242044
                Creating duplicate event of type STORAGE

            Creating UNSPECIFIED event for instrument - asset id/uid/rd: 3551/N00306/CE05MOAS-GL312-02-FLORTM000
                Created eventId: 36234 and lastModifiedTimestamp: 1474229242340
                Creating duplicate event of type UNSPECIFIED

        """
        debug = self.debug
        verbose = self.verbose
        event_types = get_supported_event_types()

        # Remove event_type value(s) which are not used in this test case.
        if 'CALIBRATION_DATA' in event_types:
            event_types.remove('CALIBRATION_DATA')
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')
        if 'DEPLOYMENT' in event_types:
            event_types.remove('DEPLOYMENT')

        if verbose: print '\n\nProcessing event_types(%d): \n%s' % (len(event_types), event_types)

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
            if debug: print 'Count: %d' % count

            asset_index = randint(0, (number_of_assets-1))
            #print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))
            start_index = randint(number_of_assets/4, number_of_assets-1)
            asset = assets[start_index]

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_id > 0)
            self.assertTrue('assetType' in asset)
            asset_type = asset['assetType']
            asset_type = get_uframe_asset_type(asset_type)
            self.assertTrue(asset_type in get_asset_types())
            if rd is not None:
                self.assertEquals(asset_type, get_asset_type_by_rd(rd))

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_id > 0)
            if rd is None:
                continue
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
            else:
                continue
        if verbose:
            print '\n Note: Number of loops to get three items of interest: %d ' % count
            print '\n ----- Mooring:'
            print '\t mooring_id: %d' % mooring_id
            print '\t mooring_uid: %s' % mooring_uid
            print '\t mooring_rd: %s' % mooring_rd
            print '\n ----- Platform:'
            print '\t platform_id: %d' % platform_id
            print '\t platform_uid: %s' % platform_uid
            print '\t platform_rd: %s' % platform_rd
            print '\n ----- Instrument:'
            print '\t instrument_id: %d' % instrument_id
            print '\t instrument_uid: %s' % instrument_uid
            print '\t instrument_rd: %s' % instrument_rd

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Mooring asset. Add event(s).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- Mooring Assets.'
        for event_type in event_types:
            if verbose: print '\n\tCreating %s event for mooring - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                mooring_id, mooring_uid, mooring_rd)
            # Create events.
            uid, input = self.create_event_data(event_type, mooring_uid, mooring_rd)
            #print '\n event_type: ', event_type
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
            self._create_duplicate_event_type(event_type, uid, input, verbose)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Platform asset. Add event(s).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- Node Assets.'
        for event_type in event_types:
            #print '\n processing event_type: ', event_type
            if verbose: print '\n\tCreating %s event for platform - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                platform_id, platform_uid, platform_rd)
            # Create events.
            uid, input = self.create_event_data(event_type, platform_uid, platform_rd)
            #print '\n event_type: ', event_type
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

            self._create_duplicate_event_type(event_type, uid, input, verbose)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Instrument asset. Add event(s).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- Sensor Assets.'
        for event_type in event_types:
            if verbose: print '\n\tCreating %s event for instrument - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                        instrument_id, instrument_uid, instrument_rd)
            # Create events.
            uid, input = self.create_event_data(event_type, instrument_uid, instrument_rd)
            #print '\n event_type: ', event_type
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
            self._create_duplicate_event_type(event_type, uid, input, verbose)

        if verbose: print '\n'

    def test_create_event_types_numerous_regular(self):
        """
        Create events of different types for one or more numerous assets.

        Routes:
        [GET]   /assets
        [GET]   /events/uid/<string:uid>
        [GET]   /events/uid/<string:uid>?type=EventType   # Example: /uframe/events/uid/A00228?type=ACQUISITION
        [PUT]   /events/<int:id>
        [POST]  /events

        Sample verbose output:
        Processing event_types(8):
        ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

         Have some assets (4742)

        ***********************************************************************

         (1) Processing Sensor asset...

         ----- ACQUISITION event.
            -- Creating ACQUISITION event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32403 and lastModifiedTimestamp: 1473773283364
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32403

         ----- ASSET_STATUS event.
            -- Creating ASSET_STATUS event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32404 and lastModifiedTimestamp: 1473773283683
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32404

         ----- ATVENDOR event.
            -- Creating ATVENDOR event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32405 and lastModifiedTimestamp: 1473773284005
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32405

         ----- INTEGRATION event.
            -- Creating INTEGRATION event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32406 and lastModifiedTimestamp: 1473773284324
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32406

         ----- LOCATION event.
            -- Creating LOCATION event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32407 and lastModifiedTimestamp: 1473773284651
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32407

         ----- RETIREMENT event.
            -- Creating RETIREMENT event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32408 and lastModifiedTimestamp: 1473773284977
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32408

         ----- STORAGE event.
            -- Creating STORAGE event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32409 and lastModifiedTimestamp: 1473773285307
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32409

         ----- UNSPECIFIED event.
            -- Creating UNSPECIFIED event - asset id/uid/rd: 3426/OL000389/None
                Created eventId: 32410 and lastModifiedTimestamp: 1473773285656
                Now performing an UPDATE on event we just created...
            -- Updated eventId: 32410

         Note: Number of assets processed: 1

        """
        debug = self.debug
        verbose = self.verbose
        event_types = get_supported_event_types()

        # Remove event_type value(s) which are not used in this test case.
        if 'CALIBRATION_DATA' in event_types:
            event_types.remove('CALIBRATION_DATA')
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')
        if 'DEPLOYMENT' in event_types:
            event_types.remove('DEPLOYMENT')
        if verbose: print '\n\nProcessing event_types(%d):\n%s' % (len(event_types), event_types)

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        count = 0
        maximum_count = 2
        while count <= number_of_assets and count < maximum_count:

            # Select an asset...Get asset_id, asset_uid, rd.
            start_index = randint(number_of_assets/4, number_of_assets-1)
            some_index = randint(35, number_of_assets-1)
            asset = assets[some_index]
            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_id > 0)
            self.assertTrue('assetType' in asset)
            asset_type = asset['assetType']
            asset_type = get_uframe_asset_type(asset_type)
            self.assertTrue(asset_type in get_asset_types())
            if rd is not None:
                self.assertEquals(asset_type, get_asset_type_by_rd(rd))

            message = '(%d) Processing %s asset...' % ((count + 1), asset_type)
            if verbose: print '\n%s' % message
            count +=1

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Add event(s) to asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Note: To test single event type, set event_types list here: event_types = ['UNSPECIFIED']
            #event_types = ['ASSET_STATUS']
            for event_type in event_types:
                if verbose:
                    print '\n ----- %s event.' % event_type
                    print '\t-- Creating %s event - asset id/uid/rd: %d/%s/%s' % (event_type, asset_id, asset_uid, rd)

                # Create an event
                uid, input = self.create_event_data(event_type, asset_uid, rd)
                if debug: print '\n input: ', dump_dict(input, True)
                self.assertTrue(input is not None)
                self.assertTrue('assetUid' in input)
                self.assertTrue(input['assetUid'] is not None)
                if event_type == 'ACQUISITION':
                    self.assertTrue('purchasePrice' in input)
                    if input['purchasePrice'] is not None:
                        if debug: print '\n test:: Update %s event, attribute purchasePrice type: %r' % \
                                        (event_type, type(input['purchasePrice']))
                        #self.assertTrue(isinstance(input['purchasePrice'], float))

                event_id, last_modified = self._create_event_type(event_type, uid, input)
                self.assertTrue(event_id is not None)
                self.assertTrue(event_id > 0)
                if verbose:
                    print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

                if verbose: print '\t\tNow performing an UPDATE on event we just created...'
                # Update the one we just created
                uid, input = self.update_event_data(event_type, asset_uid, rd, event_id, last_modified)
                self.assertTrue(input is not None)
                self.assertTrue('eventId' in input)
                self.assertEquals(int(input['eventId']), event_id)
                self.assertTrue('assetUid' in input)
                self.assertEquals(input['assetUid'], uid)
                self.assertEquals(input['assetUid'], asset_uid)
                input['eventId'] = event_id
                if not isinstance(input['eventId'], int):
                    if debug: print '\n debug -- test case -- event_id is not instance of int...'
                    input['eventId'] = int(str(input['eventId']))
                    self.assertTrue(isinstance(input['eventId'], int))
                update_event_id = self._update_event_type(event_type, input, event_id)
                if verbose: print '\t-- Updated eventId: %d ' % update_event_id
                self.assertTrue(event_id, update_event_id)

        if verbose: print '\n Note: Number of assets processed: %d ' % count
        if verbose: print '\n'

    def test_create_event_types_numerous_requests(self):
        """
        *********************************************************************************************************
        **** Fails if login and asset_manage scope required. Requires localhost:400 services to be running. *****
        *********************************************************************************************************
        Create events of different types for numerous assets, configure for more than two assets.

        Following event types supported in other TestCases:
            'DEPLOYMENT'
            'CALIBRATION_DATA'
            'CRUISE_INFO'

        Sample verbose output:
        Event_types to be added to asset(8):
        ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

        Have some assets (4742)

        ***********************************************************************

         (1) Processing Sensor asset...

         Creating ACQUISITION event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32611

         Creating ASSET_STATUS event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32612

         Creating ATVENDOR event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32613

         Creating INTEGRATION event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32614

         Creating LOCATION event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32615

         Creating RETIREMENT event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32616

         Creating STORAGE event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32617

         Creating UNSPECIFIED event - asset id/uid/rd: 1181/A01674/None

            Now performing an UPDATE on event we just created...

            Updated eventId: 32618

         Note: Number of assets processed: 1
        """
        debug = self.debug
        verbose = self.verbose
        event_types = get_supported_event_types()

        # Remove event_type value(s) which are not used in this test case.
        if 'CALIBRATION_DATA' in event_types:
            event_types.remove('CALIBRATION_DATA')
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')
        if 'DEPLOYMENT' in event_types:
            event_types.remove('DEPLOYMENT')
        if verbose: print '\nEvent_types to be added to asset(%d): \n%s' % (len(event_types), event_types)

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\nHave some assets (%d)' % number_of_assets
        count = 0
        maximum_count = 1
        while count <= number_of_assets and count < maximum_count:

            # Select an asset...
            some_index = randint(int(number_of_assets/8), number_of_assets)
            asset = assets[some_index]

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_id > 0)

            # Get asset type, verify valid asset type provided.
            asset_type = asset['assetType']
            asset_type = get_uframe_asset_type(asset_type)
            self.assertTrue(asset_type in get_asset_types())
            if rd is not None:
                self.assertEquals(asset_type, get_asset_type_by_rd(rd))

            if verbose: print '\n***********************************************************************'
            message = '(%d) Processing %s asset...' % ((count + 1), asset_type)
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
                self.assertTrue(input is not None)
                self.assertTrue('assetUid' in input)
                self.assertTrue(input['assetUid'] is not None)
                event_id, last_modified = self._create_event_type_requests(event_type, uid, input)
                self.assertTrue(last_modified > 0)
                if debug: print '\n (requests) Created eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

                if verbose:
                    print '\n\tNow performing an UPDATE on event we just created...'
                # Update the one we just created
                uid, input = self.update_event_data(event_type, asset_uid, rd, event_id, last_modified)
                input['eventId'] = event_id
                if not isinstance(input['eventId'], int):
                    if debug: print '\n debug -- test case -- event_id is not instance of int...'
                    input['eventId'] = int(str(input['eventId']))
                    self.assertTrue(isinstance(input['eventId'], int))
                update_event_id = self._update_event_type_requests(event_type, input, event_id)
                if verbose: print '\n\tUpdated eventId: %d ' % update_event_id
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

    def get_id_uid_rd(self, asset):
        """ For an asset, get id, uid and rd.
        """
        debug = False
        asset_uid = None
        asset_id = None
        rd = None
        try:
            # Get asset_id
            self.assertTrue('id' in asset)
            asset_id = asset['id']
            self.assertTrue(asset_id is not None)
            self.assertTrue(asset_id)
            if debug: print '\n Have asset_id: %d' % asset_id
            self.assertTrue(asset_id > 1)

            # Get asset uid
            self.assertTrue('uid' in asset)
            asset_uid = asset['uid']
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_uid)
            if debug: print '\n Have asset_uid: %s ' % asset_uid

            # Get reference designator
            self.assertTrue('ref_des' in asset)
            rd = asset['ref_des']
            if debug: print '\n Have rd: %s ' % rd
            return asset_id, asset_uid, rd

        except Exception:
            print '\n Exception getting asset id/uid/rd: %d/%s/%s' % (asset_id, asset_uid, rd)
            return asset_id, asset_uid, rd

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

        not_supported = ['CALIBRATION_DATA', 'CRUISE_INFO', 'DEPLOYMENT']
        self.assertTrue(_event_type not in not_supported)
        self.assertTrue(_event_type is not None)
        self.assertTrue(uid is not None)
        self.assertTrue(input is not None)

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

        if _event_type == 'ACQUISITION':
            self.assertTrue('purchasePrice' in input)
            if input['purchasePrice'] is not None:
                if debug: print '\n Update %s event, attribute purchasePrice type: %r' % (_event_type, type(input['purchasePrice']))
                #self.assertTrue(isinstance(input['purchasePrice'], float))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n -- Create %s event' % key
            dump_dict((input, debug))

        url = url_for('uframe.create_event')
        if debug: print '\n create url: ', url
        data = json.dumps(input)
        response = self.client.post(url, headers=headers, data=data)
        if response.status_code != 200:
            #print '\n Creating an event of type ', _event_type
            #print '\n Create event -- response.status_code: ', response.status_code
            if response.data and response.data is not None:
                response_error = json.loads(response.data)
                #print '\n response_data: ', response_error

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue('event' in response_data)
        event = response_data['event']
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)
        self.assertTrue(isinstance(event_id, int))
        self.assertTrue(event_id > 0)
        self.assertTrue('lastModifiedTimestamp' in event)
        last_modified = event['lastModifiedTimestamp']
        self.assertTrue(last_modified is not None)
        if debug: print '\n ===== Exit test::_create_event_type....'
        return event_id, last_modified

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create duplicate event_type, anticipate failure.
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _create_duplicate_event_type(self, _event_type, uid, input, verbose=False):
        """
        Create event.
        """
        debug = self.debug
        verbose = verbose
        headers = self.get_api_headers('admin', 'test')

        not_supported = ['CALIBRATION_DATA', 'CRUISE_INFO', 'DEPLOYMENT']
        self.assertTrue(_event_type not in not_supported)
        self.assertTrue(_event_type is not None)
        self.assertTrue(uid is not None)
        self.assertTrue(input is not None)

        # Define variables specific to event type
        if verbose: print '\t\tCreating duplicate event of type %s' % _event_type
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

        # Verify event_types is a list and not empty.
        events_by_type = results['event_types']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, list))
        if debug: print '\n -- len(events_by_type): ', len(events_by_type)

        if _event_type == 'ACQUISITION':
            self.assertTrue('purchasePrice' in input)
            if debug:
                if input['purchasePrice'] is not None:
                    print '\n Update %s event, attribute purchasePrice type: %r' % (_event_type, type(input['purchasePrice']))
                    #self.assertTrue(isinstance(input['purchasePrice'], float))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create duplicate event, expect failure.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n -- Create %s event' % key
            dump_dict((input, debug))

        url = url_for('uframe.create_event')
        if debug: print '\n create url: ', url
        data = json.dumps(input)
        response = self.client.post(url, headers=headers, data=data)
        if response.status_code != 400:
            #print '\n (Negative) Create duplicate event -- response.status_code: ', response.status_code
            if response.data:
                response_error = json.loads(response.data)
                #print '\n response_data: ', response_error

        self.assertEquals(response.status_code, 400)
        self.assertTrue(response.data is not None)

        return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create event_type using requests (to self.root url - localhost:4000/etc)
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _create_event_type_requests(self, _event_type, uid, input):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        self.assertTrue(_event_type is not None)
        self.assertTrue(input is not None)
        self.assertTrue(input)

        # Define variables specific to event type
        if verbose: print '\n Creating new event of type %s' % _event_type
        not_supported = ['CALIBRATION_DATA', 'CRUISE_INFO', 'DEPLOYMENT']
        self.assertTrue(_event_type not in not_supported)

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
            dump_dict(input, debug)

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

        if response.status_code != 200:
            if debug: print '\n Failed to execute create event, status_code: %d' % response.status_code
            dump_dict(input, debug)
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Failed Event create data from POST: %s' % response_data
            event_id = 0
            last_modified = 0
            error_text = 'Failed to create %s event, status code: %d' % (_event_type, response.status_code)
            self.assertEquals('Exception: ', error_text)
        else:
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Test: Successful Event create data from POST (json.loads(response.content)): %s' % response_data

            self.assertTrue('event' in response_data)
            event = response_data['event']
            self.assertTrue(event is not None)
            self.assertTrue('eventId' in event)
            event_id = event['eventId']
            self.assertTrue(event_id is not None)
            self.assertTrue('lastModifiedTimestamp' in event)
            last_modified = event['lastModifiedTimestamp']
            self.assertTrue(last_modified is not None)
            self.assertTrue(last_modified)
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
        not_supported = ['DEPLOYMENT', 'CALIBRATION_DATA', 'CRUISE_']
        self.assertTrue(_event_type not in not_supported)

        self.assertTrue(_event_type is not None)
        self.assertTrue(input is not None)
        self.assertTrue(event_id is not None)
        self.assertTrue(event_id > 0)
        self.assertTrue(input['eventId'], event_id)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n **** Update %s event' % _event_type
            print '\n **** Update event_id: %r' % event_id
            print '\n **** Update input: '
            dump_dict(input, verbose)

        if debug:
            print '\n Test -- Update request_data(%d): ' % len(input)
            dump_dict(input, debug)

        url = url_for('uframe.update_event', id=event_id)
        if verbose: print '\n **** Update url: ', url
        data = json.dumps(input)
        response = self.client.put(url, headers=headers, data=data)
        if response.status_code != 200:
            if debug: print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            if debug: print '\n response_error: ', response_error
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue('event' in response_data)
        event = response_data['event']
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)
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
        not_supported = ['DEPLOYMENT', 'CALIBRATION_DATA', 'CRUISE_']
        self.assertTrue(_event_type not in not_supported)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n **** Update %s event' % _event_type
            print '\n **** Update event_id: %r' % event_id
            print '\n **** Update input: %r' % input

        if debug:
            print '\n Test -- Update request_data(%d): ' % len(input)
            dump_dict(input, debug)
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
                if debug: print '\n Successful Event update data from POST: '
                dump_dict(response_data, debug)

        self.assertTrue('event' in response_data)
        event = response_data['event']
        if debug: print '\n debug -- event: ', event
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        if debug: print '\n debug -- response_data[event][eventId]: %r ' % response_data['event']['eventId']
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
        """ Get data to create different event types.
        """
        self.assertTrue(uid is not None)
        self.assertTrue(event_type is not None)
        input = {}
        unique_num = randint(1000, 2000)
        unique_float = randint(1, 1000) * 100.0
        notes = 'Create new %s event for %s, (assetUid: %s); unique number: %d' % (event_type, rd, uid, unique_num)
        if rd is None:
            eventName = event_type + '-' + str(unique_num)
        else:
            eventName = rd
        if event_type == 'ACQUISITION':
            eventStartTime = 1398039060000 + (unique_num*10)
            eventStopTime = eventStartTime + (unique_num*2)
            purchasePrice =  unique_float

            input = {
                      'purchasePrice': purchasePrice,
                      'purchaseDate': eventStartTime,
                      'deliveryDate': eventStartTime + unique_num,
                      'purchasedBy': 'purchased by: ' + str(unique_num),
                      'vendorIdentification': 'vendor identification: ' + str(unique_num),
                      'vendorPointOfContact': 'vendor point of contact: ' + str(unique_float),
                      'receivedFromVendorBy': 'received from vendor by: ' + str(unique_num) + str(unique_float),
                      'authorizationNumber': None,
                      'authorizationForPayment': None,
                      'invoiceNumber': 'invoice number: ' + str(unique_num),
                      'eventType': 'ACQUISITION',
                      'eventName': eventName + str(datetime.datetime.now()),
                      'eventStartTime': eventStartTime,
                      'eventStopTime': eventStopTime,
                      'notes': notes,
                      'tense': 'UNKNOWN',
                      'dataSource': 'Test case.' + str(datetime.datetime.now()),
                      'assetUid': uid
                      }

        elif event_type == 'ASSET_STATUS':
            valid_status_values = operational_status_values()
            status_index = randint(0, (len(valid_status_values)-1))
            #print '\n status_index: ', status_index
            status_value = valid_status_values[status_index]
            #print '\n debug -- status_value: ', status_value
            input = {
                    'severity': 5,
                    'reason': str(unique_num),
                    'location': None,
                    'status': status_value,
                    'eventType': 'ASSET_STATUS',
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'eventName': eventName + str(datetime.datetime.now()),
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num) + str(datetime.datetime.now()),
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
                    'eventName': eventName + str(datetime.datetime.now()),
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
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
                    'eventName':  eventName + str(datetime.datetime.now()),
                    'eventStartTime': eventStartTime,
                    'eventStopTime': 1405382400000,
                    'notes': notes + str(unique_num),
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
                    }

        elif event_type == 'LOCATION':
            unique_num = randint(201, 300)
            small_increment = (randint(400, 500))/10000.00
            latitude = 40.36341 + small_increment
            longitude = -70.77599 - small_increment
            depth = 551.27 + small_increment
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*2)
            orbitRadius = small_increment
            input = {
                    'depth': 551.27,
                    'longitude': longitude,
                    'latitude': latitude,
                    'orbitRadius': orbitRadius,
                    'eventType': 'LOCATION',
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'notes': notes,
                    'eventName': eventName,
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
                    'eventName': eventName + str(unique_num) + str(datetime.datetime.now()),
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_num),
                    'assetUid': uid
                    }

        elif event_type == 'STORAGE':
            unique_num = randint(301, 700)
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*3)
            input = {
                    'buildingName': 'Tower' + str(unique_num),
                    'eventName': eventName + str(datetime.datetime.now()),
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'eventType': 'STORAGE',
                    'notes': notes,
                    'performedBy': 'Engineer, RPS ASA' + str(unique_num),
                    'physicalLocation': 'Narragansett, RI',
                    'roomIdentification': '23',
                    'shelfIdentification': 'Cube 7-27',
                    'dataSource': str(unique_num),
                    'tense': None,
                    'assetUid': uid
                    }

        elif event_type == 'UNSPECIFIED':
            unique_num = randint(4500, 5500)
            eventStartTime = 1398049060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*2)
            input = {
                    'dataSource': str(unique_num),
                    'eventName': eventName + str(unique_num),
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'eventType': 'UNSPECIFIED',
                    'notes': str(datetime.datetime.now()) + ' ' + notes + str(unique_num),
                    'tense': 'UNKNOWN-' + str(unique_num),
                    'assetUid': uid
                    }
        else:
            message = 'Create event of type %s failed - unknown event type.' % event_type
            self.assertEquals(message, None)

        self.assertTrue(input is not None)
        string_input = get_event_input_as_string(input)
        self.assertTrue(string_input is not None)
        self.assertTrue(uid is not None)
        return uid, string_input

    # Data used to update different event types.
    def update_event_data(self, event_type, uid, rd, event_id, last_modified):
        """ Get event data for an update. (Note rd may not yet be defined for asset being posted to.)
        """
        debug = False
        if debug: print '\n debug -- update_event_data -- event_type: ', event_type
        self.assertTrue(uid is not None)
        self.assertTrue(event_type is not None)
        self.assertTrue(last_modified is not None)
        self.assertTrue(last_modified > 0)
        self.assertTrue(event_type in get_supported_event_types())
        self.assertTrue(event_id != -1)
        input = {}
        notes = 'Update new %s event for %s, associated with asset: %s)' % (event_type, rd, uid)
        unique_num = randint(1, 1000)
        unique_float = randint(1, 1000) * 100.0
        eventStartTime = 1398060000000 + unique_num
        eventStopTime = eventStartTime + unique_num * 5
        if rd is None:
            eventName = event_type + '-' + str(unique_num)
        else:
            eventName = rd
        if event_type == 'ACQUISITION':
            input = {
                      'purchasePrice': unique_float,
                      'purchaseDate': eventStartTime,
                      'deliveryDate': eventStopTime,
                      'purchasedBy': str(unique_num),
                      'vendorIdentification': None,
                      'vendorPointOfContact': None,
                      'receivedFromVendorBy': None,
                      'authorizationNumber': None,
                      'authorizationForPayment': None,
                      'invoiceNumber': str(unique_num),
                      'eventType': 'ACQUISITION',
                      'eventName': eventName,
                      'eventStartTime': eventStartTime,
                      'eventStopTime':  eventStopTime,
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
                    'status': 'operational',
                    'eventType': 'ASSET_STATUS',
                    'eventStartTime': 1398039160000,
                    'eventStopTime': 1405382410000,
                    'notes': notes,
                    'eventName': eventName,
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
                    'eventName': eventName,
                    'tense': 'UNKNOWN',
                    'dataSource': str(unique_float),
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
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
                    'eventName':  eventName,
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
                    'eventName': eventName,
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
                    'eventName': eventName,
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
                    'eventName': eventName,
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
            eventStopTime = 1453309000000 + (unique_num * 100)
            dataSource = 'Test case ' + str(datetime.datetime.now())
            input = {
                    'dataSource': dataSource,
                    'eventName': eventName + str(datetime.datetime.now()),
                    'eventStartTime': eventStartTime,
                    'eventStopTime': eventStopTime,
                    'eventType': 'UNSPECIFIED',
                    'notes': notes + str(datetime.datetime.now()),
                    'tense': 'UNKNOWN',
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        string_input = get_event_input_as_unicode(input, debug)
        self.assertTrue(input is not None)
        self.assertTrue('eventId' in input)
        self.assertTrue(input['eventId'] is not None)
        self.assertTrue(isinstance(input['eventId'], int))
        self.assertTrue(input['eventId'] > 0)
        self.assertTrue(uid is not None)
        return uid, string_input