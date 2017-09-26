#!/usr/bin/env python

"""
Support for media interface, functions utilized for image information.
"""
__author__ = 'Edna Donoughe'


from flask import current_app
import urllib
import os.path
from datetime import datetime
from ooiservices.app import cache
from ooiservices.app.uframe.common_tools import (rds_get_supported_years, rds_get_valid_months,
                                                 rds_get_valid_sensor_types,
                                                 rds_get_supported_sensor_types, rds_get_sensor_type,
                                                 rds_get_valid_extensions)
from ooiservices.app.uframe.config import (get_image_camera_store_url_base, get_image_store_url_base)
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app.uframe.image_tools import (_compile_large_format_files, _compile_large_format_index)

'''
from bs4 import BeautifulSoup
import PIL
from PIL import Image
from PIL import ImageFile
from StringIO import StringIO
import requests
import requests.adapters
import requests.exceptions
'''

# Get file path to thumbnail images on server.
def _get_base_url_thumbnails():
    """ Get thumbnail location on server to be used when UI is requesting thumbnails.
    """
    try:
        return get_image_store_url_base()
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get url for raw data server.
def _get_base_url_raw_data():
    """ Get data server url.
    """
    try:
        return get_image_camera_store_url_base()
    except Exception as err:
        message = str(err)
        raise Exception(message)


