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

import json

#List all annotations.
@api.route('/annotation')
def get_annotations():
    if 'stream_name' in request.args:
        annotations = Annotation.query.filter_by(stream_name=request.args.get('stream_name'))
    else:
        annotations = Annotation.query.all()
    return jsonify( {'annotations' : [annotation.to_json() for annotation in annotations] })

#List an annotation by id
@api.route('/annotation/<string:id>')
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
        annotation = Annotation.from_json(data)
        annotation.created_time = datetime.now()
        annotation.modified_time = datetime.now()
        annotation.user_name = g.current_user.user_name
        db.session.add(annotation)
        db.session.commit()
        return jsonify(annotation.to_json()), 201
    except:
        return conflict('Insufficient data, or bad data format.')

#Update an existing annotation.
@api.route('/annotation/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required('annotate')
def edit_annotation(id):
    annotation = Annotation.query.get_or_404(id)
    if g.current_user != annotation.user_name and \
            not g.current_user.can('annotate'):
        return forbidden('Scope required.')
# 	add more modifications as needed
    annotation.comment = request.json.get('comment', annotation.comment)
    annotation.title = request.json.get('title', annotation.title)
    annotation.modified_date = datetime.now()
    db.session.add(annotation)
    db.session.commit()
    return jsonify(annotation.to_json())

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
