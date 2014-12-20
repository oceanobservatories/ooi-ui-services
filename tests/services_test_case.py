#!/usr/bin/env python
'''
tests.services_test_case

The base class for the Services Test Case
'''

import unittest
import os
import shutil

import json
from ooiservices.app import app

class ServicesTestCase(unittest.TestCase):
    '''
    The base test case for the Services unit tests
    '''
    output_dir = 'test-output'
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    def set_up(self):
        '''
        Creates a directory for testing output and debugging
        '''
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_listing(self, route):
        '''
        Test that the app context initializes successfully
        '''
        rv = self.app.get(route)
        assert rv.status_code == 200

    def test_empty_response(self, route):
        rv = self.app.get(route)
        assert rv.status_code == 204

    def tearDown(self):
        '''
        Removes the directory
        '''
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)