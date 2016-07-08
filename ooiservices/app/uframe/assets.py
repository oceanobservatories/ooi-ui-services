from flask import request, jsonify, make_response, current_app
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.assetController import _compile_assets, _compile_bad_assets
from ooiservices.app.uframe.assetController import _uframe_headers
from ooiservices.app.main.alertsalarms_tools import get_assets_dict_from_list
from ooiservices.app.main.alertsalarms_tools import _compile_rd_assets, _get_rd_assets
from ooiservices.app import cache
from operator import itemgetter
from copy import deepcopy
from ooiservices.app.uframe.vocab import get_vocab, get_display_name_by_rd
from ooiservices.app.main.alertsalarms_tools import _compile_asset_rds
import json
import sys
import requests
import requests.exceptions
import requests.adapters
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.main.errors import (bad_request, internal_server_error)
import datetime as dt


requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 172800


@api.route('/assets', methods=['GET'])
def get_assets(use_min=False, normal_data=False, reset=False):
    """ Get list of all qualified assets.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered get_assets...'
        # Get 'assets_dict' if cached
        dict_cached = cache.get('assets_dict')
        if dict_cached:
            assets_dict = dict_cached
        else:
            if debug: print '\n debug -- assets_dict not cached...'

        # Get 'asset_list' if cached, else process uframe assets and cache
        if debug: print '\n debug -- Get cached assets_list or fetch and cache...'
        cached = cache.get('asset_list')
        if cached: # and reset is not True:
            if debug: print '\n debug -- assets_list is cached...'
            data = cached
        else:
            if debug: print '\n debug -- get_assets_payload...'
            data = get_assets_payload()
            if not data:
                message = 'No asset data returned from uframe.'
                current_app.logger.info(message)
                return internal_server_error(message)

    except ConnectionError as err:
        message = "ConnectionError getting uframe assets; %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout getting uframe assets;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return internal_server_error(message)

    # Determine field to sort by, sort asset data (ooi-ui-services format)
    try:
        if request.args.get('sort') and request.args.get('sort') != "":
            sort_by = str(request.args.get('sort'))
        else:
            sort_by = 'ref_des'
        data = sorted(data, key=itemgetter(sort_by))
    except Exception as err:
        current_app.logger.info(str(err))
        pass

    # If using minimized ('min') or use_min, then strip asset data
    if request.args.get('min') == 'True' or use_min is True:
        showDeployments = False
        deploymentEvents = []
        if request.args.get('deployments') == 'True':
            showDeployments = True
        for obj in data:
            try:
                # todo - update and remove if blocks which no longer apply with new assets
                if 'metaData' in obj:
                    del obj['metaData']
                if 'events' in obj:
                    if showDeployments and obj['events'] is not None:
                        for event in obj['events']:
                            if event['eventClass'] == '.DeploymentEvent':
                                deploymentEvents.append(event)
                        del obj['events']
                        obj['events'] = deploymentEvents
                        deploymentEvents = []
                    else:
                        del obj['events']
                if 'manufactureInfo' in obj:
                    del obj['manufactureInfo']
                if 'notes' in obj:
                    del obj['notes']
                if 'physicalInfo' in obj:
                    del obj['physicalInfo']
                if 'attachments' in obj:
                    del obj['attachments']
                if 'purchaseAndDeliveryInfo' in obj:
                    del obj['purchaseAndDeliveryInfo']
                if 'lastModifiedTimestamp' in obj:
                    del obj['lastModifiedTimestamp']
            except Exception as err:
                if debug: print '\n (assets) exception: ', str(err)
                current_app.logger.info(str(err))
                raise

    """
    # Create toc information using geoJSON=true
    # Sample
    # request: http://localhost:4000/uframe/assets?geoJSON=true
    # response: (list of dicts for {mooring | platform}
        {
          "assets": [
            {
              "array_id": "CE",
              "display_name": "Endurance OR Inshore Surface Mooring  ",
              "geo_location": {
                "coordinates": [
                  44.6583,
                  -124.0956
                ],
                "depth": "25"
              },
              "reference_designator": "CE01ISSM"
            },
            . . .
    """
    if request.args.get('geoJSON') and request.args.get('geoJSON') != "":
        if debug: print '\n debug -- processing geoJSON request...'
        return_list = []
        unique = set()
        if debug:
            if not data:
                print '\n debug -- no assets to process.....'

        for obj in data:
            asset = {}
            """
            if (len(obj['ref_des']) <= 14 and 'coordinates' in obj and
                    obj['ref_des'] != "" and
                    obj['assetInfo']['longName'] != "" and
                    obj['assetInfo']['longName'] is not None):

                if (obj['ref_des'] not in unique):

                    unique.add(obj['ref_des'])
                    asset['assetInfo'] = obj.pop('assetInfo')
                    asset['assetInfo']['refDes'] = obj.pop('ref_des')
                    asset['coordinates'] = obj.pop('coordinates')

                    if 'depth' in obj:
                        asset['assetInfo']['depth'] = obj.pop('depth')
                    else:
                        asset['assetInfo']['depth'] = None

                    json = {
                            'array_id': asset['assetInfo']['refDes'][:2],
                            'display_name': asset['assetInfo']['longName'],
                            'geo_location': {
                                'coordinates': [
                                    round(asset['coordinates'][0], 4),
                                    round(asset['coordinates'][1], 4)
                                    ],
                                'depth': asset['assetInfo']['depth']
                                },
                            'reference_designator': asset['assetInfo']['refDes']
                            }
                    return_list.append(json)
            """
            if debug: print '\n debug -- ref_des: ', obj['ref_des']
            if (len(obj['ref_des']) <= 14 and 'coordinates' in obj):

                if debug: print '\n debug -- unique: ', unique
                if (obj['ref_des'] not in unique):

                    if debug: print '\n step 1...'
                    unique.add(obj['ref_des'])
                    asset['assetInfo'] = obj.pop('assetInfo')
                    asset['assetInfo']['refDes'] = obj.pop('ref_des')
                    if debug: print '\n step 2...'
                    asset['coordinates'] = obj.pop('coordinates')
                    if 'depth' in obj:
                        asset['assetInfo']['depth'] = obj.pop('depth')
                    else:
                        asset['assetInfo']['depth'] = None
                    if debug: print '\n step 3...'
                    # Get display name
                    name = asset['assetInfo']['name']
                    if not name or name is None:
                        name = get_display_name_by_rd(asset['assetInfo']['refDes'])
                        if name is None:
                            name = asset['assetInfo']['refDes']
                    if debug: print '\n step 4...'
                    json = {
                            'array_id': asset['assetInfo']['refDes'][:2],
                            'display_name': name,
                            'geo_location': {
                                'coordinates': [
                                    round(asset['coordinates'][0], 4),
                                    round(asset['coordinates'][1], 4)
                                    ],
                                'depth': asset['assetInfo']['depth']
                                },
                            'reference_designator': asset['assetInfo']['refDes']
                            }
                    if debug: print '\n step 5...'
                    return_list.append(json)

        data = return_list

    if request.args.get('startAt'):
        start_at = int(request.args.get('startAt'))
        count = int(request.args.get('count'))
        total = int(len(data))
        data_slice = data[start_at:(start_at + count)]
        result = jsonify({"count": count,
                          "total": total,
                          "startAt": start_at,
                          "assets": data_slice})
        return result
    else:
        if normal_data:
            result = data
        else:
            result = jsonify({'assets': data})
        return result

"""
def match_subset(subset, value):
    result = False
    try:
        if not value or value is None:
            return False
        if subset in (str(value).lower()):
            result = True
        return result

    except Exception as err:
        current_app.logger.info(str(err))
        return False
"""

def get_assets_payload():
    """ Get all assets from uframe, process in ooi-ui-services list of assets (asset_list) and
    assets_dict by (key) asset id. Update cache for asset_list and assets_dict.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered get_assets_payload...'
        # Get uframe connect and timeout information
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, 'asset'])
        if debug: print '\n debug -- url: ', url
        if debug: print '\n debug -- Start Time: ', dt.datetime.now()
        timeout_extended = timeout_read * 40
        payload = requests.get(url, timeout=(timeout, timeout_extended))
        if debug: print '\n debug -- End Time: ', dt.datetime.now()
        if payload.status_code != 200:
            message = '(%d) Failed to get uframe assets.' % payload.status
            if debug: print '\n debug -- uframe error getting assets...', message
            current_app.logger.info(message)
            return Exception(message)

        result = payload.json()
        if debug: print '\n\t debug -- number of uframe assets: %d' % len(result)
        if not result:
            message = 'Response content from uframe asset request is empty.'
            current_app.logger.info(message)
            raise Exception(message)

        # Process uframe assets for UI and cache 'asset_list'
        if debug: print '\n\t debug -- _compile_assets...'
        data, assets_dict = _compile_assets(result)
        if "error" not in data:
            if debug: print '\n\t debug -- set \'asset_list\' cache...'
            cache.set('asset_list', data, timeout=CACHE_TIMEOUT)
            data = cache.get('asset_list')
        else:
            if debug: print '\n\t debug -- error setting asset_list cache...'

        # Cache 'assets_dict' (based on success of _compile_assets returning assets)
        if debug: print '\n\t debug -- get_assets_dict_from_list...'
        assets_dict = get_assets_dict_from_list(data)
        if not assets_dict:
            message = 'Warning: get_assets_dict_from_list returned empty assets_dict.'
            if debug: print '\n debug -- message: ', message
            current_app.logger.info(message)
        if isinstance(assets_dict, dict):
            cache.set('assets_dict', assets_dict, timeout=CACHE_TIMEOUT)
            if debug: print "[+] Assets dictionary cache reset..."
        else:
            if debug: print "[-] Error in Assets dictionary cache update....."

        # Get 'rd_assets' cache; if not cache then get and cache
        if debug: print '\n\t debug -- _get_rd_assets...'
        rd_assets = _get_rd_assets()

        return data

    except ConnectionError as err:
        message = "ConnectionError getting uframe assets; %s" % str(err)
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = "Timeout getting uframe assets;  %s" % str(err)
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = "Error getting uframe assets; %s" % str(err)
        current_app.logger.info(message)
        raise


