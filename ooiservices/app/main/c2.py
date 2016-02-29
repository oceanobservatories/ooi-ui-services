#!/usr/bin/env python
"""
API v1.0 Command and Control (C2) routes
"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app, make_response, request
from ooiservices.app.main import api
from ooiservices.app.models import Array
from ooiservices.app.main.routes import get_display_name_by_rd
import json, os
from requests.exceptions import ConnectionError, ReadTimeout
import requests
from urllib import urlencode
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from datetime import datetime as dt
from copy import deepcopy
import datetime as dt
import calendar
import pytz
import tzlocal
from operator import itemgetter
from ooiservices.app import cache
import math

CACHE_TIMEOUT = 86400


# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 array routes
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/arrays', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_arrays():
    #Get C2 arrays, return list of array abstracts
    list_of_arrays = []
    arrays = Array.query.all()
    for array in arrays:
        item = get_array_abstract(array.array_code)
        if item:
            list_of_arrays.append(item)
    return jsonify(arrays=list_of_arrays)

@api.route('/c2/array/<string:array_code>/abstract', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_array_abstract(array_code):
    '''
    Get C2 array abstract (display), return abstract
    '''
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    response_dict = get_array_abstract(array_code)
    return jsonify(abstract=response_dict)

def get_array_abstract(array_code):
    # get array abstract using valid array_code; CHECK array_code before calling
    array = Array.query.filter_by(array_code=array_code).first()
    response_dict = {}
    response_dict['display_name'] = array.display_name
    response_dict['reference_designator'] = array.array_code
    response_dict['array_id'] = array.id
    response_dict['operational_status'] = 'Online' #c2_get_array_operational_status(array_code)
    response_dict['mission_enabled'] = 'False'

    return response_dict

#TODO get operational status from uframe
@api.route('/c2/array/<string:array_code>/current_status_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_array_current_status_display(array_code):
    '''
    C2 get array Current Status tab contents, return current_status_display
    '''
    contents = []
    array_info = {}
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('Unknown array (array_code: \'%s\')' % array_code)
    # Get data, add to output
    # get ordered set of platform_deployments for array.id
    platforms = []
    _platforms = _get_platforms(array_code)
    if _platforms:
        for platform_deployment in _platforms:
            _array_code = platform_deployment['mooring_code'][0:2]
            if _array_code == array_code:
                rd = platform_deployment['reference_designator']
                platforms.append(rd)
                row = {}
                if platform_deployment['display_name']:
                    row['display_name'] = platform_deployment['display_name']
                else:
                    row['display_name'] = rd
                row['reference_designator'] = rd

                if array_code != 'RS':
                    row['operational_status'] = 'Offline'
                else:
                    # Get instruments for this platform; if no instrument mark status 'Unknown'
                    instruments, oinstruments = _get_instruments(rd)
                    if not instruments:
                        row['operational_status'] = 'Unknown'
                    else:
                        row['operational_status'] = 'Online'
                array_info[rd] = row

    # create list of dictionaries representing data row(s), ordered by reference_designator
    for r in platforms:
        if r in array_info:
            contents.append(array_info[r])
    return jsonify(current_status_display=contents)

@api.route('/c2/array/<string:array_code>/history', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_array_history(array_code):
    '''
    C2 get array history, return history
    '''
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('Unknown array (array_code: \'%s\')' % array_code)
    history = { 'event': [], 'command': [], 'configuration':[] }
    if array_code:
        history = get_history(array_code)
    return jsonify(history=history)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 platform
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/platform/<string:reference_designator>/abstract', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_abstract(reference_designator):
    #Get C2 platform abstract, return abstract
    response_dict = {}
    platform_deployment = _get_platform(reference_designator)
    if platform_deployment:
        response_dict = {}
        if platform_deployment['display_name']:
            response_dict['display_name'] = platform_deployment['display_name']
        else:
            response_dict['display_name'] = reference_designator
        response_dict['reference_designator'] = reference_designator
        response_dict['operational_status'] = 'Online' #c2_get_platform_operational_status(reference_designator)
    return jsonify(abstract=response_dict)

@api.route('/c2/platform/<string:reference_designator>/current_status_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_current_status_display(reference_designator):
    '''
    Get C2 platform Current Status tab contents, return current_status_display.
    '''
    contents = []
    platform_info = {}
    platform_deployment = _get_platform(reference_designator)
    if platform_deployment:
        platform_code = "-".join([platform_deployment['mooring_code'], platform_deployment['platform_code'] ])
        # Get instruments for this platform
        instruments, oinstruments = _get_instruments(platform_code)
        for instrument in instruments:
            row = {}
            if not instrument['display_name']:
                row['display_name'] = instrument['reference_designator']
            else:
                row['display_name'] = instrument['display_name']
            row['reference_designator'] = instrument['reference_designator']
            try:
                status = 'Unknown' #_c2_get_instrument_driver_status(instrument['reference_designator'])
            except:
                status = {}
            row['operational_status'] = status
            platform_info[instrument['reference_designator']] = row
        # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
        # 'data' == rows for initial grid ('Current Status')
        for instrument_reference_designator in oinstruments:
            if instrument_reference_designator in platform_info:
                contents.append(platform_info[instrument_reference_designator])
    return jsonify(current_status_display=contents)

@api.route('/c2/platform/<string:reference_designator>/history', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_history(reference_designator):
    '''
    C2 get platform history
    '''
    history = {}
    if not reference_designator:
        return bad_request('reference_designator parameter empty.')
    #history = { 'event': [], 'command': [], 'configuration':[] }
    platform = _get_platform(reference_designator)
    if platform:
        history = get_history(reference_designator)
    return jsonify(history=history)

# todo put content processing back in.
@api.route('/c2/platform/<string:reference_designator>/ports_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_ports_display(reference_designator):
    """
    Get C2 platform Ports tab contents, return ports_display ([{},{},...]
    where dicts for each instrument_deployment in platform_deployment:
    For example:
        http://localhost:4000/c2/platform/CP02PMCO-WFP01/ports_display
        response:
        {"ports_display": [ {
                              "class": "PARAD",
                              "instrument": "CP02PMCO-WFP01-05-PARADK000",
                              "instrument_status": "Online",
                              "port": "05",
                              "port_available": "False",
                              "port_status": "Online",
                              "sequence": "000",
                              "series": "K"
                            },
                            ...
                       ]}
    """
    contents = []
    '''
    platform_info = {}
    if not reference_designator:
        return bad_request('reference_designator parameter empty.')
    platform_deployment = _get_platform(reference_designator)
    if platform_deployment:
        # Get instruments for this platform
        platform_code = "-".join([platform_deployment['mooring_code'], platform_deployment['platform_code'] ])
        instruments, oinstruments = _get_instruments(platform_code)
        # create list of reference_designators (instruments) and accumulate dict result (key=reference_designator) for output
        for instrument_deployment in instruments:
            rd = instrument_deployment['reference_designator']
            port    = rd[15:15+2]
            iclass  = rd[18:18+5]
            iseries = rd[23:23+1]
            iseq    = rd[24:24+3]
            row = {}
            row['port'] = port
            row['port_status'] = 'Online' #c2_get_platform_operational_status(reference_designator) # same as platform for now
            row['port_available'] = str(True)
            if row['port_status'] == 'Online' or row['port_status'] == 'Unknown':
                row['port_available'] = str(False)
            row['instrument'] = rd
            row['class'] = iclass
            row['series']= iseries
            row['sequence'] = iseq
            if not instrument_deployment['display_name']:
                row['display_name'] = rd
            else:
                row['display_name'] = instrument_deployment['display_name']
            try:
                status = _c2_get_instrument_driver_status(rd)
            except:
                status = {}
            row['instrument_status'] = status
            platform_info[rd] = row

        # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
        # 'data' == rows for initial grid ('Current Status')
        for instrument_reference_designator in oinstruments:
            if instrument_reference_designator in platform_info:
                contents.append(platform_info[instrument_reference_designator])
    '''
    return jsonify(ports_display=contents)

#TODO complete with commands from uframe when platform/api available (post R5)
@api.route('/c2/platform/<string:reference_designator>/commands', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_commands(reference_designator):
    #Get C2 platform commands return commands [{},{},...]
    commands = []
    if not reference_designator:
        return bad_request('empty reference_designator parameter.')
    platform = _get_platform(reference_designator)
    if platform:
        response_text = json_get_uframe_platform_commands(reference_designator)
        if response_text:
            commands = json.loads(response_text)
    return jsonify(commands=commands)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 instrument
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/instrument/<string:reference_designator>/abstract', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_abstract(reference_designator):
    '''
    C2 get instrument abstract
    Modified to support migration to uframe
    Sample: http://localhost:4000/c2/instrument/reference_designator/abstract
    '''
    try:
        response_dict = {}
        if not reference_designator:
            return bad_request('empty reference_designator parameter.')
        instrument_deployment = _get_instrument(reference_designator)
        if instrument_deployment:
            if instrument_deployment['display_name']:
                response_dict['display_name'] = instrument_deployment['display_name']
            else:
                response_dict['display_name'] = instrument_deployment['reference_designator']
            response_dict['reference_designator'] = instrument_deployment['reference_designator']
            try:
                status = _c2_get_instrument_driver_status(instrument_deployment['reference_designator'])
            except:
                status = {}
            response_dict['operational_status'] = status
    except Exception, err:
        return bad_request(err.message)
    return jsonify(abstract=response_dict)

@api.route('/c2/instrument/<string:reference_designator>/history', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_history(reference_designator):
    '''
    C2 get instrument history, return history
    where history = { 'event': [], 'command': [], 'configuration':[] })
    '''
    history = {}
    if not reference_designator:
        return bad_request('reference_designator parameter empty.')
    instrument = _get_instrument(reference_designator)
    if instrument:
        history = get_history(reference_designator)
    return jsonify(history=history)

@api.route('/c2/instrument/<string:reference_designator>/ports_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_ports_display(reference_designator):
    '''
    Get C2 instrument Ports tab contents, return ports_display
    Modified for migration to uframe
    '''
    if not reference_designator:
        return bad_request('reference_designator parameter empty.')
    contents = []
    info = {}
    instrument_deployment = _get_instrument(reference_designator)
    if instrument_deployment:
        # get info and create dict result (key=reference_designator) for output
        port    = reference_designator[15:15+2]
        iclass  = reference_designator[18:18+5]
        iseries = reference_designator[23:23+1]
        iseq    = reference_designator[24:24+3]
        row = {}
        row['port'] = port
        row['port_status'] = 'Unknown'
        port_status = 'Online' #c2_get_platform_operational_status(reference_designator) # same as platform for now
        if port_status in ['Online', 'Offline', 'Unknown']:
            row['port_status'] = port_status
        row['port_available'] = str(True)
        if row['port_status'] == 'Online' or row['port_status'] == 'Unknown':
            row['port_available'] = str(False)
        row['instrument'] = reference_designator
        row['class'] = iclass
        row['series']= iseries
        row['sequence'] = iseq
        try:
            status = _c2_get_instrument_driver_status(reference_designator)
        except:
            status = {}
        row['instrument_status'] = status
        if instrument_deployment['display_name']:
            row['display_name'] = instrument_deployment['display_name']
        else:
            row['display_name'] = reference_designator
        info[reference_designator] = row
        # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
        # 'data' == rows for initial grid ('Current Status')
        if reference_designator in info:
            contents.append(info[reference_designator])
    return jsonify(ports_display=contents)

#----------------------------------------------------
# private general helpers
#----------------------------------------------------
def get_history(reference_designator):
    # C2 make fake history for event, command and configuration
    #TODO get history from proper source
    history = { 'event': [], 'command': [], 'configuration':[] }
    history['event'] = []
    history['command'] = []
    history['configuration'] = []
    # command history
    commands = {}
    commands[1] = { 'msg': 'CMD item 3', 'timestamp' : '2014-11-23T20:00:00' }
    commands[2] = { 'msg': 'Failed Sample Freq from 10 hz to 1 hz', 'timestamp' : '2015-02-04T04:13:56' }
    commands[3] = { 'msg': 'Changed Ping Freq from 10hz to 1 Hz', 'timestamp' : '2015-02-04T07:39:12' }
    history['command'].append(commands)
    # event history
    events = {}
    events[1] = { 'msg': '2014-10-11T14:00 Turned On' }
    events[2] = { 'msg': '2014-11-11T22:00 Turned Off' }
    history['event'].append(events)
    # configuration history
    configuration = {}
    configuration[1] = { 'msg': '2014-11-12T14:00 Initial Configuration' }
    configuration[2] = { 'msg': '2014-11-19T22:00 Loaded PowerSave.config - we needed to turn off' }
    configuration[3] = { 'msg': '2014-11-20T22:00 Loaded AllPorts.config' }
    configuration[4] = { 'msg': '2014-11-21T22:00 Loaded PowerSave.config - we needed to turn off' }
    history['configuration'].append(configuration)
    return history

#--------------------------------------------------------------
#-- file based helpers for array_display (replace with uframe)
#--------------------------------------------------------------
'''
def c2_get_array_operational_status(reference_designator):
    # C2 get array operational status, return status
    #Errors:
    #    'Malformed operational status data; not in valid json format. (\'%s\')'
    status = 'Unknown'
    response_text = json_get_uframe_array_operational_status(reference_designator)
    if response_text:
        try:
            result = json.loads(response_text)
        except:
            return bad_request('Malformed operational status data; not in valid json format. (\'%s\')' %
                               reference_designator)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status
'''
#----------------------------------------------------
#-- file based helpers for platform_display
#----------------------------------------------------
'''
def c2_get_platform_operational_status(reference_designator):

    #Get C2 platform status (string such as { "unknown" | "Online" | "Offline" }
    #Errors:
    #    bad_request('unknown platform_deployment (\'%s\')'
    #    bad_request('Malformed streams data; not in valid json format. (\'%s\')'

    status = 'Unknown'
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
    if not platform_deployment:
        return bad_request('unknown platform_deployment (\'%s\')' % reference_designator)
    response_text = json_get_uframe_platform_operational_status(reference_designator)
    if response_text:
        try:
            result = json.loads(response_text)
        except:
            return bad_request('Malformed operational status; not in valid json format. (\'%s\')' % reference_designator)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status
'''
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TODO Read notes here on migration from file based interface to uframe supported interface
# C2 helper for file data (./ooiuiservices/tests/c2data/*)
# All file based methods are targeted for migration to uframe interface.
# Each is marked for targeted migration step (A, B, C, etc)
# migration B - things where we need platform/api or other (rollup from instruments?)
# migration C - items where it is not clear how to best accomplish (maybe rollup platforms?)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# targeted for deprecation
def read_store(filename):
    """
    open filename, read data, close file and return data
    """
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    c2_data_path = os.path.join(APP_ROOT, '..', '..', 'tests', 'c2data')
    try:
        tmp = "/".join([c2_data_path, filename])
        f = open(tmp, 'rb')
        data = f.read()
        f.close()
    except Exception, err:
        raise Exception('%s' % err.message)
    return data



def read_store2(filename):
    """
    open filename, read data, close file and return data
    """
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    c2_data_path = os.path.join(APP_ROOT, '..', '..', 'tests', 'c2data')
    try:
        tmp = "/".join([c2_data_path, filename])
        f = open(tmp, 'rb')
        line = f.read()
        data = line.split('\r')
        f.close()
    except Exception, err:
        raise Exception('%s' % err.message)
    return data


# targeted for migration B
def json_get_uframe_platform_commands(platform):
    filename = "_".join([platform, 'commands'])
    try:
        data = read_store(filename)
    except:
        return None
    return data


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# uframe interface for c2 instrument/api - uframe 4.x targeted
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/instruments/status', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instruments_status():
    """
    # get status of all instrument agents, return json.
    # sample: localhost:12572/instrument/api
    """
    statuses = []
    try:
        data = _c2_get_instruments_status()
        if data:
            statuses = data
        return jsonify(statuses=statuses)
    except Exception as err:
        return bad_request(err.message)

@api.route('/c2/instrument/<string:reference_designator>/commands', methods=['GET'])
@api.route('/c2/instrument/<string:reference_designator>/status', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_driver_status(reference_designator):
    """
    Get the current overall state of the specified instrument (id is the reference designator of the instrument).
    If the query option "blocking" is specified as true, then this call will block until a state change,
    allowing for a push-like interface for web clients.
    Sample: localhost:12572/instrument/api/reference_designator/status
    """
    status = []
    response_status = {}
    response_status['status_code'] = 200
    response_status['message'] = ""
    try:
        data = _c2_get_instrument_driver_status(reference_designator)
        if data:
            status = data
        return jsonify(status)
    except Exception as err:
        message = str(err.message)          # new
        current_app.logger.info(message)    # new
        #print '\n debug --- returning exception /commands'
        #response_status['status_code'] = 400
        #response_status['message'] = message
        return bad_request(message)
        '''
        response = {}
        response['response'] = response_status
        #return jsonify(response=response_status)
        return bad_request(response)
        #return jsonify(response)
        '''

@api.route('/c2/instrument/<string:reference_designator>/state', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_driver_state(reference_designator):
    """
    Return the instrument driver state. Returns json.
    Sample: http://host:12572/instrument/api/reference_designator/state
    """
    state = []
    try:
        data = _c2_get_instrument_driver_state(reference_designator)
        if data:
            state = data
        return jsonify(state)
    except Exception as err:
        return bad_request(err.message)

@api.route('/c2/instrument/<string:reference_designator>/parameters', methods=['POST'])
@auth.login_required
@scope_required(u'command_control')
def c2_set_instrument_driver_parameters(reference_designator):
    """
    Set one or more instrument driver parameters. Returns json.
    Accepts the following urlencoded parameters:
        resource:   JSON-encoded dictionary of parameter:value pairs
        timeout:    in milliseconds, default value is 60000
    Sample: http://host:12572/instrument/api/reference_designator/resource
    """
    parameters = []
    try:
        request_data = json.loads(request.data)

        """
        # Sample request_data from UI - does not work!
        {u'resource': {u'relevel_timeout': 600, u'ytilt_relevel_trigger': u'250', u'auto_relevel': u'false',
         u'xtilt_relevel_trigger': u'300', u'heat_duration': 1, u'output_rate_hz': 20}, u'timeout': 60000}

        # This sample request data DOES work:
        request_data = {u'resource': {u'relevel_timeout': 607, u'ytilt_relevel_trigger': 257,
                                      u'auto_relevel': 'false', u'xtilt_relevel_trigger': 307, u'heat_duration': 7,
                                      u'output_rate_hz': 17}, u'timeout': 60000}

        # Works:
        request_data = {u'resource': {u'ytilt_relevel_trigger': 255, u'xtilt_relevel_trigger': 205}, u'timeout': 60000}

        # Doesn't work:
        #request_data = {u'resource': {u'ytilt_relevel_trigger': u'250', u'xtilt_relevel_trigger': 200}, u'timeout': 60000}

        # Positive test:
        request_data = {u'resource': {u'relevel_timeout': 607, u'ytilt_relevel_trigger': 257,
                                      u'auto_relevel': 'false', u'xtilt_relevel_trigger': 307, u'heat_duration': 7,
                                      u'output_rate_hz': 17}, u'timeout': 60000}
        """
        data = _c2_set_instrument_driver_parameters(reference_designator, request_data)
        if data:
            parameters = data
        return jsonify(parameters)

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return bad_request(str(err.message))


@api.route('/c2/instrument/<string:reference_designator>/execute', methods=['POST'])
@auth.login_required
@scope_required(u'command_control')
def c2_instrument_driver_execute(reference_designator):
    """
    Command the driver to execute a capability. Returns json.
    Accepts the following urlencoded parameters:
        command:    capability to execute
        kwargs:     JSON-encoded dictionary specifying any necessary keyword arguments for the command
        timeout:    in milliseconds, default value is 60000
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST/execute
    """
    execute = []
    try:
        if request.data:
            request_data = json.loads(request.data)
            data = _c2_instrument_driver_execute(reference_designator, request_data)
            if data:
                execute = data
        return jsonify(execute)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return bad_request(str(err.message))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private worker methods for instrument/api
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _c2_get_instruments_status():
    """ Get status of all instrument agents. Returns response.content as json.
    Sample: http://localhost:4000/instrument/api
    """
    try:
        data = None
        response = uframe_get_instruments_status()
        if response.status_code != 200:
            raise Exception('error retrieving instrument agents statuses from uframe')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def uframe_get_instruments_status():
    """
    Returns the uframe response for status of all instrument agents.
    Sample: http://host:12572/instrument/api
    """
    try:
        url, timeout, timeout_read = get_uframe_info()
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise

# todo re: blocking
def _c2_get_instrument_driver_status(reference_designator):
    """
    Get the current overall state of the specified instrument (id is the reference designator of the instrument).
    If the query option "blocking" is specified as true, then this call will block until a state change,
    allowing for a push-like interface for web clients.
    Sample: http://host:12572/instrument/api/reference_designator
    """
    try:
        # Get status
        data = None
        response = uframe_get_instrument_driver_status(reference_designator)
        if response.status_code != 200:
            raise Exception('Error retrieving instrument overall state from uframe.')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                return None
                #raise Exception('Malformed data; not in valid json format.')

        #print '\n -- debug data: ', json.dumps(data, indent=4, sort_keys=True)

        # Get all parameter values for instruments
        status = data
        state = None
        # verify parameters and state are in status
        if 'state' in status['value']:
            state = status['value']['state']

        # Update status to reflect parameter values for all instruments
        # Have instrument state, continue
        if state is not None:
            if state != "DRIVER_BUSY_EVENT":
                if state != 'Unknown' and state != 'UNKNOWN' and 'DISCONNECTED' not in state:
                    try:
                        result = _c2_get_instrument_driver_parameter_values(reference_designator)
                    except Exception as err:
                        result = None
                        message = str(err.message)
                        # should we be raising here....review
                    if result:
                        if 'value' in result:
                            if isinstance(result['value'], dict):
                                status['value']['parameters'] = result['value']

        # This add processing time, todo consider separating/status from /commands (review)
        if data:
            streams = {}
            try:
                streams = get_streams_dictionary(reference_designator)
            except Exception as err:
                print'\n debug -- exception: ', err.message

            data['streams'] = streams
            #print '\n -- debug data[streams]: ', json.dumps(data, indent=4, sort_keys=True)

        return data
    except Exception as err:
        print'\n debug -- (_c2_get_instrument_driver_status) exception: ', err.message  # new
        raise

# todo re: blocking
def uframe_get_instrument_driver_status(reference_designator):
    """ Returns the uframe response for status of single instrument agent
    Sample: http://host:12572/instrument/api/reference_designator
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        #print '\n debug -- uframe_get_instrument_driver_status: url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except ConnectionError:
        message = 'ConnectionError (uframe) for get instrument driver status.'
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for get instrument driver status.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def _c2_get_instrument_driver_state(reference_designator):
    """ Return the instrument driver state.
    Sample: localhost:12572/instrument/api/reference_designator/state [GET]
    """
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'state')
        if response.status_code != 200:
            raise Exception('error retrieving instrument state from uframe')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def _c2_get_instrument_driver_parameters(reference_designator):
    """ Return the instrument driver response, state, parameters and parameter values.

    Sample: localhost:12572/instrument/api/reference_designator/resource
    - call _c2_get_instrument_driver_status, get response_data['parameters'] and response_data['state']:
            "parameters": {
                      "ave": {
                        "description": "Number of measurements for each reported value.",
                        "direct_access": true,
                        "display_name": "Measurements per Reported Value",
                        "get_timeout": 10,
                        "set_timeout": 10,
                        "startup": true,
                        "value": {
                          "default": 1,
                          "description": null,
                          "type": "int"
                        },
                        "visibility": "READ_WRITE"
                      },
                      "clk": {
                        "description": "Time in the Real Time Clock.",
                        "direct_access": false,
                        "display_name": "Time",
                        "get_timeout": 10,
                        "set_timeout": 10,
                        "startup": false,
                        "value": {
                          "description": null,
                          "type": "string",
                          "units": "HH:MM:SS"
                        },
                        "visibility": "READ_ONLY"
                      },. . .
                  }
            "state": "DRIVER_STATE_COMMAND"

    - check state value, if ok, continue
    - call _c2_get_instrument_driver_parameter_values to get value, where value is dict of parameter(s) values:
            "value": {
                        "ave": 15,
                        "clk": "21:44:21",
                        "clk_interval": "00:00:00",
                        "dat": "05/08/15",
                        "int": "00:30:00",
                        "m1d": 55,
                        "m1s": 2.1e-06,
                        "m2d": 52,
                        "m2s": 0.01213,
                        "m3d": 49,
                        "m3s": 0.0909,
                        "man": 0,
                        "mem": 4095,
                        "mst": "16:33:02",
                        "pkt": 0,
                        "rat": 19200,
                        "rec": 0,
                        "seq": 0,
                        "ser": "BBFL2W-1028",
                        "set": 0,
                        "status_interval": "00:00:00",
                        "ver": "Triplet5.20",
                        "wiper_interval": "00:00:00"
                      }
    - create response, example of response [basic] structure:
    {
        "response": { "status_code": 200, "message": "" },
        "parameters": { ... }
        "state": "DRIVER_STATE_COMMAND"
        "value": { ... }
    }
    """
    result = {}
    response_status = {}
    response_status['status_code'] = 200
    response_status['message'] = ""
    try:
        data = {}
        # Get instrument status, retrieve parameters and state
        try:
            status = _c2_get_instrument_driver_status(reference_designator)
        except:
            status = None

        state = None
        # Error: unable to obtain current instrument status; retry
        if status is None:
            response_status['status_code'] = 400
            response_status['message'] = "unable to obtain instrument parameters and state; retry."
            data['response'] = response_status
            data['value'] = {}
            data['parameters'] = {}
            data['state'] = ""
            return data

        # Have instrument status, continue
        else:
            data = {}
            # verify parameters and state are in status
            status_value = status['value']
            if 'parameters' in status['value']['metadata'] and 'state' in status['value']:
                if 'parameters' in status['value']['metadata']:
                    data['parameters'] = status['value']['metadata']['parameters']
                if 'state' in status_value:
                    data['state'] = status['value']['state']
                    state = status['value']['state']
            # missing parameters and state, set response_status accordingly (error)
            else:
                response_status['status_code'] = 400
                response_status['message'] = "unable to obtain instrument parameters and state; retry."
                data['response'] = response_status
                data['value'] = {}
                data['parameters'] = {}
                data['state'] = ""
                return data

        # Error: instrument state not defined; retry
        if state is None:
            response_status['status_code'] = 400
            response_status['message'] = "unable to determine instrument state; retry."
            data['response'] = response_status
            data['value'] = {}
            return data
        # Have instrument state, continue
        else:
            if state == "DRIVER_STATE_COMMAND":
                try:
                    result = _c2_get_instrument_driver_parameter_values(reference_designator)
                    if result is None:
                        raise Exception('unable to retrieve instrument driver parameter values')
                except Exception as err:
                    message = str(err.message)
                if result:
                    if 'value' in result:
                        if isinstance(result['value'], dict):
                            data['value'] = result['value']
                        else:
                            response_status['status_code'] = 400
                            response_status['message'] = "unable to obtain instrument parameter values; retry."
                            data['response'] = response_status
                            data['value'] = {}
                            return data
            # Error: Not able to retrieve parameter values at this time due to instrument state
            else:
                response_status['status_code'] = 400
                response_status['message'] = "instrument state (%s); unable to obtain parameter values; retry." % state
                data['response'] = response_status
                data['value'] = {}
                return data

        data['response'] = response_status
        return data

    except:
        raise

