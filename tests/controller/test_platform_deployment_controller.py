#!/usr/bin/env python
'''
tests.controller.test_platform_controller

Test for the platform controller

'''
__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase

class TestPlatformDeplymentController(ServicesTestCase):

    def test_responses(self):
        ServicesTestCase.setUp()
        ServicesTestCase.test_listing('/platform_deployments')
        ServicesTestCase.test_empty_response('/platform_deployments/notreal')
        ServicesTestCase.tearDown()