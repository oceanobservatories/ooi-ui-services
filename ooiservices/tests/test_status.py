#!/usr/bin/env python
"""
Asset Management - Specific testing for status routes

Routes:
[GET]  /status/arrays                               # Get status for all arrays.
[GET]  /status/sites/<string:array_rd>              # Get status for sites associated with an array.
[GET]  /status/platforms/<string:site_rd>           # Get status for platforms associated with a site.
[GET]  /status/instrument/<string:instrument_rd>    # Get instrument status.
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
from ooiservices.app.uframe.vocab import get_vocabulary_arrays
from ooiservices.app.uframe.common_tools import operational_status_values
from unittest import skipIf
import os
from ooiservices.app.uframe.config import get_url_info_resources
import requests

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class StatusTestCase(unittest.TestCase):

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
    #   test_get_status_arrays
    #   test_get_status_sites
    #   test_get_status_platforms
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_status_arrays(self):

        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET assets
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_arrays'), headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('arrays' in results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are status objects in a list
        arrays = results['arrays']
        self.assertTrue(arrays is not None)
        self.assertTrue(isinstance(arrays, list))

        # Verify there status objects are dictionaries
        array = arrays[0]
        self.assertTrue(array is not None)
        self.assertTrue(isinstance(array, dict))

        self.assertTrue('status' in array)
        self.assertTrue(isinstance(array['status'], dict))

        # Get all array codes from vocabulary, eliminate 'SS' for now.
        vocabulary_arrays = get_vocabulary_arrays()
        if 'SS' in vocabulary_arrays:
            del vocabulary_arrays['SS']
        len_arrays = len(arrays)
        self.assertEquals(len_arrays, len(vocabulary_arrays))

    def test_get_status_sites(self):

        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        arrays = get_vocabulary_arrays()
        if not arrays or arrays is None:
            message = 'Unable to obtain required array information for processing.'
            raise Exception(message)

        array_codes = arrays.keys()
        self.assertTrue(isinstance(array_codes, list))
        self.assertTrue(len(array_codes) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_sites', array_rd=array_codes[0]), headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('sites' in results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are status objects in a list
        sites = results['sites']
        self.assertTrue(sites is not None)
        self.assertTrue(isinstance(sites, list))

        # Verify there status objects are dictionaries
        site = sites[0]
        if debug: print '\n debug -- site: ', site
        self.assertTrue(site is not None)
        self.assertTrue(isinstance(site, dict))
        self.assertTrue('status' in site)
        self.assertTrue(isinstance(site['status'], str) or isinstance(site['status'], unicode))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_sites', array_rd='no-such-array'), headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n test -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_sites', array_rd='XX'), headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n test -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_sites', array_rd=' X'), headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n test -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

    def test_get_status_platforms(self):
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')
        try:
            sites = self.get_some_sites()
        except Exception as err:
            print '\n Error getting sites: %s' % str(err)
            pass
        self.assertTrue(sites is not None)
        self.assertTrue(len(sites) > 0)
        self.assertTrue(isinstance(sites, list))
        site = sites[0]
        if debug: print '\n test --  site: ', site
        self.assertTrue(site is not None)
        self.assertTrue(len(site) > 0)
        self.assertTrue('reference_designator' in site)
        rd = site['reference_designator']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET platforms
        # Process a platform.
        """
        {
            u'status': u'failed',
            u'mindepth': 12.0,
            u'end': u'2015-12-27T05:32:27.437Z',
            u'uid': u'A00890',
            u'waterDepth': None,
            u'longitude': -89.35758,
            u'reference_designator': u'GS01SUMO-RID16-06-DOSTAD000',
            u'start': u'2014-12-05T23:45:58.645Z',
            u'depth': 0.0,
            u'maxdepth': 12.0,
            u'latitude': -54.4082,
            u'display_name': u'Dissolved Oxygen'
        }
        """
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_platforms', site_rd=rd), headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue(results is not None)
        self.assertTrue('platforms' in results)
        self.assertTrue(isinstance(results, dict))
        platforms = results['platforms']
        self.assertTrue(len(platforms) > 0)
        platform = platforms[0]

        # Process a platform.
        self.assertTrue(platform is not None)
        self.assertTrue(isinstance(platform, dict))
        self.assertTrue(platform is not None)
        self.assertTrue(isinstance(platform, dict))

        # Process platform header and items attributes - platform data in items attribute.
        self.assertTrue('header' in platform)
        self.assertTrue('items' in platform)
        items = platform['items']
        self.assertTrue(len(items) > 0)
        item = items[0]
        if debug: print '\n debug -- item: ', item
        self.assertTrue('reference_designator' in item)
        rd = item['reference_designator']
        if debug: print '\n test -- rd: ', rd

        # Verify there status objects are dictionaries
        self.assertTrue('status' in item)
        self.assertTrue(isinstance(item['status'], str) or isinstance(item['status'], unicode))
        status = item['status']
        self.assertTrue(status is not None)
        self.assertTrue(status in operational_status_values())

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_platforms', site_rd='no-such-site'), headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n test -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_platforms', site_rd='CE01ISSM-BBBBB'), headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n test -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

    def test_get_status_instruments(self):
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')
        sites = None
        try:
            sites = self.get_some_sites()
        except Exception as err:
            print '\n Error getting sites: %s' % str(err)
            pass
        self.assertTrue(sites is not None)
        self.assertTrue(len(sites) > 0)
        self.assertTrue(isinstance(sites, list))
        site = sites[0]
        if debug: print '\n test --  site: ', site
        self.assertTrue(site is not None)
        self.assertTrue(len(site) > 0)
        self.assertTrue('reference_designator' in site)
        rd = site['reference_designator']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET platforms
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_platforms', site_rd=rd), headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue(results is not None)
        self.assertTrue('platforms' in results)
        self.assertTrue(isinstance(results, dict))
        platforms = results['platforms']
        self.assertTrue(len(platforms) > 0)
        platform = platforms[0]

        self.assertTrue(platform is not None)
        self.assertTrue(isinstance(platform, dict))
        self.assertTrue(platform is not None)
        self.assertTrue(isinstance(platform, dict))
        self.assertTrue('header' in platform)
        self.assertTrue('items' in platform)
        items = platform['items']
        self.assertTrue(len(items) > 0)
        item = items[0]
        if debug: print '\n debug -- item: ', item
        self.assertTrue('reference_designator' in item)
        rd = item['reference_designator']
        if debug: print '\n test -- rd: ', rd

        # Verify there status objects are dictionaries
        self.assertTrue('status' in item)
        self.assertTrue(isinstance(item['status'], str) or isinstance(item['status'], unicode))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET platform instruments
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_instrument', instrument_rd=rd), headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue(results is not None)
        self.assertTrue('instrument' in results)
        self.assertTrue(isinstance(results, dict))
        instrument = results['instrument']
        self.assertTrue(len(platforms) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_instrument', instrument_rd='no-such-instrument'), headers=headers)
        self.assertEquals(response.status_code, 400)
        results = json.loads(response.data)
        if debug: print '\n test -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) GET sites
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_status_instrument', instrument_rd='CE01ISSM-BBBBB-01-123456789'), headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        if debug: print '\n test -- results: ', results
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_some_sites(self):
        """
        Get some sites.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')
        try:
            arrays = get_vocabulary_arrays()
            if not arrays or arrays is None:
                message = 'Unable to obtain required array information for processing.'
                raise Exception(message)

            array_codes = arrays.keys()
            self.assertTrue(isinstance(array_codes, list))
            self.assertTrue(len(array_codes) > 0)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # (Positive) GET sites
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            response = self.client.get(url_for('uframe.get_status_sites', array_rd=array_codes[0]), headers=headers)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue('sites' in results)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Verify there are status objects in a list
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            sites = results['sites']
            self.assertTrue(sites is not None)
            self.assertTrue(isinstance(sites, list))
            self.assertTrue(len(sites) > 0)
            return sites

        except Exception as err:
            if verbose: print '\n exception: ', str(err)
            return None


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