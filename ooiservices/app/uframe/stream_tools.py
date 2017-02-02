#!/usr/bin/env python

"""
Support for uframe stream interface, functions utilized for stream information.
"""
__author__ = 'Edna Donoughe'

from flask import current_app, request
from ooiservices.app import cache
from ooiservices.app.uframe.config import get_cache_timeout
from ooiservices.app.uframe.toc_tools import process_uframe_toc
from ooiservices.app.uframe.config import (iris_enabled, get_iris_base_url, rds_enabled, get_rds_base_url)
from ooiservices.app.uframe.stream_tools_iris import (get_iris_rds, build_iris_streams, get_iris_station)
from ooiservices.app.uframe.stream_tools_rds import (get_rds_rds, build_rds_streams, get_rds_suffix)
from ooiservices.app.uframe.uframe_tools import (uframe_get_stream_byname, uframe_get_instrument_metadata_parameters)
from ooiservices.app.uframe.vocab import (get_vocab, get_display_name_by_rd, get_rs_array_name_by_rd,
                                          get_long_display_name_by_rd)
import datetime as dt


def dfs_streams():
    """ Compile a list of streams from uframe data.
    """
    from ooiservices.app.uframe.status_tools import get_rd_digests_dict
    debug = False
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

        # IRIS processing check.
        is_iris_enabled = False
        iris_rds = get_iris_rds()
        iris_base_url = get_iris_base_url()
        if iris_enabled():
            is_iris_enabled = True

        # RDS processing check.
        is_rds_enabled = False
        rds_rds = get_rds_rds()
        rds_base_url = get_rds_base_url()
        if rds_enabled():
            is_rds_enabled = True

        # Get reference dictionaries once.
        rd_digests_dict = get_rd_digests_dict()
        vocab_dict = get_vocab()

        # Process each stream.
        if debug: print '\n-- Processing streams...'
        for stream in streams:
            try:
                #data_dict = new_dict_from_stream(*stream)
                #- - - - - - - - - - - - - - - - - - - - - -
                mooring, platform, instrument, stream_method, stream, reference_designator, beginTime, endTime = stream
                rd = str(reference_designator)
                try:
                    # No checks, just create _stream.
                    if '-' in stream:
                        _stream = stream.replace('-', '_')
                    else:
                        _stream = stream
                    stream_name = '_'.join([stream_method, stream])
                    ref = '-'.join([mooring, platform, instrument])
                    data_dict = {}
                    data_dict['stream'] = _stream
                    data_dict['start'] = beginTime
                    data_dict['end'] = endTime
                    data_dict['reference_designator'] = reference_designator
                    data_dict['stream_type'] = stream_method        # Deprecate and use 'stream_method'
                    data_dict['stream_method'] = stream_method
                    data_dict['stream_name'] = stream_name

                    # Get stream type, stream display name dynamically.
                    tmp, stream_dataset = get_stream_name_and_dataset(_stream)
                    if tmp is None:
                        message = 'Failed to get stream name for %s' % _stream
                        raise Exception(message)
                    data_dict['stream_dataset'] = stream_dataset
                    data_dict['stream_display_name'] = tmp          # stream engine: 'stream_content'
                    if not data_dict['stream_display_name'] or data_dict['stream_display_name'] is None or \
                        len(data_dict['stream_display_name']) == 0:
                        data_dict['stream_display_name'] = _stream

                    # Get deployment information from asset management.
                    latitude, longitude, depth, water_depth = get_stream_deployment_info(ref, rd_digests_dict)
                    data_dict['latitude'] = latitude
                    data_dict['longitude'] = longitude
                    data_dict['depth'] = depth
                    data_dict['water_depth'] = water_depth

                    # Get vocabulary items for response.
                    #array, subsite, platform, sensor, long_display_name = get_vocab_name_collection(ref)
                    processing_rs = False
                    if rd[:2] == 'RS':
                        processing_rs = True
                    if not vocab_dict or vocab_dict is None:
                        array = rd[:2]
                        subsite = rd[:8]
                        platform = rd[:14]
                        sensor = rd
                        long_display_name = rd
                    else:
                        if not processing_rs:
                            array = get_display_name_by_rd(rd[:2])
                        else:
                            array = get_rs_array_name_by_rd(rd[:8])
                        subsite = get_display_name_by_rd(rd[:8])
                        platform = get_display_name_by_rd(rd[:14])
                        sensor = get_display_name_by_rd(rd)
                        long_display_name = get_long_display_name_by_rd(rd)
                    data_dict['array_name'] = array
                    data_dict['display_name'] = sensor
                    data_dict['assembly_name'] = platform
                    data_dict['site_name'] = subsite
                    data_dict['platform_name'] = subsite
                    data_dict['long_display_name'] = long_display_name

                    # If IRIS, process IRIS components
                    if is_iris_enabled:
                        if rd not in iris_rds:
                            data_dict['iris_enabled'] = False
                        else:
                            station = get_iris_station(rd)
                            if station is None:
                                data_dict['iris_enabled'] = False
                            else:
                                link = '/'.join([iris_base_url, station])
                                data_dict['iris_enabled'] = True
                                data_dict['iris_link'] = link

                    # If Raw Data Server, process components
                    if is_rds_enabled:
                        if rd not in rds_rds:
                            data_dict['rds_enabled'] = False
                        else:
                            suffix = get_rds_suffix(rd)
                            if suffix is None:
                                data_dict['rds_enabled'] = False
                            else:
                                link = '/'.join([rds_base_url, suffix])
                                data_dict['rds_enabled'] = True
                                data_dict['rds_link'] = link

                except Exception as err:
                    message = str(err)
                    current_app.logger.info(message)
                    continue
                #- - - - - - - - - - - - - - - - - - - - - -
            except Exception as err:
                message = 'Failed to process streams to dict; %s' % str(err)
                current_app.logger.exception(message)
                continue
            if request.args.get('reference_designator'):
                if request.args.get('reference_designator') != data_dict['reference_designator']:
                    continue
            if data_dict:
                retval.append(data_dict)

        #====================================
        # If IRIS enabled, update return val for IRIS
        if is_iris_enabled:
            # Make a list of IRIS streams to add to current list
            if debug: print '\n-- Build iris streams...'
            iris_streams = build_iris_streams()

            # Add new IRIS streams to stream list
            if iris_streams:
                if debug: print '\n-- Number of streams before IRIS: %d ...' % len(retval)
                retval = retval + iris_streams
                if debug: print '\n-- New IRIS streams: %s' % len(iris_streams)
                if debug: print '\n-- Number of streams with IRIS: %d ...' % len(retval)

        #====================================
        # If Raw Data Server enabled, update retval
        if is_rds_enabled:
            # Make a list of IRIS streams to add to current list
            if debug: print '\n-- Build rds streams...'
            rds_streams = build_rds_streams()

            # Add new IRIS streams to stream list
            if rds_streams:
                if debug: print '\n-- Number of streams before RDS: %d ...' % len(retval)
                retval = retval + rds_streams
                if debug: print '\n-- New RDS streams: %s' % len(rds_streams)
                if debug: print '\n-- Number of streams with RDS: %d ...' % len(retval)
        return retval
    except Exception as err:
        message = '[dfs_streams] Exception: %s' % str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get stream_list.
