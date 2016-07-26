
"""
Event routes and supporting functions.

Routes:
[GET]    /events/<int:id>        # Get event. This should not be used by UI; if needed, then discuss!
[GET]    /events                 # DEPRECATED
[DELETE] /asset                  # Deprecated.
"""
# todo Remaining events routes to be completed for new asset model and web services:
# todo - [POST] /events         # Create an event of each eventType (12 now - more to come)
# todo - [POST] /events         # Create event - review negative tests; add negative tests to test cases
# todo - [PUT] /events/<int:id> # Update event - update test cases and add positive tests for each eventType.

from flask import (jsonify, request, current_app)
from ooiservices.app.uframe import uframe as api

# todo add authentication and scope
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required

# todo review events wrt new asset management data model
#from ooiservices.app.uframe.assetController import get_events_by_ref_des

from ooiservices.app.uframe.events_storage import create_event_storage, update_event_storage


import json
import datetime as dt
import requests
#import requests.adapters
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.main.errors import (bad_request, internal_server_error)
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_events_url_base, get_all_event_types, headers)
from ooiservices.app.uframe.asset_tools import get_timestamp_value


@api.route('/events/types', methods=['GET'])
def get_event_type():
    """ Get all valid event types supported in uframe asset web services.
    localhost:4000/events/types
    response:
        {
          "event_types": [
            "UNSPECIFIED",
            "CALIBRATION_DATA",
            "PURCHASE",
            "DEPLOYMENT",
            "RECOVERY",
            "STORAGE",
            "ATVENDOR",
            "RETIREMENT",
            "LOCATION",
            "INTEGRATION",
            "ASSET_STATUS",
            "CRUISE_INFO"
          ]
        }
    """
    try:
        event_types = get_all_event_types()
        result = jsonify({'event_types': event_types})
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo - done - Added conversion of in eventStartTime, eventStopTime, lastModifiedTimestamp to formatted datetime.
@api.route('/events/uid/<string:uid>', methods=['GET'])
def get_events_by_uid(uid):
    """ Get list of events for asset with uid, filtered by optional type value(s). If error, log and raise.

    Samples requests:
    localhost:4000/uframe/events/uid/A00416?type=INTEGRATION,STORAGE
    localhost:4000/uframe/events/uid/A00416?type=INTEGRATION
    localhost:4000/uframe/events/uid/A00416

    Sample uframe requests:
    host:12587/events/uid/A00416?type=INTEGRATION,STORAGE
    host:12587/events/uid/A00416?type=INTEGRATION
    host:12587/events/uid/A00416

    http://localhost:4000/uframe/events/uid/A00416&type=CRUISE_INFO
        {
          "events": [
            {
              "@class": ".CruiseInfo",
              "cruiseIdentifier": "Pioneer-1_KN-214_2013-11-20",
              "dataSource": null,
              "eventId": 1,
              "eventName": "Pioneer-1_KN-214_2013-11-20",
              "eventStartTime": 1384970400000,
              "eventStopTime": 1385474400000,
              "eventType": "CRUISE_INFO",
              "lastModifiedTimestamp": 1468511875592,
              "notes": "Deployed:\nCP01CNSM-00001 11/21/2013 18:16:00\nCP02PMUO-00001 11/23/2013 15:50:00\nCP02PMUI-00001 11/23/2013 23:16:00\nCP02PMUO-00002 11/25/2013 20:28:00\n\nRecovered:\nCP02PMUO-00001 11/25/2013 12:09:00",
              "shipName": "R/V Knorr",
              "tense": null,
              "uniqueCruiseIdentifer": "CP-2013-0001"
            }, ...

    http://localhost:4000/uframe/events/uid/A00416&type=STORAGE
        {
          "events": [
            {
              "@class": ".XStorageEvent",
              "buildingName": "Tower",
              "dataSource": null,
              "eventId": 14481,
              "eventName": "CP01CNSM-RID26-04-VELPTA000",
              "eventStartTime": 1398039060000,
              "eventStopTime": 1405382400000,
              "eventType": "STORAGE",
              "lastModifiedTimestamp": 1468512400236,
              "notes": "This is a test storage event against CP01CNSM-RID26-04-VELPTA000:1:1 instrument:A00416",
              "performedBy": "James Korman, Raytheon",
              "physicalLocation": "Omaha, NE",
              "roomIdentification": "222",
              "shelfIdentification": "Cube 8-22",
              "tense": null
            }
          ]
        }

    http://localhost:4000/uframe/events/uid/A00416&type=INTEGRATION
        {
          "events": [
            {
              "@class": ".XIntegrationEvent",
              "dataSource": null,
              "deploymentNumber": 1,
              "eventId": 14482,
              "eventName": "CP01CNSM-RID26-04-VELPTA000",
              "eventStartTime": 1398039060000,
              "eventStopTime": 1405382400000,
              "eventType": "INTEGRATION",
              "integratedBy": "James Korman, Raytheon",
              "integrationInto": {
                "full": true,
                "node": "RID26",
                "sensor": "04-VELPTA000",
                "subsite": "CP01CNSM"
              },
              "lastModifiedTimestamp": 1468512468747,
              "notes": "This is a test integration event against CP01CNSM-RID26-04-VELPTA000:1:1 instrument:A00416",
              "tense": null,
              "versionNumber": 1
            }
          ]
        }
    """
    debug = False
    results = []
    try:
        # Determine uid has provided, if not error.
        if not uid:
            message = 'Malformed request, no uid request argument provided.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Get uid and type
        #- - - - - - - - - - - - - - - - - - - - - - -
        #uid = request.args.get('uid')
        _type = request.args.get('type')
        if debug: print '\n debug -- _type: ', _type
        types, _ = get_event_query_types(_type)
        if debug: print '\n debug -- types: ', types

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Get uframe events
        #- - - - - - - - - - - - - - - - - - - - - - -
        result = get_uframe_events_by_uid(uid, types)
        if debug: print '\n debug -- result: %s' % json.dumps(result, indent=4, sort_keys=True)
        # Process result - error - unknown uid provided (204)
        if result is None:
            message = 'Unknown asset uid %s, unable to get events.' % uid
            raise Exception(message)
        """
        # Process result - events (200)
        elif result:
            results = process_timestamps_in_events(result)
        """

        return jsonify({'events': results})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo ======================================================
