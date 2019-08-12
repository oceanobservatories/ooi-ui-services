#!/usr/bin/env python

"""
Support for image interface, functions utilized for image information.
"""
__author__ = 'Edna Donoughe'


from flask import current_app
from bs4 import BeautifulSoup
import urllib
import os.path
from datetime import datetime
import PIL
from PIL import Image
from PIL import ImageFile
from StringIO import StringIO
import json

from ooiservices.app import cache
from ooiservices.app.uframe.config import get_cache_timeout
from ooiservices.app.uframe.common_tools import (get_image_thumbnail_route, rds_get_supported_years,
                                                 rds_get_supported_array_codes, rds_get_all_supported_sensor_types,
                                                 get_extensions_by_sensor_type, get_valid_extensions,
                                                 get_supported_folder_types, rds_get_nonstandard_sensor_types)
from ooiservices.app.uframe.config import (get_uframe_timeout_info, get_image_camera_store_url_base,
                                           get_image_store_url_base)
from ooiservices.app.uframe.config import get_rds_base_url
from ooiservices.app.uframe.rds_common_tools import (get_target_cache_by_sensor_type, _get_subfolder_list,
                                                     add_nav_urls_to_cache)
from ooiservices.app.uframe.rds_tools import (_compile_rds_files_FLOBN, _compile_rds_files_THSP,
                                                  _compile_rds_files_TRHP, _compile_rds_files_MASSP,
                                                  _compile_rds_files_PPS, _compile_rds_files_RAS,
                                                  _compile_rds_files_PREST, _compile_rds_files_HPIES,
                                                  _compile_rds_files_TMPSF)
import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)


# Get existing thumbnails and return dictionary to populate cam_images cache. (This does not build thumbnails).
def _get_cam_images():
    """ Get existing thumbnail images.
    [
    {
      "baseUrl": "/api/uframe/get_cam_image/",
      "date": "2016-01-07",
      "datetime": "20160107T202935.779Z",
      "filename": "CE04OSBP-LV01C-06-CAMDSB106_20160107T202935_779Z_thumbnail.png",
      "reference_designator": "CE04OSBP-LV01C-06-CAMDSB106",
      "thumbnail": "<server_data_folder>/images/CE04OSBP-LV01C-06-CAMDSB106_20160107T202935_779Z_thumbnail.png",
      "url": "https://rawdata.oceanobservatories.org/files/CE04OSBP/LV01C/06-CAMDSB106/2016/01/07/CE04OSBP-LV01C-06-CAMDSB106_20160107T202935,779Z.png.part"
    },
    . . .
    ]

    #===
    process this:
    {
      "data": {
        "CE02SHBP-MJ01C-08-CAMDSB107": {
          "2016": {
            "01": {
              "28": [
                {
                  "date": "2016-01-28",
                  "datetime": "20160128T182249.188Z",
                  "ext": ".png",
                  "filename": "CE02SHBP-MJ01C-08-CAMDSB107_20160128T182249,188.png",
                  "rd": "CE02SHBP-MJ01C-08-CAMDSB107",
                  "url": "/CE02SHBP/MJ01C/08-CAMDSB107/2016/01/28/"
                }
              ]
            },

    Into this for response:
    {
      "cam_images": [
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "date": "2016-09-12",
          "datetime": "20160912T235051.480Z",
          "filename": "CE02SHBP-MJ01C-08-CAMDSB107_20160912T235051_480Z_thumbnail.png",
          "reference_designator": "CE02SHBP-MJ01C-08-CAMDSB107",
          "thumbnail": "<server_data_folder>/images/CE02SHBP-MJ01C-08-CAMDSB107_20160912T235051_480Z_thumbnail.png",
          "url": "https://rawdata.oceanobservatories.org/files//CE02SHBP/MJ01C/08-CAMDSB107/2016/09/12/CE02SHBP-MJ01C-08-CAMDSB107_20160912T235051,480Z.png"
        },
    """
    debug = False
    time = False
    total_count = 0
    image_list = []
    try:

        # Provide time to complete information
        if time: print '\nGet thumbnail images...'
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Configuration or common reference items.
        ui_baseUrl = get_image_thumbnail_route()
        base_url = get_image_camera_store_url_base()
        base_thumbnail = get_image_store_url_base()

        # List of dictionaries from cache inventory associated with png files.
        data_image_list = get_data_image_list()
        if data_image_list is None or not data_image_list:
            message = 'No references returned to process for images.'
            raise Exception(message)
        if data_image_list:
            if debug: print '\n Number of image resources available to process: ', len(data_image_list)

            # Add the images to the to the folder cache.
            completed= []
            for image_item in data_image_list:
                try:
                    ext = None
                    new_filename = None
                    # Get thumbnail file path target.
                    if '.png' in image_item['filename']:
                        ext = '.png'
                        new_filename = image_item['filename'].replace('.png', '_thumbnail.png')
                        #new_filename = image_item['filename'].split('.')[0] + '_thumbnail.png'
                    else:
                        continue

                    # Remove comma and and use underscore.
                    new_filename = new_filename.replace(',', '_')
                    new_filepath = base_thumbnail + '/' + new_filename
                    if debug: print '\n debug -- new_filepath: %s' % new_filepath
                    dt = urllib.unquote(image_item['datetime']).decode('utf8')
                    dt = dt.replace(',', '.')

                    # Form complete url.
                    url = base_url + image_item['url'] + image_item['filename']
                    if debug: print '\n debug -- url: ', url

                    # Check if thumbnail is available, if so added to cam_images response dict.
                    try:
                        #if not os.path.isfile(new_filepath):
                        #    print '\n debug -- NOT found in file system: %s ' % new_filepath
                        if image_item['url'] not in completed and os.path.isfile(new_filepath):
                            item = {'url': url,
                                    'filename': new_filename,
                                    'date': image_item['date'],
                                    'reference_designator': image_item['rd'],
                                    'datetime': dt,
                                    'thumbnail': new_filepath,
                                    'baseUrl': ui_baseUrl}
                            if debug: print '\n debug -- item: ', item
                            image_list.append(item)
                            # Counters
                            total_count += 1
                    except Exception as err:
                        print 'Error getting thumbnail: ', str(err)
                        continue

                except Exception as err:
                    print 'Error: ', str(err)
                    continue

        print '\t-- Number of thumbnail images: ', len(image_list)
        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile camera images: %s' % str(end - start)
            print '\nCompleted getting camera images'
        return image_list

    except ConnectionError:
        message = 'ConnectionError getting image files.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting image files.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _compile_cam_images...', message
        current_app.logger.info(message)
        raise Exception(message)


