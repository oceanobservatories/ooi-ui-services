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

            return jsonify( {'annotations' : data['annotations'] }), 201
        else:
            return jsonify( {'error' : "no dates specified" }), 500   
    except Exception, e:
        return jsonify( {'error' : "could not obtain annotation(s): "+str(e) }), 500


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

def process_annotation(begin_dt,end_dt,annotation_text,ref_def,annotation_id=None):
    '''
    PROCESS ANNOTATION :  either update or create depending on if id is passed in
    '''

    post_req = {'beginDT': begin_dt,
                'endDT': end_dt,
                'referenceDesignator' : ref_def,
                'annotation': annotation_text,
                'id':annotation_id   
                }
   
    if annotation_id == None:
        pass
    else:
        uframe_link = current_app.config['UFRAME_ANNOTATION_URL'] + current_app.config['UFRAME_ANNOTATION_BASE']
        annotation_url = "/".join([uframe_link,'add',ref_def])

        r = requests.post(annotation_url , data=json.dumps(post_req) , timeout=10)

        if r.status_code == 200:            
            return jsonify( {} ), 201
        else:
            return jsonify( {'error' : r.reason }), r.status_code

def generate_annotation_data():
    pass


#Update an existing annotation.
@api.route('/annotation/<string:annotation_id>', methods=['PUT'])
#@auth.login_required
#@scope_required('annotate')
def edit_annotation(annotation_id):
    try:        
        data = json.loads(request.data)           
        if ('referenceDesignator'in data and 
            'annotation' in data and 
            'beginDT' in data and 
            'endDT' in data):            

            new_st_date = data['beginDT']
            new_ed_date = data['endDT']
            new_annotation = data['annotation']           
            ref_des = data['referenceDesignator']    

            return process_annotation(new_st_date,new_ed_date,new_annotation,ref_des,annotation_id)

        else:
            return jsonify( {'error' : "required information not specified" }), 500        
    except Exception, e:
        return jsonify( {'error' : "could not obtain annotation(s): "+str(e) }), 500


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
