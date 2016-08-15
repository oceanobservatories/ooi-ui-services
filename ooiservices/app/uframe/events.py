
"""
Event routes and supporting functions.

Routes:
[GET] /events/<int:id>           # Get event. This should not be used by UI; if needed, then discuss!
[GET] /events/types              # Get all supported event types
[GET] /events/uid/<string:uid>   # Get all events of all types for asset with uid
      /events/uid/<string:uid>?type=EventType   # Get all events for asset with uid, only type(s) identified
      # Example: /uframe/events/uid/A00228?type=ATVENDOR
      # Example: /uframe/events/uid/A00228?type=ATVENDOR,INTEGRATION

[POST] /events                  # Create event.
[PUT]  /events/<int:id>         # Update event.

"""
# todo ===============================================================================================
# todo Requirements
# todo - Expect two required fields to be added (in uframe) to each base event per requirement 3.1.6.23
# todo - Missing fields: (1) Event description, (2) Name of operator recording the event
# todo - Add 'g. lastModifiedTimestamp' to requirement 3.1.6.23
# todo
# todo Create and Update
# todo - 'DEPLOYMENT'           # (general)
# todo - 'CALIBRATION_DATA'     # create and update api not available
# todo ===============================================================================================

from flask import (jsonify, request, current_app)
from ooiservices.app.main.errors import (bad_request, internal_server_error)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.common_tools import (get_event_types, get_supported_event_types)
from ooiservices.app.uframe.events_create_update import (create_event_type, update_event_type)
from ooiservices.app.uframe.event_tools import (_get_events_by_uid)
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
import json


@api.route('/events/types', methods=['GET'])
@auth.login_required
@scope_required(u'asset_manager')
def get_event_type():
    """ Get all valid event types supported in uframe asset web services.
    """
    try:
        event_types = get_event_types()
        result = jsonify({'event_types': event_types})
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/events/types/supported', methods=['GET'])
@auth.login_required
@scope_required(u'asset_manager')
def get_supported_event_type():
    """ Get all valid event types supported in uframe asset web services.
    """
    try:
        event_types = get_supported_event_types()
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
    """
    try:
        # Determine uid has been provided, if not error.
        if not uid:
            message = 'Malformed request, no uid request argument provided.'
            raise Exception(message)

        # Get uid and type
        _type = request.args.get('type')
        events = _get_events_by_uid(uid, _type)
        return jsonify({'events': events})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Create event
@api.route('/events', methods=['POST'])
#@auth.login_required
#@scope_required(u'asset_manager')
def create_event():
    """ Create a new event. Returns event (dict) on success or error message.
    """
    try:
        # Verify request data is provided, if not, raise exception.
        if not request.data:
            message = 'No request data provided in request; request data is required to create an event.'
            raise Exception(message)

        # Get request data
        request_data = json.loads(request.data)
        if not request_data:
            message = 'No request data provided; request data is required to create an event.'
            raise Exception(message)

        # Create event based on event type.
        event = create_event_type(request_data)
        result = jsonify({'event': event})
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Update event
@api.route('/events/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required(u'asset_manager')
def update_event(id):
    """ Update an existing event, returns event (dict) on success or error message.
    """
    try:
        # Verify request data was provided for processing.
        if not request.data:
            message = 'No request data provided in request; request data is required to update an event.'
            raise Exception(message)

        # Get request data
        request_data = json.loads(request.data)
        if not request_data:
            message = 'Request data provided is empty; request data is required to update an event.'
            raise Exception(message)

        # Create event based on event type.
        event = update_event_type(id, request_data)
        result = jsonify({'event': event})
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return internal_server_error(message)