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

import json

#List all annotations.
@api.route('/annotation')
def get_annotations():
    annotations = Annotation.query.all()
    return jsonify( {'annotations' : [annotation.serialize() for annotation in annotations] })

#List an annotation by id
@api.route('/annotation/<int:id>')
def get_annotation(id):
    annotation = Annotation.query.filter_by(user_name=id).first_or_404()
    return jsonify(annotation.to_json())

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
        if g.current_user != annotation.user_name and \
                not g.current_user.can('annotate'):
            return forbidden('Scope required.')
    # 	add more modifications as needed
        annotation.comment = data.get('comment', annotation.comment)
        annotation.title = data.get('title', annotation.title)
        annotation.modified_date = datetime.now()
        db.session.add(annotation)
        db.session.commit()
        return jsonify(annotation.to_json())
    except:
        return conflict('Insufficient data, or bad data format.')

#Delete an existing annotation
@api.route('/annotation/<int:id>', methods=['DELETE'])
@auth.login_required
@scope_required('annotate')
def delete_annotation(id):
    annotation = Annotation.query.get_or_404(id)
    if g.current_user != annotation.user_name and \
            not g.current_user.can('annotate'):
        return forbidden('Scope required.')
    db.session.delete(annotation)
    db.session.commit()
    return jsonify({'message': 'Annotation deleted!', 'id': id})
