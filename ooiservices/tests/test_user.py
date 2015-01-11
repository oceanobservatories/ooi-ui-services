#!/usr/bin/env python
'''
Specific testing of user scopes, and passwords.

'''
__author__ = 'M.Campbell'

import unittest
from flask import url_for
from app import create_app, db
from app.models import Array, InstrumentDeployment, PlatformDeployment, Stream, \
StreamParameter, User

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class ModelTestCase(unittest.TestCase):
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

