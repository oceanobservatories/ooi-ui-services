#!/usr/bin/env python

"""
Asset Management - Assets: Supporting functions.
"""
__author__ = 'Edna Donoughe'
import requests
from flask import current_app
from ooiservices.app import cache
from copy import deepcopy
from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.vocab import (get_vocab, get_vocab_dict_by_rd, get_rs_array_name_by_rd, get_display_name_by_rd)
from ooiservices.app.uframe.uframe_tools import (get_assets_from_uframe, uframe_get_asset_by_id, uframe_get_asset_by_uid)
from ooiservices.app.uframe.common_tools import (get_asset_type_by_rd, get_asset_classes, get_supported_asset_types,
                                                 get_location_fields, get_uframe_asset_type, get_asset_type_display_name)
from ooiservices.app.uframe.asset_cache_tools import (_get_rd_assets, get_asset_deployment_info, get_asset_rds_cache,
                                                      asset_rds_cache_update, get_rd_from_rd_assets)
import datetime as dt
CACHE_TIMEOUT = 172800


def verify_cache(refresh=False):
    """ Verify necessary cached objects are available; if not get and set. Return asset_list data.
    """
    verify_cache_required = False
    try:
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Ensure cached: 'vocab_dict' and 'vocab_codes'; 'stream_list'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        vocab_dict = get_vocab()
        stream_list = get_stream_list()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check 'asset_list', 'assets_dict', 'asset_rds', 'rd_assets', 'asset_types'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not cache.get('asset_list') or not cache.get('assets_dict') or \
           not cache.get('asset_rds') or not cache.get('rd_assets'):
            verify_cache_required = True
        elif cache.get('asset_list') is None or cache.get('assets_dict') is None or \
            cache.get('asset_rds') is None or cache.get('rd_assets') is None:
            verify_cache_required = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If required, get asset(s) supporting cache(s)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verify_cache_required or refresh:
            data = get_assets_payload()
            if not data:
                message = 'No asset data returned from uframe.'
                current_app.logger.info(message)
                raise Exception(message)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Populate assets, return
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        else:
            data = cache.get('asset_list')

        return data

    except Exception as err:
        message = 'Error getting uframe assets. %s' % str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get all assets from uframe.
def get_assets_payload():
    """ Get all assets from uframe, process and update caches for:
            'asset_list', 'assets_dict', 'asset_rds', 'rd_assets'
    """
    debug = False
    try:
        print '\nCompiling assets...'
        try:
            # Clear all cache
            if cache.get('asset_list'):
                cache.delete('asset_list')
            if cache.get('assets_dict'):
                cache.delete('assets_dict')
            if cache.get('asset_rds'):
                cache.delete('asset_rds')
            if cache.get('rd_assets'):
                cache.delete('rd_assets')
        except Exception as err:
            message = str(err)
            raise Exception(message)

        # Get assets from uframe
        result = get_assets_from_uframe()
        if not result:
            message = 'No uframe asset content returned.'
            raise Exception(message)

        # Get asset_list and asset_rds.
        data, asset_rds = new_compile_assets(result, compile_all=True)
        if not data:
            message = 'Unable to process uframe assets; error creating assets_list.'
            raise Exception(message)
        if not asset_rds:
            message = 'Unable to process uframe assets; error creating asset_rds.'
            raise Exception(message)

        # Cache 'asset_list'.
        cache.set('asset_list', data, timeout=CACHE_TIMEOUT)
        check = cache.get('asset_list')
        if not check:
            message = 'Unable to process uframe assets; asset_list data is empty.'
            raise Exception(message)

        # Cache 'assets_rd'.
        cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)

        # Cache 'assets_dict'.
        assets_dict = populate_assets_dict(data)
        if assets_dict is None:
            message = 'Empty assets_dict returned from asset data.'
            raise Exception(message)

        # Cache 'rd_assets'.
        rd_assets = _get_rd_assets()
        if not rd_assets:
            message = 'Empty rd_assets returned from asset data.'
            raise Exception(message)

        print '\nCompleted compiling assets...\n'
        return data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get stream_list.
