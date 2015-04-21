#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

from flask import request, current_app
import numpy as np
from collections import OrderedDict

__author__ = 'Andy Bird'

# ignore list for data fields
FIELDS_IGNORE = ["stream_name", "quality_flag"]
COSMO_CONSTANT = 2208988800


def get_data(stream, instrument, yfields, xfields, include_time=True):
    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_stream_contents,validate_date_time
    '''get data from uframe
    # -------------------
    # m@c: 02/01/2015
    #uframe url to get stream data from instrument:
    # /sensor/user/inv/<stream_name>/<instrument_name>
    #
    #-------------------
    # TODO: create better error handler if uframe is not online/responding
    '''
    data = []

    mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))

    try:
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            ed_date = validate_date_time(st_date,ed_date)
            if 'dpa_flag' in request.args:
                dpa_flag = request.args['dpa_flag']
            else:    
                dpa_flag = "0"   

            response = get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)

            if response.status_code !=200:
                return {'error': 'could not get data'}                
            data = response.json()
        else:
            current_app.logger.exception('Failed to make plot')
            return {'error': 'start end dates not applied:'}
    except Exception, e:
        current_app.logger.exception('Failed to make plot')
        return {'error': 'uframe connection cannot be made:'+str(e)}

    if len(data) == 0:
        return {'error': 'no data available'}

    if "pk" not in data[0]:
        current_app.logger.exception('primary information not available')
        return {'error': 'primary information not available'}
    for xfield in xfields:
        if xfield == 'time':
            if "time" not in data[0]['pk']:
                current_app.logger.exception('time information not available')
                return {'error': 'time information not available'}
        else:
            if xfield not in data[0]:
                current_app.logger.exception('requested data xfield not available')
                return {'error': 'requested data xfield not available'}

    for yfield in yfields:
        if yfield == 'time':
            if "time" not in data[0]['pk']:
                current_app.logger.exception('time information not available')
                return {'error': 'time information not available'}
        else:
            if yfield not in data[0]:
                current_app.logger.exception('requested data yfield not available')
                return {'error': 'requested data yfield not available'}

    # override the timestamp to the prefered
    # xdata = OrderedDict()
    # ydata = OrderedDict()

    x = OrderedDict({k: np.empty(len(data)) for k in xfields})
    y = OrderedDict({k: np.empty(len(data)) for k in yfields})

    for ind, row in enumerate(data):
        # used to handle multiple streams
        if row['pk']['stream'] == stream:
            # x
            for xfield in xfields:
                if xfield == 'time':
                    x[xfield][ind] = float(row['pk']['time'])
                else:
                    x[xfield][ind] = row[xfield]
            # y
            for yfield in yfields:
                if yfield == 'time':
                    y[yfield][ind] = float(row['pk']['time'])
                else:
                    y[yfield][ind] = row[yfield]
    # generate dict for the data thing
    resp_data = {'x': x,
                 'y': y,
                 'data_length': len(data),
                 'x_field': xfields,
                 'x_units': '',
                 'y_field': yfields,
                 'y_units': '',
                 'dt_units': 'seconds since 1900-01-01 00:00:00'
                 }
    return resp_data
