#!/usr/bin/env python
'''
tests.controller.test_instrument_deployment.py

Test for the platform controller
'''

__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase

class TestInstrumentDeplymentController(ServicesTestCase):

    def __init__(self):
        ServicesTestCase.__init__(self)

    def test_responses(self):
        ServicesTestCase.set_up()
        ServicesTestCase.test_listing('/instrument_deployments')
        ServicesTestCase.test_empty_response('/instrument_deployments/notreal')
        ServicesTestCase.tearDown()