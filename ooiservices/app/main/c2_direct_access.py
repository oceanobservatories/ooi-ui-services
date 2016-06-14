#!/usr/bin/env python
"""
API v1.0 Command and Control (C2) direct access routes:

    Enter direct access mode:           /c2/instrument/<string:reference_designator>/direct_access/start
    Execute direct access command       /c2/instrument/<string:reference_designator>/direct_access/execute
    Exit direct access mode:            /c2/instrument/<string:reference_designator>/direct_access/exit
    Get sniffer data from instrument    /c2/instrument/<string:reference_designator>/direct_access/sniffer
"""
__author__ = 'Edna Donoughe'


from flask import jsonify, current_app, request
from ooiservices.app.decorators import scope_required
from ooiservices.app.main import api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.c2 import _c2_get_instrument_driver_status, uframe_post_instrument_driver_command, \
                                    _eval_POST_response_data
from requests.exceptions import ConnectionError, Timeout
import socket as sock
import ast
import json


# Direct Access start.
# todo deprecate 'GET'?
@api.route('/c2/instrument/<string:reference_designator>/direct_access/start', methods=['POST', 'GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_direct_access_start(reference_designator):
    """ Start direct access. (when button 'Start Direct' is selected.)

    (Transition from 'DRIVER_STATE_COMMAND' to 'DRIVER_STATE_DIRECT_ACCESS'.)

    POST Sample:
    http://uft21.ooi.rutgers.edu:12572/instrument/api/RS10ENGC-XX00X-00-FLORDD001/start
    Command: "DRIVER_EVENT_START_DIRECT"

    """
    debug = True
    rd = reference_designator
    NOT_NONE = 'NOT_NONE'
    state_DRIVER_STATE_COMMAND = 'DRIVER_STATE_COMMAND'
    capability_DRIVER_EVENT_START_DIRECT = 'DRIVER_EVENT_START_DIRECT'
    target_state = 'DRIVER_STATE_DIRECT_ACCESS'
    try:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare to execute - direct access start command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Validate reference_designator
        _state, _capabilities, result = direct_access_get_state_and_capabilities(rd)
        if _state == target_state:
            return jsonify(result)

        # Verify _state and _capabilities match expected state and capabilities
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=state_DRIVER_STATE_COMMAND,
                                      expected_capability=capability_DRIVER_EVENT_START_DIRECT)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Execute driver command 'DRIVER_EVENT_START_DIRECT' on upstream server
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Execute driver command
        suffix = 'command=%22DRIVER_EVENT_START_DIRECT%22&timeout=60000'
        response = uframe_post_instrument_driver_command(reference_designator, 'execute', suffix)
        if response.status_code != 200:
            message = '(%s) execute %s failed.' % (str(response.status_code), capability_DRIVER_EVENT_START_DIRECT)
            raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify command execution status by reviewing error information returned from instrument driver
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if response.content:
            try:
                response_data = json.loads(response.content)
            except Exception:
                raise Exception('Direct access start command - malformed response data; invalid json format.')

            # Evaluate response content for error (review 'value' list info in response_data )
            if response_data:
                status_code, status_type, status_message = _eval_POST_response_data(response_data, "")
                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                if debug:
                    print '\n START response_data: ', json.dumps(response_data, indent=4, sort_keys=True)
                    print '\n direct_access START - status_code: ', status_code
                    if status_code != 200:
                        print '\n direct_access START - status_message: ', status_message
                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                if status_code != 200:
                    raise Exception(status_message)

        # Validate reference_designator
        _state, _capabilities, result = direct_access_get_state_and_capabilities(rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Final - direct access response final checks for success or failure
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify _state and _capabilities match expected state and capabilities
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=target_state,
                                      expected_capability=NOT_NONE)

        return jsonify(result)

    except Exception as err:
        message = '(%s) direct access start exception: %s' % (rd, err.message)
        current_app.logger.info(message)
        return bad_request(err.message)


# Direct Access execute command.
@api.route('/c2/instrument/<string:reference_designator>/direct_access/execute', methods=['POST'])
@auth.login_required
@scope_required(u'command_control')
def c2_direct_access_execute(reference_designator):
    """ Execute direct access command.

    While in 'DRIVER_STATE_DIRECT_ACCESS', execute commands sent from direct access terminal window.

    Process direct access terminal commands:
        Receive content, send to instrument driver.
        [Upon receipt of response from instrument, forward response to UI.] Use sniffer.

    Note valid commands in direct_access_buttons list:
        "direct_access_buttons": [
            "Interrupt",
            "Print Menu",
            "Print Metadata",
            "Read Data",
            "Restore Factory Defaults",
            "Restore Settings",
            "Run Settings",
            "Run Wiper",
            "Save Settings",
            "Set Clock>",
            "Set Date>",
            "Set>"
            ],

        "input_dict": {
          "Interrupt": "!!!!!",
          "Print Menu": "$mnu\r\n",
          "Print Metadata": "$met\r\n",
          "Read Data": "$get\r\n",
          "Restore Factory Defaults": "$rfd\r\n",
          "Restore Settings": "$rls\r\n",
          "Run Settings": "$run\r\n",
          "Run Wiper": "$mvs\r\n",
          "Save Settings": "$sto\r\n",
          "Set Clock>": "$clk ",
          "Set Date>": "$date \r\n",
          "Set>": "set "
        },

    POST request.data shall provide attribute 'command' or 'command_text':
        {
            "command": "Print Metadata"
            "title": "FLOR"
        }
        where valid command value is one of items in direct_access_buttons dictionary (key for input_config).

     OR
        {
           "command_text": "$mnu\r\n"
           "title": "FLOR"
        }
    """
    rd = reference_designator
    TRIPS = '"""'
    NOT_NONE = 'NOT_NONE'
    state_DRIVER_STATE_DIRECT_ACCESS = 'DRIVER_STATE_DIRECT_ACCESS'
    target_state = state_DRIVER_STATE_DIRECT_ACCESS
    try:
        command_request = None
        command_text = None
        command_request_value = None
        using_command_request = True
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get request data, process required items.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not request.data:
            message = 'Direct access execute command requires request.data for POST.'
            raise Exception(message)

        # Get request data and process
        request_data = json.loads(request.data)
        if request_data is None:
            message = 'Direct access execute command did not receive request data (%s).' % rd
            raise Exception(message)

        if 'title' not in request_data:
            message = 'Malformed direct access execute command, missing title (%s).' % rd
            raise Exception(message)

        if ('command' not in request_data) and ('command_text' not in request_data):
            message = 'Malformed direct access execute command, missing command or command text (%s).' % rd
            raise Exception(message)

        # Get title, and command_request or command_text.
        title = request_data['title']
        if 'command' in request_data:
            command_request = request_data['command']
            command_text = None
        elif 'command_text' in request_data:
            command_text = request_data['command_text']
            command_request = None
            using_command_request = False

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify required fields are not None.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if title is None:
            message = 'No direct access title data provided for instrument %s.' % rd
            raise Exception(message)
        if using_command_request:
            if command_request is None:
                message = 'No direct access command data provided for instrument %s.' % rd
                raise Exception(message)
        else:
            if command_text is None:
                message = 'No direct access command_text data provided for instrument %s.' % rd
                raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare to execute - get state, capabilities and status.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        _state, _capabilities, result = direct_access_get_state_and_capabilities(rd)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify current _state and _capabilities match expected state and capabilities
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=state_DRIVER_STATE_DIRECT_ACCESS,
                                      expected_capability=NOT_NONE)

        if using_command_request:
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get valid direct access commands from direct_access_buttons
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            valid_commands = []
            if result:
                if 'direct_access_buttons' in result:
                    valid_commands = result['direct_access_buttons']
                else:
                    message = 'Instrument %s missing direct_access_buttons dictionary.' % rd
                    raise Exception(message)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Verify there are valid commands; otherwise error.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not valid_commands:
                message = 'Instrument %s direct_access_buttons list is empty.' % rd
                raise Exception(message)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Verify command_request from request data is a valid command; otherwise error.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if command_request not in valid_commands:
                message = 'Instrument %s command received \'%s\' not in list of available commands.' % \
                          (rd, command_request)
                raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify direct_config available; otherwise error.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if 'direct_config' not in result['value']:
            message = 'Instrument %s has missing direct access direct_config list.' % rd
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify direct_config is not empty; otherwise error.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not result['value']['direct_config']:
            message = 'Instrument %s has empty direct access direct_config list.' % rd
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If direct_config has contents, process list of dictionaries
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ip = None
        data = None
        eol = None
        located_requested_item = False
        for direct_config in result['value']['direct_config']:

            # Get and check title; if title in dictionary does not match requested title; go to next item.
            _title = None
            if 'title' in direct_config:
                _title = direct_config['title']
            if _title != title:
                continue

            # Identified item in direct_config; process item
            located_requested_item = True

            # Get and check ip from direct_config dictionary
            ip = None
            if 'ip' in direct_config:
                ip = direct_config['ip']
                if ip is None or not ip:
                    message = 'Instrument %s has invalid ip: \'%r\'.' % (rd, ip)
                    raise Exception(message)

            # Get and check data from direct_config dictionary
            data = None
            if 'data' in direct_config:
                data = direct_config['data']
                if data is None or not data:
                    message = 'Instrument %s has invalid data: \'%r\'.' % (rd, data)
                    raise Exception(message)

            # Get and check eol from direct_config dictionary
            eol = None
            if 'eol' in direct_config:
                eol = direct_config['eol']
                if eol is None or not eol:
                    message = 'Instrument %s has invalid or empty eol: \'%r\'.' % (rd, eol)
                    raise Exception(message)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If processing a command_request, get remaining items for processing
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if using_command_request:

                # Verify input_dict is in direct_config
                if 'input_dict' not in direct_config:
                    message = 'Instrument %s has missing direct access input_dict dictionary.' % rd
                    raise Exception(message)

                # Get command_request_values; verify command_request in list and therefore valid.
                command_request_values = direct_config['input_dict']
                if command_request not in command_request_values:
                    message = 'Instrument %s direct access command %s not found in direct_config.' % rd
                    raise Exception(message)

                # Get command_request_value from input_dict provided.
                command_request_value = command_request_values[command_request]

        # Was the requested title located in the direct_config? If not, error.
        if not located_requested_item:
            message = 'Instrument %s did not have a matching title \'%s\' in direct access direct_config.' % (rd, title)
            raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare command value to send to instrument.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if using_command_request:
            # Using command button value
            command_value = command_request_value
        else:
            # If not using command button, , prepare command_value using the command_text
            try:
                command_value = ast.literal_eval(TRIPS + command_text + TRIPS)
                if eol:
                    command_value += eol
            except Exception as err:
                message = 'Exception processing command value (literal_eval): %s' % str(err)
                raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Execute - direct access command.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            send_command(rd, command_value, ip, data)
        except Exception as err:
            message = 'Exception processing direct access command: %s' % str(err)
            raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Final - Verify _state and _capabilities match expected state and capabilities.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=target_state,
                                      expected_capability=NOT_NONE)

        return jsonify(result)

    except Exception as err:
        message = '(%s) direct access execute exception: %s' % (rd, err.message)
        current_app.logger.info(message)
        return bad_request(err.message)


