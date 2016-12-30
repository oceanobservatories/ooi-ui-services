#!/usr/bin/env python

"""
Support for image interface, functions utilized for image information.
(Original work from controller.py completed by Andy Bird and incorporated here.)
"""
__author__ = 'Edna Donoughe'


from flask import current_app
from bs4 import BeautifulSoup
import urllib
import os.path
from datetime import datetime
import PIL
from PIL import Image
from StringIO import StringIO

from ooiservices.app.uframe.common_tools import dump_dict
from ooiservices.app.uframe.config import (get_uframe_timeout_info, get_image_camera_store_url_base,
                                           get_image_store_url_base)
import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app import cache
#CACHE_TIMEOUT = 172800


# Compile camera images from image server. (Used in tasks for 'cam_images' cache.)
def _compile_cam_images():
    """ Loop over a directory list to get the images available (url>ref>year>month>day>image).

    Minimum required python is 2.7.9 to get python 3.0 ssl patch.
    Modifications:
    1. Add try/except.

    Proposed modifications:
    - Add standard config retrieval of config file variables IMAGE_CAMERA_STORE and IMAGE_STORE

    Example where png exists:
    https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/05/27/RS01SBPS-PC01A-07-CAMDSC102_20160527T215459,693.png

    Generate list of dictionaries for images where dictionary contains:
    defaults: {
        datetime:"",
        filename: "",
        reference_designator: "",
        url:"",
        thumbnail:"",
        baseUrl:"/api/uframe/get_cam_image/"
      }
    """
    debug = False
    time = True
    max_count = 10
    total_count = 0
    image_list = []
    try:
        # Provide time to complete information
        if time: print '\nCompiling camera images'
        start = datetime.now()
        if time: print '\t-- Start time: ', start

        # List of dictionaries from cache inventory associated with png files.
        data_image_list = get_data_image_list()
        if data_image_list:
            if debug: print '\n Number of images available to process: ', len(data_image_list)
            timeout, timeout_read = get_uframe_timeout_info()

            # Create a dictionary of images for data items in image list.
            #image_dict = []
            #for data_image_url in data_image_list:
            #    image_dict.append(_create_image_entry(data_image_url))

            # Add the images to the to the folder cache.
            completed= []
            process_count = 0
            for image_item in data_image_list:
                try:
                    """
                    if debug:
                        print '\n Image item to be processed: '
                        dump_dict(image_item, debug)
                    """

                    # Hack for filename (temporary while fixing large_format cache).
                    tmp = image_item['filename'].split('_')
                    tmp_rd = tmp[0]
                    #if debug: print '\n debug -- rd from filename: ', tmp_rd
                    new_filename = image_item['filename'].split('.')[0] + '_thumbnail.png'

                    # Remove command and use underscore, see if this helps thumbnail display. (if not remove)
                    new_filename = new_filename.replace(',', '_')

                    #if debug: print '\n debug -- new_filename: ', new_filename
                    new_filepath = get_image_store_url_base() + '/' + new_filename
                    #if debug: print '\n debug -- new_filepath: ', new_filepath

                    #if debug: print '\n debug -- Processing image_item[datetime]: ', image_item['datetime']
                    dt = urllib.unquote(image_item['datetime']).decode('utf8')
                    dt = dt.replace(',', '.')
                    #if debug: print '\n debug -- dt: ', dt

                    # Check its not already added and doesn't already exist, if so download it.
                    thumbnail = False
                    try:
                        if image_item['url'] not in completed and not os.path.isfile(new_filepath):
                            if debug:
                                print '\n Image item to be processed: '
                                dump_dict(image_item, debug)
                            response = requests.get(image_item['url'], timeout=(timeout, timeout_read))
                            if response.status_code != 200:
                                message = 'Failed to get image \'%s\' from server.' % image_item['url']
                                if debug: print '\n error: ', message
                                continue

                            if debug: print '\n debug -- Generate thumbnail...'
                            img = Image.open(StringIO(response.content))
                            thumb = img.copy()
                            maxsize = (200, 200)
                            thumb.thumbnail(maxsize, PIL.Image.ANTIALIAS)
                            thumb.save(new_filepath)
                            completed.append(image_item['url'])
                            thumbnail = True
                            process_count += 1
                    except Exception as err:
                        message = str(err)
                        process_count -= 1
                        current_app.logger.info(message)
                        continue



                    # Using manufactured reference designator for workaround, should be image_item['rd'],
                    # Use modified filename also instead of image_item['filename']
                    item = {"url": image_item['url'],
                            "filename": new_filename,
                            "reference_designator": tmp_rd,
                            "datetime": dt,
                            "thumbnail": new_filepath,
                            "baseUrl":"/api/uframe/get_cam_image/"}
                    image_list.append(item)

                    if thumbnail and debug: print '\n Processed image item...'

                    # Counters
                    total_count += 1
                    if debug:
                        if process_count > 0:
                            print '-- Process count: ', process_count
                        print '-- Total Count: %d and current image_list: %d' % (total_count, len(image_list))

                    if total_count >= max_count:
                        break
                except Exception as err:
                    print 'Error: ', str(err)
                    continue

        print '\t\n-- Number of images processed: ', len(image_list)
        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile camera images: %s' % str(end - start)
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
    """ Get list of image items for thumbnail processing using 'large_format' cache.

    Processing following content from 'large_format':
    {
      "result": {
        "RS01SBPS-PC01A-07-CAMDSC": {
          "2016": {
            "06": {
              "02": [
                {
                  "date": "2016-06-02",
                  "datetime": "20160602T225757.555Z",
                  "filename": "RS01SBPS-PC01A-07-CAMDSC102_20160602T225757,555Z.png",
                  "rd": "RS01SBPS-PC01A-07-CAMDSC",
                  "url": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/06/02/RS01SBPS-PC01A-07-CAMDSC102_20160602T225757,555Z.png"
                },
                {
                  "date": "2016-06-02",
                  "datetime": "20160602T225856.644Z",
                  "filename": "RS01SBPS-PC01A-07-CAMDSC102_20160602T225856,644Z.png",
                  "rd": "RS01SBPS-PC01A-07-CAMDSC",
                  "url": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/06/02/RS01SBPS-PC01A-07-CAMDSC102_20160602T225856,644Z.png"
                },
                {
                  "date": "2016-06-02",
                  "datetime": "20160602T225856.978Z",
                  "filename": "RS01SBPS-PC01A-07-CAMDSC102_20160602T225856,978Z.png",
                  "rd": "RS01SBPS-PC01A-07-CAMDSC",
                  "url": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/06/02/RS01SBPS-PC01A-07-CAMDSC102_20160602T225856,978Z.png"
                },
                {
                  "date": "2016-06-02",
                  "datetime": "20160602T232715.251Z",
                  "filename": "RS01SBPS-PC01A-07-CAMDSC102_20160602T232715,251Z.png",
                  "rd": "RS01SBPS-PC01A-07-CAMDSC",
                  "url": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/07-CAMDSC102/2016/06/02/RS01SBPS-PC01A-07-CAMDSC102_20160602T232715,251Z.png"
                }
                . . .]

    """
    debug = False
    image_list = []
    try:
        if debug: print '\n debug -- Entered _compile_cam_images...'
        large_format_cache = cache.get('large_format')
        if not large_format_cache or large_format_cache is None or 'error' in large_format_cache:
            if debug: print '\n debug -- large_format_cache failed to return information: '
        else:
            if debug: print '\n debug -- large_format_cache: ', large_format_cache.keys()

        rds = large_format_cache.keys()
        if debug:
            print '\n debug -- rds(%d): %s' % (len(rds), rds)
        for rd in rds:
            rd = str(rd)
            years = large_format_cache[rd].keys()
            if debug: print '\n Reference designator: %s years: %s' % (rd, years)
            for year in years:
                year = str(year)
                months = large_format_cache[rd][year].keys()
                #if debug: print '\n\t Year %s months: %s' % (year, months)
                for month in months:
                    month = str(month)
                    days = large_format_cache[rd][year][month].keys()
                    #if debug: print '\n\t Year %s Month %s days: %s' % (year, month, days)
                    for day in days:
                        day = str(day)
                        file_list = large_format_cache[rd][year][month][day]
                        if debug: print '\n\t Year %s Month %s Day %s Files: %d' % (year, month, day, len(file_list))
                        for file in file_list:
                            if file['ext'] == '.png':
                                image_list.append(file)

        print '\n-- Number of images available: ', len(image_list)
        image_list.sort(key=lambda x: (x['rd'], x['date']), reverse=True)
        return image_list
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _compile_cam_images...', message
        current_app.logger.info(message)
        raise Exception(message)


