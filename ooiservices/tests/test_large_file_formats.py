#!/usr/bin/env python
import unittest
from ooiservices.app import create_app
#from ooiservices.app.uframe.image_tools import _compile_large_format_files
from unittest import skipIf
import os

'''
Unit testing for Large File Format data
These tests are used to validate and test parsing of large format data
'''


@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class UframeLargeDataTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=False)

        # Set up the test case ref_des and date
        self.ref_des = 'RS03ASHS-MJ03B-05-OBSSPA302'
        self.year = '2015'
        self.month = '11'
        self.day = '30'
        self.date_str = '-'.join([self.year, self.month, self.day])

    def tearDown(self):
        self.app_context.pop()

    def test_compile_large_format_files(self):
        """
        Test that we can index the remote data server given a reference designator and date
        """

        """
        # Can't be sure this data will always be here so check the error
        data = _compile_large_format_files(self.ref_des, self.date_str)

        # There should be 15 records on this date
        self.assertEqual(len(data[self.ref_des][self.year][self.month][self.day]), 15)
        """

    def test_check_response(self):
        """
        Test the format of the response. Needs 'url'
        """

        """
        # Can't be sure this data will always be here so check the error
        data = _compile_large_format_files(self.ref_des, self.date_str)

        # Check the content of the first record
        self.assertIn('url', data[self.ref_des][self.year][self.month][self.day][0])
        """
