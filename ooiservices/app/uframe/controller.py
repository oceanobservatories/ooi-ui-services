#!/usr/bin/env python
'''
uframe endpoints

'''
__author__ = 'Andy Bird'

from flask import jsonify, request, current_app, url_for, Flask
from ooiservices.app.uframe import uframe as api
from ooiservices.app import db, cache
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname
from ooiservices.app.models import Annotation
from urllib import urlencode
import requests
import json

from ooiservices.app.uframe.data import gen_data
from ooiservices.app.main.errors import internal_server_error

import json
import datetime
import math

#ignore list for data fields
FIELDS_IGNORE = ["stream_name","quality_flag"]
#time minus ()
COSMO_CONSTANT = 2208988800



def _get_data_type(data_input):
    '''
    gets the data type in a format google charts understands
    '''
    if data_input is float or data_input is int:
        return "number"
    elif data_input is str or data_input is unicode:
        return "string"
    else:
        return "unknown"

def _get_annotation(instrument_name, stream_name):
    annotations = Annotation.query.filter_by(instrument_name=instrument_name, stream_name=stream_name).all()
    return [annotation.to_json() for annotation in annotations]

def _get_col_outline(data,pref_timestamp,inital_fields,hasAnnotation,annotations,fields_have_annotation,requested_field):
    '''
    gets the column outline for the google chart response, figures out what annotations are required where...
    '''
    data_fields = []
    data_field_list= []
    #used to cound the fields, used for annotations
    field_count = 1
    #loop and generate inital col dict
    for field in inital_fields:
        if field == pref_timestamp:
            d_type = "datetime"
        elif field in FIELDS_IGNORE or str(field).endswith('_timestamp'):
            continue
        else:
            if requested_field is not None:
                if field == requested_field:
                    d_type = _get_data_type(type(data[0][field]))
                else:
                    continue
            else:
                #map the data types to the correct data type for google charts
                d_type = _get_data_type(type(data[0][field]))

        data_field_list.append(field)
        data_fields.append({"id": "",
                            "label": field,
                            "type":  d_type})

        if hasAnnotation:
            #only append annotation fields for fields that have annotations, makes resp smaller if possible
            if field in fields_have_annotation :
                data_field_list.append("annotation")
                data_field_list.append("annotationText")
                data_fields.append({"label":"title"+str(field_count),"type":  "string" , "role":"annotation" , "origin_field":field})
                data_fields.append({"label":"text" +str(field_count),"type":  "string" , "role":"annotationText", "origin_field":field})

                field_count +=1

    return data_fields,data_field_list

def _get_annotation_content(annotation_field, pref_timestamp, annotations_list, d, data_field):
    '''
    creates the annotation content for a given field
    '''
    #right now x and y are timeseries data
    for an in annotations_list:
        if an['field_x'] == pref_timestamp or an['field_y'] == data_field:
            # and and y value
            if int(d['fixed_dt']) == int(an['pos_x']):
                if annotation_field == "annotation":
                    return {"v":an["title"]}
                elif annotation_field == "annotationText":
                    return {"v":an['comment']}

    #return nothing
    return {"v":None,"f":None}

def make_cache_key():
    return urlencode(request.args)

@cache.memoize(timeout=3600)
def get_uframe_streams():
    '''
    Lists all the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'
        response = requests.get(UFRAME_DATA)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

@cache.memoize(timeout=3600)
def get_uframe_stream(stream):
    '''
    Lists the reference designators for the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'
        response = requests.get("/".join([UFRAME_DATA,stream]))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

