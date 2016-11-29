#!/usr/bin/env python

"""
Asset Management - Status: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.asset_tools import verify_cache
from ooiservices.app.uframe.stream_tools import get_stream_list
from ooiservices.app.uframe.vocab import (get_vocab_dict_by_rd, get_vocab_codes, get_vocabulary_arrays,
                                          get_display_name_by_rd)
from ooiservices.app.uframe.uframe_tools import get_mock_status_for_rd, uframe_get_status_by_rd
from ooiservices.app.uframe.common_tools import (operational_status_values, is_array, is_instrument, is_mooring)


# development work=============================
from ooiservices.app.uframe.common_tools import get_array_locations
from ooiservices.app.uframe.asset_cache_tools import get_asset_rds_cache, get_assets_dict
from ooiservices.app.uframe.toc_tools import get_asset_ids_for_deployments
from ooiservices.app.uframe.uframe_tools import (get_rd_deployments, get_deployments_digest_by_uid,
                                                 uframe_get_sites_for_array)
from ooiservices.app.uframe.common_tools import dump_dict           # todo remove
# development work=============================

import datetime as dt
from ooiservices.app import cache
CACHE_TIMEOUT = 172800

# from ooiservices.app.uframe.uframe_tools import (get_deployments_digest_by_uid,
# from operator import itemgetter


def get_asset_list():
    results = []
    try:
        data = verify_cache()
        if not data or data is None:
            return results
        else:
            results = data
        return results
    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_status_arrays():
    """ Get status for all arrays.
    """
    results = []
    try:
        result = get_status_arrays()
        if result is not None:
            results = result
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _get_status_sites(rd):
    """ For a specific array, get all sites with status.
    Sample request: http://localhost:4000/uframe/status/sites/CE
    """
    time = True
    return_list = []
    try:
        # Verify rd is a valid reference designator for an array.
        if not rd or rd is None:
            message = 'Provide an array code.'
            raise Exception(message)
        if len(rd) != 2 or not is_array(rd):
            message = 'Provide a valid array code.'
            raise Exception(message)
        """
        array_dict = get_vocabulary_arrays()
        if rd not in array_dict:
            message = 'Unknown array code (\'%s\') provided.' % rd
            raise Exception(message)
        """

        # Process assets for result.
        start = dt.datetime.now()
        if time:
            print '\n-- Process %s site(s) status. ' % rd
            print '-- Start time: ', start

        # Call function to bridge mock interface and real interface (for now).
        results = bridge_get_sites_for_array(rd)

        # Real interface (use bridge for now.)
        #results = get_status_sites(rd)
        end = dt.datetime.now()
        if time:
            print '-- End time:   ', end
            print '-- Time to process %s site(s) status: %s\n' % (rd, str(end - start))
        if results is None:
            results = []
        if not results:
            return results

        if results is None:
            results = return_list
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def _get_status_platforms(rd):
    """ Get status for all platforms associated with a specific site.
    """
    results = []
    try:
        if not rd or rd is None:
            message = 'Provide an array code.'
            raise Exception(message)
        if len(rd) != 8:
            message = 'Provide a valid site code.'
            raise Exception(message)
        if not is_mooring(rd):
            message = 'The reference designator (\'%s\') is an invalid site.'
            raise Exception(message)
        array_dict = get_vocabulary_arrays()
        if rd[:2] not in array_dict:
            message = 'Unknown array code (\'%s\') provided, unable to process request.' % rd
            raise Exception(message)
        result = get_status_platforms(rd)
        if result is not None:
            results = result
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _get_status_instrument(rd):
    """ Get instrument status.
    """
    results = []
    try:
        # Check if rd is empty, None or an invalid format; if so, raise exception
        if not rd or rd is None:
            message = 'Provide an array code.'
            raise Exception(message)
        if len(rd) <=14 or len(rd) > 27:
            message = 'Provide a valid instrument code.'
            raise Exception(message)

        # Verify array code is for a supported/known array; if not, raise exception.
        array_dict = get_vocabulary_arrays()
        if rd[:2] not in array_dict:
            message = 'Unknown array code (\'%s\') provided.' % rd
            raise Exception(message)
        result = get_status_instrument(rd)
        if result is not None:
            results = result
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_status_arrays():
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


def get_status_platforms(rd):
    """ Get all platforms for a specific site.
    Sample requests:
        http://localhost:4000/uframe/assets/nav/platforms/CE01ISSM
    """
    time = True
    return_list = []
    try:
        start = dt.datetime.now()
        if time:
            print '\n-- Get platform status for site %s.' % rd
            print '\t-- Start time: ', start
        if len(rd) != 8:
            message = 'Provide a valid reference designator for a site, (e.g. CE01ISSM).'
            raise Exception(message)

        # Get assets. If assets weren't cached this would be a problem (uframe response expensive time wise).
        data = get_asset_list()
        if not data or data is None:
            return return_list

        # Get platforms for rd from assets data.
        results = get_platforms_for_site(data, rd)
        end = dt.datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to get platform status for site %s.: %s\n' % (rd, str(end - start))
        if results and results is not None:
            return results
        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_status_instrument(rd):
    """ Get the status for a single instrument.
    Sample requests:
        http://localhost:4000/uframe/status/instrument/CE01ISSM-MFC31-00-CPMENG000
        http://localhost:4000/uframe/status/instrument/GA01SUMO-RII11-02-CTDBPP031
    """
    return_list = []
    try:
        # Verify the rd provided is for an instrument.
        if len(rd) <= 14 or not is_instrument(rd):
            message = 'Provide a valid reference designator for an instrument, (e.g. CE01ISSM-MFC31-00-CPMENG000).'
            raise Exception(message)

        # Get assets for processing
        data = get_asset_list()
        if not data or data is None:
            return return_list
        results = None
        for item in data:
            if item['ref_des'] == rd:
                work = format_site_data(item)
                if not work or work is None:
                    return return_list
                result = add_deployment_info(work)
                results = [result]
                break
        if results is None:
            return results

        # Stream times from time_dict
        time_dict = get_stream_times([rd])
        for item in results:
            if not time_dict or time_dict is None:
                item['start'] = None
                item['end'] = None
                item['display_name'] = rd
            elif item['reference_designator'] not in time_dict:
                item['start'] = None
                item['end'] = None
                item['display_name'] = rd
            else:
                item['start'] = time_dict[item['reference_designator']]['start']
                item['end'] = time_dict[item['reference_designator']]['end']
                item['display_name'] = time_dict[item['reference_designator']]['name']

        if results and results is not None:
            return_list = results
        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


#def assets_nav_sites(data, rd=None):
def get_platforms_for_site(data, rd=None):
    """ Get assets which contain rd.

    http://localhost:4000/uframe/assets/nav/platforms/CE01ISSM (return instruments grouped by node.)
        returns all platforms and associated instruments for CE01ISSM, where a platform
        is an asset containing CE01ISSM and 14 in length. All platforms are grouped by node category.
        (Node categories are available in the vocab_codes dictionary in attribute 'nodes'.)
        By way of an example, for site CE01ISSM, get platforms grouped by node category:
            CE01ISSM-SB[D17]  (Bucket 1)
            CE01ISSM-MF[D35]  (Bucket 2)
            CE01ISSM-MF[D37]
            CE01ISSM-MF[C31]
            CE01ISSM-RI[D16]  (Bucket 3)

    http://localhost:4000/uframe/assets/nav/sites/CE01ISSM-SBD17  (just instrument(s) for this platform)
    """
    debug = False
    status = 'value'
    if not rd or rd is None:
        message = 'Please provide a site or platform reference designator for processing.'
        raise Exception(message)

    return_list = []
    unique = set()
    try:
        # Filter asset data for processing platforms by site reference designator.
        for obj in data:
                tmp = None

                if len(rd) != 8:
                    continue
                if obj['assetType'] == 'Array' or obj['assetType'] == 'notSpecified':
                    continue
                #if len(rd) == 8: # or len(rd) == 14:
                if 'ref_des' not in obj or not obj['ref_des'] or obj['ref_des'] is None:
                    continue

                #if len(rd) == 8:
                if len(obj['ref_des']) > 8:
                    tmp = obj

                if tmp is None:
                    continue
                if rd[0:2] != obj['ref_des'][0:2]:
                    continue
                if rd not in obj['ref_des']:
                    continue
                if rd == obj['ref_des']:
                    continue
                if 'latitude' in obj and 'longitude' in obj and 'depth' in obj:
                    pass
                else:
                    continue

                # Process object for final collection
                if obj['ref_des'] not in unique:
                    unique.add(str(obj['ref_des']))
                    work = format_site_data(obj)
                    if work is not None:
                        return_list.append(work)
        sections = []
        if unique:
            unique_list = list(unique)
            if unique_list:
                unique_list.sort()
            sections = get_site_sections(unique_list, return_list)
        return sections
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Create list of section to display on Platforms page navigation.
def get_site_sections(unique_list, return_list):
    """ Using unique list of rds and list of assets generate site sections and return list.
        List of sections where a section dictionary has two elements:
            1. header - a dictionary for header row,
            2. list of items in the section (instruments).
        [
         {
            header: {},
            items: [{}]
         },
        ]

        A sample section:
        {
        "header": {
                    "code": "MF",
                    "status": "Degraded",
                    "title": "Multi-Function Node"
                  },
        "items": [
                {
                  "depth": 0.0,
                  "display_name": "Platform Controller",
                  "end": "2015-10-08T00:42:54.333Z",
                  "latitude": 44.6584,
                  "log": [],
                  "longitude": -124.09538,
                  "maxdepth": 25.0,
                  "mindepth": 25.0,
                  "reference_designator": "CE01ISSM-MFC31-00-CPMENG000",
                  "sensorInventory": true,
                  "start": "2014-05-10T19:10:51.794Z",
                  "status": "Degraded",
                  "uid": "OL000193",
                  "waterDepth": null
                },
                . . .
            ]
        }
        """
    #section_list = []
    #sections = []
    try:
        # Verify there is something to process.
        if not unique_list or unique_list is None:
            message = 'Unable to process null or empty unique list to get site sections.'
            raise Exceptions(message)

        # Get vocabulary codes to use when processing sections.
        vocab_codes = get_vocab_codes()
        if vocab_codes is None:
            message = 'Unable to process sites without vocabulary information (codes).'
            raise Exception(message)

        # Get rd_root.
        rd_root = unique_list[0][:9]
        # Get unique platforms (14).
        unique_platforms = []
        for rd in unique_list:
            if rd[:14] not in unique_platforms:
                unique_platforms.append(rd[:14])

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get section codes.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        section_codes = []
        for item in unique_platforms:
            item = item.replace(rd_root, '')
            if item[:2] not in section_codes:
                section_codes.append(item[:2])
        if not section_codes:
            message = 'No section codes found for %s.' % rd_root[:8]
            return []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get lists of instruments and uids.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        instruments = []
        uids = {}
        for item in return_list:
            if len(item['reference_designator']) > 14:

                    if item['reference_designator'] and item['reference_designator'] is not None and \
                       item['uid'] and item['uid'] is not None:
                            rd = item['reference_designator'][:]
                            uid = item['uid'][:]
                            if rd not in instruments:
                                instruments.append(rd)
                            if uid not in uids:
                                uids[uid] = rd

        if not instruments or not uids:
            return None

        # Get dict of start and end times
        time_dict = get_stream_times(instruments)

        # Get deployment digests for each reference designator.
        digest_dict = get_digest_dict(uids)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create section header(s)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        sections = []
        headers = []
        for code in section_codes:
            header = {}
            header['code'] = code
            if code in vocab_codes['nodes']:
                header['title'] = vocab_codes['nodes'][code]
            header['status'] = operational_status_values()[1]   # todo - use uframe status
            headers.append(header)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Populate each section 'items' with a list of instruments.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for header in headers:
            section = {}
            section['header'] = header
            section_code = header['code']
            prefix = rd_root + section_code
            cart = []
            for item in return_list:
                if item['reference_designator'] not in instruments:
                    continue
                if prefix == item['reference_designator'][:11]:
                    # Add start and end times for reference designator.
                    if not time_dict or time_dict is None:
                        item['start'] = None
                        item['end'] = None
                        #item['display_name'] = item['reference_designator']
                    elif item['reference_designator'] not in time_dict:
                        item['start'] = None
                        item['end'] = None
                        #item['display_name'] = item['reference_designator']
                    else:
                        item['start'] = time_dict[item['reference_designator']]['start']
                        item['end'] = time_dict[item['reference_designator']]['end']
                        #item['display_name'] = time_dict[item['reference_designator']]['name']

                    # Add deployment information, if available, for reference designator.
                    # No deployment digest information.
                    if not digest_dict or digest_dict is None:
                        item['latitude'] = None
                        item['longitude'] = None
                        item['waterDepth'] = None
                        item['depth'] = None
                        item['waterDepth'] = None
                    # Get digest for reference designator from digest dictionary, process.
                    elif item['reference_designator'] in digest_dict:
                        digest = digest_dict[item['reference_designator']]
                        item['latitude'] = digest['latitude']
                        item['longitude'] = digest['longitude']
                        item['waterDepth'] = digest['waterDepth']
                        item['depth'] = digest['depth']
                        item['waterDepth'] = None
                    # The reference designator is not in the digest dictionary.
                    else:
                        item['waterDepth'] = None
                    cart.append(item)
            section['items'] = cart
            sections.append(section)
        return sections
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_stream_times(instruments):
    """ For a list of instruments, create and return dict (rd is key) with name, start and end times for rd.
    The name provided is name in the vocabulary for the sensor in the reference designator.
    The stat, end and name are garnered from stream information (produced by stream list processing.
    """
    debug = False
    stream_times = None
    try:
        if not instruments or instruments is None:
            return stream_times
        # Get stream list once and populate all startTIme and endTime values.
        stream_list = get_stream_list()
        if not stream_list or stream_list is None:
            message = 'Problem: stream_list returned null or empty.'
            raise Exception(message)

        stream_times = {}
        count = 0
        len_instruments = len(instruments)
        if debug: print '\n debug -- get_stream_times: len(instruments): ', len(instruments)
        for stream in stream_list:
            if stream['reference_designator'] in instruments:
                if stream['reference_designator'] not in stream_times:
                    count += 1
                    stream_times[stream['reference_designator']] = {}
                    stream_times[stream['reference_designator']]['start'] = stream['start']
                    stream_times[stream['reference_designator']]['end'] = stream['end']
                    stream_times[stream['reference_designator']]['name'] = stream['display_name']
            if count >= len_instruments:
                break
        if not stream_times:
            return None
        if debug:
            print '\n debug -- len(stream_times.keys(): ', len(stream_times.keys())
            if len(stream_times.keys()) != len(instruments):
                instruments_missing_times = []
                for instrument in instruments:
                    if instrument not in stream_times:
                        instruments_missing_times.append(instrument)
                if instruments_missing_times:
                    print '\n The following instruments were not available in stream_list: ', instruments_missing_times

        return stream_times
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_digest_dict(uids):
    try:
        if not uids or uids is None:
            return None
        digest_dict = {}
        for uid, rd in uids.iteritems():
            digest = get_last_deployment_digest(uid)
            if digest and digest is not None:
                digest_dict[rd] = digest
        if not digest_dict:
            digest_dict = None
        return digest_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def format_site_data(obj):
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
            if debug: print '\n debug -- work[status]: ', work['status']
        return work

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def format_rd_digest(obj):
    """
    Combine asset and digest information
    #current_digest for asset uid:
        # {u'node': u'WFP01', u'eventId': 32596, u'endTime': 1464566400000,
        # u'orbitRadius': 0.0, u'subsite': u'CP02PMCI', u'node_uid': None,
        # u'waterDepth': None, u'deploymentNumber': 5, u'longitude': -70.88897,
        # u'editPhase': u'OPERATIONAL', u'depth': 0.0, u'recoverCruiseIdentifier': None,
        # u'startTime': 1463789880000, u'latitude': 40.22655, u'mooring_uid': u'OL000237',
        # u'versionNumber': 1, u'deployCruiseIdentifier': u'AR-04', u'sensor': u'00-WFPENG000',
        # u'sensor_uid': u'A00286.1'}
    """
    debug = False
    try:
        if debug: print '\n debug -- Entered format_rd_digest...'
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

        return work

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_status_data(rd):
    """ Get status for array, site, platform or instrument.
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


def get_uframe_status_data(rd):
    """ Get uframe status for array, site, platform or instrument. Process into dictionary.
    """
    debug = False
    try:
        status_data = uframe_get_status_by_rd(rd)
        if debug:
            print '\n debug -- uframe status data for rd \'%s\': ', rd
            dump_dict(status_data, debug)

        if not status_data or status_data is None:
            status = None
        else:
            status = {}
            for item in status_data:
                if item:
                    if 'referenceDesignator' in item:
                        if item['referenceDesignator']:
                            status[item['referenceDesignator']] = item
            if not status:
                status = None
        if debug:
            print '\n debug -- uframe status for rd \'%s\':' % rd
            dump_dict(status)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_log_block():
    """ Get event log for history, default count=100.
    """
    log = []
    return log


def get_last_deployment_digest(uid):
    digest = None
    try:
        digests = get_deployments_digests(uid)
        if digests and digests is not None:
            #digests.reverse()
            digest = digests[0]
        return digest
    except Exception as err:
        message = 'get_last_deployment_digest: uid: %s: %s' % (uid, str(err))
        current_app.logger.info(message)
        return None

# development work
def get_deployments_digests(uid):
    """ Get list of deployment digest items for a uid; sorted in reverse by deploymentNumber.

    Sample response data:
        [
            {
              "startTime" : 1437159840000,
              "depth" : 0.0,
              "subsite" : "CE01ISSP",
              "node" : "SP001",
              "sensor" : "00-SPPENG000",
              "deploymentNumber" : 3,
              "versionNumber" : 1,
              "eventId" : 23362,
              "editPhase" : "OPERATIONAL",
              "longitude" : -124.09567,
              "latitude" : 44.66415,
              "orbitRadius" : 0.0,
              "mooring_uid" : "N00262",
              "node_uid" : "N00123",
              "sensor_uid" : "R00102",
              "deployCruiseIdentifier" : null,
              "recoverCruiseIdentifier" : null,
              "waterDepth" : null,
              "endTime" : 1439424000000
            },
            . . .
        ]
    """
    debug = False
    try:
        if debug: print '\n debug -- Entered get_deployments_digests for uid: %s' % uid
        digests = get_deployments_digest_by_uid(uid)
        if not digests or digests is None or len(digests) == 0:
            return None
        if debug: print '\n len(digests): ', len(digests)
        # Sort (reverse) by value of 'deploymentNumber', 'versionNumber', 'startTime'
        #result = None
        try:
            #result = sorted(digests, key=itemgetter('deploymentNumber'))
            #digests.sort(key=lambda x: (-x['deploymentNumber'], -x['versionNumber'], -x['startTime']))
            digests.sort(key=lambda x: (x['deploymentNumber'], x['versionNumber'], x['startTime']), reverse=True)
        except Exception as err:
            print '\n get_deployments_digests : errors: ', str(err)
            pass
        if not digests or digests is None:
            return None
        if debug: print '\n debug -- Exit get_deployments_digests for uid: %s' % uid
        return digests
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def bridge_get_sites_for_array(rd):
    from ooiservices.app.uframe.config import status_demo_data          # mock api
    try:
        # Real interface...
        if not status_demo_data():
            return_list = get_status_sites(rd)  # final_new_get_sites_for_array(rd)

        # Mock data interface
        else:
            return_list = mock_get_sites_for_array(rd)

        return return_list
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_status_sites(rd):
    """ Get all sites for an array; for each site provide status and some asset-based information.
    Sample request: http://localhost:4000/uframe/status/sites/CE
    """
    debug = False
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

        # Get status data dictionary.
        status_data = get_uframe_status_data(rd)       # uframe data
        if not status_data or status_data is None:
            message = 'No status data returned from uframe for reference designator %s.' % rd
            current_app.logger.info(message)
            status_data = {}

        if debug:
            print '\n debug ------ status_data: '
            dump_dict(status_data, debug)

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

            # Add status for reference designator.
            if status_data and (reference_designator in status_data):
                #rd_digests[reference_designator]['status'] = get_status_data(reference_designator)
                rd_digests_dict[reference_designator]['status'] = status_data[reference_designator]['status']
                rd_digests_dict[reference_designator]['reason'] = status_data[reference_designator]['reason']
            else:
                if debug: print '\n debug -- %s status not supplied in status_data.' % reference_designator
                rd_digests_dict[reference_designator]['status'] = None
                rd_digests_dict[reference_designator]['reason'] = None
            return_list.append(rd_digests_dict[reference_designator])

            #=======================================
            end = dt.datetime.now()
            if time:
                print '\t\t-- End time:   ', end
                print '\t\t-- Time to process %s site: %s' % (rd, str(end - start))
            #===================================
            #break

        # For each

        if debug: print '\n len(return_list): %d' % len(return_list)
        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# todo: Remove this mock interface when status/query endpoint available.
def mock_get_sites_for_array(rd):
    """ Get all sites for an array; for each site provide status and some asset-based information.
    Sample request: http://localhost:4000/uframe/status/sites/CE
    """

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
        #==================================
        start = dt.datetime.now()
        if time:
            print '\n\t-- Get information for %s site processing... ' % rd
            print '\t-- Start time: ', start
        #==================================

        # Get sensor inventory of sites for array.
        rds = uframe_get_sites_for_array(rd)
        if time: print '\n\t-- Number of %s sites: %d' % (rd, len(rds))
        if not rds:
            message = 'No sites in the sensor inventory for array %s.' % rd
            current_app.logger.info(message)
            return []

        # Get rd_digest dictionary.
        rd_digests_dict = get_rd_digests_dict()

        #==================================
        end = dt.datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to get information for %s site processing: %s' % (rd, str(end - start))
        #==================================

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

            #=======================================
            end = dt.datetime.now()
            if time:
                print '\t\t-- End time:   ', end
                print '\t\t-- Time to process %s site: %s' % (rd, str(end - start))
            #===================================

        # For each

        if debug: print '\n len(return_list): %d' % len(return_list)
        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


#============================================== start development work
def get_ids_for_rd(rd):
    """ Get list of asset ids for reference designator.
    """
    try:
        # If rd is not subsite, platform or instrument, return empty list.
        results = get_rd_deployments(rd)
        if results is None:
            return []

        # Get asset ids broken out by type.
        sensor_ids, mooring, mooring_ids, node_name, node_ids = get_asset_ids_for_deployments(rd, results)

        # get the appropriate asset ids for reference designator.
        len_rd = len(rd)
        if len_rd == 8:
            ids = mooring_ids
        elif len_rd == 14:
            ids = node_ids
        elif len_rd > 14 and len_rd <= 27:
            ids = sensor_ids
        else:
            ids = []
        return ids
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []

def get_list_of_assets(ids):
    from ooiservices.app.uframe.asset_tools import _get_asset
    assets = []
    try:
        for id in ids:
            # Get UI assets list.
            try:
                asset = _get_asset(id)
            except:
                continue
            if asset and asset is not None:
                assets.append(asset)
        return assets
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []


def get_assets_for_rd(rd):
    try:
        ids = get_ids_for_rd(rd)
        assets = get_list_of_assets(ids)
        return assets
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return []
#============================end development work


def add_deployment_info(work):
    """ Process work dictionary and add deployment items.
    """
    try:
        if not work or work is None:
            return None

        # Get deployment digest using uid from work dictionary.
        digest = get_last_deployment_digest(work['uid'])
        if digest is not None:
            work['latitude'] = digest['latitude']
            work['longitude'] = digest['longitude']
            work['depth'] = digest['depth']
            work['waterDepth'] = digest['waterDepth']
        else:
            work['latitude'] = None
            work['longitude'] = None
            work['depth'] = None
            work['waterDepth'] = None
        return work
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


#===========================================
def build_rds_cache():
    """
    Create a cache for reference designator to current asset uid deployment information.
    Used by status methods.
    """
    debug = True
    time = True
    from ooiservices.app.uframe.toc_tools import get_toc_reference_designators
    try:
        if debug: print '\n debug -- Compiling reference designator to asset uid cache.'
        rds, _, _ = get_toc_reference_designators()
        if not rds or rds is None:
            message = 'No reference designators returned from toc information.'
            raise Exception(message)

        start = dt.datetime.now()
        if time:
            print '\n-- Compiling latest asset uid for reference designators... '
            print '\t-- Start time: ', start
        rd_digests, rd_digests_dict = build_rd_digest_cache(rds)
        cache.set('rd_digests', rd_digests, timeout=CACHE_TIMEOUT)
        cache.set('rd_digests_dict', rd_digests_dict, timeout=CACHE_TIMEOUT)

        if debug: print '\n debug -- Reference designators (%d) has (%d) rd_digests' % (len(rds), len(rd_digests))
        end = dt.datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to complete: %s' % (str(end - start))
        # Set cache.
        return rd_digests
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def build_rd_digest_cache(rds):
    """
    Create a cache for reference designator to current asset uid deployment information.
    """
    debug = True
    time = True

    return_list = []
    return_dict = {}
    uid = None
    digest = None
    try:

        start = dt.datetime.now()
        if time:
            print '\n-- Preparing information before processing... '
            print '\t-- Start time: ', start

        #=======================================
        # Get asset_rds
        asset_rds = get_asset_rds_cache()
        if asset_rds is None:
            message = 'Failed to retrieve asset_rds.'
            raise Exception(message)

        # Get assets_dict
        assets_dict = get_assets_dict()
        if assets_dict is None:
            message = 'Failed to retrieve assets_dict.'
            raise Exception(message)

        #=======================================
        end = dt.datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time started: %s' % (str(end - start))

        if not rds:
            message = 'No reference designator to process, unable to build rd_digest cache.'
            raise Exception(message)

        #count = 0
        # Process each reference designator and add to rd_digests.
        for reference_designator in rds:

            #if debug: print '\n debug -- Entered get_last_deployment_for_rd: ', rd
            if debug: print '\n debug -- Processing reference designator: ', reference_designator
            start = dt.datetime.now()
            if time:
                print '\t-- Start time: ', start

            ids = []
            uids = []
            uid_dict = {}
            assets = []
            len_rd = len(reference_designator)

            # For each reference designator, get list of asset ids.
            for id in asset_rds:
                #if asset_rds[id] == reference_designator:           # single reference designator (old style)
                if reference_designator in asset_rds[id]:
                    #if debug: print '\n asset id(%d): %s' % (id, asset_rds[id])
                    if id not in ids:
                        ids.append(id)
                        if id in assets_dict:
                            if not assets_dict[id] or assets_dict[id] is None:
                                continue
                            assets.append(assets_dict[id])
                            if not assets_dict[id]['uid'] or assets_dict[id]['uid'] is None or \
                                len(assets_dict[id]['uid']) == 0:
                                continue
                            uids.append(assets_dict[id]['uid'])
                            uid_dict[assets_dict[id]['uid']] = assets_dict[id]
            if not ids:
                continue
            if not uids:
                continue
            if not uid_dict:
                continue

            # Now have list of asset uids; determine current deployment.
            digests = []
            for uid in uids:

                digest = get_last_deployment_digest(uid)
                if digest is None or not digest:
                    continue
                digests.append(digest)

            if not digests or digests is None or len(digests) == 0:
                #if debug: print '\n note -- digests is none, continue...'
                continue

            # Have digests, sort. (work on failure during sort alternatives)
            try:
                digests.sort(key=lambda x: (x['deploymentNumber'], x['versionNumber'], x['startTime']), reverse=True)
            except Exception as err:
                print '\n build_rd_digest_cache: errors: ', str(err)
                pass

            # Get digest.
            work = None
            if digests and digests is not None and len(digests) > 0:
                current_digest = digests[0]
            else:
                current_digest = None

            if current_digest is not None:
                len_rd = len(reference_designator)
                work = None
                if len_rd == 8:
                    if current_digest['mooring_uid'] is not None:
                        work = format_rd_digest(uid_dict[current_digest['mooring_uid']])
                elif len_rd == 14:
                    if current_digest['node_uid'] is not None:
                        work = format_rd_digest(uid_dict[current_digest['node_uid']])
                elif len_rd > 14 and len_rd <=27:
                    if current_digest['sensor_uid'] is not None:
                        work = format_rd_digest(uid_dict[current_digest['sensor_uid']])
                else:
                    message = 'Reference designator (\'%s\') is of unknown format.' % reference_designator
                    current_app.logger.info(message)
                    #raise Exception(message)
                    continue

            # Add deployment data.
            if work is not None:
                #item = add_deployment_info(work)
                #if current_digest is not None:
                work['latitude'] = current_digest['latitude']
                work['longitude'] = current_digest['longitude']
                work['depth'] = current_digest['depth']
                work['waterDepth'] = current_digest['waterDepth']

            if work is not None:
                return_list.append(work)
                return_dict[work['reference_designator']] = work
            #=======================================
            end = dt.datetime.now()
            if time:
                print '\t-- End time:   ', end
                print '\t-- Time to complete: %s' % (str(end - start))

            #break
            """
            count += 1
            if count >= 10:
                break
            """

        if debug: print '\n len(return_list): %d' % len(return_list)
        return return_list, return_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_rd_digests_dict():  #get_rds_uid_dict():
    try:
        rd_digests_dict_cached = cache.get('rd_digests_dict')
        if rd_digests_dict_cached:
            rd_digests_dict = rd_digests_dict_cached
        else:
            print '\n building rd_digest_cache...'
            rd_digests, rd_digests_dict = build_rd_digest_cache()
            cache.set('rd_digests', rd_digests, timeout=CACHE_TIMEOUT)
            cache.set('rd_digests_dict', rd_digests_dict, timeout=CACHE_TIMEOUT)
        return rd_digests_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_rds_digests():
    try:
        rd_digests_cached = cache.get('rd_digests')
        if rd_digests_cached:
            rd_digests = rd_digests_cached
        else:
            rd_digests, rd_digests_dict = build_rd_digest_cache()
            cache.set('rd_digests', rd_digests, timeout=CACHE_TIMEOUT)
            cache.set('rd_digests_dict', rd_digests_dict, timeout=CACHE_TIMEOUT)
        return rd_digests
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_uid_digests():
    uid_digests = {}

    try:
        assets = get_asset_list()
        if not assets or assets is None:
            message = 'No asset data.'
            raise Exception(message)

        count_items = 0
        for asset in assets:
            if 'assetType' in asset:
                if asset['assetType'] in ['Array', 'notClassified', 'Not Classified']:
                    continue
                #else:
                #    print '\n assetType: ', asset['assetType']
            if 'uid' in asset:
                #digest = get_last_deployment_digest(asset['uid'])
                if not asset['uid'] or asset['uid'] is None or len(asset['uid']) == 0:
                    continue
                uid_digests[asset['uid']] = get_last_deployment_digest(asset['uid'])
                count_items += 1
                print '\n count: ', count_items

            #if len(uid_digests) > 10:
            #    break
        print '\n debug -- len(uid_digests): ', len(uid_digests)
        cache.set('uid_digests', uid_digests, timeout=CACHE_TIMEOUT)
        return uid_digests
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None