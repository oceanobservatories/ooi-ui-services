
"""
Asset routes and supporting functions.

Routes:
[GET]    /assets                 # Get all assets from uframe and reformat for UI; get single asset reformatted for UI
[GET]    /assets/types           # [dup] Get asset types used by those assets loaded into asset management display
[GET]    /assets/types/used      # [dup] Get asset types used by those assets loaded into asset management display
[GET]    /assets/types/uframe    # List of all asset types supported by uframe.
[GET]    /assets/<int:id>        # Get asset
[GET]    /assets/<int:id>/events # Get all events for an asset; option 'type' parameter provided toget one or more types.
[DELETE] /asset                  # Deprecated.

"""

# todo Remaining asset routes to be completed for new asset model and web services:
# todo [POST]  /assets           # Create an asset
# todo [PUT]   /assets/<int:id>  # Update an existing asset
# todo [GET]   /bad_assets       # Display assets (1) are type .XAsset or (2) which do not have a reference designator.
# todo [GET]   /all_assets       # Display results from /assets and /bad_assets

from flask import request, jsonify, current_app
from ooiservices.app import cache
from ooiservices.app.main.errors import (bad_request, internal_server_error)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.assetController import _uframe_headers
from ooiservices.app.uframe.vocab import (get_vocab, get_display_name_by_rd)
from ooiservices.app.uframe.asset_tools import get_assets_dict_from_list
from ooiservices.app.uframe.deployment_tools import _get_rd_assets
from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.config import (get_uframe_assets_info, get_assets_url_base, get_asset_types)
from ooiservices.app.uframe.assetController import (_compile_assets, _compile_bad_assets)
from ooiservices.app.uframe.event_tools import _get_events_by_id


# todo Review authentication and scope
#from ooiservices.app.main.authentication import auth
#from ooiservices.app.decorators import scope_required

from operator import itemgetter
import json
import requests
import requests.exceptions
from requests.exceptions import ConnectionError, Timeout

CACHE_TIMEOUT = 172800

# Get assets.
@api.route('/assets', methods=['GET'])
def get_assets(use_min=False, normal_data=False, reset=False):
    """ Get list of all uframe assets, filtered by criteria below, and formatted for UI display.
        Criteria for an asset to be included in response:
            (1) have an associated reference designator,
            (2) are not of type 'notClassified'.

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
            }
    """
    debug = False
    try:
        if debug: print '\n debug -- entered get_assets...'
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
    if debug: print '\n debug -- request.args: ', request.args
    if request.args.get('min') == 'True' or use_min is True:
        if debug: print '\n debug -- using min...'
        showDeployments = False
        deploymentEvents = []
        if request.args.get('deployments') == 'True':
            showDeployments = True
        for obj in data:
            try:
                # todo - modify this section to reflect new asset management data model.
                if 'events' in obj:
                    del obj['events']
                """
                if showDeployments and obj['events'] is not None:
                    for event in obj['events']:
                        if event['eventClass'] == '.DeploymentEvent':
                            deploymentEvents.append(event)
                    del obj['events']
                    obj['events'] = deploymentEvents
                    deploymentEvents = []
                else:
                    del obj['events']
                """
                if 'manufactureInfo' in obj:
                    del obj['manufactureInfo']
                if 'notes' in obj:
                    del obj['notes']
                if 'physicalInfo' in obj:
                    del obj['physicalInfo']
                if 'purchaseAndDeliveryInfo' in obj:
                    del obj['purchaseAndDeliveryInfo']
                #if 'lastModifiedTimestamp' in obj:
                #    del obj['lastModifiedTimestamp']
                if 'calibration' in obj:
                    del obj['calibration']
                if 'partData' in obj:
                    del obj['partData']

                # todo - review use of attachments and asset management requirements.
                if 'attachments' in obj:
                    del obj['attachments']
            except Exception as err:
                if debug: print '\n (assets) exception: ', str(err)
                current_app.logger.info(str(err))
                raise

    # Create toc information using geoJSON=true
    if request.args.get('geoJSON') and request.args.get('geoJSON') != "":
        if debug: print '\n debug -- processing geoJSON request...'
        return_list = []
        unique = set()
        if debug:
            if not data:
                print '\n debug -- no assets to process.....'

        for obj in data:
            asset = {}
            if len(obj['ref_des']) <= 14 and 'coordinates' in obj:

                if obj['ref_des'] not in unique:
                    unique.add(obj['ref_des'])
                    asset['assetInfo'] = obj.pop('assetInfo')
                    asset['assetInfo']['refDes'] = obj.pop('ref_des')
                    asset['coordinates'] = obj.pop('coordinates')
                    if 'depth' in obj:
                        asset['assetInfo']['depth'] = obj.pop('depth')
                    else:
                        asset['assetInfo']['depth'] = None

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
                                    round(asset['coordinates'][0], 4),
                                    round(asset['coordinates'][1], 4)
                                    ],
                                'depth': asset['assetInfo']['depth']
                                },
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