def get_stream_list():
    """ [Used by verify_cache.] Get 'stream_list' from cache; if not cached, get and set cache.
    """
    time = True
    stream_list = None
    try:

        stream_list_cached = cache.get('stream_list')
        if not stream_list_cached:
            if time: print '\nCompiling stream list'
            try:
                start = dt.datetime.now()
                if time: print '\t-- Start time: ', start
                stream_list = dfs_streams()
                end = dt.datetime.now()
                if time:
                    print '\t-- End time:   ', end
                    print '\t-- Time to get stream list: %s' % str(end - start)
            except Exception as err:
                message = str(err)
                raise Exception(message)

            if stream_list:
                cache.set('stream_list', stream_list, timeout=CACHE_TIMEOUT)
                if time:
                    print 'Completed compiling stream list'
            else:
                message = 'stream_list failed to return value, error.'
                current_app.logger.info(message)

        return stream_list

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get assets_dict.
def populate_assets_dict(data):
    """ [Used by verify_cache.] Build and cache assets_dict from assets_list; on error log and return None.
    """
    try:
        # Using assets_list data, create assets_dict
        assets_dict = get_assets_dict_from_list(data)

        # If no assets_dict returned, log error
        if not assets_dict:
            message = 'Warning: empty assets_dict returned from get_assets_dict_from_list.'
            current_app.logger.info(message)

        # Verify assets_dict is type dict
        elif isinstance(assets_dict, dict):
            cache.set('assets_dict', assets_dict, timeout=CACHE_TIMEOUT)

        return assets_dict

    except Exception as err:
        message = 'Error populating \'assets_dict\'; %s' % str(err)
        current_app.logger.info(message)
        return None


def get_assets_dict_from_list(assets_list):
    """ From list of (ooi-ui-services versioned) list of assets, create assets dictionary by (key) id.
    """
    result = {}
    if assets_list:
        for item in assets_list:
            if 'id' in item:
                if item['id'] not in result:
                    result[item['id']] = item
    return result

def _has_asset(rd):
    try:
        result = get_rd_from_rd_assets(rd)
        if result is None:
            bresult = False
        else:
            bresult = True
        return bresult
    except Exception as err:
        message = 'No asset identified for \'%s\'; %s' % (rd, str(err))
        current_app.logger.info(message)
        return False


def _get_asset(id):
    """ Get an asset by asset uid.

    This function is used by routes:
        /uframe/assets/<int:id>
        /uframe/assets/uid/<string:uid>
    """
    asset = {}
    try:
        if id < 1:
            message = 'Invalid asset id value.'
            raise Exception(message)
        assets_dict = cache.get('assets_dict')
        if assets_dict is not None:
            if id in assets_dict:
                asset = assets_dict[id]
        else:
            data = uframe_get_asset_by_id(id)
            if data:
                data_list = [data]
                result, _ = new_compile_assets(data_list)
                if result:
                    asset = result[0]
        return asset
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get asset from uframe by asset uid.
def _get_ui_asset_by_uid(uid):
    """ Get asset from uframe by asset uid, return ui asset.
    """
    asset = {}
    try:
        data = uframe_get_asset_by_uid(uid)
        if data and data is not None:
            data_list = [data]
            result, _ = new_compile_assets(data_list)
            if result:
                asset = result[0]
        return asset
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get asset from uframe by asset uid.
def get_uframe_asset_by_uid(uid):
    """ Get asset from uframe by asset uid, return ui asset.
    """
    data = {}
    try:
        data = uframe_get_asset_by_uid(uid)
        return data
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def format_asset_for_ui(modified_asset):
    """ Format uframe asset into ui asset.
    """
    try:
        # Process remoteResources list.
        remoteResources = None
        if 'remoteResources' in modified_asset:
            remoteResources = modified_asset['remoteResources']
        if remoteResources is not None:
            modified_asset['remoteResources'] = post_process_remote_resources(remoteResources)

        # Prepare and convert asset.
        data_list = [modified_asset]
        try:
            asset_with_update, _ = new_compile_assets(data_list)
            updated_asset = asset_with_update[0]
        except Exception as err:
            message = 'Failed to format asset for display. %s' % str(err)
            raise Exception(message)

        if not updated_asset or updated_asset is None:
            raise Exception('Asset compilation failed to return a result.')

        return updated_asset

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Prepare remote resources for display.
def post_process_remote_resources(resources):
    """ Process resources list from uframe before returning for display (in UI).
    """
    try:
        if not resources:
            return resources
        for resource in resources:
            if '@class' in resource:
                del resource['@class']
        return resources

    except Exception as err:
        message = 'Error post-processing event for display. %s' % str(err)
        raise Exception(message)


# todo - Refactor for new asset management data model; used by controller.py: get_svg_plot and dfs_streams
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
    #result = jsonify({'events': result})
    return result


