#!/usr/bin/env python

"""
Asset Management - Deployments: supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.toc_tools import (get_toc_reference_designators)
from ooiservices.app.uframe.common_tools import (is_instrument, is_platform, is_mooring, dump_dict)
from ooiservices.app.uframe.config import (get_deployments_url_base, get_uframe_deployments_info,
                                           get_url_info_deployments_inv)
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
                      'inductiveId', 'lastModifiedTimestamp', 'notes', 'recoveredBy', 'versionNumber']
    try:
        if debug: print '\n debug -- format_deployment_for_ui - Step 1...'
        # Get values from location dictionary.
        latitude = 0.0
        longitude = 0.0
        depth = 0.0
        orbitRadius = 0.0
        updated_deployment['location'] = None
        if 'location' in modified_deployment:
            if debug: print '\n debug -- location in modified deployment'
            if modified_deployment['location'] is not None:
                updated_deployment['location'] = {}
                if debug: print '\n debug -- location is not None'
                if 'latitude' in modified_deployment['location']:
                    latitude = modified_deployment['location']['latitude']
                if 'longitude' in modified_deployment['location']:
                    longitude = modified_deployment['location']['longitude']
                if 'depth' in modified_deployment['location']:
                    if debug: print '\n debug -- depth in modified_deployment'
                    depth = modified_deployment['location']['depth']
                    if debug: print '\n debug -- depth in modified_deployment: ', depth
                if 'orbitRadius' in modified_deployment['location']:
                    orbitRadius = modified_deployment['location']['orbitRadius']
                if latitude is None or longitude is None:
                    updated_deployment['latitude'] = None
                    updated_deployment['longitude'] = None
                    updated_deployment['location']['location'] = []
                else:
                    updated_deployment['latitude'] = latitude
                    updated_deployment['longitude'] = longitude
            updated_deployment['depth'] = depth
            updated_deployment['orbitRadius'] = orbitRadius
            updated_deployment['tense'] = modified_deployment['tense']

        if debug:
            print '\n debug -- value of depth now: ', depth
            updated_deployment['depth'] = depth

        # Get reference designator from attribute 'referenceDesignator'.
        if debug: print '\n debug -- format_deployment_for_ui - Step 2...'
        rd = None
        subsite = None
        node = None
        sensor = None
        if 'referenceDesignator' in modified_deployment:
            if 'subsite' in modified_deployment['referenceDesignator']:
                subsite = modified_deployment['referenceDesignator']['subsite']
            if 'node' in modified_deployment['referenceDesignator']:
                node = modified_deployment['referenceDesignator']['node']
            if 'sensor' in modified_deployment['referenceDesignator']:
                sensor = modified_deployment['referenceDesignator']['sensor']
            if subsite is None or node is None or sensor is None:
                message = 'The subsite, node or sensor provided for deployment is empty.'
                raise Exception(message)
            rd = '-'.join([subsite, node, sensor])
        if debug: print '\n debug -- rd: ', rd
        if not is_instrument(rd):
            message = 'The referenceDesignator provided cannot be formed into instrument reference designator.'
            raise Exception(message)

        if debug: print '\n debug -- format_deployment_for_ui - Step 3...'
        updated_deployment['rd'] = rd
        updated_deployment['lastModifiedTimestamp'] = modified_deployment['lastModifiedTimestamp']

        # Get mooring, node and sensor uid values.
        if debug: print '\n debug -- format_deployment_for_ui - Step 4...'
        mooring_uid = None
        node_uid = None
        sensor_uid = None
        if debug: print '\n debug -- format_deployment_for_ui - Step 4a...'
        if 'mooring' in modified_deployment:
            if modified_deployment['mooring']:
                if 'uid' in modified_deployment['mooring']:
                    if modified_deployment['mooring']['uid']:
                        mooring_uid = modified_deployment['mooring']['uid'][:]
                    else:
                        mooring_uid = None
            #del modified_deployment['mooring']
        if debug: print '\n debug -- format_deployment_for_ui - Step 4b...'
        if 'node' in modified_deployment:
            if modified_deployment['node']:
                if 'uid' in modified_deployment['node']:
                    if modified_deployment['node']['uid']:
                        node_uid = modified_deployment['node']['uid'][:]
                    else:
                        node_uid = None
            #del modified_deployment['node']
        if debug: print '\n debug -- format_deployment_for_ui - Step 4c...'
        if 'sensor' in modified_deployment:
            if modified_deployment['sensor']:
                if 'uid' in modified_deployment['sensor']:
                    if modified_deployment['sensor']['uid']:
                        sensor_uid = modified_deployment['sensor']['uid'][:]
                    else:
                        sensor_uid = None
            #del modified_deployment['sensor']
        updated_deployment['mooring_uid'] = mooring_uid
        updated_deployment['node_uid'] = node_uid
        updated_deployment['sensor_uid'] = sensor_uid

        if debug: print '\n debug -- format_deployment_for_ui - Step 5...'
        # Get deployCruiseInfo, recoverCruiseInfo and ingestInfo.
        updated_deployment['deployCruiseInfo'] = None
        if modified_deployment['deployCruiseInfo'] is not None:
            updated_deployment['deployCruiseInfo'] = deepcopy(modified_deployment['deployCruiseInfo'])
        updated_deployment['recoverCruiseInfo'] = None
        if modified_deployment['recoverCruiseInfo'] is not None:
            updated_deployment['recoverCruiseInfo'] = deepcopy(modified_deployment['recoverCruiseInfo'])
        updated_deployment['ingestInfo'] = None
        if modified_deployment['ingestInfo'] is not None:
            updated_deployment['ingestInfo'] = deepcopy(modified_deployment['ingestInfo'])

        # Get the rest of the fields and values.
        if debug: print '\n debug -- format_deployment_for_ui - Step 6...'
        for key in regular_fields:
            if key in modified_deployment:
                #updated_deployment[key] = modified_deployment.pop(key)
                updated_deployment[key] = modified_deployment[key]
        if not updated_deployment or updated_deployment is None:
            raise Exception('Deployment compilation failed to return a result.')

        # todo - check uframe required fields for deployments

        if debug:
            print '\n debug -- ui formatted deployment(%d): ' % len(updated_deployment)
            dump_dict(updated_deployment, debug)

        if debug: print '\n debug -- format_deployment_for_ui - Step 7...'

        return updated_deployment

    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- format_deployment_for_ui exception: ', message
        raise Exception(message)


# todo - finish
def refresh_deployment_cache(id, deployment, action, remote_id=None):
    """ Perform asset cache add or update depending on action provided.
    """
    debug = False
    try:
        if action == 'create':
            #deployment_cache_add(id, deployment)
            if debug: print '\n debug -- refresh_deployment_cache -- finish %s' % action
        elif action == 'update':
            #update_deployment_cache(id, deployment, remote_id)
            if debug: print '\n debug -- refresh_deployment_cache -- finish %s' % action
        else:
            message = 'Failed to refresh deployment cache, unknown action(\'%s\').' % action
            raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# New: Deployments added to rd information inventory
def _compile_rd_assets():
    """ Get dictionary, keyed by reference designator, holding reference maps for deployments and asset_ids.

    For a reference designator, this function is used to determine the following [deployment based] information:
        all associated asset ids
        all associated asset ids by type
        deployment(s) for each associated asset id
        list of deployment numbers
        current_deployment_number
        for a deployment:
            asset ids referenced,
            asset ids referenced by type
            location information
            beginDT
            endDT
            tense
        asset id specific deployment information

    This supports all reference designators referenced in /sensor/inv/toc structure; On error, log and raise exception.
    Note: All reference designators are determined from toc structure and not just what /sensor/inv/toc provides.
    """
    result = {}
    try:
        reference_designators, toc_only, difference  = get_toc_reference_designators()
        if reference_designators and toc_only:
            result = get_rd_assets(reference_designators)
        return result

    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}


def get_rd_assets(reference_designators):
    """ Create rd_asset dictionary for reference designators provided.
    """
    debug = False
    result = {}
    try:
        for rd in reference_designators:
            try:
                if debug: print '\n debug ====================================================== rd: ', rd
                # If reference designator for instrument, get dictionary map to add to result
                if (is_instrument(rd)):
                    if rd not in result:
                        work = get_instrument_deployment_work(rd)
                        if work:
                            if work['asset_ids']:       # work['asset_ids_by_type']
                                result[rd] = work
                    else:
                        if debug: print '\n debug -- instrument rd %s is a duplicate in reference_designators!' % rd

                elif(is_mooring(rd)):
                    if rd not in result:
                        work = get_mooring_deployment_work(rd)
                        if work:
                            result[rd] = work
                    else:
                        if debug: print '\n debug -- mooring rd %s is a duplicate in reference_designators!' % rd

                elif (is_platform(rd)):
                    if rd not in result:
                        work = get_platform_deployment_work(rd)
                        if work:
                            result[rd] = work
                    else:
                        if debug: print '\n debug -- platform rd %s is a duplicate in reference_designators!' % rd
                else:
                    if debug: print '\n debug -- %s not instrument, platform or mooring...' % rd

            except Exception as err:
                message = 'Exception raised in _compile_rd_assets: %s' % str(err)
                raise Exception(message)
        return result

    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}


def get_instrument_deployments_list(rd):
    """ Get list of deployments for instrument rd.
    """
    check = False
    result = []
    try:
        # Verify rd is valid format
        if not(is_instrument(rd)):
            return result

        # Process rd into query_rd for deployments request
        subsite, node, sensor = rd.split('-', 2)
        query_rd = '/'.join([subsite, node, sensor])

        # Get uframe deployments request variables
        uframe_url, timeout, timeout_read = get_uframe_deployments_info()

        # Build uframe url: host:port/events/deployment/inv/mooring/node/sensor
        url = '/'.join([uframe_url, get_deployments_url_base(), 'inv', query_rd])
        if check: print '\n check -- [get_instrument_deployments_list] url: ', url

        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get deployments list from uframe for %r.' % (response.status_code, rd)
            current_app.logger.info(message)
            raise Exception(message)

        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError uframe getting instrument %s deployments.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout uframe getting instrument %s deployments.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        print '\n-- [get_instrument_deployments_list]: ', message
        current_app.logger.info(message)
        return None


# todo - review to replace with get_rd_deployments(rd)
def get_instrument_deployments(rd):
    """ Get all deployments for instrument rd.

    Use: http://host:12587/deployments/inv/CE05MOAS/GL326/04-DOSTAM000/-1
    """
    check = False
    result = []
    try:
        # Verify rd is valid format
        if not(is_instrument(rd)):
            return result

        # Process rd into query_rd for deployments request
        subsite, node, sensor = rd.split('-', 2)
        query_rd = '/'.join([subsite, node, sensor])

        # Get uframe deployments request variables
        uframe_url, timeout, timeout_read = get_uframe_deployments_info()
        #url = '/'.join([uframe_url, 'deployments', 'inv', query_rd, '-1'])
        url = '/'.join([uframe_url, get_deployments_url_base(), 'inv', query_rd, '-1'])
        if check: print '\n check -- [get_instrument_deployments] url: ', url

        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get all deployments from uframe for  %r.' % (response.status_code, rd)
            current_app.logger.info(message)
            raise Exception(message)

        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError uframe get_instrument_deployments for %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout uframe get_instrument_deployments for %s.' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
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
    check = True
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


'''
def get_deployments_inv_by_rd(rd):
    """ Get all deployments for an instrument reference designator.
    Note: The deployment inventory query will only return deployments for instrument reference designators.

    Use this to get all of the deployments:
        http://host:12587/events/deployment/inv/GS01SUMO/SBD12/08-FDCHPA000/-1
    """
    debug = False
    check = False
    result = []
    try:
        # Verify rd is valid.
        if not is_instrument(rd):
            message = 'The reference designator \'%s\' is not an instrument.'
            current_app.logger.info(message)
            return result

        # Build query suffix for reference designator.
        rd_suffix = ''
        subsite, node, sensor = rd.split('-', 2)
        if subsite and subsite is not None:
            rd_suffix = '/'.join([rd_suffix, subsite])
            if node and node is not None:
                rd_suffix = '/'.join([rd_suffix, node])
                if sensor and sensor is not None:
                    rd_suffix = '/'.join([rd_suffix, sensor])
        if rd_suffix:
            rd_suffix = rd_suffix.strip('/')
            rd_suffix = '/'.join([rd_suffix, '-1'])
        else:
            if debug: print '\n debug -- Unable to determine an rd_suffix for rd: %s' % rd
            return result

        if debug: print '\n debug -- rd_suffix: ', rd_suffix
        # Get uframe deployments inventory request variables
        uframe_url, timeout, timeout_read = get_url_info_deployments_inv()
        url = '/'.join([uframe_url, rd_suffix])
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
'''

def get_mooring_deployments_list(rd):
    """ Get list of deployments for mooring reference designator.
    """
    debug = False
    result = []
    results = {}
    try:
        if debug: print '\n debug -- get_mooring_deployments_list for rd: ', rd

        # Verify rd is valid format
        if not(is_mooring(rd)):
            if debug: print '\n debug -- %s is not a mooring id: ', rd
            return result, results

        # Get all deployments associated with this mooring rd
        mooring_deployments = get_rd_deployments(rd)
        if not mooring_deployments or mooring_deployments is None:
            # If no deployments, return empty result and results ([], {})
            if debug: print '\n debug -- get_mooring_deployments_list for rd %s: No deployments' % rd
            return result, results
        else:
            if debug: print '\n debug -- get_mooring_deployments_list: len(mooring_deployments): ', len(mooring_deployments)

        deployments_list = []
        all_asset_ids = []
        results = {}
        results['asset_ids'] = []
        results['asset_ids_by_type'] = {'sensor': [], 'mooring': [], 'node': []}
        for item in mooring_deployments:
            info = {}
            info['asset_ids'] = []
            info['asset_ids_by_type'] = {'sensor': [], 'mooring': [], 'node': []}
            deployment_asset_ids = []
            deployment_number = None
            if 'deploymentNumber' in item:
                deployment_number = item['deploymentNumber']

            location = None
            if 'location' in item:
                location = item['location']

            # Get deployment beginDT and endDT
            beginDT = None
            if 'eventStartTime' in item:
                beginDT = item['eventStartTime']

            endDT = None
            if 'eventStopTime' in item:
                endDT = item['eventStopTime']

            eventId = None
            if 'eventId' in item:
                eventId = item['eventId']

            tense = None
            if 'tense' in item:
                tense = item['tense']

            asset_id = None
            if 'mooring' in item:

                # Get 'mooring' component from item, check it empty or None.
                _item = item['mooring']
                if not _item or _item is None:
                    #return [], {}
                    continue

                # Process 'node' attribute in this deployment item.
                if 'assetId' in _item:
                    if _item['assetId']:
                        asset_id = _item['assetId']
                        if asset_id not in all_asset_ids:
                            all_asset_ids.append(asset_id)

                if deployment_number:
                    if asset_id:
                        if asset_id not in deployment_asset_ids:
                            deployment_asset_ids.append(asset_id)

                    info[deployment_number] = {}
                    info[deployment_number]['asset_ids_by_type'] = {'sensor': [], 'mooring': deployment_asset_ids, 'node': []}
                    if deployment_number not in deployments_list:
                        deployments_list.append(deployment_number)

                    # Processing deployment location and times...
                    # Valuable luggage
                    info[deployment_number]['location'] = location
                    info[deployment_number]['beginDT'] = beginDT
                    info[deployment_number]['endDT'] = endDT
                    info[deployment_number]['eventId'] = eventId
                    info[deployment_number]['tense'] = tense

                    if deployment_asset_ids:
                        deployment_asset_ids.sort()
                    info[deployment_number]['asset_ids'] = deployment_asset_ids

            if info:
                results.update(info)

        if all_asset_ids:
            all_asset_ids.sort()
        result = deployments_list
        results['deployments'] = deployments_list
        results['asset_ids'] = all_asset_ids
        results['asset_ids_by_type'] = {'sensor': [], 'mooring': all_asset_ids, 'node': []}

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get current deployment number, if there are deployment(s); set tense for each deployment.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not deployments_list:
            message = 'Mooring %s does not have a deployments_list!' % rd
            print '\n debug -- [get_mooring_deployments_list] (list) result: ', result
            current_app.logger.info(message)

        if deployments_list:
            deployments_list.sort(reverse=True)
            current_deployment_number = deployments_list[0]

            # Set tense to Past if deployment number not equal to current_deployment_number
            # Get 'cumulative_tense' for each deployment
            for num in deployments_list:
                tense = 'PAST'
                if num == current_deployment_number:
                    tense = 'PRESENT'
                results[num]['cumulative_tense'] = tense

        if debug:
            print '\n debug -- [get_mooring_deployments_list] (list) result: ', result
            #print '\n debug -- results: ', json.dumps(results, indent=4, sort_keys=True)

        return result, results

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_mooring_deployments_list]: ', message
        current_app.logger.info(message)
        return None, None


def get_platform_deployments_list(rd):
    """ Get list of deployments for mooring reference designator.
    """
    debug = False
    result = []
    results = {}
    try:
        if debug: print '\n debug -- get_platform_deployments_list for rd: ', rd

        # Verify rd is valid format
        if not(is_platform(rd)):
            return result, results

        # Get all deployments associated with this platform rd
        platform_deployments = get_rd_deployments(rd)
        if not platform_deployments or platform_deployments is None:
            # If no deployments, return empty result and results ([], {})
            if debug: print '\n debug -- get_platform_deployments_list for rd %s: No deployments' % rd
            return result, results
        deployments_list = []
        all_asset_ids = []
        results = {}
        results['asset_ids'] = []
        results['asset_ids_by_type'] = {'sensor': [], 'mooring': [], 'node': []}

        for item in platform_deployments:
            info = {}
            info['asset_ids'] = []
            info['asset_ids_by_type'] = {'sensor': [], 'mooring': [], 'node': []}
            deployment_asset_ids = []
            deployment_number = None
            if 'deploymentNumber' in item:
                deployment_number = item['deploymentNumber']
            if debug: print '\n debug -- deployment_number: ', deployment_number

            location = None
            if 'location' in item:
                location = item['location']
            if debug: print '\n debug -- location: ', location

            # Get deployment beginDT and endDT
            beginDT = None
            if 'eventStartTime' in item:
                beginDT = item['eventStartTime']

            endDT = None
            if 'eventStopTime' in item:
                endDT = item['eventStopTime']

            eventId = None
            if 'eventId' in item:
                eventId = item['eventId']

            tense = None
            if 'tense' in item:
                tense = item['tense']

            asset_id = None
            if 'node' in item:

                # Get 'node' component from item, check it empty or None.
                _item = item['node']
                if not _item or _item is None:
                    #return [], {}
                    continue

                # Process 'node' attribute in this deployment item.
                if 'assetId' in _item:
                    if _item['assetId']:
                        asset_id = _item['assetId']
                        if asset_id not in all_asset_ids:
                            all_asset_ids.append(asset_id)

                if debug: print '\n debug -- all_asset_ids: ', all_asset_ids
                if deployment_number:
                    if debug: print '\n debug -- have deployment_number... '
                    if asset_id:
                        if debug: print '\n debug -- have asset_id... '
                        if asset_id not in deployment_asset_ids:
                            if debug: print '\n debug -- add asset_id to deployment_asset_ids... '
                            deployment_asset_ids.append(asset_id)

                    if debug: print '\n debug -- processing info[deployment_number][asset_ids_by_type]...'
                    info[deployment_number] = {}
                    info[deployment_number]['asset_ids_by_type'] = {'sensor': [], 'mooring': [], 'node': deployment_asset_ids}
                    if deployment_number not in deployments_list:
                        deployments_list.append(deployment_number)
                    if debug: print '\n debug -- processing info[deployment_number][location]...'

                    # Valuable luggage
                    info[deployment_number]['location'] = location
                    info[deployment_number]['beginDT'] = beginDT
                    info[deployment_number]['endDT'] = endDT
                    info[deployment_number]['eventId'] = eventId
                    info[deployment_number]['tense'] = tense
                    if deployment_asset_ids:
                        deployment_asset_ids.sort()
                    info[deployment_number]['asset_ids'] = deployment_asset_ids

            if info:
                results.update(info)

        if all_asset_ids:
            all_asset_ids.sort()
        result = deployments_list
        results['deployments'] = deployments_list
        results['asset_ids'] = all_asset_ids
        results['asset_ids_by_type'] = {'sensor': [], 'mooring': [], 'node': all_asset_ids}

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get current deployment number, if there are deployment(s); set tense for each deployment.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if deployments_list:
            deployments_list.sort(reverse=True)
            current_deployment_number = deployments_list[0]

            # Set tense to Past if deployment number not equal to current_deployment_number
            # Get 'tense' for each deployment
            for num in deployments_list:
                tense = 'PAST'
                if num == current_deployment_number:
                    tense = 'PRESENT'
                results[num]['cumulative_tense'] = tense

        return result, results

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None, None


def get_deployment_asset_ids(deployment):
    """
    "referenceDesignator" :
        {
            "node" : "SP001",
            "full" : true,
            "subsite" : "CE01ISSP",
            "sensor" : "10-PARADJ000"
        },

    Sample deployment for reference designator CE01ISSP-SP001-10-PARADJ000:
    request:
        http://host:12587/deployments/inv/CE01ISSP/SP001/10-PARADJ000/1

    response:
        [{
          "@class" : ".XDeployment",
          "location" : {
            "depth" : 0.0,
            "location" : [ -124.09817, 44.6584 ],
            "longitude" : -124.09817,
            "latitude" : 44.6584,
            "orbitRadius" : 0.0
          },
          "node" : {
            "@class" : ".XNode",
            "events" : [ ],
            "assetId" : 3626,
            "serialNumber" : "WLP-001",
            "name" : "WLP-001",
            "location" : null,
            "description" : "Profiler, Coastal Surface Piercing",
            "physicalInfo" : {
              "height" : -1.0,
              "width" : -1.0,
              "length" : -1.0,
              "weight" : -1.0
            },
            "uid" : "N00121",
            "assetType" : "Node",
            "mobile" : false,
            "manufacturer" : "Wet Labs",
            "modelNumber" : "FAS-540601",
            "purchasePrice" : 29334.99,
            "purchaseDate" : 0,
            "deliveryDate" : null,
            "depthRating" : null,
            "dataSource" : "/home/asadev/uframes/uframe_ooi_20160616_ba553c7c2ce211a96098ac6db8d9b21688da8a7b/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
            "lastModifiedTimestamp" : 1467039100489
          },
          "sensor" : {
            "@class" : ".XInstrument",
            "calibration" : [ {
              "@class" : ".XCalibration",
              "name" : "CC_a0",
              "calData" : [ {
                "@class" : ".XCalibrationData",
                "values" : [ 4381.0 ],
                "dimensions" : [ 1 ],
                "cardinality" : 0,
                "comments" : null,
                "eventId" : 9951,
                "eventType" : "CALIBRATION_DATA",
                "eventName" : "CC_a0",
                "eventStartTime" : 1388534400000,
                "eventStopTime" : 1433077199000,
                "tense" : null,
                "dataSource" : null,
                "lastModifiedTimestamp" : 1467039232517
              } ]
            }, {
              "@class" : ".XCalibration",
              "name" : "CC_Im",
              "calData" : [ {
                "@class" : ".XCalibrationData",
                "values" : [ 1.3589 ],
                "dimensions" : [ 1 ],
                "cardinality" : 0,
                "comments" : null,
                "eventId" : 9952,
                "eventType" : "CALIBRATION_DATA",
                "eventName" : "CC_Im",
                "eventStartTime" : 1388534400000,
                "eventStopTime" : 1433077199000,
                "tense" : null,
                "dataSource" : null,
                "lastModifiedTimestamp" : 1467039232517
              } ]
            }, {
              "@class" : ".XCalibration",
              "name" : "CC_a1",
              "calData" : [ {
                "@class" : ".XCalibrationData",
                "values" : [ 2904.0 ],
                "dimensions" : [ 1 ],
                "cardinality" : 0,
                "comments" : null,
                "eventId" : 9953,
                "eventType" : "CALIBRATION_DATA",
                "eventName" : "CC_a1",
                "eventStartTime" : 1388534400000,
                "eventStopTime" : 1433077199000,
                "tense" : null,
                "dataSource" : null,
                "lastModifiedTimestamp" : 1467039232517
              } ]
            } ],
            "events" : [ ],
            "assetId" : 1850,
            "serialNumber" : "365",
            "name" : "365",
            "location" : null,
            "description" : "PARAD for WLP-001",
            "physicalInfo" : {
              "height" : -1.0,
              "width" : -1.0,
              "length" : -1.0,
              "weight" : -1.0
            },
            "uid" : "N00595",
            "assetType" : "Sensor",
            "mobile" : false,
            "manufacturer" : null,
            "modelNumber" : null,
            "purchasePrice" : 6775.0,
            "purchaseDate" : 0,
            "deliveryDate" : null,
            "depthRating" : null,
            "dataSource" : "/home/asadev/uframes/uframe_ooi_20160616_ba553c7c2ce211a96098ac6db8d9b21688da8a7b/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
            "lastModifiedTimestamp" : 1467039089905
          },
          "referenceDesignator" : {
            "node" : "SP001",
            "full" : true,
            "subsite" : "CE01ISSP",
            "sensor" : "10-PARADJ000"
          },
          "mooring" : {
            "@class" : ".XMooring",
            "events" : [ ],
            "assetId" : 3082,
            "serialNumber" : "CE01ISSP-00001",
            "name" : "CE01ISSP-00001",
            "location" : null,
            "description" : "MOORING ENDURANCE IS PROFILER",
            "physicalInfo" : {
              "height" : -1.0,
              "width" : -1.0,
              "length" : -1.0,
              "weight" : -1.0
            },
            "uid" : "N00262",
            "assetType" : "Mooring",
            "mobile" : false,
            "manufacturer" : "WHOI",
            "modelNumber" : "CE01ISSP",
            "purchasePrice" : 19920.0,
            "purchaseDate" : 0,
            "deliveryDate" : null,
            "depthRating" : null,
            "dataSource" : "/home/asadev/uframes/uframe_ooi_20160616_ba553c7c2ce211a96098ac6db8d9b21688da8a7b/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
            "lastModifiedTimestamp" : 1467039096977
          },
          "deploymentNumber" : 1,
          "versionNumber" : 1,
          "ingestInfo" : [ {
            "@class" : ".IngestInfo",
            "id" : 10719,
            "ingestMethod" : "telemetered",
            "ingestQueue" : "Ingest.parad-j-cspp_telemetered",
            "ingestPath" : "/omc_data/whoi/OMC/CE01ISSP/D00001/extract/",
            "ingestMask" : "ucspp_*_PPD_PARS.txt"
          }, {
            "@class" : ".IngestInfo",
            "id" : 10720,
            "ingestMethod" : "recovered_cspp",
            "ingestQueue" : "Ingest.parad-j-cspp_recovered",
            "ingestPath" : "/omc_data/whoi/OMC/CE01ISSP/R00001/extract/",
            "ingestMask" : "ucspp_*_PPB_PARS.txt"
          } ],
          "eventId" : 10718,
          "eventType" : "DEPLOYMENT",
          "eventName" : "CE01ISSP-SP001-10-PARADJ000",
          "eventStartTime" : 1397773200000,
          "eventStopTime" : 1429228800000,
          "tense" : null,
          "dataSource" : null,
          "lastModifiedTimestamp" : 1467039270676
        }]
    """
    debug = False
    # todo - deployment structure has been modified 07-21-2016; add additional required fields ****************
    required_deployment_attributes = ['mooring', 'node', 'sensor',
                                      'deploymentNumber', 'versionNumber', 'ingestInfo',
                                      'eventId', 'eventType', 'eventName',
                                      'eventStartTime', 'eventStopTime', 'tense', 'dataSource',
                                      'lastModifiedTimestamp']
    required_referenceDesignator_attributes = ['subsite', 'node', 'sensor']
    asset_ids_by_type = {'sensor': [], 'mooring': [], 'node': []}
    result = {}
    try:
        # Check parameter
        if not deployment or deployment is None:
            return result

        # Check deployment content for 'referenceDesignator'
        if 'referenceDesignator' not in deployment:
            return result

        # Build rd from 'referenceDesignator' values (use this to check integrity of deployment data
        ref_des = deployment['referenceDesignator']
        if not ref_des:
            return result

        # Check format/structure of deployment['referenceDesignator'] for required attributes
        for item in required_referenceDesignator_attributes:
            if item not in ref_des:
                return result
        rd = '-'.join([ref_des['subsite'], ref_des['node'], ref_des['sensor']])
        if debug: print ' debug -- get_deployment_asset_ids for rd: ', rd

        # Check structure of deployment provided
        if debug:
            for item in required_deployment_attributes:
                if item not in deployment:
                    print '\n debug -- Required attribute \'%s\' not in deployment object.'

        # Get asset ids for mooring, node and sensor; for each mooring, node or sensor there shall be one assetId.
        ids = []
        if 'sensor' in deployment:
            if deployment['sensor']:
                sensor_id = deployment['sensor']['assetId']
                if sensor_id is not None:
                    if sensor_id not in ids:
                        ids.append(sensor_id)
                    asset_ids_by_type['sensor'] = [sensor_id]           # ******
        if 'mooring' in deployment:
            if deployment['mooring']:
                mooring_id = deployment['mooring']['assetId']
                if mooring_id is not None:
                    if mooring_id not in ids:
                        ids.append(mooring_id)
                    asset_ids_by_type['mooring'] = [mooring_id]         # ******

        if 'node' in deployment:
            if deployment['node']:
                node_id = deployment['node']['assetId']
                if node_id is not None:
                    if node_id not in ids:
                        ids.append(node_id)
                    asset_ids_by_type['node'] = [node_id]               # ******

        if ids:
            ids.sort()
        result['asset_ids'] = ids
        result['asset_ids_by_type'] = asset_ids_by_type
        return result

    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception [get_deployment_asset_ids]: ', message
        current_app.logger.info(message)
        return result

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_instrument_deployment_work(rd):
    """ Create instrument deployment information breakout. Return dict or empty dict. Log exceptions.
    """
    debug = False
    work = {}
    try:
        if debug: print '\n debug -- entered get_instrument_deployment_work **************** ', rd

        # Create dictionary container for unique asset_ids (key) where value is deployment number
        work['asset_ids'] = {}
        work['current_deployment'] = None
        work['deployments'] = []

        # Get deployments list for reference designator
        _deployments_list = get_instrument_deployments_list(rd)
        #if debug: print '\n debug -- deployments_list: ', _deployments_list
        _deployments_list.sort(reverse=True)
        deployments_list = []
        for d in _deployments_list:
            deployments_list.append(int(str(d)))
        if debug: print '\n debug -- deployments_list: ', deployments_list
        work['deployments'] = deployments_list

        # Determine current deployment number, if no deployments then None
        current_deployment_number = None
        if deployments_list:
            current_deployment_number = deployments_list[0]
            #if debug: print '\n debug -- current deployment %s' % str(current_deployment_number)
        work['current_deployment'] = current_deployment_number

        # If deployments, process all deployments for: location info, asset ids; determine & add 'tense'
        if deployments_list:

            # Get all deployments for reference designator
            deployments = get_instrument_deployments(rd)
            #if debug: print '\n Number of deployments for rd: %d: ' % len(deployments)
            if deployments is None:
                #continue
                message = 'Failed to get deployments for %s from uframe.' % rd
                current_app.logger.info(message)
                return work

            # For each deployment number, create dictionary map of deployment data
            for deployment in deployments:

                # Get deployment number, create container for deployment number
                deployment_number = deployment['deploymentNumber']
                #if debug: print '\n debug -- processing deployment %d' % deployment_number
                work[deployment_number] = {}

                # Get deployment beginDT, endDT and eventId
                work[deployment_number]['beginDT'] = deployment['eventStartTime']
                work[deployment_number]['endDT'] = deployment['eventStopTime']
                work[deployment_number]['eventId'] = deployment['eventId']
                work[deployment_number]['tense'] = deployment['tense']

                # Get 'cumulative_tense' for this deployment
                tense = 'PAST'
                if deployment_number == current_deployment_number:
                    tense = 'PRESENT'
                work[deployment_number]['cumulative_tense'] = tense
                work[deployment_number]['asset_ids'] = []

                # Get location for this deployment
                location = deployment['location']
                work[deployment_number]['location'] = deployment['location']

                # Get asset ids for this deployment - all and by type dict
                work[deployment_number]['asset_ids'] = []
                work[deployment_number]['asset_ids_by_type'] = {'sensor': [], 'mooring': [], 'node': []}
                info = get_deployment_asset_ids(deployment)
                #if debug: print ' debug -- info: ', info
                if info:
                    work[deployment_number]['asset_ids'] = info['asset_ids']
                    work[deployment_number]['asset_ids_by_type'] = info['asset_ids_by_type']

            # Process work dictionary for all asset_ids and all asset_ids_by_type
            #if debug: print '\n debug -- Processing final asset_ids and asset_ids_by_type...'
            all_asset_ids = []
            all_asset_ids_by_type = {'sensor': [], 'mooring': [], 'node': []}
            all_sensor_ids = []
            all_mooring_ids = []
            all_node_ids = []
            for index in deployments_list:

                # Process the deployment work info
                if work[index]:
                    # Process all asset_ids
                    #all_asset_ids = all_asset_ids + work[index]['asset_ids']   # leaves dups
                    for id in work[index]['asset_ids']:
                        if id not in all_asset_ids:
                            all_asset_ids.append(id)
                    all_asset_ids.sort()

                    # Process asset_ids_by_type, accumulate for summary dict all_asset_ids_by_type
                    if work[index]['asset_ids_by_type']['sensor'] not in all_sensor_ids:
                        all_sensor_ids = all_sensor_ids + work[index]['asset_ids_by_type']['sensor']
                    if work[index]['asset_ids_by_type']['mooring'] not in all_mooring_ids:
                        all_mooring_ids = all_mooring_ids + work[index]['asset_ids_by_type']['mooring']
                    if work[index]['asset_ids_by_type']['node'] not in all_node_ids:
                        all_node_ids = all_node_ids + work[index]['asset_ids_by_type']['node']

            # sensor ids: squish and sort
            set_all_sensor_ids = set(all_sensor_ids)
            all_sensor_ids = list(set_all_sensor_ids)
            all_sensor_ids.sort()
            # mooring ids: squish and sort
            set_all_mooring_ids = set(all_mooring_ids)
            all_mooring_ids = list(set_all_mooring_ids)
            all_mooring_ids.sort()
            # node ids: squish and sort
            set_all_node_ids = set(all_node_ids)
            all_node_ids = list(set_all_node_ids)
            all_node_ids.sort()
            all_asset_ids_by_type['sensor'] = all_sensor_ids
            all_asset_ids_by_type['mooring'] = all_mooring_ids
            all_asset_ids_by_type['node'] = all_node_ids

            if all_asset_ids:
                all_asset_ids.sort()
            work['asset_ids'] = all_asset_ids
            work['asset_ids_by_type'] = all_asset_ids_by_type

        return work

    except ConnectionError:
        message = 'ConnectionError in get_instrument_deployment_work.'
        current_app.logger.info(message)
        return {}
    except Timeout:
        message = 'Timeout in get_instrument_deployment_work.'
        current_app.logger.info(message)
        return {}
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}


def get_mooring_deployment_work(rd):
    """ Create mooring deployment information breakout. Return dict or empty dict. Log exceptions.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered get_mooring_deployment_work **************** ', rd

        # Get deployments list for mooring and process deployment information
        _deployments_list, work = get_mooring_deployments_list(rd)

        #If no deployment information, return empty dict {}
        if not _deployments_list or _deployments_list is None:
            if debug: print '\n debug -- No deployment information for mooring rd: %s' % rd
            return {}

        #if debug: print '\n debug -- _deployments_list: ', _deployments_list
        _deployments_list.sort(reverse=True)
        deployments_list = []
        for d in _deployments_list:
            deployments_list.append(int(str(d)))
        work['deployments'] = deployments_list
        if debug: print '\n debug -- deployments_list: ', deployments_list

        # Determine current deployment number, if no deployments then None
        current_deployment_number = None
        if deployments_list:
            current_deployment_number = deployments_list[0]
            if debug: print '\n debug -- current deployment %s' % str(current_deployment_number)
        work['current_deployment'] = current_deployment_number

        return work

    except ConnectionError:
        message = 'ConnectionError in get_mooring_deployment_work.'
        current_app.logger.info(message)
        return {}
    except Timeout:
        message = 'Timeout in get_mooring_deployment_work.'
        current_app.logger.info(message)
        return {}
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}


