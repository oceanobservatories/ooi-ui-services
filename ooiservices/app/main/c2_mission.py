#!/usr/bin/env python
'''
API v1.0 List for Command and Control (C2) routes for Mission Control
'''
__author__ = 'Edna Donoughe'

from flask import jsonify
from ooiservices.app.main import api
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Instrumentname
import json
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.c2 import read_store, _platform_deployment, _instrument_deployment

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 array routes
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/array/<string:array_code>/mission_display', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_array_mission_display(array_code):
    #Get C2 array mission (display), return mission_display (contents of platform Mission tab)
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    mission_display = {}
    return jsonify(mission_display=mission_display)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 platform
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/platform/<string:reference_designator>/mission/instruments_list', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_platform_mission_instruments_list(reference_designator):
    # C2 get [platform] Mission tab instruments_list, return instruments [{instrument1}, {instrument2}, ...]
    # where each instrument dictionary (is a row in instruments list) contains:
    #   {'reference_designator': reference_designator, 'instrument_deployment_id': id, 'display_name': display_name }
    # Samples:
    #   http://localhost:4000/c2/platform/CP02PMCO-SBS01/mission/instruments_list
    #   http://localhost:4000/c2/platform/CP02PMCO-WFP01/mission/instruments_list
    contents = []
    platform_info = {}
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
    if not platform_deployment:
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    # get ordered set of instrument_deployments for platform
    instrument_deployments = \
        InstrumentDeployment.query.filter_by(platform_deployment_id=platform_deployment.id).all()
    for i_d in instrument_deployments:
        instrument_name = Instrumentname.query.filter(Instrumentname.instrument_class == i_d.display_name).first()
        if instrument_name:
            i_d.display_name = instrument_name.display_name
    # create list of reference_designators (instruments) and accumulate dict result (key=reference_designator) for output
    instruments = []
    for instrument_deployment in instrument_deployments:
        instruments.append(instrument_deployment.reference_designator)
        row = {}
        row['reference_designator'] = instrument_deployment.reference_designator
        row['instrument_deployment_id'] = instrument_deployment.id
        row['display_name'] = instrument_deployment.display_name
        platform_info[instrument_deployment.reference_designator] = row
    '''
    (hold for now - not sure we need status)
    # Get operational status for all instruments in platform; add to output
    statuses = c2_get_instruments_operational_status(platform_deployment.reference_designator)
    if statuses:
        for d in statuses:
            rd = d['id']
            stat = d['status']
            if rd in platform_info:
                platform_info[rd]['instrument_status'] = stat
    '''
    # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
    # 'data' == rows for initial grid ('Current Status')
    for instrument_deployment_reference_designator in instruments:
        if instrument_deployment_reference_designator in platform_info:
            contents.append(platform_info[instrument_deployment_reference_designator])
    return jsonify(instruments=contents)

@api.route('/c2/platform/<string:reference_designator>/mission_display', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_platform_mission_display(reference_designator):
    #Get C2 platform Mission tab contents, return mission_display
    if not _platform_deployment(reference_designator):
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    mission_display = {}
    return jsonify(mission_display=mission_display)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 instrument
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/instrument/<string:reference_designator>/mission_display', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_instrument_mission_display(reference_designator):
    #Get C2 instrument Mission tab contents, return mission_display
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    mission_display = {}
    return jsonify(mission_display=mission_display)

@api.route('/c2/platform/<string:reference_designator>/mission_selections', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_platform_mission_selections(reference_designator):
    # C2 get platform Mission tab mission selections content, return mission_selections [{},{}...]
    # return list of platform mission plans
    if not _platform_deployment(reference_designator):
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    mission_selections = _get_mission_selections(reference_designator)
    return jsonify(mission_selections=mission_selections)

@api.route('/c2/instrument/<string:reference_designator>/mission_selections', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_instrument_mission_selections(reference_designator):
    # C2 get instrument Mission tab mission selections content, return mission_selections [{},{}...]
    # return list of instrument mission plans
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    mission_selections = _get_mission_selections(reference_designator)
    return jsonify(mission_selections=mission_selections)

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

@api.route('/c2/platform/<string:reference_designator>/mission_selection/<string:mission_plan_store>', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_platform_mission_selection(reference_designator, mission_plan_store):
    # C2 get [platform] selected mission_plan content, return mission_plan
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
    if not platform_deployment:
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    if not mission_plan_store:
        return bad_request('mission_plan_store parameter is empty')
    mission_plan = _get_mission_selection(mission_plan_store)
    return jsonify(mission_plan=mission_plan)

@api.route('/c2/instrument/<string:reference_designator>/mission_selection/<string:mission_plan_store>', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def c2_get_instrument_mission_selection(reference_designator, mission_plan_store):
    # C2 get [instrument] selected mission_plan content from store (file, uframe), return mission_plan
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    if not mission_plan_store:
        return bad_request('mission_plan_store parameter is empty')
    mission_plan = _get_mission_selection(mission_plan_store)
    return jsonify(mission_plan=mission_plan)

def _get_mission_selection(mission_plan_store):
    mission_plan = []
    response_text = json_get_uframe_mission_selection(mission_plan_store)
    if response_text:
        try:
            mission_plan.append(response_text)
        except:
            return bad_request('Malformed mission_plan data; not in valid json format. (reference designator \'%s\')' % reference_designator)
    return mission_plan

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 helper for file data (./ooiuiservices/tests/c2data/*)
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
