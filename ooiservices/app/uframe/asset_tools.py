#!/usr/bin/env python

"""
Assets: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app import cache
from ooiservices.app.uframe.vocab import (get_vocab, get_vocab_dict_by_rd, get_rs_array_display_name_by_rd)
from ooiservices.app.uframe.vocab import get_display_name_by_rd as get_dn_by_rd
from ooiservices.app.uframe.vocab import get_long_display_name_by_rd as get_ldn_by_rd
from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.common_tools import (get_asset_type_by_rd, get_asset_classes, get_supported_asset_types)
from ooiservices.app.uframe.config import (get_uframe_toc_url, get_uframe_assets_info, get_deployments_url_base,
                                           get_assets_url_base, headers)
import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
import datetime as dt
import json

CACHE_TIMEOUT = 172800


def process_toc_information_reference_designators(toc):
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
    debug = False
    if debug: print '\n debug -- processing toc for rds...len(toc): ', len(toc)
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

        """
        In brief, the 'reference_designators' provided in the /sensor/toc response, are less than the
        hierarchical structure (ui toc) count which would be generated to support those instruments.
        Namely, the difference being the list of omitted_reference_designators identified above.
        """
        if debug:
            print '\n debug -- result(%d): %s' % (len(result), result)
            print '\n debug -- rds(%d): %s' % (len(rds), rds)

        return result, rds, ommitted_reference_designators

    except Exception as err:
        print '\n debug -- exception: ', str(err)
        current_app.logger.info(str(err))
        return [], [], []


def get_assets_dict_from_list(assets_list):
    """ From list of (ooi-ui-services versioned) list of assets, create assets dictionary by (key) id.
    """
    result = {}
    if assets_list:
        for item in assets_list:
            if 'id' in item:
                if item['id'] not in result:
                    result[item['id']] = item
    return result


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
        if debug: print '\n debug -- entered _compile_asset_rds...'
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
        reference_designators, toc_only, difference = process_toc_information_reference_designators(toc)
        if not reference_designators:
            message = 'No reference_designators identified when processing toc information.'
            raise Exception(message)

        #print '\n debug ***** Number of reference designators from toc: ', len(reference_designators)
        if reference_designators and toc_only:

            for rd in reference_designators:
                if rd and rd is not None:
                    try:
                        len_rd = len(rd)
                        ids, mrd, mids, nrd, nids = get_asset_id_by_reference_designator(rd, uframe_url,
                                                                                         timeout, timeout_read)
                    except Exception as err:
                        message = 'Exception raised in get_asset_id_by_reference_designator: %s' % err.message
                        raise Exception(message)
                    if not ids and not mids and not nids:
                        if rd and rd is not None:
                            if rd not in rds_wo_assets:
                                rds_wo_assets.append(rd)
                    if len_rd > 14 and len_rd <= 27:
                        if ids:
                            if debug: print '\n debug -- rd %s has ids: %s' % (rd, ids)
                            ids.sort()
                            for id in ids:
                                if id not in result:
                                    result[id] = rd

                    if len_rd == 8:
                        if mids:
                            if debug: print '\n debug -- %s has mooring ids: %s' %(mrd, mids)
                            #mids.sort()
                            for id in mids:
                                if id not in result:
                                    result[id] = rd

                    if len_rd == 14:
                        if nids:
                            if debug: print '\n debug -- rd %s has node ids: %s' % (rd, nids)
                            #nids.sort()
                            for id in nids:
                                if id not in result:
                                    result[id] = nrd

        """
        list_of_ids = []
        if result:
            list_of_ids = result.keys()
            if list_of_ids:
                list_of_ids.sort()
        """

        # Identify reference designators in /sensor/inv which do not have associated asset ids.
        if rds_wo_assets:
            message = 'The following reference designators do not have an associated asset(%d): %s ' % \
                      (len(rds_wo_assets), rds_wo_assets)
            if debug: print '\n ******* rds_wo_assets(%d): %s' % (len(rds_wo_assets), rds_wo_assets)
            current_app.logger.info(message)

        return result, rds_wo_assets #list_of_ids

    except ConnectionError:
        message = 'ConnectionError for _compile_asset_rds.'
        current_app.logger.info(message)
        return {}, []
    except Timeout:
        message = 'Timeout for _compile_asset_rds.'
        current_app.logger.info(message)
        return {}, []
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return {}, []


def get_asset_id_by_reference_designator(rd, uframe_url=None, timeout=None, timeout_read=None):
    """ Get asset_ids in uframe by reference designator; return list of asset ids; On error return [].
    """
    info = False
    debug = False
    check = False
    ids = []
    mooring_ids = []
    node_ids = []
    mooring = None
    platform = None
    instrument = None
    try:
        #if debug: print '\n debug -- entered get_asset_id_by_reference_designator...'
        if not rd or rd is None:
            return [], None, [], None, []

        if uframe_url is None:
            uframe_url, timeout, timeout_read = get_uframe_assets_info()

        # Get reference designator components (mooring, platform, instrument) and form url
        len_rd = len(rd)
        # Build uframe url: host:port/events/deployment/query?refdes=XXXXXXXX
        url_root = '/'.join([uframe_url, get_deployments_url_base(), 'query'])
        url_root += '?refdes='

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
        if debug: print '\n debug --- url: ', url
        if check: print '\n check -- [get_asset_id_by_reference_designator] url: ', url

        response = requests.get(url, timeout=(timeout, timeout_read)) # todo review
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
            message = 'Invalid json; failed to get_asset_id_by_reference_designator: %s' % err.message
            current_app.logger.info(message)
            return [], None, [], None, []

        # If result returned, process for ids
        if result:

            #if debug:
            #    print '\n debug -- (list) result(%d): %s' % (len(result), json.dumps(result, indent=4, sort_keys=True) )
            if debug: print '\n debug -------------------------------------------- item:'

            for item in result:
                #if debug: print '\n debug -- keys(%d): %s' % (len(item.keys()), item.keys())
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
                    print '\n debug -- ', message
                    current_app.logger.info(message)

        if ids:
            ids.sort(reverse=True)
            if debug: print '\n debug -- rd %s has ids: %s' % (rd, ids)

        if mooring_ids:
            mooring_ids.sort(reverse=True)
            if debug: print '\n debug -- mooring %s has mooring_ids: %s' % (rd, mooring_ids)

        # todo - review this
        node_name = None
        if node_ids:
            if len(rd) >= 14 and len(rd) <= 27:
                node_name = rd[:14]             # "-".join([mooring, platform])
            node_ids.sort(reverse=True)
            if debug: print '\n debug -- node %s has node_ids: %s' % (node_name, node_ids)

        return ids, mooring, mooring_ids, node_name, node_ids

    except ConnectionError:
        message = 'ConnectionError for get_asset_id_by_reference_designator'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get_asset_id_by_reference_designator'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = '[get_asset_id_by_reference_designator] exception: ', str(err)
        current_app.logger.info(message)
        return [], None, [], None, []


# todo - test this block of code, especially when cache is empty
def _get_asset(id):
    """ Get an asset by asset uid.

    This function is used by routes:
        /uframe/assets/<int:id>
        /uframe/assets/uid/<string:uid>
    """
    debug = False
    check = False
    result = []
    try:
        if debug: print '\n debug -- get asset by asset id: ', id
        assets_dict = cache.get('assets_dict')
        if assets_dict is not None:
            if debug: print '\n debug -- get asset id: ', id
            if id in assets_dict:
                result = assets_dict[id]
                if debug: print '\n debug -- result: %s' % json.dumps(result, indent=4, sort_keys=True)
        else:
            if debug: print '\n debug -- entered get_asset id: ', id
            uframe_url, timeout, timeout_read = get_uframe_assets_info()
            if id == 0:
                message = 'Zero (0) is an invalid asset id value.'
                raise Exception(message)

            url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
            if check: print '\n check -- [get_asset] url: ', url
            payload = requests.get(url, timeout=(timeout, timeout_read))
            if payload.status_code != 200:
                message = 'Unable to locate an asset with an id of %d.' % id
                raise Exception(message)
            data = payload.json()
            if debug: print '\n debug -- data returned: ', data
            if data:
                data_list = [data]
                if debug: print '\n debug -- data for compile_assets: ', data_list
                result, _ = _compile_assets(data_list)
                if debug: print '\n debug -- returned from compile_assets: ', result
                if result:
                    # todo this is where the changes where made, test here
                    if debug: print 'Process result returned from _compile_assets....'
                    result = result[0]
                    if debug:
                        print '\n debug -- (list) result(%d): %s' % (len(result),
                                                                     json.dumps(result, indent=4, sort_keys=True) )
                    #return jsonify(**result[0])

        return result
    except ConnectionError:
        message = 'Error: ConnectionError getting asset with id %d.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting asset with id %d.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Error getting asset with id %d. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)


# Get asset from uframe by asset id.
def uframe_get_asset_by_id(id):
    """ Get asset from uframe by asset id.
    """
    check = False
    try:
        # Get uframe asset
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([uframe_url, get_assets_url_base(), str(id)])
        if check: print '\n check -- [uframe_get_asset_by_id] get asset %d, url: %s' % (id, url)
        payload = requests.get(url, timeout=(timeout, timeout_read), headers=headers())
        if payload.status_code != 200:
            message = '(%d) GET request failed for asset (id %d) events.' % (payload.status_code, id)
            current_app.logger.info(message)
            raise Exception(message)
        asset = payload.json()
        return asset
    except ConnectionError:
        message = 'ConnectionError getting asset (id %d) from uframe; unable to process events.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting asset (id %d) from uframe; unable to process events.' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Error processing GET request for asset (id %d) events. %s' % (id, str(err))
        current_app.logger.info(message)
        raise Exception(message)


# Get toc information from uframe.
def get_toc_information():
    """ Get toc information from uframe. If exception, log error and return empty list.
    """
    check = False
    try:
        url, timeout, timeout_read = get_uframe_toc_url()
        if check: print '\n check -- [get_toc_information] url: ', url
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


# ========================================================
# Supporting functions:
#   verify_cache
#   get_assets_payload
#   get_stream_list
#   populate_assets_dict
#   get_assets_from_uframe
#   --get_all_asset_types
# ========================================================
def verify_cache(refresh=False):
    """ Verify necessary cached objects are available; if not get and set. Return asset_list data.
    """
    debug = False
    verify_cache_required = False
    try:

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 'vocab_dict' and 'vocab_codes'; 'stream_list'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        vocab_dict = get_vocab()
        stream_list = get_stream_list()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check 'asset_list', 'assets_dict', 'asset_rds', 'rd_assets', 'asset_types'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not cache.get('asset_list') or not cache.get('assets_dict') or \
           not cache.get('asset_rds') or not cache.get('rd_assets'):

            if debug: print '\n setting verify_cache_required True...'
            if debug:
                if not cache.get('asset_list'): print '\n debug -- asset_list not cached...'
                if not cache.get('assets_dict'): print '\n debug -- assets_dict not cached...'
                if not cache.get('asset_rds'): print '\n debug -- asset_rds not cached...'
                if not cache.get('rd_assets'): print '\n debug -- rd_assets not cached...'

            verify_cache_required = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If required, get asset(s) supporting cache(s)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verify_cache_required or refresh:
            if debug: print '\n debug -- get_assets_payload...'
            data = get_assets_payload()
            if not data:
                message = 'No asset data returned from uframe.'
                current_app.logger.info(message)
                raise Exception(message)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Populate assets, return
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        else:
            data = cache.get('asset_list')


        return data

    except Exception as err:
        message = 'Error getting uframe assets. %s' % str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get all assets from uframe.
def get_assets_payload():
    """ Get all assets from uframe, process into ooi-ui-services list of assets (asset_list).
    Update caches for: 'asset_list', 'assets_dict', 'asset_rds', 'rd_assets'
    """
    debug = False
    try:
        print '\n Compiling assets...\n'
        if debug: print '\n    debug -- Clear caches related to assets...'
        try:
            # Clear all cache
            if cache.get('asset_list'):
                cache.delete('asset_list')
            if cache.get('assets_dict'):
                cache.delete('assets_dict')
            if cache.get('asset_rds'):
                cache.delete('asset_rds')
            if cache.get('rd_assets'):
                cache.delete('rd_assets')
        except Exception as err:
            message = str(err)
            raise Exception(message)
        if debug: print '\n    debug -- Cleared caches related to assets...'

        # Get assets from uframe
        if debug: print '\n    debug -- Get assets from uframe...'
        result = get_assets_from_uframe()
        if not result:
            message = 'Response content from uframe asset request is empty.'
            raise Exception(message)

        print '\n Number of uframe assets: %d' % len(result)

        # Get asset_list and asset_rds.
        if debug: print '\n    debug -- _compile_assets...'
        data, asset_rds = _compile_assets(result, compile_all=True)
        if not data:
            if debug: print '\n    debug -- error obtaining asset_list data...'
            message = 'Unable to process uframe assets; error creating assets_list.'
            raise Exception(message)
        if not asset_rds:
            if debug: print '\n    debug -- error obtaining asset_rds data...'
            message = 'Unable to process uframe assets; error creating asset_rds.'
            raise Exception(message)

        # Cache 'asset_list'.
        cache.set('asset_list', data, timeout=CACHE_TIMEOUT)
        check = cache.get('asset_list')
        if not check:
            if debug: print '\n    debug -- error checking asset_list data...'
            message = 'Unable to process uframe assets; error asset_list data is empty.'
            raise Exception(message)
        if debug: print '    debug -- Verify asset_list is available...'

        # Cache 'assets_rd'.
        cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
        if debug:
            print '    debug -- Verify \'asset_rds\' is available...'
            print '    debug -- Number of assets: : ', len(asset_rds)

        # Cache 'assets_dict'.
        assets_dict = populate_assets_dict(data)
        if assets_dict is None:
            message = 'Empty assets_dict returned from asset data.'
            raise Exception(message)
        if debug: print '    debug -- Verify assets_dict is available...'

        # Cache 'rd_assets'.
        rd_assets = _get_rd_assets()
        if not rd_assets:
            message = 'Empty rd_assets returned from asset data.'
            raise Exception(message)
        if debug: print '    debug -- Verify \'rd_assets\' available...'

        print '\n Completed compiling assets...\n'
        return data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get stream_list.
def get_stream_list():
    """ Get 'stream_list' from cache; if not cached, get and set cache.
    """
    debug = False
    stream_list = None
    try:
        stream_list_cached = cache.get('stream_list')
        if not stream_list_cached:
            if debug: print '    debug -- stream_list is not cached, get and set...'
            try:
                stream_list = dfs_streams()
            except Exception as err:
                message = str(err)
                raise Exception(message)

            if stream_list:
                if debug: print '    debug -- stream_list get completed'
                cache.set('stream_list', stream_list, timeout=CACHE_TIMEOUT)
                if debug: print '    debug -- stream_list set completed...'
            else:
                message = 'stream_list failed to return value, error.'
                if debug: print '    debug -- ', message
                current_app.logger.info(message)

        return stream_list

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get assets_dict.
def populate_assets_dict(data):
    """ Build and cache assets_dict from assets_list; on error log and return None.
    """
    debug = False
    try:
        # Using assets_list data, create asets_dict
        assets_dict = get_assets_dict_from_list(data)

        # If no assets_dict returned, log error
        if not assets_dict:
            message = 'Warning: empty assets_dict returned from get_assets_dict_from_list.'
            if debug: print '\n debug -- message: ', message
            current_app.logger.info(message)

        # Verify assets_dict is type dict
        elif isinstance(assets_dict, dict):
            cache.set('assets_dict', assets_dict, timeout=CACHE_TIMEOUT)
            if debug: print '    debug -- set \'assets_dict\' cache...'

        return assets_dict

    except Exception as err:
        message = 'Error populating \'assets_dict\'; %s' % str(err)
        current_app.logger.info(message)
        return None


# Get all assets from uframe.
def get_assets_from_uframe():
    """ Get all assets from uframe.
    """
    debug = False
    check = False
    time = True
    try:
        if debug: print '\n debug -- entered get_assets_from_uframe...'
        # Get uframe connect and timeout information
        start = dt.datetime.now()
        if time: print '\n-- Start time: ', start
        uframe_url, timeout, timeout_read = get_uframe_assets_info()
        timeout_extended = timeout_read * 2
        if debug: print '\n timeout_extended: ', timeout_extended
        url = '/'.join([uframe_url, get_assets_url_base()])
        if check: print '\n check -- [get_assets_from_uframe] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_extended))
        end = dt.datetime.now()
        if time: print '\n-- End time: ', start
        if time: print '\n-- Time to get uframe assets: %s' % str(end - start)
        if response.status_code != 200:
            message = '(%d) Failed to get uframe assets.' % response.status_code
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe assets.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe assets.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = 'Error getting uframe assets.  %s' % str(err)
        current_app.logger.info(message)
        raise


'''
# todo ======================================================
# todo - test with new asset REST interface
# todo ======================================================
def _get_bad_assets():
    """ Get all 'bad' assets (in ooi-ui-services format)
    """
    try:
        bad_asset_cache = cache.get('bad_asset_list')
        if bad_asset_cache:
            result_data = bad_asset_cache
        else:
            data = get_assets_from_uframe()
            try:
                result_data = _compile_bad_assets(data)
                cache.set('bad_asset_list', result_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        return result_data

    except Exception:
        raise


# todo ======================================================
# todo - test with new asset REST interface
# todo ======================================================
def _get_all_assets():
    """ Get all assets (complete or incomplete) (in ooi-ui-services format).
    """
    try:
        # Get 'good' assets
        asset_cache = cache.get('asset_list')
        if asset_cache:
            asset_data = asset_cache
        else:
            try:
                asset_data = get_assets_payload()
                cache.set('asset_list', asset_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        # Get 'bad' assets
        bad_asset_cache = cache.get('bad_asset_list')
        if bad_asset_cache:
            bad_asset_data = bad_asset_cache
        else:
            data = get_assets_from_uframe()
            try:
                bad_asset_data = _compile_bad_assets(data)
                cache.set('bad_asset_list', bad_asset_data, timeout=CACHE_TIMEOUT)
            except Exception as err:
                message = err.message
                raise Exception(message)

        result_data = asset_data + bad_asset_data
        if result_data:
            result_data.sort()
        return result_data

    except Exception:
        raise
'''

#===========================
# asset controller functions
#===========================
def _compile_assets(data, compile_all=False):
    """ Process list of asset dictionaries from uframe; transform into (ooi-ui-services) list of asset dictionaries.
    """
    debug = False
    info = True         # Log missing vocab items when unable to create display name(s), etc.
    feedback = False    # For development only: Display information as assets are processed
    new_data = []
    bad_data = []
    bad_data_ids = []

    vocab_failures = []             # Vocabulary failures identified during asset processing are written to log.
    dict_asset_ids = {}
    all_asset_types = []            # Gather from uframe asset collection all values of 'assetType' used
    all_asset_types_received = []   # Gather from uframe asset collection all values of 'assetType' received

    try:
        update_asset_rds_cache = False
        if debug:
            if data:
                print '\n debug -- data received: ', len(data)
            else:
                print '\n debug -- No asset data received to process in assetController.'

        # Get 'asset_rds' cache
        cached = cache.get('asset_rds')
        if cached:
            if debug: print '\n debug -- asset_rds is cached....'
            dict_asset_ids = cached

        if not cached or not isinstance(cached, dict):

            if debug: print '\n debug -- getting asset_rds...not cached...'
            # If no asset_rds cached, then fetch and cache
            asset_rds = {}
            #rds_wo_assets = []
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
                #print '\n cache asset_rds: ', asset_rds

            dict_asset_ids = asset_rds

            """
            # List of reference designators [in toc i.e./sensor/inv] but without associated asset id(s).
            # Usage: If rd in data catalog, but also in rds_wo_assets, no asset to navigate to.
            if rds_wo_assets:
                cache.set('rds_wo_assets', rds_wo_assets, timeout=CACHE_TIMEOUT)
                print "Reference designators with out assets ('rds_wo_assets') cache reset..."
            """

        # Ensure 'rd_assets' is in cache
        rd_assets = _get_rd_assets()

    except Exception as err:
        message = 'Error compiling asset_rds: %s' % err.message
        current_app.logger.info(message)
        raise Exception(message)

    # Process uframe list of asset dictionaries (data)
    valid_asset_classes = get_asset_classes()

    # Valid processing types are those assetTypes which are subsequently mapped to reference designators.
    valid_processing_types_uc = get_supported_asset_types()
    valid_processing_types = []
    for type in valid_processing_types_uc:
        valid_processing_types.append(type.lower())
    if debug: print '\n debug -- valid_processing_types: ', valid_processing_types

    no_deployments_title = '\nFollowing reference designators are missing assets ids for deployment(s) listed: '
    all_no_deployments_message = ''
    all_no_deployments_dict = {}

    # todo ======================================
    # todo - get this out of here ASAP, refactor
    # todo ======================================
    from ooiservices.app.uframe.deployment_tools import get_asset_deployment_map

    for row in data:
        ref_des = ''
        try:
            # Get asset_id, if not asset_id then continue
            row['augmented'] = False
            asset_id = None
            if 'assetId' in row:
                row['id'] = row.pop('assetId')
                asset_id = row['id']
                if asset_id is None:
                    bad_data.append(row)
                    continue
                if not asset_id:
                    bad_data.append(row)
                    continue

            if 'events' in row:
                del row['events']
            if 'calibration' in row:
                del row['calibration']
            if 'location' in row:
                del row['location']

            if len(row['remoteResources']) == 0:
                row['remoteResources'] = []

            # If asset is of type 'notClassified', add to bad_assets and continue
            if 'assetType' in row:
                if 'notClassified' == row['assetType'] or 'Array' == row['assetType']:
                    bad_data.append(row)
                    continue

            row['asset_class'] = row.pop('@class')

            # If ref_des not provided in row, use dictionary lookup.
            if asset_id in dict_asset_ids:
                ref_des = dict_asset_ids[asset_id]

            # Gather list of all assetType values RECEIVED (for information only)
            if row['assetType']:
                if row['assetType'] not in all_asset_types_received:
                    all_asset_types_received.append(row['assetType'])

            #if debug: print '\n debug ---- CHECK -------- (%r) ref_des: *%s*' % (asset_id, ref_des)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If no reference designator available, but have asset id then continue to next row.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not ref_des or ref_des is None:
                # If reference designator not provided, add to bad_assets, continue to next.
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Set row values with reference designator
            row['ref_des'] = ref_des
            row['Ref Des'] = ref_des
            if feedback: print '\n debug ---------------- (%r) ref_des: *%s*' % (asset_id, ref_des)

            if len(row['remoteResources']) == 0:
                row['remoteResources'] = []
            else:
                if debug: print '\n debug -- Asset id %d has remoteResources available (rd: %s: ' % (asset_id, ref_des)

            # Get type of asset we are processing, using reference designator. If invalid or None, continue.
            processing_asset_type = get_asset_type_by_rd(ref_des)
            if processing_asset_type:
                processing_asset_type = processing_asset_type.lower()
            if debug: print '\n debug -- processing_asset_type: ', processing_asset_type
            if processing_asset_type not in valid_processing_types:
                print '\n debug -- bad processing_asset_type: ', processing_asset_type
                continue

            if debug: print '\n debug -- before get_asset_deployment_map...'
            # Get deployment information for this asset_id-rd; populate asset values using deployment information.
            depth, location, has_deployment_event, deployment_numbers, tense, no_deployments_nums, deployments_list \
                                        = get_asset_deployment_map(asset_id, ref_des)
            if debug: print '\n debug -- after get_asset_deployment_map...'

            # If reference designator has deployments which do not have associated asset ids, compile information.
            if no_deployments_nums:
                # if ref_des not in all collection, add
                if ref_des not in all_no_deployments_dict:
                    all_no_deployments_dict[ref_des] = no_deployments_nums
                else:
                    for did in no_deployments_nums:
                        if did not in all_no_deployments_dict[ref_des]:
                            all_no_deployments_dict[ref_des].append(did)

            row['depth'] = depth
            row['coordinates'] = location
            row['longitude'] = location[0]
            row['latitude'] = location[1]
            row['hasDeploymentEvent'] = has_deployment_event
            row['deployment_number'] = deployment_numbers
            row['deployment_numbers'] = deployments_list
            row['tense'] = tense

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get asset class based on reference designator
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['asset_class'] or row['asset_class'] is None:
                message = 'asset_class empty or null for asset id %d (reference designator %s)' % (asset_id, ref_des)
                current_app.logger.info(message)
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Validate asset_class, log asset class if unknown.
            asset_class = row.pop('asset_class')
            if asset_class not in valid_asset_classes:
                if info:
                    message = 'Reference designator (%s) has an asset class value (%s) not one of: %s' % \
                        (ref_des, asset_class, valid_asset_classes)
                    current_app.logger.info(message)
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Populate assetInfo dictionary
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            row['assetInfo'] = {
                'name': "",
                'type': '',
                'owner': '',
                'description': '',
                'longName': '',
                'array': '',
                'assembly': '',
                'asset_name': '',
                'mindepth': 0,
                'maxdepth': 0
            }
            # Asset owner
            row['assetInfo']['owner'] = row.pop('owner')

            # Populate assetInfo 'type' with uframe provided assetType todo review platform assetType values
            asset_type = row['assetType']
            if asset_type == 'Node':
                asset_type = 'Platform'
            row['assetInfo']['type'] = asset_type

            try:
                # Verify all necessary attributes are available, if not create and set to empty.
                if row['name']:
                    row['assetInfo']['asset_name'] = row.pop('name')

                if row['description']:
                    row['assetInfo']['description'] = row.pop('description')

                # Get vocabulary dict for ref_des; contains name, long_name, mindepth, maxdepth, model, manufacturer
                name = None
                longName = None
                mindepth = 0
                maxdepth = 0
                vocab_dict = get_vocab_dict_by_rd(ref_des)
                if vocab_dict:
                    row['assetInfo']['mindepth'] = vocab_dict['mindepth']
                    row['assetInfo']['maxdepth'] = vocab_dict['maxdepth']
                    name = vocab_dict['name']
                    longName = vocab_dict['long_name']
                else:
                    row['assetInfo']['mindepth'] = mindepth
                    row['assetInfo']['maxdepth'] = maxdepth

                # Populate assetInfo - name, if failure to get display name, use ref_des, log failure.
                # name = get_dn_by_rd(ref_des)
                #name = vocab_dict['name']
                if name is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    if info:
                        message = 'Vocab Note ----- reference designator (%s) failed to get display name for:' % ref_des
                        current_app.logger.info(message)
                    name = ref_des
                row['assetInfo']['name'] = name

                # Populate assetInfo - long name, if failure to get long name then use ref_des, log failure.
                #longName = get_ldn_by_rd(ref_des)
                if longName is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    if info:
                        message = 'Vocab Note ----- reference designator (%s) failed to get display name for:' % ref_des
                        current_app.logger.info(message)
                    longName = ref_des
                row['assetInfo']['longName'] = longName

                # Populate assetInfo - array and assembly
                if len(ref_des) >= 8:
                    if ref_des[:2] == 'RS':
                        row['assetInfo']['array'] = get_rs_array_display_name_by_rd(ref_des[:8])
                    else:
                        row['assetInfo']['array'] = get_dn_by_rd(ref_des[:2])
                if len(ref_des) >= 14:
                    row['assetInfo']['assembly'] = get_dn_by_rd(ref_des[:14])

                # Black box - place values into expected containers (minimize UI change)
                # todo - verify fields exist before proceeding with this section.
                row['manufactureInfo'] = {}
                row['manufactureInfo']['manufacturer'] = row.pop('manufacturer')
                row['manufactureInfo']['modelNumber'] = row.pop('modelNumber')
                row['manufactureInfo']['serialNumber'] = row.pop('serialNumber')
                row['manufactureInfo']['firmwareVersion'] = row.pop('firmwareVersion')
                row['manufactureInfo']['softwareVersion'] = row.pop('softwareVersion')
                row['manufactureInfo']['shelfLifeExpirationDate'] = row.pop('shelfLifeExpirationDate')
                row['remoteDocuments'] = []
                row['purchaseAndDeliveryInfo'] = {}
                row['purchaseAndDeliveryInfo']['deliveryDate'] = row.pop('deliveryDate')
                row['purchaseAndDeliveryInfo']['purchaseDate'] = row.pop('purchaseDate')
                row['purchaseAndDeliveryInfo']['purchasePrice'] = row.pop('purchasePrice')
                row['purchaseAndDeliveryInfo']['deliveryOrderNumber'] = row.pop('deliveryOrderNumber')
                row['partData'] = {}
                row['partData']['ooiPropertyNumber'] = row.pop('ooiPropertyNumber')
                row['partData']['ooiPartNumber'] = row.pop('ooiPartNumber')
                row['partData']['ooiSerialNumber'] = row.pop('ooiSerialNumber')
                row['partData']['institutionPropertyNumber'] = row.pop('institutionPropertyNumber')
                row['partData']['institutionPurchaseOrderNumber'] = row.pop('institutionPurchaseOrderNumber')

                # Move powerRequirements and depthRating into physicalInfo dictionary
                if 'physicalInfo' in row:
                    row['physicalInfo']['depthRating'] = row.pop('depthRating')
                    row['physicalInfo']['powerRequirements'] = row.pop('powerRequirements')     # [req 3.1.6.10]

                # Gather list of all assetType values (information only)
                if row['assetType']:
                    if row['assetType'] not in all_asset_types:
                        all_asset_types.append(row['assetType'])

            except Exception as err:
                # asset info error
                current_app.logger.info('asset info error' + str(err.message))
                if debug: print '\n debug -- error: ', str(err)
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Add new row to output dictionary
            if asset_id and ref_des:
                row['augmented'] = True
                new_data.append(row)
                # if new item for dictionary of asset ids, add id with value of reference designator
                if asset_id not in dict_asset_ids:
                    dict_asset_ids[asset_id] = ref_des
                    update_asset_rds_cache = True

        except Exception as err:
            current_app.logger.info(str(err))
            if debug: print '\n debug -- error: ', str(err)
            continue

    # If reference designators with missing deployment(s), log sorted by reference designator.
    if all_no_deployments_dict:
        the_keys = all_no_deployments_dict.keys()
        the_keys.sort()

        # Display reference designators with missing deployment(s), sorted by reference designator.
        for key in the_keys:
            all_no_deployments_message += '\n%s: %s' % (key, all_no_deployments_dict[key])
        missing_deployment_message = no_deployments_title + all_no_deployments_message
        if debug: print '\n debug -- missing_deployment_message: ', missing_deployment_message
        current_app.logger.info(missing_deployment_message)

    # Log vocabulary failures (occur when creating display names)
    if vocab_failures:
        vocab_failures.sort()
        message = 'These reference designator(s) are not defined, causing display name failures(%d): %s' \
                  % (len(vocab_failures), vocab_failures)
        current_app.logger.info(message)

    if compile_all:
        # Amend 'dict_asset_ids' to reflect information from processing
        if dict_asset_ids:
            if update_asset_rds_cache:
                cache.set('asset_rds', dict_asset_ids, timeout=CACHE_TIMEOUT)

        # Update cache for 'bad_asset_list'
        bad_assets_cached = cache.get('bad_asset_list')
        if bad_assets_cached:
            cache.delete('bad_asset_list')
            cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)
        else:
            cache.set('bad_asset_list', bad_data, timeout=CACHE_TIMEOUT)

        #if all_asset_types:
        #    cache.set('asset_types', all_asset_types, timeout=CACHE_TIMEOUT)

    if debug:
        print '\n debug -- len(dict_asset_ids): ', len(dict_asset_ids)
        print '\n debug -- len(new_data): ', len(new_data)
        print '\n Note:\n Asset types used: ', all_asset_types
        print ' Asset types received: ', all_asset_types_received

    return new_data, dict_asset_ids


def _get_rd_assets():
    """ Get 'rd_assets', if not available get and set cache; return 'rd_assets' dictionary.
    """
    # todo get this out of here.........
    from ooiservices.app.uframe.deployment_tools import _compile_rd_assets
    debug = False
    rd_assets = {}
    try:
        if debug: print '\n debug -- entered _get_rd_assets...*****************************************************'

        # Get 'rd_assets' if cached
        rd_assets_cached = cache.get('rd_assets')
        if rd_assets_cached:
            rd_assets = rd_assets_cached

        # Get 'rd_assets' - compile them
        else:
            if debug: print '\n debug -- rd_assets not cached, _compile_rd_assets then check cache...'
            try:
                rd_assets = _compile_rd_assets()
            except Exception as err:
                message = 'Error processing _compile_rd_assets: ', err.message
                current_app.logger.warning(message)

            # Cache rd_assets
            if rd_assets:
                cache.set('rd_assets', rd_assets, timeout=CACHE_TIMEOUT)
                if debug:
                    print "[+] Reference designators to assets cache reset..."
                    print '\n len(asset_rds): ', len(rd_assets)
            else:
                if debug: print "[-] Error in rd_assets cache update"

        if debug: print '\n debug -- Length of rd_assets: %d' % len(rd_assets)
        return rd_assets

    except Exception as err:
        message = 'Exception processing _get_rd_assets: %s' % str(err)
        current_app.logger.info(message)
        return {}




#====================================================================
# todo - Modify for new asset management data model
# todo - Note: used by controller.py: get_svg_plot and dfs_streams
#====================================================================
def get_events_by_ref_des(data, ref_des):
    """ Create the container for the processed response.
    """
    result = []
    '''
    # Get all the events to begin searching though...
    for row in data:
        # variables used in loop
        temp_dict = {}
        ref_des_check = ""
        try:

            if 'referenceDesignator' in row and row['referenceDesignator']['full']:
                ref_des_check = (row['referenceDesignator']['subsite'] + '-' + row['referenceDesignator']['node'] +
                                 '-' + row['referenceDesignator']['sensor'])
            else:
                if row['asset']['metaData']:
                    for metaData in row['asset']['metaData']:
                        if metaData['key'] == 'Ref Des':
                            ref_des_check = metaData['value']
            if ref_des_check == ref_des:
                temp_dict['ref_des'] = ref_des_check
                temp_dict['id'] = row['id']
                temp_dict['eventClass'] = row['eventClass']
                if row['eventClass'] == '.DeploymentEvent':
                    temp_dict['cruise_number'] = row['cruiseNumber']
                    temp_dict['cruise_plan_doc'] = row['cruisePlanDocument']
                    temp_dict['depth'] = row['depth']
                    temp_dict['lat_lon'] = row['locationLonLat']
                    temp_dict['deployment_number'] = row['deploymentNumber']
                temp_dict['tense'] = row['tense']
                start_date = num2date(float(row['startDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
                temp_dict['start_date'] = start_date.strftime("%B %d %Y, %I:%M:%S %p")
                if row['endDate'] is not None:
                    end_date = num2date(float(row['endDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
                    temp_dict['end_date'] = end_date.strftime("%B %d %Y, %I:%M:%S %p")
                temp_dict['event_description'] = row['eventDescription']
                temp_dict['event_type'] = row['eventType']
                temp_dict['notes'] = row['notes']
                result.append(temp_dict)
                temp_dict = {}
        except (KeyError, TypeError):
            raise
    '''
    result = jsonify({'events': result})
    return result


# todo - Update for new asset model
def _compile_bad_assets(data):
    """ Process list of 'bad' asset dictionaries from uframe; return list of bad assets.
    transform into (ooi-ui-services) list of asset dictionaries.
    """
    bad_data = []
    bad_data_ids = []
    info = False           # detect missing vocab items when unable to create display name(s)
    feedback = False       # (development/debug) display messages while processing each asset
    vocab_failures = []
    dict_asset_ids = {}
    try:
        cached = cache.get('asset_rds')
        if cached:
            dict_asset_ids = cached
        if not cached or not isinstance(cached, dict):
            # If no asset_rds cached, then fetch and cache
            asset_rds = {}
            rds_wo_assets = []
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
            else:
                message = 'Error in asset_rds cache update.'
                current_app.logger.warning(message)

            dict_asset_ids = asset_rds

            """
            # List of reference designators [in toc i.e./sensor/inv] but without associated asset id(s).
            # Usage: If rd in data catalog, but also in rds_wo_assets, no asset to navigate to.
            if rds_wo_assets:
                cache.set('rds_wo_assets', rds_wo_assets, timeout=CACHE_TIMEOUT)
                if debug: print "[+] Reference designators with assets cache reset..."
            """

    except Exception as err:
        message = 'Error compiling asset_rds: %s' % err.message
        current_app.logger.info(message)
        raise Exception(message)

    # Process uframe list of asset dictionaries (data)
    valid_asset_classes = ['.InstrumentAssetRecord', '.NodeAssetRecord', '.AssetRecord']
    for row in data:
        ref_des = ''
        lat = ""
        lon = ""
        latest_deployment = None
        has_deployment_event = False
        deployment_number = ""
        try:
            # Get asset_id, if not asset_id then continue
            row['augmented'] = False
            asset_id = None
            if 'assetId' in row:
                row['id'] = row.pop('assetId')
                asset_id = row['id']
                if asset_id is None:
                    bad_data.append(row)
                    continue
                if not asset_id:
                    bad_data.append(row)
                    continue

            row['asset_class'] = row.pop('@class')
            #row['events'] = associate_events(row['id'])
            if len(row['events']) == 0:
                row['events'] = []
            row['tense'] = None

            # If ref_des not provided in row, use dictionary lookup.
            if asset_id in dict_asset_ids:
                ref_des = dict_asset_ids[asset_id]

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # If no reference designator available, but have asset id, continue.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not ref_des or ref_des is None:
                # If reference designator not provided, use lookup; if still no ref_des, continue
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

            # Set row values with reference designator
            row['ref_des'] = ref_des
            row['Ref Des'] = ref_des
            if feedback: print '\n debug ---------------- (%r) ref_des: *%s*' % (asset_id, ref_des)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get asset class based on reference designator
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            if not row['asset_class'] or row['asset_class'] is None:
                if len(ref_des) == 27:
                    row['asset_class'] = '.InstrumentAssetRecord'
                elif len(ref_des) == 14:
                    row['asset_class'] = '.NodeAssetRecord'
                elif len(ref_des) == 8:
                    row['asset_class'] = '.AssetRecord'
                else:
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue
            else:
                # Log asset class is unknown.
                asset_class = row['asset_class']
                if asset_class not in valid_asset_classes:
                    if asset_id not in bad_data_ids:
                        bad_data_ids.append(asset_id)
                        bad_data.append(row)
                    continue

            if deployment_number is not None:
                row['deployment_number'] = deployment_number

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Process events
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            for events in row['events']:
                if events['eventClass'] == '.DeploymentEvent':
                    has_deployment_event = True
                    if events['tense'] == 'PRESENT':
                        row['tense'] = events['tense']
                    else:
                        row['tense'] = 'PAST'
                if latest_deployment is None and\
                        events['locationLonLat'] is not None and\
                        len(events['locationLonLat']) == 2:
                    latest_deployment = events['startDate']
                    lat = events['locationLonLat'][1]
                    lon = events['locationLonLat'][0]
                if events['locationLonLat'] is not None and\
                        latest_deployment is not None and\
                        len(events['locationLonLat']) == 2 and\
                        events['startDate'] > latest_deployment:
                    latest_deployment = events['startDate']
                    lat = events['locationLonLat'][1]
                    lon = events['locationLonLat'][0]
            row['hasDeploymentEvent'] = has_deployment_event
            #row['coordinates'] = convert_lat_lon(lat, lon)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Populate assetInfo dictionary
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['assetInfo']:
                row['assetInfo'] = {
                    'name': '',
                    'type': '',
                    'owner': '',
                    'description': ''
                }

            # Populate assetInfo type
            if row['asset_class'] == '.InstrumentAssetRecord':
                row['assetInfo']['type'] = 'Sensor'
            elif row['asset_class'] == '.NodeAssetRecord':
                row['assetInfo']['type'] = 'Mooring'
            elif row['asset_class'] == '.AssetRecord':
                if len(ref_des) == 27:
                    row['assetInfo']['type'] = 'Sensor'
                elif len(ref_des) == 14:
                    row['assetInfo']['type'] = 'Platform'
                elif len(ref_des) == 8:
                    row['assetInfo']['type'] = 'Mooring'
                else:
                    if info:
                        message = 'Asset id %d, type .AssetRecord, has malformed a reference designator (%s)' % \
                                  (asset_id, ref_des)
                        current_app.logger.info(message)
                    row['assetInfo']['type'] = 'Unknown'
            else:
                if info:
                    message = 'Note ----- Unknown asset_class (%s), set to \'Unknown\'. ' % row['assetInfo']['type']
                    current_app.logger.info(message)
                row['assetInfo']['type'] = 'Unknown'
            try:
                # Verify all necessary attributes are available, if not create and set to empty.
                if 'name' not in row['assetInfo']:
                    row['assetInfo']['name'] = ''
                if 'longName' not in row['assetInfo']:
                    row['assetInfo']['longName'] = ''
                if 'array' not in row['assetInfo']:
                    row['assetInfo']['array'] = ''
                if 'assembly' not in row['assetInfo']:
                    row['assetInfo']['assembly'] = ''

                # Populate assetInfo - name and long name; if failure to get display name, use ref_des, log failure.
                name = get_dn_by_rd(ref_des)
                if name is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    name = ref_des
                longName = get_ldn_by_rd(ref_des)
                if longName is None:
                    if ref_des not in vocab_failures:
                        vocab_failures.append(ref_des)
                    longName = ref_des
                row['assetInfo']['name'] = name
                row['assetInfo']['longName'] = longName

                # Populate assetInfo - array and assembly
                if len(ref_des) >= 8:
                    row['assetInfo']['array'] = get_dn_by_rd(ref_des[:2])
                if len(ref_des) >= 14:
                    row['assetInfo']['assembly'] = get_dn_by_rd(ref_des[:14])

            except Exception:
                if asset_id not in bad_data_ids:
                    bad_data_ids.append(asset_id)
                    bad_data.append(row)
                continue

        except Exception:
            continue

    """
    print '\n debug -- len(bad_data): ', len(bad_data)
    print '\n debug -- len(bad_data_ids): ', len(bad_data_ids)
    """

    return bad_data