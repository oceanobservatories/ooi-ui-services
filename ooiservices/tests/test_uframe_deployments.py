#!/usr/bin/env python
"""
Specific testing of uframe deployment endpoints for asset management.
"""
__author__ = 'Edna Donoughe'

import unittest
from ooiservices.tests.common_tools import (dump_dict)
from base64 import b64encode
from flask import (url_for)
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from unittest import skipIf
import os
from random import randint
import json
import datetime
import requests

from ooiservices.app.uframe.common_tools import get_supported_asset_types
from ooiservices.app.uframe.event_tools import get_uframe_event
from ooiservices.app.uframe.config import (get_url_info_deployments_inv, get_uframe_deployments_info,
                                           get_events_url_base, get_deployments_url_base)


@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class DeploymentTestCase(unittest.TestCase):

    # enable verbose (during development and documentation) to get a list of
    # urls used throughout test cases. Always set to False before check in.
    verbose = False
    debug = False
    root = 'http://localhost:4000'
    asset_uid_root = 'TEST-ASA-'        # When assets are created, provides ability to change portion of uid name.

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
        suite.addTest(unittest.makeSuite(self.test_calibration_events()))
        return suite

    if __name__ == "__main__":
        unittest.main()
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test cases
    #   test_uframe_get_deployment
    #   test_uframe_get_deployments
    #   test_uframe_create_deployment
    #   test_uframe_update_deployment
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_uframe_get_deployments(self):
        """
        host:12587/events/deployment/inv
        host:12587/events/deployment/inv/{subsite}
        host:12587/events/deployment/inv/{subsite}/{node}
        host:12587/events/deployment/inv/{subsite}/{node}/{sensor}
        host:12587/events/deployment/inv/{subsite}/{node}/{sensor}/deploy_number, where deploy_number is an int

        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment inventory url for uframe
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url, timeout, timeout_read = get_url_info_deployments_inv()
        if debug: print '\n debug -- deployment inventory base url: ', base_url

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get deployment inventory
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = base_url
        #if verbose: print '\n ----- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(len(result) > 0)
        subsite_list = result[:]
        subsite_list.sort()
        #if debug: print '\n debug -- subsite_list: ', subsite_list
        set_subsite_list = []
        for subsite in subsite_list:
            if subsite not in set_subsite_list:
                set_subsite_list.append(subsite)
        # Verify no duplicates in deployment subsites
        self.assertEquals(len(subsite_list), len(set(subsite_list)))

        for subsite in subsite_list:

            # Get deployment/inv/{subsite} (list)
            url = '/'.join([base_url, subsite])
            #if verbose: print '\n ----- url: ', url
            response = requests.get(url, timeout=(timeout, timeout_read))
            self.assertEquals(response.status_code, 200)
            node_list = json.loads(response.content)
            self.assertTrue(node_list is not None)
            self.assertTrue(isinstance(node_list, list))
            self.assertTrue(len(node_list) > 0)

            # Verify no duplicates in list of deployment nodes for a subsite.
            #if debug: print '\n debug -- %s node_list: %s' % (subsite, node_list)
            set_node_list = []
            for item in node_list:
                if item not in set_node_list:
                    set_node_list.append(item)
            #if debug: print '\n debug -- set_node_list(%d): %s' % (len(set_node_list), set_node_list)
            self.assertEquals(len(node_list), len(set_node_list))

            #if debug: print '\n debug -- %s node_list: %s' % (subsite, node_list)
            for node in node_list:
                # Get deployment/inv/{subsite}/{node} (list)
                url = '/'.join([base_url, subsite, node])
                #if verbose: print '\n ----- url: ', url
                response = requests.get(url, timeout=(timeout, timeout_read))
                self.assertEquals(response.status_code, 200)
                sensor_list = json.loads(response.content)
                self.assertTrue(sensor_list is not None)
                self.assertTrue(isinstance(sensor_list, list))
                self.assertTrue(len(sensor_list) > 0)

                # Verify no duplicates in list of deployment sensors for a subsite/node.
                set_sensor_list = []
                for item in sensor_list:
                    if item not in set_sensor_list:
                        set_sensor_list.append(item)
                self.assertEquals(len(sensor_list), len(set_sensor_list))
                #if debug: print '\n debug -- %s/%s sensor_list: %s' % (subsite, node, sensor_list)

        #node_index = randint(0, len(node_list - 1))
        #sensor_index = randint(0, len(sensor_list - 1))
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # todo (Positive) Process cruise deployment, validate fields
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #self.assertTrue(len(deployment) > 0)

        # Get edit phase values. (/uframe/events/edit_phase_values)
        url = url_for('uframe.get_edit_phase_values')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        if verbose: print '\n'

    def test_uframe_get_deployment(self):
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get deployment using deployment eventId.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployment_by_event_id', event_id=9999999)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get a random deployment object from deployment inventory
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        deployment = self.get_deployment()
        self.assertTrue(deployment is not None)
        self.assertTrue(isinstance(deployment, dict))

        self.assertTrue('eventId' in deployment)
        self.assertTrue(deployment['eventId'] is not None)
        self.assertTrue(isinstance(deployment['eventId'], int))
        deployment_id = deployment['eventId']
        self.assertTrue(deployment_id > 0)

    def test_uframe_create_deployment(self):
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get some assets to use in new deployment.
        array, mooring, node, sensor = self.create_some_assets()
        self.assertTrue(array is not None)
        self.assertTrue(mooring is not None)
        self.assertTrue(node is not None)
        self.assertTrue(sensor is not None)
        self.assertTrue('uid' in array)
        self.assertTrue('uid' in mooring)
        self.assertTrue('uid' in node)
        self.assertTrue('uid' in sensor)

        array_uid = array['uid']
        mooring_uid = mooring['uid']
        node_uid = node['uid']
        sensor_uid = sensor['uid']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get data for asset create.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        deployment_data = self.get_deployment_data_for_create(mooring_uid, node_uid, sensor_uid)
        if verbose:
            print '\n Create deployment data: '
            dump_dict(deployment_data, verbose)
            print '\n '

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Post deployment to uframe for update (host:12587/events/deployment)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_deployments_url_base()])
        if debug: print '\n debug -- Post url: ', url
        response = requests.post(url, data=json.dumps(deployment_data), headers=headers)
        if debug:
            print '\n response.status_code: ', response.status_code
            if response.content:
                print '\n response.content: ', json.loads(response.content)
        self.assertEquals(response.status_code, 201)
        result = json.loads(response.content)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('id' in result)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(isinstance(result['id'], int) or isinstance(result['id'], long))
        deployment_id = result['id']

        # ========================== START HERE ===========================================
        if debug: print '\n debug -- Created deployment: event id: %d ' % deployment_id

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment using deployment eventId. (host:12587/events/id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(deployment_id)])
        if debug: print '\n debug -- Get url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if debug:
            print '\n response.status_code: ', response.status_code
            print '\n response.content: ', json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        if debug: print '\n debug -- New deployment: event id: %d ' % deployment_id

        # Get deployment using deployment_id
        deployment = get_uframe_event(deployment_id)
        # Check result structure.
        self.assertTrue('dataSource' in deployment)
        self.assertTrue('deployedBy' in deployment)
        self.assertTrue('location' in deployment)
        self.assertTrue('versionNumber' in deployment)

        # Verify fields have been created as expected.
        self.assertEquals(deployment['dataSource'], deployment_data['dataSource'])
        self.assertEquals(deployment['deployedBy'], deployment_data['deployedBy'])
        self.assertEquals(deployment['location']['orbitRadius'], deployment_data['location']['orbitRadius'])
        self.assertEquals(deployment['versionNumber'], deployment_data['versionNumber'])

    def test_uframe_update_deployment(self):
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get a random deployment object from inventory
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        deployment = self.get_deployment()
        self.assertTrue(deployment is not None)
        self.assertTrue(isinstance(deployment, dict))

        self.assertTrue('eventId' in deployment)
        self.assertTrue(deployment['eventId'] is not None)
        self.assertTrue(isinstance(deployment['eventId'], int))
        deployment_id = deployment['eventId']
        self.assertTrue(deployment_id > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment using deployment eventId.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployment_by_event_id', event_id=deployment_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Compare deployment objects - deployment from inventory versus deployment by eventId.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # todo - suggest verifying deployment response from inventory and by eventId

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update deployment object garnered from deployment inventory.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        unique_int = randint(1000,50000)
        unique_small_int = randint(1,10)
        unique_timestamp = str(datetime.datetime.now())

        # Prepare new field values and perform field updates: dataSource, deployedBy, orbitRadius, versionNumber
        data_source = unique_timestamp
        deployed_by = 'Test user - ' + str(unique_int)
        orbit_radius = unique_small_int
        current_version_number = deployment['versionNumber']
        if current_version_number and current_version_number is not None:
            if isinstance(current_version_number, int):
                current_version_number = current_version_number + 1

        # dataSource field.
        if deployment['dataSource'] is not None:
            deployment['dataSource'] = deployment['dataSource'] + data_source
        else:
            deployment['dataSource'] = data_source

        # deployedBy field.
        if deployment['deployedBy'] is not None:
            deployment['deployedBy'] = deployment['deployedBy'] + deployed_by
        else:
            deployment['deployedBy'] = deployed_by

        # orbitRadius field.
        if deployment['location']['orbitRadius'] is not None:
            deployment['location']['orbitRadius'] = deployment['location']['orbitRadius'] + orbit_radius
        else:
            deployment['location']['orbitRadius'] = orbit_radius

        # versionNumber field.
        deployment['versionNumber'] = current_version_number

        # Perform asset update in uframe (host:12587/events/id)
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(deployment_id)])
        if debug: print '\n debug -- PUT url: ', url
        response = requests.put(url, data=json.dumps(deployment), headers=headers)
        if debug:
            print '\n response.status_code: ', response.status_code
            print '\n response.content: ', json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        if debug: print '\n debug -- Updated deployment: event id: %d ' % deployment_id

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment using deployment eventId. (host:12587/events/id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(deployment_id)])
        if debug: print '\n debug -- Get url: ', url
        response = requests.get(url, data=json.dumps(deployment), headers=headers)
        if debug:
            print '\n response.status_code: ', response.status_code
            print '\n response.content: ', json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        if debug:
            print '\n debug -- New deployment: event id: %d ' % deployment_id

        # Check result structure.
        self.assertTrue('dataSource' in result)
        self.assertTrue('deployedBy' in result)
        self.assertTrue('location' in result)
        self.assertTrue('versionNumber' in result)

        # Verify fields have been updated as expected.
        self.assertEquals(deployment['dataSource'], result['dataSource'])
        self.assertEquals(deployment['deployedBy'], result['deployedBy'])
        self.assertEquals(deployment['location']['orbitRadius'], result['location']['orbitRadius'])
        self.assertEquals(deployment['versionNumber'], result['versionNumber'])

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Functions to assist in test cases.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_deployment(self):
        debug = self.debug
        verbose = self.verbose
        # Get base deployment inventory url
        base_url, timeout, timeout_read = get_url_info_deployments_inv()
        url = base_url
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(len(result) > 0)
        subsite_list = result[:]
        subsite_list.sort()

        if verbose: print '\n Get a random subsite, node, sensor and fetch deployments.'
        # http://uframe-3-test.ooi.rutgers.edu:12587/events/deployment/inv/GS01SUMO/SBD11/04-DOSTAD000/1
        # Get a subsite/node/sensor dynamically
        subsite_index = randint(0, len(subsite_list) - 1)
        subsite = subsite_list[subsite_index]
        if debug: print '\n debug -- Working with subsite: ', subsite

        # Get deployment/inv/{subsite} (list)
        url = '/'.join([base_url, subsite])
        if verbose: print '\n Get node list ----- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        node_list = json.loads(response.content)
        self.assertTrue(node_list is not None)
        self.assertTrue(isinstance(node_list, list))
        self.assertTrue(len(node_list) > 0)
        if debug: print '\n debug -- Have node list: ', node_list

        node_index = randint(0, len(node_list) - 1)
        node = node_list[node_index]
        if debug: print '\n debug -- Working with node: ', node

        # Get deployment/inv/{subsite}/{node} (list) Sensors!
        url = '/'.join([base_url, subsite, node])
        if verbose: print '\n Get sensor list ----- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        sensor_list = json.loads(response.content)
        self.assertTrue(sensor_list is not None)
        self.assertTrue(isinstance(sensor_list, list))
        self.assertTrue(len(sensor_list) > 0)
        if verbose: print '\n Have sensor list: ', sensor_list

        sensor_index = randint(0, len(sensor_list) - 1)
        sensor = sensor_list[sensor_index]
        if debug: print '\n debug -- Working with sensor: ', sensor
        if verbose:
            print '\n Working with subsite/node/sensor: %s/%s/%s' % (subsite, node, sensor)
            print '\n Get deployments for subsite/node/sensor: %s/%s/%s' % (subsite, node, sensor)
        url = '/'.join([base_url, subsite, node, sensor])
        if verbose: print '\n Get sensor list ----- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        deployments_list = []
        deployments_list = json.loads(response.content)
        self.assertTrue(deployments_list is not None)
        self.assertTrue(isinstance(deployments_list, list))
        self.assertTrue(len(deployments_list) > 0)
        if verbose: print '\n Have deployments list: ', deployments_list
        self.assertTrue(deployments_list is not None)
        self.assertTrue(len(deployments_list) > 0)
        if len(deployments_list) > 1:
            deployment_index = randint(0, len(deployments_list)-1)
            deployment_number = deployments_list[deployment_index]
        else:
            deployment_number = deployments_list[0]
        if verbose:
            print '\n Get deployment for subsite/node/sensor: %s/%s/%s deployment number %d ' % \
                          (subsite, node, sensor, deployment_number)

        url = '/'.join([base_url, subsite, node, sensor, str(deployment_number)])
        if verbose: print '\n Get actual deployment ----- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        deployment_list = json.loads(response.content)
        self.assertTrue(deployment_list is not None)
        self.assertTrue(isinstance(deployment_list, list))
        self.assertTrue(len(deployment_list) > 0)

        self.assertEquals(len(deployment_list), 1)
        deployment = deployment_list[0]
        if verbose:
            print '\n Deployment to be processed: subsite/node/sensor: %s/%s/%s deployment number %d ' % \
                          (subsite, node, sensor, deployment_number)
            dump_dict(deployment, verbose)
        return deployment

    def create_some_assets(self):
        """
        There are five (5) kinds of assets, identified by the assetType.
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
        mooring = None
        node = None
        sensor = None
        array = None
        notClassified = None
        for asset_type in asset_types:
            if verbose: print '\n\tCreate %s asset.' % asset_type
            data = self.get_basic_UI_asset_data(asset_type)
            string_data = self.get_asset_input_as_string(data)
            url = url_for('uframe.create_asset')
            if debug: print '\n\tcreate url: ', url
            keys = data.keys()
            keys.sort()
            #print '\n keys(%d): %s' % (len(keys), keys)
            data = json.dumps(string_data)
            response = self.client.post(url, headers=headers, data=data)
            if debug: print '\n\tdebug -- received response data on asset create...'
            if debug: print '\n\tresponse.status_code: ', response.status_code
            self.assertEquals(response.status_code, 201)
            response_data = json.loads(response.data)
            if debug:
                print '\n\tresponse_data: ', response_data
            self.assertTrue('asset' in response_data)
            new_asset = response_data['asset']
            if asset_type == 'Mooring':
                mooring = new_asset.copy()
            elif asset_type == 'Node':
                node = new_asset.copy()
            elif asset_type == 'Sensor':
                sensor = new_asset.copy()
            elif asset_type == 'Array':
                array = new_asset.copy()

            # Get asset id from create response
            asset_id = None
            if 'id' in new_asset:
                asset_id = new_asset['id']
            self.assertTrue(asset_id is not None)
            self.assertTrue(isinstance(asset_id, int))
            self.assertTrue('uid' in new_asset)
            asset_uid = new_asset['uid']
            if verbose: print '\n\tCreated asset id/uid: %d/%s' % (asset_id, asset_uid)

        if verbose: print '\n '
        return array, mooring, node, sensor

    def get_basic_UI_asset_data(self, type):
        # "calibration": [],
        debug = False
        uid_suffix = str(randint(100,1000))
        unique_int = randint(1000,5000)
        description = type + '-' + str(unique_int)
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
          'dataSource': 'some.csv' + uid_suffix + description,
          'deployment_number': '3',
          'deployment_numbers': [
            3
          ],
          'depth': 0.0,
          'manufactureInfo': {
            'firmwareVersion': str(small_int),
            'manufacturer': 'WHOI',
            'modelNumber': None,
            'serialNumber': 'CP03ISSM-' + str(unique_int),
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
            'deliveryOrderNumber': None,
            'purchaseDate': 1358812800000,
            'purchasePrice': None
          },
          'ref_des': 'CP03ISSM-MFD37-00-DCLENG000',
          'remoteResources': [],
          'tense': 'PAST',
          'uid': self.asset_uid_root + uid_suffix + '-' + str(small_int),
          'editPhase': 'EDIT'
        }

        if type in ['Array', 'Mooring', 'Node', 'Sensor']:
            data['assetType'] = type
        if type == 'Sensor':
            if debug: print '\n debug -- Adding calibration since type is %s' % type
            data['calibration'] = []
        return data


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

    def get_deployment_data_for_create(self, mooring_uid, node_uid, sensor_uid):
        # uframe create deployment data.
        unique_int = randint(1, 2000)
        small_unique_int = randint(10,20)
        large_unique_int = randint(20000,50000)
        deployedBy = 'Test engineer on ' + str(datetime.datetime.now())
        eventStartTime = 1506434330000 + large_unique_int
        eventStopTime = eventStartTime + large_unique_int
        versionNumber = randint(2,10) * 2
        deployment_data = {
              '@class' : '.XDeployment',
              'referenceDesignator' : {
                'subsite' : 'CP01CNSP',
                'sensor' : '08-CTDPFJ000',
                'node' : 'SP001'
              },
              'deploymentNumber' : 100 + small_unique_int,
              'versionNumber' : versionNumber,
              'location' : {
                'depth' : 0.0,
                'longitude' : -70.7701,
                'latitude' : 40.1341,
                'orbitRadius' : 0.0
              },
              'mooring' : {
                '@class' : '.XMooring',
                'uid' : mooring_uid
              },
              'node' : {
                '@class' : '.XNode',
                'uid' : node_uid
              },
              'sensor' : {
                '@class' : '.XInstrument',
                'uid' : sensor_uid
              },
              'deployCruiseInfo' : None,
              'deployedBy' : deployedBy,
              'recoverCruiseInfo' : None,
              'recoveredBy' : 'Test engineer.',
              'eventType' : 'DEPLOYMENT',
              'eventName' : 'event name' + str(unique_int),
              'eventStartTime' : eventStartTime,
              'eventStopTime' :  eventStopTime,
              'ingestInfo' : None,
              'dataSource' : 'UI:user=testuser' + str(datetime.datetime.now())
            }
        """
        'deployCruiseInfo' : {
                '@class' : '.CruiseInfo',
                'uniqueCruiseIdentifer' : 'CP-2015-0004'
              },
              'deployedBy' : 'Test engineer.',
              'recoverCruiseInfo' : {
                '@class' : '.CruiseInfo',
                'uniqueCruiseIdentifer' : 'CP-2015-0005'
              },
              [ {
                "@class" : ".IngestInfo",
                "id" : 12471,
                "ingestPath" : "/omc_data/whoi/OMC/CP01CNSM/D00001/cg_data/cpm3/syslog/",
                "ingestMask" : "cpm_status*.txt",
                "ingestMethod" : "telemetered",
                "ingestQueue" : "Ingest.cg-cpm-eng-cpm_telemetered"
              } ],
        """
        return deployment_data

    """
    Sample deployment object

    {
        "@class": ".XDeployment",
        "assetUid": null,
        "dataSource": "Load from [RS01SUM1_Deploy.xlsx]",
        "deployCruiseInfo": {
            "@class": ".CruiseInfo",
            "assetUid": null,
            "cruiseIdentifier": "TN299",
            "dataSource": "Load from [CruiseInformation.xlsx]",
            "editPhase": "OPERATIONAL",
            "eventId": 115,
            "eventName": "TN299",
            "eventStartTime": 1372377600000,
            "eventStopTime": 1377216000000,
            "eventType": "CRUISE_INFO",
            "lastModifiedTimestamp": 1473180340315,
            "notes": null,
            "shipName": "R/V Thompson",
            "tense": "UNKNOWN",
            "uniqueCruiseIdentifier": "RSN-2013-0001"
        },
        "deployedBy": null,
        "deploymentNumber": 1,
        "editPhase": "OPERATIONAL",
        "eventId": 30470,
        "eventName": "RS01SUM1-LJ01B-05-HYDLFA104",
        "eventStartTime": 1375837860000,
        "eventStopTime": null,
        "eventType": "DEPLOYMENT",
        "inductiveId": null,
        "ingestInfo": [],
        "lastModifiedTimestamp": 1473180646802,
        "location": {
            "depth": 0.0,
            "latitude": 44.56916,
            "location": [
                -125.1479,
                44.56916
            ],
            "longitude": -125.1479,
            "orbitRadius": 0.0
        },
        "mooring": {
            "@class": ".XMooring",
            "assetId": 11,
            "assetType": "Mooring",
            "dataSource": "BulkLoad from [bulk_load-AssetRecord.csv]",
            "deliveryDate": 1358812800000,
            "deliveryOrderNumber": null,
            "depthRating": null,
            "description": "MOORING RSN",
            "editPhase": "OPERATIONAL",
            "events": [],
            "firmwareVersion": null,
            "institutionPropertyNumber": null,
            "institutionPurchaseOrderNumber": null,
            "lastModifiedTimestamp": 1473180006459,
            "location": null,
            "manufacturer": null,
            "mobile": false,
            "modelNumber": "RS01SUM1-LJ01B",
            "name": "SN0004",
            "notes": null,
            "ooiPartNumber": null,
            "ooiPropertyNumber": null,
            "ooiSerialNumber": null,
            "owner": null,
            "physicalInfo": {
                "height": -1.0,
                "length": -1.0,
                "weight": -1.0,
                "width": -1.0
            },
            "powerRequirements": null,
            "purchaseDate": 1358812800000,
            "purchasePrice": 2500.0,
            "remoteResources": [],
            "serialNumber": "SN0004",
            "shelfLifeExpirationDate": null,
            "softwareVersion": null,
            "uid": "ATAPL-65310-020-0004"
        },
        "node": null,
        "notes": null,
        "recoverCruiseInfo": null,
        "recoveredBy": null,
        "referenceDesignator": {
            "full": true,
            "node": "LJ01B",
            "sensor": "05-HYDLFA104",
            "subsite": "RS01SUM1"
        },
        "sensor": {
            "@class": ".XInstrument",
            "assetId": 81,
            "assetType": "Sensor",
            "calibration": [],
            "dataSource": "BulkLoad from [bulk_load-AssetRecord.csv]",
            "deliveryDate": null,
            "deliveryOrderNumber": null,
            "depthRating": null,
            "description": "Guralp Hydrophone (HYDLF)",
            "editPhase": "OPERATIONAL",
            "events": [],
            "firmwareVersion": null,
            "institutionPropertyNumber": null,
            "institutionPurchaseOrderNumber": null,
            "lastModifiedTimestamp": 1473180007354,
            "location": null,
            "manufacturer": "HTI",
            "mobile": false,
            "modelNumber": "HTI-90-U/Diff",
            "name": "299465",
            "notes": null,
            "ooiPartNumber": null,
            "ooiPropertyNumber": null,
            "ooiSerialNumber": null,
            "owner": null,
            "physicalInfo": {
                "height": -1.0,
                "length": -1.0,
                "weight": -1.0,
                "width": -1.0
            },
            "powerRequirements": null,
            "purchaseDate": null,
            "purchasePrice": null,
            "remoteResources": [],
            "serialNumber": "299465",
            "shelfLifeExpirationDate": null,
            "softwareVersion": null,
            "uid": "ATAPL-58693-00004"
        },
        "tense": "UNKNOWN",
        "versionNumber": 1
    }

    """