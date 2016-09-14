
"""
Events: Supporting functions.
"""

from flask import current_app
from ooiservices.app import cache
from ooiservices.app.uframe.common_tools import is_instrument
from ooiservices.app.uframe.asset_tools import uframe_get_asset_by_id
from ooiservices.app.uframe.common_tools import (get_event_types, get_event_types_by_rd, get_event_types_by_asset_type)
from ooiservices.app.uframe.events_validate_fields import get_rd_from_integrationInto
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base,
                                           get_uframe_assets_info, get_assets_url_base, headers)
import requests
from requests.exceptions import (ConnectionError, Timeout)


# Get events by asset uid and type.
def _get_events_by_uid(uid, _type):
    """ Get events by asset uid and type.
    """
    try:
        id, asset_type = _get_id_by_uid(uid)
        if not id:
            message = 'Unknown or invalid uid %s; unable to get asset id to process events.' % uid
            raise Exception(message)
        events = get_and_process_events(id, uid, _type, asset_type)
        return events
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)

# Get all events by asset uid.
def _get_all_events_by_uid(uid, _type):
    """ Get all events by asset uid, shown common field across all events.
    Display line items containing one or more of the following:
        eventId, eventType, eventName, StartTime, EndTime, lastModifiedTimestamp, dataSource | Tense,  notes

    Sample output:
    [
        {
          "dataSource": "UI=edna",
          "eventId": 33192,
          "eventName": "Acquisition test event.",
          "eventStartTime": null,
          "eventStopTime": null,
          "eventType": "ACQUISITION",
          "lastModifiedTimestamp": 1473798995742
        },
        {
          "dataSource": "PCO2W_Cal_Info.xlsx",
          "eventId": 18799,
          "eventName": "CC_calc",
          "eventStartTime": 1451606400000,
          "eventStopTime": null,
          "eventType": "CALIBRATION_DATA",
          "lastModifiedTimestamp": 1473180395102
        },
        . . .
    """
    try:
        id, asset_type = _get_id_by_uid(uid)
        if not id:
            message = 'Unknown or invalid uid %s; unable to get asset id to process events.' % uid
            raise Exception(message)
        events = get_uframe_events_by_uid(uid)
        results = condense_events(events)

        # Calibration_data events, if appropriate, get .
        if asset_type == 'Sensor':
            calibrations = get_calibration_events(id, uid)
            if calibrations and calibrations is not None:
                calib_results = condense_events(calibrations)
                if calib_results:
                    results = results + calib_results

        # todo - Add deployment events here; get rd and then deployment events.
        # Deployment events.
        # events = get_and_process_events(id, uid, _type, asset_type)
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def condense_events(events):
    """ For a set of events, condense to fields common to all events.
    """
    results = []
    columns = ['eventId', 'eventType', 'eventName', 'eventStartTime', 'eventStopTime',
               'lastModifiedTimestamp', 'dataSource', 'tense', 'notes']
    try:
        for event in events:
            temp = {}
            for col in columns:
             temp[col] = event[col]
            results.append(temp)
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get events by asset id and type.
def _get_events_by_id(id, _type):
    """ Get events by asset id and type.
    """
    try:
        uid, asset_type = _get_uid_by_id(id)
        if not uid:
            message = 'Unknown or invalid asset id %d; unable to get events.' % id
            raise Exception(message)
        events = get_and_process_events(id, uid, _type, asset_type)
        return events
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get and process events for an asset.
def get_and_process_events(id, uid, _type, asset_type):
    """ Get and process events for an asset.
    """
    debug = False
    events = {}
    types = ''
    types_list = []
    try:
        if debug: print '\n debug -- asset_type: ', asset_type
        # Determine if type parameter provided, if so process
        if _type:
            types, types_list = get_event_query_types(_type)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get reference designator
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        rd = get_rd_by_asset_id(id)
        if debug: print '\n debug -- rd: ', rd
        """
        if rd is None:
            message = 'Unable to determine the reference designator for asset id %d.' % id
            raise Exception(message)
        """

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare events dictionary
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if rd is not None:
            event_types = get_event_types_by_rd(rd)
            for type in event_types:
                events[type] = []
        else:
            if debug: print '\n debug -- before get event types by asset_type...'
            event_types = get_event_types_by_asset_type(asset_type)
            if debug: print '\n debug -- [1] event_types: ', event_types
            for type in event_types:
                events[type] = []
            if debug: print '\n debug -- [2] event_types: ', event_types

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get events, filtering by types provided. Process results
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        results = get_uframe_events_by_uid(uid, types)
        if results is None:
            # Unknown uid provided (204)
            message = 'Unknown asset uid %s, unable to get events.' % uid
            raise Exception(message)
        elif results:
            #refactor into function
            #events = process_event_by_types(result)
            #========================================================
            # Process result (200), populate events dictionary
            for event in results:
                if '@class' in event:
                    del event['@class']
                if 'eventType' in event:
                    event_type = event['eventType']
                    if not types_list or event_type in types_list:
                        if event_type in event_types:
                            if event_type == 'INTEGRATION':
                                if 'integrationInto' in event:
                                    if event['integrationInto'] is not None:
                                        if len(event['integrationInto']) > 0:
                                            _rd = get_rd_from_integrationInto(event['integrationInto'])
                                            event['integrationInto'] = _rd
                                        else:
                                            event['integrationInto'] = None

                            events[event['eventType']].append(event)
                        else:
                            message = 'Unknown or invalid event type provided: %s' % event['eventType']
                            current_app.logger.info(message)
            #=========================================================
        if debug: print '\n debug -- Check for deployment and calibration events...'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # For asset id, get deployments and calibration (calibration only if is_instrument(rd))
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        events['DEPLOYMENT'] = []
        if rd:
            if is_instrument(rd):
                events['CALIBRATION_DATA'] = []
        if rd:
            add_deployments = True
            if types_list and ('DEPLOYMENT' not in types_list):
                add_deployments = False
            if add_deployments:
                # Get deployment events
                deployment_events = get_deployment_events(rd, id, uid)
                if deployment_events:
                    events['DEPLOYMENT'] = deployment_events

            # If rd is instrument, get calibration events
            if is_instrument(rd):
                events['CALIBRATION_DATA'] = []
                add_calibrations = True
                if types_list and 'CALIBRATION_DATA' not in types_list:
                    add_calibrations = False
                if add_calibrations:
                    calibration_events = get_calibration_events(id, uid)
                    if calibration_events:
                        events['CALIBRATION_DATA'] = calibration_events
        else:
            # Assets which do not have deployments but are of asset type 'Sensor' should be
            # permitted to create and edit calibration values. The calibration values, if any, are
            # gathered here for UI.
            if asset_type == 'Sensor':
                events['CALIBRATION_DATA'] = []
                add_calibrations = True
                if types_list and 'CALIBRATION_DATA' not in types_list:
                    add_calibrations = False
                if add_calibrations:
                    calibration_events = get_calibration_events(id, uid)
                    if calibration_events:
                        events['CALIBRATION_DATA'] = calibration_events


        return events

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get reference designator for asset_id.
def get_rd_by_asset_id(id):
    """ Get reference designator for a given asset id; return None if not found. raise exception onerror.
    """
    try:
        rd = None
        asset_rds = cache.get('asset_rds')
        if asset_rds:
            if id in asset_rds:
                rd = asset_rds[id]
        return rd

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get type parameter.
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
            valid_event_types = get_event_types()
            #- - - - - - - - - - - - - - - - - - - - - - -
            # If multiple types provided
            #- - - - - - - - - - - - - - - - - - - - - - -
            if ',' in type:
                query_types = []
                # Get and validate each type
                types = type.split(',')
                for type in types:
                    if type not in valid_event_types:
                        #message = 'Invalid event type provided in request argument: %s.' % type
                        #current_app.logger.info(message)
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
        message = str(err)
        raise Exception(message)


