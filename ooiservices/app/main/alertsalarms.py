#!/usr/bin/env python
'''
Alerts & Alarms Endpoints

Routes:
 GET    /alert_alarm
 GET    /alert_alarm/<string:id>
 POST   /alert_alarm
 POST   /ack_alert_alarm
 GET    /alert_alarm_definition
 GET    /alert_alarm_definition/<string:id>
 POST   /alert_alarm_definition
 PUT    /alert_alarm_definition/<int:id>
 DELETE /delete_alert_alarm_definition/<int:id>
 GET    /ok_to_delete_alert_alarm_definition/<int:id>

'''
__author__ = 'James Case'

from flask import (jsonify, request, current_app)
from ooiservices.app import db
from ooiservices.app.main import api
from ooiservices.app.decorators import scope_required                       # todo
from ooiservices.app.main.authentication import auth                        # todo
from ooiservices.app.main.errors import (conflict, bad_request)
from ooiservices.app.models import (SystemEventDefinition, SystemEvent, UserEventNotification, User)
from ooiservices.app.main.notifications import (alert_escalation_state, begin_notification_process,
                                                update_notification_ticket, reissue_notification_ticket)
import datetime as dt
import requests
import json
import calendar

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts & Alarms
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#List all alerts and alarms
@api.route('/alert_alarm')
def get_alerts_alarms():
    """ Get all alert(s) and alarm(s) which match filter rules provided in request.args.
    Dynamically construct filters to query SystemEvent and SystemEventDefinitions.
    List output for each alert_alarm which includes system_event_definition content based request.args 'filters'.
    """
    result = []
    try:
        # Get query filters, query SystemEvents using event_filters
        event_filters, definition_filters = get_query_filters(request.args)
        alerts_alarms = None
        if event_filters is None:   # alerts_alarms
            alerts_alarms = db.session.query(SystemEvent).all()
        else:
            alerts_alarms = db.session.query(SystemEvent).filter_by(**event_filters)
        # Process alert_alarm json output based on definition filters
        if alerts_alarms is not None:
            result_json = get_alert_alarm_json(alerts_alarms, definition_filters)
            if result_json is None:
                result = []
            else:
                result = result_json
        return jsonify( {'alert_alarm': result})
    except Exception as err:
        return conflict('Insufficient data, or bad data format. (%s)' % str(err.message))

#List an alerts and alarms by id
@api.route('/alert_alarm/<int:id>')
def get_alert_alarm(id):
    alert_alarm = SystemEvent.query.filter_by(id=id).first() #_or_404()
    if alert_alarm is None:
        return jsonify(error="alert_alarm not found"), 404
    return jsonify(alert_alarm.to_json())

#Create a new alert/alarm
@api.route('/alert_alarm', methods=['POST'])
@auth.login_required
@scope_required(u'user_admin')
@scope_required(u'redmine')
def create_alert_alarm():
    """ Create an alert or an alarm; invoked when processing alerts and alarms from uframe.
    Note: offset from start of unix epoch (jan 1, 1900 at midnight 00:00) to 00:00 1 Jan 1970 GMT, in secs = 2208988800
    # todo discuss:
    # todo 'escalate_on' - amount of time, after the first alert occurred, to create a redmine ticket;
    # todo           escalate_on units? seconds?
    # todo 'escalate_boundary' - amount of time after ts_escalated to create yet another red mine ticket)
    """
    debug = False
    log = False
    try:
        # Process request.data; verify required fields are present
        data = json.loads(request.data)
        create_has_required_fields(data)
        uframe_filter_id = data['uframe_filter_id']
        uframe_event_id = data['uframe_event_id']

        # Get system_event_definition_id using uframe_filter_id provided in request.data
        try:
            system_event_definition = SystemEventDefinition.query.filter_by(uframe_filter_id=uframe_filter_id).first()
            if system_event_definition is None:
                message = 'Failed to retrieve SystemEventDefinition for uframe_filter_id: %d' % uframe_filter_id
                raise Exception(message)
            system_event_definition_id = system_event_definition.id
        except Exception as err:
            # This is a severe error, definitely should be logged (failure to record instance of alert or alarm from uframe)
            message = 'Unable to retrieve system_event_definition using uframe_filter_id; %s ' % str(err.message)
            current_app.logger.exception(message)
            raise  Exception(err.message)
        if system_event_definition_id is None:
            message = 'Unable to identify system_event_definition_id using uframe_filter_id (%d)' % uframe_filter_id
            current_app.logger.exception(message)
            raise Exception(message)

        # If the system_event_definition is not active, do not create alert_alarm instance todo - do silently? test case
        if not system_event_definition.active:
            message = 'Failed to create alert_alarm - system_event_definition is not active. (%d)' % system_event_definition.id
            current_app.logger.exception(message)
            raise Exception(message)
        # If the system_event_definition is retired, do not create alert_alarm instance todo - do silently? test case
        if system_event_definition.retired is not None:
            if system_event_definition.retired:
                message = 'Failed to create alert_alarm - system_event_definition is retired. (%d)' % system_event_definition.id
                current_app.logger.exception(message)
                raise Exception(message)

        # Determine if uframe_filter_id provided matches system_event_definition.uframe_filter_id, if not error (409)

        # Create SystemEvent
        alert_alarm = SystemEvent()
        alert_alarm.uframe_event_id = uframe_event_id
        alert_alarm.uframe_filter_id = uframe_filter_id
        alert_alarm.system_event_definition_id = system_event_definition_id
        offset = 2208988800
        uframe_float = data['event_time']
        ts_event_time = convert_from_utc(uframe_float - offset)
        alert_alarm.event_time = dt.datetime.strftime(ts_event_time, "%Y-%m-%dT%H:%M:%S")
        alert_alarm.event_type = data['event_type']
        alert_alarm.event_response = data['event_response']
        alert_alarm.method = data['method']
        alert_alarm.deployment = data['deployment']
        alert_alarm.acknowledged = False
        alert_alarm.ack_by = None
        alert_alarm.ts_acknowledged = None
        alert_alarm.timestamp = dt.datetime.now()       # when this alert or alarm is received and persisted
        try:
            db.session.add(alert_alarm)
            db.session.commit()
            db.session.flush()
        except Exception as err:
            # todo - test case
            message = 'IntegrityError creating alert_alarm; %s' % str(err.message)
            if log: print '\n message: ', message
            current_app.logger.exception(message)
            db.session.rollback()
            return bad_request('IntegrityError creating alert_alarm.')

        # If 'alert' received, start the alert escalation process, otherwise begin
        # the notification process for an alarm
        valid_actions = ['begin_notification_process', 'update_notification_ticket', 'reissue_notification_ticket']
        if debug: print '\n processing an %s with id: %d' % (alert_alarm.event_type, alert_alarm.id)
        if alert_alarm.event_type == 'alert':
            action = alert_escalation_state(alert_alarm.id)
            if debug: print '\n alert_escalation_state -- action: ', action
            if action is not None:
                if action in valid_actions:
                    if action == 'begin_notification_process':
                        if debug: print '\n action: begin_notification_process *****\n'
                        ticket_id = begin_notification_process(alert_alarm.id)
                        if ticket_id is None:
                            if debug: print '\nFailed to create redmine ticket for alert id: %d *****\n' % alert_alarm.id
                        if debug: print '\n ticket_id; ', ticket_id
                    elif action == 'update_notification_ticket':
                        if debug: print '\n action: update_notification_ticket *****\n'
                        ticket_id = update_notification_ticket(alert_alarm.id)
                        if ticket_id is None:
                            if debug: print '\nFailed to update redmine ticket for alert id: %d ***** \n' % alert_alarm.id
                    elif action == 'reissue_notification_ticket':
                        if debug: print '\n action: reissue_notification_ticket *****\n'
                        ticket_id = reissue_notification_ticket(alert_alarm.id)
                        if ticket_id is None:
                            if debug: print '\nFailed to reissue redmine ticket for alert id: %d *****\n' % alert_alarm.id

        elif alert_alarm.event_type == 'alarm':
            begin_notification_process(alert_alarm.id)

        return jsonify(alert_alarm.to_json()), 201
    except Exception as err:
        message = 'Insufficient data, or bad data format; %s' % err.message
        if log: print '\n message: ', message
        current_app.logger.exception(message)
        return conflict(message)