# todo - Requirements - review again since 2016-07-21 update
# todo - Expect two required fields to be added (in uframe) to each base event per requirement 3.1.6.23
# todo - Missing fields: (1) Event description, (2) Name of operator recording the event
# todo - Add 'g. lastModifiedTimestamp' to requirement 3.1.6.23
# todo ======================================================
'''
def process_timestamps_in_events(data):
    """ Process uframe events response (events by uid).

    All event shall have the following information [requirement 3.1.6.23]
    'The CI shall store the following information for each asset associated event:
        a. Event type
        b. Event description
        c. Name of operator recording the event
        d. Start date/time of event
        e. End  date/time of event
        f. Unique event identifier/record number
    '
    Required field names:
        a. eventType
        b. MISSING Event description                        # ***** Missing data item
        c. MISSING Name of operator recording the event     # ***** Missing data item
        d. eventStartTime
        e. eventStopTime
        f. eventId
        g. lastModifiedTimestamp [not in requirements]      # ***** Add to requirements

    """
    debug = False
    try:
        if data:
            if debug: print '\n debug -- processing data...'
            for event in data:
                convert_event_timestamps(event)
                if '@class' in event:
                    del event['@class']
        return data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


def convert_event_timestamps(event):
    """ Convert all datetime int field values in base event into formatted datetime.
    """
    try:
        if 'eventStartTime' in event:
            if event['eventStartTime']:
                event['eventStartTime'] = convert_event_time(event['eventStartTime'])
        if 'eventStopTime' in event:
            if event['eventStopTime']:
                event['eventStopTime'] = convert_event_time(event['eventStopTime'])

        if 'lastModifiedTimestamp' in event:
            if event['lastModifiedTimestamp']:
                event['lastModifiedTimestamp'] = convert_event_time(event['lastModifiedTimestamp'])
        """
        if 'lastModifiedTimestamp' in event:
            del event['lastModifiedTimestamp']
        """
        return event

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


def convert_event_time(data):
    tmp = None
    try:
        if data > 0 and data is not None:
            tmp1 = dt.datetime.fromtimestamp(data / 1e3)
            tmp = dt.datetime.strftime(tmp1, '%Y-%m-%dT%H:%M:%S')
        return tmp
    except Exception:
        return data
'''

