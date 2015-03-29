#!/usr/bin/env python
'''
uframe assets and events endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request, url_for, make_response
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app import cache
import json
import requests
import re

def _normalize_whitespace(string):
    '''
    Requires re
    - Removes extra white space from a string.

    '''
    string = string.strip()
    string = re.sub(r'\s+', ' ', string)
    return string

def _remove_duplicates(values):
    '''
    Requires re
    - Removes duplicate values, useful in getting a concise list.
    '''
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
    '''
    Two options for creating the uframe url:
    - If an id is provided, the return is a url points to a specific id.
    - If no id, a url for a GET list or a post is returned.
    '''
    if id is not None:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (endpoint, id)
    else:
        uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % endpoint
    return uframe_url

def _uframe_collection(uframe_url):
    '''
    After a url is determined, this method will do the heavy lifting of contacting
    uframe and either getting the json back, or returning a 500 error.
    '''
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
    '''
    No special headers are needed to connect to uframe.  This def simply states
    the default content type, and would be where authentication would be added
    if there ever is a need.
    '''
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def _normalize(to_translate, translate_to=u' '):
    '''
    Some of the strings from uframe contain special, non ascii characters, these
    need to be removed.
    This method is primarily used to normalize the Lat/Lon values so it can be
    later converted to decimal degrees.
    '''
    try:
        ascii =  ''.join([i if ord(i) < 128 else ' ' for i in to_translate])
        scrub = u'\'\"'
        translate_table = dict((ord(char), translate_to) for char in scrub)
        normalized = _normalize_whitespace(ascii.translate(translate_table))
        return normalized
    except Exception as e:
        return "%s" % e

def _convert_lat_lon(lat, lon):
    '''
    This is a wrapper method for _get_latlon, and basically just handles packaging
    and returning a Lat/Lon pair.

    A update to this def will assign the directional value if needed (neg).  This
    is a result of an obscure bug found in testing.
    '''
    try:

        _lat = _get_latlon(lat)
        _lon = _get_latlon(lon)
        if not (isinstance(lat, float) and isinstance(lon, float)):
            if "S" in lat:
                _lat = _lat*-1.0
            if "W" in lon:
                _lon = _lon*-1.0
        coords = (_lat, _lon)
        return coords
    except Exception as e:
        return "Error: %s" % e

def _get_latlon(item):
    '''
    given raw string for lat or lon, scrub and calculate float result;
    finally truncate to _decimal_places; default is 7 decimal places.
    returns: lat or lon as decimal degrees (float) or None
    '''
    _decimal_places = 7
    result = None
    degrees = 0.0
    minutes = 0.0
    seconds = 0.0
    # scrub input
    tmp = _normalize(item)
    # process input and round result to _decimal places
    if isinstance(item, unicode) and len(tmp.split()) > 1:
        ds = tmp.split(' ')
        degrees = float(ds[0])
        minutes = float(ds[1])
        if len(ds) == 4:
            seconds = float(ds[2])
        val = degrees +  ((minutes + (seconds/60.00000))/60.00000)
        # round to _decimal_places
        tmp = str(round(val,_decimal_places))
        result = float(tmp)
        return result
    else:
        return float(item)

def _convert_date_time(date, time=None):
    '''
    The date time is only concatenated unless there is no time.
    '''
    if time is None:
        return date
    else:
        return "%s %s" % (date, time)

def _convert_water_depth(depth):
    '''
    uframe returns the value and units in one string, this method splits out
    the value from the unit and returns a dict with the appropriate values.
    '''
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
    '''
    When an individual asset is requested from GET(id) all the events for that
    asset need to be associated.  This is represented in a list of URIs, one
    for it's services endpoint and one for it's direct endpoint in uframe.
    '''
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

class uFrameAssetCollection(object):
    '''
    uFrameAssetCollection:
    - Represents the latest attributes of the uframe endpoint.
    - Important methods:
        to_json(id=None):
            Reaches out to uframe and gets either the complete list of assets, or
            if an id is provided, an individual object.
        from_json():
            Prepares a JSON packet to be sent as either a POST or a PUT to uframe.
            There are some translation from what is sent from ooi ui, and what uframe
            is expecting.
            Please review method for further details.
    '''

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
        platform = json.get('platform')
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
                "value": "%s %s" % (water_depth['value'], water_depth['unit'])
            }
            metaData.append(dict_depth)
        if coordinates is not None and len(coordinates) == 2:
            dict_lat = {
                "key": "Latitude",
                "value": coordinates[0]
            }
            metaData.append(dict_lat)
            dict_lon =  {
                "key": "Longitude",
                "value": coordinates[1]
            }
            metaData.append(dict_lon)
        if launch_date_time is not None:
            dict_launch_date =  {
                "key": "Anchor Launch Date",
                "value": launch_date_time
            }
            metaData.append(dict_launch_date)
        if ref_des is not None:
            dict_ref_des = {
              "key": "Ref Des",
              "value": ref_des
            }
            metaData.append(dict_ref_des)
        if platform is not None:
            dict_platform = {
              "key": "Platform",
              "value": platform
            }
            metaData.append(dict_platform)

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


class uFrameEventCollection(object):
    '''
    uFrameEventCollection:
    - Represents the latest attributes of the uframe endpoint.
    - Important methods:
        to_json(id=None):
            Reaches out to uframe and gets either the complete list of events, or
            if an id is provided, an individual object.
        from_json():
            Prepares a JSON packet to be sent as either a POST or a PUT to uframe.
            There are some translation from what is sent from ooi ui, and what uframe
            is expecting.
            Please review method for further details.
    '''

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
        if deploymentLocation is not None:
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

### ---------------------------------------------------------------------------
### BEGIN Assets CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
@cache.memoize(timeout=3600)
@api.route('/assets', methods=['GET'])
def get_assets():
    '''
    Listing GET request of all assets.  This method is cached for 1 hour.
    '''
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
                    if metaData['key'] == 'Ref Des SN':
                        metaData['key'] = 'Ref Des'
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
    '''
    Object response for the GET(id) request.  This response is NOT cached.
    '''
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
            if metaData['key'] == 'Ref Des SN':
                metaData['key'] = 'Ref Des'
            if metaData['key'] == 'Ref Des':
                ref_des = (metaData['value'])
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
    '''
    Create a new asset, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
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
    '''
    Update an existing asset, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
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
    '''
    Listing GET request of all events.  This method is cached for 1 hour.
    '''
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
    '''
    Object response for the GET(id) request.  This response is NOT cached.
    '''
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
    '''
    Create a new event, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
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
    '''
    Update an existing event, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
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
@cache.memoize(timeout=3600)
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

@cache.memoize(timeout=3600)
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

@cache.memoize(timeout=3600)
@api.route('/asset/serials', methods=['GET'])

@cache.memoize(timeout=3600)
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

@cache.memoize(timeout=3600)
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

@api.route('/assets/platforms', methods=['GET'])
def get_platforms():
    '''
    This method only gets a list of all identified platforms.
    '''
    platform = None
    lat = ""
    lon = ""
    coords = [ None, None]
    temp_body = []
    data = []
    d = {}
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.to_json()
    for row in temp_list:
        asset_id = row['assetId']
        description = row['assetInfo']
        if row['metaData'] is not None:
            for metaData in row['metaData']:
                if metaData['key'] == "Platform":
                    platform = _normalize(metaData['value'])
                    if metaData['key'] == 'Laditude ':
                        metaData['key'] = 'Latitude'
                    if metaData['key'] == 'Latitude':
                        lat = metaData['value']
                        metaData['value'] = _normalize(metaData['value'])
                    if metaData['key'] == 'Longitude':
                        lon = metaData['value']
                        metaData['value'] = _normalize(metaData['value'])
            if len(lat) > 0 and len(lon) > 0:
                coords = _convert_lat_lon(lat, lon)
                lat = ""
                lon = ""
            if platform is not None:
                d[platform] = { "assetId": asset_id,
                                "assetInfo": description,
                                'url': url_for('uframe.get_asset', id=row['assetId']),
                                "coordinates": coords}
    return jsonify(**d)
