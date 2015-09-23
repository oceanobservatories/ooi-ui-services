#!/usr/bin/env python

'''
uframe assets and events endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request, url_for, make_response
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.routes import get_display_name_by_rd
import json
import requests
import re
import datetime
from netCDF4 import num2date
from operator import itemgetter
from copy import deepcopy
from ooiservices.app import cache

#Default number of times to retry the connection:
requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400

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
    data = requests.get(uframe_url)

    if (data.status_code == 200):
        return data
    else:
        return data.message, data.status_code

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

def convert_lat_lon(lat, lon):
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
        coords = (round(_lat, 4), round(_lon,4))
        return coords
    except Exception as e:
        coords = (0.0, 0.0)
        return coords

def _get_latlon(item):
    '''
    given raw string for lat or lon, scrub and calculate float result;
    finally truncate to _decimal_places; default is 7 decimal places.
    returns: lat or lon as decimal degrees (float) or None
    '''
    _decimal_places = 4
    result = None
    degrees = 0.0
    minutes = 0.0
    seconds = 0.0
    # scrub input
    tmp = _normalize(item)
    # process input and round result to _decimal places
    if isinstance(item, unicode) and len(tmp.split()) > 1:
        digits = re.findall("\S.*[0-9.]+", tmp)
        direction = re.findall("[NSEW]", tmp)
        tmp = "%s %s" % (digits[0], direction[0])
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
        if item == "":
            return 0.0
        return float(item)

def convert_date_time(date, time=None):
    '''
    The date time is only concatenated unless there is no time.
    '''
    if time is None:
        return date
    else:
        return "%s %s" % (date, time)

def convert_water_depth(depth):
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

def associate_events(id):
    '''
    When an individual asset is requested from GET(id) all the events for that
    asset need to be associated.  This is represented in a list of URIs, one
    for it's services endpoint and one for it's direct endpoint in uframe.
    '''
    uframe_url = current_app.config['UFRAME_ASSETS_URL'] + '/assets/%s/events' % (id)
    result = []
    payload = requests.get(uframe_url)
    if payload.status_code != 200:
        return [{ "error": "server responded with error code: %s" % payload.status_code }]

    json_data = payload.json()
    for row in json_data:
        try:
            d = {'url': url_for('uframe.get_event', id=row['eventId']),
                    'uframe_url': current_app.config['UFRAME_ASSETS_URL'] + '/events/%s' % row['eventId']}
            # set up some static keys
            d['locationLonLat'] = []

            d['eventId'] = row['eventId']
            d['class'] = row['@class']
            d['notes'] = len(row['notes'])
            d['startDate'] = row['startDate']
            d['endDate'] = row['endDate']
            if d['class'] == '.CalibrationEvent':
                d['calibrationCoefficient'] = row['calibrationCoefficient']
                lon = 0.0
                lat = 0.0
                for cal_coef in d['calibrationCoefficient']:
                    if cal_coef['name'] == 'CC_lon':
                        lon = cal_coef['values']
                    if cal_coef['name'] == 'CC_lat':
                        lat = cal_coef['values']
                if lon is not None and lat is not None:
                    d['locationLonLat'] = convert_lat_lon(lat, lon)
            if d['class'] == '.DeploymentEvent':
                d['deploymentDepth'] = row['deploymentDepth']
                if row['locationLonLat']:
                    d['locationLonLat'] = convert_lat_lon(row['locationLonLat'][1], row['locationLonLat'][0])
                d['deploymentNumber'] = row['deploymentNumber']
        except KeyError:
            pass
        result.append(d)

    try:
        if request.args.get('sort') and request.args.get('sort') != "":
            sort_by = request.args.get('sort')
        else:
            sort_by = 'eventId'
        result = sorted(result, key=itemgetter(sort_by))
    except (TypeError, KeyError) as e:
        raise

    return result

def get_events_by_ref_des(ref_des):
    #Create the container for the processed response
    result = []
    #Get all the events to begin searching though...
    uframe_obj = UFrameEventCollection()
    data = uframe_obj.to_json()
    for row in data:
        #variables used in loop
        temp_dict = {}
        platform = ""
        mooring = ""
        instrument = ""
        ref_des_check = ""
        try:
            if row['asset']['metaData']:
                for metaData in row['asset']['metaData']:
                    if metaData['key'] == 'Ref Des':
                        ref_des_check = metaData['value']
            if ref_des_check == ref_des:
                temp_dict['id'] = row['eventId']
                temp_dict['ref_des'] = ref_des_check
                temp_dict['start_date'] = num2date(float(row['startDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
                temp_dict['class'] = row['@class']
                temp_dict['event_description'] = row['eventDescription']
                temp_dict['event_type'] = row['eventType']
                temp_dict['notes'] = row['notes']
                temp_dict['url'] =  url_for('uframe.get_event', id=row['eventId'])
                temp_dict['uframe_url'] = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (uframe_obj.__endpoint__, row['eventId'])
                result.append(temp_dict)
                temp_dict = {}
        except (KeyError, TypeError):
            pass
    result = jsonify({ 'events' : result })
    return result

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
    asset_type = []
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.to_json()
    for row in temp_list:
        if row['assetInfo'] is not None:
            asset_type.append(row['assetInfo'])
            for a_t in asset_type:
                data.append(a_t['type'])
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
def get_asset_serials():
    '''
    Lists all the class types available from uFrame.
    '''
    data = []
    manuf_info = []
    uframe_obj = uFrameAssetCollection()
    temp_list = uframe_obj.to_json()
    for row in temp_list:
        if row['manufactureInfo'] is not None:
            manuf_info.append(row['manufactureInfo'])
            for serial in manuf_info:
                data.append(serial['serialNumber'])
    data = _remove_duplicates(data)
    return jsonify({ 'serial_numbers' : data })
