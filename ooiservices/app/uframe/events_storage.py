"""
Events - Storage event create and update functions.

"""
# todo - add authorization (authentication and scope)
from flask import (jsonify, request, current_app)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required

import json
import requests
import requests.adapters
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base, headers)

DATA_CLASS = '.XStorageEvent'

# todo - new function, in progress
# todo - review when uframe adds uid to base event type. IMPORTANT
# todo - add authorization
# Create storage event
def create_event_storage(uid, data):
    """ Create a new storage event. Return success or error message.

    Sample request - create storage event for uid=A000416:
    localhost:4000/create_event/uid/A000416/type/storage
    curl -H "Content-Type: application/json" -X POST --upload-file new_event_storage.txt localhost:4000/uframe/create_event/uid/A000416/type/storage

    curl -H "Content-Type: application/json" -X POST --upload-file new_event_storage.txt host:12587/events/postto/A00416
    Sample request.data:
    {
        "@class": ".XStorageEvent",
        "buildingName": "Tower",
        "eventName": "CP01CNSM-RID26-04-VELPTA000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "STORAGE",
        "lastModifiedTimestamp": 1468512400236,
        "notes": "This is another test storage event against CP01CNSM-RID26-04-VELPTA000:1:1 instrument:A00416",
        "performedBy": "Edna Donoughe, RPS ASA",
        "physicalLocation": "Narragansett, RI",
        "roomIdentification": "23",
        "shelfIdentification": "Cube 7-21",
        "dataSource": null,
        "tense": null,
        "eventId" : -1
    }
    Successful response:
    {
        "message" : "Element created successfully.",
        "id" : 14485,
        "statusCode" : "CREATED"
    }

    sample request:
    curl -H "Content-Type: application/json" -X POST --upload-file new_event_storage_uid391.txt localhost:4000/uframe/create_event/uid/A00391.1/type/storag
    sample request data for uid 391.1:
    {
        "@class": ".XStorageEvent",
        "buildingName": "Tower",
        "eventName": "CP02PMUO-WFP01-00-WFPENG000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "STORAGE",
        "lastModifiedTimestamp": 1468512400236,
        "notes": "This is another test storage event against CP02PMUO-WFP01-00-WFPENG000:1:1 instrument:A00391.1",
        "performedBy": "Edna Donoughe, RPS ASA",
        "physicalLocation": "Narragansett, RI",
        "roomIdentification": "23",
        "shelfIdentification": "Cube 7-21",
        "dataSource": null,
        "tense": null,
        "eventId" : -1
    }
    Sample response on success:
    {"id": 14492}
    """
    debug = False
    check = False
    try:
        # Validate fields in data to ensure required fields are provided and type is as expected.
        create_validate_required_fields_are_provided(data)

        # Add '@class' field to data; remove 'lastModifiedTimestamp' field; ensure eventId is set to -1.
        data['@class'] = '.XStorageEvent'
        if 'lastModifiedTimestamp' in data:
            del data['lastModifiedTimestamp']
        if 'eventId' in data:
            data['eventId'] = -1
        else:
            data['eventId'] = -1

        # Get configuration url and timeout information, build request url.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), 'postto', uid ])
        if check: print '\n check -- url: ', url

        response = requests.post(url, data=json.dumps(data), headers=headers())
        if debug: print '\n debug -- response.status_code: ', response.status_code
        if response.status_code != 201:
            message = 'Failed to create storage event; status code: %d' % response.status_code
            raise Exception(message)

        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            if debug:
                print '\n debug -- response_data: ', response_data
                if isinstance(response_data, dict):
                    print '\n debug -- response_data.keys(): ', response_data.keys()
            if 'statusCode' in response_data:
                if response_data['statusCode'] == 'CREATED':
                    id = response_data['id']
                    if debug: print '\n debug -- Created storage event for uid %s, id is: %d' % (uid, id)
            else:
                if debug: print '\n debug -- failed to locate statusCode in response_data.'

        return id

    except ConnectionError as err:
        message = "ConnectionError (from uframe) during create storage event;  %s" % str(err)
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = "Timeout (from uframe) during create storage event;  %s" % str(err)
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = "Error during create storage event; %s" % str(err)
        if debug: print '\n debug -- message: ', message
        #current_app.logger.info(message)
        raise Exception(message)


