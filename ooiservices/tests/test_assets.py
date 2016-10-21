#!/usr/bin/env python
"""
Asset Management - Specific testing for assets routes

Routes:
[GET]    /assets                 # Get all assets from uframe and reformat for UI; get single asset reformatted for UI
                                 # def get_assets(use_min=False, normal_data=False, reset=False):
[GET]    /assets/types           # Get asset types used by those assets loaded into asset management display
[GET]    /assets/<int:id>        # Get asset
[GET]    /assets/<int:id>/events # Get all events for an asset; option 'type' parameter provided for one or more types.
"""
__author__ = 'Edna Donoughe'

import unittest
from ooiservices.tests.common_tools import (dump_dict, get_asset_input_as_string)

import json
from random import randint
from base64 import b64encode
from flask import url_for
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_asset_types, get_uframe_asset_type)
from ooiservices.app.uframe.uframe_tools import (uframe_get_asset_by_uid, uframe_get_remote_resource_by_id)
from ooiservices.app.uframe.asset_tools import (uframe_get_asset_by_id,  _get_asset)
from ooiservices.app.uframe.assets_validate_fields import (assets_validate_required_fields_are_provided,
                                                           asset_ui_get_required_fields_and_types,
                                                           convert_required_fields)
from copy import deepcopy
import datetime
from unittest import skipIf
import os
from ooiservices.app.uframe.config import get_url_info_resources
import requests

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class AssetsTestCase(unittest.TestCase):

    # enable verbose (during development and documentation) to get a list of sample
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
    #  Assets:
    #   test_get_assets
    #   test_create_assets
    #   test_update_assets
    #   test_update_string_assets
    #   test_update_asset_supported_asset_types
    #
    # Remote Resources:
    #   test_remote_resource_create
    #   test_remote_resource_update
    #   test_remote_resource_create_negative
    # * [proposed] test_negative_update_remote_resource
    # * [proposed] test_get_remote_resources (by id and by uid)
    # * [proposed] test_get_remote_resource (by remoteResourceId)
    # * (proposed) test/function delete_remote_resource (by remoteResourceId)
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_assets(self):
        """
        def get_assets(use_min=False, normal_data=False, reset=False):
        def get_asset(id):
        def get_asset_events(id):
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET assets
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_assets'), headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('assets' in results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are asset objects in a list
        assets = results['assets']
        self.assertTrue(assets is not None)
        self.assertTrue(isinstance(assets, list))

        # Verify there asset objects are dictionaries
        asset = assets[0]
        self.assertTrue(asset is not None)
        self.assertTrue(isinstance(asset, dict))

        # todo - Examine and verify asset fields provided by ooiservices route.

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get asset by id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertTrue('id' in asset)
        asset_id = asset['id']
        if debug: print '\n debug -- get asset (id: %d)' % asset_id
        response = self.client.get(url_for('uframe.get_asset', id=asset_id))
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        url = url_for('uframe.get_remote_resources_by_asset_id', asset_id=asset_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        url = url_for('uframe.get_remote_resources_by_asset_id', asset_id=9999999)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        url = url_for('uframe.get_remote_resource_by_resource_id', resource_id=9999999)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get asset by uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertTrue('uid' in asset)
        uid = asset['uid']
        self.assertTrue(uid is not None)
        url = url_for('uframe.get_ui_asset_by_uid', uid=uid)
        if debug:
            print '\n test -- uid: ', uid
            print '\n test -- url: ', url
        response = self.client.get(url, headers=headers)
        if debug:
            print '\n debug -- response.status_code: ', response.status_code
            #print '\n debug -- response.data: ', json.loads(response.data)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        url = url_for('uframe.get_remote_resources_by_asset_uid', asset_uid=uid)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        url = url_for('uframe.get_remote_resources_by_asset_uid', asset_uid='bad-uid')
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        remote_resource_data = {
            "@class": ".XRemoteResource",
            "dataSource": str(datetime.datetime.now()),
            "keywords": str(datetime.datetime.now()) + ',' + 'test',
            "label": "testresource",
            "remoteResourceId": -1,
            "resourceNumber": "1258.1548.58756.098",
            "status": "active",
            "url": None
            }
        url = url_for('uframe.create_remote_resource', asset_uid=uid)
        response = self.client.post(url, headers=headers, data=json.dumps(remote_resource_data))
        self.assertEquals(response.status_code, 201)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        remote_resource_data = {}
        url = url_for('uframe.create_remote_resource', asset_uid='bad-uid')
        response = self.client.post(url, headers=headers, data={})
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get asset by uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_ui_asset_by_uid', uid='bad-uid'), headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get asset by id (returns empty dict if asset not found, status code 200)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_asset', id=3030303030303), headers=headers)
        self.assertEquals(response.status_code, 409)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get events for asset by id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_asset_events', id=asset_id), headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('events' in result)
        self.assertTrue(isinstance(result['events'], dict))
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, dict))
        self.assertTrue(len(events_by_type) > 0)

        event_types = get_event_types()
        for event_type in events_by_type:
            self.assertTrue(event_type in event_types)
            if verbose: print '\n debug -- event_type: ', event_type
            self.assertTrue(isinstance(events_by_type[event_type], list))


        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get events for asset by id and parameter of event types (?type=)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        type_string = ''
        #print '\n event_types: ', get_event_types()
        some_event_types = get_event_types()
        for event_type in some_event_types:
            if event_type is not None:
                type_string += event_type + ','

        url = url_for('uframe.get_asset_events', id=asset_id)
        if type_string:
            #print '\n (before) type_string: ', type_string
            type_string = type_string.rstrip(',')
            #print '\n (after) type_string: ', type_string
            url += '?type='+ type_string
        #print '\n get_asset_events url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('events' in result)
        self.assertTrue(isinstance(result['events'], dict))
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, dict))
        self.assertTrue(len(events_by_type) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get events for asset by id and parameter of event types (?type=foo)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_asset_events', id=asset_id)
        type_string = 'foo'
        if type_string is not None:
            url += '?type='+ type_string
        #print '\n get_asset_events url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))


        # (Negative)
        response = self.client.get(url_for('uframe.get_asset_events', id=999999), headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        # (Negative)
        url = url_for('uframe.get_asset_events', id=0)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        # Get event types (/uframe/assets/types)
        url = url_for('uframe.get_asset_type')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        # Get event types (/uframe/assets/types)
        url = url_for('uframe.get_asset', id=0)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)

        # Get supported event types (/uframe/assets/types/supported)
        url = url_for('uframe.get_supported_asset_type')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        # Simple asset update tests
        asset_id = asset['id']
        if debug: print '\n asset_id: ', asset_id

        # Update asset with current contents
        string_asset = get_asset_input_as_string(asset)
        if debug:
            print '\n debug ********\n string_asset(%d): ' % len(string_asset)
            dump_dict(string_asset, debug)
        data = json.dumps(string_asset)
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        #print '\n debug -- response.status_code: ', response.status_code
        #if response.data:
        #    print '\n response.data: ', json.loads(response.data)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        self.assertTrue('asset' in results)
        self.assertTrue('id' in results['asset'])
        self.assertTrue(results['asset']['id'] is not None)

        # (Negative) Update asset with mismatching asset id value in data and url.
        if debug:
            print '\n debug ********\n string_asset(%d): ' % len(string_asset)
            dump_dict(string_asset, debug)
        data = json.dumps(string_asset)
        url = url_for('uframe.update_asset', id=asset_id+1)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        self.assertEquals(response.status_code, 400)

        # (Negative) Update asset with empty data.
        data = '{}'
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        self.assertEquals(response.status_code, 400)

        # (Negative) Update asset with bad data.
        data = '{"bad": "data"}'
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        self.assertEquals(response.status_code, 400)

        # (Negative) Update asset with no data.
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=None)
        self.assertEquals(response.status_code, 400)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # /assets parameter testing
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET assets
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url = url_for('uframe.get_assets')
        if verbose: print '\n url: ', base_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('assets' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        # Verify there are asset objects in a list - set assets, len_assets
        assets = results['assets']
        self.assertTrue(assets is not None)
        self.assertTrue(isinstance(assets, list))
        len_assets = len(assets)
        self.assertTrue(len_assets > 0)
        if debug: print '\n -- len_assets: ', len_assets

        #- - - - - - - - - - - - - - -
        # Parameter: min=true
        #- - - - - - - - - - - - - - -
        min_url = base_url + '?min=True'
        if verbose: print '\n url: ', min_url
        response = self.client.get(min_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('assets' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        # Check
        min_assets = results['assets']
        self.assertTrue(min_assets is not None)
        self.assertTrue(isinstance(min_assets, list))
        len_min_assets = len(min_assets)
        self.assertTrue(len_min_assets > 0)
        self.assertEquals(len_min_assets, len_assets)

        #- - - - - - - - - - - - - - -
        # Parameter: geoJSON=true
        #- - - - - - - - - - - - - - -
        geo_url = base_url + '?geoJSON=true'
        if verbose: print '\n url: ', geo_url
        response = self.client.get(geo_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('assets' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        # Check
        geo_assets = results['assets']
        self.assertTrue(geo_assets is not None)
        self.assertTrue(isinstance(geo_assets, list))
        len_geo_assets = len(geo_assets)
        self.assertTrue(len_geo_assets > 0)
        self.assertTrue(len_geo_assets < len_assets)

        #- - - - - - - - - - - - - - -
        # Parameter: sort=ref_des
        #- - - - - - - - - - - - - - -
        sort_url = base_url + '?sort=ref_des'
        if verbose: print '\n url: ', sort_url
        response = self.client.get(sort_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('assets' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        # Check
        sort_assets = results['assets']
        self.assertTrue(sort_assets is not None)
        self.assertTrue(isinstance(sort_assets, list))
        len_sort_assets = len(sort_assets)
        self.assertTrue(len_sort_assets > 0)
        self.assertEquals(len_sort_assets, len_assets)

        #- - - - - - - - - - - - - - -
        # Parameter: sort=NOTTHERE
        #- - - - - - - - - - - - - - -
        sort_url = base_url + '?sort=NOTTHERE'
        if verbose: print '\n url: ', sort_url
        response = self.client.get(sort_url, headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        #- - - - - - - - - - - - - - -
        # Parameter: ?startAt=100&count=1
        #- - - - - - - - - - - - - - -
        startat_url = base_url + '?startAt=100&count=1'
        if verbose: print '\n url: ', startat_url
        response = self.client.get(startat_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        if debug: print '\n -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        # Check
        startat_assets = results['assets']
        self.assertTrue(startat_assets is not None)
        self.assertTrue(isinstance(startat_assets, list))
        len_startat_assets = len(startat_assets)
        self.assertTrue(len_startat_assets > 0)
        self.assertEquals(len_startat_assets, 1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Parameter: ?startAt=100 but no parameter count
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        startat_url = base_url + '?startAt=100'
        if verbose: print '\n url: ', startat_url
        response = self.client.get(startat_url, headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        startat_url = base_url + '?count=100'
        if verbose: print '\n url: ', startat_url
        response = self.client.get(startat_url, headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Get supported asset edit phase values (/asset/edit_phase_values)
        url = url_for('uframe.get_asset_edit_phase_values')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        # Does reference designator have an asset available?
        url = url_for('uframe.has_asset', rd='CE01ISSM')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('available' in result)
        self.assertEquals(result['available'], True)

        # Does reference designator have an asset available?
        url = url_for('uframe.has_asset', rd='NO-ASSET')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('available' in result)
        self.assertEquals(result['available'], False)

    def test_create_assets(self):
        """
        Create an asset of each assetType.

        Sample verbose output:
        	Create notClassified asset.
                Created notClassified asset id/uid: 5236/ASA-TEST-8484515

            Create Sensor asset.
                Created Sensor asset id/uid: 5237/ASA-TEST-3661768

            Create Node asset.
                Created Node asset id/uid: 5238/ASA-TEST-1114548

            Create Mooring asset.
                Created Mooring asset id/uid: 5239/ASA-TEST-5512019

            Create Array asset.
                Created Array asset id/uid: 5240/ASA-TEST-8102504

        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get all event types.
        asset_types = get_supported_asset_types()
        asset_types.sort(reverse=True)
        self.assertTrue(isinstance(asset_types, list))
        self.assertTrue(len(asset_types) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create asset: get base UI data to create an asset
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #asset_types = ['Mooring'] #['notClassified']
        for asset_type in asset_types:
            if verbose: print '\n\tCreate %s asset.' % asset_type
            data = self.get_basic_UI_asset_data(asset_type)

            if verbose:
                print '\n Create asset data: ------------------------------------'
                dump_dict(data, verbose)

            string_data = get_asset_input_as_string(data)
            url = url_for('uframe.create_asset')
            if debug: print '\n\tcreate url: ', url
            keys = data.keys()
            keys.sort()
            #print '\n keys(%d): %s' % (len(keys), keys)
            data = json.dumps(string_data)
            response = self.client.post(url, headers=headers, data=data)
            if debug:
                print '\n\tdebug -- received response data on asset create...'
                print '\n\tresponse.status_code: ', response.status_code
                #if response.status_code != 201:
                #    if response.data:
                #        print '\n\tresponse.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 201)
            response_data = json.loads(response.data)
            if debug: print '\n\tresponse_data: ', response_data
            self.assertTrue('asset' in response_data)
            new_asset = response_data['asset']

            # Get asset id from create response
            asset_id = None
            if 'id' in new_asset:
                asset_id = new_asset['id']
            self.assertTrue(asset_id is not None)
            self.assertTrue(isinstance(asset_id, int))

            self.assertTrue('uid' in new_asset)
            asset_uid = new_asset['uid']
            if verbose: print '\t\tCreated %s asset id/uid: %d/%s' % (asset_type, asset_id, asset_uid)

        if verbose: print '\n '

    def test_create_assets_uid(self):
        """
        Create an asset of each assetType using uid containing spaces and or slashes.
        Currently not permitting spaces or slashes in uids for assets.

        Sample verbose output:

        Create assets with uid containing spaces and/or slashes.

        Create notClassified asset.

            response.status_code:  400

            response.data:  {u'message': u'Asset uid should not contain spaces or slashes, unable to create asset.', u'error': u'bad request'}

        Create Sensor asset.

            response.status_code:  400

            response.data:  {u'message': u'Asset uid should not contain spaces or slashes, unable to create asset.', u'error': u'bad request'}

        Create Node asset.

            response.status_code:  400

            response.data:  {u'message': u'Asset uid should not contain spaces or slashes, unable to create asset.', u'error': u'bad request'}

        Create Mooring asset.

            response.status_code:  400

            response.data:  {u'message': u'Asset uid should not contain spaces or slashes, unable to create asset.', u'error': u'bad request'}

        Create Array asset.

            response.status_code:  400

            response.data:  {u'message': u'Asset uid should not contain spaces or slashes, unable to create asset.', u'error': u'bad request'}
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get all event types.
        asset_types = get_supported_asset_types()
        asset_types.sort(reverse=True)
        self.assertTrue(isinstance(asset_types, list))
        self.assertTrue(len(asset_types) > 0)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create asset: get base UI data to create an asset
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #asset_types = ['notClassified']
        if verbose: print '\nCreate assets with uid containing spaces and/or slashes.'
        for asset_type in asset_types:
            if verbose: print '\nCreate %s asset. ' % asset_type
            # Create asset with space and or slash in uid
            data = self.get_basic_UI_asset_data(asset_type)
            data['uid'] += ' / something extra'
            string_data = get_asset_input_as_string(data)
            url = url_for('uframe.create_asset')
            if debug: print '\n\tcreate url: ', url
            keys = data.keys()
            keys.sort()
            #print '\n keys(%d): %s' % (len(keys), keys)
            data = json.dumps(string_data)
            response = self.client.post(url, headers=headers, data=data)
            if verbose:
                if response.status_code != 201:
                    print '\n\tresponse.status_code: ', response.status_code
                    if response.data:
                        print '\n\tresponse.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 400)
            response_data = json.loads(response.data)
            if debug: print '\n\tresponse_data: ', response_data

        if verbose: print '\n '

    # Important test...ok.
    def test_update_asset_supported_asset_types(self):
        """
        Test update asset for asset types:      ['Mooring', 'Node', 'Sensor']
        Currently don't support asset types:    ['notClassified', 'Array']
        """
        # Setup
        debug = self.debug
        verbose = self.verbose
        #content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Get some assets to update
        some_assets = self.get_some_assets()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update asset: For each asset type, do the following.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # a. Get an asset by id of a certain asset type, from some_assets.
        # b  Save selected update field value(s).
        # c. Optional. Get same asset by id from uframe
        # d. Modify asset fields from (a), change field(s) and save new values.
        # e. Issue /assets/id PUT to update using (d)
        # f. Get asset by id (a) again.
        # g. Compare field(s) modified

        # All asset types = ['Mooring', 'Node', 'Sensor', 'notClassified', 'Array']
        # Supported asset types = ['Mooring', 'Node', 'Sensor']
        asset_types = get_supported_asset_types()
        #asset_types = ['Mooring']
        for target_type in asset_types:
            #- - - - - - -
            # a. Get an asset by id of a certain asset type, from some_assets.
            #- - - - - - -
            if verbose: print '\n Processing \'%s\' asset update.' % target_type

            # Get required fields and field types for asset type on update.
            if verbose: print '\n\t Get required fields and field types for asset type %s.' % target_type
            required_fields, field_types = asset_ui_get_required_fields_and_types(target_type, 'update')
            self.assertTrue(required_fields is not None)
            self.assertTrue(field_types is not None)
            if debug: print '\n required fields for asset type \'%s\': %s' % (target_type, required_fields)

            # Get asset of target type.
            if verbose: print '\n\t Get asset of type %s.' % target_type
            asset = None
            for some_asset in some_assets:
                if get_uframe_asset_type(some_asset['assetType']) == target_type:
                    asset = some_asset
                    break
            self.assertTrue(asset is not None)
            self.assertTrue(isinstance(asset, dict))
            if verbose: print '\n\t Have asset of type %s.' % target_type

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

            # -- Get original data fields, save a copy.
            # Get original description
            self.assertTrue('assetInfo' in asset)
            self.assertTrue('description' in asset['assetInfo'])
            original_description = asset['assetInfo']['description']

            # Get original owner
            self.assertTrue('assetInfo' in asset)
            self.assertTrue('owner' in asset['assetInfo'])
            original_owner = asset['assetInfo']['owner']

            # Get original shelfLifeExpirationDate
            original_shelfLifeExpirationDate = asset['manufactureInfo']['shelfLifeExpirationDate']

            # Get original notes
            self.assertTrue('notes' in asset)
            original_notes = asset['notes']

            # Get original depthRating
            original_depthRating = asset['physicalInfo']['depthRating']

            # Get original shelfLifeExpirationDate
            original_purchasePrice = asset['purchaseAndDeliveryInfo']['purchasePrice']

            # Get original owner
            self.assertTrue('assetInfo' in asset)
            self.assertTrue('mindepth' in asset['assetInfo'])
            original_mindepth = asset['assetInfo']['mindepth']

            # Update field values to test asset update
            new_description = '*** This has been updated.'
            new_owner = '*** This is the updated owner.'
            new_shelfLifeExpirationDate = 1476128619000 #asset['lastModifiedTimestamp']
            new_depthRating = 50.0
            new_notes = 'Some new notes here.'
            new_purchasePrice = 25500.00
            new_mindepth = 135.0

            # Set asset fields (string, string, int, float)
            asset['assetInfo']['description'] = new_description
            asset['assetInfo']['owner'] = new_owner
            asset['manufactureInfo']['shelfLifeExpirationDate'] = new_shelfLifeExpirationDate
            asset['physicalInfo']['depthRating'] = new_depthRating
            asset['notes'] = new_notes
            asset['purchaseAndDeliveryInfo']['purchasePrice'] = new_purchasePrice
            # RESERVED. mindepth is reserved and cannot be modified; verify in fact asset not updated
            asset['assetInfo']['mindepth'] = new_mindepth

            # Verify all required fields are provided in ui asset.
            if verbose: print '\n\t Verifying asset of type \'%s\' has all required fields.' % target_type
            asset_fields = asset.keys()
            for field in required_fields:
                if debug: print '\n field: ', field
                self.assertTrue(field in asset_fields)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  Update asset
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            string_asset = asset.copy()
            data = json.dumps(string_asset)
            url = url_for('uframe.update_asset', id=asset_id)
            if verbose: print '\n\t ----- url: ', url
            response = self.client.put(url, headers=headers, data=data)
            results = json.loads(response.data)
            if debug:
                print '\n *********** debug -- results: ', results
                print '\n *********** debug -- response.status_code: ', response.status_code
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            self.assertTrue('asset' in results)
            self.assertTrue('id' in results['asset'])
            self.assertTrue(results['asset']['id'] is not None)

            # Check updated asset fields
            updated_asset = results['asset']
            self.assertTrue('assetInfo' in updated_asset)
            self.assertTrue('description' in updated_asset['assetInfo'])
            self.assertTrue('owner' in updated_asset['assetInfo'])
            self.assertEquals(new_owner, updated_asset['assetInfo']['owner'])
            self.assertEquals(new_description, updated_asset['assetInfo']['description'])
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            self.assertTrue('asset' in results)
            self.assertTrue('id' in results['asset'])
            self.assertTrue(results['asset']['id'] is not None)
            updated_asset = results['asset']
            self.assertTrue('assetInfo' in updated_asset)
            self.assertTrue('description' in updated_asset['assetInfo'])
            self.assertTrue('owner' in updated_asset['assetInfo'])
            self.assertEquals(new_owner, updated_asset['assetInfo']['owner'])
            self.assertEquals(new_description, updated_asset['assetInfo']['description'])

            self.assertTrue('manufactureInfo' in updated_asset)
            self.assertTrue('shelfLifeExpirationDate' in updated_asset['manufactureInfo'])
            self.assertEquals(new_shelfLifeExpirationDate, updated_asset['manufactureInfo']['shelfLifeExpirationDate'])

            self.assertTrue('physicalInfo' in updated_asset)
            self.assertTrue('depthRating' in updated_asset['physicalInfo'])
            self.assertEquals(new_depthRating, updated_asset['physicalInfo']['depthRating'])

            self.assertTrue('notes' in updated_asset)
            self.assertTrue(updated_asset['notes'] is not None)
            self.assertEquals(new_notes, updated_asset['notes'])

            self.assertTrue('purchaseAndDeliveryInfo' in updated_asset)
            self.assertTrue('purchasePrice' in updated_asset['purchaseAndDeliveryInfo'])
            self.assertTrue(updated_asset['purchaseAndDeliveryInfo']['purchasePrice'] is not None)
            self.assertEquals(original_mindepth, updated_asset['assetInfo']['mindepth'])
            if debug:
                print '\n original_description: ', original_description
                print '\n original_owner: ', original_owner
                print '\n original_notes: ', original_notes
                print '\n original_shelfLifeExpirationDate: ', original_shelfLifeExpirationDate
                print '\n original_depthRating: ', original_depthRating
                print '\n original_purchasePrice: ', original_purchasePrice
                print '\n original_mindepth: ', original_mindepth

                print '\n updated description: '
                self.display_ui_asset_information(updated_asset)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  Get asset from services, verify selected field for update have been updated and are returned.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            url = url_for('uframe.get_asset', id=asset_id)
            if verbose: print '\n\t ----- url: ', url
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            query_asset = json.loads(response.data)
            self.assertTrue(query_asset is not None)
            self.assertTrue(query_asset['assetInfo']['description'], updated_asset['assetInfo']['description'])
            self.assertTrue(query_asset['assetInfo']['owner'], updated_asset['assetInfo']['owner'])
            self.assertTrue(query_asset['notes'], updated_asset['notes'])
            self.assertTrue(query_asset['manufactureInfo']['shelfLifeExpirationDate'], updated_asset['manufactureInfo']['shelfLifeExpirationDate'])
            self.assertTrue(query_asset['physicalInfo']['depthRating'], updated_asset['physicalInfo']['depthRating'])
            self.assertTrue(query_asset['purchaseAndDeliveryInfo']['purchasePrice'], updated_asset['purchaseAndDeliveryInfo']['purchasePrice'])
            self.assertEquals(query_asset['assetInfo']['mindepth'], updated_asset['assetInfo']['mindepth'])

        if verbose: print '\n '

    def test_update_string_assets(self):
        """
        Test update mooring, node and sensor assets. Using string asset input to simulate UI data from jgrid.

        Outline:
        a. Set target asset type to mooring.
        b. Get mooring required fields and field types.
        c. Get a mooring asset (from some_assets).
        d. Save original asset (for reference and comparison later in script).
        e. String convert values (simulate UI jgrid output).
        f. Convert string asset.
        g. Modify selected fields and save.
        h. Verify all required fields are provided in asset.
        i. Validate fields and field types for asset.
        j. String convert values (simulate UI jgrid output).
        k. Update asset. (PUT)
        l. General check updated asset fields
        m. Get asset.
        n. Verify updated fields reflect updates.
        o. Update asset to original fields values. (PUT)
        p. Verify fields are the same as the original asset we started with.
        q. Create remoteResource and update asset.

        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get some assets to update
        some_assets = self.get_some_assets()

        asset_types = get_supported_asset_types()
        if verbose: print '\n\n Processing assets of types: %s ' % asset_types
        asset_types = ['Sensor']
        for asset_type in asset_types:
            if verbose: print '\n---------- Processing %s asset. ' % asset_type
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # a. Set target asset type to mooring.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t a. Set target asset type to %s.' % asset_type
            target_type = asset_type

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # b. Get mooring required fields and field types.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t b. Get %s required fields and field types.' % asset_type
            # Get required fields and field types for asset type on update.
            required_fields, field_types = asset_ui_get_required_fields_and_types(target_type, 'update')
            self.assertTrue(required_fields is not None)
            self.assertTrue(field_types is not None)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # c. Get a mooring asset (from some_assets).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t c. Get a %s asset (from some_assets).' % asset_type
            asset = None
            for some_asset in some_assets:
                if get_uframe_asset_type(some_asset['assetType']) == target_type:
                    asset = some_asset
                    break
            self.assertTrue(asset is not None)
            self.assertTrue(isinstance(asset, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # d. Save original asset (for reference and comparison later in script).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t d. Save original asset (for reference and comparison later in script).'
            original = deepcopy(asset)
            if debug: print '\n ---------- original asset (with original values): '
            self.display_ui_asset_information(original)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # e. String convert values (simulate UI jgrid output).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t e. String convert values (simulate UI jgrid output).'
            string_asset = get_asset_input_as_string(asset)
            if debug:
                print '\n ---------- asset: '
                dump_dict(string_asset, debug)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # f. Convert string asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t f. Convert string asset.'
            converted_asset = None
            try:
                converted_asset = convert_required_fields(target_type, string_asset, required_fields, field_types, 'update')
                if debug:
                    print '\n Converted asset:'
                    dump_dict(converted_asset, debug)
            except Exception as err:
                print '\n Exception: ', str(err)
            self.assertTrue(converted_asset is not None)

            # Get values from converted asset.
            # Get asset_id
            self.assertTrue('id' in converted_asset)
            asset_id = converted_asset['id']
            self.assertTrue(asset_id is not None)
            self.assertTrue(asset_id)

            # Get asset uid
            self.assertTrue('uid' in converted_asset)
            asset_uid = converted_asset['uid']
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_uid)

            # Save original converted asset.
            original_converted = deepcopy(converted_asset)
            if debug: print '\n ---------- converted asset (with original values): '
            self.display_ui_asset_information(original_converted)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # g. Modify selected fields and save.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t g. Modify selected fields and save.'
            # Update some field values to test asset update.
            new_description = original_converted['assetInfo']['description'] + ' ' + str(datetime.datetime.now())
            if original_converted['assetInfo']['owner'] is None:
                new_owner = ' ' + str(datetime.datetime.now())
            else:
                new_owner = original_converted['assetInfo']['owner'] + ' ' + str(datetime.datetime.now())
            new_shelfLifeExpirationDate = 1476128619000 + 1100
            if original_converted['physicalInfo']['depthRating'] is None:
                new_depthRating = 4.5
            else:
                new_depthRating = original_converted['physicalInfo']['depthRating'] + 4.5
            if original_converted['notes'] is None:
                new_notes = str(datetime.datetime.now())
            else:
                new_notes = original_converted['notes'] + ' ' + str(datetime.datetime.now())
            if original_converted['purchaseAndDeliveryInfo']['purchasePrice'] is None:
                new_purchasePrice = 1000.00
            else:
                new_purchasePrice = original_converted['purchaseAndDeliveryInfo']['purchasePrice'] + 1000.00
            new_mindepth = original_converted['assetInfo']['mindepth'] + 100.0

            # Modify converted_asset: Set asset fields (string, string, long, float, string, float, float)
            converted_asset['assetInfo']['description'] = new_description
            converted_asset['assetInfo']['owner'] = new_owner
            converted_asset['manufactureInfo']['shelfLifeExpirationDate'] = new_shelfLifeExpirationDate
            converted_asset['physicalInfo']['depthRating'] = new_depthRating
            converted_asset['notes'] = new_notes
            converted_asset['purchaseAndDeliveryInfo']['purchasePrice'] = new_purchasePrice
            # RESERVED. mindepth is reserved and cannot be modified; verify in fact asset not updated
            converted_asset['assetInfo']['mindepth'] = new_mindepth

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Verify all required fields are provided in asset and valid data types.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            try:
                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # h. Verify all required fields are provided in asset.
                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if verbose: print '\n\t h. Verify all required fields are provided in asset.'
                asset_fields = converted_asset.keys()
                for field in required_fields:
                    self.assertTrue(field in asset_fields)

                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # i. Validate fields and field types for asset.
                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if verbose: print '\n\t i. Validate fields and field types for asset.'
                assets_validate_required_fields_are_provided(target_type, converted_asset, 'update')
            except Exception as err:
                self.assertEquals('Exception: assets_validate_required_fields_are_provided for update', str(err))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #  Update asset - update converted asset with new values in multiple fields.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # j. String convert values (simulate UI jgrid output).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t j. String convert values (simulate UI jgrid output).'
            string_asset = get_asset_input_as_string(converted_asset)
            if debug:
                print '\n ---------- string_asset: '
                dump_dict(string_asset, debug)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # k. Update asset. (PUT)
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t k. Update asset. (PUT)'
            data = json.dumps(string_asset)
            self.assertTrue(asset_id is not None)
            url = url_for('uframe.update_asset', id=asset_id)
            response = self.client.put(url, headers=headers, data=data)
            if debug:
                print '\n response.status_code: ', response.status_code
                print '\n json.loads(response.data): ', json.loads(response.data)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            self.assertTrue('asset' in results)
            self.assertTrue('id' in results['asset'])
            self.assertTrue(results['asset']['id'] is not None)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # l. General check updated asset fields.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t l. General check updated asset fields.'
            updated_asset = results['asset']
            self.assertTrue('assetInfo' in updated_asset)
            self.assertTrue('description' in updated_asset['assetInfo'])
            self.assertEquals(new_description, updated_asset['assetInfo']['description'])
            self.assertTrue('owner' in updated_asset['assetInfo'])
            self.assertEquals(new_owner, updated_asset['assetInfo']['owner'])
            self.assertEquals(new_description, updated_asset['assetInfo']['description'])
            self.assertTrue('manufactureInfo' in updated_asset)
            self.assertTrue('shelfLifeExpirationDate' in updated_asset['manufactureInfo'])
            self.assertEquals(new_shelfLifeExpirationDate, updated_asset['manufactureInfo']['shelfLifeExpirationDate'])
            self.assertTrue('physicalInfo' in updated_asset)
            self.assertTrue('depthRating' in updated_asset['physicalInfo'])
            self.assertEquals(new_depthRating, updated_asset['physicalInfo']['depthRating'])
            self.assertTrue('notes' in updated_asset)
            self.assertTrue(updated_asset['notes'] is not None)
            self.assertEquals(new_notes, updated_asset['notes'])
            self.assertTrue('purchaseAndDeliveryInfo' in updated_asset)
            self.assertTrue('purchasePrice' in updated_asset['purchaseAndDeliveryInfo'])
            self.assertTrue(updated_asset['purchaseAndDeliveryInfo']['purchasePrice'] is not None)
            self.assertEquals(original['assetInfo']['mindepth'], updated_asset['assetInfo']['mindepth'])

            if debug: print '\n ---------- original asset (original values): '
            self.display_ui_asset_information(original, debug)

            if debug: print '\n ---------- updated description: '
            self.display_ui_asset_information(updated_asset, debug)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  m. Get asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t m. Get asset.'
            url = url_for('uframe.get_asset', id=asset_id)
            self.assertTrue(asset_id is not None)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            uframe_asset = json.loads(response.data)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # n. Verify updated fields reflect updates.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t n. Verify updated fields reflect updates.'
            self.assertTrue(uframe_asset is not None)
            self.assertTrue(uframe_asset['assetInfo']['description'], updated_asset['assetInfo']['description'])
            self.assertTrue(uframe_asset['assetInfo']['owner'], updated_asset['assetInfo']['owner'])
            self.assertTrue(uframe_asset['notes'], updated_asset['notes'])
            self.assertTrue(uframe_asset['manufactureInfo']['shelfLifeExpirationDate'], updated_asset['manufactureInfo']['shelfLifeExpirationDate'])
            self.assertTrue(uframe_asset['physicalInfo']['depthRating'], updated_asset['physicalInfo']['depthRating'])
            self.assertTrue(uframe_asset['purchaseAndDeliveryInfo']['purchasePrice'], updated_asset['purchaseAndDeliveryInfo']['purchasePrice'])
            self.assertEquals(uframe_asset['assetInfo']['mindepth'], original['assetInfo']['mindepth'])

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  o. Update asset to original fields values. (PUT)
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t o. Update asset to original fields values.'
            uframe_asset['assetInfo']['description'] = original['assetInfo']['description']
            uframe_asset['assetInfo']['owner'] = original['assetInfo']['owner']
            uframe_asset['manufactureInfo']['shelfLifeExpirationDate'] = original['manufactureInfo']['shelfLifeExpirationDate']
            uframe_asset['physicalInfo']['depthRating'] = original['physicalInfo']['depthRating']
            uframe_asset['notes'] = original['notes']
            uframe_asset['purchaseAndDeliveryInfo']['purchasePrice'] = original['purchaseAndDeliveryInfo']['purchasePrice']
            data = json.dumps(uframe_asset)
            self.assertTrue(asset_id is not None)
            url = url_for('uframe.update_asset', id=asset_id)
            response = self.client.put(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  p. Verify fields are the same as the original asset we started with.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t p. Verify fields are the same as the original asset we started with.'
            self.assertTrue(uframe_asset is not None)
            self.assertEquals(uframe_asset['assetInfo']['description'], original['assetInfo']['description'])
            self.assertEquals(uframe_asset['assetInfo']['owner'], original['assetInfo']['owner'])
            self.assertEquals(uframe_asset['notes'], original['notes'])
            self.assertEquals(uframe_asset['manufactureInfo']['shelfLifeExpirationDate'], original['manufactureInfo']['shelfLifeExpirationDate'])
            self.assertEquals(uframe_asset['physicalInfo']['depthRating'], original['physicalInfo']['depthRating'])
            self.assertEquals(uframe_asset['purchaseAndDeliveryInfo']['purchasePrice'], original['purchaseAndDeliveryInfo']['purchasePrice'])
            self.assertEquals(uframe_asset['assetInfo']['mindepth'], original['assetInfo']['mindepth'])

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  q. Create remoteResource and update asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t q. Create remoteResource and update asset.'
            self.assertTrue(asset_id is not None)
            self.assertTrue(asset_uid is not None)
            remote_resource_id = self._create_remote_resource(asset_uid, asset_id)

        if verbose: print '\n '

    def _test_remote_resource_create(self):
        """
        Test create remote resource.

        Sample of Verbose output:

         a. Get some assets, select an asset.

         Creating create resources for Array asset.

             b. Get uframe Sensor asset by uid ('A01030').

             c. Original Number of remoteResources:  2

             d. Create remoteResource and update asset.

             e. Get updated Sensor asset by uid ('A01030').
                 1. asset_by_uid - Number of remoteResources:  3

             f. Get updated Sensor asset by id ('198').
                 1. asset_by_id - Number of remoteResources:  3

         Creating create resources for Mooring asset.

             b. Get uframe Sensor asset by uid ('A01030').

             c. Original Number of remoteResources:  3

             d. Create remoteResource and update asset.

             e. Get updated Sensor asset by uid ('A01030').
                 1. asset_by_uid - Number of remoteResources:  4

             f. Get updated Sensor asset by id ('198').
                 1. asset_by_id - Number of remoteResources:  4

         Creating create resources for Node asset.

             b. Get uframe notClassified asset by uid ('ATAPL-67612-00105').

             c. Original Number of remoteResources:  2

             d. Create remoteResource and update asset.

             e. Get updated notClassified asset by uid ('ATAPL-67612-00105').
                 1. asset_by_uid - Number of remoteResources:  3

             f. Get updated notClassified asset by id ('4129').
                 1. asset_by_id - Number of remoteResources:  3

         Creating create resources for Sensor asset.

             b. Get uframe Sensor asset by uid ('A01555').

             c. Original Number of remoteResources:  4

             d. Create remoteResource and update asset.

             e. Get updated Sensor asset by uid ('A01555').
                 1. asset_by_uid - Number of remoteResources:  5

             f. Get updated Sensor asset by id ('2834').
                 1. asset_by_id - Number of remoteResources:  5

         Creating create resources for notClassified asset.

             b. Get uframe Sensor asset by uid ('A00952').

             c. Original Number of remoteResources:  1

             d. Create remoteResource and update asset.

             e. Get updated Sensor asset by uid ('A00952').
                 1. asset_by_uid - Number of remoteResources:  2

             f. Get updated Sensor asset by id ('3274').
                 1. asset_by_id - Number of remoteResources:  2

        """
        debug = self.debug
        verbose =  self.verbose
        debug_dump = self.debug
        headers = self.get_api_headers('admin', 'test')

        if verbose: print '\n\n a. Get some assets, select an asset.'
        # Get some assets to update
        some_assets = self.get_some_assets()

        asset_types = get_supported_asset_types()
        if verbose: print '\n Create remote resources for asset types: ', asset_types
        for asset_type in asset_types:
            if verbose: print '\n Creating remote resources for %s asset.' % asset_type
            an_asset = None
            for item in some_assets:
                if item['assetType'] == asset_type:
                    an_asset = item
                    break

            self.assertTrue(an_asset is not None)

            # Add remote resource to an asset
            small_random_int = randint(3,10)
            asset_index = int(len(some_assets)/small_random_int)
            #print '\n debug -- asset_index: ', asset_index

            ui_asset = some_assets[asset_index]
            self.assertTrue(ui_asset is not None)
            self.assertTrue(ui_asset)
            if debug_dump:
                print '\n Original asset content: '
                dump_dict(ui_asset, debug)

            # Get values from converted asset.
            # Get asset_id
            self.assertTrue('id' in ui_asset)
            asset_id = ui_asset['id']
            self.assertTrue(asset_id is not None)
            self.assertTrue(asset_id)

            # Get asset uid
            self.assertTrue('uid' in ui_asset)
            asset_uid = ui_asset['uid']
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_uid)

            # Get asset type
            self.assertTrue('assetType' in ui_asset)
            asset_type = ui_asset['assetType']
            self.assertTrue(asset_type is not None)
            self.assertTrue(asset_type)
            self.assertTrue(asset_type in get_supported_asset_types())

            if verbose: print '\n\t b. Get uframe %s asset by uid (\'%s\').' % (asset_type, asset_uid)
            if debug: print '\n --- get uframe %s asset uid: %s' % (asset_type, asset_uid)
            url = url_for('uframe.get_ui_asset_by_uid', uid=asset_uid)
            if debug: print '\n --- url: ', url
            response = self.client.get(url, headers=headers)
            if debug: print '\n --- response.status_code: ', response.status_code
            self.assertEquals(response.status_code, 200)
            asset = json.loads(response.data)
            if debug_dump:
                print '\n uframe asset contents:'
                dump_dict(asset, debug_dump)

            # Determine current number of remoteResources in asset
            self.assertTrue('remoteResources' in asset)
            self.assertTrue(asset['remoteResources'] is not None)
            self.assertTrue(isinstance(asset['remoteResources'], list))
            remoteResources = asset['remoteResources']
            number_remoteResources = len(remoteResources)
            if verbose: print'\n\t c. Original Number of remoteResources: ', number_remoteResources

            if verbose: print '\n\t d. Create remoteResource and update asset.'
            self.assertTrue(asset_id is not None)
            self.assertTrue(asset_uid is not None)
            remote_resource_id = self._create_remote_resource(asset_uid, asset_id)

            if verbose: print '\n\t e. Get updated %s asset by uid (\'%s\').' % (asset_type, asset_uid)
            url = url_for('uframe.get_ui_asset_by_uid', uid=asset_uid)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            asset_by_uid = json.loads(response.data)

            # Determine current number of remoteResources in asset_by_uid
            self.assertTrue('remoteResources' in asset_by_uid)
            self.assertTrue(asset_by_uid['remoteResources'] is not None)
            self.assertTrue(isinstance(asset_by_uid['remoteResources'], list))
            remoteResources_asset_by_uid = asset_by_uid['remoteResources']
            number_remoteResources_asset_by_uid = len(remoteResources_asset_by_uid)
            if verbose: print'\t\t 1. asset_by_uid - Number of remoteResources: ', number_remoteResources_asset_by_uid
            self.assertEquals(number_remoteResources+1, number_remoteResources_asset_by_uid)

            if verbose: print '\n\t f. Get updated %s asset by id (\'%d\').' % (asset_type, asset_id)
            url = url_for('uframe.get_asset', id=asset_id)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            asset_by_id = json.loads(response.data)

            # Determine current number of remoteResources in asset_by_id
            self.assertTrue('remoteResources' in asset_by_id)
            self.assertTrue(asset_by_id['remoteResources'] is not None)
            self.assertTrue(isinstance(asset_by_id['remoteResources'], list))
            remoteResources_asset_by_id = asset_by_id['remoteResources']
            number_remoteResources_asset_by_id = len(remoteResources_asset_by_id)
            if verbose: print'\t\t 1. asset_by_id - Number of remoteResources: ', number_remoteResources_asset_by_id
            self.assertEquals(number_remoteResources+1, number_remoteResources_asset_by_id)

            self.assertEquals(number_remoteResources_asset_by_uid, number_remoteResources_asset_by_id)
            #self.assertEquals(asset_by_id['lastModifiedTimestamp'], asset_by_uid['lastModifiedTimestamp'])

            # Get remote resource by remote resource id.
            url = url_for('uframe.get_remote_resource_by_resource_id', resource_id=remote_resource_id)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)
            if debug:
                print '\n result: ', result
            self.assertTrue('remote_resource' in result)

            remote_resource = result['remote_resource']
            remote_resource_org = remote_resource.copy()
            if debug:
                print '\n debug -- (before) remote resource, id: ', remote_resource_id
                dump_dict(remote_resource, debug)
            """
            # Remote resource
            {
              "dataSource": null,
              "keywords": null,
              "label": "testresource",
              "lastModifiedTimestamp": 1473509980510,
              "remoteResourceId": 4688,
              "resourceNumber": "1258.1548.58756.098",
              "status": "active",
              "url": null
            }
            """
            # Set data fields...
            dataSource = 'Manual - vendor website.' + str(datetime.datetime.now())
            keywords = "'SEABIRD', 'SBE', 'vendor', 'ph', 'sensor', 'carousel'"
            label = 'Seabird website'
            resourceNumber = None
            status = 'active'

            #_url = 'http://www.seabird.com/ph-sensor-calibration'
            remote_resource['dataSource'] = dataSource
            remote_resource['keywords'] = keywords
            remote_resource['label'] = label
            remote_resource['resourceNumber'] = resourceNumber
            remote_resource['status'] = status
            remote_resource['url'] = 'http://www.seabird.com/ph-sensor-calibration'

            if debug:
                print '\n debug -- (after) remote resource, id: ', remote_resource_id
                dump_dict(remote_resource, debug)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Update remote resource by remote resource id.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Response info on update:
            # {u'message': u'Element updated successfully.', u'id': 5481, u'statusCode': u'OK'}
            url = url_for('uframe.update_remote_resource', asset_uid=asset_uid)
            if debug: print '\n debug -- url: ', url
            data = json.dumps(remote_resource)

            response = self.client.put(url, data=data, headers=headers)
            if response.status_code != 200:
                print '\n remote resource update '
                print '\n status code: ', response.status_code
                print '\n content: ', json.loads(response.data)

            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)

            # Get remote resource by remote resource id.
            url = url_for('uframe.get_remote_resource_by_resource_id', resource_id=remote_resource_id)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)
            if debug: print '\n result: ', result
            self.assertTrue('remote_resource' in result)
            self.assertTrue('lastModifiedTimestamp' in result['remote_resource'])
            last_modified = result['remote_resource']['lastModifiedTimestamp']
            # - - - - - - - - - - - - -

            # (Negative) Add negative test for int rather than string in status.
            remote_resource['lastModifiedTimestamp'] = last_modified
            negative_status = 999
            remote_resource['status'] = negative_status
            url = url_for('uframe.update_remote_resource', asset_uid=asset_uid)
            if debug: print '\n debug -- url: ', url
            data = json.dumps(remote_resource)
            if debug:
                print '\n update_remote_resource: '
                dump_dict(data, debug)
            response = self.client.put(url, data=data, headers=headers)
            if debug:
                if response.status_code == 400:
                    print '\n (Negative) remote resource update '
                    print '\n status code: ', response.status_code
                    print '\n content: ', json.loads(response.data)

            self.assertEquals(response.status_code, 400)
            result = json.loads(response.data)
            # Get remote resource by remote resource id.
            url = url_for('uframe.get_remote_resource_by_resource_id', resource_id=remote_resource_id)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)
            if debug: print '\n result: ', result
            self.assertTrue('remote_resource' in result)
            self.assertTrue('lastModifiedTimestamp' in result['remote_resource'])
            last_modified = result['remote_resource']['lastModifiedTimestamp']
            # - - - - - - - - - - - - -

            # (Negative) Add keywords as a list and not string that has comma delimited values.
            remote_resource['lastModifiedTimestamp'] = last_modified
            status = 'active'
            negative_keywords = ['SEABIRD', 'SBE', 'vendor', 'ph', 'sensor', 'carousel']
            remote_resource['status'] = status
            remote_resource['keywords'] = negative_keywords
            url = url_for('uframe.update_remote_resource', asset_uid=asset_uid)
            if debug: print '\n debug -- url: ', url
            data = json.dumps(remote_resource)
            if debug:
                print '\n update_remote_resource: '
                dump_dict(data, debug)
            response = self.client.put(url, data=data, headers=headers)
            if debug:
                if response.status_code == 400:
                    print '\n (Negative) remote resource update '
                    print '\n status code: ', response.status_code
                    print '\n content: ', json.loads(response.data)
            self.assertEquals(response.status_code, 400)
            result = json.loads(response.data)
            # Get remote resource by remote resource id.
            url = url_for('uframe.get_remote_resource_by_resource_id', resource_id=remote_resource_id)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)
            if debug: print '\n result: ', result
            self.assertTrue('remote_resource' in result)
            self.assertTrue('lastModifiedTimestamp' in result['remote_resource'])
            last_modified = result['remote_resource']['lastModifiedTimestamp']
            # - - - - - - - - - - - - -

            # (Positive) Add keywords as a malformed string that has comma delimited values. (Actually a 200)
            remote_resource['lastModifiedTimestamp'] = last_modified
            status = 'active'
            negative_keywords = "'SEABIRD',,, SBE 'ph', 'sensor', 'carousel'"
            remote_resource['status'] = status
            remote_resource['keywords'] = negative_keywords
            url = url_for('uframe.update_remote_resource', asset_uid=asset_uid)
            if debug: print '\n debug -- url: ', url
            data = json.dumps(remote_resource)
            if debug:
                print '\n update_remote_resource: '
                dump_dict(data, debug)
            response = self.client.put(url, data=data, headers=headers)
            if response.status_code != 200:
                print '\n (Positive) remote resource update '
                print '\n status code: ', response.status_code
                print '\n content: ', json.loads(response.data)
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.data)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Delete remote resource by remote resource id.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            """
            url_base, timeout, timeout_read = get_url_info_resources()
            url = '/'.join([url_base, str(remote_resource_id)])
            print '\n debug -- delete remote resource id: %d' % remote_resource_id
            print '\n debug -- delete remote resource url: %s' % url
            response = requests.delete(url, timeout=(timeout, timeout_read), headers=headers)
            self.assertEquals(response.status_code, 200)
            print '\n debug -- response.status_code: ', response.status_code
            if response.content:
                print '\n debug -- response.content: ', json.loads(response.content)
            """
            if debug: print '\n debug -- result: ', result

        if verbose: print '\n '

    def test_update_assets(self):
        """
        Test asset update for array, mooring, node and sensor assets.
        Using string asset input to simulate UI data from jgrid.

        Outline:
        a. Set target asset type to as asset type (for instance mooring).
        b. Get mooring required fields and field types.
        c. Get a mooring asset (from some_assets).
        d. Save original asset (for reference and comparison later in script).
        e. Modify selected fields and save.
        f. Verify all required fields are provided in asset.
        g. Validate fields and field types for asset.
        h. Update asset. (PUT)
        i. General check updated asset fields
        j. Get asset.
        k. Verify updated fields reflect updates.
        l. Update asset to original fields values. (PUT)
        m. Verify fields are the same as the original asset we started with.
        n. Create remoteResource and update asset.

        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get some assets to update
        some_assets = self.get_some_assets()
        asset_types = get_supported_asset_types()
        asset_types = ['Node']
        if verbose: print '\n\n Processing assets of types: %s ' % asset_types
        for asset_type in asset_types:
            if verbose: print '\n---------- Processing %s asset. ' % asset_type
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # a. Set target asset type to mooring.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t a. Set target asset type to %s.' % asset_type
            target_type = asset_type

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # b. Get mooring required fields and field types.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t b. Get %s required fields and field types.' % asset_type
            # Get required fields and field types for asset type on update.
            required_fields, field_types = asset_ui_get_required_fields_and_types(target_type, 'update')
            self.assertTrue(required_fields is not None)
            self.assertTrue(field_types is not None)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # c. Get a mooring asset (from some_assets).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t c. Get a %s asset (from some_assets).' % asset_type
            asset = None
            for some_asset in some_assets:
                if get_uframe_asset_type(some_asset['assetType']) == target_type:
                    asset = some_asset
                    break
            self.assertTrue(asset is not None)
            self.assertTrue(isinstance(asset, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # d. Save original asset (for reference and comparison later in script).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t d. Save original asset (for reference and comparison later in script).'
            original = deepcopy(asset)
            if debug: print '\n ---------- original asset (with original values): '
            self.display_ui_asset_information(original)

            # Get values from converted asset.
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

            # Save original converted asset.
            original_converted = deepcopy(asset)
            asset_copy = deepcopy(asset)
            if debug:
                print '\n ---------- converted asset (with original values): '
            self.display_ui_asset_information(original_converted)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # e. Modify selected fields and save.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t e. Modify selected fields and save.'

            """
            self.assertTrue('tense' in original_converted)
            if debug: print '\n test -- original_converted[tense]: ', original_converted['tense']
            if not original_converted['tense'] or original_converted is not None:
                asset_copy['tense'] = 'UNKNOWN'
            """

            # Update some field values to test asset update.
            new_description = original_converted['assetInfo']['description'] + ' ' + str(datetime.datetime.now())
            if original_converted['assetInfo']['owner'] is None:
                new_owner = str(datetime.datetime.now())
            else:
                new_owner = original_converted['assetInfo']['owner'] + ' ' + str(datetime.datetime.now())
            new_shelfLifeExpirationDate = 1476128619000 + 1100
            if original_converted['physicalInfo']['depthRating'] is None:
                new_depthRating = 4.5
            else:
                new_depthRating = original_converted['physicalInfo']['depthRating'] + 4.5
            if original_converted['notes'] is None:
                new_notes = str(datetime.datetime.now())
            else:
                new_notes = original_converted['notes'] + ' ' + str(datetime.datetime.now())
            if original_converted['purchaseAndDeliveryInfo']['purchasePrice'] is None:
                new_purchasePrice = 1000.00
            else:
                new_purchasePrice = original_converted['purchaseAndDeliveryInfo']['purchasePrice'] + 1000.00
            new_mindepth = original_converted['assetInfo']['mindepth'] + 100.0

            # Modify converted_asset: Set asset fields (string, string, long, float, string, float, float)
            asset_copy['assetInfo']['description'] = new_description
            asset_copy['assetInfo']['owner'] = new_owner
            asset_copy['manufactureInfo']['shelfLifeExpirationDate'] = new_shelfLifeExpirationDate
            asset_copy['physicalInfo']['depthRating'] = new_depthRating
            asset_copy['notes'] = new_notes
            asset_copy['purchaseAndDeliveryInfo']['purchasePrice'] = new_purchasePrice
            # RESERVED. mindepth is reserved and cannot be modified; verify in fact asset not updated
            asset_copy['assetInfo']['mindepth'] = new_mindepth

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Verify all required fields are provided in asset and valid data types.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            try:
                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # f. Verify all required fields are provided in asset.
                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if verbose: print '\n\t f. Verify all required fields are provided in asset.'
                asset_fields = asset_copy.keys()
                for field in required_fields:
                    self.assertTrue(field in asset_fields)

                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # g. Validate fields and field types for asset.
                #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if verbose: print '\n\t g. Validate fields and field types for asset.'
                assets_validate_required_fields_are_provided(target_type, asset_copy, 'update')
            except Exception as err:
                self.assertEquals('Exception: assets_validate_required_fields_are_provided for update', str(err))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #  Update asset - update converted asset with new values in multiple fields.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # h. Update asset. (PUT)
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t h. Update asset. (PUT)'
            if debug:
                print '\n debug -- data to update %s asset: ' % asset_type
                dump_dict(asset_copy, debug)
            data = json.dumps(asset_copy)
            url = url_for('uframe.update_asset', id=asset_id)
            response = self.client.put(url, headers=headers, data=data)
            if debug:
                print '\n response.status_code: ', response.status_code
                print '\n json.loads(response.data): ', json.loads(response.data)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            self.assertTrue('asset' in results)
            self.assertTrue('id' in results['asset'])
            self.assertTrue(results['asset']['id'] is not None)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # i. General check updated asset fields.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t i. General check updated asset fields.'
            updated_asset = results['asset']
            self.assertTrue('assetInfo' in updated_asset)
            self.assertTrue('description' in updated_asset['assetInfo'])
            self.assertEquals(new_description, updated_asset['assetInfo']['description'])
            self.assertTrue('owner' in updated_asset['assetInfo'])
            self.assertEquals(new_owner, updated_asset['assetInfo']['owner'])
            self.assertEquals(new_description, updated_asset['assetInfo']['description'])
            self.assertTrue('manufactureInfo' in updated_asset)
            self.assertTrue('shelfLifeExpirationDate' in updated_asset['manufactureInfo'])
            self.assertEquals(new_shelfLifeExpirationDate, updated_asset['manufactureInfo']['shelfLifeExpirationDate'])
            self.assertTrue('physicalInfo' in updated_asset)
            self.assertTrue('depthRating' in updated_asset['physicalInfo'])
            self.assertEquals(new_depthRating, updated_asset['physicalInfo']['depthRating'])
            self.assertTrue('notes' in updated_asset)
            self.assertTrue(updated_asset['notes'] is not None)
            self.assertEquals(new_notes, updated_asset['notes'])
            self.assertTrue('purchaseAndDeliveryInfo' in updated_asset)
            self.assertTrue('purchasePrice' in updated_asset['purchaseAndDeliveryInfo'])
            self.assertTrue(updated_asset['purchaseAndDeliveryInfo']['purchasePrice'] is not None)
            self.assertEquals(original['assetInfo']['mindepth'], updated_asset['assetInfo']['mindepth'])

            if debug: print '\n ---------- original asset (original values): '
            self.display_ui_asset_information(original, debug)

            if debug: print '\n ---------- updated description: '
            self.display_ui_asset_information(updated_asset, debug)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  j. Get asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t j. Get asset.'
            url = url_for('uframe.get_asset', id=asset_id)
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            uframe_asset = json.loads(response.data)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # k. Verify updated fields reflect updates.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t k. Verify updated fields reflect updates.'
            self.assertTrue(uframe_asset is not None)
            self.assertTrue(uframe_asset['assetInfo']['description'], updated_asset['assetInfo']['description'])
            self.assertTrue(uframe_asset['assetInfo']['owner'], updated_asset['assetInfo']['owner'])
            self.assertTrue(uframe_asset['notes'], updated_asset['notes'])
            self.assertTrue(uframe_asset['manufactureInfo']['shelfLifeExpirationDate'], updated_asset['manufactureInfo']['shelfLifeExpirationDate'])
            self.assertTrue(uframe_asset['physicalInfo']['depthRating'], updated_asset['physicalInfo']['depthRating'])
            self.assertTrue(uframe_asset['purchaseAndDeliveryInfo']['purchasePrice'], updated_asset['purchaseAndDeliveryInfo']['purchasePrice'])
            self.assertEquals(uframe_asset['assetInfo']['mindepth'], original['assetInfo']['mindepth'])

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  l. Update asset to original fields values.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t l. Update asset to original fields values.'
            uframe_asset['assetInfo']['description'] = original['assetInfo']['description']
            uframe_asset['assetInfo']['owner'] = original['assetInfo']['owner']
            uframe_asset['manufactureInfo']['shelfLifeExpirationDate'] = original['manufactureInfo']['shelfLifeExpirationDate']
            uframe_asset['physicalInfo']['depthRating'] = original['physicalInfo']['depthRating']
            uframe_asset['notes'] = original['notes']
            uframe_asset['purchaseAndDeliveryInfo']['purchasePrice'] = original['purchaseAndDeliveryInfo']['purchasePrice']
            data = json.dumps(uframe_asset)
            url = url_for('uframe.update_asset', id=asset_id)
            response = self.client.put(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  m. Verify fields are the same as the original asset we started with.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t m. Verify fields are the same as the original asset we started with.'
            self.assertTrue(uframe_asset is not None)
            self.assertEquals(uframe_asset['assetInfo']['description'], original['assetInfo']['description'])
            self.assertEquals(uframe_asset['assetInfo']['owner'], original['assetInfo']['owner'])
            self.assertEquals(uframe_asset['notes'], original['notes'])
            self.assertEquals(uframe_asset['manufactureInfo']['shelfLifeExpirationDate'], original['manufactureInfo']['shelfLifeExpirationDate'])
            self.assertEquals(uframe_asset['physicalInfo']['depthRating'], original['physicalInfo']['depthRating'])
            self.assertEquals(uframe_asset['purchaseAndDeliveryInfo']['purchasePrice'], original['purchaseAndDeliveryInfo']['purchasePrice'])
            self.assertEquals(uframe_asset['assetInfo']['mindepth'], original['assetInfo']['mindepth'])

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  n. Create remoteResource and update asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t n. Create a remoteResource and update asset.'
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_id is not None)
            remote_resource_id = self._create_remote_resource(asset_uid, asset_id)
            self.assertTrue(remote_resource_id is not None)

        if verbose: print '\n '

    def _test_remote_resource_create_negative(self):
        """
        Negative test cases for remote resources; property of assets.

        remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",
            "uid": asset_uid,
            "url": None
            }

        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get some assets to update
        some_assets = self.get_some_assets()
        asset_types = get_supported_asset_types()
        if verbose: print '\n\n Processing assets of types: %s ' % asset_types
        for asset_type in asset_types:
            if verbose: print '\n---------- Processing %s asset. ' % asset_type
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # a. Set target asset type to mooring.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t a. Set target asset type to %s.' % asset_type
            target_type = asset_type

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # b. Get mooring required fields and field types.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t b. Get %s required fields and field types.' % asset_type
            # Get required fields and field types for asset type on update.
            required_fields, field_types = asset_ui_get_required_fields_and_types(target_type, 'update')
            self.assertTrue(required_fields is not None)
            self.assertTrue(field_types is not None)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # c. Get a mooring asset (from some_assets).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t c. Get a %s asset (from some_assets).' % asset_type
            asset = None
            for some_asset in some_assets:
                if get_uframe_asset_type(some_asset['assetType']) == target_type:
                    asset = some_asset
                    break
            self.assertTrue(asset is not None)
            self.assertTrue(isinstance(asset, dict))

            # Get values from converted asset.
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
            if debug: print '\n Test 1a...'
            # Create some bad data...
            remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",

            "url": None
            }
            #"uid": 'bad_uid',
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid='bad_uid')
            #if debug: print '\n ----- url: ', url
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 400)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            """
            if debug: print '\n Test 1b...'
            # Create some bad data...
            remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",
            "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=None)
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            #self.assertTrue('remote_resource' in results)
            """
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 2...'
            # Create some data...
            remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label": "testresource",
            "resourceNumber": None,
            "status": "active",
            "url": None
            }
            # "uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            if debug: print '\n debug -- response.status_code: ', response.status_code
            if debug: print '\n debug -- response.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 201)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            #self.assertTrue('remote_resource' in results)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 3...'
            # Create some bad data...
            remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label": None,
            "resourceNumber": None,
            "status": None,
            "url": None
            }
            #"uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            if debug:
                print '\n debug -- response.status_code: ', response.status_code
                print '\n debug -- response.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 201)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            #self.assertTrue('remote_resource' in results)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 4...'
            # Create some bad data...
            # missing "dataSource": None,
            remote_resource_data = {
            "keywords": None,
            "label": None,
            "resourceNumber": None,
            "status": None,
            "url": None
            }
            # "uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 5...'
            # Negative test: list value, instead of string, in datasource.
            #
            remote_resource_data = {
                "dataSource": [],
                "keywords": None,
                "label": None,
                "resourceNumber": None,
                "status": None,

                "url": None
            }
            # "uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 6...'
            # Positive test...
            #
            remote_resource_data = {
                "dataSource": 'datasource information here....',
                "keywords": None,
                "label": None,
                "resourceNumber": None,
                "status": None,
                "url": None
            }
            # "uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 201)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            self.assertTrue('remote_resource' in results)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 7...'
            # Positive test...extra fields ignored
            #
            remote_resource_data = {
                "bad": "field",
                "dataSource": None,
                "keywords": None,
                "label": None,
                "resourceNumber": None,
                "status": None,
                "url": None
            }
            # "uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 201)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            self.assertTrue('remote_resource' in results)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 8...'
            # Negative test: int value, instead of string, in datasource.
            #
            remote_resource_data = {
                "dataSource": 8,
                "keywords": None,
                "label": None,
                "resourceNumber": None,
                "status": None,
                "url": None
            }
            # "uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 9...'
            # Negative test: int value, instead of string, in datasource.
            #
            remote_resource_data = {
                "dataSource": True,
                "keywords": None,
                "label": None,
                "resourceNumber": None,
                "status": None,
                "url": None
            }
            #"uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            if debug: print '\n debug -- response.data: ', response.data
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 10...'
            # Negative test: int value, instead of string, in datasource.
            #
            remote_resource_data = {
                "dataSource": {},
                "keywords": None,
                "label": None,
                "resourceNumber": None,
                "status": None,
                "url": None
            }
            # "uid": asset_uid,
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
            response = self.client.post(url, headers=headers, data=data)
            if debug: print '\n debug -- response.data: ', response.data
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

        if verbose: print '\n '

    def _test_remote_resource_update(self):
        """
        Test update mooring, node and sensor assets. Using string asset input to simulate UI data from jgrid.

        Outline:
        a. Set target asset type to mooring.
        b. Get mooring required fields and field types.
        c. Get a mooring asset (from some_assets).

        remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",
            "uid": asset_uid,
            "url": None
            }

        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get some assets to update
        some_assets = self.get_some_assets()
        asset_types = get_supported_asset_types()
        if verbose: print '\n\n Processing assets of types: %s ' % asset_types
        #asset_types = ['Node']
        for asset_type in asset_types:
            if verbose: print '\n---------- Processing %s asset. ' % asset_type
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # a. Set target asset type to mooring.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t a. Set target asset type to %s.' % asset_type
            target_type = asset_type

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # b. Get mooring required fields and field types.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t b. Get %s required fields and field types.' % asset_type
            # Get required fields and field types for asset type on update.
            required_fields, field_types = asset_ui_get_required_fields_and_types(target_type, 'update')
            self.assertTrue(required_fields is not None)
            self.assertTrue(field_types is not None)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # c. Get asset with remote resources. (from some_assets).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t c. Get a %s asset (from some_assets).' % asset_type
            asset = None
            remote_resources = []
            for some_asset in some_assets:
                if get_uframe_asset_type(some_asset['assetType']) == target_type:
                    if 'remoteResources' in some_asset:
                        if len(some_asset['remoteResources']) > 0:
                            asset = deepcopy(some_asset)
                            remote_resources = asset['remoteResources']
                            break
            self.assertTrue(asset is not None)
            self.assertTrue(isinstance(asset, dict))
            self.assertTrue(len(remote_resources) > 0)

            # Get values from converted asset.
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

            if verbose:
                print '\n\t%s asset id/uid (%d/%s) with %d remote resources.' % (asset_type, asset_id, asset_uid,
                                                                                len(remote_resources))

            # Get remoteResources, select an remoteResource to update.
            self.assertTrue('remoteResources' in asset)
            remote_resource_data = remote_resources[0]
            self.assertTrue(remote_resource_data is not None)
            self.assertTrue('remoteResourceId' in remote_resource_data)
            resource_id = None
            if 'remoteResourceId' in remote_resource_data:
                resource_id = remote_resource_data['remoteResourceId']
            self.assertTrue(resource_id is not None)
            if debug:
                print '\n Working with remote resource id: ', resource_id
                print '\n remote resource id: '
                dump_dict(remote_resource_data, debug)
            cached_last_modified = remote_resource_data['lastModifiedTimestamp']
            self.assertTrue(cached_last_modified is not None)
            if debug: print '\n\t cached lastModifiedTimestamp: ', remote_resource_data['lastModifiedTimestamp']

            # Get remote resource directly from uframe by id
            uframe_remote_resource = uframe_get_remote_resource_by_id(resource_id)
            uframe_last_modified = uframe_remote_resource['lastModifiedTimestamp']
            self.assertTrue(uframe_remote_resource is not None)
            self.assertTrue(uframe_last_modified is not None)
            if verbose: print '\n debug -- uframe_last_modified: ', uframe_last_modified
            self.assertEquals(cached_last_modified, uframe_last_modified)

            # Determine number pf remote resources in uframe for this asset.
            uframe_asset_uid = uframe_get_asset_by_uid(asset_uid)
            uframe_remote_resources_uid = uframe_asset_uid['remoteResources']
            if debug:  print '\n debug -- uframe_remote_resources (uid): ', len(uframe_remote_resources_uid)
            rr_uid = None
            for rr in uframe_remote_resources_uid:
                if rr['remoteResourceId'] == resource_id:
                    rr_uid = rr['lastModifiedTimestamp']
                    break
            if verbose: print '\n debug -- rr_uid last modified: ', rr_uid

            # Determine number pf remote resources in uframe for this asset.
            uframe_asset_id = uframe_get_asset_by_id(asset_id)
            uframe_remote_resources_id = uframe_asset_id['remoteResources']
            if debug: print '\n debug -- uframe_remote_resources(id): ', len(uframe_remote_resources_id)
            rr_id = None
            for rr in uframe_remote_resources_id:
                if rr['remoteResourceId'] == resource_id:
                    rr_id = rr['lastModifiedTimestamp']
                    break
            if verbose: print '\n debug -- rr_id last modified: ', rr_id

            if verbose:
                print '\n Original remote resource: '
                dump_dict(remote_resource_data, verbose)

            #remote_resource_data['uid'] = asset_uid
            remote_resource_data['label'] = 'this label has been updated ' + str(datetime.datetime.now())
            resource_id = remote_resource_data['remoteResourceId']
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            """
            remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource updated",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",
            "uid": asset_uid,
            "url": None,
            "lastModifiedTimeStamp": asset['lastModifiedTimestamp'],
            "remoteResourceId": asset['remoteResourceId']
            }
            """
            #self.assertEquals(len(remote_resource_data), 8)

            if verbose:
                print '\n Remote resource with updated value: '
                dump_dict(remote_resource_data, verbose)

            if debug: print '\n UPDATE - Remote resource... '
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.update_remote_resource', asset_uid=asset_uid)
            if debug: print '\n ----- url: ', url
            response = self.client.put(url, data=data, headers=headers)
            if debug:
                print '\n debug -- response.status_code: ', response.status_code
                print '\n debug -- response.content: ', json.loads(response.data)
            self.assertEquals(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertTrue('remote_resource' in response_data)
            self.assertTrue('remoteResourceId' in response_data['remote_resource'])
            id = None
            if 'remoteResourceId' in response_data['remote_resource']:
                id = response_data['remote_resource']['remoteResourceId']
            self.assertTrue(id is not None)
            updated_resource_from_uframe = uframe_get_remote_resource_by_id(id)
            self.assertTrue(updated_resource_from_uframe is not None)

            # Get asset from cache and check lastModifiedTimestamp
            cached_asset_updated = _get_asset(asset_id)
            cached_asset_updated_lastModifiedTimestamp = None
            if cached_asset_updated:
                if debug: print '\n number of [cached] remote resources: ', len(cached_asset_updated['remoteResources'])
                for res in cached_asset_updated['remoteResources']:
                    if res['remoteResourceId'] == resource_id:
                        if debug: print '\n cached_asset_updated remote resource ts: ', res['lastModifiedTimestamp']
                        cached_asset_updated_lastModifiedTimestamp = res['lastModifiedTimestamp']
            self.assertTrue(cached_asset_updated_lastModifiedTimestamp is not None)

            self.assertEquals(updated_resource_from_uframe['lastModifiedTimestamp'], cached_asset_updated_lastModifiedTimestamp)
            if verbose: print '\n The end...'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_basic_UI_asset_data(self, type):
        # "calibration": [],
        debug = False
        uid_suffix = str(randint(100,1000))
        unique_int = randint(1000,5000)
        description = type + '-' + str(unique_int)
        purchasePrice = float(randint(10000,20000) + unique_int)
        deliveryOrderNumber = 'Order No. TEST-' + uid_suffix + '-' + description
        small_int = randint(1,10)
        data = {
          'events': [],
          'assetInfo': {
            'array': 'Coastal Pioneer',
            'assembly': 'Oregon Inshore Surface Mooring - Multi-Function Node',
            'asset_name': 'CP03ISSM-00003-DCL37',
            'description': description,
            'longName': 'Coastal Pioneer Oregon Inshore Surface Mooring - Multi-Function Node - Data Concentrator Logger (DCL)',
            'maxdepth': 0,
            'mindepth': 0,
            'name': 'Coastal Pioneer Oregon Inshore Surface Mooring - Multi-Function Node - Data Concentrator Logger (DCL)',
            'owner': 'Test ' + uid_suffix,
            'type': 'Sensor'
          },
          'assetType': 'Mooring',
          'latitude': 40.3595,
          'longitude': -70.885,
          'orbitRadius': 0.0,
          'dataSource': '/home/asadev/uframes/uframe_ooi_20160727_90f4540c71d3fc4f6a4fc8262903c92c722535ee/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv',
          'deployment_number': '3',
          'deployment_numbers': [
            3
          ],
          'depth': 0.0,
          'manufactureInfo': {
            'firmwareVersion': str(small_int),
            'manufacturer': 'WHOI',
            'modelNumber': 'DCL',
            'serialNumber': 'CP03ISSM-00003-DCL37',
            'shelfLifeExpirationDate': None,
            'softwareVersion': str(small_int*2)
          },
          'mobile': False,
          'notes': None,
          'partData': {
            'institutionPropertyNumber': None,
            'institutionPurchaseOrderNumber': None,
            'ooiPartNumber': None,
            'ooiPropertyNumber': None,
            'ooiSerialNumber': None
          },
          'physicalInfo': {
            'depthRating': None,
            'height': -1.0,
            'length': -1.0,
            'powerRequirements': None,
            'weight': -1.0,
            'width': -1.0
          },
          'purchaseAndDeliveryInfo': {
            'deliveryDate': 1358812800000,
            'deliveryOrderNumber': deliveryOrderNumber,
            'purchaseDate': 1358812800000,
            'purchasePrice': purchasePrice
          },
          'ref_des': 'CP03ISSM-MFD37-00-DCLENG000',
          'remoteResources': [],
          'tense': 'PAST',
          'uid': 'ASA-TEST2-' + uid_suffix + str(unique_int),
          'editPhase': 'EDIT'
        }

        self.assertTrue(type in get_supported_asset_types())
        if type in get_supported_asset_types():
            data['assetType'] = type
        if type == 'Sensor':
            if debug: print '\n debug -- Adding calibration since type is %s' % type
            data['calibration'] = []
        return data

    def display_ui_asset_information(self, asset, debug=False):

        if debug:
            print '\n\t asset uid: ', asset['uid']
            print '\n\t asset id: ', asset['id']
            print '\n\t asset description: ', asset['assetInfo']['description']
            print '\n\t asset owner: ', asset['assetInfo']['owner']
            print '\n\t asset notes: ', asset['notes']
            print '\n\t asset shelfLifeExpirationDate: ', asset['manufactureInfo']['shelfLifeExpirationDate']
            print '\n\t asset depthRating: ', asset['physicalInfo']['depthRating']
            print '\n\t asset purchasePrice: ', asset['purchaseAndDeliveryInfo']['purchasePrice']
            print '\n\t asset mindepth (reserved): ', asset['assetInfo']['mindepth']

    def _create_remote_resource(self, asset_uid, asset_id):
        """
        Add a remote resource to asset identified as asset_uid.

        # Sample for reference:
        {
        "@class": ".XRemoteResource",
        "dataSource": null,
        "keywords": null,
        "label": "testresource",
        "lastModifiedTimestamp": 1472138644728,
        "remoteResourceId": 8446,
        "resourceNumber": "1258.1548.58756.098",
        "status": "active",
        "url": null
        }
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')
        if debug: print '\n test -----------------------\n test -- Entered Create remote resource [_create_remote_resource]...'

        # Get number of remote resources before adding one
        # Get asset from uframe directly to verify number of remote resources.
        self.assertTrue(asset_id is not None)
        self.assertTrue(asset_uid is not None)
        asset = uframe_get_asset_by_id(asset_id)
        self.assertTrue(asset is not None)
        self.assertTrue(asset)
        self.assertTrue('remoteResources' in asset)
        self.assertTrue(asset['remoteResources'] is not None)
        remote_resources = asset['remoteResources']
        len_remote_resources = len(remote_resources)
        if verbose: print '\n\tNumber of resources in uframe asset: ', len_remote_resources
        self.assertTrue(len_remote_resources >= 0)

        #if debug: print '\n debug ********\n asset to be updated (%d): %s' % (len(asset),
        #                                                  json.dumps(asset, indent=4, sort_keys=True))
        """
        {
        "@class": ".XRemoteResource",
        "dataSource": null,
        "keywords": null,
        "label": "testresource",
        "lastModifiedTimestamp": 1472138644728,
        "remoteResourceId": 8446,
        "resourceNumber": "1258.1548.58756.098",
        "status": "active",
        "url": null
        }
        """
        remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",
            "url": None
            }
        # "uid": asset_uid,
        if debug:
            print '\n\tdebug remote_resource: '
            dump_dict(remote_resource_data, debug)

        data = json.dumps(remote_resource_data)
        url = url_for('uframe.create_remote_resource', asset_uid=asset_uid)
        if debug: print '\n ----- url: ', url
        response = self.client.post(url, headers=headers, data=data)
        if debug: print '\n debug -- response.data: ', json.loads(response.data)
        if response.status_code != 201:
            print '\n debug -- response.status_code: ', json.loads(response.status_code)
            print '\n debug -- response.data: ', json.loads(response.data)
        self.assertEquals(response.status_code, 201)
        results = json.loads(response.data)
        if debug:
            print '\n debug -- Created remote resource: response_data: ', results
            #print '\n debug -- Created remote_resource: '
            #dump_dict(results, debug)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        self.assertTrue('remote_resource' in results)

        # Check updated asset contents
        if debug: print '\n\t Check contents of newly created remote resource...'
        remote_resource = results['remote_resource']
        self.assertTrue('@class' in remote_resource)
        self.assertTrue('label' in remote_resource)
        self.assertTrue('status' in remote_resource)
        self.assertTrue('resourceNumber' in remote_resource)
        self.assertTrue('url' in remote_resource)
        self.assertTrue('dataSource' in remote_resource)
        self.assertTrue('keywords' in remote_resource)
        self.assertTrue('lastModifiedTimestamp' in remote_resource)
        self.assertTrue('remoteResourceId' in remote_resource)

        self.assertTrue(remote_resource['@class'] is not None)
        self.assertTrue(remote_resource['lastModifiedTimestamp'] is not None)
        self.assertTrue(remote_resource['remoteResourceId'] is not None)
        self.assertTrue(remote_resource['resourceNumber'] is not None)
        remote_resource_id = remote_resource['remoteResourceId']
        self.assertTrue(remote_resource_id is not None)
        self.assertTrue(remote_resource_id > 0)

        # Get asset from uframe directly to verify number of remote resources.
        if debug:
            print '\n\t --------------------------------------------'
            print '\n\tGetting asset by asset_id: ', asset_id
        updated_asset = uframe_get_asset_by_id(asset_id)
        #if debug:
        #    dump_dict(updated_asset, debug)

        if debug:
            print '\n\t --------------------------------------------'
            print '\n\tGetting asset by asset_uid: ', asset_uid
        updated_asset = uframe_get_asset_by_uid(asset_uid)
        #if debug:
        #    dump_dict(updated_asset, debug)
        self.assertTrue(updated_asset is not None)
        self.assertTrue(updated_asset)
        self.assertTrue('remoteResources' in updated_asset)
        self.assertTrue(updated_asset['remoteResources'] is not None)
        if not updated_asset['remoteResources']:
            print '\n\t****** No remote resources in updated asset! '
        remote_resources = updated_asset['remoteResources']
        len_update_remote_resources = len(remote_resources)
        if verbose: print '\n\tNumber of resources in updated uframe asset (by uid): ', len_update_remote_resources

        # Get asset from uframe directly to verify number of remote resources.
        if debug: print '\n\tGetting asset by asset_uid: ', asset_uid
        updated_asset = uframe_get_asset_by_uid(asset_uid)
        self.assertTrue(updated_asset is not None)
        self.assertTrue(updated_asset)
        self.assertTrue('remoteResources' in updated_asset)
        self.assertTrue(updated_asset['remoteResources'] is not None)
        if not updated_asset['remoteResources']:
            print '\n\t****** No remote resources in updated asset! '
        remote_resources = updated_asset['remoteResources']
        len_update_remote_resources = len(remote_resources)
        if verbose: print '\n\tNumber of resources in updated uframe asset (by id): ', len_update_remote_resources

        self.assertTrue(len_update_remote_resources > 0)
        found_updated_resource = False
        for resource in remote_resources:
            if resource['remoteResourceId'] == remote_resource_id:
                found_updated_resource = True
                break
        self.assertEquals(found_updated_resource, True)
        if debug: print '\n\ttest -------------\n test -- Exit Create remote resource [_create_remote_resource]...'

        self.assertTrue(len_remote_resources < len_update_remote_resources)
        self.assertEquals(len_remote_resources+1, len_update_remote_resources)
        return remote_resource_id

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

    '''
    def get_asset_input_as_string(self, asset):
        """ Take input from UI and present all values as string type. Leaves nulls.
        Handles one dict level down. Used to simulate UI data from jgrid submit.
        """
        debug = False
        try:
            if debug: print '\n debug -- get_asset_input_as_string'
            string_asset = asset.copy()
            keys = asset.keys()
            for key in keys:
                if asset[key] is not None:
                    if not isinstance(asset[key], dict):
                        if not isinstance(asset[key], list):
                            string_asset[key] = str(asset[key])
                        else:
                            # Have a list to process...
                            list_value = asset[key]
                            if not list_value:
                                string_asset[key] = str(asset[key])
                            else:
                                if len(list_value) > 0:
                                    if not isinstance(list_value[0], dict):
                                        string_asset[key] = str(asset[key])
                                    else:
                                        #process list of dicts - stringize dict contents...
                                        #print '\n debug -- Have a list of dictionaries, field: ', key
                                        converted_list_value = []
                                        #print '\n debug -- len(converted_list_value): ', len(list_value)
                                        for remote in list_value:
                                            if debug: print '\n debug -- remote: ', remote
                                            tmp_dict = remote.copy()
                                            for k,v in tmp_dict.iteritems():
                                                #print '\n remote convert k: ', k
                                                if v is not None:
                                                    if not isinstance(v, dict):
                                                        remote[k] = str(v)
                                            if debug: print '\n debug -- converted remote: ', remote
                                            converted_list_value.append(remote)
                                        string_asset[key] = str(converted_list_value)

                    else:
                        if debug: print '\n Field is dict: ', key
                        tmp_dict = asset[key].copy()
                        for k,v in tmp_dict.iteritems():
                            if v is not None:
                                if not isinstance(v, dict):
                                    string_asset[key][k] = str(v)
            if debug:
                print '\n debug ********get_asset_input_as_string ***********'
                print '\n string_asset(%d): %s' % (len(string_asset),
                                                          json.dumps(string_asset, indent=4, sort_keys=True))

            return string_asset

        except Exception as err:
            if debug: print '\n exception: ', str(err)
            raise
    '''
