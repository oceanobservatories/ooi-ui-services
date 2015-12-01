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


def find_parameter_ids(mooring, platform, instrument, y_parameters, x_parameters):

    def shorten_time_units(unit):
        if 'seconds since 1900-01-01' in unit:
            return u'sec since 1900'
        elif 'seconds since 1900-01-01' in unit:
            return u'sec since 1970'
        else:
            return unit

    UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    url = "/".join([UFRAME_DATA, mooring, platform, instrument, "metadata/parameters"])

    parameter_list = requests.get(url).json()
    parameter_dict = {}
    parameter_ids = []
    all_units = {}
    y_units = []
    x_units = []

    units_mapping = {}
    for each in parameter_list:
        parameter_dict[each['particleKey']] = each['pdId']
        all_units[each['particleKey']] = each['units']

    for each in x_parameters:
        parameter_ids.append(str(parameter_dict[each]).strip())
        x_units.append(shorten_time_units(all_units[each]))
        units_mapping[each] = shorten_time_units(all_units[each])

    for each in y_parameters:
        parameter_ids.append(str(parameter_dict[each]).strip())
        y_units.append(shorten_time_units(all_units[each]))
        units_mapping[each] = shorten_time_units(all_units[each])

    return parameter_ids, y_units, x_units, units_mapping


def get_multistream_data(stream1, stream2, instrument1, instrument2, var1, var2):

    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_multi_stream_contents, validate_date_time
    '''
    get data from uframe
    '''
    mooring1, platform1, instrument1, stream_type1, stream1 = split_stream_name('_'.join([instrument1, stream1]))
    mooring2, platform2, instrument2, stream_type2, stream2 = split_stream_name('_'.join([instrument2, stream2]))

    parameter_ids1, y_units1, _, units_mapping1 = find_parameter_ids(mooring1, platform1, instrument1, [var1], [])
    parameter_ids2, y_units2, _, units_mapping2 = find_parameter_ids(mooring2, platform2, instrument2, [var2], [])

    units = units_mapping1.copy()
    units.update(units_mapping2)

    stream1_dict = {}
    stream2_dict = {}
    stream1_dict['refdes'] = '-'.join([mooring1, platform1, instrument1])  # 'CP05MOAS-GL340-03-CTDGVM000'
    stream2_dict['refdes'] = '-'.join([mooring2, platform2, instrument2])  # 'CP05MOAS-GL340-02-FLORTM000'

    stream1_dict['method'] = stream_type1
    stream2_dict['method'] = stream_type2

    stream1_dict['stream'] = stream1
    stream2_dict['stream'] = stream2

    stream1_dict['params'] = parameter_ids1[0]
    stream2_dict['params'] = parameter_ids2[0]

    try:
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            ed_date = validate_date_time(st_date, ed_date)

            # data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
            data, status_code = get_uframe_multi_stream_contents(stream1_dict, stream2_dict, st_date, ed_date)

            if status_code != 200:
                raise Exception(data)
            else:
                return data, units
        else:
            message = 'Failed to make interpolated data plot: Need to include startdate and enddate'
            current_app.logger.exception(message)
            raise Exception(message)

    except Exception as e:
        message = 'Failed to make interpolated data plot. Error: ' + str(e.message)
        current_app.logger.exception(message)
        raise Exception(message)


def get_simple_data(stream, instrument, yfields, xfields, include_time=True):
    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_plot_contents_chunked, validate_date_time, to_bool_str
    '''
    get data from uframe    
    '''    
    mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
    parameter_ids, y_units, x_units,units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)

    try:
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            ed_date = validate_date_time(st_date, ed_date)
            if 'dpa_flag' in request.args:
                dpa_flag = to_bool_str(request.args['dpa_flag'])
            else:
                dpa_flag = "0"

            # data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag, parameter_ids)

            if status_code != 200:
                raise Exception(data)
            else:
                return data, units_mapping

    except Exception as e:
        message = 'Failed to make plot - received error on uframe request. Error: ' + str(e.message)
        current_app.logger.exception(message)
        raise Exception(message)


def get_data(stream, instrument, yfields, xfields, include_time=True):
    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_plot_contents_chunked, validate_date_time, to_bool_str
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
    parameter_ids, y_units, x_units,units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)

    try:
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            ed_date = validate_date_time(st_date, ed_date)
            if 'dpa_flag' in request.args:
                dpa_flag = to_bool_str(request.args['dpa_flag'])
            else:
                dpa_flag = "0"

            # data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag, parameter_ids)
            if status_code != 200:
                # return {'error': 'could not get data'}
                # return {'error': '(%s) could not get_uframe_stream_contents' % str(response.status_code)}
                raise Exception(data)
        else:
            message = 'Failed to make plot - start end dates not applied.'
            current_app.logger.exception(message)
            raise Exception(message)

    except Exception as e:
        message = 'Failed to make plot - received error on uframe request. error: ' + str(e.message)
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

    # Initialize the data dicts
    vals = [[] for field in xfields]
    x = OrderedDict(zip(xfields, vals))
    vals = [[] for field in yfields]
    y = OrderedDict(zip(yfields, vals))

    if len(yfields) >= len(xfields):
        qaqc_fields = yfields
    else:
        qaqc_fields = xfields

    # vals = [np.zeros(len(data)) for field in qaqc_fields]
    vals = [[] for field in qaqc_fields]
    qaqc = OrderedDict(zip(qaqc_fields, vals))

    # Loop through rows of data and fill the response data
    for ind, row in enumerate(data):
        # used to handle multiple streams
        if row['pk']['stream'] == stream:
            # x
            for xfield in xfields:
                if xfield == 'time':
                    x[xfield].append(float(row['pk']['time']))
                else:
                    x[xfield].append(row[xfield])
                    key = xfield + '_qc_results'
                    if key in row:
                        qaqc[yfield].append(int(row[key]))
                    # else:
                    #     current_app.logger.exception('QAQC not found for {0}'.format(xfield))
            # y
            for yfield in yfields:
                if yfield == 'time':
                    y[yfield].append(float(row['pk']['time']))
                else:
                    y[yfield].append(row[yfield])
                    key = yfield + '_qc_results'
                    if key in row:
                        qaqc[yfield].append(int(row[key]))
                    # else:
                    #     current_app.logger.exception('QAQC not found for {0}'.format(yfield))

    # generate dict for the data thing
    resp_data = {'x': x,
                 'y': y,
                 'data_length': len(data),
                 'x_field': xfields,
                 'x_units': x_units,
                 'y_field': yfields,
                 'y_units': y_units,
                 'dt_units': 'seconds since 1900-01-01 00:00:00',
                 'qaqc': qaqc
                 }

    return resp_data