# Get asset types [actually used based on assets loaded into system].
@api.route('/assets/types', methods=['GET'])
@api.route('/assets/types/used', methods=['GET'])
def get_asset_types_used():
    """ Get list of all asset types available (from uFrame) and used by assets data.
    The asset types used is determined during the loading of assets into the system.
    This values is cached.

    Sample request:
        http://localhost:4000/uframe/assets/types
        http://localhost:4000/uframe/assets/types/used

    Sample response:
    {
      "asset_types": [
        "Sensor",
        "Node",
        "Mooring"
      ]
    }
    """
    debug = False
    try:
        asset_types_cached = cache.get('asset_types')
        if asset_types_cached:
            data = asset_types_cached
            if debug: print '\n debug -- asset_types is cached'
        else:
            if debug: print '\n debug -- asset_types is not cached; get and set from assets_list...'
            asset_types = get_all_asset_types()
            if asset_types is None:
                message = 'Failed to determine complete list of asset types in use.'
                raise Exception(message)
            cache.set('asset_types', asset_types, timeout=CACHE_TIMEOUT)
            data = cache.get('asset_types')
        return jsonify({'asset_types': data})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get uframe asset types.
@api.route('/assets/types/uframe', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_assets_types_supported():
    """ Get all valid asset types provided by uframe asset web services.
    http://localhost:4000/uframe/assets/types/uframe

    response:
    {
      "uframe_asset_types": [
        "Sensor",
        "notClassified",
        "Mooring",
        "Node",
        "Array"
      ]
    }

    """
    try:
        asset_types = get_asset_types()
        result = jsonify({'uframe_asset_types': asset_types})
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get asset.
@api.route('/assets/<int:id>', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_asset(id):
    """ Get asset by id.
    Object response for the GET(id) request.  This response is NOT cached.

    Requirements document, 3.1.6.10:
    The CI shall store at a minimum the following information for each asset, if available:
        a. Unique ID
        b. Asset Type (5+1 code for instruments, 8 or 8+5 character code for platform/nodes)
        c. Asset Name
        d. Asset Description
        e. Asset Owner (responsible institution or facility)
        f. OOI part number
        g. Deleted
        h. OOI property number/asset ID
        i. Institution property number
        j. Manufacturer
        k. Manufacturer Part or Model Number
        l. Manufacturer Serial Number
        m. Institution Purchase Order Number
        n. Purchase Date
        o. Purchase Cost
        p. Delivery Order Number
        q. Delivery Date
        r. Storage location when not deployed (e.g., building, room)
        s. Documentation url (s) for external documentation (e.g., link to operations manual, vendor document)
        t. OOI document numbers for OOI controlled documents related to this asset
           (e.g., assembly level design drawing for this asset, inspection report, test plans, test procedures)
        u. Asset dimensions (length, height, width)
        v. Asset weight
        w. Asset power requirements (voltage, wattage)
        x. Firmware version
        y. Software version
        z. Depth rating
        aa. shelf life expiration date
        ab. OOI serial number

    Notes for Requirement 3.1.6.10:
        1. Missing fields: m, p, q, r, w, x, y, aa, ab. Unclear about fields: f, h, I, s, t.
        2. July 21 2016 software update provided missing items; note:
            Item m has an additional data item institutionPropertyNumber which should be added as item ac.
            Item t remains unclear in terms of data item definition.
    """
    debug = False
    check = False
    result = []
    try:
        assets_dict = cache.get('assets_dict')
        if assets_dict is not None:
            if debug: print '\n debug -- get asset id: ', id
            if id in assets_dict:
                result = assets_dict[id]
                if debug: print '\n debug -- result: %s' % json.dumps(result, indent=4, sort_keys=True)
        else:
            if debug: print '\n debug -- entered get_asset id: ', id
            uframe_url, timeout, timeout_read = get_uframe_assets_info()
            if id == 0:
                message = 'Zero (0) is an invalid asset id value.'
                raise Exception(message)

            url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
            if check: print '\n check -- [get_asset] url: ', url
            payload = requests.get(url, timeout=(timeout, timeout_read))
            if payload.status_code != 200:
                message = 'Unable to locate an asset with an id of %d.' % id
                raise Exception(message)
            data = payload.json()
            if debug: print '\n debug -- data returned: ', data
            if data:
                data_list = [data]
                if debug: print '\n debug -- data for compile_assets: ', data_list
                result, _ = _compile_assets(data_list)
                if debug: print '\n debug -- returned from compile_assets: ', result
                if result:
                    return jsonify(**result[0])

        return jsonify(result)

    except ConnectionError:
        message = 'Error: ConnectionError getting asset with id %d.' % id
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Error: Timeout getting asset with id %d.' % id
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = 'Error getting asset with id %d. %s' % (id, str(err))
        current_app.logger.info(message)
        return bad_request(message)


# Get events for asset.
@api.route('/assets/<int:id>/events', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_asset_events(id):
    """ Get events for asset id. Optional type=[[event_type][,event_type, ...]]

    Note on options for approach for migrating to new asset management model:
    1. If utilize assets_dict, then forces continued support of assets_dict cache. (short term solution)
    2. If query uframe for asset, convert to ooi-services asset, then get all events for the asset.
    For now, get (1) working for initial UI drop; move on to (2) after main components in place.

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
    debug = False
    try:
        data = json.loads(request.data)
        #if valid_create_asset_request_data(data):                      # todo consider rework based on new assets
        #    if debug: print '\n debug validated required fields...'

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
            message = 'Failed to create asset.'
            raise Exception(message)

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
# todo - Modify for new asset REST interface.  TODO
# todo ======================================================
# Update asset
@api.route('/assets/<int:id>', methods=['PUT'])
#@auth.login_required
#@scope_required(u'asset_manager')
def update_asset(id):
    """ Update asset by id.
    """
    try:
        data = json.loads(request.data)
        if 'asset_class' in data:
            data['@class'] = data.pop('asset_class')

        url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % ('assets', id)
        response = requests.put(url, data=json.dumps(data), headers=_uframe_headers())
        if response.status_code != 200:
            message = '(%d) Failed to update asset %d.' % (response.status_code, id)
            raise Exceotion(message)

        if response.status_code == 200:
            data_list = [data]
            try:
                compiled_data, asset_rds = _compile_assets(data_list)
            except Exception:
                raise

            if not compiled_data or compiled_data is None:
                raise Exception('_compile_assets returned empty or None result.')

            # Cache asset_list
            asset_list_cache = cache.get('asset_list')
            if 'error' in asset_list_cache:
                message = 'Error returned in \'asset_list\' cache; unable to update cache.'
                raise Exception(message)

            if asset_list_cache:
                cache.delete('asset_list')
                for row in asset_list_cache:
                    if row['id'] == id:
                        row.update(compiled_data[0])
                        break
                cache.set('asset_list', asset_list_cache, timeout=CACHE_TIMEOUT)

            # Cache assets_rd
            if asset_rds:
                asset_rds_cache = cache.get('asset_rds')
                if asset_rds_cache:
                    cache.delete('asset_rds')
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
                #print 'Asset reference designators cache reset...'
                #print '\n len(asset_rds): ', len(asset_rds)
            else:
                print 'Error in asset_rds cache update'

        return response.text, response.status_code

    except ConnectionError:
        message = 'Error: ConnectionError during update asset (id: %d)' % id
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Error: Timeout during during update asset (id: %d)' % id
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo ======================================================
# todo - test with new asset REST interface
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


# ========================================================
# Supporting functions
# ========================================================
def verify_cache(refresh=False):
    """ Verify necessary cached objects are available; if not get and set. Return asset_list data.
    """
    debug = False
    verify_cache_required = False
    try:

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 'vocab_dict' and 'vocab_codes'; 'stream_list'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        vocab_dict = get_vocab()
        stream_list = get_stream_list()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check 'asset_list', 'assets_dict', 'asset_rds', 'rd_assets', 'asset_types'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not cache.get('asset_list') or not cache.get('assets_dict') or not cache.get('asset_rds') or \
           not cache.get('rd_assets') or not cache.get('asset_types'):

            if debug: print '\n setting verify_cache_required True...'
            if debug:
                if not cache.get('asset_list'): print '\n debug -- asset_list not cached...'
                if not cache.get('assets_dict'): print '\n debug -- assets_dict not cached...'
                if not cache.get('asset_rds'): print '\n debug -- asset_rds not cached...'
                if not cache.get('rd_assets'): print '\n debug -- rd_assets not cached...'
                if not cache.get('asset_types'): print '\n debug -- asset_types not cached...'

            verify_cache_required = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If required, get asset(s) supporting cache(s)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verify_cache_required or refresh:
            if debug: print '\n debug -- get_assets_payload...'
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
        raise


def get_assets_payload():
    """ Get all assets from uframe, process into ooi-ui-services list of assets (asset_list).
    Update caches for: 'asset_list', 'assets_dict', 'asset_rds', 'rd_assets', 'asset_types'.
    """
    debug = False
    try:

        if debug: print '\n    debug -- Clear caches related to assets...'
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
            if cache.get('asset_types'):
                cache.delete('asset_types')
        except Exception as err:
            message = str(err)
            raise Exception(message)
        if debug: print '\n    debug -- Cleared caches related to assets...'

        # Get assets from uframe
        result = get_assets_from_uframe()
        if not result:
            message = 'Response content from uframe asset request is empty.'
            raise Exception(message)
        print '\nNumber of uframe assets: %d' % len(result)

        # Get asset_list and asset_rds.
        if debug: print '\n    debug -- _compile_assets...'
        data, asset_rds = _compile_assets(result, compile_all=True)
        if not data:
            if debug: print '\n    debug -- error obtaining asset_list data...'
            message = 'Unable to process uframe assets; error creating assets_list.'
            raise Exception(message)
        if not asset_rds:
            if debug: print '\n    debug -- error obtaining asset_rds data...'
            message = 'Unable to process uframe assets; error creating asset_rds.'
            raise Exception(message)

        # Cache 'asset_list'.
        cache.set('asset_list', data, timeout=CACHE_TIMEOUT)
        check = cache.get('asset_list')
        if not check:
            if debug: print '\n    debug -- error checking asset_list data...'
            message = 'Unable to process uframe assets; error asset_list data is empty.'
            raise Exception(message)
        if debug: print '    debug -- Verify asset_list is available...'

        # Cache 'assets_rd'.
        cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
        if debug:
            print '    debug -- Verify \'asset_rds\' is available...'
            print '\n len(asset_rds): ', len(asset_rds)

        # Cache 'assets_dict'.
        assets_dict = populate_asset_dict(data)
        if assets_dict is None:
            message = 'Empty assets_dict returned from asset data.'
            raise Exception(message)
        if debug: print '    debug -- Verify asset_dict is available...'

        # Cache 'rd_assets'.
        rd_assets = _get_rd_assets()
        if not rd_assets:
            message = 'Empty rd_assets returned from asset data.'
            raise Exception(message)
        if debug: print '    debug -- Verify \'rd_assets\' available...'

        return data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise


# Get stream_list.
def get_stream_list():
    """ Get 'stream_list' from cache; if not cached, get and set cache.
    """
    debug = False
    stream_list = None
    try:
        stream_list_cached = cache.get('stream_list')
        if not stream_list_cached:
            if debug: print '    debug -- stream_list is not cached, get and set...'
            try:
                stream_list = dfs_streams()
            except Exception as err:
                message = str(err)
                raise Exception(message)

            if stream_list:
                if debug: print '    debug -- stream_list get completed'
                cache.set('stream_list', stream_list, timeout=CACHE_TIMEOUT)
                if debug: print '    debug -- stream_list set completed...'
            else:
                message = 'stream_list failed to return value, error.'
                if debug: print '    debug -- ', message
                current_app.logger.info(message)

        return stream_list

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get asset_dict
def populate_asset_dict(data):
    """ Build and cache assets_dict from assets_list; on error log and return None.
    """
    debug = False
    try:
        # Using assets_list data, create asets_dict
        assets_dict = get_assets_dict_from_list(data)

        # If no assets_dict returned, log error
        if not assets_dict:
            message = 'Warning: empty assets_dict returned from get_assets_dict_from_list.'
            if debug: print '\n debug -- message: ', message
            current_app.logger.info(message)

        # Verify asset_dict is type dict
        elif isinstance(assets_dict, dict):
            cache.set('assets_dict', assets_dict, timeout=CACHE_TIMEOUT)
            if debug: print '    debug -- set \'asset_dict\' cache...'

        return assets_dict

    except Exception as err:
        message = 'Error populating \'asset_dict\'; %s' % str(err)
        current_app.logger.info(message)
        return None


# Get all assets from uframe.
def get_assets_from_uframe():
    """ Get all assets from uframe.
    """
    debug = False
    check = False
    try:
        if debug: print '\n debug -- entered get_assets_from_uframe...'
        # Get uframe connect and timeout information
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        timeout_extended = timeout_read * 2
        url = '/'.join([uframe_url, get_assets_url_base()])
        if check: print '\n check -- [get_assets_from_uframe] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_extended))
        if response.status_code != 200:
            message = '(%d) Failed to get uframe assets.' % response.status_code
            raise Exception(message)
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
        message = 'Error getting uframe assets.  %s' % str(err)
        current_app.logger.info(message)
        raise


def get_all_asset_types():
    """ Get list of each asset type used in active set of assets (dependent on 'assets_dict' cache).
    """
    debug = False
    all_asset_types = []
    assets_dict = {}
    try:
        # Get 'assets_dict'
        assets_dict_cached = cache.get('assets_dict')
        if assets_dict_cached:
            assets_dict = assets_dict_cached
        else:
            # Get and set assets_dict from assets_list cache
            assets_list_cached = cache.get('assets_list')
            if assets_list_cached:
                if debug: print '\n debug -- assets_list is cached'
                assets_list = assets_list_cached
                if not assets_list:
                    message = 'Warning: empty assets_list, \'assets_list\' cache must be updated..'
                    if debug: print '\n debug -- message: ', message
                    current_app.logger.info(message)
                    raise Exception(message)

                # Get assets_dict from assets_list.
                assets_dict = get_assets_dict_from_list(assets_list)

        # Verify 'assets_dict' is not empty or None and is a dictionary
        if not assets_dict:
            message = 'Warning: assets_dict unavailable at this time.'
            if debug: print '\n debug -- message: ', message
            current_app.logger.info(message)
            raise Exception(message)

        if not isinstance(assets_dict, dict):
            message = 'Warning: assets_dict not properly formed (not of type \'dict\').'
            if debug: print '\n debug -- message: ', message
            current_app.logger.info(message)
            raise Exception(message)

        # set assets_dict cache
        cache.set('assets_dict', assets_dict, timeout=CACHE_TIMEOUT)
        if debug: print 'Assets dictionary (assets_dict) cache reset...'

        # Process assets_dict for asset type
        for inx in assets_dict:
            work = assets_dict[inx]
            if work:
                if 'asset_type' in assets_dict:
                    if assets_dict['asset_type']:
                        if assets_dict['asset_type'] not in all_asset_types:
                            all_asset_types.append(assets_dict['asset_type'])

        return all_asset_types

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# todo ======================================================
# todo - modify for new asset REST interface
# todo ======================================================
# todo - review base asset fields; changed 2016-07-21
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
# todo - test with new asset REST interface
# todo ======================================================
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

    except Exception:
        raise


# todo ======================================================
# todo - test with new asset REST interface
# todo ======================================================
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

    except Exception:
        raise