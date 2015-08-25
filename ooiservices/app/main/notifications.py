#!/usr/bin/env python
'''
System event notifications endpoints (for Alerts & Alarms Notification process)

'''
__author__ = 'Edna Donoughe'

from flask import (current_app)
from ooiservices.app import db
from ooiservices.app.models import (UserEventNotification, User, SystemEvent, SystemEventDefinition)
from ooiservices.app.main.errors import bad_request
from ooiservices.app.redmine.routes import (create_redmine_ticket_for_notification, get_redmine_users_by_project,
                                            update_redmine_ticket_for_notification, get_redmine_ticket_for_notification)
import datetime as dt
from sqlalchemy import desc

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Notification processing - notification of Alerts/Alarms from ooi-ui-notifications service
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def begin_notification_process(id):
    """
    Initiate the notification/escalation process for an alert or an alarm (id provided)
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
    result = None
    try:
        # Get alert_alarm, alert_alarm_definition and user_event_notification to update redmine ticket
        alert_alarm, alert_alarm_definition, user_event_notification = get_redmine_info_from_alert(id)
        if alert_alarm is None or alert_alarm_definition is None or user_event_notification is None:
            message = 'Failed to retrieve alert, definition or notification for update_notification_ticket. (id: %d)' % id
            current_app.logger.exception('[update_notification_ticket] %s ' % message)
            raise Exception(message)

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
        ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, redmine_id)
        if ticket_id is None:
            message = 'Failed to create_redmine_ticket.'
            current_app.logger.exception('[begin_notification_process] %s ' % message)
            return result

        # If successful creating redmine ticket, update escalate fields
        escalated = True
        ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S") # should this be event_time?
        SystemEvent.update_alert_alarm_escalation(id=alert_alarm.id, ticket_id=ticket_id,
                                                  escalated=escalated, ts_escalated=ts_escalated)

        #ticket_link_id = TicketSystemEventLink.insert_ticket_link(system_event_id=alert_alarm.id, ticket_id=ticket_id)
        result = ticket_id

    except Exception as err:
        current_app.logger.exception('[begin_notification_process] %s ' % err.message)
    finally:
        return result

def get_redmine_info_from_alert(id):
    """ Get information necessary to create or update a redmine ticket.
    """
    alert_alarm = None
    alert_alarm_definition = None
    user_event_notification = None
    try:
        if id is None:
            raise Exception('No alert id provided (None).')

        # Get alert_alarm
        alert_alarm = SystemEvent.query.get(id)
        if alert_alarm is None:
            message = 'Failed to identify system_event with id: %d' % id
            current_app.logger.exception('[get_redmine_info_from_alert] %s ' % message)
            raise Exception(message)

        # Get alert_alarm_definition
        alert_alarm_definition = SystemEventDefinition.query.get(alert_alarm.system_event_definition_id)
        if alert_alarm_definition is None:
            message = 'Failed to identify system_event_definition with id: %d' % alert_alarm.system_event_definition_id
            current_app.logger.exception('[get_redmine_info_from_alert] %s ' % message)
            raise Exception(message)

        # Get user_event_notification by filter on alert alarm definition value
        user_event_notification = UserEventNotification.query.filter_by(system_event_definition_id=alert_alarm_definition.id).first()
        if user_event_notification is None:
            message = 'Failed to identify user_event_notification with id: %d' % alert_alarm_definition.id
            current_app.logger.exception('[get_redmine_info_from_alert] %s ' % message)
            raise Exception(message)

    except Exception as err:
        current_app.logger.exception('[get_redmine_info_from_alert] %s ' % err.message)
    finally:
        return alert_alarm, alert_alarm_definition, user_event_notification

def alert_escalation_state(id):
    """ (Alerts only) Determine alert escalation state, return action.

    valid_actions = ['begin_notification_process', 'update_notification_ticket', 'reissue_notification_ticket', None]

    Responds by indicating one of three actions to be taken:
        - if a new ticket is to be created,           ('begin_notification_process') or
        - if an existing ticket needs to be updated   ('update_notification_ticket') or
        - if another new ticket must be issued ticket ('reissue_notification_ticket') or
        - None                                        (pass)
    """
    action = None
    try:
        action = determine_action(id)
    except Exception as err:
        message = err.message
        current_app.logger.exception('[alert_escalation_state] %s ' % message)
    finally:
        return action

def determine_action(id):
    """
    For alert id, determine which valid action (or None) is next; return action. If exception, log exception.

    Note on log, debug and verbose (please leave in for now):
        log is used to enable or disable development debug when exceptions are raised, generally written to log file.
        debug is used for development debugging.
        verbose is used specifically in this method for display the list of alerts being reviewed/processed for definition.
    """
    action = None
    previous_alert = None
    previously_escalated = False
    try:
        # Get alert
        alert = SystemEvent.query.get(id)
        if alert is None:
            message = 'Failed to retrieve alert record for id provided (id:%d).' % id
            raise Exception(message)

        # Get alert_alarm_definition
        alert_alarm_definition = SystemEventDefinition.query.get(alert.system_event_definition_id)
        if alert_alarm_definition is None:
            message = 'Failed to identify system_event_definition with id: %d' % alert.system_event_definition_id
            current_app.logger.exception('[begin_notification_process] %s ' % message)
            return action

        # Get associated alerts back to when ts_start is not None (ts_start set to timestamp when this alert first arrived).
        alerts = SystemEvent.query.filter_by(system_event_definition_id=alert.system_event_definition_id).order_by(desc(SystemEvent.id)).all()

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
                current_app.logger.exception('[determine_action] %s ' % err.message)
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
                    action = 'begin_notification_process'
                    return action

                else:
                    #if debug: print '\n (debug) -- previously escalated'
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
                        message = '[determine_action] (Escalate boundary has been crossed) %s ' % err.message
                        current_app.logger.exception(message)
                    # If boundary has not been crossed, update existing ticket
                    if delta <= alert_alarm_definition.escalate_boundary:
                        # Escalate boundary has not been crossed, update existing ticket
                        action = 'update_notification_ticket'
                        return action

                    elif delta > alert_alarm_definition.escalate_boundary:
                        # Escalate boundary has been crossed, issue new ticket 'reissue_notification_ticket'
                        action = 'reissue_notification_ticket'
                        start_alert.ts_start = None
                        try:
                            db.session.add(start_alert)
                            db.session.commit()
                        except Exception as err:
                            message = '[determine_action] (Escalate boundary has been crossed) (1) %s ' % err.message
                            current_app.logger.exception(message)

                        alert.ts_start = alert.event_time
                        try:
                            db.session.add(alert)
                            db.session.commit()
                        except Exception as err:
                            message = '[determine_action] (Escalate boundary has been crossed) [2] %s ' % err.message
                            current_app.logger.exception(message)
                        return action

        return action

    except Exception as err:
        message = err.message
        current_app.logger.exception('[determine_action] %s ' % message)
        return action

def update_notification_ticket(id):
    """ Update redmine ticket as a part of alert notification process.
    """
    result = None
    try:
        # Get alert, definition and notification to update redmine ticket
        alert, definition, notification = get_redmine_info_from_alert(id)
        if alert is None or definition is None or notification is None:
            message = 'Failed to retrieve alert, definition or notification for update_notification_ticket. (id: %d)' % id
            raise Exception(message)

        # Populate required fields to create a redmine ticket
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
            message = "Invalid User ID, User record not found."
            return bad_request(message)
        assigned_id = redmine_id

        # Get alert ticket id
        ticket_id = alert.ticket_id

        ts_updated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        update_info = '\nUpdated: %s ' % ts_updated

        # Get current redmine ticket
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
            message = 'Failed to update redmine ticket (ticket_id: %d' % ticket_id
            raise Exception(message)

        return ticket_id

    except Exception as err:
        message = err.message
        current_app.logger.exception('[update_notification_ticket] %s ' % message)
        return result

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private Methods for notification service routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_user_redmine_id(project_name, name):
    """Get the redmine id for the user assigned to this alert.
    The assigned user is defined in the UserEventNotification associated with the alert_alarm definition
    (class SystemEventDefinition).
    """
    redmine_id = None
    try:
        if name is None:
            message = 'User name is None; unable to get redmine id for user assigned to alert or alarm.'
            current_app.logger.exception('[get_user_redmine_id] %s ' % message)
            return redmine_id
        list_redmine_users = get_redmine_users_by_project(project_name)
        if len(list_redmine_users) == 0:
            message = 'No redmine user for this project (%s)' % project_name
            raise Exception(message)
        redmine_users = list_redmine_users['users']
        for user_tuple in redmine_users:
            if str(user_tuple[0]) == name:
                redmine_id = user_tuple[1]
                break
        return redmine_id
    except Exception as err:
        current_app.logger.exception('[get_user_redmine_id] %s ' % err.message)
        return redmine_id

def reissue_notification_ticket(id):
    """ Create another (re-issue) redmine ticket as a part of notification process (for alerts only)
    """
    result = None
    try:
        # Get alert, definition and notification to update redmine ticket
        alert, definition, notification = get_redmine_info_from_alert(id)
        if alert is None or definition is None or notification is None:
            message = 'Failed to retrieve alert, definition or notification for update_notification_ticket. (id: %d)' % id
            current_app.logger.exception('[update_notification_ticket] %s ' % message)
            raise Exception(message)

        # Populate required fields to create a redmine ticket
        project = current_app.config['REDMINE_PROJECT_ID']

        # Get current redmine ticket
        redmine_ticket = get_redmine_ticket_for_notification(alert.ticket_id)

        # Set assigned id to reflect update to user currently assigned to alert.ticket_id
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
                message = "Invalid User ID, User record not found."
                return bad_request(message)
            assigned_id = redmine_id

        # Update description to indicate previously issued ticket id for this alert.
        update_info = '\n* Associated with previously issued ticket: %d' % alert.ticket_id

        # Create new redmine ticket
        prefix = (alert.event_type).upper() + '*: '
        subject = prefix + alert.event_response
        description = alert.event_response + update_info
        priority = definition.severity

        ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, assigned_id)
        if ticket_id is None:
            message = 'Failed to reissue (create another new)_redmine_ticket.'
            current_app.logger.exception('[reissue_notification_ticket] %s ' % message)
            return result

        # update escalate fields, if successful, create the redmine ticket
        escalated = True
        ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S") # should this be event_time?
        try:
            SystemEvent.update_alert_alarm_escalation(id=alert.id, ticket_id=ticket_id,
                                                  escalated=escalated, ts_escalated=ts_escalated)
        except Exception as err:
            message = 'Reissued redmine ticket (id:%d) but failed to update_alert_alarm_escalation; %s' % (ticket_id, err.message)
            current_app.logger.exception('[reissue_notification_ticket] %s ' % message)
            return result

        #ticket_link_id = TicketSystemEventLink.insert_ticket_link(system_event_id=alert.id, ticket_id=ticket_id)
        result = ticket_id

    except Exception as err:
        message = err.message
        current_app.logger.exception('[reissue_notification_ticket] %s ' % message)
    finally:
        return result



