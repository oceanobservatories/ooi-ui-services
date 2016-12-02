#!/usr/bin/env python

"""
TOC: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app

from ooiservices.app.uframe.uframe_tools import get_toc_information
from ooiservices.app.uframe.vocab import (get_long_display_name_by_rd, get_display_name_by_rd)


#from ooiservices.app import cache
#from ooiservices.app.uframe.vocab import get_rs_array_name_by_rd
#from ooiservices.app import cache
#from ooiservices.app.uframe.config import stream_new_data
#from ooiservices.app.uframe.config import get_uframe_assets_info
#from ooiservices.app.uframe.uframe_tools import (get_toc_information, get_rd_deployments)
#NEW_STREAM_INFO = False

def process_uframe_toc():
    """ Get toc content from uframe; if error raise. Continue processing based on toc content.
    """
    result = None
    try:
        d = get_toc_information()
        if d is not None:
            if isinstance(d, dict):
                result = get_uframe_toc(d)
            # Using deprecated toc structure; log message here and raise exception.
            else:
                message = 'Use proper toc dictionary format. Check configuration.'
                current_app.logger.info(message)
                raise Exception(message)
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


#@cache.memoize(timeout=1600)
def get_uframe_toc(data):
    """ Process uframe response from /sensor/inv/toc into list of dictionaries for use in UI.

    The toc response has three [required] dictionaries:
        u'instruments', u'parameters_by_stream', u'parameter_definitions'.

    Process toc response into a a list of dictionaries.
    """
    debug = True
    error_debug = True  # This produces an informational message in ooiservice.log (default to True)
    error_messages = []

    results = []
    try:
        required_components = ['instruments']
        """
        if not stream_new_data():
            required_components = ['instruments', 'parameters_by_stream', 'parameter_definitions']
        else:
            required_components = ['instruments']
        """
        if data:
            # Validate required components are provided in uframe toc data and not empty.
            for component in required_components:
                if component not in data:
                    message = 'The uframe toc data does not contain required component %s.' % component
                    raise Exception(message)
                if not data[component]:
                    message = 'The uframe toc data contains required component %s, but it is empty.' % component
                    raise Exception(message)

            # Get working dictionary of parameter definitions keyed by pdId.
            # Remove for data catalog.
            #parameter_definitions_dict, all_pdids = get_toc_parameter_dict(data['parameter_definitions'])

            # Process all instruments to compile result
            instruments = data['instruments']
            """
            parameters_by_streams = {}
            if not stream_new_data():
                parameters_by_streams = data['parameters_by_stream']       # todo - Remove for data catalog
                if debug: print '\n debug -- Number of elements in parameters_by_streams: ', len(parameters_by_streams.keys())
            """
            for instrument in instruments:

                # Get reference designator and swap mooring and platform code
                rd = instrument['reference_designator']
                mooring = instrument['platform_code']
                platform = instrument['mooring_code']
                result = instrument
                result['mooring_code'] = mooring
                result['platform_code'] = platform

                # Get instrument_display_name, mooring_display_name, platform_display_name; add to result
                result['instrument_display_name'], \
                result['platform_display_name'], \
                result['mooring_display_name'] = get_names_for_toc(rd, mooring, platform)

                result['instrument_parameters'] = []
                """
                #-------------------------------- Not required for data catalog todo
                if not stream_new_data():
                    # Get "instrument_parameters" for instrument; if error return empty list and log errors.
                    param_results, error_messages = get_instrument_parameters(instrument,
                                                                              parameters_by_streams,
                                                                              parameter_definitions_dict,
                                                                              error_messages)

                    if param_results is None:
                        result['instrument_parameters'] = []
                        continue

                    instrument_parameters = param_results
                    #-------------------------------- End Not required for data catalog todo

                    result['instrument_parameters'] = instrument_parameters # [] remove not needed for data catalog
                else:
                    result['instrument_parameters'] = []
                """
                results.append(result)

            # Determine if error_messages received during processing; if so, write to log
            if error_debug:
                if error_messages:
                    error_message = 'Error messages in uframe toc content:\n'
                    for message in error_messages:
                        error_message += message + '\n'
                    current_app.logger.info(error_message)

            return results
        else:
            return []
    except Exception as err:
        message = '[get_uframe_toc] exception: %s' % str(err.message)
        current_app.logger.info(message)
        raise Exception(message)


def get_names_for_toc(rd, mooring, platform):
    """ Get display names for toc processing.
    """
    _instrument_display_name = ""
    _mooring_display_name = ""
    _platform_display_name = ""
    try:
        instrument_display_name = get_long_display_name_by_rd(rd)
        if ' - ' in instrument_display_name:
            split_name = instrument_display_name.split(' - ')
            _instrument_display_name = split_name[-1]
            _mooring_display_name = split_name[0]
            _platform_display_name = split_name[1]
        elif '-' in rd:
            mooring, platform, instr = rd.split('-', 2)
            _mooring_display_name = get_display_name_by_rd(mooring)
            tmp_platform = '-'.join([mooring, platform])
            _platform_display_name = get_display_name_by_rd(tmp_platform)
            _instrument_display_name = get_display_name_by_rd(rd)

        return _instrument_display_name, _mooring_display_name, _platform_display_name
    except:
        return "", "", ""

'''
# todo - deprecate
def get_instrument_parameters(instrument, parameters_by_stream, parameter_definitions_dict, error_messages):
    """ For an instrument, return instrument parameters list and error_messages list.

    TODO: Add error processing for following:
        if 'streams' not in instrument:
            if not instrument['streams']:
    """
    debug = False
    errors = False
    rd = None
    try:
        rd = instrument['reference_designator']

        # For each instrument, get instrument_parameters for all streams
        instrument_parameters = []

        # Get all stream names for instrument
        tmp_stream_names = get_stream_names(instrument['streams'])
        if debug: print '\n debug -- Number of stream names: ', len(tmp_stream_names)
        for stream_name in tmp_stream_names:

            # Determine stream name has parameter data; if not, error_message
            if stream_name not in parameters_by_stream:
                message = 'Stream %s not provided in parameters_by_stream; used by instrument %s' % (stream_name, rd)
                error_messages.append(message)
                errors = True
                continue

            # Get pdIds for stream from dict 'parameters_by_stream'
            tmp_pdids = parameters_by_stream[stream_name]
            for pdid in tmp_pdids:

                # Determine if pdid in definitions dictionary, if not then error_message
                if pdid not in parameter_definitions_dict:
                    message = 'A pdId %s used by instrument %s ' % (pdid, rd)
                    message += ' not provided in uframe toc \'parameter_definitions\.'
                    error_messages.append(message)
                    errors = True
                    continue

                # If parameter definition is empty, error_message
                if not parameter_definitions_dict[pdid]:
                    message = 'A pdId %s used by instrument %s ' % (pdid, rd)
                    message += ' provided in uframe toc \'parameter_definitions\ is empty.'
                    error_messages.append(message)
                    errors = True
                    continue

                # Get pdid parameter definition
                tmp_param = (parameter_definitions_dict[pdid]).copy()
                tmp_param['stream'] = stream_name

                # Add stream name to parameter dictionary (data enrichment for UI)
                instrument_parameters.append(tmp_param)

        if errors:
            instrument_parameters = None

        return instrument_parameters, error_messages

    except Exception:
        message = 'Exception processing instrument parameters for %s.' % rd
        current_app.logger.info(message)
        return None, error_messages


def get_toc_parameter_dict(definitions):
    """ Process the uframe toc['parameter_definitions'] list into a list of dict keyed by pdId. Return dict and pdids.
    """
    result = {}
    pdids = []
    if not definitions:
        return {}
    for definition in definitions:
        pdid = definition['pdId']
        if pdid:
            if pdid not in pdids:
                definition['particleKey'] = definition['particle_key']
                del definition['particle_key']
                pdids.append(pdid)
                result[pdid] = definition
    return result, pdids
'''

def get_stream_names(streams):
    """ For an instrument, process streams (list of dictionaries), create list of stream names.
    """
    stream_names = []
    if streams:
        for stream in streams:
            if stream['stream'] not in stream_names:
                stream_names.append(stream['stream'])
    return stream_names


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

'''
# DO NOT DELETE
def _compile_asset_rds():
    """ Retrieve asset_ids from uframe for all reference designators referenced in /sensor/inv/toc structure;
    return dictionary with key of asset_id. On error, log and raise exception.  Does NOT cache.
    Note:
        - All reference designators are determined from toc structure and not just what /sensor/inv/toc provides.

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
    result = {}
    rds_wo_assets = []
    time = False
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

        # Process reference designators.
        reference_designators, toc_only, difference = process_toc_reference_designators(toc)
        if not reference_designators:
            message = 'No reference_designators identified when processing toc information.'
            raise Exception(message)

        if time: print '\t-- Number of reference designators to be processed: ', len(reference_designators)
        if reference_designators and toc_only:
            uframe_url, timeout, timeout_read = get_uframe_assets_info()
            #=================================================
            for rd in reference_designators:
                if rd and rd is not None:
                    try:
                        len_rd = len(rd)
                        ids, mrd, mids, nrd, nids = get_asset_id_by_rd(rd, uframe_url, timeout, timeout_read)
                    except Exception as err:
                        message = 'Exception raised in get_asset_id_by_rd: %s' % str(err)
                        current_app.logger.info(message)
                        #raise Exception(message)
                        continue
                    if not ids and not mids and not nids:
                        if rd and rd is not None:
                            if rd not in rds_wo_assets:
                                rds_wo_assets.append(rd)
                    # Instrument?
                    if len_rd > 14 and len_rd <= 27:
                        if ids:
                            ids.sort()
                            for id in ids:
                                if id not in result:
                                    result[id] = rd
                    # Mooring?
                    if len_rd == 8:
                        if mids:
                            for id in mids:
                                if id not in result:
                                    result[id] = rd
                    # Node?
                    if len_rd == 14:
                        if nids:
                            for id in nids:
                                if id not in result:
                                    result[id] = nrd
            #=================================================
        """
        # Identify reference designators in /sensor/inv which do not have associated asset ids.
        if rds_wo_assets:
            message = 'The following reference designators do not have an associated asset(%d): %s ' % \
                      (len(rds_wo_assets), rds_wo_assets)
            current_app.logger.info(message)
        """
        return result, rds_wo_assets

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}, []
'''

'''
def get_asset_id_by_rd(rd, uframe_url=None, timeout=None, timeout_read=None):
    """ For a reference designator, get uframe asset ids. Return list of asset ids; On error return [].
    """
    try:
        if not rd or rd is None:
            return [], None, [], None, []

        # Get deployments for reference designator (no notes).
        # Query url format: host:port/events/deployment/query?refdes=XXXXXXXX
        result = get_rd_deployments(rd)

        # If deployments returned, process for ids
        if result:
            ids, mooring, mooring_ids, node_name, node_ids = get_asset_ids_for_deployments(rd, result)
        else:
            ids = []
            mooring = None
            mooring_ids = []
            node_name = None
            node_ids = []
        return ids, mooring, mooring_ids, node_name, node_ids
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return [], None, [], None, []


