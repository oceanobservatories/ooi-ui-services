#!/usr/bin/env python
"""
Asset Management - Configuration and connection support functions.
    TOC
    Vocabulary
    C2
    C2 toc
    C2 missions
    Alerts and Alarms
    Assets
    Cruises
    Deployments
    Events
    Calibrations
    Resources
    Annotations
    Status
    Streams
    common
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from requests.exceptions import (ConnectionError, Timeout)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TOC
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_uframe_toc_url():
    """ Get uframe url for toc from configuration file; raise exception if not found.
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_TOC']
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_URL or UFRAME_TOC value in configuration file.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Vocabulary
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_uframe_vocab_info():
    """ Get uframe vocabulary configuration information.
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = current_app.config['UFRAME_VOCAB_URL']
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_VOCAB_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_c2_uframe_info(type='instrument'):
    """ Returns uframe instrument/api specific configuration information. (port 12572)
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        if type == 'instrument':
            uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_INST_BASE']])
        else:
            uframe_url = "".join([current_app.config['UFRAME_INST_URL'], current_app.config['UFRAME_PLAT_BASE']])
        return uframe_url, timeout, timeout_read
    except ConnectionError:
        message = 'ConnectionError for instrument/api configuration values.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for instrument/api configuration values.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 toc
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_uframe_c2_toc_url():
    """ Get uframe c2 url for toc from configuration file; raise exception if not found.
    """
    try:
        base_url, timeout, timeout_read = get_c2_uframe_data_info()
        uframe_url = '/'.join([base_url, current_app.config['UFRAME_TOC'] ])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate C2_UFRAME_BASE_URL or UFRAME_TOC value in configuration file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_c2_uframe_data_info():
    """ Returns uframe data configuration information. (port 12576, C2_UFRAME_BASE_URL)
    """
    try:
        # Use C2 server for toc info
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_base = current_app.config['C2_UFRAME_BASE_URL']
        uframe_url = uframe_base + current_app.config['UFRAME_URL_BASE']
        return uframe_url, timeout, timeout_read
    except ConnectionError:
        message = 'ConnectionError for command and control sensor/inv.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for command and control sensor/inv.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        message = 'Unable to locate C2_UFRAME_BASE_URL or UFRAME_URL_BASE value in configuration file.'
        current_app.logger.info(message)
        raise


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 missions
# todo - review how exception handling c2_mission.py, then add try/except block here
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_c2_missions_uframe_info():
    """ Returns uframe C2 mission api specific configuration information.
    """
    #try:
    timeout, timeout_read = get_uframe_timeout_info()
    uframe_url = "".join([current_app.config['UFRAME_MISSIONS_URL'], current_app.config['UFRAME_MISSIONS_BASE']])
    return uframe_url, timeout, timeout_read
    """
    except:
        message = 'Unable to locate UFRAME_MISSIONS_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)
    """


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts and Alarms
# todo - review exception handling alertalarms.py, then add try/except block here
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_uframe_alerts_info():
    """ Get uframe alertalarm configuration information.
    """
    #try:
    timeout, timeout_read = get_uframe_timeout_info()
    uframe_url = current_app.config['UFRAME_ALERTS_URL']
    return uframe_url, timeout, timeout_read
    """
    except:
        message = 'Unable to locate UFRAME_ALERTS_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)
    """

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Assets
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_assets_url_base():
    """ 'asset' """
    assets = current_app.config['UFRAME_ASSETS']
    return assets


