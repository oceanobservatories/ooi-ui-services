#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

from flask import request
from collections import OrderedDict
from ooiservices.app.uframe.common_tools import to_bool_str
from ooiservices.app.uframe.stream_tools import get_stream_parameters
from requests.exceptions import (ConnectionError, Timeout)

__author__ = 'Andy Bird'


COSMO_CONSTANT = 2208988800


def new_find_parameter_ids(reference_designator, stream, y_parameters, x_parameters):
    """
    Using stream parameters information from preload.
    Prepare list of x and y parameters by reference designator.
    {
      "display_name": "Seawater Conductivity",
      "id": "pd1",
      "name": "conductivity",
      "parameter_type": "quantity",
      "particleKey": "conductivity",
      "type": "float",
      "unit": "S m-1",
      "shape": "scalar"
    },
    """
    debug = False
    try:
        if debug: print '\n debug -- (new_find_parameter_ids) reference_designator: ', reference_designator
        parameters = get_stream_parameters(stream, reference_designator)
        if parameters is None:
            message = 'Failed to get uframe parameters for reference designator %s, stream \'%s\'.' % \
                      (reference_designator, stream)
            raise Exception(message)
        parameter_dict = {}
        parameter_ids = []
        all_units = {}
        y_units = []
        x_units = []

        units_mapping = {}
        for each in parameters:
            parameter_dict[each['particleKey']] = each['id']
            all_units[each['particleKey']] = each['unit']

        if x_parameters:
            for each in x_parameters:
                str_each = str(each)
                if str_each in parameter_dict:
                    parameter_ids.append((parameter_dict[str_each]))
                if str_each in all_units:
                    x_units.append(all_units[str_each])
                if str_each in all_units:
                    units_mapping[str_each] = all_units[str_each]
        if y_parameters:
            for each in y_parameters:
                str_each = str(each)
                if str_each in parameter_dict:
                    parameter_ids.append(parameter_dict[str_each])
                if str_each in all_units:
                    y_units.append(all_units[str_each])
                if str_each in all_units:
                    units_mapping[str_each] = all_units[str_each]

        return parameter_ids, y_units, x_units, units_mapping
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe instrument metadata parameters.'
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe instrument metadata parameters.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def new_find_parameter_ids_stacked(reference_designator, stream, y_parameters, x_parameters, stacked=False):
    """
    Using stream parameters information from preload.
    Prepare list of x and y parameters by reference designator.
    {
      "display_name": "Seawater Conductivity",
      "id": "pd1",
      "name": "conductivity",
      "parameter_type": "quantity",
      "particleKey": "conductivity",
      "type": "float",
      "unit": "S m-1",
      "shape": "scalar"
    },
    """
    debug = False
    try:
        if debug: print '\n debug -- (new_find_parameter_ids_stacked) reference_designator: ', reference_designator
        parameters = get_stream_parameters(stream, reference_designator)
        if parameters is None:
            message = 'Failed to get uframe parameters for reference designator %s, stream \'%s\'.' % \
                      (reference_designator, stream)
            raise Exception(message)
        parameter_dict = {}
        parameter_ids = []
        all_units = {}
        y_units = []
        x_units = []
        parameter_names = []

        units_mapping = {}
        for each in parameters:
            parameter_dict[each['particleKey']] = each['id']
            all_units[each['particleKey']] = each['unit']

        if x_parameters:
            for each in x_parameters:
                str_each = str(each)
                if str_each in parameter_dict:
                    parameter_ids.append((parameter_dict[str_each]))
                    #parameter_names.append(each)
                if str_each in all_units:
                    x_units.append(all_units[str_each])
                if str_each in all_units:
                    units_mapping[str_each] = all_units[str_each]
        if y_parameters:
            for each in y_parameters:
                str_each = str(each)
                if str_each in parameter_dict:
                    parameter_ids.append(parameter_dict[str_each])
                    parameter_names.append(each)
                if str_each in all_units:
                    y_units.append(all_units[str_each])
                if str_each in all_units:
                    units_mapping[str_each] = all_units[str_each]

        # Specific check for ZPLSC plot requests.
        if stacked and 'ZPLSC' in reference_designator:

            # If ZPLSC and stacked, evaluate yfield to determine if contains 'zplsc_values', if so:
            # (1) determine the channel number
            # (2) get params for stream
            # (3) fetch parameter 'zplsc_depth_range_channel_#' for channel_number
            # (4) append parameter name to yfields list.

            if debug: print '\n debug -- ZPLSC in new_find_parameter_ids - STACKED is True! ********************'

            found_channel_number = False
            str_channel_number = None
            if y_parameters:
                for each in y_parameters:
                    str_each = str(each)
                    if debug: print '\n debug -- (y) str_each: ', str_each
                    if 'zplsc_values' in str_each:
                        if debug: print '\n debug -- Must lookup channel number in name...'
                        tmp_channel = each.rsplit('_', 1)
                        if debug: print '\n debug -- tmp_channel: ', tmp_channel
                        tmp_channel = tmp_channel[::-1]
                        _channel_number = tmp_channel[0]
                        if debug: print '\n debug -- _channel_number: %r' % _channel_number
                        str_channel_number = str(_channel_number)
                        if debug: print '\n debug -- str_channel_number: %r' % str_channel_number
                        if not str_channel_number:
                            message = 'Failed to process channel number for ZPLSC parameter %s.' % str_each
                            message += 'Unable to obtain the necessary parameter data for ZPLSC stacked plot request.'
                            raise Exception(message)
                        found_channel_number = True
                        break

            found_depth_parameter = False
            find_parameter = None
            if y_parameters and found_channel_number and str_channel_number is not None:
                find_parameter = '_'.join(['zplsc_depth_range_channel', str_channel_number])
                if debug: print '\n debug -- Looking to find parameter: ', find_parameter
                for each in parameters:
                    str_each = str(each['name'])
                    if debug: print '\n debug -- (y) parameter_name : ', str_each

                    if str_each == find_parameter:
                        if debug: print '\n debug -- Located parameter: %s' % find_parameter
                        if str_each in parameter_dict:
                            parameter_ids.append(parameter_dict[str_each])
                            parameter_names.append(each['particleKey'])
                        if str_each in all_units:
                            y_units.append(all_units[str_each])
                        if str_each in all_units:
                            units_mapping[str_each] = all_units[str_each]
                        found_depth_parameter = True
                        break
            if not found_depth_parameter or find_parameter is None:
                message = 'Failed to obtain depth range parameter for ZPLSC parameter %s.' % find_parameter
                message += ' Unable to obtain the necessary parameter data for ZPLSC stacked plot request.'
                raise Exception(message)

        return parameter_ids, y_units, x_units, units_mapping, parameter_names
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe instrument metadata parameters.'
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe instrument metadata parameters.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_multistream_data(instrument1, instrument2, stream1, stream2, var1, var2):
    from ooiservices.app.uframe.controller import get_uframe_multi_stream_contents
    debug = False
    try:
        rd_instrument1 = instrument1[:]
        rd_instrument2 = instrument2[:]
        mooring1, platform1, instrument1 = instrument1.split('-', 2)
        mooring2, platform2, instrument2 = instrument2.split('-', 2)

        # Process instrument 1
        if debug: print '\n debug -- instrument1: ', instrument1
        #stream_value1 = stream1[:]
        stream_type1, stream1 = stream1.split('_')
        stream1 = stream1.replace('-', '_')
        stream_type1 = stream_type1.replace('-', '_')

        # Process instrument 2
        if debug: print '\n debug -- instrument2: ', instrument2
        #stream_value2 = stream2[:]
        stream_type2, stream2 = stream2.split('_')
        stream2 = stream2.replace('-', '_')
        stream_type2 = stream_type2.replace('-', '_')

        parameter_ids1, y_units1, _, units_mapping1 = new_find_parameter_ids(rd_instrument1, stream1, [var1], [])
        parameter_ids2, y_units2, _, units_mapping2 = new_find_parameter_ids(rd_instrument2, stream2, [var2], [])
        units = units_mapping1.copy()
        units.update(units_mapping2)

        # Create stream dictionaries.
        stream1_dict = {}
        stream2_dict = {}

        # Populate reference designator(s), method(s), stream(s), and param(s) for both items.
        stream1_dict['refdes'] = rd_instrument1 # 'CP05MOAS-GL340-03-CTDGVM000'
        stream2_dict['refdes'] = rd_instrument2 # 'CP05MOAS-GL340-02-FLORTM000'
        stream1_dict['method'] = stream_type1
        stream2_dict['method'] = stream_type2
        stream1_dict['stream'] = stream1
        stream2_dict['stream'] = stream2
        stream1_dict['params'] = (parameter_ids1[0]).replace('pd', 'PD')
        stream2_dict['params'] = (parameter_ids2[0]).replace('pd', 'PD')

        # Get the start and end date for data request.
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            data, status_code = get_uframe_multi_stream_contents(stream1_dict, stream2_dict, st_date, ed_date)
            return data, units
        else:
            message = 'Define start and end dates.'
            raise Exception(message)

    except Exception as err:
        message = str(err)
        if debug: print '\n (data.py:get_multistream_data) Exception: %s' % message
        raise Exception(message)


