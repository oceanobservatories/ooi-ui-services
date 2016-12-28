#!/usr/bin/env python

"""
Support for uframe stream interface, functions utilized for stream information.
"""
__author__ = 'Edna Donoughe'

from flask import current_app, request                          # todo - remove flask dependencies from this file
from ooiservices.app import cache                               # todo - remove cache dependencies from this file
from ooiservices.app.uframe.uframe_tools import (uframe_get_stream_byname, uframe_get_instrument_metadata_parameters)
from ooiservices.app.uframe.toc_tools import process_uframe_toc
from ooiservices.app.uframe.vocab import (get_vocab_name_collection)

import datetime as dt
CACHE_TIMEOUT = 172800                                  # todo - remove cache dependencies from this file


def dfs_streams():
    """ Compile a list of streams from uframe data.
    """
    debug = False
    try:
        retval = []
        streams = []
        if debug: print '\n debug -- Entered dfs_streams...process_uframe_toc'
        toc = process_uframe_toc()
        if toc is None:
            message = 'The uframe toc response is empty, unable to return stream information.'
            if debug: print '\n debug -- no toc data returned...'
            raise Exception(message)
        if debug: print '\n debug -- After process_uframe_toc...'

        if debug: print '\n debug -- new stream processing...'
        """
        if stream_new_data():
            if debug: print '\n debug -- new stream processing...'
        else:
            if debug: print '\n debug -- original stream processing...'
        """

        # For each instrument, prepare parameters dictionary
        for instrument in toc:
            streams = new_data_streams_in_instrument(instrument, streams)
            """
            if stream_new_data():
                streams = new_data_streams_in_instrument(instrument, streams)
            else:
                parameters_dict = parameters_in_instrument(instrument['instrument_parameters'])
                streams = data_streams_in_instrument(instrument, parameters_dict, streams)
            """
        for stream in streams:
            try:
                data_dict = new_dict_from_stream(*stream)
                """
                if stream_new_data():
                    data_dict = new_dict_from_stream(*stream)
                else:
                    data_dict = dict_from_stream(*stream)
                """
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
                tmp_stream = str(data_stream['stream'])

                # Create stream tuple (order is important; used in  dict_from_stream)
                """
                stream = (
                        instrument['mooring_code'],
                        instrument['platform_code'],
                        instrument['instrument_code'],
                        data_stream['method'].replace("_","-"),
                        data_stream['stream'].replace("_","-"),
                        instrument['reference_designator'],
                        data_stream['beginTime'],
                        data_stream['endTime'],
                        parameters_dict[tmp_stream],
                        parameters_dict[tmp_stream+'_variable_type'],
                        parameters_dict[tmp_stream+'_units'],
                        parameters_dict[tmp_stream+'_variables_shape'],
                        parameters_dict[tmp_stream+'_pdId']
                        )

                """
                # Not required for displaying data catalog. Used for plotting parameter pull down lists.
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



