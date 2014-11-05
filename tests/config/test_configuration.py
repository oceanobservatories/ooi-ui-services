#!/usr/bin/env python
'''
tests.config.test_configuration

Tests the configuration management of the OOI Services
'''

from tests.services_test_case import ServicesTestCase

class TestConfiguration(ServicesTestCase):
    '''
    Unit Tests for configurations
    '''

    def test_configuration_string(self):
        '''
        A temporary test that validates that the configuration
        yaml file is being parsed and that it's contents are being
        set to the globals of the config module
        '''

        from ooiservices.config import DataSource
        assert DataSource['DBName'] == 'db/test.db'
