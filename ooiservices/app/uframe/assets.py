
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

# todo [POST]  /assets           # Create an asset
# todo [GET]   /bad_assets       # Display assets (1) are type .XAsset or (2) which do not have a reference designator.
# todo [GET]   /all_assets       # Display results from /assets and /bad_assets

"""
__author__ = 'Edna Donoughe'


from flask import request, jsonify, current_app
from ooiservices.app.main.errors import (bad_request, conflict, internal_server_error)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.asset_tools import (_get_asset, verify_cache)
from ooiservices.app.uframe.event_tools import (_get_events_by_id, _get_id_by_uid)
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.uframe.common_tools import (get_supported_asset_types, get_asset_types)
from ooiservices.app.uframe.assets_create_update import (_create_asset, _update_asset,
                                                         _create_remote_resource, _update_remote_resource)

from operator import itemgetter
import json

CACHE_TIMEOUT = 172800


# Get supported asset types.
@api.route('/assets/types', methods=['GET'])
def get_asset_type():
    """ Get list of all asset types.
    """
    return jsonify({'asset_types': get_asset_types()})


# Get supported asset types.
@api.route('/assets/types/supported', methods=['GET'])
def get_supported_asset_type():
    """ Get list of all supported asset types.
    """
    return jsonify({'asset_types': get_supported_asset_types()})


# Get asset by asset id.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/assets/<int:id>', methods=['GET'])
def get_asset(id):
    """ Get asset by id.
    """
    try:
        result = _get_asset(id)
        if not result:
            message = 'No asset with asset id %d.' % id
            return conflict(message)
        return jsonify(result)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get asset by asset uid.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/assets/uid/<string:uid>', methods=['GET'])
def get_asset_by_uid(uid):
    """ Get asset by uid.
    """
    try:
        # Get asset from uframe by uid, return asset id.
        id = _get_id_by_uid(uid)
        if id is None:
            message = 'No asset with asset uid %s.' % uid
            return conflict(message)

        # Get asset by asset id.
        result = _get_asset(id)
        if not result:
            message = 'No asset with asset id %d.' % id
            return conflict(message)
        return jsonify(result)

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get events for asset.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/assets/<int:id>/events', methods=['GET'])
def get_asset_events(id):
    """ Get events for asset id. Optional type=[[event_type][,event_type, ...]]

    Sample requests:
        http://localhost:4000/uframe/assets/1663/events
        http://localhost:4000/uframe/assets/1663/events?type=STORAGE
        http://localhost:4000/uframe/assets/1663/events?type=STORAGE,DEPLOYMENT
    """
    try:
        if id == 0:
            message = 'Zero (0) is an invalid asset id value.'
            raise Exception(message)

        # Determine if type parameter provided, if so process
        _type = request.args.get('type')
        events = _get_events_by_id(id, _type)
        return jsonify({'events': events})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo - Under development.
# Create asset
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/assets', methods=['POST'])
def create_asset():
    """ Create a new asset.
    """
    try:
        message = 'Create asset is not enabled at this time.'
        return bad_request(message)
        """
        if not request.data:
            message = 'No data provided to create an asset.'
            raise Exception(message)
        data = json.loads(request.data)
        asset = _create_asset(data)
        result = jsonify({'asset': asset})
        return result
        """


    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo - Under development.
# Update asset.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/assets/<int:id>', methods=['PUT'])
def update_asset(id):
    """ Update asset by id.
    """
    try:
        """
        message = 'Update asset is not enabled at this time.'
        return bad_request(message)
        """
        if not request.data:
            message = 'No data provided to update asset %d.' % id
            raise Exception(message)
        data = json.loads(request.data)
        asset = _update_asset(id, data)
        if not asset:
            message = 'Unable to get updated asset with asset id %d.' % id
            return conflict(message)
        result = jsonify({'asset': asset})
        return result


    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get assets.
@api.route('/assets', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_assets(use_min=False, normal_data=False):
    """ Get list of all uframe assets, filtered by criteria below, and formatted for UI display.
           Criteria for an asset to be included in response:
            (1) have an associated reference designator,
            (2) are not of class '.XAsset'.

    Request arguments supported:
    1. request.arg:  'min'              (bool)  Sample request: http://localhost:4000/uframe/assets?min=true
    2. request.arg:  'sort'             (str)   Asset attribute name.
    3. request.args: 'startAt', 'count' (int)   Point to begin slice and count to slice for assets list to return.
    4. request.arg:  'geoJSON'          (bool)  If true, show list of dicts for mooring and/or platform.
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
        # Verify asset information available before continuing, if failure raise internal server error.
        try:
            data = verify_cache()
            if not data:
                message = 'Failed to get assets.'
                raise Exception(message)
        except Exception as err:
            message = str(err)
            current_app.logger.info(message)
            return internal_server_error(message)

        # Determine field to sort by, sort asset data (ooi-ui-services format. On bad field, raise exception.
        sort_by = ''
        try:
            if request.args.get('sort') and request.args.get('sort') != "":
                sort_by = str(request.args.get('sort'))
            else:
                sort_by = 'ref_des'
            data = sorted(data, key=itemgetter(sort_by))
        except Exception as err:
            message = 'Unknown element to sort assets by \'%s\'. %s' % (sort_by, str(err))
            current_app.logger.info(message)
            raise Exception(message)
            #pass

        # If using minimized ('min') or use_min, then strip asset data
        if request.args.get('min') == 'True' or use_min is True:
            for obj in data:
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
                if 'partData' in obj:
                    del obj['partData']
                #if 'remoteDocuments' in obj:
                #    del obj['remoteDocuments']

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
                        asset['latitude'] = obj.pop('latitude')
                        asset['longitude'] = obj.pop('longitude')
                        asset['assetInfo']['depth'] = obj.pop('depth')
                        mindepth = 0
                        if 'mindepth' in asset['assetInfo']:
                            mindepth = asset['assetInfo']['mindepth']

                        maxdepth = 0
                        if 'maxdepth' in asset['assetInfo']:
                            maxdepth = asset['assetInfo']['maxdepth']

                        name = asset['assetInfo']['name']
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

        # Both the startAt and count parameters must be provide to get a slice.
        if ( (request.args.get('startAt') and not request.args.get('count')) or
             (not request.args.get('startAt') and request.args.get('count')) ):
            message = 'Both \'startAt\' and \'count\' are required to provide a slice of response data.'
            raise Exception(message)

        if request.args.get('startAt') and request.args.get('count'):
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
            # 'normal_data' is used to step around abuse of route for alerts and alarms. todo - correct.
            if normal_data:
                result = data
            else:
                result = jsonify({'assets': data})
            return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo - Under development.