# todo For processing parameter_display_names...
# todo Get parameter name from stream engine rest api.
def new_dict_from_stream(mooring, platform, instrument, stream_type, stream, reference_designator, beginTime, endTime):
    # variables, variable_type, units, variables_shape, parameter_id):
    """ Prepare a data dictionary from input data, where input data is constructed in data_streams_in_instrument.
    For processing stream_display_name...
        Create _stream which is valid stream value, but with hyphens replaced by '_'.
        Use _stream in database queries for stream name, i.e. get_stream_byname(_stream)
        if get_stream_byname provides null, return stream for stream_display_name (will have hyphens)

    Get stream display name from stream engine rest api.
    Get parameter information from stream engine api (todo).
    """
    from ooiservices.app.uframe.status_tools import get_rd_digests_dict
    warnings = False
    debug = False
    _stream = None
    try:

        # No checks, just create _stream (used in database queries for stream_display_name)
        if '-' in stream:
            _stream = stream.replace('-', '_')

        stream_name = '_'.join([stream_type, stream])
        ref = '-'.join([mooring, platform, instrument])
        data_dict = {}

        #=====================================
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

        if latitude is not None:
            latitude = round(latitude, 4)
        if longitude is not None:
            longitude = round(longitude, 4)
        data_dict['latitude'] = latitude
        data_dict['longitude'] = longitude
        data_dict['depth'] = depth
        data_dict['water_depth'] = water_depth
        #===============================


        #-------------------------------------
        # Added this attribute 2016-11-07, not required for data catalog view but should be considered.
        data_dict['stream'] = _stream
        #-------------------------------------
        data_dict['start'] = beginTime
        data_dict['end'] = endTime
        data_dict['reference_designator'] = reference_designator
        data_dict['stream_type'] = stream_type
        data_dict['stream_name'] = stream_name

        # --------------------------------------------- Not required for data catalog view
        """
        # Get stream_display_name using _stream (if not in database then use stream value provided (has hyphens)
        #print '\n debug -- dict_from_stream: stream: ', stream
        #print '\n debug -- dict_from_stream: _stream: ', _stream
        tmp = get_stream_name_by_stream(_stream)
        if tmp is None or not tmp:
            tmp = stream
        data_dict['stream_display_name'] = tmp
        """
        #---------------------------------------------- End not required for data catalog view.
        array, subsite, platform, sensor, long_display_name = get_vocab_name_collection(ref)
        #array, subsite, platform, sensor = get_vocab_name_collection(ref)
        data_dict['array_name'] = array
        data_dict['display_name'] = sensor
        data_dict['assembly_name'] = platform
        data_dict['site_name'] = subsite
        data_dict['platform_name'] = subsite
        data_dict['long_display_name'] = long_display_name

        # Get stream display name and processed parameters.
        tmp, parameters = get_stream_name_and_parameters(_stream)
        data_dict['stream_display_name'] = tmp #get_stream_name_by_stream(_stream)
        if not data_dict['stream_display_name'] or data_dict['stream_display_name'] is None or \
            len(data_dict['stream_display_name']) == 0:
            if debug: print '\n debug -- stream_display_name is None, use ', _stream
            data_dict['stream_display_name'] = _stream

        # Consider replacing with the actual stream name from the stream rest api. (data_dict['stream_display_name'])
        #data_dict['long_display_name'] = get_long_display_name_by_rd(ref)      # Even used for plotting? todo - remove
        #data_dict['long_display_name'] = data_dict['stream_display_name']       # todo - Check if ok!

        """
        if ref[:2] == 'RS':
            data_dict['array_name'] = get_rs_array_name_by_rd(ref[:8])
        else:
            data_dict['array_name'] = get_display_name_by_rd(ref[:2])
        data_dict['display_name'] = get_display_name_by_rd(ref)
        if data_dict['display_name'] is None:
            data_dict['display_name'] = reference_designator
        data_dict['assembly_name'] = get_display_name_by_rd(ref[:14])
        """
        #------------------------------------------------------------------- not required for data catalog
        """
        data_dict['site_name'] = get_display_name_by_rd(ref[:8])
        data_dict['long_display_name'] = get_long_display_name_by_rd(ref)
        data_dict['platform_name'] = get_display_name_by_rd(ref[:8])
        """
        #------------------------------------------------------------------- end not required for data catalog
        data_dict['download'] = {
                                 "csv" : "/".join(['api/uframe/get_csv', stream_name, ref]),
                                 "json" : "/".join(['api/uframe/get_json', stream_name, ref]),
                                 "netcdf" : "/".join(['api/uframe/get_netcdf', stream_name, ref]),
                                 "profile" : "/".join(['api/uframe/get_profiles', stream_name, ref])
                                }
        #------------------------------------- Not required for data catalog view
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
                variables_shapes.append(shape)                           # todo fix this ***************
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

        """
        data_dict['variables'] = variables
        data_dict['variable_type'] = variable_type
        data_dict['units'] = units
        data_dict['variables_shape'] = variables_shape
        data_dict['parameter_id'] = parameter_id
        display_names = []
        for variable in variables:
            # If no database entry for parameter variable, assign to variable provided
            tmp = get_parameter_name_by_parameter(variable)
            if tmp is None:
                tmp = variable
            display_names.append(tmp)

        data_dict['parameter_display_name'] = display_names
        """
        #--------------------------------------- End not required for data catalog view.

        return data_dict

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}

