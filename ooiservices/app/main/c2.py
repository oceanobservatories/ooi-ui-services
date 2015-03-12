#!/usr/bin/env python
'''
API v1.0 List for Command and Control (C2)

'''
__author__ = 'Edna Donoughe'

from flask import jsonify, request, current_app, url_for, make_response
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app import cache
from authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Instrumentname # Stream, StreamParameter, Organization,
import json
import requests
from ooiservices.app.main.errors import internal_server_error

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 array
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/array_display/<string:array_code>', methods=['GET'])
#@auth.login_required
def c2_get_array_display(array_code):
    #C2 get array display
    contents = []
    array_info = {}
    array = Array.query.filter_by(array_code=array_code).first_or_404()

    # get ordered set of platform_deployments for array.id
    platform_deployments = \
        PlatformDeployment.query.filter_by(array_id=array.id).order_by(PlatformDeployment.reference_designator).all()
    pd = [platform_deployment.to_json() for platform_deployment in platform_deployments]

    # create list of reference_designators and accumulate dict result (key=reference_designator) for use in response
    # (Set all operational_status values to 'Online' by default)
    pd_rds = []
    for p in pd:
        pd_rds.append(p['reference_designator'])
        pd_row = {}
        pd_row['platform_deployment_id'] = p['id']
        pd_row['display_name'] = p['display_name']
        pd_row['reference_designator'] = p['reference_designator']
        pd_row['operational_status'] = 'Online'
        array_info[p['reference_designator']] = pd_row

    # Get operational status for all platforms in array
    '''
    try:
        response = get_uframe_platforms_operational_status(array_code)
        if response.status_code != 200:
            message = "Failed to get operational status for platforms from uFrame"
            return jsonify(error=message), 500
    except:
        return internal_server_error('uframe connection cannot be made.')
    data = json.loads(response.text)
    '''
    response_text = json_get_uframe_platforms_operational_status(array_code)
    data = json.loads(response_text)

    # Add operational data for each platform
    for d in data:
        rd = d['id']
        stat = d['status']
        if rd in array_info:
            array_info[rd]['operational_status'] = stat

    # create list ordered by reference_designator of dictionaries representing data row(s)
    for r in pd_rds:
        if r in array_info:
            contents.append(array_info[r])

    # prepare response
    response_dict = {}
    response_dict['display_name'] = array.display_name
    response_dict['data'] = contents                       # rows for Current Status grid
    response_dict['history'] = get_history()                #TODO get real history
    return jsonify(array_display=response_dict)


def get_history():
    #TODO get history from correct source
    # C2 make fake history for event, command and configuration
    history = {}
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

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 platform
# - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/c2/platform_display/<string:reference_designator>', methods=['GET'])
#@auth.login_required
def c2_get_platform_display(reference_designator):
    # C2 get platform display
    # Sample: http://localhost:4000/c2/platform_display/CP02PMCO-WFP01   (id==104)
    contents = []
    platform_info = {}
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
    pd = platform_deployment.to_json()
    platform_deployment_id = pd['id']
    platform_deployment_display_name = pd['display_name']

    # get ordered set of instrument_deployments for reference_designator (platform)
    instrument_deployments = \
        InstrumentDeployment.query.filter_by(platform_deployment_id=platform_deployment_id).all()
    for i_d in instrument_deployments:
        instrument_name = Instrumentname.query.filter(Instrumentname.instrument_class == i_d.display_name).first()
        if instrument_name:
            i_d.display_name = instrument_name.display_name
    ids = [instrument_deployment.to_json() for instrument_deployment in instrument_deployments]

    # create list of reference_designators and accumulate dict result (key=reference_designator) for use in response
    # (Set all operational_status values to 'Online' by default)
    id_rds = []
    for id in ids:
        id_rds.append(id['reference_designator'])
        id_row = {}
        id_row['instrument_deployment_id'] = id['id']
        id_row['display_name'] = id['display_name']
        id_row['reference_designator'] = id['reference_designator']
        id_row['operational_status'] = 'Online'
        id_row['streams'] = []
        platform_info[id['reference_designator']] = id_row

    # Get operational status for all instruments in platform with reference_designator
    '''
    try:
        response = get_uframe_instruments_operational_status(reference_designator)
        if response.status_code != 200:
            message = "Failed to get operational status for instrument from uFrame"
            return jsonify(error=message), 500
    except:
        return internal_server_error('uframe connection cannot be made.')
    data = json.loads(response.text)
    '''
    response_text = json_get_uframe_instruments_operational_status(reference_designator)
    data = json.loads(response_text)
    # Add operational status to output info
    for d in data:
        rd = d['id']
        stat = d['status']
        if rd in platform_info:
            platform_info[rd]['operational_status'] = stat

    #TODO Review and remove if not needed for platforms (possibly required/helpful for navigation directly to instruments display)
    # Get list of stream_name(s) supported by instruments in this platform (multiple)
    # Note: to be used in UI for pull down list; based on selection, the ui requests instrument fields for that stream.
    '''
    try:
        streams = get_uframe_instruments_streams(id_rds)
    except Exception, err:
        return internal_server_error(err.message)
    '''
    streams = json_get_uframe_instruments_streams(id_rds)

    #Add streams for each instrument to output info
    for item in platform_info:
        res = platform_info[item]
        if res['reference_designator'] in streams:
            res['streams'] = streams[res['reference_designator']]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # create list (ordered by reference_designator) of dictionaries representing row(s) for 'data'
    for r in id_rds:
        if r in platform_info:
            contents.append(platform_info[r])

    # prepare output
    response_dict = {}
    response_dict['data'] = contents                       # rows for Current Status grid
    response_dict['display_name'] = platform_deployment_display_name
    response_dict['history'] = get_history()
    return jsonify(platform_display=response_dict)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 instrument routes
