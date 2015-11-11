#!/usr/bin/env python
"""
Alerts & Alarms Endpoints

"""
__author__ = 'James Case'

from flask import (jsonify, request, current_app, g)
from ooiservices.app import db
from ooiservices.app.main import api
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import (conflict, bad_request)
from ooiservices.app.main.notifications import handle_notifications
from ooiservices.app.models import (SystemEventDefinition, SystemEvent, UserEventNotification, User)
from ooiservices.app.uframe.assets import get_assets
from sqlalchemy import desc

import requests
import json
import datetime as dt
import calendar


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts & Alarms
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#List all alerts and alarms
@api.route('/alert_alarm', methods=['GET'])
def get_alerts_alarms():
    """ Get all alert(s) and alarm(s) which match filter rules provided in request.args.
    Dynamically construct filters to query SystemEvent and SystemEventDefinitions.
    List output for each alert_alarm which includes system_event_definition content based request.args 'filters'.
    """
    try:
        result = get_alerts_alarms_object()                
        return jsonify( {'alert_alarm': result})
    except Exception as err:
        message = 'Insufficient data, or bad data format. (%s)' % str(err.message)
        return conflict(message)


def get_alerts_alarms_object():
    """ helper function to get alert alarms
    """
    result = []
    # Get query filters, query SystemEvents using event_filters
    event_filters, definition_filters = get_query_filters(request.args)
    if event_filters is None:   # alerts_alarms
        alerts_alarms = db.session.query(SystemEvent).all()
    else:
        alerts_alarms = db.session.query(SystemEvent).filter_by(**event_filters)
    # Process alert_alarm json output based on definition filters
    if alerts_alarms is not None:
        result_json = get_alert_alarm_json(alerts_alarms, definition_filters)
        if result_json is None:
            result = []
        else:
            result = result_json
    return result

#List an alert or alarm by id
@api.route('/alert_alarm/<int:id>')
def get_alert_alarm(id):
    alert_alarm = SystemEvent.query.filter_by(id=id).first()
    if alert_alarm is None:
        message = 'alert_alarm not found.'
        return bad_request(message)
    return jsonify(alert_alarm.to_json())


def get_asset_list():   
    data = get_assets(True, True)
    ref_list = []
    name_list = []
    for d in data:
        split_ref = d['ref_des'].split('-')
        if d['ref_des'] not in name_list and len(split_ref) > 1:
            ref_list.append(d)
            name_list.append(d['ref_des'])
    return ref_list, name_list

@api.route('/alert_alarm/status', methods=['GET'])
def get_alert_alarm_status():
    """ Gets the alert alarm status for all available assets.
    """
    #the actual alert alarms
    data = get_alerts_alarms_object()      
    status_info = []
    status_outline = {}

    for d in data:        
        if d["acknowledged"] == False:
            ref_des = d['alert_alarm_definition']['reference_designator']
            if ref_des not in status_outline:
                status_outline[ref_des] = d
                status_outline[ref_des]['count'] = 0
            else:
                count = status_outline[ref_des]['count']                
                #figure out which one is higher
                if d["event_type"] == "alarm":
                    status_outline[ref_des] = d
                else:
                    pass
                status_outline[ref_des]['count'] = count+1

    #get dict of assets available
    assets_dict, assets_names = get_asset_list()

    #get the list of alert/alarm definitions
    aa_def = get_alerts_alarms_def_object()    
    aa_def_list = []

    #alerts and alarms

    for aa_item in aa_def:        
        if 'reference_designator' in aa_item:
            #get the A/A definitions
            if aa_item['reference_designator'] not in aa_def_list:
                #used to identify halth sensors            
                aa_def_list.append(aa_item['reference_designator'])
            if aa_item['reference_designator'] not in assets_names:
                #means an asset was in the A/A definition, that was not in the asset list returned  
                #create and add it so we can see the status, the TOC may not reflect this          
                print "Ref-Des not in asset name list: ERROR: appending", aa_item['reference_designator']            

                new_asset = {'ref_des':aa_item['reference_designator'],
                             'hasDeploymentEvent' : True,
                             'coordinates': [0, 0],
                             'assetInfo': {"type":"Sensor",
                                           "longName":aa_item['reference_designator'],
                                           "instrumentClass": "Sensor",
                                           "name":aa_item['reference_designator'],
                                           "owner":"N/A",
                                           "description":"N/A"
                              },                             
                            }            

                #append the dict to
                assets_dict.append(new_asset)
                aa_def.append(new_asset)

                aa_def_list.append(aa_item['reference_designator'])
                assets_names.append(aa_item['reference_designator'])


    #use all the info to create status
    for asset in assets_dict:
        d = asset['ref_des']

        if 'hasDeploymentEvent' in asset and asset['hasDeploymentEvent']:
            #create inital entry   
            if 'manufactureInfo' in asset:
                entry = {'reference_designator':d, "count":0,
                        "event_type":'unknown', 
                        'coordinates':asset['coordinates'],
                        'asset_type':asset['assetInfo']['type'],
                        'longName':asset['assetInfo']['longName'],
                        'name':asset['assetInfo']['name'],
                        'instrumentClass':asset['assetInfo']['instrumentClass'],
                        'manufacturer': asset['manufactureInfo']['manufacturer'],
                        'modelNumber': asset['manufactureInfo']['modelNumber'],
                        'serialNumber': asset['manufactureInfo']['serialNumber'],
                        'owner': asset['assetInfo']['owner'],
                        'description': asset['assetInfo']['description']}
            else:
                entry = {'reference_designator':d, "count":0,
                        "event_type":'unknown', 
                        'coordinates':asset['coordinates'],
                        'asset_type':asset['assetInfo']['type'],
                        'longName':asset['assetInfo']['longName'],
                        'name':asset['assetInfo']['name'],
                        'instrumentClass':asset['assetInfo']['instrumentClass'],
                        'manufacturer': 'N/A',
                        'modelNumber': 'N/A',
                        'serialNumber': 'N/A',
                        'owner': asset['assetInfo']['owner'],
                        'description': asset['assetInfo']['description']}
              
            
            #use alert alarms status (alarm or alert)
            if d in status_outline.keys():
                entry["count"] = status_outline[d]['count']
                entry["event_type"] = status_outline[d]["event_type"]
            #healthly 
            elif d in aa_def_list:
                #used to identify health sensors
                entry["event_type"] = 'inactive'
            #no status, unknown
            else:
                #nothing to do here
                pass

            status_info.append(entry)
    return jsonify({'alert_alarm':status_info})


