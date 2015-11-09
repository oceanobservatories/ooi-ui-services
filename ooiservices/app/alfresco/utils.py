#!/usr/bin/env python
'''

'''
__author__ = 'M@Campbell'

import os
import requests
import json
from cmislib.model import CmisClient

from flask import current_app


class AlfrescoCMIS(object):
    def __init__(self):
        object.__init__(self)
        '''
        Set up the config variables.
        '''
        self.ALFRESCO_URL = current_app.config['ALFRESCO_CMIS_URL'] or \
            os.environ.get('ALFRSCO_CMIS_URL')
        self.ALFRESCO_UN = current_app.config['ALFRESCO_USERNAME'] or \
            os.environ.get('ALFRESCO_USERNAME')
        self.ALFRESCO_PW = current_app.config['ALFRESCO_PASSWORD'] or \
            os.environ.get('ALFRESCO_PW')
        self.ALFRESCO_ID = current_app.config['ALFRESCO_REPO_ID'] or \
            os.environ.get('ALFRESCO_REPO_ID')
        self.ALFRESCO_TICKET_URL = current_app.config['ALFRESCO_TICKET_URL'] or \
            os.environ.get('ALFRSCO_TICKET_URL')
        self.ALFRESCO_DL_URL = current_app.config['ALFRESCO_DL_URL'] or \
            os.environ.get('ALFRESCO_DL_URL')
        pass

    def make_alfresco_conn(self):
        # create the cmis client
        client = CmisClient(
            self.ALFRESCO_URL, self.ALFRESCO_UN, self.ALFRESCO_PW)

        # connect to the alfresco server and return the repo object
        repo = client.getRepository(self.ALFRESCO_ID)

        # this will be what we work with primarily
        # returns a repo object
        return repo

    def make_alfresco_ticket(self):
        # make a post request, which is the preferred method to get
        # a alfresco ticket. ticket will last 1 hour.
        response = requests.post(self.ALFRESCO_TICKET_URL,
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'username': self.ALFRESCO_UN,
                'password': self.ALFRESCO_PW}))
        return response

    def make_alfresco_query(self, query):
        '''
        query the alfresco server for all documents matching the search param.
        **CAUTION: THIS MAY TAKE A WHILE TO RESPOND**
        '''
        # create the cmis client
        client = CmisClient(
            self.ALFRESCO_URL, self.ALFRESCO_UN, self.ALFRESCO_PW)

        # connect to the alfresco server and return the repo object
        repo = client.getRepository(self.ALFRESCO_ID)
        # use this files connection method

        # issue the query
        results = repo.query("select * from cmis:document where contains('\"%s\"')" % query)

        return results

    def make_alfresco_cruise_query(self, array,cruise):
        '''
        query the alfresco server for all documents relating to a cruise
        '''
        # create the cmis client
        client = CmisClient(self.ALFRESCO_URL, self.ALFRESCO_UN, self.ALFRESCO_PW)

        # connect to the alfresco server and return the repo object
        repo = client.getRepository(self.ALFRESCO_ID)
        # use this files connection method

        cruise = cruise.split(" ")[1]

        doc = repo.getObjectByPath("/OOI/"+array+" Array/Cruise Data")
        folder_query = "IN_FOLDER('"+doc.id+"')"
        cruise_query = " AND CONTAINS('cmis:name:*"+cruise+"*')"
        array_cruises = repo.query("select * FROM cmis:folder  WHERE "+folder_query)

        cruise_id = None
        for r in array_cruises:
            if cruise in r.getName():
                cruise_id = r.id
                results = repo.query("select * FROM cmis:folder"+" WHERE "+folder_query + cruise_query)
                if len(results) == 1:
                    print "\n----CRUISE"
                    for r in results:
                        print r.getName(),r.id

                    print "\n----FILES"
                    results = repo.query("select * FROM cmis:document where IN_FOLDER('"+results[0].id+"')")

                    for r in results:
                        print r.getName()
                    break

        # issue the query
        return results

    def make_alfresco_download_link(self, id, ticket):
        '''
        In order to download a document, a specific URL needs to be used.
        Each link needs to be passed in the new ticket in order to download.

        param: ticket ; this is the ticket that will be used to authenticate
            the request
        '''

        # then lets split out the object id and use use the hex portion . . .
        arrID = id.split('/')
        hex_id = arrID[3]

        # and before we return, we just need to combine all three parts
        # to make a nice url for a authenticated user to download.

        download_url = ''.join((self.ALFRESCO_DL_URL, '/',
            hex_id, '?alf_ticket=', ticket))

        return download_url
