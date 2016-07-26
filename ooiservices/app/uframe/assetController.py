#!/usr/bin/env python

""" uframe assets and events endpoint and class definition.
"""

from flask import jsonify, current_app
from ooiservices.app import cache
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.vocab import get_display_name_by_rd as get_dn_by_rd
from ooiservices.app.uframe.vocab import get_long_display_name_by_rd as get_ldn_by_rd
from ooiservices.app.uframe.asset_tools import (_compile_asset_rds, get_asset_deployment_info, _get_rd_assets)
from ooiservices.app.uframe.asset_tools import (is_instrument, is_mooring, is_platform)
from ooiservices.app.uframe.asset_tools import get_assets_dict_from_list
import re
import math

import requests
#import requests.adapters
#requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 172800

'''
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
'''

def _compile_assets(data, compile_all=False):
    """ Process list of asset dictionaries from uframe; transform into (ooi-ui-services) list of asset dictionaries.
    """
    debug = False
    info = True         # Log missing vocab items when unable to create display name(s), etc.
    feedback = False    # For development only: Display information as assets are processed
    new_data = []
    bad_data = []
    bad_data_ids = []

    vocab_failures = []             # Vocabulary failures identified during asset processing are written to log.
    dict_asset_ids = {}
    all_asset_types = []            # Gather from uframe asset collection all values of 'assetType' used
    all_asset_types_received = []   # Gather from uframe asset collection all values of 'assetType' received

    try:
        update_asset_rds_cache = False
        if debug:
            if data:
                print '\n debug -- data received: ', len(data)
            else:
                print '\n debug -- No asset data received to process in assetController.'

        # Get 'asset_rds' cache
        cached = cache.get('asset_rds')
        if cached:
            if debug: print '\n debug -- asset_rds is cached....'
            dict_asset_ids = cached

        if not cached or not isinstance(cached, dict):

            if debug: print '\n debug -- getting asset_rds...'
            # If no asset_rds cached, then fetch and cache
            asset_rds = {}
            #rds_wo_assets = []
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
                #print '\n cache asset_rds: ', asset_rds

            dict_asset_ids = asset_rds

            """
            # List of reference designators [in toc i.e./sensor/inv] but without associated asset id(s).
            # Usage: If rd in data catalog, but also in rds_wo_assets, no asset to navigate to.
            if rds_wo_assets:
                cache.set('rds_wo_assets', rds_wo_assets, timeout=CACHE_TIMEOUT)
                print "Reference designators with out assets ('rds_wo_assets') cache reset..."
            """

        # Ensure 'rd_assets' is in cache (ensure asset deployment information is available for processing)
        rd_assets = _get_rd_assets()

    except Exception as err:
        message = 'Error compiling asset_rds: %s' % err.message
        current_app.logger.info(message)
        raise Exception(message)

    # Process uframe list of asset dictionaries (data)
    print '\n Compiling assets...'
    valid_asset_classes = ['.XInstrument', '.XNode', '.XMooring', '.XAsset']

    # Valid processing types are those assetTypes which are subsequently mapped to reference designators.
    valid_processing_types = ['mooring', 'node', 'sensor']

    no_deployments_title = '\nFollowing reference designators are missing assets ids for deployment(s) listed: '
    all_no_deployments_message = ''
    all_no_deployments_dict = {}

    for row in data:

        ref_des = ''
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

            if 'events' in row:
                del row['events']
            if 'calibration' in row:
                del row['calibration']
            if 'location' in row:
                del row['location']

            if len(row['remoteResources']) == 0:
                row['remoteResources'] = []

            # If asset is of type 'notClassified', add to bad_assets and continue
            if 'assetType' in row:
                if 'notClassified' == row['assetType']:
                    bad_data.append(row)
                    continue

            row['asset_class'] = row.pop('@class')

            # If ref_des not provided in row, use dictionary lookup.
            if asset_id in dict_asset_ids:
                ref_des = dict_asset_ids[asset_id]

            # Gather list of all assetType values RECEIVED (for information only)
            if row['assetType']:
                if row['assetType'] not in all_asset_types_received:
                    all_asset_types_received.append(row['assetType'])

            #if debug: print '\n debug ---- CHECK -------- (%r) ref_des: *%s*' % (asset_id, ref_des)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If no reference designator available, but have asset id then continue to next row.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not ref_des or ref_des is None:
                # If reference designator not provided, add to bad_assets, continue to next.
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Set row values with reference designator
            row['ref_des'] = ref_des
            row['Ref Des'] = ref_des
            if feedback: print '\n debug ---------------- (%r) ref_des: *%s*' % (asset_id, ref_des)

            if len(row['remoteResources']) == 0:
                row['remoteResources'] = []
            else:
                if debug: print '\n debug -- Asset id %d has remoteResources available (rd: %s: ' % (asset_id, ref_des)

            # Get type of asset we are processing, using reference designator. If invalid or None, continue.
            processing_asset_type = get_processing_asset_type(ref_des)
            if processing_asset_type is None or processing_asset_type not in valid_processing_types:
                continue

            # Get deployment information for this asset_id-rd; populate asset values using deployment information.
            depth, location, has_deployment_event, deployment_numbers, tense, no_deployments_nums, deployments_list \
                                        = get_asset_deployment_map(asset_id, ref_des)

            # If reference designator has deployments which do not have associated asset ids, compile information.
            if no_deployments_nums:
                # if ref_des not in all collection, add
                if ref_des not in all_no_deployments_dict:
                    all_no_deployments_dict[ref_des] = no_deployments_nums
                else:
                    for did in no_deployments_nums:
                        if did not in all_no_deployments_dict[ref_des]:
                            all_no_deployments_dict[ref_des].append(did)

            row['depth'] = depth
            row['coordinates'] = location
            row['hasDeploymentEvent'] = has_deployment_event
            row['deployment_number'] = deployment_numbers
            row['deployment_numbers'] = deployments_list
            row['tense'] = tense

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get asset class based on reference designator
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['asset_class'] or row['asset_class'] is None:
                message = 'asset_class empty or null for asset id %d (reference designator %s)' % (asset_id, ref_des)
                current_app.logger.info(message)
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Validate asset_class, log asset class if unknown.
            asset_class = row.pop('asset_class')
            if asset_class not in valid_asset_classes:
                if info:
                    message = 'Reference designator (%s) has an asset class value (%s) not one of: %s' % \
                        (ref_des, asset_class, valid_asset_classes)
                    current_app.logger.info(message)
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Populate assetInfo dictionary
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            row['assetInfo'] = {
                'name': "",
                'type': '',
                'owner': '',
                'description': '',
                'longName': '',
                'array': '',
                'assembly': '',
                'asset_name': '',
            }
            # Asset owner
            row['assetInfo']['owner'] = row.pop('owner')

            # Populate assetInfo 'type' with uframe provided assetType todo review platform assetType values
            asset_type = row['assetType']
            if asset_type == 'Node':
                asset_type = 'Platform'
            row['assetInfo']['type'] = asset_type

            try:
                # Verify all necessary attributes are available, if not create and set to empty.
                if row['name']:
                    row['assetInfo']['asset_name'] = row.pop('name')

                if row['description']:
                    row['assetInfo']['description'] = row.pop('description')

                # Populate assetInfo - name, if failure to get display name, use ref_des, log failure.
                name = get_dn_by_rd(ref_des)
                if name is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    if info:
                        message = 'Vocab Note ----- reference designator (%s) failed to get get_dn_by_rd' % ref_des
                        current_app.logger.info(message)
                    name = ref_des
                row['assetInfo']['name'] = name

                # Populate assetInfo - long name, if failure to get long name then use ref_des, log failure.
                longName = get_ldn_by_rd(ref_des)
                if longName is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    if info:
                        message = 'Vocab Note ----- reference designator (%s) failed to get get_ldn_by_rd' % ref_des
                        current_app.logger.info(message)
                    longName = ref_des
                row['assetInfo']['longName'] = longName

                # Populate assetInfo - array and assembly
                if len(ref_des) >= 8:
                    row['assetInfo']['array'] = get_dn_by_rd(ref_des[:2])
                if len(ref_des) >= 14:
                    row['assetInfo']['assembly'] = get_dn_by_rd(ref_des[:14])

                # Black box - place values into expected containers (minimize UI change)
                row['manufactureInfo'] = {}
                row['manufactureInfo']['manufacturer'] = row.pop('manufacturer')
                row['manufactureInfo']['modelNumber'] = row.pop('modelNumber')
                row['manufactureInfo']['serialNumber'] = row.pop('serialNumber')
                row['manufactureInfo']['firmwareVersion'] = row.pop('firmwareVersion')
                row['manufactureInfo']['softwareVersion'] = row.pop('softwareVersion')
                row['manufactureInfo']['shelfLifeExpirationDate'] = row.pop('shelfLifeExpirationDate')
                row['remoteDocuments'] = []
                row['purchaseAndDeliveryInfo'] = {}
                row['purchaseAndDeliveryInfo']['deliveryDate'] = row.pop('deliveryDate')
                row['purchaseAndDeliveryInfo']['purchaseDate'] = row.pop('purchaseDate')
                row['purchaseAndDeliveryInfo']['purchasePrice'] = row.pop('purchasePrice')
                row['purchaseAndDeliveryInfo']['deliveryOrderNumber'] = row.pop('deliveryOrderNumber')
                row['partData'] = {}
                row['partData']['ooiPropertyNumber'] = row.pop('ooiPropertyNumber')
                row['partData']['ooiPartNumber'] = row.pop('ooiPartNumber')
                row['partData']['ooiSerialNumber'] = row.pop('ooiSerialNumber')
                row['partData']['institutionPropertyNumber'] = row.pop('institutionPropertyNumber')
                row['partData']['institutionPurchaseOrderNumber'] = row.pop('institutionPurchaseOrderNumber')
                if 'physicalInfo' in row:
                    row['physicalInfo']['depthRating'] = row.pop('depthRating')
                    row['physicalInfo']['powerRequirements'] = row.pop('powerRequirements')     # [req 3.1.6.10]

                # Gather list of all assetType values (information only)
                if row['assetType']:
                    if row['assetType'] not in all_asset_types:
                        all_asset_types.append(row['assetType'])

            except Exception as err:
                # asset info error
                current_app.logger.info('asset info error' + str(err.message))
                if debug: print '\n debug -- error: ', str(err)
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

        except Exception as err:
            current_app.logger.info(str(err))
            if debug: print '\n debug -- error: ', str(err)
            continue

    # If reference designators with missing deployment(s), log sorted by reference designator.
    if all_no_deployments_dict:
        the_keys = all_no_deployments_dict.keys()
        the_keys.sort()

        # Display reference designators with missing deployment(s), sorted by reference designator.
        for key in the_keys:
            all_no_deployments_message += '\n%s: %s' % (key, all_no_deployments_dict[key])
        missing_deployment_message = no_deployments_title + all_no_deployments_message
        if debug: print '\n debug -- missing_deployment_message: ', missing_deployment_message
        current_app.logger.info(missing_deployment_message)

    # Log vocabulary failures (occur when creating display names)
    if vocab_failures:
        vocab_failures.sort()
        message = 'These reference designator(s) are not defined, causing display name failures(%d): %s' \
                  % (len(vocab_failures), vocab_failures)
        current_app.logger.info(message)

    if compile_all:
        # Amend 'dict_asset_ids' to reflect information from processing
        if dict_asset_ids:
            if update_asset_rds_cache:
                cache.set('asset_rds', dict_asset_ids, timeout=CACHE_TIMEOUT)

        # Update cache for 'bad_asset_list'
        bad_assets_cached = cache.get('bad_asset_list')
        if bad_assets_cached:
            cache.delete('bad_asset_list')
            cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)
        else:
            cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)

        if all_asset_types:
            cache.set('asset_types', all_asset_types, timeout=CACHE_TIMEOUT)

    if debug:
        print '\n debug -- len(dict_asset_ids): ', len(dict_asset_ids)
        print '\n debug -- len(new_data): ', len(new_data)
    print '\n Note:\n Asset types used: ', all_asset_types
    print ' Asset types received: ', all_asset_types_received

    print '\n Completed compiling assets...'
    return new_data, dict_asset_ids


