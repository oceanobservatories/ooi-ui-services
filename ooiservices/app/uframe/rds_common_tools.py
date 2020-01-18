#!/usr/bin/env python

"""
Support for rds data gathering functions for specific sensors.
"""
__author__ = 'Edna Donoughe'


from flask import current_app
from bs4 import BeautifulSoup

from ooiservices.app import cache
from ooiservices.app.uframe.config import get_cache_timeout
from ooiservices.app.uframe.common_tools import (rds_get_supported_folder_types, get_valid_extensions)
from ooiservices.app.uframe.config import (get_uframe_timeout_info, get_image_camera_store_url_base)

import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)


def get_target_cache_by_sensor_type(sensor_type):
    try:
        cache_root = 'rds_'
        sensor = sensor_type[0].replace('-', '')
        target_cache = cache_root + sensor
        return target_cache
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def add_nav_urls_to_cache(work_nav_urls, sensor_type):
    debug = False
    try:
        if debug: print '\n debug -- work_nav_urls: ', json.dumps(work_nav_urls, indent=4, sort_keys=True)
        cache_name = 'rds_nav_urls'
        cache_data = cache.get(cache_name)
        if cache_data:
            if debug: print '\n Have rds_nav_urls cache data...'
            if sensor_type not in cache_data:
                cache_data[sensor_type] = work_nav_urls
            else:
                some_nav_cache_data = cache_data[sensor_type]
                for k, v in work_nav_urls.iteritems():
                    some_nav_cache_data[k] = v

            cache.set(cache_name, cache_data, timeout=get_cache_timeout())
        else:
            if debug: print '\n MAKE rds_nav_urls cache data...'
            rds_nav_urls = {'OSMOI': work_nav_urls}
            cache.set(cache_name, rds_nav_urls, timeout=get_cache_timeout())
        return
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _compile_rds_files_OSMOI: ', message
        current_app.logger.info(message)
        raise Exception(message)


# Get subfolder contents and file_list for folder.
def _get_subfolder_list(url, filetypes=None, extensions=None):
    """ Get url folder content and process the list of data links.
    """
    debug = False
    debug_summary = False


    if debug:
        print '\n\t debug -- Entered _get_subfolder_list...'
        print '\n\t debug -- filetypes: ', filetypes
        print '\n\t debug -- extensions: ', extensions
    base_url = None
    try:
        """
        # Master/complete list
        filetypes_to_check = ['HY', 'ZPL', 'CAMDS', 'CAMHD', 'OBS']
        extensions_to_check = ['.png', '.raw', '.mseed', '.mp4', '.mov']
        """
        #subfolder_filestypes = ['HYD', 'ZPL', 'OBS', 'CAMDS', 'CAMHD']
        #subfolder_extensions = ['.mseed', '.png', '.raw', '.mp4', '.mov']
        # Set filetypes and extensions to check.
        if filetypes is None:
            filetypes_to_check = rds_get_supported_folder_types()
            #filetypes_to_check = ['CAMDS']
            #filetypes_to_check = ['HY', 'ZPL', 'CAMDS', 'CAMHD', 'OBS']
        else:
            filetypes_to_check = filetypes

        if extensions is None:
            extensions_to_check = get_valid_extensions()
            #extensions_to_check = ['.png']
            #extensions_to_check = ['.png', '.raw', '.mseed', '.mp4', '.mov']
        else:
            extensions_to_check = extensions

        #print '\n debug -- extensions being checked: ', extensions_to_check
        # base_url is used for exception messages only (timeout or connection errors)
        base_url = get_image_camera_store_url_base()

        if debug:
            print '\n\t debug ==========================================='
            print '\n\t debug -- filetypes_to_check: ', filetypes_to_check
            print '\n\t debug -- extensions_to_check: ', extensions_to_check
        timeout, timeout_read = get_uframe_timeout_info()
        extended_timeout_read = timeout_read * 10
        r = requests.get(url, timeout=(timeout, extended_timeout_read))
        if debug: print '\n debug -- r.status_code: ', r.status_code
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        if debug: print '\n debug -- len(ss): ', len(ss)
        #url_list = []
        subfolders = []
        file_list = []
        for s in ss:
            if 'href' in s.attrs:
                if debug: print ' (1) s.attrs[href]: %r' % s.attrs['href']
                if ';' in s.attrs['href'] or 'files' in s.attrs['href'] or '=' in s.attrs['href']:
                    if debug: print '\n debug -- s.attrs[href] has ; or files or = ....so continue...'
                    continue

                if ';' not in s.attrs['href'] and 'files' not in s.attrs['href'] and '=' not in s.attrs['href']:

                    # Is it a folder?
                    if ('/' in s.attrs['href']) and ('./' not in s.attrs['href']):
                        if debug:
                            print '\n debug -- folder...'
                            print '\n debug -- s.attrs[href]): ', s.attrs['href']
                        subfolders.append(s.attrs['href'])
                        if debug: print '\n debug -- After append to subfolders...'

                    # Process as a file...
                    else:
                        if debug: print '\n debug -- in the else branch...'
                        working_attrs = (str(s.attrs['href']))[:]
                        if debug: print '\n debug -- working_attrs: ', working_attrs
                        if './' in working_attrs:
                            working_attrs = working_attrs.replace('./', '')
                            if debug: print '\t debug -- file (corrected): ', working_attrs

                        if debug: print '\n debug -- filter by filetype...'
                        # Filter by file type.
                        good_filetype = False
                        for filetype in filetypes_to_check:
                            if debug: print '\n debug -- ****** Checking filetype: ', filetype
                            if filetype in working_attrs:
                                if debug: print '\n debug -- Good filetype: %s in %s' % (filetype, working_attrs)
                                good_filetype = True
                                break
                            else:
                                if debug: print '\n Bad filetype %s in %s' % (filetype, working_attrs)
                                continue
                        if not good_filetype:
                            continue
                        if debug: print '\t debug -- Ok filetype: ', working_attrs

                        # Filter by file extension.
                        for ext in extensions_to_check:
                            #print '\n debug -- Checking ext %s...' % ext
                            #print '\n s.attrs[href]: ', s.attrs['href']
                            if ext in s.attrs['href']:
                                if working_attrs not in file_list and working_attrs and working_attrs is not None:
                                    file_list.append(working_attrs)
                                    break
        if debug_summary:
            if file_list:
                print '\n Returning a file list: ', file_list
                print '\n Returning subfolders: ', subfolders
        return subfolders, file_list

    except ConnectionError:
        message = 'ConnectionError getting data files for: %s' % url.replace(base_url, '/')
        print '\t** %s' % message
        return [], []
    except Timeout:
        message = 'Timeout getting data files, url: %s' % url.replace(base_url, '/')
        print '\t** %s' % message
        return [], []
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _get_subfolder_list...', message
        current_app.logger.info(message)
        return [], []

