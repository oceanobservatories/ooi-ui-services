from flask import url_for, request, current_app, jsonify
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.uframe.UFrameAssetsCollection import UFrameAssetsCollection
from ooiservices.app.uframe.assetController import get_events_by_ref_des
from ooiservices.app.uframe.assetController import convert_lat_lon
from ooiservices.app.uframe.assetController import convert_date_time
from ooiservices.app.uframe.assetController import convert_water_depth
from ooiservices.app.uframe.assetController import associate_events
from ooiservices.app.main.routes import get_display_name_by_rd
from ooiservices.app import cache
from operator import itemgetter
from copy import deepcopy

import json
import requests

#Default number of times to retry the connection:
requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400
### ---------------------------------------------------------------------------
### BEGIN Assets CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
@api.route('/assets', methods=['GET'])
def get_assets():
    '''
    Listing GET request of all assets.  This method is cached for 1 hour.
    '''
    try:
        #Manually set up the cache
        cached = cache.get('asset_list')
        will_reset_cache = False
        if request.args.get('reset') == 'true':
            will_reset_cache = True

        will_reset = request.args.get('reset')
        if cached and not(will_reset_cache):
            data = cached
        else:
            uframe_obj = UFrameAssetsCollection()
            data = uframe_obj.to_json()
            for row in data:
                lat = ""
                lon = ""
                ref_des = ""
                deployment_number = ""
                try:
                    row['id'] = row.pop('assetId')
                    row['asset_class'] = row.pop('@class')
                    row['events'] = associate_events(row['id'])
                    if row['metaData'] is not None:
                        for meta_data in row['metaData']:
                            if meta_data['key'] == 'Laditude ':
                                meta_data['key'] = 'Latitude'
                            if meta_data['key'] == 'Latitude':
                                lat = meta_data['value']
                                coord = convert_lat_lon(lat,"")
                                meta_data['value'] = coord[0]
                            if meta_data['key'] == 'Longitude':
                                lon = meta_data['value']
                                coord = convert_lat_lon("",lon)
                                meta_data['value'] = coord[1]
                            if meta_data['key'] == 'Ref Des SN':
                                meta_data['key'] = 'Ref Des'
                            if meta_data['key'] == 'Ref Des':
                                ref_des = meta_data['value']
                            if meta_data['key'] == 'Deployment Number':
                                deployment_number = meta_data['value']
                        row['ref_des'] = ref_des

                        if deployment_number is not None:
                            row['deployment_number'] = deployment_number
                        if lat > 0 and lon > 0:
                            row['coordinates'] = convert_lat_lon(lat, lon)
                        else:
                            for events in row['events']:
                                if events['locationLonLat'] is not None:
                                    lat = events['locationLonLat'][1]
                                    lon = events['locationLonLat'][0]
                            row['coordinates'] = convert_lat_lon(lat,lon)
                            lat = 0.0
                            lon = 0.0
                        if len(ref_des) > 0:
                            # determine the asset name from the DB if there is none.

                            try:
                                if (row['assetInfo']['name'] == None) or (row['assetInfo']['name'] == ""):
                                    row['assetInfo']['name'] = get_display_name_by_rd(ref_des)
                            except:
                                pass

                except AttributeError, TypeError:
                    pass

            if "error" not in data:
                cache.set('asset_list', data, timeout=CACHE_TIMEOUT)

        try:
            if request.args.get('sort') and request.args.get('sort') != "":
                sort_by = request.args.get('sort')
                if not(sort_by):
                    sort_by = 'ref_des'
                data = sorted(data, key=itemgetter(sort_by))

        except Exception as e:
            print e
            pass

        if request.args.get('min') == 'True':
            for obj in data:
                try:
                    del obj['metaData']
                    del obj['events']
                    del obj['manufactureInfo']
                    del obj['notes']
                    del obj['physicalInfo']
                    del obj['attachments']
                    del obj['purchaseAndDeliveryInfo']
                    del obj['lastModifiedTimestamp']
                except TypeError, KeyError:
                    print "could not delete one or more elements"
                    pass

        if request.args.get('search') and request.args.get('search') != "":
            return_list = []
            ven_set = []
            search_term = str(request.args.get('search')).split()
            search_set = set(search_term)
            for subset in search_set:
                if len(return_list) > 0:
                    if len(ven_set) > 0:
                        ven_set = deepcopy(ven_subset)
                    else:
                        ven_set = deepcopy(return_list)
                    ven_subset = []
                    for item in return_list:
                        if subset.lower() in str(item['assetInfo']['name']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['ref_des']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['assetInfo']['type']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['events']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['metaData']).lower():
                            ven_subset.append(item)
                    data = ven_subset
                else:
                    for item in data:
                        if subset.lower() in str(item['assetInfo']['name']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['ref_des']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['assetInfo']['type']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['events']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['metaData']).lower():
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
            result = jsonify({ 'assets' : data })
            return result

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Read (object)
@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    '''
    Object response for the GET(id) request.  This response is NOT cached.
    '''
    lat = ""
    lon = ""
    ref_des = ""
    try:
        uframe_obj = UFrameAssetsCollection()
        payload = uframe_obj.to_json(id)
        data = payload.data
        if payload.status_code != 200:
            return  jsonify({ "assets" : payload.data}), payload.status_code

        deployment_number = None
        data['events'] = associate_events(id)
        data['asset_class'] = data.pop('@class')
        data['id'] = data['assetId']

        if data['metaData'] is not None:
            for meta_data in data['metaData']:
                if meta_data['key'] == 'Laditude ':
                    meta_data['key'] = 'Latitude'
                if meta_data['key'] == 'Latitude':
                    lat = meta_data['value']
                    coord = convert_lat_lon(lat,"")
                    meta_data['value'] = coord[0]
                if meta_data['key'] == 'Longitude':
                    lon = meta_data['value']
                    coord = convert_lat_lon("",lon)
                    meta_data['value'] = coord[1]
                if meta_data['key'] == 'Ref Des SN':
                    meta_data['key'] = 'Ref Des'
                if meta_data['key'] == 'Ref Des':
                    ref_des = meta_data['value']
                if meta_data['key'] == 'Deployment Number':
                    deployment_number = meta_data['value']
            data['ref_des'] = ref_des
            if deployment_number is not None:
                data['deployment_number'] = deployment_number
            if lat > 0 and lon > 0:
                data['coordinates'] = convert_lat_lon(lat, lon)
                lat = ""
                lon = ""
            else:
                for events in data['events']:
                    if events['locationLonLat'] is not None:
                        lat = events['locationLonLat'][1]
                        lon = events['locationLonLat'][0]
                data['coordinates'] = convert_lat_lon(lat,lon)
                lat = 0.0
                lon = 0.0
            if len(ref_des) > 0:
                '''
                Determine the asset name from the DB if there is none.
                '''

                try:
                    if data['assetInfo']['name'] == None:
                        data['assetInfo']['name'] = get_display_name_by_rd(ref_des)
                except:
                    pass

        return jsonify(**data)

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Create
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
        uframe_obj = UFrameAssetsCollection()
        post_body = uframe_obj.from_json(data)
        post_body.pop('assetId')
        #post_body.pop('metaData')
        post_body.pop('lastModifiedTimestamp')
        post_body.pop('manufacturerInfo')
        post_body.pop('attachments')
        post_body.pop('classCode')
        post_body.pop('seriesClassification')
        post_body.pop('purchaseAndDeliveryInfo')
        #return json.dumps(post_body)
        uframe_assets_url = _uframe_url(uframe_obj.__endpoint__)
        #return uframe_assets_url
        response = requests.post(uframe_assets_url, data=json.dumps(post_body), headers=_uframe_headers())
        if response.status_code == 201:
            json_response = json.loads(response.text)
            data['id'] = json_response['id']
            asset_cache = cache.get('asset_list')
            cache.delete('asset_list')
            if asset_cache:
                asset_cache.append(data)
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Update
@auth.login_required
@api.route('/assets/<int:id>', methods=['PUT'])
def update_asset(id):
    '''
    Update an existing asset, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
    try:
        data = json.loads(request.data)
        uframe_obj = UFrameAssetsCollection()
        put_body = uframe_obj.from_json(data)
        uframe_assets_url = _uframe_url(uframe_obj.__endpoint__, id)
        response = requests.put(uframe_assets_url, data=json.dumps(put_body), headers=_uframe_headers())
        if response.status_code == 200:
            asset_cache = cache.get('asset_list')
            cache.delete('asset_list')
            if asset_cache:
                for row in asset_cache:
                    if row['id'] == id:
                        row.update(data)

            if "error" not in asset_cache:
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Delete
@auth.login_required
@api.route('/assets/<int:id>', methods=['DELETE'])
def delete_asset(id):
    '''
    Delete an asset by providing the id
    '''
    try:
        uframe_obj = UFrameAssetsCollection()
        uframe_assets_url = _uframe_url(uframe_obj.__endpoint__, id)
        response = requests.delete(uframe_assets_url, headers=_uframe_headers())
        if response.status_code == 200:
            asset_cache = cache.get('asset_list')
            cache.delete('asset_list')
            if asset_cache:
                for row in asset_cache:
                    if row['id'] == id:
                       thisAsset = row
                asset_cache.remove(thisAsset)

            if "error" not in asset_cache:
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

### ---------------------------------------------------------------------------
### END Assets CRUD methods.
### ---------------------------------------------------------------------------