def get_simple_data(stream, instrument, yfields, xfields, include_time=True):
    """ Get plotting data from uframe.
    """
    debug = False
    from ooiservices.app.uframe.controller import get_uframe_plot_contents_chunked_max_data
    try:
        if debug:
            print '\n debug -- Entered get_simple_data...'
        mooring, platform, sensor = instrument.split('-', 2)
        stream_value = stream[:]
        stream_type, stream = stream.split('_')
        stream = stream.replace('-', '_')
        stream_type = stream_type.replace('-', '_')
        if debug:
            print '\n stream_value: ', stream_value
            print '\n stream: ', stream
            print '\n stream_type: ', stream_type
            print '\n instrument: ', instrument
            print '\n yfields: ', yfields
        parameter_ids, y_units, x_units, units_mapping = new_find_parameter_ids(instrument, stream, yfields, xfields)

        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            if not st_date or st_date is None or not ed_date or ed_date is None or \
                            len(st_date) == 0 or len(ed_date) == 0:
                message = 'Define start and end dates, one or both are empty or null.'
                raise Exception(message)

            # Get the execDPA setting for data request.
            if 'dpa_flag' in request.args:
                dpa_flag = to_bool_str(request.args['dpa_flag'])
            else:
                dpa_flag = '0'

            # Get uframe data and check return code.
            data, status_code, query_url = get_uframe_plot_contents_chunked_max_data(mooring, platform, sensor,
                                                                          stream_type, stream,
                                                                          st_date, ed_date, dpa_flag, parameter_ids)
            if status_code != 200:
                message = 'Failed to get uframe plot contents chunked. Status code: ', status_code
                raise Exception(message)
            return data, units_mapping, query_url
        else:
            message = 'Define start and end dates.'
            raise Exception(message)

    except Exception as err:
        message = str(err)
        if debug: print '\n (data.py:get_simple_data) Exception: %s' % message
        raise Exception(message)


