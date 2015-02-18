#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'M@Campbell'

import unittest
import json
import re
from base64 import b64encode
from flask import url_for, jsonify
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, UserScopeLink
from collections import OrderedDict

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_password = 'test'
        User.insert_user(password=test_password)

        self.client = self.app.test_client(use_cookies=False)

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

    def test_user_scope(self):
        user_scope = UserScope()
        user_scope.insert_scopes()

        scope = UserScope.query.filter_by(scope_name='asset_manager').first()
        self.assertTrue(scope.scope_name == 'asset_manager')

    def test_user_insert(self):
        user_name = User.query.filter_by(user_name='admin').first()
        self.assertTrue(user_name.user_name == 'admin')

    def test_password_tampering(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_hashing(self):
        u = User(password='dog')
        self.assertTrue(u.pass_hash is not None)

    def test_password_verification(self):
        u = User(password='dog')
        self.assertTrue(u.verify_password('dog'))
        self.assertFalse(u.verify_password('cat'))

    def test_password_salts(self):
        u = User(password='dog')
        u2 = User(password='dog')
        self.assertTrue(u.pass_hash != u2.pass_hash)

    #Test user API routes
    #For route: /user/<string:id>
    def test_get_user_route(self):
        #Test unauthorized
        response = self.client.get(url_for('main.get_user',id=1), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        #Test authorized
        response = self.client.get(url_for('main.get_user',id=1), headers=self.get_api_headers('admin', 'test'))
        self.assertTrue(response.status_code == 200)

    #Test [GET] /user_scopes - 'main.get_user_scopes'
    def test_get_user_scope_route(self):


        headers = self.get_api_headers('admin', 'test')

        #Test unauthorized
        response = self.client.get(url_for('main.get_user_scopes'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        UserScope.insert_scopes()

        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

        #Test authorized
        response = self.client.get(url_for('main.get_user_scopes'), headers=headers)
        self.assertTrue(response.status_code == 200)

        # Expected user_scopes
        user_scopes_data = \
            {"user_scopes": [{"id": 1, "scope_description": None, "scope_name": "annotate"},
                             {"id": 2, "scope_description": None, "scope_name": "asset_manager"},
                             {"id": 3, "scope_description": None, "scope_name": "user_admin"},
                             {"id": 4, "scope_description": None, "scope_name": "redmine"} ]}

        # assert: (1) response.data is string, (2) greater than 0 in length and (3) contains 'user roles'
        response_data = response.data[:]
        self.assertTrue(len(response_data) > 0)
        self.assertTrue(type(response_data) == type(''))
        self.assertTrue('user_scopes' in response_data)

        # create dictionary from string; compare response data with expected user scopes
        dict_scopes = json.loads(response_data)
        self.assertTrue(dict_scopes == user_scopes_data)

    def test_create_user_route(self):
        '''
        create user
        '''
        headers = self.get_api_headers('admin', 'test')

        # 1. Test create user without authorization
        response = self.client.post(url_for('main.create_user'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        # 2. Test create user as an authorized user (user 'admin')
        data = json.dumps({'email': 'test@test', 'password': 'testing', 'repeatPassword': 'testing',
                           'phonenum': '1234', 'username': 'test_user'})
        response = self.client.post(url_for('main.create_user'), headers=headers, data=data)
        self.assertEquals(response.status_code, 201)

        # 3. Test creation of duplicate user; expect failure
        response = self.client.post(url_for('main.create_user'), headers=headers, data=data)
        self.assertTrue(response.status_code == 409)

        # 4. Test password match using bad_data; expect failure
        bad_data = json.dumps({'email': 'test@test', 'password': 'testing', 'repeatPassword': 'testing2',
                               'phonenum': '1234', 'username': 'test_user2'})
        response = self.client.post(url_for('main.create_user'), headers=headers, data=bad_data)
        self.assertTrue(response.status_code == 409)

    # Test [GET] /user_roles - 'main.get_user_roles'
    def test_get_user_roles_route(self):
        '''
        get user roles
        '''
        # Setup
        headers = self.get_api_headers('admin', 'test')
        response = self.client.get(url_for('main.get_user_roles'), headers=headers)
        self.assertTrue(response.status_code == 200)

        # test response.data against the following 'expected' role_data
        role_data = {"user_roles": [{"id": 1, "role_name": "Administrator"}, {"id": 2, "role_name": "Marine Operator"}, {"id": 3, "role_name": "Science User"}]}

        # assert: (1) response.data is string, (2) greater than 0 in length and (3) contains 'user roles'
        response_data = response.data[:]
        self.assertTrue(len(response_data) > 0)
        self.assertTrue(type(response_data) == type(''))
        self.assertTrue('user_roles' in response_data)

        # create dictionary from string;
        dict_roles = json.loads(response_data)
        self.assertTrue(dict_roles == role_data)

    #Test [GET] /current_user - 'main.get_current_user'
    def test_current_user_route(self):
        '''
        get current user
        '''
        headers = self.get_api_headers('admin', 'test')
        response = self.client.get(url_for('main.get_current_user'), headers=headers)
        self.assertTrue(response.status_code == 200)

    # Test [GET] /user - 'main.get_users'; admin priv required
    def test_get_users_route(self):
        '''
        get all users; currently scope_required is 'user_admin'
        '''
        #TODO: if role_required is utilized, suggest using @role_required('administrator').
        #TODO: (See also, arrays.py delete_array)
        UserScope.insert_scopes()
        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

        response = self.client.get(url_for('main.get_users'), headers=self.get_api_headers('admin', 'test'))
        self.assertTrue(response.status_code == 200)

    #Test [PUT] /user/<int:id> - 'main.put_user'; admin priv required
    def test_put_user_route(self):
        '''
        test ability to change current user ('admin') scopes
        '''
        headers = self.get_api_headers('admin', 'test')

        # add scopes to user_name admin
        UserScope.insert_scopes()
        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

        # 1. get current user (username 'admin')
        response = self.client.get(url_for('main.get_current_user'), headers=headers)
        self.assertTrue(response.status_code == 200)

        # 2. update current user's scopes = ['user_admin', 'asset_manager']
        data = json.dumps({'scopes': ['user_admin', 'asset_manager']})
        response = self.client.put(url_for('main.put_user', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 201)

        # 3. Observe current use, verify new scope ('asset_manager') added
        response = self.client.get(url_for('main.get_current_user'), headers=headers)
        self.assertTrue(response.status_code == 200)

        # 4. Change scopes back to single scope of 'user_admin'; send redundant active value
        expected_data = {'active': True, 'scopes': ['user_admin']}
        data = json.dumps(expected_data)
        response = self.client.put(url_for('main.put_user', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 201)

        # 5. Assert: (1) response.data is string, (2) greater than 0 in length and (3) contains 'user roles'
        response_data = response.data[:]
        self.assertTrue(len(response_data) > 0)
        self.assertTrue(type(response_data) == type(''))
        self.assertTrue('active' in response_data)
        self.assertTrue('scopes' in response_data)

        # 6. Create dictionary from resonse_data; compare response_data with expected data dict
        dict_data = json.loads(response_data)
        self.assertTrue('active' in dict_data)
        self.assertTrue('active' in expected_data)
        self.assertTrue(dict_data['active'] == expected_data['active'])
        self.assertTrue(dict_data['scopes'] == expected_data['scopes'])

    #Test [PUT] /user/<int:id> - 'main.put_user'; admin priv required
    def test_put_user_changes(self):
        '''
        test ability to create new user and change scopes and/or active status of new user

        '''
        # add scopes to user_name admin
        UserScope.insert_scopes()
        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

        headers = self.get_api_headers('admin', 'test')

        # 1. get current user
        response = self.client.get(url_for('main.get_current_user'), headers=headers)
        self.assertTrue(response.status_code == 200)

        # 2. Create new user - test_user
        data=json.dumps({'email': 'test@test', 'password': 'testing', 'repeatPassword': 'testing', 'phonenum': '1234', 'username': 'test_user'})
        response = self.client.post(url_for('main.create_user'), headers=headers, data=data)
        self.assertEquals(response.status_code, 201)

        # 3. Get all users
        response = self.client.get(url_for('main.get_users'), headers=headers)
        self.assertTrue(response.status_code == 200)

        # 4. Verify user count is now == 2
        response_data = response.data[:]
        self.assertTrue(len(response_data) > 0)
        self.assertTrue(type(response_data) == type(''))
        self.assertTrue('users' in response_data)
        user_data = json.loads(response_data)
        user_list = user_data['users']
        self.assertTrue(len(user_list) == 2)

        # 5. Update new user's scopes, add scopes = ['asset_manager']
        expected_data = {'active': True, 'scopes': ['asset_manager']}
        data = json.dumps(expected_data)
        response = self.client.put(url_for('main.put_user', id=2), headers=headers, data=data)
        self.assertTrue(response.status_code == 201)

        # 6. Get the new (and updated) user
        response = self.client.get(url_for('main.get_user',id=2), headers=headers)
        self.assertTrue(response.status_code == 200)

        # 7. Verify new user data includes expected_data: scopes=['asset_manager'] and 'active' == True
        response_data = response.data[:]
        self.assertTrue(len(response_data) > 0)
        self.assertTrue(type(response_data) == type(''))
        self.assertTrue('active' in response_data)
        self.assertTrue('scopes' in response_data)
        dict_data = json.loads(response_data)
        self.assertTrue(dict_data['active'] == expected_data['active'])
        self.assertTrue(dict_data['scopes'] == expected_data['scopes'])