#=================================================================================
#=================================================================================
# List of media references by reference designator.
def _get_media_for_rd(rd=None, year=None, month=None):
    """ Get media references associated with reference designator.
    """
    debug = False
    time = False
    total_count = 0
    image_list = []
    _baseUrl = '/api/uframe/get_cam_image/'
    filename_missing_thumbnail = 'imageNotFound404.png'
    try:
        base_url = (get_image_camera_store_url_base()).rstrip('/')
        base_thumbnail = get_image_store_url_base()
        url_missing_thumbnail = '/'.join([base_thumbnail, filename_missing_thumbnail])

        if rd is not None:
            filter_rd = rd

        # Provide time to complete information
        if time: print '\nGet media for reference designator: ', rd
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # List of dictionaries from cache inventory associated with png files.
        data_image_list = new_get_data_image_list(rd, year=year, month=month)
        if data_image_list is None or not data_image_list:
            message = 'No data returned for reference designator \'%s\'.' % rd
            if debug: print '\n Note: %s' % message
            #raise Exception(message)
            return []
        if data_image_list:
            if debug: print '\n Number of items available to process: ', len(data_image_list)

            # Add the images to the to the folder cache.
            completed = []
            for image_item in data_image_list:
                try:
                    if debug:
                        print '\n -------------------------------------'
                        print '\n filename: ', image_item['filename']

                    # Counters
                    total_count += 1
                    if debug:
                        print '\n debug -- total_count: ', total_count
                        #if total_count >= 100:
                        #    break


                    # Form complete url.
                    if not image_item['filename'] or image_item['filename'] is None:
                        if debug: print '\n debug -- Bad filename provided, empty or null.'
                        continue

                    # Get full url
                    url = base_url + image_item['url'] + image_item['filename']
                    if debug:
                        print '\t debug -- url: ', url
                        print '\t debug -- filename: ', image_item['filename']

                    ext = None
                    new_filename = None
                    new_filepath = None
                    data_link = None
                    check_thumbnail = False
                    check_data_link = False
                    have_thumbnail = False
                    thumbnail_path = None

                    # Get thumbnail file path target.
                    filename = image_item['filename']
                    if '.png' in image_item['filename']:
                        if debug: print '\t debug -- processing image (.png) file...'
                        ext = '.png'
                        new_filename = image_item['filename'].replace('.png', '_thumbnail.png')
                        # Remove comma and and use underscore.
                        new_filename = new_filename.replace(',', '_')
                        new_filepath = get_image_store_url_base() + '/' + new_filename[:]

                        if filename not in completed and os.path.isfile(new_filepath):
                            have_thumbnail = True
                            thumbnail_path = new_filepath
                            #completed.append(filename)
                        else:
                            if debug:
                                print '\t ***** debug -- (png) Thumbnail not found: %s' % new_filepath
                            thumbnail_path = None
                    elif '.raw' in image_item['filename']:
                        if debug: print '\t debug -- processing image (.raw) file...'
                        ext = '.raw'
                        check_data_link = True
                        data_link = url[:]
                        url = None

                        if debug: print '\t debug -- processing data_link: %s' % data_link
                    elif '.mseed' in image_item['filename']:
                        if debug: print '\t debug -- processing image (.mseed) file...'
                        ext = '.mseed'
                        check_data_link = True
                        data_link = url[:]
                        url = None
                        if debug: print '\t debug -- processing data_link: %s' % data_link
                        """
                        elif '.mov' in image_item['filename']:
                            if debug: print '\t debug -- processing image (.mov) file...'
                            ext = '.mov'
                            check_data_link = True
                            data_link = url[:]
                            url = None
                            if debug: print '\t debug -- processing data_link: %s' % data_link
                        elif '.mp4' in image_item['filename']:
                            if debug: print '\t debug -- processing image (.mp4) file...'
                            ext = '.mp4'
                            check_data_link = True
                            data_link = url[:]
                            url = None
                            if debug: print '\t debug -- processing data_link: %s' % data_link
                        """
                    else:
                        if debug: print '\t ************* debug -- Not processing: ', filename
                        continue

                    if filename not in completed:
                        completed.append(filename)

                    # Process datetime field
                    dt = urllib.unquote(image_item['datetime']).decode('utf8')
                    #dt = dt.replace(',', '.')
                    if debug: print '\t debug -- dt: ', dt

                    # Check if thumbnail or data is available, add or update response information.
                    try:
                        if debug:
                            print '\t debug -- check_data_link: ', check_data_link
                            print '\t debug -- have_thumbnail: ', have_thumbnail

                        updated = False
                        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                        # Update processing.
                        # If corresponding data or image already processed, update, otherwise add.
                        #if check_data_link or have_thumbnail:
                        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                        for unit in image_list:
                            if unit['datetime'] == image_item['datetime']:
                                if debug: print '\t Updating unit already in list...'
                                update_unit = unit
                                if update_unit and update_unit is not None:
                                    if check_data_link:
                                        if debug: print '\t debug -- Add data_link: %s' % data_link
                                        update_unit['data_link'] = data_link
                                    if have_thumbnail:
                                        if debug: print '\t debug -- Add thumbnail: %s' % url
                                        update_unit['thumbnail'] = thumbnail_path
                                    if unit['thumbnail'] is None:
                                        # There will be situations where there is no thumbnail..
                                        if debug: print '\t debug -- no have_thumbnail...'
                                        update_unit['thumbnail'] = url_missing_thumbnail
                                    if ext == '.png':
                                        update_unit['url'] = url
                                    unit.update(update_unit)
                                    updated = True
                                break

                        # Add processing.
                        if thumbnail_path is None:
                            thumbnail_path = url_missing_thumbnail
                        if not updated:
                            item = {'url': url,
                                    'filename': filename,
                                    'date': image_item['date'],
                                    'reference_designator': image_item['rd'],
                                    'datetime': dt,
                                    'thumbnail': thumbnail_path,
                                    'baseUrl': _baseUrl,
                                    'data_link': data_link}
                            image_list.append(item)

                    except Exception as err:
                        print '\n***** Error getting media item: ', str(err)
                        continue

                except Exception as err:
                    print '\n***** Error: ', str(err)
                    continue

        if debug: print '\t-- Number of media items: ', len(image_list)
        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to get media for %s: %s' % (rd, str(end - start))
            print 'Completed getting media for %s\n' % rd
        return image_list

    except ConnectionError:
        message = 'ConnectionError getting media references.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting media references.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _get_media_for_rd...', message
        current_app.logger.info(message)
        raise Exception(message)


