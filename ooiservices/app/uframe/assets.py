
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
from ooiservices.app.uframe.vocab import get_vocab, get_display_name_by_rd
from ooiservices.app.uframe.asset_tools import (is_instrument, get_assets_dict_from_list, _get_rd_assets)
from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.config import (get_uframe_assets_info, get_assets_url_base, get_asset_types, get_event_types)
from ooiservices.app.uframe.assetController import _compile_assets, _compile_bad_assets
from ooiservices.app.uframe.events import (get_uframe_events_by_uid, get_event_query_types)
# process_timestamps_in_events, convert_event_timestamps

# Support for development only routes
from ooiservices.app.uframe.asset_tools import _compile_rd_assets, _compile_asset_rds

from operator import itemgetter
import json
import requests
import requests.exceptions
from requests.exceptions import ConnectionError, Timeout

CACHE_TIMEOUT = 172800


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


def verify_cache():
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
        if verify_cache_required:
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
    Update caches for:
        'asset_list', 'assets_dict', 'asset_rds', 'rd_assets', 'asset_types'.
    """
    debug = False
    data = None
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


@api.route('/assets/types/uframe', methods=['GET'])
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
# todo - modify for new asset REST interface (in progress)
# todo - Requirements:
# todo - Expect additional required fields to be added (in uframe) to each base asset per requirement 3.1.6.10
# todo - Missing fields: missing fields: m, p, q, r, w, x, y, aa.
# todo - Require clarification about fields: f, h, I, s, t.
# todo ======================================================
@api.route('/assets/<int:id>', methods=['GET'])
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
                current_app.logger.info(message)
                return bad_request(message)

            url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
            if check: print '\n check -- [get_asset] url: ', url
            payload = requests.get(url, timeout=(timeout, timeout_read))
            if payload.status_code != 200:
                message = 'Unable to locate an asset with an id of %d.' % id
                current_app.logger.info(message)
                return bad_request(message)
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


# todo ======================================================
# todo - Modify for new asset REST interface (in progress)
# todo ======================================================
# Get events for asset -
@api.route('/assets/<int:id>/events', methods=['GET'])
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
    debug = True
    #events = []
    events = {}
    rd = None
    uid = None
    try:
        if id == 0:
            error = 'Zero (0) is an invalid asset id value, unable to GET asset events without valid asset id.'
            current_app.logger.info(error)
            return bad_request(error)

        # Determine if type parameter provided, if so process
        _type = request.args.get('type')
        if debug: print '\n debug -- _type: ', _type
        types, types_list = get_event_query_types(_type)
        if debug:
            print '\n debug -- types: ', types
            print '\n debug -- types_list: ', types_list

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
        _asset = _get_uframe_asset_by_id(id)
        if not _asset or _asset is None:
            message = 'Unable to obtain asset, id %d, and assocaited uid; unable to retrieve events.'
            if debug: print '\n debug -- message: ', message
            raise Exception(message)

        # Get uid from the asset
        if 'uid' in _asset:
            uid = _asset['uid']
            if debug: print '\n debug -- Asset %d has uid: %s' % (id, uid)
        """
        uid = _get_uid_by_id(id)
        if debug: print '\n debug -- Asset %d has uid: %s' % (id, uid)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get reference designator
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        rd = None
        asset_rds = cache.get('asset_rds')
        if asset_rds:
            if id in asset_rds:
                rd = asset_rds[id]
        if rd:
            if debug: print '\n debug -- reference designator: ', rd
        else:
            if debug: print '\n debug -- No reference designator found.'
            message = 'Unable to determine the reference designator for asset id %d.' % id
            current_app.logger.info(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare events dictionary
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_types = get_event_types(rd)
        for type in event_types:
            events[type] = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get events, filtering by types provided. Process results
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        results = get_uframe_events_by_uid(uid, types)
        if results is None:
            # Unknown uid provided (204)
            message = 'Unknown asset uid %s, unable to get events.' % uid
            raise Exception(message)
        elif results:
            # Process result (200)
            #_events = process_timestamps_in_events(results) # get_timestamp_value

            if debug: print '\n debug -- len(results): ', len(results)

            # Populate events dictionary
            for event in results:
                if debug: print '\n debug -- an event...'
                if 'eventType' in event:
                    event_type = event['eventType']
                    if not types_list or event_type in types_list:
                        if event_type in event_types:
                            if debug: print '\n debug -- Adding event type: %s' % event['eventType']
                            events[event['eventType']].append(event)
                        else:
                            if debug: print '\n debug -- Unknown or invalid event type provided: %s' % event['eventType']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # For asset id, get deployments and calibration (calibration only if is_instrument(rd))
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if rd:
            print '\n debug -- types_list: ', types_list
            add_deployments = True
            if types_list and ('DEPLOYMENT' not in types_list):
                if debug: print '\n debug -- do not add calibrations'
                add_deployments = False
            if add_deployments:
                # Get deployment events
                if debug: print'\n debug -- calling get_deployment_events...'
                deployment_events = get_deployment_events(rd, id, uid)
                if deployment_events:
                    #events = events + deployment_events
                    events['DEPLOYMENT'] = deployment_events

            add_calibrations = True
            if types_list and 'CALIBRATION_DATA' not in types_list:
                add_calibrations = False
            if add_calibrations:
                # If rd is instrument, get calibration events (if is_instrument(rd))
                # url: http://uframe-3-test.ooi.rutgers.edu:12587/asset/cal?assetid=500
                if is_instrument(rd):
                    calibration_events = get_calibration_events(id, uid)
                    if calibration_events:
                        #events = events + calibration_events
                        events['CALIBRATION_DATA'] = calibration_events

        return jsonify({'events': events})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


def get_calibration_events(id, uid):
    calibration_events = []
    try:
        results = get_uframe_calibration_events_by_uid(id, uid)
        if results:
            calibration_events = process_calibration_results(results, uid)
        return calibration_events
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def process_calibration_results(results, uid):
    """

    Sample calibration input data:
    "calibration" : [ {
        "@class" : ".XCalibration",
        "name" : "CC_scale_factor1",
        "calData" : [ {
          "@class" : ".XCalibrationData",
          "comments" : "units = mm",
          "values" : [ 0.45 ],
          "dimensions" : [ 1 ],
          "cardinality" : 0,
          "eventId" : 71,
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_scale_factor1",
          "eventStartTime" : 1361318400000,
          "eventStopTime" : null,
          "notes" : null,
          "tense" : null,
          "dataSource" : null,
          "lastModifiedTimestamp" : 1468511911189
        } ]
      },

      Sample calibration event output (for one parameter):
      {
          "cardinality": 0,
          "comments": "units = mm",
          "dataSource": null,
          "dimensions": [
            1
          ],
          "eventId": 71,
          "eventName": "CC_scale_factor1",
          "eventStartTime": "2013-02-19T19:00:00",
          "eventStopTime": null,
          "eventType": "CALIBRATION_DATA",
          "notes": null,
          "tense": null,
          "uid": "A00089",
          "values": [
            0.45
          ]
      },
    """
    debug = False
    names = []
    calibrations = []
    try:
        for calibration in results:
            # Get name of calibration item, if required attribute no found, log error continue
            if 'name' not in calibration:
                message = 'No required attribute \'name\' in .XCalibration; malformed .XCalibration for uid %s.'%uid
                if debug: print '\n debug -- error message: ', message
                current_app.logger.info(message)
                continue

            # Get calibration name attribute, if duplicate, log error continue
            if 'name' in calibration:
                name = calibration['name']
                if name:
                    if name in names:
                        message = 'duplicate calibration element name %s in calibration data for uid %s' % (name, uid)
                        if debug: print '\n debug -- error message: ', message
                        current_app.logger.info(message)
                        continue

            # Get calibration data for this parameter; remove '@class', 'lastModifiedTimestamp'; convert datetime fields
            if 'calData' in calibration:
                cal_data = calibration['calData']
                for cal in cal_data:
                    cal['uid'] = uid
                    if '@class' in cal:
                        del cal['@class']
                    #if 'lastModifiedTimestamp' in cal:
                    #    del cal['lastModifiedTimestamp']
                    #cal = convert_event_timestamps(cal)
                    calibrations.append(cal)

        return calibrations

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_deployment_events(rd, id, uid):
    """ Get deployment maps for
    """
    try:
        events = get_deployment_maps(rd, id, uid)
        return events

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_deployments_list(data):
    """ Convert deployment_number string to list of deployments.
    """
    debug = False
    result = []
    try:
        if debug: print '\n debug -- data: ', data
        if not data:
            return result

        tmp = data.split(',')
        for item in tmp:
            txt = item.strip()
            value = None
            try:
                value = int(txt)
            except:
                pass
            if value is not None:
                if value not in result:
                    result.append(value)
        if debug: print '\n debug -- result: ', result
        return result

    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception in get_deployments_list: ', message
        current_app.logger.info(message)
        raise Exception(message)


def get_deployment_maps(rd, id, uid):
    """ Get list of all deployment events associated with this asset id.
    """
    debug = False
    events = []
    maps = {}
    try:
        if debug: print '\n debug -- asset id: ', id
        assets_dict = cache.get('assets_dict')
        if not assets_dict:
            if debug: print '\n issue -- assets_dict is None, unable to get deployment events.'
            return events
        if id not in assets_dict:
            if debug: print '\n issue -- asset id %d not in assets_list, unable to get deployment events.' % id
            return events

        asset = assets_dict[id]
        if debug: print '\n debug -- asset: ', asset
        deployments = []
        if asset:
            tmp = asset['deployment_number']
            print '\n debug -- string deployment_number: ', tmp
            deployments = get_deployments_list(tmp)
        if not deployments:
            return events
        if debug: print '\n debug -- deployments list: ', deployments

        # Determine if deployment events are available for this reference designator.
        rd_assets = cache.get('rd_assets')
        if not rd_assets:
            return events
        if rd not in rd_assets:
            return events

        # Get all deployment maps for reference designator
        deployment_map = rd_assets[rd]

        # Compile maps dictionary using only deployments associated with the asset.
        for number in deployments:
            if number not in maps:
                maps[number] = deployment_map[number]

        # Process maps into list of deployment events
        events = []
        if maps:
            events = convert_maps_to_events(maps, uid)
        return events

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# todo - reserved
def get_all_deployment_maps(rd, uid):
    """ Use rd_assets to generate deployment summary list for all deployments associated with this reference designator.
    """
    maps = {}
    try:
        # This gets all deployments for an rd
        rd_assets = cache.get('rd_assets')
        if not rd_assets:
            return maps
        if rd not in rd_assets:
            return maps

        deployment_map = rd_assets[rd]
        deployments = []
        if 'deployments' in deployment_map:
            deployments = deployment_map['deployments']
        if not deployments:
            return maps

        # Compile maps dictionary using deployments associated with the asset.
        for number in deployments:
            if number not in maps:
                maps[number] = deployment_map[number]

        # Process maps into list of deployment events
        events = []
        if maps:
            events = convert_maps_to_events(maps, uid)
        return events

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)



