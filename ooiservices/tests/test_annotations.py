#!/usr/bin/env python
'''
unit testing for the table of contents (TOC) required classes.

'''
__author__ = 'M@Campbell'

import unittest
import json
import re
from base64 import b64encode
from flask import url_for, jsonify, g
from ooiservices.app import create_app, db
from ooiservices.app.models import Annotation, User, UserScope, UserScopeLink

'''
These tests verify the functioning of the api list.
Sample data is inserted, checked, and then removed.

'''

class TOCTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=False)
        password = 'test'
        User.insert_user(password)
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
        # Test forbbiden
        response = self.client.put(
            url_for('main.edit_annotation', id=1),
            headers=self.get_api_headers('admin', 'test'),
            data=json.dumps({'comment': 'updated annotation'}))
        self.assertTrue(response.status_code == 403)

        #give admin account the annotate scope.
        usl = UserScopeLink(user_name='admin', scope_name='annotate')
        db.session.add(usl)
        db.session.commit()

        #Test the json in the object
        annotation = Annotation()
        self.assertTrue(annotation.to_json() == {'comment': None, 'created_time': None, 'id': None, 'modified_time': None, 'title': None, 'user_name': None})

        new_annotation_json = {'comment': 'test', 'title': 'Test Annotation', 'user_name': 'admin'}

        new_annotation = Annotation.new_from_json(new_annotation_json)
        db.session.add(new_annotation)
        db.session.commit()
        result = Annotation.query.filter_by(user_name='admin').first()
        self.assertTrue(result.comment == 'test')

        #test the api route for lists
        response = self.client.get(url_for('main.get_annotations'), content_type = 'application/json')

        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_annotation',id='admin'), content_type = 'application/json')

        self.assertTrue(response.status_code == 200)

        #Test authorized
        response = self.client.post(url_for('main.create_annotation'), headers=self.get_api_headers('admin', 'test'), data=json.dumps(new_annotation_json))
        self.assertEquals(response.status_code, 201)

        # edit post
        response = self.client.put(
            url_for('main.edit_annotation', id=1),
            headers=self.get_api_headers('admin', 'test'),
            data=json.dumps({'comment': 'updated annotation'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['comment'] == 'updated annotation')