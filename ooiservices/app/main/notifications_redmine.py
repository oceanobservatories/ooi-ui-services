#!/usr/bin/env python
"""
Notification functions for Red Mine (part of Alerts & Alarms escalation process)
"""
__author__ = 'Edna Donoughe'

from flask import (current_app)
from ooiservices.app import db
from ooiservices.app.models import (User, SystemEvent, UserEventNotification, SystemEventDefinition)
from ooiservices.app.redmine.routes import (create_redmine_ticket_for_notification, get_redmine_users_by_project,
                                            update_redmine_ticket_for_notification, get_redmine_ticket_for_notification)
import datetime as dt
from sqlalchemy import desc


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Escalation notification using Red Mine
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def handle_redmine_notifications(id):
    """
    Escalation notification processing is handled here for red mine.

    When an alert or an alarm is created, the state of the alert escalation process is determined.
    For each of the three escalation states ('begin_notification', 'update_notification', 'reissue_notification'),
    there is a corresponding function (of the same name) which process the notification for that state.
    Each of these functions handles the case when use_redmine is either enabled or disabled (both are required).
    """
    try:
        # Get alert_alarm using id provided
        alert_alarm = SystemEvent.query.get(id)
        if alert_alarm is None:
            message = 'Failed to retrieve SystemEvent to handle_notifications for id: %d' % id
            current_app.logger.info('[handle_redmine_notifications] %s ' % message)
            raise Exception(message)

        # Get alert_alarm, alert_alarm_definition and user_event_notification to process redmine notification
        alert_alarm, alert_alarm_definition, user_event_notification = get_info_from_alert(id)
        if alert_alarm is None or alert_alarm_definition is None or user_event_notification is None:
            message = 'Failed to retrieve alert, definition or notification for handle_redmine_notifications. (id: %d)' % id
            current_app.logger.info('[handle_redmine_notifications] %s ' % message)
            raise Exception(message)

        # If 'alert' received, start the alert escalation process, otherwise begin the process for an alarm.
        valid_actions = ['begin_notification', 'update_notification', 'reissue_notification']

        # Process alert for redmine notifications
        if alert_alarm.event_type == 'alert':
            action = alert_escalation_state(alert_alarm.id)
            if action is not None:
                is_dirty = False
                if action in valid_actions:

                    # Begin notification
                    if action == 'begin_notification':
                        ticket_id = begin_notification(alert_alarm, alert_alarm_definition, user_event_notification)
                        if ticket_id is None:
                            message = 'Failed to create notification for alert notification (id:%d).' % alert_alarm.id
                            current_app.logger.info(message)
                            raise Exception(message)
                        else:
                            alert_alarm.ticket_id = ticket_id
                            is_dirty = True

                    # Update notification
                    elif action == 'update_notification':
                        ticket_id = update_notification(alert_alarm, alert_alarm_definition, user_event_notification)
                        if ticket_id is None:
                            message ='Failed to update notification for alert notification (id:%d)' % alert_alarm.id
                            current_app.logger.info(message)

                    # Reissue notification
                    elif action == 'reissue_notification':
                        ticket_id = reissue_notification(alert_alarm, alert_alarm_definition, user_event_notification)
                        if ticket_id is None:
                            message ='Failed to reissue notification for alert notification (id:%d)' % alert_alarm.id
                            current_app.logger.info(message)
                        else:
                            alert_alarm.ticket_id = ticket_id
                            is_dirty = True

                    # Update alert_alarm if dirty
                    if is_dirty:
                        try:
                            db.session.add(alert_alarm)
                            db.session.commit()
                        except Exception as err:
                            message = 'Error updating alert_alarm with redmine ticket_id; %s' % str(err.message)
                            current_app.logger.info(message)
                            raise Exception(message)

        # Process alarm for redmine notifications
        elif alert_alarm.event_type == 'alarm':
            ticket_id = begin_notification(alert_alarm, alert_alarm_definition, user_event_notification)
            if ticket_id is None:
                message = 'Failed to create notification for alarm (id:%d)' % alert_alarm.id
                current_app.logger.info(message)
                raise Exception(message)

    except Exception as err:
        message = 'Exception handle_redmine_notifications. %s' % err.message
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Three functions to process escalation states:  begin_notification, update_notification, reissue_notification
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def begin_notification(alert_alarm, alert_alarm_definition, user_event_notification):
    """
    Initiate the notification/escalation process for an alert or an alarm.
    Process:
    - Get alert_alarm
    - Get alert_alarm_definition
    - Get user_event_notification information
    * Create initial notification
    - if successful, then:
        alert_alarm.escalated =True;
        alert_alarms_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        alert_alarm.ticket_id = ticket_id (id from redmine or zero (0) otherwise)
        persist escalation field changes with update_alert_alarm
    """
    result = None
    try:
        ticket_id = 0

        # If red mine enabled:
        if user_event_notification.use_redmine:
            ticket_id = begin_notification_redmine(alert_alarm, alert_alarm_definition, user_event_notification)

        # Update escalate fields.
        if ticket_id is not None:
            escalated = True
            ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
            SystemEvent.update_alert_alarm_escalation(id=alert_alarm.id, ticket_id=ticket_id,
                                                      escalated=escalated, ts_escalated=ts_escalated)
        return ticket_id

    except Exception as err:
        current_app.logger.info('[begin_notification] %s ' % err.message)
        return result


