#!/usr/bin/env python
'''
Test the cmislib package created by Apache Chemistry project.

Version is currently at 0.5.1 and has very good reviews
from the community.

Created: 10/04/2015

'''

__author__ = 'M@Campbell'

import unittest
import os
from base64 import b64encode
from ooiservices.app import create_app

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class AlfrescoTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.basedir = os.path.abspath(os.path.dirname(__file__))

        # set the vars for the connection
        self.cmisUrl =  \
            'https://alfresco.oceanobservatories.org/alfresco/s/api/cmis'
        self.cmisUsername = 'ooinet'
        self.cmisPassword = '75commonLIKEbrown76'
        self.cmisId = 'c161bc66-4f7e-4a4f-b5f2-aac9fbf1d3cd'

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
        CmisClient

    def test_cmislib_connection(self):
        from cmislib.model import CmisClient

        # create the connection object
        client = CmisClient(self.cmisUrl, self.cmisUsername, self.cmisPassword)
        # check to make sure the object was created with the correct url
        self.assertEquals(client.repositoryUrl, self.cmisUrl)

        # use the client to connect to the repository
        repo = client.getRepository(self.cmisId)
        # make sure the repo information is referencing the correct repository
        self.assertEqual(repo.info['repositoryId'], self.cmisId)

    def test_cmislib_CRD(self):
        from cmislib.model import CmisClient
        client = CmisClient(self.cmisUrl, self.cmisUsername, self.cmisPassword)
        repo = client.getRepository(self.cmisId)

        # for tests, lets make sure the test folder isn't still there
        try:
            print ". . ."
            someObject = repo.getObjectByPath('/testFolder')
            someObject.deleteTree()
        except:
            print "\tno existing folders..."

        # create a new dir in the root folder
        print "\ttesting folder creation..."
        root = repo.rootFolder
        someFolder = root.createFolder('testFolder')

        # create a test file and drop it in the test folder.
        print "\ttesting file creation..."
        someFile = open(self.basedir + '/mock_data/test.txt', 'r')
        someFolder.createDocument('Test Document', contentFile=someFile)

        # test read by using a full-text search.
        print "\ttesting full-text search (read)..."
        repo.query("select * from cmis:document where contains('test')")

        # Then obliterate the folder and all it's children, mercilessly.
        print "\ttesting delete..."
        someFolder.deleteTree()
