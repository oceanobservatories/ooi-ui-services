#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'M@Campbell'

import unittest
from flask import url_for
from app import create_app, db
from app.models import User, UserScope

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_scope(self):
        user_scope = UserScope()
        user_scope.insert_scopes()

        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        self.assertTrue(scope.scope_name == 'user_admin')

    def test_user_insert(self):
        test_password = 'test'
        user_insert_test = User()
        user_insert_test.insert_user(test_password)

        user_name = User.query.filter_by(user_name='admin').first()
        self.assertTrue(user_name.user_name == 'admin')

    def test_password_tampering(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_hasing(self):
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