def update_notification(alert, definition, notification):
    """ Update notification as a part of alert notification process.
    """
    result = None
    try:
        # If red mine enabled:
        if notification.use_redmine:
            result = update_notification_redmine(alert, definition, notification)
        return result

    except Exception as err:
        current_app.logger.info('[update_notification] %s ' % err.message)
        return result


def reissue_notification(alert, definition, notification):
    """ Create another (re-issue notification) as a part of esclation process (for alerts only)
    """
    result = None
    try:
        ticket_id = 0

        # If red mine enabled:
        if notification.use_redmine:
            ticket_id = reissue_notification_redmine(alert, definition, notification)
            if ticket_id is None:
                message = 'Failed to reissue (create another new)_redmine_ticket.'
                current_app.logger.info('[reissue_notification] %s ' % message)
                return result
            # Prepare base exception message for update when using redmine for notification
            exception_message = 'Reissued redmine ticket (id:%d) but failed to update_alert_alarm_escalation; ' % ticket_id
        else:
            # Prepare base exception message for update when NOT using redmine for notification
            exception_message = 'Reissued notification but failed to update_alert_alarm_escalation; '

        # update escalate fields
        escalated = True
        ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        try:
            SystemEvent.update_alert_alarm_escalation(id=alert.id, ticket_id=ticket_id,
                                                  escalated=escalated, ts_escalated=ts_escalated)
        except Exception as err:
            message = exception_message + str(err.message)
            current_app.logger.info('[reissue_notification] %s ' % message)
            return result

        result = ticket_id

    except Exception as err:
        current_app.logger.info('[reissue_notification] %s ' % err.message)
    finally:
        return result


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Three redmine specific functions for processing escalation states:
#   'begin_notification', 'update_notification', 'reissue_notification'
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def begin_notification_redmine(alert_alarm, alert_alarm_definition, user_event_notification):
    """
    Initiate the notification for the escalation process, either for an alert or an alarm.
    Process:
    - Use alert_alarm, alert_alarm_definition, user_event_notification information
    * Create initial notification (for example, create red mine ticket and get ticket id)
    - if successful, then:
        alert_alarm.escalated =True;
        alert_alarms_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        alert_alarm.ticket_id = ticket_id (id from redmine or zero (0) otherwise)
        persist escalation field changes with update_alert_alarm
    """
    ticket_id = None
    try:
        # Create redmine ticket
        ticket_id = create_redmine_notification(alert_alarm, alert_alarm_definition, user_event_notification)
        return ticket_id

    except Exception as err:
        message = '[begin_notification_redmine] %s ' % err.message
        current_app.logger.info(message)
        return ticket_id

