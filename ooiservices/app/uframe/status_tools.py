#!/usr/bin/env python

"""
Asset Management - Status: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.stream_tools import get_stream_list
from ooiservices.app.uframe.common_tools import (operational_status_values, get_array_locations)
from ooiservices.app.uframe.asset_cache_tools import get_assets_dict
from ooiservices.app.uframe.toc_tools import get_toc_reference_designators
from ooiservices.app.uframe.stream_tools_iris import get_iris_rds
from ooiservices.app.uframe.stream_tools_rds import get_rds_rds
from ooiservices.app.uframe.vocab import (get_vocab_dict_by_rd, get_vocab_codes, get_vocab, get_vocabulary_arrays,
                                          get_display_name_by_rd)
from ooiservices.app.uframe.uframe_tools import (get_assets_from_uframe, uframe_get_status_by_rd,
                                                 uframe_get_nodes_for_site, uframe_get_sensors_for_platform,
                                                 get_deployments_digest_by_uid, uframe_get_sites_for_array,
                                                 uframe_get_asset_by_uid)

# development work
from ooiservices.app.uframe.common_tools import dump_dict
from copy import deepcopy

import datetime as dt
from ooiservices.app import cache
from ooiservices.app.uframe.config import get_cache_timeout


# Get status arrays.
def _get_status_arrays():
    """ Get status for all arrays.
    """
    results = []
    try:
        # Get array(s) status for a site.
        result = get_status_arrays()
        if result is not None:
            results = result
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get status sites.
def _get_status_sites(rd):
    """ For a specific array, get all sites with status.
    Sample request: http://localhost:4000/uframe/status/sites/CE
    """
    time = False
    try:
        # Verify rd is a valid reference designator for an array.
        if not rd or rd is None:
            message = 'Provide an array code.'
            raise Exception(message)
        if len(rd) != 2: # or not is_array(rd):
            message = 'Provide a valid array code.'
            raise Exception(message)

        """
        # Get array information from vocabulary.
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

        # Get platform(s) status for a site.
        results = get_status_sites(rd)
        end = dt.datetime.now()
        if time:
            print '-- End time:   ', end
            print '-- Time to process %s site(s) status: %s\n' % (rd, str(end - start))
        if not results or results is None:
            results = []
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Get status platforms.
def _get_status_platforms(rd):
    """ Get status for all platforms associated with a specific site.
    """
    results = []
    try:
        # Verify reference designator is proper form and valid for system.
        if not rd or rd is None:
            message = 'Provide a valid reference designator for a site.'
            raise Exception(message)
        if len(rd) != 8:
            message = 'Provide a valid site code.'
            raise Exception(message)
        '''
        if not is_mooring(rd):
            message = 'The reference designator (\'%s\') is an invalid site.'
            raise Exception(message)
        '''
        array_dict = get_vocabulary_arrays()
        if rd[:2] not in array_dict:
            message = 'Unknown array code (\'%s\') provided, unable to process request.' % rd
            raise Exception(message)

        # Get platform status for site provided.
        result = get_status_platforms(rd)
        if result is not None:
            results = result
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get status instrument.
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

        # Get instrument status for instrument provided.
        result = get_status_instrument(rd)

        if result is not None:
            results = result
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Status worker functions for arrays, sites, platforms and instrument.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Worker get status arrays.
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
          "reason": null,
          "reference_designator": "GS",
          "status": {
            "count": 1,
            "legend": {
              "degraded": 0,
              "failed": 0,
              "notTracked": 1,
              "operational": 0,
              "removedFromService": 0
            }
          }
        },
        {
          "display_name": "Global Station Papa",
          "latitude": 49.9795,
          "longitude": -144.254,
          "reason": null,
          "reference_designator": "GP",
          "status": {
            "count": 2,
            "legend": {
              "degraded": 0,
              "failed": 0,
              "notTracked": 2,
              "operational": 0,
              "removedFromService": 0
            }
          }
        },
        . . .

    When system first comes up, if no status for an array, the empty_status_template is used in response:
    {
      "arrays": [
        {
          "display_name": "Global Southern Ocean",
          "latitude": -54.0814,
          "longitude": -89.6652,
          "reason": null,
          "reference_designator": "GS",
          "status": {
            "count": 0,
            "legend": {
              "degraded": 0,
              "failed": 0,
              "notTracked": 0,
              "operational": 0,
              "removedFromService": 0
            }
          }
        },
    """
    empty_status_template = {
        'count': 0,
        'legend': {
          'degraded': 0,
          'failed': 0,
          'notTracked': 0,
          'operational': 0,
          'removedFromService': 0
        }
      }
    arrays_patch = get_array_locations()
    try:
        # Get array information from vocabulary.
        arrays = {}
        results = []
        array_dict = get_vocabulary_arrays()
        if not array_dict or array_dict is None:
            message = 'Unable to obtain required information for processing.'
            raise Exception(message)

        # Get uframe status for arrays.
        status_arrays = get_uframe_status_data_arrays()
        if not status_arrays or status_arrays is None:
            message = 'No uframe status for arrays.'
            #raise Exception(message)
            current_app.logger.info(message)
            status_arrays = {}


        # Process uframe status for response.
        for k, v in array_dict.iteritems():
            if k not in arrays:
                if k in arrays_patch:
                    arrays[k] = {}
                    arrays[k]['reference_designator'] = k
                    arrays[k]['latitude'] = arrays_patch[k]['latitude']
                    arrays[k]['longitude'] = arrays_patch[k]['longitude']
                    if status_arrays and k in status_arrays:
                        arrays[k]['status'] = status_arrays[k]['status']
                        arrays[k]['reason'] = None                          #status_arrays[k]['reason']
                    else:
                        arrays[k]['status'] = empty_status_template         #'notTracked'
                        arrays[k]['reason'] = None

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


# Worker get site(s) status for array.
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
        if debug: print '\n debug -- before get_uframe_status_data %s' % rd
        status_data = get_uframe_status_data(rd)       # uframe data
        if not status_data or status_data is None:
            if debug:
                message = 'No status data returned from uframe for reference designator %s.' % rd
                current_app.logger.info(message)
            status_data = {}

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
            _rd_digests_dict = deepcopy(rd_digests_dict[reference_designator])

            # Add status for reference designator.
            if status_data and (reference_designator in status_data):
                #rd_digests[reference_designator]['status'] = get_status_data(reference_designator)
                _rd_digests_dict['status'] = status_data[reference_designator]['status']
                _rd_digests_dict['reason'] = status_data[reference_designator]['reason']
            else:
                #if debug: print '\n debug -- %s status not supplied in status_data.' % reference_designator
                _rd_digests_dict['status'] = 'notTracked'
                _rd_digests_dict['reason'] = None
            return_list.append(_rd_digests_dict)

            #=======================================
            end = dt.datetime.now()
            if time:
                print '\t\t-- End time:   ', end
                print '\t\t-- Time to process %s site: %s' % (rd, str(end - start))
            #===================================

        if debug: print '\n len(return_list): %d' % len(return_list)
        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_status_platforms(rd=None):
    """ Get assets which contain rd.

    http://localhost:4000/uframe/status/platforms/CE01ISSM (return instruments grouped by node.)
        returns all platforms and associated instruments for CE01ISSM, where a platform
        is an asset containing CE01ISSM and 14 in length. All platforms are grouped by node category.
        (Node categories are available in the vocab_codes dictionary in attribute 'nodes'.)
        By way of an example, for site CE01ISSM, get platforms grouped by node category:
            CE01ISSM-SB[D17]  (Bucket 1 'SB')
            CE01ISSM-MF[D35]  (Bucket 2 'MF')
            CE01ISSM-MF[D37]
            CE01ISSM-MF[C31]
            CE01ISSM-RI[D16]  (Bucket 3 'RI')

    Sample request:
        http://localhost:4000/uframe/status/platforms/CE01ISSM
        http://localhost:4000/uframe/status/platforms/GP02HYPM

    Note:
        - The deployment number provided in status.
        - There should be some integrity check for deployment number on our side to ensure consistency.

    http://host:12587/status/query/CE01ISSM
    [
        {
          "reason" : "1554",
          "status" : "degraded",
          "referenceDesignator" : "CE01ISSM-RID16",
          "deployment" : 43
        },
        {
          "reason" : null,
          "status" : "notTracked",
          "referenceDesignator" : "CE01ISSM-SBC11",
          "deployment" : 2
        }]

    http://host:12587/status/query/CE01ISSM/RID16
    [
        {
          "reason" : "1554",
          "status" : "degraded",
          "referenceDesignator" : "CE01ISSM-RID16",
          "deployment" : 43
        },
        {
          "reason" : "1989",
          "status" : "degraded",
          "referenceDesignator" : "CE01ISSM-RID16-00-DCLENG000",
          "deployment" : 4
        },
        . . .
    ]

    Response:
    {
      "platforms": [
        {
          "header": {
            "code": "MF",
            "status": "degraded",
            "title": "Multi-Function Node"
          },
          "items": [
            {
              "depth": 0.0,
              "display_name": "Seawater pH",
              "end": null,
              "latitude": 44.65828,
              "longitude": -124.09525,
              "maxdepth": 25.0,
              "mindepth": 25.0,
              "reason": null,
              "reference_designator": "CE01ISSM-MFD35-06-PHSEND000",
              "start": null,
              "status": "degraded",
              "uid": "A00799",
              "waterDepth": null
            },
            {
              "depth": 0.0,
              "display_name": "Seafloor Pressure",
              "end": null,
              "latitude": 44.65828,
              "longitude": -124.09525,
              "maxdepth": 25.0,
              "mindepth": 25.0,
              "reason": null,
              "reference_designator": "CE01ISSM-MFD35-02-PRESFA000",
              "start": null,
              "status": "failed",
              "uid": "A01014",
              "waterDepth": null
            },
            . . .
    """
    total_time = False
    time = False
    debug = False
    return_list = []
    try:
        if rd is None or not rd:
            message = 'Null or empty reference designator provided for site.'
            raise Exception(message)
        start = dt.datetime.now()
        if total_time:
            print '\n-- Processing for platforms...'
            print '-- Start time: ', start
        nodes = uframe_get_nodes_for_site(rd)

        # Get node 'codes' to identify sections in response.
        node_codes = []
        for node in nodes:
            if node and len(node) > 2:
                tmp = node[:2]
                if tmp not in node_codes:
                    node_codes.append(tmp)

        platforms = []
        for node in nodes:
            if node:
                tmp = '-'.join([rd, node])
                if tmp not in platforms:
                    platforms.append(tmp)

        sensors_by_platform = {}
        instruments_by_platform = {}
        working_rds = []
        sensors_iris = get_iris_rds()
        sensors_rds = get_rds_rds()
        for platform in platforms:
            sensors = uframe_get_sensors_for_platform(platform)
            platform_replace = platform + '-'
            for iris_sensor in sensors_iris:
                if platform in iris_sensor:
                    tmp_sensor = iris_sensor[:].replace(platform_replace, '')
                    if tmp_sensor not in sensors:
                        sensors.append(tmp_sensor)
            for rds_sensor in sensors_rds:
                if platform in rds_sensor:
                    tmp_sensor = rds_sensor[:].replace(platform_replace, '')
                    if tmp_sensor not in sensors:
                        sensors.append(tmp_sensor)
            if sensors:
                sensors_by_platform[platform] = sensors
                for sensor in sensors:
                    if sensor:
                        tmp = '-'.join([platform, sensor])[:]
                        if tmp and tmp not in working_rds:
                            working_rds.append(tmp)
                        if debug: print tmp
                        if platform not in instruments_by_platform:
                            instruments_by_platform[platform] = []
                        instruments_by_platform[platform].append(tmp[:])

        if not working_rds:
            return None

        # Get rd_digest dictionary.
        rd_digests_dict = get_rd_digests_dict()

        # Process each (instrument) reference designator and add status and reason to rd_digests.
        final_rds = []
        for reference_designator in working_rds:
            if debug: print '\n debug -- [Platforms] Processing reference designator: ', reference_designator
            if reference_designator not in rd_digests_dict:
                if debug: print '\n debug -- %s not in rd_digests_dict (continue)' % reference_designator
                continue

            if reference_designator and reference_designator not in final_rds:
                final_rds.append(reference_designator)
            #===================================
            rd_start = dt.datetime.now()
            if time:
                print '\n\t-- Processing %s... ' % reference_designator
                print '\t\t-- Start time: ', rd_start
            #===================================
            status_data = get_uframe_status_data(reference_designator)
            if not status_data or status_data is None:
                #message = 'No status data returned from uframe for reference designator %s.' % reference_designator
                #current_app.logger.info(message)
                status_data = {}

            # Add status for reference designator.
            _rd_digests_dict = deepcopy(rd_digests_dict[reference_designator])
            if status_data and (reference_designator in status_data):
                _rd_digests_dict['status'] = status_data[reference_designator]['status']
                _rd_digests_dict['reason'] = status_data[reference_designator]['reason']
            else:
                #if debug: print '\n debug -- %s status not supplied in status_data.' % reference_designator
                _rd_digests_dict['status'] = 'notTracked'
                _rd_digests_dict['reason'] = None
            return_list.append(_rd_digests_dict)
            #=======================================
            rd_end = dt.datetime.now()
            if time:
                print '\t\t-- End time:   ', rd_end
                print '\t\t-- Time to process %s: %s' % (reference_designator, str(rd_end - rd_start))
            #===================================

        # Get site sections for display.
        sections = []
        if final_rds:
            final_rds.sort()
            sections = get_site_sections(final_rds, return_list)
        #=======================================
        end = dt.datetime.now()
        if total_time:
            if time:
                print '\n-- End time:   ', end
            else:
                print '-- End time:   ', end
            print '-- Time to process %s site: %s\n' % (rd, str(end - start))
        #===================================

        return sections
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Create list of sections to display on Platforms page navigation.
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

        uframe status response (note multiple deployments):
        [
            {
              "reason" : null,
              "status" : "notTracked",
              "referenceDesignator" : "CP03ISSM-SBD11",
              "deployment" : 3
            },
            {
              "reason" : null,
              "status" : "notTracked",
              "referenceDesignator" : "CP03ISSM-SBD11-00-DCLENG000",
              "deployment" : 3
            },
            {
              "reason" : null,
              "status" : "notTracked",
              "referenceDesignator" : "CP03ISSM-SBD11-00-DCLENG000",
              "deployment" : 2
            },
        """
    #section_list = []
    #sections = []
    debug = False
    warning = False
    try:
        # Verify there is something to process.
        if not unique_list or unique_list is None:
            message = 'Unable to process null or empty list to get site sections.'
            raise Exception(message)

        # Get vocabulary codes to use when processing sections.
        vocab_codes = get_vocab_codes()
        if vocab_codes is None:
            message = 'Unable to process sites without vocabulary information (codes).'
            raise Exception(message)

        # Get vocabulary dict to use when processing special sections (GP upper/lower for profiler).
        vocab_dict = get_vocab()
        if vocab_dict is None:
            message = 'Unable to process special site nodes without vocabulary information (dict).'
            raise Exception(message)

        # Get rd_array to determine if business rule apply.
        rd_array = unique_list[0][:2]
        apply_multi_node_rule = False
        #special_node_codes = 'WF'
        special_node_codes = ['WF', 'GL']
        if rd_array == 'GP':
            apply_multi_node_rule = True

        # Get rd_root.
        rd_root = unique_list[0][:9]
        # Get unique platforms (14).
        unique_platforms = []
        for rd in unique_list:
            if len(rd) > 14 and rd[:14] not in unique_platforms:
                unique_platforms.append(rd[:14])

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get section codes.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        section_codes = []
        for item in unique_platforms:
            item = item.replace(rd_root, '')
            #if item[:2] not in section_codes and item[:2] != special_node_codes and not apply_multi_node_rule:
            if item[:2] not in section_codes and item[:2] not in special_node_codes and not apply_multi_node_rule:
                section_codes.append(item[:2])
            #elif apply_multi_node_rule and item[:2] == special_node_codes:
            elif apply_multi_node_rule and item[:2] in special_node_codes:
                section_codes.append(item[:5])
            elif item[:2] in special_node_codes:
                section_codes.append(item[:5])
                if debug: print '\n debug -- section code (add): ', item[:5]
            elif item[:2] not in section_codes:
                section_codes.append(item[:2])

        if not section_codes:
            message = 'No section codes found for %s.' % rd_root[:8]
            current_app.logger.info(message)
            return []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get lists of instruments and uids.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        instruments = []
        #uids = {}
        uids = []
        for item in return_list:
            if len(item['reference_designator']) > 14:
                if item['reference_designator'] and item['reference_designator'] is not None and \
                   item['uid'] and item['uid'] is not None:
                        rd = item['reference_designator'][:]
                        uid = item['uid'][:]
                        if rd not in instruments:
                            instruments.append(rd)
                        if uid not in uids:
                            #uids[uid] = rd                 # Dynamic (slower) version, uses uid dict
                            uids.append(uid)                # Added for cache, uses list not uid dict

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

            # Set the header title.
            if len(code) == 2:
                if code in vocab_codes['nodes']:
                    header['title'] = vocab_codes['nodes'][code]
            else:
                # look up node code value for instrument from vocab_dict.
                code_value = rd_root + code
                if debug: print '\n debug -- code value: ', code_value
                if code_value in vocab_dict:
                    header['title'] = vocab_dict[code_value]['name']

            header['status'] = operational_status_values()[1]       # Update for live status
            headers.append(header)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Populate each section 'items' with a list of instruments.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for header in headers:
            section = {}
            section['header'] = header
            section_code = header['code']
            prefix = rd_root + section_code
            if debug: print '\n debug -- processing prefix: ', prefix
            cart = []
            for item in return_list:
                if item['reference_designator'] not in instruments:
                    if warning:
                        print '-- Warning: reference designator %s not in instrument list.' % \
                              item['reference_designator']
                    continue
                # For a site and first two characters of node (XXXXXXXX-XX), if match node bucket, process.
                if prefix == item['reference_designator'][:len(prefix)]:

                    # Add start and end times for reference designator.
                    if not time_dict or time_dict is None:
                        if warning:
                            print '-- Warning: No time_dict for reference designator: %s ' % \
                                  item['reference_designator']
                        item['start'] = None
                        item['end'] = None
                    elif item['reference_designator'] not in time_dict:
                        if warning:
                            print '-- Warning: No time entries in time_dict for reference designator: %s ' % \
                                  item['reference_designator']
                        item['start'] = None
                        item['end'] = None
                    else:
                        item['start'] = time_dict[item['reference_designator']]['start']
                        item['end'] = time_dict[item['reference_designator']]['end']

                    # Add deployment information, if available, for reference designator.
                    # No deployment digest information.
                    if not digest_dict or digest_dict is None:
                        item['latitude'] = None
                        item['longitude'] = None
                        item['waterDepth'] = None
                        item['depth'] = None
                    # Get digest for reference designator from digest dictionary, process.
                    elif item['reference_designator'] in digest_dict:
                        digest = digest_dict[item['reference_designator']]
                        item['latitude'] = digest['latitude']
                        item['longitude'] = digest['longitude']
                        item['waterDepth'] = digest['waterDepth']
                        item['depth'] = digest['depth']
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


# Worker get instrument status for instrument.
def get_status_instrument(rd):
    """ Get the status for a single instrument.
    Sample requests:
        http://localhost:4000/uframe/status/instrument/CE01ISSM-MFC31-00-CPMENG000
        http://localhost:4000/uframe/status/instrument/GA01SUMO-RII11-02-CTDBPP031
    """
    return_list = []
    try:
        #============================================================
        # Verify the rd provided is for an instrument.
        if not rd or rd is None or len(rd) <= 14:
            #if len(rd) <= 14 or not is_instrument(rd):
            message = 'Provide a valid reference designator for an instrument.'
            raise Exception(message)

        # Get uframe status data dictionary.
        status_data = get_uframe_status_data(rd)
        if not status_data or status_data is None:
            #message = 'No status data returned from uframe for reference designator %s.' % rd
            #current_app.logger.info(message)
            status_data = {}

        # Get rd_digest dictionary.
        rd_digests_dict = get_rd_digests_dict()
        if rd in rd_digests_dict:

            _rd_digests_dict = deepcopy(rd_digests_dict[rd])

            # Stream times from time_dict
            time_dict = get_stream_times([rd])
            if not time_dict or time_dict is None:
                _rd_digests_dict['start'] = None
                _rd_digests_dict['end'] = None
                #item['display_name'] = rd
            elif rd not in time_dict:
                _rd_digests_dict['start'] = None
                _rd_digests_dict['end'] = None
                #item['display_name'] = rd
            else:
                _rd_digests_dict['start'] = time_dict[rd]['start']
                _rd_digests_dict['end'] = time_dict[rd]['end']
                #item['display_name'] = time_dict[item['reference_designator']]['name']

            if status_data and (rd in status_data):
                _rd_digests_dict['status'] = status_data[rd]['status']
                _rd_digests_dict['reason'] = status_data[rd]['reason']
            else:
                _rd_digests_dict['status'] = 'notTracked'
                _rd_digests_dict['reason'] = None
            return_list.append(_rd_digests_dict)

        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# End Status worker functions for arrays, sites, platforms and instrument.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#===========================================
# Helper functions
#===========================================

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
    """ Gets latest deployment digest for list of uids from cache. (fast)
    """
    debug = False
    try:
        if debug: print '\n debug -- Entered get_digest_dict...'
        if not uids or uids is None:
            return None
        if debug: print '\n debug -- Number of uids: ', len(uids)
        uid_digests = get_uid_digests()
        if not uid_digests or uid_digests is None:
            message = 'No uid_digests, unable to digests for uids.'
            raise Exception(message)

        digest_dict = {}
        #for uid, item in uids.iteritems():
        for uid in uids:
            if debug:
                print '\n debug -- uid: ', uid

            #digest = get_last_deployment_digest(uid)
            #rd = item['rd']
            #asset_type = item['asset_type']
            digest = None
            digest_rd = None
            if uid in uid_digests:
                if debug: print '\n debug -- uid in uid_digests...'
                digest = uid_digests[uid]
                digest_rd = get_rd_from_uid_digest('Instrument', digest)
            if digest and digest is not None and digest_rd and digest_rd is not None:
                #digest_dict[rd] = digest
                digest_dict[digest_rd] = digest
        if not digest_dict:
            digest_dict = None

        if debug: print '\n debug -- len(digest_dict): ', len(digest_dict)
        return digest_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def format_rd_digest(obj):
    """ Format asset information for digest.
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

        reference_designator = None
        if 'ref_des' in obj:
            if obj['ref_des'] and obj['ref_des'] is not None:
                reference_designator = obj['ref_des'][:]

        if reference_designator is None:
            return None

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
        if debug: print '\n debug format_rd_digest -- exception: ', message
        current_app.logger.info(message)
        return None


# Get uframe status for a reference designator; flip into dict keyed by reference designator.
def get_uframe_status_data(rd):
    """ Get uframe status for site, platform or instrument. Process into dictionary, return.
    """
    debug = False
    try:
        status_data = uframe_get_status_by_rd(rd)
        if debug and status_data:
            print '\n debug -- uframe status data for rd \'%s\': ' % rd
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
        if debug and status and status is not None:
            print '\n debug -- uframe status for rd \'%s\':' % rd
            dump_dict(status)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Get uframe status for arrays; flip into dict keyed by reference designator.
def get_uframe_status_data_arrays():
    """ Get uframe status for array, site, platform or instrument. Process into dictionary, return.
    [
        {
          "status" : {
            "legend" : {
              "notTracked" : 1,
              "removedFromService" : 0,
              "degraded" : 0,
              "failed" : 0,
              "operational" : 0
            },
            "count" : 1
          },
          "referenceDesignator" : "RS"
        },

    """
    debug = False
    from copy import deepcopy
    try:
        status_data = uframe_get_status_by_rd()
        if debug:
            print '\n debug -- uframe status data for arrays.'
            dump_dict(status_data, debug)

        if not status_data or status_data is None:
            status = None
        else:
            status = {}
            for item in status_data:
                if item:
                    if 'referenceDesignator' in item:
                        if item['referenceDesignator']:
                            rd = deepcopy(item['referenceDesignator'])
                            del item['referenceDesignator']
                            status[rd] = item

            if not status:
                status = None
        if debug:
            print '\n debug -- uframe status for arrays: '
            dump_dict(status)
        return status
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_log_block():
    """ Get event log for history, default count=100. To be defined.
    """
    log = []
    return log


# Get uframe deployment digests, reverse sorted by ('deploymentNumber', 'versionNumber', and 'startTime'.
# Return current and operational current.
def get_last_deployment_digest(uid):
    digest = None
    #digest_operational = None
    try:
        digests = get_deployments_digests(uid)
        #digests, digests_operational = get_deployments_digests(uid)
        if digests and digests is not None:
            digest = digests[0]
        """
        if digests_operational and digests_operational is not None:
            digest_operational = digests_operational[0]
        """
        return digest   #, digest_operational
    except Exception as err:
        message = 'Exception: get_last_deployment_digest: uid: %s: %s' % (uid, str(err))
        current_app.logger.info(message)
        return None


def add_deployment_info(work):
    """ Process work dictionary and add deployment items.
    """
    try:
        if not work or work is None:
            return None

        # Get deployment digest using uid from work dictionary.
        #digest, _ = get_last_deployment_digest(work['uid'])
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


def get_deployments_digests(uid):
    """ Get list of deployment digest items for a uid; sorted in reverse by deploymentNumber, versionNumber and startTime.

    Sample request:
        http://localhost:4000/uframe/dev/digest/OL000582
        Queries uframe endpoint: http://host:12587/asset/deployments/OL000582?editphase=ALL
    Sample response data:
        {
          "digest": {
            "deployCruiseIdentifier": "RB-16-05",
            "deploymentNumber": 4,
            "depth": 0.0,
            "editPhase": "OPERATIONAL",
            "endTime": 1498867200000,
            "eventId": 57433,
            "latitude": 49.97434,
            "longitude": -144.23972,
            "mooring_uid": "OL000582",
            "node": "RIM01",
            "node_uid": null,
            "orbitRadius": 0.0,
            "recoverCruiseIdentifier": null,
            "sensor": "00-SIOENG000",
            "sensor_uid": "OL000583",
            "startTime": 1467335220000,
            "subsite": "GP03FLMA",
            "versionNumber": 1,
            "waterDepth": null
          }
        }
    """
    debug = False
    try:
        if debug:
            print '\n debug ========================================================='
            print '\n debug -- Entered get_deployments_digests for uid: %s' % uid
        digests = get_deployments_digest_by_uid(uid)
        if not digests or digests is None or len(digests) == 0:
            return None #, None
        if debug: print '\n len(digests): ', len(digests)
        # Sort (reverse) by value of 'deploymentNumber', 'versionNumber', 'startTime'
        try:
            #result = sorted(digests, key=itemgetter('deploymentNumber'))
            #digests.sort(key=lambda x: (-x['deploymentNumber'], -x['versionNumber'], -x['startTime']))
            #digests.sort(key=lambda x: (x['deploymentNumber'], x['versionNumber'], x['startTime']), reverse=True)
            digests.sort(key=lambda x: (x['startTime'], x['deploymentNumber'], x['versionNumber'], x['startTime']), reverse=True)
        except Exception as err:
            print '\n get_deployments_digests : errors: ', str(err)
            pass
        if not digests or digests is None:
            return None #, None

        """
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get 'OPERATIONAL' digests.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        digests_operational = []
        for digest in digests:
            if digest['editPhase'] == 'OPERATIONAL':
                digests_operational.append(digest)
        if digests_operational:
            try:
                digests_operational.sort(key=lambda x: (x['deploymentNumber'], x['versionNumber'], x['startTime']),
                                         reverse=True)
            except Exception as err:
                print '\n digests_operational : errors: ', str(err)
                pass
        """

        if debug:
            print '\n debug -- Exit get_deployments_digests for uid: %s' % uid
            print '\n debug ========================================================='
        return digests #, digests_operational
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None #, None


#===========================================
# Cache helper functions
#===========================================
def build_rds_cache(refresh=False):
    """
    Create a cache for reference designator to current asset uid deployment information.
    The 'rd_digests' and 'rd_digests_dict' are used by status methods.
    """
    debug = False
    time = True
    rd_digests = None
    rd_digests_dict = None
    try:
        if time: print '\n-- Building reference designator digests (refresh: %r)' % refresh
        if not refresh:
            rd_digests_cache = cache.get('rd_digests')
            if rd_digests_cache and rd_digests_cache is not None:
                rd_digests = rd_digests_cache
            else:
                rd_digests = None

            rd_digests_dict_cache = cache.get('rd_digests_dict')
            if rd_digests_dict_cache and rd_digests_dict_cache is not None:
                rd_digests_dict = rd_digests_dict_cache
            else:
                rd_digests_dict = None

        # If refresh (force build) or missing either rd_digest or rd_digest_dict, then rebuild both.
        if refresh or rd_digests is None or rd_digests_dict is None:

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get reference designators from toc...
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if time: print '\n     -- Compiling reference designators from toc...'
            start = dt.datetime.now()
            if time: print '\t-- Start time: ', start
            try:
                rds, _, _ = get_toc_reference_designators()
            except Exception as err:
                message = str(err)
                raise Exception(message)

            if not rds or rds is None:
                message = 'No reference designators returned from toc information.'
                raise Exception(message)
            rds_end = dt.datetime.now()
            if time:
                print '\t-- End time:   ', rds_end
                print '\t-- Time to complete: %s' % (str(rds_end - start))
                print '     -- Completed compiling rds from toc...'
            if debug: print '\t-- Number of reference designators: ', len(rds)

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Compile reference designator digests using rds.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            digests_start = dt.datetime.now()
            if time:
                print '\n     -- Compiling reference designator digests... '
                print '\t-- Start time: ', digests_start
            rd_digests, rd_digests_dict = build_rd_digest_cache(rds)
            if rd_digests is not None:
                cache.delete('rd_digests')
                cache.set('rd_digests', rd_digests, timeout=get_cache_timeout())
            else:
                print 'Failed to construct rd_digests.'
            if rd_digests_dict is not None:
                cache.delete('rd_digests_dict')
                cache.set('rd_digests_dict', rd_digests_dict, timeout=get_cache_timeout())
            else:
                print 'Failed to construct rd_digests_dict.'

            if debug: print '\n\t-- Reference designators (%d) have (%d) rd_digests' % (len(rds), len(rd_digests))
            end = dt.datetime.now()
            if time:
                print '\t-- End time:   ', end
                print '\t-- Time to complete: %s' % (str(end - digests_start))
                print '     -- Completed compiling reference designator digests... '

            if time:
                print '\n\t-- End time:   ', end
                print '\t-- Time (total) to complete: %s' % (str(end - start))
                print '-- Completed building reference designator digests...\n'
        return rd_digests, rd_digests_dict  # 2017-02-01
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None, None                   # 2017-02-01


def build_rd_digest_cache(rds):
    """
    Create a cache for reference designator to current [operational] asset uid deployment digest.
    """
    debug = False
    time = True

    return_list = []
    return_dict = {}
    try:
        if debug: print '\n debug -- Number of rds: ', len(rds)
        if not rds or rds is None:
            message = 'No reference designator to process, unable to build rd_digest cache.'
            raise Exception(message)
        start = dt.datetime.now()
        if time:
            print '\n\t-- Preparing information before processing... '
            print '\t-- Start time: ', start

        #=======================================
        # Get assets_dict
        assets_dict = get_assets_dict()
        if assets_dict is None:
            message = 'Failed to retrieve assets_dict.'
            raise Exception(message)

        # Get uid_digests
        uid_digests = get_uid_digests()
        if uid_digests is None or not uid_digests:
            message = 'Failed to retrieve uid_digests.'
            raise Exception(message)

        """
        # Get uid_digests operational
        uid_digests_operational = get_uid_digests_operational()
        if uid_digests_operational is None or not uid_digests_operational:
            message = 'Failed to retrieve uid_digests_operational.'
            raise Exception(message)
        """
        #=======================================
        end = dt.datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to get information: %s' % (str(end - start))
            print '\t-- Completed preparing information before processing... '

        #count = 0
        if debug:
            print '\n debug -- len(assets_dict): ', len(assets_dict)
            print '\n debug -- len(uid_digests): ', len(uid_digests)

        # Get all asset reference designators and current digest information available.
        for id, asset in assets_dict.iteritems():
            asset_type = None
            if 'assetType' in asset:
                asset_type = asset['assetType']
                if asset_type is None or not asset_type or len(asset_type) == 0:
                    continue
                if asset_type not in ['Platform', 'Mooring', 'Node', 'Instrument', 'Sensor']:
                    continue
            if asset_type is None:
                continue

            # Use uid_digests to process all assets of types which may have deployments.
            asset_uid = None
            if 'uid' in asset:
                asset_uid = asset['uid']
            if asset_uid is None or not asset_uid or len(asset_uid) == 0:
                continue

            current_digest = None
            """
            if asset_uid in uid_digests_operational:
                current_digest = uid_digests_operational[asset_uid]
            """
            if asset_uid in uid_digests:
                current_digest = uid_digests[asset_uid]
            if current_digest is None or not current_digest or len(current_digest) == 0:
                continue

            asset_rd = get_rd_from_uid_digest(asset_type, current_digest)
            if asset_rd is None or not asset_rd or len(asset_rd) == 0:
                continue

            # Build digest for reference designator.
            work = format_rd_digest(asset)

            # Add deployment data from uid_digest.
            if work is not None:
                work['latitude'] = current_digest['latitude']
                work['longitude'] = current_digest['longitude']
                work['depth'] = current_digest['depth']
                work['waterDepth'] = current_digest['waterDepth']

                return_list.append(work)
                return_dict[work['reference_designator']] = work

        if debug:
            print '\n debug -- return_list: ', len(return_list)
            dump_dict(return_list[0], debug)

        return return_list, return_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None, None


# Single uid, get fresh rd digest. (Uses uframe to get asset.)
def get_fresh_rd_digest(uid):
    from ooiservices.app.uframe.asset_tools import format_asset_for_ui

    debug = False
    try:
        if uid is None or not uid or len(uid) == 0:
            message = 'No asset uid provided, empty or null; unable to provide rd digest.'
            raise Exception(message)

        # Get uid_digests
        uid_digests = get_uid_digests()
        if uid_digests is None or not uid_digests:
            message = 'Failed to retrieve uid_digests.'
            raise Exception(message)

        current_digest = None
        if uid in uid_digests:
            if debug: print '\n debug: uid %s in uid_digests...' % uid
            current_digest = uid_digests[uid]
            if debug:
                print '\n debug -- current_digest: '
                dump_dict(current_digest, debug)
        if current_digest is None or not current_digest or len(current_digest) == 0:
            message = 'Asset uid \'%s\' returned null or empty uid_digest.' % uid
            raise Exception(message)

        asset = uframe_get_asset_by_uid(uid)
        if debug:
            print '\n debug -- asset: '
            dump_dict(asset, debug)
        if not asset or asset is None:
            message = 'Failed to get asset with uid: %s' % uid
            current_app.logger.info(message)
            raise Exception(message)

        asset_type = None
        if 'assetType' in asset:
            asset_type = asset['assetType']
        if not asset_type or asset_type is None:
            message = 'Failed to get asset_type for asset with uid: %s' % uid
            raise Exception(message)

        if debug: print '\n debug -- asset_type: ', asset_type
        asset_rd = get_rd_from_uid_digest(asset_type, current_digest)
        if asset_rd is None or not asset_rd or len(asset_rd) == 0:
            message = 'Asset uid returned null or empty reference designator.'
            raise Exception(message)

        # Build digest for reference designator.
        ui_asset = format_asset_for_ui(asset)
        work = format_rd_digest(asset)

        # Add deployment data.
        if work is not None:
            work['latitude'] = current_digest['latitude']
            work['longitude'] = current_digest['longitude']
            work['depth'] = current_digest['depth']
            work['waterDepth'] = current_digest['waterDepth']

        return asset_rd, work
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None, None


def get_rd_from_uid_digest(asset_type, digest):
    """
    Get reference designator from a single uid digest of a specific asset type.
    """
    try:
        if asset_type not in ['Platform', 'Mooring', 'Node', 'Instrument', 'Sensor']:
            message = 'Invalid asset type (\'%s\') provided to get_rd_from_uid_digest.' % asset_type
            current_app.logger.info(message)
            return None

        if not digest or digest is None or len(digest) == 0:
            message = 'Empty or null digest provided to get_rd_from_uid_digest for %s.' % asset_type
            current_app.logger.info(message)
            return None

        if 'subsite' not in digest or 'node' not in digest or 'sensor' not in digest:
            message = 'Digest provided does not contain one or more required attribute(s) (subsite, node, sensor).'
            current_app.logger.info(message)
            return None

        if digest['subsite'] is None or not digest['subsite']:
            message = 'Digest contains null or empty value for \'subsite\'.'
            current_app.logger.info(message)
            return None
        if digest['node'] is None or not digest['node']:
            message = 'Digest contains null or empty value for \'node\'.'
            current_app.logger.info(message)
            return None
        if digest['sensor'] is None or not digest['sensor']:
            message = 'Digest contains null or empty value for \'sensor\'.'
            current_app.logger.info(message)
            return None

        if asset_type in ['Platform', 'Mooring']:
            rd = digest['subsite']
        elif asset_type == 'Node':
            rd = '-'.join([digest['subsite'], digest['node']])
        elif asset_type in ['Instrument', 'Sensor']:
            rd = '-'.join([digest['subsite'], digest['node'], digest['sensor']])
        else:
            rd = None
        return rd
    except Exception as err:
        message = 'Error getting reference designator for %s: %s' % (asset_type, str(err))
        current_app.logger.info(message)
        raise Exception(message)


def get_rd_digests_dict():
    debug = False
    try:
        rd_digests_dict_cached = cache.get('rd_digests_dict')
        if rd_digests_dict_cached and rd_digests_dict_cached is not None and 'error' not in rd_digests_dict_cached:
            rd_digests_dict = rd_digests_dict_cached
        else:
            if debug: print '\n building rd_digest_cache...'
            rd_digests, rd_digests_dict = build_rds_cache(refresh=True)
            if rd_digests and rd_digests is not None:
                cache.set('rd_digests', rd_digests, timeout=get_cache_timeout())
            else:
                message = 'rd_digests failed to provide data on load.'
                raise Exception(message)
            if rd_digests_dict and rd_digests_dict is not None:
                cache.set('rd_digests_dict', rd_digests_dict, timeout=get_cache_timeout())
            else:
                message = 'rd_digests_dict failed to provide data on load.'
                raise Exception(message)
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
            rd_digests, rd_digests_dict = build_rds_cache(refresh=True)
            if not rd_digests or rd_digests is None:
                message = 'rd_digests failed to provide data on load.'
                raise Exception(message)
            if not rd_digests_dict or rd_digests_dict is None:
                message = 'rd_digests_dict failed to provide data on load.'
                raise Exception(message)
            cache.set('rd_digests', rd_digests, timeout=get_cache_timeout())
            cache.set('rd_digests_dict', rd_digests_dict, timeout=get_cache_timeout())
        return rd_digests
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_uid_digests(refresh=False):
    """ Get uid_digests, if cached then return 'uid_digests' cache, otherwise build cache.
    """
    time = True
    uid_digests = None
    try:

        if not refresh:
            uid_digests_cached = cache.get('uid_digests')
            if uid_digests_cached:
                uid_digests = uid_digests_cached

        if refresh or not uid_digests or uid_digests is None:
            start = dt.datetime.now()
            if time:
                print '\n-- Processing uframe uid_digests for reference designators... '
                print '\t-- Start time: ', start
            #uid_digests, uid_digests_operational = build_uid_digests_cache()
            uid_digests = build_uid_digests_cache()
            if not uid_digests or uid_digests is None:
                message = 'Failed to compile uid_digests cache.'
                raise Exception(message)
            cache.delete('uid_digests')
            cache.set('uid_digests', uid_digests, timeout=get_cache_timeout())

            """
            if not uid_digests_operational or uid_digests_operational is None:
                message = 'Failed to compile uid_digests_operational cache.'
                raise Exception(message)

            cache.delete('uid_digests_operational')
            cache.set('uid_digests_operational', uid_digests_operational, timeout=get_cache_timeout())
            """
            end = dt.datetime.now()
            if time:
                print '\t-- End time:   ', end
                print '\t-- Time to complete: %s' % (str(end - start))

        return uid_digests
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def build_uid_digests_cache():
    """ Full construction of 'uid_digest' cache.
    """
    debug = False
    uid_digests = {}
    #uid_digests_operational = {}
    try:
        if debug: print '\n debug -- Getting assets from uframe...'
        # Get assets from uframe.
        uframe_assets = get_assets_from_uframe()
        if not uframe_assets:
            message = 'No uframe asset content returned.'
            raise Exception(message)

        if debug: print '\n debug -- Completed getting assets from uframe...'

        # Get vocabulary dictionary once.
        vocab_dict = get_vocab()

        #count_items = 0
        for asset in uframe_assets:

            asset_type = None
            if 'assetType' in asset:
                if asset['assetType'] in ['Array', 'notClassified', 'Not Classified']:
                    continue
                if asset['assetType'] is None or not asset['assetType'] or len(asset['assetType']) == 0:
                    continue
                asset_type = asset['assetType']

            asset_id = None
            if 'assetId' in asset:
                if asset['assetId'] is None:
                    continue
                asset_id = asset['assetId']

            asset_uid = None
            if 'uid' in asset:
                if not asset['uid'] or asset['uid'] is None or len(asset['uid']) == 0:
                    continue
                asset_uid = asset['uid']

            # ok to proceed?
            if asset_id is None or asset_uid is None or asset_type is None:
                continue

            # Get current deployment digest for asset uid; if None, continue.
            #digest, digest_operational = get_last_deployment_digest(asset_uid)      # Changed 11-29-2016 editPhase
            digest = get_last_deployment_digest(asset_uid)
            if digest is None or not digest or len(digest) == 0:
                continue
            digest['id'] = asset_id
            digest['reference_designator'] = get_rd_from_uid_digest(asset_type, digest)

            # (10506) For mobile assets report depth as maximum depth value provided in vocabulary.
            if 'MOAS' in digest['reference_designator']:
                if digest['reference_designator'] in vocab_dict:
                    tmp = vocab_dict[digest['reference_designator']]
                    if 'maxdepth' in tmp:
                        digest['depth'] = tmp['maxdepth']

            uid_digests[asset['uid']] = digest

            """
            # Check and add operational digest information.
            if digest_operational is None or not digest_operational or len(digest_operational) == 0:
                continue
            digest_operational['id'] = asset_id
            digest_operational['reference_designator'] = get_rd_from_uid_digest(asset_type, digest_operational)
            uid_digests_operational[asset['uid']] = digest_operational
            """
            #count_items += 1
            #print '\n count: ', count_items

            #if len(uid_digests) > 10:
            #    break
        if debug:
            print '\n debug -- len(uid_digests): ', len(uid_digests)

        if uid_digests and uid_digests is not None:
            print '\n -- Number of uid_digests: ', len(uid_digests)
        else:
            print '\n -- No uid_digests returned from processing.'
        return uid_digests  #, uid_digests_operational
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


# Review with deployments.
def uid_digests_cache_update(uid_digests):
    """ Full update uid_digests cache.
    """
    debug = False
    try:
        if debug: print '\n debug -- Entered uid_digests...'
        if not uid_digests or uid_digests is None or not isinstance(uid_digests, dict):
            message = 'Failure to update uid_digests from digests provided.'
            raise Exception(message)

        if debug: print '\n Perform uid_digests update...'
        cache.delete('uid_digests')
        cache.set('uid_digests', uid_digests, timeout=get_cache_timeout())
        if debug: print '\n Completed uid_digests update...'
        return
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def update_uid_digests_cache(uid, digest):
    """
    Updates uid_digest cache, also updates rd_digest and rd_digest_dict cache also.
    """
    debug = False
    try:
        if debug:
            print '\n debug -- Entered update_uid_digests_cache...'
            dump_dict(digest, debug)

        # Get the cache; If cache exists, update the 'uid_digests' cache.
        uid_digests = cache.get('uid_digests')
        if uid_digests and uid_digests is not None:
            if uid in uid_digests:
                if debug: print '\n debug -- uid (%s) in uid_digests...' % uid
            uid_digests[uid] = digest
            uid_digests_cache_update(uid_digests)

            # Update rd_digests and rd_digests dict cache.
            if not update_rd_digests_cache(uid):
                message = '********* Failed to update rd_digests cache **********'
                current_app.logger.info(message)
        return
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def update_rd_digests_cache(uid):
    debug = False
    update = False
    try:
        if debug: print '\n Updating rd_digests caches.....\n'
        rd, work = get_fresh_rd_digest(uid)
        if debug:
            print '\n\t debug -- rd: ', rd
            print '\n\t debug -- work: '
            dump_dict(work, debug)
        if rd and work and rd is not None and work is not None:
            rd_digests = cache.get('rd_digests')
            rd_digests_dict = cache.get('rd_digests_dict')

            # Add
            if rd not in rd_digests_dict:
                if debug: print '\n debug -- rd in rd_digests_dict'
                rd_digests_dict[rd] = work
                rd_digests.append(work)
                update = True

            # Update
            else:
                found_it = False
                for digest in rd_digests:
                    if digest['uid'] == uid:
                        digest.update(work)
                        found_it = True
                        break
                # If found it, update dictionary.
                if found_it:
                    rd_digests_dict[rd] = work
                    update = True
                if debug: print '\n debug -- found_it: ', found_it

            if update:
                if debug: print '\n Updating rd_digests...'
                cache.delete('rd_digests')
                cache.set('rd_digests', rd_digests, timeout=get_cache_timeout())
                if debug: print '\n Updating rd_digests_dict...'
                cache.delete('rd_digests_dict')
                cache.set('rd_digests_dict', rd_digests_dict, timeout=get_cache_timeout())
        return update
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return False