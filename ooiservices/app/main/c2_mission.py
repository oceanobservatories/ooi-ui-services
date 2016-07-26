#!/usr/bin/env python
'''
API v1.0 Command and Control (C2) routes for Mission Control (Executive and Load)
'''
__author__ = 'Edna Donoughe'

from flask import jsonify, request, current_app
from ooiservices.app.main import api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.uframe.config import get_c2_missions_uframe_info
import json
import requests
from base64 import b64encode
import datetime as dt


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 Mission Control routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
'''
# SHORT VERSION - FINAL TARGETED ROUTE!
@api.route('/c2/missions', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_get_missions():
    """ Get list of missions.
    """
    valid_states = ['active', 'inactive']
    missions = []
    try:
        state = None
        if request.args:
            if 'state' in request.args:
                state = (request.args['state']).lower()
                if state not in valid_states:
                    state = None
        result = uframe_get_missions(state)
        if result is not None:
            missions = result
        return jsonify(missions=missions)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return bad_request(message)
'''


# LONG VERSION: Use until ui navigation is modified to use short version (short is recommended server side api usage)
@api.route('/c2/missions', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_get_missions():
    """ Get list of missions.
    """
    valid_states = ['active', 'inactive']
    missions = []
    try:
        state = None
        if request.args:
            if 'state' in request.args:
                state = (request.args['state']).lower()
                if state not in valid_states:
                    state = None
        result = uframe_get_missions(state)
        ids = []
        if result is not None:
            for item in result:
                ids.append(item['mission_id'])
            tmp = make_mission_response(ids)
            if tmp is not None:
                missions = tmp

        return jsonify(missions=missions)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_get_mission(mission_id):
    """ Get a mission.
    """
    try:
        result = uframe_get_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission)

    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<string:mission_id>/delete', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_delete_mission(mission_id):
    """ Delete a mission.
    """
    try:
        mission = {}
        result = uframe_delete_mission(mission_id)
        if result is not None:
            mission = result
        return jsonify(mission)
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>/activate', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_activate_mission(mission_id):
    """ Activate a mission.
    """
    try:
        result = uframe_activate_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission)
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>/deactivate', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_deactivate_mission(mission_id):
    """ Deactivate a mission.
    """
    try:
        result = uframe_deactivate_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission), 200
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions', methods=['POST'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_add_mission():
    """ Add a mission.
    """
    try:
        if request.data is None:
            message = 'Provide request data to add new mission.'
            raise Exception(message)

        result = uframe_add_mission(request.data)
        if result is None or len(result) == 0:
            message = 'Failed to add new mission.'
            raise Exception(message)

        mission_id = result['id']
        result = uframe_get_mission(mission_id)
        mission = get_mission_info(mission_id, result)
        return jsonify(mission=mission), 201

    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>/versions', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_mission_versions(mission_id):
    """ Get mission versions.
    """
    try:
        result = uframe_mission_versions(mission_id)
        return jsonify(result), 200
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>/versions/<int:version_id>', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_mission_version(mission_id, version_id):
    """ Get mission version.
    """
    try:
        result = uframe_mission_version(mission_id, version_id)
        return jsonify(result), 200
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>/versions/<int:version_id>', methods=['PUT'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_mission_set_version(mission_id, version_id):
    """ Set mission version.
    """
    try:
        if request.data is None:
            message = 'Provide request data to set script version.'
            raise Exception(message)
        result = uframe_mission_set_version(mission_id, version_id)
        return jsonify(result), 200
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>/runs', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_mission_runs(mission_id):
    """ Get mission runs.
    """
    try:
        result = uframe_mission_runs(mission_id)
        return jsonify(result), 200
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/c2/missions/<int:mission_id>/runs/<int:run_id>', methods=['GET'])
@auth.login_required
@scope_required(u'command_control')
#@scope_required(u'mission_control')
def c2_mission_run(mission_id, run_id):
    """ Get mission run.
    """
    try:
        result = uframe_mission_run(mission_id, run_id)
        return jsonify(result), 200
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return bad_request(message)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# uframe helpers
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uframe_get_missions(state=None):
    """ Helper for get missions; issue upstream server request, process response and return missions.
    Sample of uframe request executed:    http://localhost:port/missions
    """
    result = []
    try:
        suffix = None
        if state is not None:
            suffix = '?state='+state

        response = uframe_issue_get_request(method='get', suffix=suffix)
        if response.status_code != 200:
            message = '(%s) Failed to get missions. ' % response.status_code
            raise Exception(message)

        missions = json.loads(response.content)
        for key in missions.keys():
            tmp = get_mission_info_short(key, missions[key])
            result.append(tmp)
        return result
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


