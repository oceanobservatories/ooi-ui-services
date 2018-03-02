#!/usr/bin/env python

"""
Support for rds data gathering functions for recovered cabled instruments 12000.
"""
__author__ = 'Edna Donoughe'


from flask import current_app
from bs4 import BeautifulSoup
import urllib
from datetime import datetime


from ooiservices.app import cache
from ooiservices.app.uframe.config import get_cache_timeout
from ooiservices.app.uframe.common_tools import (rds_get_supported_years, rds_get_supported_array_codes,
                                                 get_extensions_by_sensor_type)
from ooiservices.app.uframe.config import (get_uframe_timeout_info, get_rds_base_url)
from ooiservices.app.uframe.rds_common_tools import (get_target_cache_by_sensor_type, _get_subfolder_list,
                                                     add_nav_urls_to_cache)
import requests
import requests.adapters
import requests.exceptions


# 12000 THSP. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_THSP(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from raw data server for
        Hydrothermal Vent Fluid In-situ Chemistry (RS03INT1-MJ03C-09-THSPHA301)

    [Under review] Optional arguments are for testing ONLY:
        ref_des: Pass in a reference designator to only retrieve those results
        date_str: Pass in a date string (yyyy-mm-dd) to only get data from a specific day

    Example where dat exists:
    https://rawdata.oceanobservatories.org/files/RS03INT1/MJ03C/THSPHA301/2017/08/

    ['THSPHA301_10.31.8.9_2101_20170815T1927_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170822T0758_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170822T1033_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170822T1052_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170823T0318_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170824T0000_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170825T0000_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170826T0000_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170827T0000_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170828T0000_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170829T0000_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170830T0000_UTC.dat',
    'THSPHA301_10.31.8.9_2101_20170831T0000_UTC.dat']

    Cache build out with ACTUAL REFERENCE DESIGNATOR:
    {
      "rds_THSP": {
        "RS03INT1-MJ03C-09-THSPHA301": {
          "2017": {
            "08": {
              "15": [
                {
                  "date": "2017-08-15",
                  "datetime": "20170815T192700.000Z",
                  "ext": ".dat",
                  "filename": "THSPHA301_10.31.8.9_2101_20170815T1927_UTC.dat",
                  "rd": "RS03INT1-MJ03C-09-THSPHA301",
                  "url": "/RS03INT1/MJ03C/THSPHA301/2017/08/"
                }
              ],
              "22": [
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T075800.000Z",
                  "ext": ".dat",
                  "filename": "THSPHA301_10.31.8.9_2101_20170822T0758_UTC.dat",
                  "rd": "RS03INT1-MJ03C-09-THSPHA301",
                  "url": "/RS03INT1/MJ03C/THSPHA301/2017/08/"
                },
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T103300.000Z",
                  "ext": ".dat",
                  "filename": "THSPHA301_10.31.8.9_2101_20170822T1033_UTC.dat",
                  "rd": "RS03INT1-MJ03C-09-THSPHA301",
                  "url": "/RS03INT1/MJ03C/THSPHA301/2017/08/"
                },
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T105200.000Z",
                  "ext": ".dat",
                  "filename": "THSPHA301_10.31.8.9_2101_20170822T1052_UTC.dat",
                  "rd": "RS03INT1-MJ03C-09-THSPHA301",
                  "url": "/RS03INT1/MJ03C/THSPHA301/2017/08/"
                }
    """
    debug = False
    debug_trace = False
    time = True
    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Specific instruments processed.
        actual_reference_designator = 'RS03INT1-MJ03C-09-THSPHA301'

        # Create  rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator] = None

        sensor_type = filetypes_to_check
        if sensor_type != ['THSP']:
            return {}
        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        # Time
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug_trace: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsite for this sensor type.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS03INT1':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)

            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            for item in subfolders:

                if len(item) != 6:
                    continue
                # Determine if item is a folder link or file
                if '/' in item:
                    if debug: print '\t\t---- %s Processing item: %s...' % (rd, item)
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)

                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:

                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================

                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)

                            if detail_subfolders:

                                # Process years
                                for year in detail_subfolders:

                                    #=======================================
                                    # Remove to process all years
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = _get_subfolder_list(month_url,
                                                                                                  filetypes=filetypes_to_check,
                                                                                                  extensions=extensions_to_check) #None)

                                            if not days_file_list:
                                                continue

                                            date_part = None
                                            for filename in days_file_list:
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break
                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if base_url in _url:
                                                    _url = _url.replace(base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Update rds_nav_urls for sensor.
                                                work_nav_urls[actual_reference_designator] = rds_base_url + nav_url

                                                # Custom for sensor.
                                                ref_des = actual_reference_designator

                                                # Build cache dictionary entry
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])
                                                tmp_item['rd'] = ref_des

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'THSP')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# 12000 TRHP. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_TRHP(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server for
        Hydrothermal Vent Fluid Temperature and Resistivity (RS03INT1-MJ03C-10-TRHPHA301)

    Example where dat exists:
    https://rawdata.oceanobservatories.org/files/RS03INT1/MJ03C/TRHPHA301/2017/08/

    ['TRHPHA301_10.31.8.10_2101_20171202T0211_UTC.dat',
    'TRHPHA301_10.31.8.10_2101_20171203T0000_UTC.dat',
    . . .]

    Cache build out with actual reference designators:
    {
      "rds_TRHP": {
        "RS03INT1-MJ03C-10-TRHPHA301": {
          "2017": {
            "08": {
              "22": [
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T075800.000Z",
                  "ext": ".dat",
                  "filename": "TRHPHA301_10.31.8.10_2101_20170822T0758_UTC.dat",
                  "rd": "RS03INT1-MJ03C-10-TRHPHA301",
                  "url": "/RS03INT1/MJ03C/TRHPHA301/2017/08/"
                },
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T103300.000Z",
                  "ext": ".dat",
                  "filename": "TRHPHA301_10.31.8.10_2101_20170822T1033_UTC.dat",
                  "rd": "RS03INT1-MJ03C-10-TRHPHA301",
                  "url": "/RS03INT1/MJ03C/TRHPHA301/2017/08/"
                },
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T104900.000Z",
                  "ext": ".dat",
                  "filename": "TRHPHA301_10.31.8.10_2101_20170822T1049_UTC.dat",
                  "rd": "RS03INT1-MJ03C-10-TRHPHA301",
                  "url": "/RS03INT1/MJ03C/TRHPHA301/2017/08/"
                },
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T105200.000Z",
                  "ext": ".dat",
                  "filename": "TRHPHA301_10.31.8.10_2101_20170822T1052_UTC.dat",
                  "rd": "RS03INT1-MJ03C-10-TRHPHA301",
                  "url": "/RS03INT1/MJ03C/TRHPHA301/2017/08/"
                }
              ],
    """
    debug = False
    debug_trace = False
    debug_details = False
    time = True
    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Specific instruments processed.
        actual_reference_designator = 'RS03INT1-MJ03C-10-TRHPHA301'

        # Create rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator] = None

        # Verify sensor type requested in processed in this function, else return {}.
        sensor_type = filetypes_to_check
        if sensor_type != ['TRHP']:
            return {}

        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        if debug: print '\n debug -- Entered _compile_rds_files_TRHP...'
        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Time
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug_trace: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsite for this sensor type.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS03INT1':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    continue
                # Determine if item is a folder link or file
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)
                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:

                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)

                            if detail_subfolders:

                                # Process years
                                for year in detail_subfolders:
                                    #=======================================
                                    # Remove to process all years
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                _get_subfolder_list(month_url,
                                                                                    filetypes=filetypes_to_check,
                                                                                    extensions=extensions_to_check)
                                            if not days_file_list:
                                                continue
                                            date_part = None
                                            for filename in days_file_list:
                                                if debug: print '\n debug ------------ Processing filename: ', filename
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break
                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if rds_base_url in _url:
                                                    _url = _url.replace(rds_base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Update rds_nav_urls for sensor.
                                                work_nav_urls[actual_reference_designator] = rds_base_url + nav_url

                                                # Custom for instrument
                                                ref_des = actual_reference_designator

                                                # Build cache dictionary entry
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])
                                                tmp_item['rd'] = ref_des

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'TRHP')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# 12000 MASSP. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_MASSP(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server for MASSP Mass Spectrometer.


    ['MASSPA101_10.33.7.6_4003_20171202T0211_UTC.dat',
     'MASSPA101_10.33.7.6_4003_20171203T0000_UTC.dat',

    Example where dat exists (2 instruments):
    https://rawdata.oceanobservatories.org/files/RS03INT1/MJ03C/MASSPA301/2017/08/
    https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/MASSPA101/2017/08/

    Cache is build out using ACTUAL REFERENCE DESIGNATOR:
    {
      "rds_MASSP": {
        "RS01SUM2-MJ01B-06-MASSPA101": {
          "2017": {
            "08": {
              "10": [
                {
                  "date": "2017-08-10",
                  "datetime": "20170810T223100.000Z",
                  "ext": ".dat",
                  "filename": "MASSPA101_10.33.7.6_4003_20170810T2231_UTC.dat",
                  "rd": "RS01SUM2-MJ01B-06-MASSPA101",
                  "url": "/RS01SUM2/MJ01B/MASSPA101/2017/08/"
                }
              ],
              "11": [
                {
                  "date": "2017-08-11",
                  "datetime": "20170811T233700.000Z",
                  "ext": ".dat",
                  "filename": "MASSPA101_10.33.7.6_4003_20170811T2337_UTC.dat",
                  "rd": "RS01SUM2-MJ01B-06-MASSPA101",
                  "url": "/RS01SUM2/MJ01B/MASSPA101/2017/08/"
                }
              ],

    """
    debug = False
    debug_trace = False
    debug_details = False
    time = True

    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Specific instruments processed.
        actual_reference_designator_SUM2 = 'RS01SUM2-MJ01B-06-MASSPA101'
        actual_reference_designator_INT1 = 'RS03INT1-MJ03C-06-MASSPA301'

        # Get rds_nav_urls cache.
        rds_base_url = get_rds_base_url()

        # Create  rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator_SUM2] = None
        work_nav_urls[actual_reference_designator_INT1] = None

        # Verify sensor type requested in processed in this function, else return {}.
        sensor_type = filetypes_to_check
        if sensor_type != ['MASSP']:
            return {}
        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        if debug: print '\n debug -- Entered _compile_rds_files_MASSP...'
        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Time
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug_trace: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsites for this sensor type.
            rd = s.attrs['href']
            #process = False
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS03INT1' and subsite != 'RS01SUM2':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    continue
                # Determine if item is a folder link or file
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)
                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:

                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)
                            if detail_subfolders:
                                # Process years
                                for year in detail_subfolders:
                                    #=======================================
                                    # Remove to process all years
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                _get_subfolder_list(month_url,
                                                                                    filetypes=filetypes_to_check,
                                                                                    extensions=extensions_to_check)
                                            if not days_file_list:
                                                continue

                                            date_part = None
                                            for filename in days_file_list:
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                sensor, junk = filename.split('_', 1)
                                                node = item.rstrip('/')
                                                ref_des = '-'.join([subsite, node, sensor])

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break

                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if rds_base_url in _url:
                                                    _url = _url.replace(rds_base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Custom for sensor.
                                                if 'INT1' in subsite:
                                                    actual_reference_designator = actual_reference_designator_INT1
                                                    work_nav_urls[actual_reference_designator_INT1] = rds_base_url + nav_url
                                                elif 'SUM2' in subsite:
                                                    actual_reference_designator = actual_reference_designator_SUM2
                                                    work_nav_urls[actual_reference_designator_SUM2] = rds_base_url + nav_url
                                                else:
                                                    continue
                                                ref_des = actual_reference_designator
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])
                                                tmp_item['rd'] = ref_des

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'MASSP')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# 12000 PPSDN. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_PPS(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server for Particulate DNA Sampler (RS03INT1-MJ03C-07-PPSDNA301)

    Note suffix to RASFLA301_PPS in path and not actual reference designator for sensor.

    Example where dat exists:
    https://rawdata.oceanobservatories.org/files/RS03INT1/MJ03C/RASFLA301_PPS/2017/08/

    ['RASFLA301_PPS_10.31.8.7_4003_20180101T0003_UTC.dat',
    'RASFLA301_PPS_10.31.8.7_4003_20180102T0000_UTC.dat',
    ...]

    Cache is build out using ACTUAL REFERENCE DESIGNATOR:
    {
      "rds_PPS": {
        "RS03INT1-MJ03C-07-PPSDNA301": {
          "2017": {
            "08": {
              "22": [
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T100600.000Z",
                  "ext": ".dat",
                  "filename": "RASFLA301_PPS_10.31.8.7_4003_20170822T1006_UTC.dat",
                  "rd": "RS03INT1-MJ03C-07-PPSDNA301",
                  "url": "/RS03INT1/MJ03C/RASFLA301_PPS/2017/08/"
                },
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T103600.000Z",
                  "ext": ".dat",
                  "filename": "RASFLA301_PPS_10.31.8.7_4003_20170822T1036_UTC.dat",
                  "rd": "RS03INT1-MJ03C-07-PPSDNA301",
                  "url": "/RS03INT1/MJ03C/RASFLA301_PPS/2017/08/"
                }, ...

    """
    debug = False
    debug_trace = False
    debug_details = False
    time = True
    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Specific instruments processed.
        actual_reference_designator = 'RS03INT1-MJ03C-07-PPSDNA301'

        # Verify sensor type requested in processed in this function, else return {}.
        sensor_type = filetypes_to_check
        if sensor_type != ['PPS']:
            return {}

        # Create rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator] = None

        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        # Timing
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        for s in ss_reduced:
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsite for this sensor type.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS03INT1':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    continue
                # Determine if item is a folder link or file
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)
                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:

                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)
                            if detail_subfolders:
                                # Process years
                                for year in detail_subfolders:
                                    #=======================================
                                    # Remove to process all years
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:

                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                    _get_subfolder_list(month_url,
                                                                                        filetypes=filetypes_to_check,
                                                                                        extensions=extensions_to_check)
                                            if not days_file_list:
                                                continue

                                            # Process filenames.
                                            date_part = None
                                            for filename in days_file_list:
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break

                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if rds_base_url in _url:
                                                    _url = _url.replace(rds_base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Custom for sensor
                                                tmp_item['rd'] = actual_reference_designator

                                                # Update rds_nav_urls for sensor.
                                                work_nav_urls[actual_reference_designator] = rds_base_url + nav_url

                                                ref_des = actual_reference_designator
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'PPS')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# 12000 RAS. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_RAS(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server for Hydrothermal Vent Fluid Interactive Sampler (RS03INT1-MJ03C-07-RASFLA301)

    Note suffix to RASFLA301_RAS in path and not actual reference designator for sensor.

    Example where dat exists, for RASFL, TWO links permitted and _PPS blocked (PPSDN):
    https://rawdata.oceanobservatories.org/files/RS03INT1/MJ03C/RASFLA301_RAS/2017/08/
    https://rawdata.oceanobservatories.org/files/RS03INT1/MJ03C/RASFLA301_D1000/2017/08/

    ['RASFLA301_PPS_10.31.8.7_4003_20180101T0003_UTC.dat',
    'RASFLA301_PPS_10.31.8.7_4003_20180102T0000_UTC.dat',
    ...]

    Cache is build out using ACTUAL REFERENCE DESIGNATOR - RS03INT1-MJ03C-07-RASFLA301
    {
      "rds_RAS": {
        "RS03INT1-MJ03C-07-RASFLA301": {
          "2017": {
            "08": {
              "22": [
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T100600.000Z",
                  "ext": ".dat",
                  "filename": "RASFLA301_RAS_10.31.8.7_4001_20170822T1006_UTC.dat",
                  "rd": "RS03INT1-MJ03C-07-RASFLA301",
                  "url": "/RS03INT1/MJ03C/RASFLA301_RAS/2017/08/"
                },
                {
                  "date": "2017-08-22",
                  "datetime": "20170822T103600.000Z",
                  "ext": ".dat",
                  "filename": "RASFLA301_RAS_10.31.8.7_4001_20170822T1036_UTC.dat",
                  "rd": "RS03INT1-MJ03C-07-RASFLA301",
                  "url": "/RS03INT1/MJ03C/RASFLA301_RAS/2017/08/"
                },
    """
    debug = False
    debug_trace = False
    debug_details = False
    time = True
    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Specific instruments processed.
        actual_reference_designator = 'RS03INT1-MJ03C-07-RASFLA301'

        # Verify sensor type requested in processed in this function, else return {}.
        sensor_type = filetypes_to_check
        if sensor_type != ['RAS']:
            return {}
        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        # Create  rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator] = None

        if debug: print '\n debug -- Entered _compile_rds_files_RAS...'
        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes


        # Timing
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug_trace: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            #-----------------------------------------------
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsite for this sensor type.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS03INT1':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    continue
                # Determine if item is a folder link or file
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)

                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:

                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                # Remove PPSDN information being reported for RASFL; permit D1000, etc.
                                if check in node_item and '_PPS' not in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================

                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)

                            if detail_subfolders:

                                # Process years
                                for year in detail_subfolders:

                                    #=======================================
                                    # Remove to process all years
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                _get_subfolder_list(month_url,
                                                                                    filetypes=filetypes_to_check,
                                                                                    extensions=extensions_to_check)
                                            if not days_file_list:
                                                continue

                                            """
                                            ['RASFLA301_PPS_10.31.8.7_4003_20180101T0003_UTC.dat',
                                             'RASFLA301_PPS_10.31.8.7_4003_20180102T0000_UTC.dat',
                                            """
                                            date_part = None
                                            for filename in days_file_list:
                                                if debug: print '\n debug ------------ Processing filename: ', filename
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break
                                                #if ext == '.dat':
                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]
                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if rds_base_url in _url:
                                                    _url = _url.replace(rds_base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}
                                                # Update rds_nav_urls for sensor.
                                                work_nav_urls[actual_reference_designator] = rds_base_url + nav_url
                                                ref_des = actual_reference_designator
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])

                                                # Custom for sensor.
                                                tmp_item['rd'] = actual_reference_designator

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'RAS')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# 12000 PREST. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_PREST(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server for Tidal Seafloor Pressure, three instruments:
        RS01SLBS-MJ01A-06-PRESTA101, RS01SUM1-LJ01B-09-PRESTB102, RS03AXBS-MJ03A-06-PRESTA301

    Example where dat exists, 3 instruments:
    https://rawdata.oceanobservatories.org/files/RS01SUM1/MJ01A/PRESTA101/2017/08/
    https://rawdata.oceanobservatories.org/files/RS01SUM1/LJ01B/PRESTB102/2017/08/
    https://rawdata.oceanobservatories.org/files/RS03AXBS/MJ03A/PRESTA301/2017/08/

    Cache is build out:
    {
      "rds_PREST": {
        "RS01SLBS-MJ01A-06-PRESTA101": {
          "2018": {
            "01": {
              "02": [
                {
                  "date": "2018-01-02",
                  "datetime": "20180102T232600.000Z",
                  "ext": ".dat",
                  "filename": "PRESTA101_10.33.2.6_2101_20180102T2326_UTC.dat",
                  "rd": "RS01SLBS-MJ01A-06-PRESTA101",
                  "url": "/RS01SLBS/MJ01A/PRESTA101/2018/01/"
                }
              ],
              "03": [
                {
                  "date": "2018-01-03",
                  "datetime": "20180103T000000.000Z",
                  "ext": ".dat",
                  "filename": "PRESTA101_10.33.2.6_2101_20180103T0000_UTC.dat",
                  "rd": "RS01SLBS-MJ01A-06-PRESTA101",
                  "url": "/RS01SLBS/MJ01A/PRESTA101/2018/01/"
                }
              ],
    """
    debug = False
    debug_trace = False
    debug_details = False
    time = True


    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Specific instruments processed.
        # RS01SLBS-MJ01A-06-PRESTA101, RS01SUM1-LJ01B-09-PRESTB102, RS03AXBS-MJ03A-06-PRESTA301
        actual_reference_designator_SLBS = 'RS01SLBS-MJ01A-06-PRESTA101'
        actual_reference_designator_SUM1 = 'RS01SUM1-LJ01B-09-PRESTB102'
        actual_reference_designator_AXBS = 'RS03AXBS-MJ03A-06-PRESTA301'

        # Create  rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator_SLBS] = None
        work_nav_urls[actual_reference_designator_SUM1] = None
        work_nav_urls[actual_reference_designator_AXBS] = None

        sensor_type = filetypes_to_check
        if sensor_type != ['PREST']:
            return {}

        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug_trace: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            #-----------------------------------------------
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsites for this sensor type.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS01SUM1' and subsite != 'RS01SLBS' and subsite != 'RS03AXBS':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    continue
                # Determine if item is a folder link or file
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)

                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:
                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)
                            if detail_subfolders:

                                # Process years
                                for year in detail_subfolders:

                                    #=======================================
                                    # Remove to process all years
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                    _get_subfolder_list(month_url,
                                                                                        filetypes=filetypes_to_check,
                                                                                        extensions=extensions_to_check)
                                            if not days_file_list:
                                                continue

                                            date_part = None
                                            for filename in days_file_list:
                                                if debug: print '\n debug ------------ Processing filename: ', filename
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break

                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if base_url in _url:
                                                    _url = _url.replace(base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Determine which reference designator, custom for sensor. Add nav_url.
                                                if 'SLBS' in subsite:
                                                    actual_reference_designator = actual_reference_designator_SLBS
                                                    work_nav_urls[actual_reference_designator_SLBS] = rds_base_url + nav_url
                                                elif 'SUM1' in subsite:
                                                    actual_reference_designator = actual_reference_designator_SUM1
                                                    work_nav_urls[actual_reference_designator_SUM1] = rds_base_url + nav_url
                                                elif 'AXBS' in subsite:
                                                    actual_reference_designator = actual_reference_designator_AXBS
                                                    work_nav_urls[actual_reference_designator_AXBS] = rds_base_url + nav_url
                                                else:
                                                    continue

                                                # Build out cache dictionary.
                                                ref_des = actual_reference_designator
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])

                                                # Custom for sensor.
                                                tmp_item['rd'] = ref_des

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'PREST')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


#===================================================================================
# 12000 FLOBN. Compile FLOBN information from raw data server. (Used in tasks.)
def _compile_rds_files_FLOBN():
    """ Get indexed information from raw data server for FLOBN instruments only. Benthic Fluid Flow

    Example where data exists for non-standard folder structure of FLOBN data:
    Deviations from standard folder structures:
        1. Sensor folder does not contain port '##-FLOBNC101'
        2. First subfolder is YYY_deployment rather than YY
        3. Second subfolders are 'metadata' and 'results', not a list of months.
        4. No days provided as subfolders.
        5. File naming conventions in metadat and results folder differ in the same folder (i.e. not consistent)

    https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/FLOBNC101/2013_deployment/metadata/
    https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/FLOBNC101/2013_deployment/results/

    File extensions: file extensions - '.jpg', '.pdf', '.xlsx'
    Cache build out:
    {
      "rds_FLOBN": {
        "RS01SUM2-MJ01B-00-FLOBNC101": {
          "2013": {
            "07": {
              "17": [
                {
                  "date": "2013-07-17",
                  "datetime": "20130717T180923.000Z",
                  "ext": ".jpg",
                  "filename": "FLOBNC101_20130717T180923_UTC_Image_ver_1-00.jpg",
                  "rd": "RS01SUM2-MJ01B-00-FLOBNC101",
                  "url": "/RS01SUM2/MJ01B/FLOBNC101/2013_deployment/metadata/"
                },
                {
                  "date": "2013-07-17",
                  "datetime": "20130717T181529.000Z",
                  "ext": ".jpg",
                  "filename": "FLOBNC101_20130717T181529_UTC_Image_ver_1-00.jpg",
                  "rd": "RS01SUM2-MJ01B-00-FLOBNC101",
                  "url": "/RS01SUM2/MJ01B/FLOBNC101/2013_deployment/metadata/"
                },
    """
    debug = False
    debug_trace = False
    debug_details = False
    time = True

    try:
        # Local variables.
        sensor_type = ['FLOBN']
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()
        subfolder_level_1 = '_deployment'
        subfolder_level_2 = ['metadata', 'results']
        supported_platforms = ['RS01SUM2']

        # Specific instruments processed.
        reference_desinator_FLOBNC = 'RS01SUM2-MJ01B-00-FLOBNC101'
        reference_desinator_FLOBNM = 'RS01SUM2-MJ01B-00-FLOBNM101'

        # Create  rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[reference_desinator_FLOBNC] = None
        work_nav_urls[reference_desinator_FLOBNM] = None

        # Filters to limit processing.
        array_codes = rds_get_supported_array_codes()

        # Currently FLOBN sensors only available for cabled array.
        if 'RS' not in array_codes:
            return {}
        years_processed = rds_get_supported_years()
        filetypes_to_check = ['FLOBN']
        extensions_to_check = get_extensions_by_sensor_type('FLOBN')

        if time:
            print '\n    Compiling FLOBN files from raw data server'
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check

        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug_trace: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            #-----------------------------------------------
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsites for this sensor type.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS01SUM2':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url, None)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - Node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                # Determine if item is a folder link or file
                if len(item) != 6:
                    continue
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url, None)

                    # Level 3 - processing sensor information
                    if node_subfolders:
                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url, None)

                            if detail_subfolders:
                                # FLOBN folder structure rule check
                                found_level_1_folder = False
                                folder_year = None
                                for folder_check in detail_subfolders:
                                    str_folder_check = str(folder_check)
                                    if subfolder_level_1 in str_folder_check:
                                        folder_year = str_folder_check.replace(subfolder_level_1, '')
                                        folder_year = folder_year.rstrip('/')
                                        found_level_1_folder = True
                                    else:
                                        continue

                                if not found_level_1_folder or folder_year is None:
                                    if debug:
                                        print '\n debug -- Unable to locate level key, or folder year is None; continue'
                                    continue

                                # Process years (detail_subfolders is years)
                                for year in detail_subfolders:      # 'YYYY_deployment'

                                    if debug:
                                        print '\n debug -- Processing \'YYYY_deployment\' in detail_subfolders...%r' % year
                                    # FLOBN folder structure rule check
                                    if subfolder_level_1 not in year:
                                        if debug: print '\n debug -- Unable to locate %s in year: %s, continue' % \
                                                        (subfolder_level_1, year)
                                        continue
                                    folder_year = year.replace(subfolder_level_1,'')

                                    #=======================================
                                    # Remove to process all years
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                    _get_subfolder_list(month_url,
                                                                                        filetypes=filetypes_to_check,
                                                                                        extensions=extensions_to_check)

                                            if not days_file_list:
                                                continue

                                            for filename in days_file_list:
                                                if debug: print '\n debug ------------ Processing filename: ', filename


                                                # Process file datetime based on extension.
                                                sensor, _dt, junk = filename.split('_', 2)
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break
                                                if ext == '.jpg':
                                                    dt = _dt + '.000Z'
                                                elif ext in ['.pdf', '.xlsx']:
                                                    dt = _dt + 'T000000.000Z'
                                                else:
                                                    continue

                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if base_url in _url:
                                                    _url = _url.replace(base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                if 'FLOBNC' in node_item:
                                                    actual_reference_designator = reference_desinator_FLOBNC
                                                    work_nav_urls[reference_desinator_FLOBNC] = rds_base_url + nav_url
                                                elif 'FLOBNM' in node_item:
                                                    actual_reference_designator = reference_desinator_FLOBNM
                                                    work_nav_urls[reference_desinator_FLOBNM] = rds_base_url + nav_url
                                                else:
                                                    continue

                                                ref_des = actual_reference_designator
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])
                                                tmp_item['rd'] = ref_des

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)


                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile rds files FLOBN: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'FLOBN')

        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())
        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in large_format cache(%d): %s' % (len(data_dict), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# 12000 HPIES. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_HPIES(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server for HPIES, Horizontal Electric Field, Pressure,
        and Inverted Echo Sounder, two instruments:
            RS01SLBS-LJ01A-05-HPIESA101, RS03AXBS-LJ03A-05-HPIESA301

    Example where dat exists, 2 instruments:
    https://rawdata.oceanobservatories.org/files/RS01SLBS/LJ01A/HPIESA101/2017/08/
    https://rawdata.oceanobservatories.org/files/RS03AXBS/LJ03A/HPIESA301/2017/08/

    Cache is build out:
    {
      "rds_HPIES": {
        "RS01SLBS-LJ01A-05-HPIESA101": {
          "2017": {
            "07": {
              "29": [
                {
                  "date": "2017-07-29",
                  "datetime": "20170729T190600.000Z",
                  "ext": ".dat",
                  "filename": "HPIESA101_10.33.5.5_2101_20170729T1906_UTC.dat",
                  "rd": "RS01SLBS-LJ01A-05-HPIESA101",
                  "url": "/RS01SLBS/LJ01A/HPIESA101/2017/07/"
                }
              ],
              "30": [
                {
                  "date": "2017-07-30",
                  "datetime": "20170730T000000.000Z",
                  "ext": ".dat",
                  "filename": "HPIESA101_10.33.5.5_2101_20170730T0000_UTC.dat",
                  "rd": "RS01SLBS-LJ01A-05-HPIESA101",
                  "url": "/RS01SLBS/LJ01A/HPIESA101/2017/07/"
                }
              ],
              "31": [
                {
                  "date": "2017-07-31",
                  "datetime": "20170731T000000.000Z",
                  "ext": ".dat",
                  "filename": "HPIESA101_10.33.5.5_2101_20170731T0000_UTC.dat",
                  "rd": "RS01SLBS-LJ01A-05-HPIESA101",
                  "url": "/RS01SLBS/LJ01A/HPIESA101/2017/07/"
                }
              ]

    """
    debug = False
    debug_details = False
    time = True
    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Specific instruments processed.
        # Reference designators for instruments: RS01SLBS-LJ01A-05-HPIESA101, RS03AXBS-LJ03A-05-HPIESA301
        actual_reference_designator_SLBS = 'RS01SLBS-LJ01A-05-HPIESA101'
        actual_reference_designator_AXBS = 'RS03AXBS-LJ03A-05-HPIESA301'

        # Create  rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator_SLBS] = None
        work_nav_urls[actual_reference_designator_AXBS] = None

        sensor_type = filetypes_to_check
        if sensor_type != ['HPIES']:
            return {}

        if debug: print '\n debug -- Entered _compile_rds_files_HPIES...'
        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        # Timing
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        for s in ss_reduced:
            #-----------------------------------------------
            # Limit to those arrays identified in array_codes, not processing platforms at this time
            # Lock down to specific subsites for this sensor type.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS01SLBS' and subsite != 'RS03AXBS':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    continue

                # HPIES specific test.
                if 'LJ01A' not in item and 'LJ03A' not in item:
                    continue

                # Determine if item is a folder link or file
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)
                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:

                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)
                            if detail_subfolders:

                                # Process years
                                for year in detail_subfolders:

                                    #=======================================
                                    # Remove to process all years
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                    _get_subfolder_list(month_url,
                                                                                        filetypes=filetypes_to_check,
                                                                                        extensions=extensions_to_check)

                                            if not days_file_list:
                                                continue

                                            date_part = None
                                            for filename in days_file_list:
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break
                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if base_url in _url:
                                                    _url = _url.replace(base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Determine which reference designator, custom for sensor.
                                                if 'SLBS' in subsite:
                                                    actual_reference_designator = actual_reference_designator_SLBS
                                                    work_nav_urls[actual_reference_designator_SLBS] = rds_base_url + nav_url
                                                elif 'AXBS' in subsite:
                                                    actual_reference_designator = actual_reference_designator_AXBS
                                                    work_nav_urls[actual_reference_designator_AXBS] = rds_base_url + nav_url
                                                else:
                                                    continue

                                                # Build out cache dictionary.
                                                tmp_item['rd'] = actual_reference_designator
                                                ref_des = actual_reference_designator
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'HPIES')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# 12000 TMPSF. Compile rds caches by specific sensor from raw data server..
def _compile_rds_files_TMPSF(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server for Diffuse Vent Fluid 3-D Temperature Array (TMPSF):
            RS03ASHS-MJ03B-07-TMPSFA301

    Example where dat exists:
    https://rawdata.oceanobservatories.org/files/RS03ASHS/MJ03B/TMPSFA301/2017/08/

    Cache is build out:
    {
      "rds_TMPSF": {
        "RS03ASHS-MJ03B-07-TMPSFA301": {
          "2017": {
            "08": {
              "15": [
                {
                  "date": "2017-08-15",
                  "datetime": "20170815T000700.000Z",
                  "ext": ".dat",
                  "filename": "TMPSFA301_10.31.7.7_2101_20170815T0007_UTC.dat",
                  "rd": "RS03ASHS-MJ03B-07-TMPSFA301",
                  "url": "/RS03ASHS/MJ03B/TMPSFA301/2017/08/"
                }
              ],
              "16": [
                {
                  "date": "2017-08-16",
                  "datetime": "20170816T000000.000Z",
                  "ext": ".dat",
                  "filename": "TMPSFA301_10.31.7.7_2101_20170816T0000_UTC.dat",
                  "rd": "RS03ASHS-MJ03B-07-TMPSFA301",
                  "url": "/RS03ASHS/MJ03B/TMPSFA301/2017/08/"
                }
              ],
    """
    debug = False
    debug_trace = False
    debug_details = False
    time = True
    try:
        # Local variables.
        rds_base_url = get_rds_base_url()
        base_url = rds_base_url + '/'
        timeout, timeout_read = get_uframe_timeout_info()

        # Reference designator for instrument.
        actual_reference_designator = 'RS03ASHS-MJ03B-07-TMPSFA301'

        # Create  rds navigation urls.
        work_nav_urls = {}
        work_nav_urls[actual_reference_designator] = None

        # Used during processing of various file extension values.
        sensor_type = filetypes_to_check
        if sensor_type != ['TMPSF']:
            return {}

        if debug: print '\n debug -- Entered _compile_rds_files_TMPSF...'
        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get and process returned content for links.
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        data_dict = {}

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug_trace: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            #-----------------------------------------------
            # Limit to those arrays identified in array_codes.
            rd = s.attrs['href']
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite != 'RS03ASHS':
                        continue
                else:
                    continue

            #-----------------------------------------------
            # Level 1 - subsite processing
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    continue

                # Sensor specific test.
                if 'MJ03B' not in item:
                    continue

                # Determine if item is a folder link or file
                if '/' in item:
                    subfolder_url = base_url + rd + item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)
                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:

                        for node_item in node_subfolders:
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if check in node_item:
                                    ok_to_go = True
                                    break
                            if not ok_to_go:
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            nav_url = '/' + node_folder_url.replace(base_url, '')
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)
                            if detail_subfolders:
                                # Process years
                                for year in detail_subfolders:
                                    # Check year before processing.
                                    folder_year = year
                                    year_tmp = folder_year.rstrip('/')
                                    if year_tmp not in years_processed:
                                        continue
                                    year_url = node_folder_url + year
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            days_subfolders, days_file_list = \
                                                                _get_subfolder_list(month_url,
                                                                        filetypes=filetypes_to_check,
                                                                        extensions=extensions_to_check)

                                            if not days_file_list:
                                                continue

                                            date_part = None
                                            for filename in days_file_list:
                                                if debug: print '\n debug ------------ Processing filename: ', filename
                                                if '_UTC.dat' in filename:
                                                    tmp_filename = filename.replace('_UTC.dat', '')
                                                    junk_part, date_part = tmp_filename.rsplit('_', 1)

                                                # Process date_part (i.e. 20170815T1927)
                                                if date_part is None:
                                                    continue
                                                _dt = date_part

                                                # Process file datetime based on extension.
                                                ext = None
                                                for extension in extensions_to_check:
                                                    if extension in filename:
                                                        ext = extension
                                                        break
                                                dt = _dt + '00.000Z'
                                                _year = _dt[0:4]
                                                _month = _dt[4:6]
                                                _day = _dt[6:8]

                                                _url = urllib.unquote(month_url).decode('utf8')
                                                if base_url in _url:
                                                    _url = _url.replace(base_url, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Add date to item
                                                _year = _year.rstrip('/')
                                                _month = _month.rstrip('/')
                                                _day = _day.rstrip('/')
                                                tmp_item['date'] = '-'.join([_year, _month, _day])

                                                # Custom for sensor.
                                                tmp_item['rd'] = actual_reference_designator

                                                # Update rds_nav_urls for sensor.
                                                work_nav_urls[actual_reference_designator] = rds_base_url + nav_url

                                                # Build out cache dictionary.
                                                ref_des = actual_reference_designator
                                                if ref_des not in data_dict:
                                                    data_dict[str(ref_des)] = {}
                                                if _year not in data_dict[ref_des]:
                                                    data_dict[ref_des][_year] = {}
                                                if _month not in data_dict[ref_des][_year]:
                                                    data_dict[ref_des][_year][_month] = {}
                                                if _day not in data_dict[ref_des][_year][_month]:
                                                    data_dict[ref_des][_year][_month][_day] = []

                                                # Add item for cache dictionary.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)

                else:
                    # Item is not a folder
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'TMPSF')

        # Populate cache for sensor type.
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in %s cache(%d): %s' % (cache_destination, len(result_keys), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)