def _c2_get_instrument_driver_parameter_values(reference_designator):
    """
    Return the instrument driver parameter values.
    Sample: localhost:12572/instrument/api/reference_designator/resource with data dictionary.
        {
        u'cmd': {   u'args': [u'DRIVER_PARAMETER_ALL'],
                    u'cmd': u'get_resource',
                    u'kwargs': {}},
        u'time': 1431106176.695633,
        u'transaction_id': 361,
        u'type': u'DRIVER_AYSNC_EVENT_REPLY',
        u'value':   {
                    u'ave': 20,
                    u'clk': u'17:24:57',
                    u'clk_interval': u'00:00:00',
                    u'dat': u'05/08/15',
                    u'int': u'00:30:00',
                    u'm1d': 55,
                    u'm1s': 2.1e-06,
                    u'm2d': 52,
                    u'm2s': 0.01213,
                    u'm3d': 49,
                    u'm3s': 0.0909,
                    u'man': 0,
                    u'mem': 4095,
                    u'mst': u'16:33:02',
                    u'pkt': 0,
                    u'rat': 19200,
                    u'rec': 0,
                    u'seq': 0,
                    u'ser': u'BBFL2W-1028',
                    u'set': 0,
                    u'status_interval': u'00:00:00',
                    u'ver': u'Triplet5.20',
                    . . .
                    }
        }

    """
    try:
        data = None
        response = uframe_get_instrument_driver_parameter_values(reference_designator, 'resource')
        if response.status_code != 200:
            message = 'error retrieving instrument driver resource (parameters) from uframe'
            raise Exception(message)
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def uframe_get_instrument_driver_parameter_values(reference_designator, command):
    """ Return the uframe response of instrument command resource with payload provided for GET
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        response = requests.get(url, timeout=(timeout, timeout_read),
                                data={'resource': json.dumps('DRIVER_PARAMETER_ALL')})
        return response
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise

def convert(data):
    test = dict([(str(k), v) for k, v in data.items()])
    for k,v in test.items():
        if type(v) == type({'a':1}):
            result = dict([(str(kk), vv) for kk, vv in v.items()])
            test[k] = result
    return test

def populate_range_values(data, key_dict):
    """ Process key_dict to populate attributes 'min', 'max' and 'set' for each int and float parameter.
    For int and float parameters, parse 'description' attribute for 'min', 'max' and 'set';
    return dict with updated values.

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Input dictionary (key: parameter name):
    key_dict:  {
        "ave": {
            "desc": "Number of measurements for each reported value: (1 - 255)",
            "max": null,
            "min": null,
            "set": null,
            "type": "int"
        }
    }
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Proposed output dictionary:
    key_dict:  {
        "ave": {
            "desc": "Number of measurements for each reported value: (1 - 255)",
            "max": 255,
            "min": 1,
            "set": null,
            "type": "int"
        }
    }
    """
    debug = False
    if debug: print '\n debug --- populate_range_values entered.....'
    valid_parameter_types = ['int', 'float', 'bool', 'string']
    try:
        result = {}
        for k,v in data.iteritems():
            if k not in key_dict:
                print '\n ******************* %s not in key_dict!!'
            if debug: print '\n ---------- %s: %r (%s)' % (k,v, key_dict[k])
            description = key_dict[k]['desc']
            display_name = key_dict[k]['display_name']
            if description is None:
                result[k] = {}
                result[k]['min'] = None
                result[k]['max'] = None
                result[k]['set'] = []
                result[k]['display_name'] = display_name
                continue

            parameter_type = key_dict[k]['type']
            display_name = key_dict[k]['display_name']
            if parameter_type not in valid_parameter_types:
                message = 'Unknown parameter type (%s), valid types: %s' % (parameter_type, valid_parameter_types)
                if debug: print '\n\tdebug -- message: ', message
                current_app.logger.info(message)
                result[k] = {'min': None, 'max': None, 'set': None, 'display_name': display_name}
                continue
            try:
                if debug: print '\n debug -- %s processing' % key_dict[k]['type']
                result[k] = {}
                result[k]['min'] = None
                result[k]['max'] = None
                result[k]['set'] = []
                result[k]['display_name'] = display_name
                min, max, set = parse_description(description, parameter_type)
                if debug: print '\n debug --- after parse_description...'

                if min is None:
                    if debug: print '\n debug ************ min is None, continue...'
                else:
                    result[k]['min'] = min
                    #continue
                if max is None:
                    if debug: print '\n debug ************ max is None, continue...'
                    #continue
                else:
                    result[k]['max'] = max

                if not set:
                    if debug: print '\n debug ************ set is empty, continue...'
                    #continue
                else:
                    result[k]['set'] = set
                    #continue
            except Exception as err:
                if debug: print '\n debug ************ message: ', err.message
                continue
            '''
            result[k] = {}
            result[k]['min'] = min
            result[k]['max'] = max
            result[k]['set'] = set
            result[k]['display_name'] = display_name
            '''


        if debug: print '\n debug --- populate_range_values exit.....'
        return result
    except Exception as err:
        print '\n debug -- (populate_range_values) exception: ', err.message
        raise


def populate_and_check_range_values(data, key_dict):
    """ Process key_dict to populate attributes 'min', 'max' and 'set' for each int and float parameter.
    For int and float parameters, parse 'description' attribute for 'min', 'max' and 'set';
    return dict with updated values.

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Input dictionary (key: parameter name):
    key_dict:  {
        "ave": {
            "desc": "Number of measurements for each reported value: (1 - 255)",
            "max": null,
            "min": null,
            "set": null,
            "type": "int"
        }
    }
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Proposed output dictionary:
    key_dict:  {
        "ave": {
            "desc": "Number of measurements for each reported value: (1 - 255)",
            "max": 255,
            "min": 1,
            "set": null,
            "type": "int"
        }
    }
    """
    debug = False
    if debug: print '\n debug --- populate_range_values entered.....'
    valid_parameter_types = ['int', 'float', 'bool', 'string']
    try:
        result = {}
        for k,v in data.iteritems():
            if k not in key_dict:
                print '\n ******************* %s not in key_dict!!'
            if debug: print '\n ---------- %s: %r (%s)' % (k,v, key_dict[k])
            description = key_dict[k]['desc']
            display_name = key_dict[k]['display_name']
            if description is None:
                result[k] = {}
                result[k]['min'] = None
                result[k]['max'] = None
                result[k]['set'] = []
                result[k]['display_name'] = display_name
                continue

            parameter_type = key_dict[k]['type']
            display_name = key_dict[k]['display_name']
            if parameter_type not in valid_parameter_types:
                message = 'Unknown parameter type (%s), valid types: %s' % (parameter_type, valid_parameter_types)
                if debug: print '\n\tdebug -- message: ', message
                current_app.logger.info(message)
                result[k] = {'min': None, 'max': None, 'set': None, 'display_name': display_name}
                continue
            try:
                if debug: print '\n debug -- %s processing' % key_dict[k]['type']
                result[k] = {}
                result[k]['min'] = None
                result[k]['max'] = None
                result[k]['set'] = []
                result[k]['display_name'] = display_name
                min, max, set = parse_description(description, parameter_type)
                if debug: print '\n debug --- after parse_description...'
                if min is None:
                    if debug: print '\n debug ************ min is None, continue...'
                else:
                    result[k]['min'] = min
                    #continue
                if max is None:
                    if debug: print '\n debug ************ max is None, continue...'
                    #continue
                else:
                    result[k]['max'] = max

                if not set:
                    if debug: print '\n debug ************ set is empty, continue...'
                    #continue
                else:
                    result[k]['set'] = set
                    #continue
            except Exception as err:
                if debug: print '\n debug ************ message: ', err.message
                continue
            '''
            result[k] = {}
            result[k]['min'] = min
            result[k]['max'] = max
            result[k]['set'] = set
            result[k]['display_name'] = display_name
            '''


        if debug: print '\n debug --- populate_range_values exit.....'
        return result
    except Exception as err:
        print '\n debug -- (populate_range_values) exception: ', err.message
        raise


def new_scrub_ui_request_data(data, parameter_types, ranges):
    """ Modify format of float, int and bool data values provided by ooi-ui.
    Validate specific values against ranges, if ranges provided.
    """
    debug = False
    result = {}
    error_result = {}
    try:
        if not data:
            message = 'Parameter data is empty or null.'
            raise Exception(message)
        if not parameter_types:
            message = 'Parameter parameter_types is empty or null.'
            raise Exception(message)

        if debug:
            print '\n debug -- new_scrub_ui_request_data....entered.........................'
            print '\n debug -- data: ', json.dumps(data, indent=4, sort_keys=True), ' .........'
            print '\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n\n'
            print '\n debug -- ranges: ', json.dumps(ranges, indent=4, sort_keys=True), '.........'
            print '\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - '

        #raise Exception('this is a test error message')
        for k,v in data.iteritems():
            if debug: print '\n %s: %r (%s)' % (k,v, parameter_types[k])

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process float value
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if parameter_types[k] == 'float':

                # Convert value provided; on error, record error.
                try:
                    float_value = float(v)
                except:
                    display_name = 'unknown'
                    if k in ranges:
                        display_name = ranges[k]['display_name']
                    #message = 'Failed to convert parameter \'%s\' (%s) value (%r) to float.' % (display_name, k, v)
                    message = 'Failed to convert parameter (%s) value (%r) to float.' % (k, v)
                    error_result[display_name] = message
                    continue

                if debug: print '\n debug --- float_value: ', float_value
                if k in ranges:
                    if debug: print '\n ------------ %s in ranges dictionary...' % k
                    min_error = False
                    max_error = False

                    # Determine min and max for ranges
                    range_min = ranges[k]['min']
                    range_max = ranges[k]['max']
                    range_set = ranges[k]['set']
                    display_name = ranges[k]['display_name']

                    if debug:
                        print '\n\tdebug -- range_min: ', range_min
                        print '\n\tdebug -- range_max: ', range_max
                        print '\n\tdebug -- range_set: ', range_set

                    # Range check data value entered against min range value
                    if range_min is not None:
                        if float_value < range_min:
                            min_error = True
                            '''
                            msg = 'Parameter \'%s\' (%s) value of (%r) is less than range minimum value of (%r).' % \
                                  (display_name, k, float_value, range_min)
                            '''
                            msg = 'Parameter (%s) value of (%r) is less than range minimum value of (%r).' % \
                                  (k, float_value, range_min)
                            error_result[display_name] = msg
                            if debug: print '\n ', msg

                    # Range check data value entered against min range value
                    if range_max is not None:
                        if float_value > range_max:
                            max_error = True
                            '''
                            msg = 'Parameter \'%s\' (%s) value of (%r) is greater than range maximum value of (%r).' % \
                                  (display_name, k, float_value, range_max)
                            '''
                            msg = 'Parameter (%s) value of (%r) is greater than range maximum value of (%r).' % \
                                  (k, float_value, range_max)
                            error_result[display_name] = msg
                            if debug: print '\n ', msg

                    if min_error or max_error:
                        continue

                    if debug: print '\n\tupdate result[%s]: %r' % (k, float_value)
                    result[k] = float_value

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process int value
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif parameter_types[k] == 'int':

                # Convert value provided; on error, record error.
                try:
                    if debug: print '\n\tdebug --- int value to convert: ', v
                    int_value = int(v)
                except:
                    display_name = 'unknown'
                    if k in ranges:
                        display_name = ranges[k]['display_name']
                    else:
                        print '\n debug -- display_name for %s not found in ranges.' % k
                    #message = 'Failed to convert parameter \'%s\' (%s) value (%r) to int.' % (display_name, k, v)
                    message = 'Failed to convert parameter (%s) value (%r) to int.' % (k, v)
                    error_result[display_name] = message
                    if debug: print '\n ****** ', message
                    continue

                if debug: print '\n\tdebug --- int_value: ', int_value

                # If there are range values for this parameter, then perform range checking.
                if k in ranges:
                    if debug: print '\n(int) %s in ranges dictionary...' % k
                    min_error = False
                    max_error = False

                    # Determine min and max for ranges
                    range_min = ranges[k]['min']
                    range_max = ranges[k]['max']
                    range_set = ranges[k]['set']
                    display_name = ranges[k]['display_name']
                    if debug:
                        print '\n\tdebug -- range_min: ', range_min
                        print '\n\tdebug -- range_max: ', range_max
                        print '\n\tdebug -- range_set: ', range_set
                        print '\n\tdebug -- display_name: ', display_name

                    if range_set:
                        if int_value in range_set:
                            result[k] = int_value
                            if debug: print '\n\tupdate result[%s]: %r' % (k, int_value)
                        else:
                            '''
                            message = 'Parameter \'%s\' (%s) has invalid int value \'%s\', not one of %s.' % \
                                      (display_name, k, int_value, range_set)
                            '''
                            message = 'Parameter (%s) has invalid int value \'%s\', not one of %s.' % \
                                      (k, int_value, range_set)
                            error_result[display_name] = message
                            if debug: print '\n ****** ', message
                            continue

                    # Range check data value entered against min range value
                    if range_min is not None:
                        if debug: print '\n\tdebug --- processing int range min...'
                        if int_value < range_min:
                            min_error = True
                            '''
                            msg = 'Parameter \'%s\' (%s) value of (%r) is less than range minimum value of (%r).' % \
                                  (display_name, k, int_value, range_min)
                            '''
                            msg = 'Parameter (%s) value of (%r) is less than range minimum value of (%r).' % \
                                  (k, int_value, range_min)
                            error_result[display_name] = msg
                            if debug: print '\n ', msg

                    # Range check data value entered against max range value
                    if range_max is not None:
                        if debug: print '\n\tdebug --- processing int range max...'
                        if int_value > range_max:
                            max_error = True
                            '''
                            msg = 'Parameter \'%s\' (%s) value of (%r) is greater than range maximum value of (%r).' % \
                                  (display_name, k, int_value, range_max)
                            '''
                            msg = 'Parameter (%s) value of (%r) is greater than range maximum value of (%r).' % \
                                  (k, int_value, range_max)
                            error_result[display_name] = msg
                            if debug: print '\n ', msg

                    if min_error or max_error:
                        continue

                    if debug: print '\n\tupdate result[%s]: %r' % (k, int_value)
                    result[k] = int_value

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process boolean value; on error record error.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif parameter_types[k] == 'bool':
                # Convert value provided, on error raise exception.
                display_name = 'unknown'
                if k in ranges:
                    display_name = ranges[k]['display_name']
                try:
                    if debug: print '\n(bool) %s in ranges dictionary...' % k
                    bool_value = to_bool(v)
                    tmp = str(bool_value)
                    result[k] = tmp.lower()
                except:
                    #message = 'Failed to convert parameter \'%s\' (%s) value (%r) to boolean.' % (display_name, k, v)
                    message = 'Failed to convert parameter (%s) value (%r) to boolean.' % (k, v)
                    error_result[display_name] = message
                    if debug: print '\n ****** ', message
                    continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process string value
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif parameter_types[k] == 'string':

                # Convert str value provided, on error, record error..
                display_name = k
                try:
                    if k in ranges:
                        display_name = ranges[k]['display_name']
                    str_value = str(v)
                except:
                    #message = 'Failed to convert parameter \'%s\' value (%r) to string.' % (k, v)
                    message = 'Failed to convert parameter (%s) value (%r) to string.' % (k, v)
                    error_result[display_name] = message
                    if debug: print '\n ****** ', message
                    continue

                if debug: print '\n debug --- str_value: ', str_value

                # If there are range values for this parameter, then perform range checking.
                if k in ranges:
                    if debug: print '\n(string) %s in ranges dictionary...' % k
                    # Determine min and max for ranges
                    range_min = ranges[k]['min']
                    range_max = ranges[k]['max']
                    range_set = ranges[k]['set']
                    display_name = ranges[k]['display_name']
                    if debug:
                        print '\n\tdebug -- range_min: ', range_min
                        print '\n\tdebug -- range_max: ', range_max
                        print '\n\tdebug -- range_set: ', range_set
                        print '\n\tdebug -- range_set: ', display_name

                    if str_value in range_set:
                        result[k] = str_value
                        if debug: print '\n\tupdate result[%s]: %r' % (k, str_value)
                    else:
                        '''
                        message = 'Parameter \'%s\' (%s) has invalid string value \'%s\', not one of %s.' % \
                                  (display_name, k, str_value, range_set)
                        '''
                        message = 'Parameter (%s) has invalid string value \'%s\', not one of %s.' % \
                                  (k, str_value, range_set)
                        error_result[display_name] = message
                        if debug: print '\n ****** ', message
                        continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Unknown parameter type (not int, float, boolean or string), log error re: parameter type
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            else:
                display_name = 'unknown'
                if k in ranges:
                    display_name = ranges[k]['display_name']
                message = 'Parameter \'%s\' (%s) is using an unknown parameter type \'%s\'.' % \
                          (display_name, k, parameter_types[k])
                current_app.logger.info(message)
                result[k] = v
        if debug:
            print '\n debug ------------ result: ', result
            print '\n debug ------------ error_result: ', error_result

        return result, error_result

    except Exception as err:
        current_app.logger.info(str(err.message))
        raise


def parse_description(description, parameter_type):
    """ Parse parameter str description for range value attributes - 'min', 'max', and 'set'.
    Currently processes into return values of str for 'min', 'max' and 'set'.

    Modify to return actual values, based on parameter type, for 'min', 'max' and 'set'.
    """
    debug = False
    min = None
    max = None
    set = []
    try:
        if not description:
            return min, max, set
        if not parameter_type:
            return min, max, set

        # Get indices of right and left parentheses
        token_end_index = description.rfind(')')
        token_start_index = description.rfind('(')

        # Some instruments may not have a range constraint. In this case, return (do not raise error).
        if token_end_index == -1 or token_start_index == -1:
            message = 'No range values provided in description. No parentheses.'
            current_app.logger.info(message)
            return None, None, []
            #raise Exception(message)

        if debug: print '\n\tdebug -- description: ', description
        if token_end_index <= token_start_index:
            raise Exception('Malformed description string; located right paren in description before left paren.')

        # Get substring of format (xxx - xxxxx). Not processing sets yet.
        if description.count('(') == 1 and description.count(')') == 1:
            token = description[token_start_index:token_end_index]

            # Remove '(' and ')' from token, strip beginning and trailing whitespace.
            token = token.replace('(', '')
            token = token.replace(')', '')
            token = token.strip(' ')
            #print '\n debug -- token: ', token

            # Process range format (xx - xxx)
            if '-' in token:
                #message = 'Unable to locate \'-\' in range token: %s' % token
                #raise Exception(message)
                #print '\n debug -- token stripped: ', token
                tokens = token.split('-')
                if len(tokens) > 2:
                    message = 'Malformed range token, multiple hyphen characters between parentheses. token: %s' % token
                    raise Exception(message)

                min_token = (tokens[0]).strip(' ')
                max_token = (tokens[1]).strip(' ')
                min = convert_to_parameter_type(min_token, parameter_type)
                max = convert_to_parameter_type(max_token, parameter_type)

            # Process range format (xx, xxx) into set value
            elif ',' in token:
                if debug: print '\n\tdebug -- processing set...(found \',\' in token)'
                subtokens = token.split(',')
                list_toks = []
                for tok in subtokens:
                    if not tok:
                        print '\n\tdebug (comma) -- tok is empty...'
                        continue
                    tok = tok.strip(' ')
                    converted_tok = convert_to_parameter_type(tok, parameter_type)
                    if converted_tok is not None:
                        list_toks.append(converted_tok)
                if list_toks:
                    if len(list_toks) > 1:
                        list_toks.sort()
                        min = list_toks[0]
                        max = (list_toks[::-1])[0]
                        set = list_toks
                        if debug:
                            print '\n\t\t parameter ----------',
                            print '\n\t\tmin: ', min
                            print '\n\t\tmax: ', max
                            print '\n\t\tset: ', set

                if debug: print '\n\tdebug -- (processing commas) len(subtokens): ', len(subtokens)

                # Process range format (xx=abc, xxx=defgh)
                if '=' in token:
                    print '\n\tdebug -- processing enumerated values in set (found \'=\' in token)...'


            # Process range format (xx | xxx)
            elif '|' in token:
                if debug: print '\n\tdebug -- processing enumerated values (found \'|\' in token)...'
                subtokens = token.split('|')
                list_toks = []
                for tok in subtokens:
                    if not tok:
                        if debug: print '\n\tdebug (vertical bar) -- tok is empty...'
                        continue
                    tok = tok.strip(' ')
                    converted_tok = convert_to_parameter_type(tok, parameter_type)
                    if converted_tok is not None:
                        list_toks.append(converted_tok)
                if list_toks:
                    if len(list_toks) > 1:
                        list_toks.sort()
                        min = list_toks[0]
                        max = (list_toks[::-1])[0]
                        set = list_toks
                        if debug:
                            print '\n\t\t parameter ----------',
                            print '\n\t\tmin: ', min
                            print '\n\t\tmax: ', max
                            print '\n\t\tset: ', set

                if debug: print '\n\tdebug -- len(subtokens): ', len(subtokens)

            else:
                message = 'Unable to locate hyphen or comma in range token: %s' % token
                if debug: print '\n\t message: ', message
                raise Exception(message)

        #print '\n returning min, max and set: %r, %r, %r' % (min, max, set)
        return min, max, set

    except Exception as err:
        #print '\n debug -- parse_description: error: ', err.message
        current_app.logger.info(str(err.message))
        raise #Exception(err.message)


def convert_to_parameter_type(token, parameter_type):
    """ Convert token value to parameter_type; if failure return None. Exceptions are logged and None returned.
    """
    debug = False
    result = None
    if not token:
        return None
    if not parameter_type:
        return None

    valid_parameter_types = ['int', 'float', 'bool', 'string']
    if parameter_type not in valid_parameter_types:
        message = 'Unknown parameter_type (%s), unable to convert token.' % parameter_type
        if debug: print '\n\tdebug -- ', message
        raise Exception(message)
    try:
        if debug: print '\n\t debug -- convert parameter_type %s' % parameter_type
        if parameter_type == 'int':
            try:
                int_value = int(token)
                result = int_value
            except:
                message = 'Failed to convert value (%r) to int.' % token
                raise Exception(message)
        elif parameter_type == 'float':
            try:
                float_value = float(token)
                result = float_value
            except:
                message = 'Failed to convert value (%r) to float.' % token
                raise Exception(message)
        elif parameter_type == 'bool':
            try:
                if debug: print '\n\t debug -- boolean token to convert: ', token
                bool_value = to_bool(token)
                tmp = str(bool_value)
                result = tmp.lower()
                if debug: print '\n\t debug -- resulting boolean value: ', result
            except:
                message = 'Failed to convert value (%r) to boolean; enter \'true\' or \'false\'' % token
                raise Exception(message)

        elif parameter_type == 'string':
            try:
                result = str(token)
            except:
                message = 'Failed to convert value (%r) to string.' % (token)
                raise Exception(message)

        return result

    except Exception as err:
        if debug: print '\n convert_token (%s) exception: %s' % (parameter_type, err.message)
        current_app.logger.info(err.message)
        raise


def to_bool(value):
    """ Converts 'something' to boolean. Raises exception for invalid formats.
    Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
    Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("true"): #("yes", "y", "true",  "t", "1"):
        return 'true'
    if str(value).lower() in ("false"):
        return 'false'
    raise Exception('Invalid value for boolean conversion: ' + str(value))