# - - - - - - - - - - - - - - - - - - - - - - - -
#TODO enable auth
@api.route('/c2/instrument_display/<string:reference_designator>', methods=['GET'])
#@auth.login_required
def c2_get_instrument_display(reference_designator):
    # C2 get instrument display
    # iff instrument has one stream, data is populated with fields for stream; commands populated also
    # Sample request:
    #   http://localhost:4000/c2/instrument_display/CP02PMCO-WFP01-05-PARADK000     (1 stream, data populated)
    #   http://localhost:4000/c2/instrument_display/CP02PMCO-WFP01-02-DOFSTK000     (2 streams, no data)
    response_dict = {}
    response_dict['data'] = []
    instrument_deployment = InstrumentDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
    id = instrument_deployment.to_json()
    instrument_deployment_display_name = id['display_name']
    instrument_deployment_id = id['id']

    #TODO def c2_get_instrument_streams(reference_designator) returns streams, [fields, commands]
    # Get instrument stream(s) list
    # Note: used in UI for pull down list; based on selection, the ui requests instrument fields for that stream.)
    '''
    try:
        streams = get_uframe_instrument_streams(reference_designator)
    except Exception, err:
        message = '(get_uframe_instrument_streams) error: '
        return internal_server_error('%s: %s' % (message, err.message))
    '''
    response_text = json_get_uframe_instrument_streams(reference_designator)
    streams = json.loads(response_text)
    # Add instrument streams to output
    response_dict['streams'] = streams      # = c2_get_instrument_streams(reference_designator)

    # Get instrument stream fields if one stream; get commands iff one stream
    fields = []
    '''
    if streams:
        if len(streams) == 1:
            try:
                # Get list of fields, where each field is dict fields = [{field}, {field},...]
                response = get_uframe_instrument_fields(reference_designator, stream_name)
                if response.status_code == 200:
                    fields = json.loads(response.text)

            except Exception, err:
                message = '(get_uframe_instrument_fields) error: '
                return internal_server_error('%s: %s' % (message, err.message))

            #TODO get commands...def c2_get_instrument_stream_commands(reference_designator, stream_name)
            response_dict['commands'] = []  # = get_instrument_stream_commands(reference_designator, stream_name)
    '''
    if streams:
        if len(streams) == 1:
            # Get list of fields, where each field is dict fields = [{field}, {field},...]
            stream_name = streams[0]
            response_text = json_get_uframe_instrument_fields(reference_designator, stream_name)
            fields = json.loads(response_text)
            #TODO get commands...def c2_get_instrument_stream_commands(reference_designator, stream_name)
            response_dict['commands'] = []  # = get_instrument_stream_commands(reference_designator, stream_name)

    # Add field for instrument stream (empty if instrument has more than one stream, or no stream)
    response_dict['data'] = fields

    # Get ports, add to output
    response_dict['ports'] = []     #TODO def c2_get_instrument_ports(reference_designator)

    # Get operational status
    operational_status = 'Unknown'  #TODO def c2_get_instrument_operational_status(reference_designator)
    '''
    try:
        response = get_uframe_instrument_operational_status(reference_designator)
        if response.status_code == 200:
            status = json.loads(response.text)
            operational_status = status[0]['status']
    except Exception, err:
        message = '(get_uframe_instrument_operational_status) error: '
        return internal_server_error('%s: %s' %(message, err.message))
    '''
    response_text = json_get_uframe_instrument_operational_status(reference_designator)
    operational_status = json.loads(response_text)
    # Prepare output result
    response_dict['operational_status'] = operational_status            #TODO get real operational_status
    response_dict['history'] = get_history()                            #TODO get real history for instrument
    response_dict['display_name'] = instrument_deployment_display_name
    response_dict['id'] = instrument_deployment_id
    response_dict['reference_designator'] = reference_designator
    return jsonify(instrument_display=response_dict)

