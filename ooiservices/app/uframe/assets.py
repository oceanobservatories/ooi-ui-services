from flask import request, jsonify, make_response, current_app
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.assetController import _compile_assets, _compile_bad_assets
from ooiservices.app.uframe.assetController import _uframe_headers
from ooiservices.app import cache
from operator import itemgetter
from copy import deepcopy

import json
import sys
import requests
import requests.exceptions
import requests.adapters
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.main.errors import (bad_request, internal_server_error)


requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 172800


@api.route('/assets', methods=['GET'])
def get_assets(use_min=False, normal_data=False, reset=False):
    """ Get list of all qualified assets.
    """
    debug = False
    try:
        # Get 'assets_dict' if cached
        dict_cached = cache.get('assets_dict')
        if dict_cached:
            assets_dict = dict_cached

        # Get 'asset_list' if cached, else process uframe assets and cache
        cached = cache.get('asset_list')
        if cached and reset is not True:
            data = cached
        else:
            data = get_assets_payload()

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
        return_list = []
        unique = set()
        for obj in data:
            asset = {}

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

                    json = {
                            'array_id': asset['assetInfo']['refDes'][:2],
                            'display_name': asset['assetInfo']['longName'],
                            'geo_location': {
                                'coordinates': [
                                    round(asset['coordinates'][0], 4),
                                    round(asset['coordinates'][1], 4)
                                    ],
                                'depth': asset['assetInfo']['depth'] or None
                                },
                            'reference_designator': asset['assetInfo']['refDes']
                            }
                    return_list.append(json)

        data = return_list


    # Search for each search item...two tiered search
    # - First get search result set: (a) all or (b) limited by tense ('Recovered' or 'Deployed')
    # - Second using first result set, search for additional search details.
    results = None
    if request.args.get('search') and request.args.get('search') != "":
        results = []
        return_list = []
        ven_subset = []
        search_term = str(request.args.get('search')).split()

        # Determine if result set to be limited by tense (either 'recovered' or 'deployed')
        limit_by_tense = False
        tense_value = None
        if 'past' in search_term or 'present' in search_term:
            limit_by_tense = True
            if 'past' in search_term:
                search_term.remove('past')
                tense_value = 'past'
            else:
                search_term.remove('present')
                tense_value = 'present'

        # Set detailed search set based on request.args provided for search
        # assetInfo_fields = ['name', 'longName', 'type', 'array']
        search_set = set(search_term)
        try:
            fields = ['name', 'longName', 'type', 'array', 'metaData', 'tense', 'events']

            # Limit by selection of 'recovered' or 'deployed'?
            if limit_by_tense:

                # Make asset result set (list), based on tense
                for item in data:
                    if 'tense' in item:
                        if item['tense']:
                            if (item['tense']).lower() == tense_value:
                                results.append(item)
                                continue

            # Not limited by tense, result set is all asset data
            else:
                results = data

            # If there are (1) assets to search, and (2) search set details provided
            if results and search_set:

                # for each item in the search set, refine list of assets by search term
                for subset in search_set:

                    subset_lower = subset.lower()
                    for item in results:

                        if 'ref_des' in item:
                            if match_subset(subset_lower, item['ref_des']):
                                return_list.append(item)
                                continue

                        for field in fields:
                            if field in item['assetInfo']:
                                if match_subset(subset_lower, item['assetInfo'][field]):
                                    return_list.append(item)
                                    break
                            else:
                                if match_subset(subset_lower, item[field]):
                                    return_list.append(item)
                                    break

                    results = return_list

        except KeyError as err:
            message = 'Asset search exception: %s' % str(err)
            if debug: print '\n debug -- ', message
            current_app.logger.info(message)
            pass

    # If search criteria used and results returned, use results as data
    if results is not None:
        data = results

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


def get_assets_payload():
    """ Get all assets from uframe, process in ooi-ui-services list of assets (asset_list) and
    assets_dict by (key) asset id. Update cache for asset_list and assets_dict.
    """
    try:
        # Get uframe connect and timeout information
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, 'assets'])
        payload = requests.get(url, timeout=(timeout, timeout_read))
        if payload.status_code != 200:
            message = '(%d) Failed to get uframe assets.' % payload.status
            current_app.logger.info(message)
            return internal_server_error(message)

        result = payload.json()
        data, assets_dict = _compile_assets(result)
        if "error" not in data:
            cache.set('asset_list', data, timeout=CACHE_TIMEOUT)
            data = cache.get('asset_list')

        return data

    except requests.exceptions.ConnectionError as err:
        message = "ConnectionError getting uframe assets; %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except requests.exceptions.Timeout as err:
        message = "Timeout getting uframe assets;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error getting uframe assets; %s" % str(err)
        current_app.logger.info(message)
        raise


def get_assets_from_uframe():
    try:
        # Get uframe connect and timeout information
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, 'assets'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get uframe assets.' % response.status_code
            current_app.logger.info(message)
            return internal_server_error(message)

        result = response.json()

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
        error = "Error getting uframe assets.  %s" % str(err)
        current_app.logger.info(error)
        raise



@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    """ Get asset by id.
    Object response for the GET(id) request.  This response is NOT cached.
    """
    try:
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
                compiled_data, _ = _compile_assets(data_list)
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

@api.route('/bad_assets', methods=['GET'])
def get_bad_assets():
    """ Get bad assets.
    """
    try:
        results = _get_bad_assets()
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
# from alertalarms_tools.py
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
