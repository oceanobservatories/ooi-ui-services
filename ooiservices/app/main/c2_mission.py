#!/usr/bin/env python
'''
API v1.0 Command and Control (C2) routes for Mission Control
'''
__author__ = 'Edna Donoughe'

from flask import jsonify, request, current_app
from ooiservices.app.main import api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
import json
import requests
import datetime as dt


from ooiservices.app.main.c2 import read_store, read_store2
from ooiservices.app.main.c2 import _get_platform, _get_instrument, _get_instruments


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 Mission Control routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/missions', methods=['GET'])
#@auth.login_required
#@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_get_missions():
    """
    Get list of missions.
    """
    debug = False
    missions = []
    try:
        active = None
        if request.args:
            if 'active' in request.args:
                active = to_bool(request.args['active'])
        result = uframe_get_missions(active)
        if result is not None:
            missions = result
        return jsonify(missions=missions)
    except Exception as err:
        message = str(err.message)
        if debug: print '\n (c2_get_missions) exception: ', message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<string:mission_id>', methods=['GET'])
#@api.route('/c2/missions/<int:mission_id>', methods=['GET'])
#@auth.login_required
#@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_get_mission(mission_id):
    """
    Get a mission.
    """
    debug = False
    try:
        result = uframe_get_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission)

    except Exception as err:
        message = err.message
        if debug: print '\n exception: ', err.message
        current_app.logger.info(message)
        return bad_request(message)

@api.route('/c2/missions/<string:mission_id>/keys', methods=['GET'])
#@api.route('/c2/missions/<int:mission_id>/keys', methods=['GET'])
#@auth.login_required
#@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_get_mission_keys(mission_id):
    """
    Get a mission.
    """
    debug = False
    try:
        result = uframe_get_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission.keys())

    except Exception as err:
        message = err.message
        if debug: print '\n exception: ', err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<string:mission_id>', methods=['DELETE'])
#@api.route('/c2/missions/<int:mission_id>', methods=['DELETE'])
#@auth.login_required
#@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_delete_mission(mission_id):
    """
    Delete a mission.
    """
    mission = {}
    result = uframe_delete_mission(mission_id)
    if result is not None:
        mission = result
    return jsonify(mission)


@api.route('/c2/missions/<string:mission_id>/activate', methods=['GET'])
#@api.route('/c2/missions/<int:mission_id>/activate', methods=['GET'])
#@auth.login_required
#@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_activate_mission(mission_id):
    """
    Activate a mission.
    """
    debug = False
    try:
        if debug: print '\n (c2_activate_mission) '
        result = uframe_activate_mission(mission_id)
        if debug: print '\n (c2_activate_mission) result: ', result
        mission = get_mission_info(mission_id, result)
        if debug: print '\n (c2_activate_mission) mission: ', mission
        return jsonify(mission=mission)
    except Exception as err:
        message = err.message
        if debug: print '\n exception: ', err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<string:mission_id>/deactivate', methods=['GET'])
#@api.route('/c2/missions/<int:mission_id>/deactivate', methods=['GET'])
#@auth.login_required
#@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_deactivate_mission(mission_id):
    """
    Deactivate a mission.
    """
    debug = False
    try:
        result = uframe_deactivate_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission), 200
    except Exception as err:
        message = err.message
        if debug: print '\n exception: ', err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions', methods=['POST'])
#@auth.login_required
#@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_add_mission():
    """
    Add a mission.
    """
    debug = False
    try:
        if request.data is None:
            message = 'Provide request data to add new mission.'
            raise Exception(message)
        data = json.loads(request.data)
        result = uframe_add_mission(data)

        if result is None or len(result) == 0:
            message = 'Failed to add new mission.'
            raise Exception(message)
        if 'name' not in result:
            message = 'Malformed mission data; required field \'name\' not returned.'
            raise Exception(message)

        mission_id = result['name']
        result = uframe_get_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission), 201

    except Exception as err:
        message = err.message
        if debug: print '\n exception: ', err.message
        current_app.logger.info(message)
        return bad_request(message)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# uframe helpers
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_get_missions(active=None):
    """ Helper for get missions; issue upstream server request, process response and return missions.
    Sample of uframe request executed:    http://localhost:port/missions
    """
    result = []
    try:
        response = uframe_issue_get_request(method='get', suffix=None)
        if response.status_code != 200:
            message = '(%s) Failed to get missions. ' % response.status_code
            raise Exception(message)

        missions = json.loads(response.content)
        for key in missions.keys():
            tmp = get_mission_info(key, missions[key])
            if active is None:
                result.append(tmp)
            else:
                if tmp['active'] == active:
                    result.append(tmp)
        return result
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_get_mission(id):
    """ Get mission.
    Sample request executed:    http://localhost:port/mission/mission_id
    response:
    """
    debug = False
    mission = {}
    try:
        suffix = '/%s' % str(id)
        #result = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to get mission \'%s\'. ' % (response.status_code, str(id))
            if debug: print '\n (uframe_get_mission) message: ', message
            raise Exception(message)
        if response.content:
            if debug:
                print '\n response_status_code == 200'
                print '\n response.content: ', response.content
            mission = json.loads(response.content)
            if debug:  print '\n mission: ', mission
        return mission
    except Exception as err:
        message = str(err.message)
        if debug: print '\n message: ', message
        current_app.logger.info(message)
        raise