def get_data_image_list():
    """ Get list of image items (in partitioned cache) for thumbnail processing.

    Processing following content from all partitioned caches supporting .png.:
    {
    "RS01SBPS-PC01A-07-CAMDSC": {
      "2016": {
        "06": {
          "02": [
            {
              "date": "2016-06-02",
              "datetime": "20160602T225757.555Z",
              "filename": "RS01SBPS-PC01A-07-CAMDSC102_20160602T225757,555Z.png",
              "rd": "RS01SBPS-PC01A-07-CAMDSC102",
              "url": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/06/02/RS01SBPS-PC01A-07-CAMDSC102_20160602T225757,555Z.png"
            },
            {
              "date": "2016-06-02",
              "datetime": "20160602T225856.644Z",
              "filename": "RS01SBPS-PC01A-07-CAMDSC102_20160602T225856,644Z.png",
              "rd": "RS01SBPS-PC01A-07-CAMDSC102",
              "url": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/06/02/RS01SBPS-PC01A-07-CAMDSC102_20160602T225856,644Z.png"
            },
            . . .]
    }

    """
    debug = False
    image_list = []
    filter_on_year = True
    years_processed = rds_get_supported_years()
    arrays_processed = rds_get_supported_array_codes()
    try:
        if debug: print '\n debug -- Entered get_data_image_list...'
        sensor_types = get_sensor_types_with_png()
        if not sensor_types:
            message = 'No sensor types returned supporting extension \'.png\'.'
            raise Exception(message)
        if debug: print '\n debug -- Consolidated cache processing for sensor_types: ', sensor_types
        large_format_cache = get_consolidated_cache(sensor_types)
        if not large_format_cache or large_format_cache is None:
            if debug: print '\n debug -- Consolidated cache processing failed to return information.'
            return None
        else:
            rds = large_format_cache.keys()
            if rds:
                rds.sort()
            if debug: print '\n Reference designators in large format index(%d): %s' % (len(rds), rds)

        for rd in rds:
            rd = str(rd)

            if rd[0:2] not in arrays_processed:
                print '\n\t -- Skip processing of %s, not in arrays processed.(%s)' % (rd, arrays_processed)
                continue
            years = large_format_cache[rd].keys()
            #years.sort(reverse=True)
            years.sort()
            if debug: print '\n\t -- Reference designator: %s years: %s' % (rd, years)

            for year in years:
                year = str(year)
                if filter_on_year:
                    if year not in years_processed:
                        continue
                months = large_format_cache[rd][year].keys()
                #if debug: print '\n\t Year %s months: %s' % (year, months)
                months.sort(reverse=True)
                for month in months:
                    month = str(month)
                    days = large_format_cache[rd][year][month].keys()
                    #if debug: print '\n\t Year %s Month %s days: %s' % (year, month, days)
                    days.sort(reverse=True)
                    for day in days:
                        day = str(day)
                        file_list = large_format_cache[rd][year][month][day]
                        #if debug: print '\t -- Year %s Month %s Day %s Total Files: %d' % (year, month, day, len(file_list))
                        count = 0
                        for file in file_list:
                            if file['ext'] == '.png':
                                if file not in image_list:
                                    image_list.append(file)
                                    count += 1
                        #if debug: print '\t -- Year %s Month %s Day %s png/Total Files: %d/%d' % \
                        #                (year, month, day, count, len(file_list))

        if image_list:
            print '\t-- Number of images available: ', len(image_list)
            #image_list.sort(key=lambda x: (x['rd']))
            image_list.sort(key=lambda x: (x['date']), reverse=True)
        return image_list
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception get_data_image_list...', message
        current_app.logger.info(message)
        raise Exception(message)

def get_sensor_types_with_png():
    """
    Review list of all sensor type and based on extensions for each, return list of
    sensor types which support '.png'. Review when adding '.jpg'.
    """
    debug = False
    sensor_types = []
    try:
        all_sensor_types = rds_get_all_supported_sensor_types()
        for check in all_sensor_types:
            extensions = get_extensions_by_sensor_type(check)
            if '.png' in extensions:
                if check not in sensor_types:
                    sensor_types.append(check)
        if debug: print '\n debug -- Sensor types supporting png processing: ', sensor_types
        return sensor_types
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception get_sensor_types_with_png...', message
        current_app.logger.info(message)
        raise Exception(message)


def get_consolidated_cache(sensor_types):
    debug = False
    data = {}
    try:
        if debug: print '\n debug -- Get consolidated cache for sensor types: ', sensor_types
        if not sensor_types or sensor_types is None:
            message = 'No sensor types provided for consolidated cache processing.'
            raise Exception(message)

        for sensor in sensor_types:
            if debug: print '\n debug -- Getting cache for sensor type: ', sensor
            cache_data = get_cache_by_sensor_type(sensor)
            if cache_data and cache_data is not None:
                for item in cache_data:
                    if debug: print '\n debug -- Add item to cache: ', item
                    data[item] = cache_data[item]
        return data
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception get_consolidated_cache...', message
        current_app.logger.info(message)
        raise Exception(message)


# Build thumbnails and populate cam_images cache. (Used in tasks for 'cam_images' cache.)
def _compile_cam_images():
    """ Build thumbnails for available image files; generate list of dictionaries for images.
    """
    debug = False
    verbose = True
    time = True
    max_count = 100000
    total_count = 0
    process_count = 0
    already_processed_count = 0
    failed_count = 0
    image_list = []
    error_messages = []
    try:
        # Provide time to complete information
        if time: print '\n\tCompiling thumbnail images'
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # List of dictionaries from cache inventory associated with png files.
        data_image_list = get_data_image_list()
        if time: print '\t-- Retrieved data image list from index...'
        if data_image_list is None or not data_image_list:
            print '\n\t*** Data image list error: %r' % data_image_list
            message = 'Failed to retrieve data image list.'
            raise Exception(message)
        available_count = len(data_image_list)

        # Process list of image resources.
        if data_image_list:

            # Configuration items.
            ui_baseUrl = get_image_thumbnail_route()
            base_url = (get_image_camera_store_url_base()).rstrip('/')
            base_thumbnail = get_image_store_url_base()

            # Add the images to the to the folder cache.
            timeout, timeout_read = get_uframe_timeout_info()
            for image_item in data_image_list:
                try:
                    # Counters
                    if verbose:
                        print '-- Counts Total/Ready/Processed/Failed: %d/%d/%d/%d  (Avail/Max: %d/%d)' % \
                        (total_count, already_processed_count, process_count, failed_count, available_count, max_count)
                    total_count += 1
                    # Get thumbnail file path target.
                    new_filename = image_item['filename'].split('.')[0] + '_thumbnail.png'

                    # Remove comma and and use underscore.
                    new_filename = new_filename.replace(',', '_')
                    new_filepath = get_image_store_url_base() + '/' + new_filename
                    #if debug: print '\n -- new_filepath: %s' % new_filepath
                    dt = urllib.unquote(image_item['datetime']).decode('utf8')
                    dt = dt.replace(',', '.')

                    # Get full url
                    url = base_url + image_item['url'] + image_item['filename']
                    if debug:
                        print '\t debug -- url: ', url
                        print '\t debug -- filename: ', image_item['filename']

                    # Check its not already added and doesn't already exist, if so download it.
                    thumbnail = False
                    try:
                        if os.path.isfile(new_filepath):
                            already_processed_count += 1
                        else:
                            #if image_item['url'] not in completed and not os.path.isfile(new_filepath):
                            if verbose:
                                print '\n Image item to be processed... '
                            response = requests.get(url, timeout=(timeout, timeout_read))
                            if response.status_code != 200:
                                message = 'Failed to get image \'%s\' from server.' % image_item['url']
                                error_messages.append(message)
                                failed_count += 1
                                continue

                            if debug: print '\n debug -- Generate thumbnail...'
                            if response.content is None or not response.content:
                                message = 'Response content is null or empty for %s' % image_item['url']
                                error_messages.append(message)
                                failed_count += 1
                                continue
                            img = Image.open(StringIO(response.content))
                            thumb = img.copy()
                            maxsize = (200, 200)
                            thumb.thumbnail(maxsize, PIL.Image.ANTIALIAS)
                            thumb.save(new_filepath)
                            thumbnail = True
                            process_count += 1
                    except Exception as err:
                        failed_count += 1
                        message = 'Failed to get image \'%s\' from server; exception: %s' % (image_item['url'], str(err))
                        error_messages.append(message)
                        #failed_count += 1
                        continue

                    # Add information for image thumbnail.
                    item = {'url': image_item['url'],
                            'filename': new_filename,
                            'reference_designator': image_item['rd'],
                            'date': image_item['date'],
                            'datetime': dt,
                            'thumbnail': new_filepath,
                            'baseUrl': ui_baseUrl}
                    image_list.append(item)
                    if thumbnail and debug: print '\n Processed image item...'

                    if total_count >= max_count or process_count >= available_count:  # or total_count >= available_count:
                        print '\n debug -- Break encoutered....'
                        break
                except Exception as err:
                    message = 'Unknown error occurred during processing: %s' % str(err)
                    error_messages.append(message)
                    failed_count += 1
                    continue

        end = datetime.now()
        if error_messages:
            print '\t-- Error messages(%d) ' % len(error_messages)
            error_count = 0
            for message in error_messages:
                error_count += 1
                error_message = '%s.  %s' % (str(error_count), message)
                print '\t\t %s' % error_message

        print '\n\t-- Total Count: ', total_count
        print '\t-- Number of thumbnail images processed: ', process_count
        print '\t-- Number of thumbnails already available: ', already_processed_count
        print '\t-- Number of thumbnails images available (total): ', already_processed_count + process_count
        print '\t-- Number of thumbnail images failed: ', failed_count
        print '\t-- Number of images available: ', available_count
        print '\t-- Setting maximum Count: ', max_count

        if time:
            print '\n\t-- End time:   ', end
            print '\t-- Time to compile camera images: %s' % str(end - start)
        image_list.sort(key=lambda x: ( x['date'], x['reference_designator']), reverse=True)
        #image_list.sort(key=lambda x: (x['date']), reverse=True)
        if image_list and image_list is not None:
            print '\n delete cam_images cache...'
            cache.delete('cam_images')
            print '\n set cam_images cache...'
            cache.set('cam_images', image_list, timeout=get_cache_timeout())
        return image_list

    except ConnectionError:
        message = 'ConnectionError getting image files.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting image files.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Tag for cache partitioning, index
