#!/usr/bin/env python
'''
API v1.0 Command and Control (C2) routes for Mission Control
'''
__author__ = 'Edna Donoughe'

from flask import jsonify
from ooiservices.app.main import api
from ooiservices.app.models import Array
import json
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.c2 import read_store
from ooiservices.app.main.c2 import _get_platform, _get_instrument, _get_instruments

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 Mission Control - array routes
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/array/<string:array_code>/mission_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_mission_instruments_list(reference_designator):
    # C2 get [platform] Mission tab instruments_list, return instruments [{instrument1}, {instrument2}, ...]
    # where each instrument dictionary (is a row in instruments list) contains:
    #   {'reference_designator': reference_designator, 'instrument_deployment_id': id, 'display_name': display_name }
    # Samples:
    #   http://localhost:4000/c2/platform/reference_designator/mission/instruments_list
    #   http://localhost:4000/c2/platform/reference_designator/mission/instruments_list
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
#@auth.login_required
#@scope_required(u'user_admin')
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
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_mission_display(reference_designator):
    #Get C2 instrument Mission tab contents, return mission_display
    mission_display = {}
    instrument = _get_instrument(reference_designator)
    if instrument:
        mission_display = {}  # todo populated display content
    return jsonify(mission_display=mission_display)

@api.route('/c2/platform/<string:reference_designator>/mission_selections', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_mission_selections(reference_designator):
    # C2 get platform Mission tab mission selections content, return mission_selections [{},{}...]
    # return list of platform mission plans
    mission_selections = []
    platform = _get_platform(reference_designator)
    if platform:
        mission_selections = _get_mission_selections(reference_designator)
    return jsonify(mission_selections=mission_selections)

@api.route('/c2/instrument/<string:reference_designator>/mission_selections', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_mission_selections(reference_designator):
    # C2 get instrument Mission tab mission selections content, return mission_selections [{},{}...]
    # return list of instrument mission plans
    mission_selections = []
    instrument = _get_instrument(reference_designator)
    if instrument:
        mission_selections = _get_mission_selections(reference_designator)
    return jsonify(mission_selections=mission_selections)

@api.route('/c2/platform/<string:reference_designator>/mission_selection/<string:mission_plan_store>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_mission_selection(reference_designator, mission_plan_store):
    # C2 get [platform] selected mission_plan content, return mission_plan
    if not mission_plan_store:
        return bad_request('mission_plan_store parameter is empty')
    mission_plan = {}
    platform = _get_platform(reference_designator)
    if platform:
        mission_plan = _get_mission_selection(mission_plan_store)
    return jsonify(mission_plan=mission_plan)

@api.route('/c2/instrument/<string:reference_designator>/mission_selection/<string:mission_plan_store>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
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
    except:
        return None
    return data

def json_get_uframe_mission_selection(mission_plan_filename):
    try:
        data = None
        if mission_plan_filename:
            data = read_store(mission_plan_filename)
    except:
        return None
    return data