#Create a new alert/alarm
@api.route('/alert_alarm', methods=['POST'])
@auth.login_required
@scope_required(u'user_admin')
@scope_required(u'redmine')
def create_alert_alarm():
    """ Create an alert or an alarm; invoked when processing alerts and alarms from uframe.
    Note: offset from start of unix epoch (jan 1, 1900 at midnight 00:00) to 00:00 1 Jan 1970 GMT, in secs = 2208988800
    """
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
                message = 'Failed to retrieve SystemEventDefinition for uframe_filter_id: %d' % uframe_filter_id
                raise Exception(message)
            system_event_definition_id = system_event_definition.id

        except Exception as err:
            # This is a severe error, should be logged (failure to record instance of alert or alarm from uframe)
            message = 'Unable to retrieve system_event_definition using uframe_filter_id; %s ' % str(err.message)
            current_app.logger.info(message)
            raise  Exception(err.message)

        # If the system_event_definition is not active, do not create alert_alarm instance
        if not system_event_definition.active:
            message = 'Failed to create alert_alarm; system_event_definition (id:%d) is not active.' % \
                      system_event_definition.id
            raise Exception(message)
        # If the system_event_definition is retired, do not create alert_alarm instance
        if system_event_definition.retired is not None:
            if system_event_definition.retired:
                message = 'Failed to create alert_alarm - system_event_definition is retired. (%d)' % \
                          system_event_definition.id
                raise Exception(message)

        # Determine if uframe_filter_id provided matches system_event_definition.uframe_filter_id, if not error (409)

        # Create SystemEvent
        alert_alarm = SystemEvent()
        alert_alarm.uframe_event_id = uframe_event_id
        alert_alarm.uframe_filter_id = uframe_filter_id
        alert_alarm.system_event_definition_id = system_event_definition_id
        offset = 2208988800
        uframe_float = data['event_time']
        ts_event_time = convert_from_utc(uframe_float - offset)
        alert_alarm.event_time = dt.datetime.strftime(ts_event_time, "%Y-%m-%dT%H:%M:%S")
        alert_alarm.event_type = data['event_type']
        alert_alarm.event_response = data['event_response']
        alert_alarm.method = data['method']
        alert_alarm.deployment = data['deployment']
        alert_alarm.acknowledged = False
        alert_alarm.ack_by = None
        alert_alarm.ts_acknowledged = None
        alert_alarm.timestamp = dt.datetime.now()       # when this alert or alarm is received and persisted
        try:
            db.session.add(alert_alarm)
            db.session.commit()
            db.session.flush()
        except Exception as err:
            message = 'IntegrityError creating alert_alarm; %s' % str(err.message)
            current_app.logger.info(message)
            db.session.rollback()
            return bad_request('IntegrityError creating alert_alarm.')

        # Perform notification processes as required
        handle_notifications(alert_alarm.id)

        return jsonify(alert_alarm.to_json()), 201
    except Exception as err:
        message = 'Insufficient data, or bad data format. %s' % err.message
        current_app.logger.info(message)
        return conflict(message)


# Acknowledge alert/alarm
@api.route('/ack_alert_alarm', methods=['POST','PUT'])
@auth.login_required
@scope_required(u'user_admin')
@scope_required(u'redmine')
def acknowledge_alert_alarm():
    """ Acknowledge an alert or an alarm.
    """
    try:
        # Process request.data; verify required fields are present
        data = json.loads(request.data)
        acknowledge_has_required_fields(data)

        # Determine if alert_alarm to be acknowledged is same as reflected in request data
        alert_alarm = is_valid_alert_alarm_for_ack(data)

        # Get alert_alarm_definition.
        #alert_alarm_definition = SystemEventDefinition.query.get(alert_alarm.system_event_definition_id)

        # Acknowledge alert/alarm in uframe. acknowledgedBy is str(user_id)
        ack_value = None
        ack_by = data['ack_by']
        ack_id = alert_alarm.uframe_event_id
        if ack_by is not None or not ack_by:
            ack_value = ack_by

        if ack_value is None:
            message = 'Required value ack_by is empty or None.'
            return bad_request(message)

        # Only alarms go through the acknowledge process with uframe (i.e. uframe only stores alarms)
        if alert_alarm.event_type == 'alarm':
            if not (uframe_acknowledge_alert_alarm(ack_id, ack_value)):
                message = 'Failed to acknowledge alarm (id:%d) in uframe.' % alert_alarm.id
                current_app.logger.info('[acknowledge_alert_alarm] %s ' % message)
                return bad_request(message)

        # Update alert_alarm acknowledged, ack_by and ts_acknowledged
        alert_alarm.acknowledged = True
        alert_alarm.ack_by = ack_by
        alert_alarm.ts_acknowledged = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        try:
            db.session.add(alert_alarm)
            db.session.commit()
        except:
            db.session.rollback()
            return bad_request('IntegrityError acknowledging alert_alarm')
        return jsonify(alert_alarm.to_json()), 201
    except Exception as err:
        message = 'Insufficient data, or bad data format; %s' % err.message
        current_app.logger.info('[acknowledge_alert_alarm] %s ' % message)
        return conflict(message)


def is_valid_alert_alarm_for_ack(data):
    """ Validate this is the alert alarm to be acknowledged.
    """
    try:
        definition_id = data['system_event_definition_id']
        definition = SystemEventDefinition.query.get(definition_id)
        if definition is None:
            message = 'Acknowledge failed to retrieve SystemEventDefinition (id: %d)' % definition_id
            current_app.logger.info('[is_valid_alert_alarm_for_ack] %s ' % message)
            raise Exception(message)

        user_event_notification = UserEventNotification.query.filter_by(system_event_definition_id=definition_id).first()
        if user_event_notification is None:
            message = 'Acknowledge failed to retrieve UserEventNotification for definition (id: %d)' % definition_id
            current_app.logger.info('[is_valid_alert_alarm_for_ack] %s ' % message)
            raise Exception(message)

        # Variables for sanity tests
        uframe_filter_id = data['uframe_filter_id']
        uframe_event_id = data['uframe_event_id']
        event_type = data['event_type']

        # Sanity test variables alert_alarm data against definition
        if definition.uframe_filter_id != uframe_filter_id:
            message = 'Acknowledge failed to match alert_alarm uframe_filter_id with SystemEventDefinition (id: %d)' % \
                      definition_id
            current_app.logger.info('[is_valid_alert_alarm_for_ack] %s ' % message)
            raise Exception(message)
        if definition.event_type != event_type:
            message = 'Acknowledge failed to match alert_alarm event_type with SystemEventDefinition (id: %d)' % \
                      definition_id
            current_app.logger.info('[is_valid_alert_alarm_for_ack] %s ' % message)
            raise Exception(message)

        # Sanity test existing alert_alarm; first get alert_alarm to be acknowledged, verify variables for consistency
        id = data['id']
        alert_alarm = SystemEvent.query.get(id)
        if alert_alarm is None:
            message = 'Acknowledge failed to retrieve SystemEvent (id: %d)' % id
            current_app.logger.info('[is_valid_alert_alarm_for_ack] %s ' % message)
            raise Exception(message)
        if alert_alarm.uframe_event_id != uframe_event_id:
            message = 'Acknowledge failed to match alert_alarm uframe_event_id  (id: %d)' % id
            current_app.logger.info('[is_valid_alert_alarm_for_ack] %s ' % message)
            raise Exception(message)
        return alert_alarm
    except:
        raise


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts & Alarms Definitions
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#List all alert and alarm definitions
@api.route('/alert_alarm_definition', methods=['GET'])
def get_alerts_alarms_def():
    """ Get a list of alert or alarm definition(s).
    """
    try:
        result = get_alerts_alarms_def_object()
        return jsonify( {'alert_alarm_definition': result})
    except Exception as err:
        return bad_request(err.message)


