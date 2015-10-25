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
    valid_items = ['status', 'state', 'name', 'mission', 'mission_id', 'desc',
                   'active', 'running', 'version', 'drivers'] #, 'current_step']

    status_items = ['Inactive', 'Loaded', 'Running']
    state_items = ['Active', 'Inactive']

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

    def create_test_missions(self):
        """
        Create test mission [objects] for test cases.
        mission_ids: ['test_mission100', 'test_mission200', 'test_mission300']
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        create_mission_ids = ['test_mission100', 'test_mission200', 'test_mission300']
        mission_ids = []
        current_number_of_missions = 0

        # Get current number of missions (current_number_of_missions)
        if verbose: print '\n Get current number of missions (current_number_of_missions)'
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        current_number_of_missions = len(data['missions'])
        for mission in data['missions']:
            mission_ids.append(mission['mission_id'])

        # Add set of test missions
        if verbose: print '\n Add set of test missions'
        for mission_id in create_mission_ids:
            if mission_id not in mission_ids:
                d = {
                    'name': mission_id,
                    'desc': 'Hydrate Ridge photos using Digital Still Camera (scheduled).',
                    'version': '1-01',
                    'drivers': ['RS01SUM1-MJ01B-05-CAMDSB103'],
                    'schedule': {'hour': '0,6,12,18'},
                    'error_policy': {'type': 'abort'},
                    'debug': True,
                    'mission': {
                        'type': 'block',
                        'sequence': [
                            {'execute': 'RS01SUM1-MJ01B-05-CAMDSB103', 'command': 'start_autosample'},
                            {'sleep': 2.5},
                            {'set': 'RS01SUM1-MJ01B-05-CAMDSB103', 'parameter': 'p1', 'value': 5},
                            {'type': 'block', 'sequence': [{'sleep': 2.5}]},
                        ]
                    },
                    'blocks': [
                        {'type': 'block', 'label': 'capture', 'sequence': []},
                    ],
                }

                # Add mission
                print '\n (add) mission_id: ', mission_id
                url = url_for('main.c2_add_mission')
                if verbose: print '\n url: ', url
                try:
                    response = self.client.post(url, content_type=content_type, headers=headers, data=json.dumps(d))
                    if verbose: print '\n (add) response: ', json.loads(response.data)
                except Exception as err:
                    if verbose: print '\n *** exception: ', err.message
                    self.assertEquals('exception: ', err.message)

         # Get missions after adding test missions
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
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
            print '\n current_number_of_missions: ', current_number_of_missions
            print '\n number_of_all_missions: ', number_of_all_missions
            print '\n len(create_mission_ids): ', len(create_mission_ids)
        if current_number_of_missions != number_of_all_missions:
            self.assertEquals((number_of_all_missions - current_number_of_missions), len(create_mission_ids))

    def _test_add_c2_missions(self):
        """
        Add test missions; this must be the first test case to run!
        """
        self.create_test_missions()

    def _test_c2_missions_get(self):
        """
        Get all missions.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_ids = []
        active_mission_ids = []
        inactive_mission_ids = []

        # Get missions
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
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
            response = self.client.get(url,content_type=content_type, headers=headers)
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
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('mission' in data)

            # Verify mission is now active
            if verbose: print '\n ------------------------ verify mission is active'
            url = url_for('main.c2_get_mission', mission_id=mission_to_activate)
            response = self.client.get(url,content_type=content_type, headers=headers)
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
            response = self.client.get(url,content_type=content_type, headers=headers)
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
            response = self.client.get(url,content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('missions' in data)
            self.assertTrue(len(data['missions']) > 0)

    def _test_c2_mission_get(self):
        """
        Get a single mission.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_name = 'test_mission100'

        # Get mission
        url = url_for('main.c2_get_mission', mission_id=mission_name)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)
        mission = data['mission']
        self.assertTrue(len(data) > 0)
        for item in self.valid_items:
            self.assertTrue(item in mission)

        # Validate Mission object 'mission' type (is script dict or str)
        # todo - Upstream server update - mission entry is str not dict
        self.assertTrue(isinstance(mission['mission'], dict))
        #self.assertTrue(isinstance(mission['mission'], str))

        # (Negative) Get non-existant mission, expect failure
        bad_name = 'unknown'
        url = url_for('main.c2_get_mission', mission_id=bad_name)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue(len(data) > 0)
        self.assertTrue('message' in data)
        self.assertTrue(len(data['message']) > 0)


    def _test_c2_mission_activate(self):
        """
        Activate a mission.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_id = 'test_mission100'
        mission_ids = []

        # Get missions
        if verbose: print '\n Get missions'
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)

        if verbose: print '\n mission_ids: ', mission_ids
        self.assertTrue(mission_id in mission_ids)

        # Activate mission
        if verbose: print '\n Activate mission: ', mission_id
        url = url_for('main.c2_activate_mission', mission_id=mission_id)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)

        # Get mission
        if verbose: print '\n Get mission: ', mission_id
        url = url_for('main.c2_get_mission', mission_id=mission_id)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)
        mission = data['mission']
        self.assertTrue(len(data) > 0)
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

    def _test_c2_mission_deactivate(self):
        """
        Deactivate a mission.
        """
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_id = 'test_mission100'
        mission_ids = []

        # Get missions
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)

        if verbose: print '\n mission_ids: ', mission_ids
        self.assertTrue(mission_id in mission_ids)

        # Deactivate mission (mission_id)
        url = url_for('main.c2_deactivate_mission', mission_id=mission_id)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        #print '\n data: ', data
        self.assertTrue('mission' in data)

        # Get mission and verify 'active' == Inactive
        url = url_for('main.c2_get_mission', mission_id=mission_id)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)
        mission = data['mission']
        self.assertTrue(len(data) > 0)
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


    def _test_c2_mission_add(self):
        """
        Add a mission.
        """
        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        delete_route_supported = False
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_ids = []
        mission_id = 'test_mission900'

        d = {
            'name': mission_id,
            'desc': 'Hydrate Ridge photos using Digital Still Camera (scheduled).',
            'version': '9-01',
            'drivers': ['RS01SUM1-MJ01B-05-CAMDSB103'],
            'schedule': {'hour': '0,6,12,18'},
            'error_policy': {'type': 'abort'},
            'debug': True,
            'mission': {
                'type': 'block',
                'sequence': [
                    {'execute': 'RS01SUM1-MJ01B-05-CAMDSB103', 'command': 'start_autosample'},
                    {'sleep': 2.5},
                    {'set': 'RS01SUM1-MJ01B-05-CAMDSB103', 'parameter': 'p1', 'value': 5},
                    {'type': 'block', 'sequence': [{'sleep': 2.5}]},
                ]
            },
            'blocks': [
                {'type': 'block', 'label': 'capture', 'sequence': []},
            ],
        }

        bench = {
                    'blocks': [
                        {
                            'label': 'mission',
                            'sequence': [
                                {
                                  { 'block_name': 'initialize'},
                                  { 'discover':  'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'get_state': 'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'execute':   'RS10ENGC-XX00X-00-BOTPTA001', 'command': 'DRIVER_EVENT_START_AUTOSAMPLE'}
                                }
                            ]
                        },
                        {
                            'label': 'initialize',
                            'sequence': [
                                {
                                  { 'reset': 'initialize' , 'timeout': 'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'sleep': 'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'set_init_params':   'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'config':
                                        { 'parameters':
                                            {
                                              'relevel_timeout': 600,
                                              'auto_relevel':    False,
                                              'heat_duration':   1,
                                              'output_rate_hz':  20,
                                              'xtilt_relevel_trigger': 300.00,
                                              'ytilt_relevel_trigger': 300.00

                                            }
                                        }
                                   }
                                }
                              ]
                        }
                      ],
                     'debug': True,
                     'drivers': ['RS10ENGC-XX00X-00-BOTPTA001'],
                     'error_policy': {'type': 'abort'},
                     'name': 'configure_bench_botpt',
                     'desc': 'Configure the bench BOTPT and place it in AUTOSAMPLE',
                     'version': '1-00'
                }


        # get current missions
        if verbose: print '\n get current missions...'
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)
        if verbose: print '\n mission_ids: ', mission_ids

        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        if delete_route_supported:
            if mission_id in mission_ids:
                if verbose:
                    print '\n\n ----- %s found in list of missions....' % mission_id
                    print '\n ----- delete current mission_id: ', mission_id
                try:
                    # delete mission
                    url = url_for('main.c2_delete_mission', mission_id=mission_id)
                    if verbose:
                        print '\n delete url: '
                        response = self.client.delete(url, content_type=content_type, headers=headers)
                    if verbose:
                        print '\n -- response: ', response
                        print '\n -- response.data: ', response.data
                    self.assertEquals(response.status_code, 200)

                    data = json.loads(response.data)
                    self.assertTrue('delete' in data)

                except Exception as err:
                    if verbose: print '\n *** err.message: ', err.message
                    self.assertEquals('exception: ', err.message)

                # get current missions
                if verbose: print '\n get current missions...'
                mission_ids = []
                url = url_for('main.c2_get_missions')
                response = self.client.get(url,content_type=content_type, headers=headers)
                self.assertEquals(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue('missions' in data)
                self.assertTrue(len(data['missions']) > 0)
                missions = data['missions']
                for mission in missions:
                    mission_ids.append(mission['mission_id'])
                    for item in self.valid_items:
                        self.assertTrue(item in mission)
                if verbose: print '\n (After delete) mission_ids: ', mission_ids

        # Add mission
        url = url_for('main.c2_add_mission')
        if verbose: print '\n url: ', url
        try:
            response = self.client.post(url, content_type=content_type, headers=headers, data=json.dumps(d))
            if verbose: print '\n (add) response: ', json.loads(response.data)
        except Exception as err:
            if verbose: print '\n *** exception: ', err.message
            self.assertEquals('exception: ', err.message)

        # get current missions
        if verbose: print '\n get current missions...'
        mission_ids = []
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)
        if verbose: print '\n mission_ids: ', mission_ids

        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        '''
        # delete mission (supported in upcoming release)
        url = url_for('main.c2_delete_mission', mission_id=mission_id)
        response = self.client.delete(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('delete' in data)
        if verbose: print '\n data[delete]: ', data['delete']
        '''

    def _test_c2_mission_add_negative(self):
        """
        Add a mission.
        """
        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        delete_route_supported = False
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_ids = []
        mission_id = 'test_mission900'

        d = {
            'name': mission_id,
            'desc': 'Hydrate Ridge photos using Digital Still Camera (scheduled).',
            'version': '9-01',
            'drivers': ['RS01SUM1-MJ01B-05-CAMDSB103'],
            'schedule': {'hour': '0,6,12,18'},
            'error_policy': {'type': 'abort'},
            'debug': True,
            'mission': {
                'type': 'block',
                'sequence': [
                    {'execute': 'RS01SUM1-MJ01B-05-CAMDSB103', 'command': 'start_autosample'},
                    {'sleep': 2.5},
                    {'set': 'RS01SUM1-MJ01B-05-CAMDSB103', 'parameter': 'p1', 'value': 5},
                    {'type': 'block', 'sequence': [{'sleep': 2.5}]},
                ]
            },
            'blocks': [
                {'type': 'block', 'label': 'capture', 'sequence': []},
            ],
        }


        # get current missions
        if verbose: print '\n get current missions...'
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)
        if verbose: print '\n mission_ids: ', mission_ids


        # (Positive) Add mission
        url = url_for('main.c2_add_mission')
        if verbose: print '\n url: ', url
        try:
            response = self.client.post(url, content_type=content_type, headers=headers, data=json.dumps(d))
            if verbose: print '\n (add) response: ', json.loads(response.data)
        except Exception as err:
            if verbose: print '\n exception: ', err.message
            self.assertEquals('exception: ', err.message)
        '''
        # delete mission
        url = url_for('main.c2_delete_mission', mission_id=mission_id)
        response = self.client.delete(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('delete' in data)
        '''

        # (Negative) Add mission Mission minus required fields
        add2 = {'name': mission_id, 'desc': 'Hydrate Ridge photos using Digital Still Camera (scheduled).'}
        url = url_for('main.c2_add_mission')
        if verbose: print '\n (add2) url: ', url
        response = self.client.post(url, content_type=content_type, headers=headers, data=json.dumps(add2))
        self.assertEquals(response.status_code, 400 )

        # (Negative) Add mission invalid dict parameter values (name is str, set to int)
        add3 = {
            'name': 1,
            'desc': 'Hydrate Ridge photos using Digital Still Camera (scheduled).',
            'version': '9-01',
            'drivers': ['RS01SUM1-MJ01B-05-CAMDSB103'],
            'schedule': {'hour': '0,6,12,18'},
            'error_policy': {'type': 'abort'},
            'debug': True,
            'mission': {
                'type': 'block',
                'sequence': [
                    {'execute': 'RS01SUM1-MJ01B-05-CAMDSB103', 'command': 'start_autosample'},
                    {'sleep': 2.5},
                    {'set': 'RS01SUM1-MJ01B-05-CAMDSB103', 'parameter': 'p1', 'value': 5},
                    {'type': 'block', 'sequence': [{'sleep': 2.5}]},
                ]
            },
            'blocks': [
                {'type': 'block', 'label': 'capture', 'sequence': []},
            ],
        }
        url = url_for('main.c2_add_mission')
        if verbose: print '\n (add3) url: ', url
        response = self.client.post(url, content_type=content_type, headers=headers, data=json.dumps(add3))
        self.assertEquals(response.status_code, 400 )


        # get current missions
        if verbose: print '\n get current missions...'
        mission_ids = []
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)
        if verbose: print '\n mission_ids: ', mission_ids





    # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
    def _test_c2_mission_delete(self):
        """
        Delete a mission. (Not complete yet; not yet supported by upstream server.)
        """
        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        delete_route_supported = False
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_id='test_mission100'

        # get mission
        url = url_for('main.c2_get_mission', mission_id=mission_id)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)
        if len(data['mission']) <= 0:
            # Add mission - if this fails, the raise Exception and assert failure
            url = url_for('main.c2_add_mission')
            if verbose: print '\n (add mission_id \%s) url: %s' % (mission_id, url)
            try:
                response = self.client.post(url, content_type=content_type, headers=headers, data=json.dumps(d))
                if verbose: print '\n ***** response: ', json.loads(response.data)
            except Exception as err:
                if verbose: print '\n *** exception: ', err.message
                self.assertEquals('exception: ', err.message)

        if delete_route_supported:
            # delete mission
            url = url_for('main.c2_delete_mission', mission_id=mission_id)
            response = self.client.delete(url,content_type=content_type, headers=headers)
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('delete' in data)

        # get mission
        url = url_for('main.c2_get_mission', mission_id=mission_id)
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('mission' in data)

    def test_c2_mission_add_bench_instrument(self):
        """
        Add a mission.
        """
        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        delete_route_supported = False
        verbose = self.verbose
        root = self.root
        if verbose: print '\n'
        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')
        mission_ids = []
        mission_id = 'test_mission900'

        '''
        d = {
            'name': mission_id,
            'desc': 'Hydrate Ridge photos using Digital Still Camera (scheduled).',
            'version': '9-01',
            'drivers': ['RS01SUM1-MJ01B-05-CAMDSB103'],
            'schedule': {'hour': '0,6,12,18'},
            'error_policy': {'type': 'abort'},
            'debug': True,
            'mission': {
                'type': 'block',
                'sequence': [
                    {'execute': 'RS01SUM1-MJ01B-05-CAMDSB103', 'command': 'start_autosample'},
                    {'sleep': 2.5},
                    {'set': 'RS01SUM1-MJ01B-05-CAMDSB103', 'parameter': 'p1', 'value': 5},
                    {'type': 'block', 'sequence': [{'sleep': 2.5}]},
                ]
            },
            'blocks': [
                {'type': 'block', 'label': 'capture', 'sequence': []},
            ],
        }
        '''

        bench = {
                'mission': {
                    'blocks': [
                        {
                            'label': 'mission',
                            'sequence': [

                                  { 'block_name': 'initialize'},
                                  { 'discover':  'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'get_state': 'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'execute':   'RS10ENGC-XX00X-00-BOTPTA001', 'command': 'DRIVER_EVENT_START_AUTOSAMPLE'}

                            ]
                        },
                        {
                            'label': 'initialize',
                            'sequence': [
                                  { 'reset': 'initialize' , 'timeout': 'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'sleep': 'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'set_init_params':   'RS10ENGC-XX00X-00-BOTPTA001'},
                                  { 'config':
                                        { 'parameters':
                                            {
                                              'relevel_timeout': 600,
                                              'auto_relevel':    False,
                                              'heat_duration':   1,
                                              'output_rate_hz':  20,
                                              'xtilt_relevel_trigger': 300.00,
                                              'ytilt_relevel_trigger': 300.00

                                            }
                                        }
                                   }
                              ]
                        }
                      ]
                    },
                    'debug': True,
                    'drivers': ['RS10ENGC-XX00X-00-BOTPTA001'],
                    'error_policy': {'type': 'abort'},
                    'name': 'configure_bench_botpt',
                    'desc': 'Configure the bench BOTPT and place it in AUTOSAMPLE',
                    'version': '1-00'
                }

        try:
            data = json.dumps(bench)
            print '\n data: ', data
        except Exception as err:
            print '\n dumps: exception: ', err.message

        # get current missions
        if verbose: print '\n get current missions...'
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)
        if verbose: print '\n mission_ids: ', mission_ids

        '''
        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        if delete_route_supported:
            if mission_id in mission_ids:
                if verbose:
                    print '\n\n ----- %s found in list of missions....' % mission_id
                    print '\n ----- delete current mission_id: ', mission_id
                try:
                    # delete mission
                    url = url_for('main.c2_delete_mission', mission_id=mission_id)
                    if verbose:
                        print '\n delete url: '
                        response = self.client.delete(url, content_type=content_type, headers=headers)
                    if verbose:
                        print '\n -- response: ', response
                        print '\n -- response.data: ', response.data
                    self.assertEquals(response.status_code, 200)

                    data = json.loads(response.data)
                    self.assertTrue('delete' in data)

                except Exception as err:
                    if verbose: print '\n *** err.message: ', err.message
                    self.assertEquals('exception: ', err.message)

                # get current missions
                if verbose: print '\n get current missions...'
                mission_ids = []
                url = url_for('main.c2_get_missions')
                response = self.client.get(url,content_type=content_type, headers=headers)
                self.assertEquals(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue('missions' in data)
                self.assertTrue(len(data['missions']) > 0)
                missions = data['missions']
                for mission in missions:
                    mission_ids.append(mission['mission_id'])
                    for item in self.valid_items:
                        self.assertTrue(item in mission)
                if verbose: print '\n (After delete) mission_ids: ', mission_ids
        '''

        # Add mission
        url = url_for('main.c2_add_mission')
        if verbose: print '\n url: ', url
        try:
            data = json.dumps(bench)
            response = self.client.post(url, content_type=content_type, headers=headers, data=data)
            if verbose: print '\n (add) response: ', json.loads(response.data)
        except Exception as err:
            if verbose: print '\n *** exception: ', err.message
            self.assertEquals('exception: ', err.message)

        # get current missions
        if verbose: print '\n get current missions...'
        mission_ids = []
        url = url_for('main.c2_get_missions')
        response = self.client.get(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('missions' in data)
        self.assertTrue(len(data['missions']) > 0)
        missions = data['missions']
        for mission in missions:
            mission_ids.append(mission['mission_id'])
            for item in self.valid_items:
                self.assertTrue(item in mission)
        if verbose: print '\n mission_ids: ', mission_ids

        # todo upstream server delete route not yet supported - todo remove delete_route_supported etc.
        '''
        # delete mission (supported in upcoming release)
        url = url_for('main.c2_delete_mission', mission_id=mission_id)
        response = self.client.delete(url,content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('delete' in data)
        if verbose: print '\n data[delete]: ', data['delete']
        '''