# todo finish when DELETE supported on upstream server
def uframe_delete_mission(id):
    """ Delete mission.
    Sample:
    request:    http://localhost:port/mission/mission_id
    response:
    """
    debug = False
    mission = {}
    try:
        suffix = '/%s' % str(id)
        #result = uframe_issue_get_request(method='delete', suffix=suffix, data=None)
        response = uframe_issue_get_request(method='delete', suffix=suffix, data=None)
        if response.status_code != 200:
            if debug: print'\n (uframe_delete_mission) response.status_code: ', response.status_code
            message = '(%d) Failed to delete mission \'%s\'. ' % (response.status_code, str(id))
            raise Exception(message)
        if response.content:
            if debug:
                print '\n response_status_code == 200'
                print '\n response.content: ', response.content
            mission = json.loads(response.content)
            if debug:  print '\n mission: ', mission
        return mission
    except Exception as err:
        message = str(err.message)
        if debug: print '\n message: ', message
        current_app.logger.info(message)
        raise


def uframe_activate_mission(id):
    """ Activate mission.
    Sample:
    request:    http://localhost:port/mission/mission_id/activate
    response:
    """
    debug = False
    mission = {}
    try:
        if debug: print '\n (uframe_activate_mission) mission_id: ', id
        suffix = '/%s/activate' % str(id)
        #result = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to activate mission \'%s\'. ' % (response.status_code, str(id))
            if debug: print '\n (uframe_activate_mission) message: ', message
            raise Exception(message)
        if response.content:
            if debug:
                print '\n (uframe_activate_mission) response_status_code == 200'
                print '\n (uframe_activate_mission) response.content: ', response.content
            mission = json.loads(response.content)
            if debug:  print '\n (uframe_activate_mission) mission: ', mission
        return mission
    except Exception as err:
        message = str(err.message)
        if debug: print '\n (uframe_activate_mission) exception message: ', message
        current_app.logger.info(message)
        raise


def uframe_deactivate_mission(id):
    """ Deactivate mission.
    Sample:
    request:    http://localhost:port/mission/mission_id/deactivate
    response:
    """
    debug = False
    mission = {}
    try:
        suffix = '/%s/deactivate' % str(id)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to deactivate mission \'%s\'. ' % (response.status_code, str(id))
            if response.content:
                message += json.loads(response.content)
            if debug: print '\n (uframe_deactivate_mission) message: ', message
            raise Exception(message)
        if response.content:
            if debug:
                print '\n response_status_code == 200'
                print '\n response.content: ', response.content
            mission = json.loads(response.content)
            if debug:  print '\n mission: ', mission
        return mission
    except Exception as err:
        message = str(err.message)
        if debug: print '\n message: ', message
        current_app.logger.info(message)
        raise


def uframe_add_mission(data):
    """ Add mission using post method.
    request:    http://localhost:port/mission/mission_id
    response:
    """
    debug = False
    try:
        result = uframe_issue_get_request(method='post', suffix=None, data=data)
        return result
    except Exception as err:
        message = str(err.message)
        if debug: print '\n message: ', message
        current_app.logger.info(message)
        raise

