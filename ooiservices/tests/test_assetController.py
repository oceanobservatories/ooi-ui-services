#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'M@Campbell'

import unittest
import json
import os
from unittest import skipIf
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization

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
        '''
        _normalize_whitespace
        '''
        from ooiservices.app.uframe.assetController import\
            _normalize_whitespace
        test_string = "TEST   THIS"
        test_length = len(test_string)
        single_space_string = _normalize_whitespace(test_string)
        norm_length = len(single_space_string)
        '''
        Test that the new string length is less than the original.
        '''
        self.assertTrue(norm_length < test_length)
        '''
        Make sure this didn't remove ALL the whitespace.
        '''
        self.assertTrue(len(single_space_string.split(' ')) == 2)
        '''
        _remove_duplicates
        '''
        from ooiservices.app.uframe.assetController import _remove_duplicates
        duplicate_data_set = ["TEST", "TEST"]
        non_dup_data_set = _remove_duplicates(duplicate_data_set)
        self.assertTrue(len(non_dup_data_set) == 1)

        '''
        #_normalize
        #Use the asset.json file as a sample set for this test.
        '''
        from ooiservices.app.uframe.assetController import _normalize
        normalized_lat = _normalize(self.asset_json['metaData'][0]['value'])
        '''
        expected return: 40 05 45.792 N
        '''
        self.assertTrue(normalized_lat == "40 05 45.792 N")

        '''
        _convert_lat_lon
        '''
        from ooiservices.app.uframe.assetController import\
            convert_lat_lon as _convert_lat_lon
        '''
        #Test a North West input
        '''
        normalized_lon = _normalize(self.asset_json['metaData'][1]['value'])
        coords = _convert_lat_lon(normalized_lat, normalized_lon)
        self.assertTrue(coords == (40.0961, -70.8797))
        '''
        #Test a South input:
        '''
        south_lat = _normalize(self.asset_json['metaData'][11]['value'])
        south_coords = _convert_lat_lon(south_lat, normalized_lon)
        self.assertTrue(south_coords == (-40.0961, -70.8797))
        '''
        #Test a East input:
        '''
        east_lon = _normalize(self.asset_json['metaData'][12]['value'])
        east_coords = _convert_lat_lon(normalized_lat, east_lon)
        self.assertTrue(east_coords == (40.0961, 70.8797))
        '''
        #Test bad input:
        '''
        bad_coords = _convert_lat_lon("ABC", "DEF")
        self.assertTrue(bad_coords == (0.0, 0.0))
        '''
        #Test the conversion does not happen when the lat/lon is in dec deg.
        '''
        dec_deg_lat = self.asset_json['metaData'][9]['value']
        dec_deg_lon = self.asset_json['metaData'][10]['value']
        no_convert = _convert_lat_lon(dec_deg_lat, dec_deg_lon)
        self.assertTrue(no_convert == (dec_deg_lat, dec_deg_lon))

        '''
        #convert_date_time
        '''
        from ooiservices.app.uframe.assetController import\
            convert_date_time as _convert_date_time
        '''
        #Date with no time:
        '''
        raw_date = self.asset_json['metaData'][4]['value']
        date = _convert_date_time(raw_date)
        self.assertTrue(date == '13-Apr-14')
        '''
        #Date and time:
        '''
        raw_time = self.asset_json['metaData'][5]['value']
        date_time = _convert_date_time(raw_date, raw_time)
        self.assertTrue(date_time == '13-Apr-14 17:29')

        '''
        #_convert_water_depth
        '''
        from ooiservices.app.uframe.assetController import\
            convert_water_depth as _convert_water_depth
        '''
        #Water depth with a space between the value and units.
        '''
        raw_depth = self.asset_json['metaData'][3]['value']
        converted_water_depth = _convert_water_depth(raw_depth)
        self.assertTrue(converted_water_depth['value'] == 148)
        self.assertTrue(converted_water_depth['unit'] == 'm')
        '''
        #Water depth without a space between value and units.
        '''
        raw_depth = self.asset_json['metaData'][7]['value']
        converted_water_depth = _convert_water_depth(raw_depth)
        self.assertTrue(converted_water_depth['value'] == 148)
        self.assertTrue(converted_water_depth['unit'] == 'm')
        '''
        #Test a bad entry
        '''
        raw_depth = self.asset_json['metaData'][8]['value']
        converted_water_depth = _convert_water_depth(raw_depth)
        self.assertTrue('Error' in converted_water_depth['message'])


class AssetCollectionTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
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

        with open(self.basedir + '/mock_results/asset_from.json', 'r') as f:
            doc = json.load(f)
        self.asset_from_json = doc

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

    '''
    Test the CRUD routes for uframe assets.
    Until uframe is public, TRAVIS CI will
    always fail this test with not uframe.
    Be sure to test with uframe running.
    '''
    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_get_assets(self):
        headers = self.get_api_headers('admin', 'test')
        response = self.client.get(
            url_for('uframe.get_assets'),
            headers=headers)
        self.assertTrue(response.status_code == 200)

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_get_asset(self):
        headers = self.get_api_headers('admin', 'test')
        response = self.client.get(
            url_for('uframe.get_asset', id=1),
            headers=headers)
        self.assertTrue(response.status_code == 200
                        or response.status_code == 404)

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_post_asset(self):
        headers = self.get_api_headers('admin', 'test')
        data = self.asset_json_in
        response = self.client.post(
            url_for('uframe.create_asset'),
            headers=headers,
            data=json.dumps(data))
        print response.data
        self.assertTrue(response.status_code == 200)

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_put_asset(self):
        headers = self.get_api_headers('admin', 'test')
        data = {"ref_des": "ABCDE"}
        response = self.client.put(
            url_for('uframe.update_asset', id=1),
            headers=headers, data=json.dumps(data))
        self.assertTrue(response.status_code == 200)


class EventCollectionTest(unittest.TestCase):
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
        with open(self.basedir + '/mock_data/event_post.json', 'r') as f:
            doc = json.load(f)
        self.event_json_in = doc

        with open(self.basedir + '/mock_results/event_from.json', 'r') as f:
            doc = json.load(f)
        self.event_from_json = doc

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

    '''
    Test the CRUD routes for uframe events.
    Until uframe is public, TRAVIS CI will
    always fail this test with not uframe.
    Be sure to test with uframe running.
    '''
    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_get_events(self):
        headers = self.get_api_headers('admin', 'test')
        response = self.client.get(
            url_for('uframe.get_events'),
            headers=headers)
        self.assertTrue(response.status_code == 200)

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_get_event(self):
        headers = self.get_api_headers('admin', 'test')
        response = self.client.get(
            url_for('uframe.get_event', id=1),
            headers=headers)
        self.assertTrue(response.status_code == 200)

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_post_event(self):
        headers = self.get_api_headers('admin', 'test')
        data = self.event_json_in
        response = self.client.post(
            url_for('uframe.create_event'),
            headers=headers,
            data=json.dumps(data))
        self.assertTrue(response.status_code == 200)

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_put_event(self):
        headers = self.get_api_headers('admin', 'test')
        data = {"recordedBy": "Campbell"}
        response = self.client.put(
            url_for('uframe.update_event', id=1),
            headers=headers, data=json.dumps(data))
        self.assertTrue(response.status_code == 200)
