#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'Jim Case'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import OperatorEvent, OperatorEventType, Watch, Organization, LogEntry
from ooiservices.app.models import LogEntryComment,User
from datetime import datetime
from wtforms import ValidationError
from sqlalchemy_searchable import search
import json
import sqlalchemy as sa

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

@api.route('/log_entry', methods=['GET'])
def get_log_entries():
    # Limits and offsets
    if 'limit' in request.args:
        limit = int(request.args['limit'])
        if limit > 100:
            limit = 100
    else:
        limit = 10

    if 'offset' in request.args:
        offset = int(request.args['offset'])
    else:
        offset = 0

    if 'organization_id' in request.args:
        query = LogEntry.query\
            .filter(LogEntry.organization_id == request.args['organization_id'])\
                .filter(sa.not_(LogEntry.retired))

    else:
        query = LogEntry.query.filter(sa.not_(LogEntry.retired))

    if 'search' in request.args:
        if request.args["search"]:
            slist = []
            clist=[]
            for s in request.args["search"].split():
                slist.append(sa.or_(sa.func.upper(LogEntry.entry_title).like("%" + s.upper() + "%")))
                slist.append(sa.or_(sa.func.upper(LogEntry.entry_description).like("%" + s.upper() + "%")))
                clist.append(sa.or_(sa.func.upper(LogEntryComment.comment).like("%" + s.upper() + "%")))

            query=LogEntry.query\
                .filter(sa.or_(*slist) | LogEntry.id.in_(LogEntryComment.query.with_entities("log_entry_id")\
                                                         .filter(sa.or_(*clist))\
                                                         .filter(LogEntryComment.retired == False)))\
                    .filter (LogEntry.user_id.in_(User.query.with_entities("id")\
                        .filter(sa.func.upper(User.first_name).in_(request.args["search"].upper().split()) | sa.func.upper(User.last_name).in_(request.args["search"].upper().split()))))\
                            .filter(LogEntry.organization_id == request.args['organization_id'])\
                                .filter(sa.not_(LogEntry.retired))

            if query.count()==0:
                query=LogEntry.query\
                    .filter(sa.or_(*slist) | LogEntry.id.in_(LogEntryComment.query.with_entities("log_entry_id")\
                                                             .filter(sa.or_(*clist))\
                                                             .filter(LogEntryComment.retired == False)))\
                        .filter(LogEntry.organization_id == request.args['organization_id'])\
                            .filter(LogEntry.retired == False)

    if 'daterange' in request.args and request.args["daterange"]:
        rdates=request.args["daterange"].split('_')
        query.whereclause.append(sa.between(LogEntry.entry_time,rdates[0] + " 00:00:00.000",rdates[1] + " 11:59:59.000"))

    log_entries = query.order_by(sa.desc(LogEntry.entry_time)).limit(limit).offset(offset).all()

    if not log_entries:
        return jsonify({}), 204

    log_entries = [l.to_json() for l in log_entries]
    return jsonify(log_entries=log_entries)

@api.route('/log_entry/<int:id>', methods=['GET'])
def get_log_entry(id):
    log_entry = LogEntry.query.get(id)
    if not log_entry or log_entry.retired:
        return jsonify({}), 204
    return jsonify(log_entry.to_json())

@api.route('/log_entry', methods=['POST'])
@auth.login_required
def post_log_entry():
    data = json.loads(request.data) or {}
    if not data:
        return jsonify(error='Empty request'), 400
    data['user_id'] = g.current_user.id
    data['organization_id'] = data.get('organization_id') or g.current_user.organization_id
    if 'entry_time' in data:
        del data['entry_time']
    try:
        entry = LogEntry.from_dict(data)
    except Exception as e:
        return jsonify(error=e.message), 400
    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_json())

