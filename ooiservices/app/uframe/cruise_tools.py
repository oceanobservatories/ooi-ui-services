
"""
Cruise supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.config import (get_url_info_cruises_inv, get_uframe_assets_info, get_events_url_base,
                                           get_url_info_cruises, get_uframe_events_info, get_url_info_cruises_rec)
import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)


def _get_cruises():
    """ Get list of cruises. On success return dict (key) of cruises.
    """
    cruises = []
    try:
        cruise_list = uframe_get_cruise_inv()
        if not cruise_list:
            return cruises
        set_cruise_list = set(cruise_list)
        cruise_list = list(set_cruise_list)
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
def _get_cruise_by_event_id(event_id):
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


# Get cruise using uniqueCruiseIdentifier.
def _get_cruise_by_cruise_id(cruise_id):
    """ Get all assets from uframe.
    """
    try:
        result = post_process_cruise(uframe_get_cruise_by_cruise_id(cruise_id))
        return result

    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_cruise_deployments(cruise_id, type):
    """ Get deployments for a specific cruise. Apply phase type selection.
    """
    abridged_deployments = []
    try:
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


def _get_deployment_by_event_id(event_id):
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
# (external) Verify unique cruise id does not exist.
def uniqueCruiseIdentifier_exists(cruise_id):
    """ Verify cruise identifier provided does not exist. Boolean result True then exists, else False.
    """
    try:
        try:
            # If uframe returns a value, then cruise exists, otherwise it does not.
            value = uframe_get_cruise_by_subsite(cruise_id)
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
        if 'referenceDesignator' not in data:
            deployment['rd'] = None
        elif 'referenceDesignator' in data:
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
        latitude = 0.0
        longitude = 0.0
        depth = 0.0
        if 'location' in data:
            if data['location']:
                if 'latitude' in data['location']:
                    deployment['latitude'] = data['location']['latitude']
                if 'longitude' in data['location']:
                    deployment['longitude'] = data['location']['longitude']
                if 'depth' in data['location']:
                    deployment['depth'] = data['location']['depth']
        else:
            deployment['latitude'] = latitude
            deployment['longitude'] = longitude
            deployment['depth'] = depth

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
# Get cruise inventory.
def uframe_get_cruise_inv():
    """ Get cruise inventory list from uframe.
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises_inv()
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get cruise inventory from uframe.'
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise inventory by subsite from uframe.
def uframe_get_cruise_by_subsite(subsite):
    """ Get cruise inventory list by subsite from uframe.
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises_rec()
        # host:12587/events/cruise/rec/{cruiseid}
        url = '/'.join([url, subsite])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get cruise inventory for \'%s\' from uframe.' % subsite
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise using uniqueCruiseIdentifier.
def uframe_get_cruise_by_cruise_id(cruise_id):
    """ Get all assets from uframe.
    """
    try:
        base_url, timeout, timeout_read = get_url_info_cruises_rec()
        url = '/'.join([base_url, cruise_id])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Unable to get cruise %s from uframe.' % (response.status_code, cruise_id)
            raise Exception(message)
        result = response.json()
        if result is None or not result:
            message = 'No cruises found with unique identifier of \'%s\'.' % cruise_id
            raise Exception(message)
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get uframe cruise by event id.
def uframe_get_cruise_by_event_id(event_id):
    """ Get cruise by event id.
    """
    try:
        # Get base url with port and timeouts.
        url_base, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([url_base, get_events_url_base(), str(event_id)])

        # Get cruise [event] information from uframe.
        payload = requests.get(url, timeout=(timeout, timeout_read))
        if payload.status_code != 200:
            message = 'Unable to locate a cruise with an id of %d.' % event_id
            raise Exception(message)
        result = payload.json()
        return result

    except ConnectionError:
        message = 'Error: ConnectionError getting cruise with event id %d.' % event_id
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting cruise with event id %d.' % event_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)



# Get uframe deployments by cruise id.
def uframe_get_deployments_by_cruise_id(cruise_id, type=None):
    """ Get deployments from uframe for cruise_id.

    Requests to uframe:
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=all           [all=deploy+recover]
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=deploy
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=recover
    """
    try:
        base_url, timeout, timeout_read = get_url_info_cruises()
        url = '/'.join([base_url, 'deployments', cruise_id])
        if type is not None:
            url += '?type=' + type
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
        if payload.status_code == 204:
            # Return None when unknown uid is provided; log invalid request.
            message = 'Unknown cruise id %s, failed to get deployments.' % cruise_id
            current_app.logger.info(message)
            return None

        # If error, raise exception
        elif payload.status_code != 200:
            message = 'Error getting deployments for cruise id %s from uframe.' % cruise_id
            raise Exception(message)
        deployments = payload.json()
        if not deployments or deployments is None:
            deployments = []
        return deployments

    except ConnectionError:
        message = 'ConnectionError getting cruise id %s from uframe.' % cruise_id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting cruise id %s from uframe.' % cruise_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get uframe event by event id.
def uframe_get_event(event_id):
    """ Get an event by eventId
    """
    try:
        url_base, timeout, timeout_read = get_uframe_events_info()
        url = '/'.join([url_base, str(event_id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get uframe event with event id: %d.' % event_id
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe event, event id: %d.' % event_id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe event, event id: %d.' % event_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)