# Direct Access exit
@api.route('/c2/instrument/<string:reference_designator>/direct_access/exit', methods=['POST', 'GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_direct_access_exit(reference_designator):
    """ Exit direct access, transition  to instrument driver state. If error, raise exception.

    Exit 'DRIVER_STATE_DIRECT_ACCESS', execute command 'DRIVER_EVENT_STOP_DIRECT'.
    """
    debug = True
    rd = reference_designator
    state_DRIVER_STATE_DIRECT_ACCESS = 'DRIVER_STATE_DIRECT_ACCESS'
    capability_DRIVER_EVENT_STOP_DIRECT = 'DRIVER_EVENT_STOP_DIRECT'
    try:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare to execute - direct access start command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Validate reference_designator, get status and capabilities
        _state, _capabilities, result = direct_access_get_state_and_capabilities(rd)

        # If current state is not in the state_DRIVER_STATE_DIRECT_ACCESS, then return status result
        # Log request to exit direct access state when not in direct access.
        if _state != state_DRIVER_STATE_DIRECT_ACCESS:
            message = 'Request to exit direct access for instrument %s, when in driver state %s' % (rd, _state)
            current_app.logger.info(message)
            return jsonify(result)

        # Verify current _state and _capabilities match expected state and capabilities
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=state_DRIVER_STATE_DIRECT_ACCESS,
                                      expected_capability=capability_DRIVER_EVENT_STOP_DIRECT)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Execute driver command 'DRIVER_EVENT_STOP_DIRECT' on upstream server
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        suffix = 'command=%22DRIVER_EVENT_STOP_DIRECT%22&timeout=60000'
        response = uframe_post_instrument_driver_command(reference_designator, 'execute', suffix)
        if response.status_code != 200:
            message = '(%s) execute %s failed.' % (str(response.status_code), capability_DRIVER_EVENT_STOP_DIRECT)
            raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify command execution status by reviewing error information returned from instrument driver
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if response.content:
            try:
                response_data = json.loads(response.content)
            except Exception:
                raise Exception('Direct access exit command - malformed response data; invalid json format.')

            # Evaluate response content for error (review 'value' list info in response_data )
            if response_data:
                status_code, status_type, status_message = _eval_POST_response_data(response_data, "")
                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                if debug:
                    print '\n direct_access EXIT - response_data: ', json.dumps(response_data, indent=4, sort_keys=True)
                    print '\n direct_access EXIT - status_code: ', status_code
                    if status_code != 200:
                        print '\n direct_access EXIT - status_message: ', status_message
                #- - - - - - - - - - - - - - - - - - - - - - - - - -
                if status_code != 200:
                    raise Exception(status_message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Final - Verify _state has changed from state_DRIVER_STATE_DIRECT_ACCESS, if not error
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get state, capabilities and response result for reference_designator
        _state, _capabilities, result = direct_access_get_state_and_capabilities(rd)
        if _state == state_DRIVER_STATE_DIRECT_ACCESS:
            message = 'The current state is \'DRIVER_STATE_DIRECT_ACCESS\'; failed to exit direct access.'
            raise Exception(message)

        return jsonify(result)

    except Exception as err:
        message = '(%s) direct access exit exception: %s' % (rd, err.message)
        current_app.logger.info(message)
        return bad_request(err.message)


# Direct Access sniffer
@api.route('/c2/instrument/<string:reference_designator>/direct_access/sniffer', methods=['POST', 'GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_direct_access_sniffer(reference_designator):
    """ Sniff port/ip/title for data, return data
    Sample request:
    http://localhost:4000/c2/instrument/RS10ENGC-XX00X-00-FLORDD001/direct_access/sniffer
        (using hardcoded message: message = '{"ip": "128.6.240.37", "port": 54366}' )

    Sample response:
    {
      "msg": "3671820966.2507 :    PA_HEARTBEAT :  CRC OK : 'HB'\n"
    }

    curl -H "Content-Type: application/json" -X POST --upload-file post_sniff_flord.txt http://localhost:4000/c2/instrument/RS10ENGC-XX00X-00-FLORDD001/direct_access/sniffer
    curl -H "Content-Type: application/json" -X POST --upload-file post_sniff_vadcp_1.txt http://localhost:4000/c2/instrument/RS10ENGC-XX00X-00-VADCPA011/direct_access/sniffer

    """
    # VADCP
    #message = '{"ip": "128.6.240.37", "port": 34868, "title": "Beams 1-4"}'
    #message = '{"ip": "128.6.240.37", "port": 48989, "title": "5th Beam"}'
    # FLORD
    #message = '{"ip": "128.6.240.37", "port": 54366, "title": "FLOR"}'
    #message = '{"ip": "128.6.240.37", "port": 54366}'
    # {"ip": "128.6.240.37", "port": 54366}

    _data = None
    rd = reference_designator
    required_variables = ['ip', 'port', 'title']
    try:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get request data, process required items.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not request.data:
            message = 'Direct access sniffer requires request data for POST.'
            raise Exception(message)

        # Get request data and process
        request_data = json.loads(request.data)
        if request_data is None:
            message = 'Direct access sniffer request data is None. (%s).' % rd
            raise Exception(message)

        # Verify required items are provided in request.data and not empty
        for item in required_variables:
            if item not in request_data:
                message = 'Malformed direct access sniffer request, missing %s (%s).' % (item, rd)
                raise Exception(message)
            else:
                if not request_data[item] or request_data[item] is None:
                    message = 'Malformed direct access sniffer request, %s is empty (%s).' % (item, rd)
                    raise Exception(message)

        # Get ip, port and title
        ip = request_data['ip']
        port = request_data['port']
        #title = request_data['title']

        # Issue request to sniffer process
        s = None
        _data = "Sniffer Connection Failed\r\n"
        try:
            s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
            s.connect((ip, port))

            try:
                _data = s.recv(4096)
            except Exception:
                _data = "Error Receiving Data\r\n"
                pass
            if s is not None:
                s.close()

        except Exception:
            if s is not None:
                s.close()
            pass

        return jsonify(msg=_data)

    except Exception as err:
        message = '(%s) direct access exception: %s' % (reference_designator, err.message)
        current_app.logger.info(message)
        return bad_request(err.message)


#==================================================================
# SUPPORTING FUNCTIONS...
#==================================================================
def direct_access_get_state_and_capabilities(reference_designator):
    """ Get current state and capabilities information for an instrument.
    Overview:
        Get instrument status
        Get state from resulting status
        Get capabilities from resulting status
        Add 'direct_access_buttons' dictionary to _status
        Return state, capabilities and  _status
    """
    state = None
    capabilities = []
    try:
        # Get instrument status.
        try:
            _status = _c2_get_instrument_driver_status(reference_designator)
        except Exception as err:
            message = err.message
            raise Exception(message)

        if _status is None:
            message = 'Instrument (%s) status failed to .' % reference_designator
            raise Exception(message)

        # Verify state is DRIVER_STATE_COMMAND, otherwise raise exception
        if 'value' in _status:
            if 'state' in _status['value']:
                state = _status['value']['state']

        # Verify capabilities
        if 'value' in _status:
            if 'capabilities' in _status['value']:
                capabilities = _status['value']['capabilities'][0]

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get 'direct_access_buttons' (list of button names for direct access)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            direct_config = None
            if _status['value']['direct_config']:
                direct_config = _status['value']['direct_config']
            temp = {}
            if direct_config:
                temp = get_direct_access_buttons(direct_config)
            _status['direct_access_buttons'] = temp
        except Exception:
            _status['direct_access_buttons'] = {}
            pass

        return state, capabilities, _status

    except Exception as err:
        message = err.message
        raise Exception(message)


def verify_state_and_capabilities(reference_designator, state, capabilities, expected_state, expected_capability):
    """ Verify current state and capabilities match expected state and capability. Raise if not.
    """
    NOT_NONE = 'NOT_NONE'
    try:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify state
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If expected_state is None, raise exception
        if expected_state is None:
            message = 'Instrument (%s) not in %s, current state is %s.' % \
                              (reference_designator, expected_state, state)
            raise Exception(message)

        # If current state is not the state expected, raise exception
        if state != expected_state:
            message = 'Instrument (%s) not in %s state, current state is %s.' % \
                      (reference_designator, expected_state, state)
            raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify capability
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If not capabilities provided in current state, raise exception
        if not capabilities:
            message = 'Instrument (%s) did not return capabilities; current state %s.' % \
                      (reference_designator, state)
            raise Exception(message)

        # If capabilities expected but unknown use NOT_NONE, there are no capabilities, raise exception
        if expected_capability == NOT_NONE:
            if not capabilities:
                message = 'Instrument (%s) does not have any capabilities; current state %s.' % \
                      (reference_designator, state)
                raise Exception(message)

        # If expected capability not provided, raise exception
        elif expected_capability not in capabilities:
            message = 'Instrument (%s) does not have %s capability; current state %s.' % \
                      (reference_designator, expected_capability, state)
            raise Exception(message)

    except Exception:
        raise


def send_command(rd, command, ip, data):
    """ Send command to rd using ip and data [port]. Sample command: '$met\r\n'
    """
    try:
        c = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        c.connect((ip, data))
        content = command
        c.sendall(content)
        c.shutdown(sock.SHUT_WR)
        c.close()
        return
    except ConnectionError:
        message = 'ConnectionError for direct access during send_command.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for direct access during send_command.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Instrument %s exception during send command %s. Error: %s' % (rd, command, str(err))
        current_app.logger.info(message)
        raise


def get_direct_access_buttons(direct_config):
    """ Get READ_ONLY and IMMUTABLE display values for UI from instrument 'parameters' dictionary.

    Sample Input:
    "direct_config": [
      {
        "character_delay": 0.0,
        "data": 40291,
        "eol": "\r\n",
        "input_dict": {
          "Interrupt": "!!!!!",
          "Print Menu": "$mnu\r\n",
          "Print Metadata": "$met\r\n",
          "Read Data": "$get\r\n",
          "Restore Factory Defaults": "$rfd\r\n",
          "Restore Settings": "$rls\r\n",
          "Run Settings": "$run\r\n",
          "Run Wiper": "$mvs\r\n",
          "Save Settings": "$sto\r\n",
          "Set Clock>": "$clk ",
          "Set Date>": "$date \r\n",
          "Set>": "set "
        },
        "ip": "uft20",
        "sniffer": 60641,
        "title": "FLOR"
      }
    ],
        . . .

    Sample Output:
    ['Interrupt', 'Print Menu', 'Print Metadata', 'Read Data', 'Restore Factory Defaults',
        'Restore Settings', 'Run Settings', 'Run Wiper', 'Save Settings', 'Set Clock>', 'Set Date>', 'Set>']
        . . .

    """
    result = []
    try:
        # If no direct_config, then return empty dict.
        if not direct_config:
            return result

        # If direct_config does not have attribute 'input_dict', raise error.
        if 'input_dict' not in direct_config[0]:
            return result

        # If direct_config attribute 'input_dict' is empty, raise error.
        if not direct_config[0]['input_dict']:
            return result

        # Create list of direct access buttons
        input_dict = direct_config[0]['input_dict']
        result = input_dict.keys()
        result.sort()
        return result

    except Exception as err:
        current_app.logger.info(err.message)
        raise