def new_get_data_image_list(reference_designator=None, year=None, month=None, sensor_type=None, extensions=None):
    """ Get list of image items for thumbnail processing using 'large_format' cache.
    Review (future): list of years, use of extensions.
    rd is reference designator
    sensor_type is one of ['-HYD', '-CAMDS', '-CAMHD', '-ZPL']
    extensions is one (or more) of valid_extensions = ['.mseed', '.png', '.raw', '.mov', '.mp4']
    Processing following content from 'large_format':
    {
      "data": {
        "CE02SHBP-LJ01D-11-HYDBBA1": {
          "2016": {
            "02": {
              "06": [
            {
              "date": "2016-02-06",
              "datetime": "20160206T000000Z",
              "ext": ".mseed",
              "filename": "OO-HYEA2--YDH-2016-02-06T00:00:00.000015.mseed",
              "rd": "CE02SHBP-LJ01D-11-HYDBBA1",
              "url": "/CE02SHBP/LJ01D/11-HYDBBA106/2016/02/06/"
            },
            . . .
            {
              "date": "2016-06-02",
              "datetime": "20160602T225856.644Z",
              "ext": ".png",
              "filename": "RS01SBPS-PC01A-07-CAMDSC102_20160602T225856,644Z.png",
              "rd": "RS01SBPS-PC01A-07-CAMDSC",
              "url": "/RS01SBPS/PC01A/07-CAMDSC102/2016/06/02/"
            },
            . . .]

    """
    debug = False
    details = False
    #sensor_types = ['-HYD', '-CAMDS', '-CAMHD', '-ZPL']
    #valid_extensions = ['.mseed', '.png', '.raw', '.mov', '.mp4']
    sensor_types = rds_get_supported_sensor_types()
    valid_extensions = rds_get_valid_extensions()
    image_list = []
    tmp_dts = []
    filter_on_year = True
    years_processed = ['2017', '2016']

    filter_on_rd = False
    filter_rd = None
    filter_on_sensor_type = False
    filter_sensor_type = None
    try:
        if debug: print '\n debug -- Entered new_get_data_image_list for: ', reference_designator

        # Get current year.
        today = datetime.now()
        current_year = str(today.year)
        current_month = str(today.month)
        if len(current_month) == 1:
            current_month = '0' + current_month
        current_day = str(today.day)
        if debug:
            print '\n Ready current_year: %s' % current_year
            print '\n Ready current_month: %s' % current_month
            print '\n Ready current_day: %s' % current_day

        if year is None:
            years_processed = [current_year]
            #years_processed = ['2016']
        else:
            years_processed = [year]
        if month is None:
            months_processed = [current_month]
        else:
            if len(month) == 1:
                month = '0' + month
            months_processed = [month]

        if debug:
            print '\t > Years to be processed: %s' % years_processed
            print '\t > Months to be processed: %s' % months_processed

        if reference_designator and reference_designator is not None:
            # Check rd value for validity.
            filter_rd = str(reference_designator)
            filter_on_rd = True
        if sensor_type is not None:
            # Check sensor type provided is valid.
            if sensor_type not in sensor_types:
                message = 'Sensor search type (%s) no in available sensor types to search.' % sensor_type
                raise Exception(message)
            filter_sensor_type = sensor_type
            filter_on_sensor_type = True

        if debug:
            if filter_on_rd:
                print '\n debug -- (new_get_data_image_list) Filter on reference designator: ', filter_rd
            if filter_on_sensor_type:
                print '\n debug -- (new_get_data_image_list) Filter on sensor type: ', filter_sensor_type

        # Get reference data
        large_format_cache = cache.get('large_format')
        if not large_format_cache or large_format_cache is None or 'error' in large_format_cache:
            if debug: print '\n debug -- large_format_cache failed to return information: '
            return None

        # Get the reference designators returned in reference data.
        rds = large_format_cache.keys()
        if rds:
            rds.sort()
        if debug: print '\n Reference designators in large format index(%d): %r' % (len(rds), rds)

        total_png = 0
        total_raw = 0
        total_mseed = 0
        for rd in rds:
            rd = str(rd)
            if filter_on_rd:
                if rd != filter_rd:
                    continue
            years = large_format_cache[rd].keys()
            years.sort(reverse=True)
            if details: print '\n\t -- Reference designator: %s years: %s' % (rd, years)

            year_total_png = 0
            year_total_raw = 0
            year_total_mseed = 0
            for year in years:
                year = str(year)
                #if filter_on_year:
                if year not in years_processed:
                    continue
                months = large_format_cache[rd][year].keys()
                if debug: print '\n\t Year %s months: %s' % (year, months)
                months.sort(reverse=True)
                month_total_png = 0
                month_total_raw = 0
                month_total_mseed = 0
                day_total_png = 0
                day_total_raw = 0
                day_total_mseed = 0
                for month in months:
                    month = str(month)
                    if month not in months_processed:
                        continue
                    days = large_format_cache[rd][year][month].keys()
                    if debug: print '\n\t Year %s Month %s days: %s' % (year, month, days)
                    days.sort(reverse=True)
                    png_count = 0
                    raw_count = 0

                    # Process days in the month.
                    for day in days:
                        if debug: print '\n debug -- Processing day: ', day
                        day = str(day)
                        file_list = large_format_cache[rd][year][month][day]
                        if details: print '\t -- Year %s Month %s Day %s Total Files: %d' % (year, month, day, len(file_list))
                        count = 0
                        png_count = 0
                        raw_count = 0
                        mseed_count = 0
                        for file in file_list:
                            #if file not in image_list:
                            if file['datetime'] not in tmp_dts:
                                #if debug: print '\tdebug -- Processing filename: ', file['filename']
                                tmp_dts.append(file['datetime'])

                                if file['ext'] == '.png':
                                    png_count += 1
                                elif file['ext'] == '.raw':
                                    raw_count += 1
                                elif file['ext'] == '.mseed':
                                    mseed_count += 1
                                image_list.append(file)
                                count += 1
                        #if debug: print '\n debug -- tmp_dts(%d): %s' % (len(tmp_dts), tmp_dts)

                        #if debug: print '\t -- Year %s Month %s Day %s png/Total Files: %d/%d' % \
                        #                (year, month, day, count, len(file_list))
                        day_total_png += png_count
                        day_total_raw += raw_count
                        day_total_mseed += mseed_count
                    month_total_png += day_total_png
                    month_total_raw += day_total_raw
                    month_total_mseed += day_total_mseed
                year_total_png += month_total_png
                year_total_raw += month_total_raw
                year_total_mseed += month_total_mseed
            total_png += year_total_png
            total_raw += year_total_raw
            total_mseed += year_total_mseed

        if image_list:
            if debug:
                print '\t-- Total number of png items: %d' % total_png
                print '\t-- Total number of raw items: %d' % total_raw
                print '\t-- Total number of mseed items: %d' % total_mseed
                print '\t-- Total number of matching items: ', len(image_list)

            image_list.sort(key=lambda x: (x['rd']))
            #image_list.sort(key=lambda x: (x['date']), reverse=True)
        return image_list
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception new_get_data_image_list...', message
        current_app.logger.info(message)
        raise Exception(message)