def get_timespan_for_index_rd(rd):
    """ Get latest start and end times for a reference designator in the index rds.
    Returns dictionary with start and end values.
    Sample request: http://localhost:4000/uframe/dev/get_rd_start_end/CE02SHBP-MJ01C-07-ZPLSCB101
    Sample response:
      {
        "end": "2017-01-29T00:00:00.000Z",
        "start": "2014-09-24T00:00:00.000Z"
      }

    If large_format_inx cache is not available, None is returned.
    If reference designator is not found None is returned for start and end.
    start and end datetime format: '2014-08-01T00:00:00.000Z'
    For 'Thh:mm:ss.sssZ' use actual datetime from actual file on server. (suffix for now)
    """
    debug = False
    start = None
    end = None
    T_suffix = 'T00:00:00.000Z'
    try:
        large_format_inx = cache.get('large_format_inx')
        if not large_format_inx or large_format_inx is None or 'error' in large_format_inx:
            if debug: print '\n No large_format_inx cache available.'
            return None
        if rd not in large_format_inx:
            return None, None

        data = large_format_inx[rd]
        years = [str(key) for key in data.keys()]
        if not years:
            # Data is malformed, review large_format_inx.
            return None, None
        years.sort()
        if debug: print '\n debug -- years: ', years
        if len(years) > 1:
            start_year = years[0]
            end_year = years[-1]
        else:
            start_year = years[0]
            end_year = years[0]
        if debug:
            print '\n debug -- start_year: ', start_year
            print '\n debug -- end_year: ', end_year

        #- - - - - - - - - - - - - - - - - - - - - - - - -
        # Get first datetime entry in start_year.
        #- - - - - - - - - - - - - - - - - - - - - - - - -
        months = [str(key) for key in data[start_year].keys()]
        if not months:
            return None, None
        months.sort()
        if debug: print '\n debug -- months: ', months
        month = months[0]
        days = data[start_year][month]
        if not days:
            return None, None
        days.sort()
        if debug: print '\n debug -- days: ', days
        day = days[0]
        if debug: print '\n debug -- year/month/day: %s/%s/%s' % (start_year, month, day)
        start = '-'.join([start_year, month, day]) + T_suffix

        #- - - - - - - - - - - - - - - - - - - - - - - - -
        # Get last datetime entry in end_year.
        #- - - - - - - - - - - - - - - - - - - - - - - - -
        months = [str(key) for key in data[end_year].keys()]
        if not months:
            return None, None
        months.sort(reverse=True)
        if debug: print '\n debug -- months: ', months
        month = months[0]
        days = data[end_year][month]
        if not days:
            return None, None
        days.sort(reverse=True)
        if debug: print '\n debug -- days: ', days
        day = days[0]
        if debug: print '\n debug -- year/month/day: %s/%s/%s' % (end_year, month, day)
        end = '-'.join([end_year, month, day]) + T_suffix
        return start, end
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _compile_cam_images...', message
        current_app.logger.info(message)
        raise Exception(message)


# Tag for cache partitioning, regression testing.
def get_index_rds():
    """ Get reference designators from raw data server index.

    (15 reference designators)
    [
    "CE02SHBP-LJ01D-11-HYDBBA106",          ['2015', '2016', 2017]
    "CE02SHBP-MJ01C-07-ZPLSCB101",          ['2014', '2015', '2016', '2017']
    "CE02SHBP-MJ01C-08-CAMDSB107",          ['2009', '2010', '2015', '2016']
    "CE04OSBP-LJ01C-11-HYDBBA105",          ['2015', '2016', 2017]
    "CE04OSBP-LV01C-06-CAMDSB106",          ['2014', '2015', '2016', '2017']
    "CE04OSPS-PC01B-05-ZPLSCB102",          ['2015', '2016', '2017']
    "RS01SBPS-PC01A-07-CAMDSC102",          ['2009', '2010', '2016', '2017']
    "RS01SBPS-PC01A-08-HYDBBA103",          ['2015', '2016', '2017']
    "RS01SLBS-LJ01A-09-HYDBBA102",          ['2015', '2016', '2017']
    "RS01SUM2-MJ01B-05-CAMDSB103",          ['2015', '2016', '2017']
    "RS03ASHS-PN03B-06-CAMHDA301",          ['2015', '2016', '2017']
    "RS03AXBS-LJ03A-09-HYDBBA302",          ['2015', '2016', '2017']
    "RS03AXPS-PC03A-07-CAMDSC302",          ['2009', '2010', '2015', '2016']
    "RS03AXPS-PC03A-08-HYDBBA303",          ['2015', '2016', '2017']
    "RS03INT1-MJ03C-05-CAMDSB303"           ['2009', '2010', '2015', '2016']
    ]

    """
    debug = False
    try:
        large_format_inx = cache.get('large_format_inx')
        if not large_format_inx or large_format_inx is None or 'error' in large_format_inx:
            if debug: print '\n No large_format_inx cache available.'
            return []
        rds = [str(key) for key in large_format_inx.keys()]
        if rds:
            rds.sort()
        return rds
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Tag for cache partitioning regression testing.
def get_rds_index():
    """ Get raw data server index cache, return.
    """
    try:
        large_format_inx = cache.get('large_format_inx')
        if not large_format_inx or large_format_inx is None or 'error' in large_format_inx:
            result = None
        else:
            result = large_format_inx
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def _compile_large_format_index():
    """
    Wrapper function to preserve tasks.py interfaces and deployment instructions during sprint 12.
    """
    debug = False
    try:
        data_dict = build_complete_rds_cache_index()
        return data_dict

    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception constructing large format index...', message
        current_app.logger.info(message)
        raise Exception(message)


