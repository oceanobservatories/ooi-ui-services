from flask import request, jsonify, make_response, current_app
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.uframe.assetController import _compile_assets
from ooiservices.app.uframe.assetController import _uframe_headers
from ooiservices.app import cache
from operator import itemgetter
from copy import deepcopy

import json
import requests
import sys

requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 172800


@api.route('/assets', methods=['GET'])
def get_assets(use_min=False, normal_data=False):
    '''
    Listing GET request of all assets.  This method is cached for 1 hour.
    add in helped params to bypass the json response and minification
    '''
    try:
        cached = cache.get('asset_list')

        if cached:
            data = cached
        else:

            url = current_app.config['UFRAME_ASSETS_URL']\
                + '/%s' % ('assets')

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
                        return make_response(
                            "unhandled exception: %s.  Line # %s"
                            % (e, sys.exc_info()[2].tb_lineno), 500)

            data = payload.json()

            data = _compile_assets(data)

            if "error" not in data:
                cache.set('asset_list', data, timeout=CACHE_TIMEOUT)

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

    try:
        sort_by = ''
        if request.args.get('sort') and request.args.get('sort') != "":
            sort_by = request.args.get('sort')
        else:
            sort_by = 'ref_des'
        data = sorted(data, key=itemgetter(sort_by))

    except Exception as e:
        print e
        pass

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
                    if showDeployments:
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
            except Exception:
                raise

    if request.args.get('search') and request.args.get('search') != "":
        return_list = []
        search_term = str(request.args.get('search')).split()
        search_set = set(search_term)
        for subset in search_set:
            if len(return_list) > 0:
                ven_subset = []
                return_list = deepcopy(data)
                for item in return_list:
                    if subset.lower() in\
                            str(item['assetInfo']['name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in\
                            str(item['assetInfo']['longName']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in\
                            str(item['ref_des']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in\
                            str(item['assetInfo']['type']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in\
                            str(item['assetInfo']['array']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in\
                            str(item['events']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in\
                            str(item['metaData']).lower():
                        ven_subset.append(item)
                data = ven_subset
            else:
                for item in data:
                    if subset.lower() in\
                            str(item['assetInfo']['name']).lower():
                        return_list.append(item)
                    elif subset.lower() in\
                            str(item['assetInfo']['longName']).lower():
                        return_list.append(item)
                    elif subset.lower() in\
                            str(item['ref_des']).lower():
                        return_list.append(item)
                    elif subset.lower() in\
                            str(item['assetInfo']['type']).lower():
                        return_list.append(item)
                    elif subset.lower() in\
                            str(item['assetInfo']['array']).lower():
                        return_list.append(item)
                    elif subset.lower() in\
                            str(item['events']).lower():
                        return_list.append(item)
                    elif subset.lower() in\
                            str(item['metaData']).lower():
                        return_list.append(item)
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


@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    '''
    Object response for the GET(id) request.  This response is NOT cached.
    '''
    try:
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('assets', id)
        payload = requests.get(url)

        data = payload.json()
        data_list = []
        data_list.append(data)
        data = _compile_assets(data_list)
        return jsonify(**data[0])

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


@api.route('/assets/<int:id>/events', methods=['GET'])
def get_asset_events(id):
    try:
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s/%s' % ('assets', id, 'events')
        response = requests.get(url,
                                headers=_uframe_headers())
        data = response.json()
        for each in data:
            each['eventClass'] = each.pop('@class')
        return jsonify({'events': data})

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


@scope_required('asset_manager')
@auth.login_required
@api.route('/assets', methods=['POST'])
def create_asset():
    '''
    Create a new asset, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
    try:
        data = json.loads(request.data)
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s' % ('assets')

        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']

        if 'asset_class' in data:
            data['@class'] = data.pop('asset_class')

        response = requests.post(url,
                                 data=json.dumps(data),
                                 headers=_uframe_headers())

        if response.status_code == 201:
            json_response = json.loads(response.text)
            data['id'] = json_response['id']
            data_list = []
            data_list.append(data)
            data = _compile_assets(data_list)

            asset_cache = cache.get('asset_list')
            if asset_cache:
                cache.delete('asset_list')
                asset_cache.append(data[0])
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        return make_response(error, 500)


@scope_required('asset_manager')
@auth.login_required
@api.route('/assets/<int:id>', methods=['PUT'])
def update_asset(id):
    try:
        data = json.loads(request.data)
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('assets', id)
        response = requests.put(url,
                                data=json.dumps(data),
                                headers=_uframe_headers())

        if response.status_code == 200:
            asset_cache = cache.get('asset_list')
            data_list = []
            data_list.append(data)
            data = _compile_assets(data_list)
            if asset_cache:
                cache.delete('asset_list')
                for row in asset_cache:
                    if row['id'] == id:
                        row.update(data[0])

            if "error" not in asset_cache:
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


@scope_required('asset_manager')
@auth.login_required
@api.route('/assets/<int:id>', methods=['DELETE'])
def delete_asset(id):
    '''
    Delete an asset by providing the id
    '''
    thisAsset = ""
    try:
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('assets', id)
        response = requests.delete(url,
                                   headers=_uframe_headers())

        asset_cache = cache.get('asset_list')
        if asset_cache:
            cache.delete('asset_list')
            for row in asset_cache:
                if row['id'] == id:
                    thisAsset = row
            asset_cache.remove(thisAsset)
            cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)
'''
END Assets CRUD methods.
'''