# Validate inputs for year and month.
def validate_year_month(year, month):
    """ Validate inputs for year and month, return actual year and month to be used.
    On error, raise exception.
    """
    debug = False
    try:
        if debug:
            print '\n debug -- validate_year_month: year: %r' % year
            print '\n debug -- validate_year_month: month: %r' % month
        supported_years = rds_get_supported_years()
        if debug: print '\n debug -- supported_years: ', supported_years

        # Validate year.
        if year is not None:
            year = str(year)
            if debug: print '\n debug ** year: %r' % year
            if len(year) != 4 and year != '-1':
                message = 'Malformed year provided. (YYYY)'
                raise Exception(message)
            if year not in supported_years and year != '-1':
                message = 'Year entered is invalid or data is not available for \'%s\'.' % year
                raise Exception(message)
            elif year == '-1':
                    year = None

        # Validate month
        valid_months = rds_get_valid_months()
        if debug: print '\n debug -- valid_months: ', valid_months
        if month is not None:
            month = str(month)
            if debug: print '\n debug ** month: %r' % month
            if month not in valid_months and month != '-1':
                message = 'Month entered is invalid.'
                raise Exception(message)
            else:
                if len(month) != 2:
                    message = 'Malformed month provided. (MM)'
                    raise Exception(message)
                elif month == '-1':
                    month = None
        return year, month
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Validate inputs for year.
def validate_year(year):
    """ Validate inputs for yearh, return actual year to be used.
    On error, raise exception.
    """
    debug = False
    try:
        if debug:
            print '\n debug -- validate_year: year: %r' % year
        supported_years = rds_get_supported_years()
        if debug: print '\n debug -- supported_years: ', supported_years

        # Validate year.
        if year is not None:
            year = str(year)
            if debug: print '\n debug ** year: %r' % year
            if len(year) != 4 and year != '-1':
                message = 'Malformed year provided. (Use: YYYY)'
                raise Exception(message)
            if year not in supported_years and year != '-1':
                message = 'Year entered is invalid or data is not available for \'%s\'.' % year
                raise Exception(message)
            elif year == '-1':
                    year = None
        return year
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_large_format():
    try:
        cached = cache.get('large_format')
        if cached:
            data = cached
            if not data or 'error' in data:
                message = 'Failed to retrieve large_format cache with success.'
                raise Exception(message)
        else:
            print '\n Compiling large format files...'
            data = _compile_large_format_files()
        return data
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_large_format_for_rd(rd=None):
    debug = False
    result = {}
    try:
        cached = cache.get('large_format')
        if cached:
            data = cached
            if not data or 'error' in data:
                message = 'Failed to retrieve large_format cache with success.'
                raise Exception(message)
        else:
            print '\n Compiling large format files...'
            data = _compile_large_format_files()

        if debug: print '\n Number of items in large_format cache(%d): %r' % (len(data), data.keys())
        keys = [str(key) for key in data.keys()]
        if keys:
            keys.sort()

        if rd and rd is not None:
            if rd in keys:
                result = data[rd]
                #if debug: print '\n Number of items in %s result(%d): %r' % (rd, len(result), result['2015'])
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_file_list_for_large_format_data(lfd, rd, sensor_type):
    """
    Given a set of data from large format file cache, process for data list based on a single sensor type.
    """
    debug = False
    details = False
    #sensor_types = ['-HYD', '-CAMDS', '-CAMHD', '-ZPL']
    #valid_extensions = ['.mseed', '.png', '.raw', '.mov', '.mp4']
    valid_extensions = rds_get_valid_extensions()

    image_list = []
    tmp_dts = []
    filter_on_year = True
    #years_processed = ['2017', '2016']
    years_processed = rds_get_supported_years()

    filter_on_rd = False
    filter_rd = None
    filter_on_sensor_type = False
    filter_sensor_type = None

    # Sprint 10
    #sensor_types = ['-HYD', '-CAMDS', '-ZPL']
    #valid_sensor_types = ['CAMDS', 'CAMHD', 'ZPL', 'HYDBB', 'HYDLF']
    valid_sensor_types = rds_get_valid_sensor_types()
    try:
        if debug: print '\n debug -- Entered get_file_list_for_large_format_data for: %s, sensor_type: %s' % (rd,
                                                                                                              sensor_type)
        if sensor_type not in valid_sensor_types:
            message = 'Invalid sensor type (%s) received; valid sensor types: %s' % (sensor_type, valid_sensor_types)
            raise Exception(message)

        if debug: print '\n debug -- type(lfd) %r' % type(lfd)
        years = lfd.keys()
        years.sort(reverse=True)
        if details: print '\n\t -- Reference designator: %s years: %s' % (rd, years)

        total_png = 0
        total_raw = 0
        total_mseed = 0

        year_total_png = 0
        year_total_raw = 0
        year_total_mseed = 0
        for year in years:
            #str_year = str(year)
            #year = str(year)
            if debug: print '\n debug -- year processing: %r' % year

            #if filter_on_year:
            if year not in years_processed:
                continue
            months = lfd[year].keys()
            if debug: print '\n\t Year %s months: %s' % (year, months)
            months.sort(reverse=True)
            month_total_png = 0
            month_total_raw = 0
            month_total_mseed = 0
            day_total_png = 0
            day_total_raw = 0
            day_total_mseed = 0
            for month in months:
                month = str(month)

                days = lfd[year][month].keys()
                if debug: print '\n\t Year %s Month %s days: %s' % (year, month, days)
                days.sort(reverse=True)
                png_count = 0
                raw_count = 0

                # Process days in the month.
                for day in days:
                    if debug: print '\n debug -- Processing day: ', day
                    day = str(day)
                    file_list = lfd[year][month][day]
                    if details: print '\t -- Year %s Month %s Day %s Total Files: %d' % (year, month, day, len(file_list))
                    count = 0
                    png_count = 0
                    raw_count = 0
                    mseed_count = 0
                    for file in file_list:
                        #if file not in image_list:
                        if file['datetime'] not in tmp_dts:
                            #if debug: print '\tdebug -- Processing filename: ', file['filename']
                            tmp_dts.append(file['datetime'])

                            if file['ext'] == '.png':
                                png_count += 1
                            elif file['ext'] == '.raw':
                                raw_count += 1
                            elif file['ext'] == '.mseed':
                                mseed_count += 1
                            image_list.append(file)
                            count += 1

                    #if debug: print '\n debug -- tmp_dts(%d): %s' % (len(tmp_dts), tmp_dts)
                    #if debug: print '\t -- Year %s Month %s Day %s png/Total Files: %d/%d' % \
                    #                (year, month, day, count, len(file_list))
                    day_total_png += png_count
                    day_total_raw += raw_count
                    day_total_mseed += mseed_count
                month_total_png += day_total_png
                month_total_raw += day_total_raw
                month_total_mseed += day_total_mseed
            year_total_png += month_total_png
            year_total_raw += month_total_raw
            year_total_mseed += month_total_mseed

        total_png += year_total_png
        total_raw += year_total_raw
        total_mseed += year_total_mseed
        if image_list:
            if debug:
                print '\t-- Total number of png items: %d' % total_png
                print '\t-- Total number of raw items: %d' % total_raw
                print '\t-- Total number of mseed items: %d' % total_mseed
                print '\t-- Total number of matching items: ', len(image_list)

            #image_list.sort(key=lambda x: (x['rd']))
            #image_list.sort(key=lambda x: (x['date']), reverse=True)
            image_list.sort(key=lambda x: (x['date']))

        return image_list
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception get_file_list_for_large_format_data...', message
        current_app.logger.info(message)
        raise Exception(message)


