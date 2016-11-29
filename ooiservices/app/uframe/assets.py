
"""
Asset Management - Asset routes.

Routes:

[GET]  /assets/types                 # Get all asset types used by those assets loaded into asset management display
[GET]  /assets/types/supported       # Get all asset types supported by uframe.
[GET]  /assets/edit_phase_values     # Get list of valid edit phase values for assets.
[GET]  /assets/available/<string:rd> # Get boolean indicating whether or not asset available for reference designator.
[GET]  /assets/<int:id>              # Get asset by asset id.
[GET]  /assets/uid/<string:uid>      # Get asset by asset uid.
[GET]  /assets/<int:id>/events       # Get all events for an asset; optional 'type' parameter for one or more types.
[GET]  /assets                       # Get all assets from uframe and format for UI

[POST]  /assets                      # Create an asset
[PUT]   /assets/<int:id>             # Update an existing asset
"""
__author__ = 'Edna Donoughe'

from flask import request, jsonify, current_app
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.errors import (bad_request, conflict, internal_server_error)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.asset_tools import (verify_cache, _get_asset, _get_ui_asset_by_uid)
from ooiservices.app.uframe.event_tools import _get_events_by_id
from ooiservices.app.uframe.assets_create_update import (_create_asset, _update_asset)
from ooiservices.app.uframe.common_tools import (asset_edit_phase_values, boolean_values, get_asset_types_for_display,
                                                 get_supported_asset_types_for_display)
from operator import itemgetter
import json

from ooiservices.app.uframe.asset_tools import assets_query_geojson


# Get all asset types.
@api.route('/assets/types', methods=['GET'])
def get_asset_type():
    """ Get list of all asset types.
    """
    #return jsonify({'asset_types': get_asset_types()})
    return jsonify({'asset_types': get_asset_types_for_display()})


# Get supported asset types.
@api.route('/assets/types/supported', methods=['GET'])
def get_supported_asset_type():
    """ Get list of all supported asset types.
    on deck: get_supported_asset_types_for_display
    """
    #return jsonify({'asset_types': get_supported_asset_types()})
    return jsonify({'asset_types': get_supported_asset_types_for_display()})


# Get edit phase values.
@api.route('/assets/edit_phase_values', methods=['GET'])
def get_asset_edit_phase_values():
    """ Get all valid event types supported in uframe asset web services.
    """
    return jsonify({'values': asset_edit_phase_values()})


# Get boolean values.
@api.route('/boolean_values', methods=['GET'])
def get_boolean_values():
    """ Get all valid event types supported in uframe asset web services.
    """
    return jsonify({'values': boolean_values()})


# Get asset by asset id.
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
@api.route('/assets/uid/<string:uid>', methods=['GET'])
def get_ui_asset_by_uid(uid):
    """ Get asset by uid.
    """
    try:
        result = _get_ui_asset_by_uid(uid)
        if not result:
            message = 'No asset with asset id %d.' % id
            return conflict(message)
        return jsonify(result)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get events for asset.
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


# Create asset.
@api.route('/assets', methods=['POST'])
@auth.login_required
@scope_required(u'asset_manager')
def create_asset():
    """ Create asset.
    """
    from ooiservices.app.uframe.common_tools import dump_dict
    try:
        if not request.data:
            message = 'No data provided to create an asset.'
            raise Exception(message)
        data = json.loads(request.data)
        asset = _create_asset(data)
        return jsonify({'asset': asset}), 201
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Update asset.
@api.route('/assets/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required(u'asset_manager')
def update_asset(id):
    """ Update asset.
    """
    try:
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
def get_assets(use_min=False, normal_data=False):
    """ Get list of all uframe assets, optionally filtered by request,args criteria below, and formatted for UI display.

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
        """
        if request.args.get('min') == 'True' or use_min is True:
            message = 'Scheduled for deprecation, do not call with ?min=True....'
            return bad_request(message)
        """

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
                if 'remoteResources' in obj:
                    del obj['remoteResources']
                #if 'remoteDocuments' in obj:
                #    del obj['remoteDocuments']

        # Create toc information using geoJSON=true
        if request.args.get('geoJSON') and request.args.get('geoJSON') != "":
            #print '\n UI Services -- assets?geoJSON'
            rd = None
            if request.args.get('rd') and request.args.get('rd') != '':
                rd = str(request.args.get('rd'))
            data = assets_query_geojson(data, rd)

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

'''
# Get assets to navigate arrays.
@api.route('/assets/nav/arrays', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def nav_get_arrays():
    """ Get navigation information for arrays.
    Sample request: http://localhost:4000/uframe/assets/nav/arrays
    """
    results = []
    try:
        #data = _nav_get_arrays()
        data = _get_status_arrays()
        if data and data is not None:
            results = data
        return jsonify({'arrays': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get sites for an array (for navigation).
@api.route('/assets/nav/sites/<string:array_rd>', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def nav_get_sites(array_rd):
    """ Get navigation information for an array - returns all sites.
    Sample request: /assets/nav/sites/CE
    """
    results = []
    try:
        #data = _nav_get_sites(array_rd)
        data = _get_status_sites(array_rd)
        if data and data is not None:
            results = data
        return jsonify({'sites': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get platforms for an array site (for navigation).
@api.route('/assets/nav/platforms/<string:site_rd>', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def nav_get_platforms(site_rd):
    """ Get navigation information for a site - returns all platforms.
    Sample request: /assets/nav/platforms/CE01ISSM
    """
    results = []
    try:
        #data = _nav_get_platforms(site_rd)
        data = _get_status_platforms(site_rd)
        if data and data is not None:
            results = data
        return jsonify({'platforms': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get instrument status.
@api.route('/assets/nav/instrument/<string:instrument_rd>', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def nav_get_instrument(instrument_rd):
    """ Get navigation information for a site - returns all platforms.
    Sample request: /assets/nav/instrument/CE01ISSM-SBD17-03-DOSTAD000
    """
    results = []
    try:
        #data = _nav_get_platforms(site_rd)
        #data = get_status_navigation(instrument_rd)
        data = _get_status_instrument(instrument_rd)
        if data and data is not None:
            results = data
        return jsonify({'instrument': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

#======================================================
# todo Add this import: from ooiservices.app.uframe.asset_tools import _get_assets
# Get assets.
@api.route('/new_assets', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def new_get_assets():
    """ Get list of all uframe assets, optionally filtered by request,args criteria below, and formatted for UI display.

    Request arguments supported:
    1. request.arg:  'min'              (bool)  Sample request: http://localhost:4000/uframe/assets?min=true
    2. request.arg:  'sort'             (str)   Asset attribute name, for instance 'ref_des'.
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
    debug = True
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

        # If using minimized ('min') or use_min, then strip asset data
        if request.args.get('min') == 'True':
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
                if 'remoteResources' in obj:
                    del obj['remoteResources']

        # Create main navigation information using geoJSON=True
        if request.args.get('geoJSON') and request.args.get('geoJSON') != "":
            if debug: print '\n debug -- new_assets: geojson processing...'
            data = _get_assets(use_min=False, sort=None, geoJSON=True)
            return jsonify({'assets': data})

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

        result = jsonify({'assets': data})
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
'''