def get_asset_ids_for_deployments(rd, result):
    ids = []
    mooring_ids = []
    node_ids = []

    #test = False
    try:
        # If result returned, process for ids
        if result:
            len_rd = len(rd)
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

                    """
                    #===========================
                    if test:
                        if 'mooring' in item:
                            if item['mooring']:
                                if 'assetId' in item['mooring']:
                                    if item['mooring']['assetId']:
                                        if item['mooring']['assetId'] not in mooring_ids:
                                            mooring_ids.append(item['mooring']['assetId'])
                        if 'node' in item:
                            if item['node']:
                                if 'assetId' in item['node']:
                                    if item['node']['assetId']:
                                        if item['node']['assetId'] not in node_ids:
                                            node_ids.append(item['node']['assetId'])
                    #===========================
                    """

                # Reference Designator of Mooring (assetType mooring)
                elif len_rd == 8:
                    if 'mooring' in item:
                        if item['mooring']:
                            if 'assetId' in item['mooring']:
                                if item['mooring']['assetId']:
                                    if item['mooring']['assetId'] not in mooring_ids:
                                        mooring_ids.append(item['mooring']['assetId'])

                    """
                    #===========================
                    if test:
                        if 'node' in item:
                            if item['node']:
                                if 'assetId' in item['node']:
                                    if item['node']['assetId']:
                                        if item['node']['assetId'] not in node_ids:
                                            node_ids.append(item['node']['assetId'])
                        if 'sensor' in item:
                            if item['sensor']:
                                if 'assetId' in item['sensor']:
                                    if item['sensor']['assetId']:
                                        if item['sensor']['assetId'] not in ids:
                                            ids.append(item['sensor']['assetId'])
                    #===========================
                    """

                # Reference Designator of Platform (assetType node)
                elif len_rd == 14:
                    if 'node' in item:
                        if item['node']:
                            if 'assetId' in item['node']:
                                if item['node']['assetId']:
                                    if item['node']['assetId'] not in node_ids:
                                        node_ids.append(item['node']['assetId'])

                    """
                    #===========================
                    if test:
                        if 'sensor' in item:
                            if item['sensor']:
                                if 'assetId' in item['sensor']:
                                    if item['sensor']['assetId']:
                                        if item['sensor']['assetId'] not in ids:
                                            ids.append(item['sensor']['assetId'])
                        if 'mooring' in item:
                            if item['mooring']:
                                if 'assetId' in item['mooring']:
                                    if item['mooring']['assetId']:
                                        if item['mooring']['assetId'] not in mooring_ids:
                                            mooring_ids.append(item['mooring']['assetId'])
                    #===========================
                    """

                else:
                    message = 'rd %s has a length of %d therefore not processed.' % (rd, len_rd)
                    current_app.logger.info(message)

        if ids:
            ids.sort(reverse=True)

        #----
        # Added when moved to get_rd_deployments(rd)
        mooring = None
        if mooring_ids:
            mooring_ids.sort(reverse=True)
            if len(rd) >= 8:
                mooring = rd[:8]
        #----
        node_name = None
        if node_ids:
            if len(rd) >= 14 and len(rd) <= 27:
                node_name = rd[:14]             # "-".join([mooring, platform])
            node_ids.sort(reverse=True)

        return ids, mooring, mooring_ids, node_name, node_ids
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []
'''

#@cache.memoize(timeout=1600)
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
        reference_designators, toc_only, difference = process_toc_reference_designators(toc)
        if not reference_designators:
            message = 'No reference_designators identified when processing toc information.'
            raise Exception(message)

        return reference_designators, toc_only, difference
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return [], [], []


'''
def _compile_asset_rds():
    """ Retrieve asset_ids from uframe for all reference designators referenced in /sensor/inv/toc structure;
    return dictionary with key of asset_id. On error, log and raise exception.  Does NOT cache.
    Note:
        - All reference designators are determined from toc structure and not just what /sensor/inv/toc provides.

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
    print '\n Warning -- Entered _compile_asset_rds...'
    result = {}
    rds_wo_assets = []
    time = True
    test = False
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

        # Process reference designators.
        reference_designators, toc_only, difference = process_toc_reference_designators(toc)
        if not reference_designators:
            message = 'No reference_designators identified when processing toc information.'
            raise Exception(message)

        if time:
            print '\t-- Number of reference designators to be processed: ', len(reference_designators)
            print '\t-- Number of reference designators in toc_only: ', len(toc_only)
        if reference_designators and toc_only:
            uframe_url, timeout, timeout_read = get_uframe_assets_info()
            #=================================================
            for rd in reference_designators:
                if rd and rd is not None:
                    try:

                        len_rd = len(rd)
                        if len_rd == 0:
                            print '\n *** Warning: Located empty reference designator in list.'
                            continue
                        #======================================

                        if test:
                            if rd[:2] != 'RS':
                                continue
                        if time: print '-- Processing: ', rd
                        #======================================
                        ids, mrd, mids, nrd, nids = get_asset_id_by_rd(rd, uframe_url, timeout, timeout_read)
                    except Exception as err:
                        message = 'Exception raised in get_asset_id_by_rd: %s' % str(err)
                        current_app.logger.info(message)
                        #raise Exception(message)
                        continue
                    if not ids and not mids and not nids:
                        if rd not in rds_wo_assets:
                            rds_wo_assets.append(rd)
                            continue
                    # Instrument?
                    if len_rd > 14 and len_rd <= 27:
                        if ids:
                            ids.sort()
                            for id in ids:
                                if id not in result:
                                    result[id] = [rd]
                                else:
                                    result[id].append(rd)
                        """
                        if test:
                            if mids:
                                print '\n\t-- processing instrument %s and have mooring ids.' % rd
                                for id in mids:
                                    if id not in result:
                                        result[id] = [rd[:8]]
                                    else:
                                        result[id].append(rd[:8])
                            if nids:
                                print '\n\t-- processing instrument %s and have node ids.' % rd
                                print '\n nhrd: ', nrd
                                for id in nids:
                                    if id not in result:
                                        result[id] = [rd[:14]]      # why not rd?
                                    else:
                                        result[id].append(rd[:14])
                        """
                    # Mooring?
                    elif len_rd == 8:
                        if mids:
                            for id in mids:
                                if id not in result:
                                    result[id] = [rd]
                                else:
                                    result[id].append(rd)
                        """
                        if test:
                            if ids:
                                print '\n\t-- processing mooring %s and have sensor ids.' % rd
                                if ids:
                                    ids.sort()
                                    for id in ids:
                                        if id not in result:
                                            result[id] = [rd]
                                        else:
                                            result[id].append(rd)
                            if nids:
                                print '\n\t-- processing mooring %s and have node ids.' % rd
                                print '\n nhrd: ', nrd
                                for id in nids:
                                    if id not in result:
                                        result[id] = [nrd]      # why not rd?
                                    else:
                                        result[id].append(nrd)
                        """
                    # Node?
                    elif len_rd == 14:
                        if nids:
                            print '\n nhrd: ', nrd
                            for id in nids:
                                if id not in result:
                                    result[id] = [rd]      # why not rd?
                                else:
                                    result[id].append(rd)
                        """
                        if test:

                            if ids:
                                print '\n\t-- processing node %s and have sensor ids.' % rd
                                if ids:
                                    ids.sort()
                                    for id in ids:
                                        if id not in result:
                                            result[id] = [rd]
                                        else:
                                            result[id].append(rd)

                            if mids:
                                print '\n\t-- processing node %s and have mooring ids.' % rd
                                for id in mids:
                                    if id not in result:
                                        result[id] = [rd[:8]]
                                    else:
                                        result[id].append(rd[:8])
                        """
                    else:
                        print '\n Warning: reference designator not processed for ids: \'%s\'.' % rd
            #=================================================
        """
        # Identify reference designators in /sensor/inv which do not have associated asset ids.
        if rds_wo_assets:
            message = 'The following reference designators do not have an associated asset(%d): %s ' % \
                      (len(rds_wo_assets), rds_wo_assets)
            current_app.logger.info(message)
        """
        return result, rds_wo_assets

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}, []
'''