#TODO enable auth
@api.route('/c2/instrument/<string:reference_designator>/<string:stream_name>/fields', methods=['GET'])
#@auth.login_required
def c2_get_instrument_fields(reference_designator, stream_name):
    # C2 get instrument stream fields
    '''
    Sample requests:
        http://localhost:4000/c2/instrument/CP02PMCO-SBS01-01-MOPAK0000/mopak_o_dcl_accel/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-02-DOFSTK000/dofst_k_wfp_metadata/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_instrument/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-03-CTDPFK000/ctdpf_ckl_wfp_metadata/fields
        http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k__stc_imodem_instrument/fields
    '''
    '''
    try:
        response = get_uframe_instrument_fields(reference_designator, stream_name)
        if response.status_code != 200:
            message = "Failed to get fields for instrument [from uFrame]"
            return jsonify(error=message), 500
    except:
        return internal_server_error('uframe connection cannot be made.')
    data = json.loads(response.text)
    '''
    response_text = json_get_uframe_instrument_fields(reference_designator, stream_name)
    data = json.loads(response_text)
    # process fields - get name-units-type-value for each field;  field id added for development and ease of use
    # create list of field dictionary items: [{name-units-type-value}, {name-units-type-value}, {name-units-type-value}]
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
    field_contents = []
    for field_name in ofields:
        field_contents.append(fields[field_name])

    # prepare output result
    result = []
    display_content = {}
    display_content['reference_designator'] = reference_designator
    display_content['stream_name'] = stream_name
    display_content['data'] = field_contents
    result.append(display_content)
    return jsonify(fields=result)

#TODO enable auth and code - under construction
'''
#curl -X PUT http://localhost:4000/c2/instrument_update/CP02PMCO-SBS01-01-MOPAK0000?stream=mopak_o_dcl_accel&field=qualityflag&command=set&value=bad
@api.route('/c2/instrument_update/<string:reference_designator>/<string:stream_name>/<string:field>/<string:command>/<string:value>', methods=['PUT'])
#@auth.login_required
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

#TODO enable auth and code
@api.route('/c2/instrument/<string:reference_designator>/operational_status', methods=['GET'])
#@auth.login_required
def c2_get_instrument_operational_status(reference_designator):
    # C2 get operational status value for instrument with reference_designator
    print reference_designator
    return jsonify({'instrument_operational_status': [reference_designator]})
'''

#TODO - routes under review
'''
#TODO enable auth and code
@api.route('/c2/platform/<string:reference_designator>/operational_status', methods=['GET'])
#@auth.login_required
def c2_get_platform_operational_status(reference_designator):
    # C2 get operational status value for instrument with reference_designator

    print reference_designator
    return jsonify({'platform_operational_status': [reference_designator]})

#TODO enable auth and code
@api.route('/c2/platform/<string:reference_designator>/history', methods=['GET'])
#@auth.login_required
def c2_get_platform_history(reference_designator, type):
    # C2 get all types of history for instrument with reference_designator
    type = 'all'
    return jsonify({'complete_history': [reference_designator]})

#TODO enable auth and code
@api.route('/c2/platform/<string:reference_designator>/history/<string:type>', methods=['GET'])
#@auth.login_required
def c2_get_platform_history_by_type(reference_designator, type):
    # C2 get specific type of history for instrument with reference_designator
    # valid type values = { all | event | command | config }
    return jsonify({'platform_operational_status': [reference_designator]})

#TODO enable auth and code
@api.route('/c2/instrument/<string:reference_designator>/history', methods=['GET'])
#@auth.login_required
def c2_get_instrument_history(reference_designator, type):
    # C2 get all types of history for instrument with reference_designator
    type = 'all'
    print reference_designator
    return jsonify({'complete_history': [reference_designator]})

#TODO enable auth and code
@api.route('/c2/instrument/<string:reference_designator>/history/<string:type>', methods=['GET'])
#@auth.login_required
def c2_get_instrument_history_by_type(reference_designator, type):
    # C2 get specific type of history for instrument with reference_designator
    # valid type values = { all | event | command | config }
    print reference_designator
    return jsonify({'instrument_operational_status': [reference_designator]})


'''