# Acknowledge alert/alarm
@api.route('/ack_alert_alarm', methods=['POST'])
#@auth.login_required
#@scope_required(u'user_admin')
#@scope_required(u'redmine')
def acknowledge_alert_alarm():
    """ Acknowledge an alert or an alarm.
    Acknowledge alert/alarm in uframe, required eventId (id) and acknowledged by value (ack_value).
    If the user acknowledging the alert/alarm is ack_by.
    """
    log = False
    debug = False
    try:
        # Process request.data; verify required fields are present
        data = json.loads(request.data)
        acknowledge_has_required_fields(data)

        # Determine if alert_alarm to be acknowledged is same as reflected in request data
        alert_alarm = is_valid_alert_alarm_for_ack(data)
        if alert_alarm is None:
            message = 'Failed to retrieve alert_alarm.'
            if log: print '\n (log) ', message
            raise Exception(message)

        # Get alert_alarm_definition, then user_event_notification. Retrieve user email address.
        alert_alarm_definition = SystemEventDefinition.query.get(alert_alarm.system_event_definition_id)
        if alert_alarm_definition is None:
            message = 'Failed to identify system_event_definition with id: %d' % alert_alarm.system_event_definition_id
            if log: print '\n (log) [acknowledge_alert_alarm] message: ', message
            current_app.logger.exception('[acknowledge_alert_alarm] %s ' % message)
            raise Exception(message)

        # Get user_event_notification by filter on alert alarm definition value
        user_event_notification = UserEventNotification.query.filter_by(system_event_definition_id=alert_alarm_definition.id).first()
        if user_event_notification is None:
            message = 'Failed to identify user_event_notification with id: %d' % alert_alarm_definition.id
            if log: print '\n (log) [acknowledge_alert_alarm] -- message: ', message
            current_app.logger.exception('[acknowledge_alert_alarm] %s ' % message)
            raise Exception(message)

        # Acknowledge alert/alarm in uframe. acknowledgedBy is str(user_id)
        ack_value = None
        ack_by = data['ack_by']
        ack_id = alert_alarm.uframe_event_id
        if ack_by is not None or not ack_by:
            ack_value = ack_by

        if ack_value is None:
            message = 'Required value ack_by is empty or None.'
            if debug: print '\n message: ', message
            return bad_request(message)

        if alert_alarm.event_type == 'alarm':
            if not (uframe_acknowledge_alert_alarm(ack_id, ack_value)):
                message = 'Failed to acknowledge alert_alarm (id: %d), in uframe.' % alert_alarm.id
                if log: print '\n (log) [acknowledge_alert_alarm] -- message: ', message
                current_app.logger.exception('[acknowledge_alert_alarm] %s ' % message)
                return bad_request(message)

        # Update alert_alarm acknowledged, ack_by and ts_acknowledged - todo revisit
        alert_alarm.acknowledged = True
        alert_alarm.ack_by = ack_by
        alert_alarm.ts_acknowledged = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        try:
            db.session.add(alert_alarm)
            db.session.commit()
        except:
            # todo - test case
            db.session.rollback()
            return bad_request('IntegrityError acknowledging alert_alarm')
        return jsonify(alert_alarm.to_json()), 201
    except Exception as err:
        message = 'Insufficient data, or bad data format; %s' % err.message
        if log: print '\n (acknowledge_alert_alarm) message: ', message
        return conflict(message)

