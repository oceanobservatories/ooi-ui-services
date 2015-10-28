#!/usr/bin/env python
'''
API v1.0 Command and Control (C2) routes

'''
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app, make_response, request, g
from ooiservices.app.main import api
from ooiservices.app.models import Array
from ooiservices.app.main.routes import get_display_name_by_rd
import json, os
import requests
from urllib import urlencode
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
import datetime as dt
from ooiservices.app.models import PlatformDeployment

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
    '''
    if array_code == 'RS':
        response_dict['mission_enabled'] = 'True'
    else:
        response_dict['mission_enabled'] = 'False'
    '''
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
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
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
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
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

@api.route('/c2/platform/<string:reference_designator>/ports_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_ports_display(reference_designator):
    '''
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
    '''
    contents = []
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
    '''
    open filename, read data, close file and return data
    '''
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
    '''
    open filename, read data, close file and return data
    '''
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

# targeted for migration C
def json_get_uframe_array_operational_status(array):
    filename = "_".join([array, 'operational_status'])
    try:
        data = read_store(filename)
    except:
        return None
    return data
# targeted for migration B
def json_get_uframe_platform_commands(platform):
    filename = "_".join([platform, 'commands'])
    try:
        data = read_store(filename)
    except:
        return None
    return data
# targeted for migration C
def json_get_uframe_platforms_operational_status(array_code):
    filename = "_".join([array_code, 'operational_statuses'])
    try:
        data = read_store(filename)
    except:
        return None
    return data
# targeted for migration B
def json_get_uframe_platform_operational_status(platform):
    filename = "_".join([platform, 'operational_status'])
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
@scope_required(u'user_admin')
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
@scope_required(u'user_admin')
def c2_get_instrument_driver_status(reference_designator):
    """
    Get the current overall state of the specified instrument (id is the reference designator of the instrument).
    If the query option "blocking" is specified as true, then this call will block until a state change,
    allowing for a push-like interface for web clients.
    Sample: localhost:12572/instrument/api/reference_designator/status
    """
    status = []
    try:
        data = _c2_get_instrument_driver_status(reference_designator)
        if data:
            status = data
        return jsonify(status)
    except Exception as err:
        return bad_request(err.message)

@api.route('/c2/instrument/<string:reference_designator>/state', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
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
@scope_required(u'user_admin')
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
        return bad_request(message)

@api.route('/c2/instrument/<string:reference_designator>/execute', methods=['POST'])
@auth.login_required
@scope_required(u'user_admin')
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
        return bad_request(str(err.message))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private worker methods for instrument/api
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _c2_get_instruments_status():
    """
    Get status of all instrument agents. Returns response.content as json.
    Sample: http://localhost:4000/instrument/api
    """
    try:
        data = None
        response = uframe_get_instruments_status()
        if response.status_code !=200:
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
    except:
        return _response_internal_server_error()

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
        if response.status_code !=200:
            raise Exception('Error retrieving instrument overall state from uframe.')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                return None
                #raise Exception('Malformed data; not in valid json format.')

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
                    if result:
                        if 'value' in result:
                            if isinstance(result['value'], dict):
                                status['value']['parameters'] = result['value']

        return data
    except:
        raise

# todo re: blocking
def uframe_get_instrument_driver_status(reference_designator):
    """
    Returns the uframe response for status of single instrument agent
    Sample: http://host:12572/instrument/api/reference_designator
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as err:
        message = str(err.message)
        return _response_internal_server_error(message)


def _c2_get_instrument_driver_state(reference_designator):
    """
    Return the instrument driver state.
    Sample: localhost:12572/instrument/api/reference_designator/state [GET]
    """
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'state')
        if response.status_code !=200:
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
    """
    Return the instrument driver response, state, parameters and parameter values.
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
        if response.status_code !=200:
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
    """
    Return the uframe response of instrument command resource with payload provided for GET
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        response = requests.get(url, timeout=(timeout, timeout_read),
                                data={'resource': json.dumps('DRIVER_PARAMETER_ALL')})
        return response
    except Exception as err:
        message = str(err.message)
        return _response_internal_server_error(message)

def convert(data):
    test = dict([(str(k), v) for k, v in data.items()])
    for k,v in test.items():
        if type(v) == type({'a':1}):
            result = dict([(str(kk), vv) for kk, vv in v.items()])
            test[k] = result
    return test

def scrub_ui_request_data(data, parameter_types):
    """ Modify format of float, int and bool data values provided by ooi-ui.
    """
    debug = False
    if not data:
        message = 'Parameter data is empty or null.'
        raise Exception(message)
    if not parameter_types:
        message = 'Parameter parameter_types is empty or null.'
        raise Exception(message)

    result = {}
    try:
        for k,v in data.iteritems():
            #print '\n %s: %r (%s)' % (k,v, parameter_types[k])
            if parameter_types[k] == 'float':
                try:
                    float_value = float(v)
                    result[k] = float_value
                except:
                    message = 'Failed to convert value for %s to float' % k
                    if debug: print '\n message: ', message
                    raise Exception(message)
            elif parameter_types[k] == 'int':
                try:
                    int_value = int(v)
                    result[k] = int_value
                except:
                    message = 'Failed to convert value for %s to int' % k
                    if debug: print '\n message: ', message
                    raise Exception(message)
            elif parameter_types[k] == 'bool':
                try:
                    bool_value = bool(v)
                    tmp = str(bool_value)
                    result[k] = tmp.lower()
                except:
                    message = 'Failed to convert value for %s to bool' % k
                    if debug: print '\n message: ', message
                    raise Exception(message)
            elif parameter_types[k] == 'string':
                try:
                    result[k] = str(v)
                except:
                    message = 'Failed to convert value for %s to string' % k
                    if debug: print '\n message: ', message
                    raise Exception(message)
            else:
                message = 'Unknown parameter type: %s' % parameter_types[k]
                if debug: print '\n message: ', message
                result[k] = v

        return result

    except:
        raise

def _c2_set_instrument_driver_parameters(reference_designator, data):
    """
    Set one or more instrument driver parameters.
    Accepts the following urlencoded parameters:
      resource: JSON-encoded dictionary of parameter:value pairs
      timeout:  in milliseconds, default value is 60000
    Sample: localhost:12572/instrument/api/reference_designator/resource [POST]
    """
    debug = False
    response_status = {}
    response_status['status_code'] = 200
    response_status['message'] = ""
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_set_instrument_driver_parameters'
    valid_args = [ 'resource', 'timeout']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)

        try:
            payload = convert(data)
        except Exception as err:
            raise Exception('Failed to process request data; %s' % str(err.message))

        # Validate arguments required for uframe are provided.
        for arg in valid_args:
            if arg not in payload:
                raise Exception(insufficient_data)

        # Get instrument status.
        parameter_dict = {}
        _status = get_instrument_status(reference_designator)
        if _status is None:
            message = 'Failed to retrieve instrument (%s) status.' % reference_designator
            if debug: print '\n message: ', message
            raise Exception(message)

        # Get parameters from status.
        _parameters = get_instrument_parameters(_status)
        if _parameters is None:
            message = 'Failed to retrieve instrument (%s) parameters from status.' % reference_designator
            if debug: print '\n message: ', message
            raise Exception(message)

        # Create parameter type dictionary.
        _parameters_list = _parameters.keys()
        for parameter in _parameters_list:
            tmp = _parameters[parameter]
            parameter_dict[str(parameter)] = str(tmp['value']['type'])
        if payload['resource'] is None or not parameter_dict:
            message = 'The payload \'resource\' element is None or parameters dictionary is empty.'
            if debug: print '\n message: ', message
            raise Exception(message)

        # Scrub payload resource value using parameter type dictionary.
        result = scrub_ui_request_data(payload['resource'], parameter_dict)
        if result is None or not result:
            message = 'Unable to process resource payload (result is None or empty).'
            if debug: print '\n message: ', message
            raise Exception(message)

        # Update value of resource in payload.
        payload['resource'] = result

        # Send request and payload to uframe; process result
        response = _uframe_post_instrument_driver_set(reference_designator, 'resource', payload)
        if response.status_code !=200:
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            if debug: print '\n message: ', message
            raise Exception(message)
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error (review 'value' list in response_data )
            if response_data:
                status_code, status_type, status_message = _eval_POST_response_data(response_data, message)
                response_status['status_code'] = status_code
                response_status['message'] = status_message

        # Add response attribute information to result
        result['response'] = response_status

        # Get current over_all state, return in status attribute of result
        try:
            status = _c2_get_instrument_driver_status(reference_designator)
        except:
            status = {}
        result['status'] = status

        return result
    except:
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
    """
    # info: resource=%7B%22ave%22%3A+20%7D&timeout=6000
    try:
        suffix = urlencode(data)
        suffix = suffix.replace('%27', '%22')
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        url = "?".join([url, suffix])
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_post_headers())
        return response
    except Exception as err:
        message = str(err.message)
        return _response_internal_server_error(message)

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
    """
    result = {}
    response_status = {}
    response_status['status_code'] = 200
    response_status['message'] = ""
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_execute'
    quote_value = '%22'
    valid_args = ['command', 'kwargs', 'timeout']   # r4.x?
    valid_args = ['command', 'timeout']             # r3.x?
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)
        # Prepare url suffix for post (todo revisit this)
        suffix = ''
        command_name = None
        executing_acquire_command = False
        for k,v in data.iteritems():
            if k in valid_args:
                if k == 'command':
                    quote = quote_value
                    command_name = v
                else:
                    quote = ''
                suffix += k + '=' + quote + str(v) + quote + '&'
        suffix = suffix.strip('&')
        fetch_data = False
        if 'ACQUIRE' in command_name:
            executing_acquire_command = True
            if 'SAMPLE' in command_name:
                fetch_data = True
            elif 'STATUS' in command_name:
                fetch_data = False
            else:
                # probably should just fetch status and failover silently. discuss.
                executing_acquire_command = False
                message = 'unknown ACQUIRE command: %s; return None: ' % command_name

        response = uframe_post_instrument_driver_command(reference_designator, 'execute', suffix)
        if response.status_code !=200:
            message = '(%s) execute %s failed.' % (str(response.status_code), command_name)
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except Exception as err:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error (review 'value' list in response_data )
            if response_data:
                status_code, status_type, status_message = _eval_POST_response_data(response_data, message)
                response_status['status_code'] = status_code
                response_status['message'] = status_message

        # Add response attribute information to result
        result['response'] = response_status

        # If command executed successfully, and command is type ACQUIRE, fetch stream contents
        if result['response']['status_code'] == 200:
            # If ACQUIRE command, retrieve status or data contents based on ACQUIRE command type; return in acquire_result
            # attribute of response.
            acquire_result = None
            if executing_acquire_command:
                try:
                    acquire_result = _get_data_from_stream(reference_designator, command_name)
                    if acquire_result is None:
                        response_status['status_code'] = 400
                        response_status['message'] = '(%s) Failed to retrieve stream contents. ' % command_name
                except Exception as err:
                    message = str(err.message)
                    response_status['status_code'] = 400
                    response_status['message'] = message

                # Populate return status due to failure to obtain stream contents; response_data already populated.
                if acquire_result is None:
                    #result['status'] = response_data
                    result['response'] = response_status
                    result['acquire_result'] = []
                else:
                    result['acquire_result'] = acquire_result

        # Get over_all state, return in status attribute of result
        try:
            status = _c2_get_instrument_driver_status(reference_designator)
        except Exception as err:
            status = {}
        result['status'] = status

        return result
    except:
        raise

def _get_data_from_stream(reference_designator, command_name):

    if not reference_designator:
        raise exception('reference_designator empty')
    if not command_name:
        raise exception('command_name empty')

    result = None
    try:
        # [default] command name: DRIVER_EVENT_ACQUIRE_SAMPLE, fetch contents from 'data' stream
        stream_key = 'data'

        # command name: DRIVER_EVENT_ACQUIRE_STATUS, fetch contents from 'status' stream
        if 'STATUS' in command_name:
            stream_key = 'status'

        # Get request info: stream types
        stream_types = None
        mooring, platform, instrument = reference_designator.split('-', 2)
        response = get_uframe_stream_types(mooring, platform, instrument)
        if response.status_code != 200:
            message = 'Failed to retrieve stream types.'
            raise Exception(message)
        try:
            stream_types = response.json()
        except:
            message = 'Failed to process stream types to json.'
            raise Exception(message)

        # Process stream types list and identify target stream name;
        stream_type = None
        # If only one stream type, use it
        if len(stream_types) > 0:
            if len(stream_types) == 1:
                stream_type = stream_types[0]
            # multiple stream_types - walk until find first instance of stream name to satisfy request (revisit!)
            else:
                #print '\n -- multiple stream types - violation of agreed upon interface rules! discuss.'
                stream_type = stream_types[0]
        else:
            # error, no stream_types to process
            message = 'Failed to retrieve stream names.'
            raise Exception(message)

        # for stream_type, fetch stream names
        response = get_uframe_streams(mooring, platform, instrument, stream_type)
        if response.status_code != 200:
            message = 'Failed to retrieve stream names.'
            raise Exception(message)
        try:
            stream_names = response.json()
        except:
            message = 'Failed to process stream names to json.'
            raise Exception(message)

        # Process stream names list and identify target stream name based on ACQUIRE request type
        stream_name = None
        for stream in stream_names:
            if stream_key in stream:
                stream_name = stream
                break

        if stream_name is None:
            message = 'Failed to identify stream name to process \'%s\' request.' % command_name
            raise Exception(message)

        # Prepare to retrieve stream contents for past 60 seconds
        X = 60
        end_time = dt.datetime.now()
        start_time = end_time - dt.timedelta(seconds=X)
        formatted_end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
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
                error_check = json.dumps(response.content)
                if 'Error' in error_check or 'HTTPConnectionPool' in error_check or 'Read timed out' in error_check:
                    message = 'Failed to retrieve valid stream (%s) contents; uframe error: %s.' % (stream_name, error_check)
                    raise Exception(message)
                else:
                    try:
                        result = response.json()
                    except:
                        message = 'Failed to process stream (%s) contents to json.' % (stream_name)
                        raise Exception(message)
            except:
                raise
        else:
            message = 'Failed to retrieve stream (%s) contents from uframe'
            raise Exception(message)

    except Exception as err:
        message = str(err.message)
        raise Exception(message)

    return result

def get_uframe_stream_types(mooring, platform, instrument):
    """
    Lists all the stream types
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_data_info()
        url = '/'.join([uframe_url, mooring, platform, instrument])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as err:
        message = str(err.message)
        return _response_internal_server_error(message)

def get_uframe_streams(mooring, platform, instrument, stream_type):
    """
    Lists all the streams
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_data_info()
        url = '/'.join([uframe_url, mooring, platform, instrument, stream_type])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as err:
        message = str(err.message)
        return _response_internal_server_error(message)

def get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag):
    """
    Gets the bounded stream contents, start_time and end_time need to be datetime objects; returns Respnse object.
    """
    try:
        if dpa_flag == '0':
            query = '?beginDT=%s&endDT=%s' % (start_time, end_time)
        else:
            query = '?beginDT=%s&endDT=%s&execDPA=true' % (start_time, end_time)
        uframe_url, timeout, timeout_read = get_uframe_data_info()
        url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if not response:
            message = 'No data available from uFrame for this request.'
            #print '\n*** message: ', message
            raise Exception(message)
        if response.status_code != 200:
            message = '(%s) failed to retrieve stream contents from uFrame.', response.status_code
            #print '\n*** message: ', message
            raise Exception(message)
        return response
    except Exception as err:
        message = str(err.message)
        #print '\n*** (exception) message: ', message
        return _response_internal_server_error(message)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private helper methods for instrument agent driver (instrument/api)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_get_instrument_driver_command(reference_designator, command):
    """
    Return the uframe response of instrument command provided for GET
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as err:
        message = str(err.message)
        return _response_internal_server_error(message)

def uframe_post_instrument_driver_command(reference_designator, command, suffix):
    """
    Return the uframe response of instrument driver command and suffix provided for POST.
    example of suffix = '?command=%22DRIVER_EVENT_STOP_AUTOSAMPLE%22&timeout=60000'
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        url = "?".join([url, suffix])
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_post_headers())
        return response
    except Exception as err:
        message = str(err.message)
        return _response_internal_server_error(message)

def get_uframe_info(type='instrument'):
    """
    returns uframe instrument/api specific configuration information. (port 12572)
    """
    if type == 'instrument':
        uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_INST_BASE']])
    else:
        uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_PLAT_BASE']])
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read

def get_uframe_data_info():
    """
    returns uframe data configuration information. (port 12576)
    """
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read

def _response_internal_server_error(msg=None):
    # internal error returned as response object
    message = json.dumps('"error" : "uframe request failed."')
    if msg:
        message = json.dumps(msg)
    response = make_response()
    response.content = message
    response.status_code = 500
    response.headers["Content-Type"] = "application/json"
    return response

def _post_headers():
    """
    urlencoded values for uframe POST.
    """
    return {"Content-Type": "application/x-www-form-urlencoded"}

def _headers():
    """
    for uframe POST.
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
    """
    Returns a dictionary of arrays, moorings, platforms and instruments from uframe.
    Augmented by the UI database for vocabulary and arrays.
    :return: json
    """
    UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
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
                            reference_designator = "-".join([mooring, platform, instrument])
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
    except Exception as e:
        return None


def _get_platforms(array):
    # Returns all platforms for specified array from uframe.
    try:
        dataset = _get_toc()
        #dataset = get_structured_toc()
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
    # Returns requested platform information from uframe.
    try:
        dataset = _get_toc()
        #dataset = get_structured_toc()
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
    # Returns requested instrument information from uframe.
    try:
        dataset = _get_toc()
        #dataset = get_structured_toc()
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
    # Returns list of all instruments (dict) for specified platform (reference_designator).
    instruments = []        # list of dictionaries
    oinstruments = []       # list of reference_designators
    dataset = _get_toc()
    #dataset = get_structured_toc()
    _instruments = dataset['instruments']
    for instrument in _instruments:
        if platform in instrument['reference_designator']:
            if instrument['reference_designator'] not in oinstruments:
                oinstruments.append(instrument['reference_designator'])
                instruments.append(instrument)
    return instruments, oinstruments


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Disabled instrument/api routes and supporting methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
'''
#@api.route('/c2/instrument/<string:reference_designator>/start', methods=['POST'])
#@auth.login_required
#@scope_required(u'user_admin')
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
#@scope_required(u'user_admin')
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


#@api.route('/c2/instrument/<string:reference_designator>/ping', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_driver_ping(reference_designator):
    """
    Get instrument driver status ('ping'). Returns json.
    This initiates a simple callback into the instrument driver class from the zeromq wrapper,
    indicating the driver is still running. Does not verify connectivity with the instrument itself.
    Sample: localhost:12572/instrument/api/reference_designator/ping
    """
    ping = []
    try:
        data = _c2_get_instrument_driver_ping(reference_designator)
        if data:
            ping = data
        return jsonify(ping)
    except Exception as err:
        return bad_request(err.message)


#@api.route('/c2/instrument/<string:reference_designator>/initialize', methods=['POST'])
#@auth.login_required
#@scope_required(u'user_admin')
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
#@scope_required(u'user_admin')
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
#@scope_required(u'user_admin')
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
#@scope_required(u'user_admin')
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
#@scope_required(u'user_admin')
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
#@scope_required(u'user_admin')
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


@api.route('/c2/instrument/<string:reference_designator>/metadata', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_instrument_driver_metadata(reference_designator):
    """
    Returns the instrument driver metadata. Returns json.
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

@api.route('/c2/instrument/<string:reference_designator>/capabilities', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
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
'''
'''
#@api.route('/c2/instrument/<string:reference_designator>/parameters', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_driver_parameters(reference_designator):
    """
    Return the instrument driver parameters and current values for all parameters.
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

#@api.route('/c2/instrument/<string:reference_designator>/parameter_values', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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
        return _response_internal_server_error()

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
        if response.status_code !=200:
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
        return _response_internal_server_error()


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
        if response.status_code !=200:
            raise Exception('Error retrieving instrument driver ping from uframe.')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
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
        if response.status_code !=200:
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
        return _response_internal_server_error()

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
        if response.status_code !=200:
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
        if response.status_code !=200:
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
        return _response_internal_server_error(str(err.message))


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
        if response.status_code !=200:
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
        if response.status_code !=200:
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
        if response.status_code !=200:
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

def _c2_get_instrument_driver_metadata(reference_designator):
    """
    Return the instrument driver metadata.
    Sample: localhost:12572/instrument/api/reference_designator/metadata [GET]
    """
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'metadata')
        if response.status_code !=200:
            if response.content:
                raise Exception('Error retrieving instrument metadata from uframe.')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
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
        if response.status_code !=200:
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