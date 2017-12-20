#!/usr/bin/env python

"""
Support for images, utilized for image information and display.

Routes:

[GET] /get_cam_images                             # Get list of available camera thumbnail/images.( Filter orDeprecate?)
[GET] /get_cam_image/<string:image_id>.png'       # Get single thumbnail image. (Deprecate)
"""
__author__ = 'Edna Donoughe'


import os.path
from flask import (jsonify, current_app, send_file)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.config import get_image_store_url_base
from ooiservices.app.uframe.image_tools import _get_server_cam_images


# Deprecate - Get list of all available images.
@api.route('/get_cam_images', methods=['GET'])
def get_uframe_cam_images():
    """ Get list of all available images.
    {
      "cam_images": [
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "date": "2016-11-30",
          "datetime": "20161130T224535.573Z",
          "filename": "RS01SBPS-PC01A-07-CAMDSC102_20161130T224535_573Z_thumbnail.png",
          "reference_designator": "RS01SBPS-PC01A-07-CAMDSC102",
          "thumbnail": "ooiservices/cam_images/RS01SBPS-PC01A-07-CAMDSC102_20161130T224535_573Z_thumbnail.png",
          "url": "https://rawdata.oceanobservatories.org/files//RS01SBPS/PC01A/07-CAMDSC102/2016/11/30/RS01SBPS-PC01A-07-CAMDSC102_20161130T224535,573Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "date": "2016-08-12",
          "datetime": "20160812T235025.625Z",
          "filename": "CE02SHBP-MJ01C-08-CAMDSB107_20160812T235025_625_thumbnail.png",
          "reference_designator": "CE02SHBP-MJ01C-08-CAMDSB107",
          "thumbnail": "ooiservices/cam_images/CE02SHBP-MJ01C-08-CAMDSB107_20160812T235025_625_thumbnail.png",
          "url": "https://rawdata.oceanobservatories.org/files//CE02SHBP/MJ01C/08-CAMDSB107/2016/08/12/CE02SHBP-MJ01C-08-CAMDSB107_20160812T235025,625.png"
        },
        ...
    }
    """
    try:
        data = _get_server_cam_images()
        return jsonify({'cam_images': data})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get single thumbnail image.
@api.route('/get_cam_image/<string:image_id>.png', methods=['GET'])
def get_uframe_cam_image(image_id):
    """ Get image thumbnail image from image store.
    """
    try:
        filename = os.getcwd() + "/" + get_image_store_url_base() + "/"+image_id + '.png'
        #filename = get_image_store_url_base() + "/"+image_id + '.png'
        filename = filename.replace(',','%2C')
        if not os.path.isfile(filename):
            filename = os.getcwd() + "/" + get_image_store_url_base() + '/imageNotFound404.png'
            #filename = get_image_store_url_base() + '/imageNotFound404.png'
        return send_file(filename, attachment_filename='cam_image.png', mimetype='image/png')
    except Exception as err:
        message = 'Image not found; image id: %s' % image_id
        current_app.logger.info(message + '; error: ' + str(err))
        return bad_request(message)