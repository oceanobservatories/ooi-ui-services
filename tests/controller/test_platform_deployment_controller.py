#!/usr/bin/env python
'''
tests.controller.test_platform_controller

Test for the platform controller

'''
__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase

class TestPlatformDeplymentController(STC):

    def __init__(self):
        STC.__init__(self)

    def test_responses(self):
        STC.set_up()
        STC.test_listing('/platform_deployments')
        STC.test_empty_response('/platform_deployments/notreal')
        STC.tearDown()