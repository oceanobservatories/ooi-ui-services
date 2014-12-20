#!/usr/bin/env python
'''
tests.controller.test_array_controller

Test for the array controller
'''

__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase

class TestArrayController(ServicesTestCase):

    def test_responses(self):
        ServicesTestCase.setUp()
        ServicesTestCase.test_listing('/arrays')
        ServicesTestCase.test_empty_response('/arrays/notreal')
        ServicesTestCase.tearDown()