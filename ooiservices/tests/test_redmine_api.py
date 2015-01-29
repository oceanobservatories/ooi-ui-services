#!/usr/bin/env python
'''
Unit testing for the Redmine API

'''

from ooiservices.app import create_app, db
from ooiservices.app.models import Array, InstrumentDeployment, PlatformDeployment, Stream, StreamParameter
# from ooiservice.app.redmine.routes
import unittest
from flask import url_for


'''
These tests verify the functioning of the Redmine api list.

'''


class RedmineTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        # db.create_all()
        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_read_redmine_issues(self):
        rv = self.client.get('redmine/ticket')
        assert 'issues' in rv.data

    def test_create_redmine_ticket(self):
        rv = self.client.post('redmine/ticket', data=dict(project='bob_test'))
        assert 'Shit' in rv.data