def get_alerts_alarms_def_object():
    try:
        result = []
        query_filter = get_definitions_query_filter(request.args)
        if query_filter is None:
            alerts_alarms_defs = SystemEventDefinition.query.filter_by(retired=False)
        else:
            alerts_alarms_defs = db.session.query(SystemEventDefinition).filter_by(**query_filter)
        if alerts_alarms_defs is not None:
            for definition in alerts_alarms_defs:
                tmp = get_alert_alarm_definition(definition.id)
                result.append(tmp)
        return result
    except:
        raise

#List an alerts and alarms definition by id
@api.route('/alert_alarm_definition/<int:id>')
def get_alert_alarm_def(id):
    """ Get an alert or alarm definition by id.
    """
    try:
        result = get_alert_alarm_definition(id)
        return jsonify(result)
    except Exception as err:
        return bad_request(err.message)


#Create a new alert/alarm definition
@api.route('/alert_alarm_definition', methods=['POST'])
@auth.login_required
@scope_required(u'user_admin')
def create_alert_alarm_def():
    """ Create an alert or alarm definition, including the the user_event_notification record.

    The create_alert_alarm_def method requires parameters for user_event_notification also. The
    user_event_notification is created immediately after the alert_alarm_definition.
    """
    try:
        # Process request.data; verify required fields provided for create, including user_event_notification
        data = json.loads(request.data)
        create_definition_has_required_fields(data)
        user_event_notification_has_required_fields(data)

        tmp = data['stream']
        data['stream'] = tmp.replace('-','_')

        # Persist alert_alarm_def in uframe using POST
        uframe_filter_id = create_uframe_alertfilter(data)
        if uframe_filter_id is None:
            message = 'Failed to create alertfilter in uframe.'
            raise Exception(message)

        # Persist alert_alarm_def in ooi-ui-services db
        alert_alarm_def = SystemEventDefinition()
        alert_alarm_def.active = data['active']
        alert_alarm_def.array_name = data['array_name']  # Array reference designator
        alert_alarm_def.description = data['description']
        alert_alarm_def.event_type = data['event_type']
        alert_alarm_def.high_value = data['high_value']
        alert_alarm_def.instrument_name = data['instrument_name']  # Instrument reference designator
        alert_alarm_def.instrument_parameter = data['instrument_parameter']
        alert_alarm_def.instrument_parameter_pdid = data['instrument_parameter_pdid']
        alert_alarm_def.low_value = data['low_value']
        alert_alarm_def.operator = data['operator']
        alert_alarm_def.platform_name = data['platform_name']  # Platform reference designator
        alert_alarm_def.reference_designator = data['reference_designator'] # Instrument reference designator
        alert_alarm_def.severity = data['severity']
        alert_alarm_def.stream = data['stream']
        alert_alarm_def.escalate_on = 0.0
        alert_alarm_def.escalate_boundary = 0.0
        if alert_alarm_def.event_type == 'alert':
            alert_alarm_def.escalate_on = float(data['escalate_on'])
            alert_alarm_def.escalate_boundary = float(data['escalate_boundary'])
        alert_alarm_def.created_time = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
        alert_alarm_def.uframe_filter_id = uframe_filter_id # Returned from POST to uFrame
        alert_alarm_def.ts_retired = None
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
        except:
            # Rollback alert_alarm_def and delete alertfilter from uframe.
            message = 'IntegrityError creating alert_alarm_definition'
            db.session.rollback()
            result = delete_alertfilter(uframe_filter_id)
            if result is None:
                message += '; failed to rollback create uframe alertfilter (id: %d) ' %  uframe_filter_id
            return bad_request(message)

        try:
            # Create corresponding UserEventNotification when alert or alarm definition is created
            system_event_definition_id = alert_alarm_def.id
            user_id = data['user_id']
            use_email = data['use_email']
            use_redmine = data['use_redmine']
            use_phone = data['use_phone']
            use_log = data['use_log']
            use_sms = data['use_sms']
            new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=system_event_definition_id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
        except:
            # Error creating user_event_notification, rollback: delete system_event_definition and uframe alertfilter
            message = 'IntegrityError creating alert_alarm_definition (failed to insert_user_event_notification).'
            try:
                db.session.delete(alert_alarm_def)
                db.session.commit()
            except:
                message += ' Failed to rollback system_event_definition (%d)' % alert_alarm_def.id
            result = delete_alertfilter(uframe_filter_id)
            if result is None:
                message += '; failed to rollback uframe alertfilter (id: %d) ' %  uframe_filter_id
            return conflict(message)

        return jsonify(alert_alarm_def.to_json()), 201
    except Exception as err:
        message = 'Insufficient data, or bad data format. (%s)' % str(err.message)
        return conflict(message)