def _compile_large_format_files():
    """
    Wrapper function to preserve tasks.py interfaces and deployment instructions during sprint 12.
    """
    debug = False
    try:
        data_dict = drive_rds_cache_builds()
        return data_dict

    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception compiling all partitioned caches...', message
        current_app.logger.info(message)
        raise Exception(message)



# Build out thumbnails for 'cam_images' and populate 'cam_images' cache.
def _build_cam_images():
    """ Create new thumbnail images based on large format index.
    """
    try:
        print '\n-- Generating thumbnails for cam_images cache...'
        data = _compile_cam_images()
        if not data or data is None:
            data = []
        return data
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _get_server_cam_images():
    """ Get cam images, if not cached retrieve cache and return results, else empty list or exception raised.
    """
    try:
        cached = cache.get('cam_images')
        if cached and cached is not None and 'error' not in cached:
            data = cached
        else:
            data = _get_cam_images()
            if data and data is not None and 'error' not in data:
                cache.set('cam_images', data, timeout=get_cache_timeout())
        if not data or data is None:
            data = []
        return data
    except Exception as err:
        message = str(err)
        raise Exception(message)


#===================================================================================
# Compile OSMOI information from raw data server. (Used in tasks.)
def _compile_rds_files_OSMOI():
    """ Get indexed information from raw data server for OSMOI instruments only. Osmosis-Based Water Sampler
        RS01SUM2-MJ01B-00-OSMOIA101, 	RS03ASHS-MJ03B-00-OSMOIA301

    Example where data exists for non-standard folder structure of OSMOI data:
    Deviations from standard folder structures:
        1. Sensor folder does not contain port '##-OSMOIA101'
        2. First subfolder is YYY_deployment rather than YY
        3. Second subfolders are 'metadata' and 'results', not a list of months.
        4. No days provided as subfolders.
        5. File naming conventions in metadat and results folder differ in the same folder (i.e. not consistent)

    https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/OSMOIA101/2014_deployment/metadata/
    https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/OSMOIA101/2014_deployment/results/

    File extensions: file extensions - '.jpg', '.pdf', '.xlsx'

    Sample file lists:
    ['OSMOIA101_20140902T143401_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20140902T144932_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20140902_UTC_Analytical_Methods_ver_1-00.pdf',
    'OSMOIA101_20140902_UTC_Image_Catalog_ver_1-00.xlsx',
    'OSMOIA101_20140902_UTC_Recovery_Notes_ver_1-00.pdf',
    'OSMOIA101_20140909T034403_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20150714T175226_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20150714T175957_UTC_Image_ver_1-00.jpg']

    ['OSMOIA101_20140902T143401_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20140902T144932_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20140909T034403_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20150714T175226_UTC_Image_ver_1-00.jpg',
    'OSMOIA101_20150714T175957_UTC_Image_ver_1-00.jpg']

    Build out cache:
    {
      "rds_OSMOI": {
        "RS01SUM2-MJ01B-00-OSMOIA101": {
          "2014": {
            "09": {
              "02": [
                {
                  "date": "2014-09-02",
                  "datetime": "20140902T143401.000Z",
                  "ext": ".jpg",
                  "filename": "OSMOIA101_20140902T143401_UTC_Image_ver_1-00.jpg",
                  "nav_url": "/RS01SUM2/MJ01B/OSMOIA101/",
                  "rd": "RS01SUM2-MJ01B-00-OSMOIA101",
                  "url": "/RS01SUM2/MJ01B/OSMOIA101/2014_deployment/metadata/"
                },
                {
                  "date": "2014-09-02",
                  "datetime": "20140902T144932.000Z",
                  "ext": ".jpg",
                  "filename": "OSMOIA101_20140902T144932_UTC_Image_ver_1-00.jpg",
                  "nav_url": "/RS01SUM2/MJ01B/OSMOIA101/",
                  "rd": "RS01SUM2-MJ01B-00-OSMOIA101",
                  "url": "/RS01SUM2/MJ01B/OSMOIA101/2014_deployment/metadata/"
                },
                {
                  "date": "2014-09-02",
                  "datetime": "20140902T000000.000Z",
                  "ext": ".pdf",
                  "filename": "OSMOIA101_20140902_UTC_Analytical_Methods_ver_1-00.pdf",
                  "nav_url": "/RS01SUM2/MJ01B/OSMOIA101/",
                  "rd": "RS01SUM2-MJ01B-00-OSMOIA101",
                  "url": "/RS01SUM2/MJ01B/OSMOIA101/2014_deployment/metadata/"
                },

    {
      "rds_nav_urls": {
        "OSMOI": {
          "RS01SUM2-MJ01B-00-OSMOIA101": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/OSMOIA101/",
          "RS03ASHS-MJ03B-00-OSMOIA301": "https://rawdata.oceanobservatories.org/files/RS03ASHS/MJ03B/OSMOIA301/"
        }
      }
    }

    """
    from ooiservices.app.uframe.common_tools import (rds_get_supported_sensor_types_osmoi,
                                                     rds_get_supported_platforms_osmoi)
    debug = False
    debug_trace = False
    debug_details = False
    time = True

    try:
        timeout, timeout_read = get_uframe_timeout_info()

        #Supported reference designators.
        reference_designator_SUM2 = 'RS01SUM2-MJ01B-00-OSMOIA101'
        reference_designator_ASHS = 'RS03ASHS-MJ03B-00-OSMOIA301'

        work_nav_urls = {}
        work_nav_urls[reference_designator_SUM2] = None
        work_nav_urls[reference_designator_ASHS] = None

        # Get cache_destination.
        # Determine cache destination.
        cache_destination = get_target_cache_by_sensor_type(['OSMOI'])

        # Get rds_nav_urls cache.
        rds_base_url = get_rds_base_url()

        subfolder_level_1 = '_deployment'
        subfolder_level_2 = ['metadata', 'results']
        supported_platforms = rds_get_supported_platforms_osmoi()

        # Used during processing of various file extension values.
        url_root = get_image_camera_store_url_base().rstrip('/')

        # Filters to limit processing for OSMOI.
        array_codes = rds_get_supported_array_codes()

        # Currently OSMOI sensors only available for cabled array.
        if 'RS' not in array_codes:
            return {}
        years_processed = rds_get_supported_years()
        filetypes_to_check = rds_get_supported_sensor_types_osmoi()
        extensions_to_check = get_extensions_by_sensor_type('OSMOI')

        if time:
            print '\n    Compiling OSMOI files from raw data server'
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get file link/information from image server.
        base_url = get_image_camera_store_url_base()

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
            # Limit to those arrays identified in array_codes.
            rd = s.attrs['href']
            process = False
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if subsite not in supported_platforms:
                        continue
                else:
                    continue
                if rd[0:2] in array_codes:
                    process = True
            if not process:
                continue
            #-----------------------------------------------
            # Level 1 - subsite processing
            if debug_trace: print '\n\t---- Processing root element %s...' % rd
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
                                # OSMOI folder structure rule check
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
                                    if debug: print '\n debug -- Unable to locate level key or folder year is None; continue'
                                    continue

                                # Process years (detail_subfolders is years)
                                for year in detail_subfolders:      # 'YYYY_deployment'

                                    if debug:
                                        print '\n debug -- Processing \'YYYY_deployment\' in detail_subfolders...%r' % year
                                    # OSMOI folder structure rule check
                                    if subfolder_level_1 not in year:
                                        if debug: print '\n debug -- Unable to locate %s in year: %s, continue' % \
                                                        (subfolder_level_1, year)
                                        continue
                                    folder_year = year.replace(subfolder_level_1, '')

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
                                            if debug_details: print '\n debug -- month: %r' % month
                                            month_url = year_url + month
                                            if debug_details: print '\n debug -- month_url: ', month_url
                                            days_subfolders, days_file_list = \
                                                        _get_subfolder_list(month_url,
                                                                            filetypes=filetypes_to_check,
                                                                            extensions=extensions_to_check)
                                            if not days_file_list:
                                                continue

                                            # Processing files.
                                            for filename in days_file_list:
                                                sensor, _dt, junk = filename.split('_', 2)
                                                node = item.rstrip('/')
                                                ref_des = '-'.join([subsite, node, sensor])

                                                # Process file datetime based on extension.
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
                                                if url_root in _url:
                                                    _url = _url.replace(url_root, '')
                                                    _url = _url.replace(filename, '')

                                                tmp_item = {'url': _url,
                                                        'filename': filename,
                                                        'datetime': dt,
                                                        'ext': ext}

                                                # Add extension type
                                                #if debug_details: print '\n after create tmp_item: ', tmp_item
                                                if 'SUM2' in subsite:
                                                    actual_reference_designator = reference_designator_SUM2
                                                    work_nav_urls[reference_designator_SUM2] = rds_base_url + nav_url
                                                elif 'ASHS' in subsite:
                                                    actual_reference_designator = reference_designator_ASHS
                                                    work_nav_urls[reference_designator_ASHS] = rds_base_url + nav_url
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

                                                # If build on previous cache, then not a duplicate item.
                                                data_dict[ref_des][_year][_month][_day].append(tmp_item)


                else:
                    # Item is not a folder.
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile rds files OSMOI: %s' % str(end - start)
        if data_dict and data_dict is not None:
            cache.delete(cache_destination)
            cache.set(cache_destination, data_dict, timeout=get_cache_timeout())

        # Process navigation urls.
        add_nav_urls_to_cache(work_nav_urls, 'OSMOI')
        result_keys = data_dict.keys()
        result_keys.sort()
        print '\n\t-- Number of items in large_format cache(%d): %s' % (len(data_dict), result_keys)
        return data_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


