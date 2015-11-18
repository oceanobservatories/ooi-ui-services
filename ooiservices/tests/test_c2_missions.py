#!/usr/bin/env python
'''
Specific testing for Command and Control (C2)
'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
import datetime as dt
from unittest import skipIf
import os

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class CommandAndControlTestCase(unittest.TestCase):

    # enable verbose during development and documentation to get a list of sample
    # urls used throughout test cases. Always set to False before check in.
    verbose = False
    root = 'http://localhost:4000'
    content_type = 'application/json'
    headers = None
    valid_items = ['status', 'next_run', 'name', 'created', 'drivers', 'schedule', 'mission', 'mission_id',
                   'running', 'state', 'version', 'run_count', 'active', 'events', 'desc']

    status_items = ['Inactive', 'Loaded', 'Running']
    state_items = ['Active', 'Inactive']
    test_missions = ['mission100', 'mission200', 'mission300']

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
        cc_scope = UserScope.query.filter_by(scope_name='command_control').first()
        admin.scopes.append(scope)
        admin.scopes.append(cc_scope)
        db.session.add(admin)
        db.session.commit()

        self.headers = self.get_api_headers('admin', 'test')

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

    def get_api_post_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

    def test_add_c2_missions(self):
        """
        Add test missions; this adds missions defined in self.test_missions.
        """
        self.delete_test_missions()
        self.create_test_missions()

    def test_zdelete_c2_missions(self):
        """
        Cleanup test missions; this deletes missions defined in self.test_missions.
        This test shall be run as the last test case (hence the 'z' in the test case name).
        """
        self.delete_test_missions()

    def test_c2_missions_get(self):
        """
        Get all missions.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        mission_ids = []
        active_mission_ids = []
        inactive_mission_ids = []

        # Get missions
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        active_missions = False
        inactive_missions = False
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)
            if verbose:
                print '\n mission_id: ', mission['mission_id']
                print '\n mission[active]: ', mission['active']
                print '\n mission[state]: ', mission['state']
            if mission['active']:
                active_missions = True
                active_mission_ids.append(mission['mission_id'])
            else:
                inactive_missions = True
                inactive_mission_ids.append(mission['mission_id'])


        # If there are no active missions, but more than one inactive_missions, then
        # activate one of the inactive missions and continue.
        self.assertTrue(len(mission_ids) > 0)
        if not active_missions and len(inactive_mission_ids) > 1:
            mission_to_activate = inactive_mission_ids[0]
            if verbose: print '\n ------------------------ activate mission: ', mission_to_activate

            # Get mission
            url = url_for('main.c2_get_mission', mission_id=mission_to_activate)
            response = self.client.get(url,content_type=self.content_type, headers=self.headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('mission' in data)
            inactive_mission_data = data['mission']
            if verbose:
                print '\n inactive_mission_data[state]: ', inactive_mission_data['state']
                print '\n inactive_mission_data[status]: ', inactive_mission_data['status']
                print '\n inactive_mission_data[active]: ', inactive_mission_data['active']
                print '\n inactive_mission_data[running]: ', inactive_mission_data['running']

            self.assertEquals(inactive_mission_data['state'], 'Inactive')
            self.assertEquals(inactive_mission_data['status'], 'Inactive')
            self.assertEquals(inactive_mission_data['active'], False)
            self.assertEquals(inactive_mission_data['running'], False)

            # Activate a mission which is currently inactive
            url = url_for('main.c2_activate_mission', mission_id=mission_to_activate)
            response = self.client.get(url,content_type=self.content_type, headers=self.headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('mission' in data)

            # Verify mission is now active
            if verbose: print '\n ------------------------ verify mission is active'
            url = url_for('main.c2_get_mission', mission_id=mission_to_activate)
            response = self.client.get(url,content_type=self.content_type, headers=self.headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('mission' in data)
            mission = data['mission']
            self.assertEquals(mission['active'], True)
            self.assertEquals(mission['state'], 'Active')
            active_missions = True

        # Get mission which are active using request.args
        if verbose: print '\n ------------------------ if active mission... '
        if active_missions:
            if verbose: print '\n active_missions...'
            # Get 'Active' missions (?active=True)
            url = url_for('main.c2_get_missions')
            url += '?active=True'
            response = self.client.get(url,content_type=self.content_type, headers=self.headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('missions' in data)
            self.assertTrue(len(data['missions']) > 0)

        # Get mission which are inactive using request.args
        if verbose: print '\n ------------------------ if inactive mission... ',
        if inactive_missions:
            # Get 'Inactive' missions (?active=False)
            if verbose: print '\n inactive_missions...'
            url = url_for('main.c2_get_missions')
            url += '?active=False'
            response = self.client.get(url,content_type=self.content_type, headers=self.headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('missions' in data)
            self.assertTrue(len(data['missions']) > 0)

    def test_c2_mission_get(self):
        """
        Get a single mission.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        #content_type = 'application/json'
        #headers = self.get_api_headers('admin', 'test')

        self.create_test_missions()
        ids, names = self.get_mission_information()

        # Get mission
        self.assertTrue(len(ids)>0)
        url = url_for('main.c2_get_mission', mission_id=ids[0])
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)
        mission = data['mission']
        self.assertTrue(len(data) > 0)
        for item in self.valid_items:
            self.assertTrue(item in mission)

        # Validate Mission element 'mission'
        self.assertTrue('mission' in mission)
        self.assertTrue(isinstance(mission['mission'], list))

        # (Negative) Get non-existent mission, expect failure
        bad_id = 999
        url = url_for('main.c2_get_mission', mission_id=bad_id)
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(len(data) > 0)
        self.assertTrue('message' in data)
        self.assertTrue(len(data['message']) > 0)

    def test_c2_mission_activate(self):
        """
        Activate a mission.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        # Get missions information
        if verbose: print '\n get_mission_information'
        mission_ids, names = self.get_mission_information()

        url = url_for('main.c2_get_missions')
        url += '?active=False'
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            for item in self.valid_items:
                self.assertTrue(item in mission)

        if verbose: print '\n mission_ids: ', mission_ids
        self.assertTrue(len(mission_ids) > 0)
        mission_id = mission_ids[0]

        # Activate mission
        if verbose: print '\n Activate mission: ', mission_id
        url = url_for('main.c2_activate_mission', mission_id=mission_id)
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)
        mission = data['mission']
        self.assertTrue(len(mission) > 0)
        for item in self.valid_items:
            self.assertTrue(item in mission)

        # Get value of active and running from data['mission']
        if verbose: print '\n Get values: active, running; set state and status for \'%s\'' % mission_id
        active = mission['active']
        running = mission['running']
        version = mission['version']
        status = mission['status']
        state = mission['state']
        if verbose:
            print '\n active: ', active
            print '\n running: ', running
            print '\n version: ', version
            print '\n mission[status]: ', mission['status']
            print '\n mission[state]: ', mission['state']
        self.assertTrue(status is not None)
        self.assertTrue(state is not None)
        self.assertTrue(status in self.status_items)
        self.assertTrue(state in self.state_items)
        self.assertEquals(state, 'Active')

    def test_c2_mission_deactivate(self):
        """
        Deactivate a mission.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n test_c2_mission_deactivate...'

        # Get missions information
        if verbose: print '\n get_mission_information'
        mission_ids, names = self.get_mission_information()
        self.assertTrue(len(mission_ids) > 0)

        url = url_for('main.c2_get_missions')
        url += '?active=True'
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)

        missions = data['missions']
        active_mission_ids = []
        for mission in missions:
            for item in self.valid_items:
                self.assertTrue(item in mission)
            if mission['name'] in self.test_missions:
                if not mission['running']:
                    active_mission_ids.append(mission['mission_id'])

        self.assertTrue(len(active_mission_ids) > 0)

        # Deactivate mission (mission_id)
        mission_id = None
        if len(active_mission_ids) > 0:
            if verbose: print '\n Located active missions(%d): %s' % (len(active_mission_ids), active_mission_ids)
            mission_id = active_mission_ids[0]

            # Get mission
            if verbose: print '\n Get mission: ', mission_id
            url = url_for('main.c2_get_mission', mission_id=mission_id)
            response = self.client.get(url,content_type=self.content_type, headers=self.headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('mission' in data)
            mission = data['mission']
            self.assertTrue(len(mission) > 0)
            if mission['active']:
                if verbose: print '\n deactivating mission_id: ', mission_id
                url = url_for('main.c2_deactivate_mission', mission_id=mission_id)
                response = self.client.get(url,content_type=self.content_type, headers=self.headers)
                if verbose: print '\n response.status_code: ', response.status_code
                data = json.loads(response.data)
                if verbose: print '\n data: ', data
                self.assertEquals(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue('mission' in data)
                mission = data['mission']
                self.assertTrue(len(mission) > 0)
                for item in self.valid_items:
                    self.assertTrue(item in mission)

                # Get value of active and running from data['mission']
                active = mission['active']
                running = mission['running']
                version = mission['version']
                status = mission['status']
                state = mission['state']
                if verbose:
                    print '\n active: ', active
                    print '\n running: ', running
                    print '\n version: ', version
                    print '\n mission[status]: ', mission['status']
                    print '\n mission[state]: ', mission['state']
                self.assertTrue(status is not None)
                self.assertTrue(state is not None)
                self.assertTrue(status in self.status_items)
                self.assertTrue(state in self.state_items)
                self.assertEquals(state, 'Inactive')

    def _test_c2_mission_add_negative(self):
        """
        Add a mission with invalid contents.
        """
        verbose = True #self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')

        # get current missions - before
        if verbose: print '\n get_mission_information...before'
        mission_ids, mission_names = self.get_mission_information()
        self.assertTrue(len(mission_ids) > 0)
        self.assertTrue(len(mission_names) > 0)

        # (Negative) Add mission with invalid (nonexistent reference designator)
        mission_name = 'mission100_bad'
        mission_data = self.read_store(mission_name)
        url = url_for('main.c2_add_mission')
        if verbose: print '\n url: ', url
        try:
            response = self.client.post(url, content_type=self.content_type, headers=self.headers, data=mission_data)
            if verbose: print '\n response.status_code: ', response.status_code
            self.assertTrue(response.status_code != 201)
            if verbose: print '\n (add) response: ', json.loads(response.data)
        except Exception as err:
            if verbose: print '\n exception: ', err.message
            self.assertEquals('exception: ', err.message)

        # (Negative) Add mission Mission minus required fields (version, drivers, error_policy
        mission_name = 'mission200_bad'
        mission_data = self.read_store(mission_name)
        url = url_for('main.c2_add_mission')
        if verbose: print '\n (add2) url: ', url
        response = self.client.post(url, content_type=self.content_type, headers=self.headers, data=mission_data)
        self.assertEquals(response.status_code, 400 )

        # Get current missions - after
        if verbose: print '\n get_mission_information...after'
        mission_ids_after, mission_names_after = self.get_mission_information()
        self.assertTrue(len(mission_ids_after) > 0)
        self.assertTrue(len(mission_names_after) > 0)
        self.assertEqual(mission_ids_after, mission_ids)
        self.assertEqual(mission_names_after, mission_names)

    def test_c2_mission_delete(self):
        """
        Delete one or more mission objects.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        if verbose: print '\n -- test_c2_mission_delete...\n'
        self.delete_test_missions()
        self.create_test_missions()
        self.delete_test_missions()

        mission_ids = []
        mission_names = []
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        current_number_of_missions = len(missions)
        if verbose:
            print '\n After delete...'
            print '\n Current number of missions: ', current_number_of_missions

        for mission in missions:
            mission_ids.append(mission['mission_id'])
            mission_names.append(mission['name'])

        for name in self.test_missions:
            if name in mission_names:
                message = 'Failed to delete mission: %s' % name
                self.assertEquals('exception', message)

        if verbose:
            ids, names = self.get_mission_information()
            self.assertEquals(len(ids), len(names))
            print '\n get_mission_information: '
            print '\n ids: ', ids
            print '\n names: ', names

    def test_c2_mission_versions(self):
        """
        Get a mission's versions.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        mission_name = 'mission300'
        self.create_test_missions()
        ids, names = self.get_mission_information()

        if mission_name not in names:
            message = 'mission_name (%s) not available.' % mission_name
            self.assertEquals('exception', message)

        # Get id for mission with name == 'mission300'
        mission_id = self.get_mission_id(mission_name)
        if mission_id is None:
            print '\n (VERSION) mission_id not found...'
            return

        # Get mission versions
        self.assertTrue(len(ids)>0)
        url = url_for('main.c2_mission_versions', mission_id=mission_id)
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('versions' in data)
        versions = data['versions']
        self.assertTrue(versions > 0)
        number_of_versions = len(versions)
        if verbose: print '\n number_of_versions: ', number_of_versions
        self.create_test_mission_versions()

        # Get mission versions
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('versions' in data)
        versions = data['versions']
        self.assertTrue(len(versions) > 0)
        number_of_versions = len(versions)
        if verbose: print '\n number_of_versions: ', number_of_versions

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# helper functions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_mission_information(self):
        """
        Get lists of missions ids and mission names, return both lists.
        """
        verbose = self.verbose
        root = self.root
        mission_ids = []
        mission_names = []

        # Get missions
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        current_number_of_missions = len(missions)
        if verbose: print '\n Number of missions: ', current_number_of_missions
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            mission_names.append(mission['name'])

        return mission_ids, mission_names

    def read_store(self, filename):
        """
        open filename, read data, close file and return data
        """
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
        c2_data_path = os.path.join(APP_ROOT, 'c2data')
        try:
            tmp = "/".join([c2_data_path, filename])
            f = open(tmp, 'rb')
            data = f.read()
            f.close()
        except Exception, err:
            raise Exception('%s' % err.message)
        return data

    def create_test_missions(self):
        """
        Create test mission [objects] for test cases.
        mission_ids: ['test_mission100', 'test_mission200', 'test_mission300']
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        mission_ids = []
        mission_names = []

        if verbose: print '\n Create test missions...\n'
        # Get current number of missions (current_number_of_missions)
        if verbose: print '\n Get current number of missions (current_number_of_missions)'
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        current_number_of_missions = len(data['missions'])
        if verbose: print '\n (CREATE) Current number of missions: ', current_number_of_missions

        for mission in data['missions']:
            mission_ids.append(mission['mission_id'])
            mission_names.append(mission['name'])

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add new missions
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add set of test missions
        if verbose: print '\n (CREATE) Add set of test missions'
        for filename in self.test_missions:
            if verbose: print '\n Processing filename: ', filename
            if filename not in mission_names:
                if verbose: print '\n\tAdd filename: ', filename
                data = self.read_store(filename)
                # Add mission
                url = url_for('main.c2_add_mission')
                try:
                    response = self.client.post(url, content_type=self.content_type, headers=self.headers, data=data)
                    if response.status_code != 201:
                        message = '(%d) Failed to add new mission (%s)' % (response.status_code, filename)
                        raise Exception(message)
                except Exception as err:
                    if verbose: print '\n *** exception: ', err.message
                    self.assertEquals('exception: ', err.message)

                # Get missions after adding test missions
                url = url_for('main.c2_get_missions')
                response = self.client.get(url,content_type=self.content_type, headers=self.headers)
                self.assertEquals(response.status_code, 200)
                response_data = json.loads(response.data)
                self.assertTrue('missions' in response_data)
                self.assertTrue(len(response_data['missions']) > 0)
                if verbose: print '\n\tNew number of missions: ', len(response_data['missions'])

        # Get missions after adding test missions
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)

        # Verify number of missions has been increased by number of test missions created.
        number_of_all_missions = len(data['missions'])
        if verbose:
            print '\n (CREATE) current_number_of_missions: ', current_number_of_missions
            print '\n (CREATE) number_of_all_missions: ', number_of_all_missions
            print '\n (CREATE) len(create_mission_ids): ', len(self.test_missions)
        if current_number_of_missions != number_of_all_missions:
            self.assertEquals((number_of_all_missions - current_number_of_missions), len(self.test_missions))

    def delete_test_missions(self):
        """
        Create test mission [objects] for test cases.
        mission_ids: ['test_mission100', 'test_mission200', 'test_mission300']
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        mission_names = []

        if verbose: print '\n Delete test missions...\n'
        # Get current number of missions (current_number_of_missions)
        if verbose: print '\n Getting current number of missions before delete...'
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        missions_before_delete = len(data['missions'])
        if verbose: print '\n Number of missions before delete: ', missions_before_delete

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Delete test missions
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        missions_dict = {}
        for mission in data['missions']:
            mission_names.append(mission['name'])
            missions_dict[mission['name']] = mission['mission_id']

        # Delete test missions if they currently exist...
        delete_count = 0
        for filename in self.test_missions:
            if verbose: print '\n delete mission: ', filename
            if filename in mission_names:
                try:
                    mission_id = missions_dict[filename]
                    url = url_for('main.c2_delete_mission', mission_id=mission_id)
                    response = self.client.get(url, content_type=self.content_type, headers=self.headers)
                    self.assertEquals(response.status_code, 200)
                    if verbose: print '\n\t deleted (%d)' % response.status_code
                    delete_count += 1
                    if response.data:
                        data = json.loads(response.data)
                        self.assertEquals(len(data), 0)
                except Exception as err:
                    if verbose: print '\n *** err.message: ', err.message
                    self.assertEquals('exception: ', err.message)

        # Get missions information...
        # Get current number of missions (current_number_of_missions)
        if verbose: print '\n Getting number of missions after delete...'
        ids, names = self.get_mission_information()
        current_number_of_missions = len(ids)
        if verbose:
            print '\n (DELETE) Summary:'
            print '\n\tNumber of missions before delete: ', missions_before_delete
            print '\n\tNumber of missions after delete: ', current_number_of_missions
            print '\n\tNumber of missions deleted: ', delete_count

    def create_test_mission_versions(self):
        """
        Create test mission with multiple versions.
        Use mission300 - create 5 versions
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        mission_ids = []
        mission_name = 'mission300'
        mission_filenames = ['mission300_v1', 'mission300_v2', 'mission300_v3', 'mission300_v4']

        # Get id for mission with name == 'mission300'
        mission_id = self.get_mission_id(mission_name)
        if mission_id is None:
            print '\n (VERSION) mission_id not found...'
            return

        if verbose: print '\n mission_id: ', mission_id
        # Get current number of mission versions (current_number_of_versions)
        if verbose: print '\n Create test mission versions...\n'
        if verbose: print '\n Get current number of versions (current_number_of_versions)'
        url = url_for('main.c2_mission_versions', mission_id=mission_id)
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('versions' in data)
        current_number_of_versions = len(data['versions'])
        if verbose: print '\n (VERSION) Current number of versions: ', current_number_of_versions

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add new versions
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add set of test missions
        if verbose: print '\n (VERSION) Add mission versions'
        for filename in mission_filenames:
            if verbose: print '\n\tAdd version filename: ', filename
            data = self.read_store(filename)
            # Add mission version
            url = url_for('main.c2_add_mission')
            try:
                response = self.client.post(url, content_type=self.content_type, headers=self.headers, data=data)
                if response.status_code != 201:
                    message = '(%d) Failed to add new mission (%s)' % (response.status_code, filename)
                    if verbose: print '\n message: ', message
                    raise Exception(message)
            except Exception as err:
                if verbose: print '\n *** exception: ', err.message
                self.assertEquals('exception: ', err.message)


            # Get mission versions after adding test missions
            url = url_for('main.c2_mission_versions', mission_id=mission_id)
            response = self.client.get(url,content_type=self.content_type, headers=self.headers)
            self.assertEquals(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertTrue('versions' in response_data)
            self.assertTrue(len(response_data['versions']) > 0)
            if verbose: print '\n\tNew number of versions: ', len(response_data['versions'])

        # Get mission versions after adding test missions
        url = url_for('main.c2_mission_versions', mission_id=mission_id)
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('versions' in data)
        self.assertTrue(len(data['versions']) > 0)
        versions = data['versions']

        # Verify number of missions has been increased by number of test missions created.
        number_of_all_versions = len(versions)
        if verbose:
            print '\n (VERSION) current_number_of_missions: ', current_number_of_versions
            print '\n (VERSION) number_of_all_missions: ', number_of_all_versions
            print '\n (VERSION) len(create_mission_ids): ', len(self.test_missions)
        if current_number_of_versions != number_of_all_versions:
            self.assertEquals((number_of_all_versions - current_number_of_versions), len(self.test_missions))

    def get_mission_id(self, mission_name):
        """
        Return id for mission-name; if not not found return None.
        """
        verbose = self.verbose
        id = None
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=self.content_type, headers=self.headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        current_number_of_missions = len(missions)
        if verbose: print '\n Number of missions: ', current_number_of_missions
        for mission in missions:
            if mission['name'] == mission_name:
                id = mission['mission_id']
                break
        return id