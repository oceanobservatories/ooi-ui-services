"""
Asset Management - Events: Create and update functions.
"""

__author__ = 'Edna Donoughe'

from ooiservices.app.uframe.uframe_tools import (uframe_get_asset_by_uid, get_uframe_event, uframe_put_event,
                                                 uframe_postto, uframe_create_cruise, uframe_create_calibration)
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_event_types, get_event_class)
from ooiservices.app.uframe.events_validate_fields import (events_validate_all_required_fields_are_provided,
                                                           events_validate_user_required_fields_are_provided)

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
        id = 0
        id = perform_uframe_create_event(event_type, uid, data)
        if id < 1:
            message = 'Failed to create %s event for asset with uid %s' % (event_type, uid)
            raise Exception(message)

        # Get newly created event and return.
        event = get_uframe_event(id)

        # Post process event content for display.
        event = post_process_event(event)

        return event
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


# Update event.
def update_event_type(id, data):
    """ Update an existing event, no success return event, on error raise exception.
    """
    debug = False
    action = 'update'
    try:
        # Verify minimum required fields to proceed with update (event_type and uid)
        if 'eventId' not in data:
            message = 'An event id must be provided in the request data.'
            raise Exception(message)

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
        if event_type != 'CRUISE_INFO' and event_type != 'DEPLOYMENT':
            # Required field: assetUid
            if 'assetUid' not in data:
                message = 'No assetUid in request data to update event %s.' % event_type
                raise Exception(message)
            uid = data['assetUid']
            if not uid or uid is None:
                message = 'The assetUid provided is empty or null, unable to update event %s.' % event_type
                raise Exception(message)

        # Verify eventId provided and of type int.
        # Required field: eventId
        if 'eventId' not in data:
            message = 'No eventId in request data to update event %s.' % event_type
            raise Exception(message)
        if not isinstance(data['eventId'], int):
            message = 'The event id value (%r) must be an integer, it is type: %s' % \
                      (data['eventId'], str(type(data['eventId'])))
            raise Exception(message)
        if data['eventId'] != id:
            message = 'The event id (\'%r\') provided in data is not equal to id (%d) in url.' % (data['eventId'], id)
            raise Exception(message)

        # Get event class and add @class field to data
        event_class = get_event_class(event_type)
        data['@class'] = event_class

        # Update event in uframe
        updated_id = uframe_put_event(event_type, id, data)
        if updated_id <= 0:
            message = 'Failed to update %s event in uframe for id %d.' % (event_type, id)
            raise Exception(message)

        if updated_id != id:
            message = 'The event id returned from event update (%d) is not equal to original id (%d).' % (updated_id, id)
        # Get updated event, return event
        event = get_uframe_event(id)
        return event

    except Exception as err:
        message = str(err)
        raise Exception(message)


def perform_uframe_create_event(event_type, uid, data):
    """ Create event using uframe interface determined by event type.
    """
    try:
        if event_type != 'CRUISE_INFO':
            if uid is None or not uid:
                message = 'Unable to create %s event for asset with uid: \'%s\'.' % (event_type, uid)
                raise Exception(message)

        # Create cruise_info event using/events/cruise POST
        if event_type == 'CRUISE_INFO':
            id = uframe_create_cruise(event_type, data)

        # Create calibration_data event
        elif event_type == 'CALIBRATION_DATA':
            if not isinstance(data['eventId'], int):
                message = 'The event id value (%r) must be an integer, it is type: %s' % \
                          (data['eventId'], str(type(data['eventId'])))
                raise Exception(message)
            id = create_calibration_data_event(event_type, uid, data)

        # Create event using /events/postto/uid POST
        else:
            if event_type == 'DEPLOYMENT':
                message = 'Create event type DEPLOYMENT is not supported at this time.'
                raise Exception(message)

            id = uframe_postto(event_type, uid, data)

        if id is None or id <= 0:
            message = 'Failed to create and retrieve event from uframe for asset uid: \'%s\'. ' % uid
            raise Exception(message)
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