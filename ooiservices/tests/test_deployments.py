#!/usr/bin/env python
"""
Specific testing of UI deployment endpoints for asset management.

Routes:

[GET]  /deployments/edit_phase_values   # Get edit phase values for deployments.
[GET]  /deployments/<int:event_id>      # Get deployment by event id.
[GET]  /deployments/<string:rd>         # Get deployments list by reference designator.

[POST]  /deployments                    # Create a deployment
[PUT]   /assets/<int:id>                # Update a deployment

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

from ooiservices.app.uframe.common_tools import (get_supported_asset_types, deployment_edit_phase_values)
from ooiservices.app.uframe.uframe_tools import get_uframe_event
from ooiservices.app.uframe.deployment_tools import format_deployment_for_ui
from ooiservices.tests.common_tools import get_asset_input_as_string
from ooiservices.app.uframe.config import (get_url_info_deployments_inv, get_uframe_deployments_info,
                                           get_events_url_base, get_deployments_url_base)
from copy import deepcopy


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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test cases
    #   test_get_deployments
    #   test_create_deployment
    #   test_update_deployment
    # *** test_negative_create_deployment_editphase
    # *** test_create_deployment_editphase
    #
    # *** Indicates UI can't be completed without review of uframe operational status and editPhase values.
    # *** Read the notes for eahc test case.
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_deployments(self):
        """
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment edit phase values
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployment_edit_phase_values')
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('values' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment from uframe
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        deployment = self.get_deployment(verbose=verbose)
        self.assertTrue(deployment is not None)
        self.assertTrue('eventId' in deployment)
        self.assertTrue(deployment['eventId'] is not None)
        self.assertTrue(isinstance(deployment['eventId'], int))
        self.assertTrue(deployment['eventId'] > 0)
        event_id = deployment['eventId']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment using event id using deployment route.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployment_by_event_id', event_id=event_id)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        ui_deployment = json.loads(response.data)
        if debug:
            print '\n debug -- ui_deployment: '
            dump_dict(ui_deployment, debug)

        self.assertTrue(ui_deployment is not None)
        self.assertTrue(isinstance(ui_deployment, dict))
        self.assertTrue('rd' in ui_deployment)
        self.assertTrue(ui_deployment['rd'] is not None)
        rd = ui_deployment['rd']
        if debug:
            print '\n debug -- ui_deployment: '
            dump_dict(ui_deployment, debug)
        if debug: print '\n -- len(results): ', len(results)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment using event id using deployment route.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployment_by_event_id', event_id=99999)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        ui_deployment = json.loads(response.data)
        self.assertTrue(ui_deployment is not None)
        self.assertTrue(isinstance(ui_deployment, dict))
        if debug: print '\n -- len(results): ', len(results)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployments by reference designator.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployments_by_rd', rd=rd)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        ui_deployments = json.loads(response.data)
        self.assertTrue(ui_deployments is not None)
        self.assertTrue(isinstance(ui_deployments, dict))
        self.assertTrue('deployments' in ui_deployments)
        self.assertTrue(ui_deployments['deployments'] is not None)
        self.assertTrue(len(ui_deployments['deployments']) > 0)
        if debug: print '\n -- len(results): ', len(results)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get deployments by reference designator.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_deployments_by_rd', rd='bad-rd')
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        ui_deployment = json.loads(response.data)
        self.assertTrue(ui_deployment is not None)
        self.assertTrue(isinstance(ui_deployment, dict))
        if debug: print '\n -- len(results): ', len(results)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get deployments by reference designator. (no deployments)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        find_rd = self.get_rd_with_empty_deployment(verbose=verbose)
        self.assertTrue(find_rd is not None)
        url = url_for('uframe.get_deployments_by_rd', rd=find_rd)
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        if debug: print '\n debug -- result: ', result
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        if verbose: print '\n'


    def test_uframe_create_deployment(self):
        """
        Create assets for a deployment, then create a deployment

        Sample verbose output:

        Create deployment

            Create assets for the deployment

            Create Sensor asset.

                Valid editPhase value 'STAGED' for Sensor asset.

                Created asset id/uid: 7519/2016-09-17:TEST-ASA-446-4

            Create Node asset.

                Valid editPhase value 'STAGED' for Node asset.

                Created asset id/uid: 7520/2016-09-17:TEST-ASA-244-7

            Create Mooring asset.

                Valid editPhase value 'STAGED' for Mooring asset.

                Created asset id/uid: 7521/2016-09-17:TEST-ASA-125-8

            Create Array asset.

                Valid editPhase value 'STAGED' for Array asset.

                Created asset id/uid: 7522/2016-09-17:TEST-ASA-127-9

            Create actual deployment

            Created deployment: event id: 35084
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        if verbose: print '\n\nCreate deployment'

        # Check next deployment number using:
        #   http://uframe-3-test.ooi.rutgers.edu:12587/events/deployment/inv/CE01ISSM/RID16/07-NUTNRB000

        """
        # Get some assets to use in new deployment.
        if verbose: print '\n\tCreate assets for the deployment'
        array, mooring, node, sensor = self.create_some_assets(editPhase='STAGED', verbose=verbose)
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
        """

        mooring_uid = None
        node_uid = None
        sensor_uid = None

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get data for deployment create.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n\tCreate deployment data...'
        #CE01ISSM, RID16, 07-NUTNRB000
        deployment_data = self.get_minimum_deployment_data_for_create(mooring_uid, node_uid, sensor_uid)
        if debug:
            print '\n\tCreate deployment data: '
            dump_dict(deployment_data, verbose)

        """
        deployment_data['referenceDesignator']['subsite'] = 'CE01ISSM'
        deployment_data['referenceDesignator']['node'] = 'RID16'
        deployment_data['referenceDesignator']['sensor'] = '07-NUTNRB000'
        """
        deployment_data['editPhase'] = 'OPERATIONAL'
        deployment_data['rd'] = 'CE01ISSM-RID16-07-NUTNRB000'

        # Get next deploymentNumber
        base_url, timeout, timeout_read = get_url_info_deployments_inv()
        rd = deployment_data['rd']
        subsite, node, sensor = rd.split('-', 2)
        url = '/'.join([base_url, subsite, node, sensor])
        if verbose: print '\n Get deployments list ----- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        self.assertEquals(response.status_code, 200)
        deployments_list = json.loads(response.content)
        self.assertTrue(deployments_list is not None)
        self.assertTrue(isinstance(deployments_list, list))
        deploymentNumber = None
        versionNumber = None
        if not deployments_list:
            deploymentNumber = 1
            versionNumber = 1
        elif deployments_list:
            deployments_list.sort(reverse=True)
            current_number = deployments_list[0]
            deploymentNumber = current_number + 1

            if verbose: print '\n debug Next deployment number: ', deploymentNumber
            # Get versionNumber
            url = '/'.join([base_url, subsite, node, sensor, str(current_number)])
            if verbose: print '\n Get actual deployment ----- url: ', url
            response = requests.get(url, timeout=(timeout, timeout_read))
            self.assertEquals(response.status_code, 200)
            deployment_item = json.loads(response.content)
            self.assertTrue(deployment_item is not None)
            self.assertTrue(isinstance(deployment_item, list))
            current_deployment = deployment_item[0]
            self.assertTrue(isinstance(current_deployment, dict))
            self.assertTrue('versionNumber' in current_deployment)
            current_version = current_deployment['versionNumber']
            versionNumber = current_version + 1
        else:
            print '\n debug -- Unable to determine deployment numbers from uframe query:'
            print '\n debug result returned: deployments_list: ', deployments_list
            self.assertTrue('Exception: ', deployments_list)


        if verbose:
            print '\n Using deployment/version numbers: %d/%d' % (deploymentNumber, versionNumber)
        deployment_data['deploymentNumber'] = deploymentNumber
        deployment_data['versionNumber'] = versionNumber

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Post deployment to uframe for update (host:12587/events/deployment)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n\tCreate deployment data: '
            dump_dict(deployment_data, verbose)

        url = url_for('uframe.create_deployment')
        response = self.client.post(url, data=json.dumps(deployment_data), headers=headers)
        if response.status_code != 201:
            print '\n\ttest_uframe_create_deployment -- response.status_code: ', response.status_code
            if response.data:
                print '\n\ttest_uframe_create_deployment -- response.data: ', json.loads(response.data)

        self.assertEquals(response.status_code, 201)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('deployment' in result)
        self.assertTrue(result['deployment']['eventId'] is not None)
        self.assertTrue(isinstance(result['deployment']['eventId'], int) or isinstance(result['deployment']['eventId'], long))
        deployment_id = result['deployment']['eventId']

        # ========================== START HERE ===========================================
        if verbose: print '\n\tCreated deployment: event id: %d ' % deployment_id

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment using deployment eventId. (host:12587/events/id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(deployment_id)])
        if debug: print '\n debug -- Get url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            print '\n\ttest_uframe_create_deployment -- response.status_code: ', response.status_code
            if response.content:
                print '\n\ttest_uframe_create_deployment -- response.content: ', json.loads(response.content)
            elif response.data:
                print '\n\ttest_uframe_create_deployment -- response.data: ', json.loads(response.data)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        if verbose: print '\n\tNew deployment: event id: %d ' % deployment_id

        # Get deployment using deployment_id
        if verbose: print '\n\tGet new deployment: event id: %d ' % deployment_id
        deployment = get_uframe_event(deployment_id)
        # Check result structure.
        self.assertTrue('dataSource' in deployment)
        self.assertTrue('deployedBy' in deployment)
        self.assertTrue('location' in deployment)
        self.assertTrue('versionNumber' in deployment)

        # Verify fields have been created as expected.
        self.assertEquals(deployment['dataSource'], deployment_data['dataSource'])
        self.assertEquals(deployment['deployedBy'], deployment_data['deployedBy'])
        self.assertEquals(deployment['versionNumber'], deployment_data['versionNumber'])

    '''
    def _test_uframe_create_deployment_editphase(self):
        """
        Problem:
        There is correlation of editPhase with operational status.
        There does not appear to be checking on uframe side for editPhase value for assets particpating in deployment.
        It is to be determined whether the UI is expected to manage the asset editPhase prior to submission of
        create/update deployment or not.
        Add this test once it is understodd how the UI is to interact with editPhase values
        for uframe create/update of deployments.

        ****
        The following script is used to test uframe directly without UI participation.
        It exercises uframe api routes to determine capabilities and processing for/of editPhase values.
        ****

        There is no checking for asset editPhase when permitting deployment editPhase entry on create or edit.
        Expect failure when supplying assets not in editPhase 'STAGED' and deployment has editPhase 'OPERATIONAL'.
        Verify deployment creation with editPhase 'OPERATIONAL', shall fail unless
        all included assets have editPhase of 'STAGED'.

        Sample verbose output:
        Create deployment

            Create assets for the deployment

            Create Sensor asset.

                Valid editPhase value 'EDIT' for Sensor asset.

                Created asset id/uid: 7547/2016-09-17:TEST-ASA-617-1

            Create Node asset.

                Valid editPhase value 'EDIT' for Node asset.

                Created asset id/uid: 7548/2016-09-17:TEST-ASA-897-6

            Create Mooring asset.

                Valid editPhase value 'EDIT' for Mooring asset.

                Created asset id/uid: 7549/2016-09-17:TEST-ASA-234-10

            Create Array asset.

                Valid editPhase value 'EDIT' for Array asset.

                Created asset id/uid: 7550/2016-09-17:TEST-ASA-639-9

            Create actual deployment

            New deployment: event id: 35091
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        if verbose: print '\n\nCreate deployment'

        # Get some assets to use in new deployment.
        if verbose: print '\n\tCreate assets for the deployment'
        array, mooring, node, sensor = self.create_some_assets(editPhase='EDIT', verbose=verbose)
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
        deployment_data['editPhase'] = 'OPERATIONAL'
        if debug:
            print '\n\tCreate deployment data: '
            dump_dict(deployment_data, verbose)
            print '\n '

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Post deployment to uframe for update (host:12587/events/deployment)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n\tCreate actual deployment'
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_deployments_url_base()])
        if debug: print '\n debug -- Post url: ', url
        response = requests.post(url, data=json.dumps(deployment_data), headers=headers)
        if response.status_code != 201:
            print '\n test_uframe_create_deployment_editphase -- response.status_code: ', response.status_code
            if response.content:
                print '\n test_uframe_create_deployment_editphase -- response.content: ', json.loads(response.content)

        self.assertEquals(response.status_code, 201)
        result = json.loads(response.content)

        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('id' in result)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(isinstance(result['id'], int) or isinstance(result['id'], long))
        deployment_id = result['id']
        if verbose: print '\n\tNew deployment: event id: %d ' % deployment_id

    def _test_negative_create_deployment_editphase(self):
        """
        Add this test for negative situations once it is determined how the UI should participate (or not)
        in the use of editPhase values during create/update of deployments.
        Reformat to include UI participation.
        ****
        The following script is used to test uframe directly without UI participation.
        It exercises uframe api routes to determine capabilities and processing for/of negative editPhase values.
        ****
        if you enter a 'bad' value for editPhase, you get an error message from uframe.
        Error message from uframe:

        Error creating element: Unable to deserialize object: Can not construct instance of
        com.raytheon.uf.common.ooi.dataplugin.xasset.
        EditPhase from String value \'EDITTTTT\': value not one of declared Enum instance names\n at
        [Source: org.apache.cxf.transport.http.AbstractHTTPDestination$1@5bbc2828; line: 1, column: 378]
        (through reference chain: com.raytheon.uf.common.ooi.dataplugin.xasset.assets.XInstrument["editPhase"])


        There is no checking for asset editPhase when after deployment editPhase entry on create or edit.
        Expect failure when supplying assets not in editPhase 'STAGED' and deployment has editPhase 'OPERATIONAL'.
        Verify deployment creation with editPhase 'OPERATIONAL', shall fail unless
        all included assets have editPhase of 'STAGED'.

        Sample verbose output:

        Create deployment

            (Negative) Create assets for the deployment

            (Negative) Create Sensor asset.

                Invalid editPhase value 'EDITTTTT' for Sensor asset.

                Failed (as planned) to created asset with editPhase EDITTTTT.

            (Negative) Create Node asset.

                Invalid editPhase value 'EDITTTTT' for Node asset.

                Failed (as planned) to created asset with editPhase EDITTTTT.

            (Negative) Create Mooring asset.

                Invalid editPhase value 'EDITTTTT' for Mooring asset.

                Failed (as planned) to created asset with editPhase EDITTTTT.

            (Negative) Create Array asset.

                Invalid editPhase value 'EDITTTTT' for Array asset.

                Failed (as planned) to created asset with editPhase EDITTTTT.

            Create assets for deployment

            Create Sensor asset.

                Valid editPhase value 'EDIT' for Sensor asset.

                Created asset id/uid: 7483/2016-09-17:TEST-ASA-768-4

            Create Node asset.

                Valid editPhase value 'EDIT' for Node asset.

                Created asset id/uid: 7484/2016-09-17:TEST-ASA-754-5

            Create Mooring asset.

                Valid editPhase value 'EDIT' for Mooring asset.

                Created asset id/uid: 7485/2016-09-17:TEST-ASA-739-6

            Create Array asset.

                Valid editPhase value 'EDIT' for Array asset.

                Created asset id/uid: 7486/2016-09-17:TEST-ASA-976-1

         Invalid editPhase value for deployment: 'BAD-EDIT-PHASE-VALUE', expect failure.

            (Negative) Create actual deployment

            Properly failed to create deployment, invalid deployment editPhase value 'BAD-EDIT-PHASE-VALUE'.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        if verbose: print '\n\nCreate deployment'

        # Fail to get assets due to invalid editPhase value.
        if verbose: print '\n\t(Negative) Create assets for the deployment'
        array, mooring, node, sensor = self.create_some_assets(editPhase='EDITTTTT', verbose=verbose)
        self.assertTrue(array is None)
        self.assertTrue(mooring is None)
        self.assertTrue(node is None)
        self.assertTrue(sensor is None)

        # Get some assets to use in new deployment.
        if verbose: print '\n\tCreate assets for deployment'
        array, mooring, node, sensor = self.create_some_assets(editPhase='EDIT', verbose=verbose)
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
        # Get data for deployment create.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = self.get_deployment_data_for_create(mooring_uid, node_uid, sensor_uid)
        data['editPhase'] = 'BAD-EDIT-PHASE-VALUE'
        if verbose: print '\n Invalid editPhase value for deployment: \'%s\', expect failure.' % data['editPhase']
        if debug:
            print '\n Create deployment data: '
            dump_dict(data, verbose)
            print '\n '

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Post deployment to uframe for update (host:12587/events/deployment)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n\t(Negative) Create actual deployment'
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_deployments_url_base()])
        if debug: print '\n debug -- Post url: ', url
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if debug:
            print '\n response.status_code: ', response.status_code
            if response.content:
                print '\n response.content: ', json.loads(response.content)
        self.assertEquals(response.status_code, 400)
        if verbose: print '\n\tProperly failed to create deployment, invalid deployment editPhase value \'%s\'.' % \
                          data['editPhase']
    '''

    def test_uframe_update_deployment(self):
        """
        Test update deployment.
        Scenario:
        Get existing deployment from uframe.
            modify contents,
            format for ui,
            issue ui update_deployment, expect success.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get a random deployment object from inventory
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        uframe_deployment = self.get_deployment(verbose=verbose)
        self.assertTrue(uframe_deployment is not None)
        self.assertTrue(isinstance(uframe_deployment, dict))
        self.assertTrue('eventId' in uframe_deployment)
        self.assertTrue(uframe_deployment['eventId'] is not None)
        self.assertTrue(isinstance(uframe_deployment['eventId'], int))
        deployment_id = uframe_deployment['eventId']
        self.assertTrue(deployment_id > 0)
        if debug:
            if uframe_deployment['location'] is not None:
                print '\n *******************************************************************************'
                print '\n debug -- Source deployment[location][depth]: ', uframe_deployment['location']['depth']
                dump_dict(uframe_deployment['location'], debug)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Compare deployment objects - deployment from inventory versus deployment by eventId.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Suggested:
        # verify deployment response from inventory and by eventId; look for equivalence in fields and values.

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Copy and update deployment object selected from deployment inventory (uframe_deployment).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        deployment = deepcopy(uframe_deployment)
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

        # Update data fields.
        # dataSource field.
        if deployment['dataSource'] is not None:
            deployment['dataSource'] = deployment['dataSource'] + data_source
        else:
            deployment['dataSource'] = data_source
        if debug: print '\n debug -- updated dataSource: ', deployment['dataSource']

        # deployedBy field.
        if deployment['deployedBy'] is not None:
            deployment['deployedBy'] = deployment['deployedBy'] + deployed_by
        else:
            deployment['deployedBy'] = deployed_by
        if debug: print '\n debug -- updated deployedBy: ', deployment['deployedBy']

        # orbitRadius field.
        if deployment['location'] is not None:
            if deployment['location']['orbitRadius'] is not None:
                if debug: print '\n updating orbitRadius, adding: ', orbit_radius
                deployment['location']['orbitRadius'] = deployment['location']['orbitRadius'] + orbit_radius
                if debug: print '\n updated deployment location orbitRadius: ', deployment['location']['orbitRadius']
            else:
                deployment['location']['orbitRadius'] = orbit_radius
        if debug: print '\n debug -- updated location orbitRadius: ', deployment['location']['orbitRadius']

        # versionNumber field.
        deployment['versionNumber'] = current_version_number
        #bkp_deployment = deepcopy(deployment)
        if debug:
            if deployment['location'] is not None:
                print '\n debug -- deployment[location][orbitRadius]: ', deployment['location']['orbitRadius']
                #dump_dict(deployment['location'], debug)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Format uframe deployment for ui, send as input to ui update_deployment.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ui_deployment = format_deployment_for_ui(deployment)
        if verbose:
            print '\n debug -- Update Deployment (ui_deployment) data for update: -----------------------'
            dump_dict(ui_deployment, debug)
        self.assertTrue(ui_deployment is not None)
        self.assertTrue(len(ui_deployment) > 0)
        url = url_for('uframe.update_deployment', event_id=deployment_id)
        response = self.client.put(url, data=json.dumps(ui_deployment), headers=headers)
        self.assertEquals(response.status_code, 200)
        ui_result = json.loads(response.data)
        self.assertTrue(ui_result is not None)
        self.assertTrue(isinstance(ui_result, dict))
        if debug: print '\n debug -- Updated deployment: event id: %d ' % deployment_id

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get updated uframe deployment using deployment eventId. (host:12587/events/id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(deployment_id)])
        response = requests.get(url, data=json.dumps(deployment), headers=headers)
        if debug:
            print '\n response.status_code: ', response.status_code
            #print '\n response.content: ', json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        updated_uframe_result = json.loads(response.content)
        self.assertTrue(updated_uframe_result is not None)
        self.assertTrue(isinstance(updated_uframe_result, dict))
        if verbose:
            print '\n debug -- Updated uframe deployment (updated_uframe_result) event_id: %d' % deployment_id
            dump_dict(updated_uframe_result, debug)

        # Check result structure. Note: Expecting location attribute to populated in this test.
        self.assertTrue('dataSource' in updated_uframe_result)
        self.assertTrue('deployedBy' in updated_uframe_result)
        self.assertTrue('location' in updated_uframe_result)
        self.assertTrue('orbitRadius' in updated_uframe_result['location'])
        self.assertTrue( updated_uframe_result['location']['orbitRadius'] is not None)
        if debug: print '\n debug ** Updated_result location orbitRadius: ', updated_uframe_result['location']['orbitRadius']
        self.assertTrue('versionNumber' in updated_uframe_result)

        # Verify fields have been updated as expected.
        self.assertTrue('dataSource' in deployment)
        self.assertTrue('deployedBy' in deployment)
        self.assertTrue('location' in deployment)
        self.assertTrue('orbitRadius' in deployment['location'])
        self.assertTrue( deployment['location']['orbitRadius'] is not None)
        if debug: print '\n debug ** deployment location orbitRadius: ', deployment['location']['orbitRadius']
        self.assertTrue('versionNumber' in deployment)

        self.assertEquals(deployment['dataSource'], updated_uframe_result['dataSource'])
        self.assertEquals(deployment['deployedBy'], updated_uframe_result['deployedBy'])
        self.assertEquals(deployment['location']['orbitRadius'], updated_uframe_result['location']['orbitRadius'])
        self.assertEquals(deployment['versionNumber'], updated_uframe_result['versionNumber'])

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Functions to assist in test cases.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_deployment(self, verbose=False):
        """
        Get uframe deployment.
        """
        debug = self.debug
        verbose = verbose

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
        # host:12587/events/deployment/inv/GS01SUMO/SBD11/04-DOSTAD000/1
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
        deployments_list = json.loads(response.content)
        self.assertTrue(deployments_list is not None)
        self.assertTrue(isinstance(deployments_list, list))
        self.assertTrue(len(deployments_list) > 0)
        if verbose: print '\n Have deployments list: ', deployments_list
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
            dump_dict(deployment, debug)
        return deployment

    def get_rd_with_empty_deployment(self, verbose=False):
        from ooiservices.app.uframe.toc_tools import get_toc_reference_designators
        debug = self.debug
        verbose = verbose
        rd_no_deployments = None

        # Get base deployment inventory url
        deployments_query_url, timeout, timeout_read = get_uframe_deployments_info()
        base_deployments_query_url = '/'.join([deployments_query_url, get_deployments_url_base(), 'query'])
        if debug: print '\n debug -- base_deployments_query_url: ', base_deployments_query_url

        # Get reference designators from toc
        reference_designators, toc_only, difference = get_toc_reference_designators()
        for refdes in reference_designators:
            query_suffix = '?refdes='+ refdes
            url = '/'.join([base_deployments_query_url, query_suffix])
            if debug: print '\n debug -- sensor deployments url: ', url
            response = requests.get(url, timeout=(timeout, timeout_read))
            self.assertEquals(response.status_code, 200)
            result = json.loads(response.content)
            self.assertTrue(result is not None)
            self.assertTrue(isinstance(result, list))
            if not result:
                rd_no_deployments = refdes
                break
        self.assertTrue(rd_no_deployments is not None)
        if debug: print '\n debug -- rd_no_deployments: ', rd_no_deployments

        return rd_no_deployments

    def create_some_assets(self, editPhase='EDIT', verbose=False):
        """
        Create assets using editPhase value passed in.
            If valid editPhase value, expect successful creation of asset.
            If invalid editPhase value, expect failure.
        """
        debug = self.debug
        verbose = verbose
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
        if 'notClassified' in asset_types:
            asset_types.remove('notClassified')
        for asset_type in asset_types:
            prefix = ''
            if editPhase not in deployment_edit_phase_values():
                prefix = '(Negative) '
            if verbose: print '\n\t%sCreate %s asset.' % (prefix, asset_type)
            data = self.get_basic_UI_asset_data(asset_type, editPhase=editPhase)
            url = url_for('uframe.create_asset')
            if debug: print '\n\tcreate url: ', url
            string_data = get_asset_input_as_string(data)
            data = json.dumps(string_data)
            response = self.client.post(url, headers=headers, data=data)

            # Valid editPhase value.
            if editPhase in deployment_edit_phase_values():
                if verbose: print '\n\t\tValid editPhase value \'%s\' for %s asset.' % (editPhase, asset_type)
                if response.status_code != 201:
                    print '\n\tcreate_some_assets -- response.status_code: ', response.status_code
                    if response.data:
                        response_data = json.loads(response.data)
                        print '\n\tcreate_some_assets -- response_data: ', response_data
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
                if verbose: print '\n\t\tCreated asset id/uid: %d/%s' % (asset_id, asset_uid)

            # Invalid editPhase value.
            else:
                if verbose: print '\n\t\tInvalid editPhase value \'%s\' for %s asset.' % (editPhase, asset_type)
                self.assertEquals(response.status_code, 400)
                if debug:
                    response_data = json.loads(response.data)
                    print '\n\tresponse_data: ', response_data
                if verbose: print '\n\t\tFailed (as planned) to created asset with editPhase %s.' % editPhase

        return array, mooring, node, sensor


    def get_basic_UI_asset_data(self, type, editPhase=None):
        self.assertTrue(editPhase is not None)
        #self.assertTrue(editPhase in deployment_edit_phase_values())
        debug = False
        uid_suffix = str(randint(100,1000))
        unique_int = randint(1000,5000)
        description = type + '-' + str(unique_int)
        small_int = randint(1,10)
        data = {
          'events': [],
          'assetInfo': {
            'array': 'some vocabulary array',
            'assembly': 'some assembly name',
            'asset_name': 'CE01ISSM-RID16-07-NUTNRB000',
            'description': description,
            'longName': 'some vocabulary long name',
            'maxdepth': 0,
            'mindepth': 0,
            'name': 'some vocabulary name',
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
            'serialNumber': 'CE01ISSM-' + str(unique_int),
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
          'ref_des': 'CE01ISSM-RID16-07-NUTNRB000',
          'remoteResources': [],
          'tense': 'UNKNOWN',
          'uid': '2016-09-21:'+ self.asset_uid_root + uid_suffix + '-' + str(small_int),
          'editPhase': editPhase
        }
        # original: CP03ISSM-MFD37-00-DCLENG000
        # 'CE01ISSM-RID16-07-NUTNRB000'
        if type in ['Array', 'Mooring', 'Node', 'Sensor']:
            data['assetType'] = type
        if type == 'Sensor':
            if debug: print '\n debug -- Adding calibration since type is %s' % type
            data['calibration'] = []

        self.assertTrue(data is not None)
        return data

    def get_deployment_data_for_create(self, mooring_uid, node_uid, sensor_uid):
        # uframe create deployment data.

        #self.assertTrue(mooring_uid is not None)
        #self.assertTrue(node_uid is not None)
        #self.assertTrue(sensor_uid is not None)
        unique_int = randint(2000, 3000)
        small_unique_int = randint(10,20)
        medium_unique_int = randint(300,400)
        large_unique_int = randint(20000,50000)
        deployedBy = 'Deployed by test engineer on ' + str(datetime.datetime.now())
        eventStartTime = 1506434330000 + large_unique_int + medium_unique_int
        eventStopTime = eventStartTime + large_unique_int + small_unique_int
        versionNumber = randint(2,10) * 2
        deployment_data = {
              '@class' : '.XDeployment',
              'rd' : 'CP01CNSP-SP001-08-CTDPFJ000',
              'deploymentNumber': unique_int + medium_unique_int + small_unique_int,
              'versionNumber': versionNumber,
              'mooring_uid': mooring_uid,
              'node_uid': node_uid,
              'sensor_uid': sensor_uid,
              'deployCruiseInfo': None,
              'deployedBy': deployedBy,
              'recoverCruiseInfo': None,
              'recoveredBy': 'Recovered by test engineer.' + str(unique_int) + str(datetime.datetime.now()),
              'eventType': 'DEPLOYMENT',
              'eventName': 'event name' + str(datetime.datetime.now()),
              'eventStartTime': eventStartTime,
              'eventStopTime':  eventStopTime,
              'ingestInfo': None,
              'dataSource': 'test ' + str(datetime.datetime.now()),
              'tense': None,
              'assetUid': None,
              'depth': float(small_unique_int * 1.33),
              'longitude': -70.7701,
              'latitude': 40.1341,
              'orbitRadius': 30.0,
              'inductiveId': None,
              'notes': str(datetime.datetime.now()) + ' notes'

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

    def get_minimum_deployment_data_for_create(self, mooring_uid, node_uid, sensor_uid):
        # uframe create deployment data.

        #self.assertTrue(mooring_uid is not None)
        #self.assertTrue(node_uid is not None)
        #self.assertTrue(sensor_uid is not None)
        unique_int = randint(2000, 3000)
        small_unique_int = randint(10,20)
        medium_unique_int = randint(300,400)
        large_unique_int = randint(20000,50000)
        deployedBy = 'Deployed by test engineer on ' + str(datetime.datetime.now())
        eventStartTime = 1506434330000 + large_unique_int + medium_unique_int
        eventStopTime = eventStartTime + large_unique_int + small_unique_int
        versionNumber = randint(2,10) * 2
        deploymentNumber = randint(50,99)
        deploymentNumber = 50
        deployment_data = {
              '@class' : '.XDeployment',
              'rd' : 'CP01CNSP-SP001-08-CTDPFJ000',
              'deploymentNumber': deploymentNumber,
              'versionNumber': versionNumber,
              'mooring_uid': mooring_uid,
              'node_uid': node_uid,
              'sensor_uid': sensor_uid,
              'deployCruiseInfo': None,
              'deployedBy': None,
              'recoverCruiseInfo': None,
              'recoveredBy': None,
              'eventType': 'DEPLOYMENT',
              'eventName': str(datetime.datetime.now()),
              'eventStartTime': None,
              'eventStopTime':  None,
              'ingestInfo': None,
              'dataSource': None,
              'tense': None,
              'assetUid': None,
              'depth': None,
              'longitude': None,
              'latitude': None,
              'orbitRadius': None,
              'inductiveId': None,
              'notes': None
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

'''
    def get_rd_with_empty_deployment(self, verbose=False):
        debug = self.debug
        verbose = verbose
        rd_no_deployments = None

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

        # Get base deployment inventory url
        deployments_query_url, timeout, timeout_read = get_uframe_deployments_info()
        base_deployments_query_url = '/'.join([deployments_query_url, get_deployments_url_base(), 'query'])
        print '\n debug -- base_deployments_query_url: ', base_deployments_query_url
        for subsite in subsite_list:

            # Get deployment/inv/{subsite} (list)
            get_nodes_url = '/'.join([base_url, subsite])
            if verbose: print '\n Get node list ----- url: ', get_nodes_url
            response = requests.get(get_nodes_url, timeout=(timeout, timeout_read))
            self.assertEquals(response.status_code, 200)
            node_list = json.loads(response.content)
            self.assertTrue(node_list is not None)
            self.assertTrue(isinstance(node_list, list))
            self.assertTrue(len(node_list) > 0)
            if debug: print '\n debug -- Have node list: ', node_list

            for node in node_list:
                # Get deployment/inv/{subsite}/{node} (list)
                get_sensors_url = '/'.join([base_url, subsite, node])
                if verbose: print '\n Get sensor list ----- url: ', get_sensors_url
                response = requests.get(get_sensors_url, timeout=(timeout, timeout_read))
                self.assertEquals(response.status_code, 200)
                sensor_list = json.loads(response.content)
                self.assertTrue(sensor_list is not None)
                self.assertTrue(isinstance(sensor_list, list))
                self.assertTrue(len(sensor_list) > 0)
                if debug: print '\n debug -- Have sensor list: ', sensor_list

                for sensor in sensor_list:
                    refdes = '-'.join([subsite, node, sensor])
                    query_suffix = '?refdes='+ refdes
                    url = '/'.join([base_deployments_query_url, query_suffix])
                    print '\n debug -- sensor deployments url: ', url
                    response = requests.get(url, timeout=(timeout, timeout_read))
                    self.assertEquals(response.status_code, 200)
                    result = json.loads(response.content)
                    self.assertTrue(result is not None)
                    self.assertTrue(isinstance(result, list))
                    if not result:
                        rd_no_deployments = subsite
                        break


        self.assertTrue(rd_no_deployments is not None)
        print '\n debug -- rd_no_deployments: ', rd_no_deployments


        """
        if verbose: print '\n Get a random subsite, node, sensor and fetch deployments.'
        # host:12587/events/deployment/inv/GS01SUMO/SBD11/04-DOSTAD000/1
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
            dump_dict(deployment, debug)
        """
        return rd_no_deployments
'''