#!/usr/bin/env python

"""
Support for uframe stream interface, functions utilized for stream information.
"""
__author__ = 'Edna Donoughe'

from flask import current_app, request
from ooiservices.app import cache
from ooiservices.app.uframe.uframe_tools import (uframe_get_stream_byname, uframe_get_instrument_metadata_parameters)
from ooiservices.app.uframe.toc_tools import process_uframe_toc
from ooiservices.app.uframe.vocab import (get_vocab_name_collection)

import datetime as dt
CACHE_TIMEOUT = 172800


def dfs_streams():
    """ Compile a list of streams from uframe data.
    """
    try:
        retval = []
        streams = []
        toc = process_uframe_toc()
        if toc is None:
            message = 'The uframe toc response is empty, unable to return stream information.'
            raise Exception(message)

        # For each instrument, prepare parameters dictionary
        for instrument in toc:
            streams = new_data_streams_in_instrument(instrument, streams)

        for stream in streams:
            try:
                data_dict = new_dict_from_stream(*stream)
            except Exception as e:
                message = 'Failed to process streams to dict; %s' % e.message
                current_app.logger.exception(message)
                continue
            if request.args.get('reference_designator'):
                if request.args.get('reference_designator') != data_dict['reference_designator']:
                    continue
            if data_dict:
                retval.append(data_dict)
        return retval
    except Exception as err:
        message = '[dfs_streams] Exception: %s' % str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get stream_list.
def get_stream_list(refresh=False):
    """ [Used by verify_cache.] Get 'stream_list' from cache; if not cached, get and set cache.
    """
    debug = False
    time = True
    try:
        if debug: print '\n debug -- Entered get_stream_list, refresh: ', refresh
        stream_list_cached = cache.get('stream_list')
        if debug: print '\n debug -- after get stream_list cache...'
        if refresh or not stream_list_cached or stream_list_cached is None or 'error' in stream_list_cached:
            if time: print '\nCompiling stream list'
            try:
                start = dt.datetime.now()
                if time: print '\t-- Start time: ', start
                stream_list = dfs_streams()
                end = dt.datetime.now()
                if time:
                    print '\t-- End time:   ', end
                    print '\t-- Time to get stream list: %s' % str(end - start)
            except Exception as err:
                message = str(err)
                raise Exception(message)

            if stream_list and stream_list is not None:
                if debug: print '\n debug -- Removing stream_list cache...'
                cache.delete('stream_list')
                if debug: print '\n debug -- Reset stream_list cache...'
                cache.set('stream_list', stream_list, timeout=CACHE_TIMEOUT)
                if time:
                    print 'Completed compiling stream list'
            else:
                message = 'stream_list failed to return value, error.'
                current_app.logger.info(message)
        else:
            stream_list = stream_list_cached
        if debug: print '\n debug -- Exit get_stream_list...', len(stream_list)
        return stream_list

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def new_data_streams_in_instrument(instrument, streams):
    """ Format data tuples to be processing in function 'dict_from_stream'.
    """
    for data_stream in instrument['streams']:
        try:
            if data_stream['stream'] and data_stream['stream'] is not None:

                # Create stream tuple (order is important; used in  dict_from_stream)
                stream = (
                        instrument['mooring_code'],
                        instrument['platform_code'],
                        instrument['instrument_code'],
                        data_stream['method'].replace("_","-"),
                        data_stream['stream'].replace("_","-"),
                        instrument['reference_designator'],
                        data_stream['beginTime'],
                        data_stream['endTime']
                        )

                streams.append(stream)
        except KeyError as e:
            print '[data_streams_in_instrument] Error parsing stream on key: %s' % str(e)

    return streams


