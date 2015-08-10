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
from ooiservices.app.uframe.controller import split_stream_name
import json
import requests

#List all annotations. build 6
@api.route('/annotation/<string:instrument>/<string:stream>')
def get_annotations(instrument,stream):
    try:
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
            #fixed parameter request            
            query = '?beginDT=%s&endDT=%s&limit=%s&include_annotations=true&parameters=PD7' % (st_date, ed_date, 3)

            UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
            url = "/".join([UFRAME_DATA,mooring, platform, instrument, stream_type, stream + query])

            r = requests.get(url)
            data = r.json()        

            print "ANNOTATION ***:",url

            return jsonify( {'annotations' : data['annotations'] })

        else:
            return jsonify( {'error' : "no dates specified" })        
    except Exception, e:
        return jsonify( {'error' : "could not obtain annotation(s)"+str(e) })


#DEPRECATED
#List an annotation by id
#@api.route('/annotation/<int:id>')
def get_annotation(id):
    annotation = Annotation.query.filter_by(id=id).first_or_404()
    return jsonify(annotation.serialize())

#DEPRECATED
#Create a new annotation
#@api.route('/annotation', methods=['POST'])
#@auth.login_required
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


#DEPRECATED
#Update an existing annotation.
#@api.route('/annotation/<int:id>', methods=['PUT'])
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

#DEPRECATED
#Delete an existing annotation
#@api.route('/annotation/<int:id>', methods=['DELETE'])
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