def convert_maps_to_events(maps, uid):
    """ Generate list of deployment events, reverse order with most recent first.

    Sample request: http://localhost:4000/uframe/assets/1663/events

    Target format structure:         ***** update documentation*****

    """
    events = []
    events_template = {'deployment_number': 0,
                       'depth': 0.0,
                       'eventName': '',
                       'eventStartTime': None,
                       'eventStopTime': None,
                       'eventType': 'DEPLOYMENT',
                       'location': [ 0.0, 0.0],
                       'notes': '',
                       'tense': '',
                       'uid': uid}
    ordered_keys = (maps.keys())
    ordered_keys.sort(reverse=True)
    try:
        for k in ordered_keys:
            v = maps[k]
            event = events_template.copy()
            event['deployment_number'] = k
            event['eventStartTime'] = v['beginDT']
            event['eventStopTime'] = v['endDT']
            #event['event_id'] = v['eventId']                               # todo - add to rd_assets
            #event['lastModifiedTimestamp'] = v['lastModifiedTimestamp']    # todo - add to rd_assets
            event['location'] = [v['location']['longitude'], v['location']['latitude']]
            event['depth'] = v['location']['depth']
            event['tense'] = v['tense']
            #event = convert_event_timestamps(event)
            event['eventName'] = 'Deployment ' + str(k)
            event['notes'] = ''                             # todo - add to rd_assets
            #event['uid'] = ''                              # todo - add to rd_assets; by passing right now
            events.append(event)
        return events

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _get_uframe_asset_by_id(id):
    """ Get asset from uframe by id.

    Sample request: http:host:12587/asset/500
    """
    debug = False
    check = True
    try:
        # Get uframe asset
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
        if debug: print '\n debug -- url to get asset %d: %s' % (id, url)
        if check: print '\n check -- [_get_uframe_asset_by_id] url to get asset %d: %s' % (id, url)
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=_uframe_headers())
        if payload.status_code != 200:
            error = '(%d) GET request failed for asset (id %d) events.' % (payload.status_code, id)
            current_app.logger.info(error)
            return bad_request(error)
        asset = payload.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting asset (id %d) from uframe; unable to process events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (id %d) from uframe; unable to process events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Error processing GET request for asset (id %d) events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)


