#!/usr/bin/env python

import requests

from flask import Response
from flask import current_app, jsonify
from flask import request
from requests.exceptions import ConnectionError, Timeout
from werkzeug.datastructures import MultiDict
from ooiservices.app.m2m import m2m as api
from ooiservices.app.models import User

import json
import os

from ooiservices.app.m2m.help_data import get_help_data
from ooiservices.app.m2m.exceptions import InvalidPortException, InvalidPathException, \
    InvalidMethodException, InvalidScopeException


def build_url(path, request_method='GET', scope_names=None):
    """
    Given an M2M request path, build the corresponding UFrame URL
    Paths must conform to the following specification:
    <UFRAME PORT>/<UFRAME URL>
    :param path: input path
    :return: URL
    """
    debug = False
    """
    try:
        port, path = path.split('/', 1)
        port = int(port)

        help_request = False
        if 'help/' in path:
            help_request = True
            path = path.replace('help/', '')

    except ValueError:
        raise InvalidPathException(path)
    """
    port, path, help_request = get_port_path_help(path)
    if debug:
        print '\n debug -- port: ', port
        print '\n debug -- path: ', path
        print '\n debug -- help_request: ', help_request
    if help_request:
        if debug: print '\n debug -- Help was requested for (%s) %s...' % (request_method, path)

    uframe_host = current_app.config['UFRAME_HOST']
    allowed_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS']
    post_allowed_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS_POST']
    put_allowed_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS_PUT']
    if request_method == 'GET':
        if port not in allowed_ports:
            raise InvalidPortException(port)
    elif request_method == 'POST':
        if port not in post_allowed_ports:
            raise InvalidMethodException(port, request_method)
        if port == 12580:
            if 'annotate' not in scope_names:
                raise InvalidScopeException(port, request_method)
    elif request_method == 'PUT':
        if port not in put_allowed_ports:
            raise InvalidMethodException(port, request_method)
        if port == 12580:
            if 'annotate' not in scope_names:
                raise InvalidScopeException(port, request_method)
    else:
        raise InvalidMethodException(port, request_method)

    base_url = 'http://%s:%d' % (uframe_host, port)
    return '/'.join((base_url, path))


#-----------------------------------------------
# Help requests
#-----------------------------------------------
def get_port_path_help(path):
    debug = False
    try:
        if debug:
            print '\n debug -- entered get_port_path_help...'
            print '\n debug -- path: ', path
        port, path = path.split('/', 1)
        port = int(port)

        if debug:
            print '\n debug -- entered get_port_path_help...'
            print '\n debug -- port: ', port
            print '\n debug -- path: ', path

        help_request = False
        if 'help/' in path:
            if debug: print '\n debug -- this is a help request...'
            help_request = True
            path = path.replace('help/', '')
        return port, path, help_request
    except ValueError:
        print '\n debug -- Exception (get_port_path_help): ', path
        raise InvalidPathException(path)


def get_help(port, path, request_method, json_result=False):
    """ Get specific help information for a port, path and request type.
    """
    debug = False
    result = []
    separator = '\n==========\n'
    try:
        if debug:
            print '\n debug -- Help request...'
            print '\n debug -- port: ', port
            print '\n debug -- path: ', path
            print '\n debug -- request_method: ', request_method

        port_data = get_help_data(port)
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
                    if debug: print '\n debug ***** result: %r' % result
                    results += result[0]

        return results

    except Exception as err:
        message = str(err)
        print '\n debug -- Exception (get_help): ', message
        raise Exception(message)


def formatted_help(port, path, request_method, data):
    """
    Process raw help data into human readable help output.
    """
    debug = False
    if debug:
        print '\n debug -- formatted_help entered...'
        print '\n debug -- port: ', port
        print '\n debug -- path: ', path
        print '\n debug -- request_method: ', request_method

    try:
        if not data:
            return None
        if debug: print '\n data(%d): %s' % (len(data), data)
        result = get_formatted_template(port, path, request_method, data)
        return result

    except Exception as err:
        message = str(err)
        print '\n debug -- Exception (formatted_help): ', message
        raise Exception(message)


