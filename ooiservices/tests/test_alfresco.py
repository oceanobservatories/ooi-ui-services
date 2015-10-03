#!/usr/bin/env python
'''
Specific testing of routes.

'''

__author__ = 'M@Campbell'

import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app


class AlfrescoTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_cmislib_loaded(self):
        '''
        Make sure the cmislib library is properly loaded.
        '''
        from cmislib.model import CmisClient

    def test_cmislib_connection(self):
        from cmislib.model import CmisClient
        # set the vars for the connection
        cmisUrl = 'https://alfresco.oceanobservatories.org/alfresco/s/api/cmis'
        cmisUsername = 'ooinet'
        cmisPassword = '75commonLIKEbrown76'
        cmisId = 'c161bc66-4f7e-4a4f-b5f2-aac9fbf1d3cd'

        # create the connection object
        client = CmisClient(cmisUrl, cmisUsername, cmisPassword)
        # check to make sure the object was created with the correct url
        self.assertEquals(client.repositoryUrl, cmisUrl)

        # use the client to connect to the repository
        repo = client.getRepository(cmisId)
        # make sure the repo information is referencing the correct repository
        self.assertEqual(repo.info['repositoryId'], cmisId)
