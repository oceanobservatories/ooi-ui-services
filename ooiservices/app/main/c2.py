#!/usr/bin/env python
'''
API v1.0 List for Command and Control (C2)

'''
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app
from ooiservices.app.main import api
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Instrumentname
import json, requests, os
from ooiservices.app.main.errors import internal_server_error, bad_request
from ooiservices.app import cache
from authentication import auth
from ooiservices.app.decorators import scope_required
#from ooiservices.app import db

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 array
# - - - - - - - - - - - - - - - - - - - - - - - -
#TODO enable auth and scope
'''
@api.route('/c2/array_display/<string:array_code>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_display(array_code):
    #C2 get array display, return array_display dict with: abstract, data, history
    #
    #Uses:
    #    c2_get_platforms_operational_status(reference_designator), return statuses
    #    c2_get_array_history(reference_designator)
    #    *c2_get_array_status_display(reference_designator), return status_display (content of Status tab)
    #    *c2_get_array_mission_display(reference_designator), return mission_display (content of Mission tab)
    #    * under construction
    #Sample:
    #    http://localhost:4000/c2/array_display/CP   (operational_status available for some platforms)
    #    http://localhost:4000/c2/array_display/GS   (operational_status not available)
    #
    response_dict = {}
    contents = []
    array_info = {}
    reference_designator = array_code
    array = Array.query.filter_by(array_code=array_code).first_or_404()
    response_dict['abstract'] = {}
    response_dict['abstract']['display_name'] = array.display_name
    response_dict['abstract']['reference_designator'] = array.array_code
    response_dict['abstract']['array_id'] = array.id
    response_dict['abstract']['operational_status'] = c2_get_array_operational_status(reference_designator)

    # Get history, add to output
    response_dict['history'] = c2_get_array_history(reference_designator)

    # Get data, add to output
    # get ordered set of platform_deployments for array.id
    platform_deployments = \
        PlatformDeployment.query.filter_by(array_id=array.id).order_by(PlatformDeployment.reference_designator).all()

    # create list of reference_designators and accumulate dict result (key=reference_designator) for use in response
    # (Set all operational_status values to 'Unknown' by default)
    platforms = []
    for platform_deployment in platform_deployments:
        platforms.append(platform_deployment.reference_designator)
        row = {}
        row['platform_deployment_id'] = platform_deployment.id
        row['display_name'] = platform_deployment.proper_display_name
        row['reference_designator'] = platform_deployment.reference_designator
        row['operational_status'] = 'Unknown'
        array_info[platform_deployment.reference_designator] = row

    # Get operational status for all platforms in array
    statuses = c2_get_platforms_operational_status(reference_designator)
    if statuses:
        for d in statuses:
            rd = d['id']
            stat = d['status']
            if rd in array_info:
                array_info[rd]['operational_status'] = stat

    # create list of dictionaries representing data row(s), ordered by reference_designator
    for r in platforms:
        if r in array_info:
            contents.append(array_info[r])
    response_dict['data'] = contents

    # Create status_display dict (contents for Status tab), add to output (TODO)
    response_dict['status_display'] = c2_get_array_status_display(reference_designator)

    # Create mission_display dict (contents for Mission tab), add to output (TODO)
    response_dict['mission_display'] = c2_get_array_mission_display(reference_designator)
    return jsonify(array_display=response_dict)
'''
#TODO (start) -- for array_display
@api.route('/c2/array/<string:array_code>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_abstract(array_code):
    #Get C2 array abstract (display), return abstract
    response_dict = {}
    array = Array.query.filter_by(array_code=array_code).first_or_404()
    response_dict = {}
    response_dict['display_name'] = array.display_name
    response_dict['reference_designator'] = array.array_code
    response_dict['array_id'] = array.id
    response_dict['operational_status'] = c2_get_array_operational_status(array_code)
    return jsonify(abstract=response_dict)

@api.route('/c2/array/<string:array_code>/current_status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_current_status_display(array_code):
    # C2 get array Current Status tab contents, return current_status_display
    response_dict = {}
    contents = []
    array_info = {}
    reference_designator = array_code
    array = Array.query.filter_by(array_code=array_code).first_or_404()

    # Get data, add to output
    # get ordered set of platform_deployments for array.id
    platform_deployments = \
        PlatformDeployment.query.filter_by(array_id=array.id).order_by(PlatformDeployment.reference_designator).all()

    # create list of reference_designators and accumulate dict result (key=reference_designator) for use in response
    # (Set all operational_status values to 'Unknown' by default)
    platforms = []
    for platform_deployment in platform_deployments:
        platforms.append(platform_deployment.reference_designator)
        row = {}
        row['platform_deployment_id'] = platform_deployment.id
        row['display_name'] = platform_deployment.proper_display_name
        row['reference_designator'] = platform_deployment.reference_designator
        row['operational_status'] = 'Unknown'
        array_info[platform_deployment.reference_designator] = row

    # Get operational status for all platforms in array
    statuses = c2_get_platforms_operational_status(reference_designator)
    if statuses:
        for d in statuses:
            rd = d['id']
            stat = d['status']
            if rd in array_info:
                array_info[rd]['operational_status'] = stat

    # create list of dictionaries representing data row(s), ordered by reference_designator
    for r in platforms:
        if r in array_info:
            contents.append(array_info[r])
    return jsonify(current_status_display=contents)

@api.route('/c2/array/<string:array_code>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_history(array_code):
    # C2 get array history, return history
    #   where history is data dict { 'history': {'event': [], 'command': [], 'configuration':[]} }
    history = { 'event': [], 'command': [], 'configuration':[] }
    if array_code:
        history = get_history(array_code)
    return jsonify(history=history)

@api.route('/c2/array/<string:array_code>/status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_status_display(array_code):
    #Get C2 array status (display), return status_display (contents of platform Status tab)
    status_display = {}
    return jsonify(status_display=status_display)

@api.route('/c2/array/<string:array_code>/mission_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_mission_display(array_code):
    #Get C2 array mission (display), return mission_display (contents of platform Mission tab)
    mission_display = {}
    return jsonify(mission_display=mission_display)

#TODO (end) -- for array_display

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 platform
# - - - - - - - - - - - - - - - - - - - - - - - -
#TODO enable auth and scope
'''
@api.route('/c2/platform_display/<string:reference_designator>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_display(reference_designator):
    # C2 get platform display, return platform_display dict with: abstract, data, history, ports_display
    #
    #Uses:
    #    c2_get_instruments_operational_status(reference_designator), return statuses
    #    c2_get_instruments_streams(instrument_deployment_rds), return streams
    #    c2_get_platform_history(reference_designator), return history
    #    *c2_get_platform_ports_display(reference_designator), return port_display (contents of Ports tab)
    #    *c2_get_platform_status_display(reference_designator), return status_display (contents of Status tab)
    #    *c2_get_platform_mission_display(reference_designator), return mission_display (contents of Mission tab)
    #    * under construction
    #Sample: http://localhost:4000/c2/platform_display/CP02PMCO-WFP01   (id==104)

    contents = []
    platform_info = {}
    response_dict = {}
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
    response_dict['abstract'] = {}
    response_dict['abstract']['display_name'] = platform_deployment.display_name
    response_dict['abstract']['reference_designator'] = platform_deployment.reference_designator
    response_dict['abstract']['platform_deployment_id'] = platform_deployment.id
    response_dict['abstract']['operational_status'] = c2_get_platform_operational_status(reference_designator)

    # get ordered set of instrument_deployments for platform
    instrument_deployments = \
        InstrumentDeployment.query.filter_by(platform_deployment_id=platform_deployment.id).all()
    for i_d in instrument_deployments:
        instrument_name = Instrumentname.query.filter(Instrumentname.instrument_class == i_d.display_name).first()
        if instrument_name:
            i_d.display_name = instrument_name.display_name

    # create list of reference_designators (instruments) and
    # accumulate dict result (key=reference_designator) for output
    instruments = []
    for instrument_deployment in instrument_deployments:
        instruments.append(instrument_deployment.reference_designator)
        row = {}
        row['instrument_deployment_id'] = instrument_deployment.id
        row['display_name'] = instrument_deployment.display_name
        row['reference_designator'] = instrument_deployment.reference_designator
        row['operational_status'] = 'Unknown'
        row['streams'] = []
        platform_info[instrument_deployment.reference_designator] = row

    # Get operational status for all instruments in platform; add to output
    statuses = c2_get_instruments_operational_status(platform_deployment.reference_designator)
    if statuses:
        for d in statuses:
            rd = d['id']
            stat = d['status']
            if rd in platform_info:
                platform_info[rd]['operational_status'] = stat

    # Get streams for all instruments; add to output
    streams = c2_get_instruments_streams(instruments)
    if streams:
        for item in platform_info:
            res = platform_info[item]
            if res['reference_designator'] in streams:
                res['streams'] = streams[res['reference_designator']]

    # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
    # 'data' == rows for initial grid ('Current Status')
    for instrument_deployment_reference_designator in instruments:
        if instrument_deployment_reference_designator in platform_info:
            contents.append(platform_info[instrument_deployment_reference_designator])
    response_dict['data'] = contents

    # Get history, add history to output
    response_dict['history'] = c2_get_platform_history(reference_designator)

    # Get ports_display, add ports_display to output
    response_dict['ports_display'] = c2_get_platform_ports_display(reference_designator)

    # Create status_display dict (contents for Status tab), add to output (TODO)
    response_dict['status_display'] = c2_get_platform_status_display(reference_designator)

    # Create mission_display dict (contents for Mission tab), add to output (TODO)
    response_dict['mission_display'] = c2_get_platform_mission_display(reference_designator)
    return jsonify(platform_display=response_dict)
'''

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_abstract(reference_designator):
    #Get C2 platform abstract, return abstract
    response_dict = {}
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
    response_dict = {}
    response_dict['display_name'] = platform_deployment.display_name
    response_dict['reference_designator'] = platform_deployment.reference_designator
    response_dict['platform_deployment_id'] = platform_deployment.id
    response_dict['operational_status'] = c2_get_platform_operational_status(reference_designator)
    return jsonify(abstract=response_dict)

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/current_status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_current_status_display(reference_designator):
    #Get C2 platform Current Status tab contents, return current_status_display
    contents = []
    platform_info = {}
    response_dict = {}
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
    response_dict['abstract'] = {}
    response_dict['abstract']['display_name'] = platform_deployment.display_name
    response_dict['abstract']['reference_designator'] = platform_deployment.reference_designator
    response_dict['abstract']['platform_deployment_id'] = platform_deployment.id
    response_dict['abstract']['operational_status'] = c2_get_platform_operational_status(reference_designator)

    # get ordered set of instrument_deployments for platform
    instrument_deployments = \
        InstrumentDeployment.query.filter_by(platform_deployment_id=platform_deployment.id).all()
    for i_d in instrument_deployments:
        instrument_name = Instrumentname.query.filter(Instrumentname.instrument_class == i_d.display_name).first()
        if instrument_name:
            i_d.display_name = instrument_name.display_name

    # create list of reference_designators (instruments) and
    # accumulate dict result (key=reference_designator) for output
    instruments = []
    for instrument_deployment in instrument_deployments:
        instruments.append(instrument_deployment.reference_designator)
        row = {}
        row['instrument_deployment_id'] = instrument_deployment.id
        row['display_name'] = instrument_deployment.display_name
        row['reference_designator'] = instrument_deployment.reference_designator
        row['operational_status'] = 'Unknown'
        row['streams'] = []
        platform_info[instrument_deployment.reference_designator] = row

    # Get operational status for all instruments in platform; add to output
    statuses = c2_get_instruments_operational_status(platform_deployment.reference_designator)
    if statuses:
        for d in statuses:
            rd = d['id']
            stat = d['status']
            if rd in platform_info:
                platform_info[rd]['operational_status'] = stat

    # Get streams for all instruments; add to output
    streams = c2_get_instruments_streams(instruments)
    if streams:
        for item in platform_info:
            res = platform_info[item]
            if res['reference_designator'] in streams:
                res['streams'] = streams[res['reference_designator']]

    # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
    # 'data' == rows for initial grid ('Current Status')
    for instrument_deployment_reference_designator in instruments:
        if instrument_deployment_reference_designator in platform_info:
            contents.append(platform_info[instrument_deployment_reference_designator])
    return jsonify(current_status_display=contents)

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_history(reference_designator):
    # C2 get platform history, return history
    #   where history is data dict { 'history': {'event': [], 'command': [], 'configuration':[]} }
    history = { 'event': [], 'command': [], 'configuration':[] }
    if reference_designator:
        history = get_history(reference_designator)
    return jsonify(history=history)

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/ports_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_ports_display(reference_designator):
    #Get C2 platform Ports tab contents, return ports_display
    ports_display =  {}
    return jsonify(ports_display=ports_display)

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_status_display(reference_designator):
    #Get C2 platform Status tab contents, return status_display
    status_display = {}
    return jsonify(status_display=status_display)

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/mission_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_mission_display(reference_designator):
    #Get C2 platform Mission tab contents, return mission_display
    mission_display = {}
    return jsonify(mission_display=mission_display)

#TODO enable auth and scope
@api.route('/c2/platform/<string:reference_designator>/commands', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_commands(reference_designator):
    #Get C2 platform commands (pulldown list) contents, return commands
    commands =  {}
    if reference_designator:
        commands =  {}
    return jsonify(commands=commands)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 instrument
# - - - - - - - - - - - - - - - - - - - - - - - -
#TODO enable auth and scope
'''
@api.route('/c2/instrument_display/<string:reference_designator>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_display(reference_designator):
    # C2 get instrument display, return platform_display dict with: abstract, data, history, ports_display, streams
    #
    #iff instrument has one stream, data is populated with fields for stream
    #Sample request:
    #   http://localhost:4000/c2/instrument_display/CP02PMCO-WFP01-05-PARADK000     (1 stream, data populated)
    #   http://localhost:4000/c2/instrument_display/CP02PMCO-WFP01-02-DOFSTK000     (2 streams, no data)
    #Uses:
    #    c2_get_instrument_streams(reference_designator) returns streams, fields
    #    *c2_get_instrument_ports(reference_designator) returns ports
    #    c2_get_instrument_operational_status(reference_designator) returns status
    #    c2_get_instrument_history(reference_designator) returns history
    #   *c2_get_instrument_status_display return status_display (content of Status tab)
    #    *c2_get_instrument_mission_display return mission_display (content of Mission tab)
    #    * under construction
    #
    response_dict = {}
    response_dict['data'] = []
    instrument_deployment = InstrumentDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()

    # Add abstract to output
    response_dict['abstract'] = {}
    response_dict['abstract']['display_name'] = instrument_deployment.display_name
    response_dict['abstract']['reference_designator'] = instrument_deployment.reference_designator
    response_dict['abstract']['instrument_deployment_id'] = instrument_deployment.id
    response_dict['abstract']['operational_status'] = c2_get_instrument_operational_status(reference_designator)

    # Get data, add to output
    # data: streams and fields; if available add or data = []
    #TODO discuss with Jim
    streams = None
    fields = None
    try:
        streams, fields = c2_get_instrument_streams(reference_designator)
    except Exception, err:
        return bad_request(err.message)             # 400 - bad request (no streams or fields; bad reference_designator, etc.)

    if streams:
        response_dict['streams']  = streams
        if fields:
            response_dict['data'] = fields          # iff one stream, then field data
        else:
            response_dict['data'] = []              # no streams or more than one stream
    else:
        response_dict['streams']  = []              # no streams, then no fields (error)
        response_dict['data']     = []

    # Get ports, add to output
    response_dict['ports_display'] = c2_get_instrument_ports_display(reference_designator)

    # Get history, add to output
    response_dict['history'] = c2_get_instrument_history(reference_designator)

    # Create status_display dict (contents for Status tab), add to output (TODO)
    response_dict['status_display'] = c2_get_instrument_status_display(reference_designator)

    # Create mission_display dict (contents for Mission tab), add to output (TODO)
    response_dict['mission_display'] = c2_get_instrument_mission_display(reference_designator)
    return jsonify(instrument_display=response_dict)
'''

#TODO (start) -- for instrument_display
@api.route('/c2/instrument/<string:reference_designator>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_abstract(reference_designator):
    # C2 get instrument abstract, return abstract
    response_dict = {}
    response_dict['data'] = []
    instrument_deployment = InstrumentDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()

    # Add abstract to output
    response_dict = {}
    response_dict['display_name'] = instrument_deployment.display_name
    response_dict['reference_designator'] = instrument_deployment.reference_designator
    response_dict['instrument_deployment_id'] = instrument_deployment.id
    response_dict['operational_status'] = c2_get_instrument_operational_status(reference_designator)
    return jsonify(abstract=response_dict)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/streams', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_streams(reference_designator):
    # C2 get instrument streams, return streams
    streams = None
    try:
        streams, fields = c2_get_instrument_streams(reference_designator)
    except Exception, err:
        return bad_request(err.message)             # 400 - bad request (no streams or fields; bad reference_designator, etc.)

    '''
    if streams:
        response_dict['streams']  = streams
        if fields:
            response_dict['data'] = fields          # iff one stream, then field data
        else:
            response_dict['data'] = []              # no streams or more than one stream
    else:
        response_dict['streams']  = []              # no streams, then no fields (error)
        response_dict['data']     = []
    '''
    return jsonify(streams=streams)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_history(reference_designator):
    # C2 get instrument history, return history
    #   where history is data dict { 'event': [], 'command': [], 'configuration':[] }
    history = { 'event': [], 'command': [], 'configuration':[] }
    if reference_designator:
        history = get_history(reference_designator)
    return jsonify(history=history)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/ports_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_ports_display(reference_designator):
    #Get C2 instrument Ports tab contents, return ports_display
    ports_display =  {}
    if reference_designator:
        ports_display =  {}
    return jsonify(ports_display=ports_display)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_status_display(reference_designator):
    #Get C2 instrument Status tab contents, return status_display
    status_display = {}
    return jsonify(status_display=status_display)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/mission_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_mission_display(reference_designator):
    #Get C2 instrument Mission tab contents, return mission_display
    mission_display = {}
    return jsonify(mission_display=mission_display)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/commands', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_commands(reference_designator):
    #Get C2 instrument commands (pulldown list) contents, return commands
    commands =  {}
    if reference_designator:
        commands =  {}
    return jsonify(commands=commands)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/<string:stream_name>/fields', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_fields(reference_designator, stream_name):
    # C2 get instrument stream fields, return list of field dict items: [{name-units-type-value-command}, ...]
    # Used by UI when c2 instrument display stream selection pull down changes (stream1 selected, then select stream2)
    '''
    Sample requests:
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/mopak_o_dcl_accel/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/dofst_k_wfp_metadata/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_instrument/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_metadata/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k_stc_imodem_instrument/fields

        Errors:
        bad_request('reference_designator parameter is empty')
        bad_request('stream_name parameter is empty')
        bad_request('Invalid reference designator for instrument (\'%s\').' % reference_designator)
        bad_request('Failed to retrieve stream data for instrument (reference designator \'%s\')' % reference_designator)
        bad_request('Invalid stream name (\'%s\') for instrument (\'%s\')' % (stream_name, reference_designator))

    '''
    if not reference_designator:
        return bad_request('reference_designator parameter is empty')
    if not stream_name:
        return bad_request('stream_name parameter is empty')

    if len(reference_designator) != 27:
        return bad_request('Invalid reference designator for instrument (\'%s\').' % reference_designator)

    # Validate instrument reference_designator and stream_name
    streams = None
    response_text = json_get_uframe_instrument_streams(reference_designator)
    if response_text:
        streams = json.loads(response_text)
    else:
        return bad_request('Failed to retrieve stream data for instrument (reference designator \'%s\')' % reference_designator)

    # Verify valid stream_name (verify stream requested is one of streams available for this instrument)
    if stream_name not in streams:
        return bad_request('Invalid stream name (\'%s\') for instrument (\'%s\')' % (stream_name, reference_designator))

    display_content = {}
    # Get and add fields to output
    field_contents = []
    try:
        fields = c2_get_instrument_stream_fields(reference_designator, stream_name) # TODO change to get_instrument_fields ?
    except Exception, err:
        return bad_request(err.message)
    if fields:
        #TODO need try except for bad data
        data = json.loads(fields)
        # process fields - get name-units-type-value for each field;  field id added for development and ease of use
        fields = {}
        ofields = []
        inx = 1
        for elem in data:
            field = {}
            for k,v in elem.iteritems():
                field[k] = v
            field['id'] = inx
            if field['name'] not in ofields:
                fields[field['name']] = field
                ofields.append(field['name'])
            inx += 1
        for field_name in ofields:
            field_contents.append(fields[field_name])
    display_content['data'] = field_contents

    # prepare output result
    result = []
    display_content['stream_name'] = stream_name
    result.append(display_content)
    return jsonify(fields=result)

#TODO enable auth and scope; code - under construction
'''
#curl -X PUT http://localhost:4000/c2/instrument_update/CP02PMCO-SBS01-01-MOPAK0000?stream=mopak_o_dcl_accel&field=qualityflag&command=set&value=bad
@api.route('/c2/instrument_update/<string:reference_designator>/<string:stream_name>/<string:field>/<string:command>/<string:value>', methods=['PUT'])
#@auth.login_required
@scope_required(u'user_admin')
def c2_update_instrument_field_value(reference_designator, stream_name, field, command, value):
    # C2 update instrument stream field with value using command
    # http://localhost:4000/c2/instrument_update/CP02PMCO-SBS01-01-MOPAK0000/mopak_o_dcl_accel/quality_flag/set/bad
    id = InstrumentDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
    instrument_deployment = id.to_json()
    instrument_deployment_display_name = instrument_deployment['display_name']
    instrument_deployment_id = instrument_deployment['id']
    fields = c2_get_instrument_fields(reference_designator,stream_name)
    #data = request.json or {}
    return jsonify({'instrument_field_value': [reference_designator]})

#TODO enable auth and scope; code
@api.route('/c2/instrument/<string:reference_designator>/operational_status', methods=['GET'])
#@auth.login_required
@scope_required(u'user_admin')
def c2_get_instrument_operational_status(reference_designator):
    # C2 get instrument operational status
    return jsonify({'instrument_operational_status': [reference_designator]})
'''

#TODO - routes under review
'''
#TODO enable auth and scope; code
@api.route('/c2/array/<string:reference_designator>/operational_status', methods=['GET'])
#@auth.login_required
@scope_required(u'user_admin')
def c2_get_array_operational_status(reference_designator):
    # C2 get array operational status
    return jsonify({'array_operational_status': [reference_designator]})

#TODO enable auth and scope; code
@api.route('/c2/platform/<string:reference_designator>/operational_status', methods=['GET'])
#@auth.login_required
@scope_required(u'user_admin')
def c2_get_platform_operational_status(reference_designator):
    # C2 get instrument operational status
    return jsonify({'platform_operational_status': [reference_designator]})
'''

#TODO supporting methods - history
'''
#TODO enable cache and code
#@cache.memoize(timeout=3600)
def get_uframe_array_history(array_code):
    #Lists complete history (event, configuration and command) for array (i.e. 'CP')
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, array_code, 'history'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')
#TODO enable cache and code
#@cache.memoize(timeout=3600)
def get_uframe_array_event_history(array_code):
    #Lists event history for array (i.e. 'CP')
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, array_code, 'history', 'event'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')
#TODO enable cache and code
#@cache.memoize(timeout=3600)
def get_uframe_array_command_history(array_code):
    #Lists command history for array (i.e. 'CP')
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, array_code, 'history', 'command'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

#TODO enable cache and code
#@cache.memoize(timeout=3600)
def get_uframe_array_configuration_history(array_code):
    #Lists configuration history for array (i.e. 'CP')
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, array_code, 'history', 'configuration])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

'''

#TODO May need - not off the fence yet...
'''
@api.route('/c2/instrument/<string:reference_designator>/commands/<string:field>', methods=['GET'])
#@auth.login_required
@scope_required(u'user_admin')
def c2_get_instrument_commands(reference_designator, field):
    # C2 get all commands for field for instrument
    return jsonify({'commands': [reference_designator]})

@api.route('/c2/instrument/<string:reference_designator>/<string:stream>/<string:field>', methods=['GET'])
#@auth.login_required
@scope_required(u'user_admin')
def c2_get_instrument_field(reference_designator, field):
    # C2 get instrument stream field for
    return jsonify({'field': [reference_designator]})
'''
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 json data helper methods (json_* version of get_uframe_* methods; one to one)
# uses file data (./ooiuiservices/tests/c2data/*)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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

def json_get_uframe_array_operational_status(array):
    filename = "_".join([array, 'operational_status'])
    try:
        data = read_store(filename)
    except:
        return None
    return data

def json_get_uframe_platforms_operational_status(array_code):
    filename = "_".join([array_code, 'operational_statuses'])
    try:
        data = read_store(filename)
    except:
        return None
    return data

def json_get_uframe_platform_operational_status(platform):
    filename = "_".join([platform, 'operational_status'])
    try:
        data = read_store(filename)
    except:
        return None
    return data

def json_get_uframe_instruments_operational_status(platform):
    filename = "_".join([platform, 'operational_statuses'])
    try:
        data = read_store(filename)
    except:
        return None
    return data

def json_get_uframe_instrument_operational_status(instrument):
    filename = "_".join([instrument, 'operational_status'])
    try:
        data = read_store(filename)
    except:
        return None
    return data

def json_get_uframe_instruments_streams(instruments):
    try:
        streams = {}
        for instrument in instruments:
            filename = "_".join([instrument, 'streams'])
            data = read_store(filename)
            if data:
                streams[instrument] = json.loads(data)
    except:
        return None
    return streams

def json_get_uframe_instrument_streams(instrument):
    try:
        filename = "_".join([instrument, 'streams'])
        data = read_store(filename)
    except:
        return None
    return data

def json_get_uframe_instrument_fields(reference_designator, stream_name):
    try:
        filename = "_".join([reference_designator, stream_name, 'fields'])
        data = read_store(filename)
    except:
        return None
    return data

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 uframe data helpers - use json* helpers until upstream data
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#TODO Increase scope of operational status response (more data!)
#TODO enable cache
#@cache.memoize(timeout=3600)
def get_uframe_platforms_operational_status(array_code):
    '''
    Lists operational status for all platforms in array (i.e. 'CP')

    Sample: http://localhost:7090/service=/sensor/inv/CP/operational_status
    Format of response (list):
    [
        {"id":"CP02PMCO","status":"Online"},
        {"id":"CP02PMCO-RII01","status":"Online"},
        {"id":"CP02PMCO-SBS01","status":"Online"},
        {"id":"CP02PMCO-WFP01","status":"Online"}
    ]
    '''
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, array_code, 'operational_status'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

#TODO enable cache
#@cache.memoize(timeout=3600)
def get_uframe_instruments_operational_status(platform):
    '''
    Lists operational status for all [deployed] instruments in platform (i.e. Central Offshore Platform Mooring)

    Sample: http://localhost:7090/service=/sensor/inv/CP02PMCO-WFP01/operational_status
    Format of response (list):
    [
        {"id":"CP02PMCO-WFP01-03-CTDPFK000","status":"Online"},
        {"id":"CP02PMCO-WFP01-04-FLORTK000","status":"Online"},
        {"id":"CP02PMCO-WFP01-05-PARADK000","status":"Online"},
        {"id":"CP02PMCO-WFP01-02-DOFSTK000","status":"Online"},
        {"id":"CP02PMCO-WFP01-01-VEL3DK000","status":"Online"}
    ]
    output requirements:
        - no duplicate reference_designators provided
        - operational status is 'display worthy' string; no filtering upon receipt from uframe
    '''
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, platform, 'operational_status'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

#TODO enable cache
#@cache.memoize(timeout=3600)
def get_uframe_instrument_operational_status(instrument):
    '''
    Lists operational status for an instrument
    Sample: http://localhost:7090/service=/sensor/inv/CP02PMCO-WFP01-03-CTDPFK000/operational_status
    Format of response (list):
        [ {'id':'CP02PMCO-WFP01-03-CTDPFK000','status':'Online'}]
    '''
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, instrument, 'operational_status'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

#TODO enable cache
#@cache.memoize(timeout=3600)
def get_uframe_instruments_streams(instruments):
    '''
    Lists streams for multiple instruments, return dict keyed by reference_designator.
    For a list of instruments (reference_designators), get streams for each instrument, return dictionary.
    Sample input (instruments):
    instruments = [ 'CP02PMCO-WFP01-03-CTDPFK000', 'CP02PMCO-WFP01-04-FLORTK000', 'CP02PMCO-WFP01-05-PARADK000',
                    'CP02PMCO-WFP01-02-DOFSTK000', 'CP02PMCO-WFP01-01-VEL3DK000']

    For each instrument in instruments:
        get instrument_streams for instrument
        streams[instrument] = instrument_streams

    Response format (dict):
    { 'reference_designator1' : [ "stream_name1", "stream_name2", "stream_name3"],
      'reference_designator2' : [ "stream_name1", "stream_name2"], ...}

    Sample Response:
    {
        'CP02PMCO-WFP01-01-VEL3DK000': ['vel3d_k_wfp_stc_instrument', 'vel3d_k_wfp_stc_metadata'],
        'CP02PMCO-WFP01-02-DOFSTK000': ['dofst_k_wfp_metadata', 'dofst_k_wfp_instrument'],
        'CP02PMCO-WFP01-03-CTDPFK000': ['ctdpf_ckl_wfp_metadata', 'ctdpf_ckl_wfp_instrument'],
        'CP02PMCO-WFP01-05-PARADK000': ['parad_k__stc_imodem_instrument'],
        'CP02PMCO-WFP01-04-FLORTK000': ['flort_kn_stc_imodem_instrument']
    }
    '''
    # get streams for each instrument (instrument==reference_designator)
    streams = {}
    for instrument in instruments:
        try:
            uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
            url = '/'.join([uframe_data, instrument, 'streams'])
            current_app.logger.info("GET %s", url)
            response = requests.get(url)
            if response.status_code != 200:
                continue
            streams[instrument] = json.loads(response.text)
        except:
            return internal_server_error('uframe connection cannot be made.')
    return streams

#TODO enable cache
#@cache.memoize(timeout=3600)
def get_uframe_instrument_streams(instrument):
    '''
    Lists instrument streams for single instrument
    Response format (list):   [ "stream_name1", "stream_name2", "stream_name3"]
    Sample:
        http://localhost:7090/service=/sensor/inv/CP02PMCO-WFP01-03-CTDPFK000/streams provides:
        [ "ctdpf_ckl_wfp_metadata", "ctdpf_ckl_wfp_instrument" ]
    '''
    streams = []
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, instrument, 'streams'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        if response.status_code != 200:     #TODO test this return on error code
            return streams
        streams = json.loads(response.text)
    except:
        return internal_server_error('uframe connection cannot be made.')
    return streams

#TODO enable cache
#@cache.memoize(timeout=3600)
def get_uframe_instrument_fields(instrument, stream_name):
    '''
    Lists field name, units, type and value for instrument in platform (i.e. Central Offshore Platform Mooring)

    Issue with uframe is use of method for stream
    http://localhost:7090/service=/sensor/inv/CP02PMCO/WFP01/05-PARADK000/telemetered/parad_k__stc_imodem_instrument

    Samples:
        Basic syntax: /instrument_rd/stream_name/fields
        http://localhost:7090/service=/sensor/inv/CP02PMCO-WFP01-05-PARADK000/parad_k__stc_imodem_instrument/fields
        http://localhost:7090/service=/sensor/inv/CP02PMCO-SBS01-01-MOPAK0000/mopak_o_dcl_accel/fields

    Format of response (list):
        [{'name':'parad_k_par', 'units': 'umol photons m-2 s-1', 'type': 'Float32', value':'0.27'},
         {'name':'internal_timestamp','units': 'UTC', 'type': 'Float64', 'value':'' },
         {'name':'preferred_timestamp','units': '1', 'type': 'String', 'value':'' },
         {'name':'par_val_v', 'units': 'mV', 'type': 'Float32', 'value':'0.31'},
         {'name':'wfp_timestamp','units': 'UTC', 'type': 'Float64', 'value':'' },
         {'name':'internal_timestamp','units': 'UTC', 'type': 'Float64','value':''},
         {'name':'driver_timestamp', 'units': 'UTC', 'type': 'Float64', ,'value':''}]

    output requirements:
        - output represents fields from a single stream
        - output reflects actual stream associated with instrument
        - no duplicate name(s) in list
        - add more here
    '''
    try:
        uframe_data = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = '/'.join([uframe_data, instrument, stream_name, 'fields'])
        current_app.logger.info("GET %s", url)
        response = requests.get(url)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

#----------------------------------------------------
#-- helpers for array_display
#----------------------------------------------------
def c2_get_platforms_operational_status(reference_designator):
    # Get C2 platform statuses (list of dict) [ {}, {}, {}, ...]
    statuses = None
    '''
    try:
        response = get_uframe_platforms_operational_status(array_code)
        if response.status_code != 200:
            message = "Failed to get operational status for platforms from uFrame"
            return jsonify(error=message), 500
    except:
        return internal_server_error('uframe connection cannot be made.')
    statuses = json.loads(response.text)
    '''
    response_text = json_get_uframe_platforms_operational_status(reference_designator)
    if response_text:
        statuses = json.loads(response_text)
    return statuses

def c2_get_array_operational_status(reference_designator):
    # C2 get array operational status, return status (where status is display value)
    status = 'Unknown'
    if not reference_designator:
        return status
    '''
    #TODO one to one, so make/test uframe version and response
    try:
        response = get_uframe_array_operational_status(reference_designator)
        if response.status_code == 200:
            status = json.loads(response.text)
            operational_status = status[0]['status']
    except Exception, err:
        message = '(get_uframe_array_operational_status) error: '
        return internal_server_error('%s: %s' %(message, err.message))
    '''
    response_text = json_get_uframe_array_operational_status(reference_designator)
    if response_text:
        result = json.loads(response_text)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status


#TODO get history from proper source
def get_history(reference_designator):
    # C2 make fake history for event, command and configuration
    history = { 'event': [], 'command': [], 'configuration':[] }
    history['event'] = []
    history['command'] = []
    history['configuration'] = []

    commands = {}
    commands[1] = { 'msg': 'CMD item 3', 'timestamp' : '2014-11-23T20:00:00' }
    commands[2] = { 'msg': 'Failed Sample Freq from 10 hz to 1 hz', 'timestamp' : '2015-02-04T04:13:56' }
    commands[3] = { 'msg': 'Changed Ping Freq from 10hz to 1 Hz', 'timestamp' : '2015-02-04T07:39:12' }
    history['command'].append(commands)

    # for Power Controller
    events = {}
    events[1] = { 'msg': '2014-10-11T14:00 Turned On' }
    events[2] = { 'msg': '2014-11-11T22:00 Turned Off' }
    history['event'].append(events)

    # for Power Controller
    configuration = {}
    configuration[1] = { 'msg': '2014-11-12T14:00 Initial Configuration' }
    configuration[2] = { 'msg': '2014-11-19T22:00 Loaded PowerSave.config - we needed to turn off' }
    configuration[3] = { 'msg': '2014-11-20T22:00 Loaded AllPorts.config' }
    configuration[4] = { 'msg': '2014-11-21T22:00 Loaded PowerSave.config - we needed to turn off' }
    history['configuration'].append(configuration)
    return history

#----------------------------------------------------
#-- Helpers for platform_display
#----------------------------------------------------
def c2_get_instrument_streams(reference_designator):
    '''
    C2 Get instrument stream(s) list, return streams, fields where
        streams is [stream_name1, stream_name2, ...] and
        fields  is fields = [{field}, {field},...]
    Uses:
        c2_get_instrument_stream_fields(reference_designator, stream_name) returns fields list [{field1}, {field2},...]
    '''
    fields = None
    streams = None
    if not reference_designator:
        return streams, fields

    # Validate reference_designator
    if len(reference_designator) != 27:
        raise bad_request('Invalid reference designator(\'%s\') for instrument; unable to retrieve stream(s).' % reference_designator)
    '''
    try:
        streams = get_uframe_instrument_streams(reference_designator)
    except Exception, err:
        message = '(get_uframe_instrument_streams) error: '
        return internal_server_error('%s: %s' % (message, err.message))
    '''

    response_text = json_get_uframe_instrument_streams(reference_designator)
    if response_text:
        streams = json.loads(response_text)
    # Get instrument fields iff one stream
    if streams:
        if len(streams) == 1:
            stream_name = streams[0]
            # Get list of fields, where each field is dictionary; fields = [{field}, {field},...]
            response_text = c2_get_instrument_stream_fields(reference_designator, stream_name)
            if response_text:
                fields = json.loads(response_text)
    return streams, fields

def c2_get_platform_operational_status(reference_designator):
    # Get C2 platform status (string such as { "unknown" | "Online" | "Offline" }
    status = None
    '''
    # adjust/test this to handle response.text as done in json section
    try:
        response = get_uframe_platform_operational_status(array_code)
        if response.status_code != 200:
            message = "Failed to get operational status for platforms from uFrame"
            return jsonify(error=message), 500
    except:
        return internal_server_error('uframe connection cannot be made.')
    status = json.loads(response.text)
    '''
    response_text = json_get_uframe_platform_operational_status(reference_designator)
    if response_text:
        result = json.loads(response_text)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status


#----------------------------------------------------
# -- Helpers for instrument display
#----------------------------------------------------
def c2_get_instrument_stream_fields(reference_designator, stream_name):
    # C2 get instrument stream fields, return fields (as list [{field1}, {field2},...])
    if not reference_designator:
        raise bad_request('reference_designator parameter is empty.')
        return None, None
    if not stream_name:
        raise bad_request('stream_name parameter is empty.')

    # Validate reference_designator
    if len(reference_designator) != 27:
        raise bad_request('Invalid reference designator(\'%s\') for instrument; unable to retrieve stream(s).' % reference_designator)

    fields = []
    '''
    try:
        # Get list of fields, where each field is dict fields = [{field}, {field},...]
        response = get_uframe_instrument_fields(reference_designator, stream_name)
        if response.status_code == 200:
            fields = json.loads(response.text)
    except Exception, err:
        message = '(get_uframe_instrument_fields) error: '
        return internal_server_error('%s: %s' % (message, err.message))
    '''
    response_text = json_get_uframe_instrument_fields(reference_designator, stream_name)
    if response_text:
        fields = response_text
    return fields

def c2_get_instrument_operational_status(reference_designator):
    # C2 get instrument operational status, return status (where status is operational status display value)
    status = 'Unknown'
    if not reference_designator:
        return status
    '''
    try:
        response = get_uframe_instrument_operational_status(reference_designator)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result:
                if len(result) == 1:
                    if 'id' in result[0] and 'status' in result[0]:
                        if result[0]['id'] == reference_designator:
                            status = result[0]['status']
            status = result[0]['status']
    except Exception, err:
        message = '(get_uframe_instrument_operational_status) error: '
        return internal_server_error('%s: %s' %(message, err.message))
    '''
    response_text = json_get_uframe_instrument_operational_status(reference_designator)
    if response_text:
        result = json.loads(response_text)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status



def c2_get_instruments_operational_status(instruments):
    # Get operational status for all instruments in platform with reference_designator
    statuses = None
    '''
    try:
        response = get_uframe_instruments_operational_status(reference_designator)
        if response.status_code != 200:
            message = "Failed to get operational status for instrument from uFrame"
            return jsonify(error=message), 500
    except:
        return internal_server_error('uframe connection cannot be made.')
    statuses = json.loads(response.text)
    '''
    response_text = json_get_uframe_instruments_operational_status(instruments)
    if response_text:
        statuses = json.loads(response_text)
    return statuses

def c2_get_instruments_streams(instruments):
    # Get C2 streams for each instrument in instruments; return streams (dict keyed by instrument reference_designator)
    # Get list of stream_name(s) supported by instruments in this platform (multiple)
    # Note: to be used in UI for pull down list; based on selection, the ui requests instrument fields for that stream.
    streams = None
    if not instruments:
        return streams
    '''
    try:
        data = get_uframe_instruments_streams(instruments)
    except Exception, err:
        return internal_server_error(err.message)
    '''
    data = json_get_uframe_instruments_streams(instruments)
    if data:
        if len(data) > 0:
            streams = data
    return streams
