
"""
Asset Management - Cruise supporting functions.
"""
__author__ = 'Edna Donoughe'

from ooiservices.app.uframe.uframe_tools import (uframe_get_cruise_inv, uframe_get_cruise_by_event_id,
                                                 uframe_get_deployments_by_cruise_id, uframe_get_event,
                                                 uframe_get_cruise_by_cruise_id)


def _get_cruises():
    """ Get list of cruises. On success return dict (key) of cruises.
    """
    cruises = []
    try:
        cruise_list = uframe_get_cruise_inv()
        if not cruise_list:
            return cruises
        set_cruise_list = []
        for cruise in cruise_list:
            if cruise not in set_cruise_list:
                set_cruise_list.append(cruise)
        cruise_list = set_cruise_list
        if not cruise_list:
            return cruises
        for cruise in cruise_list:
            cruise_dict = _get_cruise_by_cruise_id(cruise)
            if not cruise_dict or cruise_dict is None:
                continue
            cruise_dict = post_process_cruise(cruise_dict)
            cruises.append(cruise_dict)
        return cruises
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise by event id.
def _get_cruise(event_id):
    """ Get cruise by event id.
    """
    try:
        result = uframe_get_cruise_by_event_id(event_id)
        if result is not None:
            result = post_process_cruise(result)
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise deployments by event id.
def _get_cruise_deployments(event_id, type):
    """ Get deployments for a cruise using the event id. Apply phase type selection.
    """
    abridged_deployments = []
    try:
        cruise = _get_cruise(event_id)
        if cruise is None:
            message = 'Unable to get cruise for event id %d.' % event_id
            raise Exception(message)

        cruise_id = None
        if 'uniqueCruiseIdentifier' in cruise:
            cruise_id = cruise['uniqueCruiseIdentifier']
        if cruise_id is None:
            message = 'The cruise returned for event id %d does not contain a  unique cruise id.' % event_id
            raise Exception(message)

        # Get deployments
        deployments = uframe_get_deployments_by_cruise_id(cruise_id, type=type)
        if not deployments or deployments is None:
            message = 'No deployments associated with cruise identifier \'%s\'.' % cruise_id
            raise Exception(message)
        for deploy in deployments:
            result = process_deployment_row(deploy)
            if result is not None:
                abridged_deployments.append(result)
        return abridged_deployments

    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_cruise_deployment(event_id):
    try:
        # Get deployment
        deployment = uframe_get_event(event_id)
        if not deployment or deployment is None:
            message = 'No deployment for cruise with event id \'%d\'.' % event_id
            raise Exception(message)
        deployment = process_deployment_view(deployment)
        return deployment

    except Exception as err:
        message = str(err)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Helper functions - External and internal.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get cruise using uniqueCruiseIdentifier.
def _get_cruise_by_cruise_id(cruise_id):
    """ Get all assets from uframe.
    """
    result = None
    try:
        cruise = uframe_get_cruise_by_cruise_id(cruise_id)
        if cruise is not None:
            result = post_process_cruise(cruise)
        return result

    except Exception as err:
        message = str(err)
        raise Exception(message)


# (external) Verify unique cruise id does not exist.
def uniqueCruiseIdentifier_exists(cruise_id):
    """ Verify cruise identifier provided does not exist. Boolean result True if exists, else False.
    """
    try:
        try:
            # If uframe returns a value, then cruise exists, otherwise it does not.
            #value = uframe_get_cruise_by_subsite(cruise_id)
            value = uframe_get_cruise_by_cruise_id(cruise_id)
            if value is None or not value:
                result = False
            else:
                result = True
        except Exception:
            result = False
        return result

    except Exception as err:
        message = str(err)
        raise Exception(message)


# todo -- process deployment data as required for UI display.
# (internal)
def process_deployment_view(data):
    """ Process deployment data for UI display, where data represents a complete deployment object.
    """
    try:
        result = data
        # Process deployment data as required for UI display.
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)



# (internal)
def process_deployment_row(data):
    """ Process deployment information and present following attributes:
            Attribute                 Type          Notes
        1.  'eventId',                integer
        2.  'deploymentNumber',       integer
        3.  'editPhase',              string        One of 'EDIT', 'OPERATIONAL', 'STAGED'.
        4.  'eventStartTime',         long
        5.  'eventStopTime',          long
        6.  'sensor_uid',             string
        7.  'mooring_uid',            string
        8.  'node_uid',               string
        9.  'rd',                     string
        10. 'latitude',               float
        11  'longitude',              float
        12. 'depth'                   float
    """
    deployment = {}
    try:
        # Create deployment row
        property_fields = ['eventId', 'deploymentNumber', 'editPhase', 'eventStartTime', 'eventStopTime']

        for field in property_fields:
            if field in data:
                deployment[field] = data[field]

        # Get rd from referenceDesignator dictionary
        subsite = None
        node = None
        sensor = None
        rd = None
        if 'referenceDesignator' in data:
            if 'subsite' in data['referenceDesignator']:
                subsite = data['referenceDesignator']['subsite']
            if 'node' in data['referenceDesignator']:
                node = data['referenceDesignator']['node']
            if 'sensor' in data['referenceDesignator']:
                sensor = data['referenceDesignator']['sensor']
            if subsite is not None:
                rd = subsite
                if node is not None:
                    rd = '-'.join([subsite, node])
                    if sensor is not None:
                        rd = '-'.join([subsite, node, sensor])
            deployment['rd'] = rd

        # Get location dictionary information:  latitude, longitude, depth and orbitRadius
        if 'location' in data:
            if data['location']:
                if 'latitude' in data['location']:
                    deployment['latitude'] = data['location']['latitude']
                if 'longitude' in data['location']:
                    deployment['longitude'] = data['location']['longitude']
                if 'depth' in data['location']:
                    deployment['depth'] = data['location']['depth']

        # Get mooring, node and sensor uids.
        mooring_uid = None
        node_uid = None
        sensor_uid = None
        if 'mooring' in data:
            if data['mooring'] is not None:
                if 'uid' in data['mooring']:
                    mooring_uid = data['mooring']['uid']
        if 'node' in data:
            if data['node'] is not None:
                if 'uid' in data['node']:
                    node_uid = data['node']['uid']
        if 'sensor' in data:
            if data['sensor'] is not None:
                if 'uid' in data['sensor']:
                    sensor_uid = data['sensor']['uid']
        deployment['mooring_uid'] = mooring_uid
        deployment['node_uid'] = node_uid
        deployment['sensor_uid'] = sensor_uid
        return deployment

    except Exception as err:
        message = str(err)
        raise Exception(message)


# (internal)
def post_process_cruise(data):
    try:
        if '@class' in data:
            del data['@class']
        if 'assetUid' in data:
            del data['assetUid']
        if 'cruiseIdentifier' in data:
            del data['cruiseIdentifier']
        return data
    except Exception as err:
        message = str(err)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Functions which get data from uframe server.
# Note: all functions shall start with 'uframe_'.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
