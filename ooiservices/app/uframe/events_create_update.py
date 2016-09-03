"""
Events: Create and update functions.
"""

__author__ = 'Edna Donoughe'

from flask import current_app
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app.uframe.event_tools import get_uframe_event
from ooiservices.app.uframe.asset_tools import uframe_get_asset_by_uid
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_event_types, get_event_class)
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base,
                                           headers, get_url_info_cruises, get_uframe_info_calibration)
from ooiservices.app.uframe.events_validate_fields import (events_validate_all_required_fields_are_provided,
                                                           events_validate_user_required_fields_are_provided)
import json
import requests


# Create event.
def create_event_type(request_data):
    """ Create a new event. Return new event on success, or raise exception on error.

    Response on success:
    {
        "message" : "Element created successfully.",
        "id" : 14501,
        "statusCode" : "CREATED"
    }
    """
    event_type = None
    action = 'create'
    try:
        # Verify minimum required fields to proceed with create (event_type and uid)
        # Required field: event_type
        if 'eventType' not in request_data:
            message = 'No eventType in request data to create event.'
            raise Exception(message)
        event_type = request_data['eventType']
        if event_type not in get_event_types():
            message = 'The event type provided %s is invalid.' % event_type
            raise Exception(message)

        # If event type create/update not yet supported, raise exception.
        if event_type not in get_supported_event_types():
            message = 'Event type %s \'%s\' is not supported.' % (event_type, action)
            raise Exception(message)

        # Required field: assetUid
        uid = None
        if event_type != 'CRUISE_INFO':
            if 'assetUid' not in request_data:
                message = 'No assetUid in request data to create event %s.' % event_type
                raise Exception(message)
            uid = request_data['assetUid']
            if not uid:
                message = 'The assetUid is empty or null, unable to create a %s event.' % event_type
                raise Exception(message)

        # Validate data fields to ensure required fields are provided for create.
        data = events_validate_all_required_fields_are_provided(event_type, request_data, action=action)
        events_validate_user_required_fields_are_provided(event_type, data, action=action)

        # Add '@class' field to data; remove 'lastModifiedTimestamp' field; ensure eventId is set to -1.
        # Get event class
        event_class = get_event_class(event_type)
        data['@class'] = event_class
        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']
        # Set eventId for create
        data['eventId'] = -1

        # Create event.
        id = perform_uframe_create_event(event_type, uid, data)
        if id == 0:
            message = 'Failed to create %s event for asset with uid %s' % (event_type, uid)
            raise Exception(message)

        # Get newly created event and return.
        event = get_uframe_event(id)
        return event

    except ConnectionError as err:
        message = 'ConnectionError during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Timeout as err:
        message = 'Timeout during create %s event, %s.' % (event_type, str(err))
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Update event.
def update_event_type(id, data):
    """ Update an existing event, no success return event, on error raise exception.
    """
    event_type = None
    action = 'update'
    try:
        # Verify minimum required fields to proceed with update (event_type and uid)
        # Required field: event_type
        if 'eventType' not in data:
            message = 'An event type must be provided in the request data.'
            raise Exception(message)

        # Get event type, verify if valid event type.
        event_type = data['eventType']
        if event_type not in get_event_types():
            message = 'The event type provided %s is invalid.' % event_type
            raise Exception(message)

        # If event type create/update not yet supported, raise exception.
        if event_type not in get_supported_event_types():
            message = 'Event type %s \'%s\' is not supported.' % (event_type, action)
            raise Exception(message)

        # Validate data fields to ensure required fields are provided for update.
        data = events_validate_all_required_fields_are_provided(event_type, data, action=action)
        events_validate_user_required_fields_are_provided(event_type, data, action=action)

        # Verify uid provided in data for all event types except CRUISE_INFO.
        uid = None
        if event_type != 'CRUISE_INFO':
            # Required field: assetUid
            if 'assetUid' not in data:
                message = 'No assetUid in request data to update event %s.' % event_type
                raise Exception(message)
            uid = data['assetUid']
            if not uid:
                message = 'The assetUid provided is empty or null, unable to update event %s.' % event_type
                raise Exception(message)

        # Get event class
        event_class = get_event_class(event_type)

        # Add @class field to data
        data['@class'] = event_class

        # Get configuration url and timeout information, build request url.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(id)])

        # Issue uframe PUT to update, process response status_code and content.
        response = requests.put(url, data=json.dumps(data), headers=headers())
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

        # Get updated event, return event
        event = get_uframe_event(id)
        return event

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


