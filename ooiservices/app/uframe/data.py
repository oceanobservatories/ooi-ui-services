#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

from flask import request, current_app
from collections import OrderedDict
from ooiservices.app.uframe.common_tools import to_bool_str, dump_dict
from ooiservices.app.uframe.uframe_tools import uframe_get_instrument_metadata_parameters
from ooiservices.app.uframe.stream_tools import get_stream_parameters
from requests.exceptions import (ConnectionError, Timeout)
__author__ = 'Andy Bird'


COSMO_CONSTANT = 2208988800


def find_parameter_ids(mooring, platform, instrument, y_parameters, x_parameters):
    """
    Using uframe instrument metadata, prepare list of x and y parameters by reference designator.
    Deprecate: This should be using the stream parameters functions and not instrument metadata.
    """
    debug = False
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
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe instrument metadata parameters.'
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe instrument metadata parameters.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- (data.py:find_parameter_ids) Exception: %s' % message
        raise Exception(message)


def new_find_parameter_ids(reference_designator, stream, y_parameters, x_parameters):
    """
    Using stream parameters functions from preload (not uframe instrument metadata).
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
        parameters = get_stream_parameters(stream, reference_designator)
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
        if debug: print '\n debug -- (data.py:find_parameter_ids) Exception: %s' % message
        raise Exception(message)


#def get_multistream_data(stream1, stream2, instrument1, instrument2, var1, var2):
def get_multistream_data(instrument1, instrument2, stream1, stream2, var1, var2):
    from ooiservices.app.uframe.controller import get_uframe_multi_stream_contents
    debug = False
    from ooiservices.app.uframe.common_tools import dump_dict
    try:
        rd_instrument1 = instrument1[:]
        rd_instrument2 = instrument2[:]
        if debug:
            print '\n debug -- Entered get_multistream_data.................'
            print '\n debug -- instrument1: ', instrument1
            print '\n debug -- instrument2: ', instrument2
            print '\n debug -- rd_instrument1: ', rd_instrument1
            print '\n debug -- rd_instrument2: ', rd_instrument2
            print '\n debug -- stream1: ', stream1
            print '\n debug -- stream2: ', stream2


        if debug: print '\n debug -- instrument1: ', instrument1
        mooring1, platform1, instrument1 = instrument1.split('-', 2)
        if debug: print '\n debug -- instrument2: ', instrument2
        mooring2, platform2, instrument2 = instrument2.split('-', 2)

        # Process instrument 1
        if debug: print '\n debug -- instrument1: ', instrument1
        stream_value1 = stream1[:]
        stream_type1, stream1 = stream1.split('_')
        stream1 = stream1.replace('-', '_')
        stream_type1 = stream_type1.replace('-', '_')
        if debug:
            print '\n stream1: ', stream1
            print '\n stream_value1: ', stream_value1
            print '\n stream_type1: ', stream_type1

        # Process instrument 2
        if debug: print '\n debug -- instrument2: ', instrument2
        stream_value2 = stream2[:]
        stream_type2, stream2 = stream2.split('_')
        stream2 = stream2.replace('-', '_')
        stream_type2 = stream_type2.replace('-', '_')
        if debug:
            print '\n stream2: ', stream2
            print '\n stream_value2: ', stream_value2
            print '\n stream_type2: ', stream_type2

        if debug: print '\n debug ------ calling new_find_parameter_ids...rd_instrument1: ', rd_instrument1
        parameter_ids1, y_units1, _, units_mapping1 = new_find_parameter_ids(rd_instrument1, stream1, [var1], [])
        if debug: print '\n debug -- stream1 (%s) parameter_ids1(%d): %s' % (stream1, len(parameter_ids1), parameter_ids1)

        if debug: print '\n debug ------ calling new_find_parameter_ids...rd_instrument2: ', rd_instrument2
        parameter_ids2, y_units2, _, units_mapping2 = new_find_parameter_ids(rd_instrument2, stream2, [var2], [])
        if debug: print '\n debug -- stream2 (%s) parameter_ids2(%d): %s' % (stream2, len(parameter_ids2), parameter_ids2)
        """
        parameter_ids1, y_units1, _, units_mapping1 = find_parameter_ids(mooring1, platform1, instrument1, [var1], [])
        parameter_ids2, y_units2, _, units_mapping2 = find_parameter_ids(mooring2, platform2, instrument2, [var2], [])
        """
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
        if debug:
            print '\n debug -- stream1_dict: =================================='
            dump_dict(stream1_dict, debug)
            print '\n debug -- stream2_dict: =================================='
            dump_dict(stream2_dict, debug)

        # Get the start and end date for data request.
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            data, status_code = get_uframe_multi_stream_contents(stream1_dict, stream2_dict, st_date, ed_date)
            if debug:
                print '\n debug -- status code from controller get_uframe_multi_stream_content is 200 !!'
                print '\n debug -- data from multistream: '
            return data, units
        else:
            message = 'Define start and end dates.'
            raise Exception(message)

    except Exception as err:
        message = str(err)
        if debug: print '\n (data.py:get_multistream_data) Exception: %s' % message
        current_app.logger.exception(message)
        raise Exception(message)


def get_simple_data(stream, instrument, yfields, xfields, include_time=True):
    """ Get 'simple' data from uframe (using get_uframe_plot_contents_chunked).
    """
    debug = False
    from ooiservices.app.uframe.controller import get_uframe_plot_contents_chunked
    try:
        if debug:
            print '\n debug -- Entered get_simple_data...'
        mooring, platform, instrument = instrument.split('-', 2)
        stream_value = stream[:]
        stream_type, stream = stream.split('_')
        stream = stream.replace('-', '_')
        stream_type = stream_type.replace('-', '_')
        if debug:
            print '\n stream_value: ', stream_value
            print '\n stream: ', stream
            print '\n stream_type: ', stream_type
        parameter_ids, y_units, x_units, units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)

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

            if debug:
                print '\n debug -- Calling get_uframe_plot_contents_chunked...'
            # data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                                                 st_date, ed_date, dpa_flag, parameter_ids)
            if debug:
                print '\n debug -- After calling get_uframe_plot_contents_chunked...'
                print '\n debug -- status_code: ', status_code
            if status_code != 200:
                message = 'Failed to get uframe plot contents chunked. Status code: ', status_code
                raise Exception(message)
            return data, units_mapping
        else:
            message = 'Define start and end dates.'
            raise Exception(message)

    except Exception as err:
        message = str(err)
        if debug: print '\n (data.py:get_simple_data) Exception: %s' % message
        current_app.logger.exception(message)
        raise Exception(message)


def get_data(stream, instrument, yfields, xfields, include_time=True):
    """ Get data from uframe using get_uframe_plot_contents_chunked.
    """
    from ooiservices.app.uframe.controller import get_uframe_plot_contents_chunked
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
        parameter_ids, y_units, x_units, units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)

        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
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
                current_app.logger.exception(message)
                raise Exception(message)
        else:
            message = 'Please define start and end dates.'
            current_app.logger.exception(message)
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
            current_app.logger.exception(message)
            raise Exception(message)

        for xfield in xfields:
            if xfield == 'time':
                if "time" not in data[0]:
                    message = 'Time variable not available for x field.'
                    current_app.logger.exception(message)
                    raise Exception(message)
            else:
                if xfield not in data[0]:
                    message = 'Requested data (%s) not available' % xfield
                    current_app.logger.exception(message)
                    raise Exception(message)

        for yfield in yfields:
            if yfield == 'time':
                if "time" not in data[0]:
                    message = 'Time variable not available for y field.'
                    current_app.logger.exception(message)
                    raise Exception(message)
            else:
                if yfield not in data[0]:
                    message = 'Requested data (%s) not available' % yfield
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
                     'qaqc': qaqc
                     }

        return resp_data
    except Exception as err:
        message = str(err.message)
        if debug: print '\n (data.py:get_data) Exception: %s' % message
        #current_app.logger.exception(message)
        raise Exception(message)

