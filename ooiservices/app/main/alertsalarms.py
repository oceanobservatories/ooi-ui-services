#!/usr/bin/env python
'''
Alerts & Alarms Endpoints

'''
__author__ = 'James Case'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.models import SystemEventDefinition, SystemEvent, User
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import conflict, bad_request
from datetime import datetime
import requests

import json

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts & Alarms
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#List all alerts and alarms
@api.route('/alert_alarm')
def get_alerts_alarms():
    result = []
    if 'type' in request.args:
        alerts_alarms = SystemEvent.query.filter_by(event_type=request.args.get('type'))
    else:
        alerts_alarms = SystemEvent.query.all()
    if alerts_alarms:
        result = [alert_alarm.to_json() for alert_alarm in alerts_alarms]
    return jsonify( {'alert_alarm' : result })

#List an alerts and alarms by id
@api.route('/alert_alarm/<string:id>')
def get_alert_alarm(id):
    alert_alarm = SystemEvent.query.filter_by(id=id).first_or_404()
    return jsonify(alert_alarm.to_json())

#Create a new alert/alarm
@api.route('/alert_alarm', methods=['POST'])
# @auth.login_required
# @scope_required('annotate')
def create_alert_alarm():
    """
    Create an alert or an alarm; invoked by uframe_qpid service.
    """
    # todo: utilize event_time received from uframe.
    try:
        # Process request.data; verify required fields are present
        data = json.loads(request.data)
        create_has_required_fields(data)
        uframe_filter_id = data['uframe_filter_id']
        uframe_event_id = data['uframe_event_id']

        # Get system_event_definition_id using uframe_filter_id provided in request.data
        try:
            system_event_definition = SystemEventDefinition.query.filter_by(uframe_filter_id=uframe_filter_id).first()
            if system_event_definition is None:
                raise Exception('Failed to retrieve SystemEventDefinition for uframe_filter_id: %d' % uframe_filter_id)
            system_event_definition_id = system_event_definition.id
        except Exception as err:
            # This is a severe error, definitely should be logged (failure to record instance of alert or alarm from uframe)
            print '\n message: ', err.message
            raise  Exception(err.message)

        if system_event_definition_id is None:
            message = 'Unable to identify system_event_definition_id using uframe_filter_id (%d)' % uframe_filter_id
            print '\n message: ', message
            raise Exception(message)

        # Create SystemEvent
        alert_alarm = SystemEvent()
        alert_alarm.uframe_event_id = uframe_event_id
        alert_alarm.uframe_filter_id = uframe_filter_id
        alert_alarm.system_event_definition_id = system_event_definition_id
        alert_alarm.event_time = datetime.now()                             # todo data['event_time'] to date
        alert_alarm.event_type = data['event_type']
        alert_alarm.event_response = data['event_response']
        alert_alarm.method = data['method']
        alert_alarm.deployment = data['deployment']
        try:
            db.session.add(alert_alarm)
            db.session.commit()
        except Exception as err:
            # todo - test case
            #print '\n create_alert_alarm db exception message: ', err.message
            db.session.rollback()
            return bad_request('IntegrityError creating alert_alarm')

        return jsonify(alert_alarm.to_json()), 201
    except Exception as err:
        #print '\n create_alert_alarm message: ', err.message
        return conflict('Insufficient data, or bad data format.')