'''
# no longer used
def get_stream_name_by_stream(stream):
    """ Get stream name using database. (deprecate)
    http://uihost:4000/streams response:
    {
      "streams": [
        {
          "concatenated_name": " Ancillary System Data    ",
          "content": "Data",
          "data_type": "Engineering",
          "delivery_method": "Streamed",
          "id": 1,
          "stream": "adcp_ancillary_system_data",
          "stream_description": "Streamed Engineering Data"
        },
        {
          "concatenated_name": " Compass Calibration     ",
          "content": "Data",
          "data_type": "Calibration",
          "delivery_method": "Streamed",
          "id": 2,
          "stream": "adcp_compass_calibration",
          "stream_description": "Streamed Calibration Data"
        },
        . . .
      ]
    }

    Using rest api:
    request: http://host:12575/stream/byname/cg_cpm_eng_cpm_recovered
    response:
    {
          "name" : "cg_cpm_eng_cpm_recovered",
          "id" : 507,
          "time_parameter" : 7,
          "binsize_minutes" : 20160,
          "stream_type" : {
            "value" : "Engineering"
          },
          "stream_content" : {
            "value" : "CPM Controller Status Data"
          },
          "description" : null,
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
          . . .
          ],
          "dependencies" : [ ]
    }
    """
    debug = False
    try:
        if not stream or stream is None:
            return None
        stream_display_name = None
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            if debug: print '\n stream_contents is None for %s' % stream
            return None
        if 'stream_content' in stream_contents:
            if stream_contents['stream_content']:
                if 'value' in stream_contents['stream_content']:
                    stream_display_name = stream_contents['stream_content']['value']
        return stream_display_name
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None
'''
'''
# no longer used
def get_stream_parameters(stream):
    """
    Get stream parameters and process parameters.

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
    Return list as follows:
           parameters :
                   [
                      {'name' : name, display_name, id, unit, type, shape },
                      {'name' : name, display_name, id, unit, type, shape },
                      {'name' : name, display_name, id, unit, type, shape }
                   ]
    """
    debug = False
    parameters = []
    try:
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            if debug: print '\n stream_contents is None for %s' % stream
            return None
        if 'parameters' in stream_contents:
            if debug: print '\n\t-- Number of input parameters (%d)' % len(stream_contents['parameters'])
            if stream_contents['parameters']:
                for item in stream_contents['parameters']:
                    parameter = {}
                    name = None
                    if 'name' in item:
                        name = item['name']

                    # Populate parameter to dictionary
                    parameter['name'] = name
                    parameter['particleKey'] = name
                    if 'display_name' in item:
                        parameter['display_name'] = item['display_name']
                    parameter['id'] = None
                    if 'id' in item:
                        parameter['id'] = 'pd' + str(item['id'])
                    parameter['unit'] = None
                    if 'unit' in item:
                        if item['unit']:
                            if 'value' in item['unit']:
                                parameter['unit'] = item['unit']['value']
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
                    if parameter:
                        parameters.append(parameter)
        if not parameters:
            parameters = None
        if debug: print '\n\t-- Number of parameters in result: parameters: ', len(parameters)

        return parameters
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None
'''

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
        """
        if not rd or rd is None:
            return None
        if not stream or stream is None:
            return None
        """
        if not _parameters or _parameters is None:
            return None

        """
        metadata_dict = {}
        metadata = uframe_get_instrument_metadata_parameters(rd)
        if metadata:
            #if debug: print '\n debug -- Before -- len(metadata): ', len(metadata)
            metadata[:] = [item for item in metadata if not match_stream(stream, item)]
            #if debug: print '\n debug -- After -- len(metadata): ', len(metadata)
            for item in metadata:
                metadata_dict[(item['pdId']).lower()] = {'particleKey': item['particleKey'],
                                                         'fillValue': item['fillValue'],
                                                         'shape': (item['shape']).lower(),
                                                         'type': (item['type']).lower()}
        #if debug: print '\n debug -- metadata_dict keys(%d): %s' % (len(metadata_dict.keys()), metadata_dict.keys())
        """
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
        """
        else:
            #if debug: print '\n debug -- process metadata_dict...'
            for parameter in parameters:
                if parameter['id'] in metadata_dict:
                    parameter['shape'] = metadata_dict[parameter['id']]['shape']
                    parameter['type'] = metadata_dict[parameter['id']]['type']
                else:
                    if debug: print '\n Was unable to find %s %s parameter %s in metadata_dict.' % \
                                    (rd, stream, parameter['id'])

        #if debug: print '\n\t-- Number of parameters in result: parameters: ', len(parameters)
        """
        if debug_parameter_types:
            print '\n List of parameter_type values identified(%d): %s' % (len(parameter_types), parameter_types)
        return parameters
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None

