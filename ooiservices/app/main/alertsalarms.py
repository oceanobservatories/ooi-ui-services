#!/usr/bin/env python
'''
Alerts & Alarms Endpoints

'''
__author__ = 'James Case'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import SystemEventDefinition, SystemEvent, User
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.errors import forbidden, conflict
from datetime import datetime

import json

#List all alerts and alarms
@api.route('/alertsalarms')
def get_alerts_alarms():
    if 'array_name' in request.args:
        alerts_alarms = SystemEvent.query.filter_by(array_name=request.args.get('array_name'))
    elif 'platform_name' in request.args:
        alerts_alarms = SystemEvent.query.filter_by(platform_name=request.args.get('platform_name'))
    elif 'instrument_name' in request.args:
        alerts_alarms = SystemEvent.query.filter_by(instrument_name=request.args.get('instrument_name'))
    else:
        alerts_alarms = SystemEvent.query.all()
    return jsonify( {'alerts_alarms' : [alert_alarm.to_json() for alert_alarm in alerts_alarms] })

#List an alerts and alarms by id
@api.route('/alertsalarms/<string:id>')
def get_alert_alarm(id):
    alert_alarm = SystemEvent.query.filter_by(id=id).first_or_404()
    return jsonify(alert_alarm.to_json())

#Create a new alert/alarm
@api.route('/alertsalarms', methods=['POST'])
# @auth.login_required
# @scope_required('annotate')
def create_alert_alarm():
    try:
        data = json.loads(request.data)
        alert_alarm = SystemEvent() #uframe_event_id, system_event_definition_id, event_time, event_type, event_response
        alert_alarm.uframe_event_id = data['uframe_event_id']
        alert_alarm.system_event_definition_id = data['system_event_definition_id']
        alert_alarm.event_time = datetime.now()
        alert_alarm.event_type = data['event_type']
        alert_alarm.event_response = data['event_response']
        db.session.add(alert_alarm)
        db.session.commit()
        return jsonify(alert_alarm.to_json()), 201
    except:
        return conflict('Insufficient data, or bad data format.')
