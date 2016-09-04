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
        Verbose output sample:
         Processing event_types(8): ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

         Have some assets (521)

         Note: Number of loops to get three items of interest: 35

         ----- Mooring:
             mooring_id: 3066
             mooring_uid: N00265
             mooring_rd: CE01ISSP

         ----- Platform:
             platform_id: 474
             platform_uid: A00078
             platform_rd: CE05MOAS-GL311

         ----- Instrument:
             instrument_id: 1940
             instrument_uid: A00174
             instrument_rd: CE01ISSM-RID16-03-DOSTAD000

         -- Mooring Assets.

            Creating ACQUISITION event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55914 and lastModifiedTimestamp: 1472902292847

            Creating ASSET_STATUS event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55915 and lastModifiedTimestamp: 1472902293027

            Creating ATVENDOR event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55916 and lastModifiedTimestamp: 1472902293224

            Creating INTEGRATION event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55917 and lastModifiedTimestamp: 1472902293400

            Creating LOCATION event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55918 and lastModifiedTimestamp: 1472902293584

            Creating RETIREMENT event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55919 and lastModifiedTimestamp: 1472902293764

            Creating STORAGE event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55920 and lastModifiedTimestamp: 1472902293948

            Creating UNSPECIFIED event for mooring - asset id/uid/rd: 3066/N00265/CE01ISSP
                Created eventId: 55921 and lastModifiedTimestamp: 1472902294129

         -- Node Assets.

            Creating ACQUISITION event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55922 and lastModifiedTimestamp: 1472902294327

            Creating ASSET_STATUS event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55923 and lastModifiedTimestamp: 1472902294520

            Creating ATVENDOR event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55924 and lastModifiedTimestamp: 1472902294706

            Creating INTEGRATION event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55925 and lastModifiedTimestamp: 1472902294908

            Creating LOCATION event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55926 and lastModifiedTimestamp: 1472902295089

            Creating RETIREMENT event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55927 and lastModifiedTimestamp: 1472902295281

            Creating STORAGE event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55928 and lastModifiedTimestamp: 1472902295480

            Creating UNSPECIFIED event for platform - asset id/uid/rd: 474/A00078/CE05MOAS-GL311
                Created eventId: 55929 and lastModifiedTimestamp: 1472902295678

         -- Sensor Assets.

            Creating ACQUISITION event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55930 and lastModifiedTimestamp: 1472902295902

            Creating ASSET_STATUS event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55931 and lastModifiedTimestamp: 1472902296109

            Creating ATVENDOR event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55932 and lastModifiedTimestamp: 1472902296307

            Creating INTEGRATION event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55933 and lastModifiedTimestamp: 1472902296500

            Creating LOCATION event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55934 and lastModifiedTimestamp: 1472902296707

            Creating RETIREMENT event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55935 and lastModifiedTimestamp: 1472902296892

            Creating STORAGE event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55936 and lastModifiedTimestamp: 1472902297095

            Creating UNSPECIFIED event for instrument - asset id/uid/rd: 1940/A00174/CE01ISSM-RID16-03-DOSTAD000
                Created eventId: 55937 and lastModifiedTimestamp: 1472902297294
        """
        verbose = self.verbose
        event_types = get_supported_event_types()

        # Remove event_type value(s) which are not used in this test case.
        if 'CALIBRATION_DATA' in event_types:
            event_types.remove('CALIBRATION_DATA')
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')
        if 'DEPLOYMENT' in event_types:
            event_types.remove('DEPLOYMENT')

        if verbose: print '\n\nProcessing event_types(%d): %s' % (len(event_types), event_types)

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
            event_id, last_modified = self._create_event_type(event_type, uid, input)
            if verbose:
                print '\t\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

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
        if verbose: print '\n\nProcessing event_types(%d): %s' % (len(event_types), event_types)

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
            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)

            # Asset with uid 'A00056' is corrupted....do not use it...
            if asset_uid == 'A00056':
                # Get a different asset
                asset = assets[count+50]
                asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
                self.assertTrue(asset_uid != 'A00056')
            self.assertTrue(asset_uid != 'A00056')
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
            for event_type in event_types:
                if verbose:
                    print '\n ----- %s event.' % event_type
                    print '\n\t----- Creating %s event - asset id/uid/rd: %d/%s/%s' % (event_type, asset_id, asset_uid, rd)

                # Create an event
                uid, input = self.create_event_data(event_type, asset_uid, rd)
                if verbose: print '\n input: ', self.dump_dict(input, True)
                self.assertTrue(input is not None)
                self.assertTrue('assetUid' in input)
                self.assertTrue(input['assetUid'] is not None)
                if event_type == 'ACQUISITION':
                    self.assertTrue('purchasePrice' in input)
                    if input['purchasePrice'] is not None:
                        if debug: print '\n test:: Update %s event, attribute purchasePrice type: %r' % (event_type, type(input['purchasePrice']))
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
                if not isinstance(input['eventId'], int):
                    if verbose: print '\n debug -- test case -- event_id is not instance of int...'
                    input['eventId'] = int(str(input['eventId']))
                    self.assertTrue(isinstance(input['eventId'], int))
                update_event_id = self._update_event_type(event_type, input, event_id)
                if verbose: print '\n Updated eventId: %d ' % update_event_id
                self.assertTrue(event_id, update_event_id)

        if verbose: print '\n Note: Number of assets processed: %d ' % count
        if verbose: print '\n'

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
        event_types = get_supported_event_types()

        # Remove event_type value(s) which are not used in this test case.
        if 'CALIBRATION_DATA' in event_types:
            event_types.remove('CALIBRATION_DATA')
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')
        if 'DEPLOYMENT' in event_types:
            event_types.remove('DEPLOYMENT')

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
            if asset_uid == 'A00056':
                # Get a different asset
                asset = assets[count+50]
                asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
                self.assertTrue(asset_uid != 'A00056')

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
                self.assertTrue(input is not None)
                self.assertTrue('assetUid' in input)
                self.assertTrue(input['assetUid'] is not None)
                event_id, last_modified = self._create_event_type_requests(event_type, uid, input)
                if verbose: print '\n (requests) Created eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

                if verbose:
                    print '\n Now performing an UPDATE on event we just created...'
                # Update the one we just created
                uid, input = self.update_event_data(event_type, asset_uid, rd, event_id, last_modified)
                if not isinstance(input['eventId'], int):
                    if verbose: print '\n debug -- test case -- event_id is not instance of int...'
                    input['eventId'] = int(str(input['eventId']))
                    self.assertTrue(isinstance(input['eventId'], int))
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
            self.assertTrue(asset_id > 1)

            # Get asset uid
            self.assertTrue('uid' in asset)
            asset_uid = asset['uid']
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_uid)
            if debug: print '\n Have asset_uid: %s ' % asset_uid
            self.assertTrue(asset_uid is not None)

            # Get reference designator
            rd = get_rd_by_asset_id(asset_id)
            if debug: print '\n Have rd: %s ' % rd
            self.assertTrue(rd is not None)

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
        if debug:
            print '\n ===== Enter test::_create_event_type....'
            print '\n _event_type: ', _event_type
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
        self.assertTrue(isinstance(event_id, int))
        self.assertTrue(event_id > 0)
        self.assertTrue('lastModifiedTimestamp' in event)
        last_modified = event['lastModifiedTimestamp']
        self.assertTrue(last_modified is not None)
        if debug: print '\n ===== Exit test::_create_event_type....'
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
                if debug: print '\n Successful Event update data from POST: '
                self.dump_dict(response_data, debug)

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

    def dump_dict(self, dict, debug=False):
            if debug:
                print '\n dump dictionary(%d): %s' % (len(dict),
                                                          json.dumps(dict, indent=4, sort_keys=True))
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
        import datetime

        self.assertTrue(uid is not None)
        self.assertTrue(event_type is not None)
        self.assertTrue(rd is not None)
        input = {}
        unique_num = randint(1000, 2000)
        unique_float = randint(1, 1000) * 100.0
        notes = 'Create new %s event for %s, (assetUid: %s); unique number: %d' % (event_type, rd, uid, unique_num)
        if event_type == 'ACQUISITION':
            eventStartTime = 1398039060000 + (unique_num*10)
            purchasePrice =  unique_float

            input = {
                      'purchasePrice': None,
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
                      'eventName': rd,
                      'eventStartTime': eventStartTime,
                      'eventStopTime': None,
                      'notes': notes,
                      'tense': 'UNKNOWN',
                      'dataSource': 'Test case.' + str(datetime.datetime.now()),
                      'assetUid': uid
                      }
            """
            input = {
                      'purchasePrice': None,
                      'purchaseDate': None,
                      'deliveryDate': None,
                      'purchasedBy': None,
                      'vendorIdentification': None,
                      'vendorPointOfContact': None,
                      'receivedFromVendorBy': None,
                      'authorizationNumber': None,
                      'authorizationForPayment': None,
                      'invoiceNumber': None,
                      'eventType': 'ACQUISITION',
                      'eventName': rd,
                      'eventStartTime': None,
                      'eventStopTime': None,
                      'notes': None,
                      'tense': 'UNKNOWN',
                      'dataSource': None,
                      'assetUid': uid
                      }
            """
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
            unique_num = randint(301, 700)
            eventStartTime = 1398039060000 + unique_num
            eventStopTime = eventStartTime + (unique_num*3)
            input = {
                    'buildingName': 'Tower' + str(unique_num),
                    'eventName': rd,
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
        else:
            message = 'Create event of type %s failed - unknown event type.' % event_type
            self.assertEquals(message, None)

        self.assertTrue(input is not None)
        string_input = self.get_event_input_as_string(input)
        self.assertTrue(string_input is not None)
        self.assertTrue(uid is not None)
        return uid, string_input

    # Data used to update different event types.
    def update_event_data(self, event_type, uid, rd, event_id, last_modified):
        debug = False
        if debug: print '\n debug -- update_event_data -- event_type: ', event_type
        self.assertTrue(uid is not None)
        self.assertTrue(event_type is not None)
        self.assertTrue(rd is not None)
        self.assertTrue(last_modified is not None)
        self.assertTrue(last_modified > 0)
        self.assertTrue(event_type in get_supported_event_types())

        input = {}
        notes = 'Update new %s event for %s, associated with asset: %s)' % (event_type, rd, uid)
        unique_num = randint(1, 1000)
        unique_float = randint(1, 1000) * 100.0
        eventStartTime = 1398060000000 + unique_num
        eventStopTime = eventStartTime + unique_num * 5
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
        self.assertTrue(input is not None)
        self.assertTrue('eventId' in input)
        self.assertTrue(input['eventId'] is not None)
        self.assertTrue(isinstance(input['eventId'], int))
        self.assertTrue(input['eventId'] > 0)
        self.assertTrue(uid is not None)
        return uid, string_input

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