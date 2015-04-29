#!/usr/bin/env python
'''
uframe assets and events endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request, url_for, make_response
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.routes import get_display_name_by_rd
from ooiservices.app import cache
import json
import requests
import re


#Default number of times to retry the connection:
requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 3600

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
            coords = (0.0, 0.0)
            return coords

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

    #Define the connection

    __endpoint__ = 'assets'
    # m@c: Updated 03/03/2015
    class_type =  None
    meta_data = []
    asset_info = None
    manufacture_info = None
    notes = None
    asset_id = None
    attachments = []
    purchase_and_delivery_info = None
    physical_info = None
    identifier = None
    traceI_id = None
    overwrite_allowed = False

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
        class_type = json.get('class')
        asset_info = json.get('assetInfo')
        manufacture_info = json.get('manufactureInfo')
        notes = json.get('notes')
        #asset_id = json.get('assetId')
        attachments = json.get('attachments')
        purchase_and_delivery_info = json.get('purchaseAndDeliveryInfo')
        physical_info = json.get('physicalInfo')
        coordinates = json.get('coordinates')
        launch_date_time = json.get('launch_date_time')
        water_depth = json.get('water_depth')
        ref_des = json.get('ref_des')
        #meta_data = json.get('metaData')
        ### These are not returned, for now they don't exist in uframe.
        identifier = json.get('identifier')
        trace_id = json.get('traceId')
        overwrite_allowed = json.get('overwriteAllowed')
        platform = json.get('platform')
        last_modified_imestamp = json.get("lastModifiedTimestamp")
        #####
        #Build metadata dictionary
        meta_data = []
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
            meta_data.append(dict_depth)
        if coordinates is not None and len(coordinates) == 2:
            dict_lat = {
                "key": "Latitude",
                "value": coordinates[0]
            }
            meta_data.append(dict_lat)
            dict_lon =  {
                "key": "Longitude",
                "value": coordinates[1]
            }
            meta_data.append(dict_lon)
        if launch_date_time is not None:
            dict_launch_date =  {
                "key": "Anchor Launch Date",
                "value": launch_date_time
            }
            meta_data.append(dict_launch_date)
        if ref_des is not None:
            dict_ref_des = {
              "key": "Ref Des",
              "value": ref_des
            }
            meta_data.append(dict_ref_des)
        if platform is not None:
            dict_platform = {
              "key": "Platform",
              "value": platform
            }
            meta_data.append(dict_platform)

        #TODO:
        #temp_metaData needs to be checked against the existing metaData and
        #appended or updated as necessary.  For now, temp_metaData goes no where
        #, as it would over write the existing values.


        #Below section's keys are uFrame specific and shouldn't be modified
        #unless necessary to support uframe updates.
        formatted_return = {
                "@class": class_type,
                "metaData": meta_data,
                "assetInfo": asset_info,
                "manufacturerInfo": manufacture_info,
                "notes": notes,
                "attachments": attachments,
                "purchaseAndDeliveryInfo": purchase_and_delivery_info,
                "physicalInfo": physical_info,
                "lastModifiedTimestamp": last_modified_imestamp,
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
        event_class = json.get('class')
        reference_designator = json.get('referenceDesignator')
        deployment_number = json.get('deploymentNumber')
        deployment_name = json.get('deploymentName')
        deployment_depth = json.get('deploymentDepth')
        depthUnit_string = json.get('depthUnitString')
        deployment_doc_urls = json.get('deploymentDocUrls')
        deployment_location = json.get('deploymentLocation')
        cruise_number = json.get('cruiseNumber')
        location_lon_lat = json.get('locationLonLat')
        location_name = json.get('locationName')
        event_type = json.get('eventType')
        start_date = json.get('startDate')
        end_date = json.get('endDate')
        event_description = json.get('eventDescription')
        recorded_by = json.get('recordedBy')
        asset = json.get('asset')
        notes = json.get('notes')
        attachments = json.get('attachments')
        tense = json.get('tense')
        last_modified_timestamp = json.get('lastModifiedTimestamp')

        #Update deploymentLocation to send a float even if Lat/Lon is an int.
        if deployment_location is not None:
            deployment_location = [
                float(deployment_location[0]),
                float(deployment_location[1])
            ]

        formatted_return = {
            '@class' : event_class,
            'referenceDesignator': reference_designator,
            'deploymentNumber': deployment_number,
            'deploymentName': deployment_name,
            'deploymentDepth': deployment_depth,
            'depthUnitString': depthUnit_string,
            'deploymentDocUrls': deployment_doc_urls,
            'deploymentLocation': deployment_location,
            'cruiseNumber': cruise_number,
            'locationLonLat': location_lon_lat,
            'locationName': location_name,
            'eventType': event_type,
            'startDate': start_date,
            'endDate': end_date,
            'eventDescription': event_description,
            'recordedBy': recorded_by,
            'asset': asset,
            'notes': notes,
            'attachments': attachments,
            'tense': tense,
            'lastModifiedTimestamp': last_modified_timestamp
        }
        return formatted_return

### ---------------------------------------------------------------------------
### BEGIN Assets CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
@api.route('/assets', methods=['GET'])
def get_assets():
    '''
    Listing GET request of all assets.  This method is cached for 1 hour.
    '''
    #Manually set up the cache
    cached = cache.get('asset_list')
    if cached:
        return cached

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
                for meta_data in row['metaData']:
                    if meta_data['key'] == 'Laditude ':
                        meta_data['key'] = 'Latitude'
                    if meta_data['key'] == 'Latitude':
                        lat = meta_data['value']
                        meta_data['value'] = _normalize(meta_data['value'])
                    if meta_data['key'] == 'Longitude':
                        lon = meta_data['value']
                        meta_data['value'] = _normalize(meta_data['value'])
                    if meta_data['key'] == "Anchor Launch Date":
                        date_launch = meta_data['value']
                    if meta_data['key'] == "Anchor Launch Time":
                        time_launch = meta_data['value']
                    if meta_data['key'] == 'Water Depth':
                        depth = meta_data['value']
                    if meta_data['key'] == 'Ref Des SN':
                        meta_data['key'] = 'Ref Des'
                    if meta_data['key'] == 'Ref Des':
                        ref_des = (meta_data['value'])
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
                    display_name = get_display_name_by_rd(ref_des)
                    if display_name:
                        row['display_name'] = display_name
                    else:
                        row['display_name'] = 'Metadata Error: Name Not Found'
                    '''
                    Determine the asset name from the DB if there is none.
                    '''
                    try:
                        if row['assetInfo']['name'] == None:
                            row['assetInfo']['name'] = get_display_name_by_rd(ref_des)
                    except:
                        pass
                    '''
                    Create a url to uframe which can be used to navigate
                    to the stream data.
                    '''
                    try:
                        ref_des_split = ref_des.split('-')
                        stream_url =  current_app.config['UFRAME_URL'] + \
                        '/sensor/inv/%s' % (ref_des_split[0])
                        res = requests.head(stream_url, timeout=(.5, 3))
                        content_length = int(res.headers['content-length'])
                        if content_length > 0:
                            row.update({'stream_url': stream_url})
                        ref_des = ""
                        content_length = 0
                    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                        row.update({'stream_url': "Request Time Out"})

            row['class'] = row.pop('@class')
            row.pop('metaData', None)
            row.pop('physicalInfo', None)
            row.pop('purchaseAndDeliveryInfo', None)
            row.update({'url': url_for('uframe.get_asset', id=row['assetId']),
                    'uframe_url': current_app.config['UFRAME_ASSETS_URL'] + \
                    '/%s/%s' % (uframe_obj.__endpoint__, row['assetId'])})
    except (KeyError, TypeError, AttributeError) as e:
        pass

    result = jsonify({ 'assets' : data })
    if "error" not in data:
        cache.set('asset_list', result, timeout=CACHE_TIMEOUT)
    return result

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
        for meta_data in data['metaData']:
            if meta_data['key'] == 'Laditude ':
                meta_data['key'] = 'Latitude'
            if meta_data['key'] == 'Latitude':
                lat = meta_data['value']
                meta_data['value'] = _normalize(meta_data['value'])
            if meta_data['key'] == 'Longitude':
                lon = meta_data['value']
                meta_data['value'] = _normalize(meta_data['value'])
            if meta_data['key'] == "Anchor Launch Date":
                date_launch = meta_data['value']
            if meta_data['key'] == "Anchor Launch Time":
                time_launch = meta_data['value']
            if meta_data['key'] == 'Water Depth':
                depth = meta_data['value']
            if meta_data['key'] == 'Ref Des SN':
                meta_data['key'] = 'Ref Des'
            if meta_data['key'] == 'Ref Des':
                ref_des = (meta_data['value'])
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
            '''
            Determine the asset name from the DB if there is none.
            '''
            try:
                if data['assetInfo']['name'] == None:
                    data['assetInfo']['name'] = get_display_name_by_rd(ref_des)
            except:
                pass
            '''
            Create a url to uframe which can be used to navigate
            to the stream data.
            '''
            try:
                ref_des_split = ref_des.split('-')
                stream_url =  current_app.config['UFRAME_URL'] + \
                '/sensor/inv/%s' % (ref_des_split[0])
                res = requests.head(stream_url, timeout=(.5, 3))
                content_length = int(res.headers['content-length'])
                if content_length > 0:
                    data.update({'stream_url': stream_url})
                ref_des = ""
                content_length = 0
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                data.update({'stream_url': "Request Time Out"})

            data['events'] = _associate_events(id)
            data['class'] = data.pop('@class')
    except (KeyError, TypeError, AttributeError) as e:
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
    cache.delete('asset_list')
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
    cache.delete('asset_list')
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
    '''
    Listing GET request of all events.  This method is cached for 1 hour.
    '''
    #Manually set up the cache
    cached = cache.get('event_list')
    if cached:
        return cached
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

    result = jsonify({ 'events' : data })
    if "error" not in data:
        cache.set('event_list', result, timeout=CACHE_TIMEOUT)

    return result


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

#Read (object)
@api.route('/events/<string:ref_des>', methods=['GET'])
def get_events_by_ref_des(ref_des):
    '''
    Return all the events and their cooresponding asset ID when
    provided a reference designator (Logical Instrument).
    '''
    #Setup the cache, just in case
    cached = cache.get('events_by_ref_des')
    if cached:
        return cached

    #Create the container for the processed response
    result = []
    temp_dict = {}
    #variables used in loop
    platform = ""
    mooring = ""
    instrument = ""

    #Get all the events to begin searching though...
    uframe_obj = uFrameEventCollection()
    data = uframe_obj.to_json()
    for row in data:
        try:
            if  row['referenceDesignator']['subsite'] is not None:
                platform = row['referenceDesignator']['subsite']
            if row['referenceDesignator']['node'] is not None:
                mooring = row['referenceDesignator']['node']
            if row['referenceDesignator']['sensor'] is not None:  
                instrument = row['referenceDesignator']['sensor']
            concat_ref_des =  '-'.join([platform, mooring, instrument])
            if concat_ref_des == ref_des:
                temp_dict['ref_des'] = concat_ref_des
                temp_dict['start_date'] = row['startDate']
                temp_dict['class'] = row['@class']
                temp_dict['event_description'] = row['eventDescription']
                temp_dict['event_type'] = row['eventType']
                temp_dict['notes'] = row['notes']
                temp_dict['url'] =  url_for('uframe.get_event', id=row['eventId'])
                temp_dict['uframe_url'] = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (uframe_obj.__endpoint__, row['eventId'])
                result.append(temp_dict)
                temp_dict = ""
        except:
            pass 
    result = jsonify({ 'events' : result })
    return result


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
    cache.delete('event_list')
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
    cache.delete('event_list')
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
