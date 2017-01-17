#!/usr/bin/env python

"""
Support for uframe stream interface, functions utilized for stream information.
"""
__author__ = 'Edna Donoughe'

from flask import current_app, request
from ooiservices.app import cache
from ooiservices.app.uframe.uframe_tools import uframe_get_stream_byname
from ooiservices.app.uframe.toc_tools import process_uframe_toc
from ooiservices.app.uframe.vocab import get_vocab_name_collection

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
    time = True
    try:
        stream_list_cached = cache.get('stream_list')
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
                cache.delete('stream_list')
                cache.set('stream_list', stream_list, timeout=CACHE_TIMEOUT)
                if time:
                    print 'Completed compiling stream list'
            else:
                message = 'stream_list failed to return value, error.'
                current_app.logger.info(message)
        else:
            stream_list = stream_list_cached
        return stream_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def new_data_streams_in_instrument(instrument, streams):
    """ Format data tuples to be processing in function 'dict_from_stream'.
    """
    count = 0
    for data_stream in instrument['streams']:
        try:
            if data_stream['stream'] and data_stream['stream'] is not None:

                if data_stream['beginTime'] == data_stream['endTime']:
                    message = 'Reference designator %s stream %s (%s) have equal start and end times.' % \
                              (instrument['reference_designator'], data_stream['stream'], data_stream['method'])
                    current_app.logger.info(message)
                    count += 1
                    #continue
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
        except Exception as err:
            message = 'Exception: %s' % str(err)
            current_app.logger.info(message)
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
    _stream = None
    try:
        # No checks, just create _stream.
        if '-' in stream:
            _stream = stream.replace('-', '_')
        stream_name = '_'.join([stream_method, stream])
        ref = '-'.join([mooring, platform, instrument])
        data_dict = {}

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Use deployment information from asset management.
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
            pass

        if latitude and latitude is not None:
            latitude = round(latitude, 5)
        if longitude and longitude is not None:
            longitude = round(longitude, 5)
        data_dict['latitude'] = latitude
        data_dict['longitude'] = longitude
        data_dict['depth'] = depth
        data_dict['water_depth'] = water_depth
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -

        data_dict['stream'] = _stream
        data_dict['start'] = beginTime
        data_dict['end'] = endTime
        data_dict['reference_designator'] = reference_designator
        data_dict['stream_type'] = stream_method        # Deprecate and use 'stream_method'
        data_dict['stream_method'] = stream_method
        data_dict['stream_name'] = stream_name

        # Get vocabulary items for response.
        array, subsite, platform, sensor, long_display_name = get_vocab_name_collection(ref)
        data_dict['array_name'] = array
        data_dict['display_name'] = sensor
        data_dict['assembly_name'] = platform
        data_dict['site_name'] = subsite
        data_dict['platform_name'] = subsite
        data_dict['long_display_name'] = long_display_name

        # Get stream type, stream display name dynamically.
        parameters = {}
        tmp, stream_dataset = get_stream_name_and_dataset(_stream)
        if tmp is None:
            message = 'Failed to get stream name for %s' % _stream
            raise Exception(message)

        data_dict['stream_dataset'] = stream_dataset
        data_dict['stream_display_name'] = tmp          # stream engine: 'stream_content'
        if not data_dict['stream_display_name'] or data_dict['stream_display_name'] is None or \
            len(data_dict['stream_display_name']) == 0:
            data_dict['stream_display_name'] = _stream

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
              "unit": "S m-1",
              "shape": "scalar"
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
    parameters = []
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
                if item['unit'] and item['unit'] is not None:
                    if 'value' in item['unit']:
                        if item['unit']['value'] is None:
                            parameter['unit'] = ''
                        else:
                            parameter['unit'] = item['unit']['value']
                else:
                    parameter['unit'] = ''

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

            if parameter:
                parameters.append(parameter)
        if not parameters:
            parameters = None
        return parameters
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_stream_name_and_dataset(stream):
    """
    For a stream, return stream display name and all processed parameters.
    Get stream contents byname, get stream display name and process stream parameters.
    Added stream_type (for searches filtered by Dataset Type).
    """
    stream_display_name = None
    stream_type = None
    try:
        # Get stream byname.
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            return None, None, None
        # Get stream display name ('stream_content')
        stream_display_name = stream
        if 'stream_content' in stream_contents:
            if stream_contents['stream_content']:
                if 'value' in stream_contents['stream_content']:
                    stream_display_name = stream_contents['stream_content']['value']
        # Get stream type. It reflects which dataset stream is categorized with.
        #(Instrument, Metadata, Engineering, Status)
        if 'stream_type' in stream_contents:
            if stream_contents['stream_type']:
                if 'value' in stream_contents['stream_type']:
                    stream_type = stream_contents['stream_type']['value']

        return stream_display_name, stream_type
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return stream_display_name, stream_type

