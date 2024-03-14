
"""
Asset Management - Upstream server (uframe) interface functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base,
                                           get_uframe_assets_info, get_assets_url_base, headers,
                                           get_url_info_resources, get_uframe_info_calibration,
                                           get_url_info_cruises, get_url_info_cruises_inv,
                                           get_uframe_events_info, get_url_info_cruises_rec,
                                           get_url_info_deployments_inv, get_deployments_url_base,
                                           get_url_info_status_query, get_uframe_toc_url,
                                           get_url_info_stream_byname, get_uframe_info, get_url_info_stream_parameters,
                                           get_url_da_info, get_uframe_timeout_info, get_uframe_versions_url)
from ooiservices.app.uframe.common_tools import deployment_edit_phase_values


import requests
from requests.exceptions import (ConnectionError, Timeout)
import datetime as dt
import json
import urllib


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Events.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_postto(event_type, uid, data):
    try:
        # Set uframe query parameter, get configuration url and timeout information, build request url.
        query = 'postto'
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), query, uid])

        response = requests.post(url, data=json.dumps(data), headers=headers())
        # Process error.
        if response.status_code != 201:
            if response.content is None:
                message = 'Failed to create %s event; status code: %d' % (event_type, response.status_code)
                raise Exception(message)

            elif response.content is not None:
                response_data = json.loads(response.content)

                # Determine if success or failure.
                if 'error' not in response_data:
                    # Success? If success get id.
                    if 'statusCode' in response_data:
                        # Failure? If failure build error message.
                        if 'message' in response_data and 'statusCode' in response_data:
                            message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                            raise Exception(message)
                else:
                    # Failure? If failure build error message.
                    if 'message' in response_data and 'statusCode' in response_data:
                        message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                        raise Exception(message)

        # Get response data, check status code returned from uframe.
        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)

            # Determine if success or failure.
            if 'error' not in response_data:
                # Success? If success get id.
                if 'statusCode' in response_data:
                    if response_data['statusCode'] == 'CREATED':
                        id = response_data['id']
                    else:
                        message = 'Failed to create %s event; statusCode from uframe: %s' % \
                                  (event_type, response_data['statusCode'])
                        raise Exception(message)
            else:
                # Failure? If failure build error message.
                if 'message' in response_data and 'statusCode' in response_data:
                    message = response_data['statusCode'] + ': ' + response_data['message']
                    raise Exception(message)
        return id

    except ConnectionError as err:
        message = 'ConnectionError during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Timeout as err:
        message = 'Timeout during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_create_cruise(event_type, data):
    """ Create a cruise event; assetUid for cruise event shall be None.
    """
    try:
        data['assetUid'] = None
        # Set uframe query parameter, get configuration url and timeout information, build request url.
        url, timeout, timeout_read = get_url_info_cruises()
        response = requests.post(url, data=json.dumps(data), headers=headers())

        # Process error.
        if response.status_code != 201:
            message = 'Failed to create %s event in uframe; status code: %d' % (event_type, response.status_code)
            raise Exception(message)

        # Get response data, check status code returned from uframe.
        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            # Determine if success or failure.
            if 'error' not in response_data:
                # Success? If success get id.
                if 'statusCode' in response_data:
                    if response_data['statusCode'] == 'CREATED':
                        id = response_data['id']
                    else:
                        message = 'Failed to create %s event; statusCode from uframe: %s' % \
                                  (event_type, response_data['statusCode'])
                        raise Exception(message)
            else:
                # Failure? If failure build error message.
                if 'message' in response_data and 'statusCode' in response_data:
                    message = response_data['statusCode'] + ': ' + response_data['message']
                    raise Exception(message)
        return id

    except ConnectionError as err:
        message = 'ConnectionError during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Timeout as err:
        message = 'Timeout during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_create_calibration(event_type, uid, data):
    """ Create a calibration event.
    """
    try:
        if 'eventId' in data:
            del data['eventId']
        # Set uframe query parameter, get configuration url and timeout information, build request url.
        base_url, timeout, timeout_read = get_uframe_info_calibration()
        url = '/'.join([base_url, uid])
        response = requests.post(url, data=json.dumps(data), headers=headers())
        # Process error.
        if response.status_code != 201 and response.status_code != 204:
            uframe_message = None
            if response.content:
                error = json.loads(response.content)
                if 'message' in error:
                    uframe_message = '%s' % error['message']
                    if uframe_message is not None:
                        current_app.logger.info(uframe_message)
            message = 'Failed to create %s event in uframe. ' % event_type
            if uframe_message is not None:
                message += '%s' % uframe_message
            raise Exception(message)
        return response.status_code
    except ConnectionError as err:
        message = 'ConnectionError during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Timeout as err:
        message = 'Timeout during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_uframe_events_by_uid(uid, types=None):
    """ Get list of events from uframe for a specific asset uid and optional list of event types.
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


