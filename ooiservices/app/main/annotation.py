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
from ooiservices.app.main.errors import forbidden

from datetime import datetime

@api.route('/annotations')
def get_annotations():
    annotations = Annotation.query.all()
    return jsonify( {'annotations' : [annotation.to_json() for annotation in annotations] })

@api.route('/annotations/', methods=['POST'])
@auth.login_required
@scope_required('annotate')
def create_annotation():
    annotation = Annotation.new_from_json(request.json)
    db.session.add(annotation)
    db.session.commit()
    return jsonify(annotation.to_json()), 201

@api.route('/annotations/<string:id>')
def get_annotation(id):
    annotation = Annotation.query.filter_by(user_name=id).first_or_404()
    return jsonify(annotation.to_json())

@api.route('/annotations/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required('annotate')
def edit_annotation(id):
    annotation = Annotation.query.get_or_404(id)
    if g.current_user != annotation.user_name and \
            not g.current_user.can('annotate'):
        return forbidden('Scope required.')
# 	add more modifications as needed
    annotation.comment = request.json.get('comment', annotation.comment)
    annotation.modified_date = datetime.now()
    db.session.add(annotation)
    return jsonify(annotation.to_json())