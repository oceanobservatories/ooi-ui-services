#!/usr/bin/env python

"""
Deployments - supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.config import (get_deployments_url_base, get_uframe_deployments_info)
from ooiservices.app.uframe.common_tools import (is_instrument, is_platform, is_mooring, get_asset_type_by_rd,
                                                 get_supported_asset_types)
from ooiservices.app.uframe.asset_tools import (process_toc_information_reference_designators,
                                                get_toc_information, _get_rd_assets)

import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
import json
import datetime as dt
import calendar

CACHE_TIMEOUT = 172800


# New: Deployments added to rd information inventory
def _compile_rd_assets():
    """ Get dictionary, keyed by reference designator, holding reference maps for deployments and asset_ids.

    Exercise this function using development route: http://localhost:4000/uframe/get_rd_assets

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

    [Proposed] Sample response:         TODO correct this comment.
        {
            "CE02SHSM-RID26-08-SPKIRB000":
                {
                    "current_deployment": 4,
                    "deployments": [1,2,3,4],
                    1:  {
                        "beginDT": 1397767980000,
                        "endDT": 1412899200000,
                        "asset_ids": [1022, 3089, 100],     # deployment 1 has these asset ids (Note 100) - all types
                        # deployment 1 has these asset ids by type
                        "asset_ids_by_type":
                            {
                                'mooring': [1022],
                                'node': [3089],
                                'sensor': [100]
                            },
                        "tense": "PAST",
                        "location": {
                            "depth" : 0.0,
                            "location" : [ -124.09817, 44.6584 ],
                            "longitude" : -124.09817,
                            "latitude" : 44.6584,
                            "orbitRadius" : 0.0
                          }
                        },
                    2: {
                        "beginDT": 1397767980000,
                        "endDT": 1412899200000,
                        "asset_ids": [100],                         # deployment 2 has these asset ids
                        "tense": "PAST",
                        "location": {
                            "depth" : 0.0,
                            "location" : [ -124.09817, 44.6584 ],
                            "longitude" : -124.09817,
                            "latitude" : 44.6584,
                            "orbitRadius" : 0.0
                          }
                        },
                    3: {
                        "beginDT": 1433352120000,
                        "endDT": 1444003200000,
                        "asset_ids": [200],                         # deployment 3 has these asset ids
                        "tense": "PAST",
                        "location": {
                            "depth" : 0.0,
                            "location" : [ -124.09817, 44.6584 ],
                            "longitude" : -124.09817,
                            "latitude" : 44.6584,
                            "orbitRadius" : 0.0
                          }
                        },
                    4: {
                        "beginDT": 1444003200100,
                        "endDT": 1444003200500,
                        "asset_ids": [300, 100],                    # deployment 4 has these asset ids
                        "tense": "PRESENT",
                        "location": {
                            "depth" : 0.0,
                            "location" : [ -124.09817, 44.6584 ],
                            "longitude" : -124.09817,
                            "latitude" : 44.6584,
                            "orbitRadius" : 0.0
                          }
                        },

                    # actual asset id deployment number (bingo? what if list? yikes)
                    "asset_ids": {1022: [1], 3089: [1], 100: [1, 2, 4], 200: 3, 300: 4}
                }
            "CP02PMUI-WFP01":
                {
                "current_deployment": 4,
                "deployments": [1, 2],
                1: {
                    "asset_ids": [600],                         # deployment 1 has these asset ids
                    "tense": "PAST",
                    "location": {
                        "depth" : 0.0,
                        "location" : [ -124.09817, 44.6584 ],
                        "longitude" : -124.09817,
                        "latitude" : 44.6584,
                        "orbitRadius" : 0.0
                      }
                    },
                2: {
                    "asset_ids": [700, 800],                    # deployment 2 has these asset ids
                    "tense": "PRESENT",
                    "location": {
                        "depth" : 0.0,
                        "location" : [ -124.09817, 44.6584 ],
                        "longitude" : -124.09817,
                        "latitude" : 44.6584,
                        "orbitRadius" : 0.0
                      }
                    },
                "asset_ids": {600: [1], 700: [2], 800: [2]}    # actual asset id deployment number
                }
                . . .
        }

    """
    debug = False
    result = {}
    try:
        if debug: print '\n debug -- entered _compile_rd_assets...'
        # Get contents of /sensor/inv/toc
        toc = get_toc_information()

        # If toc is of type dict, then processing newer style toc format
        if isinstance(toc, dict):
            if 'instruments' not in toc:
                message = 'TOC does not have attribute \'instruments\', unable to process for reference designators.'
                raise Exception(message)

            # Verify toc attribute 'instruments' is not None or empty, if so, raise Exception.
            toc = toc['instruments']
            if not toc or toc is None:
                message = 'TOC attribute \'instruments\' is None or empty, unable to process for reference designators.'
                raise Exception(message)

        # Process toc to get lists of:
        # (1) reference designators (generated by accumulation),
        # (2) actual reference designators called out in each element of toc response,
        # (3)list of differences

        #uframe_url, timeout, timeout_read = get_uframe_deployments_info()
        reference_designators, toc_only, difference = process_toc_information_reference_designators(toc)
        if not reference_designators:
            message = 'No reference_designators identified when processing toc information.'
            raise Exception(message)

        #print '\n debug ***** Number of reference designators from toc: ', len(reference_designators)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if reference_designators and toc_only:
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
                    message = 'Exception raised in _compile_rd_assets: %s' % err.message
                    raise Exception(message)

        return result

    except ConnectionError:
        message = 'ConnectionError for _compile_rd_assets.'
        current_app.logger.info(message)
        return {}
    except Timeout:
        message = 'Timeout for _compile_rd_assets.'
        current_app.logger.info(message)
        return {}
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}


def get_asset_deployment_map(asset_id, ref_des):
    """ For an asset id and associated reference designator, get deployment [map] information.
    Process deployment information to obtain/return the following for the asset id/reference designator:
        depth (float, default: 0.0)
        location (list, [0.0, 0.0])
        has_deployment_event (bool, default: False)
        deployment_numbers (str, default: '')
        tense (str, default: '')

    Each asset displays the following information related to deployment(s):
      hasDeploymentEvent (bool),
      New deployment display grid covers these deployment related items on per deployment basis:
        deployment_number, beginDT, endDT, tense, and
        location dict with: latitude, longitude, location [], orbit radius and depth
    Note: on current deployment the endDT will be null if deployment is active.

    """
    # Valid processing types are those assetTypes which are subsequently mapped to reference designators.
    valid_processing_types_uc = get_supported_asset_types()
    valid_processing_types = []
    for type in valid_processing_types_uc:
        valid_processing_types.append(type.lower())

    debug = False
    depth = 0.0
    location = [0.0, 0.0]
    has_deployment_event = False
    deployment_numbers = ''
    _deployment_numbers = []
    tense = ''
    try:
        # Get type of asset we are processing, using reference designator.
        processing_asset_type = get_asset_type_by_rd(ref_des)
        if processing_asset_type:
            processing_asset_type = processing_asset_type.lower()
        if debug:
            if processing_asset_type not in valid_processing_types:
                if debug: print '\n debug ------------ processing_asset_type not valid: ', processing_asset_type

        no_deployments_nums = []
        if processing_asset_type in valid_processing_types:
            if debug: print '\n debug ------------ processing_asset_type: ', processing_asset_type
            deployments_info = get_asset_deployment_info(asset_id, ref_des)
            if deployments_info:
                deployments_list = deployments_info['deployments']

                # Determine if has_deployment_event and location
                if deployments_list:
                    has_deployment_event = True
                    deployments_list.sort(reverse=True)

                    # Get coordinate information from most recent deployment
                    current_deployment_number = deployments_info['current_deployment']
                    current_deployment = deployments_info[current_deployment_number]
                    latitude = round(current_deployment['location']['latitude'], 4)
                    longitude = round(current_deployment['location']['longitude'], 4)
                    location = [longitude, latitude]
                    depth = current_deployment['location']['depth']
                    if debug:
                        print '\n debug -- Most recent deployment number: %d -- tense %s' % \
                              (current_deployment_number, current_deployment['tense'])

                    # Get deployment number(s) for this asset id
                    _deployment_numbers = []
                    for deploy_number in deployments_list:

                        # Get asset ids, based on asset type (of associated) reference designator being processed,
                        tmp = deployments_info[deploy_number]['asset_ids_by_type'][processing_asset_type]
                        if tmp:
                            if debug: print '\n debug -- %s %s deployment %d has asset ids: %s' % \
                                            (ref_des, processing_asset_type, deploy_number, tmp)
                            if asset_id in tmp:
                                if deploy_number not in _deployment_numbers:
                                    _deployment_numbers.append(deploy_number)
                        else:
                            # In this case there is a deployments_list, but deployments_info for this deploy_number
                            # does not have asset ids for processing_asset_type in assets map. (uframe missing data problem)
                            # Basically 'sensor' data does not have assetId for deploy_number deployment.
                            # This MAY lead to incorrectly identifying the most recent or current deployment for
                            # this asset id; certainly deployment asset map will have 'holes' if data is missing.
                            # Example: CP02PMUO-SBS01-01-MOPAK0000 (sensor) has 7 deployments, and deployment 7
                            # does not have a node value which identifies an assetId. So deployment 7 will not have
                            # a value in deployment_info[7][asset_ids_by_type]['sensor'] but instead is [].
                            # http://host:12587/events/deployment/inv/CP02PMUO/SBS01/01-MOPAK0000/7
                            # [{
                            #   "@class" : ".XDeployment",
                            #   "location" : {
                            #       "depth" : 0.0,
                            #       "location" : [ -70.7800166, 39.942116 ],
                            #       "longitude" : -70.7800166,
                            #       "latitude" : 39.942116,
                            #       "orbitRadius" : 0.0
                            #   },
                            #   "sensor" : null,
                            #   "node" : null,
                            #   "referenceDesignator" : {
                            #       "subsite" : "CP02PMUO",
                            #       "sensor" : "01-MOPAK0000",
                            #       "node" : "SBS01",
                            #       "full" : true
                            #   }, . . .
                            # }]
                            if deploy_number not in no_deployments_nums:
                                no_deployments_nums.append(deploy_number)
                            if debug:
                                message = 'No asset ids for %s, deployment %d.' % (ref_des, deploy_number)
                                print '\n debug -- ', message

                    # Get tense value for last deployment provided
                    if _deployment_numbers:
                        _deployment_numbers.sort(reverse=True)
                        recent_deployment_number = _deployment_numbers[0]
                        if current_deployment_number != recent_deployment_number:
                            if debug: print '\n debug -- reporting recent_deployment number %d, as last, not %d' % \
                                            (recent_deployment_number, current_deployment_number)
                        tense = deployments_info[recent_deployment_number]['tense']
                        _deployment_numbers.sort()
                        for dn in _deployment_numbers:
                                deployment_numbers += str(dn) + ', '

                        if deployment_numbers:
                            deployment_numbers = deployment_numbers.strip(', ')

                    # Highlight (*) deployments if most recent deployment has an empty 'node' attribute.
                    if no_deployments_nums:
                        if current_deployment_number in no_deployments_nums:
                            deployment_numbers += ' *'

        return depth, location, has_deployment_event, deployment_numbers, tense, no_deployments_nums, _deployment_numbers

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_processing_asset_type]: ', message
        current_app.logger.info(message)
        return None

def get_instrument_deployments_list(rd):
    """ Get list of deployments for instrument rd.
    """
    debug = False
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
        if debug: print '\n debug -- [get_instrument_deployments_list] url: ', url
        if check: print '\n check -- [get_instrument_deployments_list] url: ', url

        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get deployments list for  %r.' % (response.status_code, rd)
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
        print '\n debug -- exception [get_instrument_deployments_list]: ', message
        current_app.logger.info(message)
        return None


# todo - review to replace with get_rd_deployments(rd)
def get_instrument_deployments(rd):
    """ Get all deployments for instrument rd.

    Use: http://host:12587/deployments/inv/CE05MOAS/GL326/04-DOSTAM000/-1
    """
    debug = False
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
        if debug: print '\n debug -- [get_instrument_deployments] url: ', url
        if check: print '\n check -- [get_instrument_deployments] url: ', url

        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get all for  %r.' % (response.status_code, rd)
            current_app.logger.info(message)
            raise Exception(message)

        result = response.json()
        #if debug: print '\n debug -- [get_instrument_deployments] (list) result: ', result
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
        print '\n debug -- exception [get_instrument_deployments]: ', message
        current_app.logger.info(message)
        raise


# todo review to see if we can use /deployments/query?refdes=CE05MOAS-GL326-04-DOSTAM000 instead
def get_rd_deployments(rd):
    """ Get all deployments for mooring and platform.

    Use urls such as:
        (http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326-04-DOSTAM000)
         http://host:12587/events/deployment/query?refdes=CE05MOAS-GL326
         http://host:12587/events/deployment/query?refdes=CE05MOAS
         http://host:12587/events/deployment/query?refdes=CP02PMUI
    """
    debug = False
    check = False
    result = []
    try:
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator %s is not a mooring, platform or instrument.'
            current_app.logger.info(message)
            return result

        # Get uframe deployments request variables
        uframe_url, timeout, timeout_read = get_uframe_deployments_info()

        # Build uframe url: host:port/events/deployment/query?refdes=XXXXXXXX
        url = '/'.join([uframe_url, get_deployments_url_base(), 'query']) # todo hard coded - track uframe
        url += '?refdes=' + rd
        if debug: print '\n debug -- [get_rd_deployments] url: ', url
        if check: print '\n Check -- [get_rd_deployments] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Failed to get deployments from uframe for  %r.' % (response.status_code, rd)
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

            #if debug: print '\n debug -- deployment_number: ', deployment_number

            location = None
            if 'location' in item:
                location = item['location']
            #if debug: print '\n debug -- location: ', location

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

            asset_id = None
            if 'mooring' in item:

                # Get 'mooring' component from item, check it empty or None.
                _item = item['mooring']
                if not _item or _item is None:
                    #return [], {}
                    continue

                # Process 'node' attribute in this deployment item.
                #if debug: print '\n debug -- item[mooring]: ', json.dumps(item['mooring'], indent=4, sort_keys=True)
                if 'assetId' in _item:
                    if _item['assetId']:
                        asset_id = _item['assetId']
                        if asset_id not in all_asset_ids:
                            all_asset_ids.append(asset_id)

                if deployment_number:
                    #if debug: print '\n debug -- have deployment_number... '
                    if asset_id:
                        #if debug: print '\n debug -- have asset_id... '
                        if asset_id not in deployment_asset_ids:
                            #if debug: print '\n debug -- add asset_id to deployment_asset_ids... '
                            deployment_asset_ids.append(asset_id)

                    #if debug: print '\n debug -- processing info[deployment_number][asset_ids_by_type]...'
                    info[deployment_number] = {}
                    info[deployment_number]['asset_ids_by_type'] = {'sensor': [], 'mooring': deployment_asset_ids, 'node': []}
                    if deployment_number not in deployments_list:
                        deployments_list.append(deployment_number)

                    #if debug: print '\n debug -- processing deployment location and times...'
                    # Valuable luggage
                    info[deployment_number]['location'] = location
                    info[deployment_number]['beginDT'] = beginDT
                    info[deployment_number]['endDT'] = endDT
                    info[deployment_number]['eventId'] = eventId

                    if deployment_asset_ids:
                        deployment_asset_ids.sort()
                    info[deployment_number]['asset_ids'] = deployment_asset_ids

            if info:
                #print '\n debug -- info: ', json.dumps(info, indent=4, sort_keys=True)
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
            print '\n debug -- Mooring %s does not have a deployments_list! -----------------'

        if deployments_list:

            deployments_list.sort(reverse=True)
            current_deployment_number = deployments_list[0]

            # Set tense to Past if deployment number not equal to current_deployment_number
            # Get 'tense' for each deployment
            for num in deployments_list:
                tense = 'PAST'
                if num == current_deployment_number:
                    tense = 'PRESENT'
                results[num]['tense'] = tense

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

            asset_id = None
            if 'node' in item:

                # Get 'node' component from item, check it empty or None.
                _item = item['node']
                if not _item or _item is None:
                    #return [], {}
                    continue

                # Process 'node' attribute in this deployment item.
                #if debug: print '\n debug -- _item: ', json.dumps(_item, indent=4, sort_keys=True)
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
                    if deployment_asset_ids:
                        deployment_asset_ids.sort()
                    info[deployment_number]['asset_ids'] = deployment_asset_ids

            if info:
                #print '\n debug -- info: ', json.dumps(info, indent=4, sort_keys=True)
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
                results[num]['tense'] = tense

        if debug:
            print '\n debug -- [get_platform_deployments_list] (list) result: ', result
            print '\n debug -- results: ', json.dumps(results, indent=4, sort_keys=True)

        return result, results

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_platform_deployments_list]: ', message
        current_app.logger.info(message)
        return None, None


def get_asset_deployment_info(asset_id, rd):
    """ Use rd to fetch dict from 'rd_assets' cache. Process dict and create result info.
    On error, log and return {}.

    The result dict value returned is described in get_asset_deployment_detail function.
    """
    debug = False
    result = {}
    try:
        if debug: print '\n debug -- get_asset_deployment_info for rd: ', rd

        # Get asset and deployment data for reference designator.
        data = get_asset_deployment_data(rd)

        # If data is returned, process into result and return. On error, log and return empty dict {}.
        if data:
            # Get specific info for asset id from data
            result = get_asset_deployment_detail(asset_id, data)
        else:
            if debug: print '\n debug -- no deployment info for asset_id %s,  rd: %s' % (str(asset_id), rd)

        return result

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_asset_deployment_info]: ', message
        current_app.logger.info(message)
        return {}


def get_asset_deployment_detail(id, data):
    """ Using deployment info in data, process and return specific details. (Only instruments)
    {
        "deployments": [4,3,2,1],
        "current_deployment": 4,
        # Multiple entries as follows, one for each deployment in 'deployments' list #
        "4": {
              "asset_ids": [
                1799,
                3085,
                3628
              ],
              "asset_ids_by_type": {
                "mooring": [
                  3085
                ],
                "node": [
                  3628
                ],
                "sensor": [
                  1799
                ]
              },
              "beginDT": 1439850000000,
              "endDT": null,
              "location": {
                "depth": 0.0,
                "latitude": 44.65602,
                "location": [
                  -124.09524,
                  44.65602
                ],
                "longitude": -124.09524,
                "orbitRadius": 0.0
              },
              "tense": "PRESENT"
            }
    }

    """
    debug = False
    try:
        if debug: print '\n debug -- get_asset_deployment_detail for id: ', id

        # Determine if asset_id in data['asset_ids'], if not log and return empty dict.
        if id not in data['asset_ids']:
            message = 'Unable to find asset id %s for %s in rd_assets entry.' % (str(id), rd)
            raise Exception(message)

        result = data.copy()
        del result['asset_ids']
        del result['asset_ids_by_type']

        return result

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_asset_deployment_detail]: ', message
        current_app.logger.info(message)
        return {}


def get_asset_deployment_data(rd):
    """ Get deployment specific information for a reference designator from rd_cache. Returns dictionary from cache.
    """
    debug = False
    result = {}
    try:
        if debug: print '\n debug -- get_asset_deployment_data for rd: ', rd

        # Validate reference designator
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator provided (%s) is not an instrument or mooring.' % rd
            message += 'unable to provide asset deployment info.'
            raise Exception(message)

        # Verify rd_assets cache available, if not get rd_assets and cache.
        rd_assets = _get_rd_assets()
        if not rd_assets:
            message = 'The \'rd_assets\' cache is empty; unable to provide asset deployment info for %s.' % rd
            raise Exception(message)

        # Pluck from rd_assets information required
        if rd in rd_assets:
            result = rd_assets[rd]

        return result

    except Exception as err:
        message = str(err)
        print '\n debug -- exception [get_asset_deployment_data]: ', message
        current_app.logger.info(message)
        return {}


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
        if debug: print '\n debug -- get_deployment_asset_ids... '
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
                print '\n debug -- %s not provided in deployment attribute \'referenceDesignator\'.'
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
        print '\n debug -- exception [get_deployment_asset_ids]: ', message
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
                if debug: print '\n debug -- ', message
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

                # Get 'tense' for this deployment
                tense = 'PAST'
                if deployment_number == current_deployment_number:
                    tense = 'PRESENT'
                work[deployment_number]['tense'] = tense
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



#===========================================================
def get_timestamp_value(value):
    """ Convert float value into formatted string.
    """
    result = value
    try:
        formatted_value = timestamp_to_string(value)
        if formatted_value is not None:
            result = formatted_value
        return result
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return result


def timestamp_to_string(time_float):
    """ Convert float to formatted time string. If failure to convert, return None.
    """
    offset = 2208988800
    formatted_time = None
    try:
        if not isinstance(time_float, float):
            return None
        ts_time = convert_from_utc(time_float - offset)
        formatted_time = dt.datetime.strftime(ts_time, "%Y-%m-%dT%H:%M:%S")
        return formatted_time
    except Exception as err:
        current_app.logger.info(str(err.message))
        return None


# Note: start of unix epoch (jan 1, 1900 at midnight 00:00) in seconds == 2208988800
# http://stackoverflow.com/questions/13260863/convert-a-unixtime-to-a-datetime-object-
# and-back-again-pair-of-time-conversion (url continued from previous line)
# Convert a unix time u to a datetime object d, and vice versa
def convert_from_utc(u):
    return dt.datetime.utcfromtimestamp(u)


def ut(d):
    return calendar.timegm(d.timetuple())


'''
def process_timestamps_in_events(data):

    debug = False
    try:
        if data:
            if debug: print '\n debug -- processing data...'
            for event in data:
                convert_event_timestamps(event)
                if '@class' in event:
                    del event['@class']
        return data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


def convert_event_timestamps(event):
    """ Convert all datetime int field values in base event into formatted datetime.
    """
    try:
        if 'eventStartTime' in event:
            if event['eventStartTime']:
                event['eventStartTime'] = convert_event_time(event['eventStartTime'])
        if 'eventStopTime' in event:
            if event['eventStopTime']:
                event['eventStopTime'] = convert_event_time(event['eventStopTime'])

        if 'lastModifiedTimestamp' in event:
            if event['lastModifiedTimestamp']:
                event['lastModifiedTimestamp'] = convert_event_time(event['lastModifiedTimestamp'])
        """
        if 'lastModifiedTimestamp' in event:
            del event['lastModifiedTimestamp']
        """
        return event

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


def convert_event_time(data):
    tmp = None
    try:
        if data > 0 and data is not None:
            tmp1 = dt.datetime.fromtimestamp(data / 1e3)
            tmp = dt.datetime.strftime(tmp1, '%Y-%m-%dT%H:%M:%S')
        return tmp
    except Exception:
        return data
'''