# Create a remote resource for an asset.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/remote_resource', methods=['POST'])
def create_remote_resource():
    """ Create a new remote resource for an asset.
    """
    try:
        """
        message = 'Create remote resource is not enabled at this time.'
        return bad_request(message)
        """
        if not request.data:
            message = 'No data provided to create a remote resource.'
            raise Exception(message)
        data = json.loads(request.data)
        remote_resource = _create_remote_resource(data)
        if not remote_resource:
            message = 'Failed to create remote resource for asset.'
            return conflict(message)
        result = jsonify({'remote_resource': remote_resource})
        """
        asset = _create_remote_resource(data)
        if not asset:
            message = 'Failed to create remote resource for asset.'
            return conflict(message)
        result = jsonify({'asset': asset})
        """
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo - Under development.
# Update a remote resource for an asset.
#@auth.login_required
#@scope_required(u'asset_manager')
@api.route('/remote_resource', methods=['PUT'])
def update_remote_resource():
    """ Update a remote resource for an asset.
    """
    try:
        if not request.data:
            message = 'No data provided to update a remote resource.'
            raise Exception(message)
        data = json.loads(request.data)
        asset = _update_remote_resource(data)
        if not asset:
            message = 'Unable to get update remote resource for asset.'
            return conflict(message)
        result = jsonify({'asset': asset})
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
