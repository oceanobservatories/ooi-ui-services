#!/usr/bin/env python

'''
uframe assets and events endpoint and class definition.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.routes import\
    get_display_name_by_rd as get_dn_by_rd,\
    get_long_display_name_by_rd as get_ldn_by_rd
import requests, requests.adapters
import re
import math
from netCDF4 import num2date
from operator import itemgetter
from ooiservices.app import cache
from ooiservices.app.main.alertsalarms_tools import _compile_asset_rds

requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400


def _compile_events(data):
    try:
        for row in data:
            row['id'] = row.pop('eventId')
            row['eventClass'] = row.pop('@class')
        return data
    except Exception as err:
        message = 'exception _compile_events: %s' % (str(err))
        current_app.logger.info(message)
        raise Exception(message)


def _compile_assets(data):
    """ Process list of asset dictionaries from uframe; transform into (ooi-ui-services) list of asset dictionaries.

    Keys in row:
        [u'purchaseAndDeliveryInfo', u'assetId', u'lastModifiedTimestamp', u'physicalInfo', u'manufactureInfo',
        u'dataSource', u'remoteDocuments', u'assetInfo', u'@class', u'metaData']

    Sample Event:
        {'eventId': 83, 'startDate': -62135769600000, 'endDate': None, 'locationLonLat': [], 'notes': 0,
        'tense': u'PRESENT', 'eventClass': u'.TagEvent'}

    Metadata:
        [{u'type': u'java.lang.String', u'key': u'Anchor Launch Date', u'value': u'20-Apr-14'},
        {u'type': u'java.lang.String', u'key': u'Water Depth', u'value': u'0'},
        {u'type': u'java.lang.String', u'key': u'Anchor Launch Time', u'value': u'18:26'},
        {u'type': u'java.lang.String', u'key': u'Ref Des', u'value': u'CE05MOAS-GL319'},
        {u'type': u'java.lang.String', u'key': u'Cruise Number', u'value': u'Oceanus'},
        {u'type': u'java.lang.String', u'key': u'Latitude', u'value': u"44\xb042.979' N"},
        {u'type': u'java.lang.String', u'key': u'Deployment Number', u'value': u'1'},
        {u'type': u'java.lang.String', u'key': u'Recover Date', u'value': u'28-May-14'},
        {u'type': u'java.lang.String', u'key': u'Longitude', u'value': u"124\xb032.0615' W"}]

    """
    debug = False       # general development and debugging
    info = False        # log missing vocab items when unable to create display name(s)
    feedback = False    # display information as assets are processed
    new_data = []
    bad_data = []
    bad_data_ids = []

    vocab_failures = []
    dict_asset_ids = {}
    try:
        update_asset_rds_cache = False
        cached = cache.get('asset_rds')
        if cached:
            if debug: print '\n **************** debug -- asset_rds cached...'
            dict_asset_ids = cached
            if debug: print '\n **************** debug -- type(dict_asset_ids): ', type(dict_asset_ids)
        if not cached or not isinstance(cached, dict):
            if debug: print '\n **************** debug -- asset_rds NOT cached...type(cached): ', type(cached)

            #--------------------------------------------------------
            # If no asset_rds cached, then fetch and cache
            asset_rds = {}
            try:
                asset_rds, _ = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
                if debug:
                    #print '\n debug --- asset_rds: ', json.dumps(asset_rds, indent=4, sort_keys=True)
                    print '\n debug --- len(asset_rds.keys()): ', len(asset_rds.keys())
                    print "[+] Asset reference designators cache reset..."
            else:
                if debug: print "[-] Error in cache update"
            dict_asset_ids = asset_rds
            #--------------------------------------------------------
        if debug:
            print '\n debug -------------------------------------------------------------'
            print '\n debug --- len(dict_asset_ids.keys()): ', len(dict_asset_ids.keys())
            print '\n debug -------------------------------------------------------------'

    except Exception as err:
        message = 'Error compiling asset_rds: %s' % err.message
        if debug: print '\n debug --- ', message
        current_app.logger.info(message)
        raise Exception(message)

    # Process uframe list of asset dictionaries (data)
    print '\n Compiling assets...'
    valid_asset_classes = ['.InstrumentAssetRecord', '.NodeAssetRecord', '.AssetRecord']
    for row in data:
        ref_des = ''
        lat = ""
        lon = ""
        latest_deployment = None
        has_deployment_event = False
        deployment_number = ""
        try:
            # Get asset_id, if not asset_id then continue
            row['augmented'] = False
            asset_id = None
            if 'assetId' in row:
                row['id'] = row.pop('assetId')
                asset_id = row['id']
                if asset_id is None:
                    bad_data.append(row)
                    continue
                if not asset_id:
                    bad_data.append(row)
                    continue

            row['asset_class'] = row.pop('@class')
            row['events'] = associate_events(row['id'])
            if len(row['events']) == 0:
                row['events'] = []
            row['tense'] = None

            # If ref_des not provided in row, use dictionary lookup.
            if asset_id in dict_asset_ids:
                ref_des = dict_asset_ids[asset_id]

            # Process metadata (Note: row['metaData'] is often an empty list (especially for instruments).
            # -- Process when row['metaData'] is None (add metaData if possible)
            if row['metaData'] is None:
                if debug: print '\n debug -- metaData is None...'
                if ref_des:
                    row['metaData'] = [{u'type': u'java.lang.String', u'key': u'Ref Des', u'value': ref_des}]
                else:
                    if debug: print '\n debug -- NO metaData...NO ref_des...continue'
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue

            # -- Process when row['metaData'] is not None
            elif row['metaData'] is not None:
                # If metaData provided is empty and ref_des is available manually add metaData; no ref_des then continue
                if not row['metaData']:
                    # Manually add 'Ref Des' value to row using ref_des.
                    if ref_des:
                        row['metaData'] = [{u'type': u'java.lang.String', u'key': u'Ref Des', u'value': ref_des}]

                    # No 'metaData' and no ref_des, continue.
                    else:
                        if asset_id not in bad_data_ids:
                            bad_data_ids.append(asset_id)
                            bad_data.append(row)
                        continue

                # Process 'metaData' provided
                else:
                    for meta_data in row['metaData']:
                        if meta_data['key'] == 'Latitude':
                            lat = meta_data['value']
                            coord = convert_lat_lon(lat, "")
                            meta_data['value'] = coord[0]
                        if meta_data['key'] == 'Longitude':
                            lon = meta_data['value']
                            coord = convert_lat_lon("", lon)
                            meta_data['value'] = coord[1]
                        if meta_data['key'] == 'Deployment Number':
                            deployment_number = meta_data['value']

                        # If key 'Ref Des' has a value, use it, otherwise use ref_des value.
                        if meta_data['key'] == 'Ref Des':
                            if meta_data['value']:
                                ref_des = meta_data['value']
                            meta_data['value'] = ref_des

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If no reference designator available, but have asset id, continue.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not ref_des or ref_des is None:
                # If reference designator not provided, use lookup; if still no ref_des, continue
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Set row values with reference designator
            row['ref_des'] = ref_des
            row['Ref Des'] = ref_des
            if feedback: print '\n debug ---------------- (%r) ref_des: *%s*' % (asset_id, ref_des)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get asset class based on reference designator
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['asset_class'] or row['asset_class'] is None:
                if len(ref_des) == 27:
                    row['asset_class'] = '.InstrumentAssetRecord'
                elif len(ref_des) == 14:
                    row['asset_class'] = '.NodeAssetRecord'
                elif len(ref_des) == 8:
                    row['asset_class'] = '.AssetRecord'
                else:
                    message = 'ref_des is malformed (%s), unable to determine asset_class.' % row['asset_class']
                    print '\n INFO: ', message
                    current_app.logger.info(message)
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue
            else:
                # Log asset class is unknown.
                asset_class = row['asset_class']
                if asset_class not in valid_asset_classes:
                    if info:
                        message = 'Reference designator (%s) has an asset class value (%s) is not one of: %s' % \
                              (ref_des, asset_class, valid_asset_classes)
                        print '\n INFO: ', message
                        current_app.logger.info(message)
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue

            if deployment_number is not None:
                row['deployment_number'] = deployment_number

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process events
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            for events in row['events']:
                if events['eventClass'] == '.DeploymentEvent':
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

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Populate assetInfo dictionary
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['assetInfo']:
                row['assetInfo'] = {
                    'name': '',
                    'type': '',
                    'owner': '',
                    'description': ''
                }

            # Populate assetInfo type
            if row['asset_class'] == '.InstrumentAssetRecord':
                row['assetInfo']['type'] = 'Sensor'
            elif row['asset_class'] == '.NodeAssetRecord':
                row['assetInfo']['type'] = 'Mooring'
            elif row['asset_class'] == '.AssetRecord':
                if len(ref_des) == 27:
                    row['assetInfo']['type'] = 'Sensor'
                elif len(ref_des) == 14:
                    row['assetInfo']['type'] = 'Platform'
                elif len(ref_des) == 8:
                    row['assetInfo']['type'] = 'Mooring'
                else:
                    if info:
                        message = 'Asset id %d, type .AssetRecord, has malformed a reference designator (%s)' % \
                                  (asset_id, ref_des)
                        print '\n INFO: ', message
                        current_app.logger.info(message)
                    row['assetInfo']['type'] = 'Unknown'
            else:
                if info:
                    message = 'Note ----- Unknown asset_class (%s), set to \'Unknown\'. ' % row['assetInfo']['type']
                    print '\n INFO: ', message
                    current_app.logger.info(message)
                row['assetInfo']['type'] = 'Unknown'
            try:
                # Verify all necessary attributes are available, if not create and set to empty.
                if 'name' not in row['assetInfo']:
                    row['assetInfo']['name'] = ''
                if 'longName' not in row['assetInfo']:
                    row['assetInfo']['longName'] = ''
                if 'array' not in row['assetInfo']:
                    row['assetInfo']['array'] = ''
                if 'assembly' not in row['assetInfo']:
                    row['assetInfo']['assembly'] = ''

                # Populate assetInfo - name and long name; if failure to get display name, use ref_des, log failure.
                name = get_dn_by_rd(ref_des)
                if name is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    if info:
                        message = 'Vocab Note ----- reference designator (%s) failed to get get_dn_by_rd' % ref_des
                        current_app.logger.info(message)
                    name = ref_des
                longName = get_ldn_by_rd(ref_des)
                if longName is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    if info:
                        message = 'Vocab Note ----- reference designator (%s) failed to get get_ldn_by_rd' % ref_des
                        current_app.logger.info(message)
                    longName = ref_des
                row['assetInfo']['name'] = name
                row['assetInfo']['longName'] = longName

                # Populate assetInfo - array and assembly
                if len(ref_des) >= 8:
                    row['assetInfo']['array'] = get_dn_by_rd(ref_des[:2])
                if len(ref_des) >= 14:
                    row['assetInfo']['assembly'] = get_dn_by_rd(ref_des[:14])

            except Exception as err:
                # asset info error
                current_app.logger.info('asset info error' + str(err.message))
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Add new row to output dictionary
            if asset_id and ref_des:
                row['augmented'] = True
                new_data.append(row)
                # if new item for dictionary of asset ids, add id with value of reference designator
                if asset_id not in dict_asset_ids:
                    dict_asset_ids[asset_id] = ref_des
                    update_asset_rds_cache = True

        except Exception as e:
            current_app.logger.info(str(e))
            continue

    if dict_asset_ids:
        if debug: print '\n debug -- (final) len(dict_asset_ids): %d' % len(dict_asset_ids)
        if update_asset_rds_cache:
            if debug: print '\n debug -- (final) update asset_rds cache'
            cache.set('asset_rds', dict_asset_ids, timeout=CACHE_TIMEOUT)
    else:
        if debug: print '\n debug -- (final) NO dict_asset_ids...'

    # Log vocabulary failures (occur when creating display names)
    if vocab_failures:
        vocab_failures.sort()
        message = 'The following reference designator(s) are not defined in vocab.sql causing display name failures: %s' \
                  % (vocab_failures)
        current_app.logger.info(message)

    if debug:
        print '\n debug -- len(new_data): ', len(new_data)
        print '\n debug -- len(dict_asset_ids): ', len(dict_asset_ids)
        print '\n debug -- len(bad_data): ', len(bad_data)
        print '\n debug -- len(bad_data_ids): ', len(bad_data_ids)

    # Update cache for bad_asset_list
    bad_assets_cached = cache.get('bad_asset_list')
    if bad_assets_cached:
        cache.delete('bad_asset_list')
        cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)
        if debug: print '\n debug - reset bad_asset_list (%d): ' % len(bad_data)
    else:
        cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)
        if debug: print '\n debug - set bad_asset_list (%d): ' % len(bad_data)

    print '\n Completed compiling assets...'
    return new_data, dict_asset_ids


def _uframe_headers():
    """
    No special headers are needed to connect to uframe.  This def simply states
    the default content type, and would be where authentication would be added
    if there ever is a need.
    """
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


def _normalize_whitespace(string):
    """
    Requires re
    - Removes extra white space from a string.
    """
    string = string.strip()
    string = re.sub(r'\s+', ' ', string)
    return string


def _remove_duplicates(values):
    """
    Requires re
    - Removes duplicate values, useful in getting a concise list.
    """
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
    """
    Some of the strings from uframe contain special,
    non ascii characters, these need to be removed.
    This method is primarily used to normalize the Lat/Lon
    values so it can be later converted to decimal degrees.
    """
    try:
        ascii = ''.join([i if ord(i) < 128 else ' ' for i in to_translate])
        scrub = u'\'\"'
        translate_table = dict((ord(char), translate_to) for char in scrub)
        normalized = _normalize_whitespace(ascii.translate(translate_table))
        return normalized
    except Exception as e:
        return "%s" % e


def convert_lat_lon(lat, lon):
    """
    This is a wrapper method for _get_latlon, and basically
    just handles packaging and returning a Lat/Lon pair.

    A update to this def will assign the directional value
    if needed (neg).  This is a result of an obscure bug
    found in testing.
    """
    try:

        _lat = _get_latlon(lat)
        _lon = _get_latlon(lon)
        if not (isinstance(lat, float) and isinstance(lon, float)):
            if "S" in lat:
                _lat = _lat*-1.0
            if "W" in lon:
                _lon = _lon*-1.0
        coords = (round(_lat, 4), round(_lon, 4))
        return coords
    except Exception as e:
        coords = (0.0, 0.0)
        return coords


def _get_latlon(item):
    """
    given raw string for lat or lon, scrub and calculate float result;
    finally truncate to _decimal_places; default is 7 decimal places.
    returns: lat or lon as decimal degrees (float) or None
    """
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
        val = degrees + ((minutes + (seconds/60.00000))/60.00000)
        # round to _decimal_places
        tmp = str(round(val, _decimal_places))
        result = float(tmp)
        if math.isnan(result):
            return 0.0
        return result
    else:
        if item == "":
            return 0.0
        return float(item)


def convert_date_time(date, time=None):
    """ The date time is only concatenated unless there is no time.
    """
    if time is None:
        return date
    else:
        return "%s %s" % (date, time)


def convert_water_depth(depth):
    """
    uframe returns the value and units in one string, this method splits out
    the value from the unit and returns a dict with the appropriate values.
    """
    d = {}
    try:
        if len(depth.split()) == 2:
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
        return {'message': 'Conversion Error! %s' % ve,
                'input': depth}


def associate_events(id):
    """ Get all associated events for an asset (by id).
    When an individual asset is requested from GET(id) all the events for that
    asset need to be associated.  This is represented in a list of URIs, one
    for it's services endpoint and one for it's direct endpoint in uframe.
    """
    uframe_url = current_app.config['UFRAME_ASSETS_URL'] + \
        '/assets/%s/events' % (id)
    result = []
    payload = requests.get(uframe_url)
    if payload.status_code != 200:
        return [{"error": "server responded with error code: %s" %
                payload.status_code}]

    json_data = payload.json()
    for row in json_data:
        try:

            d = {}
            # set up some static keys
            d['locationLonLat'] = []

            d['eventId'] = row['eventId']
            d['eventClass'] = row['@class']
            d['notes'] = len(row['notes'])
            d['startDate'] = row['startDate']
            d['endDate'] = row['endDate']
            d['tense'] = row['tense']
            if d['eventClass'] == '.CalibrationEvent':
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
            if d['evetClass'] == '.DeploymentEvent':
                d['deploymentDepth'] = row['deploymentDepth']
                if row['locationLonLat']:
                    d['locationLonLat'] = convert_lat_lon(
                        row['locationLonLat'][1],
                        row['locationLonLat'][0])
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
    """ Create the container for the processed response.
    """
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
                temp_dict['eventClass'] = row['eventClass']
                if row['eventClass'] == '.DeploymentEvent':
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


#-----------------------------------------------------------------------------
#-- The following routes are for generating drop down lists, used in filtering view.
#-----------------------------------------------------------------------------
@cache.memoize(timeout=3600)
@api.route('/asset/types', methods=['GET'])
def get_asset_types():
    """ Lists all the asset types available from uFrame.
    """
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


def _compile_bad_assets(data):
    """ Process list of 'bad' asset dictionaries from uframe; return list of bad assets.
    transform into (ooi-ui-services) list of asset dictionaries.

    Keys in row:
        [u'purchaseAndDeliveryInfo', u'assetId', u'lastModifiedTimestamp', u'physicalInfo', u'manufactureInfo',
        u'dataSource', u'remoteDocuments', u'assetInfo', u'@class', u'metaData']

    Route: http://localhost:4000/uframe/assets?augmented=false

    """
    bad_data = []
    bad_data_ids = []
    debug = False          # general development
    info = False           # detect missing vocab items when unable to create display name(s)
    feedback = True        # (development/debug) display messages while processing each asset
    vocab_failures = []
    dict_asset_ids = {}
    try:
        cached = cache.get('asset_rds')
        if cached:
            dict_asset_ids = cached
        if not cached or not isinstance(cached, dict):
            # If no asset_rds cached, then fetch and cache
            asset_rds = {}
            try:
                asset_rds, _ = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
            else:
                message = 'Error in asset_rds cache update.'
                current_app.logger.warning(message)
            dict_asset_ids = asset_rds

    except Exception as err:
        message = 'Error compiling asset_rds: %s' % err.message
        current_app.logger.info(message)
        raise Exception(message)

    # Process uframe list of asset dictionaries (data)
    valid_asset_classes = ['.InstrumentAssetRecord', '.NodeAssetRecord', '.AssetRecord']
    for row in data:
        ref_des = ''
        lat = ""
        lon = ""
        latest_deployment = None
        has_deployment_event = False
        deployment_number = ""
        try:
            # Get asset_id, if not asset_id then continue
            row['augmented'] = False
            asset_id = None
            if 'assetId' in row:
                row['id'] = row.pop('assetId')
                asset_id = row['id']
                if asset_id is None:
                    bad_data.append(row)
                    continue
                if not asset_id:
                    bad_data.append(row)
                    continue

            row['asset_class'] = row.pop('@class')
            row['events'] = associate_events(row['id'])
            if len(row['events']) == 0:
                row['events'] = []
            row['tense'] = None

            # If ref_des not provided in row, use dictionary lookup.
            if asset_id in dict_asset_ids:
                ref_des = dict_asset_ids[asset_id]

            # Process metadata (Note: row['metaData'] is often an empty list (especially for instruments).
            # -- Process when row['metaData'] is None (add metaData if possible)
            if row['metaData'] is None:
                if debug: print '\n debug -- metaData is None...'
                if ref_des:
                    row['metaData'] = [{u'type': u'java.lang.String', u'key': u'Ref Des', u'value': ref_des}]
                else:
                    if debug: print '\n debug -- NO metaData...NO ref_des...continue'
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue

            # -- Process when row['metaData'] is not None
            elif row['metaData'] is not None:
                # If metaData provided is empty and ref_des is available manually add metaData; no ref_des then continue
                if not row['metaData']:
                    # Manually add 'Ref Des' value to row using ref_des.
                    if ref_des:
                        row['metaData'] = [{u'type': u'java.lang.String', u'key': u'Ref Des', u'value': ref_des}]

                    # No 'metaData' and no ref_des, continue.
                    else:
                        if asset_id not in bad_data_ids:
                            bad_data_ids.append(asset_id)
                            bad_data.append(row)
                        continue

                # Process 'metaData' provided
                else:
                    for meta_data in row['metaData']:
                        if meta_data['key'] == 'Latitude':
                            lat = meta_data['value']
                            coord = convert_lat_lon(lat, "")
                            meta_data['value'] = coord[0]
                        if meta_data['key'] == 'Longitude':
                            lon = meta_data['value']
                            coord = convert_lat_lon("", lon)
                            meta_data['value'] = coord[1]
                        if meta_data['key'] == 'Deployment Number':
                            deployment_number = meta_data['value']

                        # If key 'Ref Des' has a value, use it, otherwise use ref_des value.
                        if meta_data['key'] == 'Ref Des':
                            if meta_data['value']:
                                ref_des = meta_data['value']
                            meta_data['value'] = ref_des

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If no reference designator available, but have asset id, continue.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not ref_des or ref_des is None:
                # If reference designator not provided, use lookup; if still no ref_des, continue
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Set row values with reference designator
            row['ref_des'] = ref_des
            row['Ref Des'] = ref_des
            if feedback: print '\n debug ---------------- (%r) ref_des: *%s*' % (asset_id, ref_des)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get asset class based on reference designator
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            if not row['asset_class'] or row['asset_class'] is None:
                if len(ref_des) == 27:
                    row['asset_class'] = '.InstrumentAssetRecord'
                elif len(ref_des) == 14:
                    row['asset_class'] = '.NodeAssetRecord'
                elif len(ref_des) == 8:
                    row['asset_class'] = '.AssetRecord'
                else:
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue
            else:
                # Log asset class is unknown.
                asset_class = row['asset_class']
                if asset_class not in valid_asset_classes:
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue

            if deployment_number is not None:
                row['deployment_number'] = deployment_number

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process events
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            for events in row['events']:
                if events['eventClass'] == '.DeploymentEvent':
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

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Populate assetInfo dictionary
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['assetInfo']:
                row['assetInfo'] = {
                    'name': '',
                    'type': '',
                    'owner': '',
                    'description': ''
                }

            # Populate assetInfo type
            if row['asset_class'] == '.InstrumentAssetRecord':
                row['assetInfo']['type'] = 'Sensor'
            elif row['asset_class'] == '.NodeAssetRecord':
                row['assetInfo']['type'] = 'Mooring'
            elif row['asset_class'] == '.AssetRecord':
                if len(ref_des) == 27:
                    row['assetInfo']['type'] = 'Sensor'
                elif len(ref_des) == 14:
                    row['assetInfo']['type'] = 'Platform'
                elif len(ref_des) == 8:
                    row['assetInfo']['type'] = 'Mooring'
                else:
                    if info:
                        message = 'Asset id %d, type .AssetRecord, has malformed a reference designator (%s)' % \
                                  (asset_id, ref_des)
                        current_app.logger.info(message)
                    row['assetInfo']['type'] = 'Unknown'
            else:
                if info:
                    message = 'Note ----- Unknown asset_class (%s), set to \'Unknown\'. ' % row['assetInfo']['type']
                    current_app.logger.info(message)
                row['assetInfo']['type'] = 'Unknown'
            try:
                # Verify all necessary attributes are available, if not create and set to empty.
                if 'name' not in row['assetInfo']:
                    row['assetInfo']['name'] = ''
                if 'longName' not in row['assetInfo']:
                    row['assetInfo']['longName'] = ''
                if 'array' not in row['assetInfo']:
                    row['assetInfo']['array'] = ''
                if 'assembly' not in row['assetInfo']:
                    row['assetInfo']['assembly'] = ''

                # Populate assetInfo - name and long name; if failure to get display name, use ref_des, log failure.
                name = get_dn_by_rd(ref_des)
                if name is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    name = ref_des
                longName = get_ldn_by_rd(ref_des)
                if longName is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    longName = ref_des
                row['assetInfo']['name'] = name
                row['assetInfo']['longName'] = longName

                # Populate assetInfo - array and assembly
                if len(ref_des) >= 8:
                    row['assetInfo']['array'] = get_dn_by_rd(ref_des[:2])
                if len(ref_des) >= 14:
                    row['assetInfo']['assembly'] = get_dn_by_rd(ref_des[:14])

            except Exception:
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

        except Exception:
            continue

    """
    print '\n debug -- len(bad_data): ', len(bad_data)
    print '\n debug -- len(bad_data_ids): ', len(bad_data_ids)
    """

    return bad_data
