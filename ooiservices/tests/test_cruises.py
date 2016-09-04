#!/usr/bin/env python
"""
Specific testing for events routes

Routes:
[GET]   /cruises                                 # Get all cruises in inventory.
[GET]   /cruises/<int:id>                        # Get cruise by event id.
[GET]   /cruises/<string:cruise_id>              # Get cruise by unique cruise id.
[GET]   /cruises/<string:cruise_id>/deployments  # Get all deployments for a cruise.
[GET]   /cruises/deployment/<int:event_id>       # Get a specific deployment for a specific cruise.

"""
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from random import randint
from flask import (url_for)
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.uframe.event_tools import get_rd_by_asset_id
from ooiservices.app.uframe.cruise_tools import uniqueCruiseIdentifier_exists
from unittest import skipIf
import os
import requests

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
        suite.addTest(unittest.makeSuite(self.test_get_cruises()))
        return suite

    if __name__ == "__main__":
        unittest.main()
    """


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Test cases
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_cruises(self):
        """
        Exercise event routes:
        [GET]    /events/types           # Get all supported event types
        [GET]    /events/uid/<string:uid # Get events for asset with uid
        [GET]    /assets/<int:id>/events # Get all events for asset with asset id.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get cruises
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruises')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)
        self.assertTrue('cruises' in result)
        cruises = result['cruises']
        self.assertTrue(cruises is not None)
        self.assertTrue(cruises)
        self.assertTrue(isinstance(cruises, list))
        self.assertTrue(len(cruises) > 0)
        if verbose: print '\n -- len(assets): ', len(cruises)

        # Verify there cruise objects which are dictionaries
        index = 0
        cruise = cruises[index]
        self.assertTrue(cruise is not None)
        self.assertTrue(cruise)
        self.assertTrue(isinstance(cruise, dict))

        # Get asset_id
        self.assertTrue('uniqueCruiseIdentifier' in cruise)
        cruise_id = cruise['uniqueCruiseIdentifier']
        self.assertTrue(cruise_id is not None)
        self.assertTrue(cruise_id)

        self.assertTrue('eventId' in cruise)
        cruise_event_id = cruise['eventId']
        self.assertTrue(cruise_event_id is not None)
        self.assertTrue(cruise_event_id)

        # Get asset uid
        self.assertTrue('assetUid' not in cruise)
        #asset_uid = cruise['assetUid']
        #self.assertTrue(asset_uid is None)


        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get cruise by uniqueCruiseIdentifier
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruise_by_cruise_id', cruise_id=cruise_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get cruise by bad uniqueCruiseIdentifier
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruise_by_cruise_id', cruise_id='notgood')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(result)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get cruise by bad uniqueCruiseIdentifier
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruise_by_cruise_id', cruise_id='')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 404)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get cruise by eventId
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruise_by_event_id', event_id=cruise_event_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get cruise by bad eventId
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        bad_cruise_event_id = 12345
        url = url_for('uframe.get_cruise_by_event_id', event_id=999999)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched cruise(%d): %s' % (cruise_event_id, result)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get cruise by bad eventId
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruise_by_event_id', event_id=0)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched cruise(%d): %s' % (cruise_event_id, result)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get deployments list view for a cruise
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruise_deployments', cruise_id=cruise_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('cruise_deployments' in result)
        self.assertTrue(isinstance(result['cruise_deployments'], list))
        cruise_deployments = result['cruise_deployments']
        self.assertTrue(cruise_deployments is not None)
        self.assertTrue(isinstance(cruise_deployments, list))
        self.assertTrue(len(cruise_deployments) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get cruise deployments list view for a cruise
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_cruise_deployments', cruise_id='bad-cruise-id')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Process cruise deployment, validate fields
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertTrue(len(cruise_deployments) > 0)
        test_deployment = cruise_deployments[0]
        """
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
        """

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get deployment for a cruise.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get cruise deployment, get deployment eventId.
        self.assertTrue(len(cruise_deployments) > 0)
        cruise_deployment = cruise_deployments[0]
        self.assertTrue('eventId' in cruise_deployment)
        deployment_event_id = cruise_deployment['eventId']
        self.assertTrue(deployment_event_id is not None)
        #print '\n debug -- deployment_event_id: ', deployment_event_id

        #Get deployment using deployment eventId.
        url = url_for('uframe.get_deployment_by_event_id', event_id=deployment_event_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('deployment' in result)
        self.assertTrue(isinstance(result['deployment'], dict))
        deployment = result['deployment']
        self.assertTrue(deployment is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Process cruise deployment, validate fields
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertTrue(len(deployment) > 0)
        """
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
        """
        # Get supported event types (/events/edit_phase_values)
        url = url_for('uframe.get_edit_phase_values')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get deployment using deployment eventId.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployment_by_event_id', event_id=99999)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

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

        # Get unique cruise identifier.
        cruise_id, input = self.get_cruise_by_cruise_id(None, None)
        self.assertTrue(cruise_id is not None)
        self.assertTrue(input is not None)

        # Create cruise event.
        event_id, last_modified = self._create_event_type(event_type, None, input)
        if verbose:
            print '\n\tCreated eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)
            print '\n\tUnique cruise identifier: ', cruise_id
            print '\n\tNow performing an UPDATE on event we just created...'

        # Get data to update the newly created cruise.
        input = self.update_event_data_cruise(event_type, event_id, last_modified, cruise_id=cruise_id)

        # Refresh event id in string values.
        self.assertTrue(input is not None)
        self.assertTrue('eventId' in input)
        self.assertEquals(int(input['eventId']), event_id)
        self.assertTrue('assetUid' in input)
        if not isinstance(input['eventId'], int):
            input['eventId'] = int(str(input['eventId']))
            self.assertTrue(isinstance(input['eventId'], int))
        if verbose: print '\n\tUpdated eventId: %d' % input['eventId']

        # Update cruise event.
        update_event_id = self._update_event_type(event_type, input, event_id)
        if verbose: print '\n\tUpdated eventId: %d, cruise id: %s ' % (update_event_id, cruise_id)

        if verbose: print '\n'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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

                exists = uniqueCruiseIdentifier_exists(uniqueCruiseIdentifer)
                #print '\n ============> uniqueCruiseIdentifier %s exists?: %r' % (uniqueCruiseIdentifer, exists)
                if uniqueCruiseIdentifier_exists(uniqueCruiseIdentifer):
                    if debug: print '\n Do not have unique cruise identifier: ', uniqueCruiseIdentifer
                    continue
                else:
                    if debug: print '\n Have unique cruise identifier: ', uniqueCruiseIdentifer
                    cruise_id = uniqueCruiseIdentifer
                    break


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

    # Data used to create different event types.
    def create_event_data(self, event_type, uid, rd):
        input = {}
        unique_num = randint(1, 1000)
        unique_float = randint(1, 1000) * 100.0
        notes = 'Create new %s event for %s, (assetUid: %s); unique number: %d' % (event_type, rd, uid, unique_num)
        if event_type == 'CRUISE_INFO':
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

        self.assertTrue(input is not None)
        string_input = self.get_event_input_as_string(input)
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

