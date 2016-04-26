#!/usr/bin/env python
"""
API v1.0 Command and Control (C2) routes
"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app, request
from ooiservices.app import cache
from ooiservices.app.decorators import scope_required
from ooiservices.app.main import api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.routes import get_display_name_by_rd, get_long_display_name_by_rd
from ooiservices.app.models import Array
import json, os
import requests
import requests.exceptions
from requests.exceptions import ConnectionError, Timeout
from datetime import datetime as dt
from copy import deepcopy
import datetime as dt
import calendar
import pytz
import tzlocal
from operator import itemgetter
import math

CACHE_TIMEOUT = 86400


# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 array routes
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/arrays', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_arrays():
    """ Get C2 arrays, return list of array abstracts
    """
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
    """ Get C2 array abstract (display), return abstract
    """
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    response_dict = get_array_abstract(array_code)
    return jsonify(abstract=response_dict)


def get_array_abstract(array_code):
    """ Get array abstract using valid array_code; CHECK array_code before calling
    """
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
    """ C2 get array Current Status tab contents, return current_status_display
    """
    contents = []
    array_info = {}
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('Unknown array (array_code: \'%s\')' % array_code)

    toc = _compile_c2_toc()
    if toc is not None:
        cache.set('c2_toc', toc, timeout=CACHE_TIMEOUT)
    """
        print "[+] C2 toc cache reset..."
    else:
        print "[-] Error in C2 toc cache update"
    """

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
    """ C2 get array history, return history
    """
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
    """ C2 get platform abstract, return abstract.
    """
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
    """
    Get C2 platform Current Status tab contents, return current_status_display.
    Was: #status = _c2_get_instrument_driver_status(instrument['reference_designator'])
    """
    start = dt.datetime.now()
    timing = False
    contents = []
    platform_info = {}
    platform_deployment = _get_platform(reference_designator)
    if platform_deployment:
        platform_code = "-".join([platform_deployment['mooring_code'], platform_deployment['platform_code'] ])
        # Get instruments for this platform
        instruments, oinstruments = _get_instruments(platform_code)
        for instrument in instruments:
            istart = dt.datetime.now()
            row = {}
            if not instrument['display_name']:
                row['display_name'] = instrument['reference_designator']
            else:
                row['display_name'] = instrument['display_name']
            row['reference_designator'] = instrument['reference_designator']

            # Get instrument operational status based on instrument driver and agent status
            status = _get_instrument_operational_status(instrument['reference_designator'])

            row['operational_status'] = status
            platform_info[instrument['reference_designator']] = row
            if timing:
                iend = dt.datetime.now()
                iexecution_time = str(iend-istart)
                message = '\t debug --- Execution time:  %s ' % iexecution_time
                print '\n', message
        # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
        # 'data' == rows for initial grid ('Current Status')
        for instrument_reference_designator in oinstruments:
            if instrument_reference_designator in platform_info:
                contents.append(platform_info[instrument_reference_designator])
    if timing:
        end = dt.datetime.now()
        execution_time = str(end-start)
        message = '\t debug --- Total Execution time:  %s ' % execution_time
        print '\n', message

    return jsonify(current_status_display=contents)


def _get_instrument_operational_status(rd):
    """ Get instrument operational status, using ping and instrument/api/rd.
    """
    debug = False
    status = 'Unknown'
    offline_driver_states = ['DRIVER_STATE_UNCONFIGURED', 'DRIVER_STATE_DISCONNECTED', 'DRIVER_STATE_INST_DISCONNECTED']
    try:
        # If ping result is empty, instrument driver offline; otherwise instrument driver online
        temp = _c2_get_instrument_driver_ping(rd)
        if not temp:
            status = 'Offline'
        else:
            # instrument driver is running, check instrument agent...
            _status = get_instrument_status(rd)
            if _status:
                if 'value' in _status:
                    if 'state' in _status['value']:
                        if _status['value']['state']:
                            current_driver_state = _status['value']['state']
                            if current_driver_state in offline_driver_states:
                                status = 'Offline'
                            else:
                                status = 'Online'
                        else:
                            status = 'Unknown'
            else:
                status = 'Offline'
                message = 'Instrument driver running; instrument status returned empty state.'
                current_app.logger.warning(message)

        if debug: print '\n debug --- operational status: ', status
        return status
    except Exception as err:
        if debug: print '\n debug --- Exception - operational status: ', 'Unknown'
        current_app.logger.warning(err.message)
        return 'Unknown'

@api.route('/c2/platform/<string:reference_designator>/history', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_history(reference_designator):
    """ C2 get platform history
    """
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
    """ Get C2 platform Ports tab contents, return ports_display ([{},{},...]
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
    """ Get C2 platform commands return commands [{},{},...]
    """
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
    """ C2 get instrument abstract.
    Modified to support migration to uframe
    Sample: http://localhost:4000/c2/instrument/reference_designator/abstract
    Was: status = _c2_get_instrument_driver_status(instrument_deployment['reference_designator'])
    """
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
            status = _get_instrument_operational_status(instrument_deployment['reference_designator'])
            response_dict['operational_status'] = status
    except Exception, err:
        return bad_request(err.message)
    return jsonify(abstract=response_dict)


@api.route('/c2/instrument/<string:reference_designator>/history', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_history(reference_designator):
    """ C2 get instrument history, return history
    where history = { 'event': [], 'command': [], 'configuration':[] })
    """
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
    """ Get C2 instrument Ports tab contents, return ports_display
    Modified for migration to uframe
    """
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

        status = _get_instrument_operational_status(instrument_deployment['reference_designator'])
        row['port_status'] = status

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
    """ C2 make fake history for event, command and configuration
    """
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
    """ Get status of all instrument agents, return json.
    Sample: localhost:12572/instrument/api
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
    """ Get the current overall state of the specified instrument (id is the instrument reference designator).
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
        message = str(err.message)
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/instrument/<string:reference_designator>/state', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_driver_state(reference_designator):
    """ Return the instrument driver state. Returns json.
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
    """ Set one or more instrument driver parameters. Returns json.
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
    """ Command the driver to execute a capability. Returns json.
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
    """ Returns the uframe response for status of all instrument agents.
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


def _c2_get_instrument_driver_status(reference_designator):
    """ Get the current overall state of the specified instrument (id is the instrument reference designator).

    Sample: http://host:12572/instrument/api/reference_designator
            http://host:12572/instrument/api/RS10ENGC-XX00X-00-NUTNRA001

    Will NOT be doing any blocking:
    If the query option "blocking" is specified as true, then this call will block until a state change,
    allowing for a push-like interface for web clients.
    """
    debug = False
    try:
        # Get status
        data = None
        try:
            response = uframe_get_instrument_driver_status(reference_designator)
        except Exception as err:
            message = 'Error retrieving instrument overall state from uframe. Error: %s' % str(err)
            raise Exception(message)

        # No response
        if response is None:
            message = 'Error retrieving instrument overall state from uframe.'
            raise Exception(message)

        # Bad response
        if response.status_code != 200:
            message = 'Error retrieving instrument overall state from uframe.'
            raise Exception(message)

        # Have a response, parse response content
        if response.content:
            try:
                data = json.loads(response.content)
            except:
                message = 'Malformed data; not in valid json format.'
                current_app.logger.info(message)
                return None



        # If data received in response, process.
        if data is None:
            message = 'No response content returned for status (from instrument/api/%s).' % reference_designator
            raise Exception(message)

        if debug: print '\n /commands execute data: ', json.dumps(data, indent=4, sort_keys=True)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add attribute streams and display_parameters, both dictionaries.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if data:
            # - - - - - - - - - - - - - - - - - - - - - -
            # Get streams
            # - - - - - - - - - - - - - - - - - - - - - -
            streams = {}
            try:
                streams = get_streams_dictionary(reference_designator)
            except Exception as err:
                message = 'Exception from get_streams_dictionary: %s' % str(err)
                current_app.logger.info(message)
                pass
            data['streams'] = streams

            # - - - - - - - - - - - - - - - - - - - - - -
            # Get READ_WRITE display_parameters for pull downs
            # - - - - - - - - - - - - - - - - - - - - - -
            try:
                _params = None
                if data['value']['metadata']:
                    _params = data['value']['metadata']['parameters']
                #print '\n debug -- (1) params: ', _params
                temp = {}
                if _params:
                    temp = get_parameter_display_values(_params)
                data['parameter_display_values'] = temp
            except Exception as err:
                message = 'Exception from get_parameter_display_values: %s' % str(err)
                current_app.logger.info(message)
                data['parameter_display_values'] = {}
                pass

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get READ_ONLY and IMMUTABLE display_parameters for pull downs
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            try:
                _params = None
                if data['value']['metadata']:
                    _params = data['value']['metadata']['parameters']
                #print '\n debug -- (2) params: ', _params
                temp = {}
                if _params:
                    temp = get_ro_parameter_display_values(_params)
                data['ro_parameter_display_values'] = temp
            except Exception as err:
                message = 'Exception from get_ro_parameter_display_values: %s' % str(err)
                current_app.logger.info(message)
                data['ro_parameter_display_values'] = {}
                pass

        return data
    except Exception:
        raise


def uframe_get_instrument_driver_status(reference_designator):
    """ Returns the uframe response for status of single instrument agent.
    Sample: http://host:12572/instrument/api/reference_designator
    """
    debug = False
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator])
        if debug: print '\n debug --- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))

        if response is None:
            message = 'instrument driver status returned None.'
            current_app.logger.info(message)
            raise Exception(message)
        return response
    except ConnectionError:
        message = 'ConnectionError for get instrument driver status, reference designator: %s.' % reference_designator
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get instrument driver status, reference designator: %s.' % reference_designator
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        if err is None:
            message = 'uframe_get_instrument_driver_status failed, response of None'
        else:
            message = '[uframe_get_instrument_driver_status] %s' % str(err.message)
        current_app.logger.info(message)
        raise Exception(message)


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

    #====================================================== DEPRECATE THE PARAMETER VALUES UPDATE ==============
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
    #====================================================== DEPRECATE THE PARAMETER VALUES UPDATE ==============

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

        # Error: No instrument state (not defined); retry
        if state is None:
            response_status['status_code'] = 400
            response_status['message'] = "unable to determine instrument state; retry."
            data['response'] = response_status
            data['value'] = {}
            return data

        data['response'] = response_status
        return data

    except:
        raise


