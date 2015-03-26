#!/usr/bin/env python
'''
API v1.0 List for Command and Control (C2)

'''
__author__ = 'Edna Donoughe'

from flask import jsonify
from ooiservices.app.main import api
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Instrumentname
import json, os
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
import simplejson

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 array routes
# - - - - - - - - - - - - - - - - - - - - - - - -
#TODO enable auth and scope
@api.route('/c2/arrays', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_arrays():
    #Get C2 arrays, return list of abstracts for each array
    list_of_arrays = []
    arrays = Array.query.all()
    for array in arrays:
        item = get_array_abstract(array.array_code)
        if item:
            list_of_arrays.append(item)
    return jsonify(arrays=list_of_arrays)

#TODO enable auth and scope; get operational status from uframe
@api.route('/c2/array/<string:array_code>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_abstract(array_code):
    #Get C2 array abstract (display), return abstract
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    response_dict = get_array_abstract(array_code)
    return jsonify(abstract=response_dict)

def get_array_abstract(array_code):
    # raise, don't return error
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    response_dict = {}
    response_dict['display_name'] = array.display_name
    response_dict['reference_designator'] = array.array_code
    response_dict['array_id'] = array.id
    response_dict['operational_status'] = c2_get_array_operational_status(array_code)
    return response_dict

#TODO enable auth and scope; get operational status from uframe
@api.route('/c2/array/<string:array_code>/current_status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_current_status_display(array_code):
    # C2 get array Current Status tab contents, return current_status_display
    contents = []
    array_info = {}
    reference_designator = array_code
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
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

#TODO enable auth and scope
@api.route('/c2/array/<string:array_code>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_history(array_code):
    # C2 get array history, return history
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    history = { 'event': [], 'command': [], 'configuration':[] }
    if array_code:
        history = get_history(array_code)
    return jsonify(history=history)

#TODO enable auth and scope; complete using uframe status
@api.route('/c2/array/<string:array_code>/status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_array_status_display(array_code):
    #Get C2 array status (display), return status_display (contents of platform Status tab)
    array = Array.query.filter_by(array_code=array_code).first()
    if not array:
        return bad_request('unknown array (array_code: \'%s\')' % array_code)
    status_display = {}
    return jsonify(status_display=status_display)

# - - - - - - - - - - - - - - - - - - - - - - - -
# C2 platform
# - - - - - - - - - - - - - - - - - - - - - - - -
#TODO enable auth and scope; get operational status from uframe
@api.route('/c2/platform/<string:reference_designator>/abstract', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_abstract(reference_designator):
    #Get C2 platform abstract, return abstract
    response_dict = {}
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
    if not platform_deployment:
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    response_dict = {}
    response_dict['display_name'] = platform_deployment.display_name
    response_dict['reference_designator'] = platform_deployment.reference_designator
    response_dict['platform_deployment_id'] = platform_deployment.id
    response_dict['operational_status'] = c2_get_platform_operational_status(reference_designator)
    return jsonify(abstract=response_dict)

#TODO enable auth and scope
#TODO complete with actual status from uframe
@api.route('/c2/platform/<string:reference_designator>/current_status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_current_status_display(reference_designator):
    #Get C2 platform Current Status tab contents, return current_status_display
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
    if not _platform_deployment(reference_designator):
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    history = { 'event': [], 'command': [], 'configuration':[] }
    if reference_designator:
        history = get_history(reference_designator)
    return jsonify(history=history)

#TODO enable auth and scope
#TODO complete with port and instrument status from uframe
@api.route('/c2/platform/<string:reference_designator>/ports_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_ports_display(reference_designator):
    #Get C2 platform Ports tab contents, return ports_display ([{},{},...] where
    # dicts for each instrument_deployment in platform_deployment:
    #   For example:
    #   http://localhost:4000/c2/platform/CP02PMCO-WFP01/ports_display
    #   response:
    #   {"ports_display": [
    #                        {
    #                          "class": "PARAD",
    #                          "instrument": "CP02PMCO-WFP01-05-PARADK000",
    #                          "instrument_status": "Online",
    #                          "port": "05",
    #                          "port_available": "False",
    #                          "port_status": "Online",
    #                          "sequence": "000",
    #                          "series": "K"
    #                        },
    #                   ...]}
    #
    # Samples:
    #   http://localhost:4000/c2/platform/CP02PMCO-WFP01/ports_display    Pioneer (CP)
    #   http://localhost:4000/c2/platform/CP02PMCO-RII01/ports_display    Pioneer (CP)
    #   http://localhost:4000/c2/platform/CP02PMCO-SBS01/ports_display    Pioneer (CP)
    #   http://localhost:4000/c2/platform/CE01ISSM-MFD00/ports_display    Endurance (CE)
    #   http://localhost:4000/c2/platform/RS03ECAL-MJ03E/ports_display    Regional Scale (RS)
    contents = []
    platform_info = {}
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
    if not platform_deployment:
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    # get ordered set of instrument_deployments for platform
    instrument_deployments = \
        InstrumentDeployment.query.filter_by(platform_deployment_id=platform_deployment.id).all()
    '''
    # hold for now
    for i_d in instrument_deployments:
        instrument_name = Instrumentname.query.filter(Instrumentname.instrument_class == i_d.display_name).first()
        if instrument_name:
            i_d.display_name = instrument_name.display_name
    '''
    # create list of reference_designators (instruments) and accumulate dict result (key=reference_designator) for output
    instruments = []
    for instrument_deployment in instrument_deployments:
        rd = instrument_deployment.reference_designator
        instruments.append(instrument_deployment.reference_designator)
        port    = rd[15:15+2]
        iclass  = rd[18:18+5]
        iseries = rd[23:23+1]
        iseq    = rd[24:24+3]
        row = {}
        row['port'] = port
        row['port_status'] = c2_get_platform_operational_status(reference_designator) # same as platform for now
        row['port_available'] = str(True)
        if row['port_status'] == 'Online' or row['port_status'] == 'Unknown':
            row['port_available'] = str(False)
        row['instrument'] = instrument_deployment.reference_designator
        row['class'] = iclass
        row['series']= iseries
        row['sequence'] = iseq
        row['instrument_status'] = 'Unknown'
        platform_info[instrument_deployment.reference_designator] = row
    # Get operational status for all instruments in platform; add to output
    statuses = c2_get_instruments_operational_status(platform_deployment.reference_designator)
    if statuses:
        for d in statuses:
            rd = d['id']
            stat = d['status']
            if rd in platform_info:
                platform_info[rd]['instrument_status'] = stat
    # Create list of dictionaries representing row(s) for 'data' (ordered by reference_designator)
    # 'data' == rows for initial grid ('Current Status')
    for instrument_deployment_reference_designator in instruments:
        if instrument_deployment_reference_designator in platform_info:
            contents.append(platform_info[instrument_deployment_reference_designator])
    return jsonify(ports_display=contents)

#TODO enable auth and scope
#TODO complete using status from uframe
@api.route('/c2/platform/<string:reference_designator>/status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_status_display(reference_designator):
    #Get C2 platform Status tab contents, return status_display
    if not _platform_deployment(reference_designator):
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    status_display = {}
    return jsonify(status_display=status_display)

#TODO enable auth and scope
#TODO complete with commands from uframe (TBD)
@api.route('/c2/platform/<string:reference_designator>/commands', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_platform_commands(reference_designator):
    #Get C2 platform commands (pulldown list) contents, return commands [{},{},...]
    if not _platform_deployment(reference_designator):
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    commands = []
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
    # C2 get instrument abstract, return abstract
    try:
        response_dict = {}
        response_dict['data'] = []
        instrument_deployment = InstrumentDeployment.query.filter_by(reference_designator=reference_designator).first()
        if not instrument_deployment:
            return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
        response_dict = {}
        response_dict['display_name'] = instrument_deployment.display_name
        response_dict['reference_designator'] = instrument_deployment.reference_designator
        response_dict['instrument_deployment_id'] = instrument_deployment.id
        response_dict['operational_status'] = c2_get_instrument_operational_status(reference_designator)
    except Exception, err:
        return bad_request(err.message)
    return jsonify(abstract=response_dict)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/streams', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_streams(reference_designator):
    # C2 get instrument streams, return streams
    try:
        if not _instrument_deployment(reference_designator):
            return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
        streams, fields = _c2_get_instrument_streams(reference_designator)
        if not streams:
            return bad_request('Failed to retrieve streams for instrument (reference designator \'%s\')' % reference_designator)
    except Exception, err:
        return bad_request(err.message)
    return jsonify(streams=streams)

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/history', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_history(reference_designator):
    # C2 get instrument history, return history
    # (history = { 'event': [], 'command': [], 'configuration':[] })
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    history = get_history(reference_designator)
    return jsonify(history=history)

#TODO enable auth and scope; contents TBD by UI
@api.route('/c2/instrument/<string:reference_designator>/ports_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_ports_display(reference_designator):
    #Get C2 instrument Ports tab contents, return ports_display
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    ports_display =  {}
    return jsonify(ports_display=ports_display)

#TODO enable auth and scope; uframe status required
@api.route('/c2/instrument/<string:reference_designator>/status_display', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_status_display(reference_designator):
    #Get C2 instrument Status tab contents, return status_display
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    status_display = {}
    return jsonify(status_display=status_display)

#TODO enable auth and scope; uframe data required
@api.route('/c2/instrument/<string:reference_designator>/commands', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_commands(reference_designator):
    #Get C2 instrument commands, return commands [{},{},...]
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    commands = []
    response_text = json_get_uframe_instrument_commands(reference_designator)
    if response_text:
        try:
            commands = json.loads(response_text)
        except:
            return bad_request('Failed to retrieve commands for instrument (reference designator \'%s\')' % reference_designator)
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
    Errors:
        bad_request('Invalid reference designator for instrument (\'%s\').' % reference_designator)
        bad_request('Failed to retrieve stream data for instrument (reference designator \'%s\')' % reference_designator)
        bad_request('Invalid stream name (\'%s\') for instrument (\'%s\')' % (stream_name, reference_designator))
        bad_request('Malformed fields data; not in valid json format (\'%s\',\'%s\')' % (reference_designator, stream_name))
    '''
    # Verify reference_designator is for existing instrument_deployment; get streams
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    streams = None
    response_text = json_get_uframe_instrument_streams(reference_designator)
    if response_text:
        try:
            streams = json.loads(response_text)
        except:
            return bad_request('Malformed stream data; not in valid json format. (reference designator \'%s\')' % reference_designator)
    else:
        return bad_request('Failed to retrieve stream data for instrument (reference designator \'%s\')' % reference_designator)

    # Verify valid stream_name (verify stream requested is one of streams available for this instrument)
    if stream_name not in streams:
        return bad_request('Invalid stream name (\'%s\') for instrument (\'%s\')' % (stream_name, reference_designator))
    # Get and add fields to output
    field_contents = []
    try:
        fields = c2_get_instrument_stream_fields(reference_designator, stream_name)
    except Exception, err:
        return bad_request(err.message)
    if fields:
        try:
            data = json.loads(fields)
        except:
            return bad_request('Malformed fields data; not in valid json format (\'%s\',\'%s\')' % (reference_designator, stream_name))
        # process fields - get name-units-type-value for each field;  field id added for development and ease of use
        fields = {}
        ofields = []
        inx = 1
        for elem in data:
            field = {}
            for k,v in elem.iteritems():
                field[k] = v
            if field['name'] not in ofields:
                field['id'] = inx
                fields[field['name']] = field
                ofields.append(field['name'])
                inx += 1
        for field_name in ofields:
            field_contents.append(fields[field_name])
    return jsonify(fields=field_contents)

#TODO enable auth and scope
@api.route('/c2/instrument_update/<string:reference_designator>/<string:stream_name>/<string:field_name>/<string:command_name>/<string:field_value>',methods=['PUT'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_update_instrument_field_value(reference_designator, stream_name, field_name, command_name, field_value):
    # C2 update instrument stream field value with value provided using command (just value update now)
    # TODO attributes other than value; type checking for valid types; verify command
    # Samples:
    # http://localhost:4000/c2/instrument_update/CP02PMCO-SBS01-01-MOPAK0000/mopak_o_dcl_accel/control_String/set/bad
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    if not stream_name:
        return bad_request('stream_name parameter is empty')
    if not field_name:
        return bad_request('field parameter is empty')
    if not command_name:
        return bad_request('command parameter is empty')
    try:
        available_streams, available_fields = _c2_get_instrument_streams(reference_designator)
    except Exception, err:
        return bad_request('c2_get_instrument_streams exception: %s' % err.message)
    if available_streams == None:
        return bad_request('no streams for instrument_deployment (reference_designator: \'%s\')' % \
            (reference_designator))
    if stream_name not in available_streams:
        return bad_request('unknown stream (\'%s\') for instrument_deployment (reference_designator: \'%s\')' % \
        (stream_name,reference_designator))
    fields = available_fields
    if not available_fields:
        response_text = c2_get_instrument_fields(reference_designator,stream_name)
        try:
            fields = json.loads(response_text)
        except:
            return bad_request('Malformed fields data; not in valid json format. (reference designator \'%s\')' %
                               reference_designator)
    if not fields:
        return bad_request('No fields for stream (\'%s\') in instrument_deployment (reference designator \'%s\')' %
                           (stream_name, reference_designator))
    # verify field_name in fields
    field = None
    out_fields = []
    for _field in fields:
        if _field['name'] == field_name:
            field = _field
        else:
            out_fields.append(_field)
    if not field:
        return bad_request('Unknown field_name (\'%s\') for stream (\'%s\') in instrument_deployment (reference_designator: \'%s\')' % \
            (field_name, stream_name, reference_designator))
    #valid_commands = ['SET']
    #valid_unit_types = ['UTC', 'rad s-1', 'Gs', 'mV', '1']
    #Verify type of value against field value type
    valid_value_types = ['Float32', 'Float64', 'String', 'Int16', 'Int32']   # 'Byte'
    _field_type = field['type']
    if not _field_type:
        return bad_request('field type (\'%s\') not defined for field (\'%s\') in stream (\'%s\') in instrument_deployment (reference_designator: \'%s\')' % \
                                (_field_type, field, stream_name, reference_designator))
    if _field_type not in valid_value_types:
        return bad_request('Unknown field type (\'%s\') for field (\'%s\') in stream (\'%s\') in instrument_deployment (reference_designator: \'%s\')' % \
                            (_field_type, field, stream_name, reference_designator))
    # Update attribute 'value' based on field type
    try:
        if _field_type == 'Float32' or _field_type == 'Float64':
            value = float(field_value)
        elif _field_type == 'String':
            value = str(field_value)
        elif _field_type == 'Int16' or _field_type == 'Int32':
            value = int(field_value)
        else:
            raise Exception()
    except:
        return bad_request('field_value (\'%s\') not of type %s for stream (\'%s\') in instrument_deployment (reference_designator: \'%s\')' % \
                            (field_value, _field_type, stream_name, reference_designator))
    field['value'] = str(value)
    out_fields.append(field)
    # Update store
    try:
        filename = "_".join([reference_designator, stream_name, 'fields'])
        write_store(filename, out_fields)
    except:
        return bad_request('Failed to write store (\'%s\') for field (\'%s\') in stream (\'%s\') in instrument_deployment (reference_designator: \'%s\')' % \
                (filename,  field_name, stream_name,reference_designator))
    return jsonify({'message': 'field updated', 'field': field_name, 'value': value }), 200

#TODO enable auth and scope
@api.route('/c2/instrument/<string:reference_designator>/<string:stream_name>/<string:field_name>', methods=['GET'])
#@auth.login_required
#@scope_required(u'user_admin')
def c2_get_instrument_stream_field(reference_designator, stream_name, field_name):
    # C2 get instrument field_name
    # Sample:
    #   http://localhost:4000/c2/instrument/CP02PMCO-WFP01-05-PARADK000/parad_k_stc_imodem_instrument/parad_k_par
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    if not stream_name:
        return bad_request('stream_name parameter is empty')
    if not field_name:
        return bad_request('field parameter is empty')
    try:
        available_streams, available_fields = _c2_get_instrument_streams(reference_designator)
    except Exception, err:
        return bad_request('c2_get_instrument_streams exception: %s' % err.message)
    if available_streams == None:
        return bad_request('no streams for instrument_deployment (reference_designator: \'%s\')' % \
            (reference_designator))
    if stream_name not in available_streams:
        return bad_request('unknown stream (\'%s\') for instrument_deployment (reference_designator: \'%s\')' % \
        (stream_name,reference_designator))
    fields = available_fields
    if not available_fields:
        response_text = c2_get_instrument_fields(reference_designator,stream_name)
        try:
            fields = json.loads(response_text)
        except:
            return bad_request('Malformed fields data; not in valid json format. (reference designator \'%s\')' %
                               reference_designator)
    if not fields:
        return bad_request('No fields for stream (\'%s\') in instrument_deployment (reference designator \'%s\')' %
                           (stream_name, reference_designator))
    # verify field in fields
    field = None
    out_fields = []
    _field = {}
    for _field in fields:
        if _field['name'] == field_name:
            field = _field
        else:
            out_fields.append(_field)
    if not field:
        return bad_request('unknown field (\'%s\') for stream (\'%s\') in instrument_deployment (reference_designator: \'%s\')' % \
            (field_name, stream_name, reference_designator))
    return jsonify(field=field)

#----------------------------------------------------
# general helpers
#----------------------------------------------------
def _platform_deployment(reference_designator):
    result = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
    return result

def _instrument_deployment(reference_designator):
    result = InstrumentDeployment.query.filter_by(reference_designator=reference_designator).first()
    return result

#TODO get history from proper source
def get_history(reference_designator):
    # C2 make fake history for event, command and configuration
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
def c2_get_platforms_operational_status(reference_designator):
    # Get C2 platform statuses (list of dict) [ {}, {}, {}, ...]
    statuses = None
    response_text = json_get_uframe_platforms_operational_status(reference_designator)
    if response_text:
        try:
            statuses = json.loads(response_text)
        except:
            return bad_request('Malformed operational statuses data; not in valid json format. (reference designator \'%s\')' % reference_designator)
    return statuses

def c2_get_array_operational_status(reference_designator):
    # C2 get array operational status, return status (where status is display value)
    status = 'Unknown'
    response_text = json_get_uframe_array_operational_status(reference_designator)
    if response_text:
        try:
            result = json.loads(response_text)
        except:
            return bad_request('Malformed operational status data; not in valid json format. (reference designator \'%s\')' % reference_designator)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status

#----------------------------------------------------
#-- file based helpers for platform_display
#----------------------------------------------------
#TODO get_instrument_stream
def _c2_get_instrument_streams(reference_designator):
    '''
    C2 Get instrument stream(s) list, return streams, fields where
        streams is [stream_name1, stream_name2, ...] and
        fields  is fields = [{field}, {field},...]
    Uses:
        c2_get_instrument_stream_fields(reference_designator, stream_name) returns fields list [{field1}, {field2},...]
    '''
    fields = None
    streams = None
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    response_text = json_get_uframe_instrument_streams(reference_designator)
    if response_text:
        try:
            streams = json.loads(response_text)
        except:
            raise Exception('Malformed streams data; not in valid json format. (reference designator \'%s\')' % reference_designator)
    # Get instrument fields iff one stream
    if streams:
        if len(streams) == 1:
            stream_name = streams[0]
            if stream_name:
                # Get list of fields, where each field is dictionary; fields = [{field}, {field},...]
                response_text = c2_get_instrument_stream_fields(reference_designator, stream_name)
                if response_text:
                    try:
                        fields = json.loads(response_text)
                    except:
                        raise Exception('Malformed fields data; not in valid json format. (reference designator \'%s\')' % reference_designator)
    return streams, fields

def c2_get_platform_operational_status(reference_designator):
    # Get C2 platform status (string such as { "unknown" | "Online" | "Offline" }
    status = 'Unknown'
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
    if not platform_deployment:
        return bad_request('unknown platform_deployment (reference_designator: \'%s\')' % reference_designator)
    response_text = json_get_uframe_platform_operational_status(reference_designator)
    if response_text:
        try:
            result = json.loads(response_text)
        except:
            return bad_request('Malformed streams data; not in valid json format. (reference designator \'%s\')' % reference_designator)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status

#----------------------------------------------------
# -- file based helpers for instrument display
#----------------------------------------------------
def c2_get_instrument_stream_fields(reference_designator, stream_name):
    # C2 get instrument stream fields, return fields (as list [{field1}, {field2},...])
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    fields = []
    response_text = json_get_uframe_instrument_fields(reference_designator, stream_name)
    if response_text:
        fields = response_text
    return fields

def c2_get_instrument_operational_status(reference_designator):
    # C2 get instrument operational status, return status (where status is operational status display value)
    status = 'Unknown'
    if not _instrument_deployment(reference_designator):
        return bad_request('unknown instrument_deployment (reference_designator: \'%s\')' % reference_designator)
    response_text = json_get_uframe_instrument_operational_status(reference_designator)
    if response_text:
        try:
            result = json.loads(response_text)
        except:
            raise Exception('Malformed operational status data; not in valid json format. (reference designator \'%s\')' % reference_designator)
        if result:
            if len(result) == 1:
                if 'id' in result[0] and 'status' in result[0]:
                    if result[0]['id'] == reference_designator:
                        status = result[0]['status']
    return status

def c2_get_instruments_operational_status(instruments):
    # Get operational status for all instruments in platform
    statuses = None
    response_text = json_get_uframe_instruments_operational_status(instruments)
    if response_text:
        try:
            statuses = json.loads(response_text)
        except:
            raise Exception('Malformed operational statuses data for list of instruments; not in valid json format.')
    return statuses

def c2_get_instruments_streams(instruments):
    # Get C2 streams for each instrument in instruments; return streams (dict keyed by instrument reference_designator)
    # Get list of stream_name(s) supported by instruments in this platform (multiple)
    # Note: to be used in UI for pull down list; based on selection, the ui requests instrument fields for that stream.
    streams = None
    data = json_get_uframe_instruments_streams(instruments)
    if data:
        if len(data) > 0:
            streams = data
    return streams

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 helper for file data (./ooiuiservices/tests/c2data/*)
# Each of these will be replaced with interface to uframe or interface other than file
# TODO replace all file based data with uframe data
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

def json_get_uframe_platform_commands(platform):
    filename = "_".join([platform, 'commands'])
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

def json_get_uframe_instrument_commands(instrument):
    filename = "_".join([instrument, 'commands'])
    try:
        data = read_store(filename)
    except:
        return None
    return data

def write_store(filename, data):
    '''
    open filename, write data list and close file
    note: used by c2_update_instrument_field_value
    '''
    try:
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
        c2_data_path = os.path.join(APP_ROOT, '..', '..', 'tests', 'c2data')
        tmp = "/".join([c2_data_path, filename])
        f = open(tmp, 'wb')
        simplejson.dump(data, f)
        f.close()
    except Exception, err:
        raise Exception('%s' % err.message)
    return None