def perform_uframe_create_event(event_type, uid, data):
    """ Create event using uframe interface determined by event type.
    """
    try:
        # Create cruise_info event using/events/cruise POST
        if event_type == 'CRUISE_INFO':
            id = uframe_create_cruise(event_type, data)

        # Create calibration_data event
        elif event_type == 'CALIBRATION_DATA':
            id = create_calibration_data_event(event_type, uid, data)

        # Create event using /events/postto/uid POST
        else:
            id = uframe_postto(event_type, uid, data)

        return id

    except Exception as err:
        message = str(err)
        raise Exception(message)


def create_calibration_data_event(event_type, uid, data):
    success_codes = [201, 204]
    try:
        # create calibration data using /assets/cal POST
        event_name = None
        if 'eventName' in data:
            event_name = data['eventName']
        if calibration_data_exists(uid, event_name):
            message = 'Calibration data event name \'%s\' exists for asset with uid \'%s\'.' % (event_name, uid)
            raise Exception(message)
        status_code = uframe_create_calibration(event_type, uid, data)
        if status_code not in success_codes:
            message = 'Failed to create calibration data for asset uid \'%s\', event name \'%s\'.' % (uid, event_name)
            raise Exception(message)

        # Get eventId for calibration data event where eventName is event_name and asset uid is uid.
        id, _ = get_calibration_event_id(uid, event_name)
        return id

    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_calibration_event_id(uid, event_name):
    """
    "calibration" : [ {
        "@class" : ".XCalibration",
        "name" : "CC_a1",
        "calData" : [ {
          "@class" : ".XCalibrationData",
          "values" : [ -1.493703E-4 ],
          "dimensions" : [ 1 ],
          "cardinality" : 0,
          "comments" : "Test entry",
          "eventId" : 31534,
          "assetUid" : "A01682",
          "eventType" : "CALIBRATION_DATA",
          "eventName" : "CC_a1",
          "eventStartTime" : 1443614400000,
          "eventStopTime" : null,
          "notes" : null,
          "tense" : "UNKNOWN",
          "dataSource" : "API:createCalibration:2016-08-31T22:37:22.096Z",
          "lastModifiedTimestamp" : 1472683042096
        } ]
      } ],
    """
    id = None
    last_modified = None
    try:
        asset = uframe_get_asset_by_uid(uid)
        calibrations = asset['calibration']
        for cal in calibrations:
            if 'name' in cal:
                if cal['name'] == event_name:
                    # Get eventId
                    if 'calData' in cal:
                        for item in cal['calData']:
                            if 'eventId' in item:
                                id = item['eventId']
                                last_modified = item['lastModifiedTimestamp']
                                break
        if id is None:
            message = 'Failed to locate calibration name \'%s\' in asset with uid %s.' % (event_name, uid)
            raise Exception(message)

        return id, last_modified

    except Exception as err:
        message = str(err)
        raise Exception(message)


def calibration_data_exists(uid, event_name):
    """ Determine if calibration data contains event name. Return True or False.
    """
    result = False
    try:
        try:
            event_id, _ = get_calibration_event_id(uid, event_name)
        except:
            event_id = 0
        if event_id > 0:
            result = True
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


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
            message = 'Failed to create %s event in uframe; status code: %d' % (event_type, response.status_code)
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