def get_alert_alarm_definition_id(uframe_filter_id):
    """ Get alert_alarm_definition id using alert_alarm.uframe_filter_id.
    """
    log = False
    try:
        # Get system_event_definition_id using uframe_filter_id provided in request.data
        try:
            system_event_definition = SystemEventDefinition.query.filter_by(uframe_filter_id=uframe_filter_id).first()
            if system_event_definition is None:
                message = 'Failed to retrieve SystemEventDefinition for uframe_filter_id: %d' % uframe_filter_id
                if log: print '\n message: ', message
                current_app.logger.exception(message)
                raise Exception(message)
            system_event_definition_id = system_event_definition.id
        except Exception as err:
            # This is a severe error, failure to record instance of alert or alarm from uframe.
            message = 'Failure to record instance of alert or alarm from uframe. Error: %s' % err.message
            if log: print '\n message: ', message
            current_app.logger.exception(message)
            raise  Exception(err.message)
        if system_event_definition_id is None:
            message = 'Unable to identify system_event_definition_id using uframe_filter_id (%d)' % uframe_filter_id
            if log: print '\n message: ', message
            current_app.logger.exception(message)
            raise Exception(message)
        return system_event_definition_id
    except:
        raise

def is_valid_alert_alarm_for_ack(data):
    """ Validate this is the alert alarm to be acknowledged.
    """
    log = False
    try:
        definition_id = data['system_event_definition_id']
        definition = SystemEventDefinition.query.get(definition_id)
        if definition is None:
            message = 'Acknowledge failed to retrieve SystemEventDefinition (id: %d)' % definition_id
            if log: print '\n (is_valid_alert_alarm_for_ack) message: ', message
            raise Exception(message)

        # Variables for sanity tests
        uframe_filter_id = data['uframe_filter_id']
        uframe_event_id = data['uframe_event_id']
        event_type = data['event_type']
        # Sanity test variables alert_alarm data against definition
        if definition.uframe_filter_id != uframe_filter_id:
            message = 'Acknowledge failed to match alert_alarm uframe_filter_id with SystemEventDefinition (id: %d)' % definition_id
            if log: print '\n (is_valid_alert_alarm_for_ack) message: ', message
            raise Exception(message)
        if definition.event_type != event_type:
            message = 'Acknowledge failed to match alert_alarm event_type with SystemEventDefinition (id: %d)' % definition_id
            if log: print '\n (is_valid_alert_alarm_for_ack) message: ', message
            raise Exception(message)

        # Sanity test existing alert_alarm; first get alert_alarm to be acknowledged, verify variables for consistency
        id = data['id']
        alert_alarm = SystemEvent.query.get(id)
        if alert_alarm is None:
            return alert_alarm

        if alert_alarm.uframe_filter_id != uframe_filter_id:
            message = 'Acknowledge failed to match alert_alarm uframe_filter_id (id: %d)' % id
            if log: print '\n (is_valid_alert_alarm_for_ack) message: ', message
            raise Exception(message)
        if alert_alarm.uframe_event_id != uframe_event_id:
            message = 'Acknowledge failed to match alert_alarm uframe_event_id  (id: %d)' % id
            if log: print '\n (is_valid_alert_alarm_for_ack) message: ', message
            raise Exception(message)
        if alert_alarm.event_type != event_type:
            message = 'Acknowledge failed to match alert_alarm event_type (id: %d)' % id
            if log: print '\n (is_valid_alert_alarm_for_ack) message: ', message
            raise Exception(message)
        return alert_alarm
    except Exception as err:
        if log: print '\n (is_valid_alert_alarm_for_ack) message: ', err.message
        raise

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts & Alarms Definitions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#List all alert and alarm definitions
@api.route('/alert_alarm_definition')
def get_alerts_alarms_def():
    """ Get a list of alert or alarm definition(s).
    """
    result = []
    query_filter = get_definitions_query_filter(request.args)
    if query_filter is None:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(retired=False)
    else:
        alerts_alarms_def = db.session.query(SystemEventDefinition).filter_by(**query_filter)
    if alerts_alarms_def is not None:
        result = [alert_alarm_def.to_json() for alert_alarm_def in alerts_alarms_def]
    return jsonify( {'alert_alarm_definition' : result })

#List an alerts and alarms definition by id
@api.route('/alert_alarm_definition/<int:id>')
def get_alert_alarm_def(id):
    """ Get an alert or alarm definition by id.
    """
    alert_alarm_def = SystemEventDefinition.query.filter_by(id=id).first()
    if alert_alarm_def is None:
        return jsonify(error="alert_alarm_definition not found"), 404
    return jsonify(alert_alarm_def.to_json())

