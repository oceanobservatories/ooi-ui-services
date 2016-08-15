
"""
Asset routes and supporting functions.

Routes:
[GET]  /assets                 # Get all assets from uframe and reformat for UI; get single asset reformatted for UI
[GET]  /assets/types           # [dup] Get asset types used by those assets loaded into asset management display
[GET]  /assets/types/used      # [dup] Get asset types used by those assets loaded into asset management display
[GET]  /assets/types/uframe    # List of all asset types supported by uframe.
[GET]  /assets/<int:id>        # Get asset by asset id.
[Get]  /assets/uid/<string:uid># Get asset by asset uid.
[GET]  /assets/<int:id>/events # Get all events for an asset; option 'type' parameter provided for one or more types.
[PUT]  /assets/<int:id>        # Update an existing asset
[DELETE] /asset                # Deprecated.

"""
__author__ = 'Edna Donoughe'

# todo Remaining asset routes to be completed for new asset model and web services:
# todo [POST]  /assets           # Create an asset
# todo [GET]   /bad_assets       # Display assets (1) are type .XAsset or (2) which do not have a reference designator.
# todo [GET]   /all_assets       # Display results from /assets and /bad_assets

from flask import request, jsonify, current_app
from ooiservices.app.main.errors import (bad_request, internal_server_error)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.vocab import get_display_name_by_rd
from ooiservices.app.uframe.common_tools import get_supported_asset_types
from ooiservices.app.uframe.asset_tools import (_get_asset, verify_cache)
from ooiservices.app.uframe.assets_create_update import (_create_asset, _update_asset)
from ooiservices.app.uframe.event_tools import (_get_events_by_id, _get_id_by_uid)

# todo Review authentication and scope
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required

from operator import itemgetter
import json
import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)

CACHE_TIMEOUT = 172800


# Get assets.
# todo - add try/except
# todo - review use of attachments and asset management requirements.
# todo - modify for section for request.arg 'min' to reflect new asset management data model.
@api.route('/assets', methods=['GET'])
def get_assets(use_min=False, normal_data=False, reset=False):
    """ Get list of all uframe assets, filtered by criteria below, and formatted for UI display.
        Criteria for an asset to be included in response:
            (1) have an associated reference designator,
            (2) are not of class '.XAsset'.

    Request arguments supported:
    1. request.arg: 'min'           (bool)
        Sample request: http://localhost:4000/uframe/assets?min=true
    2. request.arg: 'deployments'   (bool)  Note: Only relevant when request.arg 'min' is used. [deprecate]
        Sample request: http://localhost:4000/uframe/assets?min=true&deployments=true
    3. request.arg: 'sort'          (str)   Asset attribute name.
    4. request.arg: 'startAt'       (int)   Point to begin slice of assets list to return.
    5. request.arg: 'count'         (int)   Number of assets to show in a slice.
    6. request.arg: 'geoJSON'       (bool)  If true, show list of dicts for mooring and/or platform.
        Sample request: http://localhost:4000/uframe/assets?geoJSON=true
        Sample response:
            {
              "assets": [
                {
                  "array_id": "CP",
                  "display_name": "Central Surface Mooring",
                  "geo_location": {
                    "coordinates": [
                      -70.7715,
                      40.1398
                    ],
                    "depth": 0.0
                  },
                  "maxdepth": 133.0,
                  "mindepth": 0.0,
                  "reference_designator": "CP01CNSM"
                },
                . . .
            }
    """
    try:
        data = verify_cache()
        if not data:
            message = 'Failed to get assets.'
            raise Exception(message)

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
        for obj in data:
            try:
                if 'events' in obj:
                    del obj['events']
                if 'manufactureInfo' in obj:
                    del obj['manufactureInfo']
                if 'notes' in obj:
                    del obj['notes']
                if 'physicalInfo' in obj:
                    del obj['physicalInfo']
                if 'purchaseAndDeliveryInfo' in obj:
                    del obj['purchaseAndDeliveryInfo']
                if 'lastModifiedTimestamp' in obj:
                    del obj['lastModifiedTimestamp']
                if 'calibration' in obj:
                    del obj['calibration']
                if 'partData' in obj:
                    del obj['partData']
                if 'attachments' in obj:
                    del obj['attachments']
            except Exception as err:
                current_app.logger.info(str(err))
                raise

    # Create toc information using geoJSON=true
    if request.args.get('geoJSON') and request.args.get('geoJSON') != "":
        return_list = []
        unique = set()
        for obj in data:
            asset = {}
            if len(obj['ref_des']) <= 14 and 'latitude' in obj and 'longitude' in obj:

                if obj['ref_des'] not in unique:
                    unique.add(obj['ref_des'])
                    asset['assetInfo'] = obj.pop('assetInfo')
                    asset['assetInfo']['refDes'] = obj.pop('ref_des')
                    #asset['coordinates'] = obj.pop('coordinates')
                    asset['latitude'] = obj.pop('latitude')
                    asset['longitude'] = obj.pop('longitude')
                    if 'depth' in obj:
                        asset['assetInfo']['depth'] = obj.pop('depth')
                    else:
                        asset['assetInfo']['depth'] = None

                    mindepth = 0
                    if 'mindepth' in asset['assetInfo']:
                        mindepth = asset['assetInfo']['mindepth']

                    maxdepth = 0
                    if 'maxdepth' in asset['assetInfo']:
                        maxdepth = asset['assetInfo']['maxdepth']

                    # Get display name
                    name = asset['assetInfo']['name']
                    if not name or name is None:
                        name = get_display_name_by_rd(asset['assetInfo']['refDes'])
                        if name is None:
                            name = asset['assetInfo']['refDes']
                    json = {
                            'array_id': asset['assetInfo']['refDes'][:2],
                            'display_name': name,
                            'geo_location': {
                                'coordinates': [
                                    round(asset['longitude'], 4),
                                    round(asset['latitude'], 4)
                                    ],
                                'depth': asset['assetInfo']['depth']
                                },
                            'mindepth': mindepth,
                            'maxdepth': maxdepth,
                            'reference_designator': asset['assetInfo']['refDes']
                            }
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


