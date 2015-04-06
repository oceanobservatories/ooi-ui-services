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
from ooiservices.app.main.errors import forbidden, conflict, bad_request
from datetime import datetime

import json

#List all alerts and alarms
@api.route('/alert_alarm')
def get_alerts_alarms():
    result = []
    if 'type' in request.args:
        alerts_alarms = SystemEvent.query.filter_by(type=request.args.get('type'))
    else:
        alerts_alarms = SystemEvent.query.all()
    if alerts_alarms:
        result = [alert_alarm.to_json() for alert_alarm in alerts_alarms]
    return jsonify( {'alert_alarm' : result })

#List an alerts and alarms by id
@api.route('/alert_alarm/<string:id>')
def get_alert_alarm(id):
    alert_alarm = SystemEvent.query.filter_by(id=id).first_or_404()
    return jsonify(alert_alarm.to_json())

#Create a new alert/alarm
@api.route('/alert_alarm', methods=['POST'])
# @auth.login_required
# @scope_required('annotate')
def create_alert_alarm():
    try:
        data = json.loads(request.data)
        alert_alarm = SystemEvent()
        alert_alarm.uframe_event_id = data['uframe_event_id']
        alert_alarm.system_event_definition_id = data['system_event_definition_id']
        alert_alarm.event_time = datetime.now()
        alert_alarm.event_type = data['event_type']
        alert_alarm.event_response = data['event_response']
        db.session.add(alert_alarm)
        db.session.commit()
        db.session.flush()

        return jsonify(alert_alarm.to_json()), 201
    except Exception as err:
        return conflict('Insufficient data, or bad data format.')


# Alerts & Alarms Definitions

#List all alert and alarm definitions
@api.route('/alert_alarm_definition')
def get_alerts_alarms_def():
    if 'array_name' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(array_name=request.args.get('array_name'))
    elif 'platform_name' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(platform_name=request.args.get('platform_name'))
    elif 'instrument_name' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(instrument_name=request.args.get('instrument_name'))
    elif 'reference_designator' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(reference_designator=request.args.get('reference_designator'))
    else:
        alerts_alarms_def = SystemEventDefinition.query.all()
    return jsonify( {'alert_alarm_definition' : [alert_alarm_def.to_json() for alert_alarm_def in alerts_alarms_def] })

#List an alerts and alarms definition by id
@api.route('/alert_alarm_definition/<string:id>')
def get_alert_alarm_def(id):
    alert_alarm_def = SystemEventDefinition.query.filter_by(id=id).first_or_404()
    return jsonify(alert_alarm_def.to_json())

#Create a new alert/alarm definition
@api.route('/alert_alarm_definition', methods=['POST'])
# @auth.login_required
# @scope_required('annotate')
def create_alert_alarm_def():
    try:
        data = json.loads(request.data)
        alert_alarm_def = SystemEventDefinition()
        # uframe_definition_id, reference_designator, array_name, platform_name,
        # instrument_name, instrument_parameter, operator, values,
        # created_time, priority, active, description
        alert_alarm_def.uframe_definition_id = data['uframe_definition_id'] # Returned from POST to uFrame
        alert_alarm_def.reference_designator = data['reference_designator'] # Instrument reference designator
        alert_alarm_def.array_name = data['array_name']  # Array reference designator
        alert_alarm_def.platform_name = data['platform_name']  # Platform reference designator
        alert_alarm_def.instrument_name = data['instrument_name']  # Instrument reference designator
        alert_alarm_def.instrument_parameter = data['instrument_parameter']
        alert_alarm_def.operator = data['operator']
        alert_alarm_def.values = data['values']
        alert_alarm_def.created_time = datetime.now()
        alert_alarm_def.priority = data['priority']
        alert_alarm_def.active = data['active']
        alert_alarm_def.description = data['description']
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
            db.session.flush()
        except Exception as err:
            return bad_request(err.message)

        if current_app.config['USE_MOCK_DATA']:
            insert_alert_alarm_demo(alert_alarm_def.id,
                                    alert_alarm_def.priority,
                                    alert_alarm_def.instrument_name,
                                    alert_alarm_def.instrument_parameter,
                                    alert_alarm_def.operator,
                                    alert_alarm_def.values)
        return jsonify(alert_alarm_def.to_json()), 201
    except:
        return conflict('Insufficient data, or bad data format.')

#Update an alert/alarm definition
@api.route('/alert_alarm_definition/<int:id>', methods=['PUT'])
# @auth.login_required
# @scope_required('annotate')
def update_alert_alarm_def(id):
    try:
        data = json.loads(request.data)
        # alert_alarm_def = SystemEventDefinition()
        alert_alarm_def = SystemEventDefinition.query.filter_by(uframe_definition_id=id).first()
        if alert_alarm_def is None:
            return jsonify(error="Invalid ID, record not found"), 404
        # uframe_definition_id, reference_designator, array_name, platform_name,
        # instrument_name, instrument_parameter, operator, values,
        # created_time, priority, active, description
        # alert_alarm_def.uframe_definition_id = data['uframe_definition_id'] # Returned from POST to uFrame
        alert_alarm_def.reference_designator = data['reference_designator'] # Instrument reference designator
        alert_alarm_def.array_name = data['array_name']  # Array reference designator
        alert_alarm_def.platform_name = data['platform_name']  # Platform reference designator
        alert_alarm_def.instrument_name = data['instrument_name']  # Instrument reference designator
        alert_alarm_def.instrument_parameter = data['instrument_parameter']
        alert_alarm_def.operator = data['operator']
        alert_alarm_def.values = data['values']
        # alert_alarm_def.created_time = datetime.now()
        alert_alarm_def.priority = data['priority']
        alert_alarm_def.active = data['active']
        alert_alarm_def.description = data['description']
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
            db.session.flush()
        except Exception as err:
            return bad_request(err.message)

        return jsonify(alert_alarm_def.to_json()), 201
    except:
        return conflict('Insufficient data, or bad data format.')

def insert_alert_alarm_demo(system_event_definition_id, event_type, instrument_name, instrument_parameter, operator, values):
    #uframe_event_id, event_response
    records = SystemEvent.query.all()
    if not records:
        last_record_id = 1
    else:
        last_record_id = len(records) + 1
    uframe_event_id_list = [i+last_record_id for i in xrange(5)]
    event_response_message = "Instrument: {0} boundary condition exceeded where parameter {1} {2} {3}".format(instrument_name, instrument_parameter, operator, values)
    for uframe_event_id in uframe_event_id_list:
        alert_alarm = SystemEvent()
        alert_alarm.uframe_event_id = uframe_event_id
        alert_alarm.system_event_definition_id = system_event_definition_id
        alert_alarm.event_time = datetime.now()
        alert_alarm.event_type = event_type
        alert_alarm.event_response = event_response_message
        try:
            db.session.add(alert_alarm)
            db.session.commit()
            db.session.flush()
        except Exception as err:
            raise Exception(err.message)