#Create a new alert/alarm definition
@api.route('/alert_alarm_definition', methods=['POST'])
@auth.login_required
@scope_required(u'user_admin')
def create_alert_alarm_def():
    """ Create an alert or alarm definition, including the the user_event_notification record.

    The create_alert_alarm_def method requires parameters for user_event_notification also. The
    user_event_notification is created immediately after the alert_alarm_definition.
    """
    debug = False
    try:
        # Process request.data; verify required fields provided for create, including user_event_notification
        data = json.loads(request.data)
        create_definition_has_required_fields(data)
        user_event_notification_has_required_fields(data)
        # Persist alert_alarm_def in uframe using POST
        uframe_filter_id = create_uframe_alertfilter(data)
        if uframe_filter_id is None:
            message = 'Failed to create alertfilter in uframe.'
            if debug: print '\n (create_alert_alarm_def) message: ', message
            raise Exception(message)
        # Persist alert_alarm_def in ooi-ui-services db
        alert_alarm_def = SystemEventDefinition()
        alert_alarm_def.active = data['active']
        alert_alarm_def.array_name = data['array_name']  # Array reference designator
        alert_alarm_def.description = data['description']
        alert_alarm_def.event_type = data['event_type']
        alert_alarm_def.high_value = data['high_value']
        alert_alarm_def.instrument_name = data['instrument_name']  # Instrument reference designator
        alert_alarm_def.instrument_parameter = data['instrument_parameter']
        alert_alarm_def.instrument_parameter_pdid = data['instrument_parameter_pdid']
        alert_alarm_def.low_value = data['low_value']
        alert_alarm_def.operator = data['operator']
        alert_alarm_def.platform_name = data['platform_name']  # Platform reference designator
        alert_alarm_def.reference_designator = data['reference_designator'] # Instrument reference designator
        alert_alarm_def.severity = data['severity']
        alert_alarm_def.stream = data['stream']
        alert_alarm_def.escalate_on = data['escalate_on']
        alert_alarm_def.escalate_boundary = data['escalate_boundary']
        alert_alarm_def.created_time = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        alert_alarm_def.uframe_filter_id = uframe_filter_id # Returned from POST to uFrame
        alert_alarm_def.ts_retired = None
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
        except:
            # todo - test case
            # Rollback alert_alarm_def and delete alertfilter from uframe.
            message = 'IntegrityError creating alert_alarm_definition'
            db.session.rollback()
            result = delete_alertfilter(uframe_filter_id)
            if result is None:
                message += '; failed to rollback create uframe alertfilter (id: %d) ' %  uframe_filter_id
            if debug: print '\, (create_alert_alarm_def) message: ', message
            return bad_request(message)

        # todo put this into it's own method...
        try:
            # Create corresponding UserEventNotification when alert or alarm definition is created
            system_event_definition_id = alert_alarm_def.id
            user_id = data['user_id']
            use_email = data['use_email']
            use_redmine = data['use_redmine']
            use_phone = data['use_phone']
            use_log = data['use_log']
            use_sms = data['use_sms']
            new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=system_event_definition_id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            if new_id is None:
                message = 'Unable to create user_event_notification record.'
                if debug: print '\n (create_alert_alarm_def) message: ', message
                raise Exception(message)

        except Exception as err:
            # todo - test case(s)
            # Error creating user_event_notification, rollback: delete system_event_definition and uframe alertfilter
            message += 'IntegrityError creating alert_alarm_definition. Failed to insert_user_event_notification (%s)' % str(err.message)
            try:
                SystemEventDefinition.delete_system_event_definition(alert_alarm_def)
            except Exception as err:
                message += '; %s' % err.message
            '''
            # Remove alert_alarm_def
            definition = SystemEventDefinition.query.get(alert_alarm_def.id)
            if definition is None:
                message += " system_event_definition (id: %d) Not Found" % alert_alarm_def.id
            db.session.delete(definition)
            db.session.commit()
            '''
            result = delete_alertfilter(uframe_filter_id)
            if result is None:
                message += '; failed to rollback uframe alertfilter (id: %d) ' %  uframe_filter_id
            if debug: print '\n (create_alert_alarm_def) message: ', message
            return conflict(message)

        return jsonify(alert_alarm_def.to_json()), 201
    except Exception as err:
        message = 'Insufficient data, or bad data format. (%s)' % str(err.message)
        if debug: print '\n (create_alert_alarm_def) message: ', message
        return conflict(message)

@api.route('/alert_alarm_definition/<int:id>', methods=['PUT'])
# @auth.login_required
# @scope_required(u'user_admin')
def update_alert_alarm_def(id):
    """Update an alert or an alarm definition. Optional update of associated user_event_notification available.

    update_alert_alarm_def only requires request.data for alert_alarm_def; no parameters for user_event_notification
    are required. If 'update_user_event_notification' in the request.data (set to true), then
    the user_event_notification will be updated within this method; in this case, all user_event_notification
    fields must also be provided in the request.data.
    """
    # todo discuss:
    # todo 'escalate_on' - amount of time, after the first alert occurred, to create a redmine ticket;
    # todo           escalate_on units? seconds?
    # todo 'escalate_boundary' - amount of time after ts_escalated to create yet another red mine ticket)
    try:
        # Verify SystemEventDefinition with this id exists
        alert_alarm_def = SystemEventDefinition.query.get(id)
        if alert_alarm_def is None:
            message = "Invalid ID, alert_alarm_definition record not found"
            #print '\n message: ', message
            return jsonify(error=message), 404
        original_alert_alarm_def = alert_alarm_def
        # Process request.data; verify required fields provided for update.
        data = json.loads(request.data)
        create_definition_has_required_fields(data)
        if 'uframe_filter_id' not in data:
            message = 'uframe_filter_id not in alertfilter update request.data'
            #print '\n message: ', message
            raise Exception(message)
        user_event_notification = None
        user_event_notification_id = None
        update_user_event_notification = False
        if 'update_user_event_notification' in data:
            update_user_event_notification = data['update_user_event_notification']
            if update_user_event_notification:
                user_event_notification_has_required_fields(data)
                user_event_notification = UserEventNotification.query.filter_by(system_event_definition_id=id).first()
                if user_event_notification is None:
                    message = 'Invalid ID, user_event_notification record not found for requested update.'
                    #print '\n message: ', message
                    return jsonify(error="Invalid ID, user_event_notification record not found for requested update."), 404
                user_event_notification_id = user_event_notification.id

        # Persist alert_alarm_def in uframe using POST; retain original definition for rollback
        uframe_filter_id = data['uframe_filter_id']
        original_uframe_definition = get_alertfilter(uframe_filter_id)
        update_uframe_alertfilter(data, uframe_filter_id)

        # Persist alert_alarm_def in ooi-ui-services database
        alert_alarm_def.uframe_filter_id = uframe_filter_id # Returned from POST to uFrame
        alert_alarm_def.reference_designator = data['reference_designator'] # Instrument reference designator
        alert_alarm_def.array_name = data['array_name']  # Array reference designator
        alert_alarm_def.platform_name = data['platform_name']  # Platform reference designator
        alert_alarm_def.instrument_name = data['instrument_name']  # Instrument reference designator
        alert_alarm_def.instrument_parameter = data['instrument_parameter']
        alert_alarm_def.instrument_parameter_pdid = data['instrument_parameter_pdid']
        alert_alarm_def.operator = data['operator']
        # alert_alarm_def.created_time = datetime.now()
        alert_alarm_def.event_type = data['event_type']
        alert_alarm_def.active = data['active']
        alert_alarm_def.description = data['description']
        alert_alarm_def.high_value = data['high_value']
        alert_alarm_def.low_value = data['low_value']
        alert_alarm_def.severity = data['severity']
        alert_alarm_def.stream = data['stream']
        alert_alarm_def.escalate_on = data['escalate_on']
        alert_alarm_def.escalate_boundary = data['escalate_boundary']
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
            #db.session.flush()
        except:
            # Restore original alertfilter in uframe. Restore original original_alert_alarm_def_ todo - test case
            #db.session.rollback()
            db.session.add(original_alert_alarm_def)
            db.session.commit()
            result = update_uframe_alertfilter(uframe_filter_id, original_uframe_definition)
            message = 'IntegrityError update_alert_alarm_def'
            if result is None:
                message += '; failed to rollback updates to uframe alertfilter (id: %d) ' %  uframe_filter_id
            return bad_request(message)
        # If user has indicated an updatefor the user_event_notification, perform update.
        if update_user_event_notification:
            #print '\n debug -- Performing UserEventNotification.update_user_event_notification....'
            try:
                # Update corresponding UserEventNotification for when alert or alarm instance
                system_event_definition_id = alert_alarm_def.id
                user_id = data['user_id']
                use_email = data['use_email']
                use_redmine = data['use_redmine']
                use_phone = data['use_phone']
                use_log = data['use_log']
                use_sms = data['use_sms']
                UserEventNotification.update_user_event_notification(id=user_event_notification_id,
                                                                     system_event_definition_id=system_event_definition_id,
                                                                     user_id=user_id,
                                                                     use_email=use_email,
                                                                     use_redmine=use_redmine,
                                                                     use_phone=use_phone,
                                                                     use_log=use_log,
                                                                     use_sms=use_sms)
            except Exception as err:
                # Error updating user_event_notification, rollback: updates to system_event_definition and uframe alertfilter
                message = 'IntegrityError update_alert_alarm_def; Failed to update_user_event_notification (%s)' % str(err.message)
                print '\n (update_alert_alarm_def) exception: %s' % message
                result = update_uframe_alertfilter(uframe_filter_id, original_uframe_definition)
                if result is None:
                    message += '; failed to rollback updates to uframe alertfilter (id: %d) ' %  uframe_filter_id
                #print '\n (update_alert_alarm_def) message: ', message
                return conflict(message)

        return jsonify(alert_alarm_def.to_json()), 201
    except Exception as err:
        #message = 'Insufficient data, or bad data format. (%s)' % str(err.message)
        message = str(err.message)
        #print '\n (update_alert_alarm_def) message: ', message
        return conflict(message)