def get_event_query_types(_type):
    """ Get type parameter - if value, process into query string, otherwise return None. On error, raise.
    """
    debug = False
    types_list = []
    try:
        #- - - - - - - - - - - - - - - - - - - - - - -
        # If no type value
        #- - - - - - - - - - - - - - - - - - - - - - -
        if not _type:
            types = None

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If type value - single or multiple types provided?
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
                if debug: print '\n debug -- query_types: ', query_types
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

    except Exception:
        raise


def get_uframe_events_by_uid(uid, types):
    """ For a specific asset uid and optional list of event types, get list of events from uframe.
    On status_code(s):
        200     Success, return events
        204     Error, raise exception unknown uid
        not 200 Error, raise exception

    """
    debug = False
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
        if debug: print '\n debug -- [get_uframe_events_by_uid] url: ', url
        if check: print '\n check -- [get_uframe_events_by_uid] url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
        if debug: print '\n debug -- uframe get events status_code: ', payload.status_code
        if payload.status_code == 204:
            # Return None when unknown uid is provided; log invalid request.
            message = '(204) Unknown asset uid %s, unable to get events.' % uid
            current_app.logger.info(message)
            return None

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
                if debug: print '\n debug -- len(result): ', len(result)
                #print '\n debug -- result: %s' % json.dumps(result, indent=4, sort_keys=True)
            else:
                if debug: print '\n debug ** result: ', result

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


# todo - add authorization
@api.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    """ Get uframe event with id. Return dict, None or raise Exception.

    Sample request: http://localhost:4000/events/1
    Invokes uframe request: http://uframe-host:port/events/1)
        {
          "@class": ".CruiseInfo",
          "cruiseIdentifier": "Pioneer-1_KN-214_2013-11-20",
          "dataSource": null,
          "eventId": 1,
          "eventName": "Pioneer-1_KN-214_2013-11-20",
          "eventStartTime": "2013-11-20T13:00:00",
          "eventStopTime": "2013-11-26T09:00:00",
          "eventType": "CRUISE_INFO",
          "lastModifiedTimestamp": "2016-07-14T11:57:55",
          "notes": "Deployed:\nCP01CNSM-00001 11/21/2013 18:16:00\nCP02PMUO-00001 11/23/2013 15:50:00\nCP02PMUI-00001 11/23/2013 23:16:00\nCP02PMUO-00002 11/25/2013 20:28:00\n\nRecovered:\nCP02PMUO-00001 11/25/2013 12:09:00",
          "shipName": "R/V Knorr",
          "tense": null,
          "uniqueCruiseIdentifer": "CP-2013-0001"
        }
    """
    check = False
    try:
        # Get configuration url and timeout information, build request url.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_events_url_base(), str(id) ])
        if check: print '\n check -- url: ', url

        # Request data from uframe, on error return bad_request.
        payload = requests.get(url, timeout=(timeout, timeout_read))
        data = payload.json()
        if payload.status_code != 200:
            message = 'Error getting event id %d; status code: %d' % (id, payload.status_code)
            return bad_request(message)

        # Convert int time values into formatted datetime values.
        if data:
            data = convert_event_timestamps(data)
        return jsonify(data)

    except ConnectionError as err:
        message = "ConnectionError getting event %d from uframe;  %s" % (id, str(err))
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout getting event %d from uframe;  %s" % (id, str(err))
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error getting event %d from uframe; %s" % (id, str(err))
        current_app.logger.info(message)
        return bad_request(message)