def _c2_get_instrument_driver_parameter_values(reference_designator):
    """ Return the instrument driver parameter values.
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
            message = 'Error retrieving instrument driver resource (parameters) from uframe.'
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


def populate_and_check_range_values(data, key_dict):
    """ Process key_dict to populate attributes 'min', 'max' and 'set' for each read_write parameter.

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
    valid_parameter_types = ['int', 'float', 'bool', 'string']
    try:
        result = {}
        for k, v in data.iteritems():

            display_name = key_dict[k]['display_name']
            range = key_dict[k]['range']
            parameter_type = key_dict[k]['type']
            if parameter_type not in valid_parameter_types:
                message = 'Unknown parameter type (%s), valid types: %s' % (parameter_type, valid_parameter_types)
                current_app.logger.info(message)
                result[k] = {'min': None, 'max': None, 'set': None, 'display_name': display_name}
                continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If range is None (not provided in parameter dictionary)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if range is None:
                result[k] = {}
                result[k]['min'] = None
                result[k]['max'] = None
                result[k]['set'] = []
                result[k]['display_name'] = display_name

                message = '(%s) range not provided.' % k
                #current_app.logger.info(message)
                continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Range provided in parameter dictionary
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            try:
                result[k] = {}
                result[k]['min'] = None
                result[k]['max'] = None
                result[k]['set'] = []
                result[k]['display_name'] = display_name

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Process range - type list
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                if isinstance(range, list):

                    # If list, requires exactly 2 values - one for min and one for max
                    if len(range) != 2:
                        message = '(%s) Invalid attribute \'range\' from uframe, require exactly two (2) values.' % k
                        current_app.logger.info(message)
                        result[k] = {'min': None, 'max': None, 'set': None, 'display_name': display_name}
                        continue

                    min = range[0]
                    max = range[1]
                    set = []

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Process range - type dict
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                elif isinstance(range, dict):

                    min = None
                    max = None
                    set = []
                    if range:
                        keys = range.values()
                        keys.sort()
                        set = keys

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Process range - type unknown
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                else:
                    result[k] = {'min': None, 'max': None, 'set': None, 'display_name': display_name}
                    continue

                result[k]['display_name'] = display_name
                result[k]['min'] = min
                result[k]['max'] = max
                result[k]['set'] = set
                result[k]['display_name'] = display_name

            except Exception as err:
                current_app.logger.info(str(err.message))
                continue

        return result

    except Exception as err:
        current_app.logger.info(err.message)
        raise

