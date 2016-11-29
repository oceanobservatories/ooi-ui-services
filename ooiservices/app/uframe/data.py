#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

from flask import request, current_app
from collections import OrderedDict
from ooiservices.app.uframe.common_tools import to_bool_str
from ooiservices.app.uframe.uframe_tools import uframe_get_instrument_metadata_parameters

__author__ = 'Andy Bird'


COSMO_CONSTANT = 2208988800


def find_parameter_ids(mooring, platform, instrument, y_parameters, x_parameters):
    """
    Using uframe instrument metadata, prepare list of x and y parameters by reference designator.
    This is getting all parameters, where it should only get parameters for the stream being plotted. Review.
    """
    try:
        rd = '-'.join([mooring, platform, instrument])
        parameter_list = uframe_get_instrument_metadata_parameters(rd)
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
            parameter_ids.append(str(parameter_dict[each]))
            x_units.append(all_units[each])
            units_mapping[each] = all_units[each]

        for each in y_parameters:
            parameter_ids.append(str(parameter_dict[each]))
            y_units.append(all_units[each])
            units_mapping[each] = all_units[each]

        return parameter_ids, y_units, x_units, units_mapping
    except Exception as err:
        message = str(err)
        #print '\n (data.py:find_parameter_ids) Exception: %s' % message
        raise Exception(message)



def get_multistream_data(stream1, stream2, instrument1, instrument2, var1, var2):

    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_multi_stream_contents #, validate_date_time
    '''
    get data from uframe
    '''
    debug = False
    try:
        if debug: print '\n debug -- Entered get_multistream_data...'
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

        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            #ed_date = validate_date_time(st_date, ed_date)
            # data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
            data, status_code = get_uframe_multi_stream_contents(stream1_dict, stream2_dict, st_date, ed_date)

            if status_code != 200:
                raise Exception(data)
            else:
                return data, units
        else:
            message = 'Define start and end dates.'
            raise Exception(message)

    except Exception as e:
        message = str(e.message)
        #print '\n (data.py:get_multistream_data) Exception: %s' % message
        #current_app.logger.exception(message)
        raise Exception(message)


def get_simple_data(stream, instrument, yfields, xfields, include_time=True):
    debug = True
    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_plot_contents_chunked #, validate_date_time
    """
    get data from uframe
    """
    try:
        if debug: print '\n debug -- Entered get_simple_data...'
        mooring, platform, instrument = instrument.split('-', 2)
        stream_value = stream[:]
        stream_type, stream = stream.split('_')
        stream = stream.replace('-', '_')
        stream_type = stream_type.replace('-', '_')
        if debug:
            print '\n stream_value: ', stream_value
            print '\n stream: ', stream
            print '\n stream_type: ', stream_type
        #mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
        parameter_ids, y_units, x_units, units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)

        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            if not st_date or st_date is None or not ed_date or ed_date is None or \
                            len(st_date) == 0 or len(ed_date) == 0:
                message = 'Define start and end dates, one or both are empty or null.'
                raise Exception(message)

            #ed_date = validate_date_time(st_date, ed_date)
            if 'dpa_flag' in request.args:
                dpa_flag = to_bool_str(request.args['dpa_flag'])
            else:
                dpa_flag = '0'

            if debug:
                print '\n debug -- Calling get_uframe_plot_contents_chunked...'
            # data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                                                 st_date, ed_date, dpa_flag, parameter_ids)
            if debug:
                print '\n debug -- After calling get_uframe_plot_contents_chunked...'
                print '\n debug -- status_code: ', status_code
            if status_code != 200:
                message = 'Failed to get uframe plot contents chunked. Error message: ', status_code
                raise Exception(message)
                #raise Exception(data)
            return data, units_mapping
        else:
            message = 'Define start and end dates.'
            raise Exception(message)

    except Exception as e:
        message = str(e.message)
        if debug: print '\n (data.py:get_simple_data) Exception: %s' % message
        #current_app.logger.exception(message)
        raise Exception(message)


def get_data(stream, instrument, yfields, xfields, include_time=True):
    from ooiservices.app.uframe.controller import split_stream_name, get_uframe_plot_contents_chunked
    #validate_date_time, to_bool_str
    """ get data from uframe
    # -------------------
    # m@c: 02/01/2015
    #uframe url to get stream data from instrument:
    # /sensor/user/inv/<stream_name>/<instrument_name>
    #
    #-------------------
    # TODO: create better error handler if uframe is not online/responding
    """
    #mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
    #parameter_ids, y_units, x_units,units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)
    debug = False
    data = []
    try:
        if debug: print '\n debug -- Entered get_data...'
        if debug: print '\n debug -- Step 1 -- have data, review data......'
        mooring, platform, instrument = instrument.split('-', 2)
        stream_value = stream[:]
        stream_type, stream = stream.split('_')
        stream = stream.replace('-', '_')
        stream_type = stream_type.replace('-', '_')
        if debug:
            print '\n stream_value: ', stream_value
            print '\n stream_type: ', stream_type
            print '\n stream: ', stream
        #mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
        parameter_ids, y_units, x_units, units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)

        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']

            #ed_date = validate_date_time(st_date, ed_date)
            if 'dpa_flag' in request.args:
                dpa_flag = to_bool_str(request.args['dpa_flag'])
            else:
                dpa_flag = "0"

            # data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type,
            # stream, st_date, ed_date, dpa_flag)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type,
                                                                 stream, st_date, ed_date, dpa_flag, parameter_ids)
            if status_code != 200:
                message = 'Failed to get data from uframe, status code: %d' % status_code
                if data is not None:
                    if debug: print '\n debug -- get_data: data: ', data
                current_app.logger.exception(message)
                raise Exception(message)
            if not data or data is None:
                message = 'No data returned for stream %s and instrument %s.' % (stream[0], instrument[0])
                raise Exception(message)
        else:
            message = 'Please Define Start and End Dates'
            current_app.logger.exception(message)
            raise Exception(message)

    except Exception as e:
        message = str(e.message)
        #current_app.logger.exception(message)
        raise Exception(message)

    if debug: print '\n debug -- Step 2 -- have data?, review data......'
    try:
        if data is None or not data or len(data) == 0:
            raise Exception('No Data Available')

        if "pk" not in data[0]:
            message = 'Primary Information Not Available'
            current_app.logger.exception(message)
            raise Exception(message)

        for xfield in xfields:
            if xfield == 'time':
                if "time" not in data[0]:
                    message = 'Time Variable Not Available'
                    current_app.logger.exception(message)
                    raise Exception(message)
            else:
                if xfield not in data[0]:
                    message = 'Requested Data (%s) Not Available' % xfield
                    current_app.logger.exception(message)
                    raise Exception(message)

        for yfield in yfields:
            if yfield == 'time':
                if "time" not in data[0]:
                    message = 'Time Variable Not Available'
                    current_app.logger.exception(message)
                    raise Exception(message)
            else:
                if yfield not in data[0]:
                    message = 'Requested Data (%s) Not Available' % yfield
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
                        x[xfield].append(float(row['time']))
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
                        y[yfield].append(float(row['time']))
                    else:
                        y[yfield].append(row[yfield])
                        key = yfield + '_qc_results'
                        if key in row:
                            qaqc[yfield].append(int(row[key]))
                        # else:
                        #     current_app.logger.exception('QAQC not found for {0}'.format(yfield))

        if debug: print '\n debug -- Step 3 -- have data, prepare resp_data......'
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
    except Exception as err:
        message = str(err.message)
        if debug: print '\n (data.py:get_data) Exception: %s' % message
        #current_app.logger.exception(message)
        raise Exception(message)
