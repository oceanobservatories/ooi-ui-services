#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'M@Campbell'

import unittest
import json
import re
import os
from unittest import skipIf
from base64 import b64encode
from flask import url_for, jsonify
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, UserScopeLink, Organization
from collections import OrderedDict
from ooiservices.app.uframe.assetController import uFrameAssetCollection

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''

class PrivateMethodsTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.client = self.app.test_client(use_cookies=False)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        with open(self.basedir + '/mock_data/asset.json', 'r') as f:
            doc = json.load(f)
        self.asset_json = doc
        with open(self.basedir + '/mock_data/event.json', 'r') as f:
            doc = json.load(f)
        self.event_json = doc

    def tearDown(self):
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_private_methods(self):
    #_normalize_whitespace
        from ooiservices.app.uframe.assetController import _normalize_whitespace
        test_string = "TEST   THIS"
        test_length = len(test_string)
        single_space_string = _normalize_whitespace(test_string)
        norm_length = len(single_space_string)
        #Test that the new string length is less than the original.
        self.assertTrue(norm_length < test_length)
        #Make sure this didn't remove ALL the whitespace.
        self.assertTrue(len(single_space_string.split(' ')) == 2)

    #_remove_duplicates
        from ooiservices.app.uframe.assetController import _remove_duplicates
        duplicate_data_set = ["TEST", "TEST"]
        non_dup_data_set = _remove_duplicates(duplicate_data_set)
        self.assertTrue(len(non_dup_data_set) == 1)

    #_uframe_url
        from ooiservices.app.uframe.assetController import _uframe_url
        endpoint = "assets"
        endpoint_id = "1"
        uframe_base_url = self.app.config['UFRAME_ASSETS_URL']
        #Build the control url: List
        control = '/'.join([uframe_base_url, endpoint])
        list_endpoint_url = _uframe_url(endpoint)
        #Verify the url matches the config
        self.assertTrue(control == list_endpoint_url)
        #Build the control url: object
        control = '/'.join([uframe_base_url, endpoint, endpoint_id])
        obj_endpoint_url = _uframe_url(endpoint, endpoint_id)
        self.assertTrue(control == obj_endpoint_url)

    #_uframe_collection
        from ooiservices.app.uframe.assetController import _uframe_collection
        #using uframe url created previously
        #This will be more meaningful when uframe is up and running.
        collection = _uframe_collection(obj_endpoint_url)
        self.assertTrue(type(collection) is dict)
        #Test error message if uframe is not running.
        spoof_conn = _uframe_collection('NOTAREALURL')
        self.assertTrue(spoof_conn['status_code'] == 500)

    #_api_headers
        from ooiservices.app.uframe.assetController import _uframe_headers
        uframe_headers = _uframe_headers()
        self.assertTrue(uframe_headers['Accept'] == 'application/json')

    #_normalize
        #Use the asset.json file as a sample set for this test.
        from ooiservices.app.uframe.assetController import _normalize
        normalized_lat = _normalize(self.asset_json['metaData'][0]['value'])
        #expected return: 40 05 45.792 N
        self.assertTrue(normalized_lat == "40 05 45.792 N")

    #_convert_lat_lon
        from ooiservices.app.uframe.assetController import _convert_lat_lon
        #Test a North West input
        normalized_lon = _normalize(self.asset_json['metaData'][1]['value'])
        coords = _convert_lat_lon(normalized_lat, normalized_lon)
        self.assertTrue(coords == (40.0960533, -70.8797183))
        #Test a South input:
        south_lat = _normalize(self.asset_json['metaData'][11]['value'])
        south_coords = _convert_lat_lon(south_lat, normalized_lon)
        self.assertTrue(south_coords == (-40.0960533, -70.8797183))
        #Test a East input:
        east_lon = _normalize(self.asset_json['metaData'][12]['value'])
        east_coords = _convert_lat_lon(normalized_lat, east_lon)
        self.assertTrue(east_coords == (40.0960533, 70.8797183))
        #Test bad input:
        bad_coords = _convert_lat_lon("ABC", "DEF")
        self.assertTrue("Error" in bad_coords)

    #_convert_date_time
        from ooiservices.app.uframe.assetController import _convert_date_time
        #Date with no time:
        raw_date = self.asset_json['metaData'][4]['value']
        date = _convert_date_time(raw_date)
        self.assertTrue(date == '13-Apr-14')
        #Date and time:
        raw_time = self.asset_json['metaData'][5]['value']
        date_time = _convert_date_time(raw_date, raw_time)
        self.assertTrue(date_time == '13-Apr-14 17:29')

    #_convert_water_depth
        from ooiservices.app.uframe.assetController import _convert_water_depth
        #Water depth with a space between the value and units.
        raw_depth = self.asset_json['metaData'][3]['value']
        converted_water_depth = _convert_water_depth(raw_depth)
        self.assertTrue(converted_water_depth['value'] == 148)
        self.assertTrue(converted_water_depth['unit'] == 'm')
        #Water depth without a space between value and units.
        raw_depth = self.asset_json['metaData'][7]['value']
        converted_water_depth = _convert_water_depth(raw_depth)
        self.assertTrue(converted_water_depth['value'] == 148)
        self.assertTrue(converted_water_depth['unit'] == 'm')
        #Test a bad entry
        raw_depth = self.asset_json['metaData'][8]['value']
        converted_water_depth = _convert_water_depth(raw_depth)
        self.assertTrue('Error' in converted_water_depth['message'])

    #_associate_events
        #TODO: This will need to be tackled when uframe is more permanent

class AssetCollectionTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_password = 'test'
        Organization.insert_org()
        UserScope.insert_scopes()
        User.insert_user(password=test_password)

        self.client = self.app.test_client(use_cookies=False)
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        with open(self.basedir + '/mock_data/asset_post.json', 'r') as f:
            doc = json.load(f)
        self.asset_json_in = doc

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

    def test_uFrameAssetCollection_class(self):
        obj = uFrameAssetCollection()
        self.assertTrue(isinstance(obj, object))

    #to_json
        asset_object = obj.to_json(1)
        self.assertTrue(isinstance(asset_object, dict))

    #from_json
        data = self.asset_json_in
        asset_json = obj.from_json(data)
        #print asset_json