def new_compile_assets(data, compile_all=False):
    """ Process list of asset dictionaries from uframe; transform into (ooi-ui-services) list of asset dictionaries.
    """
    debug = False
    info = False                # Log missing vocab items when unable to create display name(s), etc. (default is True)
    new_data = []               # (assets) Mooring, Node and Sensor assets which have been deployed
    bad_data = []               # (assets with unknown asset type or error.)
    bad_data_ids = []
    vocab_failures = []             # Vocabulary failures identified during asset processing are written to log.
    all_asset_types = []            # Gather from uframe asset collection all values of 'assetType' used
    all_asset_types_received = []   # Gather from uframe asset collection all values of 'assetType' received
    time = False

    try:
        if compile_all:
            time = True
            if time: print '\n-- Loading assets from uframe... '
            start = dt.datetime.now()
            if time: print '\t-- Start time: ', start

        update_asset_rds_cache = False
        dict_asset_ids = get_asset_rds_cache()

        # Ensure 'rd_assets' is in cache
        rd_assets = _get_rd_assets()

    except Exception as err:
        message = 'Error compiling asset_rds: %s' % err.message
        current_app.logger.info(message)
        raise Exception(message)

    # Process uframe list of asset dictionaries (data)
    valid_asset_classes = get_asset_classes()

    # Valid processing types are those assetTypes which are subsequently mapped to reference designators.
    valid_processing_types_uc = get_supported_asset_types()
    valid_processing_types = []
    for type in valid_processing_types_uc:
        valid_processing_types.append(type.lower())

    # for reporting informational message regarding deployments.
    no_deployments_title = '\t-- Note: Following reference designators are missing assets ids for deployment(s) listed: '
    all_no_deployments_message = ''
    all_no_deployments_dict = {}
    asset_supported_types = get_supported_asset_types()

    for row in data:
        ref_des = ''
        try:
            # Get asset_id, if not asset_id then continue
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

            if 'uid' in row:
                row['uid'] = row.pop('uid')
                asset_uid = row['uid']
                if asset_uid is None:
                    bad_data.append(row)
                    continue
                if not asset_uid:
                    bad_data.append(row)
                    continue

            if 'events' in row:
                del row['events']
            if 'calibration' in row:
                del row['calibration']
            if len(row['remoteResources']) == 0:
                row['remoteResources'] = []

            row['asset_class'] = row.pop('@class')

            # If ref_des not provided in row, use dictionary lookup.
            ref_des = None
            if 'ref_des' in row:
                if row['ref_des'] and row['ref_des'] is not None:
                    ref_des = row['ref_des']

            if ref_des is None:
                if asset_id in dict_asset_ids:
                    ref_des = dict_asset_ids[asset_id]

            # Gather list of all assetType values RECEIVED (for information only)
            asset_type = None
            uframe_asset_type = get_uframe_asset_type(row['assetType'])
            if row['assetType'] and row['assetType'] is not None:
                try:
                    asset_type = get_asset_type_display_name(row['assetType'])
                    row['assetType'] = asset_type

                    # Values processed
                    if uframe_asset_type not in all_asset_types_received:
                        all_asset_types_received.append(row['assetType'])

                except Exception as err:
                    message = 'get_uframe_asset_type: %s; error: %s' % (row['assetType'], str(err))
                    current_app.logger.info(message)
            else:
                message = 'Asset (id: %d) has a null or empty assetType value.' % asset_id
                current_app.logger.info(message)
                continue

            # Black box - place values into expected containers (minimize UI change)
            row['manufactureInfo'] = {}
            row['manufactureInfo']['manufacturer'] = row.pop('manufacturer')
            row['manufactureInfo']['modelNumber'] = row.pop('modelNumber')
            row['manufactureInfo']['serialNumber'] = row.pop('serialNumber')
            row['manufactureInfo']['firmwareVersion'] = row.pop('firmwareVersion')
            row['manufactureInfo']['softwareVersion'] = row.pop('softwareVersion')
            row['manufactureInfo']['shelfLifeExpirationDate'] = row.pop('shelfLifeExpirationDate')

            row['purchaseAndDeliveryInfo'] = {}
            if not row['deliveryDate'] or row['deliveryDate'] is None:
                row['purchaseAndDeliveryInfo']['deliveryDate'] = None
            else:
                row['purchaseAndDeliveryInfo']['deliveryDate'] = row.pop('deliveryDate')

            if not row['purchaseDate'] or row['purchaseDate'] is None:
                row['purchaseAndDeliveryInfo']['purchaseDate'] = None
            else:
                row['purchaseAndDeliveryInfo']['purchaseDate'] = row.pop('purchaseDate')
            row['purchaseAndDeliveryInfo']['purchasePrice'] = row.pop('purchasePrice')
            row['purchaseAndDeliveryInfo']['deliveryOrderNumber'] = row.pop('deliveryOrderNumber')

            row['partData'] = {}
            row['partData']['ooiPropertyNumber'] = row.pop('ooiPropertyNumber')
            row['partData']['ooiPartNumber'] = row.pop('ooiPartNumber')
            row['partData']['ooiSerialNumber'] = row.pop('ooiSerialNumber')
            row['partData']['institutionPropertyNumber'] = row.pop('institutionPropertyNumber')
            row['partData']['institutionPurchaseOrderNumber'] = row.pop('institutionPurchaseOrderNumber')

            # Populate physicalInfo dictionary. Move powerRequirements and depthRating into physicalInfo dictionary
            physicalInfo = {}
            physicalInfo['height'] = -1.0
            physicalInfo['weight'] = -1.0
            physicalInfo['width'] = -1.0
            physicalInfo['length'] = -1.0
            physicalInfo['depthRating'] = None
            physicalInfo['powerRequirements'] = None
            if 'physicalInfo' in row:
                if row['physicalInfo'] or row['physicalInfo'] is not None:
                    physicalInfo = row.pop('physicalInfo')
            if 'depthRating' in row:
                physicalInfo['depthRating'] = row.pop('depthRating')
            if 'powerRequirements' in row:
                physicalInfo['powerRequirements'] = row.pop('powerRequirements')
            row['physicalInfo'] = physicalInfo

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get asset class based on reference designator
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['asset_class'] or row['asset_class'] is None:
                message = 'asset_class empty or null for asset id %d.' % asset_id
                current_app.logger.info(message)
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                    continue

            # Validate asset_class, log asset class if unknown.
            asset_class = row.pop('asset_class')
            if asset_class not in valid_asset_classes:
                if info:
                    message = 'Asset class value (%s) not one of: %s' % (asset_class, valid_asset_classes)
                    current_app.logger.info(message)
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                    continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If no reference designator available, but have asset id then continue to next row.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not ref_des or ref_des is None:
                if uframe_asset_type not in asset_supported_types:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                    continue

            # Set default field values for assets without deployment/reference designators.
            row['deployment_number'] = ''
            row['deployment_numbers'] = []
            if 'lastModifiedTimestamp' in row:
                del row['lastModifiedTimestamp']

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Prepare assetInfo dictionary, populate with information or defaults.
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
                'mindepth': 0.0,
                'maxdepth': 0.0
            }
            # Asset owner
            row['assetInfo']['owner'] = row.pop('owner')

            # Populate assetInfo 'type' with uframe provided assetType.
            #asset_type = row['assetType']
            row['assetInfo']['type'] = asset_type

            # Verify all necessary attributes are available, if not create and set to empty.
            if row['name']:
                row['assetInfo']['asset_name'] = row.pop('name')
            if row['description']:
                row['assetInfo']['description'] = row.pop('description')

            name = None
            longName = None
            mindepth = 0.0
            maxdepth = 0.0
            row['assetInfo']['mindepth'] = mindepth
            row['assetInfo']['maxdepth'] = maxdepth
            row['assetInfo']['name'] = name
            row['assetInfo']['longName'] = longName
            row['assetInfo']['array'] = None
            row['assetInfo']['assembly'] = None
            row['ref_des'] = None

            # Handle location information.
            latitude = None
            longitude = None
            depth = None
            orbitRadius = None
            if 'location' in row:
                if row['location'] is not None:
                    tmp = deepcopy(row['location'])
                    latitude, longitude, depth, orbitRadius, loc_list = get_location_fields(tmp)
           
            #This section of code is used to popualte lat/lons in assets.  Assets no longer have lat/lon
            #in uFrame, so this must pull from the asset's deployments.
            debug = False
            uframe_url = current_app.config['UFRAME_DEPLOYMENTS_URL']
            asset_deployments = requests.get(uframe_url+'/asset/deployments/'+str(asset_uid)).json()
            most_recent_time = 0
            try:
                for deployment in asset_deployments:
                    if deployment['startTime'] > most_recent_time:
                        most_recent_time = deployment['startTime']
                        data_to_use = deployment
                latitude = data_to_use['latitude']
                longitude = data_to_use['longitude'] 
            except:
                if debug == True:
                    current_app.logger.info('No Lat/Lon for Asset ' + asset_uid)
            row['latitude'] = latitude
            row['longitude'] = longitude


            row['depth'] = depth
            row['orbitRadius'] = orbitRadius
            if 'location' in row:
                del row['location']

            if ref_des:
                #======================================================================
                # Set row values with reference designator
                row['ref_des'] = ref_des

                # Get type of asset we are processing, using reference designator. If invalid or None, continue.
                processing_asset_type = get_asset_type_by_rd(ref_des)
                if processing_asset_type:
                    processing_asset_type = processing_asset_type.lower()
                if processing_asset_type not in valid_processing_types:
                    #if debug: print '\n debug *** processing_asset_type %s not in valid_processing_types: %s' % \
                    #                (processing_asset_type, valid_processing_types)
                    continue

                # Get deployment information for this asset_id-rd; populate asset values using deployment information.
                deployment_numbers, no_deployments_nums, deployments_list = get_asset_deployment_map(asset_id, ref_des)
                row['deployment_number'] = deployment_numbers
                row['deployment_numbers'] = deployments_list

                # If reference designator has deployments which do not have associated asset ids, compile information.
                if no_deployments_nums:
                    # if ref_des not in all collection, add
                    if ref_des not in all_no_deployments_dict:
                        all_no_deployments_dict[ref_des] = no_deployments_nums
                    else:
                        for did in no_deployments_nums:
                            if did not in all_no_deployments_dict[ref_des]:
                                all_no_deployments_dict[ref_des].append(did)

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Populate assetInfo dictionary
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                try:
                    # Get vocabulary dict for ref_des; contains name, long_name, mindepth, maxdepth, model, manufacturer
                    name = None
                    longName = None
                    mindepth = 0.0
                    maxdepth = 0.0
                    vocab_dict = get_vocab_dict_by_rd(ref_des)
                    if vocab_dict:
                        row['assetInfo']['mindepth'] = vocab_dict['mindepth']
                        row['assetInfo']['maxdepth'] = vocab_dict['maxdepth']
                        name = vocab_dict['name']
                        longName = vocab_dict['long_name']
                    else:
                        row['assetInfo']['mindepth'] = mindepth
                        row['assetInfo']['maxdepth'] = maxdepth

                    # Populate assetInfo - name, if failure to get display name, use ref_des, log failure.
                    if name is None:
                        if ref_des not in vocab_failures:
                            vocab_failures.append(ref_des)
                        if info:
                            message = 'Vocab Note ----- reference designator (%s) failed to get display name for:' % ref_des
                            current_app.logger.info(message)
                        name = ref_des
                    row['assetInfo']['name'] = name

                    # Populate assetInfo - long name, if failure to get long name then use ref_des, log failure.
                    if longName is None:
                        if ref_des not in vocab_failures:
                            vocab_failures.append(ref_des)
                        if info:
                            message = 'Vocab Note ----- reference designator (%s) failed to get display name for:' % ref_des
                            current_app.logger.info(message)
                        longName = ref_des
                    row['assetInfo']['longName'] = longName

                    # Populate assetInfo - array and assembly
                    if len(ref_des) >= 8:
                        if ref_des[:2] == 'RS':
                            row['assetInfo']['array'] = get_rs_array_name_by_rd(ref_des[:8])
                        else:
                            row['assetInfo']['array'] = get_display_name_by_rd(ref_des[:2])
                    if len(ref_des) >= 14:
                        row['assetInfo']['assembly'] = get_display_name_by_rd(ref_des[:14])
                    #=============================================================================

                except Exception as err:
                    # asset info error
                    message = 'asset (with rd) processing error: ' + str(err.message)
                    current_app.logger.info(message)
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue

            # Gather list of all assetType values (information only)
            if row['assetType']:
                if row['assetType'] not in all_asset_types:
                    all_asset_types.append(row['assetType'])

            #row['assetType'] = row['type']
            # Add new row to output dictionary
            if asset_id:    # and ref_des:
                new_data.append(row)
                # if new item for dictionary of asset ids, add id with value of reference designator
                if asset_id not in dict_asset_ids:
                    if ref_des:
                        if ref_des is not None:
                            dict_asset_ids[asset_id] = ref_des
                            update_asset_rds_cache = True

        except Exception as err:
            message = str(err)
            current_app.logger.info(message)
            continue

        # end of asset processing loop

    if compile_all:
        # If reference designators with missing deployment(s), log sorted by reference designator.
        if all_no_deployments_dict:
            the_keys = all_no_deployments_dict.keys()
            the_keys.sort()

            # Display reference designators with missing deployment(s), sorted by reference designator.
            for key in the_keys:
                all_no_deployments_message += '\n\t\t%s: %s' % (key, all_no_deployments_dict[key])
            missing_deployment_message = no_deployments_title + all_no_deployments_message
            #current_app.logger.info(missing_deployment_message)
            if debug: print '\n%s' % missing_deployment_message

        # Log vocabulary failures (occur when creating display names)
        if vocab_failures:
            vocab_failures.sort()
            message = 'These reference designator(s) are not defined, causing display name failures(%d): %s' \
                      % (len(vocab_failures), vocab_failures)
            current_app.logger.info(message)

        # Amend 'dict_asset_ids' to reflect information from processing
        if dict_asset_ids:
            if update_asset_rds_cache:
                asset_rds_cache_update(dict_asset_ids)

        if debug:
            print '\n All asset types processed: ', all_asset_types
            print '\n All asset types received: ', all_asset_types_received

        print '\n\t-- Total number of assets compiled: ', len(new_data)

    if time:
        end = dt.datetime.now()
        if time: print '\n\t-- End time:   ', end
        if time: print '\t-- Time to load uframe assets: %s' % str(end - start)

    return new_data, dict_asset_ids


