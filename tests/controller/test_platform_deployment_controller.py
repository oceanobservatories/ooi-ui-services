#!/usr/bin/env python
'''
tests.controller.test_platform_controller

Test for the platform controller

'''
__author__ = 'Matt Campbell'

from tests.services_test_case import ServicesTestCase

class TestPlatformDeplymentController(ServicesTestCase):

    new_stc = ServicesTestCase()

    def test_responses(self):
        self.new_stc.setUp()
        self.new_stc.test_listing('/platform_deployments')
        self.new_stc.test_empty_response('/platform_deployments/notreal')
        self.new_stc.tearDown()