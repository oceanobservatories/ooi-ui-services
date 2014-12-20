#!/usr/bin/env python
'''
tests.controller.test_instrument_deployment.py

Test for the platform controller
'''

__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase as STC

class TestInstrumentDeplymentController(STC):

    def __init__(self):
        STC.__init__(self)

    def test_responses(self):
        STC.set_up()
        STC.test_listing('/instrument_deployments')
        STC.test_empty_response('/instrument_deployments/notreal')
        STC.tearDown()