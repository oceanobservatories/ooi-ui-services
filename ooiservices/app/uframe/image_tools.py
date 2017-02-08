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

from ooiservices.app import cache
from ooiservices.app.uframe.config import get_cache_timeout
from ooiservices.app.uframe.common_tools import get_image_thumbnail_route
from ooiservices.app.uframe.config import (get_uframe_timeout_info, get_image_camera_store_url_base,
                                           get_image_store_url_base)
import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
#from ooiservices.app.uframe.common_tools import (get_supported_years, get_valid_months, get_supported_sensor_types)


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
    time = True
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
                        if not os.path.isfile(new_filepath):
                            print '\n debug -- NOT found in file system: %s ' % new_filepath
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
    """ Get list of image items (in 'large_format' cache) for thumbnail processing.

    Processing following content from 'large_format':
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
    years_processed = ['2017', '2016']
    try:
        if debug: print '\n debug -- Entered get_data_image_list...'
        large_format_cache = cache.get('large_format')
        if not large_format_cache or large_format_cache is None or 'error' in large_format_cache:
            if debug: print '\n debug -- large_format_cache failed to return information: '
            return None
        else:
            rds = large_format_cache.keys()
            if rds:
                rds.sort()
            if debug: print '\n Reference designators in large format index(%d): %s' % (len(rds), rds)

        for rd in rds:
            rd = str(rd)
            years = large_format_cache[rd].keys()
            years.sort(reverse=True)
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


# Build thumbnails and populate cam_images cache. (Used in tasks for 'cam_images' cache.)
def _compile_cam_images():
    """ Build thumbnails for available image files; generate list of dictionaries for images.
    """
    debug = False
    verbose = True
    time = True
    max_count = 250
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
                        failed_count += 1
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

                    if total_count >= max_count or total_count >= available_count:
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


def get_large_format_rds():
    """ Get reference designators from raw data server large format files cache.
    {
      "reference_designators": [
        "CE02SHBP-MJ01C-07-ZPLSCB101",
        "CE02SHBP-MJ01C-08-CAMDSB107",
        "CE04OSBP-LV01C-06-CAMDSB106",
        "CE04OSPS-PC01B-05-ZPLSCB102",
        "RS01SBPS-PC01A-07-CAMDSC102",
        "RS01SBPS-PC01A-08-HYDBBA103",
        "RS01SLBS-LJ01A-09-HYDBBA102",
        "RS01SUM2-MJ01B-05-CAMDSB103",
        "RS03INT1-MJ03C-05-CAMDSB303"
      ]
    }
    """
    debug = False
    try:
        large_format = cache.get('large_format')
        if not large_format or large_format is None or 'error' in large_format:
            if debug: print '\n No large_format cache available.'
            return []
        rds = [str(key) for key in large_format.keys()]
        if rds:
            rds.sort()
        return rds
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Compile large format index information from raw data server. (Used in tasks.)
def _compile_large_format_index():
    """ Get indexed information from server for time span of sensor resources.
    """
    debug = False
    verbose = False
    time = True
    url_root = get_image_camera_store_url_base().rstrip('/')
    print '\n TESTING --  url_root: ', url_root

    # Processing filters.
    array_codes = ['RS', 'CE', 'CP']
    years_processed = ['2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009']
    filetypes_to_check = ['-HYD','-ZPL', '-OBS', '-CAMDS', '-CAMHD' ]
    extensions_to_check = ['.mseed', '.png', '.raw', '.mp4', '.mov']

    # Processing subfolders.
    subfolder_filestypes = ['HYD', 'ZPL', 'OBS', 'CAMDS', 'CAMHD']
    subfolder_extensions = ['.mseed', '.png', '.raw', '.mp4', '.mov']
    try:
        if debug: print '\n debug -- Entered _compile_large_format_index...'
        if time:
            print '\nCompiling large format index'
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # Get file link/information from image server.
        base_url = get_image_camera_store_url_base()
        timeout, timeout_read = get_uframe_timeout_info()
        r = requests.get(base_url, timeout=(timeout, timeout_read))

        # Process returned content for links.
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')

        """
        # Get any data previously cached.
        data_dict = {}
        large_format_cache = cache.get('large_format')
        if large_format_cache or large_format_cache is not None and 'error not in large_format_cache':
            if debug: print '\n Some data already cached...'
            data_dict = large_format_cache
            if debug: print '\n len(data_dict): ', len(data_dict)
        """
        data_dict = {}

        # Get the current date to use to check against the data server
        current_year = datetime.utcnow().strftime('%Y')
        current_month = datetime.utcnow().strftime('%m')
        current_day = datetime.utcnow().strftime('%d')
        if debug:
            print '\n debug -- year: ', current_year
            print '\n debug -- month: ', current_month
            print '\n debug -- day: ', current_day


        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)
        ss_reduced.sort()
        if debug: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            #-----------------------------------------------
            # Limit to those arrays identified in array_codes.
            rd = s.attrs['href']
            process = False
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if debug: print '\n debug -- Subsite: ', subsite
                else:
                    platform = rd.rstrip('/')
                    if debug: print '\n debug -- Platform: ', platform

                if rd[0:2] in array_codes:
                    process = True
            if not process:
                continue
            #-----------------------------------------------
            #- - - - - - - - - - - - - - - - - - - - - - -
            # Level 1 - subsite processing
            #- - - - - - - - - - - - - - - - - - - - - - -
            if verbose: print '\n\t---- Processing root element %s...' % rd
            d_url = base_url + s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url,
                                                        filetypes=subfolder_filestypes,
                                                        extensions=subfolder_extensions)
            if not subfolders:
                continue

            #- - - - - - - - - - - - - - - - - - - - - - -
            # Level 2 - node processing
            #- - - - - - - - - - - - - - - - - - - - - - -
            for item in subfolders:
                # If not a possible reference designator node/, continue.
                if len(item) != 6:
                    continue

                # Determine if item is a folder link or file
                if debug: print '\n debug -- item: ', item
                if '/' not in item:
                    if debug: print '\n debug -- item %s is not a folder.' % item
                    continue

                if verbose: print '\t\t---- %s Processing item: %s...' % (rd, item)
                subfolder_url = base_url + rd + item

                node_subfolders, node_file_list = _get_subfolder_list(subfolder_url,
                                                                      filetypes=subfolder_filestypes,
                                                                      extensions=subfolder_extensions)
                if node_file_list:
                    if debug:
                        print '\n debug -- ***** (node subfolder search) %s file_list(%d): %s' % \
                        (item, len(node_file_list), node_file_list)

                #- - - - - - - - - - - - - - - - - - - - - - -
                # Level 3 - processing sensor information
                #- - - - - - - - - - - - - - - - - - - - - - -
                if node_subfolders:
                    if debug:
                        print '\n\t debug -- (node subfolder search) %s subfolders(%d): %s' % \
                          (item, len(node_subfolders), node_subfolders)

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
                        # https://rawdata.oceanobservatories.org/files/CE02SHBP/LJ01D/11-HYDBBA106/
                        node_folder_url = subfolder_url + node_item
                        if debug: print '\n debug *** node_folder_url: ', node_folder_url

                        # Define reference designator
                        junk = node_folder_url.replace(base_url, '')
                        junk = junk.rstrip('/')
                        ref_des = str(junk.replace('/', '-'))
                        if debug: print '\n ====== ref_des: ', ref_des

                        # Process year/month/day subfolders...
                        detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url,
                                                                                  filetypes=subfolder_filestypes,
                                                                                  extensions=subfolder_extensions)
                        if debug:
                            if detail_file_list:
                                print '\ndebug --*** (node detail_file_list search) %s file_list(%d): %s' % \
                                    (item, len(detail_file_list), detail_file_list)
                        if detail_subfolders:
                            if debug:
                                print '\n\tdebug -- (node detail_subfolders search) %s subfolders(%d): %s' % \
                                  (item, len(detail_subfolders), detail_subfolders)
                                print '\ndebug -- detail_subfolders (years): ', detail_subfolders

                            if ref_des not in data_dict:
                                data_dict[ref_des] = {}

                            # Process years (detail_subfolders is years)
                            for year in detail_subfolders:
                                #=======================================
                                # Remove to process all years
                                year_tmp = year.rstrip('/')
                                if debug: print '\n debug -- year_tmp: ', year_tmp
                                if year_tmp not in years_processed:
                                    continue
                                #=======================================
                                year_url = node_folder_url + year
                                months_subfolders, months_file_list = _get_subfolder_list(year_url,
                                                                                          filetypes=subfolder_filestypes,
                                                                                          extensions=subfolder_extensions)
                                if debug: print '\n debug -- detail_subfolders (years): ', months_subfolders

                                # Process months.
                                if months_subfolders:
                                    for month in months_subfolders:
                                        month_url = year_url + month
                                        days_subfolders, days_file_list = _get_subfolder_list(month_url,
                                                                                              filetypes=subfolder_filestypes,
                                                                                              extensions=subfolder_extensions)
                                        if debug: print '\n debug -- days_subfolders: ', days_subfolders

                                        # Process days.
                                        if days_subfolders:
                                            _days_subfolders = [str(day.rstrip('/')) for day in days_subfolders]
                                            if debug: print '\n ref_des (regular): ', ref_des
                                            # Add date to item
                                            _year = year.rstrip('/')
                                            _month = month.rstrip('/')
                                            if _year not in data_dict[ref_des]:
                                                data_dict[ref_des][_year] = {}
                                            if _month not in data_dict[ref_des][_year]:
                                                #data_dict[ref_des][_year][_month] = {}
                                                data_dict[ref_des][_year][_month] = _days_subfolders

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile large format index: %s' % str(end - start)
        if data_dict and data_dict is not None:
            cache.delete('large_format_inx')
            cache.set('large_format_inx', data_dict, timeout=get_cache_timeout())
        print '\n Number of items in large_format_inx cache(%d): %s' % (len(data_dict), data_dict.keys())
        if debug: print '\n debug -- Exit _compile_large_format_index...'
        return data_dict
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _compile_large_format_index...', message
        current_app.logger.info(message)
        raise Exception(message)


# Compile large format image information from raw data server. (Used in tasks.)
def _compile_large_format_files(): #test_ref_des=None, test_date_str=None):
    """ Get indexed information from server.

    [Under review] Optional arguments are for testing ONLY:
        ref_des: Pass in a reference designator to only retrieve those results
        date_str: Pass in a date string (yyyy-mm-dd) to only get data from a specific day

    Example where png exists:
    https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/05/27/RS01SBPS-PC01A-07-CAMDSC102_20160527T215459,693.png

    """
    debug = False
    verbose = False
    time = True

    """
    # Master/complete list
    #filetypes_to_check = ['-HYD', '-OBS', '-CAMDS', '-CAMHD', '-ZPL']
    #extensions_to_check = ['.mseed', '.png', '.mp4', '.mov', '.raw']
    """

    # Used during processing of various file extension values.
    url_root = get_image_camera_store_url_base().rstrip('/')
    if debug: print '\n TESTING --  url_root: ', url_root

    # Filters to limit processing for initial release.
    array_codes = ['RS', 'CE']
    years_processed = ['2017', '2016']

    # Initial release until data mining has UI target defined for sensor specific displays.
    filetypes_to_check = ['-ZPL', '-CAMDS' ]
    extensions_to_check = ['.png']
    try:
        if debug: print '\n debug -- Entered _compile_large_format_files...'
        if time:
            print '\nCompiling large format files'
            print '\t-- Years processed: ', years_processed
            print '\t-- Sensor types processed: ', filetypes_to_check
            print '\t-- Extensions checked: ', extensions_to_check
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        """
        # Left over from prototype implementation, review and update or remove.
        testing = False
        test_year = None
        test_month = None
        test_day = None
        if test_ref_des is not None and test_date_str is not None:
            testing = True
            # Get the date we're looking for
            date = test_date_str.split('-')
            test_year = date[0]
            test_month = date[1]
            test_day = date[2]
        """

        # Get file link/information from image server.
        base_url = get_image_camera_store_url_base()
        timeout, timeout_read = get_uframe_timeout_info()
        r = requests.get(base_url, timeout=(timeout, timeout_read))

        # Process returned content for links.
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')

        """
        # Get any data previously cached.
        data_dict = {}
        large_format_cache = cache.get('large_format')
        if large_format_cache or large_format_cache is not None and 'error not in large_format_cache':
            if debug: print '\n Some data already cached...'
            data_dict = large_format_cache
            if debug: print '\n len(data_dict): ', len(data_dict)
        """
        data_dict = {}

        # Get the current date to use to check against the data server
        current_year = datetime.utcnow().strftime('%Y')
        current_month = datetime.utcnow().strftime('%m')
        current_day = datetime.utcnow().strftime('%d')
        if debug:
            print '\n debug -- year: ', current_year
            print '\n debug -- month: ', current_month
            print '\n debug -- day: ', current_day

        # Get root entry (either subsite or subsite-node).
        ss_reduced = []
        for s in ss:
            if 'href' in s.attrs:
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    ss_reduced.append(s)

        if debug: print '\n debug -- The root folder items: ', len(ss_reduced)
        for s in ss_reduced:
            #-----------------------------------------------
            # Limit to those arrays identified in array_codes.
            rd = s.attrs['href']
            process = False
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd.rstrip('/')
                    if debug: print '\n debug -- Subsite: ', subsite
                else:
                    platform = rd.rstrip('/')
                    if debug: print '\n debug -- Platform: ', platform
                if rd[0:2] in array_codes:
                    process = True
            if not process:
                continue
            #-----------------------------------------------

            # Level 1 - subsite processing
            if verbose: print '\n\t---- Processing root element %s...' % rd
            d_url = base_url+s.attrs['href']
            subfolders, file_list = _get_subfolder_list(d_url, None)
            if debug:
                print '\n debug -- subfolders(%d): %s' % (len(subfolders), subfolders)

            if not subfolders:
                continue

            # Level 2 - node processing
            if debug: print '\n debug -- Now walking subfolders...'
            for item in subfolders:
                # Determine if item is a folder link or file
                if debug: print '\n debug -- item: ', item
                if '/' in item:
                    if verbose: print '\t\t---- %s Processing item: %s...' % (rd, item)
                    subfolder_url = base_url + rd + item

                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url, None)
                    if node_file_list:
                        if debug: print '\n debug -- ***** (node subfolder search) %s file_list(%d): %s' % \
                            (item, len(node_file_list), node_file_list)

                    # Level 3 - processing sensor information
                    if node_subfolders:
                        if debug: print '\n\t debug -- (node subfolder search) %s subfolders(%d): %s' % \
                              (item, len(node_subfolders), node_subfolders)

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
                            if debug: print '\n debug *** node_folder_url: ', node_folder_url
                            detail_subfolders, detail_file_list = _get_subfolder_list(node_folder_url, None)

                            if detail_file_list:
                                if debug: print '\ndebug --*** (node detail_file_list search) %s file_list(%d): %s' % \
                                    (item, len(detail_file_list), detail_file_list)
                            if detail_subfolders:
                                if debug: print '\n\tdebug -- (node detail_subfolders search) %s subfolders(%d): %s' % \
                                      (item, len(detail_subfolders), detail_subfolders)
                                if debug: print '\ndebug -- detail_subfolders (years): ', detail_subfolders

                                # Process years (detail_subfolders is years)
                                for year in detail_subfolders:
                                    #=======================================
                                    # Remove to process all years
                                    year_tmp = year.rstrip('/')
                                    if debug: print '\n debug -- year_tmp: ', year_tmp
                                    if year_tmp not in years_processed:
                                        continue
                                    #=======================================
                                    year_url = node_folder_url + year
                                    if debug: print '\n debug -- year_url: ', year_url
                                    months_subfolders, months_file_list = _get_subfolder_list(year_url, None)
                                    if debug: print '\n debug -- detail_subfolders (years): ', months_subfolders

                                    if months_subfolders:
                                        for month in months_subfolders:
                                            month_url = year_url + month
                                            if debug: print '\n debug -- month_url: ', month_url
                                            days_subfolders, days_file_list = _get_subfolder_list(month_url, None)
                                            if debug: print '\n debug -- days_subfolders: ', days_subfolders
                                            if days_subfolders:
                                                for day in days_subfolders:
                                                    day_url = month_url + day
                                                    if debug: print '\n debug -- day_url: ', day_url
                                                    day_folders, day_file_list = _get_subfolder_list(day_url, None)
                                                    if day_file_list and day_file_list is not None:
                                                        if debug:
                                                            print '\n debug -- day_file_list(%d): %s' % \
                                                                        (len(day_file_list), day_file_list)
                                                        """
                                                        debug -- day_file_list(144):
                                                        [u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001534,671Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001538,338Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001539,005Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T004534,523Z.png', ...]
                                                        """
                                                        for filename in day_file_list:
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
                                                            if ext is not None:
                                                                if ext == '.png':
                                                                    is_hy_file = False
                                                                    if '--YDH-' in filename:
                                                                        is_hy_file = True
                                                                        # Fails for files like ('--YDH-'):
                                                                        # 'OO-HYVM2--YDH-2015-12-16T10:35:00.000000.png'
                                                                        # Get dt, let filename_rd be created below.
                                                                        dt_chunk = filename.replace('.png', '')
                                                                        if debug: print '\n dt_check (no ext): ', dt_chunk
                                                                        dt_chunk = dt_chunk.split('--YDH-')
                                                                        if debug: print '\n len(dt_check): ', len(dt_chunk)
                                                                        dt = urllib.unquote(dt_chunk[1]).decode('utf8')
                                                                        if debug: print '\n Initial dt: ', dt
                                                                        dt = dt.replace('-', '')
                                                                        dt = dt.replace(':', '')
                                                                        if debug: print '\n debug -- before adding Z...', dt
                                                                        dt += 'Z'
                                                                        if debug: print '\n HY filename png, dt: ', dt

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
                                                                    if debug:
                                                                        print '\n Processing mseed...'
                                                                        print '\n Processing filename: ', filename
                                                                    # OO-HYVM2--YDH.2015-09-03T23:53:17.272250.mseed
                                                                    ref = filename.split(ext)[0].split('.')
                                                                    if debug: print '\n debug -- len(ref): ', len(ref)
                                                                    date = None
                                                                    if len(ref) == 3:
                                                                        # 2015
                                                                        # OO-HYVM2--YDH.2015-09-04T00:40:00.000000.mseed
                                                                        #if debug:
                                                                        if debug: print '\n MSEED file -- BAD-- split len 3!---', \
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
                                                                                if debug: print '\n debug -- [-] BAD MSEED DATE: ', date
                                                                        elif '--YDH.' in ref[0]:
                                                                            tmp = ref[0].split('--YDH.')
                                                                            if len(tmp) == 2:
                                                                                date = tmp[1] + '.' + ref[1] + 'Z'
                                                                                #print '\n debug -- [.] GOOD MSEED DATE: ', date
                                                                            else:
                                                                                date = ref[0] + '.' + ref[1] + 'Z'
                                                                                if debug: print '\n debug -- [.] BAD MSEED DATE: ', date
                                                                        if date is None:
                                                                            if debug: print '\n MSEED Eject - date is None for: ', filename
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
                                                                # Create item
                                                                if debug:
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
                                                                if debug: print '\n after create item: ', item
                                                                # Add extension type
                                                                item['ext'] = ext

                                                                # Reference designator
                                                                #ref_des = ref[0]
                                                                if (ext == '.png' or ext == '.raw') \
                                                                        and filename_rd is not None:
                                                                    #print '\n should not be in here for HY png files...'
                                                                    item['rd'] = str(filename_rd)
                                                                    ref_des = filename_rd
                                                                    if debug:
                                                                        print '\n debug -- filename_rd: ', filename_rd
                                                                    if len(ref_des) != 8 and len(ref_des) != 27 and \
                                                                        len(ref_des) != 14:
                                                                        if debug:
                                                                            print '\n debug -- SUSPECT rd(%d): %s', \
                                                                                (len(ref_des), ref_des)
                                                                else:
                                                                    if debug: print '\n debug -- else branch, filename: ', filename
                                                                    junk = node_folder_url.replace(base_url, '')
                                                                    junk = junk.rstrip('/')
                                                                    junk = junk.replace('/','-')
                                                                    if debug: print '\n ====== junk: ', junk
                                                                    ref_des = junk
                                                                    item['rd'] = junk[:]
                                                                    if debug: print '\n ref_des (regular): ', ref_des

                                                                # Add date to item
                                                                if debug: print '\n debug: year: ', year
                                                                _year = year.rstrip('/') #[:-1]
                                                                if debug: print '\n debug: month: ', month
                                                                _month = month.rstrip('/') #[:-1]
                                                                if debug: print '\n debug: day: ', day
                                                                _day = day.rstrip('/') #[:-1]
                                                                item['date'] = '-'.join([_year, _month, _day])
                                                                if debug:
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
                                                                data_dict[ref_des][_year][_month][_day].append(item)
                                                                if debug: print '\n debug -- Step 6...'
                else:
                    if debug: print '\n debug -- item %s is not a folder.' % item
                    continue

        end = datetime.now()
        if time:
            print '\n\t-- End time:   ', end
            print '\t-- Time to compile large format files: %s' % str(end - start)
        if data_dict and data_dict is not None:
            if verbose: print '\n delete large_format cache...'
            cache.delete('large_format')
            if verbose: print '\n set large_format cache...'
            cache.set('large_format', data_dict, timeout=get_cache_timeout())
        if verbose: print '\n\t-- Number of items in large_format cache(%d): %s' % (len(data_dict), data_dict.keys())
        if debug: print '\n debug -- Exit _compile_large_format_files...'
        return data_dict
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _compile_large_format_files...', message
        current_app.logger.info(message)
        raise Exception(message)


# Get subfolder contents and file_list for folder.
def _get_subfolder_list(url, filetypes=None, extensions=None):
    """ Get url folder content and process the list of data links.
    """
    debug = False
    """
    # Master/complete list
    filetypes_to_check = ['HY', 'ZPL', 'CAMDS', 'CAMHD', 'OBS']
    extensions_to_check = ['.png', '.raw', '.mseed', '.mp4', '.mov']
    """

    # Set filetypes and extensions to check.
    if filetypes is None:
        filetypes_to_check = ['ZPL', 'CAMDS']
    else:
        filetypes_to_check = filetypes

    if extensions is None:
        extensions_to_check = ['.png']
    else:
        extensions_to_check = extensions

    # base_url is used for exception messages only (timeout or connection errors)
    base_url = get_image_camera_store_url_base()
    try:
        if debug:
            print '\n debug -- Entered _get_subfolder_list...', url
        timeout, timeout_read = get_uframe_timeout_info()
        r = requests.get(url, timeout=(timeout, timeout_read))
        if debug: print '\n debug -- r.status_code: ', r.status_code
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')
        if debug: print '\n debug -- len(ss): ', len(ss)
        #url_list = []
        subfolders = []
        file_list = []
        for s in ss:
            if 'href' in s.attrs:
                if debug: print ' (1) s.attrs[href]: ', s.attrs['href']
                if ';' not in s.attrs['href'] and 'files' not in s.attrs['href'] and '=' not in s.attrs['href']:

                    if '/' in s.attrs['href'] and not './' in s.attrs['href']:
                        if debug: print '\n debug -- folder...'
                        subfolders.append(s.attrs['href'])
                    else:
                        working_attrs = (str(s.attrs['href']))[:]
                        if './' in working_attrs:
                            working_attrs = working_attrs.replace('./', '')
                            if debug: print '\t debug -- file (corrected): ', working_attrs

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
                            if ext in s.attrs['href']:
                                if working_attrs not in file_list and working_attrs and working_attrs is not None:
                                    file_list.append(working_attrs)
                                    break
        if debug:
            if file_list:
                print '\n Returning a file list: ', file_list

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