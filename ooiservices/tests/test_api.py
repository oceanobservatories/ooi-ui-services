#!/usr/bin/env python
'''
unit testing for the api classes.

'''
__author__ = 'M.Campbell'

import unittest
from flask import url_for
from app import create_app, db
from app.models import Array, InstrumentDeployment, PlatformDeployment, Stream, \
StreamParameter, User

'''
These tests verify the functioning of the api list.
Sample data is inserted, checked, and then removed.

'''

#TODO: Only GET routes tested for now, furture task to test PUT/POST/DELETE.

class APITestCase(unittest.TestCase):
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

    def test_array(self):
        #Create a sample data set.
        #TODO : This will be replaced by an endpoint
        array_code = Array(array_code='CE')

        db.session.add(array_code)
        db.session.commit()

        #test the api route for lists
        response = self.client.get(url_for('api.get_arrays'), content_type = \
        'application/json')

        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('api.get_array',id='CE'), content_type = \
        'application/json')

        self.assertTrue(response.status_code == 200)