# todo - note no timeout info on get request; correct this.
def uframe_get_mission(id):
    """ Get mission.
    Sample request to be executed:    http://localhost:port/mission/mission_id
    """
    mission = {}
    try:
        suffix = '/%s' % str(id)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to get mission \'%s\'. ' % (response.status_code, str(id))
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_delete_mission(id):
    """ Delete mission.
    Sample request to be executed:    http://localhost:port/mission/mission_id
    """
    mission = {}
    try:
        suffix = '/%s' % id
        response = uframe_issue_get_request(method='delete', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%d) Failed to delete mission \'%s\'. ' % (response.status_code, id)
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_activate_mission(id):
    """ Activate mission.
    Sample request to be executed:    http://localhost:port/mission/mission_id/activate
    """
    mission = {}
    try:
        suffix = '/%s/activate' % str(id)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to activate mission \'%s\'. ' % (response.status_code, str(id))
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_deactivate_mission(id):
    """ Deactivate mission.
    Sample request to be executed:    http://localhost:port/mission/mission_id/deactivate
    """
    mission = {}
    try:
        suffix = '/%s/deactivate' % str(id)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to deactivate mission \'%s\'. ' % (response.status_code, str(id))
            #if response.content:
            #    message += json.loads(response.content)
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_add_mission(data):
    """ Add mission using post method.
    request:    http://localhost:port/mission/mission_id
    """
    mission = {}
    try:
        response = uframe_issue_get_request(method='post', suffix=None, data=data)
        if response.status_code != 200:
            message = '(%s) Failed to add mission. ' % response.status_code
            # if response.content:
            #     message += json.loads(response.content)
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_mission_versions(id):
    """ Get mission versions.
    Sample request to be executed:    http://localhost:port/mission/mission_id/versions
    """
    mission = {}
    try:
        suffix = '/%s/versions' % str(id)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to get mission versions. (id: \'%s\'). ' % (response.status_code, str(id))
            if response.content:
                message += json.loads(response.content)
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_mission_version(id, version_id):
    """ Get mission version by version id.
    Sample request to be executed:    http://localhost:port/mission/mission_id/versions/version_id
    """
    mission = {}
    try:
        suffix = '/%s/versions/%s' % (str(id), str(version_id))
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to get mission versions. (id: \'%s\'; version: \'%s\'). ' \
                      % (response.status_code, str(id), str(version_id))
            if response.content:
                message += json.loads(response.content)
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_mission_set_version(id, version_id):
    """ Set mission version to version id.
    Sample request to be executed:    http://localhost:port/mission/mission_id/versions/version_id
    """
    mission = {}
    try:
        suffix = '/%s/versions/%s' % (str(id), str(version_id))
        response = uframe_issue_get_request(method='put', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to set mission version. (id: \'%s\'; version: \'%s\'). ' \
                      % (response.status_code, str(id), str(version_id))
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_mission_runs(id):
    """ Get mission runs.
    Sample request to be executed:    http://localhost:port/mission/id/runs
    response:
    {
      "runs": [
        1088,
        1089,
        1090,
        1091,
        1092
      ]
    }
    """
    mission = {}
    try:
        suffix = '/%s/runs' % str(id)
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to get mission runs. (id: \'%s\'). ' % (response.status_code, str(id))
            if response.content:
                message += json.loads(response.content)
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise


def uframe_mission_run(id, run_id):
    """ Get mission run by run id.
    Sample request to be executed:    http://localhost:port/mission/id/runs/run_id
    response:
    {
      "run": [
        [
          "2015-10-28T22:13:35.974476",
          "start",
          ""
        ],
        [
          "2015-10-28T22:13:35.988206",
          "lock",
          "RS10ENGC-XX00X-00-BOTPTA001"
        ],
        [
          "2015-10-28T22:13:35.993006",
          "step",
          {
            "block_name": "initialize"
          }
        ],
        . . .
    }
    """
    mission = {}
    try:
        suffix = '/%s/runs/%s' % (str(id), str(run_id))
        response = uframe_issue_get_request(method='get', suffix=suffix, data=None)
        if response.status_code != 200:
            message = '(%s) Failed to get mission run. (id: \'%s\'; run id: \'%s\'). ' \
                      % (response.status_code, str(id), str(run_id))
            if response.content:
                message += json.loads(response.content)
            raise Exception(message)
        if response.content:
            mission = json.loads(response.content)
        return mission
    except Exception as err:
        message = str(err.message)
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

    Really should validate result is well-formed before using.
    valid_items = ['name', 'version', 'active', 'running', 'events', 'created', 'next_run', 'schedule', 'run_count']
    """
    mission = {}
    name = ''
    desc = ''
    running = False
    active = False
    version = ''
    created = ''
    next_run = ""
    schedule = {}
    run_count = -1
    drivers = []
    mission_plan = ''

    if result is not None:
        tmp = result
        name = tmp['name']
        version = tmp['version']
        active = tmp['active']
        running = tmp['running']
        #events = tmp['events']
        created = tmp['created']
        next_run = tmp['next_run']
        schedule = tmp['schedule']
        run_count = tmp['run_count']
        if 'desc' in tmp:
            desc = tmp['desc']
        if 'drivers' in tmp:
            drivers = tmp['drivers']
        if 'script' in tmp:
            # todo splitting here for ui; coordinate with ui and leave as a str
            data = (tmp['script']).split('\n')
            mission_plan = data

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
    mission['mission_id'] = mission_id
    mission['mission'] = mission_plan
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


def get_mission_info_short(mission_id, result):
    """
    Set return mission object content for ui /missions request (SHORT). No drivers, script
    Using active/running to build the status:
    active | running | status
    F | F | inactive
    T | F | loaded
    T | T | running

    Fields provided:
    {
      "1": {
        "active": false,
        "created": "2015-10-26T22:12:50.044857",
        "current_step": null,
        "desc": "Periodic acquire status for BOTPT",
        "id": 1,
        "name": "BOTPT_periodic_acquire_status",
        "next_run": null,
        "run_count": 1082,
        "running": false,
        "schedule": {
          "second": 0
        },
        "version": "1-00"
      }
    }
    """
    mission = {}
    active = False
    created = ''
    current_step = ''
    desc = ''
    name = ''
    next_run = ''
    run_count = -1
    running = False
    schedule = {}
    version = ''

    # Set values
    if result is not None:
        tmp = result
        active = tmp['active']
        created = tmp['created']
        current_step = tmp['current_step']
        desc = tmp['desc']
        name = tmp['name']
        next_run = tmp['next_run']
        run_count = tmp['run_count']
        running = tmp['running']
        schedule = tmp['schedule']
        version = tmp['version']
        mission_id = tmp['id']

    # Set state. Using 'active' element value ['Active' | 'Inactive']
    if active:
        state = 'Active'
    else:
        state = 'Inactive'

    # Set Status. Determine status (uses 'active' and 'running'; valid status: ['Inactive', 'Loaded', 'Running']
    if not active:
        status = 'Inactive'
    else:
        status = 'Loaded'
        if running:
            status = 'Running'
    mission['status']= status
    mission['state'] = state

    # Populate remaining mission executive dictionary values
    mission['active'] = active
    mission['created'] = created
    mission['current_step'] = current_step
    mission['desc'] = desc
    mission['name'] = name
    mission['next_run'] = next_run
    mission['run_count'] = run_count
    mission['running'] = running
    mission['version'] = version
    mission['schedule'] = schedule
    mission['mission_id'] = mission_id

    return mission


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# uframe specific functions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_api_headers(username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }


def uframe_issue_get_request(method='get', suffix=None, data=None):
    """ Issue uframe get request; returns response.content as result, otherwise None or raise Exception.
    """
    valid_methods = ['get', 'post', 'delete', 'put']
    headers = {"Content-Type": "application/json"}
    try:
        # Determine if supported/valid method request (i.e. one of valid_methods)
        if method not in valid_methods:
            message = 'Unknown or unsupported method for uframe request: %s' % method
            raise Exception(message)

        # Setup basic request info
        url, timeout, timeout_read = get_c2_missions_uframe_info()
        if suffix is not None:
            url += suffix

        # Get response based on method
        response = None

        # Methods: 'get' and 'delete'
        if method == 'get' or method == 'delete':
            if method == 'get':
                response = requests.get(url, timeout=(timeout, timeout_read))
            elif method == 'delete':
                response = requests.delete(url, timeout=(timeout, timeout_read))

        # Methods: 'post' and 'put'
        else:
            if method == 'post':
                response = requests.post(url, timeout=(timeout, timeout_read), data=data)

            if method == 'put':
                if data:
                    response = requests.put(url, timeout=(timeout, timeout_read), headers=headers, data=data)
                else:
                    response = requests.put(url, timeout=(timeout, timeout_read), headers=headers)


        return response
    except Exception as err:
        message = str(err.message)
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
            if len(event_text) > 50:
                event_text = str(event_text)[0:50] + ' ...'

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

def make_mission_response(ids):
    """
    USED WITH LONG VERSION of /missions route.
    Temporary workaround.

    Used until UI navigates using (short) /missions route output uses selected mission_id
    to invoke /missions/mission_id and process the output (which includes script and events).

    For each mission id in ids, get mission (using /missions/id, append response data to result.
    """
    result = []
    try:
        for id in ids:
            mission = uframe_get_mission(id)
            tmp = get_mission_info(id, mission)
            result.append(tmp)
        return result
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        raise