"""
def match_stream(stream, item):
    #metadata[:] = [item for item in metadata if not match_stream(stream, item)]
    result = False
    if item:
        if 'stream' in item:
            if item['stream'] != stream:
                result = True
    return result
"""

'''
def process_parameters_dict(_parameters):
    """
    Process list of stream parameters and return dictionary keyed by parameter name.
    Returns dictionary:
    {
        "VOID_heading": {
          "display_name": "VOID Heading",
          "id": "pd563",
          "name": "VOID_heading",
          "parameter_type": "quantity",
          "particleKey": "VOID_heading",
          "type": "float",
          "unit": "degrees"
        },
        "VOID_pitch": {
          "display_name": "VOID Pitch",
          "id": "pd564",
          "name": "VOID_pitch",
          "parameter_type": "quantity",
          "particleKey": "VOID_pitch",
          "type": "float",
          "unit": "degrees"
        },
        . . .
    }


    Note Values of parameter types:
    List of parameter_type values identified(8):
        [u'quantity', u'boolean', u'function', u'array<quantity>', u'category<int8:str>',
         u'constant<str>', u'external', u'category<uint8:str>']

    """
    debug_parameter_types = False
    debug = False
    parameters = []
    parameter_types = []
    parameters_dict = {}        # dictionary keyed by parameter name
    try:
        if not _parameters or _parameters is None:
            return None

        for item in _parameters:
            parameter = {}
            name = None
            if 'name' in item:
                name = item['name']

            # Populate parameter in dictionary
            parameter['name'] = name
            parameter['particleKey'] = name
            if 'display_name' in item:
                parameter['display_name'] = item['display_name']
            parameter['id'] = None
            if 'id' in item:
                parameter['id'] = 'pd' + str(item['id'])
            parameter['unit'] = None
            if 'unit' in item:
                if item['unit']:
                    if 'value' in item['unit']:
                        parameter['unit'] = item['unit']['value']
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

            # Get 'parameter_type' attribute.
            parameter['parameter_type'] = item['parameter_type']['value']
            if debug_parameter_types:
                if parameter['parameter_type'] and parameter['parameter_type'] is not None:
                    if parameter['parameter_type'] not in parameter_types:
                        parameter_types.append(parameter['parameter_type'])
            if parameter:
                parameters.append(parameter)
        if not parameters:
            parameters = None
        else:
            for item in parameters:
                parameters_dict[item['name']] = item
        if debug: print '\n\t-- Number of parameters in result: parameters: ', len(parameters)
        if debug_parameter_types:
            print '\n List of parameter_type values identified(%d): %s' % (len(parameter_types), parameter_types)
        return parameters_dict
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None
'''


