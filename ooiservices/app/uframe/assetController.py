#!/usr/bin/env python
'''
uframe assets endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, url_for, Flask, make_response, request
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
    else:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % endpoint
    return uframe_url

def _api_headers():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


#This class will handle the default checks of the uframe assets endpoint
# as well as cleaning up each of the route implementation (CRUD).
class uFrameAssetCollection(object):
    __endpoint__ = 'assets'
    # m@c: Updated 03/03/2015
    classType =  None
    metaData = []
    assetInfo = None
    manufactureInfo = None
    notes = None
    assetId = None
    attachments = []
    purchaseAndDeliveryInfo = None
    physicalInfo = None
    identifier = None
    traceId = None
    overwriteAllowed = False

    #Create a json object that contains all uframe assets.
    #This will be the collection that will may be parsed.
    obj = None

    def __init__(self):
        object.__init__(self)
        pass

    def to_json(self,id=None):
        data = []
        uframe_assets_url = _uframe_url(self.__endpoint__, id)
        try:
            data = requests.get(uframe_assets_url)
        except:
            raise data.status_code
        self.obj = data.json()
        return self.obj

    def from_json(self, json):
        # This currently is a 1 to 1 mapping from UI to uFrame.
        # Below section is from UI
        classType = json.get('@class')
        metaData = json.get('metaData')
        assetInfo = json.get('assetInfo')
        manufactureInfo = json.get('manufactureInfo')
        notes = json.get('notes')
        assetId = json.get('assetId')
        attachments = json.get('attachments')
        purchaseAndDeliveryInfo = json.get('purchaseAndDeliveryInfo')
        physicalInfo = json.get('physicalInfo')
        ### These are not returned, for now they don't exist in uframe.
        identifier = json.get('identifier')
        traceId = json.get('traceId')
        overwriteAllowed = json.get('overwriteAllowed')
        #####

        #Below section's keys are uFrame specific and shouldn't be modified
        #unless necessary to support uframe updates.
        formatted_return = {
                "@class": classType,
                "metaData": metaData,
                "assetInfo": assetInfo,
                "manufacturerInfo": manufactureInfo,
                "notes": notes,
                "assetId": assetId,
                "attachments": attachments,
                "purchaseAndDeliveryInfo": purchaseAndDeliveryInfo,
                "physicalInfo": physicalInfo,
                "manufactureInfo": manufactureInfo
                }
        return formatted_return

    #Displays the default top level attributes of this class.
    def __repr__(self):
        return '<AssetID: %r>' % (self.assetId)

#This class will handle the default checks of the uframe event endpoint
# as well as cleaning up each of the route implementation (CRUD).
class uFrameEventCollection(object):
    __endpoint__ = 'events'
    # m@c: Updated 03/03/2015
    assetEventType = None
    integratedInto = {}
    notes = []
    startDate = None
    endDate = None
    attachments = None
    eventId = None
    eventDescription = None
    recordedBy = None
    assets = {}
    identifier = None
    traceId = None
    overwriteAllowed = None

    #Create a json object that contains all uframe assets.
    #This will be the collection that will may be parsed.
    obj = None

    def __init__(self):
        object.__init__(self)
        pass

    def to_json(self,id=None):
        data = []
        print(id)
        uframe_events_url = _uframe_url(self.__endpoint__, id)
        try:
            data = requests.get(uframe_events_url)
        except:
            raise data.status_code
        self.obj = data.json()
        return self.obj

    def from_json(json):
        assetEventType = json.get('assetEventType')
        integratedInto = json.get('integratedInto')
        notes = json.get('notes')
        startDate = json.get('startDate')
        endDate = json.get('endDate')
        attachments = json.get('attachments')
        eventId = json.get('eventId')
        eventDescription = json.get('eventDescription')
        recordedBy = json.get('recordedBy')
        assets = json.get('assets')
        ### These are not returned, for now they don't exist in uframe.
        identifier = json.get('identifier')
        traceId = json.get('traceId')
        overwriteAllowed = json.get('overwriteAllowed')
        ########
        return uFrameEventCollection(assetEventType = assetEventType, integratedInto = integratedInto, notes = notes, startDate = startDate, endDate = endDate, attachments = attachments, eventId = eventId, eventDescription = eventDescription, recordedBy = recordedBy, assets = assets)


    #Displays the default top level attributes of this class.
    def __repr__(self):
        return '<EventID: %r>' % (self.assetId)

### ---------------------------------------------------------------------------
### BEGIN Assets CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
    ##TABLE THIS FOR NOW...
    '''@api.route('/assets', methods=['GET'])
    def get_asset_list():
        #set up all the contaners.
        d = {}
        data = {}
        ref_des = None
        temp_body = []
        #create uframe instance, and fetch the data.
        uframe_obj = uFrameAssetCollection()
        temp_list = uframe_obj.to_json()
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
    '''

@api.route('/assets', methods=['GET'])
def get_assets():
    '''
    Lists all the assets
    '''
    #set up all the contaners.
    data = {}
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameAssetCollection()
    data = uframe_obj.to_json()
    #parse the result and assign ref_des as top element.
    return jsonify({ 'assets' : data })

#Read (object)
@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    '''
    Lists one asset by id
    '''
    uframe_obj = uFrameAssetCollection()
    data = uframe_obj.to_json(id)
    #parse the result and assign ref_des as top element.
    return jsonify(**data)

#Create
@api.route('/assets', methods=['POST'])
def create_asset():
    from ooiservices.app.uframe.assetController import uFrameAssetCollection as Uframe
    '''
    Create an asset from json input.
    '''
    data = json.loads(request.data)
    uframe_obj = uFrameAssetCollection()
    post_body = uframe_obj.from_json(data)
    uframe_assets_url = _uframe_url(uframe_obj.__endpoint__)
    response = requests.post(uframe_assets_url, data=json.dumps(post_body), headers=_api_headers())
    return response.text

#Update
@api.route('/assets/<int:id>', methods=['PUT'])
def update_asset(id):
    data = json.loads(request.data)
    uframe_obj = uFrameAssetCollection()
    put_body = uframe_obj.from_json(data)
    uframe_assets_url = _uframe_url(uframe_obj.__endpoint__, id)
    response = requests.put(uframe_assets_url, data=json.dumps(put_body), headers=_api_headers())
    return response.text

### ---------------------------------------------------------------------------
### END Assets CRUD methods.
### ---------------------------------------------------------------------------

### ---------------------------------------------------------------------------
### BEGIN Events CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
@api.route('/events', methods=['GET'])
def get_events():
    '''
    Lists all the events
    '''
    #set up all the contaners.
    data = {}
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameEventCollection()
    data = uframe_obj.to_json()
    #parse the result and assign ref_des as top element.
    return jsonify({ 'events' : data })

#Read (object)
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
### ---------------------------------------------------------------------------
### END Events CRUD methods.
### ---------------------------------------------------------------------------

### ---------------------------------------------------------------------------
### The following routes are for generating drop down lists, used in filtering view.
### ---------------------------------------------------------------------------

@api.route('/asset/types', methods=['GET'])
def get_asset_types():
    '''
    Lists all the asset types available from uFrame.
    '''
    data = []
    assetType = []
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.to_json()
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
    temp_list = uframe_obj.to_json()
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
    temp_list = uframe_obj.to_json()
    for row in temp_list:
        if row['manufactureInfo'] is not None:
            manufInfo.append(row['manufactureInfo'])
            for serial in manufInfo:
                data.append(serial['serialNumber'])
    data = _remove_duplicates(data)
    return jsonify({ 'serial_numbers' : data })