@api.route('/log_entry/<int:id>', methods=['PUT'])
@auth.login_required
def put_log_entry(id):
    data = json.loads(request.data) or {}
    log_entry = LogEntry.query.get(id)
    if not log_entry:
        return jsonify(error="No matching record"), 404
    user_id = log_entry.user_id
    current_scopes = [s.scope_name for s in g.current_user.scopes]
    if g.current_user.id != user_id and 'user_admin' not in current_scopes:
        return jsonify(error='Unauthorized: This user lacks sufficient privileges to change this entry'), 401
    log_entry.log_entry_type = data.get('log_entry_type')
    if 'entry_title' not in data:
        return jsonify(error='entry_title required to create LogEntry'), 400
    log_entry.entry_title = data.get('entry_title')
    log_entry.entry_description = data.get('entry_description')
    db.session.add(log_entry)
    db.session.commit()
    return jsonify(log_entry.to_json())

@api.route('/log_entry/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_log_entry(id):
    log_entry = LogEntry.query.get(id)
    if not log_entry:
        return jsonify(error='No matching record'), 404
    user_id = log_entry.user_id
    current_scopes = [s.scope_name for s in g.current_user.scopes]
    if g.current_user.id != user_id and 'user_admin' not in current_scopes:
        return jsonify(error='Unauthorized: This user lacks sufficient privileges to change this entry'), 401
    log_entry.retired = True
    db.session.add(log_entry)
    db.session.commit()
    return jsonify(), 204

@api.route('/log_entry_comment', methods=['GET'])
def get_log_entry_comments():
    if 'log_entry_id' in request.args:
        query = LogEntryComment.query.filter(LogEntryComment.log_entry_id == request.args['log_entry_id'], sa.not_(LogEntryComment.retired))
    else:
        query = LogEntryComment.query.filter(sa.not_(LogEntryComment.retired))
    comments = query.order_by(sa.desc(LogEntryComment.comment_time)).all()
    comments = [c.to_json() for c in comments]
    return jsonify(log_entry_comments=comments)

@api.route('/log_entry_comment', methods=['POST'])
@auth.login_required
def post_log_entry_comment():
    data = json.loads(request.data) or {}
    if 'log_entry_id' not in data:
        return jsonify(error='Parent log_entry_id required'), 400
    data['user_id'] = g.current_user.id
    if 'comment_time' in data:
        del data['comment_time']
    comment = LogEntryComment.from_dict(data)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json())

@api.route('/log_entry_comment/<int:id>', methods=['GET'])
def get_log_entry_comment(id):
    comment = LogEntryComment.query.get(id)
    if not comment or comment.retired:
        return jsonify(), 204
    return jsonify(comment.to_json())

@api.route('/log_entry_comment/<int:id>', methods=['PUT'])
@auth.login_required
def put_log_entry_comment(id):
    data = json.loads(request.data) or {}
    # Get the record, if it's not found or retired return a 404
    comment = LogEntryComment.query.get(id)
    if not comment or comment.retired:
        return jsonify(error='No matching records'), 404

    # Make sure it's the original author or an admin
    user_id = comment.user_id
    current_scopes = [s.scope_name for s in g.current_user.scopes]
    if g.current_user.id != user_id and 'user_admin' not in current_scopes:
        return jsonify(error='Unauthorized: This user lacks sufficient privileges to change this entry'), 401
    
    comment.comment = data.get('comment')
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json())

@api.route('/log_entry_comment/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_log_entry_comment(id):
    # Get the record, if it's not found or retired return a 404
    comment = LogEntryComment.query.get(id)
    if not comment or comment.retired:
        return jsonify(error='No matching records'), 404

    # Make sure it's the original author or an admin
    user_id = comment.user_id
    current_scopes = [s.scope_name for s in g.current_user.scopes]
    if g.current_user.id != user_id and 'user_admin' not in current_scopes:
        return jsonify(error='Unauthorized: This user lacks sufficient privileges to change this entry'), 401

    comment.retired = True
    db.session.add(comment)
    db.session.commit()

    return jsonify(), 204
