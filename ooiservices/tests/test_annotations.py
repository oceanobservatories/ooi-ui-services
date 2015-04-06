#!/usr/bin/env python
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

        '''
        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()
        '''


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
        content_type = 'application/json'

        'Test model and GET/PUT/POST'
        response = self.client.put(
            url_for('main.edit_annotation', id=1),headers=headers,data=json.dumps({'comment': 'updated annotation'}))
        self.assertTrue(response.status_code == 403)

        'Test delete annotation without proper scope'
        response = self.client.delete(url_for('main.delete_annotation', id=1), headers=headers)
        self.assertEquals(response.status_code, 403)

        # give admin account the annotate scope.
        admin = User.query.filter(User.user_name == 'admin').first()
        scope = UserScope.query.filter(UserScope.scope_name == 'annotate').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

        'Test Annotation model'
        #Test the json in the object
        annotation = Annotation()
        self.assertTrue(annotation.to_json() == {'comment': None, 'created_time': None,
            'field_x1': None, 'field_y1': None, 'id': None, 'instrument_name': None,
            'modified_time': None, 'pos_x1': None, 'pos_y1': None, 'stream_name': None,
            'title': None, 'user_name': None,
            'field_x2': None, 'field_y2': None, 'pos_x2': None, 'pos_y2': None}
        )

        'Test new annotation submission'
        new_annotation_json = {'comment': 'test', 'field_x1': 'x-files', 'field_y1': 'y-files',
            'instrument_name': 'CP02PMUO-WFP01-04-FLORTK000', 'pos_x1': 5, 'pos_y1': 5,
            'stream_name': 'flort_kn_stc_imodem_instrument', 'title': 'test',
            'field_x2': 'x-files-2', 'field_y2': 'y-files-2', 'pos_x2': 10, 'pos_y2': 10}
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
        response = self.client.get(url_for('main.get_annotations'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        'Test API GET by id'
        response = self.client.get(url_for('main.get_annotation',id='admin'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        'Test API GET by id with request arg stream_name'
        url = url_for('main.get_annotations',id='admin')
        url += '&stream_name=some_stream_name'
        response = self.client.get(url, content_type=content_type)
        self.assertTrue(response.status_code == 200)

        'Test POST with user authorized'
        response = self.client.post(url_for('main.create_annotation'), headers=headers, data=None)
        self.assertEquals(response.status_code, 409)

        'Test POST user authorized and missing data fields'
        bad_annotation = {'comment': 'test', 'field_x1': 'x-files', 'field_y1': 'y-files',
            'instrument_name': 'CP02PMUO-WFP01-04-FLORTK000', 'pos_x1': 5, 'pos_y1': 5,
            'field_x2': 'x-files-2', 'field_y2': 'y-files-2', 'pos_x2': 10, 'pos_y2': 10}
        response = self.client.post(url_for('main.create_annotation'), headers=headers, data=json.dumps(bad_annotation))
        self.assertEquals(response.status_code, 201)

        'Test edit annotation'
        response = self.client.put(
            url_for('main.edit_annotation', id=1), headers=headers,data=json.dumps({'comment': 'updated annotation'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['comment'] == 'updated annotation')

        'Test bad edit annotation'
        response = self.client.put(url_for('main.edit_annotation', id=1), headers=headers,data=None)
        self.assertEquals(response.status_code, 409)

        # 'remove admin account annotate scope.'
        admin = User.query.filter(User.user_name == 'admin').first()
        scope = UserScope.query.filter(UserScope.scope_name == 'annotate').first()
        admin.scopes.remove(scope)
        db.session.add(admin)
        db.session.commit()

        # 'Test delete annotation without proper scope'
        response = self.client.delete(url_for('main.delete_annotation', id=1), headers=headers)
        self.assertEquals(response.status_code, 403)

        # 'add admin account annotate scope.'
        admin = User.query.filter(User.user_name == 'admin').first()
        scope = UserScope.query.filter(UserScope.scope_name == 'annotate').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

        # 'Test delete annotation'
        response = self.client.delete(url_for('main.delete_annotation', id=1), headers=headers)
        self.assertEquals(response.status_code, 200)

        # Test delete non-existent annotation
        response = self.client.delete(url_for('main.delete_annotation', id=5), headers=headers)
        self.assertEquals(response.status_code, 404)