# TODO UI If an instrument has no READ_WRITE parameters, the 'Apply Settings' button should be disabled.
def _c2_set_instrument_driver_parameters(reference_designator, data):
    """
    Set one or more instrument driver parameters.
    Accepts the following urlencoded parameters:
      resource: JSON-encoded dictionary of parameter:value pairs
      timeout:  in milliseconds, default value is 60000
    Sample: localhost:12572/instrument/api/reference_designator/resource [POST]

    The UI sends all READ_WRITE parameters in data; so data should never be empty.

    """
    debug = False
    response_status = {}
    response_status['status_code'] = 200
    response_status['message'] = ""
    response_status['range_errors'] = ""
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_set_instrument_driver_parameters'
    valid_args = [ 'resource', 'timeout']
    try:

        if not reference_designator:
            message = insufficient_data + ' (reference_designator is None or empty)'
            raise Exception(message)
        if not data:
            message = insufficient_data + ' (data is None or empty)'
            raise Exception(message)

        try:
            payload = convert(data)
        except Exception as err:
            message = 'Failed to process request data; %s' % str(err.message)
            raise Exception(message)

        # Validate arguments required for uframe are provided.
        for arg in valid_args:
            if arg not in payload:
                raise Exception(insufficient_data)

        # Get instrument status.
        if debug: print '\n debug -- get instrument status....'

        _status = get_instrument_status(reference_designator)
        if _status is None:
            message = 'Failed to retrieve instrument (%s) status.' % reference_designator
            if debug: print '\n debug -- message: ', message
            raise Exception(message)

        #if debug:
        print '\n ********** debug -- _status: ', json.dumps(_status, indent=4, sort_keys=True)

        # Verify payload['resource'] is not empty or None
        if payload['resource'] is None or not payload['resource']:
            message = 'The payload [resource] element is None or empty.'
            if debug: print '\n debug -- message: ', message
            raise Exception(message)

        parameter_dict, key_dict_ranges = get_range_dictionary(payload['resource'], _status, reference_designator)
        new_result, error_result = new_scrub_ui_request_data(payload['resource'], parameter_dict, key_dict_ranges)
        if error_result:
            if debug: print '\n debug ***** range error_result(%d): %s' % \
              (len(error_result), json.dumps(error_result, indent=4, sort_keys=True))

            # Create dictionary with response data and return.
            # todo - this will require status to be returned also !!!!!!!!!!! FIX *****************
            new_result = {}
            response_status['range_errors'] = error_result
            response_status['status_code'] = 400
            new_result['response'] = response_status
            print '\n -- debug result: ', json.dumps(new_result, indent=4, sort_keys=True)
            return new_result

        elif new_result is None or not new_result:
            message = 'Unable to process resource payload.'
            if debug: print '\n debug -- message: ', message
            raise Exception(message)
        if debug: print '\n debug --  (from new scrub) result(%d): %s' % (len(new_result), new_result)

        '''
        # Original
        # Scrub payload resource value using parameter type dictionary.
        result = scrub_ui_request_data(payload['resource'], parameter_dict)
        if result is None or not result:
            message = 'Unable to process resource payload (result is None or empty).'
            print '\n debug -- message: ', message
            raise Exception(message)
        print '\n debug -- result (from scrub): ', result
        '''

        # Update value of resource in payload.
        payload['resource'] = new_result

        # Send request and payload to uframe; process result
        response = _uframe_post_instrument_driver_set(reference_designator, 'resource', payload)
        if response.status_code != 200:
            message = '(%s) Failed to execute instrument driver set.' % str(response.status_code)
            print '\n debug -- message: ', message
            raise Exception(message)

        if response.content:
            try:
                response_data = json.loads(response.content)
                if debug: print '\n debug -- response_data: ', json.dumps(response_data, indent=4, sort_keys=True)
            except:
                message = 'Malformed data; not in valid json format. (C2 instrument driver set)'
                raise Exception(message)

            # Evaluate response content for error (review 'value' list in response_data )
            if response_data:
                status_code, status_type, status_message = _eval_POST_response_data(response_data, message)
                response_status['status_code'] = status_code
                response_status['message'] = status_message

        # Add response attribute information to result
        new_result['response'] = response_status

        # Get current over_all state, return in status attribute of result
        try:
            status = _c2_get_instrument_driver_status(reference_designator)
        except Exception:
            status = {}
        new_result['status'] = status

        if key_dict_ranges is None:
            key_dict_ranges = {}
        new_result['ranges'] = key_dict_ranges

        #streams = {}
        #try:
        #    streams = get_streams_dictionary(reference_designator)
        #except Exception as err:
        #    print'\n debug -- exception: ', err.message
        #new_result['streams'] = streams
        #print '\n -- debug result: ', json.dumps(new_result, indent=4, sort_keys=True)
        return new_result

    except Exception as err:
        message = str(err.message)
        #print '\n (_c2_set_instrument_driver_parameters) exception - message: ', message
        current_app.logger.info(message)
        raise