# Compile large format image information from image server. (Used in tasks for 'large_format' cache.)
def _compile_large_format_files(test_ref_des=None, test_date_str=None):
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
    #filetypes_to_check = ['-HYD', '-OBS', '-CAMDS', '-CAMHD', '-ZPL']
    #extensions_to_check = ['.mseed', '.png', '.mp4', '.mov', '.raw']
    filetypes_to_check = ['-CAMDS', '-CAMHD']
    extensions_to_check = ['.png', '.mp4', '.mov']
    try:
        if debug: print '\n debug -- Entered _compile_large_format_files...'

        if time: print '\nCompiling large format files'
        start = datetime.now()
        if time: print '\t-- Start time: ', start

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

        # Get file link/information from image server.
        base_url = get_image_camera_store_url_base()
        timeout, timeout_read = get_uframe_timeout_info()
        r = requests.get(base_url, timeout=(timeout, timeout_read))
        #if debug: print '\n debug -- r.status_code: ', r.status_code

        # Process returned content for links.
        soup = BeautifulSoup(r.content, "html.parser")
        ss = soup.findAll('a')

        # Get any data previously cached.
        data_dict = {}
        large_format_cache = cache.get('large_format')
        if large_format_cache or large_format_cache is not None and 'error not in large_format_cache':
            if debug: print '\n Some data already cached...'
            data_dict = large_format_cache
            if debug: print '\n len(data_dict): ', len(data_dict)

        # Get the current date to use to check against the data on HYRAX server
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
                #if debug: print '\n debug -- s.attrs[href]: ', s.attrs['href']
                len_href = len(s.attrs['href'])
                if len_href == 9 or len_href == 15 or len_href == 28:
                    #if debug: print '\n debug -- ss_reduced: ', s.attrs['href']
                    ss_reduced.append(s)

        if debug: print '\n debug -- The root folder items: ', len(ss_reduced)

        subfolder = []
        subsite = None
        platform = None
        sensor = None
        node = None
        array_codes = ['CE', 'RS']
        for s in ss_reduced:
            #-----------------------------------------------
            # Just work cabled array for testing.
            rd = s.attrs['href']
            process = False
            if rd and len(rd) == 9 or len(rd) == 15:
                if len(rd) == 9:
                    subsite = rd[:-1]
                    if debug: print '\n debug -- Subsite: ', subsite
                else:
                    platform = rd[:-1]
                    if debug: print '\n debug -- Platform: ', platform

                if rd[0:2] in array_codes:
                    process = True
            if not process:
                continue
            #-----------------------------------------------
            print '\n ---- Processing root element %s...' % rd
            d_url = base_url+s.attrs['href']
            #if debug: print '\n debug -- d_url: ', d_url
            subfolders, file_list = _get_subfolder_list(d_url, None)
            if debug:
                print '\n debug -- subfolders(%d): %s' % (len(subfolders), subfolders)
            #if debug: print '\n debug -- url_list: ', url_list

            if not subfolders:
                continue

            if debug: print '\n debug -- Now walking subfolders...'
            node_subfolders = []
            node_file_list = []
            for item in subfolders:
                # Determine if item is a folder link or file
                if debug: print '\n debug -- item: ', item
                if '/' in item:
                    print '\n\t ----------- %s Processing item: %s...' % (rd, item)
                    #for subfolder_url in url_list:
                    subfolder_url = base_url + rd + item
                    node = item
                    node_subfolders, node_file_list = _get_subfolder_list(subfolder_url, None)

                    if node_file_list:
                        if debug: print '\n debug -- ***** (node subfolder search) %s file_list(%d): %s' % \
                            (item, len(node_file_list), node_file_list)
                    if node_subfolders:
                        if debug: print '\n\t debug -- (node subfolder search) %s subfolders(%d): %s' % \
                              (item, len(node_subfolders), node_subfolders)
                        detail_file_list = []
                        detail_subfolders = []
                        for node_item in node_subfolders:
                            if node_item in ['data/', 'subset/']:
                                continue
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
                                if debug: print '\n debug -- ***** (node detail_file_list search) %s file_list(%d): %s' % \
                                    (item, len(detail_file_list), detail_file_list)
                            if detail_subfolders:
                                if debug: print '\n\t debug -- (node detail_subfolders search) %s subfolders(%d): %s' % \
                                      (item, len(detail_subfolders), detail_subfolders)

                                if debug: print '\n debug -- detail_subfolders (years): ', detail_subfolders
                                # Process years (detail_subfolders is years)
                                for year in detail_subfolders:
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
                                                        if debug: print '\n debug -- day_file_list(%d): %s' % \
                                                                        (len(day_file_list), day_file_list)
                                                        """
                                                        debug -- day_file_list(144):
                                                        [u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001534,671Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001538,338Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T001539,005Z.png',
                                                        u'RS01SBPS-PC01A-07-CAMDSC102_20161129T004534,523Z.png', ...]
                                                        """
                                                        for filename in day_file_list:
                                                            ext = None
                                                            ref = None
                                                            filename_rd = None
                                                            for extension in extensions_to_check:
                                                                if extension in filename:
                                                                    ext = extension
                                                                    break
                                                            if ext is not None:
                                                                if ext == '.png':
                                                                    # Fails for files like:
                                                                    # 'OO-HYVM2--YDH-2015-12-16T10:35:00.000000.png'
                                                                    if '_' not in filename:
                                                                        continue
                                                                    ref = filename.split(ext)[0].split('_')
                                                                    filename_rd = ref[0]
                                                                    dt = urllib.unquote(ref[1]).decode('utf8')
                                                                    dt = dt.replace(',', '.')

                                                                elif ext == '.raw':
                                                                    ref = filename.split(ext)[0].split('_OOI-D')
                                                                    date = ref[1] + 'Z'
                                                                    dt = urllib.unquote(date).decode('utf8')

                                                                elif ext == '.mseed':
                                                                    if debug: print '\n Processing mseed...'
                                                                    # OO-HYVM2--YDH.2015-09-03T23:53:17.272250.mseed
                                                                    ref = filename.split(ext)[0].split('.')
                                                                    if len(ref) == 3:
                                                                        date = ref[1] + 'Z'
                                                                        dt = urllib.unquote(date).decode('utf8')
                                                                    else:
                                                                        split = ref[0].split('-')
                                                                        date = '-'.join([split[-3], split[-2], split[-1]]) + 'Z'
                                                                        dt = urllib.unquote(date).decode('utf8')
                                                                    tmp = day_url.replace(filename, '')[:]
                                                                    tmp = tmp.replace(day,'')
                                                                    tmp = tmp.replace(month, '')
                                                                    tmp = tmp.replace(year, '')
                                                                    tmp = tmp.replace(base_url, '')
                                                                    tmp = tmp.replace('/','-')
                                                                    tmp = tmp[:-1]
                                                                    if debug: print '\n tmp: ', tmp

                                                                    ref = tmp[:]
                                                                elif ext == '.mov' or ext == '.mp4':
                                                                    ref = filename.split(ext)[0].split('-')
                                                                    date = ref[1]
                                                                    dt = urllib.unquote(date).decode('utf8')

                                                                item = {"url": day_url + filename,
                                                                        "filename": urllib.unquote(filename).decode('utf8'),
                                                                        "datetime": dt.replace("-", "").replace(":", "")}

                                                                # Add extension type
                                                                item['ext'] = ext

                                                                # Reference designator
                                                                #ref_des = ref[0]
                                                                if ext == '.png' and filename_rd is not None:
                                                                    item['rd'] = filename_rd
                                                                    ref_des = filename_rd
                                                                    if debug:
                                                                        print '\n debug -- filename_rd: ', filename_rd
                                                                    if len(ref_des) != 8 and len(ref_des) != 27 and \
                                                                        len(ref_des) != 14:
                                                                        if debug:
                                                                            print '\n debug -- SUSPECT rd(%d): %s', \
                                                                                (len(ref_des), ref_des)
                                                                else:
                                                                    # Build reference designator from navigation. (*)
                                                                    tmp = day_url.replace(filename, '')[:]
                                                                    tmp = tmp.replace(day,'')
                                                                    tmp = tmp.replace(month, '')
                                                                    tmp = tmp.replace(year, '')
                                                                    tmp = tmp.replace(base_url, '')
                                                                    tmp = tmp.rstrip('/')
                                                                    tmp = tmp.replace('/','-')
                                                                    #tmp = tmp[:-1]
                                                                    if debug: print '\n ====== tmp: ', tmp
                                                                    ref_des = tmp
                                                                    item['rd'] = tmp[:]
                                                                    if debug: print '\n ref_des (regular): ', ref_des

                                                                # Add date to item
                                                                _year = year[:-1]
                                                                _month = month[:-1]
                                                                _day = day[:-1]
                                                                item['date'] = '-'.join([_year, _month, _day])
                                                                if debug:
                                                                    print '\n debug -- _create item: '
                                                                    dump_dict(item, debug)
                                                                if debug:
                                                                    print '\n debug -- _year: ', _year
                                                                    print '\n debug -- _month: ', _month
                                                                    print '\n debug -- _day: ', _day
                                                                    print '\n debug -- ref_des: ', ref_des

                                                                if debug: print '\n debug -- Step 1...'
                                                                if ref_des not in data_dict:
                                                                    data_dict[ref_des] = {}
                                                                if debug: print '\n debug -- Step 2...'
                                                                if _year not in data_dict[ref_des]:
                                                                    data_dict[ref_des][_year] = {}
                                                                if debug: print '\n debug -- Step 3...'
                                                                if _month not in data_dict[ref_des][_year]:
                                                                    data_dict[ref_des][_year][_month] = {}
                                                                if debug: print '\n debug -- Step 4...'
                                                                if _day not in data_dict[ref_des][_year][_month]:
                                                                    data_dict[ref_des][_year][_month][_day] = []
                                                                if debug: print '\n debug -- Step 5...'
                                                                data_dict[ref_des][_year][_month][_day].append(item)
                                                                if debug: print '\n debug -- Step 6...'
                else:
                    if debug: print '\n debug -- item %s is not a folder.' % item
                    continue

        end = datetime.now()
        if time:
            print '\t-- End time:   ', end
            print '\t-- Time to compile large format files: %s' % str(end - start)
        if debug:
            #print '\n debug -- data_dict: ', len(data_dict)
            print '\n debug -- Exit _compile_large_format_files...'
        return data_dict
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _compile_large_format_files...', message
        current_app.logger.info(message)
        raise Exception(message)