#=============================================

def get_asset_deployment_map(asset_id, ref_des):
    """ For an asset id and associated reference designator, get deployment [map] information.
    Process deployment information to obtain/return the following for the asset id/reference designator:
        depth (float, default: 0.0)
        location (list, [0.0, 0.0])
        has_deployment_event (bool, default: False)
        deployment_numbers (str, default: '')
        tense (str, default: '')

    Each asset displays the following information related to deployment(s):
      New deployment display grid covers these deployment related items on per deployment basis:
        deployment_number, beginDT, endDT, tense, and
        location dict with: latitude, longitude, location [], orbit radius and depth
    Note: on current deployment the endDT will be null if deployment is active.

    """
    try:
        # Valid processing types are those assetTypes which are subsequently mapped to reference designators.
        valid_processing_types_uc = get_supported_asset_types()
        valid_processing_types = []
        for type in valid_processing_types_uc:
            valid_processing_types.append(type.lower())
        deployment_numbers = ''
        _deployment_numbers = []

        # Get type of asset we are processing, using reference designator.
        asset_type = get_asset_type_by_rd(ref_des)
        if asset_type:
            asset_type = asset_type.lower()

        no_deployments_nums = []
        if asset_type in valid_processing_types:
            deployments_info = get_asset_deployment_info(asset_id, ref_des)
            if deployments_info:
                deployments_list = deployments_info['deployments']

                # Determine if has_deployment_event and location
                if deployments_list:
                    deployments_list.sort(reverse=True)
                    # Get coordinate information from most recent deployment
                    current_deployment_number = deployments_info['current_deployment']

                    # Get deployment number(s) for this asset id
                    _deployment_numbers = []
                    for deploy_number in deployments_list:
                        # Get asset ids, based on asset type (of associated) reference designator being processed,
                        tmp = deployments_info[deploy_number]['asset_ids_by_type'][asset_type]
                        if tmp:
                            if asset_id in tmp:
                                if deploy_number not in _deployment_numbers:
                                    _deployment_numbers.append(deploy_number)
                        else:
                            # In this case there is a deployments_list, but deployments_info for this deploy_number
                            # does not have asset ids for asset_type in assets map. (uframe missing data problem)
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

                    if _deployment_numbers:
                        _deployment_numbers.sort()
                        for dn in _deployment_numbers:
                                deployment_numbers += str(dn) + ', '
                        if deployment_numbers:
                            deployment_numbers = deployment_numbers.strip(', ')

                    # Highlight (*) deployments if most recent deployment has an empty 'node' attribute.
                    if no_deployments_nums:
                        if current_deployment_number in no_deployments_nums:
                            deployment_numbers += ' *'
        return deployment_numbers, no_deployments_nums, _deployment_numbers

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None
