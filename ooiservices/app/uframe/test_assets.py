#!/usr/bin/env python
'''
Specific testing for assets routes

Routes:
[GET]    /assets                 # Get all assets from uframe and reformat for UI; get single asset reformatted for UI
                                 # def get_assets(use_min=False, normal_data=False, reset=False):
[GET]    /assets/types           # [dup] Get asset types used by those assets loaded into asset management display
[GET]    /assets/types/used      # [dup] Get asset types used by those assets loaded into asset management display
[GET]    /assets/types/uframe    # List of all asset types supported by uframe.
[GET]    /assets/<int:id>        # Get asset
[GET]    /assets/<int:id>/events # Get all events for an asset; option 'type' parameter provided toget one or more types.
[DELETE] /asset                  # Deprecated.
'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_asset_types)
from ooiservices.app.uframe.assets_validate_fields import (assets_validate_required_fields_are_provided,
                                                           asset_ui_get_required_fields_and_types,
                                                           convert_required_fields)
from ooiservices.app.uframe.asset_tools import (uframe_get_asset_by_id, uframe_get_asset_by_uid)

from copy import deepcopy
import datetime
from unittest import skipIf
import os


'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''

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
#   test_get_assets
# * test_create_asset
#   test_update_asset_supported_asset_types
#   _test_update_string_asset_sensor
#   _test_update_asset_sensor
#   test_update_string_asset_mooring
#   test_update_string_asset_node
#
#   test_update_string_assets
#   test_update_assets
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
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are asset objects in a list
        assets = results['assets']
        self.assertTrue(assets is not None)
        self.assertTrue(isinstance(assets, list))
        if debug: print '\n -- len(assets): ', len(assets)

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
        response = self.client.get(url_for('uframe.get_asset', id=asset_id), headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get asset by uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertTrue('uid' in asset)
        uid = asset['uid']
        response = self.client.get(url_for('uframe.get_asset_by_uid', uid=uid), headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get asset by uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_asset_by_uid', uid='baduid'), headers=headers)
        self.assertEquals(response.status_code, 409)
        result = json.loads(response.data)
        #print '\n -- bad asset by uid (%s): %s' % (uid, result)
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
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('events' in result)
        self.assertTrue(isinstance(result['events'], dict))
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, dict))
        self.assertTrue(len(events_by_type) > 0)

        if debug: print '\n -- len(result): ', len(result)
        event_types = get_event_types()
        for event_type in events_by_type:
            self.assertTrue(event_type in event_types)
            if verbose: print '\n debug -- event_type: ', event_type
            self.assertTrue(isinstance(events_by_type[event_type], list))

        # (Negative)
        response = self.client.get(url_for('uframe.get_asset_events', id=999999), headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        #print '\n -- bad get asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)

        # (Negative)
        url = url_for('uframe.get_asset_events', id=0)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        #print '\n -- bad get asset(%d): %s' % (asset_id, result)
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

        # Update asset wit current contents
        string_asset = self.get_asset_input_as_string(asset)
        if debug:
            print '\n debug ********\n string_asset(%d): %s' % (len(string_asset),
                                                          json.dumps(string_asset, indent=4, sort_keys=True))
        data = json.dumps(string_asset)
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))
        self.assertTrue('asset' in results)
        self.assertTrue('id' in results['asset'])
        self.assertTrue(results['asset']['id'] is not None)

        # (Negative) Update asset with mismatching asset id value in data and url.
        if debug:
            print '\n debug ********\n string_asset(%d): %s' % (len(string_asset),
                                                          json.dumps(string_asset, indent=4, sort_keys=True))
        data = json.dumps(string_asset)
        url = url_for('uframe.update_asset', id=asset_id+1)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        #print '\n debug -- (400) response_data: ',json.loads(response.data)
        self.assertEquals(response.status_code, 400)

        # (Negative) Update asset with empty data.
        data = '{}'
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        #print '\n debug -- empty data (400) response_data: ',json.loads(response.data)
        self.assertEquals(response.status_code, 400)

        # (Negative) Update asset with bad data.
        data = '{"bad": "data"}'
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=data)
        #print '\n debug -- bad data (400) response_data: ',json.loads(response.data)
        self.assertEquals(response.status_code, 400)

        # (Negative) Update asset with no data.
        url = url_for('uframe.update_asset', id=asset_id)
        if verbose: print '\n\t ----- url: ', url
        response = self.client.put(url, headers=headers, data=None)
        #print '\n debug -- bad data (400) response_data: ',json.loads(response.data)
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
        if debug: print '\n -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        startat_url = base_url + '?count=100'
        if verbose: print '\n url: ', startat_url
        response = self.client.get(startat_url, headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

    def _test_create_asset(self):
        """
        There are five (5) kinds of assets, identified by the assetType and defined by data structures.

        Example of a base asset:
            {
              "@class" : ".XAsset",
              "events" : [ ],
              "assetId" : 4220,
              "remoteResources" : [ ],
              "name" : "3",
              "location" : null,
              "owner" : null,
              "notes" : null,
              "serialNumber" : "3",
              "description" : "LOAD CELL U/W 3500  LBS TEST",
              "physicalInfo" : {
                "length" : -1.0,
                "height" : -1.0,
                "width" : -1.0,
                "weight" : -1.0
              },
              "firmwareVersion" : null,
              "softwareVersion" : null,
              "powerRequirements" : null,
              "uid" : "A00003",
              "assetType" : "notClassified",
              "mobile" : false,
              "manufacturer" : "SENSING SYST",
              "modelNumber" : "10740-3C/3500",
              "purchasePrice" : null,
              "purchaseDate" : null,
              "deliveryDate" : null,
              "depthRating" : null,
              "ooiPropertyNumber" : null,
              "ooiPartNumber" : null,
              "ooiSerialNumber" : null,
              "deliveryOrderNumber" : null,
              "institutionPropertyNumber" : null,
              "institutionPurchaseOrderNumber" : null,
              "shelfLifeExpirationDate" : null,
              "dataSource" : "/home/asadev/uframes/uframe_ooi_20160727_90f4540c71d3fc4f6a4fc8262903c92c722535ee/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
              "lastModifiedTimestamp" : 1469665637289
            }

            Base asset fields:
            base_required_fields = [
                                    '@class',
                                    'events',
                                    'assetId',
                                    'remoteResources',
                                    'name',
                                    'location',
                                    'owner',
                                    'notes',
                                    'serialNumber',
                                    'description',
                                    'physicalInfo',
                                    'firmwareVersion',
                                    'softwareVersion',
                                    'powerRequirements',
                                    'uid',
                                    'assetType',
                                    'mobile',
                                    'manufacturer',
                                    'modelNumber',
                                    'purchasePrice',
                                    'purchaseDate',
                                    'deliveryDate',
                                    'depthRating',
                                    'ooiPropertyNumber',
                                    'ooiPartNumber',
                                    'ooiSerialNumber',
                                    'deliveryOrderNumber',
                                    'institutionPropertyNumber',
                                    'institutionPurchaseOrderNumber',
                                    'shelfLifeExpirationDate',
                                    'dataSource'
                                    ]

        Example of a sensor asset:
            {
              "@class" : ".XInstrument",
              "calibration" : [ ],
              "events" : [ ],
              "assetId" : 5883,
              "remoteResources" : [ ],
              "name" : "ML12936-01",
              "location" : null,
              "owner" : null,
              "notes" : null,
              "serialNumber" : "ML12936-01",
              "description" : "WFP COASTAL (1ST ARTICLE) Electronics #1",
              "physicalInfo" : {
                "length" : -1.0,
                "height" : -1.0,
                "width" : -1.0,
                "weight" : -1.0
              },
              "firmwareVersion" : "54",
              "softwareVersion" : null,
              "powerRequirements" : null,
              "uid" : "A00391.1",
              "assetType" : "Sensor",
              "mobile" : false,
              "manufacturer" : "MCLANE",
              "modelNumber" : "MMP-1ST ARTICLE",
              "purchasePrice" : 0.0,
              "purchaseDate" : 1433376000000,
              "deliveryDate" : 1433376000000,
              "depthRating" : null,
              "ooiPropertyNumber" : null,
              "ooiPartNumber" : null,
              "ooiSerialNumber" : null,
              "deliveryOrderNumber" : null,
              "institutionPropertyNumber" : null,
              "institutionPurchaseOrderNumber" : null,
              "shelfLifeExpirationDate" : null,
              "dataSource" : "/home/asadev/uframes/uframe_ooi_20160727_90f4540c71d3fc4f6a4fc8262903c92c722535ee/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
              "lastModifiedTimestamp" : 1470377622775
            }
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get all event types.
        event_types = get_event_types()
        self.assertTrue(isinstance(event_types, list))
        self.assertTrue(len(event_types) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create asset: base
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {
          "calibration": [],
          "events": [],
          "assetInfo": {
            "array": "Coastal Pioneer",
            "assembly": "Oregon Inshore Surface Mooring - Multi-Function Node",
            "asset_name": "CP03ISSM-00003-DCL37",
            "description": "Data Concetrator Logger",
            "longName": "Coastal Pioneer Oregon Inshore Surface Mooring - Multi-Function Node - Data Concentrator Logger (DCL)",
            "maxdepth": 0,
            "mindepth": 0,
            "name": "Coastal Pioneer Oregon Inshore Surface Mooring - Multi-Function Node - Data Concentrator Logger (DCL)",
            "owner": None,
            "type": "Sensor"
          },
          "assetType": "Sensor",
          "latitude": 40.3595,
          "longitude": -70.885,
          "dataSource": "/home/asadev/uframes/uframe_ooi_20160727_90f4540c71d3fc4f6a4fc8262903c92c722535ee/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
          "deployment_number": "3",
          "deployment_numbers": [
            3
          ],
          "depth": 0.0,
          "manufactureInfo": {
            "firmwareVersion": None,
            "manufacturer": "WHOI",
            "modelNumber": "DCL",
            "serialNumber": "CP03ISSM-00003-DCL37",
            "shelfLifeExpirationDate": None,
            "softwareVersion": None
          },
          "mobile": False,
          "notes": None,
          "partData": {
            "institutionPropertyNumber": None,
            "institutionPurchaseOrderNumber": None,
            "ooiPartNumber": None,
            "ooiPropertyNumber": None,
            "ooiSerialNumber": None
          },
          "physicalInfo": {
            "depthRating": None,
            "height": -1.0,
            "length": -1.0,
            "powerRequirements": None,
            "weight": -1.0,
            "width": -1.0
          },
          "purchaseAndDeliveryInfo": {
            "deliveryDate": 1358812800000,
            "deliveryOrderNumber": None,
            "purchaseDate": 1358812800000,
            "purchasePrice": None
          },
          "ref_des": "CP03ISSM-MFD37-00-DCLENG000",
          "remoteResources": [],
          "tense": "PAST",
          "uid": "ED0100"
        }

        string_data = self.get_asset_input_as_string(data)
        url = url_for('uframe.create_asset')
        if debug: print '\n create url: ', url
        keys = data.keys()
        keys.sort()
        #print '\n keys(%d): %s' % (len(keys), keys)
        data = json.dumps(string_data)
        response = self.client.post(url, headers=headers, data=data)
        if debug: print '\n debug -- received response data on asset create...'
        if debug:
            print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            print '\n response_error: ', response_error

        #self.assertEquals(response.status_code, 201)
        self.assertEquals(response.status_code, 400)
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
        asset_types = ['Mooring']
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
                if some_asset['assetType'] == target_type:
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
            new_shelfLifeExpirationDate = asset['lastModifiedTimestamp']
            new_depthRating = 50.0
            new_notes = 'Some new notes here.'
            new_purchasePrice = 250.00
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

            # Verify all required fields are provided in asset.
            if verbose: print '\n\t Verifying asset of type \'%s\' has all required fields.' % target_type
            asset_fields = asset.keys()
            for field in required_fields:
                if debug: print '\n field: ', field
                self.assertTrue(field in asset_fields)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #  Update asset
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            """
            # Convert asset to 'all string' data to simulate UI form data. test conversion to valid (original) data.
            string_asset = self.get_asset_input_as_string(asset)
            if debug: print '\n debug ********\n string_asset(%d): %s' % (len(string_asset),
                                                              json.dumps(string_asset, indent=4, sort_keys=True))
            """
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
                self.display_asset_information(updated_asset)

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

    # Causing issues - null asset or event id.
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
                if some_asset['assetType'] == target_type:
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
            self.display_asset_information(original)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # e. String convert values (simulate UI jgrid output).
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t e. String convert values (simulate UI jgrid output).'
            string_asset = self.get_asset_input_as_string(asset)
            if debug: print '\n ---------- asset: '
            self.dump_asset(string_asset, debug)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # f. Convert string asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t f. Convert string asset.'
            converted_asset = None
            try:
                converted_asset = convert_required_fields(target_type, string_asset, required_fields, field_types, 'update')
                self.dump_asset(converted_asset, debug)
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
            self.display_asset_information(original_converted)

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
            new_shelfLifeExpirationDate = original_converted['lastModifiedTimestamp'] + 1100
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
            string_asset = self.get_asset_input_as_string(converted_asset)
            if debug: print '\n ---------- string_asset: '
            self.dump_asset(string_asset, debug)

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
            self.display_asset_information(original, debug)

            if debug: print '\n ---------- updated description: '
            self.display_asset_information(updated_asset, debug)

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
            self._create_remote_resource(asset_uid, asset_id)

        if verbose: print '\n '

    def test_update_assets(self):
        """
        Test update mooring, node and sensor assets. Using string asset input to simulate UI data from jgrid.

        Outline:
        a. Set target asset type to mooring.
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
                if some_asset['assetType'] == target_type:
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
            self.display_asset_information(original)

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
            if debug: print '\n ---------- converted asset (with original values): '
            self.display_asset_information(original_converted)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # e. Modify selected fields and save.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t e. Modify selected fields and save.'
            # Update some field values to test asset update.
            new_description = original_converted['assetInfo']['description'] + ' ' + str(datetime.datetime.now())
            if original_converted['assetInfo']['owner'] is None:
                new_owner = str(datetime.datetime.now())
            else:
                new_owner = original_converted['assetInfo']['owner'] + ' ' + str(datetime.datetime.now())
            new_shelfLifeExpirationDate = original_converted['lastModifiedTimestamp'] + 1100
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
            self.display_asset_information(original, debug)

            if debug: print '\n ---------- updated description: '
            self.display_asset_information(updated_asset, debug)

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
            self._create_remote_resource(asset_uid, asset_id)

        if verbose: print '\n '

    def test_negative_create_remote_resource(self):
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
        asset_types = ['Node']
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
                if some_asset['assetType'] == target_type:
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
            "uid": 'bad_uid',
            "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
            #if debug: print '\n ----- url: ', url
            response = self.client.post(url, headers=headers, data=data)
            if debug:
                print '\n debug -- response.status_code: ', response.status_code
                print '\n debug --a-- response.data: ', response.data
                print '\n debug --b-- response.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 400)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 1b...'
            # Create some bad data...
            remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",
            "uid": None,
            "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))
            #self.assertTrue('remote_resource' in results)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 2...'
            # Create some data...
            remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label": "testresource",
            "resourceNumber": None,
            "status": "active",
            "uid": asset_uid,
            "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
            response = self.client.post(url, headers=headers, data=data)
            if debug: print '\n debug -- response.status_code: ', response.status_code
            if debug: print '\n debug -- response.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 200)
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
            "uid": asset_uid,
            "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
            response = self.client.post(url, headers=headers, data=data)
            if debug:
                print '\n debug -- response.status_code: ', response.status_code
                print '\n debug -- response.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 200)
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
            "uid": asset_uid,
            "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
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
                "uid": asset_uid,
                "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
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
                "uid": asset_uid,
                "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 200)
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
                "uid": asset_uid,
                "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
            response = self.client.post(url, headers=headers, data=data)
            self.assertEquals(response.status_code, 200)
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
                "uid": asset_uid,
                "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
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
                "uid": asset_uid,
                "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
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
                "uid": asset_uid,
                "url": None
            }
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.create_remote_resource')
            response = self.client.post(url, headers=headers, data=data)
            if debug: print '\n debug -- response.data: ', response.data
            self.assertEquals(response.status_code, 400)
            results = json.loads(response.data)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

        if verbose: print '\n '

    def test_update_remote_resource(self):
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
        asset_types = ['Mooring']
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
            remote_resources = []
            for some_asset in some_assets:
                if some_asset['assetType'] == target_type:
                    if 'remoteResources' in some_asset:
                        if len(some_asset['remoteResources']) > 0:
                            asset = some_asset
                            remote_resources = some_asset['remoteResources']
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

            # Get remoteResources, select an remoteResource to update.
            self.assertTrue('remoteResources' in asset)
            remote_resource_data = remote_resources[0]
            self.assertTrue(remote_resource_data is not None)


            remote_resource_data['uid'] = asset_uid
            remote_resource_data['label'] = 'this label has been updated'
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if debug: print '\n Test 1a...'
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
            self.assertEquals(len(remote_resource_data), 10)
            if debug: print '\n debug -- remote_resource_data: ', remote_resource_data
            data = json.dumps(remote_resource_data)
            url = url_for('uframe.update_remote_resource')
            #if debug: print '\n ----- url: ', url
            response = self.client.put(url, headers=headers, data=data)
            if debug: print '\n debug -- response.status_code: ', response.status_code
            if debug: print '\n debug --a-- response.data: ', response.data
            if debug: print '\n debug --b-- response.data: ', json.loads(response.data)
            self.assertEquals(response.status_code, 200)

            if verbose: print '\n '


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dump_asset(self, asset, debug=False):
        """
        Print asset if debug enabled.
        """
        if debug:
            print '\n --------------\n asset: %s' % json.dumps(asset, indent=4, sort_keys=True)

    def display_asset_information(self, asset, debug=False):

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
        if verbose: print '\n Number of resources in uframe asset: ', len_remote_resources
        self.assertTrue(len_remote_resources >= 0)

        #if debug: print '\n debug ********\n asset to be updated (%d): %s' % (len(asset),
        #                                                  json.dumps(asset, indent=4, sort_keys=True))
        remote_resource_data = {
            "dataSource": None,
            "keywords": None,
            "label" : "testresource",
            "resourceNumber" : "1258.1548.58756.098",
            "status" : "active",
            "uid": asset_uid,
            "url": None
            }

        if debug: print '\n\tdebug remote_resource: ', remote_resource_data

        data = json.dumps(remote_resource_data)
        url = url_for('uframe.create_remote_resource')
        if debug: print '\n ----- url: ', url
        response = self.client.post(url, headers=headers, data=data)
        if debug: print '\n debug -- response.data: ', json.loads(response.data)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        if debug: print '\n debug ********\nCreated remote_resource: %s' % json.dumps(results, indent=4, sort_keys=True)
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

        # Get asset from uframe directly to verify number of remote resources.
        if debug:
            print '\n\t --------------------------------------------'
            print '\n\tGetting asset by asset_id: ', asset_id
        updated_asset = uframe_get_asset_by_id(asset_id)
        if debug:
            self.dump_asset(updated_asset, debug)

        if debug:
            print '\n\t --------------------------------------------'
            print '\n\tGetting asset by asset_uid: ', asset_uid
        updated_asset = uframe_get_asset_by_uid(asset_uid)
        if debug:
            self.dump_asset(updated_asset, debug)
        self.assertTrue(updated_asset is not None)
        self.assertTrue(updated_asset)
        self.assertTrue('remoteResources' in updated_asset)
        self.assertTrue(updated_asset['remoteResources'] is not None)
        if not updated_asset['remoteResources']:
            print '\n\t****** No remote resources in updated asset! '
        remote_resources = updated_asset['remoteResources']
        len_update_remote_resources = len(remote_resources)
        if verbose: print '\n\tNumber of resources in updated uframe asset: ', len_update_remote_resources

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
        if verbose: print '\n\tNumber of resources in updated uframe asset: ', len_update_remote_resources

        self.assertTrue(len_update_remote_resources > 0)
        found_updated_resource = False
        for resource in remote_resources:
            if resource['remoteResourceId'] == remote_resource_id:
                found_updated_resource = True
                break
        self.assertEquals(found_updated_resource, True)
        if debug: print '\n\ttest -----------------------\n test -- Exit Create remote resource [_create_remote_resource]...'

        return

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