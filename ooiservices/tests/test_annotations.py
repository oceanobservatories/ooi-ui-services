#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
unit testing for the annotations feature

'''
__author__ = 'M@Campbell'

import unittest
import json
from base64 import b64encode
from flask import url_for, jsonify, g
from ooiservices.app import create_app, db
from ooiservices.app.models import Annotation, User, UserScope, UserScopeLink, Organization
from datetime import datetime
from dateutil.parser import parse as dateparse

'''
These tests verify the functioning of the api list.
Sample data is inserted, checked, and then removed.

'''

class AnnotationsTestCase(unittest.TestCase):
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
        scope = UserScope.query.filter_by(scope_name='annotate').first()
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

    def test_annotation(self):

        headers = self.get_api_headers('admin', 'test')

        # POST /annotation
        data = {
            'reference_designator' : 'CP02PMCO-WFP01-01-VEL3DK000',
            'start_time' : '2014-04-12T1826Z',
            'end_time' : '2014-04-13T00:00Z',
            'stream_parameter_name': 'vel3d_k_temp_c',
            'stream_name':'vel3d_k_wfp_instrument',
            'description' : u'僕にとって、その球が完璧だ。'
            # User is matched by authentication
        }
        response = self.client.post('/annotation', data=json.dumps(data), headers=headers)
        self.assertEquals(response.status_code, 201)

        record = json.loads(response.data)

        annotation_id = record['id']

        # GET /annotation/<id>
        response = self.client.get('/annotation/%s' % annotation_id)
        self.assertEquals(response.status_code, 200)
        record = json.loads(response.data)

        for key in data:
            if 'time' in key:
                rval = dateparse(record[key])
                lval = dateparse(data[key])
                self.assertEquals(rval, lval)
                continue
            self.assertEquals(record[key], data[key])

        record['description'] = u'How about in english this time?'
        # PUT /annotation/<id>
        response = self.client.put('/annotation/%s' % annotation_id, data=json.dumps(record), headers=headers)
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/annotation/%s' % annotation_id)
        self.assertEquals(response.status_code, 200)
        new_record = json.loads(response.data)
        self.assertEquals(record['description'], new_record['description'])

        # GET /annotation
        response = self.client.get('/annotation')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.data)
        self.assertEquals(len(records['annotations']), 1)

        # DELETE /annotation/<id>
        response = self.client.delete('/annotation/%s' % annotation_id, headers=headers)
        self.assertEquals(response.status_code, 204)

        # GET /annotation
        response = self.client.get('/annotation')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.data)
        self.assertEquals(len(records['annotations']), 0)

    def test_searching(self):
        headers = self.get_api_headers('admin', 'test')
        entries = [
            {
                'reference_designator' : 'CP02PMCO-WFP01-01-VEL3DK000',
                'start_time' : '2014-04-12T1826Z',
                'end_time' : '2014-04-13T00:00Z',
                'stream_parameter_name': 'vel3d_k_temp_c',
                'stream_name':'vel3d_k_wfp_instrument',
                'description' : u'僕にとって、その球が完璧だ。'
            },
            {
                'reference_designator' : 'CP02PMCO-WFP01-01-VEL3DK000',
                'start_time' : '2014-06-12T1826Z',
                'end_time' : '2014-07-13T00:00Z',
                'stream_parameter_name': 'vel3d_k_temp_c',
                'stream_name':'vel3d_k_wfp_instrument',
                'description' : u'Second Statement'
            },
            {
                'reference_designator' : 'CP02PMCO-WFP01-01-CTDPF0000',
                'start_time' : '2014-04-12T1826Z',
                'end_time' : '2014-04-13T00:00Z',
                'stream_parameter_name': 'seawater_temperature',
                'stream_name':'ctdpf_wfp_instrument',
                'description' : u'Instrument was removed for testing'
            },
            {
                'reference_designator' : 'CP02PMCO-WFP01-01-VEL3DK000',
                'start_time' : '2014-04-12T1826Z',
                'end_time' : '2014-04-13T00:00Z',
                'stream_parameter_name': 'vel3d_k_temp_c',
                'stream_name':'vel3d_k_wfp_instrument',
                'description' : u'Followup annotation'
            },
            {
                'reference_designator' : 'CP02PMCO-WFP01-01-VEL3DK000',
                'start_time' : '2014-04-12T1826Z',
                'end_time' : '2014-04-13T00:00Z',
                'stream_parameter_name': 'vel3d_k_u',
                'stream_name':'vel3d_k_wfp_instrument',
                'description' : u'Annotation on separate variable'
            }
        ]

        for entry in entries:
            response = self.client.post('/annotation', data=json.dumps(entry), headers=headers)
            self.assertEquals(response.status_code, 201)

        # GET /annotation?stream_name=vel3d_k_wfp_instrument
        response = self.client.get('/annotation?stream_name=vel3d_k_wfp_instrument')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.data)
        self.assertEquals(len(records['annotations']), 4)

        # GET /annotation?reference_designator=CP02PMCO-WFP01-01-CTDPF0000
        response = self.client.get('/annotation?reference_designator=CP02PMCO-WFP01-01-CTDPF0000')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.data)
        self.assertEquals(len(records['annotations']), 1)
        
        # GET /annotation?start_time=2014-06-01T00:00:00Z
        # Search for all annotations after 2014-06-01T00:00Z
        response = self.client.get('/annotation?start_time=2014-06-01T00:00Z')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.data)
        self.assertEquals(len(records['annotations']), 1)
        
        # GET /annotation?start_time=2014-04-01T00:00Z&end_time=2014-05-01T00:00Z
        # Search for all annotations after between 2014-04-01 and 2014-05-01
        response = self.client.get('/annotation?start_time=2014-04-01T00:00Z&end_time=2014-05-01T00:00Z')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.data)
        self.assertEquals(len(records['annotations']), 4)
                
        # GET /annotation?stream_parameter_name=seawater_temperature
        response = self.client.get('/annotation?stream_parameter_name=seawater_temperature')
        self.assertEquals(response.status_code, 200)
        records = json.loads(response.data)
        self.assertEquals(len(records['annotations']), 1)