def get_range_dictionary(resource, _status, reference_designator):
    key_dict = {}
    parameter_dict = {}
    debug = False
    try:
        # Get parameters from status.
        if debug: print '\n debug -- get parameters from status....'
        _parameters = get_instrument_parameters(_status)
        if _parameters is None:
            message = 'Failed to retrieve instrument (%s) parameters from status.' % reference_designator
            if debug: print '\n debug -- message: ', message
            current_app.logger.info(message)
            raise Exception(message)

        # Create parameter type dictionary.
        if debug: print '\n debug -- create parameter dictionary....'
        _parameters_list = _parameters.keys()
        for parameter in _parameters_list:

            tmp = _parameters[parameter]
            #if debug: print '\n debug -- tmp[value]: ', tmp['value']
            parameter_dict[parameter] = str(tmp['value']['type'])

            # Create range value checking dictionary
            key_dict[parameter] = {}
            key_dict[parameter]['type'] = str(tmp['value']['type'])

            key_dict[parameter]['desc'] = str(tmp['description'])
            key_dict[parameter]['display_name'] = str(tmp['display_name'])
            '''
            if 'description' in tmp:
                key_dict[parameter]['desc'] = str(tmp['description'])
            else:
                key_dict[parameter]['desc'] = None
            if 'display_name' in tmp:
                key_dict[parameter]['display_name'] = str(tmp['display_name'])
                #print '\n debug -- display_name: ', str(tmp['display_name'])
            else:
                key_dict[parameter]['display_name'] = None
            '''
            key_dict[parameter]['min'] = None
            key_dict[parameter]['max'] = None
            key_dict[parameter]['set'] = []

        if debug: print '\n debug -- verify resource and parameter_dict have been provided....'
        if resource is None or not parameter_dict:
            message = 'The payload [resource] element is None or parameters dictionary is empty.'
            if debug: print '\n debug -- message: ', message
            current_app.logger.info(message)
            raise Exception(message)

        # Parse description to populate min, max and set attributes.
        # TODO Move (into new scrub_ui_request_data) to only populate range values for items modified.
        # TODO remove when 'min', 'max', 'set' values are provided in parameter 'value' dictionary.
        if debug: print '\n debug --- resource: ', json.dumps(resource, indent=4, sort_keys=True)
        key_dict_ranges = populate_range_values(resource, key_dict)
        if debug:
            print '\n debug ***** key_dict_ranges(%d): %s' % \
              (len(key_dict_ranges), json.dumps(key_dict_ranges, indent=4, sort_keys=True))

        return parameter_dict, key_dict_ranges

    except Exception as err:
        message = str(err.message)
        print '\n debug -- (get_range_dictionary) exception - message: ', message
        current_app.logger.info(message)
        raise


