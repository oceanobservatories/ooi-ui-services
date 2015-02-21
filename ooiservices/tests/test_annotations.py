#!/usr/bin/env python
'''
unit testing for the annotations feature

'''
__author__ = 'M@Campbell'

import unittest
import json
import re
from base64 import b64encode
from flask import url_for, jsonify, g
from ooiservices.app import create_app, db
from ooiservices.app.models import Annotation, User, UserScope, UserScopeLink, Organization
from datetime import datetime

'''
These tests verify the functioning of the api list.
Sample data is inserted, checked, and then removed.

'''

class AnnotationsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(is_test=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=False)
        password = 'test'
        Organization.insert_org()
        User.insert_user(password=password)
        UserScope.insert_scopes()

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
        'Test model and GET/PUT/POST'
        response = self.client.put(
            url_for('main.edit_annotation', id=1),
            headers=self.get_api_headers('admin', 'test'),
            data=json.dumps({'comment': 'updated annotation'}))
        self.assertTrue(response.status_code == 403)

        #give admin account the annotate scope.
        admin = User.query.filter(User.user_name == 'admin').first()
        scope = UserScope.query.filter(UserScope.scope_name == 'annotate').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

        'Test Annotation model'
        #Test the json in the object
        annotation = Annotation()
        self.assertTrue(annotation.to_json() == {'comment': None, 'created_time': None, \
            'field_x': None, 'field_y': None, 'id': None, 'instrument_name': None, \
            'modified_time': None, 'pos_x': None, 'pos_y': None, 'stream_name': None, \
            'title': None, 'user_name': None})

        'Test new annotation submission'
        new_annotation_json = {'comment': 'test', 'field_x': 'x-files', 'field_y': 'y-files', \
            'instrument_name': 'CP02PMUO-WFP01-04-FLORTK000', 'pos_x': 5, 'pos_y': 5, \
            'stream_name': 'flort_kn_stc_imodem_instrument', 'title': 'test'}
        new_annotation = Annotation.from_json(new_annotation_json)
        new_annotation.created_time = datetime.now()
        new_annotation.modified_time = datetime.now()
        new_annotation.user_name = g.current_user.user_name
        db.session.add(new_annotation)
        db.session.commit()
        result = Annotation.query.filter_by(user_name='admin').first()
        self.assertTrue(result.comment == 'test')

        'Test API GET list'
        #test the api route for lists
        response = self.client.get(url_for('main.get_annotations'), content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

        'Test API GET by id'
        response = self.client.get(url_for('main.get_annotation',id='admin'), content_type = 'application/json')
        self.assertTrue(response.status_code == 200)

        'Test user authorized'
        response = self.client.post(url_for('main.create_annotation'), headers=self.get_api_headers('admin', 'test'), data=json.dumps(new_annotation_json))
        self.assertEquals(response.status_code, 201)

        'Test edit annotation'
        response = self.client.put(
            url_for('main.edit_annotation', id=1),
            headers=self.get_api_headers('admin', 'test'),
            data=json.dumps({'comment': 'updated annotation'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['comment'] == 'updated annotation')
