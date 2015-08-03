#!/usr/bin/env python
'''
User event notifications endpoints (for Alerts & Alarms Notification process)

'''
__author__ = 'Edna Donoughe'

from flask import (jsonify, request, current_app, url_for)
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.models import (UserEventNotification, User, SystemEvent, SystemEventDefinition, TicketSystemEventLink)
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import conflict, bad_request
from ooiservices.app.redmine.routes import create_redmine_ticket_for_notification, get_redmine_users_by_project
from ooiservices.app.main.user import get_current_user
import json
import requests
import datetime as dt
from base64 import b64encode

#PROJECT = 'ooi-ui-api-testing'

# todo - discuss scope_required for 'notifications'
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Notification routes and processing - notification of Alerts/Alarms from ooi-ui-notifications service
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Begin notification process for an alert or an alarm
#@api.route('/notifications/begin_notification_process/<int:id>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
#@scope_required(u'redmine')
def begin_notification_process(id):
    # todo if not a route, then return dict {status: 'ok', message: ''}
    """
    Initiate the escalation process for an alert or an alarm (id provided)
    Process:
    - Get alert_alarm
    - Get alert_alarm_definition
    - Get user_event_notification information
    * Create initial [red mine] ticket, get ticket id
    - if successful creating ticket, then:
        alert_alarm.escalated =True;
        alert_alarms_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        alert_alarm.ticket_id = ticket_id
        persist escalation field changes with update_alert_alarm
    """
    debug = False
    log = True
    if debug: print '\n debug -- (notifications) begin_notification_process...'
    try:
        # Get alert_alarm
        alert_alarm = SystemEvent.query.get(id)
        if alert_alarm is None:
            message = 'Failed to identify system_event with id: %d' % id
            if log: print '\n message: ', message
            current_app.logger.exception('[begin_notification_process] %s ' % message)
            return jsonify(), 200

        if debug: print '\n debug -- (notifications) processing event_type: ', alert_alarm.event_type
        # Get alert_alarm_definition
        alert_alarm_definition = SystemEventDefinition.query.get(alert_alarm.system_event_definition_id)
        if alert_alarm is None:
            message = 'Failed to identify system_event_definition_id with id: %d' % alert_alarm.system_event_definition_id
            if log: print '\n message: ', message
            current_app.logger.exception('[begin_notification_process] %s ' % message)
            return jsonify(), 200
        # Get user_event_notification by filter on alert alarm definition value
        user_event_notification = UserEventNotification.query.filter_by(system_event_definition_id=alert_alarm_definition.id).first()
        if user_event_notification is None:
            message = 'Failed to identify user_event_notification with id: %d' % alert_alarm_definition.id
            #print '\n +++ message: ', message
            if log: print '\n message: ', message
            current_app.logger.exception('[begin_notification_process] %s ' % message)
            return jsonify(), 200

        # Populate required fields to create a redmine ticket
        project = current_app.config['REDMINE_PROJECT_ID']

        # TODO Get targeted user for notification - NOT current user

        if debug: print '\n ---- Get targeted user for redmine assignment using user_event_notification...'
        # Use user_event_notification for determining assigned user's redmine id
        redmine_id = 1
        name = None
        assigned_user = User.query.get(user_event_notification.user_id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
            tmp_id = get_user_redmine_id(project, name)
            if tmp_id is not None:
                redmine_id = tmp_id

        if debug: print '\n debug -- (notifications) Creating redmine ticket for \'%s\' (project: %s), get ticket_id...' % \
                        (name, project)

        # Create redmine ticket
        prefix = (alert_alarm.event_type).upper() + ': '
        subject = prefix + alert_alarm.event_response
        description = alert_alarm.event_response
        priority = alert_alarm_definition.severity
        ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, redmine_id)
        if ticket_id is None:
            message = 'Failed to create_redmine_ticket.'
            current_app.logger.exception('[begin_notification_process] %s ' % message)
            return jsonify(), 200

        # If successful creating redmine ticket, update escalate fields
        escalated = True
        ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        SystemEvent.update_alert_alarm_escalation(id=alert_alarm.id, ticket_id=ticket_id,
                                                  escalated=escalated, ts_escalated=ts_escalated)
        ticket_link_id = TicketSystemEventLink.insert_ticket_link(system_event_id=alert_alarm.id, ticket_id=ticket_id)
        #if debug: print '\n debug -- (notifications) ticket_link_id: ', ticket_link_id
        '''
        # debug - view contents of alert_alarm escalation fields; verify changes have been persisted
        escalated_alert_alarm = SystemEvent.query.get(alert_alarm.id)
        print '\n *** escalated alert_alarm.to_json(): ', escalated_alert_alarm.to_json()
        '''

        if debug: print '\n debug -- (notifications) \'%s\' has been escalated!' % alert_alarm.event_type
        return jsonify(), 200
    except Exception as err:
        message = '[begin_notification_process] Exception: ', err.message
        if debug: print '\n message: ', message
        current_app.logger.exception('[begin_notification_process] %s ' % err.message)
        return jsonify(), 200