def get_stream_list(refresh=False):
    """ Get 'stream_list' from cache; if not cached, get and set cache.
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
                cache.set('stream_list', stream_list, timeout=get_cache_timeout())
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
    """ Format data tuples to be processing into stream dictionaries.
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
        except Exception as err:
            message = 'Exception: %s' % str(err)
            current_app.logger.info(message)
    return streams


def get_stream_deployment_info(rd, rd_digests_dict):
    """ For a reference designator, get deployment items required for stream dictionary.
    latitude, longitude, depth, waterDepth
    """
    latitude = None
    longitude = None
    depth = None
    water_depth = None
    try:
        if rd_digests_dict and rd_digests_dict is not None:
            if rd in rd_digests_dict:
                digest = rd_digests_dict[rd]
                if digest and digest is not None:
                    latitude = digest['latitude']
                    longitude = digest['longitude']
                    depth = digest['depth']
                    water_depth = digest['waterDepth']

            # Round to five decimal places is not None.
            if latitude and latitude is not None:
                latitude = round(latitude, 5)
            if longitude and longitude is not None:
                longitude = round(longitude, 5)
            if depth and depth is not None:
                depth = round(depth, 5)
            if water_depth and water_depth is not None:
                water_depth = round(water_depth, 5)

        return latitude, longitude, depth, water_depth
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}