def update_notification_redmine(alert, definition, notification):
    """ Update redmine ticket as a part of alert notification process.
    """
    result = None
    try:
        # Get alert ticket id
        ticket_id = alert.ticket_id

        # Populate required fields to update a redmine ticket
        project = current_app.config['REDMINE_PROJECT_ID']

        # Use user_event_notification for determining assigned user's redmine id
        redmine_id = 1
        assigned_user = User.query.get(notification.user_id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
            tmp_id = get_user_redmine_id(project, name)
            if tmp_id is not None:
                redmine_id = tmp_id
        else:
            message = 'Invalid User ID, User record not found.'
            current_app.logger.info(message)
            raise Exception(message)
        assigned_id = redmine_id

        ts_updated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        update_info = '\nUpdated: %s ' % ts_updated

        # If no previous ticket_id associated (case where 'use_redmine' was enabled AFter alert has escalated)
        if ticket_id == 0:

            # Create redmine ticket
            prefix = (alert.event_type).upper() + ': '
            subject = prefix + alert.event_response
            description = alert.event_response
            priority = definition.severity
            ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, redmine_id)
            if ticket_id is None:
                message = 'Failed to create base redmine ticket (on update) for alert notification (id:%d).' % alert.id
                current_app.logger.info(message)
                raise Exception(message)

            # Update escalate fields.
            if ticket_id is not None:
                escalated = True
                ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
                SystemEvent.update_alert_alarm_escalation(id=alert.id, ticket_id=ticket_id,
                                                          escalated=escalated, ts_escalated=ts_escalated)
        # Get existing redmine ticket
        redmine_ticket = get_redmine_ticket_for_notification(ticket_id)

        # Set fields for update
        project = redmine_ticket['project']
        subject = redmine_ticket['subject']
        description = redmine_ticket['description']
        priority = redmine_ticket['priority']
        if 'assigned_to' in redmine_ticket:
            assigned_id = redmine_ticket['assigned_to']

        # Update subject for recent receipt of alert (not past escalate boundary yet)
        description += update_info
        result = update_redmine_ticket_for_notification(ticket_id, project, subject, description, priority, assigned_id)
        if result is None:
            message = 'Failed to update redmine ticket (ticket_id: %d)' % ticket_id
            current_app.logger.info(message)
            raise Exception(message)

        return ticket_id

    except Exception as err:
        message = '[update_redmine_notification_ticket] %s ' % str(err.message)
        current_app.logger.info(message)
        return result