def get_stream_name_and_parameters(stream):
    """
    For a stream, return stream display name and all processed parameters.
    Get stream contents byname, get stream display name and process stream parameters.
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

        # Get stream parameters, return dictionary of processed parameters
        if 'parameters' in stream_contents:
            _parameters = stream_contents['parameters']
            parameters = process_stream_parameters(_parameters)

        return stream_display_name, parameters
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
            if debug: print '\n stream_contents is None for %s' % stream
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


#================================================================
#================================================================
#================================================================
#================================================================
# OLD STREAM FUNCTIONS - TO BE REMOVED.
#================================================================
#================================================================
#================================================================
#================================================================

'''

# todo - deprecate...
def get_stream_name_and_parameter_names(stream):
    """
    For a stream, return stream display name and a dictionary of parameter-name values (key is parameter).
    """
    debug = True
    parameters_dict = {}
    parameters = None
    try:
        # Get stream display name (byname)
        stream_display_name = None
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            if debug: print '\n stream_contents is None for %s' % stream
            return None, None
        if 'stream_content' in stream_contents:
            if stream_contents['stream_content']:
                if 'value' in stream_contents['stream_content']:
                    stream_display_name = stream_contents['stream_content']['value']

        # Get stream parameters, return dictionary of parameters
        if 'parameters' in stream_contents:
            parameters = stream_contents['parameters']
        if not parameters or parameters is None:
            if debug: print '\n parameters is None for %s' % stream
            return stream_display_name, None
        for parameter in parameters:
            if not parameter['name'] or len(parameter['name']) == 0 or parameter['name'] is None:
                continue
            if parameter['name'] not in parameters_dict:
                parameters_dict[parameter['name']] = parameter['display_name']
        return stream_display_name, parameters_dict
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None, None


def get_stream_parameters_raw(stream):
    """ Get parameters for a stream.
    """
    debug = True
    parameters = None
    try:
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            if debug: print '\n stream_contents is None for %s' % stream
            return None
        if 'parameters' in stream_contents:
            parameters = stream_contents['parameters']
        return parameters
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None


def get_stream_parameter_names(stream):
    """ Get parameters for a stream, build dictionary of parameter-name pairs.
    """
    debug = True
    parameters_dict = {}
    try:
        parameters = get_stream_parameters_raw(stream)
        if not parameters or parameters is None:
            if debug: print '\n parameters is None for %s' % stream
            return None
        for parameter in parameters:
            if not parameter['name'] or len(parameter['name']) == 0 or parameter['name'] is None:
                continue
            if parameter['name'] not in parameters_dict:
                parameters_dict[parameter['name']] = parameter['display_name']
        return parameters_dict
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None


# ========================================================================
# Database queries for stream and stream parameters
# ========================================================================

#todo - deprecate database StreamParameter call.
def get_parameter_name_by_parameter(stream_parameter_name):
    """ Get parameter name using database.
    """
    debug = True
    try:
        if debug: print '\n REMOVE ****************** Alert: Using StreamParameter from database - REMOVE ************'
        if stream_parameter_name is None:
            return None
        streamParameter = StreamParameter.query.filter_by(stream_parameter_name = stream_parameter_name).first()
        if streamParameter is None or streamParameter is []:
            if debug: print '[param] ', stream_parameter_name
            return None
        stream_display_name = streamParameter.standard_name
        return stream_display_name
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None

# todo - to be deprecated
def parameters_in_instrument(parameters):
    """ Process an instrument's parameters when parameter shape is 'scalar' or 'function'.
        "instrument_parameters": [
            {
              "fill_value": "-9999999",
              "particleKey": "time",
              "pdId": "PD7",
              "shape": "SCALAR",
              "stream": "cg_cpm_eng_cpm_recovered",
              "type": "DOUBLE",
              "units": "seconds since 1900-01-01",
              "unsigned": false
            },
            {
              "fill_value": "-9999999",
              "particleKey": "port_timestamp",
              "pdId": "PD10",
              "shape": "SCALAR",
              "stream": "cg_cpm_eng_cpm_recovered",
              "type": "DOUBLE",
              "units": "seconds since 1900-01-01",
              "unsigned": false
            },
    """
    parameters_dict = {}
    for parameter in parameters:
        if parameter['shape'].lower() in ['scalar', 'function']:
            tmp_stream = parameter['stream']
            if tmp_stream not in parameters_dict.iterkeys():
                parameters_dict[parameter['stream']] = []
                parameters_dict[parameter['stream']+'_variable_type'] = []
                parameters_dict[parameter['stream']+'_units'] = []
                parameters_dict[parameter['stream']+'_variables_shape'] = []
                parameters_dict[parameter['stream']+'_pdId'] = []

            parameters_dict[parameter['stream']].append(parameter['particleKey'])
            parameters_dict[parameter['stream']+'_variable_type'].append(parameter['type'].lower())
            parameters_dict[parameter['stream']+'_units'].append(parameter['units'])
            parameters_dict[parameter['stream']+'_variables_shape'].append(parameter['shape'].lower())
            parameters_dict[parameter['stream']+'_pdId'].append(parameter['pdId'].lower())
    return parameters_dict

# todo For processing parameter_display_names...
# todo Get parameter name from stream engine rest api.
def dict_from_stream(mooring, platform, instrument, stream_type, stream, reference_designator, beginTime, endTime,
                     variables, variable_type, units, variables_shape, parameter_id):
    """ Prepare a data dictionary from input data, where input data is constructed in data_streams_in_instrument.
    For processing stream_display_name...
        Create _stream which is valid stream value, but with hyphens replaced by '_'.
        Use _stream in database queries for stream name, i.e. get_stream_byname(_stream)
        if get_stream_byname provides null, return stream for stream_display_name (will have hyphens)

    Get stream display name from stream engine rest api.
    Get parameter information from stream engine api (todo).
    """
    _stream = None
    try:

        # No checks, just create _stream (used in database queries for stream_display_name)
        if '-' in stream:
            _stream = stream.replace('-', '_')

        stream_name = '_'.join([stream_type, stream])
        ref = '-'.join([mooring, platform, instrument])
        data_dict = {}

        #-------------------------------------
        # Added this attribute 2016-11-07, not required for data catalog view but should be considered.
        #data_dict['stream'] = _stream
        #-------------------------------------
        data_dict['start'] = beginTime
        data_dict['end'] = endTime
        data_dict['reference_designator'] = reference_designator
        data_dict['stream_type'] = stream_type
        data_dict['stream_name'] = stream_name

        # --------------------------------------------- Not required for data catalog view
        # Get stream_display_name using _stream (if not in database then use stream value provided (has hyphens)
        #print '\n debug -- dict_from_stream: stream: ', stream
        #print '\n debug -- dict_from_stream: _stream: ', _stream
        #tmp, parameter_names = get_stream_name_and_parameter_names(_stream)
        tmp = get_stream_name_by_stream(_stream)
        if tmp is None or not tmp:
            tmp = stream
        data_dict['stream_display_name'] = tmp
        #---------------------------------------------- End not required for data catalog view.

        if ref[:2] == 'RS':
            data_dict['array_name'] = get_rs_array_name_by_rd(ref[:8])
        else:
            data_dict['array_name'] = get_display_name_by_rd(ref[:2])
        data_dict['display_name'] = get_display_name_by_rd(ref)
        if data_dict['display_name'] is None:
            data_dict['display_name'] = reference_designator
        data_dict['assembly_name'] = get_display_name_by_rd(ref[:14])

        #------------------------------------------------------------------- not required for data catalog
        data_dict['site_name'] = get_display_name_by_rd(ref[:8])
        data_dict['long_display_name'] = get_long_display_name_by_rd(ref)
        data_dict['platform_name'] = get_display_name_by_rd(ref[:8])
        #------------------------------------------------------------------- end not required for data catalog
        data_dict['download'] = {
                                 "csv" : "/".join(['api/uframe/get_csv', stream_name, ref]),
                                 "json" : "/".join(['api/uframe/get_json', stream_name, ref]),
                                 "netcdf" : "/".join(['api/uframe/get_netcdf', stream_name, ref]),
                                 "profile" : "/".join(['api/uframe/get_profiles', stream_name, ref])
                                }
        #-------------------------------------
        # Not required for data catalog view
        data_dict['variables'] = []
        data_dict['variable_type'] = []
        data_dict['units'] = {}
        data_dict['variables_shape'] = []
        data_dict['variables'] = variables
        data_dict['variable_type'] = variable_type
        data_dict['units'] = units
        data_dict['variables_shape'] = variables_shape
        data_dict['parameter_id'] = parameter_id
        display_names = []
        for variable in variables:
            # If no database entry for parameter variable, assign to variable provided
            tmp = get_parameter_name_by_parameter(variable)
            if tmp is None:
                tmp = variable
            display_names.append(tmp)

        """
        #parameter_names = get_stream_parameter_names(_stream)
        if parameter_names and parameter_names is not None:
            for variable in variables:
                tmp = parameter_names[variable]
                if tmp is None:
                    tmp = variable
                display_names.append(tmp)
        """
        data_dict['parameter_display_name'] = display_names
        # End not required for data catalog view.
        #---------------------------------------

        return data_dict

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}




def data_streams_in_instrument(instrument, parameters_dict, streams):
    """ Format data tuples to be processing in function 'dict_from_stream'.
    """
    debug = False
    if debug: print '\n debug -- Number of instrument[streams]: ', len(instrument['streams'])
    for data_stream in instrument['streams']:
        try:
            if data_stream['stream'] and data_stream['stream'] is not None:
                tmp_stream = str(data_stream['stream'])
                #if parameters_dict:
                if tmp_stream not in parameters_dict:
                    print '\n Stream %s not in parameters_dict.' % tmp_stream
                    continue

                # Create stream tuple (order is important; used in  dict_from_stream)
                stream = (
                        instrument['mooring_code'],
                        instrument['platform_code'],
                        instrument['instrument_code'],
                        data_stream['method'].replace("_","-"),
                        data_stream['stream'].replace("_","-"),
                        instrument['reference_designator'],
                        data_stream['beginTime'],
                        data_stream['endTime'],
                        parameters_dict[tmp_stream],
                        parameters_dict[tmp_stream+'_variable_type'],
                        parameters_dict[tmp_stream+'_units'],
                        parameters_dict[tmp_stream+'_variables_shape'],
                        parameters_dict[tmp_stream+'_pdId']
                        )
                streams.append(stream)
        except KeyError as e:
            print '[data_streams_in_instrument] Error parsing stream on key: %s' % str(e)

    return streams
'''


'''
# Very heavy just to get one parameter display name, and requires stream and parameter.
# Alternative for plotting.py where plot_layout == 'stacked'
def get_parameter_name_by_parameter_stream(stream_parameter_name, stream):
    """ Get parameter name using stream rest api.
    """
    debug = True
    parameter_display_name = None
    try:
        if not stream or stream is None:
            return None
        if not stream_parameter_name or stream_parameter_name is None:
            return None

        # Get the stream
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            if debug: print '\n stream_contents is None for %s' % stream
            return None

        # Get the parameters for the stream.
        parameters = None
        if 'parameters' in stream_contents:
            parameters = stream_contents['parameters']
        if not parameters or parameters is None:
            if debug: print '\n stream parameters is None for stream %s' % stream
            return None

        # Get parameter display name.
        # review: If for a stream, there can be multiple parameters with the same attribute 'name',
        # then this loop must be refined by id.
        for parameter in parameters:
            if parameter['name'] == stream_parameter_name:
                parameter_display_name = parameter['display_name']
                break

        if debug: print '\n Get parameter (%s) name for stream %s: %s' % (stream_parameter_name, stream,
                                                                          parameter_display_name)
        return parameter_display_name
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return None

'''