# Get subfolder contents and file_list for folder.
def _get_subfolder_list(url, search_filter):
    """ Get url folder link list.

    OO-HYVM2--YDH.2015-09-05T00:00:00.000000.mseed
    """
    debug = False
    #filetypes_to_check = ['-HYD', '-OBS', '-CAMDS', '-CAMHD', '-ZPL']
    #extensions_to_check = ['.mseed', '.png', '.mp4', '.mov', '.raw']
    foldertypes_to_check = ['-CAMHD']
    #filetypes_to_check = ['CAMHD']
    #extensions_to_check = ['.mp4', '.mov']
    filetypes_to_check = ['CAMDS', 'CAMHD']
    extensions_to_check = ['.png', '.mp4', '.mov']
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
                        #if any(filetype in s.attrs['href'] for filetype in filetypes_to_check):
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
                        #if s.attrs['href'] not in file_list:
                        #    file_list.append(s.attrs['href'])

                        # Filter by file extension.
                        #if debug: print '\n\t debug -- check extensions...'
                        for ext in extensions_to_check:
                            #if debug: print '\t\t debug -- Check %s in %s...' % (ext, s.attrs['href'])
                            if ext in s.attrs['href']:
                                #if debug: print '\n\t debug -- good extension...'
                                if working_attrs not in file_list:
                                    file_list.append(working_attrs)
                                    break
        if debug:
            if file_list:
                print '\n Returning a file list: ', file_list

        return subfolders, file_list # url_list,

    except ConnectionError:
        message = 'ConnectionError getting image files.'
        current_app.logger.info(message)
        return [], []
    except Timeout:
        message = 'Timeout getting image files.'
        current_app.logger.info(message)
        return [], []
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- Exception _get_subfolder_list...', message
        current_app.logger.info(message)
        return [], []