def get_mission_info(mission_id, result):
    """
    Set return mission object content for ui.
    Using active/running to build the status:
    active | running | status
    F | F | inactive
    T | F | loaded
    T | T | running

    Fields provided (10-27-2015):
    "active": true,
    "created": "2015-10-26T22:12:50.044857",
    "current_step": null,
    "events"
    "name": "BOTPT_periodic_acquire_status",
    "next_run": "2015-10-27T09:58:00+00:00",
    "run_count": 704,
    "running": false,
    "schedule": {"second": 0},
    "version": "1-00"
    """
    mission = {}
    name = ''
    desc = ''
    running = False
    active = False
    version = ''
    events = []
    created = ''
    next_run = ""
    schedule = {}
    run_count = -1
    body = {}
    drivers = []

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # todo remove this script from file processing
    # Display something for script; use previous work to display script file contents (for now).
    mission_plan = ''
    try:
        mission_plan = _get_mission_selection(mission_id) #'BOTPT_periodic_acquire_status')
        # If no mission_plan in test data, display default ('mission_shallow_profiler')
        if mission_plan is None or not mission_plan:
            mission_plan = _get_mission_selection('mission_shallow_profiler') #mission_id) #'BOTPT_periodic_acquire_status')
        #print '\n mission_plan: ', mission_plan
    except:
        message = 'exception fetching contents of mission plan from file datastore for mission: %s' % str(mission_id)
        #if debug: print '\n mission response processing exception: ', message
        current_app.logger.info(message)
        raise Exception(message)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if result is not None:
        tmp = result
        name = tmp['name']
        version = tmp['version']
        active = tmp['active']
        running = tmp['running']
        events = tmp['events']
        created = tmp['created']
        next_run = tmp['next_run']
        schedule = tmp['schedule']
        run_count = tmp['run_count']

        # todo remove default here when 'desc' field provided in response
        desc = 'Element \'desc\' not provided.'
        if 'desc' in tmp:
            desc = tmp['desc']

        # todo remove default here when 'drivers' field provided in response
        drivers = ['Element \'drivers\' not provided.']
        if 'drivers' in tmp:
            drivers = tmp['drivers']

    # Process events
    events = []
    if 'events' in result:
        if result['events'] is not None or result['events']:
            event_data = result['events']
            events = process_events(event_data)

    # Populate resulting mission dictionary values
    mission['name'] = name
    mission['version'] = version
    mission['active'] = active
    mission['running'] = running
    mission['events'] = events
    mission['created'] = created
    mission['next_run'] = next_run
    mission['schedule'] = schedule
    mission['run_count'] = run_count

    # if not used downstream, remove
    mission['mission_id'] = mission_id

    # todo remove when available - currently missing fields....populating with sample information
    mission['mission'] = mission_plan[0]
    mission['desc'] = desc
    mission['drivers'] = drivers

    # Set state (using 'active') ['Active' | 'Inactive']
    if active:
        state = 'Active'
    else:
        state = 'Inactive'

    # Determine status (uses 'active' and 'running'; valid status: ['Inactive', 'Loaded', 'Running']
    if not active:
        status = 'Inactive'
    else:
        status = 'Loaded'
        if running:
            status = 'Running'
    mission['status']= status
    mission['state'] = state
    return mission


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# uframe specific functions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_uframe_info():
    """
    returns uframe C2 mission api specific configuration information.
    """
    uframe_url = "".join([current_app.config['UFRAME_MISSIONS_URL'], current_app.config['UFRAME_MISSIONS_BASE']])
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read


def uframe_issue_get_request(method='get', suffix=None, data=None):
    """ Issue uframe get request; returns response.content as result, otherwise None or raise Exception.
    """
    debug = False
    valid_methods = ['get', 'post', 'delete']
    headers = {"Content-Type": "application/json"}
    try:
        # Determine if supported/valid method request (i.e. one of valid_methods)
        if method not in valid_methods:
            message = 'Unknown or unsupported method for uframe request: %s' % method
            if debug: print '\n message: ', message
            raise Exception(message)

        # Setup basic request info
        url, timeout, timeout_read = get_uframe_info()
        if suffix is not None:
            url += suffix

        if debug: print '\n (uframe_issue_get_request) %s url: %s' % (method.upper(), url)
        # Get response based on method
        # Methods: 'get' and 'delete'
        response = None
        if method == 'get' or method == 'delete':
            if method == 'get':
                response = requests.get(url, timeout=(timeout, timeout_read))
            elif method == 'delete':
                response = requests.delete(url, timeout=(timeout, timeout_read))

        # Methods: 'post' and 'put'
        else:
            if method == 'post':
                response = requests.post(url, timeout=(timeout, timeout_read), headers=headers, data=json.dumps(data))

        return response
    except Exception as err:
        message = str(err.message)
        #print '\n (uframe_issue_get_request) exception: ', message
        current_app.logger.info(message)
        raise