@api.route('/alert_alarm_definition/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required(u'user_admin')
def update_alert_alarm_def(id):
    """Update an alert or an alarm definition. Optional update of associated user_event_notification available.

    update_alert_alarm_def only requires request.data for alert_alarm_def; no parameters for user_event_notification
    are required. If 'update_user_event_notification' (not empty) in the request.data, then
    the user_event_notification will be updated within this method; in this case, all user_event_notification
    fields must also be provided in the request.data.
    """
    try:
        # Verify SystemEventDefinition with this id exists
        alert_alarm_def = SystemEventDefinition.query.get(id)
        if alert_alarm_def is None:
            message = "Invalid ID, alert_alarm_definition record not found"
            return bad_request(message)
        original_alert_alarm_def = alert_alarm_def

        # Process request.data; verify required fields provided for update.
        data = json.loads(request.data)
        create_definition_has_required_fields(data)
        if 'uframe_filter_id' not in data:
            message = 'uframe_filter_id not in alertfilter update request.data'
            raise Exception(message)

        tmp = data['stream']
        data['stream'] = tmp.replace('-','_')

        #user_event_notification = None
        user_event_notification_id = None
        update_user_event_notification = False
        if 'update_user_event_notification' in data:
            update_user_event_notification = data['update_user_event_notification']
            if update_user_event_notification:
                user_event_notification_has_required_fields(data)
                user_event_notification = UserEventNotification.query.filter_by(system_event_definition_id=id).first()
                if user_event_notification is None:
                    message = 'Invalid ID, user_event_notification record not found for requested update.'
                    return bad_request(message)
                user_event_notification_id = user_event_notification.id

        # Persist alert_alarm_def in uframe using POST; retain original definition for rollback
        uframe_filter_id = data['uframe_filter_id']
        original_uframe_definition = get_alertfilter(uframe_filter_id)
        if original_uframe_definition is None:
            message = 'Invalid uframe_filter_id (%r) provided in request data.' % (uframe_filter_id)
            return bad_request(message)
        update_uframe_alertfilter(data, uframe_filter_id)

        # Persist alert_alarm_def in ooi-ui-services database
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
        alert_alarm_def.escalate_on = data['escalate_on']
        alert_alarm_def.escalate_boundary = data['escalate_boundary']
        try:
            db.session.add(alert_alarm_def)
            db.session.commit()
        except:
            # Restore original alertfilter in uframe and original_alert_alarm_def_
            db.session.add(original_alert_alarm_def)
            db.session.commit()
            result = update_uframe_alertfilter(uframe_filter_id, original_uframe_definition)
            message = 'IntegrityError update_alert_alarm_def'
            if result is None:
                message += '; failed to rollback updates to uframe alertfilter (id: %d) ' %  uframe_filter_id
            return bad_request(message)
        # If user has provided 'update_user_event_notification' for the user_event_notification, perform update.
        if update_user_event_notification:
            try:
                # Update corresponding UserEventNotification for when alert or alarm instance
                sys_event_definition_id = alert_alarm_def.id
                user_id = data['user_id']
                use_email = data['use_email']
                use_redmine = data['use_redmine']
                use_phone = data['use_phone']
                use_log = data['use_log']
                use_sms = data['use_sms']
                UserEventNotification.update_user_event_notification(id=user_event_notification_id,
                                                                     system_event_definition_id=sys_event_definition_id,
                                                                     user_id=user_id,
                                                                     use_email=use_email,
                                                                     use_redmine=use_redmine,
                                                                     use_phone=use_phone,
                                                                     use_log=use_log,
                                                                     use_sms=use_sms)
            except:
                # Error updating user_event_notification, rollback: updates to system_event_definition and
                # updates to uframe alertfilter
                message = 'IntegrityError update_alert_alarm_def; failed to update_user_event_notification.'
                result = update_uframe_alertfilter(original_alert_alarm_def.to_json(), uframe_filter_id)
                if result is None:
                    message += '; failed to rollback updates to uframe alertfilter (id: %d) ' %  uframe_filter_id
                return conflict(message)

        return jsonify(alert_alarm_def.to_json()), 201
    except Exception as err:
        message = str(err.message)
        return conflict(message)


@api.route('/delete_alert_alarm_definition/<int:id>', methods=['DELETE'])
@auth.login_required
@scope_required(u'user_admin')
def delete_alert_alarm_definition(id):
    """ Delete SystemEventDefinition for alert or alarm; this retires SystemEventDefinition (no deletion).
    """
    # Get alert_alarm_definition
    alert_alarm_def = SystemEventDefinition.query.get(id)
    if alert_alarm_def is None:
        message = 'alert_alarm_definition not found.'
        return bad_request(message)
    # If alert_alarm_definition already retired, just return
    if alert_alarm_def.retired is not None:
        if alert_alarm_def.retired == True:
            return jsonify(), 200

    # Determine if definition id is used by any alert or alarm instances where acknowledged is False)
    active_alerts_alarms = SystemEvent.query.filter_by(system_event_definition_id=id, acknowledged=False).first()
    if active_alerts_alarms is not None:
        # There are existing alert_alarm instances using this id which have not been acknowledged
        message = 'There are existing %s instance(s) using this definition id (%d) not yet acknowledged.' \
                  % (alert_alarm_def.event_type, id)
        return bad_request(message)
    alert_alarm_def.retired = True
    alert_alarm_def.ts_retired = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
    try:
        db.session.add(alert_alarm_def)
        db.session.commit()
    except:
        db.session.rollback()
        message = 'IntegrityError deleting alert_alarm_definition'
        return bad_request(message)
    return jsonify(), 200


@api.route('/ok_to_delete_alert_alarm_definition/<int:id>', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def ok_to_delete_alert_alarm_definition(id):
    """ Determine if an alert_alarm_definition can be deleted (retired). Response format:  { "status": false | true }
    """
    if safe_to_delete_alert_alarm_definition(id):
        return jsonify(status=True), 200
    else:
        return jsonify(status=False), 200


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Private Methods for routes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_alert_alarm_definition(id):
    """ Get alert or alarm definition with user_event_notification; return json.
    """
    try:
        alert_alarm_def = SystemEventDefinition.query.filter_by(id=id).first()
        if alert_alarm_def is None:
            message = 'alert_alarm_definition not found.'
            raise Exception(message)
        user_event_notification = get_user_event_notification(id)
        if user_event_notification is None:
            message = 'user_event_notification (for alert_alarm_definition) not found.'
            raise Exception(message)
        result = alert_alarm_def.to_json()
        result['user_event_notification'] = user_event_notification
        return result
    except:
        raise


def get_user_event_notification(definition_id):
    """ Get user_event_notification for system_event_definition; return json.
    """
    result = []
    notification = UserEventNotification.query.filter_by(system_event_definition_id=definition_id).first()
    if notification is not None:
        result = notification.to_json()
    return result


def create_definition_has_required_fields(data):
    """ Verify SystemEventDefinition creation has required fields in request.data. Error otherwise.
    SystemEventDefinition update can re-use this method but must also check for uframe_filter_id.
    Review what to do with create_time on update SystemEventDefinition.
    Verify operator value is one of valid uframe operators.
    """
    try:
        required_fields = ['active', 'array_name', 'description', 'event_type', 'high_value',
                           'instrument_name', 'instrument_parameter', 'instrument_parameter_pdid', 'low_value',
                           'operator',  'platform_name', 'reference_designator', 'severity',  'stream',
                           'escalate_on', 'escalate_boundary']
        valid_operators = ['GREATER', 'LESS', 'BETWEEN_EXCLUSIVE', 'OUTSIDE_EXCLUSIVE']
        valid_event_types = ['alert', 'alarm']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%r) in request.data' % field
                raise Exception(message)
            if data[field] is None:
                if field != 'description':
                    message = 'Required field (%r), in request.data, has a value of None' % field
                    raise Exception(message)

        if data['event_type'] not in valid_event_types:
            message = 'Invalid event_type value provided (%s).' % data['event_type']
            raise Exception(message)
        if data['operator'] not in valid_operators:
            message = 'Invalid operator value provided (%r).' % data['operator']
            raise Exception(message)
        if data['event_type'] == 'alert':
            if (not isinstance(data['escalate_on'], type(1.0))) and (not isinstance(data['escalate_on'], type(1))):
                message = 'Invalid escalate_on value type (%r).' % data['escalate_on']
                raise Exception(message)
            if (not isinstance(data['escalate_boundary'], type(1.0))) and \
                    (not isinstance(data['escalate_boundary'], type(1))):
                message = 'Invalid escalate_boundary value type (%r).' % data['escalate_boundary']
                raise Exception(message)
        if data['escalate_on'] < 0:
            message = 'Invalid escalate_on value provided (%r).' % data['escalate_on']
            raise Exception(message)
        if data['escalate_boundary'] < 0:
            message = 'Invalid escalate_boundary value provided (%r).' % data['escalate_boundary']
            raise Exception(message)
        return
    except:
        raise


def user_event_notification_has_required_fields(data):
    """ Verify insert_user_event_notification data has required fields. Error otherwise.
    """
    try:
        required_fields = ['user_id', 'use_email', 'use_redmine', 'use_phone', 'use_log', 'use_sms']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%r) in request.data' % field
                raise Exception(message)
            if data[field] is None:
                message = 'Required field (%s) value provided is None for user_event_notification.' % field
                raise Exception(message)
        return
    except:
        raise


def create_has_required_fields(data):
    """ Verify SystemEvent creation has required fields in request.data. Error otherwise.
    """
    try:
        required_fields = ['uframe_event_id', 'uframe_filter_id', 'system_event_definition_id',
                           'event_time', 'event_type', 'event_response', 'method', 'deployment']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%r) in request.data' % field
                raise Exception(message)
        return
    except:
        raise