# List of media references by reference designator.
def fetch_media_for_rd(data_list, rd):
    """ Get media references associated with reference designator.
    Process the data_list to return media information for reference designator.
    """
    debug = False
    time = False
    total_count = 0
    image_list = []
    _baseUrl = '/api/uframe/get_cam_image/'
    filename_missing_thumbnail = 'imageNotFound404.png'
    try:
        base_url = (get_image_camera_store_url_base()).rstrip('/')
        base_thumbnail = get_image_store_url_base()
        url_missing_thumbnail = '/'.join([base_thumbnail, filename_missing_thumbnail])
        if rd is not None:
            filter_rd = rd
        else:
            message = 'Reference designator not provided to fetch_media_for_rd.'
            raise Exception(message)

        # Provide time to complete information
        if time: print '\nGet media for reference designator: ', rd
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # List of dictionaries from cache inventory associated with png files.
        if data_list is None or not data_list:
            message = 'No data returned for reference designator \'%s\'.' % rd
            if debug: print '\n Note: %s' % message
            #raise Exception(message)
            return []
        if data_list:
            if debug: print '\n Number of items available to process: ', len(data_list)

            # Add the media item to the to the folder cache.
            completed = []
            for media_item in data_list:
                try:
                    if debug:
                        print '\n -------------------------------------'
                        print '\n filename: ', media_item['filename']

                    # Counters
                    total_count += 1
                    if debug: print '\n debug -- total_count: ', total_count

                    # Form complete url.
                    if not media_item['filename'] or media_item['filename'] is None:
                        if debug: print '\n debug -- Bad filename provided, empty or null.'
                        continue

                    # Get full url
                    url = base_url + media_item['url'] + media_item['filename']
                    if debug:
                        print '\t debug -- url: ', url
                        print '\t debug -- filename: ', media_item['filename']

                    ext = None
                    new_filename = None
                    new_filepath = None
                    data_link = None
                    check_thumbnail = False
                    check_data_link = False
                    have_thumbnail = False
                    thumbnail_path = None

                    # Get thumbnail file path target.
                    filename = media_item['filename']
                    if '.png' in media_item['filename']:
                        if debug: print '\t debug -- processing image (.png) file...'
                        ext = '.png'
                        new_filename = media_item['filename'].replace('.png', '_thumbnail.png')
                        # Remove comma and and use underscore.
                        new_filename = new_filename.replace(',', '_')
                        new_filepath = get_image_store_url_base() + '/' + new_filename[:]

                        if filename not in completed and os.path.isfile(new_filepath):
                            have_thumbnail = True
                            thumbnail_path = new_filepath
                            #completed.append(filename)
                        else:
                            if debug:
                                print '\t ***** debug -- (png) Thumbnail not found: %s' % new_filepath
                            thumbnail_path = None
                    elif '.raw' in media_item['filename']:
                        if debug: print '\t debug -- processing image (.raw) file...'
                        ext = '.raw'
                        check_data_link = True
                        data_link = url[:]
                        url = None

                        if debug: print '\t debug -- processing data_link: %s' % data_link
                    elif '.mseed' in media_item['filename']:
                        if debug: print '\t debug -- processing image (.mseed) file...'
                        ext = '.mseed'
                        check_data_link = True
                        data_link = url[:]
                        url = None
                        if debug: print '\t debug -- processing data_link: %s' % data_link
                        """
                        elif '.mov' in media_item['filename']:
                            if debug: print '\t debug -- processing image (.mov) file...'
                            ext = '.mov'
                            check_data_link = True
                            data_link = url[:]
                            url = None
                            if debug: print '\t debug -- processing data_link: %s' % data_link
                        elif '.mp4' in media_item['filename']:
                            if debug: print '\t debug -- processing image (.mp4) file...'
                            ext = '.mp4'
                            check_data_link = True
                            data_link = url[:]
                            url = None
                            if debug: print '\t debug -- processing data_link: %s' % data_link
                        """
                    else:
                        if debug: print '\t ************* debug -- Not processing: ', filename
                        continue

                    if filename not in completed:
                        completed.append(filename)

                    # Process datetime field
                    dt = urllib.unquote(media_item['datetime']).decode('utf8')
                    #dt = dt.replace(',', '.')
                    if debug: print '\t debug -- dt: ', dt

                    # Check if thumbnail or data is available, add or update response information.
                    try:
                        if debug:
                            print '\t debug -- check_data_link: ', check_data_link
                            print '\t debug -- have_thumbnail: ', have_thumbnail

                        updated = False
                        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                        # Update processing.
                        # If corresponding data or image already processed, update, otherwise add.
                        #if check_data_link or have_thumbnail:
                        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                        for unit in image_list:
                            if unit['datetime'] == media_item['datetime']:
                                if debug: print '\t Updating unit already in list...'
                                update_unit = unit
                                if update_unit and update_unit is not None:
                                    if check_data_link:
                                        if debug: print '\t debug -- Add data_link: %s' % data_link
                                        update_unit['data_link'] = data_link
                                    if have_thumbnail:
                                        if debug: print '\t debug -- Add thumbnail: %s' % url
                                        update_unit['thumbnail'] = thumbnail_path
                                    if unit['thumbnail'] is None:
                                        # There will be situations where there is no thumbnail..
                                        if debug: print '\t debug -- no have_thumbnail...'
                                        update_unit['thumbnail'] = url_missing_thumbnail
                                    if ext == '.png':
                                        update_unit['url'] = url
                                    unit.update(update_unit)
                                    updated = True
                                break

                        # Add processing.
                        if thumbnail_path is None:
                            thumbnail_path = url_missing_thumbnail
                        if not updated:
                            item = {'url': url,
                                    'filename': filename,
                                    'date': media_item['date'],
                                    'reference_designator': media_item['rd'],
                                    'datetime': dt,
                                    'thumbnail': thumbnail_path,
                                    'baseUrl': _baseUrl,
                                    'data_link': data_link}
                            image_list.append(item)

                    except Exception as err:
                        print '\n***** Error getting media item: ', str(err)
                        continue

                except Exception as err:
                    print '\n***** Error: ', str(err)
                    continue

        if debug: print '\t-- Number of media items: ', len(image_list)
        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to get media for %s: %s' % (rd, str(end - start))
            print 'Completed getting media for %s\n' % rd
        return image_list

    except ConnectionError:
        message = 'ConnectionError getting media references.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting media references.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _get_media_for_rd...', message
        current_app.logger.info(message)
        raise Exception(message)


