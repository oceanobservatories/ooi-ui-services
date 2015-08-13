#!/usr/bin/env python
'''
User event notifications endpoints (for Alerts & Alarms Notification process)

'''
__author__ = 'Edna Donoughe'

from flask import (current_app)
from ooiservices.app import db
#from ooiservices.app.decorators import scope_required
#from ooiservices.app.main.authentication import auth
from ooiservices.app.models import (UserEventNotification, User, SystemEvent, SystemEventDefinition, TicketSystemEventLink)
from ooiservices.app.main.errors import bad_request
from ooiservices.app.redmine.routes import (create_redmine_ticket_for_notification, get_redmine_users_by_project,
                                            update_redmine_ticket_for_notification, get_redmine_ticket_for_notification)
import datetime as dt
from sqlalchemy import desc

# todo - discuss scope_required for 'notifications'
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Notification processing - notification of Alerts/Alarms from ooi-ui-notifications service
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Begin notification process for an alert or an alarm
def begin_notification_process(id):
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
    #log = False
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

        if debug: print '\n \t(debug) ---- Get targeted user for redmine assignment using user_event_notification...'
        # Use user_event_notification for determining assigned user's redmine id
        redmine_id = 1  # this assumes Redmine ADmin is assigned to redmine user id 1; should lookup 'Redmine Admin' todo
        name = None
        assigned_user = User.query.get(user_event_notification.user_id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
            tmp_id = get_user_redmine_id(project, name)
            if tmp_id is not None:
                redmine_id = tmp_id

        if debug: print '\n \t(debug) -- Creating redmine ticket for \'%s\' (project: %s), get ticket_id...' % \
                        (name, project)

        # Create redmine ticket
        prefix = (alert_alarm.event_type).upper() + ': '
        subject = prefix + alert_alarm.event_response
        description = alert_alarm.event_response
        priority = alert_alarm_definition.severity
        ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, redmine_id)
        if ticket_id is None:
            message = 'Failed to create_redmine_ticket.'
            print'\n \t-- message: ', message
            current_app.logger.exception('[begin_notification_process] %s ' % message)
            return result

        # If successful creating redmine ticket, update escalate fields
        escalated = True
        ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S") # should this be event_time?
        SystemEvent.update_alert_alarm_escalation(id=alert_alarm.id, ticket_id=ticket_id,
                                                  escalated=escalated, ts_escalated=ts_escalated)

        if debug: print '\n \t(debug) -- updated alert_alarm: ', alert_alarm.to_json()
        ticket_link_id = TicketSystemEventLink.insert_ticket_link(system_event_id=alert_alarm.id, ticket_id=ticket_id)
        if debug: print '\n \t(debug) -- [begin_notification_process] \'%s\' has been escalated!' % alert_alarm.event_type
        if debug: print '\n \tbegin_notification_process - ticket_id: ', ticket_id
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
    #debug = False
    #log = False
    try:
        if id is None:
            raise Exception('No alert id provided (None).')

        # Get alert_alarm
        alert_alarm = SystemEvent.query.get(id)
        if alert_alarm is None:
            message = 'Failed to identify system_event with id: %d' % id
            #if log: print '\n (debug) -- get_redmine_info_from_alert - message: ', message
            current_app.logger.exception('[get_redmine_info_from_alert] %s ' % message)
            raise Exception(message)

        #if debug: print '\n (debug) -- get_redmine_info_from_alert - processing event_type: ', alert_alarm.event_type

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
        valid_actions = ['begin_notification_process', 'update_notification_ticket', 'reissue_notification_ticket', None]
        action = determine_action(id)          # actual alert escalation state review to determine action goes here
        '''
        if action not in valid_actions:
            message = 'Invalid action \'%s\' situation, failure to process alert (id:%d) escalation.' % (action, id)
            if log: print '\n (log) [alert_escalation_state] - message: ', message
            current_app.logger.exception('[alert_escalation_state] %s ' % message)
        '''
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
    #log = False
    debug = False
    #verbose = False
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
            #if debug: print '\n (debug) -- (determine_action) alerts is None, set ts_start!!! \n'
            alert.ts_start = alert.event_time
            try:
                db.session.add(alert)
                db.session.commit()
            except Exception as err:
                # todo review exception handling
                current_app.logger.exception('[determine_action] %s ' % err.message)
            #if debug: print '\n (debug) -- ***** set alert.ts_start: ', alert.to_json()
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
                        #if debug: print '\n (debug) -- ***** alert -- previously_escalated !'
                        break
                inx += 1

            # Determine start_alert (ts_start is not None)
            #if debug: print '\n (debug) -- (determine_action) have alerts...get start alert...'
            '''
            inx = 1
            if verbose:
                for item in alerts:
                    print '\n (verbose) alert -- %d: %s' % (inx, item.to_json())
                    inx += 1
            '''
            start_alert = None
            for item in alerts:
                if item.ts_start is not None:
                    start_alert = item
                    break
            #if debug: print '\n (debug) -- Found start_alert: ', start_alert.to_json()
            #if debug: print '\n (debug) -- type(start_alert): ', type(start_alert)

            # Now have initial alert which kicked off (start_alert)
            # Evaluate time delta (event_time) of this alert versus start_alert
            delta = (alert.event_time - start_alert.ts_start).total_seconds()
            #if debug: print '\n (debug) -- delta: ', delta
            #if debug: print '\n (debug) -- alert_alarm_definition.escalate_on: ', alert_alarm_definition.escalate_on

            # if delta is greater than escalate_on value (from definition), has alert been previously escalated?
            if delta <= alert_alarm_definition.escalate_on:
                #if debug: print '\n (debug) -- have not reached escalate on!  Keep going....no ticket yet....'
                pass
            elif delta > alert_alarm_definition.escalate_on:

                # if alert hasn't been previously escalated, begin escalation
                #if debug: print '\n (debug) -- delta > alert_alarm_definition.escalate_on'
                if not previously_escalated: #alert.escalated:
                    #if debug: print '\n (debug) -- not previously_escalated - begin_notification_process', alert.to_json()
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
                        #if debug: print '\n (debug) -- Escalate boundary has not been crossed, update existing ticket (ticket_id: %d) \n' % alert.ticket_id
                        action = 'update_notification_ticket'
                        return action

                    elif delta > alert_alarm_definition.escalate_boundary:
                        # Escalate boundary has been crossed, issue new ticket 'reissue_notification_ticket'
                        #if debug: print '\n (debug) -- Escalate boundary has been crossed, reissue ticket (current ticket_id: %d) \n' % alert.ticket_id
                        #if debug: print '\n (debug) -- delta > alert_alarm_definition.escalate_boundary'
                        action = 'reissue_notification_ticket'
                        start_alert.ts_start = None
                        try:
                            db.session.add(start_alert)
                            db.session.commit()
                        except Exception as err:
                            # todo review exception handling
                            if debug: print '\n (debug) -- (Escalate boundary has been crossed) (1) exception: ', err.message

                        #if debug: print '\n (debug) -- ***** start_alert.ts_start (should be None): ', start_alert.to_json()

                        alert.ts_start = alert.event_time
                        try:
                            db.session.add(alert)
                            db.session.commit()
                        except Exception as err:
                            # todo review exception handling
                            if debug: print '\n (debug) -- (Escalate boundary has been crossed) (2) exception: ', err.message

                        return action

        return action

    except Exception as err:
        message = err.message
        #if log: print'\n (debug) -- (determine_action) exception: ', err.message
        current_app.logger.exception('[determine_action] %s ' % message)
        return action

