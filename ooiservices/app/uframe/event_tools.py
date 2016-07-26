
"""
Event supporting functions.

"""
# todo Requirements
# todo - Review again since 2016-07-21 web services update)
# todo - Expect two required fields to be added (in uframe) to each base event per requirement 3.1.6.23
# todo - Missing fields: (1) Event description, (2) Name of operator recording the event
# todo - Add 'g. lastModifiedTimestamp' to requirement 3.1.6.23
# todo
# todo Details
# todo - Review events wrt new asset management data model
# todo - Review all code paths when uid is provided with base event. (important)
#
# Create and Update
# 'STORAGE'                     # Basic create and update completed
# 'UNSPECIFIED'                 # Basic create and update completed
# 'ATVENDOR'                    # Basic create and update completed
# 'ASSET_STATUS'                # Basic create and update completed
# 'RETIREMENT'                  # Basic create and update completed
# 'INTEGRATION'                 # Basic create and update completed
# 'LOCATION'                    # Basic create and update completed
# 'CRUISE_INFO'                 # (general) Basic create and update completed
# todo - 'DEPLOYMENT'           # (general)
# todo - 'CALIBRATION_DATA'     # create and update api not available
# todo - 'RECOVERY'             # not available?
# todo - 'PURCHASE'             # not available?
# todo ===============================================================================================

from flask import current_app
from ooiservices.app import cache
from ooiservices.app.uframe.deployment_tools import is_instrument
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base, get_all_event_types,
                                           get_event_types, get_uframe_assets_info, get_assets_url_base, headers)
import requests
from requests.exceptions import (ConnectionError, Timeout)

def _get_events_by_uid(uid, _type):
    try:
        id = _get_id_by_uid(uid)
        if not id:
            message = 'Unknown or invalid uid %s; unable to get asset id.' % uid
            raise Exception(message)
        events = get_and_process_events(id, uid, _type)
        return events
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _get_events_by_id(id, _type):
    debug = False
    try:
        uid = _get_uid_by_id(id)
        if not uid:
            message = 'Unknown or invalid id %d; unable to get asset id.' % id
            raise Exception(message)
        events = get_and_process_events(id, uid, _type)
        return events
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_and_process_events(id, uid, _type):
    debug = False
    events = {}
    types = ''
    types_list = []
    try:
        # Determine if type parameter provided, if so process
        if _type:
            types, types_list = get_event_query_types(_type)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get reference designator
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        rd = None
        asset_rds = cache.get('asset_rds')
        if asset_rds:
            if debug: print '\n debug -- have asset_rds...'
            if id in asset_rds:
                rd = asset_rds[id]
        if not rd:
            if debug: print '\n debug -- No reference designator found.'
            message = 'Unable to determine the reference designator for asset id %d.' % id
            current_app.logger.info(message)
            raise Exception(message)

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
            # Populate events dictionary
            for event in results:
                if '@class' in event:
                    del event['@class']
                if 'eventType' in event:
                    event_type = event['eventType']
                    if not types_list or event_type in types_list:
                        if event_type in event_types:
                            events[event['eventType']].append(event)
                        else:
                            if debug: print '\n debug -- Unknown or invalid event type provided: %s' % event['eventType']

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # For asset id, get deployments and calibration (calibration only if is_instrument(rd))
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        events['DEPLOYMENT'] = []           # Note: if no deployments, there is a serious issue.
        if rd:
            add_deployments = True
            if types_list and ('DEPLOYMENT' not in types_list):
                add_deployments = False
            if add_deployments:
                # Get deployment events
                deployment_events = get_deployment_events(rd, id, uid)
                if deployment_events:
                    events['DEPLOYMENT'] = deployment_events

            if is_instrument(rd):
                add_calibrations = True
                if types_list and 'CALIBRATION_DATA' not in types_list:
                    add_calibrations = False
                if add_calibrations:
                    # If rd is instrument, get calibration events (if is_instrument(rd))
                    # url: http://host:12587/asset/cal?assetid=500
                        calibration_events = get_calibration_events(id, uid)
                        if calibration_events:
                            events['CALIBRATION_DATA'] = calibration_events

        return events

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_event_query_types(_type):
    """ Get type parameter - if value, process into query string, otherwise return None. On error, raise.
    """
    types_list = []
    try:
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If no type value (None), or determine if single or multiple types provided?
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not _type:
            types = None
        else:
            _type = _type.replace(' ', '')
            type = _type.upper()
            valid_event_types = get_all_event_types()
            #- - - - - - - - - - - - - - - - - - - - - - -
            # If multiple types provided
            #- - - - - - - - - - - - - - - - - - - - - - -
            if ',' in type:
                query_types = []
                # Get and validate each type
                types = type.split(',')
                for type in types:
                    if type not in valid_event_types:
                        message = 'Invalid event type provided in request argument: %s.' % type
                        current_app.logger.info(message)
                        continue
                    elif type not in query_types:
                        query_types.append(type)
                        types_list.append(type)

                # If none of the type values provided is a valid type, raise error.
                if not query_types:
                    message = 'None of the event types provided are valid. %s.' % _type
                    raise Exception(message)

                # query_types as string
                types = ''
                for item in query_types:
                    types += item + ','
                types = types.strip(',')

            #- - - - - - - - - - - - - - - - - - - - - - -
            # Single type provided
            #- - - - - - - - - - - - - - - - - - - - - - -
            else:
                if type not in valid_event_types:
                    message = 'Invalid event type provided in request argument: %s.' % type
                    raise Exception(message)
                types = type
                types_list = [type]

        return types, types_list

    except Exception as err:
        if debug: print '\n debug -- exception: ', str(err)
        raise


