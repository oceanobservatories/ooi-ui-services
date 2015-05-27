#!/usr/bin/env python
'''
Annotation endpoints

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import Annotation, User
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.errors import forbidden, conflict
from datetime import datetime
from dateutil.parser import parse as date_parse
import sqlalchemy as sa

import json

#List all annotations.
@api.route('/annotation')
def get_annotations():
    query = Annotation.query
    query = query.filter(sa.not_(Annotation.retired))
    if 'stream_name' in request.args:
        query = query.filter(Annotation.stream_name == request.args.get('stream_name'))
    if 'reference_designator' in request.args:
        query = query.filter(Annotation.reference_designator == request.args.get('reference_designator'))
    if 'start_time' in request.args:
        start_time = request.args['start_time']
        start_time = date_parse(start_time)
        query = query.filter(Annotation.end_time >= start_time)
    if 'end_time' in request.args:
        end_time = request.args['end_time']
        end_time = date_parse(end_time)
        query = query.filter(Annotation.start_time <= end_time)
    if 'stream_parameter_name' in request.args:
        query = query.filter(Annotation.stream_parameter_name == request.args.get('stream_parameter_name'))

    annotations = query.all()
    return jsonify( {'annotations' : [annotation.serialize() for annotation in annotations] })

#List an annotation by id
@api.route('/annotation/<int:id>')
def get_annotation(id):
    annotation = Annotation.query.filter_by(id=id).first_or_404()
    return jsonify(annotation.serialize())

#Create a new annotation
@api.route('/annotation', methods=['POST'])
@auth.login_required
@scope_required('annotate')
def create_annotation():
    try:
        data = json.loads(request.data)        
        # Let PSQL assign the timestamp
        if 'created_time' in data:
            del data['created_time']

        # Convert the ISO-8601 to Python datetime
        if 'start_time' in data:
            data['start_time'] = date_parse(data['start_time'])

        if 'end_time' in data:
            data['end_time'] = date_parse(data['end_time'])

        # Regardless of what was posted, the current user is assigned
        data['user_id'] = g.current_user.id

        annotation = Annotation.from_dict(data)
        db.session.add(annotation)
        db.session.commit()
        return jsonify(annotation.serialize()), 201
    except Exception as e:
        return jsonify(error=e.message), 400

#Update an existing annotation.
@api.route('/annotation/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required('annotate')
def edit_annotation(id):
    try:
        data = json.loads(request.data)
        annotation = Annotation.query.get_or_404(id)
        user_scopes = [s.scope_name for s in g.current_user.scopes]
        if g.current_user.id != annotation.user_id and 'user_admin' not in user_scopes and 'annotate' not in user_scopes:
            return forbidden('Must be author of annotation or have administrator privileges')
    # 	add more modifications as needed
        if 'start_time' in data:
            data['start_time'] = date_parse(data['start_time'])

        if 'end_time' in data:
            data['end_time'] = date_parse(data['end_time'])

        for field in ['start_time', 'end_time', 'stream_parameter_name', 'description', 'reference_designator']:
            val = data.get(field) or getattr(annotation, field)
            setattr(annotation, field, val)
        db.session.add(annotation)
        db.session.commit()
        return jsonify(annotation.serialize())
    except:
        return conflict('Insufficient data, or bad data format.')

#Delete an existing annotation
@api.route('/annotation/<int:id>', methods=['DELETE'])
@auth.login_required
@scope_required('annotate')
def delete_annotation(id):
    annotation = Annotation.query.get_or_404(id)
    user_scopes = [s.scope_name for s in g.current_user.scopes]
    if g.current_user.id != annotation.user_id and 'user_admin' not in user_scopes and 'annotate' not in user_scopes:
        return forbidden('Must be author of annotation or have administrator privileges')
    annotation.retired = True
    db.session.add(annotation)
    db.session.commit()
    return jsonify({}), 204