def _get_uid_by_id(id):
    """ Get uid from uframe asset.
    Sample request: http:host:12587/asset/500
    """
    debug = False
    check = True
    try:
        # Get uframe asset by uid.
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
        if debug: print '\n debug -- url to get asset %d: %s' % (id, url)
        if check: print '\n check -- [_get_uframe_asset_by_id] url to get asset %d: %s' % (id, url)
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=_uframe_headers())
        if payload.status_code != 200:
            error = '(%d) GET request failed for asset (id %d) events.' % (payload.status_code, id)
            current_app.logger.info(error)
            return bad_request(error)
        asset = payload.json()
        uid = None
        if asset:
            if 'uid' in asset:
                uid = asset['uid']
        return uid
    except ConnectionError:
        message = 'ConnectionError getting asset (id %d) from uframe; unable to process events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (id %d) from uframe; unable to process events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Error processing GET request for asset (id %d) events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)


def get_uframe_calibration_events_by_uid(id, uid):
    """ Get list of calibration events from uframe for a specific sensor asset uid.

    Function also outfitted for using asset id instead of uid. Both required for error processing at this time.

    On status_code(s):
        200     Success, return events
        204     Error, raise exception unknown uid
        not 200 Error, raise exception

    Sample request (using uid): http://host:12587/asset/cal?uid=A00089
    (Sample request (sing id): http://host:12587/asset/cal?assetid=500)
    Sample response:
    {
      "@class" : ".XInstrument",
      "calibration" : [ {
        "@class" : ".XCalibration",
        "name" : "CC_scale_factor1",
        "calData" : [ {
          "@class" : ".XCalibrationData",
          "comments" : "units = mm",
          "values" : [ 0.45 ],
          "dimensions" : [ 1 ],
          "cardinality" : 0,
          "eventId" : 71,
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_scale_factor1",
          "eventStartTime" : 1361318400000,
          "eventStopTime" : null,
          "notes" : null,
          "tense" : null,
          "dataSource" : null,
          "lastModifiedTimestamp" : 1468511911189
        } ]
      }, {
        "@class" : ".XCalibration",
        "name" : "CC_scale_factor3",
        "calData" : [ {
          "@class" : ".XCalibrationData",
          "comments" : null,
          "values" : [ 0.45 ],
          "dimensions" : [ 1 ],
          "cardinality" : 0,
          "eventId" : 73,
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_scale_factor3",
          "eventStartTime" : 1361318400000,
          "eventStopTime" : null,
          "notes" : null,
          "tense" : null,
          "dataSource" : null,
          "lastModifiedTimestamp" : 1468511911189
        } ]
      },
      . . .

    """
    debug = False
    check = False
    try:
        if not uid:
            message = 'Malformed request, no uid request argument provided.'
            raise Exception(message)

        # Build query_suffix for uframe url if required
        #query_suffix = 'cal?assetid=' + str(id)        # by id
        query_suffix = 'cal?uid=' + uid                 # by uid

        # Build uframe request for events, issue request
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base(), query_suffix])
        if debug: print '\n debug -- [get_uframe_calibration_events_by_id] url: ', url
        if check: print '\n check -- [get_uframe_calibration_events_by_id] url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
        if debug: print '\n debug -- uframe get events status_code: ', payload.status_code
        if payload.status_code == 204:
            # Return None when unknown uid is provided; log invalid request.
            message = '(204) Unknown asset uid %s, unable to get calibration events.' % uid
            current_app.logger.info(message)
            return None

        # If error, raise exception
        elif payload.status_code != 200:
            message = '(%d) Error getting calibration event information for uid \'%s\'' % (payload.status_code, uid)
            raise Exception(message)

        # Process events returned (status_code success)
        else:
            result = payload.json()
            calibrations = []
            if result:
                if 'calibration' in result:
                    calibrations = result['calibration']
                    if debug: print '\n debug -- len(calibrations): ', len(calibrations)

                # Process calibration data - add uid if not present, remove '@class' and 'lastModifiedTimestamp'.
                for event in calibrations:
                    # Add uid to each event if not present todo - remove if provided by uframe
                    if 'uid' not in event:
                        event['uid'] = uid
                    # Remove 'lastModifiedTimestamp'
                    #if 'lastModifiedTimestamp' in event:
                    #    del event['lastModifiedTimestamp']
                    # Remove '@class'
                    if '@class' in event:
                        del event['@class']

                if debug: print '\n debug -- len(calibrations): ', len(calibrations)
                if debug: print '\n debug -- calibrations: %s' % json.dumps(calibrations, indent=4, sort_keys=True)
            else:
                if debug: print '\n debug ** calibrations: ', calibrations

        return calibrations

    except ConnectionError as err:
        message = 'ConnectionError getting calibration events from uframe for asset id/uid: %d/%s;  %s' % (id, uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = 'Timeout getting calibration events from uframe for asset id/uid: %d/%s;  %s' % (id, uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# todo ======================================================
# todo - Modify for new asset REST interface. Not done.
# todo ======================================================
# Create asset
@api.route('/assets', methods=['POST'])
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
# todo - Modify for new asset REST interface. Not done.
# todo ======================================================
# Update asset
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

            # Cache asset_list
            asset_list_cache = cache.get('asset_list')
            if 'error' in asset_list_cache:
                message = 'Error returned in \'asset_list\' cache; unable to update cache.'
                return bad_request(message)

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
                print 'Asset reference designators cache reset...'
                print '\n len(asset_rds): ', len(asset_rds)
            else:
                print 'Error in asset_rds cache update'

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


# todo ==============================================================================================
# todo ==============================================================================================
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
# todo ======================================================
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

    except Exception as err:
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

    except Exception as err:
        raise


#==========================================================================================
# Development only routes...
#==========================================================================================
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
            if debug: print '\n debug -- assets_dict not cached, get_assets_payload then check cache...'
            data = get_assets_payload()
            if not data:
                message = 'No asset data returned from uframe.'
                current_app.logger.info(message)
                return internal_server_error(message)
            dict_cached = cache.get('assets_dict')
            if dict_cached:
                assets_dict = dict_cached
            else:
                message = 'assets_dict not cached after calling get_assets_payload..'
                if debug: print '\n debug -- ', message
                return internal_server_error(message)

        if debug: print '\n debug -- Length of asset_dict: %d' % len(assets_dict)
        return jsonify(assets_dict), 200

    except Exception as err:
        message = 'Exception processing dev_assets_dict: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)

#===================================================================================
#===================================================================================
'''
# Development only route......
@api.route('/get_asset_list', methods=['GET'])
def dev_get_asset_list():
    """ Get cached 'asset_list' or generate 'asset_list'. Does NOT cache.
    """
    debug = False
    asset_list = []
    try:
        if debug: print '\n debug -- entered dev_get_asset_list...'
        asset_rds = {}

        # Get 'asset_list' if cached
        asset_list_cached = cache.get('asset_list')
        if asset_list_cached:
            asset_list = asset_list_cached
        else:
            if debug: print '\n debug -- asset_list not cached...'
            """
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)
            """

        if debug: print '\n debug -- Length of asset_list: %d' % len(asset_list)
        return jsonify(asset_list), 200

    except Exception as err:
        message = 'Exception processing dev_get_asset_list: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)
'''


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
                print '[+] Reference designators asset cache reset...'
            else:
                print '[-] Error in cache update'

        if debug: print '\n debug -- Length of rd_assets: %d' % len(rd_assets)
        return jsonify(rd_assets), 200

    except Exception as err:
        message = 'Exception processing dev__get_rd_assets: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)