def acknowledge_has_required_fields(data):
    """ Verify SystemEvent acknowledge has required fields in request.data. Error otherwise.
    """
    try:
        required_fields = ['id', 'uframe_event_id', 'uframe_filter_id', 'system_event_definition_id',
                           'event_type', 'ack_by']
        for field in required_fields:
            if field not in data:
                message = 'Missing required field (%r) in request.data' % field
                raise Exception(message)
        return
    except:
        raise


def get_query_filters(request_args):
    """ Create filter dictionaries for SystemEvent and SystemEventDefinition; used in route /alert_alarm.

    Current filter options for request.args:
        'type', 'method', 'deployment', 'acknowledged', 'array_name', 'platform_name', 'instrument_name',
        'reference_designator', 'active', 'retired'

    Breakout for filters by class (where actual filter item is):
        for alert_alarm:            'event_type', 'method', 'deployment', 'acknowledged'
        for alert_alarm_definition: 'array_name', 'platform_name', 'instrument_name', 'reference_designator',
                                    'active', 'retired'
    """
    event_filters = {}
    definition_filters = {}
    event_type = None
    acknowledged = None
    method = None
    deployment = None
    array_name = None
    platform_name = None
    reference_designator = None
    instrument_name = None
    active = None
    retired = None
    # Set filter values based on request.args
    if 'type' in request.args:
        tmp = str(request_args.get('type'))
        if tmp is not None and tmp != '' and tmp != 'None':
            event_type = request_args.get('type')
    elif 'event_type' in request.args:
        tmp = str(request_args.get('event_type'))
        if tmp is not None and tmp != '' and tmp != 'None':
            event_type = request_args.get('event_type')
    if 'method' in request_args:
        if request_args.get('method') is not None:
            method = request_args.get('method')
    if 'deployment' in request_args:
        tmp = str(request_args.get('deployment'))
        if tmp is not None and tmp != '' and tmp != 'None':
            try:
                deployment = float(tmp)
            except:
                pass
    if 'acknowledged' in request_args:
        if request_args.get('acknowledged') is not None:
            try:
                # default to false
                acknowledged = to_bool(request_args.get('acknowledged'))
                acknowledged = str(acknowledged).lower()
            except:
                pass
    if 'array_name' in request_args:
        if request_args.get('array_name') is not None:
            array_name = request_args.get('array_name')
    if 'platform_name' in request_args:
        if request_args.get('platform_name') is not None:
            platform_name = request_args.get('platform_name')
    if 'reference_designator' in request_args:
        if request_args.get('reference_designator') is not None:
            reference_designator = request_args.get('reference_designator')
    if 'instrument_name' in request_args:
        if request_args.get('instrument_name') is not None:
            instrument_name = request_args.get('instrument_name')
    if 'active' in request_args:
        if request_args.get('active') is not None:
            try:
                # defaults to true
                active = to_bool(str(request_args.get('active')))
                active = str(active).lower()
            except:
                active = None
                pass
    if 'retired' in request_args:
        if request_args.get('retired') is not None:
            try:
                # defaults to false
                retired = to_bool(request_args.get('retired'))
                retired = str(retired).lower()
            except:
                pass
    # SystemEvent query filter (NOTE: keys must be class properties)
    event_keys = ['event_type', 'method', 'deployment', 'acknowledged']
    event_values = [event_type, method, deployment, acknowledged]
    tmp_dictionary = dict(zip(event_keys, event_values))
    for k, v in tmp_dictionary.items():
        if v is not None:
            event_filters[k] = v
    if len(event_filters) == 0:
        event_filters = None

    # SystemEventDefinition query filter (NOTE: keys must be class properties)
    def_keys = ['array_name', 'platform_name', 'instrument_name', 'reference_designator','active','retired']
    def_values = [array_name, platform_name, instrument_name, reference_designator, active, retired]
    tmp_dictionary = dict(zip(def_keys, def_values))
    for k, v in tmp_dictionary.items():
        if v is not None:
            definition_filters[k] = v
    if len(definition_filters) == 0:
        definition_filters = None
    return event_filters, definition_filters


def to_bool(value):
    """ Converts 'something' to boolean. Raises exception for invalid formats.
    Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
    Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def get_alert_alarm_json(alerts_alarms, definition_filters):
    """ For a collection of alert_alarm objects, use definition_filters to determine if this alert_alarm
    meets criteria requested, if so return alert_alarm json with the
    alert_alarm_definition embedded as a new element 'alert_alarm_definition'.
    """
    result = None
    result_json = []
    try:
        # Process each alert_alarm and include alert_alarm_definition as element in json
        if alerts_alarms:
            for alert_alarm in alerts_alarms:
                definition_id = alert_alarm.system_event_definition_id
                tmp_json_dict = alert_alarm.to_json()

                # Get SystemEventDefinition, filter based on variables in definition_filters
                event_type = alert_alarm.event_type
                definition = SystemEventDefinition.query.filter_by(id=definition_id, event_type=event_type).first()
                if definition is None:
                    message = 'No alert_alarm_definition (id:%d) for alert_alarm (id: %d, %s).' % \
                              (definition_id, alert_alarm.id, alert_alarm.event_type)
                    raise Exception(message)

                # Determine if this alert_alarm_definition data matches definition_filters
                tmp_json_dict['alert_alarm_definition'] = {}
                if definition_filters is None:
                    tmp_json_dict['alert_alarm_definition'] = definition.to_json()
                    result_json.append(tmp_json_dict)
                else:
                    # use definition_filters to determine if request criteria is met.
                    matches = False
                    for k,v in definition_filters.items():
                        value = getattr(definition, k)
                        if k == 'retired' or k == 'active':      # booleans
                            value = str(value).lower()
                        matches = True
                        if value != v:
                            matches = False
                            break
                    if matches:
                        tmp_json_dict['alert_alarm_definition'] = definition.to_json()
                        result_json.append(tmp_json_dict)
            result = result_json
        return result
    except:
        raise


def get_definitions_query_filter(request_args):
    """ Get query_filter for alert_alarm_definition list route.
    """
    query_filters = None
    display_retired = False
    valid_args = ['array_name', 'platform_name', 'instrument_name', 'reference_designator']
    # Process request arguments
    if 'retired' in request_args:
        if (request_args.get('retired')).lower() == 'true':
            display_retired = True
    key = None
    key_value = None
    for key in valid_args:
        if key in request_args:
            tmp = request_args.get(key)
            if tmp:
                key_value = str(tmp)
                break
    # If query_filter to be created, create it
    if key_value is not None or display_retired:
        query_filters = {}
        if key_value is not None:
            query_filters[key] = key_value
        if display_retired:
            query_filters['retired'] = True
    return query_filters

def safe_to_delete_alert_alarm_definition(id):
    """ Verify this alert_alarm_definition can be retired.
    """
    result = False
    # Get alert_alarm_definition
    alert_alarm_def = SystemEventDefinition.query.get(id)
    if alert_alarm_def is None:
        return result
    # If alert_alarm_definition already retired, just return
    if alert_alarm_def.retired is not None:
        if alert_alarm_def.retired:
            return result
    # Determine if definition id is used by any alert or alarm instances where acknowledged is False
    active_alerts_alarms = SystemEvent.query.filter_by(system_event_definition_id=id, acknowledged=False).first()
    if active_alerts_alarms is not None:
        return result
    return True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Methods for uframe integration
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_uframe_alertfilter(request_data):
    """ Create alertfilter in uframe. Return uframe alertfilter id, None or raise Exception.
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

        # Create alertfilter in uframe
        response = uframe_create_alertfilter(uframe_data)
        if response.status_code !=201:
            message = '(%s) Failed to execute create_uframe_alertfilter.' % str(response.status_code)
            raise Exception(message)

        # Evaluate response content for error or alertfilter id
        # Sample: {"message" : "Record created successfully", "id" : 2, "statusCode" : "CREATED" }
        if response.content is not None:
            response_data = json.loads(response.content)
            if 'statusCode' in response_data:
                if response_data['statusCode'] == successful_response:
                    result = response_data['id']
        return result
    except:
        raise