def uframe_put_event(event_type, id, data):
    """ Update event with id using data provided. Returns id from update
    """
    debug = False
    try:
        #=================================
        # Get configuration url and timeout information, build request url.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(id)])
        # Issue uframe PUT to update, process response status_code and content.
        if debug:
            print(url)
            print(json.dumps(data))
            print(headers)
        response = requests.put(url, data=json.dumps(data), headers=headers())
        if debug:
            print(response.request)
        if response.status_code != 200:
            if response.content is None:
                message = 'Failed to create %s event in uframe.' % event_type
                raise Exception(message)
            elif response.content is not None:
                response_data = json.loads(response.content)
                # Determine if success or failure.
                if 'error' not in response_data:
                    # Success? If success get id.
                    if 'statusCode' in response_data:
                        # Failure? If failure build error message.
                        if 'message' in response_data and 'statusCode' in response_data:
                            message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                            raise Exception(message)
                else:
                    # Failure? If failure build error message.
                    if 'message' in response_data and 'statusCode' in response_data:
                        message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                        raise Exception(message)

        # Get response data, check status code returned from uframe.
        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            # Determine if success or failure.
            if 'error' not in response_data:
                # Success? If success get id.
                if 'id' in response_data:
                    id = response_data['id']
            else:
                # Failure? If failure build error message.
                if 'message' in response_data:
                    message = response_data['error'] + ': ' + response_data['message']
                    raise Exception(message)
        #=================================
        return id

    except ConnectionError as err:
        message = 'ConnectionError updating %s event; %s.' % (event_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = 'Timeout updating %s event; %s.' % (event_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Assets.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get assets from uframe.
def get_assets_from_uframe():
    """ Get all assets from uframe.
    """
    extend_timeout = True
    time = True
    try:
        # Get uframe connect and timeout information
        if time: print '\n-- Getting assets from uframe... '
        start = dt.datetime.now()
        if time: print '\t-- Start time: ', start
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        timeout_extended = timeout_read
        if extend_timeout:
            timeout_extended = timeout_read * 5
            timeout = timeout * 3
        url = '/'.join([uframe_url, get_assets_url_base()])
        response = requests.get(url, timeout=(timeout, timeout_extended))
        end = dt.datetime.now()
        if time: print '\t-- End time:   ', end
        if time: print '\t-- Time to get uframe assets: %s' % str(end - start)
        if response.status_code != 200:
            message = '(%d) Failed to get uframe assets.' % response.status_code
            raise Exception(message)
        result = response.json()
        print '\t-- Number of assets from uframe: ', len(result)
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
        message = str(err)
        current_app.logger.info(message)
        raise


# Get asset from uframe by asset id.
def uframe_get_asset_by_id(id):
    """ Get asset from uframe by asset id.
    """
    debug = False
    try:
        # Get uframe asset
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
        if debug: print '\n debug -- uframe_get_asset_by_id url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if payload.status_code != 200:
            message = 'Failed to get asset (id: %d) from uframe.' % id
            current_app.logger.info(message)
            raise Exception(message)
        asset = payload.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting asset (id: %d) from uframe.' % id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (id: %d) from uframe.' % id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get asset from uframe by asset uid.
def uframe_get_asset_by_uid(uid):
    """ Get asset from uframe by asset uid.
    """
    check = False
    try:
        # Get uframe asset by uid.
        query = '?uid=' + uid
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base()])
        url += query
        if check: print '\n check url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if response.status_code == 204:
            message = 'Failed to receive content from uframe for asset with uid \'%s\'.' % uid
            current_app.logger.info(message)
            raise Exception(message)
        elif response.status_code != 200:
            message = 'Failed to get asset from uframe with uid: \'%s\'.' % uid
            current_app.logger.info(message)
            raise Exception(message)
        asset = response.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting asset (uid %s) from uframe.' % uid
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (uid %s) from uframe.' % uid
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get remote resource from uframe by remote resource id.
def uframe_get_remote_resource_by_id(id):
    """ Get remote resource from uframe by remoteResourceId..
    """
    try:
        # Get uframe asset by uid.
        uframe_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([uframe_url, str(id)])
        response = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if response.status_code == 204:
            message = 'Failed to get content from uframe for remote resource with id \'%d\'.' % id
            raise Exception(message)
        elif response.status_code != 200:
            message = 'Failed to get remote resource from uframe with id: %d.' % id
            raise Exception(message)
        remote_resource = response.json()
        return remote_resource
    except ConnectionError:
        message = 'ConnectionError getting remote resource (uid %d) from uframe.' % id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting remote resource (uid %d) from uframe.' % id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Update asset in uframe.