def get_platform_deployment_work(rd):
    """ Create platform deployment information breakout. Return dict or empty dict. Log exceptions.
    """
    debug = False
    try:
        if debug: print '\n debug -- entered get_platform_deployment_work **************** ', rd

        # Get deployments list for mooring and process deployment information
        _deployments_list, work = get_platform_deployments_list(rd)

        #If no deployment information, return empty dict {}
        if not _deployments_list or _deployments_list is None:
            if debug: print '\n debug -- No deployment information for platform rd: %s' % rd
            return {}

        if debug: print '\n debug -- deployments_list: ', _deployments_list
        _deployments_list.sort(reverse=True)
        deployments_list = []
        for d in _deployments_list:
            deployments_list.append(int(str(d)))
        work['deployments'] = deployments_list
        if debug: print '\n debug -- deployments_list: ', deployments_list

        # Determine current deployment number, if no deployments then None
        current_deployment_number = None
        if deployments_list:
            current_deployment_number = deployments_list[0]
            if debug: print '\n debug -- current deployment %s' % str(current_deployment_number)
        work['current_deployment'] = current_deployment_number

        return work

    except ConnectionError:
        message = 'ConnectionError in get_platform_deployment_work.'
        current_app.logger.info(message)
        return {}
    except Timeout:
        message = 'Timeout in get_platform_deployment_work.'
        current_app.logger.info(message)
        return {}
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}

