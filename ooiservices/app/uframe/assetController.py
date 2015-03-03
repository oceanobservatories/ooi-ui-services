#!/usr/bin/env python
'''
uframe assets endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, url_for, Flask, make_response
from ooiservices.app.uframe import uframe as api
from ooiservices.app import db, cache, celery
from ooiservices.app.main.authentication import auth,verify_auth
from ooiservices.app.main.errors import internal_server_error
import json
import requests



#This class will handle the default checks of the uframe assets endpoint
# as well as cleaning up each the route implementation (CRUD).
class uFrameAssetCollection(object):
    # m@c: Updated 03/03/2015
    __defaults__ = {
        "@class": None,
        "metadata": [],
        "assetInfo": None,
        "manufacturerInfo": None,
        "notes": None,
        "assetId": None,
        "attachments": [],
        "purchaseAndDeliveryInfo": None,
        "physicalInfo": None,
        "identifier": None,
        "traceId": None,
        "overwriteAllowed": False
    }

    #Create a json object that contains all uframe assets.
    #This will be the collection that will may be parsed.
    obj = None

    def __init__(self):
        object.__init__(self)
        pass

    #READ (list)
    def fetch(self,id=None):
        data = []

        if id is not None:
            uframe_assets_url = current_app.config['UFRAME_ASSETS_URL'] + '/assets/%s' % id
        else:
            uframe_assets_url = current_app.config['UFRAME_ASSETS_URL'] + '/assets'

        try:
            data = requests.get(uframe_assets_url)
        except:
            raise data.status_code
        self.obj = data.text
        return self.obj

    #TODO: Create, Update, Delete methods.


    #Displays the default top level attributes of this class.
    def __repr__(self):
        return '[ %s ]' % self.__defaults__



@api.route('/assets', methods=['GET'], defaults={'id': None})
@api.route('/assets/<int:id>', methods=['GET'])
def get_list(id):
    '''
    Lists all the assets if id is none, returns a single asset if id is a valid int
    '''
    uframe_obj = uFrameAssetCollection()
    response = uframe_obj.fetch(id)
    return response