# UI client call to obtain parameter information for reference designator, stream method and stream name.
def get_stream_for_stream_model(reference_designator, stream_method, stream):
    """ Get complete stream dictionary with legacy content, including parameters, for UI stream model.
    """
    try:
        # Get stream information from cache.
        _stream = None
        stream_list_cached = cache.get('stream_list')
        if stream_list_cached and stream_list_cached is not None and 'error' not in stream_list_cached:
            for item in stream_list_cached:
                if 'reference_designator' in item and 'stream' in item:
                    if item['reference_designator'] == reference_designator:
                        if item['stream_method'] == stream_method:
                            if item['stream'] == stream:
                                _stream = item
                                break

        if _stream is None:
            message = 'Failed to retrieve \'%s\' from \'stream_list\' cache.' % stream
            raise Exception(message)

        # Get [processed] parameters for stream
        parameters = get_stream_parameters(stream)
        if parameters is None:
            message = 'Failed to retrieve parameters for stream \'%s\'.' % stream
            raise Exception(message)

        # Add parameter information to stream dictionary.
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
                    shape = 'scalar'
                variables_shapes.append(shape)
                if not parameter['display_name'] or parameter['display_name'] is None:
                    parameter['display_name'] = parameter['name']
                if not parameter['unit'] or parameter['unit'] is None or len(parameter['unit']) == 0:
                    display_name = parameter['display_name']
                else:
                    display_name = parameter['display_name'] + '  (' + parameter['unit'] + ')'
                parameter_display_names.append(display_name)
                parameter_ids.append(parameter['id'])

        _stream['variables'] = variables
        _stream['variable_type'] = variable_types
        _stream['units'] = units
        _stream['variables_shape'] = variables_shapes
        _stream['parameter_display_name'] = parameter_display_names
        _stream['parameter_id'] = parameter_ids

        # Check
        if _stream is None:
            _stream = {}
        return _stream
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}


def get_stream_parameters(stream):
    """
    For a stream, return all processed parameters.
    Get stream contents byname, get and process all stream parameters.
    Return processed stream parameters.
    """
    parameters = None
    try:
        # Get stream byname.
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            return None
        if 'parameters' in stream_contents:
            _parameters = stream_contents['parameters']
            parameters = process_stream_parameters(_parameters)
        return parameters
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return parameters


# Used by binned pseudo and rose plotting functions.
def get_parameter_name_by_parameter_stream(stream_parameter_name, stream):
    """ Get parameter display name using stream rest api to get english name and units.
    (Used in plotting.py where plot_layout == 'stacked')
    """
    display_name = None
    try:
        # Check input parameters.
        if not stream or stream is None:
            return None
        if not stream_parameter_name or stream_parameter_name is None:
            return None

        # Get the stream by name.
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            return None
        # Get the parameters for the stream.
        parameters = None
        if 'parameters' in stream_contents:
            _parameters = stream_contents['parameters']
            parameters = process_stream_parameters(_parameters)
        if not parameters or parameters is None:
            return None

        # Get parameter display name using parameter name and units.
        for parameter in parameters:
            if parameter['name'] == stream_parameter_name:
                if not parameter['unit'] or parameter['unit'] is None or len(parameter['unit']) == 0:
                    print '\n Note: Parameter %s unit is null or empty.' % (str(parameter['display_name']))
                    display_name = str(parameter['display_name'])
                    break
                else:
                    display_name = str(parameter['display_name']) + '  (' + str(parameter['unit']) + ')'
                break
        return display_name
    except Exception as err:
        message = str(err)
        return None