#!/usr/bin/env python
'''
Alerts & Alarms Notification Endpoints

'''
__author__ = 'Edna Donoughe'

from flask import jsonify, request
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.models import UserEventNotification, User
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import conflict, bad_request

import json

#List all notifications (by user_id if provided)
@api.route('/notifications')
def get_notifications():
    result = []
    if 'user_id' in request.args:
        notifications = UserEventNotification.query.filter_by(event_type=request.args.get('user_id'))
    else:
        notifications = UserEventNotification.query.all()
    if notifications:
        result = [notify.to_json() for notify in notifications]
    return jsonify( {'notifications' : result })

#List an notification by id
@api.route('/notification/<string:id>')
def get_notification(id):
    notification = UserEventNotification.query.filter_by(id=id).first_or_404()
    return jsonify(notification.to_json())

#Create a new notification
@api.route('/notification', methods=['POST'])
# @auth.login_required
# @scope_required('annotate')
def create_notification():
    """
    Create notification associated with SystemEventDefinition.

    Usage: Whenever a SystemEvent occurs, for the system_event_definition_id, this notification
    indicates who and how to contact them with the SystemEvent information.
    """
    try:
        data = json.loads(request.data)
        # todo Validate request.data fields

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
        print '\n exception: ', err.message
        return conflict('Insufficient data, or bad data format.')

def create_has_required_fields(data):
    """
    Verify UserEventNotification create request.data has required fields. Error otherwise.
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
    except:
        raise
