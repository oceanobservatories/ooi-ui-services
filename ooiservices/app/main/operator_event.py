#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'Jim Case'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import OperatorEvent, OperatorEventType, Watch, Organization
from datetime import datetime
import json
from wtforms import ValidationError

@api.route('/watch', methods=['GET'])
def get_watches():
    if 'organization_id' in request.args:
        organization_id = request.args['organization_id']
        organization = Organization.query.filter(Organization.id == organization_id).first()
        users = organization.users
        watches = []
        for u in users:
            watches.extend([w.to_json() for w in u.watches])
    else:
        watches = [w.to_json() for w in Watch.query.all()]
    if not watches:
        return '{}', 204
    return jsonify(watches=watches)

def has_open_watches():
    user = g.current_user
    watches = Watch.query.filter(Watch.user_id == user.id, Watch.end_time == None).all()
    if watches:
        return True
    return False

def get_open_watch():
    user = g.current_user
    watch = Watch.query.filter(Watch.user_id == user.id, Watch.end_time == None).first()
    return watch


@api.route('/watch', methods=['POST'])
@auth.login_required
def post_watch():
    # We actually ignore all input from the user
    if has_open_watches():
        return '{"error":"Can not open a new watch until existing watch is closed"}', 405
    user = g.current_user
    watch = Watch()
    watch.start_time = datetime.utcnow()
    watch.user_id = user.id
    db.session.add(watch)
    db.session.commit()
    response = watch.to_json()
    return jsonify(**response), 201

@api.route('/watch/<int:watch_id>', methods=['GET'])
def get_watch(watch_id):
    watch = Watch.query.filter(Watch.id==watch_id).first()
    if not watch:
        return '{"error":"not found"}', 204
    response = watch.to_json()
    return jsonify(**response)

@api.route('/watch/<int:watch_id>', methods=['PUT'])
@auth.login_required
def put_watch(watch_id):
    watch = Watch.query.filter(Watch.id==watch_id).first()
    if not watch:
        return '{"error":"not found"}', 404
    if watch.user_id != g.current_user.id:
        return '{"error":"Unauthorized"}', 401
    data = request.json or {}
    watch.start_time = data.get('start_time', watch.start_time)
    if not (watch.end_time or data.get('end_time')):
        watch.end_time = datetime.utcnow()
    watch.end_time = data.get('end_time', watch.end_time)
    db.session.add(watch)
    db.session.commit()
    response = watch.to_json()
    return jsonify(**response), 201

@api.route('/watch/user', methods=['GET'])
@auth.login_required
def get_watch_user():
    user = g.current_user
    watches = [w.to_json() for w in Watch.query.filter(Watch.user_id == user.id)]
    if not watches:
        return '{}', 204
    return jsonify(watches=watches)

@api.route('/watch/open', methods=['GET'])
@auth.login_required
def get_watch_opened():
    watch = get_open_watch()
    if not watch:
        return '{}', 204 # No currently opened watch
    response = watch.to_json()
    return jsonify(**response)

@api.route('/operator_event', methods=['GET'])
def get_operator_events():
    if 'watch_id' in request.args:
        watch_id = request.args['watch_id']
        operator_events = OperatorEvent.query.filter(OperatorEvent.watch_id == watch_id).all()
    else:
        operator_events = OperatorEvent.query.all()
    if not operator_events:
        return '{}', 204
    response = []
    for event in operator_events:
        record = event.serialize()
        del record['operator_event_type_id']
        record['event_type'] = event.operator_event_type.serialize()
        response.append(record)
    return jsonify(operator_events=response)


@api.route('/operator_event/<int:operator_event_id>', methods=['GET'])
def get_operator_event(operator_event_id):
    operator_event = OperatorEvent.query.filter(OperatorEvent.id == operator_event_id).first()
    if not operator_event:
        return '{}', 204
    response = operator_event.serialize()
    response['event_type'] = operator_event.operator_event_type.serialize()
    del response['operator_event_type_id']
    return jsonify(**response)

@api.route('/operator_event/<int:operator_event_id>', methods=['PUT'])
@auth.login_required
def put_operator_event(operator_event_id):
    operator_event = OperatorEvent.query.filter(OperatorEvent.id == operator_event_id).first()
    if not operator_event:
        return '{}', 401
    if operator_event.watch.user.id != g.current_user.id:
        return '{"error":"Unauthorized to modify this resource"}', 405
    data = request.json or {}
    operator_event.operator_event_type_id = data.get("operator_event_type_id", operator_event.operator_event_type_id)
    operator_event.event_time = data.get("event_time", operator_event.event_time)
    operator_event.event_title = data.get("event_title", operator_event.event_title)
    operator_event.event_comment = data.get("event_comment", operator_event.event_comment)
    db.session.add(operator_event)
    db.session.commit()
    operator_event = operator_event.serialize()
    return jsonify(**operator_event), 201

@api.route('/operator_event', methods=['POST'])
@auth.login_required
def post_operator_event():
    data = json.loads(request.data) or {}
    if not data:
        return '{"error":"Empty request"}', 400
    watch = get_open_watch()
    if not watch:
        return '{"error":"No open watches"}', 400
    data['watch_id'] = watch.id
    data['event_time'] = datetime.utcnow()
    operator_event = OperatorEvent()
    event_type = data.get('event_type', {})
    if 'id' in event_type:
        operator_event.operator_event_type_id = event_type['id']
    elif 'type_name' in event_type:
        operator_event_type = OperatorEventType.query.filter(OperatorEventType.type_name == event_type['type_name']).first()
        operator_event.operator_event_type_id = operator_event_type.id
    else:
        operator_event_type = OperatorEventType.query.filter(OperatorEventType.type_name == 'INFO').first()
        operator_event.operator_event_type_id = operator_event_type.id

    operator_event.event_title = data.get('event_title')
    operator_event.event_comment = data.get('event_comment')
    operator_event.watch_id = data.get('watch_id')
    operator_event.event_time = datetime.utcnow()

    db.session.add(operator_event)
    db.session.commit()
    response = operator_event.serialize()
    response['event_type'] = operator_event.operator_event_type.serialize()
    del response['operator_event_type_id']

    return jsonify(**response), 201
    

@api.route('/operator_event_type')
def get_operator_event_types():
    operator_event_types = [o.serialize() for o in OperatorEventType.query.all()]
    return jsonify(operator_event_types=operator_event_types)
