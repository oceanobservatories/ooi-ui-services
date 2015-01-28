#!/usr/bin/env python
'''
uframe controller

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth

from ooiservices.app.main.data import gen_data

import json
import datetime

def get_uframe_data():
    '''
    stub mock function to get some sample data
    '''
    json_data=open('ooiservices/tests/sampleData.json')
    data = json.load(json_data)
    return data

@api.route('/get_data')
def get_data():
    #get data from uframe
    data = get_uframe_data()
    #create the data fields,assumes the same data fields throughout
    d_row = data[0]
    data_fields = []
    some_data = []
    #time minus ()
    cosmo_constant = 2208988800
    time_idx = -1
    for field in d_row:
        if field == "preferred_timestamp" or field == u'stream_name' or field == u'driver_timestamp':
            pass
        else:
            data_fields.append(field)

    for d in data:
        r = []
        for field in data_fields:
            if field.endswith("_timestamp"):
                r.append(d[field] - cosmo_constant)
                if field == "internal_timestamp":
                    time_idx = len(r)-1
            else:
                r.append(d[field])
        some_data.append(r)

    #genereate dict for the data thing
    resp_data = {}
    resp_data['cols'] = data_fields
    resp_data['rows'] = some_data
    resp_data['size'] = len(some_data)
    resp_data['start_time'] = datetime.datetime.fromtimestamp((some_data[0][time_idx])).isoformat()
    resp_data['end_time'] = datetime.datetime.fromtimestamp((some_data[-1][time_idx])).isoformat()
    return jsonify(**resp_data)