#----------------------------------------------------------------------
# Data for help request (move to database with vocab like interface)
#----------------------------------------------------------------------
def get_formatted_template(port, path, request_method, data):
    debug = False
    separator = '\n=====\n'
    m2m_root = 'http://host/api/m2m'
    try:
        if debug: print '\n debug -- get_formatted_template entered...'
        uframe_host = current_app.config['UFRAME_HOST']
        base_url = 'http://%s:%d' % (uframe_host, port)
        url =  '/'.join((base_url, path))
        if debug:
            print '\n debug -- uframe_host: ', uframe_host
            print '\n debug -- base_url: ', base_url
            print '\n debug -- url: ', url

        results = []
        # If help data to be processed....
        if data is not None:
            for item in data:
                result = ''
                # Data description
                #enhanced_endpoint = 'http://ui-server-address/api/m2m/%s/%s' % (port, item['endpoint'])
                enhanced_endpoint = '/'.join([m2m_root, str(port), item['endpoint']])
                if debug: print '\n debug -- enhanced_endpoint: ', enhanced_endpoint
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
                    #formatted__parameters = format_parameters(item['data_format'])
                    #result += '\n\nParameters: \n\tName\t\t\tData Type\tDescription'
                    result += '\n\nParameters: \n'
                    formatted__parameters = format_parameters(item['data_format'])
                    result += formatted__parameters

                # Sample Request (optional)
                if 'sample_request' in item:
                    if item['sample_request']:
                        result += '\n\nSample Request: \n'
                        result += item['sample_request']
                        #result += json.dumps(item['sample_request'], indent=4, sort_keys=True)

                # Sample Data (optional)
                if 'sample_data' in item:
                    if item['sample_data']:
                        result += '\n\nSample Data: \n'
                        result += json.dumps(item['sample_data'], indent=4, sort_keys=True)

                # Sample Response (optional)
                if 'sample_response' in item:
                    if item['sample_response']:
                        result += '\n\nSample Response: \n'
                        result += json.dumps(item['sample_response'], indent=4, sort_keys=True)

                if result:
                    results.append(result)

        # If no help data...
        else:
            result = 'M2M %s Request: %s \n\nDescription: None' % (request_method, url)
            result += '\n\nNo help information available at this time.'
            #results = result
            results.append(result)
        if debug: print '\n debug -- Returning results(%d): %s' % (len(results), results)
        return results
    except Exception as err:
        raise Exception(str(err))


def format_parameters(parameters):
    """
    Returns a string of formatted parameters; 3 columns: Name, Data Type, and Description
    """
    result = None
    try:
        if parameters:
            result = ''
        #---
        template = "  {0:20}|{1:15}|{2:35}" # column widths: 20, 15, 35
        result += template.format("Name", "Data Type", "Description")# header
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
        #---
        #for item in parameters:
        #    result += '\n\t%s\t\t\t%s\t\t%s' % (item['name'], item['type'], item['description'])
        return result
    except Exception as err:
        raise Exception(str(err))

#===========================================
# Read data from file
#===========================================
def read_store(filename):
    """
    Open filename, read data, close file and return data
    """
    debug = True
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    data_path = os.path.join(APP_ROOT, '..', '..', 'app', 'm2m', 'help')
    if debug: print '\n debug -- help - read_store entered, data_path: ', data_path
    try:
        tmp = "/".join([data_path, filename])
        if debug: print '\n debug -- tmp: ', tmp
        f = open(tmp, 'rb')
        data = f.read()
        f.close()
        return data
    except Exception, err:
        raise Exception('%s' % err.message)

def read_store2(filename):
    """
    open filename, read data, close file and return data
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
    print '\n debug -- filename: ', filename
    try:
        data = read_store2(filename)
        for line in data:
            results += line + '\n'
        return results
    except:
        return None