def new_dict_from_stream(mooring, platform, instrument, stream_method, stream, reference_designator, beginTime, endTime):
    # variables, variable_type, units, variables_shape, parameter_id):
    """ Prepare a data dictionary from input data, where input data is constructed in data_streams_in_instrument.
    For processing stream_display_name...
        Create _stream which is valid stream value, but with hyphens replaced by '_'.
        Use _stream in queries for stream name, i.e. get_stream_byname(_stream)
        if get_stream_byname provides null, return stream for stream_display_name (will have hyphens)
    Get stream display name from stream engine rest api.
    Get parameter information from stream engine api.
    """
    from ooiservices.app.uframe.status_tools import get_rd_digests_dict
    warnings = False
    debug = False
    _stream = None
    try:

        # No checks, just create _stream.
        if '-' in stream:
            _stream = stream.replace('-', '_')

        stream_name = '_'.join([stream_method, stream])
        ref = '-'.join([mooring, platform, instrument])
        data_dict = {}

        #== Use deployment information from asset management.
        latitude = None
        longitude = None
        depth = None
        water_depth = None
        try:
            rd_digests_dict = get_rd_digests_dict()
            if rd_digests_dict and rd_digests_dict is not None:
                if ref in rd_digests_dict:
                    digest = rd_digests_dict[ref]
                    if digest and digest is not None:
                        latitude = digest['latitude']
                        longitude = digest['longitude']
                        depth = digest['depth']
                        water_depth = digest['waterDepth']
        except Exception as err:
            message = str(err)
            if debug: print '\n debug -- (%s) error getting rd_digests_dict: %s' % (ref, message)
            pass

        if latitude and latitude is not None:
            latitude = round(latitude, 4)
        if longitude and longitude is not None:
            longitude = round(longitude, 4)
        data_dict['latitude'] = latitude
        data_dict['longitude'] = longitude
        data_dict['depth'] = depth
        data_dict['water_depth'] = water_depth
        #--

        data_dict['stream'] = _stream
        data_dict['start'] = beginTime
        data_dict['end'] = endTime
        data_dict['reference_designator'] = reference_designator
        data_dict['stream_type'] = stream_method        # Deprecate and use 'stream_method'
        data_dict['stream_method'] = stream_method
        data_dict['stream_name'] = stream_name

        array, subsite, platform, sensor, long_display_name = get_vocab_name_collection(ref)
        data_dict['array_name'] = array
        data_dict['display_name'] = sensor
        data_dict['assembly_name'] = platform
        data_dict['site_name'] = subsite
        data_dict['platform_name'] = subsite
        data_dict['long_display_name'] = long_display_name

        # Get stream type, stream display name and processed parameters.
        tmp, parameters, stream_dataset = get_stream_name_and_parameters(_stream)
        data_dict['stream_dataset'] = stream_dataset
        data_dict['stream_display_name'] = tmp          # Deprecate, use next line 'stream_content'
        #data_dict['stream_content'] = tmp
        if not data_dict['stream_display_name'] or data_dict['stream_display_name'] is None or \
            len(data_dict['stream_display_name']) == 0:
            if debug: print '\n debug -- stream_display_name is None, use ', _stream
            data_dict['stream_display_name'] = _stream

        data_dict['download'] = {
                                 "csv" : "/".join(['api/uframe/get_csv', stream_name, ref]),
                                 "json" : "/".join(['api/uframe/get_json', stream_name, ref]),
                                 "netcdf" : "/".join(['api/uframe/get_netcdf', stream_name, ref]),
                                 "profile" : "/".join(['api/uframe/get_profiles', stream_name, ref])
                                }
        variables = []
        variable_types = []
        units = []
        variables_shapes = []
        parameter_display_names = []
        parameter_ids = []
        if parameters and parameters is not None:
            for parameter in parameters:
                variables.append(parameter['name'])
                variable_types.append(parameter['type'])
                units.append(parameter['unit'])
                shape = parameter['shape']
                if not shape or shape is None or len(shape) == 0:
                    if debug: print '\n shape is null or empty for parameter %s ', parameter['name']
                    shape = 'scalar'
                variables_shapes.append(shape)
                if not parameter['display_name'] or parameter['display_name'] is None:
                    parameter['display_name'] = parameter['name']
                    if warnings:
                        message = 'Warning -- %s (stream: %s) display_name is null/empty, using: %s' % \
                                  (ref, _stream, parameter['name'])
                        current_app.logger.info(message)
                if not parameter['unit'] or parameter['unit'] is None or len(parameter['unit']) == 0:
                    if debug:
                        print '\n debug -- %s (%s) parameter %s unit is null or empty.' % \
                              (ref, _stream, parameter['display_name'])
                    display_name = parameter['display_name']
                else:
                    display_name = parameter['display_name'] + '  (' + parameter['unit'] + ')'
                parameter_display_names.append(display_name)
                parameter_ids.append(parameter['id'])

        data_dict['variables'] = variables
        data_dict['variable_type'] = variable_types
        data_dict['units'] = units
        data_dict['variables_shape'] = variables_shapes
        data_dict['parameter_display_name'] = parameter_display_names
        data_dict['parameter_id'] = parameter_ids

        return data_dict

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}