def get_data(stream, instrument, yfields, xfields, include_time=True):
    """ Get plotting data from uframe.
    """
    from ooiservices.app.uframe.controller import get_uframe_plot_contents_chunked_max_data
    debug = False
    data = []
    try:
        if debug: print '\n debug -- Entered get_data........................................'
        if debug: print '\n debug -- Step 1 -- have data, review data......'
        mooring, platform, sensor = instrument.split('-', 2)
        stream_value = stream[:]
        stream_type, stream = stream.split('_')
        stream = stream.replace('-', '_')
        stream_type = stream_type.replace('-', '_')
        if debug:
            print '\n stream_value: ', stream_value
            print '\n stream_type: ', stream_type
            print '\n stream: ', stream
            print '\n instrument: ', instrument
        parameter_ids, y_units, x_units, units_mapping = new_find_parameter_ids(instrument, stream, yfields, xfields)

        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            if 'dpa_flag' in request.args:
                dpa_flag = to_bool_str(request.args['dpa_flag'])
            else:
                dpa_flag = "0"

            data, status_code, query_url = get_uframe_plot_contents_chunked_max_data(mooring, platform, sensor, stream_type,
                                                                 stream, st_date, ed_date, dpa_flag, parameter_ids)
            if status_code != 200:
                message = 'Failed to get data from uframe, status code: %d' % status_code
                if data is not None:
                    if debug: print '\n debug -- get_data: data: ', data
                raise Exception(message)
            if not data or data is None:
                message = 'No data returned for stream %s and instrument %s.' % (stream[0], instrument[0])
                raise Exception(message)
        else:
            message = 'Please define start and end dates.'
            raise Exception(message)

    except Exception as err:
        message = str(err)
        raise Exception(message)

    if debug: print '\n debug -- Step 2 -- have data?, review data......'
    try:
        if data is None or not data or len(data) == 0:
            raise Exception('No Data Available')

        if "pk" not in data[0]:
            message = 'Primary information (pk) not available.'
            raise Exception(message)

        for xfield in xfields:
            if xfield == 'time':
                if "time" not in data[0]:
                    message = 'Time variable not available for x field.'
                    raise Exception(message)
            else:
                if xfield not in data[0]:
                    message = 'Requested data (%s) not available' % xfield
                    raise Exception(message)

        for yfield in yfields:
            if yfield == 'time':
                if "time" not in data[0]:
                    message = 'Time variable not available for y field.'
                    raise Exception(message)
            else:
                if yfield not in data[0]:
                    message = 'Requested data (%s) not available' % yfield
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
                            qaqc[xfield].append(int(row[key]))
                        #else:
                        #    current_app.logger.exception('QAQC not found for {0}'.format(xfield))
                # y
                for yfield in yfields:
                    if yfield == 'time':
                        y[yfield].append(float(row['time']))
                    else:
                        y[yfield].append(row[yfield])
                        key = yfield + '_qc_results'
                        if key in row:
                            qaqc[yfield].append(int(row[key]))
                        #else:
                        #    current_app.logger.exception('QAQC not found for {0}'.format(yfield))

        if debug: print '\n debug -- Step 3 -- have data, prepare resp_data......'
        # Generate response data dictionary.
        resp_data = {'x': x,
                     'y': y,
                     'data_length': len(data),
                     'x_field': xfields,
                     'x_units': x_units,
                     'y_field': yfields,
                     'y_units': y_units,
                     'dt_units': 'seconds since 1900-01-01 00:00:00',
                     'qaqc': qaqc,
                     'query_url': query_url
                     }

        return resp_data
    except Exception as err:
        message = str(err.message)
        raise Exception(message)