def process_stream_parameters_no_shapes(_parameters):
    """
    Get stream parameters, return list of parameters in digest form; no shape or type.
    Returns list as follows:
        [
            {
              "display_name": "Seawater Conductivity",
              "id": "pd1",
              "name": "conductivity",
              "parameter_type": "quantity",
              "particleKey": "conductivity",
              "type": null,
              "unit": "S m-1",
              "shape": null
            },
            . . .
        ]
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

            parameter['type'] = None
            parameter['shape'] = None
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
    """ For a stream, return stream display name and all processed parameters.
    """
    stream_display_name = None
    stream_type = None
    try:
        # Get stream byname.
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            return None, None
        # Get stream display name ('stream_content')
        stream_display_name = stream
        if 'stream_content' in stream_contents:
            if stream_contents['stream_content']:
                if 'value' in stream_contents['stream_content']:
                    stream_display_name = stream_contents['stream_content']['value']
        # Get stream type, the dataset stream is categorized with.
        # (Instrument, Metadata, Engineering, Status, Calibration, Science)
        if 'stream_type' in stream_contents:
            if stream_contents['stream_type']:
                if 'value' in stream_contents['stream_type']:
                    stream_type = stream_contents['stream_type']['value']
        return stream_display_name, stream_type
    except Exception as err:
        message = str(err)
        #current_app.logger.info(message)
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
        parameters = get_stream_parameters(stream, reference_designator)    # changed
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
                    display_name = parameter['display_name'] + ' (' + parameter['unit'] + ')'
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


def get_stream_parameters(stream, reference_designator):
    """
    For a stream, return all processed parameters.
    Get stream contents byname, get, process and return all stream parameters.
    """
    debug = False
    parameters = None
    try:
        if debug:
            print '\n debug -- Entered get_stream_parameters...'
            print '\n debug -- input stream: %r' % stream
            print '\n debug -- input reference_designator: %r' % reference_designator
        # Get stream byname.
        stream_contents = uframe_get_stream_byname(stream)
        if not stream_contents or stream_contents is None:
            return None
        if 'parameters' in stream_contents:
            _parameters = stream_contents['parameters']
            metadata_parameters = uframe_get_instrument_metadata_parameters(reference_designator)
            parameters = process_stream_parameters(_parameters, stream, metadata_parameters)
        return parameters
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return parameters


# Used by plotting functions (binned pseudo and rose).
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
            parameters = process_stream_parameters_no_shapes(_parameters)
        if not parameters or parameters is None:
            return None

        # Get parameter display name using parameter name and units.
        for parameter in parameters:
            if parameter['name'] == stream_parameter_name:
                if not parameter['unit'] or parameter['unit'] is None or len(parameter['unit']) == 0:
                    #print '\n Note: Parameter %s unit is null or empty.' % (str(parameter['display_name']))
                    display_name = str(parameter['display_name'])
                    break
                else:
                    display_name = str(parameter['display_name']) + '  (' + str(parameter['unit']) + ')'
                break
        return display_name
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Helper function (high overhead) to provide stream display name (see function get_data_api in controller.py)
def get_stream_name_byname(stream):
    """
    For a stream, return stream display name. (This is overkill, refactor plotting requests.)
    """
    try:
        # Get stream display name.
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


def process_stream_parameters(_parameters, stream, metadata_parameters):
    """
    Get stream parameters, return list of parameters in digest form.
    (Using metadata for instrument to get shape and type; deprecate.)

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
    """
    debug = False
    parameters = []
    try:
        if not _parameters or _parameters is None:
            return None

        # Process parameters.
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

            # Getting parameter['type'] and parameter['shape'] from metadata.
            parameter['shape'] = None
            for mitem in metadata_parameters:
                if mitem['stream'] == stream:
                    if mitem['particleKey'] == name:
                        if (mitem['pdId']).replace('PD', '') == str(item['id']):
                            parameter['shape'] = (mitem['shape']).lower()
                            break
            if parameter['shape'] is None:
                message = 'Failed to identify parameter (\'%s\') shape in metadata for stream \'%s\'.' % (name, stream)
                current_app.logger.info(message)

            # Type processing
            type = None
            if 'value_encoding' in item:
                if 'value' in item['value_encoding']:
                    tmp_type = item['value_encoding']['value']
                    if tmp_type and tmp_type is not None:
                        if 'uint' in tmp_type:
                            type = 'uint'
                        elif 'int' in tmp_type:
                            type = 'int'
                        elif 'float' in tmp_type:
                            type = 'float'
                        elif 'double' in tmp_type:
                            type = 'double'
                        elif 'ubyte' in tmp_type:
                            type = 'ubyte'
                        elif 'byte' in tmp_type:
                            type = 'byte'
                        elif 'string' in tmp_type:
                            type = 'string'
                        else:
                            print '\n unaccounted for type: %s' % tmp_type
                            type = tmp_type
            parameter['type'] = type

            '''
            #====================================
            # Return once shape and type issues resolved with new dynamic parameters, namely ARRAY1D.
            # Type processing using new dynamic query for parameter information.
            type = None
            if 'value_encoding' in item:
                if 'value' in item['value_encoding']:
                    tmp_type = item['value_encoding']['value']
                    if tmp_type and tmp_type is not None:
                        type = tmp_type
            parameter['type'] = type

            # Get 'parameter_type' attribute (previously known as 'shape' in the metadata.)
            parameter['parameter_type'] = item['parameter_type']['value']
            if parameter['parameter_type'] and parameter['parameter_type'] is not None:
                if parameter['parameter_type'] == 'quantity':
                    parameter['shape'] = 'scalar'
                else:
                    parameter['shape'] = parameter['parameter_type']
            '''
            #====================================

            if parameter:
                parameters.append(parameter)
        if not parameters:
            parameters = None
        return parameters
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None