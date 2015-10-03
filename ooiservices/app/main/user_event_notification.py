#!/usr/bin/env python
'''
User event notifications endpoints (for Alerts & Alarms Notification process)

'''
__author__ = 'Edna Donoughe'

from flask import (jsonify, request)
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import (UserEventNotification, User, SystemEventDefinition)
from ooiservices.app.main.errors import conflict, bad_request
import json

@api.route('/user_event_notifications')
def get_user_event_notifications():
    """ List all user_event_notifications (by user_id if provided)
    """
    result = []
    try:
        if 'user_id' in request.args:
            user_id = request.args.get('user_id')
            user = User.query.get(user_id)
            if user is None:
                message = "Invalid User ID, User record not found."
                return bad_request(message)
            notifications = UserEventNotification.query.filter_by(user_id=user_id).all()
        else:
            notifications = UserEventNotification.query.all()
        if notifications:
            result = [notify.to_json() for notify in notifications]
        return jsonify( {'notifications' : result })
    except:
        return conflict('Insufficient data, or bad data format.')

#List a user_event_notification by id
@api.route('/user_event_notification/<int:id>')
def get_user_event_notification(id):
    result = {}
    notification = UserEventNotification.query.filter_by(id=id).first()
    if notification is not None:
        result = notification.to_json()
    return jsonify(result)

#Create a new user_event_notification
@api.route('/user_event_notification', methods=['POST'])
@auth.login_required
@scope_required(u'user_admin')
def create_user_event_notification():
    """
    Create user_event_notification associated with SystemEventDefinition.

    Usage: Whenever a SystemEvent occurs, for the system_event_definition_id, this notification
    indicates who and how to contact them with the SystemEvent information.
    """
    try:
        data = json.loads(request.data)
        create_has_required_fields(data)

        system_event_definition_id = data['system_event_definition_id']
        definition = SystemEventDefinition.query.get(system_event_definition_id)
        if definition is None:
            message = "Invalid SystemEventDefinition ID, SystemEventDefinition record not found."
            return bad_request(message)

        # Validate user to be notified exists
        user_id = data['user_id']
        user = User.query.filter_by(id=user_id).first()
        if not user:
            message = "Invalid User ID, User record not found."
            return bad_request(message)

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
            db.session.rollback()
            return bad_request('IntegrityError creating notification')
        return jsonify(notification.to_json()), 201
    except Exception as err:
        return conflict('Insufficient data, or bad data format.')

@api.route('/user_event_notification/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required(u'user_admin')
def update_user_event_notification(id):
    """ Update user_event_notification associated with SystemEventDefinition.
    """
    try:
        data = json.loads(request.data)

        # Get existing notification
        notification_id = data['id']
        if notification_id != id:
            message = "Inconsistent ID, user_event_notification id provided in data does not match id provided."
            return bad_request(message)

        notification = UserEventNotification.query.filter_by(id=notification_id).first()
        if notification is None:
            message = "Invalid ID, user_event_notification record not found."
            return bad_request(message)

        # Validate user to be notified exists
        user = User.query.filter_by(id=notification.user_id).first()

        # Validate user_id matches id value
        user_id = data['user_id']
        if user_id != notification.user_id:
            message = "Inconsistent User ID, user_id provided in data does not match id."
            return bad_request(message)

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
        except:
            db.session.rollback()
            return bad_request('IntegrityError creating user_event_notification.')

        return jsonify(notification.to_json()), 201
    except:
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
                message = 'Missing required field (%r) in request.data' % field
                raise Exception(message)
        if not isinstance(data['user_id'], int):
            message = 'Invalid user_id; parameter type invalid.'
            raise Exception(message)
        return
    except:
        raise




