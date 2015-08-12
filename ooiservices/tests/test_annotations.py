#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
unit testing for the annotations feature

'''
__author__ = 'AndyBird'

import unittest
import json
from base64 import b64encode
from flask import url_for, jsonify, g
from ooiservices.app import create_app, db
from ooiservices.app.models import Annotation, User, UserScope, UserScopeLink, Organization
from datetime import datetime
from dateutil.parser import parse as dateparse
from unittest import skipIf
'''
These tests verify the functioning of the api list.
Sample data is inserted, checked, and then removed.

'''
@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class AnnotationsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push() 
        
        db.create_all()

        self.client = self.app.test_client(use_cookies=False)
        self.root = 'http://localhost:4000'

        test_username = 'admin'
        test_password = 'test'
        self.content_type =  'application/json'
        self.headers = self.get_api_headers('admin', 'test')

    def tearDown(self):
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_create_annotation_for_ref_des(self):
        pass              

    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_get_annotation_list_for_ref_des(self):   
        ref_des = "CE01ISSM-SBD17-04-VELPTA000"
        stream = "telemetered_velpt_ab_dcl_instrument"

        url = "/annotation/"+ref_des+"/"+stream
        
        print url

        response = self.client.get(url, content_type=self.content_type, headers=self.headers)

        print response

        self.assertTrue(response.status_code == 200)        
        
    @skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
    def test_searching(self):
        self.assertTrue(False)


