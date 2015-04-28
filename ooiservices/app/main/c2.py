#!/usr/bin/env python
'''
API v1.0 Command and Control (C2) routes

'''
__author__ = 'Edna Donoughe'

from flask import (jsonify, current_app, make_response, request)
from ooiservices.app import cache
from ooiservices.app.main import api
from ooiservices.app.models import Array
from ooiservices.app.main.routes import get_display_name_by_rd
import json, os
import requests
from urllib import urlencode
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 array routes
# - - - - - - - - - - - - - - - - - - - - - - - -
#TODO enable auth and scope
@api.route('/c2/arrays', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_arrays():
    #Get C2 arrays, return list of array abstracts
    list_of_arrays = []
    arrays = Array.query.all()
    for array in arrays:
        item = get_array_abstract(array.array_code)
        if item:
            list_of_arrays.append(item)
    return jsonify(arrays=list_of_arrays)

#TODO enable auth and scope
@api.route('/c2/array/<string:array_code>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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

#TODO enable auth and scope; get operational status from uframe
@api.route('/c2/array/<string:array_code>/current_status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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

#TODO enable auth and scope
@api.route('/c2/array/<string:array_code>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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
#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/current_status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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
                status = _c2_get_instrument_driver_status(instrument['reference_designator'])
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

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/ports_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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

#TODO enable auth and scope
#TODO complete with commands from uframe platform/api
@api.route('/c2/platform/<string:reference_designator>/commands', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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
#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_abstract(reference_designator):
    '''
    C2 get instrument abstract
    Modified to support migration to uframe
    Sample: http://localhost:4000/c2/instrument/CP02PMCI-WFP50-50-CTDPFK001/abstract
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

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/ports_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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
# All file based methods are targeted for migration to uframe base interface.
# Each is marked for targeted migration step (A, B, C, etc)
# migration A - things that can be accomplished now with instrument/api (4.x)
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
    data = None
    try:
        tmp = "/".join([c2_data_path, filename])
        f = open(tmp, 'rb')
        data = f.read()
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
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instruments_status():
    '''
    # get status of all instrument agents, return json.
    # sample: localhost:12572/instrument/api
    '''
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
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_driver_status(reference_designator):
    '''
    Get the current overall state of the specified instrument (id is the reference designator of the instrument).
    If the query option "blocking" is specified as true, then this call will block until a state change,
    allowing for a push-like interface for web clients.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/status
    '''
    status = []
    try:
        data = _c2_get_instrument_driver_status(reference_designator)
        if data:
            status = data
        return jsonify(status)
    except Exception as err:
        return bad_request(err.message)
        #return jsonify(status)

#@api.route('/c2/instrument/<string:reference_designator>/start', methods=['POST'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_instrument_driver_start(reference_designator):
    '''
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
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/start
    '''
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
    '''
    Stop the specified driver and corresponding agent. Return json.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/stop
    '''
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
    '''
    Get instrument driver status ('ping'). Returns json.
    This initiates a simple callback into the instrument driver class from the zeromq wrapper,
    indicating the driver is still running. Does not verify connectivity with the instrument itself.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/ping
    '''
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
    '''
    Initialize the instrument driver. Valid only from the disconnected state,
    returns the driver to the unconfigured state.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/initialize
    '''
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
    '''
    Configure the instrument driver. Return json.
    Accepts the following urlencoded parameters:
        config:     Port agent config, JSON encoded
        timeout:    timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/configure
    '''
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
    '''
    # Configure the instrument driver startup parameters. Returns json.
    Accepts the following urlencoded parameters:
        config:     Startup config, JSON encoded
        timeout:    timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/initparams
    '''
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
    '''
    Command the driver to connect to the instrument. Returns json.
    Accepts the following urlencoded parameters:
        timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/connect
    '''
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
    '''
    Command the driver to disconnect to the instrument. Returns json.
    Accepts the following urlencoded parameters:
        timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/disconnect
    '''
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
    '''
    Command the driver to discover the current instrument state. returns json
    Accepts the following urlencoded parameters:
        timeout:    timeout for command, in milliseconds, defaults to 60000
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST/discover
    '''
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
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_driver_metadata(reference_designator):
    '''
    Returns the instrument driver metadata. Returns json.
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST/metadata
    '''
    metadata = []
    try:
        data = _c2_get_instrument_driver_metadata(reference_designator)
        if data:
            metadata = data
        return jsonify(metadata)
    except Exception as err:
        return bad_request(err.message)

@api.route('/c2/instrument/<string:reference_designator>/capabilities', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_driver_capabilities(reference_designator):
    '''
    Return the instrument driver capabilities available in the current state. Returns json.
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST/capabilities
    '''
    capabilities = []
    try:
        data = _c2_get_instrument_driver_capabilities(reference_designator)
        if data:
            capabilities = data
        return jsonify(capabilities)
    except Exception as err:
        return bad_request(err.message)

@api.route('/c2/instrument/<string:reference_designator>/state', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_driver_state(reference_designator):
    '''
    Return the instrument driver state. Returns json.
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST/state
    '''
    state = []
    try:
        data = _c2_get_instrument_driver_state(reference_designator)
        if data:
            state = data
        return jsonify(state)
    except Exception as err:
        return bad_request(err.message)

#@api.route('/c2/instrument/<string:reference_designator>/resource', methods=['GET'])
#@api.route('/c2/instrument/<string:reference_designator>/parameters', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_driver_parameters(reference_designator):
    '''
    Return the instrument driver parameters. returns json
    sample: http://host:12572/instrument/api/TEST-TEST-TEST/resource
    '''
    parameters = []
    try:
        data = _c2_get_instrument_driver_parameters(reference_designator)
        if data:
            parameters = data
        return jsonify(parameters)
    except Exception as err:
        return bad_request(err.message)

# TODO - this fails to return a response from uframe
#@api.route('/c2/instrument/<string:reference_designator>/parameters', methods=['POST'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_set_instrument_driver_parameters(reference_designator):
    '''
    Set one or more instrument driver parameters. Returns json.
    Accepts the following urlencoded parameters:
        resource:   JSON-encoded dictionary of parameter:value pairs
        timeout:    in milliseconds, default value is 60000
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST/resource
    '''
    parameters = []
    try:
        request_data = json.loads(request.data)
        data = _c2_set_instrument_driver_parameters(reference_designator, request_data)
        if data:
            parameters = data
        return jsonify(parameters)
    except Exception as err:
        return bad_request(err.message)

@api.route('/c2/instrument/<string:reference_designator>/execute', methods=['POST'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_instrument_driver_execute(reference_designator):
    '''
    Command the driver to execute a capability. Returns json.
    Accepts the following urlencoded parameters:
        command:    capability to execute
        kwargs:     JSON-encoded dictionary specifying any necessary keyword arguments for the command
        timeout:    in milliseconds, default value is 60000
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST/execute
    '''
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
    '''
    Get status of all instrument agents. Returns response.content as json.
    Sample: http://localhost:4000/instrument/api
    '''
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
    '''
    Returns the uframe response for status of all instrument agents.
    Sample: http://host:12572/instrument/api
    '''
    try:
        url, timeout, timeout_read = get_uframe_info()
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except:
        return _response_internal_server_error()

# todo re: blocking
def _c2_get_instrument_driver_status(reference_designator):
    '''
    Get the current overall state of the specified instrument (id is the reference designator of the instrument).
    Returns response.content as json.
    If the query option "blocking" is specified as true, then this call will block until a state change,
    allowing for a push-like interface for web clients.
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST
    '''
    try:
        data = None
        response = uframe_get_instrument_driver_status(reference_designator)
        if response.status_code !=200:
            raise Exception('error retrieving instrument overall state from uframe')
            #data = {}
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

# todo re: blocking
def uframe_get_instrument_driver_status(reference_designator):
    '''
    Returns the uframe response for status of single instrument agent
    Sample: http://host:12572/instrument/api/TEST-TEST-TEST
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except:
        return _response_internal_server_error()

def _c2_instrument_driver_start(reference_designator, data):
    '''
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
    '''
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
            #raise Exception(message)
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
    '''
    Start an instrument agent and the corresponding driver.
    The interface supports two methods of encoding the start parameters,
    x-www-form-urlencoded and JSON.
    The required parameters are as follows:
        module:     python module containing the instrument driver to be launched
        class:      name of the python class to be run from the specified driver
        host:       hostname where the driver will be run (currently only localhost supported)
        commandPort:unique port for the zeromq command interface
        eventPort:  unique port for the zeromq event interface
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/start [POST]
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        #current_app.logger.info("POST %s", url)
        urlencode(payload)
        response = requests.post(url, timeout=(timeout, timeout_read), data=json.dumps(payload), headers=_post_headers())
        return response
    except:
        return _response_internal_server_error()

def _c2_instrument_driver_stop(reference_designator):
    '''
    Stop the specified driver and corresponding agent. Returns response.content as json.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST  [DELETE]
    '''
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
    '''
    Stop an instrument agent and the corresponding driver.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/stop
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        #current_app.logger.info("DELETE %s", url)
        #print "DELETE %s" % url
        response = requests.delete(url, timeout=(timeout, timeout_read), headers=_headers())
        return response
    except:
        return _response_internal_server_error()

# TODO uframe does not return a response (/id/ping)
def _c2_get_instrument_driver_ping(reference_designator):
    '''
    Get instrument driver status ('ping'). This initiates a simple callback into
    the instrument driver class from the zeromq wrapper, indicating the driver is still running.
    Does not verify connectivity with the instrument itself.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/ping
    '''
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'ping')
        if response.status_code !=200:
            raise Exception('error retrieving instrument driver ping from uframe')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def _c2_instrument_driver_initialize(reference_designator):
    '''
    Initialize the instrument driver. Valid only from the disconnected state,
    returns the driver to the unconfigured state. Returns response.content as json.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/initialize [POST]
    '''
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
    '''
    Initialize the instrument driver. Valid only from the disconnected state,
    returns the driver to the unconfigured state.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/initialize [POST]
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, 'initialize'])
        current_app.logger.info("POST %s", url)
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_post_headers())
        return response
    except:
        return _response_internal_server_error()

def _c2_instrument_driver_configure(reference_designator, data):
    '''
    Configure the instrument driver. Returns response.content as json
    Accepts the following urlencoded parameters:
        config: Port agent config, JSON encoded
        timeout: timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/configure [POST]
    '''
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
    '''
    Configure the instrument driver startup parameters. Returns response.content as json
    Accepts the following urlencoded parameters:
        config: Startup config, JSON encoded
        timeout: timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/initparams [POST]
    config = {'parameters': None}
    '''
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_initparams'
    valid_args = ['config', 'timeout']
    #valid_args = ['parameters', 'timeout','config']
    try:
        if not reference_designator:
            raise Exception('reference_designator parameter is empty')
        if not data:
            raise Exception('data parameter is empty')

        '''
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        '''
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
    '''
    Configure the instrument driver startup parameters.
    Accepts the following urlencoded parameters:
        config: Startup config, JSON encoded
        timeout: timeout for command, in milliseconds, defaults to 2000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/initparams [POST]
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        #current_app.logger.info("POST %s", url)
        #print '\n-> url: ', url
        urlencode(payload)
        response = requests.post(url, timeout=(timeout, timeout_read),data=payload, headers=_post_headers())
        return response
    except Exception as err:
        return _response_internal_server_error(str(err.message))

def _c2_instrument_driver_connect(reference_designator, data):
    '''
    Command the driver to connect to the instrument. Returns response.content as json
    Accepts the following urlencoded parameters:
        timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/connect [POST]
    '''
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
    '''
    Command the driver to disconnect from the instrument. Returns response.content as json
    Accepts the following urlencoded parameters:
       timeout: timeout for command, in milliseconds, defaults to 60000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/disconnect todo [POST]
    '''
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
    '''
    Command the driver to discover the current instrument state. Returns response.content as json
    Accepts the following urlencoded parameters:
       timeout: timeout for command, in milliseconds, defaults to 60000
    Sample:  localhost:12572/instrument/api/TEST-TEST-TEST/discover todo [POST]
    '''
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
    '''
    Return the instrument driver metadata. Returns response.content as json
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/metadata [GET]
    '''
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'metadata')
        if response.status_code !=200:
            raise Exception('error retrieving instrument metadata from uframe')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def _c2_get_instrument_driver_capabilities(reference_designator):
    '''
    Return the instrument driver capabilities available in the current state.
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/capabilities [GET]
    '''
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'capabilities')
        if response.status_code !=200:
            raise Exception('error retrieving instrument capabilities from uframe')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def _c2_get_instrument_driver_state(reference_designator):
    '''
    Return the instrument driver state. Returns response.content as json
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/state [GET]
    '''
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

# TODO - no response from uframe (/id/resource)
def _c2_get_instrument_driver_parameters(reference_designator):
    '''
    Return the instrument driver parameters. Returns response.content as json
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/resource
    '''
    try:
        data = None
        response = uframe_get_instrument_driver_command(reference_designator, 'resource')
        if response.status_code !=200:
            raise Exception('error retrieving instrument driver resource (parameters) from uframe')
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise

def _c2_set_instrument_driver_parameters(reference_designator, data):
    '''
    Set one or more instrument driver parameters. Returns response.content as json
    Accepts the following urlencoded parameters:
      resource: JSON-encoded dictionary of parameter:value pairs
      timeout:  in milliseconds, default value is 60000
    Sample: localhost:12572/instrument/api/TEST-TEST-TEST/resource todo [POST]
    '''
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_set_instrument_driver_parameters'
    valid_args = [ 'resource', 'timeout']
    try:
        if not reference_designator:
            raise Exception(insufficient_data)
        if not data:
            raise Exception(insufficient_data)

        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                #print '-> arg %s is required, not in data' % arg
                raise Exception(insufficient_data)
        # create post body using valid_args
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        response = uframe_post_instrument_driver_command(reference_designator, 'resource', payload)
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

def _c2_instrument_driver_execute(reference_designator, data):
    '''
    Command the driver to execute a capability. Returns response.content as json. [POST]
    Accepts the following urlencoded parameters:
       command: capability to execute
       kwargs:  JSON-encoded dictionary specifying any necessary keyword arguments for the command
       timeout: in milliseconds, default value is 60000

    json response is constructed from /status response (as attribute 'status') and a 'response' attribute, whose format is:
        "response" : {"status_code": int, "message": ""}
    Example:
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
    '''
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
        '''
        # validate arguments required for uframe
        for arg in valid_args:
            if arg not in data:
                raise Exception(insufficient_data)
        '''
        '''
        # post body using valid_args
        payload = {}
        for k,v in data.iteritems():
            if k in valid_args:
                payload[k] = v
        #print '-> payload: ', payload
        '''
        # Prepare url suffix for post (todo revisit this)
        suffix = ''
        for k,v in data.iteritems():
            if k in valid_args:
                if k == 'command':
                    quote = quote_value
                else:
                    quote = ''
                suffix += k + '=' + quote + str(v) + quote + '&'
        suffix = suffix.strip('&')
        response = uframe_post_instrument_driver_command(reference_designator, 'execute', suffix)
        if response.status_code !=200:
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)
        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')
            # Evaluate response content for error (review 'value' list in response_data )
            if response_data:
                #print '-> calling _new_eval_POST_response_data'
                status_code, status_type, status_message = _new_eval_POST_response_data(response_data, message)
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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private helper methods for instrument agent driver (instrument/api)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_get_instrument_driver_command(reference_designator, command):
    '''
    Return the uframe response of instrument command provided for GET
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        #print '\n-> url: ', url
        #current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except:
        return _response_internal_server_error()

def uframe_post_instrument_driver_command(reference_designator, command, suffix):
    '''
    Return the uframe response of instrument driver command and suffix provided for POST.
    example of suffix = '?command=%22DRIVER_EVENT_STOP_AUTOSAMPLE%22&timeout=60000'
    '''
    try:
        #print '-> suffix: ', suffix
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        url = "?".join([url, suffix])
        #print '-> url: ', url
        #current_app.logger.info("POST %s", url)
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_post_headers())
        return response
    except Exception as err:
        #print '\n--> [POST] exception: ', err.message
        return _response_internal_server_error(str(err.message))

def get_uframe_info(type='instrument'):
    '''
    returns uframe specific configuration information.
    Namely, uframe_url for {instrument | platform} api, uframe timeout connect and timeout read.
    '''
    if type == 'instrument':
        uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_INST_BASE']])
    else:
        uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_PLAT_BASE']])
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read

def _response_internal_server_error(msg=None):
    # internal error returned as response object
    message = json.dumps('"error" : "uframe connection cannot be made."')
    if msg:
        message = json.dumps(msg)
    response = make_response()
    response.content = message
    response.status_code = 500
    response.headers["Content-Type"] = "application/json"
    return response

def _post_headers():
    '''
    urlencoded values for uframe POST.
    '''
    #return {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    return {"Content-Type": "application/x-www-form-urlencoded"}

def _headers():
    '''
    urlencoded values for uframe POST.
    '''
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def _eval_POST_response_data(response_data, msg):
    '''
    Evaluate the value dictionary from uframe POST response data.
    Return error code, type and message if applicable.
    '''
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
                return
            # Process error message from uframe (stored in value dictionary
            if value[0] != 200:
                if msg:
                    current_app.logger.info("POST %s", msg)
                if type:
                    raise Exception('(%s, %s) %s' % (str(value[0]),type, value[1]))
                else:
                    raise Exception('(%s) %s' % (str(value[0]),value[1]))
        return
    except:
        raise

def _new_eval_POST_response_data(response_data, msg=None):
    '''
    Evaluate the value dictionary from uframe POST response data.
    Return error code, type and message.
    '''
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
                current_app.logger.info("POST %s", message)
                return value[0], type, message
        else:
            if not msg:
                msg = 'value attribute not available in response data from uframe.'
            current_app.logger.info("POST %s", msg)
            return 500, None, msg
    except:
        raise

def server_read_timeout_error(message):
    response = jsonify({'error': 'server read timeout error', 'message': message})
    current_app.logger.info('error: 500 - %s' % message)
    response.status_code = 500
    return response

@cache.memoize(timeout=3600)
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
        #print '\n ***** Exception: ', e.message
        #raise
        return None

def _get_platforms(array):
    # Returns all platforms for specified array from uframe.
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
    # Returns requested platform information from uframe.
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
    # Returns requested instrument information from uframe.
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
    # Returns list of all instruments (dict) for specified platform (reference_designator).
    instruments = []        # list of disctionaries
    oinstruments = []       # list of reference_designators
    dataset = _get_toc()
    _instruments = dataset['instruments']
    for instrument in _instruments:
        if platform in instrument['reference_designator']:
            if instrument['reference_designator'] not in oinstruments:
                oinstruments.append(instrument['reference_designator'])
                instruments.append(instrument)
    return instruments, oinstruments
