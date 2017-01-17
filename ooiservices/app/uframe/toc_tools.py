#!/usr/bin/env python

"""
TOC: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app import cache
from ooiservices.app.uframe.uframe_tools import get_toc_information
from ooiservices.app.uframe.vocab import (get_long_display_name_by_rd, get_display_name_by_rd)
CACHE_TIMEOUT = 172800


def process_uframe_toc():
    """ Get toc content from uframe; if error raise. Continue processing based on toc content.
    """
    result = None
    debug = False
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
        if debug: print '\n debug -- get_uframe_toc result: ', result
        return result
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception process_uframe_toc...'
        raise Exception(message)


#@cache.memoize(timeout=1600)
def get_uframe_toc(data):
    """ Process uframe response from /sensor/inv/toc into list of dictionaries for use in UI.

    The toc response has three [required] dictionaries:
        u'instruments', u'parameters_by_stream', u'parameter_definitions'.

    Process toc response into a a list of dictionaries.
    """
    debug = False
    error_debug = True  # (default to True) This produces an informational message in ooiservice.log
    error_messages = []

    results = []
    try:
        if debug: print '\n Entered get_uframe_toc...'
        required_components = ['instruments']
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
            if debug: print '\n debug -- No data to be returned....'
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


#@cache.memoize(timeout=1600)
def get_toc_reference_designators():
    """ Get toc and process for reference designators.
    """
    try:
        toc_rds = cache.get('toc_rds')
        if toc_rds and toc_rds is not None and 'error' not in toc_rds:
            reference_designators = toc_rds
            toc_only = []
            difference = None
        else:
            reference_designators, toc_only, difference = compile_toc_reference_designators()

        """
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
        """
        return reference_designators, toc_only, difference
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return [], [], []


def compile_toc_reference_designators():
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

        cache.set('toc_rds', reference_designators, timeout=CACHE_TIMEOUT)

        return reference_designators, toc_only, difference
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return [], [], []