@api.route('/c2/instrument/<string:reference_designator>/get_last_particle/<string:_method>/<string:_stream>', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_last_particle(reference_designator, _method, _stream):
    """
    Get the last particle for this reference designator with method and stream name provided. If error, return error.
    Sample:
        http://localhost:4000/c2/instrument/RS10ENGC-XX00X-00-NUTNRA001/get_last_particle/streamed/nutnr_a_sample
    """
    particle = {}
    try:
        data = _c2_get_last_particle(reference_designator, _method, _stream)
        if data:
            particle = data
        return jsonify(particle)
    except Exception as err:
        current_app.logger.info(err.message)
        return bad_request(str(err.message))


def _c2_get_last_particle(rd, _method, _name):
    """ Using the reference designator, stream method and name, fetch last particle.
    Get reference designator metadata to determine time span for last particle.

    metadata: {
        "times": [
            {
                "beginTime": "2015-10-09T21:41:48.301Z",
                "count": 30,
                "endTime": "2016-02-04T23:45:57.489Z",
                "method": "streamed",
                "sensor": "RS10ENGC-XX00X-00-NUTNRA001",
                "stream": "nutnr_a_dark_sample"
            },
            {
                "beginTime": "2015-10-09T21:41:50.790Z",
                "count": 65,
                "endTime": "2016-02-04T23:45:59.971Z",
                "method": "streamed",
                "sensor": "RS10ENGC-XX00X-00-NUTNRA001",
                "stream": "nutnr_a_sample"
            },
            {
                "beginTime": "2015-10-09T21:44:18.026Z",
                "count": 12,
                "endTime": "2015-11-19T14:00:46.909Z",
                "method": "streamed",
                "sensor": "RS10ENGC-XX00X-00-NUTNRA001",
                "stream": "nutnr_a_status"
            }
        ]
    }

    """
    result = None
    debug = False
    particle = None
    metadata = None
    try:
        try:
            data = _c2_get_instrument_metadata(rd)
        except Exception as err:
            raise Exception(err.message)

        if data.status_code != 200:
            message = '(%d) Failed to get %s metadata.' % (data.status_code, rd)
            raise Exception(message)

        if data.status_code == 200:
            if data.content:
                metadata = json.loads(data.content)

        if metadata is None:
            message = 'Failed to retrieve stream (%s) contents from uframe.'
            raise Exception(message)

        time_set = process_stream_metadata_for_timeset(metadata, _method, _name)
        if time_set is None:
            message = 'Failed to obtain metadata times for reference_designator %s' % rd
            raise Exception(message)

        if debug: print '\n time_set: ', json.dumps(time_set, indent=4, sort_keys=True)

        mooring, platform, instrument = rd.split('-', 2)
        stream_type = time_set['method']
        stream_name = time_set['stream']
        formatted_end_time = time_set['endTime']
        formatted_start_time = time_set['beginTime']

        # When metadata indicates endTime and beginTime are equal, log and raise error
        if formatted_start_time == formatted_end_time:
            message = 'uFrame indicates beginTime and endTime are equal; no data to retrieve for stream (%s).' % \
                      stream_name
            raise Exception(message)

        dpa_flag = '0'
        response = get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream_name,
                                   formatted_start_time, formatted_end_time, dpa_flag)

        if response is None:
            message = 'Get stream contents failed for stream (%s).' % stream_name
            raise Exception(message)

        if response.status_code != 200:
            message = '(%s) Failed to retrieve stream (%s) contents.' % (str(response.status_code), stream_name)
            raise Exception(message)

        if response.content:
            try:
                result = response.json()
            except:
                message = 'Failed to process stream (%s) contents to json.' % stream_name
                raise Exception(message)

        # If stream contents provided sort and retrieve first item in list as particle.
        particle_metadata = {}
        particle_values = {}
        if result:
            data = sorted(result, key=itemgetter('driver_timestamp'), reverse=True)
            if data:
                particle = data[0]
                if particle:
                    if isinstance(particle, dict):
                        for k,v in particle.iteritems():
                            if is_nan(v):
                                particle_values[k] = 'NaN'
                            elif 'timestamp' in k or 'time' == k:
                                value = timestamp_to_string(v)
                                particle_values[k] = value
                            elif k == 'pk':
                                if isinstance(v, dict):
                                    if 'time' in particle['pk']:
                                        time_float = particle['pk']['time']
                                        value = timestamp_to_string(time_float)
                                        particle['pk']['time'] = value
                                particle_metadata = particle['pk']
                            else:
                                particle_values[k] = value

        particle = {}
        particle['particle_metadata'] = particle_metadata
        particle['particle_values'] = particle_values
        return particle

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise

def get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag):
    """
    Gets the bounded stream contents; returns Response object.
    Note: start_time and end_time need to be datetime objects.
    """
    try:
        if dpa_flag == '0':
            query = '?beginDT=%s&endDT=%s' % (start_time, end_time)
        else:
            query = '?beginDT=%s&endDT=%s&execDPA=true' % (start_time, end_time)
        query += '&limit=100'
        uframe_url, timeout, timeout_read = get_uframe_data_info()
        url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if not response or response is None:
            message = 'No data available from uFrame for this request. Instrument: %s, Method: %s, Stream: %s' % \
                            (instrument, stream_type, stream)
            current_app.logger.info('C2 Failed request: ' + url)
            raise Exception(message)
        if response.status_code != 200:
            message = '(%s) Failed to retrieve stream contents from uFrame.', response.status_code
            raise Exception(message)
        return response
    except ConnectionError:
        message = 'ConnectionError (uframe) for get stream contents.'
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for get stream contents.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise


def _c2_get_instrument_metadata(reference_designator):
    """ Get metadata for reference designator.

    Sample uframe qery to be made:
    http://uframe-2-test.ooi.rutgers.edu:12576/sensor/inv/CP02PMCO/WFP01/01-VEL3DK000/metadata

    Receive:
    {
      "parameters" : [ {
        "particleKey" : "time",
        "shape" : "SCALAR",
        "unsigned" : false,
        "type" : "DOUBLE",
        "stream" : "vel3d_k_wfp_instrument",
        "units" : "seconds since 1900-01-01",
        "fillValue" : "-9999999",
        "pdId" : "PD7"
        },
        . . .
        ],
      "times" : [ {
        "endTime" : "2014-11-04T22:42:21.500Z",
        "method" : "recovered_wfp",
        "count" : 4024808,
        "beginTime" : "2014-04-13T18:00:03.000Z",
        "stream" : "vel3d_k_wfp_instrument",
        "sensor" : "CP02PMCO-WFP01-01-VEL3DK000"
      }, {
        "endTime" : "2014-11-04T22:30:02.000Z",
        "method" : "recovered_wfp",
        "count" : 3106,
        "beginTime" : "2014-04-13T18:00:03.000Z",
        "stream" : "vel3d_k_wfp_metadata",
        "sensor" : "CP02PMCO-WFP01-01-VEL3DK000"
      } ]
    }
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_data_info()
        mooring, platform, instrument = reference_designator.split('-', 2)
        url = '/'.join([uframe_url, mooring, platform, instrument, 'metadata'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except ConnectionError:
        message = 'ConnectionError (uframe) for get instrument (%s) metadata.' % reference_designator
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for get instrument (%s) metadata.' % reference_designator
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def process_stream_metadata_for_timeset(metadata, method, stream):
    """
    Parse instrument metadata 'times' attribute for method and stream. Sort by greatest endTime.
    Return time_set with greatest endTime. Sample time_set returned:
        {
            "beginTime" : "2015-10-09T21:41:50.790Z",
            "endTime" : "2016-02-04T23:45:59.971Z",
            "method" : "streamed",
            "sensor" : "RS10ENGC-XX00X-00-NUTNRA001",
            "count" : 65,
            "stream" : "nutnr_a_sample"
        }
    Return dictionary of streams with start and end times when stream name does not include 'recovered' or 'playback'.

    Note: exclude stream methods which include 'playback' and 'recover'.
    Note exclude stream names which include 'metadata'.

    Input:
    {
      "parameters" : [ {
        "shape" : "SCALAR",
        "particleKey" : "time",
        "unsigned" : false,
        "type" : "DOUBLE",
        "fillValue" : "-9999999",
        "stream" : "nutnr_a_dark_sample",
        "units" : "seconds since 1900-01-01",
        "pdId" : "PD7"
      },
        . . .
      ],
      "times" : [ {
        "beginTime" : "2015-10-09T21:41:48.301Z",
        "endTime" : "2016-02-04T23:45:57.489Z",
        "method" : "streamed",
        "sensor" : "RS10ENGC-XX00X-00-NUTNRA001",
        "count" : 30,
        "stream" : "nutnr_a_dark_sample"
      }, {
        "beginTime" : "2015-10-09T21:41:50.790Z",
        "endTime" : "2016-02-04T23:45:59.971Z",
        "method" : "streamed",
        "sensor" : "RS10ENGC-XX00X-00-NUTNRA001",
        "count" : 65,
        "stream" : "nutnr_a_sample"
      }, {
        "beginTime" : "2015-10-09T21:44:18.026Z",
        "endTime" : "2015-11-19T14:00:46.909Z",
        "method" : "streamed",
        "sensor" : "RS10ENGC-XX00X-00-NUTNRA001",
        "count" : 12,
        "stream" : "nutnr_a_status"
      } ]
    }
    """
    debug = False
    result = None
    try:
        if 'times' in metadata:
            time_sets = metadata['times']
            if time_sets:
                time_int = 0
                save_time_set = None

                # Loop through all dicts in time_sets, identify most recent end time.
                for time_set in time_sets:
                    if time_set['method'] != method or time_set['stream'] != stream:
                        continue
                    _end = time_set['endTime']
                    local_timezone = tzlocal.get_localzone()
                    utc_time =  dt.datetime.strptime(_end, "%Y-%m-%dT%H:%M:%S.%fZ")
                    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
                    temp = ut(local_time)
                    if debug:
                        print '\n debug -- get local_timezone: ', local_timezone
                        print '\n debug -- utc_time: ', utc_time
                        print '\n debug -- local_time: ', local_time
                        print '\n debug -- temp: ', temp

                    # If first time...
                    if time_int == 0:
                        time_int = temp
                        save_time_set = time_set

                    # After first time_set
                    else:
                        if temp > time_int:
                            save_time_set = time_set

                # Set result
                if save_time_set is not None:
                    result = save_time_set

        return result

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


# Note: start of unix epoch (jan 1, 1900 at midnight 00:00) in seconds == 2208988800
# http://stackoverflow.com/questions/13260863/convert-a-unixtime-to-a-datetime-object-
# and-back-again-pair-of-time-conversion (url continued from previous line)
# Convert a unix time u to a datetime object d, and vice versa
def convert_from_utc(u):
    return dt.datetime.utcfromtimestamp(u)


def ut(d):
    return calendar.timegm(d.timetuple())


def get_streams_dictionary(reference_designator):
    """ Return dictionary of stream names whose value is the stream method.
    The UI will then return both the stream name and method when a 'get last particle' request is made.

    Dictionary returned:
    {
    "streams": {
        "nutnr_a_dark_sample": "streamed",
        "nutnr_a_sample": "streamed",
        "nutnr_a_status": "streamed"
    },

    """
    streams = {}
    try:
        # Get request info: stream types
        stream_types = None
        mooring, platform, instrument = reference_designator.split('-', 2)
        response = get_uframe_stream_types(mooring, platform, instrument)
        if response.status_code != 200:
            message = 'Failed to retrieve stream types for reference designator: %s' % reference_designator
            raise Exception(message)
        try:
            stream_types = response.json()
        except:
            message = 'Failed to process stream types to json for reference designator: %s' % reference_designator
            raise Exception(message)

        # For each method, get stream names
        for stream_type in stream_types:
            # for stream_type, fetch stream names
            response = get_uframe_streams(mooring, platform, instrument, stream_type)
            if response.status_code != 200:
                message = 'Failed to retrieve stream names for stream method: %s.', stream_type
                raise Exception(message)
            try:
                stream_names = response.json()
                if stream_names:
                    for stream_name in stream_names:
                        if stream_name not in streams:
                            streams[stream_name] = stream_type
            except:
                message = 'Failed to process stream names to json for stream method: %s.', stream_type
                raise Exception(message)

        #print '\n debug *** streams(%d): %s' % (len(streams), json.dumps(streams, indent=4, sort_keys=True))

        #return streams dictionary, keyed by stream_name(s); value is stream method
        return streams

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def get_uframe_stream_types(mooring, platform, instrument):
    """ Lists all the stream types
    """
    rd = None
    try:
        uframe_url, timeout, timeout_read = get_uframe_data_info()
        rd = '-'.join([mooring, platform, instrument])
        url = '/'.join([uframe_url, mooring, platform, instrument])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except ConnectionError:
        message = 'ConnectionError (uframe) for get stream methods, reference designator: %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for get stream methods, reference designator: %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise

def get_uframe_streams(mooring, platform, instrument, stream_type):
    """ Lists all the stream names
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_data_info()
        url = '/'.join([uframe_url, mooring, platform, instrument, stream_type])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except ConnectionError:
        message = 'ConnectionError (uframe) for get stream names for method %s.' % stream_type
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for get stream names for method %s.' % stream_type
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def get_instrument_status(reference_designator):
    status = None
    try:
        status = _c2_get_instrument_driver_status(reference_designator)
    except:
        pass
    return status


def get_instrument_parameters(status):
    parameters = None
    if 'value' in status:
        if 'metadata' in status['value']:
            metadata = status['value']['metadata']
            if 'parameters' in metadata:
                parameters = metadata['parameters']
    return parameters


def _uframe_post_instrument_driver_set(reference_designator, command, data):
    """
    Return the uframe response of instrument driver command and suffix provided for POST.
    example of suffix = '?command=%22DRIVER_EVENT_STOP_AUTOSAMPLE%22&timeout=60000'
    info: resource=%7B%22ave%22%3A+20%7D&timeout=6000

    Added exception processing. Was:
    except Exception as err:
        message = str(err.message)
        print '\n debug -- (_uframe_post_instrument_driver_set) err: ', str(err)
        #return _response_internal_server_error(message)
        current_app.logger.info(message)
        raise

    """
    try:
        suffix = urlencode(data)
        suffix = suffix.replace('%27', '%22')
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        url = "?".join([url, suffix])
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_post_headers())
        return response

    except ConnectionError:
        message = 'ConnectionError (uframe) for get instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for get instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