def process_events(data):
    """
    Process response events data, return list of event dictionaries:

    About events:
        [
         [timestamp, event type, event text],
         [timestamp, event type, event text],
         ...
        ]

    Sample output showing events as a list of lists
    {
      "active": true,
      "created": "2015-10-26T22:12:50.044857",
      "current_step": null,
      "events": [
        [
          "2015-10-27T13:52:00.020653",
          "start",
          ""
        ],
        [
          "2015-10-27T13:52:00.037720",
          "lock",
          "RS10ENGC-XX00X-00-BOTPTA001"
        ],
        ...
      ]
    '''
    """
    events = []
    for item in data:
        event = {}
        timestamp = ''
        event_type = ''
        event_text = None
        if item[0] is not None:
            timestamp = item[0]
        if item[1] is not None:
            event_type = item[1]

        if item[2] is not None:
            event_text = str(item[2])
            if len(event_text) > 60:
                event_text = str(event_text)[0:60] + ' ...'
            #print '\n event_text: ', event_text

        event['timestamp'] = timestamp
        event['event_type'] = event_type
        event['event_text'] = event_text

        events.append(event)

    return events


def to_bool(value):
    """ Converts 'something' to boolean. Raises exception for invalid formats.
    Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
    Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    Otherwise None
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    elif str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    else:
        return None

#==============================================================================
#==============================================================================

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 Mission Control - array routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/array/<string:array_code>/mission_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_array_mission_display(array_code):
    #Get C2 array mission (display), return mission_display (contents of platform Mission tab)
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    mission_display = {}
    return jsonify(mission_display=mission_display)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 Mission Control - platform
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/platform/<string:reference_designator>/mission/instruments_list', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_mission_instruments_list(reference_designator):
    """
    C2 get [platform] Mission tab instruments_list, return instruments [{instrument1}, {instrument2}, ...]
    where each instrument dictionary (is a row in instruments list) contains:
       {'reference_designator': reference_designator, 'instrument_deployment_id': id, 'display_name': display_name }
    Samples:
      http://localhost:4000/c2/platform/reference_designator/mission/instruments_list
    Request:  http://localhost:4000/c2/platform/RS03ASHS-MJ03B/mission/instruments_list
    Response:
    {
      "instruments": [
        {
          "display_name": "Diffuse Vent Fluid 3-D Temperature Array",
          "reference_designator": "RS03ASHS-MJ03B-07-TMPSFA301"
        }
      ]
    }
    """
    contents = []
    platform_info = {}
    platform_deployment = _get_platform(reference_designator)
    if platform_deployment:
        # get ordered set of instrument_deployments for platform
        # Get instruments for this platform
        instruments, oinstruments = _get_instruments(reference_designator)
        # create list of reference_designators (instruments) and accumulate dict result (key=reference_designator) for output
        for instrument_deployment in instruments:
            row = {}
            row['reference_designator'] = instrument_deployment['reference_designator']
            if instrument_deployment['display_name']:
                row['display_name'] = instrument_deployment['display_name']
            else:
                row['display_name'] = instrument_deployment['reference_designator']
            platform_info[instrument_deployment['reference_designator']] = row

        # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
        # 'data' == rows for initial grid ('Current Status')
        for instrument_reference_designator in oinstruments:
            if instrument_reference_designator in platform_info:
                contents.append(platform_info[instrument_reference_designator])
    return jsonify(instruments=contents)

@api.route('/c2/platform/<string:reference_designator>/mission_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_mission_display(reference_designator):
    #Get C2 platform Mission tab contents, return mission_display
    mission_display = {}
    platform = _get_platform(reference_designator)
    if platform:
        mission_display = {}  # todo populate display content
    return jsonify(mission_display=mission_display)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 Mission Control - instrument
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/instrument/<string:reference_designator>/mission_display', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_mission_display(reference_designator):
    #Get C2 instrument Mission tab contents, return mission_display
    mission_display = {}
    instrument = _get_instrument(reference_designator)
    if instrument:
        mission_display = {}  # todo populated display content
    return jsonify(mission_display=mission_display)

@api.route('/c2/platform/<string:reference_designator>/mission_selections', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_mission_selections(reference_designator):
    # C2 get platform Mission tab mission selections content, return mission_selections [{},{}...]
    # return list of platform mission plans
    mission_selections = []
    platform = _get_platform(reference_designator)
    if platform:
        mission_selections = _get_mission_selections(reference_designator)
    return jsonify(mission_selections=mission_selections)

@api.route('/c2/instrument/<string:reference_designator>/mission_selections', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_mission_selections(reference_designator):
    # C2 get instrument Mission tab mission selections content, return mission_selections [{},{}...]
    # return list of instrument mission plans
    # Sample: http://localhost:4000/c2/instrument/RS03ASHS-MJ03B-07-TMPSFA301/mission_selections
    '''
    {
      "mission_selections": [
        {
          "last-modified": "2014-11-23T20:00:00",
          "mission_name": "Shallow Profiler",
          "store": "mission_shallow_profiler"
        },
        {
          "last-modified": "2014-12-12T09:20:00",
          "mission_name": "Mission 1",
          "store": "mission1"
        },
        . . .
        {
          "last-modified": "2015-03-14T07:14:00",
          "mission_name": "Mission 4",
          "store": "mission4"
        }
      ]
    }
    '''
    mission_selections = []
    instrument = _get_instrument(reference_designator)
    if instrument:
        mission_selections = _get_mission_selections(reference_designator)
    return jsonify(mission_selections=mission_selections)

@api.route('/c2/platform/<string:reference_designator>/mission_selection/<string:mission_plan_store>', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_platform_mission_selection(reference_designator, mission_plan_store):
    # C2 get [platform] selected mission_plan content, return mission_plan
    # http://localhost:4000/c2/instrument/RS03ASHS-MJ03B-07-TMPSFA301/mission_selection/mission4
    '''
    {
      "mission_plan": [
        "name: Mission 4\rversion: 0.4\rdescription: Shallow Profiler Mission\r\r\r
        platform:\r  platformID: SWPROF\rmission:\r  - missionThread: \r    instrumentID: ['OPTAA', 'PCO2W', 'CTDPF']\r
            errorHandling:\r      default: retry\r      maxRetries: 3\r    schedule:\r      startTime: 2014-07-18T00:00:00\r
              timeZone:\r      loop:\r        quantity: -1   # No. of loops (-1 for infinite)\r
                      value: 1      # Repeat missionParams every 'xx' 'units'\r
                              units: hrs    # mins, hrs, days\r      event:\r
                                      parentID:\r
                                              eventID:\r    preMissionSequence:\r
                                                    - command: SWPROF, execute_resource(TURN_ON_PORT{OPTAA})\r
                                                            onError: retry\r
                                                                  - command: SWPROF, execute_resource(TURN_ON_PORT{PCO2W})\r
                                                                          onError: retry\r      - command: SWPROF, execute_resource(TURN_ON_PORT{CTDPF})\r        onError: retry\r      - command: SWPROF, execute_resource(CLOCK_SYNC)\r        onError: retry\r      - command: OPTAA, execute_resource(CLOCK_SYNC)\r        onError: retry\r      - command: PCO2W, execute_resource(CLOCK_SYNC)\r        onError: retry\r      - command: CTDPF, execute_resource(CLOCK_SYNC)\r        onError: retry\r    missionSequence:\r      - command: SWPROF, execute_resource(TURN_ON_PORT{OPTAA})\r        onError: retry\r      - command: OPTAA, execute_agent(INITIALIZE) #OPTAA INACTIVE\r        onError: retry\r        onError: retry\r      - command: CTDPF, execute_agent(RUN) #CTD COMMAND\r        onError: retry\r      - command: CTDPF, set_resource(INTERVAL{1}) #CTD Set sampling interval\r        onError: retry\r      - command: CTDPF, execute_resource(START_AUTOSAMPLE)\r        onError: retry\r      - command: SWPROF, execute_resource(TURN_OFF_PORT{PCO2W})\r        onError: retry\r      - command: SWPROF, execute_resource(LOAD_MISSION{0})\r        onError: retry\r      - command: SWPROF, execute_resource(RUN_MISSION{0})\r        onError: retry\r    postMissionSequence:\r\r\r  - missionThread: \r    instrumentID: [SWPROF OPTAA]\r    errorHandling:\r      default: retry\r      maxRetries: 3\r    schedule:\r      startTime:\r      timeZone:\r      loop:\r        quantity:\r        value:\r        units:\r      event:\r        parentID: SWPROF\r        eventID: PROFILER_AT_CEILING\r    preMissionSequence:\r    missionSequence:\r      - command: OPTAA, execute_agent(GO_INACTIVE) #OPTAA INACTIVE\r        onError: retry\r      - command: SWPROF, execute_resource(TURN_OFF_PORT{OPTAA})\r        onError: retry\r    postMissionSequence:\r\r\r  - missionThread: \r    instrumentID: [SWPROF, PCO2W]\r    errorHandling:\r      default: retry\r      maxRetries: 3\r    schedule:\r      startTime:\r      timeZone:\r      loop:\r        quantity:\r        value:\r        units:\r      event:\r        parentID: SWPROF\r        eventID: PROFILER_AT_STEP\r    preMissionSequence:\r    missionSequence:\r      - command: PCO2W, execute_agent(GO_ACTIVE) #PCO2W IDLE\r        onError: retry\r      - command: PCO2W, execute_agent(RUN) #PCO2W COMMAND\r        onError: retry\r      - command: PCO2W, set_resource(INTERVAL{1}) #PCO2W Set Sampling Interval\r        onError: retry\r      - command: PCO2W, execute_resource(ACQUIRE_SAMPLE)\r        onError: retry\r      - command: PCO2W, execute_agent(GO_INACTIVE)\r        onError: retry\r    postMissionSequence:\r\r\r  - missionThread: \r    instrumentID: [SWPROF, OPTAA, PCO2W, CTDPF]\r    errorHandling:\r      default: retry\r      maxRetries: 3\r    schedule:\r      startTime:\r      timeZone:\r      loop:\r        quantity:\r        value:\r        units:\r      event:\r        parentID: SWPROF\r        eventID: PROFILER_AT_FLOOR\r    preMissionSequence:\r    missionSequence:\r      - command: CTDPF, execute_resource(STOP_AUTOSAMPLE)\r        onError: retry\r      - command: CTDPF, execute_agent(GO_INACTIVE)\r        onError: retry\r      - command: SWPROF, execute_resource(CLOCK_SYNC)\r        onError: retry\r      - command: OPTAA, execute_resource(CLOCK_SYNC)\r        onError: retry\r      - command: PCO2W, execute_resource(CLOCK_SYNC)\r        onError: retry\r      - command: CTDPF, execute_resource(CLOCK_SYNC)\r        onError: retry\r    postMissionSequence:"
      ]
    }

    '''
    if not mission_plan_store:
        return bad_request('mission_plan_store parameter is empty')
    mission_plan = {}
    platform = _get_platform(reference_designator)
    if platform:
        mission_plan = _get_mission_selection(mission_plan_store)
    return jsonify(mission_plan=mission_plan)

@api.route('/c2/instrument/<string:reference_designator>/mission_selection/<string:mission_plan_store>', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
def c2_get_instrument_mission_selection(reference_designator, mission_plan_store):
    # C2 get [instrument] selected mission_plan content from store (file, uframe), return mission_plan
    if not mission_plan_store:
        return bad_request('mission_plan_store parameter is empty')
    mission_plan = {}
    instrument = _get_instrument(reference_designator)
    if instrument:
        mission_plan = _get_mission_selection(mission_plan_store)
    return jsonify(mission_plan=mission_plan)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private helper methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _get_mission_selections(reference_designator):
    mission_selections = []
    response_text = json_get_uframe_mission_selections(reference_designator)
    if response_text:
        try:
            mission_selections = json.loads(response_text)
        except:
            return bad_request('Malformed mission_selections; not in valid json format. (reference designator \'%s\')'
                               % reference_designator)
    return mission_selections

def _get_mission_selection(mission_plan_store):
    mission_plan = []
    response_text = json_get_uframe_mission_selection(mission_plan_store)
    if response_text:
        try:
            mission_plan.append(response_text)
            #mission_plan = response_text
            #print '\n ***** type(response_txt): ', type(response_text)
            #print '\n ***** response_text: ', response_text[0].split('\r')
        except:
            return bad_request('Malformed mission_plan data; not in valid json format.')
    return mission_plan
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private helpers for file data (./ooiuiservices/tests/c2data/*)
# Each of these will be replaced with interface to uframe or other interface (other than file)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def json_get_uframe_mission_selections(reference_designator):
    try:
        data = None
        if reference_designator:
            if len(reference_designator) == 27:
                mission_type = 'instrument'
            elif len(reference_designator) == 14:
                mission_type = 'platform'
            else:
                return []
            filename = "_".join([mission_type, 'missions'])
            data = read_store(filename)
            #print '\n ***** data: ', data
    except:
        return None
    return data

def json_get_uframe_mission_selection(mission_plan_filename):
    try:
        data = None
        if mission_plan_filename:
            data = read_store2(mission_plan_filename)
    except:
        return None
    return data
