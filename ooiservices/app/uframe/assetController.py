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

def _uframe_url(endpoint, id=None):
    if id is not None:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (endpoint, id)
        print uframe_url
    else:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % endpoint
        print uframe_url

    return uframe_url



#This class will handle the default checks of the uframe assets endpoint
# as well as cleaning up each of the route implementation (CRUD).
class uFrameAssetCollection(object):
    __endpoint__ = 'assets'
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

        uframe_assets_url = _uframe_url(self.__endpoint__, id)

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

#This class will handle the default checks of the uframe event endpoint
# as well as cleaning up each of the route implementation (CRUD).
class uFrameEventCollection(object):
    __endpoint__ = 'events'
    # m@c: Updated 03/03/2015
    __defaults__ = {
        "assetEventType" : None,
        "integratedInto" : {
            "metaData" : [ ],
            "assetInfo" : None,
            "manufacturerInfo" : None,
            "notes" : [ ],
            "assetId" : None,
            "attachments" : [ ],
            "purachaseAndDeliveryInfo" : None,
            "physicalInfo" : None,
            "identifier" : None,
            "traceId" : "",
            "overwriteAllowed" : False
            },
        "notes" : [ ],
        "startDate" : None,
        "endDate" : None,
        "attachments" : [ ],
        "eventId" : None,
        "eventDescription" : None,
        "recordedBy" : None,
        "assets" : [ {
            "metaData" : [ ],
            "assetInfo" : None,
            "manufacturerInfo" : None,
            "notes" : [ ],
            "assetId" : None,
            "attachments" : [ ],
            "purachaseAndDeliveryInfo" : None,
            "physicalInfo" : None,
            "identifier" : None,
            "traceId" : "",
            "overwriteAllowed" : False
            } ],
        "identifier" : None,
        "traceId" : "",
        "overwriteAllowed" : False
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
        print(id)
        uframe_events_url = _uframe_url(self.__endpoint__, id)

        try:
            data = requests.get(uframe_events_url)
        except:
            raise data.status_code
        self.obj = data.json()
        return self.obj

    #TODO: Create, Update, Delete methods.


    #Displays the default top level attributes of this class.
    def __repr__(self):
        return '[ %s ]' % self.__defaults__

@api.route('/events', methods=['GET'])
def get_events():
    '''
    Lists all the events
    '''
    #set up all the contaners.
    data = {}
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameEventCollection()
    data = uframe_obj.fetch()
    #parse the result and assign ref_des as top element.
    return jsonify({ 'events' : data })

@api.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    '''
    Lists one event by id
    '''
    #set up all the contaners.
    data = {}
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameEventCollection()
    data = uframe_obj.fetch(id)
    #parse the result and assign ref_des as top element.
    return jsonify(**data)


@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    '''
    Lists one asset by id
    '''
    uframe_obj = uFrameAssetCollection()
    data = uframe_obj.fetch(id)
    #parse the result and assign ref_des as top element.
    return jsonify(**data)

@api.route('/assets', methods=['GET'])
def get_asset_list():
    '''
    Lists all the assets
    '''
    #set up all the contaners.
    d = {}
    data = {}
    ref_des = None
    temp_body = []
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.fetch()
    #parse the result and assign ref_des as top element.
    for row in temp_list:
        if row['metaData'] is not None:
            for metaData in row['metaData']:
                if metaData['key'] == 'Ref Des':
                    ref_des = (metaData['value'])
                else:
                    d[metaData['key']] = metaData['value']
            temp_body.append(d)
            if len(temp_body) > 0:
                data[ref_des] = temp_body
            temp_body = []
    return jsonify({ 'assets' : data })



##################
#The following routes are for generating drop down lists, used in filtering view.
##################

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
    return jsonify({ 'asset_types' : data })

@api.route('/asset/classes', methods=['GET'])
def get_asset_classes_list():
    '''
    Lists all the class types available from uFrame.
    '''
    data = []
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.fetch()
    for row in temp_list:
        if row['@class'] is not None:
            data.append(row['@class'])
    data = _remove_duplicates(data)
    return jsonify({ 'class_types' : data })

@api.route('/asset/serials', methods=['GET'])
def get_asset_serials():
    '''
    Lists all the class types available from uFrame.
    '''
    data = []
    manufInfo = []
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.fetch()
    for row in temp_list:
        if row['manufactureInfo'] is not None:
            manufInfo.append(row['manufactureInfo'])
            for serial in manufInfo:
                data.append(serial['serialNumber'])
    data = _remove_duplicates(data)
    return jsonify({ 'serial_numbers' : data })


