"""
Events: integration event create and update functions.

Event Type INTEGRATION

{
  "@class" : ".XIntegrationEvent",
  "integrationInto" : null,          Suggested
  "deploymentNumber" : null,         Suggested
  "versionNumber" : null,            Suggested
  "integratedBy" : null,             Suggested
  "eventId" : -1,                    Reserved - (-1 or null for Create)
  "eventType" : "INTEGRATION",      Mandatory -
  "eventStartTime" : null,           Suggested for most events.
  "eventStopTime" : null,            Optional for most events.
  "notes" : null,                    Optional
  "eventName" : null,                Suggested
  "tense" : "UNKNOWN",               Readonly from api
  "dataSource" : null,               Suggested - Identifies the source of this edit. "UI:user=username" for example
  "lastModifiedTimestamp" : null     Reserved - Not specified for Create/Use returned value for modify.
}


"""

# todo - Review create and update when uframe adds uid attribute to base event type. IMPORTANT

from flask import current_app
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base, headers)
import json
import requests

DATA_CLASS = '.XIntegrationEvent'
EVENT_TYPE = 'INTEGRATION'


# Create integration event.
def create_event_integration(uid, data):
    """ Create a new integration event. Return success or error message.

    Sample request - create event of type integration for uid=A000416, using /uframe/event:

    curl -H "Content-Type: application/json" -X POST --upload-file new_event_integration_uid391.txt localhost:4000/uframe/event
    Sample request.data (new_event_integration_uid391.txt):
    {
        "integrationInto" : null,
        "deploymentNumber" : 1,
        "versionNumber" : 1,
        "integratedBy" : null,
        "eventType" : "INTEGRATION",
        "eventName" : "New integration events for CP02PMUO-WFP01-00-WFPENG000, uid A00391.1 ",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "notes" : "CP02PMUO-WFP01-00-WFPENG000",
        "tense" : "UNKNOWN",
        "dataSource" : null,
        "uid": "A00391.1"
    }


    Add '@class' and 'eventId'; send data to uframe.
    {
        "@class" : ".XIntegrationEvent",
        "integrationInto" : null,
        "deploymentNumber" : null,
        "versionNumber" : null,
        "integratedBy" : null,
        "eventType" : "INTEGRATION",
        "eventName" : null,
        "eventStartTime" : null,
        "eventStopTime" : null,
        "notes" : null,
        "tense" : "UNKNOWN",
        "dataSource" : null,
        "eventId": -1
    }


    Sample uframe curl command to test uframe events postto:
    curl -H "Content-Type: application/json" -X POST --upload-file new_event_integration_uid391_uframe.txt uframe-3-test.ooi.rutgers.edu:12587/events/postto/A00391.1
    Add '@class' and 'eventId'; send data to uframe:
    {
      "@class" : ".XIntegrationEvent",
      "integrationInto" : null,
      "deploymentNumber" : 1,
      "versionNumber" : 1,
      "integratedBy" : null,
      "eventId" : 14530,
      "eventType" : "INTEGRATION",
      "eventName" : "New integration events for CP02PMUO-WFP01-00-WFPENG000, uid A00391.1 ",
      "eventStartTime" : 1398039060000,
      "eventStopTime" : 1405382400000,
      "notes" : "CP02PMUO-WFP01-00-WFPENG000",
      "tense" : "UNKNOWN",
      "dataSource" : null,
      "lastModifiedTimestamp" : 1469464531545
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
        if debug: print '\n debug -- after validate fields...'

        # Add '@class' field to data; remove 'lastModifiedTimestamp' field; ensure eventId is set to -1.
        data['@class'] = DATA_CLASS
        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']
        # Set eventId for create
        data['eventId'] = -1


        if debug: print '\n debug -- data: ', json.dumps(data, indent=4, sort_keys=True)
        """
        If eventName is null, uframe throws error.eventName is set to null.
        Error (note - no 'error' in response_data when error occurs in uframe.)
        {
          "message" : "Error creating element: not-null property references a null or transient value: com.raytheon.uf.common.ooi.dataplugin.xasset.events.AssetStatusEvent.eventName; nested exception is org.hibernate.PropertyValueException: not-null property references a null or transient value: com.raytheon.uf.common.ooi.dataplugin.xasset.events.AssetStatusEvent.eventName",
          "id" : null,
          "statusCode" : "INTERNAL_SERVER_ERROR"
        }
        """


        # Set uframe query parameter, get configuration url and timeout information, build request url.
        query = 'postto'
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), query, uid ])
        if check: print '\n check -- url: ', url
        response = requests.post(url, data=json.dumps(data), headers=headers())
        if debug: print '\n debug -- response.status_code: ', response.status_code
        if response.status_code != 201:
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
                if 'message' in response_data and 'statusCode' in response_data:
                    message = response_data['statusCode'] + ': ' + response_data['message']
                    if debug: print '\n exception debug -- ', message
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


# Update event of type integration.
def update_event_integration(id, uid, data):
    """ Update an existing integration event.

    Sample request - update event of type integration for uid=A000416, using /uframe/event/{event_id}
    Sample request.data from UI:
    {
      "integrationInto" : null,
      "deploymentNumber" : 1,
      "versionNumber" : 1,
      "integratedBy" : "Engineer, RPS ASA",
      "eventId" : 14530,
      "eventType" : "INTEGRATION",
      "eventName" : "CP02PMUO-WFP01-00-WFPENG000",
      "eventStartTime" : 1398039060000,
      "eventStopTime" : 1405382400000,
      "notes" : "Updated integration event for CP02PMUO-WFP01-00-WFPENG000, uid A00391.1 ",
      "tense" : "UNKNOWN",
      "dataSource" : null,
      "lastModifiedTimestamp" : 1469464531545
    }


    Add '@class' and sent to uframe....
    curl -H "Content-Type: application/json" -X PUT --upload-file update_event_integration_uid391.txt localhost:4000/uframe/events/14530
    sample request data for uid 391.1 (new_event_integration_uid391.txt)
    {
      "@class" : ".XIntegrationEvent",
      "integrationInto" : null,
      "deploymentNumber" : 1,
      "versionNumber" : 1,
      "integratedBy" : "Engineer, RPS ASA",
      "eventId" : 14530,
      "eventType" : "INTEGRATION",
      "eventName" : "CP02PMUO-WFP01-00-WFPENG000",
      "eventStartTime" : 1398039060000,
      "eventStopTime" : 1405382400000,
      "notes" : "Updated integration event for CP02PMUO-WFP01-00-WFPENG000, uid A00391.1 ",
      "tense" : "UNKNOWN",
      "dataSource" : null,
      "lastModifiedTimestamp" : 1469465195955
    }


    Sample uframe response on success:
    {"id": 14530}

    Contents (from uframe) on success :
    http://host:12587/events/14530
    {
      "@class" : ".XIntegrationEvent",
      "integrationInto" : null,
      "deploymentNumber" : 1,
      "versionNumber" : 1,
      "integratedBy" : "Engineer, RPS ASA",
      "eventId" : 14530,
      "eventType" : "INTEGRATION",
      "eventName" : "CP02PMUO-WFP01-00-WFPENG000",
      "eventStartTime" : 1398039060000,
      "eventStopTime" : 1405382400000,
      "notes" : "Updated integration event for CP02PMUO-WFP01-00-WFPENG000, uid A00391.1 ",
      "tense" : "UNKNOWN",
      "dataSource" : null,
      "lastModifiedTimestamp" : 1469465195955
    }



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
        if debug: print '\n debug -- ', message
        current_app.logger.info(message)
        raise Exception(message)


