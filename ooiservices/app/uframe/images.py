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
        #filename = os.getcwd() + "/" + get_image_store_url_base() + "/"+image_id + '.png'
        filename = get_image_store_url_base() + "/"+image_id + '.png'
        filename = filename.replace(',','%2C')
        if not os.path.isfile(filename):
            #filename = os.getcwd() + "/" + get_image_store_url_base() + '/imageNotFound404.png'
            filename = get_image_store_url_base() + '/imageNotFound404.png'
        return send_file(filename, attachment_filename='cam_image.png', mimetype='image/png')
    except Exception as err:
        message = 'Image not found; image id: %s' % image_id
        current_app.logger.info(message + '; error: ' + str(err))
        return bad_request(message)

