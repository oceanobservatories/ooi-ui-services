#!/usr/bin/env python
'''
uframe assets endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, Flask, make_response, request
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth,verify_auth
from ooiservices.app.main.errors import internal_server_error
from LatLon import string2latlon
import json
import requests
import re

def _normalize_whitespace(string):
    #Requires re
    string = string.strip()
    string = re.sub(r'\s+', ' ', string)
    return string

def _remove_duplicates(values):
    #Requires re
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        #  add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def _uframe_collection(endpoint, id=None):
    data = None
    if id is not None:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (endpoint, id)
    else:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % endpoint
    try:
        data = requests.get(uframe_url)
        return data.json()
    except:
        if data == None:
            raise Exception("uframe connection cannot be established for: Assets")
        raise data.status_code

def _api_headers():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def _normalize(to_translate, translate_to=u' '):
    ascii =  ''.join([i if ord(i) < 128 else ' ' for i in to_translate])
    not_letters_or_digits = u'\'\"'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    normalized = _normalize_whitespace(ascii.translate(translate_table))
    return normalized

def _convert_lat_lon(lat, lon):
    #Requires LatLon
    conv_lat = _normalize(lat)
    conv_lon = _normalize(lon)
    try:
        coords = string2latlon(conv_lat, conv_lon, 'd% %M% %H')
        return coords.to_string('D')
    except Exception as e:
        return "Error: %s" % e

def _convert_date_time(date, time="00:00"):
    #For now, just concat the date and time:
    return "%s %s" % (date, time)

def _convert_water_depth(depth):
    d = {}
    if len(depth.split( )) == 2:
        value = depth.split()[0]
        unit = depth.split()[1]
        d['value'] = float(value)
        d['unit'] = str(unit)
        return d
    else:
        no_alpha = re.sub("[^0-9]", "", depth)
        d['value'] = float(no_alpha)
        d['unit'] = "m"
        return d

def _associate_events(id):
    uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/assets/%s/event' % (id)
    try:
        data = requests.get(uframe_url)
        return data.json()
    except:
        return data.text

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
        data = _uframe_collection(self.__endpoint__, id)
        return data

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
    #Create a json object that contains all uframe assets.
    #This will be the collection that will may be parsed.
    obj = None

    def __init__(self):
        object.__init__(self)
        pass

    def to_json(self,id=None):
        data = _uframe_collection(self.__endpoint__, id)
        return data

    def from_json(self, json):
        eventClass = json.get('@class')
        referenceDesignator = json.get('referenceDesignator')
        deploymentNumber = json.get('deploymentNumber')
        deploymentName = json.get('deploymentName')
        deploymentDepth = json.get('deploymentDepth')
        depthUnitString = json.get('depthUnitString')
        deploymentDocUrls = json.get('deploymentDocUrls')
        cruiseNumber = json.get('cruiseNumber')
        locationLonLat = json.get('locationLonLat')
        locationName = json.get('locationName')
        eventType = json.get('eventType')
        startDate = json.get('startDate')
        endDate = json.get('endDate')
        eventId = json.get('eventId')
        eventDescription = json.get('eventDescription')
        recordedBy = json.get('recordedBy')
        asset = json.get('asset')
        notes = json.get('notes')
        attachments = json.get('attachments')
        tense = json.get('tense')
        lastModifiedTimestamp = json.get('lastModifiedTimestamp')

        formatted_return = {
            '@class' : eventClass,
            'referenceDesignator': referenceDesignator,
            'deploymentNumber': deploymentNumber,
            'deploymentName': deploymentName,
            'deploymentDepth': deploymentDepth,
            'depthUnitString': depthUnitString,
            'deploymentDocUrls': deploymentDocUrls,
            'cruiseNumber': cruiseNumber,
            'locationLonLat': locationLonLat,
            'locationName': locationName,
            'eventType': eventType,
            'startDate': startDate,
            'endDate': endDate,
            'eventId': eventId,
            'eventDescription': eventDescription,
            'recordedBy': recordedBy,
            'asset': asset,
            'notes': notes,
            'attachments': attachments,
            'tense': tense,
            'lastModifiedTimestamp': lastModifiedTimestamp
        }
        return formatted_return

    #Displays the default top level attributes of this class.
    def __repr__(self):
        return '<EventID: %r>' % (self.assetId)

### ---------------------------------------------------------------------------
### BEGIN Assets CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
@api.route('/assets', methods=['GET'])
def get_assets():
    #set up all the contaners.
    data = {}
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameAssetCollection()
    data = uframe_obj.to_json()
    lat = ""
    lon = ""
    date_launch = ""
    time_launch = ""
    ref_des = ""
    depth = ""
    for row in data:
        row['class'] = row.pop('@class')
        if row['metaData'] is not None:
            for metaData in row['metaData']:
                if metaData['key'] == 'Latitude':
                    lat = metaData['value']
                if metaData['key'] == 'Longitude':
                    lon = metaData['value']
                if metaData['key'] == "Anchor Launch Date":
                    date_launch = metaData['value']
                if metaData['key'] == "Anchor Launch Time":
                    time_launch = metaData['value']
                if metaData['key'] == 'Water Depth':
                    depth = metaData['value']
                if metaData['key'] == 'Ref Des':
                    ref_des = (metaData['value'])
            if len(lat) > 0 and len(lon) > 0:
                row['coordinates'] = _convert_lat_lon(lat, lon)
                lat = ""
                lon = ""
            if len(date_launch) > 0 and len(time_launch) > 0:
                row['launch_date_time'] = _convert_date_time(date_launch, time_launch)
                date_launch = ""
                time_launch = ""
            elif len(date_launch) > 0:
                row['launch_date_time'] = _convert_date_time(date_launch)
                date_launch = ""
                time_launch = ""
            if len(depth) > 0:
                row['water_depth'] = _convert_water_depth(depth)
                depth = ""
            if len(ref_des) > 0:
                row['ref_des'] = ref_des
                ref_des = ""

        row['metaData'] = ""
    return jsonify({ 'assets' : data })

#Read (object)
@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    uframe_obj = uFrameAssetCollection()
    data = uframe_obj.to_json(id)
    lat = ""
    lon = ""
    date_launch = ""
    time_launch = ""
    ref_des = ""
    depth = ""
    data['class'] = data.pop('@class')
    for metaData in data['metaData']:
        if metaData['key'] == 'Latitude':
            lat = metaData['value']
        if metaData['key'] == 'Longitude':
            lon = metaData['value']
        if metaData['key'] == "Anchor Launch Date":
            date_launch = metaData['value']
        if metaData['key'] == "Anchor Launch Time":
            time_launch = metaData['value']
        if metaData['key'] == 'Water Depth':
            depth = metaData['value']
    if len(lat) > 0 and len(lon) > 0:
        data['coordinates'] = _convert_lat_lon(lat, lon)
        lat = ""
        lon = ""
    if len(date_launch) > 0 and len(time_launch) > 0:
        data['launch_date_time'] = _convert_date_time(date_launch, time_launch)
        date_launch = ""
        time_launch = ""
    elif len(date_launch) > 0:
        data['launch_date_time'] = _convert_date_time(date_launch)
        date_launch = ""
        time_launch = ""
    if len(depth) > 0:
        data['water_depth'] = _convert_water_depth(depth)
        depth = ""
    if len(ref_des) > 0:
        data['ref_des'] = ref_des
        ref_des = ""

    data['events'] = _associate_events(id)

    return jsonify(**data)

#Create
@api.route('/assets', methods=['POST'])
def create_asset():
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

#Delete
#Not supported

### ---------------------------------------------------------------------------
### END Assets CRUD methods.
### ---------------------------------------------------------------------------

### ---------------------------------------------------------------------------
### BEGIN Events CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
@api.route('/events', methods=['GET'])
def get_events():
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
    #set up all the contaners.
    data = {}
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameEventCollection()
    data = uframe_obj.fetch(id)
    return jsonify(**data)

#Create
@api.route('/events', methods=['POST'])
def create_event():
    data = json.loads(request.data)
    uframe_obj = uFrameEventCollection()
    post_body = uframe_obj.from_json(data)
    uframe_events_url = _uframe_url(uframe_obj.__endpoint__)
    response = requests.post(uframe_events_url, data=json.dumps(post_body), headers=_api_headers())
    return response.text

#Update
@api.route('/events/<int:id>', methods=['PUT'])
def update_event(id):
    data = json.loads(request.data)
    uframe_obj = uFrameEventCollection()
    put_body = uframe_obj.from_json(data)
    uframe_events_url = _uframe_url(uframe_obj.__endpoint__, id)
    response = requests.put(uframe_events_url, data=json.dumps(put_body), headers=_api_headers())
    return response.text

#Delete
#Not supported

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

@api.route('/assets/condense', methods=['GET'])
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