#TODO enable kwargs parameter
def _c2_instrument_driver_execute(reference_designator, data):
    """
    Command the driver to execute a capability. [POST]
    Accepts the following urlencoded parameters:
       command: capability to execute
       kwargs:  JSON-encoded dictionary specifying any necessary keyword arguments for the command
       timeout: in milliseconds, default value is 60000

    json response is constructed from /status response (as attribute 'status') and a 'response' attribute, whose format is:
        "response" : {"status_code": int, "message": ""}

    Example of response structure:
        {
            "response": { "status_code": 200, "message": "" },
            "status":
            {
              "cmd": {
                "args": [],
                "cmd": "overall_state",
                "kwargs": {}
              },
              ...
            }
        }

    In the case of ACQUIRE commands (DRIVER_EVENT_ACQUIRE_STATUS, DRIVER_EVENT_ACQUIRE_SAMPLE),
    the status block in the response contains execution results in ['status']['cmd']value[1].
        {
          "response": {
            "message": "",
            "status_code": 200
          },
          "status": {
            "cmd": {
              "args": [
                "DRIVER_EVENT_ACQUIRE_STATUS"
              ],
              "cmd": "execute_resource",
              "kwargs": {}
            },
            "time": 1431086557.084415,
            "transaction_id": 196,
            "type": "DRIVER_AYSNC_EVENT_REPLY",
            "value": [
              null,
              "Ser BBFL2W-1028\r\nVer Triplet5.20\r\nAve 7\r\nPkt 0\r\nM1d 55\r\nM2d 52\r\nM3d 49\r\nM1s
              2.100E-06\r\nM2s 1.213E-02\r\nM3s 9.090E-02\r\nSeq 0\r\nRat 19200\r\nSet 0\r\nRec 0\r\nMan 0\r\nInt
              00:30:00\r\nDat 05/08/15\r\nClk 12:02:36\r\nMst 16:33:02\r\nMem 4095"
            ]
          }
        }

    Sample response value attribute portion, using value[1] dictionary and parsing for name value pairs.
    (FLORD bench instrument)
    "value": [
        null,
        [
            {
                "driver_timestamp": 3665151633.544963,
                "internal_timestamp": 3665151502.0,
                "pkt_format_id": "JSON_Data",
                "pkt_version": 1,
                "port_timestamp": 3665151633.4370704,
                "preferred_timestamp": "port_timestamp",
                "quality_flag": "ok",
                "stream_name": "flort_d_status",
                "values": [
                    {
                        "value": "BBFL2W-1028",
                        "value_id": "serial_number"
                    },
                    {
                        "value": "Triplet5.20",
                        "value_id": "firmware_version"
                    },


    BOTPT Bench Instrument:
    "value": [
        null,
        {
            "driver_timestamp": 3665151802.462715,
            "internal_timestamp": 2209500967.0,
            "pkt_format_id": "JSON_Data",
            "pkt_version": 1,
            "port_timestamp": 3665151794.73597,
            "preferred_timestamp": "internal_timestamp",
            "quality_flag": "ok",
            "stream_name": "botpt_status",
            "values": [
                {
                    "value": "IRIS,1970/01/06 22:16:11,*APPLIED GEOMECHANICS Model MD900-T Firmware V5.2 SN-N8643 ID01\nIRIS,1970/01/06 22:16:11,*01: Vbias= 0.0000 0.0000 0.0000 0.0000\nIRIS,1970/01/06 22:16:11,*01: Vgain= 0.0000 0.0000 0.0000 0.0000\nIRIS,1970/01/06 22:16:11,*01: Vmin:  -2.50  -2.50   2.50   2.50\nIRIS,1970/01/06 22:16:11,*01: Vmax:   2.50   2.50   2.50   2.50\nIRIS,1970/01/06 22:16:11,*01: a0=    0.00000    0.00000    0.00000    0.00000    0.00000    0.00000\nIRIS,1970/01/06 22:16:11,*01: a1=    0.00000    0.00000    0.00000    0.00000    0.00000    0.00000\nIRIS,1970/01/06 22:16:11,*01: a2=    0.00000    0.00000    0.00000    0.00000    0.00000    0.00000\nIRIS,1970/01/06 22:16:11,*01: a3=    0.00000    0.00000    0.00000    0.00000    0.00000    0.00000\nIRIS,1970/01/06 22:16:11,*01: Tcoef 0: Ks=           0 Kz=           0 Tcal=           0\nIRIS,1970/01/06 22:16:11,*01: Tcoef 1: Ks=           0 Kz=           0 Tcal=           0\nIRIS,1970/01/06 22:16:12,*01: N_SAMP= 460 Xzero=  0.00 Yzero=  0.00\nIRIS,1970/01/06 22:16:12,*01: TR-PASH-OFF E99-ON  SO-NMEA-SIM XY-EP  9600 baud FV-   \nIRIS,1970/01/06 22:16:12,*9900XY-DUMP-SETTINGS",
                    "value_id": "botpt_iris_status_01"
                },
                {
                    "value": "IRIS,1970/01/06 22:16:13,*01: TBias: 9.76 \nIRIS,1970/01/06 22:16:13,*Above 0.00(KZMinTemp): kz[0]=           0, kz[1]=           0\nIRIS,1970/01/06 22:16:13,*Below 0.00(KZMinTemp): kz[2]=           0, kz[3]=           0\nIRIS,1970/01/06 22:16:13,*01: ADCDelay:  310 \nIRIS,1970/01/06 22:16:13,*01: PCA Model: 90009-01\nIRIS,1970/01/06 22:16:13,*01: Firmware Version: 5.2 Rev N\nIRIS,1970/01/06 22:16:13,*01: X Ch Gain= 1.0000, Y Ch Gain= 1.0000, Temperature Gain= 1.0000\nIRIS,1970/01/06 22:16:13,*01: Output Mode: Degrees\nIRIS,1970/01/06 22:16:13,*01: Calibration performed in Degrees\nIRIS,1970/01/06 22:16:13,*01: Control: Off\nIRIS,1970/01/06 22:16:13,*01: Using RS232\nIRIS,1970/01/06 22:16:13,*01: Real Time Clock: Not Installed\nIRIS,1970/01/06 22:16:13,*01: Use RTC for Timing: No\nIRIS,1970/01/06 22:16:13,*01: External Flash Capacity: 0 Bytes(Not Installed)\nIRIS,1970/01/06 22:16:13,*01: Relay Thresholds:\nIRIS,1970/01/06 22:16:13,*01:   Xpositive= 1.0000   Xnegative=-1.0000\nIRIS,1970/01/06 22:16:13,*01:   Ypositive= 1.0000   Ynegative=-1.0000\nIRIS,1970/01/06 22:16:13,*01: Relay Hysteresis:\nIRIS,1970/01/06 22:16:13,*01:   Hysteresis= 0.0000\nIRIS,1970/01/06 22:16:13,*01: Calibration method: Dynamic \nIRIS,1970/01/06 22:16:13,*01: Positive Limit=26.25   Negative Limit=-26.25 \nIRIS,1970/01/06 22:16:14,*01: Calibration Points:025  X: Disabled  Y: Disabled\nIRIS,1970/01/06 22:16:14,*01: Biaxial Sensor Type (0)\nIRIS,1970/01/06 22:16:14,*01: ADC: 12-bit (internal)\nIRIS,1970/01/06 22:16:14,*01: DAC Output Scale Factor: 0.10 Volts/Degree\nIRIS,1970/01/06 22:16:14,*01: Total Sample Storage Capacity: 372\nIRIS,1970/01/06 22:16:14,*01: BAE Scale Factor:  2.88388 (arcseconds/bit)\nIRIS,1970/01/06 22:16:14,*9900XY-DUMP2",
                    "value_id": "botpt_iris_status_02"
                },


    """
    debug = False
    result = {}
    response_status = {}
    response_status['status_code'] = 200
    response_status['message'] = ""
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_execute'
    quote_value = '%22'
    #valid_args = ['command', 'kwargs', 'timeout']   # r4.x?
    #valid_args = ['command', 'timeout']             # r3.x?
    valid_args = ['command']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)

        # Get instrument status.
        _status = get_instrument_status(reference_designator)
        if _status is None:
            message = 'Failed to retrieve instrument (%s) status.' % reference_designator
            raise Exception(message)

        '''
        "metadata": {
            "commands": {
                "DRIVER_EVENT_ACQUIRE_SAMPLE": {
                    "arguments": {},
                    "display_name": "Acquire Sample",
                    "return": {},
                    "timeout": 10
                },
                "DRIVER_EVENT_ACQUIRE_STATUS": {
                    "arguments": {},
                    "display_name": "Acquire Status",
                    "return": {},
                    "timeout": 10
                },

        '''
        _commands = _status['value']['metadata']['commands']
        #if debug: print '\n debug -- _commands: ', json.dumps(_commands, indent=4, sort_keys=True)
        if debug: print '\n debug -------------- _status: ', json.dumps(_status, indent=4, sort_keys=True)


        # Prepare url suffix for post (todo revisit this)
        suffix = ''
        command_name = None
        executing_acquire_command = False
        for k,v in data.iteritems():
            if debug: print '\n debug --- %s: %r' % (k,v)
            if k in valid_args:
                if k == 'command':
                    quote = quote_value
                    command_name = v
                else:
                    quote = ''
                suffix += k + '=' + quote + str(v) + quote + '&'
        suffix = suffix.strip('&')
        if debug: print '\n debug -- suffix: ', suffix


        # Get driver command timeout from status
        if command_name not in _commands:
            message = 'Failed to retrieve command (%s) timeout from status.' % command_name
            if debug: print '\n debug -- message: ', message
            raise Exception(message)

        # Get timeout from command dictionary and convert to milliseconds; default 60 seconds.
        _timeout = _commands[command_name]['timeout']
        if _timeout:
            _timeout = _timeout * 1000
        else:
            _timeout = 30000
        if debug: print '\n debug ------- (_c2_instrument_driver_execute) _timeout: ', _timeout

        # Add driver timeout to suffix for execute
        suffix += '&timeout=' + str(_timeout)

        fetch_data = False
        if 'ACQUIRE' in command_name:
            executing_acquire_command = True
            if 'SAMPLE' in command_name:
                fetch_data = True
            elif 'STATUS' in command_name:
                fetch_data = False
            else:
                # probably should just fetch status and silently fail. discuss.
                executing_acquire_command = False
                message = 'unknown ACQUIRE command: %s; return None: ' % command_name

        response = uframe_post_instrument_driver_command(reference_designator, 'execute', suffix)
        if response.status_code != 200:
            message = '(%s) execute %s failed.' % (str(response.status_code), command_name)
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)

        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except Exception:
                raise Exception('Malformed data; not in valid json format.')

            # Evaluate response content for error (review 'value' list in response_data )
            if response_data:
                if debug:
                    print '\n debug -- response_data: ', json.dumps(response_data, indent=4, sort_keys=True)
                status_code, status_type, status_message = _eval_POST_response_data(response_data, message)
                response_status['status_code'] = status_code
                response_status['message'] = status_message

        # Add response attribute information to result
        result['response'] = response_status

        # If command executed successfully, and command is type ACQUIRE, fetch stream contents
        check_state_change = False
        acquire_results = []
        if result['response']['status_code'] == 200:

            # If ACQUIRE command, retrieve status or data contents based on ACQUIRE command type;
            # return result in 'acquire_result' attribute of response.
            acquire_result = None
            if executing_acquire_command:

                # If failed to retrieve particle, populate response_status
                if not response_data:

                    if acquire_result is None:
                        message = '(%s) Failed to retrieve particle. ' % command_name
                        current_app.logger.info(message)
                        response_status['status_code'] = 400
                        response_status['message'] = message

                # Process particle retrieved
                else:
                    try:

                        # Malformed response - no attribute 'value'
                        if 'value' not in response_data:
                            message = '(%s) Error in response data: ' % command_name
                            message += ' Attribute \'value\' not provided in response data.'
                            current_app.logger.info(message)
                            response_status['status_code'] = 400
                            response_status['message'] = message

                        # Bad response - attribute 'value' is empty
                        elif not response_data['value']:
                            message = '(%s) Error in response data: ' % command_name
                            message += ' Attribute \'value\' is empty.'
                            current_app.logger.info(message)
                            response_status['status_code'] = 400
                            response_status['message'] = message

                        # If acquire command returns something other than a list...
                        elif not isinstance(response_data['value'], list):
                            message = '(%s) Error in response data: ' % command_name
                            message += ' Attribute \'value\' returned %s' % response_data['value']
                            current_app.logger.info(message)
                            response_status['status_code'] = 400
                            response_status['message'] = message

                        # If acquire command returns response_data['value'][1] == None...
                        elif len(response_data['value']) < 2:
                            message = '(%s) Error in response data: ' % command_name
                            message += ' Attribute \'value\' less than 2 items in list.'
                            current_app.logger.info(message)
                            response_status['status_code'] = 400
                            response_status['message'] = message

                        # If acquire command returns response_data['value'][1] == None...
                        elif response_data['value'][1] is None:
                            message = '(%s) Error in response data: ' % command_name
                            message += ' Attribute values list is None; should be a list of name:value pairs.'
                            current_app.logger.info(message)
                            response_status['status_code'] = 400
                            response_status['message'] = message

                        else:
                            if debug:
                                print '\n debug **************************'
                                print '\n debug -- response_data[value][1]: ', response_data['value'][1]
                                print '\n debug -- type(response_data[value][1]): ', type(response_data['value'][1])
                                print '\n debug **************************'

                            # Get acquire_result...Driver code should always return a list; under development so check type
                            acquire_result_list = []
                            if not isinstance(response_data['value'][1], list):
                                if response_data['value'][1] is not None:
                                    if debug: print '\n debug -- (1) have acquire_result....Not a list!!'
                                    acquire_result = deepcopy(response_data['value'][1])

                            # Work around until BOTPT driver code is checked in at Raytheon (handles dict)
                            else:
                                if response_data['value'][1]:
                                    if response_data['value'][1][0] is not None:
                                        if debug: print '\n debug -- (2) have acquire_result_list....'
                                        #acquire_result = deepcopy(response_data['value'][1][0])
                                        acquire_result_list = deepcopy(response_data['value'][1])
                                else:
                                    if debug: print '\n debug -- check_state_change = True '
                                    check_state_change = True

                            for acquire_result in acquire_result_list:
                                # If acquire_result is None, set response_status
                                if acquire_result is None and not check_state_change:
                                    message = '(%s) Error in response data: No results to process.' % command_name
                                    current_app.logger.info(message)
                                    response_status['status_code'] = 400
                                    response_status['message'] = message

                                if acquire_result is not None:
                                    if debug:
                                        print '\n acquire_result(%d): %s' % (len(acquire_result), acquire_result)
                                        print '\n acquire_result.keys(): ', acquire_result.keys()

                                    """
                                    If values provided, process the list of (dict) values into acquire_result.
                                    Format of value dictionary item:
                                        {"value": 0.0909, "value_id": "measurement_3_slope_value"}
                                    """

                                    # -- Process information not in 'values'
                                    keys = acquire_result.keys()
                                    if debug:
                                        print '\n debug -- Process keys in acquire_result....'
                                        print '\n debug -- keys: ', keys
                                    particle_metadata = {}
                                    for key in keys:
                                        if key != 'values':
                                            id = key
                                            value = acquire_result[id]
                                            if debug: print '\n debug -- key: %s, %r ' % (id, value)
                                            if is_nan(value):
                                                particle_metadata[id] = 'NaN'
                                            elif 'timestamp' in id or 'time' == id:
                                                if isinstance(value, float):
                                                    time_value = timestamp_to_string(value)
                                                    particle_metadata[id] = time_value
                                            else:
                                                particle_metadata[id] = value

                                    acquire_result['particle_metadata'] = particle_metadata

                                    particle_values = {}
                                    # -- Process information in 'values'
                                    if 'values' in acquire_result:
                                        if debug:
                                            print '\n debug -- Process values in acquire_result....'
                                        values = deepcopy(acquire_result['values'])
                                        #print '\n ---------- values: ', values

                                        # If executing ACQUIRE_SAMPLE (fetch_data == True) and no values,
                                        # return acquire_result as [].
                                        if not values:
                                            if fetch_data:
                                                acquire_result = []

                                        # If values, loop and process values into acquire_result
                                        else:

                                            for item in values:
                                                id = item['value_id']
                                                value = item['value']
                                                if debug: print '\n debug -- item: %s, %r ' % (id, value)
                                                if is_nan(value):
                                                    particle_values[id] = 'NaN'
                                                elif 'timestamp' in id or 'time' == id:
                                                    if debug: print '\n debug -- timestamp in ', id
                                                    time_value = timestamp_to_string(value)
                                                    particle_values[id] = time_value
                                                else:
                                                    particle_values[id] = value

                                            acquire_result['particle_values'] = particle_values

                                            del acquire_result['values']

                                        #acquire_result = [acquire_result]
                                    if acquire_result:
                                        acquire_result = {}
                                        acquire_result['particle_metadata'] = particle_metadata
                                        acquire_result['particle_values'] = particle_values
                                        acquire_results.append(acquire_result)

                    except Exception as err:
                        message = str(err.message)
                        current_app.logger.info(message)
                        response_status['status_code'] = 400
                        response_status['message'] = message

                    #if acquire_result is None:
                    if not acquire_results:
                        # Populate return status due to failure to obtain particle;
                        result['response'] = response_status
                        result['acquire_result'] = []
                    else:
                        # Set acquire_result value
                        #result['acquire_result'] = acquire_result
                        result['acquire_result'] = acquire_results

        #print '\n ***\n result: ', json.dumps(result, indent=4, sort_keys=True)

        # Get over_all state, return in status attribute of result
        #if response_status['status_code'] == 200:
        try:
            status = _c2_get_instrument_driver_status(reference_designator)
            #print '\n ***\n status: ', json.dumps(status, indent=4, sort_keys=True)

            if check_state_change:
                # verify no longer in DRIVER_STATE_COMMAND
                if debug:
                    print '\n debug -- check_state_change ......'
                    print '\n debug -- (2) status[status][value][state]: ',  status['value']['state']
                if status['value']['state'] == 'DRIVER_STATE_COMMAND':
                    message = '(%s) Error in response data:' % command_name
                    message += ' No results to process and no state change.'
                    current_app.logger.info(message)
                    response_status['status_code'] = 400
                    response_status['message'] = message

        except Exception as err:
            if debug: print '\n debug -- exception: ', err.message
            status = {}
        result['status'] = status

        #print '\n ***\n result: ', json.dumps(result, indent=4, sort_keys=True)

        return result

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise

def timestamp_to_string(time_float):
    """ Convert float to formatted time string. If failure to convert, return None.
    """
    offset = 2208988800
    formatted_time = None
    try:
        if isinstance(time_float, float):
            ts_time = convert_from_utc(time_float - offset)
            formatted_time = dt.datetime.strftime(ts_time, "%Y-%m-%dT%H:%M:%S")
        return formatted_time
    except Exception as err:
        current_app.logger.info(str(err.message))
        return None

def is_nan(x):
    return isinstance(x, float) and math.isnan(x)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private helper methods for instrument agent driver (instrument/api)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_get_instrument_driver_command(reference_designator, command):
    """ Return the uframe response of instrument command provided for GET

    2016-02-25 Added exception processing. Was:
        except Exception:
            raise
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response

    except ConnectionError:
        message = 'ConnectionError (uframe) for get instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for get instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_post_instrument_driver_command(reference_designator, command, suffix):
    """ Return the uframe response of instrument driver command and suffix provided for POST.
    Example of suffix = '?command=%22DRIVER_EVENT_STOP_AUTOSAMPLE%22&timeout=60000'
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        url = "?".join([url, suffix])
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_post_headers())
        return response
    except ConnectionError:
        message = 'ConnectionError (uframe) for post instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for post instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise

def get_uframe_info(type='instrument'):
    """ returns uframe instrument/api specific configuration information. (port 12572)
    """
    try:
        if type == 'instrument':
            uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_INST_BASE']])
        else:
            uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_PLAT_BASE']])
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        return uframe_url, timeout, timeout_read
    except ConnectionError:
        message = 'ConnectionError (uframe) for instrument/api.'
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for for instrument/api.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise

def get_uframe_data_info():
    """ returns uframe data configuration information. (port 12576)
    """
    try:
        # Use C2 server for toc info
        tmp_uframe_base = current_app.config['UFRAME_INST_URL']
        uframe_base = tmp_uframe_base.replace('12572', '12576')
        uframe_url = uframe_base + current_app.config['UFRAME_URL_BASE']
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        return uframe_url, timeout, timeout_read
    except ConnectionError:
        message = 'ConnectionError (uframe) for command and control sensor/inv.'
        current_app.logger.info(message)
        raise Exception(message)
    except ReadTimeout:
        message = 'ReadTimeout (uframe) for for command and control sensor/inv.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise


def _post_headers():
    """ urlencoded values for uframe POST.
    """
    return {"Content-Type": "application/x-www-form-urlencoded"}


def _headers():
    """ Headers for uframe POST.
    """
    return {"Content-Type": "application/json"}


def _eval_POST_response_data(response_data, msg=None):
    """
    Evaluate the value dictionary from uframe POST response data.
    Return error code, type and message.
    """
    try:
        value = None
        type = None
        if 'type' in response_data:
            type = response_data['type']
        if 'value' in response_data:
            value = response_data['value']
            # if value[0] contains int, then there was an error for command issued (verify uframe syntax)
            # if no uframe error, then int conversion will force return to continue processing
            try:
                get_int = int(  str(value[0]).decode("utf-8")  )
            except:
                return 200, type, ''

            # Process error message from uframe (stored in value dictionary)
            if value[0] != 200:
                if type:
                    message = '(%s, %s) %s' % (str(value[0]), type, value[1])
                else:
                    message = '(%s) %s' % (str(value[0]), value[1])
                return value[0], type, message
        else:
            if not msg:
                msg = 'value attribute not available in response data from uframe.'
            return 500, None, msg
    except:
        raise


def _get_toc():
    """ Returns a dictionary of arrays, moorings, platforms and instruments from uframe.
    Augmented by the UI database for vocabulary and arrays.
    """
    try:
        cached = cache.get('c2_toc')
        if cached:
            toc = cached
        else:
            toc = _compile_c2_toc()
            if toc is not None:
                cache.set('c2_toc', toc, timeout=CACHE_TIMEOUT)
        return toc

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return None


def _compile_c2_toc():
    """ Returns a dictionary of arrays, moorings, platforms and instruments from uframe.
    Augmented by the UI database for vocabulary and arrays, returns json
    """

    # Use instrument/api server for toc info
    tmp_uframe_base = current_app.config['UFRAME_INST_URL']
    uframe_base = tmp_uframe_base.replace('12572', '12576')
    UFRAME_DATA = uframe_base + current_app.config['UFRAME_URL_BASE']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    try:
        toc = {}
        mooring_list = []
        platform_list = []
        instrument_list = []
        url = "/".join([UFRAME_DATA])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            raise Exception('uframe connection cannot be made.')
        moorings = response.json()
        for mooring in moorings:
            mooring_list.append({'reference_designator': mooring,
                                 'array_code': mooring[:2],
                                 'display_name': get_display_name_by_rd(mooring)
                                 })
            url = "/".join([UFRAME_DATA, mooring])
            response = requests.get(url, timeout=(timeout, timeout_read))
            if response.status_code == 200:
                platforms = response.json()
                for platform in platforms:
                    platform_list.append({'reference_designator': "-".join([mooring, platform]),
                                          'mooring_code': mooring,
                                          'platform_code': platform,
                                          'display_name': get_display_name_by_rd("-".join([mooring, platform]))
                                          })
                    url = "/".join([UFRAME_DATA, mooring, platform])
                    response = requests.get(url, timeout=(timeout, timeout_read))
                    if response.status_code == 200:
                        instruments = response.json()
                        for instrument in instruments:
                            # Verify valid reference designator, if not skip
                            reference_designator = _get_validate_instrument_rd(mooring, platform, instrument)
                            if reference_designator is not None:
                                instrument_list.append({'mooring_code': mooring,
                                                        'platform_code': platform,
                                                        'instrument_code': instrument,
                                                        'reference_designator': reference_designator,
                                                        'display_name': get_display_name_by_rd(reference_designator=reference_designator)
                                                        })
                arrays = Array.query.all()
                toc['arrays'] = [array.to_json() for array in arrays]
                toc['moorings'] = mooring_list
                toc['platforms'] = platform_list
                toc['instruments'] = instrument_list

        return toc

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return None


def _get_validate_instrument_rd(mooring, platform, instrument):
    """ Verify an instrument reference designator is not malformed; if malformed, return None.
    """
    if mooring is None:
        return None
    if len(mooring) != 8:
        return None

    if platform is None:
        return None
    if len(platform) != 5:
        return None

    if instrument is None:
        return None
    if len(instrument) != 12:
        return None
    if '-' not in instrument:
        return None

    rd = "-".join([mooring, platform, instrument])
    if rd:
        if len(rd) != 27:
            return None
        if not _instrument_has_streams(rd):
            return None
        return rd


def _instrument_has_streams(rd):
    """ Verify an instrument reference designator has stream methods which do not contain 'recover' or 'playback'.
    """
    result = False
    methods = []
    try:

        response = _c2_get_instrument_metadata(rd)
        if response.status_code != 200:
            return False

        if response.content:
            try:
                data = json.loads(response.content)
            except Exception:
                return False

            if data is not None:
                if 'times' in data:
                    times = data['times']
                    for time_dict in times:
                        if 'method' in time_dict:
                            method = time_dict['method']
                            if method:
                                if 'recover' not in method and 'playback' not in method:
                                    if method not in methods:
                                        methods.append(method)

        if methods:
            result = True

        return result

    except Exception:
        return False


def _get_platforms(array):
    """ Returns all platforms for specified array from uframe.
    """
    try:
        dataset = _get_toc()
        if dataset:
            _platforms = dataset['platforms']
            platforms = []
            if _platforms:
                for platform in _platforms:
                    if platform['reference_designator'][0:2] == array:
                        platforms.append(platform)
            return platforms
    except:
        return None


def _get_platform(reference_designator):
    """ Returns requested platform information from uframe.
    """
    try:
        dataset = _get_toc()
        if dataset:
            platforms = dataset['platforms']
            platform_deployment = None
            for platform in platforms:
                if platform['reference_designator'] == reference_designator:
                    platform_deployment = platform
                    break
            return platform_deployment
    except:
        return None


def _get_instrument(reference_designator):
    """ Returns requested instrument information from uframe.
    """
    try:
        dataset = _get_toc()
        if dataset:
            instruments = dataset['instruments']
            _instrument = None
            for instrument in instruments:
                if instrument['reference_designator'] == reference_designator:
                    _instrument = instrument
                    break
            return _instrument
    except:
        return None


def _get_instruments(platform):
    """ Returns list of all instruments (dict) for specified platform (reference_designator).
    """
    instruments = []        # list of dictionaries
    oinstruments = []       # list of reference_designators
    dataset = _get_toc()
    _instruments = dataset['instruments']
    for instrument in _instruments:
        if platform in instrument['reference_designator']:
            if instrument['reference_designator'] not in oinstruments:
                oinstruments.append(instrument['reference_designator'])
                instruments.append(instrument)
    return instruments, oinstruments