# todo - Verify fields required for uframe create and update.
# todo - Review updated documentation (received: 2016-07-21)
# todo - Review again when uframe adds uid to base event type. IMPORTANT
# Validate event type integration.
def validate_required_fields_are_provided(data, action=None):
    """ Verify required fields are present in the data and each field has input data of correct type.

    Sample Create integration event request data (from UI) ('@class' and 'eventId' added during processing.
    {
        "@class" : ".XIntegrationEvent",
        "integrationInto" : null,
        "deploymentNumber" : null,
        "versionNumber" : null,
        "integratedBy" : null,
        "eventType" : "INTEGRATION",
        "eventName" : null,
        "eventStartTime" : null,
        "eventStopTime" : null,
        "notes" : null,
        "tense" : "UNKNOWN",
        "dataSource" : null,
    }


    Add following fields and send to uframe:
        "@class": ".XRetirementEvent",
        "eventId:": -1,

    Sample request uframe retirement event:           [Review when uframe provides uid in event base class.]
    request: http://host:12587/events/14525
    response:


    request:    http://localhost:4000/uframe/events/14525
    response:


    Remove "@class" from uframe event before returning response for display.

    """
    event_type = EVENT_TYPE.lower()
    actions = ['create', 'update']

    # Fields required (from UI) for uframe create event.
    required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'integrationInto', 'deploymentNumber', 'versionNumber', 'integratedBy',
                       'notes', 'dataSource', 'tense', 'uid']

    field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'int', 'eventStopTime': 'int', 'eventType': 'string',
                    'lastModifiedTimestamp': 'int', 'notes': 'string', 'dataSource': 'string',
                    'tense': 'string', 'uid': 'string', 'location': 'string', 'status': 'string',
                    'integrationInto': 'string', 'deploymentNumber': 'string',
                    'versionNumber': 'string', 'integratedBy': 'string'}

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