def get_processing_asset_type(rd):
    """ For reference designator, return asset type being processed, one item from ['mooring, 'node', 'sensor'] or None.
    """
    result = None
    try:
        if is_instrument(rd):
            result = 'sensor'
        elif is_mooring(rd):
            result = 'mooring'
        elif is_platform(rd):
            result = 'node'
        return result

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_processing_asset_type]: ', message
        current_app.logger.info(message)
        return None


def get_asset_deployment_map(asset_id, ref_des):
    """ For an asset id and associated reference designator, get deployment [map] information.
    Process deployment information to obtain/return the following for the asset id/reference designator:
        depth (float, default: 0.0)
        location (list, [0.0, 0.0])
        has_deployment_event (bool, default: False)
        deployment_numbers (str, default: '')
        tense (str, default: '')

    Each asset displays the following information related to deployment(s):
      hasDeploymentEvent (bool),
      New deployment display grid covers these deployment related items on per deployment basis:
        deployment_number, beginDT, endDT, tense, and
        location dict with: latitude, longitude, location [], orbit radius and depth
    Note: on current deployment the endDT will be null if deployment is active.

    """
    # Valid processing types are those assetTypes which are subsequently mapped to reference designators.
    valid_processing_types = ['mooring', 'node', 'sensor']

    debug = False
    depth = 0.0
    location = [0.0, 0.0]
    has_deployment_event = False
    deployment_numbers = ''
    _deployment_numbers = []
    tense = ''
    try:
        # Get type of asset we are processing, using reference designator.
        processing_asset_type = get_processing_asset_type(ref_des)
        if debug:
            if processing_asset_type not in valid_processing_types:
                print '\n debug ------------ processing_asset_type not valid: ', processing_asset_type

        no_deployments_nums = []
        if processing_asset_type is not None and processing_asset_type in ['mooring', 'node', 'sensor']:
            if debug: print '\n debug ------------ processing_asset_type: ', processing_asset_type
            deployments_info = get_asset_deployment_info(asset_id, ref_des)
            if deployments_info:
                deployments_list = deployments_info['deployments']

                # Determine if has_deployment_event and location
                if deployments_list:
                    has_deployment_event = True
                    deployments_list.sort(reverse=True)

                    # Get coordinate information from most recent deployment
                    current_deployment_number = deployments_info['current_deployment']
                    current_deployment = deployments_info[current_deployment_number]
                    latitude = round(current_deployment['location']['latitude'], 4)
                    longitude = round(current_deployment['location']['longitude'], 4)
                    location = [longitude, latitude]
                    depth = current_deployment['location']['depth']
                    if debug:
                        print '\n debug -- Most recent deployment number: %d -- tense %s' % \
                              (current_deployment_number, current_deployment['tense'])

                    # Get deployment number(s) for this asset id
                    _deployment_numbers = []
                    for deploy_number in deployments_list:

                        # Get asset ids, based on asset type (of associated) reference designator being processed,
                        tmp = deployments_info[deploy_number]['asset_ids_by_type'][processing_asset_type]
                        if tmp:
                            if debug: print '\n debug -- %s %s deployment %d has asset ids: %s' % \
                                            (ref_des, processing_asset_type, deploy_number, tmp)
                            if asset_id in tmp:
                                if deploy_number not in _deployment_numbers:
                                    _deployment_numbers.append(deploy_number)
                        else:
                            # In this case there is a deployments_list, but deployments_info for this deploy_number
                            # does not have asset ids for processing_asset_type in assets map. (uframe missing data problem)
                            # Basically 'sensor' data does not have assetId for deploy_number deployment.
                            # This MAY lead to incorrectly identifying the most recent or current deployment for
                            # this asset id; certainly deployment asset map will have 'holes' if data is missing.
                            # Example: CP02PMUO-SBS01-01-MOPAK0000 (sensor) has 7 deployments, and deployment 7
                            # does not have a node value which identifies an assetId. So deployment 7 will not have
                            # a value in deployment_info[7][asset_ids_by_type]['sensor'] but instead is [].
                            # http://host:12587/events/deployment/inv/CP02PMUO/SBS01/01-MOPAK0000/7
                            # [{
                            #   "@class" : ".XDeployment",
                            #   "location" : {
                            #       "depth" : 0.0,
                            #       "location" : [ -70.7800166, 39.942116 ],
                            #       "longitude" : -70.7800166,
                            #       "latitude" : 39.942116,
                            #       "orbitRadius" : 0.0
                            #   },
                            #   "sensor" : null,
                            #   "node" : null,
                            #   "referenceDesignator" : {
                            #       "subsite" : "CP02PMUO",
                            #       "sensor" : "01-MOPAK0000",
                            #       "node" : "SBS01",
                            #       "full" : true
                            #   }, . . .
                            # }]
                            if deploy_number not in no_deployments_nums:
                                no_deployments_nums.append(deploy_number)
                            if debug:
                                message = 'No asset ids for %s, deployment %d.' % (ref_des, deploy_number)
                                print '\n debug -- ', message

                    # Get tense value for last deployment provided
                    if _deployment_numbers:
                        _deployment_numbers.sort(reverse=True)
                        recent_deployment_number = _deployment_numbers[0]
                        if current_deployment_number != recent_deployment_number:
                            if debug: print '\n debug -- reporting recent_deployment number %d, as last, not %d' % \
                                            (recent_deployment_number, current_deployment_number)
                        tense = deployments_info[recent_deployment_number]['tense']
                        _deployment_numbers.sort()
                        for dn in _deployment_numbers:
                                deployment_numbers += str(dn) + ', '

                        if deployment_numbers:
                            deployment_numbers = deployment_numbers.strip(', ')

                    # Highlight (*) deployments if most recent deployment has an empty 'node' attribute.
                    if no_deployments_nums:
                        if current_deployment_number in no_deployments_nums:
                            deployment_numbers += ' *'

        return depth, location, has_deployment_event, deployment_numbers, tense, no_deployments_nums, _deployment_numbers

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_processing_asset_type]: ', message
        current_app.logger.info(message)
        return None


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
    """ Removes extra white space from a string. (Requires re)
    """
    string = string.strip()
    string = re.sub(r'\s+', ' ', string)
    return string