def get_large_format_index_for_rd(rd=None):
    """
    Get large format index from cache. Note hierarchy only, no data items provided.
    Request: http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103
    Response:
    {
      "index": {
        "2015": {
          "09": [
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22"
          ],
          "10": [
            "20",
            "21",
            "22",
            "23"
          ],
          "11": [
            "30"
          ],
          "12": [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16"
          ]
        },
        "2016": {
          "01": [
            "04",
            . . .
    """
    debug = False
    result = {}
    try:
        cached = cache.get('large_format_inx')
        if cached:
            data = cached
            if not data or 'error' in data:
                message = 'Failed to retrieve large_format cache with success.'
                raise Exception(message)
        else:
            print '\n Compiling large format_index...'
            data = _compile_large_format_index()

        if debug: print '\n Number of items in large_format cache(%d): %r' % (len(data), data.keys())
        keys = [str(key) for key in data.keys()]
        if keys:
            keys.sort()

        if rd and rd is not None:
            if rd in keys:
                result = data[rd]
                #if debug: print '\n Number of items in %s result(%d): %r' % (rd, len(result), result['2015'])
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_large_format_index():
    """
    Get large format index from cache.
    Request: http://localhost:4000/uframe/media/get_instruments_by_sensor_type
    Response:
    {
        "2015": {
          "09": [
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22"
          ],
          "10": [
            "20",
            "21",
            "22",
            "23"
          ],
          "11": [
            "30"
          ],
          "12": [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16"
          ]
        },
        "2016": {
          "01": [
            "04",
            . . .
    }
    """
    debug = False
    try:
        cached = cache.get('large_format_inx')
        if cached:
            data = cached
            if not data or 'error' in data:
                message = 'Failed to retrieve large_format cache with success.'
                raise Exception(message)
        else:
            print '\n Compiling large format_index...'
            data = _compile_large_format_index()

        if debug: print '\n Number of items in large_format_inx cache(%d): %r' % (len(data), data.keys())
        return data
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


