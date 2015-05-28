#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

from flask import request, current_app
import numpy as np
from collections import OrderedDict
import requests

__author__ = 'Andy Bird'

# ignore list for data fields
FIELDS_IGNORE = ["stream_name", "quality_flag"]
COSMO_CONSTANT = 2208988800

def find_parameter_ids(mooring, platform, instrument, yfields,xfields):

    UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    url = "/".join([UFRAME_DATA,mooring, platform, instrument,"metadata/parameters"])
    
    parameter_list = requests.get(url).json()

    parameter_dict = {}
    
    for each in parameter_list:
        parameter_dict[each['particleKey']] = each['pdId']
    
    parameters = yfields
    parameter_ids = [str(parameter_dict['time']).strip()]

    for each in parameters:
        parameter_ids.append(str(parameter_dict[each]).strip())
    return parameter_ids


def get_data(stream, instrument, yfields, xfields, include_time=True):
    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_plot_contents_chunked,validate_date_time, get_uframe_stream_contents_chunked
    '''get data from uframe
    # -------------------
    # m@c: 02/01/2015
    #uframe url to get stream data from instrument:
    # /sensor/user/inv/<stream_name>/<instrument_name>
    #
    #-------------------
    # TODO: create better error handler if uframe is not online/responding
    '''
    mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
    
    parameter_ids = find_parameter_ids(mooring, platform, instrument, yfields,xfields)
    
    
    try:
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            ed_date = validate_date_time(st_date,ed_date)
            if 'dpa_flag' in request.args:
                dpa_flag = request.args['dpa_flag']
            else:    
                dpa_flag = "0"   

            data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
            if status_code !=200:
                #return {'error': 'could not get data'}
                #return {'error': '(%s) could not get_uframe_stream_contents' % str(response.status_code)}
                raise Exception('(%s) could not get_uframe_stream_contents' % str(status_code))           
        else:
            message = 'Failed to make plot - start end dates not applied.'
            current_app.logger.exception(message)
            raise Exception(message)

    except Exception as e:
        message = 'Failed to make plot - received error on uframe request. error: '+ str(e.message)
        current_app.logger.exception(message)
        raise Exception(message)

    if len(data) == 0:
        raise Exception('no data available')

    if "pk" not in data[0]:
        message = 'primary information not available'
        current_app.logger.exception(message)
        raise Exception(message)

    for xfield in xfields:
        if xfield == 'time':
            if "time" not in data[0]['pk']:
                message = 'time information not available'
                current_app.logger.exception(message)
                raise Exception(message)
        else:
            if xfield not in data[0]:
                message = 'requested data xfield (%s) not available' % xfield
                current_app.logger.exception(message)
                raise Exception(message)

    for yfield in yfields:
        if yfield == 'time':
            if "time" not in data[0]['pk']:
                message = 'time information not available'
                current_app.logger.exception(message)
                raise Exception(message)
        else:
            if yfield not in data[0]:
                message = 'requested data yfield (%s) not available' % yfield
                current_app.logger.exception(message)
                raise Exception(message)

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
