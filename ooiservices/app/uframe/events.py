
"""
Event routes and supporting functions.

Routes:
[GET]    /events/<int:id>        # Get event. This should not be used by UI; if needed, then discuss!
[GET]    /events                 # DEPRECATED
[DELETE] /asset                  # Deprecated.

All events shall have the following information [requirement 3.1.6.23]
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
# todo ===============================================================================================
# todo Remaining events routes to be completed for new asset model and web services:
# todo - [POST] /events          # Create an event of each eventType (12 now - more to come)
# todo - [POST] /events          # Create event - review negative tests; add negative tests to test cases
# todo - [PUT]  /events/<int:id> # Update event - update test cases and add positive tests for each eventType.
# todo
# todo Test Cases:
# todo - Create event route - review negative tests; add negative tests to test cases
# todo - Update event route - update test cases and add positive tests for each eventType.
# todo - Review negative tests; add negative tests to test cases for all routes
# todo - Update test cases for all routes to have positive test cases for new asset management data model.
# todo
# todo Requirements
# todo - Review again since 2016-07-21 web services update)
# todo - Expect two required fields to be added (in uframe) to each base event per requirement 3.1.6.23
# todo - Missing fields: (1) Event description, (2) Name of operator recording the event
# todo - Add 'g. lastModifiedTimestamp' to requirement 3.1.6.23
# todo
# todo Authentication and Scope
# todo - Review authentication and scope for all routes
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

from flask import (jsonify, request, current_app)
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.main.errors import (bad_request, internal_server_error)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.events_storage import (create_event_storage, update_event_storage)
from ooiservices.app.uframe.events_unspecified import (create_event_unspecified, update_event_unspecified)
from ooiservices.app.uframe.events_atvendor import (create_event_atvendor, update_event_atvendor)
from ooiservices.app.uframe.events_asset_status import (create_event_asset_status, update_event_asset_status)
from ooiservices.app.uframe.events_retirement import (create_event_retirement, update_event_retirement)
from ooiservices.app.uframe.events_integration import (create_event_integration, update_event_integration)
from ooiservices.app.uframe.events_location import (create_event_location, update_event_location)
from ooiservices.app.uframe.events_cruise_info import (create_event_cruise_info, update_event_cruise_info)
from ooiservices.app.uframe.config import get_all_event_types
from ooiservices.app.uframe.event_tools import (get_uframe_event, _get_events_by_uid)

# todo Review authentication and scope
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required

import json


@api.route('/events/types', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
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


@api.route('/events/uid/<string:uid>', methods=['GET'])
#@auth.login_required
#@scope_required(u'asset_manager')
def get_events_by_uid(uid):
    """ Get list of events for asset with uid, filtered by optional type value(s). If error, log and raise.

    Samples requests:
    localhost:4000/uframe/events/uid/A00391.1
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
    try:
        # Determine uid has provided, if not error.
        if not uid:
            message = 'Malformed request, no uid request argument provided.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Get uid and type
        #- - - - - - - - - - - - - - - - - - - - - - -
        _type = request.args.get('type')
        events = _get_events_by_uid(uid, _type)
        return jsonify({'events': events})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/events/<int:id>', methods=['GET'])
@auth.login_required
@scope_required(u'asset_manager')
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
    try:
        event = get_uframe_event(id)
        return jsonify(event)

    except ConnectionError as err:
        message = "ConnectionError getting event %d from uframe;  %s" % (id, str(err))
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout getting event %d from uframe;  %s" % (id, str(err))
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error getting event %d; %s" % (id, str(err))
        current_app.logger.info(message)
        return bad_request(message)