def get_assets_from_uframe():
    debug = False
    try:
        if debug: print '\n debug -- entered get_assets_from_uframe...'
        # Get uframe connect and timeout information
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, 'asset'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get uframe asset.' % response.status_code
            current_app.logger.info(message)
            #return internal_server_error(message)
            raise Exception(message)

        result = response.json()

        return result
    except ConnectionError:
        message = 'ConnectionError getting uframe asset.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe asset.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = "Error getting uframe asset.  %s" % str(err)
        current_app.logger.info(message)
        raise


# todo ======================================================
# todo - modify for new asset REST interface
@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    """ Get asset by id.
    Object response for the GET(id) request.  This response is NOT cached.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered get_asset...'
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        if id == 0:
            error = 'Zero (0) is an invalid asset id value.'
            current_app.logger.info(error)
            return make_response(error, 400)

        url = '/'.join([uframe_url, 'assets', str(id)])
        payload = requests.get(url, timeout=(timeout, timeout_read))
        if payload.status_code != 200:
            error = 'Unable to locate an asset with an id of %d.' % id
            current_app.logger.info(error)
            return make_response(error, 400)
        data = payload.json()
        data_list = [data]
        result, _ = _compile_assets(data_list)
        return jsonify(**result[0])

    except ConnectionError:
        error = 'Error: ConnectionError during GET request for asset with id %d.' % id
        current_app.logger.info(error)
        return bad_request(error)
    except Timeout:
        error = 'Error: Timeout during GET request for asset with id %d.' % id
        current_app.logger.info(error)
        return bad_request(error)
    except Exception as err:
        error = 'Error processing GET request for asset with id %d. %s' % (id, str(err))
        current_app.logger.info(error)
        return bad_request(error)


# todo ======================================================
# todo - modify for new asset REST interface
@api.route('/assets/<int:id>/events', methods=['GET'])
def get_asset_events(id):
    """ Get events for asset id.
    """
    try:
        if id == 0:
            error = 'Zero (0) is an invalid asset id value, unable to GET asset events without valid asset id.'
            current_app.logger.info(error)
            return bad_request(error)

        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = "/".join([uframe_url, 'assets', str(id), 'events'])
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=_uframe_headers())
        if payload.status_code != 200:
            error = '(%d) GET request failed for asset (id %d) events.' % (payload.status_code, id)
            current_app.logger.info(error)
            return bad_request(error)
        data = payload.json()
        for each in data:
            each['eventClass'] = each.pop('@class')
        return jsonify({'events': data})

    except ConnectionError:
        error = 'Error: ConnectionError during GET request for asset (id %d) events.' % id
        current_app.logger.info(error)
        return bad_request(error)
    except Timeout:
        error = 'Error: Timeout during GET request for asset (id %d) events.' % id
        current_app.logger.info(error)
        return bad_request(error)
    except Exception as err:
        error = 'Error processing GET request for asset (id %d) events. %s' % (id, str(err))
        current_app.logger.info(error)
        return bad_request(error)


# todo ======================================================
# todo - modify for new asset REST interface
@api.route('/assets', methods=['POST'])
def create_asset():
    """ Create a new asset, the return will be uframe asset format (not ooi-ui-services format).
    Cache ('asset_list') is updated with new asset
    Either a success or an error message.
    Login required.
    """
    debug = False
    try:
        data = json.loads(request.data)
        if valid_create_asset_request_data(data):
            if debug: print '\n debug validated required fields...'

        url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % 'assets'
        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']
        if 'asset_class' in data:
            data['@class'] = data.pop('asset_class')

        # Create asset in uframe
        response = requests.post(url, data=json.dumps(data), headers=_uframe_headers())

        if response.status_code == 201:
            json_response = json.loads(response.text)
            data['assetId'] = json_response['id']
            data['tense'] = 'NEW'
            data_list = [data]
            try:
                compiled_data, _ = _compile_assets(data_list)
            except Exception:
                raise

            if not compiled_data or compiled_data is None:
                raise Exception('_compile_assets returned empty or None result.')

            # Update asset cache ('asset_list')
            asset_cache = cache.get('asset_list')
            if asset_cache:
                cache.delete('asset_list')
                asset_cache.append(compiled_data[0])
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
        else:
            return bad_request('Failed to create asset!')

        return response.text, response.status_code

    except ConnectionError:
        message = 'ConnectionError during create asset.'
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Timeout during during create asset.'
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

# todo ======================================================
# todo - modify for new asset REST interface
'''
def valid_create_asset_request_data(data):
    """ Validate request_data provides required fields to create an asset. Must have metaData with key 'Ref Des'.

    TODO: validate other required items are provided, see following list of keys (data[0].keys()):
    ['Ref Des', 'deployment_number', 'asset_class', u'purchaseAndDeliveryInfo', u'lastModifiedTimestamp',
    u'physicalInfo', u'manufactureInfo', 'hasDeploymentEvent', 'coordinates', 'id', 'tense', u'dataSource',
    u'remoteDocuments', 'events', 'ref_des', u'assetInfo', u'metaData']

    """
    try:
        # Process reference designator (in metaData)
        if not 'metaData':
            message = 'Attribute \'metaData\' not provided in request data.'
            raise Exception(message)

        rd = None
        for item in data['metaData']:
            if item['key'] == 'Ref Des':
                rd = item['value']
                break

        if rd is None:
            message = 'Attribute \'Ref Des\' not provided, or empty, in request data (metaData).'
            raise Exception(message)

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise
'''

# todo ======================================================
# todo - modify for new asset REST interface
@api.route('/assets/<int:id>', methods=['PUT'])
def update_asset(id):
    """ Update asset by id.
    Last writer wins; new format of request.data to be handled (post 5/31):
        {"assetInfo.array":"EnduranceAss","assetInfo.assembly":"testass","oper":"edit","id":"227"}
    """
    try:
        data = json.loads(request.data)

        if 'asset_class' in data:
            data['@class'] = data.pop('asset_class')

        url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % ('assets', id)
        response = requests.put(url, data=json.dumps(data), headers=_uframe_headers())
        if response.status_code != 200:
            message = '(%d) Failed to update asset %d.' % (response.status_code, id)
            return bad_request(message)

        if response.status_code == 200:
            data_list = [data]
            try:
                compiled_data, asset_rds = _compile_assets(data_list)
            except Exception:
                raise

            if not compiled_data or compiled_data is None:
                raise Exception('_compile_assets returned empty or None result.')

            asset_cache = cache.get('asset_list')
            if "error" in asset_cache:
                message = 'Error returned in \'asset_list\' cache; unable to update cache.'
                return bad_request(message)

            if asset_cache:
                cache.delete('asset_list')
                for row in asset_cache:
                    if row['id'] == id:
                        row.update(compiled_data[0])
                        break
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

            # Cache assets_rd
            if asset_rds:
                asset_rds_cache = cache.get('asset_rds')
                if asset_rds_cache:
                    cache.delete('asset_rds')
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
                print "[+] Asset reference designators cache reset..."
                print '\n len(asset_rds): ', len(asset_rds)
            else:
                print "[-] Error in asset_rds cache update"

        return response.text, response.status_code

    except ConnectionError:
        message = 'Error: ConnectionError during update asset request (id: %d)' % id
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Error: Timeout during during update asset request (id: %d)' % id
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo ======================================================
# todo - modify for new asset REST interface
@api.route('/assets/<int:id>', methods=['DELETE'])
def delete_asset(id):
    """ Delete an asset by id.
    """
    this_asset = ""
    try:
        url = current_app.config['UFRAME_ASSETS_URL'] + '/assets/%s' % str(id)
        response = requests.delete(url, headers=_uframe_headers())

        asset_cache = cache.get('asset_list')
        if asset_cache:
            cache.delete('asset_list')
            for row in asset_cache:
                if row['id'] == id:
                    this_asset = row
                    break
            if this_asset:
                cache.delete('asset_list')
                asset_cache.remove(this_asset)
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

        return response.text, response.status_code

    except ConnectionError:
        message = 'ConnectionError during delete asset.'
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Timeout during during delete asset.'
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

# END Assets CRUD methods.

# todo ======================================================
# todo - test with new asset REST interface
@api.route('/bad_assets', methods=['GET'])
def get_bad_assets():
    """ Get bad assets.
    """
    debug = False
    try:
        results = _get_bad_assets()
        if debug: print '\n debug -- Number of bad assets: %d' % len(results)
        return jsonify({"assets": results})

    except ConnectionError:
        message = 'ConnectionError during get bad assets.'
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Timeout during during get bad asset.'
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

# todo ======================================================
# todo - test with new asset REST interface
@api.route('/all_assets', methods=['GET'])
def get_all_assets():
    """ Get bad assets.
    """
    try:
        results = _get_all_assets()
        return jsonify({"assets": results})

    except ConnectionError:
        message = 'ConnectionError during get bad assets.'
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Timeout during during get bad asset.'
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

# todo ======================================================
# todo - test with new asset REST interface
def _get_bad_assets():
    """ Get all 'bad' assets (in ooi-ui-services format)
    """
    try:
        bad_asset_cache = cache.get('bad_asset_list')
        if bad_asset_cache:
            result_data = bad_asset_cache
        else:
            data = get_assets_from_uframe()
            try:
                result_data = _compile_bad_assets(data)
                cache.set('bad_asset_list', result_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        return result_data

    except Exception as err:
        raise

# todo ======================================================
# todo - test with new asset REST interface
def _get_all_assets():
    """ Get all assets (complete or incomplete) (in ooi-ui-services format).
    """
    try:
        # Get 'good' assets
        asset_cache = cache.get('asset_list')
        if asset_cache:
            asset_data = asset_cache
        else:
            try:
                asset_data = get_assets_payload()
                cache.set('asset_list', asset_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        # Get 'bad' assets
        bad_asset_cache = cache.get('bad_asset_list')
        if bad_asset_cache:
            bad_asset_data = bad_asset_cache
        else:
            data = get_assets_from_uframe()
            try:
                bad_asset_data = _compile_bad_assets(data)
                cache.set('bad_asset_list', bad_asset_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        result_data = asset_data + bad_asset_data
        if result_data:
            result_data.sort()
        return result_data

    except Exception as err:
        raise


#=====================================================
def get_uframe_assets_info():
    """ Get uframe assets configuration information.
    """
    try:
        uframe_url = current_app.config['UFRAME_ASSETS_URL']
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_ASSETS_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)

#=====================================================
# Development only routes...
#=====================================================
# Development only route......
@api.route('/compile_asset_rds', methods=['GET'])
def dev_compile_asset_rds():
    """ Get dictionary of asset ids for reference designators.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered dev_compile_asset_rds...'
        # If no asset_rds cached, then fetch and cache
        asset_rds = {}
        rds_wo_assets = []
        try:
            asset_rds, rds_wo_assets = _compile_asset_rds()
        except Exception as err:
            message = 'Error processing _compile_asset_rds: ', err.message
            current_app.logger.warning(message)

        if debug: print '\n debug -- length of asset_rds: %d' % len(asset_rds)
        return jsonify(asset_rds), 200

    except Exception as err:
        message = 'Exception processing dev_compile_asset_rds: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Development only route......
