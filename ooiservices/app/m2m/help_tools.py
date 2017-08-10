#!/usr/bin/env python

from flask import current_app
import json
import os

from ooiservices.app.m2m.help_data import get_help_data
from ooiservices.app.m2m.exceptions import InvalidPortException, InvalidPathException, \
    InvalidMethodException, InvalidScopeException

def get_m2m_ports():
    try:
        uframe_host = current_app.config['UFRAME_HOST']
        get_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS']
        post_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS_POST']
        put_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS_PUT']
        delete_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS_DELETE']
        return uframe_host, get_ports, post_ports, put_ports, delete_ports
    except Exception as err:
        message = 'Undefined configuration variable for m2m port selection; ' + str(err)
        raise Exception(message)


def build_url(path, request_method='GET', scope_names=None):
    """
    Given an M2M request path, build the corresponding uframe url.
    Verify permissions for port, request type and scope provided.
    Paths must conform to the following specification: <UFRAME PORT>/<UFRAME URL>
    """
    debug = False
    # Get configuration and request information.
    port, path, help_request = get_port_path_help(path)
    uframe_host, get_ports, post_ports, put_ports, delete_ports = get_m2m_ports()

    if debug:
        print '\n debug: uframe_host: ', uframe_host
        print '\n debug: request_method: ', request_method
    #- - - - - - - - - - - - - - - - - - - - - -
    # GET requests
    #- - - - - - - - - - - - - - - - - - - - - -
    if request_method == 'GET':
        # Verify the port is available for GET requests.
        if port not in get_ports:
            raise InvalidPortException(port)

    #- - - - - - - - - - - - - - - - - - - - - -
    # POST requests
    #- - - - - - - - - - - - - - - - - - - - - -
    elif request_method == 'POST':
        # Verify the port is available for POST requests.
        if port not in post_ports:
            raise InvalidMethodException(port, request_method)
        if port == 12580:
            if 'annotate' not in scope_names:
                raise InvalidScopeException(port, request_method)
        if port == 12589:
            if 'ingest' not in scope_names:
                raise InvalidScopeException(port, request_method)

    #- - - - - - - - - - - - - - - - - - - - - -
    # PUT requests
    #- - - - - - - - - - - - - - - - - - - - - -
    elif request_method == 'PUT':
        # Verify the port is available for PUT requests.
        if port not in put_ports:
            raise InvalidMethodException(port, request_method)

        # For each port available in put_ports, verify required permission for each port.
        # Annotations.
        if port == 12580:
            # Verify permission valid and available for user to perform request method.
            if 'annotate' not in scope_names:
                raise InvalidScopeException(port, request_method)
        # Ingestion.
        if port == 12589:
            # Verify permission valid and available for user to perform request method.
            if 'ingest' not in scope_names:
                raise InvalidScopeException(port, request_method)

    #- - - - - - - - - - - - - - - - - - - - - -
    # DELETE requests
    #- - - - - - - - - - - - - - - - - - - - - -
    elif request_method == 'DELETE':
        if debug: print '\n debug -- build_url delete....'
        # Verify the port is available for DELETE requests.
        if port not in delete_ports:
            raise InvalidMethodException(port, request_method)
        # Annotations.
        if port == 12580:
            if debug: print '\n debug -- build_url delete port ok...'
            # Verify permission valid and available for user to perform request method.
            if 'annotate' not in scope_names and 'annotate_admin' not in scope_names:
                raise InvalidScopeException(port, request_method)
    else:
        raise InvalidMethodException(port, request_method)

    base_url = 'http://%s:%d' % (uframe_host, port)
    return '/'.join((base_url, path))


#-----------------------------------------------
# Help requests
#-----------------------------------------------
def get_port_path_help(path):
    try:
        port, path = path.split('/', 1)
        port = int(port)
        help_request = False
        if 'help/' in path:
            help_request = True
            path = path.replace('help/', '')
        return port, path, help_request
    except ValueError:
        raise InvalidPathException(path)


def get_help(port, path, request_method, json_result=False, keyword=None):
    """ Get specific help information for a port, path and request type.
    """
    result = []
    separator = '\n==========\n'
    try:
        port_data = get_help_data(port, keyword)
        if json_result:
            return port_data
        if port_data:
            for item in port_data:
                if request_method is None:
                    result.append(item)
                #if item['method'] == request_method and item['endpoint'] in path:
                elif item['method'] == request_method and item['root'] in path:
                    result.append(item)
        results = ''
        if result:
            result = formatted_help(port, path, request_method, result)
            if len(result) > 0:
                if len(result) > 1:
                    for res in result:
                        results += separator
                        results += res + '\n'
                else:
                    results += result[0]
        return results
    except Exception as err:
        message = str(err)
        raise Exception(message)