def uframe_update_asset(asset):
    """ Update asset in uframe. On success return updated asset, on error, raise exception.
    """
    id = None
    uid = None
    debug = False
    try:
        # Get asset id from asset data provided.
        if 'assetId' in asset:
            id = asset['assetId']
        if id is None:
            message = 'Invalid asset, missing attribute \'assetId\', unable to request asset update.'
            raise Exception(message)
        if 'uid' in asset:
            uid = asset['uid']
        if uid is None:
            message = 'Invalid asset, missing attribute \'uid\', unable to request asset update.'
            raise Exception(message)

        # Update asset in uframe.
        base_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([base_url, get_assets_url_base(), str(id)])
        if debug:
            print('just before PUT')
            print(asset)
        response = requests.put(url, data=json.dumps(asset), headers=headers())
        if response.status_code != 200:
            message = '(%d) Uframe failed to update asset (id/uid: %d/%s).' % (response.status_code, id, uid)
            raise Exception(message)

        # Get updated asset from uframe and return.
        updated_asset = uframe_get_asset_by_uid(uid)
        return updated_asset

    except ConnectionError:
        message = 'Error: ConnectionError during uframe asset update(id: %d)' % id
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout during during uframe asset update (id: %d)' % id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Create asset in uframe.
def uframe_create_asset(asset):
    """ Create asset in uframe. On success return updated asset, on error, raise exception.
    """
    check = False
    success = 'CREATED'
    try:
        # Check asset data provided.
        if not asset or asset is None:
            message = 'Asset data must be provided to create asset in uframe.'
            raise Exception(message)
        if not isinstance(asset, dict):
            message = 'Asset data must be provided in dict form to create asset in uframe.'
            raise Exception(message)

        # Create asset in uframe.
        base_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([base_url, get_assets_url_base()])
        if check: print '\n check: url: ', url
        response = requests.post(url, data=json.dumps(asset), headers=headers())
        if response.status_code != 201:
            message = '(%d) uframe failed to create asset.' % response.status_code
            if response.content:
                uframe_message = json.loads(response.content)
                if 'message' in uframe_message:
                    uframe_message = uframe_message['message']
                message += ' %s' % uframe_message
            current_app.logger.info(message)
            raise Exception(message)

        # Get id for new asset.
        if not response.content:
            message = 'No response content returned from create asset.'
            raise Exception(message)

        # Review response.content:
        #   {u'message': u'Element created successfully.', u'id': 4292, u'statusCode': u'CREATED'}
        response_data = json.loads(response.content)
        id = None
        if 'id' in response_data and 'statusCode' in response_data:
            if response_data['statusCode'] and response_data['id']:
                if response_data['statusCode'] == success and response_data['id'] > 0:
                    id = response_data['id']
        if id is None:
            message = 'Failed to create uframe asset.'
            raise Exception(message)

        # Get new asset from uframe.
        new_asset = uframe_get_asset_by_id(id)
        if not new_asset or new_asset is None:
            message = 'Failed to get asset with id %d from uframe.' % id
            raise Exception(message)
        return new_asset
    except ConnectionError:
        message = 'Error: ConnectionError during uframe asset create.'
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout during during uframe asset create.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_postto_asset(uid, data):
    try:
        # Post request. Get configuration url and timeout information, build request url and post.
        base_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([base_url, 'resource', 'postto', uid])
        response = requests.post(url, data=json.dumps(data), headers=headers())

        # Process error.
        if response.status_code == 204:
            message = 'Failed to get an asset with the uid (\'%s\') provided.' % uid
            raise Exception(message)
        elif response.status_code != 201:
            if response.content is None:
                message = 'Failed to create remote resource; status code: %d' % response.status_code
                raise Exception(message)

            elif response.content is not None:
                response_data = json.loads(response.content)
                # Determine if success or failure.
                if 'error' not in response_data:
                    # Success? If success get id.
                    if 'statusCode' in response_data:
                        # Failure? If failure build error message.
                        if 'message' in response_data and 'statusCode' in response_data:
                            message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                            raise Exception(message)
                else:
                    # Failure? If failure build error message.
                    if 'message' in response_data and 'statusCode' in response_data:
                        message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                        raise Exception(message)

        # Get response data, check status code returned from uframe. Return error in exception.
        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            # Determine if success or failure.
            if 'error' not in response_data:
                # Success? If success get id.
                if 'statusCode' in response_data:
                    if response_data['statusCode'] == 'CREATED':
                        id = response_data['id']
                    else:
                        message = 'Failed to create remote resource; statusCode from uframe: %s' % \
                                  response_data['statusCode']
                        raise Exception(message)
            else:
                # Failure? If failure build error message.
                if 'message' in response_data and 'statusCode' in response_data:
                    message = response_data['statusCode'] + ': ' + response_data['message']
                    raise Exception(message)

        if id == 0:
            message = 'Failed to create a remote resource for asset with uid %s' % uid
            raise Exception(message)

        # Get newly created event and return.
        remote_resource = uframe_get_remote_resource_by_id(id)
        return remote_resource

    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_update_remote_resource_by_resource_id(resource_id, data):
    try:
        # Put remote resource.
        base_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([base_url, str(resource_id)])
        response = requests.put(url, data=json.dumps(data), headers=headers())
        if response.status_code != 200:
            message = 'Failed to update remote resource in uframe using remoteResourceId: %d.' % resource_id
            if response.content:
                message += ' uframe response status code: %s, %s' % (response.status_code, json.loads(response.content))
            raise Exception(message)

        if not response.content or response.content is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)

        # Get remote resource.
        base_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([base_url, str(resource_id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get remote resource from uframe using remoteResourceId: %d.' % resource_id
            raise Exception(message)

        remote_resource = json.loads(response.content)
        if not remote_resource or remote_resource is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)
        return remote_resource
    except Exception as err:
        message = str(err)
        raise Exception(message)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Cruises.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get cruise inventory.
def uframe_get_cruise_inv():
    """ Get cruise inventory list from uframe.
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises_inv()
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get cruise inventory from uframe.'
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise inventory by subsite from uframe.
def uframe_get_cruise_by_subsite(subsite):
    """ Get cruise inventory list by subsite from uframe.
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises_rec()
        # host:12587/events/cruise/rec/{cruiseid}
        url = '/'.join([url, subsite])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get cruise inventory for \'%s\' from uframe.' % subsite
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise using uniqueCruiseIdentifier.
def uframe_get_cruise_by_cruise_id(cruise_id):
    """ Get all assets from uframe.
    """
    try:
        base_url, timeout, timeout_read = get_url_info_cruises_rec()
        _cruise_id = (urllib.quote(cruise_id, ''))
        url = '/'.join([base_url, _cruise_id])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Unable to get cruise \'%s\' from uframe.' % (response.status_code, cruise_id)
            current_app.logger.info(message)
            return None
        result = response.json()
        if result is None or not result:
            message = 'No cruises found with unique identifier of \'%s\'.' % cruise_id
            raise Exception(message)
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises for cruise id: ', cruise_id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises for cruise id: ', cruise_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get uframe cruise by event id.
def uframe_get_cruise_by_event_id(event_id):
    """ Get cruise by event id.
    """
    try:
        # Get base url with port and timeouts.
        url_base, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([url_base, get_events_url_base(), str(event_id)])
        # Get cruise [event] information from uframe.
        payload = requests.get(url, timeout=(timeout, timeout_read))
        if payload.status_code != 200:
            message = 'Unable to locate a cruise with an id of %d.' % event_id
            raise Exception(message)
        result = payload.json()
        return result

    except ConnectionError:
        message = 'Error: ConnectionError getting cruise with event id %d.' % event_id
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting cruise with event id %d.' % event_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get uframe deployments by cruise id.
def uframe_get_deployments_by_cruise_id(cruise_id, type=None):
    """ Get deployments from uframe for cruise_id (the uniqueCruiseIdentifier).

    Requests to uframe:
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=all           [all=deploy+recover]
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=deploy
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=recover

        http://uframe-test.intra.oceanobservatories.org:12587/events/cruise/deployments/AT-26-29?type=recover
    """
    check = False
    try:
        base_url, timeout, timeout_read = get_url_info_cruises()
        _cruise_id = (urllib.quote(cruise_id, ''))
        url = '/'.join([base_url, 'deployments', _cruise_id])
        if type is not None and type:
            url += '?type=' + type
        if check: print '\n check -- url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
        if payload.status_code == 204:
            # Return None when unknown uid is provided; log invalid request.
            message = 'Unknown cruise id %s, failed to get deployments.' % cruise_id
            current_app.logger.info(message)
            return None

        # If error, raise exception
        elif payload.status_code != 200:
            message = 'Error getting deployments for cruise id %s from uframe.' % cruise_id
            raise Exception(message)

        deployments = payload.json()
        if not deployments or deployments is None:
            deployments = []
        return deployments

    except ConnectionError:
        message = 'ConnectionError getting cruise id %s from uframe.' % cruise_id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting cruise id %s from uframe.' % cruise_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get uframe event by event id.
def uframe_get_event(event_id):
    """ Get an event by eventId
    """
    try:
        url_base, timeout, timeout_read = get_uframe_events_info()
        url = '/'.join([url_base, str(event_id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get uframe event with event id: %d.' % event_id
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe event, event id: %d.' % event_id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe event, event id: %d.' % event_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Deployments.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get deployment inventory.
def uframe_get_deployment_inv():
    """ Get subsites in deployment inventory.
    """
    try:
        url, timeout, timeout_read = get_url_info_deployments_inv()
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get uframe deployment inventory.'
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe deployment inventory.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe deployment inventory.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_deployment_inv_nodes(subsite):
    """ Get uframe deployment inventory nodes given a subsite.
    """
    try:
        base_url, timeout, timeout_read = get_url_info_deployments_inv()
        url = '/'.join([base_url, subsite])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get uframe deployment inventory for subsite \'%s\'.' % subsite
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe deployment inventory for subsite \'%s\'.' % subsite
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe deployment inventory for subsite \'%s\'.' % subsite
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_deployment_inv_sensors(subsite, node):
    """
    """
    check = False
    try:
        base_url, timeout, timeout_read = get_url_info_deployments_inv()
        url = '/'.join([base_url, subsite, node])
        if check: print '\n check -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get uframe deployment inventory for subsite \'%s\' and node \'%s\'.' % (subsite, node)
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe deployment inventory for subsite \'%s\' and node \'%s\'.' % \
                  (subsite, node)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe deployment inventory for subsite \'%s\' and node \'%s\'.' % (subsite, node)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Create deployment in uframe.
def uframe_create_deployment(deployment):
    """ Create deployment in uframe. On success return updated deployment, on error, raise exception.
    """
    check = False
    success = 'CREATED'
    try:
        # Check deployment data provided.
        if not deployment or deployment is None:
            message = 'Deployment data must be provided to create deployment in uframe.'
            raise Exception(message)
        if not isinstance(deployment, dict):
            message = 'Deployment data must be provided in dictionary form to create a deployment in uframe.'
            raise Exception(message)

        # Create deployment in uframe.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_deployments_url_base()])
        if check: print '\n check: url: ', url
        response = requests.post(url, data=json.dumps(deployment), headers=headers())
        if response.status_code != 201:
            message = '(%d) uframe failed to create deployment.' % response.status_code
            if response.content:
                uframe_message = json.loads(response.content)
                if 'message' in uframe_message:
                    uframe_message = uframe_message['message']
                message += ' %s' % uframe_message
            current_app.logger.info(message)
            raise Exception(message)

        # Get id for new deployment.
        if not response.content:
            message = 'No response content returned from create deployment.'
            raise Exception(message)

        # Review response.content:
        #   {u'message': u'Element created successfully.', u'id': 4292, u'statusCode': u'CREATED'}
        response_data = json.loads(response.content)
        id = None
        if 'id' in response_data and 'statusCode' in response_data:
            if response_data['statusCode'] and response_data['id']:
                if response_data['statusCode'] == success and response_data['id'] > 0:
                    id = response_data['id']
        if id is None:
            message = 'Failed to create uframe deployment.'
            raise Exception(message)

        # Get new deployment from uframe.
        new_deployment = get_uframe_event(id)
        if not new_deployment or new_deployment is None:
            message = 'Failed to get deployment with event id %d from uframe.' % id
            raise Exception(message)
        return new_deployment
    except ConnectionError:
        message = 'Error: ConnectionError during uframe create deployment.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout during during uframe create deployment.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# include deployment inventory reference designators.
def compile_deployment_rds():
    """ Get reference designators identified in deployment inventory.
    """
    rds = []
    try:
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment inventory url for uframe
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url, timeout, timeout_read = get_url_info_deployments_inv()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get deployment inventory
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = base_url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get deployment inventory from uframe.'
            raise Exception(message)

        result = json.loads(response.content)
        if result is not None and isinstance(result, list) and len(result) > 0:

            subsite_list = result[:]
            subsite_list.sort()
            set_subsite_list = []
            for subsite in subsite_list:
                if subsite not in set_subsite_list:
                    set_subsite_list.append(subsite)

            for subsite in subsite_list:
                if subsite not in rds:
                    rds.append(subsite)
                # Get deployment/inv/{subsite} (list)
                url = '/'.join([base_url, subsite])
                response = requests.get(url, timeout=(timeout, timeout_read))
                if response.status_code != 200:
                    message = 'Unable to get deployment %s node inventory from uframe.' % subsite
                    raise Exception(message)
                node_list = json.loads(response.content)
                if node_list is not None and isinstance(node_list, list) and len(node_list) > 0:

                    # Verify no duplicates in list of deployment nodes for a subsite.
                    set_node_list = []
                    for item in node_list:
                        if item not in set_node_list:
                            set_node_list.append(item)
                    for node in node_list:
                        # Get deployment/inv/{subsite}/{node} (list)
                        node_rd = '-'.join([subsite, node])
                        if node_rd not in rds:
                            rds.append(node_rd)
                        url = '/'.join([base_url, subsite, node])
                        response = requests.get(url, timeout=(timeout, timeout_read))
                        if response.status_code != 200:
                            message = 'Unable to get deployment %s node inventory from uframe.' % node_rd
                            raise Exception(message)
                        sensor_list = json.loads(response.content)

                        # Verify no duplicates in list of deployment sensors for a subsite/node.
                        for sensor in sensor_list:
                            sensor_rd = '-'.join([subsite, node, sensor])
                            if sensor_rd not in rds:
                                rds.append(sensor_rd)
        if rds:
            rds.sort()
        return rds
    except ConnectionError:
        message = 'Error: ConnectionError during compile_deployment_rds.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout during during compile_deployment_rds.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get deployments digest for asset uid.
def get_deployments_digest_by_uid(uid, editPhase='ALL'):
    """
    http://host:port/asset/deployments/N00123?editphase=ALL (default)
    http://host:port/asset/deployments/N00123?editphase=OPERATIONAL

    http://host:port/asset/deployments/CGCON-GLDRCP-00376?editphase=ALL
    [
        {
          "startTime" : 1412638080000,
          "depth" : null,
          "latitude" : 39.83333,
          "longitude" : -70.70833,
          "node" : "GL376",
          "sensor" : "00-ENG000000",
          "subsite" : "CP05MOAS",
          "deploymentNumber" : 1,
          "node_uid" : "CGVEH-GLDRCP-00376",
          "mooring_uid" : "CGVCP-05MOAS-00000",
          "sensor_uid" : "CGCON-GLDRCP-00376",
          "deployCruiseIdentifier" : "KN-222",
          "recoverCruiseIdentifier" : "KN-224",
          "endTime" : 1418428800000,
          "versionNumber" : 1,
          "editPhase" : "OPERATIONAL",
          "eventId" : 2798,
          "orbitRadius" : null,
          "waterDepth" : null
        },

        Note, to get the asset for the uid, use:
        http://host:port/asset?uid=ATAPL-71403-00002
    """
    check = False
    try:
        # Get uframe deployments by uid.
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        if not editPhase or editPhase is None or editPhase not in deployment_edit_phase_values():
            editPhase = 'ALL'
        suffix = '?editphase=' + editPhase
        url = '/'.join([uframe_url, get_assets_url_base(), 'deployments', uid])
        url = url + suffix
        if check: print '\n check -- [get_deployments_digest_by_uid] url to get asset %s: %s' % (uid, url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get deployments for asset uid \'%s\'.' % uid
            raise Exception(message)
        digest = json.loads(response.content)
        return digest
    except ConnectionError:
        message = 'Error: ConnectionError getting deployments for asset uid \'%s\'.' % uid
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting deployments for asset uid \'%s\'.' % uid
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_rd_deployments(rd):
    """ Get all deployments for reference designator, whether mooring, platform or instrument.

    Use urls such as:
        (http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326-04-DOSTAM000)
         http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326
         http://host:12587/events/deployment/query?refdes=CE05MOAS
         http://host:12587/events/deployment/query?refdes=CP02PMUI
    """
    check = False
    result = []
    try:
        """
        # Verify rd is valid.
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator %s is not a mooring, platform or instrument.' % rd
            current_app.logger.info(message)
            return result
        """
        if rd is None or not rd or len(rd) == 0:
            return result

        # Get uframe deployments request variables
        uframe_url, timeout, timeout_read = get_uframe_deployments_info()

        # Build uframe url: host:port/events/deployment/query?refdes=XXXXXXXX
        url = '/'.join([uframe_url, get_deployments_url_base(), 'query'])
        url += '?refdes=' + rd + '&editphase=ALL'
        #url += '?refdes=' + rd + '&notes=true'
        if check: print '\n Check -- [get_rd_deployments] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get deployments from uframe for %r.' % rd
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Timeout for for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []

# - - - - - - - - - - - - - - - - - - - - - - - - - -
# toc
# - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get toc information from uframe.
def get_toc_information():
    """ Get toc information from uframe. If exception, log error and return empty list.
    """
    extended_read = True
    check = False
    try:
        url, timeout, timeout_read = get_uframe_toc_url()
        if check:
            print '\n check -- get_uframe_toc_url: ', url
        if extended_read:
            timeout_read = timeout_read * 3
            timeout = timeout * 2
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            toc = response.json()
        else:
            message = 'Failure to retrieve toc using url: ', url
            raise Exception(message)
        if toc is not None:
            result = toc
        else:
            message = 'toc returned as None: ', url
            raise Exception(message)
        return result
    except ConnectionError:
        message = 'ConnectionError for get_toc_information'
        #current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get_toc_information'
        #current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        #current_app.logger.info(str(err))
        return []


# - - - - - - - - - - - - - - - - - - - - - - - - - -
# Streams
# - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_get_stream_byname(stream):
    # http://host:12575/stream/byname/cg_cpm_eng_cpm_recovered
    check = False
    url = None
    error = False
    try:
        # Get uframe stream by stream name.
        base_url, timeout, timeout_read = get_url_info_stream_byname()
        url = '/'.join([base_url, stream])
        if check: print '\n check -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get uframe stream \'%s\'.' % stream
            raise Exception(message)
        stream = json.loads(response.content)
        return stream
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe stream name %s.' % stream
        #current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe stream name %s.' % stream
        #current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        if error:
            print '\n Check -- url: ', url
            print 'Check -- message: ', message
            current_app.logger.info(message)
        raise Exception(message)


def uframe_get_parameters():
    """ Get all stream parameters.
    # http://host:12575/parameter
    """
    check = False
    try:
        # Get uframe stream by stream name.
        url, timeout, timeout_read = get_url_info_stream_parameters()
        if check: print '\n check -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get uframe parameters.'
            raise Exception(message)
        parameters = json.loads(response.content)
        return parameters
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe parameters.'
        #current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe parameters.'
        #current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_instrument_metadata_parameters(rd):
    """ Returns the uFrame metadata parameters for a reference designator.
    """
    check = False
    result = []
    try:
        mooring, platform, instrument = rd.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata', 'parameters'])
        if check: print '\n check -- %s' % url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if check: print '\n check -- response.status_code: ', response.status_code
        if response.status_code != 200:
            message = 'Failed to get metadata parameters for \'%s\'. ' % rd
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe metadata parameters for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe metadata parameters for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except:
        message = 'Failed to get metadata parameters for \'%s\'. ' % rd
        raise Exception(message)


def uframe_get_instrument_metadata_times(rd, partition=False):
    """ Returns the uFrame metadata times for a reference designator.
    """
    debug = False
    result = []
    try:
        mooring, platform, instrument = rd.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata', 'times'])
        if partition:
            url += '?partition=true'
        if debug: print '\n debug -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get metadata times for \'%s\'. ' % rd
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe metadata times for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe metadata times for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except:
        message = 'Failed to get metadata times for \'%s\'. ' % rd
        raise Exception(message)


#------------------------------------------------------------------------------------
# Status
#------------------------------------------------------------------------------------
# Get uframe status for reference designator.
def uframe_get_status_by_rd(rd=None):
    """ Get uframe status for a reference designator.
    Sample requests:
        http://host:12587/status/query/CE
        http://host:12587/status/query/CE01ISSM
        http://host:12587/status/query/CE01ISSM-MFC31
        http://host:12587/status/query/CE01ISSM-MFC31-00-CPMENG000

    http://host:12587/status/inv/GA01SUMO/SBD12
    [
        {
          "rd" : "GA01SUMO-SBD12",
          "reason" : null,
          "status" : "notTracked",
          "deployment" : 1
        },
        {
          "rd" : "GA01SUMO-SBD12-01-OPTAAD000",
          "reason" : "Test 0.0.2-Eng",
          "status" : "operational",
          "deployment" : 1
        },
        {
          "rd" : "GA01SUMO-SBD12-04-PCO2AA000",
          "reason" : "Test 0.0.2",
          "status" : "degraded",
          "deployment" : 1
        }
    ]

    http://host:12587/status/query/GA01SUMO/SBD12/04-PCO2AA000
    [
        {
          "rd" : "GA01SUMO-SBD12-04-PCO2AA000",
          "reason" : "Test 0.0.2",
          "status" : "operational",
          "deployment" : 1
        }
    ]

    """
    debug = False
    check = False
    try:
        # Get uframe status by reference designator.
        url, timeout, timeout_read = get_url_info_status_query()

        # Format reference designator for uframe query.
        uframe_rd = None
        if rd is not None:
            if len(rd) > 14:
                site, node, sensor = rd.split('-', 2)
                uframe_rd = '/'.join([site, node, sensor])
            elif len(rd) == 14:
                site, node = rd.split('-')
                uframe_rd = '/'.join([site, node])
            elif len(rd) == 8 or len(rd) == 2:
                uframe_rd = rd
            else:
                message = 'The reference designator provided is malformed (\'%s\').' % rd
                raise Exception(message)

        if debug: print '\n debug -- uframe_get_status_by_rd: ', rd
        if rd is not None:
            url = '/'.join([url, uframe_rd])
        if check: print '\n check -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            return None
        results = json.loads(response.content)
        if debug: print '\n debug -- results: ', results
        return results
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe status for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe status for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def uframe_get_sites_for_array(rd):
    """
    Get /sensor/inv and process for sites matching array rd provided. (Used by status)
    Returns a list of sites for an array code.
    """
    check = False
    result = []
    try:
        if not rd or rd is None:
            message = 'Invalid reference designator (\'%s\') provided to get sites from uframe sensor inventory.' % rd
            current_app.logger.info(message)
            return []
        url, timeout, timeout_read = get_uframe_info()
        if check: print '\n check -- %s' % url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get sensor inventory for \'%s\'. ' % rd
            raise Exception(message)
        if response.content:
            sites = json.loads(response.content)
            if sites:
                for site in sites:
                    if site[:3] == rd:
                        result.append(site)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Error: Timeout getting uframe sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []
    except:
        message = 'Failed to get sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []


# Get nodes for a site reference designator
def uframe_get_nodes_for_site(rd):
    """
    Get /sensor/inv and process for platforms for site name provided. (Used by status)
    For a site reference designator (subsite), get list of platforms (subsite-node).
    """
    check = False
    result = []
    try:
        if not rd or rd is None or len(rd) != 8:
            message = 'Invalid site (\'%s\') provided for platforms from uframe sensor inventory.' % rd
            current_app.logger.info(message)
            return []
        base_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([base_url, rd])
        if check: print '\n check -- %s' % url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get sensor inventory for \'%s\'. ' % rd
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Error: Timeout getting uframe sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []
    except:
        message = 'Failed to get sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []


# Get sensors for a platform reference designator
def uframe_get_sensors_for_platform(rd):
    """
    Get /sensor/inv and process for platforms for site name provided. (Used by status)
    For a site reference designator (subsite-node), get list of sensors (subsite-node).
    """
    check = False
    result = []
    try:
        if not rd or rd is None or len(rd) != 14:
            message = 'Invalid site (\'%s\') provided for platforms from uframe sensor inventory.' % rd
            current_app.logger.info(message)
            return []
        rd = rd.replace('-', '/')
        base_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([base_url, rd])
        if check: print '\n check -- %s' % url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get sensor inventory for \'%s\'. ' % rd
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Error: Timeout getting uframe sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []
    except:
        message = 'Failed to get sensor inventory for \'%s\'. ' % rd
        current_app.logger.info(message)
        return []


# Development. Dump stream and list of parameter names for each stream.
def get_uframe_streams():
    from ooiservices.app.uframe.config import (get_uframe_stream_info, get_stream_url_base)
    check = False
    result = []
    try:
        #timeout, timeout_read = get_uframe_timeout_info()
        url, timeout, timeout_read = get_uframe_stream_info()
        uframe_url = '/'.join([url, get_stream_url_base() ])
        if check: print '\n Check: ', uframe_url
        response = requests.get(uframe_url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get streams.'
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting stream information.'
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Error: Timeout getting getting stream information.'
        current_app.logger.info(message)
        return []
    except:
        message = 'Failed to get stream information.'
        current_app.logger.info(message)
        return []


# Get data availability from uframe for reference designator and parameters.
def uframe_get_da_by_rd(rd, params=None):
    """ Get asset from uframe by asset id.
    """
    debug = False
    try:
        # Get uframe asset
        timeout, timeout_read = get_uframe_timeout_info()
        url = '/'.join([get_url_da_info(), 'available', rd])
        if debug: print '\n debug -- uframe_get_da_by_rd: url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read), headers=headers(), params=params)
        if response.status_code != 200:
            message = 'Failed to get data availability from uframe for reference designator: %s.' % rd
            raise Exception(message)
        asset = response.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting data availability from uframe for reference designator: %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting data availability from uframe for reference designator: %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def uframe_get_versions(component=None):
    """
    Return version information, for component if provided.
    https://redmine.oceanobservatories.org/projects/ooi/wiki/Version_Service
    """
    check = False
    result = []
    try:
        url, timeout, timeout_read = get_uframe_versions_url()
        if component is not None:
            url = '/'.join([url, component, 'latest'])
        if check: print '\n (uframe_get_versions) check -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get uframe latest version.'
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe latest version'
        if component is not None:
            message += ' for component %s.' % component
        else:
            message += '.'
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting getting uframe latest version'
        if component is not None:
            message += ' for component %s.' % component
        else:
            message += '.'
        raise Exception(message)

    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_versions_list(component=None):
    """
    Return version information, for component if provided.
    https://redmine.oceanobservatories.org/projects/ooi/wiki/Version_Service
    """
    check = False
    result = []
    try:
        if component is None:
            message = 'A component is required to get uframe list of versions for the component.'
            raise Exception(message)
        url, timeout, timeout_read = get_uframe_versions_url()
        url = '/'.join([url, component])
        if check: print '\n (uframe_get_versions_list) check -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get uframe component %s versions.' % component
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe component %s versions.' % component
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting getting uframe component %s versions.' % component
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_component_version(component=None, version=None):
    """
    Return component version details for component and version provided.
    https://redmine.oceanobservatories.org/projects/ooi/wiki/Version_Service
    http://uframe-test.intra.oceanobservatories.org:12590/versions/uFrame/1.2.7
    {
      "component" : "uFrame",
      "version" : "1.2.7",
      "release" : "2017-09-00",
      "notes" : [ "Develop a strategy for separately deploying uFrame software on test systems. (12557)", "Prevent creating/updating annotations where beginDT > endDT. (12509)", "Add support for open-ended annotations. (11444)", "Add virtual streams to stream and partition metadata on ingest. (12488)", "Handle \"PD\" prefix in alert filter pdIds. (12172)", "Enhance ingestion logging in EDEX. (12618)", "Uncabled_ingest mode unable to start. (12581)", "Gracefully handle error in Sensor Inventory Service TOC endpoint. (12546)", "Fix DOI SQL Errors on uframe-test and production. (12580)", "Add version endpoint. (12497)" ]
    }
    """
    check = False
    result = []
    try:
        # Check input values.
        if component is None:
            message = 'A valid component is required to obtain release information.'
            raise Exception(message)
        if version is None:
            message = 'A valid version is required to obtain release information for component \'%s\'.' % component
            raise Exception(message)

        url, timeout, timeout_read = get_uframe_versions_url()
        url = '/'.join([url, component, version])
        if check: print '\n (uframe_get_component_version) check -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get uframe release information'
            message += ' for component %s and version %s.' % (component, version)
            raise Exception(message)
        if response.content:
            result = json.loads(response.content)
        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe release information'
        message += ' for component %s and version %s.' % (component, version)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting getting uframe release information'
        message += ' for component %s and version %s.' % (component, version)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)





