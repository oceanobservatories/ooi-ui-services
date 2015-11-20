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
import requests

#List all annotations. build 6
@api.route('/annotation/<string:instrument>/<string:stream>')
def get_annotations(instrument,stream):
    try:
        url = current_app.config['UFRAME_ANNOTATION_URL'] + current_app.config['UFRAME_ANNOTATION_BASE']+"/find/"+instrument
        r = requests.get(url)
        data = r.json()

        return jsonify( {'annotations' : data }), 201

    except Exception, e:
        return jsonify( {'error' : "could not obtain annotation(s): "+str(e) }), 500

#List all annotations. build 6
@api.route('/annotation/all')
def get_all_annotations():
    try:
        url = current_app.config['UFRAME_ANNOTATION_URL'] + current_app.config['UFRAME_ANNOTATION_BASE']+"/find/all"
        r = requests.get(url)
        data = r.json()

        return jsonify( {'annotations' : data }), 200

    except Exception, e:
        return jsonify( {'error' : "could not obtain annotation(s): "+str(e) }), 500

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
        if 'id' in post_req: del post_req['id']

    uframe_link = current_app.config['UFRAME_ANNOTATION_URL'] + current_app.config['UFRAME_ANNOTATION_BASE']
    annotation_url = "/".join([uframe_link,'add',ref_def])

    r = requests.post(annotation_url , data=json.dumps(post_req) , timeout=10)

    if r.status_code == 200:
        return jsonify( {} ), 201
    else:
        return jsonify( {'error' : r.reason }), r.status_code

#Update an existing annotation.
@api.route('/annotation', methods=['POST'])
#@auth.login_required
#@scope_required('annotate')
def create_annotation():
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

            return process_annotation(new_st_date,new_ed_date,new_annotation,ref_des,None)

        else:
            return jsonify( {'error' : "required information not specified" }), 500
    except Exception, e:
        return jsonify( {'error' : "could not obtain annotation(s): "+str(e) }), 500

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
