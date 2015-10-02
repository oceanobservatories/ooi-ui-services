#!/usr/bin/env python
"""
System event notifications endpoints (for Alerts & Alarms escalation process)

"""
__author__ = 'Edna Donoughe'

from flask import (current_app)
from ooiservices.app.main.notifications_redmine import (handle_redmine_notifications, get_info_from_alert)
from ooiservices.app.main.errors import (conflict)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Notification processing
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def handle_notifications(id):
    """
    Handle notification types here. Available notification types are as follows:
        "use_redmine", ["use_email",  "use_phone", "use_log", "use_sms"]

    Note: "use_redmine" is the only notification type available at this time.
    """
    try:
        alert_alarm, alert_alarm_definition, notification = get_info_from_alert(id)
        if alert_alarm is None or alert_alarm_definition is None or notification is None:
            message = 'Failed to retrieve alert, definition or notification for handle_notifications. (id: %d)' % id
            current_app.logger.info('[handle_notifications] %s ' % message)
            raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Process based on notification type(s) selected
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Notification type: red mine
        handle_redmine_notifications(id)

        # Notification type: Proposed (but unavailable) notification types.
        if notification.use_email or notification.use_phone or notification.use_log or notification.use_sms:
            message = 'Unavailable alert alarm notification type (one of: use_email, use_phone, use_log or use_sms)'
            current_app.logger.info(message)

        # Notification type: Unknown
        else:
            message = 'No notification type selected; it is recommended MIOs be notified of alert or alarm activity.'
            current_app.logger.info(message)
        return

    except Exception as err:
        message = 'handle_notifications exception. %s' % err.message
        current_app.logger.info(message)
        return conflict(message)
