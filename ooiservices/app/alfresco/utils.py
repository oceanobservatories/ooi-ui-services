#!/usr/bin/env python
'''

'''
__author__ = 'M@Campbell'

import os
import requests
import json
from cmislib.model import CmisClient
import re
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
        self.ALFRESCO_LINK_URL = current_app.config['ALFRESCO_LINK_URL'] or \
            os.environ.get('ALFRESCO_LINK_URL')
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


    def get_cruise_documents(self, cruise):
        """
         Get_cruise_documents for KN-222
        =====Pioneer-3_Leg-1_KN-222_2014-10-03=====
          -- 3204-00302_Quick_Look_Cruise_Report_Coastal_Pioneer_3_Leg_1_2015-01-29_Ver_1-00.pdf workspace://SpacesStore/5b22d992-7165-4e5b-80aa-5e6cca46fdd5
          -- 3204-00301_Cruise_Plan_Coastal_Pioneer_3_Leg_1_2014-10-02_Ver_1-00.pdf workspace://SpacesStore/afac7be0-8b79-421e-86a9-70fd65f24270
          -- 3204-00303_Cruise_Report_Coastal_Pioneer_3_Leg_1_2015-04-28_Ver_1-00.pdf workspace://SpacesStore/30d41068-2714-443a-bd92-660319cf9f68

        document.name:  3204-00303_Cruise_Report_Coastal_Pioneer_3_Leg_1_2015-04-28_Ver_1-00.pdf
        document.id:    workspace://SpacesStore/30d41068-2714-443a-bd92-660319cf9f68
        """
        # Create the cmis client
        client = CmisClient(self.ALFRESCO_URL, self.ALFRESCO_UN, self.ALFRESCO_PW)

        # Connect to the alfresco server and return the repo object
        repo = client.getRepository(self.ALFRESCO_ID)

        cruise_param = '%'+cruise+'%'
        query_folder_id = "select cmis:objectId, cmis:name from cmis:folder where cmis:name like '" +cruise_param+ "'"
        folders = repo.query(query_folder_id)
        cruise_id = None
        documents = []
        # Get items in folder
        for folder in folders:
            cruise_id = folder
            cruise_id.type = 'cruise'
            query_get_files = "select cmis:objectId, cmis:name from cmis:document where in_folder('%s') order by cmis:lastModificationDate desc" % folder.id
            documents = repo.query(query_get_files)
            for document in documents:
                #print "  --", document.name, document.id
                document.type = 'cruise'
            # UI can only process one set at a time with current response structure.
            break

        return documents, cruise_id

    def make_alfresco_cruise_query(self, array, cruise):
        """ Query the alfresco server for all documents relating to a cruise
        """
        # create the cmis client
        client = CmisClient(self.ALFRESCO_URL, self.ALFRESCO_UN, self.ALFRESCO_PW)

        # connect to the alfresco server and return the repo object
        repo = client.getRepository(self.ALFRESCO_ID)
        # use this files connection method

        doc = repo.getObjectByPath("/OOI/"+array+" Array/Cruise Data")
        folder_query = "IN_FOLDER('"+doc.id+"')"

        array_cruises = repo.query("select * FROM cmis:folder  WHERE "+folder_query)

        #setup the cruise information
        results = []
        cruise_id = None
        if len(cruise) > 0:
            cruise_split = re.split('\s|-|;|,|\*|\n',cruise)
            cruise = "-".join(cruise_split)
            #unique case...
            if cruise == "Scarlett-Isabella":
                cruise = "SI"

            for r in array_cruises:
                cruise_str = r.getName().split("_")[1]
                if cruise in cruise_str:
                    cruise_id = r
                    break

            # Only if the cruise information if its available.
            if cruise_id is not None:
                cruise_results = repo.query("select * FROM cmis:document where IN_FOLDER('"+cruise_id.id+"')")
                for c in cruise_results:
                    c.type = "cruise"
                #add the cruise link
                cruise_id.type = "link"
                return cruise_results,cruise_id

        #return the defaults if not available
        return results, cruise_id

    def make_alfresco_page_link(self,id,ticket):
        '''
        creates an alfresco url page link
        '''
        arrID = id.split('/')
        hex_id = arrID[3]
        url = self.ALFRESCO_LINK_URL+hex_id
        return url

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

        download_url = ''.join((self.ALFRESCO_DL_URL, '/', hex_id, '?alf_ticket=', ticket))

        return download_url
