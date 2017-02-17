#!/usr/bin/env python

"""
Asset Management - Deployments: supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.config import (get_deployments_url_base, get_uframe_deployments_info)
from ooiservices.app.uframe.common_tools import (is_instrument, is_platform, is_mooring,get_location_fields)
from ooiservices.app.uframe.vocab import (get_vocab_dict_by_rd, get_rs_array_name_by_rd,
                                          get_display_name_by_rd, get_vocab)
from ooiservices.app.uframe.uframe_tools import (uframe_get_deployment_inv, uframe_get_deployment_inv_nodes,
                                                 uframe_get_deployment_inv_sensors, get_deployments_digest_by_uid)

import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
from copy import deepcopy


def format_deployment_for_ui(modified_deployment):
    """ Format uframe deployment into ui deployment.
    """
    debug = False
    updated_deployment = {}
    regular_fields = ['assetUid', 'dataSource', 'deployedBy', 'deploymentNumber',
                      'editPhase', 'eventId', 'eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                      'inductiveId', 'lastModifiedTimestamp', 'notes', 'recoveredBy', 'versionNumber', 'waterDepth']
    try:
        if debug: print '\n debug -- Entered format_deployment_for_ui...'
        # Process location information.
        latitude = None
        longitude = None
        depth = None
        orbitRadius = None
        if 'location' in modified_deployment:
            if debug: print '\n debug -- Have location...'
            if modified_deployment['location'] is not None:
                if debug: print '\n\t debug -- Location is not None...'
                tmp = deepcopy(modified_deployment['location'])
                if debug: print '\n\t debug -- Location: tmp: ', tmp
                latitude, longitude, depth, orbitRadius, loc_list = get_location_fields(tmp)
                if debug:
                    print '\n\t debug -- latitude: ', latitude
                    print '\n\t debug -- longitude: ', longitude
                    print '\n\t debug -- depth: ', depth
                    print '\n\t debug -- orbitRadius: ', orbitRadius

        updated_deployment['latitude'] = latitude
        updated_deployment['longitude'] = longitude
        updated_deployment['depth'] = depth
        updated_deployment['orbitRadius'] = orbitRadius

        # Get reference designator from attribute 'referenceDesignator'.
        rd = None
        if 'referenceDesignator' in modified_deployment:
            rd = modified_deployment['referenceDesignator']
        if not is_instrument(rd):
            message = 'The referenceDesignator provided cannot be formed into instrument reference designator.'
            raise Exception(message)

        updated_deployment['rd'] = rd
        updated_deployment['lastModifiedTimestamp'] = modified_deployment['lastModifiedTimestamp']

        # Get mooring, node and sensor uid values.
        mooring_uid = None
        node_uid = None
        sensor_uid = None
        if 'mooring' in modified_deployment:
            if modified_deployment['mooring']:
                if 'uid' in modified_deployment['mooring']:
                    if modified_deployment['mooring']['uid']:
                        mooring_uid = modified_deployment['mooring']['uid'][:]
                    else:
                        mooring_uid = None
            #del modified_deployment['mooring']
        if 'node' in modified_deployment:
            if modified_deployment['node']:
                if 'uid' in modified_deployment['node']:
                    if modified_deployment['node']['uid']:
                        node_uid = modified_deployment['node']['uid'][:]
                    else:
                        node_uid = None
            #del modified_deployment['node']
        if 'sensor' in modified_deployment:
            if modified_deployment['sensor']:
                if 'uid' in modified_deployment['sensor']:
                    if modified_deployment['sensor']['uid']:
                        sensor_uid = modified_deployment['sensor']['uid'][:]
                    else:
                        sensor_uid = None
        updated_deployment['mooring_uid'] = mooring_uid
        updated_deployment['node_uid'] = node_uid
        updated_deployment['sensor_uid'] = sensor_uid

        # Get deployCruiseInfo, recoverCruiseInfo and ingestInfo.
        updated_deployment['deployCruiseInfo'] = None
        if modified_deployment['deployCruiseInfo'] is not None:
            if 'uniqueCruiseIdentifier' in modified_deployment['deployCruiseInfo']:
                updated_deployment['deployCruiseInfo'] = modified_deployment['deployCruiseInfo']['uniqueCruiseIdentifier']
        updated_deployment['recoverCruiseInfo'] = None
        if modified_deployment['recoverCruiseInfo'] is not None:
            if 'uniqueCruiseIdentifier' in modified_deployment['recoverCruiseInfo']:
                updated_deployment['recoverCruiseInfo'] = modified_deployment['recoverCruiseInfo']['uniqueCruiseIdentifier']

        # Deprecate
        # Hide ingestInfo until further notice; need api in uframe for ingestInfo (an api similar to remoteResources)
        updated_deployment['ingestInfo'] = None
        """
        if modified_deployment['ingestInfo'] is not None:
            updated_deployment['ingestInfo'] = None #deepcopy(modified_deployment['ingestInfo'])
        """

        # Get the rest of the fields and values.
        for key in regular_fields:
            if key in modified_deployment:
                updated_deployment[key] = modified_deployment[key]
                if debug:
                    if key == 'editPhase':
                        print '\n debug -- The modified deployment value for editPhase is: ', modified_deployment[key]

        if not updated_deployment or updated_deployment is None:
            raise Exception('Deployment compilation failed to return a result.')

        # Note: This must remain until uframe editPhase changes are finalized.
        updated_deployment['editPhase'] = 'OPERATIONAL'
        if debug: print '\n debug -- Final value for editPhase (to be returned is): ', updated_deployment['editPhase']

        if 'location' in updated_deployment:
            del updated_deployment['location']

        if debug: print '\n debug -- Exit format_deployment_for_ui...'
        return updated_deployment

    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_rd_deployments(rd):
    """ Get all deployments for reference designator, whether mooring, platform or instrument.

    Use urls such as:
        (http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326-04-DOSTAM000)
         http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326
         http://host:12587/events/deployment/query?refdes=CE05MOAS
         http://host:12587/events/deployment/query?refdes=CP02PMUI
    """
    check = False
    result = []
    try:
        # Verify rd is valid.
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator %s is not a mooring, platform or instrument.' % rd
            current_app.logger.info(message)
            return result

        # Get uframe deployments request variables
        uframe_url, timeout, timeout_read = get_uframe_deployments_info()

        # Build uframe url: host:port/events/deployment/query?refdes=XXXXXXXX
        url = '/'.join([uframe_url, get_deployments_url_base(), 'query'])
        url += '?refdes=' + rd
        #url += '?refdes=' + rd + '&notes=true'
        if check: print '\n Check -- [get_rd_deployments] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get deployments from uframe for %r.' % rd
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Timeout for for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []


def get_rd_deployments_with_notes(rd):
    """ Get all deployments for reference designator, whether mooring, platform or instrument.

    Use urls such as:
        (http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326-04-DOSTAM000)
         http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326&notes=true
         http://host:12587/events/deployment/query?refdes=CE05MOAS
         http://host:12587/events/deployment/query?refdes=CP02PMUI
         http://host:12587/events/deployment/inv/GS01SUMO/SBD12/08-FDCHPA000/-1?note=true
    """
    check = False
    result = []
    try:
        # Verify rd is valid.
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator %s is not a mooring, platform or instrument.' % rd
            current_app.logger.info(message)
            return result

        # Get uframe deployments request variables
        uframe_url, timeout, timeout_read = get_uframe_deployments_info()

        # Build uframe url: host:port/events/deployment/query?refdes=XXXXXXXX
        url = '/'.join([uframe_url, get_deployments_url_base(), 'query'])
        #url += '?refdes=' + rd
        url += '?refdes=' + rd + '&notes=true'
        if check: print '\n Check -- [get_rd_deployments] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get deployments from uframe for %r.' % rd
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Timeout for for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []


def get_rd_deployment(rd, deployment_number):
    """ Get all deployments for reference designator, whether mooring, platform or instrument.

    Use urls such as:
        (http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326-04-DOSTAM000)
         http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326
         http://host:12587/events/deployment/query?refdes=CE05MOAS
         http://host:12587/events/deployment/query?refdes=CP02PMUI
    """
    check = False
    deployment = None
    try:
        # Check deployment_number
        if deployment_number < 1:
            message = 'The deployment number provided (%d) is invalid.' % deployment_number
            raise Exception(message)

        # Verify rd is valid.
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator \'%s\' is not a mooring, platform or instrument.' % rd
            current_app.logger.info(message)
            return result

        # Get uframe deployments request variables
        uframe_url, timeout, timeout_read = get_uframe_deployments_info()

        # Build uframe url: host:port/events/deployment/query?refdes=XXXXXXXX
        url = '/'.join([uframe_url, get_deployments_url_base(), 'query'])
        url += '?refdes=' + rd
        if check: print '\n Check -- [get_rd_deployments] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get deployments from uframe for %r.' % rd
            raise Exception(message)
        results = response.json()

        # If result, then get deployment_number, if available, from result.
        if results:
            for result in results:
                if result:
                    if 'deploymentNumber' in result:
                        if result['deploymentNumber'] == deployment_number:
                            deployment = result
                            break
        return deployment

    except ConnectionError:
        message = 'ConnectionError for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Timeout:
        message = 'Timeout for for uframe get_rd_deployments %s.' % rd
        current_app.logger.info(message)
        return []
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []


def _get_deployment_subsites():
    """ Get deployment inventory for subsites.
    Sample response:
        {
          "subsites": {
            "CE01ISSM": {
              "array": "Coastal Endurance",
              "name": "Oregon Inshore Surface Mooring",
              "rd": "CE01ISSM"
            },
            ...
            ,
            "CE04OSSM": {
              "array": "Coastal Endurance",
              "name": "Oregon Offshore Surface Mooring",
              "rd": "CE04OSSM"
            },
          }
        }
    """
    results = None
    try:
        result_list = uframe_get_deployment_inv()
        results = process_rds_for_names(result_list)
        return results
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return results


def _get_deployment_nodes(subsite):
    """ Get uframe deployment inventory list of nodes for a subsite.
    Sample
        request: http://localhost:4000/uframe/deployments/inv/CE04OSSM
        response:
            {
              "nodes": {
                "RIC21": {
                  "array": "Coastal Endurance",
                  "name": "Oregon Offshore Surface Mooring - Near Surface Instrument Frame",
                  "rd": "CE04OSSM-RIC21"
                },
                "RID26": {
                  "array": "Coastal Endurance",
                  "name": "Oregon Offshore Surface Mooring - Near Surface Instrument Frame",
                  "rd": "CE04OSSM-RID26"
                },
                ...
              }
            }
    """
    results = None
    try:
        result_list = uframe_get_deployment_inv_nodes(subsite)
        results = process_rds_for_names(result_list, subsite)
        return results
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return results


def _get_deployment_sensors(subsite, node):
    """ Get uframe deployment inventory list of sensors for a subsite and node.
    Sample:
        request: http://localhost:4000/uframe/deployments/inv/CE04OSSM/RID27
        response:
        {
          "sensors": {
            "00-DCLENG000": {
              "array": "Coastal Endurance",
              "name": "Data Concentrator Logger (DCL)",
              "rd": "CE04OSSM-RID27-00-DCLENG000"
            },
            "01-OPTAAD000": {
              "array": "Coastal Endurance",
              "name": "Spectrophotometer",
              "rd": "CE04OSSM-RID27-01-OPTAAD000"
            },
            ...
            }
        }

    """
    results = None
    try:
        result_list = uframe_get_deployment_inv_sensors(subsite, node)
        results = process_rds_for_names(result_list, subsite, node)
        return results
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return results


def process_rds_for_names(rds, subsite=None, node=None):
    """ For each rd in list, get vocab name and long name. Return list of dictionaries.
    """
    results = []
    try:
        for rd_dict in rds:

            # Get the key
            if isinstance(rd_dict, dict):
                rd = rd_dict['key']
            else:
                rd = rd_dict

            # Form prefix
            if subsite is not None and node is None:
                prefix = subsite
            elif subsite is not None and node is not None:
                prefix = '-'.join([subsite, node])
            else:
                prefix = None
            if prefix is not None:
                tmp_rd = '-'.join([prefix, rd])
            else:
                tmp_rd = rd
            # Populate the dictionary, add to list.
            tmp = {'key': rd, 'rd': tmp_rd, 'name': '', 'array': ''}
            tmp['name'], tmp['array'] = get_vocab_info(tmp_rd)
            results.append(tmp)
        return results
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return results


def get_vocab_info(rd):
    try:
        # Get array name
        if rd[:2] == 'RS':
            if len(rd) >= 8:
                array = get_rs_array_name_by_rd(rd[:8])
            else:
                array = get_display_name_by_rd(rd[:2])
        else:
            array = get_display_name_by_rd(rd[:2])

        # Get name for reference designator from vocabulary.
        vocab_dict = get_vocab_dict_by_rd(rd)
        if vocab_dict:
            name = vocab_dict['name']
        else:
            name = rd
        return name, array
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return results


# Get list of deployments for reference designator, return formatted for ui.
def _get_deployments_by_rd(rd):
    """ Get list of deployments for a reference designator; return formatted for UI.
    """
    ui_deployments = []
    try:
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator provided (\'%s\') is not a mooring, platform or instrument.' % rd
            raise Exception(message)

        # Get vocabulary dictionary once.
        vocab_dict = get_vocab()

        # Get deployment event from uframe.
        uframe_deployments = get_rd_deployments_with_notes(rd)
        if not uframe_deployments or uframe_deployments is None:
            message = 'Failed to get deployments using reference designator \'%s\' from uframe.' % rd
            raise Exception(message)

        # Format deployment event for ui.
        for uframe_deployment in uframe_deployments:
            ui_deployment = format_deployment_for_ui(uframe_deployment)
            if not ui_deployment or ui_deployment is None:
                continue

            # (10506) Add maxdepth as depth for mobile assets (MOAS)
            if 'MOAS' in ui_deployment['rd']:
                if ui_deployment['rd'] in vocab_dict:
                    ui_deployment['depth'] = vocab_dict[ui_deployment['rd']]['maxdepth']

            ui_deployments.append(ui_deployment)
        return ui_deployments

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get list of deployments for uid, return formatted for ui.
def _get_deployments_digest_by_uid(uid):
    """ Get list of deployments for a reference designator; return digests.
    (See also event_tools.py, get_deployment_events. Supports asset management Deployment tab.)
    """
    results = []
    try:
        # Get vocabulary dictionary once.
        vocab_dict = get_vocab()

        # Get deployment event from uframe.
        uframe_deployments = get_deployments_digest_by_uid(uid)
        print '\n uframe_deployment[0]: ', uframe_deployments[0]
        if not uframe_deployments or uframe_deployments is None:
            message = 'Failed to get deployments from uframe for uid \'%s\' .' % uid
            raise Exception(message)

        # (10506) Check for mobile assets and use maxdepth as depth for mobile assets (MOAS).
        # Note: the maxdepth value used across current and past deployments will be the current
        # maxdepth setting from vocabulary for the reference designator.
        for uframe_deployment in uframe_deployments:
            if 'MOAS' in uframe_deployment['subsite']:
                rd = get_rd_from_deployment_digest(uframe_deployment)
                if rd and rd is not None:
                    if rd in vocab_dict:
                        uframe_deployment['depth'] = vocab_dict[rd]['maxdepth']
            results.append(uframe_deployment)
        return results
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_rd_from_deployment_digest(uframe_deployment):
    """ Get reference designator from
    """
    result = None
    try:
        if not uframe_deployment:
            return result
        if 'subsite' not in uframe_deployment:
            return result
        if 'subsite' in uframe_deployment:
            if not uframe_deployment['subsite']:
                return result
            if 'node' in uframe_deployment:
                if not uframe_deployment['node']:
                    return str(uframe_deployment['subsite'])
                if 'sensor' in uframe_deployment:
                    if not uframe_deployment['sensor']:
                        result = '-'.join([str(uframe_deployment['subsite']), str(uframe_deployment['node'])])
                    else:

                        result = '-'.join([str(uframe_deployment['subsite']), str(uframe_deployment['node']),
                                       str(uframe_deployment['sensor'])])

        return result
    except Exception as err:
        message = str(err)
        print '\n debug -- message: ', message
        #raise Exception(message)
        return None