def scrub_ui_request_data(data, parameter_types, ranges):
    """ Modify format of float, int and bool data values provided by ooi-ui.
    Validate specific values against ranges, if ranges provided.

    Inputs:
    data                dict    Represents the payload['resource'], or values for READ_WRITE parameters sent from UI.
    parameter_types     dict    Parameter type values used for type validation and conversion.
    ranges              dict    Dictionary (keyed by parameter code) where dict contains parameter min, max, set.

    Outputs:
    result              dict    Converted payload parameter and values after range checking has been applied.
    error_result        dict    Dictionary of error messages to be reported in UI.

    Ranges errors reported in error_result; format of error_result dict, key is parameter code:
        . . .
        "range_errors": {
                "a_cutoff": {
                    "display_name": "Absorbance Cutoff",
                    "message": "Parameter (a_cutoff) value 0.0001 must be between 0.01 and 10.0."
                },
                "brmtrace": {
                    "display_name": "Bromide Tracing",
                    "message": "Failed to convert parameter (brmtrace) value (u'trueblah') to boolean."
                },
                "countdwn": {
                    "display_name": "Countdown",
                    "message": "Parameter (countdwn) value 15000 must be between 0 and 3600."
                },
                "intadmax": {
                    "display_name": "Integration Time Max",
                    "message": "Parameter (intadmax) value 0 must be between 1 and 20."
                }
            },
        . . .

    """
    result = {}
    error_result = {}
    try:
        if not data:
            message = 'Parameter data is empty.'
            raise Exception(message)
        if not parameter_types:
            message = 'Parameter parameter_types is empty.'
            raise Exception(message)

        for k,v in data.iteritems():

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process float value; Convert value provided; on error, record error.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if parameter_types[k] == 'float':
                try:
                    float_value = float(v)
                except:
                    display_name = 'unknown'
                    if k in ranges:
                        display_name = ranges[k]['display_name']
                    message = 'Failed to convert parameter (%s) value (%r) to float.' % (k, v)
                    error_result[k] = {'display_name': display_name, 'message': message}
                    continue

                if k in ranges:
                    min_error = False
                    max_error = False

                    # Determine min and max for ranges
                    range_min = ranges[k]['min']
                    range_max = ranges[k]['max']
                    range_set = ranges[k]['set']
                    display_name = ranges[k]['display_name']

                    # Range check data value entered against list of valid floats
                    if range_set:
                        if float_value in range_set:
                            result[k] = float_value
                        else:
                            message = 'Parameter (%s) has invalid float value %r, not one of %s.' % \
                                      (k, float_value, range_set)
                            error_result[k] = {'display_name': display_name, 'message': message}
                            continue

                    # Range check data value entered against min range value
                    if range_min is not None:
                        if float_value < range_min:
                            min_error = True
                            message = 'Parameter (%s) value %r must be between %r and %r.' % \
                                    (k, float_value, range_min, range_max)
                            error_result[k] = {'display_name': display_name, 'message': message}

                    # Range check data value entered against min range value
                    if range_max is not None:
                        if float_value > range_max:
                            max_error = True
                            message = 'Parameter (%s) value %r must be between %r and %r.' % \
                                  (k, float_value, range_min, range_max)
                            error_result[k] = {'display_name': display_name, 'message': message}

                    if min_error or max_error:
                        continue

                    result[k] = float_value

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process int value; Convert value provided; on error, record error.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif parameter_types[k] == 'int':
                try:
                    int_value = int(v)
                except:
                    display_name = 'unknown'
                    if k in ranges:
                        display_name = ranges[k]['display_name']
                    message = 'Failed to convert parameter (%s) value (%r) to int.' % (k, v)
                    error_result[k] = {'display_name': display_name, 'message': message}
                    continue

                # If there are range values for this parameter, then perform range checking.
                if k in ranges:
                    min_error = False
                    max_error = False

                    # Determine min and max for ranges
                    range_min = ranges[k]['min']
                    range_max = ranges[k]['max']
                    range_set = ranges[k]['set']
                    display_name = ranges[k]['display_name']
                    if range_set:
                        if int_value in range_set:
                            result[k] = int_value
                        else:
                            message = 'Parameter (%s) has invalid int value \'%r\', not one of %s.' % \
                                      (k, int_value, range_set)
                            error_result[k] = {'display_name': display_name, 'message': message}
                            continue

                    # Range check data value entered against min range value
                    if range_min is not None:
                        if int_value < range_min:
                            min_error = True
                            message = 'Parameter (%s) value %r must be between %r and %r.' % \
                                  (k, int_value, range_min, range_max)
                            error_result[k] = {'display_name': display_name, 'message': message}

                    # Range check data value entered against max range value
                    if range_max is not None:
                        if int_value > range_max:
                            max_error = True
                            message = 'Parameter (%s) value %r must be between %r and %r.' % \
                                  (k, int_value, range_min, range_max)
                            error_result[k] = {'display_name': display_name, 'message': message}

                    if min_error or max_error:
                        continue

                    result[k] = int_value

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process boolean value; Convert value provided, on error raise exception.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif parameter_types[k] == 'bool':
                display_name = 'unknown'
                if k in ranges:
                    display_name = ranges[k]['display_name']
                try:
                    bool_value = to_bool(v)
                    result[k] = bool_value
                except:
                    message = 'Failed to convert parameter (%s) value (%r) to boolean.' % (k, v)
                    error_result[k] = {'display_name': display_name, 'message': message}
                    continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process string value; Convert str value provided, on error, record error.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            elif parameter_types[k] == 'string':

                display_name = k
                try:

                    if k in ranges:
                        display_name = ranges[k]['display_name']
                    str_value = str(v)
                except:
                    message = 'Failed to convert parameter (%s) value (%r) to string.' % (k, v)
                    error_result[k] = {'display_name': display_name, 'message': message}
                    continue

                # If there are range values for this parameter, then perform range checking.
                if k in ranges:

                    # Determine min and max for ranges
                    range_min = ranges[k]['min']
                    range_max = ranges[k]['max']
                    range_set = ranges[k]['set']
                    display_name = ranges[k]['display_name']

                    # If range_set not provided, send value on to instrument as provided.
                    if not range_set:
                        result[k] = str_value
                        continue

                    range_set.sort()
                    if str_value in range_set:
                        result[k] = str_value
                    else:
                        message = 'Parameter (%s) has invalid string value %r, not one of %s.' % \
                                  (k, str_value, range_set)
                        error_result[k] = {'display_name': display_name, 'message': message}
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

        return result, error_result

    except Exception as err:
        current_app.logger.info(str(err.message))
        raise


