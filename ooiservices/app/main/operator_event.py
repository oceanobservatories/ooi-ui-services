#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'Jim Case'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import OperatorEvent, OperatorEventType
import json
from wtforms import ValidationError

@api.route('/operator_event/<string:id>')
@auth.login_required
def get_operator_events_by_user(id):
    operator_events = OperatorEvent.query.filter_by(user_id = id)
    return jsonify( {'operator_events' : [operator_event.to_json() for operator_event in operator_events] })

@api.route('/operator_event', methods=['POST'])
@auth.login_required
def create_operator_event():
    data = json.loads(request.data)
    try:
        new_operator_event = OperatorEvent.from_json(data)
        db.session.add(new_operator_event)
        db.session.commit()
    except ValidationError as e:
        return jsonify(error=e.message), 409
    return jsonify(new_operator_event.to_json()), 201

@api.route('/operator_event_type')
@auth.login_required
def get_operator_event_types():
    operator_event_types = OperatorEventType.query.all()
    return jsonify( {'operator_event_types' : [operator_event_type.to_json() for operator_event_type in operator_event_types] })
