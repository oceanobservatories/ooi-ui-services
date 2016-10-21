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
# todo - not yet incorporated into c2.py
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
    except Exception:
        raise


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# C2 toc
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# todo - get ports dynamically and do replace.
def get_uframe_data_info():
    """ Returns uframe data configuration information. (port 12576)
    """
    try:
        # Use C2 server for toc info
        timeout, timeout_read = get_uframe_timeout_info()
        tmp_uframe_base = current_app.config['UFRAME_INST_URL']
        uframe_base = tmp_uframe_base.replace('12572', '12576')
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
# todo - review how exception handling alertalarms.py, then add try/except block here
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
    """ Get complete url to query uframe cruises ('uframe-host:12587/events/cruise/inv')
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
        message = 'Unable to form uframe url for cruises using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_cruises_rec():
    """ Get complete url to query uframe cruises ('uframe-host:12587/events/cruise/inv')
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises()
        uframe_url = '/'.join([url, 'rec'])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for cruises using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Deployments
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_deployments_url_base():
    """'events/deployment' """
    deployments = current_app.config['UFRAME_DEPLOYMENTS']
    return deployments


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
    """ Get complete url to query uframe cruises ('uframe-host:12587/events/deployment/inv')
    """
    try:
        url, timeout, timeout_read = get_uframe_deployments_info()
        uframe_url = '/'.join([url, get_deployments_url_base(), 'inv'])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for cruises using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def deployment_inv_load():
    """ Used to enable loading of deployment inventory reference designators during cache rebuild.
    Forced to False at this time. Use on development machines;
    Detrimentally increases cache load time due to large increase in reference designators from deployments.
    """
    use_deployments_on_load = False
    try:
        """
        tmp = current_app.config['DEPLOYMENTS_INV_LOAD']
        if tmp == True:
            use_deployments_on_load = True
        """
        return use_deployments_on_load
    except:
        message = 'Unable to obtain DEPLOYMENT_INV_LOAD using current config file variables.'
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
# Status
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_status_url_base():
    """ Returns configuration file value for UFRAME_STATUS. ('status') If error, raise exception.
    'events/cruise'
    """
    try:
        cruises = current_app.config['UFRAME_STATUS']
        return cruises
    except:
        message = 'Unable to locate UFRAME_STATUS in config file.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_status():
    """ Get complete url to query uframe status ('uframe-host:12587/status/inv')
    """
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        uframe_url = '/'.join([current_app.config['UFRAME_DEPLOYMENTS_URL'], get_status_url_base()])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for status using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


def get_url_info_status_inv():
    """ Get complete url to query uframe cruises ('uframe-host:12587/status/inv')
    """
    try:
        url, timeout, timeout_read = get_url_info_status()
        uframe_url = '/'.join([url, 'inv'])
        return uframe_url, timeout, timeout_read
    except:
        message = 'Unable to form uframe url for status using config file variables.'
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common utility functions
# todo - note controller.py requires review, mods and test for try/except before using.
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