def formatted_help(port, path, request_method, data):
    """ Process raw help data into human readable help output.
    """
    try:
        if not data:
            return None
        result = get_formatted_template(port, path, request_method, data)
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


#----------------------------------------------------------------------
# Data for help request (move to database with vocab like interface)
#----------------------------------------------------------------------
def get_formatted_template(port, path, request_method, data):
    m2m_root = 'http://host/api/m2m'
    try:
        uframe_host = current_app.config['UFRAME_HOST']
        base_url = 'http://%s:%d' % (uframe_host, port)
        url = '/'.join((base_url, path))
        results = []
        # If help data to be processed....
        if data is not None:
            for item in data:
                result = ''
                # Data description
                enhanced_endpoint = '/'.join([m2m_root, str(port), item['endpoint']])
                if item['description'] is not None:
                    result += 'M2M %s Request (Syntax): %s \n\nDescription: %s' % (item['method'],
                                                                                   enhanced_endpoint,
                                                                                   item['description'])
                else:
                    result += 'M2M %s Request (Syntax): %s \n\nDescription: None' % (item['method'],
                                                                                     enhanced_endpoint)
                # Data required
                if item['data_required']:
                    result += '\n\nData required for request: True'

                # Permission required
                if item['permission_required']:
                    result += '\n\nPermission required: True'

                # Data Format
                if item['data_format'] is not None:
                    result += '\n\nParameters: \n'
                    formatted__parameters = format_parameters(item['data_format'])
                    result += formatted__parameters

                # Process one or more samples if available (samples are optional)
                if 'samples' in item:
                    samples = item['samples']
                    for sample in samples:
                        # Sample Request (optional)
                        if 'sample_request' in sample:
                            if sample['sample_request']:
                                result += '\n\nSample Request: \n'
                                result += sample['sample_request']

                        # Sample Data (optional)
                        if 'sample_data' in sample:
                            if sample['sample_data']:
                                result += '\n\nSample Data: \n'
                                result += json.dumps(sample['sample_data'], indent=4, sort_keys=True)

                        # Sample Response (optional)
                        if 'sample_response' in sample:
                            if sample['sample_response']:
                                result += '\n\nSample Response: \n'
                                result += json.dumps(sample['sample_response'], indent=4, sort_keys=True)

                if result:
                    results.append(result)

        # If no help data...
        else:
            result = 'M2M %s Request: %s \n\nDescription: None' % (request_method, url)
            result += '\n\nNo help information available at this time.'
            results.append(result)
        return results
    except Exception as err:
        raise Exception(str(err))


def format_parameters(parameters):
    """ Returns a string of formatted parameters; 3 columns: Name, Data Type, and Description
    """
    result = None
    try:
        if parameters:
            result = ''
        template = "  {0:20}|{1:15}|{2:35}" # column widths: 20, 15, 35
        result += template.format("Name", "Data Type", "Description")   # header
        result += '\n'
        for item in parameters:
            if 'valid_values' in item and item['valid_values'] is not None:
                string_valid_values = ''
                for val in item['valid_values']:
                    string_valid_values += '\'' + val + '\', '
                string_valid_values = string_valid_values.strip(', ')
                tmp = item['description'] + ' (One of: ' + string_valid_values + ')'
                result += template.format(item['name'], item['type'], tmp)
            else:
                result += template.format(item['name'], item['type'], item['description'])
            result += '\n'
        return result
    except Exception as err:
        raise Exception(str(err))


#===========================================
# Read data from file
#===========================================
def read_store(filename):
    """ Open filename, read data, close file and return data.
    """
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    data_path = os.path.join(APP_ROOT, '..', '..', 'app', 'm2m', 'help')
    try:
        tmp = "/".join([data_path, filename])
        f = open(tmp, 'rb')
        data = f.read()
        f.close()
        return data
    except Exception, err:
        raise Exception('%s' % err.message)


def read_store2(filename):
    """ Open filename, read data and split on /r, close file and return data
    """
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    data_path = os.path.join(APP_ROOT, '..', '..', 'app', 'm2m', 'help')
    try:
        tmp = "/".join([data_path, filename])
        f = open(tmp, 'rb')
        line = f.read()
        data = line.split('\r')
        f.close()
    except Exception, err:
        raise Exception('%s' % err.message)
    return data


def json_get_help_file(port):
    results = ''
    if port is None:
        port = 'general'
    filename = "_".join(['help', port])
    try:
        data = read_store2(filename)
        for line in data:
            results += line + '\n'
        return results
    except:
        return None