# Create event
@api.route('/event', methods=['POST'])
#@auth.login_required
#@scope_required(u'asset_manager')
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

        # Create event based on event type.
        if event_type == 'STORAGE':
            id = create_event_storage(uid, request_data)
        elif event_type == 'UNSPECIFIED':
            id = create_event_unspecified(uid, request_data)
        elif event_type == 'ATVENDOR':
            id = create_event_atvendor(uid, request_data)
        elif event_type == 'ASSET_STATUS':
            id = create_event_asset_status(uid, request_data)
        elif event_type == 'RETIREMENT':
            id = create_event_retirement(uid, request_data)
        elif event_type == 'INTEGRATION':
            id = create_event_integration(uid, request_data)
        elif event_type == 'LOCATION':
            id = create_event_location(uid, request_data)
        elif event_type == 'CRUISE_INFO':
            id = create_event_cruise_info(uid, request_data)

        # Event types not yet defined (by uframe): PURCHASE and RECOVERY
        elif event_type == 'PURCHASE' or event_type == 'RECOVERY':
            if debug: print '\n debug -- Event type %s is undefined, cannot create.' % event_type

        # Event type CALIBRATION_DATA does not have create and update api support.
        elif event_type == 'CALIBRATION_DATA':
            if debug: print '\n debug -- Event type %s is not supported in api, cannot create.' % event_type

        # Event types not support by these services (to do):
        # 'DEPLOYMENT'
        else:
            message = 'Create event type %s is not supported at this time.' % event_type
            if debug: print '\n exception: Create event type %s is not supported at this time.' % event_type
            raise Exception(message)

        if id == 0:
            message = 'Failed to create %s event for uid %s' % (event_type, uid)
            raise Exception(message)

        if debug: print '\n debug -- Created %s event for uid %s with id: %d' % (event_type, uid, id)

        # Get newly created event and return.
        result = jsonify({'event_id': id})
        # if debug: print '\n debug -- response_data: %s' % json.dumps(response_data, indent=4, sort_keys=True)
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# todo - Modified for new asset web services.
# todo - review negative tests; add negative tests to test cases
# todo - update test cases to have positive test cases for new asset management data model.
# Update event
@api.route('/events/<int:id>', methods=['PUT'])
#@auth.login_required
#@scope_required(u'asset_manager')
def update_event(id):
    """ Update an existing event.
    """
    debug = False
    try:
        if debug: print '\n debug -- Update event with id: ', id
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
        if debug: print '\n debug -- event_id: ', event_id
        if not event_id:
            message = 'The eventId provided is empty or null, a valid eventId is required to update event %s.' % event_type
            raise Exception(message)
        if event_id != id:
            message = 'The eventId provided in request data does not match url id for update event %s.' % event_type
            raise Exception(message)

        if debug: print '\n debug -- Event type %s...' % (event_type.lower())
        if event_type == 'STORAGE':
            id = update_event_storage(id, uid, request_data)
        elif event_type == 'UNSPECIFIED':
            id = update_event_unspecified(id, uid, request_data)
        elif event_type == 'ATVENDOR':
            id = update_event_atvendor(id, uid, request_data)
        elif event_type == 'ASSET_STATUS':
            id = update_event_asset_status(id, uid, request_data)
        elif event_type == 'RETIREMENT':
            id = update_event_retirement(id, uid, request_data)
        elif event_type == 'INTEGRATION':
            id = update_event_integration(id, uid, request_data)
        elif event_type == 'LOCATION':
            id = update_event_location(id, uid, request_data)
        elif event_type == 'CRUISE_INFO':
            id = update_event_cruise_info(id, uid, request_data)

        # Event types not yet defined by uframe: PURCHASE and RECOVERY
        elif event_type == 'PURCHASE' or event_type == 'RECOVERY':
            if debug: print '\n debug -- Event type %s is undefined, cannot update.' % event_type

        # Event type CALIBRATION_DATA does not have create and update api support.
        elif event_type == 'CALIBRATION_DATA':
            if debug: print '\n debug -- Event type %s is not supported in api, cannot update.' % event_type

        # Event types not support by these services (to do):
        # 'DEPLOYMENT'
        else:
            message = 'Update event type %s is not supported at this time.' % event_type
            if debug: print '\n exception: Update event type %s is not supported at this time.' % event_type
            raise Exception(message)

        # If update failed, raise exception.
        if id == 0:
            message = 'Failed to update %s for uid %s' % (event_type, uid)
            if debug: print '\n debug -- ', message
            raise Exception(message)

        if debug: print '\n debug -- Updating storage event for uid %s with id: %d' % (uid, id)

        # Get updated event, return event
        event = get_uframe_event(id)
        if debug: print '\n debug -- event: ', event
        result = jsonify({'event_id': id})
        return result

    except ConnectionError as err:
        message = 'ConnectionError from uframe during update event;  %s' % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = 'Timeout from uframe during update event;  %s' % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- update_event exception: ', message
        current_app.logger.info(message)
        return internal_server_error(message)