@api.route('/delete_alert_alarm_definition/<int:id>', methods=['DELETE'])
#@auth.login_required
#@scope_required(u'user_admin')
def delete_alert_alarm_definition(id):
    """ Delete SystemEventDefinition for alert or alarm; this retires SystemEventDefinition (no deletion).
    """
    # Get alert_alarm_definition
    alert_alarm_def = SystemEventDefinition.query.get(id)
    if alert_alarm_def is None:
        return jsonify(error="alert_alarm_definition not found"), 404
    # If alert_alarm_definition already retired, just return
    if alert_alarm_def.retired is not None:
        if alert_alarm_def.retired == True:
            return jsonify(), 200
    # Determine if definition id is used by any alert or alarm instances where acknowledged is False)
    active_alerts_alarms = SystemEvent.query.filter_by(system_event_definition_id=id, acknowledged=False).first()
    if active_alerts_alarms is not None:
        # There are existing alert_alarm instances using this id which have not been acknowledged
        message = 'There are existing alert_alarm instances using this id which have not yet been acknowledged.'
        return bad_request(message)
    alert_alarm_def.retired = True
    alert_alarm_def.ts_retired = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
    try:
        db.session.add(alert_alarm_def)
        db.session.commit()
        #db.session.flush()
    except:
        db.session.rollback()
        message = 'IntegrityError deleting alert_alarm_definition'
        return bad_request(message)
    return jsonify(), 200

@api.route('/ok_to_delete_alert_alarm_definition/<int:id>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def ok_to_delete_alert_alarm_definition(id):
    """ Determine if an alert_alarm_definition can be deleted (retired) at this time.
    Response format:  { "status": false | true }
    """
    if safe_to_delete_alert_alarm_definition(id):
        return jsonify(status=True), 200
    else:
        return jsonify(status=False), 200

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private Methods for routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_definition_has_required_fields(data):
    """ Verify SystemEventDefinition creation has required fields in request.data. Error otherwise.
    SystemEventDefinition update can re-use this method but must also check for uframe_filter_id.
    Review what to do with create_time on update SystemEventDefinition.
    Verify operator value is one of valid uframe operators.
    """
    try:
        required_fields = ['active', 'array_name', 'description', 'event_type', 'high_value',
                           'instrument_name', 'instrument_parameter', 'instrument_parameter_pdid', 'low_value',
                           'operator',  'platform_name', 'reference_designator', 'severity',  'stream',
                           'escalate_on', 'escalate_boundary']
                           # not created_time, id, 'uframe_filter_id'
        valid_operators = ['GREATER', 'LESS', 'BETWEEN_EXCLUSIVE', 'OUTSIDE_EXCLUSIVE']
        valid_event_types = ['alert', 'alarm']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%s) in request.data' % field
                #print '\n debug -- (create_definition_has_required_fields) %s' % message
                raise Exception(message)
        if data['event_type'] is None:
            message = 'Failed to provide event_type value provided. (None).'
            #print '\n debug -- (create_definition_has_required_fields) %s' % message
            raise Exception(message)
        if data['event_type'] not in valid_event_types:
            message = 'Invalid event_type value provided (%s).' % data['event_type']
            #print '\n debug -- (create_definition_has_required_fields) %s' % message
            raise Exception(message)
        if data['operator'] is None:
            message = 'Failed to provide operator value provided. (None).'
            #print '\n debug -- (create_definition_has_required_fields) %s' % message
            raise Exception(message)
        if data['operator'] not in valid_operators:
            message = 'Invalid operator value provided (%s).' % data['operator']
            #print '\n debug -- (create_definition_has_required_fields) %s' % message
            raise Exception(message)
        return
    except Exception as err:
        #print '\n (create_definition_has_required_fields) message: ', err.message
        raise

