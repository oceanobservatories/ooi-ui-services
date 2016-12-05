#!/usr/bin/env python

"""
Asset Management - Status: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.vocab import (get_vocab_dict_by_rd, get_vocabulary_arrays, get_display_name_by_rd)
from ooiservices.app.uframe.common_tools import (get_array_locations, operational_status_values)
from ooiservices.app.uframe.uframe_tools import (uframe_get_sites_for_array, uframe_get_status_by_rd)
from ooiservices.app.uframe.config import status_demo_data

import datetime as dt
from random import randint


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Mock status functions.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Mock api.
def mock_get_status_arrays():
    """ Get all arrays with status information.
    Sample request: http://localhost:4000/uframe/status/arrays
    Sample response:
    {
      "arrays": [
        {
          "display_name": "Global Southern Ocean",
          "latitude": -54.0814,
          "longitude": -89.6652,
          "reference_designator": "GS",
          "status": {
            "legend": {
              "degraded": 0,
              "failed": 1,
              "notTracked": 0,
              "operational": 9,
              "removedFromService": 0
            },
            "total": 10
          }
        },
        {
          "display_name": "Global Station Papa",
          "latitude": 49.9795,
          "longitude": -144.254,
          "reference_designator": "GP",
          "status": {
            "legend": {
              "degraded": 0,
              "failed": 0,
              "notTracked": 3,
              "operational": 7,
              "removedFromService": 0
            },
            "total": 10
          }
        },
        . . .
      ]
    }

    """
    arrays_patch = get_array_locations()
    try:
        # Get COL approved array information from vocabulary.
        arrays = {}
        results = []
        array_dict = get_vocabulary_arrays()
        if not array_dict or array_dict is None:
            message = 'Unable to obtain required information for processing.'
            raise Exception(message)

        # Get uframe status for arrays.
        status_arrays = get_status_data(None)
        if not status_arrays or status_arrays is None:
            message = 'Unable to obtain uframe status for arrays.'
            raise Exception(message)

        # Process uframe status for response.
        for k, v in array_dict.iteritems():
            if k not in arrays:
                if k in arrays_patch:
                    arrays[k] = {}
                    arrays[k]['reference_designator'] = k
                    arrays[k]['latitude'] = arrays_patch[k]['latitude']
                    arrays[k]['longitude'] = arrays_patch[k]['longitude']
                    if k in status_arrays:
                        arrays[k]['status'] = status_arrays[k]
                    else:
                        arrays[k]['status'] = None
                    vocab_dict = get_vocab_dict_by_rd(k)
                    if vocab_dict:
                        arrays[k]['display_name'] = vocab_dict['name']
                    else:
                        arrays[k]['display_name'] = k

        if not arrays or arrays is None:
            message = 'Failed to process array information for response.'
            raise Exception(message)

        # Form list of dictionaries for response.
        for k, v in arrays.iteritems():
            if v and v is not None:
                results.append(v)
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def mock_get_sites_for_array(rd):
    """ Get all sites for an array; for each site provide status and some asset-based information.
    Sample request: http://localhost:4000/uframe/status/sites/CE
    """
    from ooiservices.app.uframe.status_tools import get_rd_digests_dict
    debug = True
    time = False
    return_list = []

    if rd is None:
        return None
    if len(rd) == 2:
        pass
    else:
        return None

    try:
        start = dt.datetime.now()
        if time:
            print '\n\t-- Get information for %s site processing... ' % rd
            print '\t-- Start time: ', start

        # Get sensor inventory of sites for array.
        rds = uframe_get_sites_for_array(rd)
        if time: print '\n\t-- Number of %s sites: %d' % (rd, len(rds))
        if not rds:
            message = 'No sites in the sensor inventory for array %s.' % rd
            current_app.logger.info(message)
            return []

        # Get rd_digest dictionary.
        rd_digests_dict = get_rd_digests_dict()

        end = dt.datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to get information for %s site processing: %s' % (rd, str(end - start))

        if not rds:
            return None

        for reference_designator in rds:

            #===================================
            start = dt.datetime.now()
            if time:
                print '\n\t-- Processing %s... ' % reference_designator
                print '\t\t-- Start time: ', start
            #===================================

            if reference_designator not in rd_digests_dict:
                continue

            rd_digests_dict[reference_designator]['status'] = get_status_data(reference_designator)
            rd_digests_dict[reference_designator]['reason'] = None
            return_list.append(rd_digests_dict[reference_designator])

            #===================================
            end = dt.datetime.now()
            if time:
                print '\t\t-- End time:   ', end
                print '\t\t-- Time to process %s site: %s' % (rd, str(end - start))
            #===================================

        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Mock get platform status (was 'get_platforms_for_site')
def mock_get_status_platforms(data, rd=None):
    """ Get assets which contain rd.

    http://localhost:4000/uframe/status/platforms/CE01ISSM (return instruments grouped by node.)
        returns all platforms and associated instruments for CE01ISSM, where a platform
        is an asset containing CE01ISSM and 14 in length. All platforms are grouped by node category.
        (Node categories are available in the vocab_codes dictionary in attribute 'nodes'.)
        By way of an example, for site CE01ISSM, get platforms grouped by node category:
            CE01ISSM-SB[D17]  (Bucket 1)
            CE01ISSM-MF[D35]  (Bucket 2)
            CE01ISSM-MF[D37]
            CE01ISSM-MF[C31]
            CE01ISSM-RI[D16]  (Bucket 3)
    """
    from ooiservices.app.uframe.status_tools import get_site_sections
    debug = False
    if debug: print '\n debug -- Entered get_platforms_for_site: ', rd
    if not rd or rd is None:
        message = 'Please provide a site or platform reference designator for processing.'
        raise Exception(message)

    if not data or data is None:
        message = 'No asset data provided for processing site %s platforms.' % rd
        raise Exception(message)

    return_list = []
    unique = set()
    try:
        # Require site reference designator.
        if len(rd) != 8:
            return []

        # Filter asset data for processing platforms by site reference designator.
        for obj in data:
                if 'ref_des' not in obj or not obj['ref_des'] or obj['ref_des'] is None:
                    continue
                if rd not in obj['ref_des']:
                    continue
                if rd == obj['ref_des']:
                    continue

                # Process object for final collection
                if obj['ref_des'] not in unique:
                    unique.add(str(obj['ref_des']))
                    work = format_site_data(obj)
                    if work is not None:
                        return_list.append(work)

        if debug: print '\n debug -- Get sections...'
        sections = []
        if unique:
            unique_list = list(unique)
            unique_list.sort()
            if debug: print '\n debug -- unique_list(%d): %s ' % (len(unique_list), unique_list)
            if unique_list:
                unique_list.sort()
            sections = get_site_sections(unique_list, return_list)
        return sections
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def mock_get_status_instrument(rd):
    """ Get the status for a single instrument.
    Sample requests:
        http://localhost:4000/uframe/status/instrument/CE01ISSM-MFC31-00-CPMENG000
        http://localhost:4000/uframe/status/instrument/GA01SUMO-RII11-02-CTDBPP031
    """
    from ooiservices.app.uframe.status_tools import get_rd_digests_dict, get_stream_times
    return_list = []
    try:
        #============================================================
        # Verify the rd provided is for an instrument.
        if not rd or rd is None or len(rd) <= 14:
            #if len(rd) <= 14 or not is_instrument(rd):
            message = 'Provide a valid reference designator for an instrument.'
            raise Exception(message)

        # Get rd_digest dictionary.
        rd_digests_dict = get_rd_digests_dict()
        if rd in rd_digests_dict:
            rd_digests_dict[rd]['status'] = get_status_data(rd)
            rd_digests_dict[rd]['reason'] = None

            # Stream times from time_dict
            time_dict = get_stream_times([rd])
            if not time_dict or time_dict is None:
                rd_digests_dict[rd]['start'] = None
                rd_digests_dict[rd]['end'] = None
            elif rd not in time_dict:
                rd_digests_dict[rd]['start'] = None
                rd_digests_dict[rd]['end'] = None
            else:
                rd_digests_dict[rd]['start'] = time_dict[rd]['start']
                rd_digests_dict[rd]['end'] = time_dict[rd]['end']
            return_list.append(rd_digests_dict[rd])

        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# End mock status functions.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Mock status helper functions.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_status_data(rd):
    """ Get mock status for array, site, platform or instrument.
    """
    debug = False
    try:
        status = get_mock_status_for_rd(rd)
        if debug: print '\n debug -- status for rd \'%s\': %s' % (rd, status)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Mock api.
def format_site_data(obj):
    """
    Format asset data for mock api, returns status and reason as part of return object.
    """
    debug = False
    try:
        if debug: print '\n debug -- format_site_data... '
        work = {}
        latitude = None
        longitude = None
        depth = None
        mindepth = None
        maxdepth = None
        name = None
        uid = None

        reference_designator = obj['ref_des'][:]

        if 'latitude' in obj:
            latitude = obj['latitude']
            if latitude is not None:
                latitude = round(latitude, 4)
        if 'longitude' in obj:
            longitude = obj['longitude']
            if longitude is not None:
                longitude = round(longitude, 4)
        if 'depth' in obj:
            depth = obj['depth']
        if 'uid' in obj:
            uid = obj['uid']

        work['uid'] = uid
        work['reference_designator'] = reference_designator
        work['latitude'] = latitude
        work['longitude'] = longitude
        work['depth'] = depth
        if 'assetInfo' in obj:
            mindepth = 0
            if 'mindepth' in obj['assetInfo']:
                mindepth = obj['assetInfo']['mindepth']
            maxdepth = 0
            if 'maxdepth' in obj['assetInfo']:
                maxdepth = obj['assetInfo']['maxdepth']
            if 'name' in obj['assetInfo']:
                name = obj['assetInfo']['name']
            else:
                name = get_display_name_by_rd(reference_designator)
        work['display_name'] = name
        work['mindepth'] = mindepth
        work['maxdepth'] = maxdepth
        #================
        if not work:
            work = None
        else:
            if debug: print '\n Get status for %s...', reference_designator
            work['status'] = get_status_data(reference_designator)
            work['reason'] = None
            if debug: print '\n debug -- work[status]: ', work['status']
        return work

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# End mock status helper functions.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_mock_status_for_rd(rd):
    """ Get uframe status for reference designator, process result and return.
    """
    debug = False
    demo_data = status_demo_data()
    result = None
    try:
        # Get status data.
        if not demo_data:
            message = 'Should never be here if using actual uframe interface! (Check configuration settings.)'
            #raise Exception(message)
            current_app.logger.info(message)

            results = uframe_get_status_by_rd(rd)
            if results is not None:
                # Get array status
                if rd is None:
                    if debug: print '\n debug -- Process status arrays...', rd
                    if results is not None:
                        result = None
                    else:
                        result = process_status_arrays(results)
                    if debug: print '\n debug -- result: ', result

                # Get sites status for an array; includes all sites for an array.
                elif len(rd) == 2:
                    if debug: print '\n debug -- Process status sites...', rd
                    if results is not None:
                        result = None
                    else:
                        result = process_status_sites(results)
                    if debug: print '\n debug -- result: ', result
                # Get platform status for a site; includes instruments per platform.
                elif len(rd) == 8:
                    if debug: print '\n debug -- Process status platforms...' , rd
                    if results is not None:
                        result = None
                    else:
                        result = process_status_platforms(results)
                    if debug: print '\n debug -- result: ', result

                # Get instrument status.
                elif len(rd) > 14:
                    if debug:
                        print '\n debug -- Process status instrument...' , rd
                        print '\n debug -- results: ', results
                    if results is not None:
                        result = None
                    else:
                        result = process_status_instrument(results)
                    if debug: print '\n debug -- result: ', result
                else:
                    message = 'Processing uframe status failed for reference designator \'%s\'.' % rd
                    raise Exception(message)

        else:
            # Get array status
            if rd is None:
                result = get_mock_array_data()
            # Get sites status for an array; includes all sites for an array.
            elif len(rd) == 2:
                result = get_mock_site_data(rd)
            # Get platform status for a site; includes instruments per platform.
            elif len(rd) == 8:
                result = get_mock_platform_data(rd)
            # Get instrument status.
            elif len(rd) > 14:
                result = get_mock_instrument_data(rd)
            else:
                # Malformed or unknown reference designator.
                message = 'Unknown or malformed reference designator: %s' % rd
                if debug: current_app.logger.info(message)
                result = None

        # No result returned from uframe.
        if not result or result is None:
            result = None

        if debug: print '\n *** Return %s status result: %s' % (rd, result)
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


def process_status_arrays(results):
    """
    """
    try:
        # Build status response
        status = build_status_response(results)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception


def process_status_sites(results):
    """ For an array, process return status for sites.
    """
    try:
        # Build status response
        status = get_status_response(results)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception


def process_status_platforms(results):
    """ For a platform rd, process return status.
    """
    try:
        # Build status response
        status = get_status_response(results)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception

def process_status_instrument(results):
    """ For an instrument, process return status.
    """
    try:
        # Build status response
        status = get_status_response(results)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_mock_array_data():
    debug = False
    try:
        if debug: print '\n debug -- Entered get_mock_array_data...'
        # Mock data from uframe
        result = \
        [
            {
                "rd": "CE",
                "status": {
                    "legend": {
                          "degraded": 3,
                          "failed": 0,
                          "notTracked": 0,
                          "operational": 7,
                          "removedFromService": 0
                        },
                        "count": 10
                    }
            },
            {
                "rd": "GP",
                "status": {
                    "legend": {
                      "degraded": 0,
                      "failed": 0,
                      "notTracked": 3,
                      "operational": 7,
                      "removedFromService": 0
                    },
                    "count": 10
                }
            },
            {
                "rd": "CP",
                "status": {
                    "legend": {
                      "degraded": 0,
                      "failed": 0,
                      "notTracked": 1,
                      "operational": 9,
                      "removedFromService": 0
                    },
                    "count": 10
                }
           },
           {
              "rd": "GA",
              "status": {
                "legend": {
                  "degraded": 2,
                  "failed": 2,
                  "notTracked": 2,
                  "operational": 4,
                  "removedFromService": 0
                },
                "count": 10
             }
           },
           {
              "rd": "GI",
              "status": {
                "legend": {
                  "degraded": 4,
                  "failed": 4,
                  "notTracked": 2,
                  "operational": 0,
                  "removedFromService": 0
                },
                "count": 10
             }
           },
           {
              "rd": "GS",
              "status": {
                "legend": {
                  "degraded": 0,
                  "failed": 1,
                  "notTracked": 0,
                  "operational": 9,
                  "removedFromService": 0
                },
                "count": 10
             }
           },
           {
              "rd": "RS",
              "status": {
                "legend": {
                  "degraded": 0,
                  "failed": 0,
                  "notTracked": 0,
                  "operational": 10,
                  "removedFromService": 0
                },
                "count": 10
             }
           }
        ]
        # Build status response
        status = build_status_response(result)
        return status
    except Exception as err:
        message = str(err)
        raise Exception(message)


def build_status_response(uframe_status_data):
    """ Using uframe list of dictionaries and create dictionary of status with rd as key.
    """
    try:
        status = {}
        for item in uframe_status_data:
            if 'rd' in item and 'status' in item:
                status[item['rd']] = item['status']
        return status
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Deprecate - mock data.
def get_status_response(uframe_status_data):
    """ Using uframe list of dictionaries and create dictionary of status with rd as key.
    """
    try:
        status = None
        for item in uframe_status_data:
            if 'rd' in item and 'status' in item:
                status= item['status']
        return status
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Deprecate - mock data.
def get_mock_site_data(rd):
    debug = False
    try:
        if debug: print '\n debug -- Entered get_mock_site_data: %s' % rd
        # The rd is for a site.
        status = get_status_value()
        return status
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Deprecate - mock data.
def get_mock_platform_data(rd):
    debug = False
    try:
        if debug: print '\n debug -- Entered get_mock_platform_data: %s' % rd
        status = get_status_value()
        return status
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Deprecate - mock data.
def get_mock_instrument_data(rd):
    debug = False
    try:
        if debug: print '\n debug -- Entered get_mock_platform_data: %s' % rd
        status = get_status_value()
        return status
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Deprecate - mock data.
def get_status_value():
    values = None
    default = None
    try:
        values = operational_status_values()
        default = values[0]
        maxint = len(values) - 1
        index = randint(0,maxint)
        value = values[index]
        return value
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return default


# Deprecate - mock data.
def get_status_block():
    """ Generate some status counts for status block, to be used for pie chart.
    Replace this with uframe status block information.
    """
    count_operational = randint(60,100)
    max_degraded = 100 - count_operational
    count_degraded = randint(0, max_degraded)
    count_not_tracked = 100 - count_operational - count_degraded
    count_removed = 0
    status = {
        'legend':
        {
         'operational': count_operational,
         'degraded': count_degraded,
         'failed': 0,
         'notTracked': count_not_tracked,
         'removedFromService': count_removed
        }
    }
    return status