def reissue_notification_redmine(alert, definition, notification):
    """ Create another (re-issue) redmine ticket as a part of notification process (for alerts only).
    """
    result = None
    try:
        # Populate required fields to create a redmine ticket and get current redmine ticket
        project = current_app.config['REDMINE_PROJECT_ID']
        redmine_ticket = get_redmine_ticket_for_notification(alert.ticket_id)

        # Set  new notification assigned_id to be same user assigned in alert.ticket_id
        if 'assigned_to' in redmine_ticket:
            assigned_id = redmine_ticket['assigned_to']
        else:
            # Use user_event_notification for determining assigned user's redmine id
            redmine_id = 1
            assigned_user = User.query.get(notification.user_id)
            if assigned_user is not None:
                name = assigned_user.first_name + ' ' + assigned_user.last_name
                tmp_id = get_user_redmine_id(project, name)
                if tmp_id is not None:
                    redmine_id = tmp_id
            else:
                message = 'Invalid User ID, User record not found.'
                current_app.logger.info(message)
                raise exception(message)
            assigned_id = redmine_id

        # Update description to indicate previously issued ticket id for this alert.
        update_info = '\n* Associated with previously issued ticket: %d' % alert.ticket_id

        # Create new redmine ticket; on error, log info and return None
        prefix = (alert.event_type).upper() + '*: '
        subject = prefix + alert.event_response
        description = alert.event_response + update_info
        priority = definition.severity
        ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, assigned_id)
        if ticket_id is None:
            message = 'Failed to reissue (create another)_redmine_ticket.'
            current_app.logger.info('[reissue_redmine_notification_ticket] %s ' % message)
            return result

        result = ticket_id
        return result

    except Exception as err:
        message = '[reissue_redmine_notification_ticket] message: %s' % err.message
        current_app.logger.info(message)
        return result


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private red mine specific utility functions for processing red mine notifications.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_redmine_notification(alert_alarm, alert_alarm_definition, user_event_notification):
    """ Create redmine notification (ticket) to begin notification process using redmine. Returns ticket_id or None.
    """
    result = None
    try:
        # Populate required fields to create a redmine ticket
        project = current_app.config['REDMINE_PROJECT_ID']

        # Use user_event_notification for determining assigned user's redmine id
        redmine_id = 1  # this assumes Redmine Admin is assigned to redmine user id 1
        assigned_user = User.query.get(user_event_notification.user_id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
            tmp_id = get_user_redmine_id(project, name)
            if tmp_id is not None:
                redmine_id = tmp_id

        # Create redmine ticket
        prefix = (alert_alarm.event_type).upper() + ': '
        subject = prefix + alert_alarm.event_response
        description = alert_alarm.event_response
        priority = alert_alarm_definition.severity
        result = create_redmine_ticket_for_notification(project, subject, description, priority, redmine_id)
        return result

    except Exception as err:
        message = '[create_redmine_notification] %s ' % err.message
        current_app.logger.info(message)
        return result


def get_user_redmine_id(project_name, name):
    """Get the redmine id for the user assigned to this alert.
    The assigned user is defined in the UserEventNotification associated with the alert_alarm definition
    (class SystemEventDefinition).
    """
    redmine_id = None
    try:
        if name is None:
            message = 'User name is None; unable to get redmine id for user assigned to alert or alarm.'
            current_app.logger.info('[get_user_redmine_id] %s ' % message)
            return redmine_id
        list_redmine_users = get_redmine_users_by_project(project_name)
        if len(list_redmine_users) == 0:
            message = 'No redmine user for this project (%s)' % project_name
            current_app.logger.info('[get_user_redmine_id] %s ' % message)
            raise Exception(message)
        redmine_users = list_redmine_users['users']
        for user_tuple in redmine_users:
            if str(user_tuple[0]) == name:
                redmine_id = user_tuple[1]
                break
        return redmine_id
    except Exception as err:
        current_app.logger.info('[get_user_redmine_id] %s ' % err.message)
        return redmine_id


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private functions for handling notification processing, regardless of notification type.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_info_from_alert(id):
    """ Get information necessary to create or update a notification.
    """
    alert_alarm = None
    alert_alarm_definition = None
    user_event_notification = None
    try:
        if id is None:
            message = 'No alert id provided (None).'
            current_app.logger.info('[get_info_from_alert] %s ' % message)
            raise Exception(message)

        # Get alert_alarm
        alert_alarm = SystemEvent.query.get(id)
        if alert_alarm is None:
            message = 'Failed to identify system_event with id: %d' % id
            current_app.logger.info('[get_info_from_alert] %s ' % message)
            raise Exception(message)

        # Get alert_alarm_definition
        alert_alarm_definition = SystemEventDefinition.query.get(alert_alarm.system_event_definition_id)
        if alert_alarm_definition is None:
            message = 'Failed to identify system_event_definition with id: %d' % alert_alarm.system_event_definition_id
            current_app.logger.info('[get_info_from_alert] %s ' % message)
            raise Exception(message)

        # Get user_event_notification by filter on alert alarm definition value
        user_event_notification = UserEventNotification.query.filter_by(system_event_definition_id=alert_alarm_definition.id).first()
        if user_event_notification is None:
            message = 'Failed to identify user_event_notification with id: %d' % alert_alarm_definition.id
            current_app.logger.info('[get_info_from_alert] %s ' % message)
            raise Exception(message)

    except Exception as err:
        current_app.logger.info('[get_info_from_alert] %s ' % err.message)
    finally:
        return alert_alarm, alert_alarm_definition, user_event_notification

def alert_escalation_state(id):
    """ (Alerts only) Determine alert escalation state, return action.

    valid_actions = ['begin_notification', 'update_notification', 'reissue_notification', None]

    Responds by indicating one of three actions to be taken:
        - if a new notification is to be created,           ('begin_notification') or
        - if an existing notification needs to be updated   ('update_notification') or
        - if another new notification must be issued ticket ('reissue_notification') or
        - None                                        (pass)
    """
    action = None
    try:
        action = determine_action(id)
    except Exception as err:
        current_app.logger.info('[alert_escalation_state] %s ' % err.message)
    finally:
        return action


def determine_action(id):
    """ For alert id, determine which valid action (or None) is next; return action. If exception, log exception.
    """
    action = None
    previous_alert = None
    previously_escalated = False
    try:
        # Get alert
        alert = SystemEvent.query.get(id)
        if alert is None:
            message = 'Failed to retrieve alert record for id provided (id:%d).' % id
            current_app.logger.info('[determine_action] %s ' % message)
            raise Exception(message)

        # Get alert_alarm_definition
        alert_alarm_definition = SystemEventDefinition.query.get(alert.system_event_definition_id)
        if alert_alarm_definition is None:
            message = 'Failed to identify system_event_definition with id: %d' % alert.system_event_definition_id
            current_app.logger.info('[determine_action] %s ' % message)
            return action

        # Get associated alerts back to when ts_start is not None (ts_start set to timestamp when
        # this alert first arrived).
        alerts = SystemEvent.query.filter_by(
            system_event_definition_id=alert.system_event_definition_id).order_by(desc(SystemEvent.id)).all()

        # Determine whether additional alerts have arrived since first alert
        found_alerts = False
        if alerts is not None:
            for item in alerts:
                if item.id == alert.id:
                    pass
                else:
                    found_alerts = True

        # If this is the FIRST alert for this definition, set ts_start to current datetime, return None
        if not found_alerts:
            alert.ts_start = alert.event_time
            try:
                db.session.add(alert)
                db.session.commit()
            except Exception as err:
                current_app.logger.info('[determine_action][1] %s ' % err.message)
            return action

        # Not the first alert received for this definition, evaluate this alert to determine whether to escalate.
        # Or if escalated == True, then have we exceeded the escalate boundary (if so, re-issue ticket)
        else:
            # Determine if previously escalated, review previous alert to see if escalated is True. Save previous_alert.
            previously_escalated = False
            inx = 1
            for item in alerts:
                if inx > 1:
                    if item.escalated == True:
                        previously_escalated = True
                        previous_alert = item
                        break
                inx += 1

            # Determine start_alert (ts_start is not None)
            start_alert = None
            for item in alerts:
                if item.ts_start is not None:
                    start_alert = item
                    break

            # Now have initial alert which kicked off (start_alert)
            # Evaluate time delta (event_time) of this alert versus start_alert
            delta = (alert.event_time - start_alert.ts_start).total_seconds()

            # if delta is greater than escalate_on value (from definition), has alert been previously escalated?
            if delta <= alert_alarm_definition.escalate_on:
                pass
            elif delta > alert_alarm_definition.escalate_on:

                # if alert hasn't been previously escalated, begin escalation
                if not previously_escalated: #alert.escalated:
                    action = 'begin_notification'
                    return action

                else:
                    # if alert previously escalated, determine if we have crossed escalate_boundary.
                    # If escalate boundary is crossed:
                    #     First:
                    #        reset start_alert.ts_start - None
                    #        alert.ts_start - event_time
                    #     Proceed to reissue ticket where:
                    #      escalated True, timestamp None
                    #      update ticket_id to be for new ticket_id created
                    # Carry forward some escalation data from previous alert...
                    try:
                        alert.escalated = previous_alert.escalated
                        alert.ts_escalated = previous_alert.ts_escalated
                        alert.ticket_id = previous_alert.ticket_id
                        db.session.add(alert)
                        db.session.commit()
                    except Exception as err:
                        message = '[determine_action][2] (Escalate boundary has been crossed) %s ' % err.message
                        current_app.logger.info(message)
                    # If boundary has not been crossed, update existing ticket
                    if delta <= alert_alarm_definition.escalate_boundary:
                        # Escalate boundary has not been crossed, update existing ticket
                        action = 'update_notification'
                        return action

                    elif delta > alert_alarm_definition.escalate_boundary:
                        # Escalate boundary has been crossed, issue new ticket 'reissue_notification_ticket'
                        action = 'reissue_notification'
                        start_alert.ts_start = None
                        try:
                            db.session.add(start_alert)
                            db.session.commit()
                        except Exception as err:
                            message = '[determine_action][3] (Escalate boundary has been crossed) (1) %s ' % err.message
                            current_app.logger.info(message)

                        alert.ts_start = alert.event_time
                        try:
                            db.session.add(alert)
                            db.session.commit()
                        except Exception as err:
                            message = '[determine_action][4] (Escalate boundary has been crossed) [2] %s ' % err.message
                            current_app.logger.info(message)
                        return action

        return action

    except Exception as err:
        current_app.logger.info('[determine_action] %s ' % err.message)
        return action