def process_stream_parameters(_parameters):
    """
    Get stream parameters, return list of parameters in digest form.
    (Consider using metadata for instrument to get shape and type.)

    Process list of stream parameters:
    "parameters" : [ {
        "name" : "time",
        "display_name" : "Time, UTC",
        "standard_name" : "time",
        "description" : "Time, UTC",
        "id" : 7,
        "data_product_identifier" : null,
        "precision" : 0,
        "fill_value" : {
          "value" : "-9999999"
        },
        "unit" : {
          "value" : "seconds since 1900-01-01"
        },
        "data_level" : null,
        "code_set" : null,
        "value_encoding" : {
          "value" : "float64"
        },
        "parameter_type" : {
          "value" : "quantity"
        },
        "parameter_function" : null,
        "data_product_type" : null,
        "dimensions" : [ ],
        "parameter_function_map" : null
      },

    Returns list as follows:
        [
            {
              "display_name": "Seawater Conductivity",
              "id": "pd1",
              "name": "conductivity",
              "parameter_type": "quantity",
              "particleKey": "conductivity",
              "type": "float",
              "unit": "S m-1"
            },

    Note Values of parameter types:  (currently using 'quantity' and calling it 'scalar' to fit with client code now.)
        INSERT INTO "parameter_type" VALUES(1,'array');
        INSERT INTO "parameter_type" VALUES(2,'array<>');
        INSERT INTO "parameter_type" VALUES(3,'array<quantity>');
        INSERT INTO "parameter_type" VALUES(4,'binary');
        INSERT INTO "parameter_type" VALUES(5,'boolean');
        INSERT INTO "parameter_type" VALUES(6,'category<int8:str>');
        INSERT INTO "parameter_type" VALUES(7,'category<uint8:str>');
        INSERT INTO "parameter_type" VALUES(8,'constant<str>');
        INSERT INTO "parameter_type" VALUES(9,'external');
        INSERT INTO "parameter_type" VALUES(10,'function');
        INSERT INTO "parameter_type" VALUES(11,'quantity');
        INSERT INTO "parameter_type" VALUES(12,'record<>');

        Anything with "array" in the name will be 2+ dimensions when retrieved
        (1 dimension for time, 1 or more dimensions for the data).

    """
    debug_parameter_types = False           # List all parameter types identified during processing.
    debug = False
    parameters = []
    parameter_types = []
    try:
        if not _parameters or _parameters is None:
            return None

        for item in _parameters:
            parameter = {}
            if 'name' in item:
                if item['name'] is None or not item['name'] or len(item['name']) == 0:
                    name = 'Unknown'
                else:
                    name = item['name']
            else:
                name = 'Unknown'
                if debug: print '\n debug -- parameter name is null, set to Unknown.'

            # Populate parameter in dictionary
            parameter['name'] = name
            parameter['particleKey'] = name
            if 'display_name' in item:
                parameter['display_name'] = item['display_name']
            else:
                parameter['display_name'] = name
            parameter['id'] = None
            if 'id' in item:
                parameter['id'] = 'pd' + str(item['id'])

            else:
                parameter['id'] = -1
            parameter['unit'] = None
            if 'unit' in item:
                if item['unit']:
                    if 'value' in item['unit']:
                        parameter['unit'] = item['unit']['value']

            # Type processing
            type = None
            if 'value_encoding' in item:
                if 'value' in item['value_encoding']:
                    tmp_type = item['value_encoding']['value']
                    if tmp_type and tmp_type is not None:
                        if 'int' in tmp_type:
                            type = 'int'
                        elif 'float' in tmp_type:
                            type = 'float'
                        elif 'double' in tmp_type:
                            type = 'double'
                        elif 'byte' in tmp_type:
                            type = 'byte'
                        elif 'string' in tmp_type:
                            type = 'string'
                        else:
                            print '\n unaccounted for type: %s' % tmp_type
                            type = tmp_type
            parameter['type'] = type

            # Get 'parameter_type' attribute (previously known as 'shape' in the metadata.)
            parameter['parameter_type'] = item['parameter_type']['value']
            if parameter['parameter_type'] and parameter['parameter_type'] is not None:
                if parameter['parameter_type'] == 'quantity':
                    parameter['shape'] = 'scalar'
                else:
                    parameter['shape'] = parameter['parameter_type']
            if debug_parameter_types:
                if parameter['parameter_type'] and parameter['parameter_type'] is not None:
                    if parameter['parameter_type'] not in parameter_types:
                        parameter_types.append(parameter['parameter_type'])

            if parameter:
                parameters.append(parameter)
        if not parameters:
            parameters = None
        if debug_parameter_types:
            print '\n List of parameter_type values identified(%d): %s' % (len(parameter_types), parameter_types)
        return parameters
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None


def get_stream_name_and_parameters(stream):
    """
    For a stream, return stream display name and all processed parameters.
    Get stream contents byname, get stream display name and process stream parameters.
    Added stream_type (for searches filtered by Dataset Type).
    """
    stream_display_name = None
    parameters = None
    try:
        # Get stream display name (byname)
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            return None, None

        stream_display_name = stream
        if 'stream_content' in stream_contents:
            if stream_contents['stream_content']:
                if 'value' in stream_contents['stream_content']:
                    stream_display_name = stream_contents['stream_content']['value']

        # Get stream type, reflects which dataset stream is categorized with.
        #(Instrument, Metadata, Engineering, Status)
        stream_type = None
        if 'stream_type' in stream_contents:
            if stream_contents['stream_type']:
                if 'value' in stream_contents['stream_type']:
                    stream_type = stream_contents['stream_type']['value']
        # Get stream parameters, return dictionary of processed parameters
        if 'parameters' in stream_contents:
            _parameters = stream_contents['parameters']
            parameters = process_stream_parameters(_parameters)

        return stream_display_name, parameters, stream_type
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return stream_display_name, parameters


# Helper function (high overhead) to provide stream display name (see function get_data_api in controller.py)
def get_stream_name_byname(stream):
    """
    For a stream, return stream display name. (This is overkill, refactor plotting requests.)
    """
    try:
        # Get stream display name (byname)
        stream_display_name = None
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            return None, None
        if 'stream_content' in stream_contents:
            if stream_contents['stream_content']:
                if 'value' in stream_contents['stream_content']:
                    stream_display_name = stream_contents['stream_content']['value']
        if stream_display_name is None:
            stream_display_name = stream
        return stream_display_name
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return stream
