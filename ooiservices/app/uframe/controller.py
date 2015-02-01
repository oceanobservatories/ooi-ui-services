#!/usr/bin/env python
'''
uframe endpoints

'''
__author__ = 'Andy Bird'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.uframe import uframe as api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname
from ooiservices.app.models import Annotation
import requests
import json

from ooiservices.app.uframe.data import gen_data

import json
import datetime

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
        raise

    #got normal data plot
    #create the data fields,assumes the same data fields throughout
    d_row = data[0]
    data_fields = []
    data_field_list= []
    some_data = []
    #time minus ()
    cosmo_constant = 2208988800
    time_idx = -1
    pref_timestamp = d_row["preferred_timestamp"]
    #ignore list for data fields
    ignore_list = ["preferred_timestamp","stream_name","driver_timestamp","quality_flag"]
    #figure out the header rows
    inital_fields = d_row.keys()
    #move timestamp to the front
    inital_fields.insert(0, inital_fields.pop(inital_fields.index(pref_timestamp)))

    for field in inital_fields:
        if field in ignore_list:
            pass
        else:
            #map the data types to the correct data type for google charts
            if field == pref_timestamp:
                d_type = "datetime"
            else:
                d_type = _get_data_type(type(data[0][field]))

            data_field_list.append(field)
            data_fields.append({"id": "",
                                "label": field,
                                "type":  d_type})

    #figure out the data content
    for d in data:
        c_r = []
        for field in data_field_list:
            if field.endswith("_timestamp"):
                #create data time object
                c_dt = datetime.datetime.fromtimestamp(d[field] - cosmo_constant)
                str_date = c_dt.isoformat()
                date_str = "Date("+str(c_dt.year)+","+str(c_dt.month)+","+str(c_dt.day)+","+str(c_dt.hour)+","+str(c_dt.minute)+","+str(c_dt.second)+")"
                c_r.append({"f":str_date,"v":date_str})
                if field == pref_timestamp:
                    time_idx = len(c_r)-1
            else:
                c_r.append({"v":d[field],"f":d[field]})
        some_data.insert(0,{"c":c_r})

    #genereate dict for the data thing
    resp_data = {'annotations':_get_annotation(instrument, stream),
                 'cols':data_fields,
                 'rows':some_data
                 #'size':len(some_data),
                 #'start_time' : datetime.datetime.fromtimestamp(data[0][pref_timestamp]).isoformat(),
                 #'end_time' : datetime.datetime.fromtimestamp(data[-1][pref_timestamp]).isoformat()
                 }

    return jsonify(**resp_data)