#=====================================================================================
#
# Partitioned caches.
#
#=====================================================================================
def drive_rds_cache_builds():
    """
    Replace _compile_large_format_files with this function.
    Rename this function to be '_compile_large_format_files' to prevent tasks.py changes. (maybe)
    """
    debug = False
    data_dict = {}
    try:
        if debug: print 'Entered drive_rds_cache_builds...'
        array_codes = rds_get_supported_array_codes()
        years_processed = rds_get_supported_years()
        filetypes_to_check = rds_get_all_supported_sensor_types()
        all_valid_extensions = get_valid_extensions()

        print '\n Complete cache builds for raw data server in progress...'
        print '\t-- Arrays processed: ', array_codes
        print '\t-- Years processed: ', years_processed
        print '\t-- Sensor types processed: ', filetypes_to_check
        print '\t-- All valid extensions: ', all_valid_extensions

        for sensor_type in filetypes_to_check:
            if debug: print '\n -- Processing sensor type \'%s\'' % sensor_type

            # Verify sensor_type provided one of all supported sensor types, otherwise continue.
            if sensor_type not in rds_get_all_supported_sensor_types():
                message = 'Sensor type (%s) processing requested, but not currently enabled.' % sensor_type
                current_app.logger.info(message)
                continue

            # # Get harvested data.
            if sensor_type in rds_get_nonstandard_sensor_types():
                # 11473 OSMOI - Osmosis-Based Water Sampler
                if sensor_type == 'OSMOI':
                    data_dict = _compile_rds_files_OSMOI()

                # 12000 FLOBN - Benthic Fluid Flow (C and M series)
                elif sensor_type == 'FLOBN':
                    data_dict = _compile_rds_files_FLOBN()

                # 12000 THSP - Hydrothermal Vent Fluid In-situ Chemistry
                elif sensor_type == 'THSP':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = get_supported_folder_types(sensor_type)
                    data_dict = _compile_rds_files_THSP(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

                # 12000 TRHP - Hydrothermal Vent Fluid Temperature and Resistivity
                elif sensor_type == 'TRHP':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = get_supported_folder_types(sensor_type)
                    data_dict = _compile_rds_files_TRHP(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

                # 12000 MASSP - Mass Spectrometer
                elif sensor_type == 'MASSP':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = get_supported_folder_types(sensor_type)
                    data_dict = _compile_rds_files_MASSP(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

                # 12000 PPSDN - Particulate DNA Sampler
                elif sensor_type == 'PPS':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = ['RASFLA301_PPS']
                    data_dict = _compile_rds_files_PPS(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

                # 12000 RASFL - Hydrothermal Vent Fluid Interactive Sampler
                elif sensor_type == 'RAS':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = ['RASFLA301_RAS']
                    data_dict = _compile_rds_files_RAS(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

                # 12000 PREST - Tidal Seafloor Pressure
                elif sensor_type == 'PREST':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = get_supported_folder_types(sensor_type)
                    data_dict = _compile_rds_files_PREST(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

                # 12000 HPIES - Horizontal Electric Field, Pressure, and Inverted Echo Sounder
                elif sensor_type == 'HPIES':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = get_supported_folder_types(sensor_type)
                    data_dict = _compile_rds_files_HPIES(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

                # 12000 TMPSF - Diffuse Vent Fluid 3-D Temperature Array
                elif sensor_type == 'TMPSF':
                    extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                    supported_folder_types = get_supported_folder_types(sensor_type)
                    data_dict = _compile_rds_files_TMPSF(array_codes,
                                                  years_processed,
                                                  [sensor_type],
                                                  extensions_to_check,
                                                  supported_folder_types)

            # CAMDS, ZPL, HYD
            else:
                extensions_to_check = get_extensions_by_sensor_type(sensor_type)
                supported_folder_types = get_supported_folder_types(sensor_type)
                data_dict = _compile_rds_caches_by_sensor(array_codes,
                                              years_processed,
                                              [sensor_type],
                                              extensions_to_check,
                                              supported_folder_types)
            if debug:
                if data_dict and data_dict is not None:
                    print '\n\t-- Successfully processed %s cache.' % sensor_type.replace('-','')
                else:
                    print '\n\t** No %s cache produced.' % sensor_type.replace('-','')

        return data_dict
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception drive_rds_cache_builds...', message
        current_app.logger.info(message)
        raise Exception(message)


# Compile rds caches by sensor from raw data server..
def _compile_rds_caches_by_sensor(array_codes, years_processed, filetypes_to_check, extensions_to_check,
                                  subfolder_filestypes):
    """ Get indexed information from server.

    [Under review] Optional arguments are for testing ONLY:
        ref_des: Pass in a reference designator to only retrieve those results
        date_str: Pass in a date string (yyyy-mm-dd) to only get data from a specific day

    Example where png exists:
    https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/05/27/RS01SBPS-PC01A-07-CAMDSC102_20160527T215459,693.png

    """
    debug = False
    debug_trace = False
    debug_details = False
    verbose = False
    time = True

    # Used during processing of various file extension values.
    url_root = get_image_camera_store_url_base().rstrip('/')
    if debug: print '\n TESTING --  url_root: ', url_root

    sensor_type = filetypes_to_check
    if sensor_type == ['-ZPL'] and 'CE' not in array_codes:
        return {}
    if sensor_type == ['-OBS'] and 'RS' not in array_codes:
        return {}

    """
    # Lock down broad band hydrophone years processed temporarily.
    if sensor_type == ['-HYD']:
        years_processed = ['2017', '2018']

    # Lock down ZPL years processed temporarily.
    if sensor_type == ['-ZPL']:
        years_processed = ['2016', '2017', '2018']
    """
    try:
        if debug: print '\n debug -- Entered _compile_rds_caches_by_sensor...'
        if time:
            print '\n    Compiling cache for ', filetypes_to_check[0].replace('-','')
            print '\t-- Arrays processed: ', array_codes
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
            print '\t-- Subfolder filetypes to check: ', subfolder_filestypes

        # Determine cache destination...'
        cache_destination = get_target_cache_by_sensor_type(sensor_type)

        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get file link/information from image server.
        base_url = get_image_camera_store_url_base()
        timeout, timeout_read = get_uframe_timeout_info()
        r = requests.get(base_url, timeout=(timeout, timeout_read))

        # Process returned content for links.
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
            process = False
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if debug_details: print ' debug -- Subsite: ', subsite
                else:
                    platform = rd.rstrip('/')
                    if debug_details: print ' debug -- Platform: ', platform
                    continue    # Not processing platforms at this time.

                if rd[0:2] in array_codes:
                    process = True
            if not process:
                continue
            #-----------------------------------------------
            # Level 1 - subsite processing
            if verbose or debug_trace: print '\n\t---- Processing root element %s...' % rd
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=extensions_to_check)
            if debug_trace: print '\n debug -- subfolders(%d): %s' % (len(subfolders), subfolders)

            if not subfolders or subfolders is None:
                continue

            # Level 2 - node processing
            if debug_details: print '\n debug -- Now walking subfolders...'
            for item in subfolders:

                if len(item) != 6:
                    if debug_trace: print '-- debug_trace -- Skip processing folder: ', item
                    continue
                # Determine if item is a folder link or file
                if debug_details: print '\n debug -- item: ', item
                if '/' in item:
                    if verbose: print '\t\t---- %s Processing item: %s...' % (rd, item)
                    subfolder_url = base_url + rd + item

                    #node_subfolders, node_file_list = _get_subfolder_list(subfolder_url, None)
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                          filetypes=subfolder_filestypes,
                                                                          extensions=extensions_to_check)
                    if node_file_list:
                        if debug_details: print '\n debug -- ***** (node subfolder search) %s file_list(%d): %s' % \
                            (item, len(node_file_list), node_file_list)

                    if not node_subfolders or node_subfolders is None:
                        continue

                    # Level 3 - processing sensor information
                    if node_subfolders:
                        if debug_details: print '\n\t debug -- (node subfolder search) %s subfolders(%d): %s' % \
                              (item, len(node_subfolders), node_subfolders)

                        if debug: print '\n Checking subfolders against list filetypes_to_check: ', filetypes_to_check
                        for node_item in node_subfolders:
                            if debug_details: print '\n\t Check node_item: ', node_item
                            #==================
                            ok_to_go = False
                            for check in filetypes_to_check:
                                if debug_details: print '\n\t Check: ', check
                                if check in node_item:
                                    ok_to_go = True
                                    break

                            if not ok_to_go:
                                if debug: print '\t -- node_item %s does not contain filetypes_to_check (%s), cont' % \
                                                (node_item, filetypes_to_check)
                                continue
                            #================
                            node_folder_url = subfolder_url + node_item
                            if debug_details: print '\n debug *** node_folder_url: ', node_folder_url
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                      filetypes=subfolder_filestypes,
                                                                                      extensions=extensions_to_check)
                            if detail_file_list:
                                if debug_details: print '\ndebug --*** (node detail_file_list search) %s file_list(%d): %s' % \
                                    (item, len(detail_file_list), detail_file_list)
                            if detail_subfolders:
                                if debug_details: print '\n\tdebug -- (node detail_subfolders search) %s subfolders(%d): %s' % \
                                      (item, len(detail_subfolders), detail_subfolders)
                                if debug_details: print '\ndebug -- detail_subfolders (years): ', detail_subfolders

                                # Process years (detail_subfolders is years)
                                for year in detail_subfolders:
                                    #=======================================
                                    # Remove to process all years
                                    year_tmp = year.rstrip('/')
                                    if debug_details: print '\n debug -- year_tmp: ', year_tmp
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    if debug_details: print '\n debug -- year_url: ', year_url
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url,
                                                                                              filetypes=subfolder_filestypes,
                                                                                              extensions=extensions_to_check)
                                    if debug_details:
                                        print '\n debug -- detail_subfolders (months): ', months_subfolders
                                        print '\n debug =============================================================='
                                    if months_subfolders:
                                        for month in months_subfolders:
                                            if debug_details: print '\n debug -- month: %r' % month
                                            month_url = year_url + month
                                            if debug_details: print '\n debug -- month_url: ', month_url
                                            days_subfolders, days_file_list = \
                                                _get_subfolder_list(month_url,
                                                                    filetypes=subfolder_filestypes,
                                                                    extensions=extensions_to_check)
                                            if debug_details: print '\n debug -- days_subfolders: ', days_subfolders

                                            if days_subfolders:
                                                for day in days_subfolders:
                                                    day_url = month_url + day
                                                    if debug_details: print '\n debug -- day_url: ', day_url
                                                    day_folders, day_file_list = \
                                                        _get_subfolder_list(day_url,
                                                                            filetypes=subfolder_filestypes,
                                                                            extensions=extensions_to_check)
                                                    if day_file_list and day_file_list is not None:
                                                        if debug_details:
                                                            print '\n debug -- day_file_list(%d): %s' % \
                                                                        (len(day_file_list), day_file_list)
                                                        """
                                                        debug -- day_file_list(144):
                                                        [u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001534,671Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001538,338Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001539,005Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T004534,523Z.png', ...]
                                                        """
                                                        """
                                                        PREST (.dat)
                                                        PRESTB102_10.33.8.9_2101_20170810T2306_UTC.dat
                                                        """

                                                        if debug_details: print '\n debug -- Processing day_file_list...'
                                                        # Process files for a given day.
                                                        for filename in day_file_list:
                                                            if debug_details: print '\n debug -- Process file: ', filename
                                                            if not filename or filename is None:
                                                                print '\n bad filename in day_file_list...%r' % filename
                                                                continue
                                                            ext = None
                                                            ref = None
                                                            filename_rd = None
                                                            for extension in extensions_to_check:
                                                                if extension in filename:
                                                                    ext = extension
                                                                    break

                                                            # Get datetime by ext type, from filename.
                                                            if ext is not None:
                                                                if debug_details: print '\n debug -- Processing ext: %r' % ext
                                                                if ext == '.png':
                                                                    is_hy_file = False
                                                                    if '--YDH-' in filename:
                                                                        is_hy_file = True
                                                                        # Fails for files like ('--YDH-'):
                                                                        # 'OO-HYVM2--YDH-2015-12-16T10:35:00.000000.png'
                                                                        # Get dt, let filename_rd be created below.
                                                                        dt_chunk = filename.replace('.png', '')
                                                                        if debug_details: print '\n dt_check (no ext): ', dt_chunk
                                                                        dt_chunk = dt_chunk.split('--YDH-')
                                                                        if debug_details: print '\n len(dt_check): ', len(dt_chunk)
                                                                        dt = urllib.unquote(dt_chunk[1]).decode('utf8')
                                                                        if debug_details: print '\n Initial dt: ', dt
                                                                        dt = dt.replace('-', '')
                                                                        dt = dt.replace(':', '')
                                                                        if debug_details: print '\n debug -- before adding Z...', dt
                                                                        dt += 'Z'
                                                                        if debug_details: print '\n HY filename png, dt: ', dt

                                                                    elif '_' not in filename:
                                                                        continue

                                                                    if not is_hy_file:
                                                                        ref = filename.split(ext)[0].split('_')
                                                                        filename_rd = ref[0]
                                                                        dt = urllib.unquote(ref[1]).decode('utf8')
                                                                        if ',' in dt:
                                                                            dt = dt.replace(',', '.')
                                                                        # For ZPL png files like:
                                                                        # CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20160106-T221728.png
                                                                        if 'OOI-D' in dt:
                                                                            dt = dt.replace('OOI-D', '')
                                                                        # 20160725T234137.510.000Z
                                                                        if dt[-1] != 'Z':
                                                                            if '.' in dt:
                                                                                dt = dt + 'Z'
                                                                            else:
                                                                                dt = dt + '.000Z'

                                                                elif ext == '.raw':
                                                                    if '_' not in filename:
                                                                        continue
                                                                    # For ZPL files like:
                                                                    # CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170101-T000000.raw
                                                                    ref = filename.split(ext)[0].split('_')
                                                                    filename_rd = ref[0]
                                                                    #ref = filename.split(ext)[0].split('_OOI-D')
                                                                    dt = urllib.unquote(ref[1]).decode('utf8')
                                                                    if 'OOI-D' in dt:
                                                                        dt = dt.replace('OOI-D', '')
                                                                    dt.replace('-', '')
                                                                    dt = dt + '.000Z'
                                                                    #date = ref[1] + 'Z'
                                                                    #dt = urllib.unquote(date).decode('utf8')

                                                                elif ext == '.mseed':
                                                                    if debug_details:
                                                                        print '\n Processing mseed...'
                                                                        print '\n Processing filename: ', filename
                                                                    # OO-HYVM2--YDH.2015-09-03T23:53:17.272250.mseed
                                                                    ref = filename.split(ext)[0].split('.')
                                                                    if debug_details: print '\n debug -- len(ref): ', len(ref)
                                                                    date = None
                                                                    if len(ref) == 3:
                                                                        # 2015
                                                                        # OO-HYVM2--YDH.2015-09-04T00:40:00.000000.mseed
                                                                        #if debug:
                                                                        if debug_details: print '\n MSEED file -- BAD-- split len 3!---', \
                                                                        filename
                                                                        date = ref[1] + ref[2] + 'Z'
                                                                        dt = urllib.unquote(date).decode('utf8')
                                                                        if verbose: print '\t-- MSEDD split 3: dt: ', dt
                                                                    elif len(ref) == 2:
                                                                        if '--YDH-' in ref[0]:
                                                                            tmp = ref[0].split('--YDH-')
                                                                            if len(tmp) == 2:
                                                                                date = tmp[1] + '.' + ref[1] + 'Z'
                                                                                #print '\n debug -- [-] GOOD MSEED DATE: ', date
                                                                            else:
                                                                                date = ref[0] + '.' + ref[1] + 'Z'
                                                                                if debug_details: print '\n debug -- [-] BAD MSEED DATE: ', date
                                                                        elif '--YDH.' in ref[0]:
                                                                            tmp = ref[0].split('--YDH.')
                                                                            if len(tmp) == 2:
                                                                                date = tmp[1] + '.' + ref[1] + 'Z'
                                                                                #print '\n debug -- [.] GOOD MSEED DATE: ', date
                                                                            else:
                                                                                date = ref[0] + '.' + ref[1] + 'Z'
                                                                                if debug_details: print '\n debug -- [.] BAD MSEED DATE: ', date
                                                                        if date is None:
                                                                            if debug_details: print '\n MSEED Eject - date is None for: ', filename
                                                                        dt = urllib.unquote(date).decode('utf8')
                                                                    else:
                                                                        split = ref[0].split('-')
                                                                        date = '-'.join([split[-3], split[-2], split[-1]]) + 'Z'
                                                                        dt = urllib.unquote(date).decode('utf8')

                                                                elif ext == '.mov' or ext == '.mp4':
                                                                    ref = filename.split(ext)[0].split('-')
                                                                    date = ref[1]
                                                                    dt = urllib.unquote(date).decode('utf8')
                                                                    if dt[-1] != 'Z':
                                                                        dt = dt + 'Z'
                                                                else:
                                                                    print '\n *** Unknown extension: %s' % ext
                                                                    continue

                                                                #=========================================
                                                                # Create item dictionary with elements:
                                                                #   'url','filename','datetime','ext','rd', date
                                                                if debug_details:
                                                                    print '\n before create item...'
                                                                    print '\n before create item, filename: ', filename
                                                                    print '\n before create item, day_url: ', day_url
                                                                    print '\n before create item, dt: ', dt
                                                                _url = urllib.unquote(day_url).decode('utf8')
                                                                if url_root in _url:
                                                                    _url = _url.replace(url_root, '')
                                                                    _url = _url.replace(filename, '')

                                                                item = {'url': _url,
                                                                        'filename': urllib.unquote(filename).decode('utf8'),
                                                                        'datetime': dt.replace('-', '').replace(':', '')}
                                                                if debug_details: print '\n after create item: ', item

                                                                # Add extension type to item
                                                                item['ext'] = ext

                                                                # Add reference designator to item
                                                                #ref_des = ref[0]
                                                                if (ext == '.png' or ext == '.raw') \
                                                                        and filename_rd is not None:
                                                                    #print '\n should not be in here for HY png files...'
                                                                    item['rd'] = str(filename_rd)
                                                                    ref_des = filename_rd
                                                                    if debug_details:
                                                                        print '\n debug -- filename_rd: ', filename_rd
                                                                    if len(ref_des) != 8 and len(ref_des) != 27 and \
                                                                        len(ref_des) != 14:
                                                                        if debug_details:
                                                                            print '\n debug -- SUSPECT rd(%d): %s', \
                                                                                (len(ref_des), ref_des)
                                                                else:
                                                                    if debug_details: print '\n debug -- else branch, filename: ', filename
                                                                    junk = node_folder_url.replace(base_url, '')
                                                                    junk = junk.rstrip('/')
                                                                    junk = junk.replace('/','-')
                                                                    if debug_details: print '\n ====== junk: ', junk
                                                                    ref_des = junk
                                                                    item['rd'] = junk[:]
                                                                    if debug_details: print '\n ref_des (regular): ', ref_des

                                                                # Add date to item
                                                                _year = year.rstrip('/')
                                                                _month = month.rstrip('/')
                                                                _day = day.rstrip('/')
                                                                item['date'] = '-'.join([_year, _month, _day])
                                                                if debug_details:
                                                                    print '\n debug -- _year: ', _year
                                                                    print '\n debug -- _month: ', _month
                                                                    print '\n debug -- _day: ', _day
                                                                    print '\n debug -- ref_des: ', ref_des

                                                                ref_des = str(ref_des)
                                                                if len(ref_des) > 27:
                                                                    ref_des = ref_des[0:27]
                                                                if ref_des not in data_dict:
                                                                    data_dict[str(ref_des)] = {}
                                                                if _year not in data_dict[ref_des]:
                                                                    data_dict[ref_des][_year] = {}
                                                                if _month not in data_dict[ref_des][_year]:
                                                                    data_dict[ref_des][_year][_month] = {}
                                                                if _day not in data_dict[ref_des][_year][_month]:
                                                                    data_dict[ref_des][_year][_month][_day] = []

                                                                # If build on previous cache, then not a duplicate item.
                                                                # Check item[datetime] for item before appending.
                                                                # If datetime, verify if same ext - if so, continue.
                                                                data_dict[ref_des][_year][_month][_day].append(item)
                                                                if debug_details: print '\n debug -- Step 6...'
                else:
                    if debug: print '\n debug -- item %s is not a folder.' % item
                    continue

        end = datetime.now()
        if time:
            print '\n\t-- End time:   ', end
            print '\t-- Time to compile information for cache: %s' % str(end - start)

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


def get_rds_nav_urls_cache_by_sensor_type(sensor_type):
    result = None
    try:
        cache_name = 'rds_nav_urls'
        cache_data = cache.get(cache_name)
        if not cache_data:
            message = 'Warning: The rds_nav_urls cache (%s) for sensor type \'%s\' is not available.' % (cache_name, sensor_type)
            current_app.logger.info(message)
            return None

        if sensor_type in cache_data:
            result = cache_data[sensor_type]
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_cache_by_sensor_type(sensor_type):
    try:
        cache_name = get_target_cache_by_sensor_type([sensor_type])
        cache_data = cache.get(cache_name)
        if not cache_data:
            message = 'The cache (%s) for sensor type \'%s\' is not available.' % (cache_name, sensor_type)
            current_app.logger.info(message)
            return None
        return cache_data
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_index_from_cache(sensor_type):
    try:
        cache_name = get_target_cache_by_sensor_type([sensor_type])
        cache_data = cache.get(cache_name)
        if not cache_data:
            message = 'Warning: The cache (%s) for sensor type \'%s\' is not available.' % (cache_name, sensor_type)
            current_app.logger.info(message)
            return None
        cache_index = process_index_for_cache(cache_data)
        return cache_index
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_rds_nav_urls_cache(sensor_type):
    try:
        cache_name = get_target_cache_by_sensor_type([sensor_type])
        cache_data = cache.get(cache_name)
        if not cache_data:
            message = 'Warning: The cache (%s) for sensor type \'%s\' is not available.' % (cache_name, sensor_type)
            current_app.logger.info(message)
            return None
        cache_index = process_index_for_cache(cache_data)
        return cache_index
    except Exception as err:
        message = str(err)
        raise Exception(message)


def process_index_for_cache(cache_data):
    index_data = {}
    try:
        if not cache_data or cache_data is None:
            message = 'No cache data provided for processing the index.'
            raise Exception(message)

        cache_keys = cache_data.keys()
        for key in cache_keys:
            index_data[key] = {}

        for rd in cache_keys:
            years = cache_data[rd].keys()
            if not years:
                continue
            for year in years:
                index_data[rd][year] = {}
                months = cache_data[rd][year].keys()
                if not months:
                    continue
                for month in months:
                    days = cache_data[rd][year][month].keys()
                    index_data[rd][year][month] = days

        return index_data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)

# TODO
def build_complete_rds_cache_index():
    """
    Builds and populates large_format_inx cache from partitioned sensor caches.
    """
    index_dict = {}
    try:
        filetypes_to_check = rds_get_all_supported_sensor_types()
        for sensor_type in filetypes_to_check:
            # Get harvested data.
            cache_index = get_index_from_cache(sensor_type)
            if not cache_index or cache_index is None:
                continue
            cache_keys = cache_index.keys()
            for rd in cache_keys:
                if rd not in index_dict:
                    index_dict[rd] = cache_index[rd]
        if index_dict and index_dict is not None:
            cache.delete('large_format_inx')
            cache.set('large_format_inx', index_dict, timeout=get_cache_timeout())
        return index_dict
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_cache_by_rd(rd=None):
    """
    Get partitioned cache for a specific reference designator.
    """
    try:
        # If rd is None, return None.
        if not rd or rd is None:
            message = '*** Request to return cache with empty or null rd parameter.'
            current_app.logger.info(message)
            return None
        sensor_type = get_sensor_type_from_rd(rd)
        cache_data = get_cache_by_sensor_type(sensor_type)
        return cache_data
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_sensor_type_from_rd(rd):
    try:
        # If rd is None, return None.
        if not rd or rd is None:
            message = '*** Request to return cache with empty or null rd parameter.'
            current_app.logger.info(message)
            return None

        # Get sensor type from reference designator.
        if len(rd) <= 14:
            message = '*** Incomplete sensor reference designator provided (%s).' % rd
            current_app.logger.info(message)
            return None

        subsite, node, sensor = rd.split('-', 2)
        valid_sensor_types = rds_get_all_supported_sensor_types()
        sensor_type = None
        for valid_type in valid_sensor_types:
            if '-' in valid_type:
                check = valid_type.replace('-', '')
            else:
                check = valid_type
            if check in sensor:
                sensor_type = check
                break

        if sensor_type is None:
            message = '*** Unable to determine sensor type from reference designator (%s).' % rd
            current_app.logger.info(message)
            return None

        return sensor_type
    except Exception as err:
        message = str(err)
        raise Exception(message)