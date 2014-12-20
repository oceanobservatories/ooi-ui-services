#!/usr/bin/env python
'''
tests.controller.test_instrument_deployment.py

Test for the platform controller
'''

__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase

class TestInstrumentDeplymentController(ServicesTestCase):

    new_stc = ServicesTestCase()

    def test_responses(self):
        self.new_stc.set_up()
        self.new_stc.test_listing('/instrument_deployments')
        self.new_stc.test_empty_response('/instrument_deployments/notreal')
        self.new_stc.tearDown()