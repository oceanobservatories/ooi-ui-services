#!/usr/bin/env python

'''
uframe assets and events endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request, url_for
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.routes import\
    get_display_name_by_rd as get_dn_by_rd,\
    get_long_display_name_by_rd as get_ldn_by_rd,\
    get_assembly_by_rd
import requests
import re
import math
from netCDF4 import num2date
from operator import itemgetter
from ooiservices.app import cache

requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400


def _compile_assets(data):
    for row in data:
        latest_deployment = None
        lat = ""
        lon = ""
        ref_des = ""
        has_deployment_event = False
        deployment_number = ""
        try:
            row['id'] = row.pop('assetId')
            row['asset_class'] = row.pop('@class')
            row['events'] = associate_events(row['id'])
            if len(row['events']) == 0:
                row['events'] = []
            row['tense'] = None
            if row['metaData'] is not None:
                for meta_data in row['metaData']:
                    if meta_data['key'] == 'Latitude':
                        lat = meta_data['value']
                        coord = convert_lat_lon(lat, "")
                        meta_data['value'] = coord[0]
                    if meta_data['key'] == 'Longitude':
                        lon = meta_data['value']
                        coord = convert_lat_lon("", lon)
                        meta_data['value'] = coord[1]
                    if meta_data['key'] == 'Ref Des':
                        ref_des = meta_data['value']
                    if meta_data['key'] == 'Deployment Number':
                        deployment_number = meta_data['value']
                row['ref_des'] = ref_des

                if len(row['ref_des']) == 27:
                    row['asset_class'] = '.InstrumentAssetRecord'
                if len(row['ref_des']) < 27:
                    row['asset_class'] = '.AssetRecord'

                if deployment_number is not None:
                    row['deployment_number'] = deployment_number
                for events in row['events']:
                    if events['class'] == '.DeploymentEvent':
                        has_deployment_event = True
                        if events['tense'] == 'PRESENT':
                            row['tense'] = events['tense']
                        else:
                            row['tense'] = 'PAST'
                    if latest_deployment is None and\
                            events['locationLonLat'] is not None and\
                            len(events['locationLonLat']) == 2:
                        latest_deployment = events['startDate']
                        lat = events['locationLonLat'][1]
                        lon = events['locationLonLat'][0]
                    if events['locationLonLat'] is not None and\
                            latest_deployment is not None and\
                            len(events['locationLonLat']) == 2 and\
                            events['startDate'] > latest_deployment:
                        latest_deployment = events['startDate']
                        lat = events['locationLonLat'][1]
                        lon = events['locationLonLat'][0]
                row['hasDeploymentEvent'] = has_deployment_event
                row['coordinates'] = convert_lat_lon(lat, lon)

            if (not(row['assetInfo'])):
                row['assetInfo'] = {
                    'name': '',
                    'type': '',
                    'owner': '',
                    'description': ''
                }

            # determine the asset name from the DB if there is none.
            if (not('name' in row['assetInfo']) and len(ref_des) > 0):
                row['assetInfo']['name'] = get_dn_by_rd(ref_des) or ""
                row['assetInfo']['longName'] = get_ldn_by_rd(ref_des)
            elif ('name' in row['assetInfo'] and len(ref_des) > 0):
                row['assetInfo']['name'] = row['assetInfo']['name']\
                    or get_dn_by_rd(ref_des) or ""
                row['assetInfo']['longName'] = get_ldn_by_rd(ref_des)
            else:
                row['assetInfo']['name'] = ""
                row['assetInfo']['longName'] = ""
            row['assetInfo']['array'] = get_dn_by_rd(ref_des[:2])
            row['assetInfo']['assembly'] = get_assembly_by_rd(ref_des)

        except Exception as e:
            print e
            continue

    return data


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
        if math.isnan(result):
            return 0.0
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
           
            d = {}
            # set up some static keys
            d['locationLonLat'] = []

            d['eventId'] = row['eventId']
            d['class'] = row['@class']
            d['notes'] = len(row['notes'])
            d['startDate'] = row['startDate']
            d['endDate'] = row['endDate']
            d['tense'] = row['tense']
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

def get_events_by_ref_des(data, ref_des):
    # Create the container for the processed response
    result = []
    # Get all the events to begin searching though...
    for row in data:
        # variables used in loop
        temp_dict = {}
        ref_des_check = ""
        try:

            if 'referenceDesignator' in row and row['referenceDesignator']['full']:
                ref_des_check = (row['referenceDesignator']['subsite'] + '-' + row['referenceDesignator']['node'] +
                                 '-' + row['referenceDesignator']['sensor'])
            else:
                if row['asset']['metaData']:
                    for metaData in row['asset']['metaData']:
                        if metaData['key'] == 'Ref Des':
                            ref_des_check = metaData['value']
            if ref_des_check == ref_des:
                temp_dict['ref_des'] = ref_des_check
                temp_dict['id'] = row['id']
                temp_dict['class'] = row['class']
                if row['class'] == '.DeploymentEvent':
                    temp_dict['cruise_number'] = row['cruiseNumber']
                    temp_dict['cruise_plan_doc'] = row['cruisePlanDocument']
                    temp_dict['depth'] = row['depth']
                    temp_dict['lat_lon'] = row['locationLonLat']
                    temp_dict['deployment_number'] = row['deploymentNumber']
                temp_dict['tense'] = row['tense']
                start_date = num2date(float(row['startDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
                temp_dict['start_date'] = start_date.strftime("%B %d %Y, %I:%M:%S %p")
                if row['endDate'] is not None:
                    end_date = num2date(float(row['endDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
                    temp_dict['end_date'] = end_date.strftime("%B %d %Y, %I:%M:%S %p")
                temp_dict['event_description'] = row['eventDescription']
                temp_dict['event_type'] = row['eventType']
                temp_dict['notes'] = row['notes']
                result.append(temp_dict)
                temp_dict = {}
        except (KeyError, TypeError):
            raise
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
