#!/usr/bin/env python
'''
tests.controller.test_array_controller

Test for the array controller
'''

__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase

class TestArrayController(ServicesTestCase):

    new_stc = ServicesTestCase()

    def test_responses(self):
        self.new_stc.setUp()
        self.new_stc.test_listing('/arrays')
        self.new_stc.test_empty_response('/arrays/notreal')
        self.new_stc.tearDown()