#TODO supporting methods - history
'''
#TODO enable cache and code
#@cache.memoize(timeout=3600)
def get_uframe_array_history(array_code):
    #Lists complete history for array (i.e. 'CP')
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
        url = '/'.join([uframe_data, array_code, 'event_history'])
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
        url = '/'.join([uframe_data, array_code, 'command_history'])
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
def c2_get_instrument_commands(reference_designator, field):
    # C2 get all commands for field for instrument with reference_designator
    print reference_designator
    return jsonify({'commands': [reference_designator]})

@api.route('/c2/instrument/<string:reference_designator>/<string:field>', methods=['GET'])
#@auth.login_required
def c2_get_instrument_field(reference_designator, field):
    # C2 get field=field for instrument with reference_designator
    print reference_designator
    return jsonify({'instrument_field': [reference_designator]})
'''
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 json uframe helper methods (json_* version of get_uframe_* methods)
# uses file data (./ooiuiservices/tests/c2data/*)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def read_store(filename):
    '''
    open filename, read data, close file and return data
    '''
    c2_data_path = './ooiservices/tests/c2data'
    data = None
    try:
        tmp = "/".join([c2_data_path, filename])
        f = open(tmp, 'rb')
        data = f.read()
        f.close()
    except Exception, err:
        raise Exception('%s' % err.message)
    return data

def json_get_uframe_platforms_operational_status(array_code):
    filename = "_".join([array_code, 'operational_status'])
    try:
        data = read_store(filename)
    except Exception, err:
        message = '(json_get_uframe_platforms_operational_status) error: %s' % err.message
        return jsonify({'error': message})
    return data

def json_get_uframe_instruments_operational_status(platform):
    filename = "_".join([platform, 'operational_status'])
    try:
        data = read_store(filename)
    except Exception, err:
        message = '(json_get_uframe_instruments_operational_status) error: %s' % err.message
        return jsonify({'error': message})
    return data

def json_get_uframe_instrument_operational_status(instrument):
    filename = "_".join([instrument, 'operational_status'])
    try:
        data = read_store(filename)
    except Exception, err:
        message = '(json_get_uframe_instrument_operational_status) error: %s' % err.message
        return jsonify({'error': message})
    return data

def json_get_uframe_instruments_streams(instruments):
    try:
        streams = {}
        for instrument in instruments:
            filename = "_".join([instrument, 'streams'])
            data = read_store(filename)
            streams[instrument] = json.loads(data)
    except Exception, err:
        message = '(json_get_uframe_instruments_streams) error: %s' % err.message
        return jsonify({'error': message})
    return streams

def json_get_uframe_instrument_streams(instrument):
    try:
        filename = "_".join([instrument, 'streams'])
        data = read_store(filename)
    except Exception, err:
        message = '(json_get_uframe_instrument_streams) error: %s' % err.message
        return jsonify({'error': message})
    return data

def json_get_uframe_instrument_fields(reference_designator, stream_name):
    filename = "_".join([reference_designator, stream_name, 'fields'])
    try:
        data = read_store(filename)
    except Exception, err:
        message = '(json_get_instrument_fields) error: %s' % err.message
        return jsonify({'error': message})
    return data

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 uframe helpers - use json* helpers instead
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#TODO Increase scope of operational status response (more data)
#TODO enable cache
#@cache.memoize(timeout=3600)
def get_uframe_platforms_operational_status(array_code):
    '''
    Lists operational status for all [deployed] platforms in array (i.e. 'CP')

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
#TODO enable command attribute at param level
#TODO rename fields to params throughout
#@cache.memoize(timeout=3600)
def get_uframe_instrument_fields(instrument, stream_name):
    '''
    Lists field name, units, type and value for instrument in platform (i.e. Central Offshore Platform Mooring)

    Issue with uframe:
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