def _remove_duplicates(values):
    """ Removes duplicate values, useful in getting a concise list. (Requires re)
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


#====================================================================
# todo - modify or remove for new uframe asset management data model
# todo used by controller.py: get_svg_plot and dfs_streams
def get_events_by_ref_des(data, ref_des):
    """ Create the container for the processed response.
    """
    result = []
    '''
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
    '''
    result = jsonify({'events': result})
    return result


#---------------------------------------------------------------------------------------
#-- The following routes are for generating drop down lists, used in filtering view.
#---------------------------------------------------------------------------------------
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
    info = False           # detect missing vocab items when unable to create display name(s)
    feedback = False       # (development/debug) display messages while processing each asset
    vocab_failures = []
    dict_asset_ids = {}
    try:
        cached = cache.get('asset_rds')
        if cached:
            dict_asset_ids = cached
        if not cached or not isinstance(cached, dict):
            # If no asset_rds cached, then fetch and cache
            asset_rds = {}
            rds_wo_assets = []
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
            else:
                message = 'Error in asset_rds cache update.'
                current_app.logger.warning(message)

            dict_asset_ids = asset_rds

            """
            # List of reference designators [in toc i.e./sensor/inv] but without associated asset id(s).
            # Usage: If rd in data catalog, but also in rds_wo_assets, no asset to navigate to.
            if rds_wo_assets:
                cache.set('rds_wo_assets', rds_wo_assets, timeout=CACHE_TIMEOUT)
                if debug: print "[+] Reference designators with assets cache reset..."
            """

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
            #row['events'] = associate_events(row['id'])
            if len(row['events']) == 0:
                row['events'] = []
            row['tense'] = None

            # If ref_des not provided in row, use dictionary lookup.
            if asset_id in dict_asset_ids:
                ref_des = dict_asset_ids[asset_id]

            """
            # Process metadata (Note: row['metaData'] is often an empty list (especially for instruments).
            # -- Process when row['metaData'] is None (add metaData if possible)
            if row['metaData'] is None:
                if ref_des:
                    row['metaData'] = [{u'type': u'java.lang.String', u'key': u'Ref Des', u'value': ref_des}]
                else:
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
            """
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
            #row['coordinates'] = convert_lat_lon(lat, lon)

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


#====================================
# todo review, rework or remove - no further asset metadata with new asset management data model
'''
def _get_instrument_asset_by_id(id):
    """ Get uframe instrument asset for id. Return instrument asset dict, None or raise exception.

    Sample request:
        http://localhost:12587/asset/cal?assetId=1725

    Sample response:
    {
      "@class" : ".XInstrument",
      "calibration" : [ {
        "@class" : ".XCalibration",
        "name" : "CC_csv",
        "calData" : [ {
          "@class" : ".XCalibrationData",
          "values" : [ 0.00281984, 1.203E-4, 2.37169E-6, 230.373, -0.353858, -56.5682, 4.56096 ],
          "comments" : null,
          "dimensions" : [ 7 ],
          "cardinality" : 1,
          "eventId" : 5961,
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_csv",
          "eventStartTime" : 1420070400000,
          "eventStopTime" : null,
          "dataSource" : null,
          "lastModifiedTimestamp" : 1465243531300
        } ]
      }, {
        "@class" : ".XCalibration",
        "name" : "CC_lon",
        "calData" : [ {
          "@class" : ".XCalibrationData",
          "values" : [ -70.7701333333333 ],
          "comments" : null,
          "dimensions" : [ 1 ],
          "cardinality" : 0,
          "eventId" : 5962,
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_lon",
          "eventStartTime" : 1420070400000,
          "eventStopTime" : null,
          "dataSource" : null,
          "lastModifiedTimestamp" : 1465243531300
        } ]
      }, {
        "@class" : ".XCalibration",
        "name" : "CC_lat",
        "calData" : [ {
          "@class" : ".XCalibrationData",
          "values" : [ 40.1340833333333 ],
          "comments" : null,
          "dimensions" : [ 1 ],
          "cardinality" : 0,
          "eventId" : 5963,
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_lat",
          "eventStartTime" : 1420070400000,
          "eventStopTime" : null,
          "dataSource" : null,
          "lastModifiedTimestamp" : 1465243531300
        } ]
      } ],
      "events" : null,
      "assetId" : 1725,
      "name" : "351",
      "location" : null,
      "serialNumber" : "351",
      "uid" : "N00556",
      "assetType" : "Sensor",
      "mobile" : false,
      "manufacturer" : "AANDERAA",
      "modelNumber" : "4831",
      "description" : null,
      "physicalInfo" : null,
      "purchasePrice" : 5258.25,
      "purchaseDate" : 0,
      "deliveryDate" : null,
      "depthRating" : null,
      "dataSource" : "/home/asadev/uframes/uframe_ooi_20160606_20cf4e35f193cda57d8c397ab57370c33486da33/uframe-1.0/edex/data/ooi/xasset_spreadsheet/newA_bulk_load-AssetRecord.csv",
      "lastModifiedTimestamp" : 1465243413906
    }
    """
    debug = True
    result = None
    try:
        if debug: print '\n debug -- _get_instrument_asset_by_id for id: ', id
        # Get uframe connect and timeout information
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, 'asset/cal?assetid='])
        url += str(id)
        if debug: print '\n debug -- [_get_instrument_asset_by_id] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get instrument asset for id %r.' % (response.status_code, id)
            current_app.logger.info(message)
            raise Exception(message)

        result = response.json()
        if debug: print '\n debug -- (dict) result: ', result
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)

# todo review, remove or rework for new asset management data model
def _get_asset_metadata(id):
    """
    Require: latitude
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
        if meta_data['key'] == 'Water Depth':
            depth = meta_data['value']
        # If key 'Ref Des' has a value, use it, otherwise use ref_des value.
        if meta_data['key'] == 'Ref Des':
            if meta_data['value']:
                ref_des = meta_data['value']
            meta_data['value'] = ref_des
    """
    debug = True
    try:
        if debug: print '\n debug -- _get_asset_metadata for id: ', id

        result = _get_instrument_asset_by_id(id)

        if debug: print '\n debug -- _metadata: ', result

        # todo - perform surgery on result
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)
    except ConnectionError:
        message = 'ConnectionError getting uframe instrument asset for id %r.  %s' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe instrument asset for id %r.  %s' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        print '\n debug -- exception [_get_instrument_asset_by_id]: ', message
        current_app.logger.info(message)
        raise
'''