@api.route('/assets_dict', methods=['GET'])
def dev_assets_dict():
    """ Get cached 'assets_dict', if not available generate cache and return 'assets_dict' dictionary. Does NOT cache.
    """
    debug = False
    assets_dict = {}
    try:
        if debug: print '\n debug -- entered dev_assets_dict...'
        # Get 'assets_dict' if cached
        dict_cached = cache.get('assets_dict')
        if dict_cached:
            assets_dict = dict_cached
        else:
            if debug: print '\n debug -- assets_dict not cached, get_asset_payload then check cache...'
            data = get_assets_payload()
            if not data:
                message = 'No asset data returned from uframe.'
                current_app.logger.info(message)
                return internal_server_error(message)
            dict_cached = cache.get('assets_dict')
            if dict_cached:
                assets_dict = dict_cached
            else:
                message = 'assets_dict STILL not cached. after calling get_assets_payload..'
                if debug: print '\n debug -- ', message
                return internal_server_error(message)

        if debug: print '\n debug -- Length of asset_dict: %d' % len(assets_dict)

        return jsonify(assets_dict), 200

    except Exception as err:
        message = 'Exception processing dev_assets_dict: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)

# Development only route......
@api.route('/get_asset_rds', methods=['GET'])
def dev_get_asset_rds():
    """ Get cached 'asset_rds' or generate 'asset_rds'. Does NOT cache.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered dev_get_asset_rds...'
        asset_rds = {}

        # Get 'asset_rds' if cached
        asset_rds_cached = cache.get('asset_rds')
        if asset_rds_cached:
            asset_rds = asset_rds_cached
        else:
            if debug: print '\n debug -- asset_rds not cached, compile_asset_rds then check cache...'
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

        if debug: print '\n debug -- Length of asset_rds: %d' % len(asset_rds)

        return jsonify(asset_rds), 200

    except Exception as err:
        message = 'Exception processing dev_get_asset_rds: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Development only route......
@api.route('/get_rd_assets', methods=['GET'])
def dev_get_rd_assets():
    """ Get cached 'rd_assets', if not available generate cache and return 'rd_assets' dictionary. Does NOT cache.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered dev_get_rd_assets...'
        rd_assets = {}

        # Get 'rd_assets' if cached
        rd_assets_cached = cache.get('rd_assets')
        if rd_assets_cached:
            rd_assets = rd_assets_cached

        # Get 'rd_assets' - compile them
        else:
            if debug: print '\n debug -- rd_assets not cached, get rd_assets, cache and then check cache...'
            try:
                rd_assets = _compile_rd_assets()
            except Exception as err:
                message = 'Error processing _compile_rd_assets: ', err.message
                current_app.logger.warning(message)

        if debug: print '\n debug -- Length of rd_assets: %d' % len(rd_assets)

        return jsonify(rd_assets), 200

    except Exception as err:
        message = 'Exception processing dev_get_rd_assets: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)