def update_uframe_alertfilter(request_data, id):
    """ Update alertfilter in uframe. Return if successful, Exception if error.
    Process:
        Create uframe data dictionary from request.data;
        Update alertfilter in uframe using uframe data dictionary created
        Return uframe alertfilter id, None or exception.
    """
    successful_response = 'OK'
    result = None
    try:
        # Create uframe data dictionary from request.data
        uframe_data = create_uframe_alertfilter_data(request_data)

        # Update alertfilter in uframe
        response = uframe_update_alertfilter(uframe_data, id)
        if response.status_code !=200:
            message = '(%s) Failed to execute update_uframe_alertfilter (id: %d).' % (str(response.status_code), id)
            raise Exception(message)

        # Evaluate response content for error or alertfilter id
        if response.content is not None:
            response_data = json.loads(response.content)
            if 'statusCode' in response_data:
                if response_data['statusCode'] == successful_response:
                    result = response_data['id']
        return result
    except:
        raise


def delete_alertfilter(id):
    """ Delete alertfilter in uframe. On error return None, else return id.

    Used when create_alert_alarm_def fails to persist to ooi-ui-services db after
    an alertfilter was created in uframe.

    Sample response dictionary for uframe for delete:
        {u'message': u'Delete successful.', u'id': 204, u'statusCode': u'OK'}
    """
    successful_response = 'OK'
    result = None
    try:
        uframe_url, timeout, timeout_read = get_uframe_alerts_info()
        url = "/".join([uframe_url, 'alertfilters', str(id)])
        response = requests.delete(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%r) Failed to execute alertfilter deletion (id: %d)' % (response.status_code, id)
            raise Exception(message)

        if response.content is not None:
            uframe_data = json.loads(response.content)
            if 'statusCode' in uframe_data:
                if uframe_data['statusCode'] == successful_response:
                    result = uframe_data['id']
        return result
    except:
        return result