def get_uframe_events_by_uid(uid, types):
    """ For a specific asset uid and optional list of event types, get list of events from uframe.
    On status_code(s):
        200     Success, return events
        204     Error, raise exception unknown uid
        not 200 Error, raise exception
    """
    check = False
    try:
        if not uid:
            message = 'Malformed request, no uid request argument provided.'
            raise Exception(message)

        # Build query_suffix for uframe url if required
        query_suffix = None
        if types:
            query_suffix = '?type=' + types

        # Build uframe request for events.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), 'uid', uid ])
        if query_suffix:
            url += query_suffix
        if check: print '\n check -- [get_uframe_events_by_uid] url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
        if payload.status_code == 204:
            # Return None when unknown uid is provided; log invalid request.
            message = '(204) Unknown asset uid %s, unable to get events.' % uid
            current_app.logger.info(message)
            #return None
            raise Exception(message)

        # If error, raise exception
        elif payload.status_code != 200:
            message = '(%d) Error getting event information for uid \'%s\'' % (payload.status_code, uid)
            raise Exception(message)

        # Process events returned (status_code success)
        else:
            result = payload.json()
            if result:
                for event in result:
                    # Add uid to each event if not present todo - remove if provided by uframe
                    if 'uid' not in event:
                        event['uid'] = uid

        return result

    except ConnectionError as err:
        message = 'ConnectionError getting events from uframe for %s;  %s' % (uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = 'Timeout getting events from uframe for %s;  %s' % (uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_deployment_events(rd, id, uid):
    """ Get deployment maps for
    """
    try:
        results = get_deployment_maps(rd, id, uid)
        return results

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_deployments_list(data):
    """ Convert deployment_number string to list of deployments.
    """
    result = []
    try:
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
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_deployment_maps(rd, id, uid):
    """ Get list of all deployment events associated with this asset id.
    """
    debug = False
    events = []
    maps = {}
    try:
        if debug:
            print '\n debug -- asset rd: ', rd
            print '\n debug -- asset id: ', id
            print '\n debug -- asset rd: ', uid
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
            deployments = get_deployments_list(tmp)
        if not deployments:
            return events

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
            if debug: print '\n debug -- have maps...'
            events = convert_maps_to_deployment_events(maps, uid)
            if debug:
                print '\n debug -- after convert_maps_to_deployment_events...'
                print '\n debug -- len(events): ', len(events)
                print '\n debug -- type(events): ', type(events)
                print '\n debug -- events: ', events
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
            events = convert_maps_to_deployment_events(maps, uid)
        return events

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def convert_maps_to_deployment_events(maps, uid):
    """ Generate list of deployment events, reverse order with most recent first.

    Sample request: http://localhost:4000/uframe/assets/1663/events
    Target format structure:         ***** update documentation*****

    """
    events = []
    if not maps:
        print '\n debug -- no maps to process in convert_maps_to_deployment_events...'
        return events
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
            event['event_id'] = v['eventId']                               # todo - add to rd_assets
            #event['lastModifiedTimestamp'] = v['lastModifiedTimestamp']    # todo - add to rd_assets
            event['location'] = [v['location']['longitude'], v['location']['latitude']]
            event['depth'] = v['location']['depth']
            event['tense'] = v['tense']
            #event = convert_event_timestamps(event)
            event['eventName'] = 'Deployment ' + str(k)
            event['notes'] = ''                             # todo - add to rd_assets
            #event['uid'] = uid                              # todo - add to rd_assets; by passing right now
            events.append(event)
        return events

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


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
        "eventStartTime": 1361318400000,
        "eventStopTime": null,
        "eventType": "CALIBRATION_DATA",
        "lastModifiedTimestamp": 1468511911189,
        "notes": null,
        "tense": "UNKNOWN",
        "uid": "A00089",
        "values": [
          0.45
        ]
      },
    """
    names = []
    calibrations = []
    try:
        for calibration in results:
            # Get name of calibration item, if required attribute no found, log error continue
            if 'name' not in calibration:
                message = 'No required attribute \'name\' in .XCalibration; malformed .XCalibration for uid %s.'%uid
                current_app.logger.info(message)
                continue

            # Get calibration name attribute, if duplicate, log error continue
            if 'name' in calibration:
                name = calibration['name']
                if name:
                    if name in names:
                        message = 'duplicate calibration element name %s in calibration data for uid %s' % (name, uid)
                        current_app.logger.info(message)
                        continue

            # Get calibration data for this parameter; remove '@class', 'lastModifiedTimestamp'; convert datetime fields
            if 'calData' in calibration:
                cal_data = calibration['calData']
                for cal in cal_data:
                    cal['uid'] = uid
                    if '@class' in cal:
                        del cal['@class']
                    calibrations.append(cal)

        return calibrations

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _get_id_by_uid(uid):
    """ Get id from uframe asset.
    Sample request: http://host:12587/asset?uid=A00089
    """
    check = False
    try:
        # Get uframe asset by uid.
        query = '?uid=' + uid
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base()])
        url += query
        if check: print '\n check -- [_get_id_by_uid] url to get asset %s: %s' % (uid, url)
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if payload.status_code != 200:
            message = '(%d) GET request failed for asset (uid %s) events.' % (payload.status_code, uid)
            raise Exception(message)
        asset = payload.json()
        id = None
        if asset:
            if 'assetId' in asset:
                id = asset['assetId']
        return id
    except ConnectionError:
        message = 'ConnectionError getting asset (uid %s) from uframe; unable to process events. %s' % (uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (uid %s) from uframe; unable to process events. %s' % (uid, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Error processing GET request for asset (uid %s) events. %s' % (uid, str(err))
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
        if check: print '\n check -- [get_uframe_calibration_events_by_id] url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
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
                # Process calibration data - add uid if not present, remove '@class' and 'lastModifiedTimestamp'.
                for event in calibrations:
                    # Add uid to each event if not present todo - remove if provided by uframe
                    if 'uid' not in event:
                        event['uid'] = uid
                    # Remove '@class'
                    if '@class' in event:
                        del event['@class']

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


def _get_uframe_asset_by_id(id):
    """ Get asset from uframe by id.

    Sample request: http:host:12587/asset/500
    """
    debug = False
    check = False
    try:
        # Get uframe asset
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
        if debug: print '\n debug -- url to get asset %d: %s' % (id, url)
        if check: print '\n check -- [_get_uframe_asset_by_id] url to get asset %d: %s' % (id, url)
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if payload.status_code != 200:
            message = '(%d) GET request failed for asset (id %d) events.' % (payload.status_code, id)
            current_app.logger.info(message)
            raise Exception(message)
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


# Get uid from uframe asset.
def _get_uid_by_id(id):
    """ Get uid from uframe asset.
    Sample request: http:host:12587/asset/500
    """
    try:
        asset = _get_uframe_asset_by_id(id)
        uid = None
        if asset:
            if 'uid' in asset:
                uid = asset['uid']
        return uid

    except Exception as err:
        message = 'Error processing GET request for asset (id %d) events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)


# Get uframe event by id.
def get_uframe_event(id):
    """ Get event from uframe by id.
    """
    check = False
    debug = False
    try:
        # Build uframe request for events, issue request
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_events_url_base(), str(id)])
        if check: print '\n check -- [get_uframe_event] url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
        if payload.status_code == 204:
            # Return None when unknown uid is provided; log invalid request.
            message = '(204) Unknown event id %d, failed to get event.' % id
            current_app.logger.info(message)
            return None

        # If error, raise exception
        elif payload.status_code != 200:
            message = '(%d) Error getting event id %d from uframe.' % (payload.status_code, id)
            raise Exception(message)
        event = payload.json()
        if not event:
            message = 'Unable to get event %d from uframe.' % id
            raise Exception(message)

        # Get event_type
        event_type = None
        if 'eventType' in event:
            event_type = event['eventType']
            if event_type is None:
                message = 'Failed to obtain eventType from uframe event, event id: %d' % id
                raise Exception(message)

        # Post process event content for display.
        if debug: print '\n debug -- post process event'
        event = post_process_event(event)
        if debug: print '\n debug -- after post process event'

        return event

    except Exception as err:
        message = 'Error processing GET request for event (id %d). %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)


# Prepare event for display.
def post_process_event(event):
    """ Process event from uframe before returning for display (in UI).
    """
    try:
        if not event:
            message = 'Event provided for post processing is empty.'
            raise Exception(message)

        if '@class' in event:
            del event['@class']
        return event

    except Exception as err:
        message = 'Error post-processing event (id %d) for display. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)