# Development only route......
@api.route('/_get_rd_assets', methods=['GET'])
def dev__get_rd_assets():
    """ Get cached 'rd_assets', if not available generate cache and return 'rd_assets' dictionary. This caches!!!.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered dev__get_rd_assets...'
        rd_assets = {}

        # Get 'rd_assets' if cached
        rd_assets_cached = cache.get('rd_assets')
        if rd_assets_cached:
            rd_assets = rd_assets_cached

        # Get 'rd_assets' - compile them
        else:
            if debug: print '\n debug -- rd_assets not cached, get rd_assets, cache and then check cache...'
            try:
                rd_assets = _compile_rd_assets()
            except Exception as err:
                message = '[dev route _get_rd_assets] Error processing _compile_rd_assets: ', err.message
                current_app.logger.warning(message)

            # Cache rd_assets, if not rd_assets to be cached, print error.
            if rd_assets:
                cache.set('rd_assets', rd_assets, timeout=CACHE_TIMEOUT)
                print "[+] Reference designators asset cache reset..."
            else:
                print "[-] Error in cache update"


        if debug: print '\n debug -- Length of rd_assets: %d' % len(rd_assets)

        return jsonify(rd_assets), 200

    except Exception as err:
        message = 'Exception processing dev__get_rd_assets: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)