def user_event_notification_has_required_fields(data):
    """ Verify insert_user_event_notification data has required fields. Error otherwise.
    """
    field = None
    try:
        required_fields = ['user_id', 'use_email', 'use_redmine', 'use_phone', 'use_log', 'use_sms']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%s) in request.data' % field
                #print '\n message: ', message
                raise Exception(message)
            if data[field] is None:
                message = 'Required field (%s) value provided is None for user_event_notification.' % field
                #print '\n message: ', message
                raise Exception(message)
        return
    except Exception as err:
        message = '(user_event_notification_has_required_fields) %s ' % err.message
        #print '\n message: ', message
        raise

def create_has_required_fields(data):
    """ Verify SystemEvent creation has required fields in request.data. Error otherwise.
    """
    try:
        required_fields = ['uframe_event_id', 'uframe_filter_id', 'system_event_definition_id',
                           'event_time', 'event_type', 'event_response', 'method', 'deployment']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%s) in request.data' % field
                raise Exception(message)
        return
    except Exception as err:
        raise

def acknowledge_has_required_fields(data):
    """ Verify SystemEvent acknowledge has required fields in request.data. Error otherwise.
    """
    try:
        required_fields = ['id', 'uframe_event_id', 'uframe_filter_id', 'system_event_definition_id',
                           'event_type', 'ack_by']
                           # 'acknowledged',, 'ts_acknowledged']
                           #'event_response', 'method', 'deployment']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%s) in request.data' % field
                #print '\n (acknowledge_has_required_fields) message: ', message
                raise Exception(message)
        return
    except Exception as err:
        #print '\n (acknowledge_has_required_fields) message: ', err.message
        raise

def get_query_filters(request_args):
    """ Create filter dictionaries for SystemEvent and SystemEventDefinition; used in route /alert_alarm.

    Current filter options for request.args:
        'type', 'method', 'deployment', 'acknowledged', 'array_name', 'platform_name', 'instrument_name',
        'reference_designator', 'active', 'retired'

    Breakout for filters by class (where actual filter item is):
        for alert_alarm:            'event_type', 'method', 'deployment', 'acknowledged'
        for alert_alarm_definition: 'array_name', 'platform_name', 'instrument_name', 'reference_designator',
                                    'active', 'retired'
    """
    event_filters = {}
    definition_filters = {}
    event_type = None
    acknowledged = None
    method = None
    deployment = None
    array_name = None
    platform_name = None
    reference_designator = None
    instrument_name = None
    active = None
    retired = None
    # Set filter values based on request.args
    if 'type' in request.args:
        tmp = str(request_args.get('type'))
        if tmp is not None and tmp != '' and tmp != 'None':
            event_type = request_args.get('type')
    if 'method' in request_args:
        if request_args.get('method') is not None:
            method = request_args.get('method')
    if 'deployment' in request_args:
        tmp = str(request_args.get('deployment'))
        if tmp is not None and tmp != '' and tmp != 'None':
            try:
                deployment = float(tmp)
            except:
                pass
    if 'acknowledged' in request_args:
        if request_args.get('acknowledged') is not None:
            try:
                # default to false
                acknowledged = to_bool(request_args.get('acknowledged'))
                acknowledged = str(acknowledged).lower()
            except:
                pass
    if 'array_name' in request_args:
        if request_args.get('array_name') is not None:
            array_name = request_args.get('array_name')
    if 'platform_name' in request_args:
        if request_args.get('platform_name') is not None:
            platform_name = request_args.get('platform_name')
    if 'reference_designator' in request_args:
        if request_args.get('reference_designator') is not None:
            reference_designator = request_args.get('reference_designator')
    if 'instrument_name' in request_args:
        if request_args.get('instrument_name') is not None:
            instrument_name = request_args.get('instrument_name')
    if 'active' in request_args:
        if request_args.get('active') is not None:
            try:
                # defaults to true
                active = to_bool(str(request_args.get('active')))
                active = str(active).lower()
            except:
                active = None
                pass
    if 'retired' in request_args:
        if request_args.get('retired') is not None:
            try:
                # defaults to false
                retired = to_bool(request_args.get('retired'))
                retired = str(retired).lower()
            except:
                pass
    # SystemEvent query filter (NOTE: keys must be class properties)
    event_keys = ['event_type', 'method', 'deployment', 'acknowledged']
    event_values = [event_type, method, deployment, acknowledged]
    tmp_dictionary = dict(zip(event_keys, event_values))
    for k, v in tmp_dictionary.items():
        if v is not None:
            event_filters[k] = v
    if len(event_filters) == 0:
        event_filters = None
    # SystemEventDefinition query filter (NOTE: keys must be class properties)
    def_keys = ['array_name', 'platform_name', 'instrument_name', 'reference_designator','active','retired']
    def_values = [array_name, platform_name, instrument_name, reference_designator, active, retired]
    tmp_dictionary = dict(zip(def_keys, def_values))
    for k, v in tmp_dictionary.items():
        if v is not None:
            definition_filters[k] = v
    if len(definition_filters) == 0:
        definition_filters = None
    return event_filters, definition_filters

