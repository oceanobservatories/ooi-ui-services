#!/usr/bin/env python
'''
tests.services_test_case

The base class for the Services Test Case
'''

import unittest
import os
import shutil

class ServicesTestCase(unittest.TestCase):
    '''
    The base test case for the Services unit tests
    '''
    output_dir = 'test-output'
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        '''
        Creates a directory for testing output and debugging
        '''
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def tearDown(self):
        '''
        Removes the directory
        '''
        shutil.rmtree(self.output_dir)

