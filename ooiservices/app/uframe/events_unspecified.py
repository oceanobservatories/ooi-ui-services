"""
Events: Unspecified event create and update functions.

Event Type UNSPECIFIED

{
  "@class" : ".XEvent",
  "eventId" : -1,                    Reserved - (-1 or null for Create)
  "eventType" : "UNSPECIFIED",       Mandatory -
  "eventStartTime" : null,           Suggested for most events.
  "eventStopTime" : null,            Optional for most events.
  "notes" : null,                    Optional
  "eventName" : null,                Suggested
  "tense" : "UNKNOWN",               Readonly from api
  "dataSource" : null,               Suggested - Identifies the source of this edit. "UI:user=username" for example
  "lastModifiedTimestamp" : null     Reserved - Not specified for create; required in values for modify.
}


"""

# todo - Review create and update when uframe adds uid attribute to base event type. IMPORTANT

from flask import current_app
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base, headers)
import json
import requests

DATA_CLASS = '.XEvent'
EVENT_TYPE = 'UNSPECIFIED'


# Create unspecified event.
def create_event_unspecified(uid, data):
    """ Create a new unspecified event. Return success or error message.

    Sample request - create event of type unspecified for uid=A000416, using /uframe/event:

    curl -H "Content-Type: application/json" -X POST --upload-file new_event_unspecified_uid391.txt localhost:4000/uframe/event
    Sample request.data (new_event_unspecified_uid391.txt):
    {
        "eventName": "CP02PMUO-WFP01-00-WFPENG000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "UNSPECIFIED",
        "notes": "Test unspecified event for CP02PMUO-WFP01-00-WFPENG000:1:1 instrument:A00391.1",
        "dataSource": null,
        "tense": null,
        "uid": "A00391.1"
    }
    Add '@class' and 'eventId'; data sent to uframe.

    Sample uframe curl command to test uframe events postto:
    curl -H "Content-Type: application/json" -X POST --upload-file new_event_unspecified_uid391_uframe.txt
        uframe-3-test.ooi.rutgers.edu:12587/events/postto/A00391.1

    Add '@class' and 'eventId'; data sent to uframe:
    {
        "@class": ".XEvent",
        "dataSource": null,
        "eventId": -1,
        "eventName": "CP02PMUO-WFP01-00-WFPENG000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "UNSPECIFIED",
        "notes": "Updated unspecified event for CP02PMUO-WFP01-00-WFPENG000 A00391.1",
        "tense": "UNKNOWN"
    }
    Response on success:
    {
        "message" : "Element created successfully.",
        "id" : 14501,
        "statusCode" : "CREATED"
    }

    """
    event_type = EVENT_TYPE
    debug = False
    check = False
    try:
        if debug: print '\n debug -- create %s event....validate fields...' % event_type
        # Validate data fields to ensure required fields are provided for create.
        validate_required_fields_are_provided(data, action='create')

        # Add '@class' field to data; remove 'lastModifiedTimestamp' field; ensure eventId is set to -1.
        data['@class'] = DATA_CLASS
        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']

        # Set eventId for create
        data['eventId'] = -1

        # Set uframe query parameter, get configuration url and timeout information, build request url.
        query = 'postto'
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), query, uid ])
        if check: print '\n check -- url: ', url
        response = requests.post(url, data=json.dumps(data), headers=headers())
        if debug: print '\n debug -- response.status_code: ', response.status_code
        if response.status_code != 201:
            message = 'Failed to create %s event; status code: %d' % (event_type, response.status_code)
            raise Exception(message)

        # Get response data, check status code returned from uframe.
        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            if debug:
                print '\n debug -- response_data: ', response_data
                if isinstance(response_data, dict):
                    print '\n debug -- response_data.keys(): ', response_data.keys()
            # Determine if success or failure.
            if 'error' not in response_data:
                # Success? If success get id.
                if 'statusCode' in response_data:
                    if response_data['statusCode'] == 'CREATED':
                        id = response_data['id']
                        if debug: print '\n debug -- Created %s event for uid %s, id is: %d' % (event_type, uid, id)
                    else:
                        message = 'Failed to create %s event; statusCode from uframe: %s' % \
                                  (event_type, response_data['statusCode'])
                        if debug: print '\n debug -- ', message
                        raise Exception(message)
            else:
                # Failure? If failure build error message.
                if 'message' in response_data:
                    message = response_data['error'] + ': ' + response_data['message']
                    if debug: print '\n debug -- ', message
                    raise Exception(message)

        return id

    except ConnectionError as err:
        message = "ConnectionError (from uframe) during create %s event;  %s." % (event_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = "Timeout (from uframe) during create %s event;  %s." % (event_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = "Error during create %s event; %s." % (event_type, str(err))
        if debug: print '\n debug -- message: ', message
        #current_app.logger.info(message)
        raise Exception(message)


# Update event of type unspecified.
def update_event_unspecified(id, uid, data):
    """ Update an existing unspecified event.

    Sample request - create event of type unspecified for uid=A000416, using /uframe/event/{event_id}
    Sample request.data from UI::
    {
        "dataSource": null,
        "eventId": 14501,
        "eventName": "CP02PMUO-WFP01-00-WFPENG000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "UNSPECIFIED",
        "lastModifiedTimestamp": 1469434166813,
        "notes": "Update for unspecified event for CP02PMUO-WFP01-00-WFPENG000 A00391.1",
        "tense": "UNKNOWN",
        "uid": "A00391.1"
    }

    Add '@class' and sent to uframe....
    curl -H "Content-Type: application/json" -X PUT --upload-file update_event_unspecified_uid391.txt localhost:4000/uframe/events/14500
    sample request data for uid 391.1 (new_event_unspecified_uid391.txt)
    {
        "@class": ".XEvent"
        "dataSource": null,
        "eventId": 14501,
        "eventName": "CP02PMUO-WFP01-00-WFPENG000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "UNSPECIFIED",
        "lastModifiedTimestamp": 1469434166813,
        "notes": "Update for unspecified event for CP02PMUO-WFP01-00-WFPENG000 A00391.1",
        "tense": "UNKNOWN",
        "uid": "A00391.1"
    }
    Sample uframe response on success:
    {"id": 14501}

    Sample uframe response on error:
    {
      "error": "bad request",
      "message": "Invalid control character at: line 11 column 38 (char 405)"
    }
    """
    event_type = EVENT_TYPE
    debug = False
    check = False
    try:
        if debug: print '\n debug -- entered update %s event...' % event_type
        # Validate data fields to ensure required fields are provided for update.
        validate_required_fields_are_provided(data, action='update')

        # Add @class field to data
        data['@class'] = DATA_CLASS

        # Get configuration url and timeout information, build request url.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(id)])
        if check: print '\n check -- url: ', url
        response = requests.put(url, data=json.dumps(data), headers=headers())
        if debug: print '\n debug -- response.status_code: ', response.status_code
        if response.status_code != 200:
            if response.content is None:
                message = 'Failed to create %s event; status code: %d' % (event_type, response.status_code)
                if debug: print '\n exception debug -- ', message
                raise Exception(message)
            elif response.content is not None:
                response_data = json.loads(response.content)
                if debug: print '\n debug -- data: ', json.dumps(response_data, indent=4, sort_keys=True)
                # Determine if success or failure.
                if 'error' not in response_data:
                    # Success? If success get id.
                    if 'statusCode' in response_data:
                        # Failure? If failure build error message.
                        if 'message' in response_data and 'statusCode' in response_data:
                            message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                            if debug: print '\n exception debug -- ', message
                            raise Exception(message)
                else:
                    # Failure? If failure build error message.
                    if 'message' in response_data and 'statusCode' in response_data:
                        message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                        if debug: print '\n exception debug -- ', message
                        raise Exception(message)

        # Get response data, check status code returned from uframe.
        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            if debug:
                print '\n debug -- response_data: ', response_data
                if isinstance(response_data, dict):
                    print '\n debug -- response_data.keys(): ', response_data.keys()

            # Determine if success or failure.
            if 'error' not in response_data:
                # Success? If success get id.
                if 'id' in response_data:
                    id = response_data['id']
                    if debug: print '\n debug -- Update %s event for uid %s, id is: %d' % (event_type, uid, id)
            else:
                # Failure? If failure build error message.
                if 'message' in response_data:
                    message = response_data['error'] + ': ' + response_data['message']
                    if debug: print '\n debug -- ', message
                    raise Exception(message)

        return id

    except ConnectionError as err:
        message = "ConnectionError (from uframe) during update %s event; %s." % (event_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = "Timeout (from uframe) during update %s event; %s." % (event_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = "Error during update %s event; %s." % (event_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)


# todo - Verify fields required for uframe create and update.
# todo - Review updated documentation (received: 2016-07-21)
# todo - Review again when uframe adds uid to base event type. IMPORTANT
def validate_required_fields_are_provided(data, action=None):
    """ Verify required fields are present in the data and each field has input data of correct type.

    Sample unspecified event request data for create ('@class' and 'eventId' added during processing.
    {
      "@class" : ".XEvent",
      "eventId" : -1,                    Reserved - (-1 or null for Create)
      "eventType" : "UNSPECIFIED",       Mandatory -
      "eventStartTime" : null,           Suggested for most events.
      "eventStopTime" : null,            Optional for most events.
      "notes" : null,                    Optional
      "eventName" : null,                Suggested
      "tense" : "UNKNOWN",               Readonly from api
      "dataSource" : null,               Suggested - Identifies the source of this edit. "UI:user=username" for example
      "lastModifiedTimestamp" : null     Reserved - Not specified for create; required in values for modify.
    }

    Add following fields and send to uframe:
        "@class": ".XStorageEvent",
        "eventId:": -1,

    Sample unspecified event from uframe: [Review when uframe provides uid in event base class.]
    request:    http://localhost:4000/uframe/events/14495
    response:
    {
      "@class": ".XStorageEvent",
      "buildingName": "Tower",
      "dataSource": null,
      "eventId": 14495,
      "eventName": "CP02PMUO-WFP01-00-WFPENG000",
      "eventStartTime": "2014-04-20T20:11:00",
      "eventStopTime": "2014-07-14T20:00:00",
      "eventType": "STORAGE",
      "notes": "This is another test storage event against CP02PMUO-WFP01-00-WFPENG000:1:1 instrument:A00391.1",
      "performedBy": "Edna Donoughe, RPS ASA",
      "physicalLocation": "Narragansett, RI",
      "roomIdentification": "23",
      "shelfIdentification": "Cube 7-21",
      "tense": "UNKNOWN"
      "uid": "A00391.1"                           # Review - uid currently NOT provided by uframe. **********
    }

    Remove "@class" from uframe event before returning response for display.

    Review valid fields:
    valid_fields = ['@class', 'eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                    'lastModifiedTimestamp', 'notes', 'dataSource', 'tense']
    """
    event_type = EVENT_TYPE.lower()
    actions = ['create', 'update']

    # Fields required (from UI) for uframe create STORAGE event.
    required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'notes', 'dataSource', 'tense', 'uid']


    field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'int', 'eventStopTime': 'int', 'eventType': 'string',
                    'lastModifiedTimestamp': 'int', 'notes': 'string', 'dataSource': 'string',
                     'tense': 'string', 'uid': 'string'}
    update_additional_fields = ['eventId', 'lastModifiedTimestamp']

    number_of_required_fields = len(required_fields)
    number_of_data_fields = len(data.keys())
    try:
        if action is None:
            message = 'Action value of \'create\' or \'update\' required to validate %s event fields.' % event_type
            raise Exception(message)

        if action not in actions:
            message = 'Valid action value of \'create\' or \'update\' required to validate %s event fields.' % event_type
            raise Exception(message)

        if action == 'update':
            required_fields += update_additional_fields

        # Verify required fields are present in the data and each field has input data of correct type.
        for field in required_fields:
            # Verify field is provided in data
            if field not in data:
                message = 'required field %s not provided in request.data.' % field
                raise Exception(message)
            # Verify field value in data is of expected type.
            if field_types == 'string':
                if not isinstance(data[field], str):
                    message = 'required field %s provided, but value is not of type %s.' % (field, field_types(field))
                    raise Exception(message)
            elif field_types == 'int':
                if not isinstance(data[field], int):
                    message = 'required field %s provided, but value is not of type %s.' % (field, field_types(field))
                    raise Exception(message)

        # Determine if 'extra' fields are being provided in the data, if so, report in log.
        extra_fields = []
        if number_of_data_fields != number_of_required_fields:
            data_fields = data.keys()
            for field in data_fields:
                if field not in required_fields:
                    if field not in extra_fields:
                        extra_fields.append(field)

        if extra_fields:
            message = 'data contain extra fields %s, ' % extra_fields
            message += 'correct and re-submit create %s event request.' % event_type
            raise Exception(message)

        return

    except Exception as err:
        message = str(err)
        raise Exception(message)