# Get asset by asset id.
@api.route('/assets/<int:id>', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_asset(id):
    """ Get asset by id.
    """
    try:
        result = _get_asset(id)
        return jsonify(result)
    except Exception as err:
        message = 'Error getting asset with id %d. %s' % (id, str(err))
        current_app.logger.info(message)
        return bad_request(message)


# Get asset by asset uid.
@api.route('/assets/uid/<string:uid>', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_asset_by_uid(uid):
    """ Get asset by uid.
    """
    try:
        # Get asset from uframe by uid, return asset id.
        id = _get_id_by_uid(uid)
        if id is None:
            message = 'Unable to identify an asset with uid: \'%s\'.' % uid
            raise Exception(message)

        # Get asset by asset id.
        result = _get_asset(id)
        return jsonify(result)

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get events for asset.
@api.route('/assets/<int:id>/events', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_asset_events(id):
    """ Get events for asset id. Optional type=[[event_type][,event_type, ...]]

    Sample requests:
        http://localhost:4000/uframe/assets/1663/events
        http://localhost:4000/uframe/assets/1663/events?type=STORAGE
        http://localhost:4000/uframe/assets/1663/events?type=STORAGE,DEPLOYMENT
    """
    try:
        if id == 0:
            message = 'Zero (0) is an invalid asset id value, unable to GET asset events without valid asset id.'
            raise Exception(message)

        # Determine if type parameter provided, if so process
        _type = request.args.get('type')
        events = _get_events_by_id(id, _type)
        return jsonify({'events': events})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo ======================================================
# todo - Modify for new asset REST interface. Not done.
# todo ======================================================
# Create asset
@api.route('/assets', methods=['POST'])
#@auth.login_required
#@scope_required(u'asset_manager')
def create_asset():
    """ Create a new asset.
    """
    test = False
    try:

        if not test:
            if not request.data:
                message = 'No data provided to perform an update for asset %d.' % id
                raise Exception(message)
            data = json.loads(request.data)
        else:
            # Test driven
            data = _get_asset(8409)
            if 'assetInfo' in data:
                if 'owner' in data['assetInfo']:
                    data['assetInfo']['owner'] = 'James'
            if 'notes' in data:
                data['notes'] = 'Test: Jim - updated notes again.'

        asset = _create_asset(data)
        result = jsonify({'asset': asset})
        return result
        '''
        if debug: print '\n entered create assets...'
        if not request.data:
            message = 'Create asset requires request data.'
            raise Exception(message)
        data = json.loads(request.data)


        if debug: print '\n loaded request data...'
        if debug: print '\n debug -- data: ', data
        #if valid_create_asset_request_data(data):                      # todo consider rework based on new assets
        #    if debug: print '\n debug validated required fields...'

        url = '/'.join([get_uframe_assets_info(), 'asset'])
        if check: print '\n check: url: ', url
        """
        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']
        if 'asset_class' in data:
            data['@class'] = data.pop('asset_class')
        """

        # Create asset in uframe
        response = requests.post(url, data=json.dumps(data), headers=headers())
        if debug: print '\n response.status_code: ', response.status_code
        if response.status_code != 201:
            response_data = json.loads(response.text)
            if debug: print '\n debug -- response_data (in assets): ', response_data
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
            message = 'Failed to create asset.'
            raise Exception(message)

        return response.text, response.status_code
        '''

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


# Update asset
@api.route('/assets/<int:id>', methods=['PUT'])
#@auth.login_required
#@scope_required(u'asset_manager')
def update_asset(id):
    """ Update asset by id.
    """
    try:
        if not request.data:
            message = 'No data provided to perform an update for asset %d.' % id
            raise Exception(message)
        data = json.loads(request.data)
        asset = _update_asset(id, data)
        result = jsonify({'asset': asset})
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get supported asset types.
@api.route('/assets/types', methods=['GET'])
def get_asset_types_used():
    """ Get list of all asset types available (from uFrame) and used by assets data.

    Sample response:
    {
      "asset_types": [
        "Sensor",
        "Node",
        "Mooring"
      ]
    }
    """
    try:
        return jsonify({'asset_types': get_supported_asset_types()})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


'''
# todo ======================================================
# todo - test with new asset REST interface -
# todo - Note class .XAsset with assetType notClassified are assets in preparation.
# todo - Note assets with assetType 'Array' should be promoted and included in assets.
# todo ======================================================
@api.route('/bad_assets', methods=['GET'])
def get_bad_assets():
    """ Get bad assets.
    """
    debug = False
    try:
        results = _get_bad_assets()
        if debug: print '\n debug -- Number of bad assets: %d' % len(results)
        return jsonify({"assets": results})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo ======================================================
# todo - test with new asset REST interface
# todo ======================================================
@api.route('/all_assets', methods=['GET'])
def get_all_assets():
    """ Get bad assets.
    """
    try:
        results = _get_all_assets()
        return jsonify({"assets": results})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
'''

