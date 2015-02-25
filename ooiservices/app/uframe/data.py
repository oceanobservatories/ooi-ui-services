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
import json

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
    #dt_bounds = '?beginDT=2014-05-03T12:12:12.000Z&endDT=2014-05-03T23:12:12.000Z'
    dt_bounds = ''
    instrument = instrument.replace('-','/',2) # replace the - with a / for the new uframe

    try:
        url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE'] +'/' + instrument+ "/telemetered/"+stream + "/" + dt_bounds        
        print url
        data = requests.get(url)
        data = data.json()   
    except Exception,e:
        return {'error':'uframe connection cannot be made:'+str(e)}

    if len(data)==0:
        return {'error':'no data available'}    

    if "pk" not in data[0]:
        return {'error':'primary information not available'}    


    if xfield == 'time':
        if "time" not in data[0]['pk']:
            return {'error':'time information not available'}
    else:
        if xfield not in data[0]:
            return {'error':'requested data xfield not available'}  


    if yfield == 'time':
        if "time" not in data[0]['pk']:
            return {'error':'time information not available'}
    else:
        if yfield not in data[0]:
            return {'error':'requested data yfield not available'}      

    hasStartDate = False
    hasEndDate = False

    if 'startdate' in request.args:
        st_date = datetime.datetime.strptime(request.args['startdate'], "%Y-%m-%d %H:%M:%S")
        hasStartDate = True

    if 'enddate' in request.args:
        ed_date = datetime.datetime.strptime(request.args['enddate'], "%Y-%m-%d %H:%M:%S")
        hasEndDate = True   

    #override the timestamp to the prefered
    x = []
    y = []  

    for row in data:
        #used to handle multiple streams
        if row['stream_name'] == stream:
            #x
            if xfield == 'time':                   
                x.append(float(row['pk']['time']))
            else:
                x.append(row[xfield])
            #y
            if yfield == 'time':                   
                y.append(float(row['pk']['time']))
            else:
                y.append(row[yfield])                                

    #genereate dict for the data thing
    resp_data = {'x':x,
                 'y':y,
                 'data_length':len(x),
                 'x_field':xfield,
                 'x_units':'',                 
                 'y_field':yfield,
                 'y_units':'',
                 'dt_units':'seconds since 1900-01-01 00:00:00'
                 }

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
