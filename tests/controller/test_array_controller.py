#!/usr/bin/env python
'''
tests.controller.test_array_controller

Test for the array controller
'''

__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase as STC

class TestArrayController(STC):

    def __init__(self):
        STC.__init__(self)

    def test_responses(self):
        STC.set_up()
        STC.test_listing('/arrays')
        STC.test_empty_response('/arrays/notreal')
        STC.tearDown()