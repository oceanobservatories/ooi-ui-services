#!/usr/bin/env python

"""
Support for images, utilized for image information.
(Original work from controller.py completed by Andy Bird and incorporated here.)

"""
__author__ = 'Edna Donoughe'


from flask import (jsonify, current_app, request, send_file)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.image_tools import (_compile_large_format_files, _compile_cam_images)
from bs4 import BeautifulSoup
import os.path

#=======================================================================
# Temporary: remove once re-factored for requests within routes.
import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)

from ooiservices.app import cache
CACHE_TIMEOUT = 172800
#=======================================================================


# todo - Note: Route under development and test.
@api.route('/get_large_format_files_by_ref/<string:ref_des>/<string:date_str>')
def get_uframe_large_format_files_by_ref(ref_des, date_str):
    """ Walk the data server and parse out all available large format files
    """
    filetypes_to_check = ['-HYD', '-OBS', '-CAMDS', '-CAMHD', '-ZPL']
    extensions_to_check = ['mseed', 'png', 'mp4', 'mov', 'raw']

    site = ref_des[0:8]
    assembly = ref_des[9:14]
    instrument = ref_des[15:]

    date = date_str.split('-')
    if len(date) < 3:
        message = 'Date format not compliant, expecting ISO8601 (yyyy-mm-dd)'
        return bad_request(message)
    year = date[0]
    month = date[1]
    day = date[2]

    data_payload = site + '/' + assembly + '/' + instrument + '/'
    date_payload = str(year) + '/' + str(month) + '/' + str(day)

    url = current_app.config['IMAGE_CAMERA_STORE'] + data_payload + date_payload
    r = requests.get(url, verify=False)

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

    response = {'data': entry_list}

    if len(entry_list) < 1:
        message = 'Error: %s data not available for this date.' % ref_des
        return bad_request(message)
    return jsonify(response)


# Build 'large_format' cache.
@api.route('/get_large_format_files')
def get_uframe_large_format_files():
    """ Get all available large format files.
    """
    try:
        cached = cache.get('large_format')
        if cached:
            data = cached
        else:
            print '\n Compiling large format files...'
            data = _compile_large_format_files()
            if data and data is not None and 'error' not in data:
                cache.set('large_format', data, timeout=CACHE_TIMEOUT)
        return jsonify(data)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get camera image.
@api.route('/get_cam_image/<string:image_id>.png', methods=['GET'])
def get_uframe_cam_image(image_id):
    """
    Get camera image from ooiservices image store where file name is '[image_id]_thumbnail.png'.

    Notes:
    1. Added 'IMAGE_STORE' function to config.py
    2. Propose return bad_request instead of current coding; improve error message.
    """
    try:
        #filename = os.getcwd()+"/"+current_app.config['IMAGE_STORE']+"/"+image_id+'_thumbnail.png'
        filename = os.getcwd()+"/"+current_app.config['IMAGE_STORE']+"/"+image_id + '.png'
        filename = filename.replace(',','%2C')
        if not os.path.isfile(filename):
            filename = os.getcwd()+"/"+current_app.config['IMAGE_STORE']+'/imageNotFound404.png'
        return send_file(filename, attachment_filename='cam_image.png', mimetype='image/png')
    except Exception as err:
        return jsonify(error="image not found"), 404


# Get 'cam_images'.
@api.route('/get_cam_images')
def get_uframe_cam_images():
    """ Get cam images.
    """
    try:
        """
        will_reset_cache = False
        if request.args.get('reset') == 'true':
            will_reset_cache = True
        """

        cached = cache.get('cam_images')
        if cached and cache is not None and 'error' not in cached: # and not(will_reset_cache):
            data = cached
        else:
            print '\n-- Generating cam_images cache...'
            data = _compile_cam_images()
            if data and data is not None and 'error' not in data:
                cache.set('cam_images', data, timeout=CACHE_TIMEOUT)
        if not data or data is None:
            data = []
        return jsonify({"cam_images": data})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)