#!/usr/bin/env python
"""
API v1.0 Command and Control (C2) direct access routes:

    Enter direct access mode:       /c2/instrument/<string:reference_designator>/direct_access/start
    Execute direct access command   /c2/instrument/<string:reference_designator>/direct_access/execute
    Exit direct access mode:        /c2/instrument/<string:reference_designator>/direct_access/exit
"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app, request
from ooiservices.app.decorators import scope_required
from ooiservices.app.main import api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.c2 import _c2_get_instrument_driver_status
import json


# Direct Access start.
# todo deprecate 'GET' and remove fake_data
@api.route('/c2/instrument/<string:reference_designator>/direct_access/start', methods=['POST', 'GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_direct_access_start(reference_designator):
    """ Start direct access. (when button 'Start Direct' is selected.)

    (Transition from 'DRIVER_STATE_COMMAND' to 'DRIVER_STATE_DIRECT_ACCESS'.)
    """
    log = False
    fake_data = True
    rd = reference_designator

    NOT_NONE = 'NOT_NONE'
    state_DRIVER_STATE_COMMAND = 'DRIVER_STATE_COMMAND'
    capability_DRIVER_EVENT_START_DIRECT = 'DRIVER_EVENT_START_DIRECT'
    target_state = 'DRIVER_STATE_DIRECT_ACCESS'

    try:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare to execute - direct access start command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if log:
            message = 'Log -- (%s) Get instrument state and capabilities.' % rd
            current_app.logger.info(message)

        # Validate reference_designator
        _state, _capabilities, fake_response = direct_access_get_state_and_capabilities(rd)
        if log:
            message = '----- (%s) Instrument state (%s) and capabilities (%s)' % (rd, _state, _capabilities)
            current_app.logger.info(message)

        # Verify _state and _capabilities match expected state and capabilities
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=state_DRIVER_STATE_COMMAND,
                                      expected_capability=capability_DRIVER_EVENT_START_DIRECT)

        if log:
            message = 'Instrument %s in %s state and has %s capability. Start direct access.' % \
                      (rd, _state, capability_DRIVER_EVENT_START_DIRECT)
            current_app.logger.info(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Execute - direct access command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Log current state, capability and action
        if log:
            message = '----- (%s) Instrument state (%s) and capabilities (%s)' % (rd, _state, _capabilities)
            current_app.logger.info(message)

        if fake_data:
            _state = target_state
            result = direct_access_start_update_response(fake_response, target_state)

        else:
            # todo EXECUTE DIRECT ACCESS EXECUTE COMMAND with command_request (using upstream server)
            result = None

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Final - direct access response final checks for success or failure
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify _state and _capabilities match expected state and capabilities
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=target_state,
                                      expected_capability=NOT_NONE)

        return jsonify(result)

    except Exception as err:
        message = '(%s) exception: %s' % (rd, err.message)
        current_app.logger.info(message)
        return bad_request(err.message)


# Direct Access execute command.
# todo deprecate 'GET' and remove fake_data
@api.route('/c2/instrument/<string:reference_designator>/direct_access/execute', methods=['POST', 'GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_direct_access_execute(reference_designator):
    """ Execute direct access command.

    While in 'DRIVER_STATE_DIRECT_ACCESS', execute commands sent from direct access terminal window.

    Process direct access terminal commands:
        Receive content, send to instrument driver.
        Upon receipt of response from instrument, forward response to UI.

    POST request.data shall provide attribute 'command_request':
    {
    'command_request': 'some direct access command text to process...'
    }

    """
    log = False
    fake_data = True
    rd = reference_designator
    command_request = None
    command_response = None
    embedded_command_response = 'Received direct access command request; this is your response!!'

    NOT_NONE = 'NOT_NONE'
    state_DRIVER_STATE_DIRECT_ACCESS = 'DRIVER_STATE_DIRECT_ACCESS'
    capability_DRIVER_EVENT_EXIT_DIRECT = 'DRIVER_EVENT_EXIT_DIRECT'   # todo verify capability name
    target_state = state_DRIVER_STATE_DIRECT_ACCESS

    try:
        # Get request data
        request_data = None
        if request.data:

            # Get request data
            request_data = json.loads(request.data)

            # Process request_data
            if request_data is None:
                message = 'Direct access execute command did not receive request data for instrument %s.' % rd
                current_app.logger.info(message)
                raise Exception(message)

            if 'command_request' not in request_data:
                message = 'Malformed direct access execute command, no command_request (instrument %s).' % rd
                current_app.logger.info(message)
                raise Exception(message)

            command_request = request_data['command_request']

        if command_request is None:
            message = 'No direct access command data provided for instrument %s.' % rd
            current_app.logger.info(message)
            if not fake_data: raise Exception(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare to execute - direct access start command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if log:
            message = 'Log -- (%s) Get instrument state and capabilities.' % rd
            current_app.logger.info(message)

        # Validate reference_designator
        _state, _capabilities, fake_response = direct_access_get_state_and_capabilities(rd)
        if log:
            message = '----- (%s) Instrument state (%s) and capabilities (%s)' % (rd, _state, _capabilities)
            current_app.logger.info(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Execute - direct access command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fake_data:
            _state = target_state
            result = direct_access_start_update_response(fake_response, target_state,
                                                         command_response=embedded_command_response)
        else:
            # Verify current _state and _capabilities match expected state and capabilities
            verify_state_and_capabilities(rd, _state, _capabilities,
                                          expected_state=state_DRIVER_STATE_DIRECT_ACCESS,
                                          expected_capability=NOT_NONE)
            if log:
                message = 'Instrument %s in %s state and has %s capability. Start direct access.' % \
                          (rd, _state, capability_DRIVER_EVENT_EXIT_DIRECT)
                current_app.logger.info(message)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Execute - direct access command
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # todo EXECUTE DIRECT ACCESS EXECUTE COMMAND with command_request (using upstream server)
            result = None

        # Log current state, capability and action
        if log:
            message = '----- (%s) Instrument state (%s) and capabilities (%s)' % (rd, _state, _capabilities)
            current_app.logger.info(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Final - direct access response final checks for success or failure
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify _state and _capabilities match expected state and capabilities
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=target_state,
                                      expected_capability=NOT_NONE)

        return jsonify(result)
    except Exception as err:
        message = '(%s) exception: %s' % (reference_designator, err.message)
        current_app.logger.info(message)
        return bad_request(err.message)


# Direct Access exit
# todo deprecate 'GET' and remove fake_data
@api.route('/c2/instrument/<string:reference_designator>/direct_access/exit', methods=['POST', 'GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_direct_access_exit(reference_designator):
    """ Exit direct access. (when button 'Exit Direct' is selected.)

    Transition from 'DRIVER_STATE_DIRECT_ACCESS' to 'DRIVER_EVENT_EXIT_DIRECT'
    """
    log = False
    fake_data = True
    rd = reference_designator

    NOT_NONE = 'NOT_NONE'
    state_DRIVER_STATE_DIRECT_ACCESS = 'DRIVER_STATE_DIRECT_ACCESS'
    capability_DRIVER_EVENT_EXIT_DIRECT = 'DRIVER_EVENT_EXIT_DIRECT'   # todo verify capability
    target_state = 'DRIVER_STATE_COMMAND'

    try:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Prepare to execute - direct access start command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if log:
            message = 'Log -- (%s) Get instrument state and capabilities.' % rd
            current_app.logger.info(message)

        # Validate reference_designator
        _state, _capabilities, fake_response = direct_access_get_state_and_capabilities(rd)
        if log:
            message = '----- (%s) Instrument state (%s) and capabilities (%s)' % (rd, _state, _capabilities)
            current_app.logger.info(message)

        if fake_data:
            # Log current state, capability and action
            if log:
                message = '----- (%s) Instrument state (%s) and capabilities (%s)' % (rd, _state, _capabilities)
                current_app.logger.info(message)

        else:
            # Verify current _state and _capabilities match expected state and capabilities
            verify_state_and_capabilities(rd, _state, _capabilities,
                                          expected_state=state_DRIVER_STATE_DIRECT_ACCESS,
                                          expected_capability=capability_DRIVER_EVENT_EXIT_DIRECT)

            if log:
                message = 'Instrument %s in %s state and has %s capability. Start direct access.' % \
                          (rd, _state, capability_DRIVER_EVENT_EXIT_DIRECT)
                current_app.logger.info(message)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Execute - direct access command
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if fake_data:
            # direct access simulated response (fake_response) with target state
            _state = target_state
            result = direct_access_start_update_response(fake_response, target_state)
        else:
            # todo EXECUTE DIRECT ACCESS EXIT COMMAND (using upstream server)
            print '\n direct access: issue command exit to upstream server'
            result = None

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Final - direct access response final checks for success or failure
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify _state and _capabilities match expected state and capabilities
        verify_state_and_capabilities(rd, _state, _capabilities,
                                      expected_state=target_state,
                                      expected_capability=NOT_NONE)

        return jsonify(result)

    except Exception as err:
        message = '(%s) exception: %s' % (reference_designator, err.message)
        current_app.logger.info(message)
        return bad_request(err.message)

#==================================================================
# SUPPORTING FUNCTIONS...
#==================================================================
# todo remove return _status (for fake_response)
def direct_access_get_state_and_capabilities(reference_designator):
    """ Get current state and capabilities information for an instrument.
    Overview:
        Get instrument status
        Get state rom resulting status
        Get capabilities from resulting status
        Return state, capabilities and (for now) _status to be used for fake_response
    """
    debug = False
    state = None
    capabilities = []
    try:
        # Get instrument status.
        try:
            _status = _c2_get_instrument_driver_status(reference_designator)
            if debug:
                #print '\n debug ***** status: %s' % json.dumps(_status, indent=4, sort_keys=True)
                print '\n debug -- _status[value][state]: ', _status['value']['state']
                print '\n debug -- _status[value][capabilities]: ', _status['value']['capabilities'][0]
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


# todo remove when up stream services are available.
def direct_access_start_update_response(fake_response, target_state, command_response=None):
    """ Update response status 'state' attribute to target state.
    Modify capabilities and commands iff processing execute state
    """
    execute_state = 'DRIVER_STATE_DIRECT_ACCESS'
    #start_state = 'DRIVER_STATE_COMMAND'
    target_capabilities = [
          "DRIVER_EVENT_EXIT_DIRECT",
          "DRIVER_EVENT_DIRECT_ACTION_1",
          "DRIVER_EVENT_DIRECT_ACTION_2"]
    target_commands = {
            "DRIVER_EVENT_EXIT_DIRECT": {
            "arguments": {},
            "display_name": "Exit",
            "return": {},
            "timeout": 20
          },
            "DRIVER_EVENT_DIRECT_ACTION_1": {
            "arguments": {},
            "display_name": "Action 1",
            "return": {},
            "timeout": 10
          },
            "DRIVER_EVENT_DIRECT_ACTION_2": {
            "arguments": {},
            "display_name": "Action 2",
            "return": {},
            "timeout": 10
          },
        }

    try:
        # Update result with content provided from instrument/driver
        result = fake_response

        # Always update target state to what we expect
        result['value']['state'] = target_state

        # Modify capabilities and commands iff processing execute state
        #if target_state != execute_state:
        if target_state == execute_state:
            result['value']['metadata']['commands'] = target_commands
            result['value']['capabilities'][0] = target_capabilities
            if command_response is not None:
                result['direct_access_response'] = command_response

        return result

    except:
        raise


#==================================================================
# CONSTRUCTION ZONE...
#==================================================================
'''
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
'''