#==============================================================================================
# todo - rework for new asset web services, in progress
# todo - add authorization
# todo - [hold] added required parameters uid and type=eventType, where eventType is one of (config) get_all_event_types()
# todo - [hold] forces change in UI route. (was /event/id [POST] if uid present, then back to original and minimal UI change.
# todo - review negative tests; add negative tests to test cases
# todo - update test cases to have positive test cases for new asset management data model.
# @api.route('/create_event/uid/<string:uid>/type/<string:event_type>', methods=['POST'])
# Create event
@api.route('/event', methods=['POST'])
def create_event():
    """ Create a new event. Return success or error message.

    All of the (twelve) event types are supported except for event type 'UNSPECIFIED'.
    Each event type has a create capability and a defined request.data format.

    All event_types = ['UNSPECIFIED', 'CALIBRATION_DATA', 'PURCHASE', 'DEPLOYMENT', 'RECOVERY', 'STORAGE',
                   'ATVENDOR', 'RETIREMENT', 'LOCATION', 'INTEGRATION', 'ASSET_STATUS', 'CRUISE_INFO']

    Sample storage event request data for create:
    {
        "buildingName": "Tower",
        "eventName": "CP02PMUO-WFP01-00-WFPENG000",
        "eventStartTime": 1398039060000,
        "eventStopTime": 1405382400000,
        "eventType": "STORAGE",
        "notes": "This is another test storage event against CP02PMUO-WFP01-00-WFPENG000:1:1 instrument:A00391.1",
        "performedBy": "Engineer, RPS ASA",
        "physicalLocation": "Narragansett, RI",
        "roomIdentification": "23",
        "shelfIdentification": "Cube 7-21",
        "dataSource": null,
        "tense": null,
        "uid": "A00391.1"
    }

    """
    debug = False
    id = 0
    try:
        if not request.data:
            message = 'No request data provided in request; request data is required to create an event.'
            raise Exception(message)

        # Get request data
        request_data = json.loads(request.data)
        if not request_data:
            message = 'No request data provided; request data is required to create an event.'
            raise Exception(message)

        # Validate minimum required fields to proceed with create (event_type and uid)
        # Required field: event_type
        if 'eventType' not in request_data:
            message = 'No eventType in request data, a eventType is required to create event.'
            raise Exception(message)
        event_type = request_data['eventType']
        valid_event_types = get_all_event_types()
        if event_type not in valid_event_types:
            message = 'The event type provided %s is invalid; valid event types: %s.' % (event_type, valid_event_types)
            raise Exception(message)

        # Required field: uid
        if 'uid' not in request_data:
            message = 'No uid in request data, a valid uid is required to create event %s.' % event_type
            raise Exception(message)
        uid = request_data['uid']
        if not uid:
            message = 'The uid provided is empty or null, a valid uid is required to create event %s.' % event_type
            raise Exception(message)

        if debug: print '\n debug -- Event type %s...' % (event_type.lower())
        if event_type == 'STORAGE':
            id = create_event_storage(uid, request_data)
            if id == 0:
                message = 'Failed to create %s event for uid %s' % (event_type, uid)
                if debug: print '\n debug -- ', message
                raise Exception(message)

        elif event_type == 'INTEGRATION':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'CALIBRATION_DATA':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'PURCHASE':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'DEPLOYMENT':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'RECOVERY':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'ATVENDOR':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'RETIREMENT':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'LOCATION':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'ASSET_STATUS':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        elif event_type == 'CRUISE_INFO':
            if debug: print '\n debug -- Create event type %s is not supported at this time.' % event_type
        else:
            if event_type == 'UNSPECIFIED':
                if debug: print '\n debug -- Create event type %s is not supported.' % event_type
            else:
                if debug: print '\n debug -- Create invalid event type %s is not supported.' % event_type

        if debug: print '\n debug -- Created storage event for uid %s with id: %d' % (uid, id)

        # Get newly created event
        # if debug: print '\n debug -- response_data: %s' % json.dumps(response_data, indent=4, sort_keys=True)
        result = jsonify({'event_id': id})
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo - rework for new asset web services.
# todo - [hold] forces change in UI route. (was /event/id [POST] if uid present, then back to original and minimal UI change.
# todo - [hold] @api.route('/update_event/<int:id>/uid/<string:uid>/type/<string:event_type>', methods=['PUT'])
# todo - review negative tests; add negative tests to test cases
# todo - update test cases to have positive test cases for new asset management data model.
# todo - add authorization
# Update event
@api.route('/events/<int:id>', methods=['PUT'])
def update_event(id):
    """ Update an existing event.
    """
    debug = False
    id = 0
    try:
        if not request.data:
            message = 'No request data provided in request; request data is required to update an event.'
            raise Exception(message)

        # Get request data
        request_data = json.loads(request.data)
        if not request_data:
            message = 'No request data provided; request data is required to update an event.'
            raise Exception(message)

        # Validate minimum required fields to proceed with create (event_type and uid)
        # Required field: event_type
        if 'eventType' not in request_data:
            message = 'No eventType in request data, a eventType is required to update event.'
            raise Exception(message)
        event_type = request_data['eventType']
        valid_event_types = get_all_event_types()
        if event_type not in valid_event_types:
            message = 'The event type provided %s is invalid; valid event types: %s.' % (event_type, valid_event_types)
            raise Exception(message)

        # Required field: uid
        if 'uid' not in request_data:
            message = 'No uid in request data, a valid uid is required to update event %s.' % event_type
            raise Exception(message)
        uid = request_data['uid']
        if not uid:
            message = 'The uid provided is empty or null, a valid uid is required to update event %s.' % event_type
            raise Exception(message)

        # Required field: eventId
        if 'eventId' not in request_data:
            message = 'No eventId in request data, a valid eventId is required to update event %s.' % event_type
            raise Exception(message)

        event_id = request_data['eventId']
        if not event_id:
            message = 'The eventId provided is empty or null, a valid eventId is required to update event %s.' % event_type
            raise Exception(message)
        if event_id != id:
            message = 'The eventId provided in request data does not match url id for update event %s.' % event_type
            raise Exception(message)

        if debug: print '\n debug -- Event type %s...' % (event_type.lower())
        if event_type == 'STORAGE':
            id = update_event_storage(uid, request_data)
            if id == 0:
                message = 'Failed to create storage event for uid %s' % uid
                if debug: print '\n debug -- ', message
                raise Exception(message)

        elif event_type == 'INTEGRATION':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'CALIBRATION_DATA':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'PURCHASE':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'DEPLOYMENT':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'RECOVERY':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'ATVENDOR':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'RETIREMENT':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'LOCATION':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'ASSET_STATUS':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        elif event_type == 'CRUISE_INFO':
            if debug: print '\n debug -- Update event type %s is not supported at this time.' % event_type
        else:
            if event_type == 'UNSPECIFIED':
                if debug: print '\n debug -- Updating event type %s is not supported.' % event_type
            else:
                if debug: print '\n debug -- Updating unknown event type %s is not supported.' % event_type

        if debug: print '\n debug -- Updating storage event for uid %s with id: %d' % (uid, id)
        result = jsonify({'event_id': id})
        return result


    except ConnectionError as err:
        message = "ConnectionError from uframe during update event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout from uframe during update event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error from uframe during update event; %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)