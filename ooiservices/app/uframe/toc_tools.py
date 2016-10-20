#!/usr/bin/env python

"""
TOC: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.config import (get_uframe_toc_url, get_uframe_assets_info,
                                           get_deployments_url_base, deployment_inv_load)
from ooiservices.app.uframe.uframe_tools import compile_deployment_rds
import json
import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)

def process_toc_reference_designators(toc):
    """
    Get list of unique reference designators in /sensor/inv/toc; sorted ascending.
    If error log exception and return []. Includes all stream methods.
    Response output:
    {
      "reference_designators": [
        "CE01ISSP",                             # platform code
        "CE01ISSP-SP001",                       # platform code + mooring code
        "CE01ISSP-SP001-05-VELPTJ000",          # platform code + mooring code + instrument code
        "CE01ISSP-SP001-07-SPKIRJ000",
        "CE01ISSP-SP001-08-FLORTJ000",
        "CE01ISSP-SP001-09-CTDPFJ000",
        "CE01ISSP-SP001-10-PARADJ000",
        "CE01ISSP-XX001",
        "CE01ISSP-XX001-01-CTDPFJ999",
        "CE01ISSP-XX001-01CTDPFJ999",
        "CE01ISSP-XX099",
        "CE01ISSP-XX099-01-CTDPFJ999",
        "CE02SHBP",
        "CE02SHBP-LJ01D",
        . . .
        ]
    }
    """
    result = []
    rds = []
    try:
        if toc is None or not toc:
            message = 'toc is None or empty.'
            raise Exception(message)

        for item in toc:
            if item['reference_designator'] not in rds:
                rds.append(item['reference_designator'])                # format 'CP02PMCO-SBS01-00-RTE000000'

            platform_code = item['platform_code']                       # format 'CP02PMCO'
            if platform_code not in result:
                result.append(platform_code)

            mooring_code = item['mooring_code']                         # format 'SBS01', used with platform code
            instrument_code = item['instrument_code']

            _platform_code = "-".join([platform_code, mooring_code])    # format CP02PMCO-SBS01
            if _platform_code not in result:
                result.append(_platform_code)
            _instrument_code = "-".join([platform_code, mooring_code, instrument_code])  #'CP02PMCO-SBS01-00-RTE000000'
            if _instrument_code not in result:
                result.append(_instrument_code)

        if rds:
            rds.sort()
        if result:
            result.sort()

        # Reviewing data from toc to see what we have and don't have...
        # Which items in result were not provided in rds?
        ommitted_reference_designators = []
        for item in result:
            if item not in rds:
                if item not in ommitted_reference_designators:
                    ommitted_reference_designators.append(item)
        if ommitted_reference_designators:
            ommitted_reference_designators.sort()

        # In brief, the 'reference_designators' provided in the /sensor/toc response, are less than the
        # hierarchical structure (ui toc) count which would be generated to support those instruments.
        # Namely, the difference being the list of omitted_reference_designators identified above.
        return result, rds, ommitted_reference_designators

    except Exception as err:
        current_app.logger.info(str(err))
        return [], [], []


# Get toc information from uframe.
def get_toc_information():
    """ Get toc information from uframe. If exception, log error and return empty list.
    """
    try:
        url, timeout, timeout_read = get_uframe_toc_url()
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            toc = response.json()
        else:
            message = 'Failure to retrieve toc using url: ', url
            raise Exception(message)
        if toc is not None:
            result = toc
        else:
            message = 'toc returned as None: ', url
            raise Exception(message)
        return result

    except ConnectionError:
        message = 'ConnectionError for get_toc_information'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get_toc_information'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        current_app.logger.info(str(err))
        return []


def _compile_asset_rds():
    """ Retrieve asset_ids from uframe for all reference designators referenced in /sensor/inv/toc structure;
    return dictionary with key of asset_id. On error, log and raise exception.  Does NOT cache.
    Note:
        - All reference designators are determined from toc structure and not just what /sensor/inv/toc provides.
        - The original toc response format was a list of dicts; the more recent (May 2016) toc format is a dict.
        - This function has been updated to handle both the original toc list format and newer toc dict format.

    Sample response:
        {
          "1006": "CE02SHSM-RID26-08-SPKIRB000",
          "1022": "CE02SHSM-RID27-02-FLORTD000",
          "1024": "CE01ISSM-RID16-03-DOSTAD000",
          "1033": "CE02SHSM-SBD12-04-PCO2AA000",
          "1112": "CE01ISSP-SP001-00-SPPENG000",
          "1226": "CE04OSSM-RID26-01-ADCPTA000",
          . . .
        }
    """
    debug = False
    result = {}
    rds_wo_assets = []
    try:
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
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        reference_designators, toc_only, difference = process_toc_reference_designators(toc)
        if not reference_designators:
            message = 'No reference_designators identified when processing toc information.'
            raise Exception(message)

        #-----------------------------------
        if deployment_inv_load():
            # Add deployment reference designators to total reference designators processed.
            if debug: print '\n\tNumber of reference designators from toc: ', len(reference_designators)
            deployment_rds = compile_deployment_rds()
            if debug: print '\n\tNumber of reference designators from deployments: ', len(deployment_rds)
            if deployment_rds and deployment_rds is not None:
                for rd in deployment_rds:
                    if rd not in reference_designators:
                        reference_designators.append(rd)
            if debug:
                print '\n\tNumber of reference designators (toc and deployments): ', len(reference_designators)
        #-----------------------------------

        if reference_designators and toc_only:

            for rd in reference_designators:
                if rd and rd is not None:
                    try:
                        len_rd = len(rd)
                        ids, mrd, mids, nrd, nids = get_asset_id_by_rd(rd, uframe_url, timeout, timeout_read)
                    except Exception as err:
                        message = 'Exception raised in get_asset_id_by_rd: %s' % err.message
                        raise Exception(message)
                    if not ids and not mids and not nids:
                        if rd and rd is not None:
                            if rd not in rds_wo_assets:
                                rds_wo_assets.append(rd)
                    if len_rd > 14 and len_rd <= 27:
                        if ids:
                            #if debug: print '\n debug -- rd %s has ids: %s' % (rd, ids)
                            ids.sort()
                            for id in ids:
                                if id not in result:
                                    result[id] = rd

                    if len_rd == 8:
                        if mids:
                            #if debug: print '\n debug -- %s has mooring ids: %s' %(mrd, mids)
                            #mids.sort()
                            for id in mids:
                                if id not in result:
                                    result[id] = rd

                    if len_rd == 14:
                        if nids:
                            #if debug: print '\n debug -- rd %s has node ids: %s' % (rd, nids)
                            #nids.sort()
                            for id in nids:
                                if id not in result:
                                    result[id] = nrd

        # Identify reference designators in /sensor/inv which do not have associated asset ids.
        if rds_wo_assets:
            message = 'The following reference designators do not have an associated asset(%d): %s ' % \
                      (len(rds_wo_assets), rds_wo_assets)
            current_app.logger.info(message)

        return result, rds_wo_assets

    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}, []


def get_asset_id_by_rd(rd, uframe_url=None, timeout=None, timeout_read=None):
    """ Get asset_ids in uframe by reference designator; return list of asset ids; On error return [].
    """
    info = False
    #debug = False
    check = False
    ids = []
    mooring_ids = []
    node_ids = []
    try:
        if not rd or rd is None:
            return [], None, [], None, []

        if uframe_url is None:
            uframe_url, timeout, timeout_read = get_uframe_assets_info()

        # Get reference designator components (mooring, platform, instrument) and form url
        # Build uframe url: host:port/events/deployment/query?refdes=XXXXXXXX
        url_root = '/'.join([uframe_url, get_deployments_url_base(), 'query'])
        url_root += '?refdes='
        len_rd = len(rd)

        # Instrument
        if len_rd == 27 and ('-' in rd):
            mooring, platform, instrument = rd.split('-', 2)
            name = "-".join([mooring, platform, instrument])
            url = url_root + name

        # Platform
        elif len_rd == 14 and ('-' in rd):
            mooring, platform = rd.split('-')
            name = "-".join([mooring, platform])
            url = url_root + name

        # Mooring
        elif len_rd == 8:   # and ('-' not in rd):
            url = url_root + rd
            mooring = rd

        # Instruments with irregular reference designators (e.g. CE02SHBP-LJ01D-00-ENG)
        elif len_rd > 14 and len_rd < 27:
            mooring, platform, instrument = rd.split('-', 2)
            url = "/".join([url_root, mooring, platform, instrument])
            #print '\n debug (irregular) -- url: ', url
        else:
            message = 'Malformed reference designator: %s' % rd
            current_app.logger.info(message)
            return [], None, [], None, []

        # Query uframe for reference designator asset ids.
        if check: print '\n get_asset_id_by_rd -- url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            if info:
                message = '(%d) Failed to get uframe asset id for reference designator: %s' % (response.status_code,rd)
                current_app.logger.info(message)
            return [], None, [], None, []
        try:
            result = json.loads(response.content)
            if not result:
                return [], None, [], None, []
        except Exception as err:
            message = 'Invalid json; failed to get_asset_id_by_rd: %s' % err.message
            current_app.logger.info(message)
            return [], None, [], None, []

        # If result returned, process for ids
        if result:
            #if debug: print '\n debug -------------------------------------------- item:'
            for item in result:
                # This gets asset ids from deployment 'sensor', 'mooring' OR 'node' based on rd type.
                # Reference Designator of Instrument (assetType sensor)
                if len_rd > 14 and len_rd <= 27:
                    if 'sensor' in item:
                        if item['sensor']:
                            if 'assetId' in item['sensor']:
                                if item['sensor']['assetId']:
                                    if item['sensor']['assetId'] not in ids:
                                        ids.append(item['sensor']['assetId'])

                # Reference Designator of Mooring (assetType mooring)
                elif len_rd == 8:
                    if 'mooring' in item:
                        if item['mooring']:
                            if 'assetId' in item['mooring']:
                                if item['mooring']['assetId']:
                                    if item['mooring']['assetId'] not in mooring_ids:
                                        mooring_ids.append(item['mooring']['assetId'])

                # Reference Designator of Platform (assetType node)
                elif len_rd == 14:
                    if 'node' in item:
                        if item['node']:
                            if 'assetId' in item['node']:
                                if item['node']['assetId']:
                                    if item['node']['assetId'] not in node_ids:
                                        node_ids.append(item['node']['assetId'])
                else:
                    message = 'rd %s has a length of %d therefore not processed.' % (rd, len_rd)
                    current_app.logger.info(message)

        if ids:
            ids.sort(reverse=True)
            #if debug: print '\n debug -- rd %s has ids: %s' % (rd, ids)

        if mooring_ids:
            mooring_ids.sort(reverse=True)
            #if debug: print '\n debug -- mooring %s has mooring_ids: %s' % (rd, mooring_ids)

        node_name = None
        if node_ids:
            if len(rd) >= 14 and len(rd) <= 27:
                node_name = rd[:14]             # "-".join([mooring, platform])
            node_ids.sort(reverse=True)
            #if debug: print '\n debug -- node %s has node_ids: %s' % (node_name, node_ids)

        return ids, mooring, mooring_ids, node_name, node_ids

    except ConnectionError:
        message = 'ConnectionError for get_asset_id_by_rd, reference designator rd: ', rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout error for get_asset_id_by_rd, reference designator rd: ', rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return [], None, [], None, []


def get_toc_reference_designators():
    """ Get toc and process for reference designators.
    """
    try:
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
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        reference_designators, toc_only, difference = process_toc_reference_designators(toc)
        if not reference_designators:
            message = 'No reference_designators identified when processing toc information.'
            raise Exception(message)

        return reference_designators, toc_only, difference
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return [], None, [], None, []