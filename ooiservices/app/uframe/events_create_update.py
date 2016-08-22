"""
Events: Create and update functions.
"""

__author__ = 'Edna Donoughe'

from flask import current_app
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app.uframe.event_tools import get_uframe_event
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_event_types, get_event_class)
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base, headers)
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
        if 'assetUid' not in request_data:
            message = 'No assetUid in request data to create event %s.' % event_type
            raise Exception(message)
        uid = request_data['assetUid']
        if not uid:
            message = 'The assetUid is empty or null, unable to create an event.'
            raise Exception(message)

        # Get event class
        event_class = get_event_class(event_type)

        # Validate data fields to ensure required fields are provided for create.
        data = events_validate_all_required_fields_are_provided(event_type, request_data, action=action)
        events_validate_user_required_fields_are_provided(event_type, data, action=action)

        # Add '@class' field to data; remove 'lastModifiedTimestamp' field; ensure eventId is set to -1.
        data['@class'] = event_class
        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']
        # Set eventId for create
        data['eventId'] = -1

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

        # Verify minimum required fields to proceed with update (event_type and uid)
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
        current_app.logger.info(message)
        raise Exception(message)