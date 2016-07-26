#!/usr/bin/env python

"""
Support functions used for configurations and connection to uframe for:
    toc
    assets
    events
    deployments
    vocabulary
    c2
    c2 toc
    c2 missions
    alertsalarms

"""
__author__ = 'Edna Donoughe'

from flask import current_app


# todo - note controller.py requires review, modifications and test for try/except before using.
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


def get_uframe_info():
    """ Get uframe configuration information. (uframe_url, uframe timeout_connect and timeout_read.) """
    timeout, timeout_read = get_uframe_timeout_info()
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    return uframe_url, timeout, timeout_read


# toc
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


# assets
def get_assets_url_base():
    """ 'asset' """
    assets = current_app.config['UFRAME_ASSETS']
    return assets


def get_asset_types():
    asset_types = ['Sensor', 'notClassified', 'Mooring', 'Node', 'Array']
    return asset_types

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


# events
def get_events_url_base():
    events = current_app.config['UFRAME_EVENTS']
    return events


def get_all_event_types():
    event_types = ['UNSPECIFIED', 'CALIBRATION_DATA', 'PURCHASE', 'DEPLOYMENT', 'RECOVERY', 'STORAGE',
                   'ATVENDOR', 'RETIREMENT', 'LOCATION', 'INTEGRATION', 'ASSET_STATUS', 'CRUISE_INFO']
    return event_types

def get_event_types(rd):
    len_rd = len(rd)
    event_types = ['UNSPECIFIED', 'PURCHASE', 'DEPLOYMENT', 'RECOVERY', 'STORAGE',
                    'ATVENDOR', 'RETIREMENT', 'LOCATION', 'INTEGRATION', 'ASSET_STATUS', 'CRUISE_INFO']

    # For instruments add event type 'CALIBRATION_DATA'
    if len_rd >14 and len_rd <=27:
        event_types.append('CALIBRATION_DATA')

    return event_types


# deployments
def get_deployments_url_base():
    """'events/deployment """
    deployments = current_app.config['UFRAME_DEPLOYMENTS']
    return deployments


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


# vocabulary
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
# todo - not yet incorporated into c2.py
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# c2
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


# c2 toc
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



# c2 missions
# todo - review how exception handling c2_mission.py, then add try/except block here
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
# todo - review how exception handling c2_mission.py, then add try/except block here
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# alertalarms
def get_uframe_alerts_info():
    """ Get uframe alertalarm configuration information. """
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


# Common utility functions
def _uframe_headers():
    """
    No special headers are needed to connect to uframe.  This simply states
    the default content type, and would be where authentication would/could be added.
    """
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def headers():
    """ Headers for uframe PUT and POST. """
    return {"Content-Type": "application/json"}




