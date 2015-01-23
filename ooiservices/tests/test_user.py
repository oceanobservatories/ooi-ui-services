#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'M@Campbell'

import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import User, UserScope, UserScopeLink

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
        User.insert_user(test_password)

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

        scope = UserScope.query.filter_by(scope_name='user_read').first()
        self.assertTrue(scope.scope_name == 'user_read')

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
        response = self.client.get(url_for('main.get_user',id='admin'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        #Test authorized
        response = self.client.get(url_for('main.get_user',id='admin'), headers=self.get_api_headers('admin', 'test'))
        self.assertTrue(response.status_code == 200)

    def test_get_user_scope_route(self):
        #Test unauthorized
        response = self.client.get(url_for('main.get_user_scopes'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        #Test authorized
        response = self.client.get(url_for('main.get_user_scopes'), headers=self.get_api_headers('admin', 'test'))

        self.assertTrue(response.status_code == 200)

    def test_create_user_route(self):
        #Test unauthorized
        response = self.client.post(url_for('main.create_user'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

        #Test authorized
        response = self.client.post(url_for('main.create_user'), headers=self.get_api_headers('admin', 'test'), data=json.dumps({'email': 'test@test', 'password': 'testing', 'repeatPassword': 'testing', 'phonenum': '1234', 'username': 'test_user'}))
        self.assertEquals(response.status_code, 201)

        #Test duplicate user
        response = self.client.post(url_for('main.create_user'), headers=self.get_api_headers('admin', 'test'), data=json.dumps({'email': 'test@test', 'password': 'testing', 'repeatPassword': 'testing', 'phonenum': '1234', 'username': 'test_user'}))
        self.assertTrue(response.status_code == 409)

        #Test password match
        response = self.client.post(url_for('main.create_user'), headers=self.get_api_headers('admin', 'test'), data=json.dumps({'email': 'test@test', 'password': 'testing', 'repeatPassword': 'testing2', 'phonenum': '1234', 'username': 'test_user2'}))
        self.assertTrue(response.status_code == 409)