@api.route('/c2/instrument/<string:reference_designator>/metadata', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_driver_metadata(reference_designator):
    """ Returns the instrument driver metadata as json.
    Sample: http://host:12572/instrument/api/reference_designator/metadata
    """
    metadata = []
    try:
        data = _c2_get_instrument_driver_metadata(reference_designator)
        if data:
            metadata = data
        return jsonify(metadata)
    except Exception as err:
        return bad_request(err.message)


@api.route('/c2/instrument/<string:reference_designator>/parameters', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_driver_parameters(reference_designator):
    """ Return the instrument driver parameters and current values for all parameters.

    sample: http://host:12572/instrument/api/reference_designator/resource

    - call _c2_get_instrument_driver_status, get response_data['parameters'] and response_data['state']:
            "parameters": {
                      "ave": {
                        "description": "Number of measurements for each reported value.",
                        "direct_access": true,
                        "display_name": "Measurements per Reported Value",
                        "get_timeout": 10,
                        "set_timeout": 10,
                        "startup": true,
                        "value": {
                          "default": 1,
                          "description": null,
                          "type": "int"
                        },
                        "visibility": "READ_WRITE"
                      },
                      "clk": {
                        "description": "Time in the Real Time Clock.",
                        "direct_access": false,
                        "display_name": "Time",
                        "get_timeout": 10,
                        "set_timeout": 10,
                        "startup": false,
                        "value": {
                          "description": null,
                          "type": "string",
                          "units": "HH:MM:SS"
                        },
                        "visibility": "READ_ONLY"
                      },. . .
                  }
            "state": "DRIVER_STATE_COMMAND"

    - check state value, if ok, continue
    - call _c2_get_instrument_driver_parameter_values to get value, where value is dict of parameter(s) values:
            "value": {
                        "ave": 15,
                        "clk": "21:44:21",
                        "clk_interval": "00:00:00",
                        "dat": "05/08/15",
                        "int": "00:30:00",
                        "m1d": 55,
                        "m1s": 2.1e-06,
                        "m2d": 52,
                        "m2s": 0.01213,
                        "m3d": 49,
                        "m3s": 0.0909,
                        "man": 0,
                        "mem": 4095,
                        "mst": "16:33:02",
                        "pkt": 0,
                        "rat": 19200,
                        "rec": 0,
                        "seq": 0,
                        "ser": "BBFL2W-1028",
                        "set": 0,
                        "status_interval": "00:00:00",
                        "ver": "Triplet5.20",
                        "wiper_interval": "00:00:00"
                      }
    - create response, example of response [basic] structure:
    {
        "response": { "status_code": 200, "message": "" },
        "parameters": { ... }
        "state": "DRIVER_STATE_COMMAND"
        "value": { ... }
    }
    """
    parameters = []
    try:
        data = _c2_get_instrument_driver_parameters(reference_designator)
        if data:
            parameters = data
        return jsonify(parameters)
    except Exception as err:
        return bad_request(err.message)


@api.route('/c2/instrument/<string:reference_designator>/ping', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_driver_ping(reference_designator):
    """ Get instrument driver status ('ping'). Returns json.

    This initiates a simple callback into the instrument driver class from the zeromq wrapper,
    indicating the driver is still running. Does not verify connectivity with the instrument itself.
    Sample: localhost:12572/instrument/api/reference_designator/ping

    request:    http://localhost:12572/instrument/api/RS10ENGC-XX00X-00-BOTPTA001/ping
    response:
    {"cmd": {"cmd": "driver_ping", "args": ["PONG"], "kwargs": {}}, "type": "DRIVER_ASYNC_RESULT",
    "value": "driver_ping: <mi.instrument.noaa.botpt.ooicore.driver.InstrumentDriver object at 0x7fe42207af10> PONG",
    "time": 1455057480.654446}
    """
    ping = []
    try:
        data = _c2_get_instrument_driver_ping(reference_designator)
        if data:
            ping = data
        return jsonify(ping)
    except Exception as err:
        return bad_request(err.message)


# TODO uframe does not return a response (/id/ping)
def _c2_get_instrument_driver_ping(reference_designator):
    """
    Get instrument driver status ('ping'). This initiates a simple callback into
    the instrument driver class from the zeromq wrapper, indicating the driver is still running.
    Does not verify connectivity with the instrument itself.
    Sample: localhost:12572/instrument/api/reference_designator/ping
    """
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'ping')
        if response.status_code != 200:
            raise Exception('Error retrieving instrument driver ping from uframe.')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def _c2_get_instrument_driver_metadata(reference_designator):
    """ Return the instrument driver metadata.
    Sample: localhost:12572/instrument/api/reference_designator/metadata [GET]

    Basically returns the command dictionary (lighter weight than status):
        {
          "cmd": {
            "args": [],
            "cmd": "get_config_metadata",
            "kwargs": {}
          },
          "time": 1456356157.921629,
          "type": "DRIVER_ASYNC_RESULT",
          "value": {
            "commands": {
              "DRIVER_EVENT_ACQUIRE_SAMPLE": {
                "arguments": {},
                "display_name": "Acquire Sample",
                "return": {},
                "timeout": 10
              },
              "DRIVER_EVENT_ACQUIRE_STATUS": {
                "arguments": {},
                "display_name": "Acquire Status",
                "return": {},
                "timeout": 10
              },
              "DRIVER_EVENT_CLOCK_SYNC": {
                "arguments": {},
                "display_name": "Synchronize Clock",
                "return": {},
                "timeout": 5
              },

    """
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'metadata')
        if response.status_code != 200:
            if response.content:
                raise Exception('Error retrieving instrument metadata from uframe.')
        if response.content:
            try:
                data = json.loads(response.content)
                print '\n debug -- instrument metadata: %s' % json.dumps(data, indent=4, sort_keys=True)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

'''
#original
def scrub_ui_request_data(data, parameter_types):
    """ Modify format of float, int and bool data values provided by ooi-ui.
    """
    result = {}
    try:
        if not data:
            message = 'Parameter data is empty or null.'
            raise Exception(message)
        if not parameter_types:
            message = 'Parameter parameter_types is empty or null.'
            raise Exception(message)

        for k,v in data.iteritems():
            #print '\n %s: %r (%s)' % (k,v, parameter_types[k])
            if parameter_types[k] == 'float':
                try:
                    float_value = float(v)
                    result[k] = float_value
                except:
                    message = 'Failed to convert parameter \'%s\' value of %r to float.' % (k, v)
                    current_app.logger.info(message)
                    raise Exception(message)
            elif parameter_types[k] == 'int':
                try:
                    int_value = int(v)
                    result[k] = int_value
                except:
                    message = 'Failed to convert parameter \'%s\' value of %r to int.' % (k, v)
                    current_app.logger.info(message)
                    raise Exception(message)
            elif parameter_types[k] == 'bool':
                try:
                    bool_value = bool(v)
                    tmp = str(bool_value)
                    result[k] = tmp.lower()
                except:
                    message = 'Failed to convert parameter \'%s\' value of %r to boolean.' % (k, v)
                    current_app.logger.info(message)
                    raise Exception(message)

            elif parameter_types[k] == 'string':
                try:
                    result[k] = str(v)
                except:
                    message = 'Failed to convert parameter \'%s\' value of %r to string.' % (k, v)
                    current_app.logger.info(message)
                    raise Exception(message)
            else:
                message = 'Unknown parameter type: %s' % parameter_types[k]
                current_app.logger.info(message)
                result[k] = v

        return result

    except:
        raise
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Disabled instrument/api routes and supporting methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Disabled instrument/api routes
'''
#@api.route('/c2/instrument/<string:reference_designator>/start', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_start(reference_designator):
    """
    Start an instrument agent and the corresponding driver. return json
    The interface supports two methods of encoding the start parameters, x-www-form-urlencoded and JSON.
    The required parameters are as follows:
        module:     python module containing the instrument driver to be launched
        class:      name of the python class to be run from the specified driver
        host:       hostname where the driver will be run (currently only localhost supported)
        commandPort:unique port for the zeromq command interface
        eventPort:  unique port for the zeromq event interface
    Pete anticipates that this data will be supplied by asset management and this call will
    no longer require parameters. The action itself will still require a POST call.
    Sample: localhost:12572/instrument/api/reference_designator/start
    """
    start = []
    try:
        request_data = json.loads(request.data)
        data = _c2_instrument_driver_start(reference_designator, request_data)
        if data:
            start = data
        return jsonify(start)
    except Exception as err:
        return bad_request(err.message)


#@api.route('/c2/instrument/<string:reference_designator>/stop', methods=['DELETE'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_stop(reference_designator):
    """
    Stop the specified driver and corresponding agent. Return json.
    Sample: localhost:12572/instrument/api/reference_designator/stop
    """
    stop = []
    try:
        data = _c2_instrument_driver_stop(reference_designator)
        if data:
            stop = data
        return jsonify(stop)
    except Exception as err:
        return bad_request(err.message)

#@api.route('/c2/instrument/<string:reference_designator>/initialize', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_initialize(reference_designator):
    """
    Initialize the instrument driver. Valid only from the disconnected state,
    returns the driver to the unconfigured state.
    Sample: localhost:12572/instrument/api/reference_designator/initialize
    """
    initialize = []
    try:
        data = _c2_instrument_driver_initialize(reference_designator)
        if data:
            initialize = data
        return jsonify(initialize)
    except Exception as err:
        return bad_request(err.message)

#@api.route('/c2/instrument/<string:reference_designator>/configure', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_configure(reference_designator):
    """
    Configure the instrument driver. Return json.
    Accepts the following urlencoded parameters:
        config:     Port agent config, JSON encoded
        timeout:    timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/reference_designator/configure
    """
    configure = []
    try:
        request_data = json.loads(request.data)
        data = _c2_instrument_driver_configure(reference_designator, request_data)
        if data:
            configure = data
        return jsonify(configure)
    except Exception as err:
        return bad_request(err.message)


#@api.route('/c2/instrument/<string:reference_designator>/initparams', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_initparams(reference_designator):
    """
    # Configure the instrument driver startup parameters. Returns json.
    Accepts the following urlencoded parameters:
        config:     Startup config, JSON encoded
        timeout:    timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/reference_designator/initparams
    """
    initparams = []
    try:
        request_data = json.loads(request.data)
        data = _c2_instrument_driver_initparams(reference_designator, request_data)
        if data:
            initparams = data
        return jsonify(initparams)
    except Exception as err:
        return bad_request(err.message)


#@api.route('/c2/instrument/<string:reference_designator>/connect', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_connect(reference_designator):
    """
    Command the driver to connect to the instrument. Returns json.
    Accepts the following urlencoded parameters:
        timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/reference_designator/connect
    """
    connect = [reference_designator]
    try:
        request_data = json.loads(request.data)
        data = _c2_instrument_driver_connect(reference_designator, request_data)
        if data:
            connect = data
        return jsonify(connect)
    except Exception as err:
        return bad_request(err.message)


#@api.route('/c2/instrument/<string:reference_designator>/disconnect', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_disconnect(reference_designator):
    """
    Command the driver to disconnect to the instrument. Returns json.
    Accepts the following urlencoded parameters:
        timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/reference_designator/disconnect
    """
    disconnect = []
    try:
        request_data = json.loads(request.data)
        data = _c2_instrument_driver_disconnect(reference_designator, request_data)
        if data:
            disconnect = data
        return jsonify(disconnect)
    except Exception as err:
        return bad_request(err.message)


#@api.route('/c2/instrument/<string:reference_designator>/discover', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_instrument_driver_discover(reference_designator):
    """
    Command the driver to discover the current instrument state. returns json
    Accepts the following urlencoded parameters:
        timeout:    timeout for command, in milliseconds, defaults to 60000
    Sample: http://host:12572/instrument/api/reference_designator/discover
    """
    discover = []
    try:
        request_data = json.loads(request.data)
        data = _c2_instrument_driver_discover(reference_designator, request_data)
        if data:
            discover = data
        return jsonify(discover)
    except Exception as err:
        return bad_request(err.message)


@api.route('/c2/instrument/<string:reference_designator>/capabilities', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_driver_capabilities(reference_designator):
    """
    Return the instrument driver capabilities available in the current state. Returns json.
    Sample: http://host:12572/instrument/api/reference_designator/capabilities
    """
    capabilities = []
    try:
        data = _c2_get_instrument_driver_capabilities(reference_designator)
        if data:
            capabilities = data
        return jsonify(capabilities)
    except Exception as err:
        return bad_request(err.message)


#@api.route('/c2/instrument/<string:reference_designator>/parameter_values', methods=['GET'])
#@auth.login_required
#@scope_required(u'command_control')
def c2_get_instrument_driver_parameter_values(reference_designator):
    """
    Return the instrument driver parameter values.
    sample: http://host:12572/instrument/api/reference_designator/resource
    """
    parameters = []
    try:
        data = _c2_get_instrument_driver_parameter_values(reference_designator)
        if data:
            parameters = data
        return jsonify(parameters)
    except Exception as err:
        return bad_request(err.message)
'''

# Disabled supporting functions
'''
def _c2_instrument_driver_start(reference_designator, data):
    """
    Start an instrument agent and the corresponding driver. Returns response.content as json.
    The interface supports two methods of encoding the start parameters, x-www-form-urlencoded and JSON.
    The required parameters are as follows:
         module:        python module containing the instrument driver to be launched
         class:         name of the python class to be run from the specified driver
         host:          hostname where the driver will be run (currently only localhost supported)
         commandPort:   unique port for the zeromq command interface
         eventPort:     unique port for the zeromq event interface
    Peter anticipates that this data will be supplied by asset management and this call
    will no longer require parameters. The action itself will still require a POST call.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST todo [POST]
    Sample parameters (from Jim)
    instrument: ctdpf_optode_virtual
    module: mi.instrument.virtual.driver
    klass: InstrumentDriver
    command_port: 10010
    event_port: 10011
    port_agent_config: {}
    startup_config:
        parameters:
        ctdpf_optode_sample: 1
        ctdpf_optode_status: 1
        ctdpf_optode_calibration_coefficients: 1
        ctdpf_optode_hardware: 1
        ctdpf_optode_configuration: 1
        ctdpf_optode_settings: 1

    expected_particles:
    starting_state: DRIVER_STATE_COMMAND
    script:
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_start'
    valid_args = ['module','class', 'host', 'commandPort','eventPort']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        # create post body using valid_args
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        response = uframe_start_instrument_agent_and_driver(reference_designator, payload)
        if response.status_code != 200:
            raise Exception('(%s) %s' % (str(response.status_code), response.content))
        response_data = None
        if response.content:
            if response.content == 'nope':  # todo remove
                raise Exception('Failed to start instrument agent and driver')
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise

def uframe_start_instrument_agent_and_driver(reference_designator, payload):
    """
    Start an instrument agent and the corresponding driver.
    The interface supports two methods of encoding the start parameters,
    x-www-form-urlencoded and JSON.
    The required parameters are as follows:
        module:     python module containing the instrument driver to be launched
        class:      name of the python class to be run from the specified driver
        host:       hostname where the driver will be run (currently only localhost supported)
        commandPort:unique port for the zeromq command interface
        eventPort:  unique port for the zeromq event interface
    Sample: localhost:12572/instrument/api/reference_designator/start [POST]
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        urlencode(payload)
        response = requests.post(url, timeout=(timeout, timeout_read), data=json.dumps(payload), headers=_post_headers())
        return response
    except:
        #return _response_internal_server_error()
        raise

def _c2_instrument_driver_stop(reference_designator):
    """
    Stop the specified driver and corresponding agent. Returns response.content as json.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST  [DELETE]
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_stop'
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        response = uframe_instrument_driver_stop(reference_designator)
        if response.status_code != 200:
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise


def uframe_instrument_driver_stop(reference_designator):
    """
    Stop an instrument agent and the corresponding driver.
    Sample: localhost:12572/instrument/api/reference_designator/stop
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        response = requests.delete(url, timeout=(timeout, timeout_read), headers=_headers())
        return response
    except:
        #return _response_internal_server_error()
        raise

def _c2_instrument_driver_initialize(reference_designator):
    """
    Initialize the instrument driver. Valid only from the disconnected state,
    returns the driver to the unconfigured state. Returns response.content as json.
    Sample: localhost:12572/instrument/api/reference_designator/initialize [POST]
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_initialize'
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        response = uframe_instrument_driver_initialize(reference_designator)
        if response.status_code != 200:
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise

def uframe_instrument_driver_initialize(reference_designator):
    """
    Initialize the instrument driver. Valid only from the disconnected state,
    returns the driver to the unconfigured state.
    Sample: localhost:12572/instrument/api/reference_designator/initialize [POST]
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, 'initialize'])
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_post_headers())
        return response
    except:
        #return _response_internal_server_error()
        raise

def _c2_instrument_driver_configure(reference_designator, data):
    """
    Configure the instrument driver.
    Accepts the following urlencoded parameters:
        config: Port agent config, JSON encoded
        timeout: timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/reference_designator/configure [POST]
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_configure'
    valid_args = ['config', 'timeout']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        # create post body using valid_args
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        response = uframe_post_instrument_driver_command(reference_designator, 'configure', payload)
        if response.status_code != 200:
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise

def _c2_instrument_driver_initparams(reference_designator, data):
    """
    Configure the instrument driver startup parameters.
    Accepts the following urlencoded parameters:
        config: Startup config, JSON encoded
        timeout: timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/reference_designator/initparams [POST]
    config = {'parameters': None}
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_initparams'
    valid_args = ['config', 'timeout']
    #valid_args = ['parameters', 'timeout','config']
    try:
        if not reference_designator:
            raise Exception('reference_designator parameter is empty')
        if not data:
            raise Exception('data parameter is empty')

        """
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        """
        # create post body using valid_args (data is dictionary)
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        response = uframe_set_instrument_driver_initparams(reference_designator, 'initparams', payload)
        if response.status_code != 200:
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise


# TODO Testing, remove
def uframe_set_instrument_driver_initparams(reference_designator, command, payload):
    """
    Configure the instrument driver startup parameters.
    Accepts the following urlencoded parameters:
        config: Startup config, JSON encoded
        timeout: timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/reference_designator/initparams [POST]
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        urlencode(payload)
        response = requests.post(url, timeout=(timeout, timeout_read),data=payload, headers=_post_headers())
        return response
    except Exception as err:
        #return _response_internal_server_error(str(err.message))
        raise


def _c2_instrument_driver_connect(reference_designator, data):
    """
    Command the driver to connect to the instrument.
    Accepts the following urlencoded parameters:
        timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/reference_designator/connect [POST]
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_connect'
    valid_args = ['timeout']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        # create post body using valid_args
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        response = uframe_post_instrument_driver_command(reference_designator, 'connect', payload)
        if response.status_code != 200:
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise

def _c2_instrument_driver_disconnect(reference_designator, data):
    """
    Command the driver to disconnect from the instrument.
    Accepts the following urlencoded parameters:
       timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/reference_designator/disconnect [POST]
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_disconnect'
    valid_args = ['timeout']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        # create post body using valid_args
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        response = uframe_post_instrument_driver_command(reference_designator, 'disconnect', payload)
        if response.status_code != 200:
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise

def _c2_instrument_driver_discover(reference_designator, data):
    """
    Command the driver to discover the current instrument state.
    Accepts the following urlencoded parameters:
       timeout: timeout for command, in milliseconds, defaults to 60000
    Sample:  localhost:12572/instrument/api/reference_designator/discover [POST]
    """
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in c2_instrument_driver_discover'
    valid_args = ['timeout']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        # create post body using valid_args
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        response = uframe_post_instrument_driver_command(reference_designator, 'discover', payload)
        if response.status_code != 200:
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error in 'value' list
            if response_data:
                _eval_POST_response_data(response_data, message)
        return response_data
    except:
        raise


def _c2_get_instrument_driver_capabilities(reference_designator):
    """
    Return the instrument driver capabilities available in the current state.
    Sample: localhost:12572/instrument/api/reference_designator/capabilities [GET]
    ""
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'capabilities')
        if response.status_code != 200:
            raise Exception('Error retrieving instrument capabilities from uframe.')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise
'''
'''
def _response_internal_server_error(msg=None):
    """ internal error returned as response object
    """
    message = json.dumps('"error" : "uframe request failed."')
    if msg:
        message = json.dumps(msg)
    response = make_response()
    response.content = message
    response.status_code = 500
    response.headers["Content-Type"] = "application/json"
    return response
'''
