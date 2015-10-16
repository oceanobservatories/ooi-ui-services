#!/usr/bin/env python
'''
Specific testing for Command and Control (C2) Mission Executive & Load
'''
__author__ = 'Andrew Bird'

import unittest
import json
from base64 import b64encode
from flask import url_for
import datetime as dt
from unittest import skipIf
import os

from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, Organization
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
# me = mission executive
from ooiservices.app.main.c2 import get_missions as me_get_missions 
from ooiservices.app.main.c2 import add_mission_entry as me_add_mission
from ooiservices.app.main.c2 import remove_mission_entry as me_remove_mission

'''
These tests...test the services for mission executive...MOCK!

'''
@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class CommandAndControlMissionTestCase(unittest.TestCase):

    # enable verbose during development and documentation to get a list of sample
    # urls used throughout test cases. Always set to False before check in.
    verbose = False
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
        cc_scope = UserScope.query.filter_by(scope_name='command_control').first()
        admin.scopes.append(scope)
        admin.scopes.append(cc_scope)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_mission_list(self):
        '''
            test user can get the list of missions...
        '''
        mission_list = me_get_missions()        
        self.assertTrue(len(mission_list)>0)

    def test_add_additional_mission_valid(self):
        '''
            test user can get the list of missions, add one, then get the list and see the new one
        '''
        entry ={
                'reference_designator': 'RS01SUM1-MJ01B-05-CAMDSB103',
                'name': 'sample test mission',
                'desc': 'SAMPLE: '
                        '',
                'version': '1-00',                
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
                'created_by':"system",
                }

        ret = me_add_mission(entry)
        self.assertTrue(ret)

    def test_add_additional_mission_none(self):
        '''
            test user can get the list of missions, add one, then get the list and see the new one
        '''
        entry = None
        ret = me_add_mission(entry)
        self.assertFalse(ret)        

    def test_add_additional_mission_empty(self):
        '''
            test user can get the list of missions, try to add one
        '''
        entry = {}
        ret = me_add_mission(entry)
        self.assertFalse(ret)

    def test_add_additional_mission_invalid(self):
        '''
            test user can get the list of missions, try to add one
        '''
        entry = {'rar':''}
        ret = me_add_mission(entry)
        self.assertFalse(ret)

    def test_check_additional_added_invalid(self):
        '''
            we dont want to add an entry with the auto fields
        '''
        entry ={'reference_designator': 'RS01SUM1-MJ01B-05-CAMDSB103',
                'name': 'sample test mission',
                'desc': 'SAMPLE: '
                        '',
                'version': '1-00',                
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
                'created_by':"system",
                'runs':[],
                'status':'',
                'state':'',
                'created_date':'',
                'mission_id':" ",
                }

        ret = me_add_mission(entry)
        self.assertFalse(ret)

    def test_check_additional_added_fields(self):
        '''
            we add some fields to the date store during creation, check they are there
        '''
        #check the length
        mission_list = me_get_missions()        
        self.assertTrue(len(mission_list) > 0)
        f_len = len(mission_list)
        entry ={
                'reference_designator': 'RS01SUM1-MJ01B-05-CAMDSB103',
                'name': 'sample test mission',
                'desc': 'SAMPLE: '
                        '',
                'version': '1-00',                
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
                'created_by':"system",
                }

        ret = me_add_mission(entry)
        mission_list = me_get_missions() 
        self.assertTrue(len(mission_list) > f_len )

        added_fields = ['runs','status','state','created_date','mission_id']
        sel_mission = mission_list[len(mission_list)-1]
        for field in added_fields:
            print field
            self.assertTrue(field in sel_mission)


    def test_remove_mission_using_id(self):
        '''
            get an entry and remove it from the store, should reduce the mission from the store
        '''
        mission_list = me_get_missions()        
        self.assertTrue(len(mission_list) > 0)
        f_len = len(mission_list)

        sel_mission = mission_list[len(mission_list)-1]
        mission_id = sel_mission['mission_id']

        #remove mission
        ret_val = me_remove_mission(mission_id)
        self.assertTrue(ret_val)

        #check its not there anymore
        mission_list = me_get_missions() 
        for mission in mission_list:
            self.assertFalse(mission['mission_id'] == mission_id)