def get_deployment_events(rd, id, uid):
    """ Get deployment maps for and asset/reference designator.
    """
    try:
        results = get_deployment_maps(rd, id, uid)
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# todo deprecate and use 'deployment_numbers'.
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


# Get list of all deployment events associated with an asset id.
def get_deployment_maps(rd, id, uid):
    """ Get list of all deployment events associated with this asset id.
    """
    events = []
    maps = {}
    try:
        assets_dict = cache.get('assets_dict')
        if not assets_dict:
            return events
        if id not in assets_dict:
            return events

        asset = assets_dict[id]
        deployments = []
        if asset:
            if 'deployment_numbers' in asset:
                deployments = asset['deployment_numbers']
            else:
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
            events = convert_maps_to_deployment_events(maps, uid)
        return events

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get deployments events list, reverse order.
def convert_maps_to_deployment_events(maps, uid):
    """ Generate list of deployment events, with most recent first (reverse order).
    """
    events = []
    if not maps:
        return events
    #'eventName': '',
    events_template = {'deployment_number': 0,
                       'depth': 0.0,
                       'eventStartTime': None,
                       'eventStopTime': None,
                       'eventType': 'DEPLOYMENT',
                       'location': [ 0.0, 0.0],
                       'notes': '',
                       'tense': '',
                       'assetUid': uid}
    ordered_keys = (maps.keys())
    ordered_keys.sort(reverse=True)
    try:
        for k in ordered_keys:
            v = maps[k]
            event = events_template.copy()
            event['deployment_number'] = k
            event['eventStartTime'] = v['beginDT']
            event['eventStopTime'] = v['endDT']
            event['eventId'] = v['eventId']                                # todo - add to rd_assets
            #event['lastModifiedTimestamp'] = v['lastModifiedTimestamp']    # todo - add to rd_assets
            event['location'] = [v['location']['longitude'], v['location']['latitude']]
            event['depth'] = v['location']['depth']
            event['tense'] = v['tense']
            event['notes'] = ''                             # todo - add to rd_assets
            events.append(event)
        return events

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get calibration results from uframe.
def get_calibration_events(id, uid):
    calibration_events = []
    try:
        results = get_uframe_calibration_events_by_uid(id, uid)
        if results:
            calibration_events = process_calibration_results(results, uid)
        return calibration_events
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Process calibration results from uframe.
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
        "assetUid": "A00089",
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
                    #cal['uid'] = uid
                    if '@class' in cal:
                        del cal['@class']
                    calibrations.append(cal)

        return calibrations

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get uid from using asset id.
def _get_uid_by_id(id):
    """ Get uid from using asset id.
    """
    try:
        asset = uframe_get_asset_by_id(id)
        uid = None
        asset_type = None
        if asset:
            if 'uid' in asset:
                uid = asset['uid']
            if 'assetType' in asset:
                asset_type = asset['assetType']
        return uid, asset_type

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Prepare event for display.
def post_process_event(event):
    """ Process event from uframe before returning for display (in UI).
    """
    try:
        if not event:
            message = 'The event provided for post processing is empty.'
            raise Exception(message)
        if '@class' in event:
            del event['@class']
        return event

    except Exception as err:
        message = 'Error post-processing event for display. %s' % str(err)
        raise Exception(message)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Functions requiring uframe.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
            message = 'Malformed request, no uid parameter value provided.'
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
            return None

        # If error, raise exception
        elif payload.status_code != 200:
            message = 'Error getting event information for uid \'%s\'' % uid
            raise Exception(message)

        # Process events returned (status_code success)
        else:
            result = payload.json()
            if result:
                for event in result:
                    # Add uid to each event if not present todo - remove if provided by uframe
                    if 'assetUid' not in event:
                        event['assetUid'] = uid

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


# Get event from uframe by event id.
def get_uframe_event(id):
    """ Get event from uframe by id, some error checking applied for return event.
    """
    check = False
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
        if not event_type:
            message = 'Failed to obtain valid eventType from uframe event, event id: %d' % id
            raise Exception(message)

        # Post process event content for display.
        event = post_process_event(event)
        return event

    except ConnectionError:
        message = 'ConnectionError getting event (id %d) from uframe.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting event (id %d) from uframe; unable to process events.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Error processing GET request for event (id %d). %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)


# Get asset id and asset type using asset uid.
def _get_id_by_uid(uid):
    """ Get asset id using asset uid.
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
        if payload.status_code == 204:
            return None
        elif payload.status_code != 200:
            message = 'Failed to get asset with uid: \'%s\'.' % uid
            raise Exception(message)
        asset = payload.json()
        id = None
        asset_type = None
        if asset:
            if 'assetId' in asset:
                id = asset['assetId']
            if 'assetType' in asset:
                asset_type = asset['assetType']
        return id, asset_type
    except ConnectionError:
        message = 'ConnectionError getting asset (uid %s) from uframe.' % uid
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (uid %s) from uframe.' % uid
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
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