@cache.memoize(timeout=3600)
def get_uframe_stream_contents(stream, ref):
    '''
    Gets the stream contents
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'
        response =  requests.get("/".join([UFRAME_DATA,stream,ref]))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')


@api.route('/streams')
def streams_list():
    UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'
    response = get_uframe_streams()
    if response.status_code != 200:
        return response
    streams = response.json()

    #with open('/tmp/response.json', 'w') as f:
    #    buf = streams.text.encode('UTF-8')
    #    f.write(buf)

    retval = []
    for stream in streams:
        if request.args.get('stream_name'):
            if request.args.get('stream_name') not in stream:
                continue
        response = get_uframe_stream(stream)
        if response.status_code != 200:
            return response
        refs = response.json()

        if request.args.get('reference_designator'):
            refs = [r for r in refs if request.args.get('reference_designator') in r]

        for ref in refs:
            data_dict = {}
            response = get_uframe_stream_contents(stream, ref)
            if response.status_code != 200:
                return response
            data =  response.json()
            preferred = data[0][u'preferred_timestamp']
            data_dict['start'] = data[0][preferred] - COSMO_CONSTANT
            data_dict['end'] = data[-1][preferred] - COSMO_CONSTANT
            data_dict['reference_designator'] = ref
            data_dict['download'] = "/".join([UFRAME_DATA,stream,ref])
            data_dict['stream_name'] = stream
            retval.append(data_dict)

    return jsonify(streams=retval)

@api.route('/get_data/<string:instrument>/<string:stream>',methods=['GET'])
def get_data(stream, instrument):
    #get data from uframe
    #-------------------
    # m@c: 02/01/2015
    #uframe url to get stream data from instrument:
    # /sensor/user/inv/<stream_name>/<instrument_name>
    #
    #-------------------
    #TODO: create better error handler if uframe is not online/responding
    try:
        data = requests.get(current_app.config['UFRAME_URL'] + '/sensor/user/inv/' + stream + '/' + instrument)
        data = data.json()
    except:
        return internal_server_error('uframe connection cannot be made.')

    annotations = []
    hasAnnotation = False
    hasStartDate = False
    hasEndDate = False
    field = None
    #this is needed as some plots dont have annotations
    if 'field' in request.args:
        field =  request.args['field']

    if 'annotation' in request.args:
        #generate annotation plot
        if request.args['annotation'] == "true":
            hasAnnotation = True

    if 'startdate' in request.args:
        st_date = datetime.datetime.strptime(request.args['startdate'], "%Y-%m-%d %H:%M:%S")
        hasStartDate = True

    if 'enddate' in request.args:
        ed_date = datetime.datetime.strptime(request.args['enddate'], "%Y-%m-%d %H:%M:%S")
        hasEndDate = True

    #got normal data plot
    #create the data fields,assumes the same data fields throughout
    d_row = data[0]
    #data store
    some_data = []

    time_idx = -1
    pref_timestamp = d_row["preferred_timestamp"]
    #figure out the header rows
    inital_fields = d_row.keys()
    #move timestamp to the front
    inital_fields.insert(0, inital_fields.pop(inital_fields.index(pref_timestamp)))

    fields_have_annotation = []
    #get the annotations, only get the annotations if requested
    if hasAnnotation:
        annotations = _get_annotation(instrument, stream)
        for an in annotations:
            # add the annotations to the list, but dont add them for the preferred timestamp
            if an['field_x'] not in fields_have_annotation and an['field_x'] != pref_timestamp:
                fields_have_annotation.append(an['field_x'])
            if an['field_y'] not in fields_have_annotation and an['field_y'] != pref_timestamp:
                fields_have_annotation.append(an['field_y'])

    data_cols,data_field_list = _get_col_outline(data,pref_timestamp,inital_fields,hasAnnotation,annotations,fields_have_annotation,field)

    #figure out the data content
    #annotations will be in order and
    for d in data:        
        c_r = []
        
        #used to store the actual datafield in use by the annotations, as it will always go datafield then annotation
        data_field = None

        #create data time object, should only ever be one timestamp....the pref one
        d['fixed_dt'] = d[pref_timestamp] - COSMO_CONSTANT
        c_dt = datetime.datetime.fromtimestamp(d['fixed_dt'])

        if hasStartDate:            
            if not c_dt >= st_date:                
                continue
        if hasEndDate:              
            if not c_dt <= ed_date:
                continue

        d['dt'] = c_dt
        str_date = c_dt.isoformat()
        #create the data
        date_str = "Date("+str(c_dt.year)+","+str(c_dt.month)+","+str(c_dt.day)+","+str(c_dt.hour)+","+str(c_dt.minute)+","+str(c_dt.second)+")"

        for field in data_field_list:
            if field == pref_timestamp:
                #datetime field
                c_r.append({"f":str_date,"v":date_str})
                time_idx = len(c_r)-1

            elif field.startswith("annotation"):
                #field = annotation, data_field = actual field in use
                annotation_content = _get_annotation_content(field,pref_timestamp,annotations,d, data_field)
                c_r.append(annotation_content)

            else:
                #non annotation field
                data_field = field
                c_r.append({"v":d[field],"f":d[field]})

        some_data.insert(0,{"c":c_r})

    #genereate dict for the data thing
    resp_data = {'cols':data_cols,
                 'rows':some_data,
                 'data_length':len(some_data)
                 #'start_time' : datetime.datetime.fromtimestamp(data[0][pref_timestamp]).isoformat(),
                 #'end_time' : datetime.datetime.fromtimestamp(data[-1][pref_timestamp]).isoformat()
                 }

    return jsonify(**resp_data)