# todo - discuss this method [finish, test case]
'''
@api.route('/delete_alert_alarm/<int:id>', methods=['DELETE'])
#@auth.login_required
#@scope_required('user_admin')
def delete_alert_alarm(id):
    """
    Delete SystemEvent for alert or alarm.
    """
    event = SystemEvent.query.get(id)
    if event is None:
        return jsonify(error="alert_alarm Not Found"), 404
    db.session.delete(event)
    db.session.commit()
    return jsonify(), 200
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts & Alarms Definitions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#List all alert and alarm definitions
@api.route('/alert_alarm_definition')
def get_alerts_alarms_def():
    if 'array_name' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(array_name=request.args.get('array_name'))
    elif 'platform_name' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(platform_name=request.args.get('platform_name'))
    elif 'instrument_name' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(instrument_name=request.args.get('instrument_name'))
    elif 'reference_designator' in request.args:
        alerts_alarms_def = SystemEventDefinition.query.filter_by(reference_designator=request.args.get('reference_designator'))
    else:
        alerts_alarms_def = SystemEventDefinition.query.all()
    return jsonify( {'alert_alarm_definition' : [alert_alarm_def.to_json() for alert_alarm_def in alerts_alarms_def] })

#List an alerts and alarms definition by id
@api.route('/alert_alarm_definition/<string:id>')
def get_alert_alarm_def(id):
    alert_alarm_def = SystemEventDefinition.query.filter_by(id=id).first_or_404()
    return jsonify(alert_alarm_def.to_json())

# todo - test case
@api.route('/delete_alert_alarm_definition/<int:id>', methods=['DELETE'])
#@auth.login_required
#@scope_required('user_admin')
def delete_alert_alarm_definition(id):
    """
    Delete SystemEventDefinition for alert or alarm; this also removes associated alertfilter in uframe.
    """
    alert_alarm_def = SystemEventDefinition.query.get(id)
    if alert_alarm_def is None:
        return jsonify(error="alert_alarm_definition Not Found"), 404
    result = delete_alertfilter(alert_alarm_def.uframe_filter_id)
    if result is None:
        message = 'Failed to delete uframe alertfilter (id: %d) ' %  alert_alarm_def.uframe_filter_id
        #print '\n message: ', message
        return jsonify(error=message), 409
    db.session.delete(alert_alarm_def)
    db.session.commit()
    return jsonify(), 200

#Create a new alert/alarm definition
@api.route('/alert_alarm_definition', methods=['POST'])
# @auth.login_required
# @scope_required('annotate')
def create_alert_alarm_def():
    try:
        data = json.loads(request.data)
        create_definition_has_required_fields(data)

        # Persist alert_alarm_def in uframe using POST
        uframe_filter_id = create_uframe_alertfilter(data)
        if uframe_filter_id is None:
            raise Exception('Failed to create alertfilter in uframe.')

        # Persist alert_alarm_def in ooi-ui-services db
        alert_alarm_def = SystemEventDefinition()
        alert_alarm_def.uframe_filter_id = uframe_filter_id # Returned from POST to uFrame
        alert_alarm_def.reference_designator = data['reference_designator'] # Instrument reference designator
        alert_alarm_def.array_name = data['array_name']  # Array reference designator
        alert_alarm_def.platform_name = data['platform_name']  # Platform reference designator
        alert_alarm_def.instrument_name = data['instrument_name']  # Instrument reference designator
        alert_alarm_def.instrument_parameter = data['instrument_parameter']
        alert_alarm_def.instrument_parameter_pdid = data['instrument_parameter_pdid']
        alert_alarm_def.operator = data['operator']
        alert_alarm_def.created_time = datetime.now()
        alert_alarm_def.event_type = data['event_type']
        alert_alarm_def.active = data['active']
        alert_alarm_def.description = data['description']
        alert_alarm_def.high_value = data['high_value']
        alert_alarm_def.low_value = data['low_value']
        alert_alarm_def.severity = data['severity']
        alert_alarm_def.stream = data['stream']
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
            db.session.flush()
        except:
            # Rollback alert_alarm_def and delete alertfilter from uframe. todo - test case
            db.session.rollback()
            result = delete_alertfilter(uframe_filter_id)
            message = 'IntegrityError creating alert_alarm_definition'
            if result is None:
                message += '; failed to rollback uframe alertfilter (id: %d) ' %  uframe_filter_id
            #print '\n create_alert_alarm_def exception message: ', message
            return bad_request(message)

        return jsonify(alert_alarm_def.to_json()), 201

    except Exception as err:
        #print '\n debug: exception message: ', err.message
        return conflict('Insufficient data, or bad data format.')


@api.route('/alert_alarm_definition/<int:id>', methods=['PUT'])
# @auth.login_required
# @scope_required('annotate')
def update_alert_alarm_def(id):
    """
    Update an alert/alarm definition.
    """
    try:
        # Process request.data; verify required fields provided for update.
        data = json.loads(request.data)

        # Check all required fields for update have been provided.
        create_definition_has_required_fields(data)
        if 'uframe_filter_id' not in data:
            raise Exception('uframe_filter_id not in alertfilter update request.data')

        # Persist alert_alarm_def in uframe using POST; retain original definition for rollback
        uframe_filter_id = data['uframe_filter_id']
        original_uframe_definition = get_alertfilter(uframe_filter_id)
        update_uframe_alertfilter(data, uframe_filter_id)

        # Persist alert_alarm_def in ooi-ui-services database
        alert_alarm_def = SystemEventDefinition.query.filter_by(id=id).first()
        if not alert_alarm_def:
            return jsonify(error="Invalid ID, record not found"), 404
        alert_alarm_def.uframe_filter_id = uframe_filter_id # Returned from POST to uFrame
        alert_alarm_def.reference_designator = data['reference_designator'] # Instrument reference designator
        alert_alarm_def.array_name = data['array_name']  # Array reference designator
        alert_alarm_def.platform_name = data['platform_name']  # Platform reference designator
        alert_alarm_def.instrument_name = data['instrument_name']  # Instrument reference designator
        alert_alarm_def.instrument_parameter = data['instrument_parameter']
        alert_alarm_def.instrument_parameter_pdid = data['instrument_parameter_pdid']
        alert_alarm_def.operator = data['operator']
        # alert_alarm_def.created_time = datetime.now()
        alert_alarm_def.event_type = data['event_type']
        alert_alarm_def.active = data['active']
        alert_alarm_def.description = data['description']
        alert_alarm_def.high_value = data['high_value']
        alert_alarm_def.low_value = data['low_value']
        alert_alarm_def.severity = data['severity']
        alert_alarm_def.stream = data['stream']
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
        except:
            # Rollback updates made to uframe alertfilter; Restore original alertfilter in uframe. todo - test case
            db.session.rollback()
            result = update_uframe_alertfilter(uframe_filter_id, original_uframe_definition)
            message = 'IntegrityError updating update_alert_alarm_def'
            if result is None:
                message += '; failed to delete uframe alertfilter (id: %d) ' %  uframe_filter_id
            #print '\n update db exception message: ', message
            return bad_request(message)

        return jsonify(alert_alarm_def.to_json()), 201
    except Exception as err:
        #print '\n update alertalarm definition exception: ', err.message
        return conflict('Insufficient data, or bad data format.')

def create_definition_has_required_fields(data):
    """
    Verify SystemEventDefinition creation has required fields in request.data. Error otherwise.
    SystemEventDefinition update can re-use this method but must also check for uframe_filter_id.
    Review what to do with create_time on update SystemEventDefinition.
    Verify operator value is one of valid uframe operators.
    """
    try:
        required_fields = ['active', 'array_name', 'description', 'event_type', 'high_value',
                           'instrument_name', 'instrument_parameter', 'instrument_parameter_pdid', 'low_value',
                           'operator',  'platform_name', 'reference_designator', 'severity',  'stream']
                           # not created_time, id, 'uframe_filter_id'
        valid_operators = ['GREATER', 'LESS', 'BETWEEN_EXCLUSIVE', 'OUTSIDE_EXCLUSIVE']

        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%s) in request.data' % field
                #print '\n message: ', message
                raise Exception(message)

        # todo - add negative test case with invalid operator
        if data['operator'] not in valid_operators:
            message = 'Invalid operator value provided (%s).' % data['operator']
            #print '\n message: ', message
            raise Exception(message)
        return
    except:
        raise

def create_has_required_fields(data):
    """
    Verify SystemEvent creation has required fields in request.data. Error otherwise.
    """
    try:
        required_fields = ['uframe_event_id', 'uframe_filter_id', 'system_event_definition_id',
                           'event_time', 'event_type', 'event_response', 'method', 'deployment']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%s) in request.data' % field
                #print '\n message: ', message
                raise Exception(message)
        return
    except:
        raise

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Methods for uframe integration
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_uframe_alertfilter(request_data):
    """
    Create alertfilter in uframe. Return uframe alertfilter id, None or raise Exception.
    Process:
        Create uframe data dictionary from request.data;
        Create alertfilter in uframe using uframe data dictionary created
        Return uframe alertfilter id, None or exception.
    """
    result = None
    successful_response = 'CREATED'
    try:
        # Create uframe data dictionary from request.data
        uframe_data = create_uframe_alertfilter_data(request_data)
        if uframe_data is None:
            raise Exception('Failed to create alertfilter dictionary for uframe.')

        # Create alertfilter in uframe
        response = uframe_create_alertfilter(uframe_data)
        if response.status_code !=201:
            message = '(%s) Failed to execute create_uframe_alertfilter.' % str(response.status_code)
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)

        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')

            # Evaluate response content for error or alertfilter id
            # Sample: {"message" : "Record created successfully", "id" : 2, "statusCode" : "CREATED" }
            if response_data:
                if 'statusCode' in response_data:
                    if response_data['statusCode'] == successful_response:
                        result = response_data['id']
        return result

    except Exception as err:
        #print '\n Message -- ', err.message
        raise

def update_uframe_alertfilter(request_data, id):
    """
    Update alertfilter in uframe. Return if successful, Exception if error.
    Process:
        Create uframe data dictionary from request.data;
        Update alertfilter in uframe using uframe data dictionary created
        Return uframe alertfilter id, None or exception.
    """
    successful_response = 'OK'
    try:
        # Create uframe data dictionary from request.data
        uframe_data = create_uframe_alertfilter_data(request_data)
        if uframe_data is None:
            raise Exception('Unable to update alertfilter data for uframe.')

        # Update alertfilter in uframe
        response = uframe_update_alertfilter(uframe_data, id)
        if response.status_code !=200:
            message = '(%s) Failed to execute update_uframe_alertfilter (id: %d).' % (str(response.status_code), id)
            if response.content:
                message = '(%s) %s' % (str(response.status_code), str(response.content))
            raise Exception(message)

        if response.content:
            try:
                response_data = json.loads(response.content)
            except:
                raise Exception('Malformed data; not in valid json format.')

            # Evaluate response content for error or alertfilter id
            if response_data:
                if 'statusCode' in response_data:
                    if response_data['statusCode'] != successful_response:
                        raise Exception('Failed to update uframe alertfilter (id: %d).' % id)
        else:
            raise Exception('uframe failed on update of alertfilter (id: %d).' % id)

        return

    except Exception as err:
        #print '\n Exception - Message: ', err.message
        raise

def delete_alertfilter(id):
    """
    Delete alertfilter in uframe. On error return None, else return id.
    Sample uframe response dictionary for delete:
        {u'message': u'Delete successful.', u'id': 204, u'statusCode': u'OK'}
    """
    successful_response = 'OK'
    result = None
    try:
        #headers = get_api_headers('admin', 'test')
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters', str(id)])
        response = requests.delete(url, timeout=(timeout, timeout_read)) # , headers=headers)
        if response.status_code != 200:
            raise Exception('(%r) Failed to execute alertfilter deletion (id: %d)' % (response.status_code, id))
        uframe_data = json.loads(response.content)
        if uframe_data is None:
            raise Exception('Failed to execute alertfilter deletion (id: %d)' % id)
        if 'statusCode' not in uframe_data:
            raise Exception('uframe returned malformed response for alertfilter deletion (id: %d)' % id)
        if 'id' not in uframe_data:
            raise Exception('uframe returned malformed response for alertfilter deletion (id: %d)' % id)
        if uframe_data['statusCode'] != successful_response:
            raise Exception('uframe failed to delete alertfilter (id: %d); statusCode: %r ' % (id, uframe_data['statusCode']) )

        result = uframe_data['id']
        return result

    except Exception as err:
        #print '\n delete_alertfilter exception: ', err.message
        return result

def get_alertfilter(id):
    """
    Get alertfilter in uframe. On error return None, else return id.
    Sample uframe response dictionary - see sample in create_uframe_alertfilter_data method.
    """
    result = None
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters', str(id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        alertfilter = json.loads(response.content)
        if alertfilter is None:
            raise Exception('Failed to get alertfilter (id: %d)' % id)
        result = alertfilter
        return result
    except Exception as err:
        #print '\n get alertfilter exception: ', err.message
        return result

def create_uframe_alertfilter_data(data):
    """ Create alertfilter dictionary for uframe processing.

    Sample of uframe alertfilter input to create and update:
    {
        "@class":"com.raytheon.uf.common.ooi.dataplugin.alert.alertfilter.AlertFilterRecord",
        "pdId":"PD180",
        "enabled":true,
        "stream":"ctdpf_optode_calibration_coefficients",
        "referenceDesignator":{
            "node":"SP017","full":true,"subsite":"CE01ISSP","sensor":"01-CTDPFJ123"
        },
        "alertMetadata":{
            "severity" : 2,"description":"Rule 42"},
        "alertRule":{
            "filter":"GREATER","valid":true,"highVal":31.0,"lowVal":12.0,"errMessage":null
        }
    }
    """
    try:
        # Verify required fields to create alert alarm are present in data dictionary.
        create_definition_has_required_fields(data)
        instrument_parameter_pdid = data['instrument_parameter_pdid']
        stream = data['stream']
        reference_designator = data['reference_designator']
        severity = data['severity']
        description = data['description']
        high_value = data['high_value']
        low_value = data['low_value']
        if reference_designator is None or len(reference_designator) != 27:
            raise Exception('reference_designator is None or malformed. ')
        if high_value is None and low_value is None:
            raise Exception('Parameters high_value and low_value are both None.')
        if reference_designator is None:
            raise Exception('Required parameter (reference_designator) is None.')
        else:
            subsite = reference_designator[0:8]
            node = reference_designator[9:14]
            sensor = reference_designator[15:27]

        # uframe will fail if None is provided for description  todo check similar problem with other fields!
        if description is None:
            description = ''
        uframe_data = {}
        uframe_data['@class'] = 'com.raytheon.uf.common.ooi.dataplugin.alert.alertfilter.AlertFilterRecord'
        uframe_data['enabled'] = True
        uframe_data['pdId'] = instrument_parameter_pdid
        uframe_data['stream'] = stream
        uframe_data['referenceDesignator'] = {}
        uframe_data['referenceDesignator']['subsite'] = subsite
        uframe_data['referenceDesignator']['node'] = node
        uframe_data['referenceDesignator']['sensor'] = sensor
        uframe_data['referenceDesignator']['full'] = True
        uframe_data['alertMetadata'] = {}
        uframe_data['alertMetadata']['severity'] = severity
        uframe_data['alertMetadata']['description'] = description
        uframe_data['alertRule'] = {}
        uframe_data['alertRule']['filter'] = data['operator']
        uframe_data['alertRule']['valid'] = True
        uframe_data['alertRule']['highVal'] = float(high_value)
        uframe_data['alertRule']['lowVal'] = float(low_value)
        uframe_data['alertRule']['errMessage'] = None
    except Exception as err:
        #print '\n Exception Message: ', err.message
        raise

    return uframe_data

def get_uframe_info():
    """ Get uframe alertalarm configuration information. (port 12577) """
    uframe_url = current_app.config['UFRAME_ALERTS_URL']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read

def get_api_headers(username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

def _headers():
    """ Headers for uframe PUT and POST. """
    return {"Content-Type": "application/json"}

def uframe_create_alertfilter(uframe_data):
    """ Create alertfilter in uframe. """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters'])
        data = json.dumps(uframe_data)
        response = requests.post(url, timeout=(timeout, timeout_read), headers=_headers(), data=data)
        return response
    except:
        raise

def uframe_update_alertfilter(uframe_data, alertfilter_id):
    """ Update alertfilter in uframe. """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, 'alertfilters', str(alertfilter_id)])
        data = json.dumps(uframe_data)
        response = requests.put(url, timeout=(timeout, timeout_read), headers=_headers(), data=data)
        return response
    except:
        raise