def update_notification_ticket(id):
    """ Update redmine ticket as a part of notification process (for alerts only)
    """
    debug = False
    #log = False
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
        name = None
        assigned_user = User.query.get(notification.user_id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
            tmp_id = get_user_redmine_id(project, name)
            if tmp_id is not None:
                redmine_id = tmp_id
        else:
            # todo issue - assigned_user is None
            message = "Invalid User ID, User record not found."
            #if log: print '\n message: ', message
            return bad_request(message)

        # Get alert ticket id
        ticket_id = alert.ticket_id

        #if debug: print '\n (debug) update_notification_ticket id: ', ticket_id
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
        else:
            # Use user_event_notification for determining assigned user's redmine id
            redmine_id = 1
            name = None
            assigned_user = User.query.get(notification.user_id)
            if assigned_user is not None:
                name = assigned_user.first_name + ' ' + assigned_user.last_name
                tmp_id = get_user_redmine_id(project, name)
                if tmp_id is not None:
                    redmine_id = tmp_id
            else:
                # todo issue - assigned_user is None
                message = "Invalid User ID, User record not found."
                #if log: print '\n message: ', message
                return bad_request(message)
            assigned_id = redmine_id

        # Update subject for recent receipt of alert (not past escalate boundary yet)
        description += update_info
        result = update_redmine_ticket_for_notification(ticket_id, project, subject, description, priority, assigned_id)
        if result is None:
            message = 'Failed to update redmine ticket (ticket_id: %d' % ticket_id
            raise Exception(message)

        if debug: print '\n \tupdate_notification_ticket - ticket_id: ', ticket_id
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
    debug = False   # development debug
    #log = False     # used in except blocks
    result = None
    try:
        if debug: print '\n \t(debug) entered reissue_notification_ticket, id: ', id

        # Get alert, definition and notification to update redmine ticket
        alert, definition, notification = get_redmine_info_from_alert(id)
        if alert is None or definition is None or notification is None:
            message = 'Failed to retrieve alert, definition or notification for update_notification_ticket. (id: %d)' % id
            current_app.logger.exception('[update_notification_ticket] %s ' % message)
            raise Exception(message)

        # Populate required fields to create a redmine ticket
        project = current_app.config['REDMINE_PROJECT_ID']

        if debug:
            print '\n \t(debug) -- Reissue redmine ticket (project: %s), get ticket_id...' % project
            print'\n \t(debug) -- Current ticket id: ', alert.ticket_id

        # Get current redmine ticket
        redmine_ticket = get_redmine_ticket_for_notification(alert.ticket_id)
        if debug: print '\n \t(debug) -- Current redmine ticket: ', redmine_ticket

        # Set assigned id to reflect update to user currently assigned to alert.ticket_id
        #assigned_id = redmine_ticket['assigned_to']
        if 'assigned_to' in redmine_ticket:
            assigned_id = redmine_ticket['assigned_to']
        else:
            # Use user_event_notification for determining assigned user's redmine id
            redmine_id = 1
            name = None
            assigned_user = User.query.get(notification.user_id)
            if assigned_user is not None:
                name = assigned_user.first_name + ' ' + assigned_user.last_name
                tmp_id = get_user_redmine_id(project, name)
                if tmp_id is not None:
                    redmine_id = tmp_id
            else:
                # todo issue - assigned_user is None
                message = "Invalid User ID, User record not found."
                #if log: print '\n message: ', message
                return bad_request(message)
            assigned_id = redmine_id

        # Update description to indicate previously issued ticket id for this alert.
        update_info = '\n* Associated with previously issued ticket: %d' % alert.ticket_id
        if debug: print '\n \t(debug) -- New reissued ticket update_info: ', update_info

        # Create new redmine ticket
        prefix = (alert.event_type).upper() + '*: '
        subject = prefix + alert.event_response
        description = alert.event_response + update_info
        priority = definition.severity
        if debug: print '\n \t(debug) New ticket subject: ', subject
        if debug: print '\n \t(debug) New ticket description: ', description

        ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, assigned_id)
        if ticket_id is None:
            message = 'Failed to reissue (create another new)_redmine_ticket.'
            current_app.logger.exception('[reissue_notification_ticket] %s ' % message)
            return result

        # update escalate fields if successful creating the redmine ticket
        escalated = True
        ts_escalated = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S") # should this be event_time?
        SystemEvent.update_alert_alarm_escalation(id=alert.id, ticket_id=ticket_id,
                                                  escalated=escalated, ts_escalated=ts_escalated)

        if debug: print '\n \t(debug) reissue_notification_ticket -- updated alert_alarm: ', alert.to_json()
        ticket_link_id = TicketSystemEventLink.insert_ticket_link(system_event_id=alert.id, ticket_id=ticket_id)
        if debug: print '\n \t(debug) -- (notifications) ticket_link_id: ', ticket_link_id
        '''
        # debug - view contents of alert_alarm escalation fields; verify changes have been persisted
        escalated_alert_alarm = SystemEvent.query.get(alert_alarm.id)
        print '\n (debug) *** escalated alert_alarm.to_json(): ', escalated_alert_alarm.to_json()
        '''

        result = ticket_id
        if debug: print '\n \treissue_notification_ticket - ticket_id: ', ticket_id

    except Exception as err:
        message = err.message
        current_app.logger.exception('[reissue_notification_ticket] %s ' % message)
    finally:
        return result