#=================================================================================
#=================================================================================
'''
# Validate inputs for year and month.
def get_sensor_type_for_rd(rd):
    """ Get sensor type for rd. On error, raise exception.
    """
    sensor_type = None
    try:
        if not rd or rd is None:
            message = 'Invalid reference designator provided (null or empty).'
            raise Exception(message)
        if len(rd) <= 14:
            message = 'Invalid instrument reference designator.'
            raise Exception(message)
        sensor_types = rds_get_supported_sensor_types()
        for value in sensor_types:
            if value in rd:
                sensor_type = value
                break
        return sensor_type
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)
'''

'''
# Under review.
# Compile large format image information from image server. (Used in tasks for 'large_format' cache.)
def _get_large_format_files_by_rd(rd, date_str):
    """ Get image information from server; loop over a directory list to get the files
    available (url>ref>year>month>day>image)

    Optional arguments are for testing ONLY:
        ref_des: Pass in a reference designator to only retrieve those results
        date_str: Pass in a date string (yyyy-mm-dd) to only get data from a specific day

    Example where png exists:
    https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/05/27/RS01SBPS-PC01A-07-CAMDSC102_20160527T215459,693.png

    """
    debug = False
    time = True
    verbose = False

    try:
        #======================================================
        filetypes_to_check = ['-HYD', '-OBS', '-CAMDS', '-CAMHD', '-ZPL']
        extensions_to_check = ['mseed', 'png', 'mp4', 'mov', 'raw']

        site = rd[0:8]
        assembly = rd[9:14]
        instrument = rd[15:]

        date = date_str.split('-')
        if len(date) < 3:
            message = 'Date format not compliant, expecting ISO8601 (yyyy-mm-dd)'
            return bad_request(message)
        year = date[0]
        month = date[1]
        day = date[2]

        data_payload1 = site + '/' + assembly + '/' + instrument + '/'
        date_payload2 = str(year) + '/' + str(month) + '/' + str(day)

        url = get_image_camera_store_url_base() + data_payload1 + date_payload2
        timeout, timeout_read = get_uframe_timeout_info()
        r = requests.get(url, timeout=(timeout, timeout_read))

        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')

        entry = {}
        entry_list = []
        for s in ss:
            entry_url = url+s.attrs['href'][1:]
            if entry_url.split('.')[-1] in extensions_to_check:
                entry['url'] = entry_url
                entry['datetime'] = date_str
                entry['filename'] = entry_url.split('/')[-1]
                entry_list.append(entry)

        if len(entry_list) < 1:
            message = 'Error: %s data not available for this date: %s' % (rd, date_str)
            raise Exception(message)
        return entry_list

    except Exception as err:
        message = str(err)
        raise Exception(message)
    #======================================================
'''
