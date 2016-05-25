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
import requests.exceptions, requests.adapters
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.main.errors import (bad_request)
#from ooiservices.app.main.alertsalarms_tools import get_uframe_assets_info, get_assets_dict_from_list


requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 172800


@api.route('/assets', methods=['GET'])
def get_assets(use_min=False, normal_data=False, reset=False):
    """
    Get list of all assets.  This method is cached for 1 hour.
    add in helped params to bypass the json response and minification

    Parameter 'augmented':
        Sample 'bad assets' route: http://localhost:4000/uframe/assets?augmented=false
    """
    debug = False
    try:
        # Get uframe connect and timeout information
        uframe_url, timeout, timeout_read = get_uframe_assets_info()

        # Get 'assets_dict' if cached
        dict_cached = cache.get('assets_dict')
        if dict_cached:
            assets_dict = dict_cached
            if debug: print '\n debug - have assets_dict payload (cached)...assets_dict(%d): ' % len(assets_dict)
        else:
            if debug: print '\n debug - assets_dict payload (not cached)...'

        # Get 'asset_list' if cached, else process uframe assets and cache
        cached = cache.get('asset_list')
        if cached and reset is not True:
            data = cached
            if debug: print '\n debug - have cached: ', len(data)
        else:
            if debug: print '\n debug - get assets payload...'
            data = get_assets_payload(uframe_url)

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % str(e)
        if debug: print '\n debug - error: ', error
        current_app.logger.info(error)
        return make_response(error, 500)
    except Exception as err:
        error = "Error:  %s" % str(err)
        current_app.logger.info(error)
        return make_response(error, 500)

    # Determine field to sort by, sort asset data (ooi-ui-services format)
    try:
        if request.args.get('sort') and request.args.get('sort') != "":
            sort_by = str(request.args.get('sort'))
        else:
            sort_by = 'ref_des'

        data = sorted(data, key=itemgetter(sort_by))

    except Exception as e:
        if debug: print '\n debug --- get_assets: exception on sorted: ', str(e)
        current_app.logger.info(str(e))
        pass

    # If using minimized as request.arg or use_min, then strip asset data
    if request.args.get('min') == 'True' or use_min is True:
        if debug: print '\n debug --- STEP 1.......................'
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

    if request.args.get('geoJSON') and request.args.get('geoJSON') != "":
        return_list = []
        unique = set()
        for obj in data:
            asset = {}

            if (len(obj['ref_des']) <= 14 and
                    'coordinates' in obj and
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
        if debug: print '\n debug --- search_set: ', search_set
        try:

            fields = ['name', 'longName', 'type', 'array', 'metaData', 'tense', 'events']

            # Limit by selection of 'recovered' or 'deployed'?
            if limit_by_tense:

                # Make asset result set (list), based on tense
                if debug: print '\n looking for tense: ', tense_value
                for item in data:
                    if 'tense' in item:
                        if item['tense']:
                            if (item['tense']).lower() == tense_value:
                                results.append(item)
                                continue

            # Not limited by tense, result set is all asset data
            else:
                results = data

            if debug:
                print '\n debug limit_by_tense: ', limit_by_tense
                print '\n debug -- len(results): ', len(results)
                print '\n debug -- search_set: ', search_set

            # If there are (1) assets to search, and (2) search set details provided
            if results and search_set:

                # for each item in the search set, refine list of assets by search term
                for subset in search_set:

                    subset_lower = subset.lower()
                    if debug: print '\n debug ------------ searching for: ', subset_lower

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

        except KeyError as e:
            message = 'Asset (get_assets) Search exception: %s' % str(e)
            if debug: print '\n debug -- ', message
            current_app.logger.info(str(e))
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
        message = str(err)
        current_app.logger.info(message)
        return False


def get_assets_payload(uframe_url):
    """ Get all assets from uframe, process in ooi-ui-services list of assets (asset_list) and
    assets_dict by (key) asset id. Update cache for asset_list and assets_dict.
    """
    debug = False
    try:
        url = '/'.join([uframe_url, 'assets'])
        payload = requests.get(url)
        if payload.status_code != 200:
            try:
                return jsonify({"assets": payload.json()}),\
                    payload.status_code
            except AttributeError:
                try:
                    return jsonify({"assets": 'Undefined response'}),\
                        payload.status_code
                except Exception as e:
                    error = "unhandled exception: %s. Line # %s" % (e, sys.exc_info()[2].tb_lineno)
                    current_app.logger.info(error)
                    return make_response(error, 500)

        result = payload.json()
        data, assets_dict = _compile_assets(result)
        if "error" not in data:
            cache.set('asset_list', data, timeout=CACHE_TIMEOUT)
            data = cache.get('asset_list')
            if debug:
                print '\n debug -- ************ (get_assets_payload) type(data): ', type(data)
                print '\n debug -- ************ (get_assets_payload) len(data): ', len(data)

        return data

    except Exception as e:
        error = "Error: Cannot connect to uframe.  %s" % str(e)
        current_app.logger.info(error)
        raise


def get_assets_from_uframe(uframe_url):
    try:
        payload = requests.get(uframe_url)
        if payload.status_code != 200:
            try:
                return jsonify({"assets": payload.json()}), payload.status_code
            except AttributeError:
                try:
                    return jsonify({"assets": 'Undefined response'}), payload.status_code
                except Exception as e:
                    error = "unhandled exception: %s. Line # %s" % (e, sys.exc_info()[2].tb_lineno)
                    current_app.logger.info(error)
                    return make_response(error, 500)

        result = payload.json()

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
    CE01ISSP-XX099-01-CTDPFJ999
    40.365,-70.7695
    Latitude: 40.2266
    Longitude: -70.8886

    """
    debug = False
    try:
        data = json.loads(request.data)
        if debug:
            print '\n debug --- request_data: ', json.dumps(data, indent=4, sort_keys=True)
            print '\n debug --- request_data.keys: ', data.keys()
            #raise Exception('manual speed bump here...')

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
            except Exception as err:
                raise

            if not compiled_data or compiled_data is None:
                raise Exception('_compile_assets returned empty or None result.')

            # Update asset cache ('asset_list')
            asset_cache = cache.get('asset_list')
            if asset_cache:
                if debug: print '\n debug -- Create asset - updating asset_list cache...'
                cache.delete('asset_list')
                asset_cache.append(compiled_data[0])
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
            else:
                if debug: print '\n debug -- Create asset - NOT updating asset_list cache...'
        else:
            return bad_request('Failed to create asset!')

        return response.text, response.status_code

    except ConnectionError:
        error = 'Error: ConnectionError during create asset.'
        current_app.logger.info(error)
        return bad_request(error)
    except Timeout:
        error = 'Error: Timeout during during create asset.'
        current_app.logger.info(error)
        return bad_request(error)
    except Exception as err:
        error = str(err)
        if debug: print '\n create asset exception: ', error
        current_app.logger.info(error)
        return bad_request(error)


def valid_create_asset_request_data(data):
    """ Validate request_data provides required fields to create an asset. Must have metaData with key 'Ref Des'.

    TODO: validate other required items are provided, see following list of keys (data[0].keys()):
    ['Ref Des', 'deployment_number', 'asset_class', u'purchaseAndDeliveryInfo', u'lastModifiedTimestamp',
    u'physicalInfo', u'manufactureInfo', 'hasDeploymentEvent', 'coordinates', 'id', 'tense', u'dataSource',
    u'remoteDocuments', 'events', 'ref_des', u'assetInfo', u'metaData']

    """
    debug = False
    try:
        if debug: print '\n debug --- (valid_create_asset_request_data) validated required fields...'

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

        if debug: print '\n debug -- rd: ', rd

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
    debug = False
    try:
        if debug: print '\n debug *************************************** Enter Update Asset........'
        data = json.loads(request.data)
        if debug:
            print '\n debug --- request_data: ', json.dumps(data, indent=4, sort_keys=True)
            print '\n debug --- request_data.keys: ', data.keys()
            #raise Exception('Update asset: manual speed bump here...')

        if 'asset_class' in data:
            if debug: print '\n debug --- asset_class: ', data['asset_class']
            data['@class'] = data.pop('asset_class')

        if debug:
            print '\n debug --- request data: ', json.dumps(data, indent=4, sort_keys=True)

        url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % ('assets', id)
        response = requests.put(url, data=json.dumps(data), headers=_uframe_headers())
        if response.status_code != 200:
            message = '(%d) Failed to update asset %d.' % (response.status_code, id)
            if debug: print '\n debug -- %s' % message
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
                message = 'error returned in \'asset_list\' cache; unable to update cache.'
                return bad_request(message)

            if asset_cache:
                if debug: print '\n debug -- have asset...'
                cache.delete('asset_list')
                for row in asset_cache:
                    if row['id'] == id:
                        row.update(compiled_data[0])
                        break
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

            else:
                if debug: print '\n debug -- Update asset - NOT updating asset_list cache...'

        if debug: print '\n debug *************************************** Exit Update Asset........'
        return response.text, response.status_code

    except ConnectionError:
        error = 'Error: ConnectionError during update asset request (id: %d)' % id
        current_app.logger.info(error)
        return bad_request(error)
    except Timeout:
        error = 'Error: Timeout during during update asset request (id: %d)' % id
        current_app.logger.info(error)
        return bad_request(error)
    except Exception as err:
        error = str(err)
        if debug: print '\n update asset exception: ', error
        current_app.logger.info(error)
        return bad_request(error)


@api.route('/assets/<int:id>', methods=['DELETE'])
def delete_asset(id):
    """ Delete an asset by id.
    """
    debug = False
    this_asset = ""
    try:
        if debug: print '\n debug --- Delete asset: ', id
        url = current_app.config['UFRAME_ASSETS_URL'] + '/assets/%s' % str(id)
        response = requests.delete(url, headers=_uframe_headers())

        asset_cache = cache.get('asset_list')
        if asset_cache:
            if debug: print '\n debug ---\t have asset_cache...'
            cache.delete('asset_list')
            for row in asset_cache:
                if row['id'] == id:
                    this_asset = row
                    break
            if this_asset:
                if debug: print '\n debug ---\t have this_asset...updating asset_list cache'
                cache.delete('asset_list')
                asset_cache.remove(this_asset)
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
            else:
                if debug: print '\n debug -- Did not locate requested asset; cannot delete asset (%d).' % id

        if debug: print '\n debug ---\t exit Delete asset...'
        return response.text, response.status_code

    except ConnectionError:
        error = 'Error: ConnectionError during delete asset.'
        current_app.logger.info(error)
        return bad_request(error)
    except Timeout:
        error = 'Error: Timeout during during delete asset.'
        current_app.logger.info(error)
        return bad_request(error)
    except Exception as err:
        error = str(err)
        if debug: print '\n delete asset exception: ', error
        current_app.logger.info(error)
        return bad_request(error)

# END Assets CRUD methods.

@api.route('/bad_assets', methods=['GET'])
def get_bad_assets():
    """ Get bad assets.
    """
    debug = False
    try:
        if debug: print '\n debug --- GET bad_assets.... '
        results = _get_bad_assets()
        if debug: print '\n debug -- len(bad assets): ', len(results)
        return jsonify({"assets": results})

    except ConnectionError:
        error = 'Error: ConnectionError during get bad assets.'
        current_app.logger.info(error)
        return bad_request(error)
    except Timeout:
        error = 'Error: Timeout during during get bad asset.'
        current_app.logger.info(error)
        return bad_request(error)
    except Exception as err:
        error = str(err)
        if debug: print '\n get bad asset exception: ', error
        current_app.logger.info(error)
        return bad_request(error)


@api.route('/all_assets', methods=['GET'])
def get_all_assets():
    """ Get bad assets.
    """
    debug = False
    try:
        if debug: print '\n debug --- GET all_assets.... '
        results = _get_all_assets()
        if debug: print '\n debug -- len(all assets): ', len(results)
        return jsonify({"assets": results})

    except ConnectionError:
        error = 'Error: ConnectionError during get bad assets.'
        current_app.logger.info(error)
        return bad_request(error)
    except Timeout:
        error = 'Error: Timeout during during get bad asset.'
        current_app.logger.info(error)
        return bad_request(error)
    except Exception as err:
        error = str(err)
        if debug: print '\n get bad asset exception: ', error
        current_app.logger.info(error)
        return bad_request(error)


def _get_bad_assets():
    """ Get all 'bad' assets (in ooi-ui-services format)
    """
    debug = False
    try:
        bad_asset_cache = cache.get('bad_asset_list')
        if bad_asset_cache:
            if debug: print '\n debug --- bad_assets cached.... '
            result_data = bad_asset_cache
        else:
            if debug: print '\n debug --- bad_assets NOT cached.... '
            url = current_app.config['UFRAME_ASSETS_URL'] + '/assets'
            data = get_assets_from_uframe(url)
            try:
                result_data = _compile_bad_assets(data)
                cache.set('bad_asset_list', result_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        return result_data

    except Exception as err:
        error = str(err)
        if debug: print '\n get bad asset exception: ', error
        raise


def _get_all_assets():
    """ Get all assets (complete or incomplete) (in ooi-ui-services format).
    """
    debug = False
    try:
        # Get 'good' assets
        asset_cache = cache.get('asset_list')
        if asset_cache:
            if debug: print '\n debug --- assets cached.... '
            asset_data = asset_cache
        else:
            if debug: print '\n debug --- assets NOT cached.... '
            url = current_app.config['UFRAME_ASSETS_URL']
            try:
                asset_data = get_assets_payload(url)
                cache.set('asset_list', asset_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        if debug: print '\n debug -- len(asset_data): ', len(asset_data)

        # Get 'bad' assets
        bad_asset_cache = cache.get('bad_asset_list')
        if bad_asset_cache:
            if debug: print '\n debug --- bad_assets cached.... '
            bad_asset_data = bad_asset_cache
        else:
            if debug: print '\n debug --- bad_assets NOT cached.... '
            url = current_app.config['UFRAME_ASSETS_URL'] + '/assets'
            data = get_assets_from_uframe(url)
            try:
                bad_asset_data = _compile_bad_assets(data)
                cache.set('bad_asset_list', bad_asset_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        if debug: print '\n debug -- len(bad_asset_data): ', len(bad_asset_data)

        result_data = asset_data + bad_asset_data
        if result_data:
            result_data.sort()
        return result_data

    except Exception as err:
        error = str(err)
        if debug: print '\n get bad asset exception: ', error
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