def to_bool(value):
    """ Converts value to boolean. Raises exception for invalid formats.
    """
    if str(value).lower() == 'true':
        return True
    if str(value).lower() == 'false':
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def _c2_set_instrument_driver_parameters(reference_designator, data):
    """ Set one or more instrument driver parameters, return status.
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
    response_status['display_parameters'] = {}
    insufficient_data = 'Insufficient data, or bad data format.'
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

        if debug: print '\n debug --- Original payload: ', json.dumps(payload, indent=4, sort_keys=True)

        # Validate arguments required for uframe are provided.
        for arg in valid_args:
            if arg not in payload:
                raise Exception(insufficient_data)

        # Get instrument status.
        _status = get_instrument_status(reference_designator)
        if _status is None:
            message = 'Failed to retrieve instrument (%s) status.' % reference_designator
            raise Exception(message)

        # Verify payload['resource'] is not empty or None
        if payload['resource'] is None or not payload['resource']:
            message = 'The payload [resource] element is None or empty.'
            raise Exception(message)

        # Get dict of parameters and range values
        parameter_dict, key_dict_ranges = get_range_dictionary(payload['resource'], _status, reference_designator)

        # Scrub data and determine if range errors
        result, error_result = scrub_ui_request_data(payload['resource'], parameter_dict, key_dict_ranges)

        # If range error messages, return error dictionary
        if error_result:

            # Create dictionary with response data and return.
            result = {}
            response_status['message'] = 'Range Error(s)'
            response_status['range_errors'] = error_result
            response_status['status_code'] = 400
            result['response'] = response_status
            if debug: print '\n debug ***** RANGE Error(s): %s' % json.dumps(result, indent=4, sort_keys=True)
            return result

        # If no errors and result is empty or None, raise exception
        elif result is None or not result:
            message = 'Unable to process resource payload (result is None or empty).'
            raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Process parameter set request in uframe
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update value of resource in payload.
        payload['resource'] = json.dumps(result)
        if 'CAMDS' in reference_designator:
            payload['timeout'] = 200000 # 200 millisecs

        if debug: print '\n debug --- payload: ', json.dumps(payload, indent=4, sort_keys=True)
        # Send request and payload to instrument/api and process result
        try:
            response = _uframe_post_instrument_driver_set(reference_designator, 'resource', payload)
        except Exception as err:
            message = str(err.message)
            raise Exception(message)

        if response.status_code != 200:
            message = '(%s) Failed to execute instrument driver set.' % str(response.status_code)
            raise Exception(message)

        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                message = 'Malformed data; not in valid json format. (C2 instrument driver set)'
                raise Exception(message)

            # Evaluate response content for error (review 'value' list in response_data)
            if response_data:
                status_code, status_type, status_message = _eval_POST_response_data(response_data, None)
                response_status['status_code'] = status_code
                response_status['message'] = status_message
        else:
            message = 'No response.content returned from _uframe_post_instrument_driver_set.'
            raise Exception(message)

        # Add response attribute information to result
        result['response'] = response_status

        # Get current over_all status, return in attribute 'status' of result
        try:
            status = _c2_get_instrument_driver_status(reference_designator)
        except Exception:
            status = {}
        result['status'] = status
        return result

    except Exception:
        raise


def get_parameter_display_values(parameters):
    """ Get READ_WRITE display values for UI from instrument 'parameters' dictionary.

    Sample Input:
    "parameters": {
        . . .
        "brmtrace": {
                      "description": "Enable bromide tracing: (true | false)",
                      "direct_access": true,
                      "display_name": "Bromide Tracing",
                      "get_timeout": 10,
                      "range": {
                        "False": false,
                        "True": true
                      },
                      "set_timeout": 10,
                      "startup": true,
                      "value": {
                        "default": false,
                        "description": null,
                        "type": "bool"
                      },
                      "visibility": "READ_WRITE"
                    },
        . . .

    Sample Output:
    "parameter_display_values": {
                "brmtrace": {
                  "False": false,
                  "True": true
                },
                "drkcormt": {
                  "SWAverage": "SWAverage",
                  "SpecAverage": "SpecAverage"
                },
                "intpradj": {
                  "False": false,
                  "True": true
                },
                "operctrl": {
                  "Duration": "Duration",
                  "Samples": "Samples"
                },
                "opermode": {
                  "Continuous": "Continuous",
                  "Polled": "Polled"
                },
                "salinfit": {
                  "False": false,
                  "True": true
                },
                "tempcomp": {
                  "False": false,
                  "True": true
                }
              },
        . . .

    """
    result = {}
    read_write = 'READ_WRITE'
    try:
        # If no parameters, then return empty dict.
        if not parameters:
            return result

        # Process each READ_WRITE parameter - if range attribute is provided (and not null)
        keys = parameters.keys()
        for key in keys:
            param = parameters[key]

            # If parameter is READ_WRITE, process parameter
            if param['visibility'] == read_write:

                # If parameter has a 'range' attribute, process 'range' value information
                if 'range' in param:
                    range = param['range']

                    # if parameter attribute 'range' is available, process and add to result dict.
                    if range:
                        if isinstance(range, dict):
                            result[key] = range

        return result

    except Exception as err:
        current_app.logger.info(err.message)
        raise

def get_ro_parameter_display_values(parameters):
    """ Get READ_ONLY and IMMUTABLE display values for UI from instrument 'parameters' dictionary.

    Sample Input:
    "parameters": {
            "rat": {
              "description": "Baud rate for instrument communications: (2400 to 230400)",
              "direct_access": false,
              "display_name": "Baud Rate",
              "get_timeout": 10,
              "range": {
                "115200": 115200,
                "14400": 14400,
                "19200": 19200,
                "19201": 19201,
                "230400": 230400,
                "2400": 2400,
                "28800": 28800,
                "38400": 38400,
                "4800": 4800,
                "57600": 57600,
                "9600": 9600
              },
              "set_timeout": 10,
              "startup": false,
              "value": {
                "description": null,
                "type": "int"
              },
              "visibility": "READ_ONLY"
            },
        . . .

    Sample Output:
    "parameter_display_values": {
                "rat": {
              "115200": 115200,
              "14400": 14400,
              "19200": 19200,
              "19201": 19201,
              "230400": 230400,
              "2400": 2400,
              "28800": 28800,
              "38400": 38400,
              "4800": 4800,
              "57600": 57600,
              "9600": 9600
            },
        . . .

    """
    result = {}
    valid_visibility = ['READ_ONLY', 'IMMUTABLE']
    try:
        # If no parameters, then return empty dict.
        if not parameters:
            return result

        # Process each READ_WRITE parameter - if range attribute is provided (and not null)
        keys = parameters.keys()
        for key in keys:
            param = parameters[key]

            # If parameter is READ_WRITE, process parameter
            if param['visibility'] in valid_visibility:

                # If parameter has a 'range' attribute, process 'range' value information
                if 'range' in param:
                    range = param['range']

                    # if parameter attribute 'range' is available, process and add to result dict.
                    if range:
                        if isinstance(range, dict):
                            result[key] = range

        return result

    except Exception as err:
        current_app.logger.info(err.message)
        raise



def get_range_dictionary(resource, _status, reference_designator):
    """
    """
    key_dict = {}
    parameter_dict = {}
    try:
        # Get parameters from status.
        _parameters = get_instrument_parameters(_status)
        if _parameters is None:
            message = 'Failed to retrieve instrument (%s) parameters from status.' % reference_designator
            raise Exception(message)

        # Create parameter type dictionary.
        _parameters_list = _parameters.keys()
        for parameter in _parameters_list:

            # Process READ_WRITE_parameters
            tmp = _parameters[parameter]

            if tmp['visibility'] == 'READ_WRITE':

                parameter_dict[parameter] = str(tmp['value']['type'])

                # Create range value checking dictionary
                key_dict[parameter] = {}
                key_dict[parameter]['type'] = str(tmp['value']['type'])
                key_dict[parameter]['display_name'] = str(tmp['display_name'])
                if 'description' in tmp:
                    key_dict[parameter]['desc'] = str(tmp['description'])
                else:
                    key_dict[parameter]['desc'] = None

                # Prepare for instrument parameters without 'range' attribute
                if 'range' in tmp:
                    if tmp['range'] is None or not tmp['range']:
                        key_dict[parameter]['range'] = None
                    else:
                        key_dict[parameter]['range'] = tmp['range']
                else:
                    key_dict[parameter]['range'] = None

                key_dict[parameter]['min'] = None
                key_dict[parameter]['max'] = None
                key_dict[parameter]['set'] = []

        if resource is None or not parameter_dict:
            message = 'The payload [resource] element is None or parameters dictionary is empty.'
            raise Exception(message)

        # Utilize parameter 'range' attribute
        key_dict_ranges = populate_and_check_range_values(resource, key_dict)

        return parameter_dict, key_dict_ranges

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


@api.route('/c2/instrument/<string:reference_designator>/get_last_particle/<string:_method>/<string:_stream>',
           methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_last_particle(reference_designator, _method, _stream):
    """ Get the last particle for reference designator; method and stream name provided. If error, return error.
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


# todo - discuss command state update after an error is raised and returned (400, bad_request).
def _c2_get_last_particle(rd, _method, _name):
    """ Using the reference designator, stream method and name, fetch last particle.
    Get reference designator metadata to determine time span for last particle.

    Sample query:
    http://localhost:4000/c2/instrument/RS10ENGC-XX00X-00-FLORDD001/get_last_particle/streamed/flord_d_status
    generates request url to http://host:12576:
    /sensor/inv/RS10ENGC/XX00X/00-FLORDD001/streamed/flord_d_status?beginDT=2016-02-09T23:43:53.884Z&limit=1

    Returns:
        {
          "particle_metadata": {
            "deployment": 0,
            "method": "streamed",
            "node": "XX00X",
            "sensor": "00-FLORDD001",
            "stream": "flord_d_status",
            "subsite": "RS10ENGC",
            "time": "2016-02-09T23:43:53"
          },
          "particle_values": {
            "baud_rate": 19200,
            "clock": "23:41:51",
            "date": "02/09/16",
            "driver_timestamp": "2016-02-09T23:43:53",
            "firmware_version": "Triplet5.20",
            "ingestion_timestamp": "2016-02-09T23:43:56",
            "internal_memory": 4095,
            "internal_timestamp": "2016-02-09T23:41:51",
            "latitude": 90.0,
            "longitude": -180.0,
            "manual_mode": 0,
            "manual_start_time": "17:55:00",
            "measurement_1_dark_count_value": 55,
            "measurement_1_slope_value": 2.100000074278796e-06,
            "measurement_2_dark_count_value": 52,
            "measurement_2_slope_value": 0.012129999697208405,
            "number_measurements_per_reported_value": 1,
            "number_of_packets_per_set": 0,
            "number_of_reported_values_per_packet": 0,
            "port_timestamp": "2016-02-09T23:43:53",
            "predefined_output_sequence": 0,
            "preferred_timestamp": "port_timestamp",
            "provenance": "",
            "recording_mode": 0,
            "sampling_interval": "00:30:00",
            "serial_number": "BBFL2W-1028",
            "time": "2016-02-09T23:43:53"
          }
        }


    If an attribute in particle contains 0.0 as value for 'timestamp', it is converted to "1900-01-01T00:00:00".

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
    metadata = None
    try:
        # Get reference designator metadata
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
            message = 'Failed to get metadata stream contents from uframe for reference designator (%s).' % rd
            raise Exception(message)

        time_set = process_stream_metadata_for_timeset(metadata, _method, _name)
        if time_set is None:
            message = 'Failed to obtain metadata times for reference_designator %s.' % rd
            raise Exception(message)

        mooring, platform, instrument = rd.split('-', 2)
        stream_type = time_set['method']
        stream_name = time_set['stream']
        formatted_end_time = time_set['endTime']
        formatted_start_time = time_set['beginTime']

        times_equal = False
        if formatted_start_time == formatted_end_time:
            times_equal = True

        # Get single particle using endTime for beginTime and limit=1 (dpa=0 does this for you)
        dpa_flag = '0'
        response = get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream_name,
                                   formatted_start_time, formatted_end_time, dpa_flag, times_equal)

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

        # Process result returned for most recent particle
        particle_metadata = {}
        particle_values = {}
        if result:
            # If stream contents provided, sort in reverse
            data = sorted(result, key=itemgetter('driver_timestamp'), reverse=True)
            if data:

                # Retrieve first item in list as particle.
                particle = data[0]
                if particle:
                    # Add each name-value pair to response dict attribute 'particle_metadata' or 'particle_values'
                    if isinstance(particle, dict):

                        # Process 'particle_metadata'; format 'time' attribute, return
                        if 'pk' in particle:
                            temp = particle['pk']
                            if temp:
                                if isinstance(temp, dict):
                                    if 'time' in temp:
                                        time_float = temp['time']
                                        temp['time'] = get_timestamp_value(time_float)
                                particle_metadata = temp
                            del particle['pk']

                        # Process values
                        for k, v in particle.iteritems():

                            # if value if Nan, convert to str; add to response attribute 'particle_values'
                            if is_nan(v):
                                particle_values[k] = 'NaN'

                            # if k contains 'timestamp' or 'time', process
                            elif 'timestamp' in k or 'time' == k:
                                particle_values[k] = get_timestamp_value(v)

                            # regular key-value pair, add to response attribute 'particle_values'
                            else:
                                particle_values[k] = v

        particle = {}
        particle['particle_metadata'] = particle_metadata
        particle['particle_values'] = particle_values
        return particle

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def get_timestamp_value(value):
    """ Convert float value into formatted string.
    """
    result = value
    try:
        formatted_value = timestamp_to_string(value)
        if formatted_value is not None:
            result = formatted_value
        return result
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return result


def get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, start_time, end_time,
                               dpa_flag, times_equal=False):
    """ Gets the bounded stream contents (specifically for C2 get last particle); returns Response object.
    Note: start_time and end_time need to be datetime objects.

    Sample url:
    12576/sensor/inv/RS10ENGC/XX00X/00-FLORDD001/streamed/flord_d_status?limit=1&beginDT=2016-02-09T23:43:53.884Z
    """
    rd = None
    equal_times = times_equal
    try:
        if dpa_flag == '0':
            # For get last particle, use endTime and limit of 1
            if times_equal:
                query = '?beginDT=%s' % end_time

            # For get_last_particle when times are not equal
            else:
                query = '?beginDT=%s&endDT=%s' % (start_time, end_time)

        else:
            query = '?beginDT=%s&endDT=%s&execDPA=true' % (start_time, end_time)

        # Always add a limit to query...
        query += '&limit=10'

        uframe_url, timeout, timeout_read = get_uframe_data_info()
        rd = '-'.join([mooring, platform, instrument])
        url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if not response or response is None:
            message = 'No data available from uFrame for this request. Instrument: %s, Method: %s, Stream: %s' % \
                            (instrument, stream_type, stream)
            current_app.logger.info('C2 Failed request: ' + url)
            raise Exception(message)
        if response.status_code != 200:
            message = '(%s) Failed to retrieve stream contents from uFrame.' % response.status_code
            raise Exception(message)
        return response
    except ConnectionError:
        message = 'ConnectionError for get stream contents, reference designator: %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get stream contents, reference designator: %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise


def _c2_get_instrument_metadata(reference_designator):
    """ Get metadata for reference designator.

    Sample uframe query to be made:
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
        message = 'ConnectionError for get instrument metadata (%s).' % reference_designator
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get instrument metadata (%s).' % reference_designator
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
                    _start = time_set['beginTime']
                    _end = time_set['endTime']
                    local_timezone = tzlocal.get_localzone()
                    utc_time =  dt.datetime.strptime(_end, "%Y-%m-%dT%H:%M:%S.%fZ")
                    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
                    temp = ut(local_time)

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


def get_streams_dictionary(rd):
    """ Return dictionary of stream names whose value is the stream method.
    The UI will then return both the stream name and method when a 'get last particle' request is made.

    "times" : [   {
                    "endTime" : "2016-02-09T23:43:53.884Z",
                    "beginTime" : "2016-02-09T23:43:53.884Z",
                    "method" : "streamed",
                    "sensor" : "RS10ENGC-XX00X-00-FLORDD001",
                    "count" : 1,
                    "stream" : "flord_d_status"
                  }, {
                    "endTime" : "2016-04-15T00:27:35.848Z",
                    "beginTime" : "2015-10-09T19:30:56.757Z",
                    "method" : "streamed",
                    "sensor" : "RS10ENGC-XX00X-00-FLORDD001",
                    "count" : 13038814,
                    "stream" : "flort_d_data_record"
                  }, {
                    "endTime" : "2016-04-13T17:34:58.718Z",
                    "beginTime" : "2015-10-09T20:40:59.618Z",
                    "method" : "streamed",
                    "sensor" : "RS10ENGC-XX00X-00-FLORDD001",
                    "count" : 1180,
                    "stream" : "flort_d_status"
                  } ],

    Dictionary returned:
    {
    "flort_d_data_record": "streamed",
    "flort_d_status": "streamed",
    "flord_d_status": "streamed"
    },

    Helper urls:
    http://uft21.ooi.rutgers.edu:12576/sensor/inv/RS10ENGC/XX00X/00-NUTNRA001/metadata
    http://localhost:4000/c2/instrument/RS10ENGC-XX00X-00-NUTNRA001/commands

    """
    times = []
    empty_streams = {}
    streams = {}
    try:
        # Get metadata for reference designator
        metadata = get_instrument_metadata(rd)

        # Get metadata 'times' element (list of dictionaries)
        if 'times' in metadata:

            # If times is empty list return
            if not metadata['times']:
                return empty_streams
            times = metadata['times']

        # Process 'times' elements to create streams dictionary
        if times:
            for item in times:
                stream = item['stream']
                method = item['method']
                streams[stream] = method

        return streams

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return empty_streams


def get_instrument_metadata(rd):
    """ Get metadata for reference designator. If error, raise error
    """
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
            message = 'Failed to get metadata contents from uframe for reference designator (%s).' % rd
            raise Exception(message)

        return metadata

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
    """ Execute set parameters for instrument driver using command and data; return uframe response. (POST)
    """
    debug = False
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        if 'CAMDS' in reference_designator:
            timeout = 10
            timeout_read = 200
        url = "/".join([uframe_url, reference_designator, command])
        if debug: print '\n debug -- (_uframe_post_instrument_driver_set) url: ', url
        response = requests.post(url, data=data, timeout=(timeout, timeout_read), headers=_post_headers())
        return response

    except ConnectionError:
        message = 'ConnectionError for instrument driver set command.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout for instrument driver set command.'
        raise Exception(message)
    except Exception:
        raise


# TODO enable kwargs parameter
def _c2_instrument_driver_execute(reference_designator, data):
    """
    Command the driver to execute a capability. [POST]
    Accepts the following urlencoded parameters:
       command: capability to execute
       kwargs:  JSON-encoded dictionary specifying any necessary keyword arguments for the command
       timeout: in milliseconds, default value is 60000

    valid_args = ['command', 'kwargs', 'timeout'], but 'command' is only one utilized at this time.
    json response is constructed from /status response (as attribute 'status') and a
    'response' attribute, whose format is:
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
    the status block in the response contains execution results in ['status']['cmd']['value'][1].
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


    BOTPT Bench Instrument (WAS dict as shown below; should be list):
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
    result = {}
    response_status = {}
    response_status['status_code'] = 200
    response_status['message'] = ""
    insufficient_data = 'Insufficient data, or bad data format.'
    message = 'uframe error reported in _c2_instrument_driver_execute.'
    quote_value = '%22'
    valid_args = ['command']
    _command_timeout_default = 30000
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

        """
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

        """
        _commands = _status['value']['metadata']['commands']

        # Prepare url suffix for post
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

        if command_name is None:
            message = 'Malformed execute request, failed to retrieve command name from request data.'
            raise Exception(message)
        if not command_name:
            message = 'Malformed execute request, failed to retrieve command name from request data.'
            raise Exception(message)

        # Get driver command timeout from status
        if command_name not in _commands:
            message = 'Failed to retrieve command (%s) timeout from status.' % command_name
            raise Exception(message)

        # Get timeout from command dictionary and convert to milliseconds; default 60 seconds.
        _timeout = _commands[command_name]['timeout']
        if _timeout:
            _timeout = _timeout * 1000
        else:
            _timeout = _command_timeout_default

        # Add driver timeout to suffix for execute
        suffix += '&timeout=' + str(_timeout)

        # Determine if this is an ACQUIRE_STATUS or ACQUIRE_SAMPLE command; prep for post processing
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

        # Execute driver command
        response = uframe_post_instrument_driver_command(reference_designator, 'execute', suffix)
        if response.status_code != 200:
            message = '(%s) execute %s failed.' % (str(response.status_code), command_name)
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)

        # If response_data, review error information returned
        response_data = None
        if response.content:
            try:
                response_data = json.loads(response.content)
            except Exception:
                raise Exception('Malformed data; not in valid json format.')

            # Evaluate response content for error (review 'value' list info in response_data )
            if response_data:
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

                # If failed to retrieve particle(s), populate response_status
                if not response_data:

                    if acquire_result is None:
                        message = '(%s) Failed to retrieve particle. ' % command_name
                        current_app.logger.info(message)
                        response_status['status_code'] = 400
                        response_status['message'] = message

                # Process particle retrieved
                else:
                    try:
                        # Get acquire_result...
                        if check_response_data_contents(response_data, command_name, response_status):

                            acquire_result_list = []

                            # Driver code should always return a list; if not error.
                            if not isinstance(response_data['value'][1], list):
                                message = '(%s) Error in response data: ' % command_name
                                message += 'Result returned from driver is not of type list.'
                                current_app.logger.info(message)
                                response_status['status_code'] = 400
                                response_status['message'] = message

                            # Get list for processing acquire result
                            else:
                                if response_data['value'][1]:
                                    if response_data['value'][1][0] is not None:
                                        acquire_result_list = deepcopy(response_data['value'][1])
                                else:
                                    check_state_change = True

                            # Process all particles in acquire_result_list
                            for acquire_result in acquire_result_list:

                                # If acquire_result is None, set response_status
                                if acquire_result is None and not check_state_change:
                                    message = '(%s) Error in response data: No results to process.' % command_name
                                    current_app.logger.info(message)
                                    response_status['status_code'] = 400
                                    response_status['message'] = message

                                # Process particle
                                if acquire_result is not None:

                                    # -- Get particle_metadata information
                                    keys = acquire_result.keys()
                                    particle_metadata = {}
                                    for key in keys:
                                        if key != 'values':
                                            id = key
                                            value = acquire_result[id]
                                            if is_nan(value):
                                                particle_metadata[id] = 'NaN'
                                            elif 'timestamp' in id or 'time' == id:
                                                particle_metadata[id] = get_timestamp_value(value)
                                            else:
                                                particle_metadata[id] = value

                                    acquire_result['particle_metadata'] = particle_metadata
                                    particle_values = {}

                                    # -- Get particle_values information (i.e. process information in 'values')
                                    if 'values' in acquire_result:
                                        values = deepcopy(acquire_result['values'])

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
                                                if is_nan(value):
                                                    particle_values[id] = 'NaN'
                                                elif 'timestamp' in id or 'time' == id:
                                                    particle_values[id] = get_timestamp_value(value)
                                                else:
                                                    particle_values[id] = value

                                            acquire_result['particle_values'] = particle_values
                                            del acquire_result['values']

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

                    if not acquire_results:
                        # Populate return status due to failure to obtain particle;
                        result['response'] = response_status
                        result['acquire_result'] = []
                    else:
                        # Set acquire_result value
                        result['acquire_result'] = acquire_results

        return result

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def check_response_data_contents(response_data, command_name, response_status):

    result = False

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
        result = True

    return result


def timestamp_to_string(time_float):
    """ Convert float to formatted time string. If failure to convert, return None.
    """
    offset = 2208988800
    formatted_time = None
    try:
        if not isinstance(time_float, float):
            return None
        ts_time = convert_from_utc(time_float - offset)
        formatted_time = dt.datetime.strftime(ts_time, "%Y-%m-%dT%H:%M:%S")
        return formatted_time
    except Exception as err:
        current_app.logger.info(str(err.message))
        return None


def is_nan(x):
    return isinstance(x, float) and math.isnan(x)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private helper methods for instrument agent driver (instrument/api)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_get_instrument_driver_command(reference_designator, command):
    """ Return the uframe response of instrument command provided for GET
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, reference_designator, command])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response

    except ConnectionError:
        message = 'ConnectionError for get instrument driver command, reference designator: %s.' % reference_designator
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get instrument driver command, reference designator: %s.' % reference_designator
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
        message = 'ConnectionError for post instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for post instrument driver command.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise


def get_uframe_info(type='instrument'):
    """ Returns uframe instrument/api specific configuration information. (port 12572)
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
        message = 'ConnectionError for instrument/api configuration values.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for instrument/api configuration values.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise


def get_uframe_data_info():
    """ Returns uframe data configuration information. (port 12576)
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
        message = 'ConnectionError for command and control sensor/inv.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for command and control sensor/inv.'
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
    """ Evaluate the value dictionary from uframe POST response data.
    Return error code, type and message.
    """
    debug = False
    try:
        value = None
        type = None
        if debug:
            print '\n _eval_POST_response_data response_data: ', response_data
            print '\n _eval_POST_response_data response_data: ', json.dumps(response_data, indent=4, sort_keys=True)
        if 'type' in response_data:
            type = response_data['type']

        if 'value' in response_data:
            value = response_data['value']

            if not isinstance(value, list):
                """
                Sample:
                {
                    "cmd": {
                        "args": [
                            {
                                "ave": 2
                            }
                        ],
                        "cmd": "set_resource",
                        "kwargs": {}
                    },
                    "time": 1456961624.485942,
                    "type": "DRIVER_ASYNC_RESULT",
                    "value": null
                }
                """
                if value is None:
                    return 200, type, ''
                else:
                    if debug: print '\n debug --- instr exception error: ', value
                    return 400, None, 'Error occurred while instrument/api was processing payload.'

            # if value[0] contains int, then there was an error for command issued (verify uframe syntax)
            # if no uframe error, then int conversion will force return to continue processing
            try:
                get_int = int(str(value[0]).decode("utf-8"))
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
            if not msg or msg is None:
                msg = 'value attribute not available in response data from uframe.'
            return 500, None, msg
    except:
        raise


def _get_toc():
    """ Returns a toc dictionary of arrays, moorings, platforms and instruments.
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

# Retain: deprecated, now using instruments (instrument/api) as toc data source rather than /sensor/inv port 12576.
def _compile_c2_toc_standard():
    """ Returns a toc dictionary of arrays, moorings, platforms and instruments from uframe data (port 12576).
    Augmented by the UI database for vocabulary and arrays, returns json.

    Note: was named _compile_c2_toc, but changed when we went with C2 toc
    from instruments (instrument/api) and not data on 12576.
    To retrieve C2 toc from data port (12576) use this function.
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
                                          'display_name': get_long_display_name_by_rd("-".join([mooring, platform]))
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

    except ConnectionError:
        message = 'ConnectionError for _compile_c2_toc_standard.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for _compile_c2_toc_standard.'
        current_app.logger.info(message)
        raise Exception(message)
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
    #====================================================== DEPRECATE THE PARAMETER VALUES UPDATE ==============
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
    #====================================================== DEPRECATE THE PARAMETER VALUES UPDATE ==============
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
    C2 Sample:  http://localhost:4000/c2/instrument/RS10ENGC-XX00X-00-BOTPTA001/ping

    request:    http://localhost:12572/instrument/api/RS10ENGC-XX00X-00-BOTPTA001/ping
    response:
    {"cmd": {"cmd": "driver_ping", "args": ["PONG"], "kwargs": {}}, "type": "DRIVER_ASYNC_RESULT",
    "value": "driver_ping: <mi.instrument.noaa.botpt.ooicore.driver.InstrumentDriver object at 0x7fe42207af10> PONG",
    "time": 1455057480.654446}
    """
    ping = {}
    try:
        data = _c2_get_instrument_driver_ping(reference_designator)
        if data:
            ping = data
        return jsonify(ping)
    except Exception as err:
        return bad_request(err.message)


def _c2_get_instrument_driver_ping(reference_designator):
    """
    Get instrument driver status ('ping'). This initiates a simple callback into
    the instrument driver class from the zeromq wrapper, indicating the driver is still running.
    Does not verify connectivity with the instrument itself.
    Sample: localhost:12572/instrument/api/reference_designator/ping
    """
    try:
        data = {}
        response = uframe_get_instrument_driver_command(reference_designator, 'ping')
        if not response.content:
            return {}

        if response.status_code != 200:
            raise Exception('Error retrieving %s instrument driver ping from uframe.' % reference_designator)

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
            except:
                raise Exception('Malformed data; not in valid json format.')
        return data
    except:
        raise


# todo development only (exercise _get_toc)
@api.route('/c2/toc', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_toc():
    """ Returns the C2 toc dictionary. (Sample: http://host:4000/c2/toc)
    """
    toc = []
    try:
        data = _compile_c2_toc()
        if data:
            toc = data
        return jsonify(toc)
    except Exception as err:
        return bad_request(err.message)


def _compile_c2_toc():
    """ Returns a C2 toc dictionary of arrays, moorings, platforms and instruments from instruments/api (port 12572).

    Sample Moorings:
    [
        "RS03ASHS",
        "SSRSPACC",
        "RS01SHBP",
        . . .
    ]
    Sample Platforms:  [
            "MJ03C"
        ]
    Sample Instruments:
        [
            "09-TRHPHA301",
            "06-MASSPA301-MCU",
            "05-CAMDSB303",
            "09-IP5",
            "00-ENG",
            "06-IP2",
            "09-THSPHA301",
            "10-IP6",
            "10-TRHPHA301",
            "07-IP3",
            "05-IP1",
            "07-D1000A301"
        ]

    Current toc instrument is a list of dictionaries:
        [
            {'reference_designator': u'RS03ASHS-MJ03B-06-OBSSPA301',
            'instrument_code': u'06-OBSSPA301',
            'display_name': u'Short-Period Ocean Bottom Seismometer',
            'platform_code': u'MJ03B',
            'mooring_code': u'RS03ASHS'
            },
            . . .
        ]
    """
    moorings = []
    platforms = []
    instruments = []
    try:
        toc = {}
        mooring_list = []
        platform_list = []
        instrument_list = []

        # Get list of instruments from instrument/api
        uframe_url, timeout, timeout_read = get_uframe_info()
        response = requests.get(uframe_url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get instrument/api list of instruments.' % response.status_code
            raise Exception(message)

        arrays = Array.query.all()
        array_display_names = {}
        for array in arrays:
            array_display_names[array.array_code] = array.display_name

        # Process response.content for moorings, platforms and instruments
        _instruments = response.json()
        for rd in _instruments:

            # Calculate values to be used in toc
            _mooring, _platform, _instrument = rd.split('-', 2)
            array_code = _mooring[:2]
            array_name = array_display_names[array_code]
            mooring_name = get_display_name_by_rd(_mooring)
            if mooring_name is None:
                mooring_name = _mooring
            platform_name = get_display_name_by_rd("-".join([_mooring, _platform]))
            if platform_name is None:
                platform_name = "-".join([_mooring, _platform])
            instrument_name = get_display_name_by_rd(reference_designator=rd)
            if instrument_name is None:
                instrument_name = rd

            # Determine display names - mooring, platform
            mooring_display_name = ' '.join([array_name, mooring_name])
            if platform_name == 'RS10ENGC-XX00X':
                platform_display_name = 'Bench Instruments'
            else:
                platform_display_name = ' '.join([mooring_name, platform_name])

            # Add entries for moorings, platforms and instruments dictionaries
            if _mooring not in moorings:
                moorings.append(_mooring)
                mooring_list.append({'reference_designator': _mooring,
                                 'array_code': array_code,
                                 'display_name': mooring_display_name
                                 })
            if _platform not in platforms:
                platforms.append(_platform)
                platform_list.append({'reference_designator': "-".join([_mooring, _platform]),
                              'mooring_code': _mooring,
                              'platform_code': _platform,
                              'display_name': platform_display_name
                              })
            if _instrument not in instruments:
                instruments.append(_instrument)
                instrument_list.append({'mooring_code': _mooring,
                                'platform_code': _platform,
                                'instrument_code': _instrument,
                                'reference_designator': rd,
                                'display_name': instrument_name
                                })

        # Assemble toc for response
        arrays = Array.query.all()
        toc['arrays'] = [array.to_json() for array in arrays]
        toc['moorings'] = mooring_list
        toc['platforms'] = platform_list
        toc['instruments'] = instrument_list

        return toc

    except ConnectionError:
        message = 'ConnectionError for get_C2_instruments.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get_C2_instruments.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return {}