#@api.route('/notifications/start_alert_escalation_process/<int:id>', methods=['GET'])
# @auth.login_required
# @scope_required(u'user_admin')
# @scope_required(u'redmine')
def alert_escalation_state(id):
    """ (Alerts only) Set notification service in motion when alert is received; fire and forget.
    Alert has occurred and persisted - send SystemEvent id to notification service GET request. (Note: alerts only!)

    Responds by indicating one of three actions to be taken:
        - if a new ticket is to be created,           ('begin_notification_process') or
        - if an existing ticket needs to be updated   ('update_notification_ticket') or
        - if another new ticket must be issued ticket ('reissue_notification_ticket')
    """
    #print '\n (notifications) start_alert_escalation_process...'
    action = None
    try:
        valid_actions = ['begin_notification_process', 'update_notification_ticket', 'reissue_notification_ticket']
        #action = 'reissue_notification_ticket' # this path exercised, another new ticket created for existing alert
        action = 'begin_notification_process'   # todo insert logic block for alert escalation state review here
        #action = determine_action(id)          # actual alert escalation state review to determine action goes here
        if action not in valid_actions:
            message = 'Invalid action \'%s\' situation, failure to process alert (id:%d) escalation.' % (action, id)
            current_app.logger.exception('[start_alert_escalation_process] %s ' % message)
        return action
    except Exception as err:
        message = err.message
        #print '\n [start_alert_escalation_process] %s ' % message
        current_app.logger.exception('[start_alert_escalation_process] %s ' % message)
        return action

#@api.route('/notifications/update_notification_ticket/<>int:id', methods=['GET'])
# @auth.login_required
# @scope_required(u'user_admin')
# @scope_required(u'redmine')
def update_notification_ticket(id):
    """ Update redmine ticket as a part of notification process (for alerts only)
    """
    result = None
    try:
        if id is None:
            raise Exception('No alert id provided (None).')

        alert = SystemEvent.query.get(id)
        if alert is None:
            raise Exception('Failed to retrieve alert record for id provided (id:%d).' % id)

        # Get alert ticket id (last instance of alert entered in ticket_system_event_link
        ticket_id = alert.ticket_id
        #print '\n update_notification_ticket: ', ticket_id
        result = update_redmine_ticket(ticket_id)
        if not result:
            raise Exception('Failed to update redmine ticket (ticket_id: %d' % ticket_id)
        return ticket_id
    except Exception as err:
        message = err.message
        current_app.logger.exception('[update_notification_ticket] %s ' % message)
        return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private Methods for notification service routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_user_redmine_id(project_name, name):

    # for testing use name = 'OOI_UI_User for API Testing'
    redmine_id = None
    try:
        if name is None:
            message = 'User name is None; unable to get redmine id for user assigned to alert or alarm.'
            current_app.logger.exception('[get_user_redmine_id] %s ' % message)
            return redmine_id
        #list_redmine_users = _get_redmine_users()
        list_redmine_users = get_redmine_users_by_project(project_name)
        #print '\n --- list_redmine_users: ', list_redmine_users
        redmine_users = list_redmine_users['users']
        for user_tuple in redmine_users:
            if str(user_tuple[0]) == name:
                redmine_id = user_tuple[1]
                #print '\n found the name!! redmine_id: ', redmine_id
                break
        return redmine_id
    except Exception as err:
        print '\n [get_user_redmine_id] %s ' % err.message
        current_app.logger.exception('[get_user_redmine_id] %s ' % err.message)

def update_redmine_ticket(ticket_id):
    """
    Update redmine ticket and return unique ticket_id. Return None or raise exception if failure.
    """
    # todo under construction
    try:
        if ticket_id is None:
            raise Exception('No ticket_id provided (None).')
        print '\n todo -- update_redine_ticket'
        return ticket_id
    except Exception as err:
        message = 'Insufficient data, or bad data format. (%s)' % err.message
        print '\n message: ', message
        raise

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# UserEventNotification routes and processing - User event notification details (who and how to notify)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#List all user_event_notifications (by user_id if provided)
@api.route('/user_event_notifications')
def get_user_event_notifications():
    result = []
    if 'user_id' in request.args:
        notifications = UserEventNotification.query.filter_by(event_type=request.args.get('user_id'))
    else:
        notifications = UserEventNotification.query.all()
    if notifications:
        result = [notify.to_json() for notify in notifications]
    return jsonify( {'notifications' : result })