def get_uframe_assets_info():
    """ Get uframe assets configuration information.
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = current_app.config['UFRAME_ASSETS_URL']
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_ASSETS_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Camera
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_image_store_url_base():
    """ Returns configuration file value for IMAGE_STORE.  If error, raise exception.
    ('ooiservices/cam_images')
    """
    try:
        result = current_app.config['IMAGE_STORE']
        return result
    except:
        message = 'Unable to locate IMAGE_STORE in config file.'
        current_app.logger.info(message)
        raise Exception(message)

def get_image_camera_store_url_base():
    """ Returns configuration file value for IMAGE_CAMERA_STORE. (Generally a url to ooi store server for images.)
    """
    try:
        result = current_app.config['IMAGE_CAMERA_STORE']
        return result
    except:
        message = 'Unable to locate IMAGE_CAMERA_STORE in config file.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Cruises
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_cruises_url_base():
    """ Returns configuration file value for UFRAME_CRUISES. ('events/cruise') If error, raise exception.
    'events/cruise'
    """
    try:
        cruises = current_app.config['UFRAME_CRUISES']
        return cruises
    except:
        message = 'Unable to locate UFRAME_CRUISES in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_cruises():
    """ Get complete url to query uframe cruises ('uframe-host:12587/events/cruise')
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = '/'.join([current_app.config['UFRAME_DEPLOYMENTS_URL'], get_cruises_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for cruises using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_cruises_inv():
    """ Get complete url to query uframe cruises ('uframe-host:12587/events/cruise/inv')
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises()
        uframe_url = '/'.join([url, 'inv'])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for cruises (inv) using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_cruises_rec():
    """ Get complete url to query uframe cruises ('uframe-host:12587/events/cruise/rec')
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises()
        uframe_url = '/'.join([url, 'rec'])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for cruises (rec) using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Deployments
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_deployments_url_base():
    """'events/deployment' """
    try:
        deployments = current_app.config['UFRAME_DEPLOYMENTS']
        return deployments
    except:
        message = 'Unable to locate UFRAME_DEPLOYMENTS in config file.'
        current_app.logger.info(message)
        raise Exception(message)


#def get_url_info_deployment():
def get_uframe_deployments_info():
    """ Get uframe deployments configuration information.
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = current_app.config['UFRAME_DEPLOYMENTS_URL']
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_DEPLOYMENTS_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_deployments_inv():
    """ Get complete url to query uframe deployment inventory ('uframe-host:12587/events/deployment/inv').
    """
    try:
        url, timeout, timeout_read = get_uframe_deployments_info()
        uframe_url = '/'.join([url, get_deployments_url_base(), 'inv'])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for deployments (inv) using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


# todo - proposed endpoint to provide deployment, version and uid for a reference designator.
# todo - use to replace dependency for asset to reference designator mapping.
def get_url_info_deployments_rec():
    """ Get complete url to query uframe deployment records for a reference designator.
    ('uframe-host:12587/events/deployment/rec)
    Use: uframe-host:12587/events/deployment/rec/reference_designator
        where reference designator is array, site, platform, or instrument)
    """
    try:
        url, timeout, timeout_read = get_uframe_deployments_info()
        uframe_url = '/'.join([url, get_deployments_url_base(), 'rec'])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for deployments (rec) using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Events
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_events_url_base():
    """ Returns string value from configuration file for UFRAME_EVENTS. (i.e. 'events') If error, raise exception.
    """
    try:
        events = current_app.config['UFRAME_EVENTS']
        return events
    except:
        message = 'Unable to locate UFRAME_EVENTS in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_uframe_events_info():
    """ Get uframe events configuration information.
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = '/'.join([current_app.config['UFRAME_DEPLOYMENTS_URL'], get_events_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_DEPLOYMENTS_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Calibration
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_calibration_url_base():
    """ Returns string value from configuration file for UFRAME_CALIBRATION. (i.e. 'cal') If error, raise exception.
    """
    try:
        events = current_app.config['UFRAME_CALIBRATION']
        return events
    except:
        message = 'Unable to locate UFRAME_CALIBRATION in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_uframe_info_calibration():
    """ Get uframe calibration event configuration information.
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = '/'.join([current_app.config['UFRAME_ASSETS_URL'], get_assets_url_base(), get_calibration_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate calibration resources in config file.'
        current_app.logger.info(message)
        raise Exception(message)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Resources
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_resources_url_base():
    """ Returns configuration file value for UFRAME_RESOURCES. ('resource') If error, raise exception.
    """
    try:
        resources = current_app.config['UFRAME_RESOURCES']
        return resources
    except:
        message = 'Unable to locate UFRAME_RESOURCES in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_resources():
    """ Get complete url to query uframe [remote] resources ('http://uframe-host:12587/resource')
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = '/'.join([current_app.config['UFRAME_ASSETS_URL'], get_resources_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for asset resources using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Annotations
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_annotations_base_url():
    try:
        result = current_app.config['UFRAME_ANNOTATION_URL'] + current_app.config['UFRAME_ANNOTATION_BASE']
        return result
    except:
        message = 'Unable to form uframe url for annotations using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Status
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_status_url_base():
    """ Returns configuration file value for UFRAME_STATUS. ('status') If error, raise exception.
    'status/query'
    """
    try:
        result = current_app.config['UFRAME_STATUS']
        return result
    except:
        message = 'Unable to locate UFRAME_STATUS in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_status_query_base():
    """ Returns configuration file value for UFRAME_STATUS_QUERY. ('query') If error, raise exception.
    Used in 'status/query'
    """
    try:
        result = current_app.config['UFRAME_STATUS_QUERY']
        return result
    except:
        message = 'Unable to locate UFRAME_STATUS_QUERY in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_status_inv_base():
    """ Returns configuration file value for UFRAME_STATUS_INV. ('query') If error, raise exception.
    Used in 'status/query'
    """
    try:
        result = current_app.config['UFRAME_STATUS_INV']
        return result
    except:
        message = 'Unable to locate UFRAME_STATUS_INV in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_status():
    """ Get complete url to query uframe status ('uframe-host:12587/status')
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = '/'.join([current_app.config['UFRAME_DEPLOYMENTS_URL'], get_status_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for status using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_status_query():
    """ Get complete url to query uframe status ('uframe-host:12587/status/query')
    """
    try:
        url, timeout, timeout_read = get_url_info_status()
        uframe_url = '/'.join([url, get_status_query_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for status using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_status_inv():
    """ Get complete url to query uframe status ('uframe-host:12587/status/inv')
    """
    try:
        url, timeout, timeout_read = get_url_info_status()
        uframe_url = '/'.join([url, get_status_inv_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for status using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Streams
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_stream_url_base():
    """'stream' """
    try:
        result = current_app.config['UFRAME_STREAM']
        return result
    except:
        message = 'Unable to locate UFRAME_STREAM in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_stream_parameter_url_base():
    """'parameter' """
    try:
        result = current_app.config['UFRAME_STREAM_PARAMETER']
        return result
    except:
        message = 'Unable to locate UFRAME_STREAM_PARAMETER in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_stream_byname_url_base():
    """'byname' """
    try:
        result = current_app.config['UFRAME_STREAM_BYNAME']
        return result
    except:
        message = 'Unable to locate UFRAME_STREAM_BYNAME in config file.'
        current_app.logger.info(message)
        raise Exception(message)


# Get base url for streams processing (stream, parameter and byname)
def get_uframe_stream_info():
    """ Get uframe stream base url configuration information.
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = current_app.config['UFRAME_STREAMS_URL']
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_STREAMS_URL, UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_streams():
    """ Get complete url to query uframe stream ('uframe-host:12575/stream')
    Used to form urls:
        host:12575/stream/byname/{name} where {name} is the stream name
        host:12575/stream/{id} where {id} is the stream id number from preload.
    """
    try:
        url, timeout, timeout_read = get_uframe_stream_info()
        uframe_url = '/'.join([url, get_stream_byname_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for streams using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_stream_byname():
    """ Get complete url to query uframe stream byname ('uframe-host:12575/stream/byname')
    Use host:12575/stream/byname/{name} where {name} is the stream name
    """
    try:
        url, timeout, timeout_read = get_uframe_stream_info()
        uframe_url = '/'.join([url, get_stream_url_base(), get_stream_byname_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for streams using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_stream_parameters():
    """ Get complete url to query uframe stream ('http:uframe-host:12575/parameter')
    Use: host:12575/parameter/{id} where {id} is the parameter id number from preload.
    """
    try:
        url, timeout, timeout_read = get_uframe_stream_info()
        uframe_url = '/'.join([url, get_stream_parameter_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for stream parameters using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)

def get_stream_parameters_switch():
    """ Boolean switch for enabling/disabling parameter content in stream_list cache. """
    add_parameters = False
    try:
        result = current_app.config['UFRAME_STREAM_PARAMETERS']
        if result == 'true' or result == True:
            add_parameters = True
        return add_parameters
    except:
        message = 'Unable to locate UFRAME_STREAM_PARAMETERS in config file.'
        current_app.logger.info(message)
        raise Exception(message)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common utility functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# uframe timeout information
def get_uframe_timeout_info():
    """ Get uframe timeout configuration information.
    """
    try:
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        return timeout, timeout_read
    except:
        message = 'Unable to locate UFRAME_TIMEOUT_CONNECT or UFRAME_TIMEOUT_READ in config file.'
        current_app.logger.info(message)
        raise Exception(message)


# Get uframe timeout, timeout_read and base url.
def get_uframe_info():
    """ Get uframe configuration information. (uframe_url, uframe timeout_connect and timeout_read.) """
    timeout, timeout_read = get_uframe_timeout_info()
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    return uframe_url, timeout, timeout_read


# Get uframe headers.
def _uframe_headers():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


# Headers for uframe PUT and POST.
def headers():
    return {"Content-Type": "application/json"}




