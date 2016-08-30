#!/usr/bin/env python

"""
Assets: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app import cache
from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.toc_tools import _compile_asset_rds
from ooiservices.app.uframe.config import (get_uframe_assets_info, get_assets_url_base, headers, get_url_info_resources)
from ooiservices.app.uframe.common_tools import (get_asset_type_by_rd, get_asset_classes, get_supported_asset_types)
from ooiservices.app.uframe.vocab import (get_vocab, get_vocab_dict_by_rd, get_rs_array_display_name_by_rd,
                                          get_display_name_by_rd)
import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
import datetime as dt
import json

CACHE_TIMEOUT = 172800


def _compile_assets(data, compile_all=False):
    """ Process list of asset dictionaries from uframe; transform into (ooi-ui-services) list of asset dictionaries.
    """
    info = True         # Log missing vocab items when unable to create display name(s), etc. (default is True)
    new_data = []
    bad_data = []
    bad_data_ids = []
    vocab_failures = []             # Vocabulary failures identified during asset processing are written to log.
    all_asset_types = []            # Gather from uframe asset collection all values of 'assetType' used
    all_asset_types_received = []   # Gather from uframe asset collection all values of 'assetType' received

    try:
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
    no_deployments_title = '\nFollowing reference designators are missing assets ids for deployment(s) listed: '
    all_no_deployments_message = ''
    all_no_deployments_dict = {}

    # todo - refactor
    from ooiservices.app.uframe.deployment_tools import get_asset_deployment_map

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
                if 'notClassified' == row['assetType'] or 'Array' == row['assetType']:
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

            if len(row['remoteResources']) == 0:
                row['remoteResources'] = []

            # Get type of asset we are processing, using reference designator. If invalid or None, continue.
            processing_asset_type = get_asset_type_by_rd(ref_des)
            if processing_asset_type:
                processing_asset_type = processing_asset_type.lower()
            if processing_asset_type not in valid_processing_types:
                continue

            # Get deployment information for this asset_id-rd; populate asset values using deployment information.
            depth, location, has_deployment_event, deployment_numbers, cumulative_tense, tense, \
                no_deployments_nums, deployments_list = get_asset_deployment_map(asset_id, ref_des)

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
            row['longitude'] = location[0]
            row['latitude'] = location[1]
            row['deployment_number'] = deployment_numbers
            row['deployment_numbers'] = deployments_list
            row['cumulative_tense'] = cumulative_tense                 # tense based on review of deployment numbers
            row['tense'] = tense                            # uframe deployment tense

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
                'mindepth': 0,
                'maxdepth': 0
            }
            # Asset owner
            row['assetInfo']['owner'] = row.pop('owner')

            # Populate assetInfo 'type' with uframe provided assetType.
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

                # Get vocabulary dict for ref_des; contains name, long_name, mindepth, maxdepth, model, manufacturer
                name = None
                longName = None
                mindepth = 0
                maxdepth = 0
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
                #longName = get_ldn_by_rd(ref_des)
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
                        row['assetInfo']['array'] = get_rs_array_display_name_by_rd(ref_des[:8])
                    else:
                        row['assetInfo']['array'] = get_display_name_by_rd(ref_des[:2])
                if len(ref_des) >= 14:
                    row['assetInfo']['assembly'] = get_display_name_by_rd(ref_des[:14])

                # Black box - place values into expected containers (minimize UI change)
                row['manufactureInfo'] = {}
                row['manufactureInfo']['manufacturer'] = row.pop('manufacturer')
                row['manufactureInfo']['modelNumber'] = row.pop('modelNumber')
                row['manufactureInfo']['serialNumber'] = row.pop('serialNumber')
                row['manufactureInfo']['firmwareVersion'] = row.pop('firmwareVersion')
                row['manufactureInfo']['softwareVersion'] = row.pop('softwareVersion')
                row['manufactureInfo']['shelfLifeExpirationDate'] = row.pop('shelfLifeExpirationDate')
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

                # Move powerRequirements and depthRating into physicalInfo dictionary
                if 'physicalInfo' in row:
                    row['physicalInfo']['depthRating'] = row.pop('depthRating')
                    row['physicalInfo']['powerRequirements'] = row.pop('powerRequirements')     # [req 3.1.6.10]

                # Gather list of all assetType values (information only)
                if row['assetType']:
                    if row['assetType'] not in all_asset_types:
                        all_asset_types.append(row['assetType'])

                #row['augmented'] = False
                #row['remoteDocuments'] = []
                #row['Ref Des'] = ref_des
                #row['coordinates'] = location
                #row['hasDeploymentEvent'] = has_deployment_event

            except Exception as err:
                # asset info error
                current_app.logger.info('asset info error' + str(err.message))
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Add new row to output dictionary
            if asset_id and ref_des:
                #row['augmented'] = True
                new_data.append(row)
                # if new item for dictionary of asset ids, add id with value of reference designator
                if asset_id not in dict_asset_ids:
                    dict_asset_ids[asset_id] = ref_des
                    update_asset_rds_cache = True

        except Exception as err:
            current_app.logger.info(str(err))
            continue

    # If reference designators with missing deployment(s), log sorted by reference designator.
    if all_no_deployments_dict:
        the_keys = all_no_deployments_dict.keys()
        the_keys.sort()

        # Display reference designators with missing deployment(s), sorted by reference designator.
        for key in the_keys:
            all_no_deployments_message += '\n%s: %s' % (key, all_no_deployments_dict[key])
        missing_deployment_message = no_deployments_title + all_no_deployments_message
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
                asset_rds_cache_update(dict_asset_ids)

        update_bad_asset_list(bad_data)

    return new_data, dict_asset_ids


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
    try:
        print '\n Compiling assets...\n'
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
        data, asset_rds = _compile_assets(result, compile_all=True)
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

        print '\n Completed compiling assets...\n'
        return data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get stream_list.
def get_stream_list():
    """ [Used by verify_cache.] Get 'stream_list' from cache; if not cached, get and set cache.
    """
    stream_list = None
    try:
        stream_list_cached = cache.get('stream_list')
        if not stream_list_cached:
            try:
                stream_list = dfs_streams()
            except Exception as err:
                message = str(err)
                raise Exception(message)

            if stream_list:
                cache.set('stream_list', stream_list, timeout=CACHE_TIMEOUT)
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


# Get all assets from uframe.
def get_assets_from_uframe():
    """ Get all assets from uframe.
    """
    time = True
    try:
        # Get uframe connect and timeout information
        if time: print '\n-- Getting assets from uframe... '
        start = dt.datetime.now()
        if time: print '\n-- Start time: ', start
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        timeout_extended = timeout_read * 2
        url = '/'.join([uframe_url, get_assets_url_base()])
        response = requests.get(url, timeout=(timeout, timeout_extended))
        end = dt.datetime.now()
        if time: print '\n-- End time:   ', end
        if time: print '\n-- Time to get uframe assets: %s' % str(end - start)
        if response.status_code != 200:
            message = '(%d) Failed to get uframe assets.' % response.status_code
            raise Exception(message)
        result = response.json()
        print '\n-- Number of assets fom uframe: ', len(result)
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe assets.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe assets.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise


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


def _get_asset(id):
    """ Get an asset by asset uid.

    This function is used by routes:
        /uframe/assets/<int:id>
        /uframe/assets/uid/<string:uid>
    """
    asset = {}
    try:
        if id == 0:
            message = 'Zero (0) is an invalid asset id value.'
            raise Exception(message)

        assets_dict = cache.get('assets_dict')
        if assets_dict is not None:
            if id in assets_dict:
                asset = assets_dict[id]
        else:
            uframe_url, timeout, timeout_read = get_uframe_assets_info()
            url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
            payload = requests.get(url, timeout=(timeout, timeout_read))
            if payload.status_code != 200:
                message = 'Unable to locate an asset with an id of %d.' % id
                raise Exception(message)
            data = payload.json()
            if data:
                data_list = [data]
                result, _ = _compile_assets(data_list)
                if result:
                    asset = result[0]

        return asset
    except ConnectionError:
        message = 'Error: ConnectionError getting asset with id %d from uframe.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting asset with id %d from uframe.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get asset from uframe by asset id.
def uframe_get_asset_by_id(id):
    """ Get asset from uframe by asset id.
    """
    try:
        # Get uframe asset
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if payload.status_code != 200:
            message = 'Failed to get asset (id: %d) from uframe.' % id
            current_app.logger.info(message)
            raise Exception(message)
        asset = payload.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting asset (id: %d) from uframe.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (id: %d) from uframe.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get asset from uframe by asset uid.
def uframe_get_asset_by_uid(uid):
    """ Get asset from uframe by asset uid.
    """
    check = False
    try:
        # Get uframe asset by uid.
        query = '?uid=' + uid
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base()])
        url += query
        if check: print '\n check -- [uframe_get_asset_by_uid] url to get asset %s: %s' % (uid, url)
        response = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if response.status_code == 204:
            message = 'Failed to receive content from uframe for asset with uid \'%s\'.' % uid
            raise Exception(message)
        elif response.status_code != 200:
            message = 'Failed to get asset from uframe with uid: \'%s\'.' % uid
            raise Exception(message)
        asset = response.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting asset (uid %s) from uframe.' % uid
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (uid %s) from uframe.' % uid
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get asset from uframe by asset uid.
def uframe_get_remote_resource_by_id(id):
    """ Get asset from uframe by asset uid.
    """
    check = False
    try:
        # Get uframe asset by uid.
        uframe_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([uframe_url, str(id)])
        if check: print '\n check -- [uframe_get_remote_resource_by_id] url to get remote resource %d: %s' % (id, url)
        response = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if response.status_code == 204:
            message = 'Failed to receive content from uframe for remote resource with id \'%d\'.' % id
            raise Exception(message)
        elif response.status_code != 200:
            message = 'Failed to get asset from uframe with uid: \'%s\'.' % uid
            raise Exception(message)
        asset = response.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting remote resource (uid %d) from uframe.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting remote resource (uid %d) from uframe.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _get_rd_assets():
    """ Get 'rd_assets', if not available get and set cache; return 'rd_assets' dictionary.
    """
    from ooiservices.app.uframe.deployment_tools import _compile_rd_assets
    rd_assets = {}
    try:
        # Get 'rd_assets' if cached
        rd_assets_cached = cache.get('rd_assets')
        if rd_assets_cached:
            rd_assets = rd_assets_cached

        # Get 'rd_assets' - compile them
        else:
            try:
                rd_assets = _compile_rd_assets()
            except Exception as err:
                message = 'Error processing _compile_rd_assets: ', err.message
                current_app.logger.warning(message)

            # Cache rd_assets
            if rd_assets:
                cache.set('rd_assets', rd_assets, timeout=CACHE_TIMEOUT)

        return rd_assets

    except Exception as err:
        message = 'Exception processing _get_rd_assets: %s' % str(err)
        current_app.logger.info(message)
        return {}


def _get_asset_from_assets_dict(id):
    """ Get 'assets_dict', if not available get and set cache; return 'assets_dict' dictionary.
    """
    asset = None
    try:
        # Get 'assets_dict' if cached
        cached = cache.get('assets_dict')
        if cached:
            assets_dict = cached

        # Get 'assets_dict' - compile them
        else:
            # Could use asset list (if available): populate_assets_dict(data), better than verify cache?
            # print '\n debug -- assets_dict not available, verify_cache...'
            verify_cache()
            assets_dict = cache.get('assets_dict')

        if id in assets_dict:
            asset = assets_dict[id]
        return asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_asset_rds_cache():
    asset_rds = None
    try:
        cached = cache.get('asset_rds')
        if cached:
            asset_rds = cached
        else:
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                raise Exception(message)
            # Cache rd_assets
            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
        return asset_rds

    except Exception as err:
        message = str(err)
        raise Exception(message)


def asset_rds_cache_update(dict_asset_ids):
    if dict_asset_ids:
        cache.set('asset_rds', dict_asset_ids, timeout=CACHE_TIMEOUT)


def update_bad_asset_list(bad_data):
    # Update cache for 'bad_asset_list'
    bad_assets_cached = cache.get('bad_asset_list')
    if bad_assets_cached:
        cache.delete('bad_asset_list')
        cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)
    else:
        cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)


def format_asset_for_ui(modified_asset):
    """ Format uframe asset into ui asset.
    """
    try:
        # Process remoteResources list.
        remoteResources = None
        if  'remoteResources' in modified_asset:
            remoteResources = modified_asset['remoteResources']
        if remoteResources is not None:
            modified_asset['remoteResources'] = post_process_remote_resources(remoteResources)

        # Prepare and convert asset.
        data_list = [modified_asset]
        try:
            asset_with_update, _ = _compile_assets(data_list)
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


def update_asset_cache(id, asset):
    try:
        # Update asset cache ('asset_list')
        asset_cache = cache.get('asset_list')
        if asset_cache:
            found_asset = False
            for item in asset_cache:
                if item['id'] == id:
                    item = asset
                    found_asset = True
                    break
            if found_asset:
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

        # Update assets_dict cache ('assets_dict')
        assets_dict_cache = cache.get('assets_dict')
        if assets_dict_cache:
            if id in assets_dict_cache:
                assets_dict_cache[id] = asset
                cache.set('assets_dict', assets_dict_cache, timeout=CACHE_TIMEOUT)

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get asset id using asset uid.
def _get_id_by_uid(uid):
    """ Get asset id using asset uid.
    """
    try:
        # Get uframe asset by uid.
        query = '?uid=' + uid
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base()])
        url += query
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if payload.status_code == 204:
            return None
        elif payload.status_code != 200:
            message = 'Failed to get asset with uid: \'%s\'.' % uid
            raise Exception(message)
        asset = payload.json()
        id = None
        if asset:
            if 'assetId' in asset:
                id = asset['assetId']
        return id
    except ConnectionError:
        message = 'ConnectionError getting asset (uid %s) from uframe. %s' % (uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (uid %s) from uframe. %s' % (uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# todo - Refactor for new asset management data model,
# todo - used by controller.py: get_svg_plot and dfs_streams
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

def dump_dict(self, dict, debug=False):
        """
        Print dict if debug enabled.
        """
        if debug:
            print '\n --------------\n dictionary: %s' % json.dumps(dict, indent=4, sort_keys=True)