#List a user_event_notification by id
@api.route('/user_event_notification/<int:id>')
def get_user_event_notification(id):
    notification = UserEventNotification.query.filter_by(id=id).first_or_404()
    return jsonify(notification.to_json())

#Create a new user_event_notification
@api.route('/user_event_notification', methods=['POST'])
# @auth.login_required
# @scope_required('annotate')
def create_user_event_notification():
    """
    Create user_event_notification associated with SystemEventDefinition.

    Usage: Whenever a SystemEvent occurs, for the system_event_definition_id, this notification
    indicates who and how to contact them with the SystemEvent information.
    """
    try:
        data = json.loads(request.data)
        create_has_required_fields(data)
        # Validate user to be notified exists
        user_id = data['user_id']
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify(error="Invalid User ID, User record not found"), 404
        # Create UserEventNotification
        notification = UserEventNotification()
        notification.system_event_definition_id = data['system_event_definition_id']
        notification.user_id = data['user_id']
        notification.use_email = data['use_email']
        notification.use_redmine = data['use_redmine']
        notification.use_phone = data['use_phone']
        notification.use_log = data['use_log']
        notification.use_sms = data['use_sms']
        try:
            db.session.add(notification)
            db.session.commit()
        except Exception as err:
            print '\n message: ', err.message
            db.session.rollback()
            return bad_request('IntegrityError creating notification')
        return jsonify(notification.to_json()), 201
    except Exception as err:
        #print '\n exception: ', err.message
        return conflict('Insufficient data, or bad data format.')

#Update an existing user_event_notification
@api.route('/user_event_notification/<int:id>', methods=['PUT'])
# @auth.login_required
# @scope_required('annotate')
def update_user_event_notification(id):
    """ Update user_event_notification associated with SystemEventDefinition.
    """
    try:
        data = json.loads(request.data)
        create_has_required_fields(data)
        # Validate user to be notified exists
        user_id = data['user_id']
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify(error="Invalid User ID, User record not found"), 404
        # Get existing notification
        notification = UserEventNotification.query.filter_by(id=id).first()
        if not notification:
            return jsonify(error="Invalid ID, record not found"), 404
        notification.system_event_definition_id = data['system_event_definition_id']
        notification.user_id = data['user_id']
        notification.use_email = data['use_email']
        notification.use_redmine = data['use_redmine']
        notification.use_phone = data['use_phone']
        notification.use_log = data['use_log']
        notification.use_sms = data['use_sms']
        try:
            db.session.add(notification)
            db.session.commit()
        except Exception as err:
            print '\n message: ', err.message
            db.session.rollback()
            return bad_request('IntegrityError creating notification')
        return jsonify(notification.to_json()), 201
    except Exception as err:
        #print '\n exception: ', err.message
        return conflict('Insufficient data, or bad data format.')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private Methods for user_event_notification routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_has_required_fields(data):
    """ Verify create_user_event_notification request.data has required fields. Error otherwise.
    """
    try:
        required_fields = ['system_event_definition_id', 'user_id', 'use_email', 'use_redmine',
                           'use_phone', 'use_log', 'use_sms']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%s) in request.data' % field
                #print '\n message: ', message
                raise Exception(message)
        return
    except Exception as err:
        message = 'Insufficient data, or bad data format. (%s)' % err.message
        #print '\n message: ', message
        raise

'''
# Hold following until we determine if we wish to tag as 'reissued'; use begin_notification_process
#@api.route('/notifications/reissue_notification_ticket')
# @auth.login_required
# @scope_required(u'user_admin')
# @scope_required(u'redmine')
def reissue_notification_ticket(id):
    """ Create another (re-issue) redmine ticket as a part of notification process (for alerts only)
    """
    result = None
    try:
        if id is None:
            raise Exception('No alert id provided (None).')

        alert = SystemEvent.query.get(id)
        if alert is None:
            raise Exception('Failed to retrieve alert record for id provided (id:%d).' % id)

        print '\n (notifications) reissue_notification_ticket...'

        # Populate required fields to create another redmine ticket
        # Create another redmine ticket for this alert

        return jsonify(), 200
    except Exception as err:
        message = err.message
        #print '\n message: ', message
        current_app.logger.exception('[reissue_notification_ticket] %s ' % message)
        raise
'''

