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

def _remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        #  add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

#This class will handle the default checks of the uframe assets endpoint
# as well as cleaning up each of the route implementation (CRUD).
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
        self.obj = data.json()
        return self.obj

    #TODO: Create, Update, Delete methods.


    #Displays the default top level attributes of this class.
    def __repr__(self):
        return '[ %s ]' % self.__defaults__


@api.route('/assets', methods=['GET'], defaults={'id': None})
@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    '''
    Lists all the assets if id is none, returns a single asset if id is a valid int
    '''
    uframe_obj = uFrameAssetCollection()
    response = uframe_obj.fetch(id)
    return jsonify({ 'assets' : [response] })

@api.route('/asset/types', methods=['GET'])
def get_asset_types():
    '''
    Lists all the asset types available from uFrame.
    '''
    data = []
    assetType = []
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.fetch()
    for row in temp_list:
        if row['assetInfo'] is not None:
            assetType.append(row['assetInfo'])
            for assType in assetType:
                data.append(assType['type'])
    data = _remove_duplicates(data)
    #unique_list = {v['assetInfo']:v for v in temp_list}.values()
    return jsonify({ 'asset_types' : data })


