#!/usr/bin/env python
'''
Annotation endpoints

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import Annotation
from ooiservices.app.decorators import scope_required

@api.route('/annotations')
def get_annotations():
    annotations = Annotation.query.all()
    return jsonify( {'annotations' : [annotations.to_json() for annotation in annotations] })

@api.route('/annotations/', methods=['POST'])
@auth.login_required
@scope_required('annotate')
def set_annotation():
    annotation = Annotation.from_json(request.json)
    db.session.add(annotation)
    db.session.commit()
    return jsonify(annotation.to_json())

@api.route('/annotations/<string:id>')
def get_annotation(id):
    annotation = Annotation.query.filter_by(user_name=id).first_or_404()
    return jsonify(annotation.to_json())