# todo - Verify fields required for uframe create (seems like extra fields provided here).
# todo - Examine timestamp data and creation. utc. Review updated documentation (received: 2016-07-21)
# todo - Review when uframe adds uid to base event type. IMPORTANT
def create_validate_required_fields_are_provided(data):
    """ Verify required fields are present in the data and each field has input data of correct type.

    Sample storage event request data for create ('@class' and 'eventId' added during processing.
    {
        "buildingName": "Tower",
        "eventName": "CP02PMUO-WFP01-00-WFPENG000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "STORAGE",
        "notes": "This is another test storage event against CP02PMUO-WFP01-00-WFPENG000:1:1 instrument:A00391.1",
        "performedBy": "Edna Donoughe, RPS ASA",
        "physicalLocation": "Narragansett, RI",
        "roomIdentification": "23",
        "shelfIdentification": "Cube 7-21",
        "dataSource": null,
        "tense": null,
        "uid": "A00391.1"
    }

    Sample storage event from uframe: [Review when uframe provides uid in event base class.]
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

    Review valid fields:
    valid_fields = ['@class', 'buildingName', 'eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                    'lastModifiedTimestamp', 'notes', 'performedBy', 'physicalLocation', 'roomIdentification',
                    'shelfIdentification', 'dataSource', 'tense']
    """
    type = 'storage'

    required_fields = ['buildingName', 'eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'notes', 'performedBy', 'physicalLocation', 'roomIdentification',
                       'shelfIdentification', 'dataSource', 'tense', 'uid']
    field_types = { 'buildingName': 'string', 'eventName': 'string',
                    'eventStartTime': 'int', 'eventStopTime': 'int', 'eventType': 'string',
                    'lastModifiedTimestamp': 'int', 'notes': 'string', 'performedBy': 'string',
                    'physicalLocation': 'string', 'roomIdentification': 'string',
                    'shelfIdentification': 'string', 'dataSource': 'string', 'tense': 'string', 'uid': 'string'}

    number_of_required_fields = len(required_fields)
    number_of_data_fields = len(data.keys())
    try:
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
            message += 'correct and re-submit create %s event request.' % type
            raise Exception(message)

        return

    except Exception as err:
        message = str(err)
        #print '\n debug -- storage event field validation error: ', message
        raise Exception(message)



# todo - rework for new asset web services. In progress.
# todo - add authorization
# Update storage event
def update_event_storage(uid, data):
    """ Update an existing event.
    """
    debug = False
    check = False
    try:
        # Validate fields in data to ensure required fields are provided and type is as expected.
        # todo -
        create_validate_required_fields_are_provided(data)

        # Add @class field to data
        data['@class'] = DATA_CLASS

        # Get configuration url and timeout information, build request url.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), 'postto', uid ])
        if check: print '\n check -- url: ', url

        response = requests.put(url, data=json.dumps(data), headers=headers())
        if debug: print '\n debug -- response.status_code: ', response.status_code
        if response.status_code != 201:
            message = 'Failed to update storage event; status code: %d' % response.status_code
            raise Exception(message)

        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            if debug:
                print '\n debug -- response_data: ', response_data
                if isinstance(response_data, dict):
                    print '\n debug -- response_data.keys(): ', response_data.keys()
            if 'statusCode' in response_data:
                if response_data['statusCode'] == 'OK':
                    id = response_data['id']
                    if debug: print '\n debug -- Update storage event for uid %s, id is: %d' % (uid, id)
            else:
                if debug: print '\n debug -- failed to locate statusCode in response_data.'

        return id

    except ConnectionError as err:
        message = "ConnectionError (from uframe) during update event;  %s" % str(err)
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout as err:
        message = "Timeout (from uframe) during update event;  %s" % str(err)
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = "Error from uframe during update event; %s" % str(err)
        current_app.logger.info(message)
        raise Exception(message)