def to_bool(value):
    """ Converts 'something' to boolean. Raises exception for invalid formats.
    Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
    Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

def get_alert_alarm_json(alerts_alarms, definition_filters):
    """ For a collection of alert_alarm objects, use definition_filters to determine if this alert_alarm
    meets criteria requested, if so return alert_alarm json with the
    alert_alarm_definition embedded as a new element 'alert_alarm_definition'.
    """
    result = None
    result_json = []
    try:
        # Process each alert_alarm and include alert_alarm_definition as element in json
        if alerts_alarms:
            for alert_alarm in alerts_alarms:
                definition_id = alert_alarm.system_event_definition_id
                tmp_json_dict = alert_alarm.to_json()

                # Get SystemEventDefinition, filter based on variables in definition_filters
                event_type = alert_alarm.event_type
                definition = SystemEventDefinition.query.filter_by(id=definition_id, event_type=event_type).first()
                if definition is None:
                    message = 'No alert_alarm_definition (id:%d) for alert_alarm (id: %d).' % (definition_id, alert_alarm.id)
                    raise Exception(message)

                # Determine if this alert_alarm_definition data matches definition_filters
                tmp_json_dict['alert_alarm_definition'] = {}
                if definition_filters is None:
                    tmp_json_dict['alert_alarm_definition'] = definition.to_json()
                    result_json.append(tmp_json_dict)
                else:
                    # use definition_filters to determine if request criteria is met.
                    matches = False
                    for k,v in definition_filters.items():
                        value = getattr(definition, k)
                        if k == 'retired' or k == 'active':      # booleans
                            value = str(value).lower()
                        matches = True
                        if value != v:
                            matches = False
                            break
                    if matches:
                        tmp_json_dict['alert_alarm_definition'] = definition.to_json()
                        result_json.append(tmp_json_dict)
            result = result_json
        return result
    except:
        raise

def get_definitions_query_filter(request_args):
    """ Get query_filter for alert_alarm_definition list route.
    """
    query_filters = None
    display_retired = False
    valid_args = ['array_name', 'platform_name', 'instrument_name', 'reference_designator']
    # Process request arguments
    if 'retired' in request_args:
        if (request_args.get('retired')).lower() == 'true':
            display_retired = True
    key = None
    key_value = None
    for key in valid_args:
        if key in request_args:
            tmp = request_args.get(key)
            if tmp:
                key_value = str(tmp)
                break
    # If query_filter to be created, create it
    if key_value is not None or display_retired:
        query_filters = {}
        if key_value is not None:
            query_filters[key] = key_value
        if display_retired:
            query_filters['retired'] = True
    return query_filters

def safe_to_delete_alert_alarm_definition(id):
    """ Verify this alert_alarm_definition can be retired.
    """
    result = False
    try:
        # Get alert_alarm_definition
        alert_alarm_def = SystemEventDefinition.query.get(id)
        if alert_alarm_def is None:
            return result
        # If alert_alarm_definition already retired, just return
        if alert_alarm_def.retired is not None:
            if alert_alarm_def.retired:
                return result
        # Determine if definition id is used by any alert or alarm instances where acknowledged is False
        active_alerts_alarms = SystemEvent.query.filter_by(system_event_definition_id=id, acknowledged=False).first()
        if active_alerts_alarms is not None:
            return result
        result = True
    except:
        pass
    finally:
        return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Methods for uframe integration
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_uframe_alertfilter(request_data):
    """ Create alertfilter in uframe. Return uframe alertfilter id, None or raise Exception.
    Process:
        Create uframe data dictionary from request.data;
        Create alertfilter in uframe using uframe data dictionary created
        Return uframe alertfilter id, None or exception.
    """
    result = None
    successful_response = 'CREATED'
    try:
        # Create uframe data dictionary from request.data
        uframe_data = create_uframe_alertfilter_data(request_data)
        if uframe_data is None:
            raise Exception('Failed to create alertfilter dictionary for uframe.')

        # Create alertfilter in uframe
        response = uframe_create_alertfilter(uframe_data)
        if response.status_code !=201:
            message = '(%s) Failed to execute create_uframe_alertfilter.' % str(response.status_code)
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)

        # Evaluate response content for error or alertfilter id
        # Sample: {"message" : "Record created successfully", "id" : 2, "statusCode" : "CREATED" }
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            if response_data:
                if 'statusCode' in response_data:
                    if response_data['statusCode'] == successful_response:
                        result = response_data['id']
        return result
    except:
        raise

def update_uframe_alertfilter(request_data, id):
    """ Update alertfilter in uframe. Return if successful, Exception if error.
    Process:
        Create uframe data dictionary from request.data;
        Update alertfilter in uframe using uframe data dictionary created
        Return uframe alertfilter id, None or exception.
    """
    successful_response = 'OK'
    try:
        # Create uframe data dictionary from request.data
        uframe_data = create_uframe_alertfilter_data(request_data)
        if uframe_data is None:
            raise Exception('Unable to update alertfilter data for uframe.')
        # Update alertfilter in uframe
        response = uframe_update_alertfilter(uframe_data, id)
        if response.status_code !=200:
            message = '(%s) Failed to execute update_uframe_alertfilter (id: %d).' % (str(response.status_code), id)
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)
        # Evaluate response content for error or alertfilter id
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            if response_data:
                if 'statusCode' in response_data:
                    if response_data['statusCode'] != successful_response:
                        raise Exception('Failed to update uframe alertfilter (id: %d).' % id)
        else:
            raise Exception('uframe failed on update of alertfilter (id: %d).' % id)
        return
    except:
        raise

# todo test cases
def delete_alertfilter(id):
    """ Delete alertfilter in uframe. On error return None, else return id.

    Used when create_alert_alarm_def fails to persist to ooi-ui-services db after
    an alertfilter was created in uframe.

    Sample response dictionary for uframe for delete:
        {u'message': u'Delete successful.', u'id': 204, u'statusCode': u'OK'}
    """
    successful_response = 'OK'
    result = None
    try:
        #headers = get_api_headers('admin', 'test')                         # todo will we need some kind of auth?
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters', str(id)])
        response = requests.delete(url, timeout=(timeout, timeout_read))    # , headers=headers) todo see above
        if response.status_code != 200:
            raise Exception('(%r) Failed to execute alertfilter deletion (id: %d)' % (response.status_code, id))
        uframe_data = json.loads(response.content)
        if uframe_data is None:
            raise Exception('Failed to execute alertfilter deletion (id: %d)' % id)
        if 'statusCode' not in uframe_data:
            raise Exception('uframe returned malformed response for alertfilter deletion (id: %d)' % id)
        if 'id' not in uframe_data:
            raise Exception('uframe returned malformed response for alertfilter deletion (id: %d)' % id)
        if uframe_data['statusCode'] != successful_response:
            raise Exception('uframe failed to delete alertfilter (id: %d); statusCode: %r ' % (id, uframe_data['statusCode']) )
        result = uframe_data['id']
        return result
    except:
        return result

def get_alertfilter(id):
    """ Get alertfilter in uframe. On error return None, else return id.
    Used by update_alert_alarm on rollback when error persisting to ooi-ui-services db, then rollback
    uframe alertfilter changes. For sample response dictionary from uframe, create_uframe_alertfilter_data.
    """
    result = None
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters', str(id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        alertfilter = json.loads(response.content)
        if alertfilter is None:
            raise Exception('Failed to get alertfilter (id: %d)' % id)
        result = alertfilter
        return result
    except:
        return result

def create_uframe_alertfilter_data(data):
    """ Create alertfilter dictionary for uframe processing.

    Sample of uframe alertfilter input to create and update:
    {
        "@class":"com.raytheon.uf.common.ooi.dataplugin.alert.alertfilter.AlertFilterRecord",
        "pdId":"PD180",
        "enabled":true,
        "stream":"ctdpf_optode_calibration_coefficients",
        "referenceDesignator":{
            "node":"SP017","full":true,"subsite":"CE01ISSP","sensor":"01-CTDPFJ123"
        },
        "alertMetadata":{
            "severity" : 2,"description":"Rule 42"},
        "alertRule":{
            "filter":"GREATER","valid":true,"highVal":31.0,"lowVal":12.0,"errMessage":null
        }
    }
    """
    try:
        # Verify required fields to create alert alarm are present in data dictionary.
        #create_definition_has_required_fields(data)
        instrument_parameter_pdid = data['instrument_parameter_pdid']
        stream = data['stream']
        reference_designator = data['reference_designator']
        severity = data['severity']
        description = data['description']
        high_value = data['high_value']
        low_value = data['low_value']
        if reference_designator is None or len(reference_designator) != 27:
            raise Exception('reference_designator is None or malformed. ')
        if high_value is None and low_value is None:
            raise Exception('Parameters high_value and low_value are both None.')
        if reference_designator is None:
            raise Exception('Required parameter (reference_designator) is None.')
        else:
            subsite = reference_designator[0:8]
            node = reference_designator[9:14]
            sensor = reference_designator[15:27]

        # uframe will fail if None is provided for description
        if description is None:
            description = ''
        uframe_data = {}
        uframe_data['@class'] = 'com.raytheon.uf.common.ooi.dataplugin.alert.alertfilter.AlertFilterRecord'
        uframe_data['enabled'] = True
        uframe_data['pdId'] = instrument_parameter_pdid
        uframe_data['stream'] = stream
        uframe_data['referenceDesignator'] = {}
        uframe_data['referenceDesignator']['subsite'] = subsite
        uframe_data['referenceDesignator']['node'] = node
        uframe_data['referenceDesignator']['sensor'] = sensor
        uframe_data['referenceDesignator']['full'] = True
        uframe_data['alertMetadata'] = {}
        uframe_data['alertMetadata']['severity'] = severity
        uframe_data['alertMetadata']['description'] = description
        uframe_data['alertRule'] = {}
        uframe_data['alertRule']['filter'] = data['operator']
        uframe_data['alertRule']['valid'] = True
        uframe_data['alertRule']['highVal'] = float(high_value)
        uframe_data['alertRule']['lowVal'] = float(low_value)
        uframe_data['alertRule']['errMessage'] = None
    except:
        raise
    return uframe_data

# Note: start of unix epoch (jan 1, 1900 at midnight 00:00) in seconds == 2208988800
# http://stackoverflow.com/questions/13260863/convert-a-unixtime-to-a-datetime-object-and-back-again-pair-of-time-conversion
# Convert a unix time u to a datetime object d, and vice versa
def convert_from_utc(u): return dt.datetime.utcfromtimestamp(u)
def ut(d): return calendar.timegm(d.timetuple())

def get_uframe_info():
    """ Get uframe alertalarm configuration information. (port 12577) """
    uframe_url = current_app.config['UFRAME_ALERTS_URL']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read

def headers():
    """ Headers for uframe PUT and POST. """
    return {"Content-Type": "application/json"}

def uframe_create_alertfilter(uframe_data):
    """ Create alertfilter in uframe. """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters'])
        data = json.dumps(uframe_data)
        response = requests.post(url, timeout=(timeout, timeout_read), headers=headers(), data=data)
        return response
    except:
        raise

def uframe_update_alertfilter(uframe_data, alertfilter_id):
    """ Update alertfilter in uframe. """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters', str(alertfilter_id)])
        data = json.dumps(uframe_data)
        response = requests.put(url, timeout=(timeout, timeout_read), headers=headers(), data=data)
        return response
    except:
        raise

def uframe_acknowledge_alert_alarm(uframe_event_id, value):
    """ Update alertfilter in uframe using eventId and user email for acknowledgeBy. Return response object.
        Sample data for PUT:
        {
          "eventId":"2",
          "acknowledgedBy":"jimkorman@raytheon"
        }
    """
    log = True
    debug = True
    uframe_success = 'OK'
    result = False
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertalarms', 'ack'])
        uframe_data = {}
        uframe_data['eventId'] = str(uframe_event_id)
        uframe_data['acknowledgedBy'] = str(value)

        if debug: print '\n url: ', url
        data = json.dumps(uframe_data)
        response = requests.put(url, timeout=(timeout, timeout_read), headers=headers(), data=data)
        if response.status_code != 200:
            message = 'Failure to issue uframe acknowledge for alert_alarm (event id: %d) in uframe. ' % uframe_event_id
            if log: print '\n (uframe_acknowledge_alert_alarm) message: ', message
            raise Exception(message)

        if response.content:
            """
            Sample uframe response content:
            {"message" : "Acknowledged record [2] by [jimkorman@raytheon]", "id" : 2, "statusCode" : "OK"}
            """
            acknowledgement = json.loads(response.content)
            if 'statusCode' in acknowledgement:
                status_code =  acknowledgement['statusCode']
                if status_code == uframe_success:
                    result = True
                else:
                    message = 'Failure to acknowledge alert_alarm (event id: %d) in uframe. ' % uframe_event_id
                    if log: print '\n (uframe_acknowledge_alert_alarm) message: ', message
                    raise Exception(message)
    except Exception as err:
        if log: print '\n (log) [acknowledge_alert_alarm] message: ', err.message
        current_app.logger.exception('[acknowledge_alert_alarm] %s ' % err.message)
        #pass
    finally:
        return result