def get_alertfilter(id):
    """ Get alertfilter in uframe. On error return None, else return id.
    Used by update_alert_alarm on rollback when error persisting to ooi-ui-services db, then rollback
    uframe alertfilter changes. For sample response dictionary from uframe, create_uframe_alertfilter_data.

    Output format for uframe response.content when uframe response.status_code != 200:
        {u'message': u'Unable to locate element', u'id': 90999, u'statusCode': u'NOT_FOUND'}
        Sample error message:
            '(404) Failed to get alertfilter from uframe; uframe error: Unable to locate element 90999'
    """
    result = None
    try:
        uframe_url, timeout, timeout_read = get_uframe_alerts_info()
        url = "/".join([uframe_url, 'alertfilters', str(id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get alertfilter from uframe' % response.status_code
            if response.content is not None:
                tmp = json.loads(response.content)
                if 'message' in tmp:
                    message += '; uframe error: %s %r' % (tmp['message'], tmp['id'])
            current_app.logger.info(message)
            raise Exception(message)
        result = json.loads(response.content)
        return result
    except:
        return result


def create_uframe_alertfilter_data(data):
    """ Create alertfilter dictionary for uframe processing.

    Sample of uframe alertfilter input being created and updated:
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
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify required fields to create alert alarm are present in data dictionary.
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        create_definition_has_required_fields(data)
        instrument_parameter_pdid = data['instrument_parameter_pdid']
        if instrument_parameter_pdid is None:
            raise Exception('Required parameter (instrument_parameter_pdid) is None.')

        stream = data['stream']
        reference_designator = data['reference_designator']
        severity = data['severity']
        if data['event_type'] == 'alarm':
            severity = severity * -1
        high_value = data['high_value']
        low_value = data['low_value']
        description = data['description']
        if description is None:                     # uframe will fail if None is provided for description
            description = ''

        if '-' in stream:
            stream.replace('-', '_')

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Validate reference_designator length and set additional field (subsite, node and sensor)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if len(reference_designator) != 27:
            raise Exception('reference_designator is malformed.')
        else:
            subsite = reference_designator[0:8]
            node = reference_designator[9:14]
            sensor = reference_designator[15:27]
            subsite = subsite.replace(' ','')
            node = node.replace(' ','')
            sensor = sensor.replace(' ','')

        if not subsite or not node or not sensor:
            raise Exception('Required parameter (subsite, node or sensor) is empty or malformed.')

        if len(subsite) != 8 or len(node) != 5 or len(sensor) != 12:
            message = 'One or more field(s), derived from reference_designator is malformed: subsite, node or sensor.'
            raise Exception(message)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Populate return dictionary
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        uframe_data = {}
        uframe_data['@class'] = 'com.raytheon.uf.common.ooi.dataplugin.alert.alertfilter.AlertFilterRecord'
        uframe_data['enabled'] = data['active']
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
        return uframe_data
    except:
        raise


# Note: start of unix epoch (jan 1, 1900 at midnight 00:00) in seconds == 2208988800
# http://stackoverflow.com/questions/13260863/convert-a-unixtime-to-a-datetime-object-
# and-back-again-pair-of-time-conversion (url continued from previous line)
# Convert a unix time u to a datetime object d, and vice versa
def convert_from_utc(u):
    return dt.datetime.utcfromtimestamp(u)


def ut(d):
    return calendar.timegm(d.timetuple())


def get_uframe_alerts_info():
    """ Get uframe alertalarm configuration information. """
    uframe_url = current_app.config['UFRAME_ALERTS_URL']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read


def get_uframe_info():
    """ Get uframe configuration information. (uframe_url, uframe timeout_connect and timeout_read.) """
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read


def headers():
    """ Headers for uframe PUT and POST. """
    return {"Content-Type": "application/json"}


def uframe_create_alertfilter(uframe_data):
    """ Create alertfilter in uframe. """
    uframe_url, timeout, timeout_read = get_uframe_alerts_info()
    url = "/".join([uframe_url, 'alertfilters'])
    data = json.dumps(uframe_data)
    response = requests.post(url, timeout=(timeout, timeout_read), headers=headers(), data=data)
    return response


def uframe_update_alertfilter(uframe_data, alertfilter_id):
    """ Update alertfilter in uframe. """
    uframe_url, timeout, timeout_read = get_uframe_alerts_info()
    url = "/".join([uframe_url, 'alertfilters', str(alertfilter_id)])
    data = json.dumps(uframe_data)
    response = requests.put(url, timeout=(timeout, timeout_read), headers=headers(), data=data)
    return response


def uframe_acknowledge_alert_alarm(uframe_event_id, value):
    """ Acknowledge alert or alarm in uframe using eventId and value. Return True (success), False or error.
        Sample data for PUT:
        {
          "eventId":"2",
          "acknowledgedBy":"1"
        }
        where acknowledgedBy represents ooi-ui-service assigned str(user_id)
    """
    uframe_success = 'OK'
    result = False
    try:
        uframe_url, timeout, timeout_read = get_uframe_alerts_info()
        url = "/".join([uframe_url, 'alertalarms', 'ack'])
        uframe_data = {}
        uframe_data['eventId'] = str(uframe_event_id)
        uframe_data['acknowledgedBy'] = str(value)
        data = json.dumps(uframe_data)
        response = requests.put(url, timeout=(timeout, timeout_read), headers=headers(), data=data)
        if response.status_code != 200:
            message = 'Failure to issue uframe acknowledge for alert_alarm (event id: %d) in uframe. ' % uframe_event_id
            current_app.logger.info('[uframe_acknowledge_alert_alarm] %s ' % message)
            return result

        if response.content:
            """ Sample uframe response content:
            {"message" : "Acknowledged record [2] by [testuser@company]", "id" : 2, "statusCode" : "OK"}
            """
            acknowledgement = json.loads(response.content)
            if 'statusCode' in acknowledgement:
                if acknowledgement['statusCode'] == uframe_success:
                    result = True
    except Exception as err:
        current_app.logger.info('[acknowledge_alert_alarm] %s ' % err.message)
    finally:
        return result


@api.route('/alert_alarm_instrument_available/<string:ref>', methods=['GET'])
def uframe_instrument_available(ref):
    """
    Retrieve uframe metadata parameters for a specific instrument.
    """
    results = None
    try:
        # Get instrument metadata
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            return bad_request('(%d) Failure to retrieve metadata from uframe.' % response.status_code)
        metadata = response.json()
        if 'parameters' in metadata:
            parameters = metadata['parameters']
            if parameters is None:
                return bad_request('Failure to get metadata parameters from uframe response.')
            else:
                results = parameters
        return jsonify(metadata=results)
    except Exception as err:
        return bad_request('Failed to retrieve instrument metadata from uframe. ' + str(err.message))


@api.route('/alert_alarm_get_instrument_metadata/<string:ref>', methods=['GET'])
def uframe_get_instrument_metadata(ref):
    '''
    Returns the uFrame metadata response for an instrument, for all methods - concatenate method and stream_name.
    Example: method + '_' + stream_name

    Sample request:
        http://localhost:4000/alert_alarm_get_instrument_metadata/CE01ISSM-SBD17-04-VELPTA000

    Reference regarding urls utilized to process the sample request above:
        http://host:port/sensor/inv/CE01ISSM/SBD17/04-VELPTA000
        http://host:port/sensor/inv/CE01ISSM/SBD17/04-VELPTA000/telemetered
        http://host:port/sensor/inv/CE01ISSM/SBD17/04-VELPTA000/recoveredi
        http://host:port/sensor/inv/CE01ISSM/SBD17/04-VELPTA000/metadata
    '''
    methods = None
    parameters = None
    streams = {}
    results = None
    try:
        # Get instrument metadata
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            metadata = response.json()
            if 'parameters' in metadata:
                parameters = metadata['parameters']
        if parameters is None:
            return bad_request('Failure to compile response, metadata parameters is None.')

        # Get instrument methods
        url = "/".join([uframe_url, mooring, platform, instrument])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            methods = response.json()
        if methods is None:
            return bad_request('Failure to compile response, instrument %s has no methods.' % ref)

        # Get streams for each method (expects unique list of methods from uframe; no duplicates)
        for method in methods:
            url = "/".join([uframe_url, mooring, platform, instrument, method])
            response = requests.get(url, timeout=(timeout, timeout_read))
            if response.status_code == 200:
                streams_data = response.json()
                if streams_data is not None:
                    streams[str(method)] = streams_data

        if len(streams) == 0:
            return bad_request('Failure to compile response, instrument %s has methods with no streams.' % ref)

        # Compile result from methods, streams and parameters
        tmp = {}
        for method in methods:
            streams_for_method = streams[str(method)]
            tmp[method] = {}
            for stream in streams_for_method:
                key = "_".join([str(method), str(stream).replace('_', '-')])
                #key = "_".join([str(method), str(stream)])
                list_of_parameters = []
                for param in parameters:
                    if str(param['stream']) == str(stream):
                        list_of_parameters.append(param)
                if len(list_of_parameters) > 0:
                    tmp[method][key] = list_of_parameters

        if len(tmp) > 0:
            results = tmp

        return jsonify(stream_metadata=results)
    except Exception as err:
        return bad_request('Failed to compile instrument metadata by stream. ' + str(err.message))


# Acknowledge instances for alert/alarm definition
@api.route('/ack_alert_alarm_definition/<int:definition_id>', methods=['GET'])
@auth.login_required
@scope_required(u'user_admin')
def ack_alert_alarm_definition(definition_id):
    """ Acknowledge all alert(s) or an alarm(s) associated with the definition identified by definition_id.
    """
    try:
        # Get definition identified in request
        definition = SystemEventDefinition.query.get(definition_id)
        if definition is None:
            message = 'Failed to retrieve SystemEventDefinition for id provided: %d' % definition_id
            return bad_request(message)

        # Verify definition is not in active state; otherwise error
        if definition.active:
            message = '%s definition must be disabled before clearing any associated instances.' % definition.event_type
            return bad_request(message)

        # Determine current user who is auto clearing alert or alarm instances (written to log)
        assigned_user = User.query.get(g.current_user.id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
        else:
            name = 'Unknown/unassigned user with g.current_user.id: %s' % str(g.current_user.id)

        # Identify default user and message for auto acknowledgment; log activity
        ack_by = 1
        ack_value = 'Log: Auto acknowledge (ooi-ui-services) OBO user \'%s\'; %s definition id: %d' % \
                        (name,definition.event_type, definition.id)
        current_app.logger.info(ack_value)

        # Get all active instances for this definition which have not been acknowledged.
        instances = SystemEvent.query.filter_by(system_event_definition_id=definition.id,acknowledged=False).all()
        for instance in instances:
            if instance.event_type=='alarm':
                if not (uframe_acknowledge_alert_alarm(instance.uframe_event_id, ack_value)):
                    message = 'Failed to acknowledge alarm (id:%d) in uframe, prior to clearing instance.' % instance.id
                    current_app.logger.info('[clear_alert_alarm] %s ' % message)
                    return bad_request(message)

            # Update alert_alarm acknowledged, ack_by and ts_acknowledged
            instance.acknowledged = True
            instance.ack_by = ack_by
            instance.ts_acknowledged = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%dT%H:%M:%S")
            try:
                db.session.add(instance)
                db.session.commit()
            except:
                db.session.rollback()
                return bad_request('IntegrityError during auto-acknowledgment of %s by %s.' %
                                   (instance.event_type, str(ack_by)))

        result = 'ok'
        return jsonify( {'result' : result }), 200

    except Exception as err:
        message = 'Insufficient data, or bad data format. %s' % str(err.message)
        current_app.logger.info(message)
        return conflict(message)

#------------------------------------------------
#------------------------------------------------
# Resolve instance of alert/alarm
@api.route('/resolve_alert_alarm/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required(u'user_admin')
def resolve_alert_alarm(id):
    """ Resolve an alert or an alarm.
    """
    try:
        # Input request data must provide resolved comment field; regardless of event_type.
        if request.data is None:
            message = 'Failed to provide request data to resolve alert or alarm.'
            return bad_request(message)

        data = json.loads(request.data)
        if 'resolved_comment' not in data:
            message = 'Failed to provide resolved comment in request data; unable to resolve alert or alarm.'
            return bad_request(message)
        resolved_comment = data['resolved_comment']

        # Get instance identified in request
        instance = SystemEvent.query.get(id)
        if instance is None:
            message = 'Failed to retrieve SystemEvent for id provided: %d' % id
            return bad_request(message)

        # Instance must be acknowledged to be resolved
        if not instance.acknowledged:
            message = 'Cannot clear %s unless it is acknowledged. (id: %d)' % (instance.event_type, id)
            return bad_request(message)

        # To resolve an alarm instance, the resolved_comment must be provided and not None.
        if instance.event_type == 'alarm':
            if resolved_comment is None:
                message = 'Resolved comment in request data is empty of None; unable to resolve alert or alarm.'
                return bad_request(message)

        # Determine current user who is auto clearing alert or alarm instances (written to log)
        assigned_user = User.query.get(g.current_user.id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
        else:
            message = 'Unknown/unassigned user with g.current_user.id: %s' % str(g.current_user.id)
            return bad_request(message)

        # Resolve alert or alarm instance
        instance.resolved_comment = '[' + name + '] ' + resolved_comment
        instance.resolved = True
        try:
            db.session.add(instance)
            db.session.commit()
        except:
            db.session.rollback()
            return bad_request('IntegrityError during resolve of %s.' % instance.event_type)

        result = 'ok'
        return jsonify( {'result' : result }), 200

    except Exception as err:
        message = 'Insufficient data, or bad data format. %s' % str(err.message)
        current_app.logger.info(message)
        return conflict(message)


# Resolve all instances for alert/alarm definition
@api.route('/resolve_alert_alarm_definition/<int:definition_id>', methods=['PUT'])
@auth.login_required
@scope_required(u'user_admin')
def resolve_alert_alarm_definition(definition_id):
    """ Resolve alert alarm definition. ('Clear')

    To 'Clear' an alert or alarm definition:
        Definition must not be active and
        All instances must be previously acknowledged.
        And, for alarms, resolved_comment shall not be None.
    """
    try:
        # Input request data must provide resolved comment field; regardless of event_type.
        if request.data is None:
            message = 'Failed to provide request data to resolve alert or alarm.'
            current_app.logger.info(message)
            return bad_request(message)

        data = json.loads(request.data)
        if 'resolved_comment' not in data:
            message = 'Failed to provide resolved comment in request data; unable to resolve alert or alarm.'
            current_app.logger.info(message)
            return bad_request(message)
        resolved_comment = data['resolved_comment']

        # Get definition identified in request
        definition = SystemEventDefinition.query.get(definition_id)
        if definition is None:
            message = 'Failed to retrieve SystemEventDefinition for id provided: %d' % definition_id
            current_app.logger.info(message)
            return bad_request(message)

        if definition.event_type is 'alarm:':
            if resolved_comment is None:
                message = 'Resolved comment must not be None for this alarm definition (id: %d).'  % definition.id
                current_app.logger.info(message)
                current_app.logger.info('[resolve_alert_alarm_definition] %s ' % message)
                return bad_request(message)

        # Verify definition is not in active state; otherwise error
        if definition.active == True:
            message = '%s definition must be disabled before clearing any associated instances.' % definition.event_type
            current_app.logger.info(message)
            return bad_request(message)

        # Determine current user who is auto clearing alert or alarm instances (written to log)
        assigned_user = User.query.get(g.current_user.id)
        if assigned_user is not None:
            name = assigned_user.first_name + ' ' + assigned_user.last_name
        else:
            message = 'Unknown/unassigned user with g.current_user.id: %s' % str(g.current_user.id)
            current_app.logger.info(message)
            return bad_request(message)

        # Get all instances for this definition which have not been resolved.
        ack_instances = SystemEvent.query.filter_by(system_event_definition_id=definition.id, acknowledged=False).first()
        if ack_instances is not None:
            message = 'To resolve %s definition, all associated instances must be acknowledged.' % definition.event_type
            current_app.logger.info(message)
            return bad_request(message)

        # Get all instances for this definition which have not been resolved.
        instances = SystemEvent.query.filter_by(system_event_definition_id=definition.id, resolved=False).all()
        for instance in instances:
            instance.resolved_comment = '[' + name + '] ' + resolved_comment
            instance.resolved = True
            try:
                db.session.add(instance)
                db.session.commit()
            except:
                db.session.rollback()
                message = 'IntegrityError during resolve of %s.' % instance.event_type
                current_app.logger.info(message)
                return bad_request(message)

        result = 'ok'
        return jsonify( {'result' : result }), 200

    except Exception as err:
        message = 'Insufficient data, or bad data format. %s' % str(err.message)
        current_app.logger.info(message)
        return conflict(message)


#==============================================================
#List all alert and alarm definitions
@api.route('/alert_alarms', methods=['GET'])
def get_triggered_alerts_alarms():
    """ Get a list of triggered alert(s) or alarm(s).
    """
    try:
        alert_alarm = get_alert_alarm_definitions_list()
        return jsonify( {'alert_alarm': alert_alarm})
    except Exception as err:
        return bad_request(err.message)


def get_alert_alarm_definitions_list(limit=None):
    """ Get list of alert or alarm definition ids; return list.
    """
    ids = []
    alerts_alarms = []
    try:
        # Get all definitions, if definitions continue otherwise raise Exception.
        definitions = SystemEventDefinition.query.order_by(SystemEventDefinition.id).all()
        if definitions is None:
            message = 'No alert or alarm definitions found; unable to retrieve triggered alerts and alarms.'
            raise Exception(message)

        # Get list of definition ids
        #for definition in definitions:
        #    ids.append(definition.id)

        # For each definition, get SystemEvent(s) using definition id; order by descending SystemEvent id.
        for definition in definitions:
            id = definition.id
            instance = SystemEvent.query.filter_by(system_event_definition_id=id).order_by(desc(SystemEvent.id)).first()
            if instance is None:
                continue
            the_count = SystemEvent.query.filter_by(system_event_definition_id=id).order_by(desc(SystemEvent.id)).count()
            json_instance = instance.to_json()
            json_definition = (SystemEventDefinition.query.get(id)).to_json()
            json_instance['count'] = the_count
            json_instance['alert_alarm_definition'] = json_definition
            alerts_alarms.append(json_instance)

        return alerts_alarms
    except:
        raise
