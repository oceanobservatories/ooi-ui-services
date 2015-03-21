#!/usr/bin/env python
'''
uframe assets endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request, url_for, make_response
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app import cache
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

def _uframe_url(endpoint, id=None):
    if id is not None:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (endpoint, id)
    else:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % endpoint
    return uframe_url

def _uframe_collection(uframe_url):
    data = []
    try:
        data = requests.get(uframe_url)
        return data.json()
    except:
        data = {'error': 'INTERNAL_SERVER_ERROR',
                'status_code': 500,
                'message': 'Cannot connect to uframe.'}
        return data

def _uframe_headers():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def _normalize(to_translate, translate_to=u' '):
    try:
        ascii =  ''.join([i if ord(i) < 128 else ' ' for i in to_translate])
        scrub = u'\'\"'
        translate_table = dict((ord(char), translate_to) for char in scrub)
        normalized = _normalize_whitespace(ascii.translate(translate_table))
        return normalized
    except Exception as e:
        return "%s" % e

def _convert_lat_lon(lat, lon):
    #Requires LatLon
    conv_lat = _normalize(lat)
    conv_lon = _normalize(lon)
    try:
        if len(conv_lat.split()) == 4  and len(conv_lon.split()) == 4:
            coords = string2latlon(conv_lat, conv_lon, 'd% %m% %M% %H')
        else:
            coords = string2latlon(conv_lat, conv_lon, 'd% %M% %H')
        str_coords = coords.to_string('D')
        float_coords = [float(str_coords[0]), float(str_coords[1])]
        return float_coords
    except Exception as e:
        return "Error: %s" % e

def _convert_date_time(date, time=None):
    if time is None:
        return date
    else:
        return "%s %s" % (date, time)

def _convert_water_depth(depth):
    d = {}
    try:
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
    except ValueError as ve:
        return {'message': 'Conversion Error!',
                'input': depth}

def _associate_events(id):
    uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/assets/%s/events' % (id)
    result = []
    data = requests.get(uframe_url)
    json_data = data.json()
    for row in json_data:
        d = {'url': url_for('uframe.get_event', id=row['eventId']),
                'uframe_url': current_app.config['UFRAME_ASSETS_URL'] + '/events/%s' % row['eventId']}
        d['eventId'] = row['eventId']
        d['class'] = row['@class']
        d['notes'] = len(row['notes'])
	d['startDate'] = row['startDate']
        result.append(d)

    return result

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
        url = _uframe_url(self.__endpoint__, id)
        data = _uframe_collection(url)
        return data

    def from_json(self, json):
        # Below section is from UI
        classType = json.get('class')
        assetInfo = json.get('assetInfo')
        manufactureInfo = json.get('manufactureInfo')
        notes = json.get('notes')
        assetId = json.get('assetId')
        attachments = json.get('attachments')
        purchaseAndDeliveryInfo = json.get('purchaseAndDeliveryInfo')
        physicalInfo = json.get('physicalInfo')
        coordinates = json.get('coordinates')
        launch_date_time = json.get('launch_date_time')
        water_depth = json.get('water_depth')
        ref_des = json.get('ref_des')
        ### These are not returned, for now they don't exist in uframe.
        identifier = json.get('identifier')
        traceId = json.get('traceId')
        overwriteAllowed = json.get('overwriteAllowed')
        #####
        #Build metadata dictionary
        metaData = []
        dict_depth = {}
        dict_lat = {}
        dict_lon = {}
        dict_launch_date = {}
        dict_ref_des = {}
        if water_depth is not None:
            dict_depth = {
                "key": "Water Depth",
                "value": "%s %s" % (water_depth['value'], water_depth['unit']),
                "type": "java.lang.String"
            }
            metaData.append(dict_depth)
        if coordinates is not None and len(coordinates) == 2:
            dict_lat = {
                "key": "Latitude",
                "value": coordinates[0],
                "type": "java.lang.String"
            }
            metaData.append(dict_lat)
            dict_lon =  {
                "key": "Longitude",
                "value": coordinates[1],
                "type": "java.lang.String"
            }
            metaData.append(dict_lon)
        if launch_date_time is not None:
            dict_launch_date =  {
                "key": "Anchor Launch Date",
                "value": launch_date_time,
                "type": "java.lang.String"
            }
            metaData.append(dict_launch_date)
        if ref_des is not None:
            dict_ref_des = {
              "key": "Ref Des",
              "type": "java.lang.String",
              "value": ref_des
            }
            metaData.append(dict_ref_des)

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
                "physicalInfo": physicalInfo
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
        url = _uframe_url(self.__endpoint__, id)
        data = _uframe_collection(url)
        return data

    def from_json(self, json):
        eventClass = json.get('class')
        referenceDesignator = json.get('referenceDesignator')
        deploymentNumber = json.get('deploymentNumber')
        deploymentName = json.get('deploymentName')
        deploymentDepth = json.get('deploymentDepth')
        depthUnitString = json.get('depthUnitString')
        deploymentDocUrls = json.get('deploymentDocUrls')
        deploymentLocation = json.get('deploymentLocation')
        cruiseNumber = json.get('cruiseNumber')
        locationLonLat = json.get('locationLonLat')
        locationName = json.get('locationName')
        eventType = json.get('eventType')
        startDate = json.get('startDate')
        endDate = json.get('endDate')
        eventDescription = json.get('eventDescription')
        recordedBy = json.get('recordedBy')
        asset = json.get('asset')
        notes = json.get('notes')
        attachments = json.get('attachments')
        tense = json.get('tense')
        lastModifiedTimestamp = json.get('lastModifiedTimestamp')

        #Update deploymentLocation to send a float even if Lat/Lon is an int.
        deploymentLocation = [
            float(deploymentLocation[0]),
            float(deploymentLocation[1])
        ]

        formatted_return = {
            '@class' : eventClass,
            'referenceDesignator': referenceDesignator,
            'deploymentNumber': deploymentNumber,
            'deploymentName': deploymentName,
            'deploymentDepth': deploymentDepth,
            'depthUnitString': depthUnitString,
            'deploymentDocUrls': deploymentDocUrls,
            'deploymentLocation': deploymentLocation,
            'cruiseNumber': cruiseNumber,
            'locationLonLat': locationLonLat,
            'locationName': locationName,
            'eventType': eventType,
            'startDate': startDate,
            'endDate': endDate,
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
@cache.memoize(timeout=3600)
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
    try:
        for row in data:
            if row['metaData'] is not None:
                for metaData in row['metaData']:
                    if metaData['key'] == 'Laditude ':
                        metaData['key'] = 'Latitude'
                    if metaData['key'] == 'Latitude':
                        lat = metaData['value']
                        metaData['value'] = _normalize(metaData['value'])
                    if metaData['key'] == 'Longitude':
                        lon = metaData['value']
                        metaData['value'] = _normalize(metaData['value'])
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

                row['class'] = row.pop('@class')
                row.pop('metaData', None)
                row.pop('physicalInfo', None)
                row.pop('purchaseAndDeliveryInfo', None)
                row.update({'url': url_for('uframe.get_asset', id=row['assetId']),
                        'uframe_url': current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (uframe_obj.__endpoint__, row['assetId'])})
    except (KeyError, TypeError, AttributeError):
        pass

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
    try:
        for metaData in data['metaData']:
            if metaData['key'] == 'Laditude ':
                metaData['key'] = 'Latitude'
            if metaData['key'] == 'Latitude':
                lat = metaData['value']
                metaData['value'] = _normalize(metaData['value'])
            if metaData['key'] == 'Longitude':
                lon = metaData['value']
                metaData['value'] = _normalize(metaData['value'])
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
        data['class'] = data.pop('@class')
    except (KeyError, TypeError):
        pass

    return jsonify(**data)

#Create
@auth.login_required
@api.route('/assets', methods=['POST'])
def create_asset():
    data = json.loads(request.data)
    uframe_obj = uFrameAssetCollection()
    post_body = uframe_obj.from_json(data)
    #return json.dumps(post_body)
    uframe_assets_url = _uframe_url(uframe_obj.__endpoint__)
    #return uframe_assets_url
    response = requests.post(uframe_assets_url, data=json.dumps(post_body), headers=_uframe_headers())
    return response.text

#Update
@auth.login_required
@api.route('/assets/<int:id>', methods=['PUT'])
def update_asset(id):
    data = json.loads(request.data)
    uframe_obj = uFrameAssetCollection()
    put_body = uframe_obj.from_json(data)
    uframe_assets_url = _uframe_url(uframe_obj.__endpoint__, id)
    response = requests.put(uframe_assets_url, data=json.dumps(put_body), headers=_uframe_headers())
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
@cache.memoize(timeout=3600)
@api.route('/events', methods=['GET'])
def get_events():
    #set up all the contaners.
    data = {}
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameEventCollection()
    data = uframe_obj.to_json()
    try:
        for row in data:
            row['class'] = row.pop('@class')
            row.update({'url': url_for('uframe.get_event', id=row['eventId']),
                'uframe_url': current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (uframe_obj.__endpoint__, row['eventId'])})
            row.pop('asset')
        #parse the result and assign ref_des as top element.
    except (KeyError, TypeError, AttributeError):
        pass
    return jsonify({ 'events' : data })

#Read (object)
@api.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    #set up all the contaners.
    data = {}
    asset_id = ""
    #create uframe instance, and fetch the data.
    uframe_obj = uFrameEventCollection()
    data = uframe_obj.to_json(id)
    try:
        data['class'] = data.pop('@class')
    except (KeyError, TypeError):
        pass
    return jsonify(**data)

#Create
@auth.login_required
@api.route('/events', methods=['POST'])
def create_event():
    data = json.loads(request.data)
    uframe_obj = uFrameEventCollection()
    post_body = uframe_obj.from_json(data)
    uframe_events_url = _uframe_url(uframe_obj.__endpoint__)
    response = requests.post(uframe_events_url, data=json.dumps(post_body), headers=_uframe_headers())
    return response.text

#Update
@auth.login_required
@api.route('/events/<int:id>', methods=['PUT'])
def update_event(id):
    data = json.loads(request.data)
    uframe_obj = uFrameEventCollection()
    put_body = uframe_obj.from_json(data)
    uframe_events_url = _uframe_url(uframe_obj.__endpoint__, id)
    response = requests.put(uframe_events_url, data=json.dumps(put_body), headers=_uframe_headers())
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