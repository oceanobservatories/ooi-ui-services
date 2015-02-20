#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

__author__ = 'Andy Bird'

from flask import jsonify, request, current_app, url_for, Flask, make_response
from ooiservices.app.uframe import uframe as api

import numpy as np
import calendar
import time
from dateutil.parser import parse
from datetime import datetime
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app import cache
import requests

#ignore list for data fields
FIELDS_IGNORE = ["stream_name","quality_flag"]
COSMO_CONSTANT = 2208988800


def get_data(stream, instrument,yfield,xfield,include_time=False):
    #get data from uframe
    #-------------------
    # m@c: 02/01/2015
    #uframe url to get stream data from instrument:
    # /sensor/user/inv/<stream_name>/<instrument_name>
    #
    #-------------------
    #TODO: create better error handler if uframe is not online/responding
    data = []
    try:
        url = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv/' + stream + '/' + instrument
        data = requests.get(url)
        data = data.json()        
    except Exception,e:
        return {'error':'uframe connection cannot be made:'+str(e)}

    if len(data)==0:
        return {'error':'no data available'}    

    hasStartDate = False
    hasEndDate = False

    if 'startdate' in request.args:
        st_date = datetime.datetime.strptime(request.args['startdate'], "%Y-%m-%d %H:%M:%S")
        hasStartDate = True

    if 'enddate' in request.args:
        ed_date = datetime.datetime.strptime(request.args['enddate'], "%Y-%m-%d %H:%M:%S")
        hasEndDate = True

    #got normal data plot
    #create the data fields,assumes the same data fields throughout
    d_row = data[0]   
    if yfield not in d_row or xfield not in d_row :
        return {'error':'requested data fields not available'}      

    #override the timestamp to the prefered
    if "_timestamp" in xfield:
        xfield = d_row["preferred_timestamp"]

    x = [ d[xfield] for d in data ]
    y = [ d[yfield] for d in data ]    

    #genereate dict for the data thing
    resp_data = {'x':x,
                 'y':y,
                 'data_length':len(x),
                 'x_field':xfield,
                 'y_field':yfield,
                 'dt_units':'seconds since 1900-01-01 00:00:00'
                 #'start_time' : datetime.datetime.fromtimestamp(data[0][pref_timestamp]).isoformat(),
                 #'end_time' : datetime.datetime.fromtimestamp(data[-1][pref_timestamp]).isoformat()
                 }

    #return jsonify(**resp_data)
    return resp_data

def get_time_label(ax, dates):
    '''
    Custom date axis formatting
    '''
    def format_func(x, pos=None):
        x = mdates.num2date(x)
        if pos == 0:
            fmt = '%Y-%m-%d %H:%M'
        else:
            fmt = '%H:%M'
        label = x.strftime(fmt)
        # label = label.rstrip("0")
        # label = label.rstrip(".")
        return label
    day_delta = (max(dates)-min(dates)).days

    if day_delta < 1:
        ax.xaxis.set_major_formatter(FuncFormatter(format_func))
    else:
        # pass
        major = mdates.AutoDateLocator()
        formt = mdates.AutoDateFormatter(major, defaultfmt=u'%Y-%m-%d')
        formt.scaled[1.0] = '%Y-%m-%d'
        formt.scaled[30] = '%Y-%m'
        formt.scaled[1./24.] = '%Y-%m-%d %H:%M:%S'
        # formt.scaled[1./(24.*60.)] = FuncFormatter(format_func)
        ax.xaxis.set_major_locator(major)
        ax.xaxis.set_major_formatter(formt)
