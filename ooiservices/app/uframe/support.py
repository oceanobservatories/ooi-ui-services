#!/usr/bin/env python

"""
Support functions for service data management.
"""
__author__ = 'Edna Donoughe'


from flask import (jsonify, current_app)
from ooiservices.app import cache
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import (internal_server_error, bad_request)
from ooiservices.app.uframe.stream_tools import (get_stream_list, get_instrument_list)

# Support only route.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_uid_cache
@api.route('/build_uid_cache', methods=['GET'])
def build_uid_cache():
    """ Force update of asset information.
    """
    from ooiservices.app.uframe.status_tools import get_uid_digests
    try:
        uid_digests = get_uid_digests(refresh=True)
        print '\n Completed compiling uid digests information.'
        print '\n Number of digests: ', len(uid_digests)
        result = {'result': 'Done'}
        return jsonify(result), 200

    except Exception as err:
        message = 'Exception processing build_assets_cache: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Support only route.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_assets_cache
@api.route('/build_assets_cache', methods=['GET'])
def build_assets_cache():
    """ Force update of asset information.
    """
    from ooiservices.app.uframe.asset_tools import verify_cache
    try:
        asset_list = verify_cache(refresh=True)
        print '\n Completed compiling asset information.'
        print '\n Number of assets: ', len(asset_list)
        result = {'result': 'Done'}
        return jsonify(result), 200

    except Exception as err:
        message = 'Exception processing build_assets_cache: %s' % str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Support only route.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_stream_cache
@api.route('/build_stream_cache')
def build_stream_cache():
    """ Force stream cache build. (Streams currently (celery) set to build every hour on the hour.)
    Responses:
        Success:
        {
          "build_stream_cache": true
        }

        Failure:
        {
          "build_stream_cache": false
        }
    """
    success = False
    try:
        streams = get_stream_list(refresh=True)
        if streams and streams is not None and 'error' not in streams:
            stream_cache = cache.get('stream_list')
            if stream_cache and stream_cache is not None and "error" not in stream_cache:
                success = True
        return jsonify({'build_stream_cache': success}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Support only route.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_instrument_list
@api.route('/build_instrument_list')
def build_instrument_cache():
    """ Force instrument_list cache build. (Instruments currently (celery) set to build every hour on the hour.)
    Responses:
        Success:
        {
          "build_instrument_cache": true
        }

        Failure:
        {
          "build_instrument_cache": false
        }
    """
    success = False
    try:
        instruments = get_instrument_list(refresh=True)
        if instruments and instruments is not None and 'error' not in instruments:
            instrument_cache = cache.get('instrument_list')
            if instrument_cache and instrument_cache is not None and "error" not in instrument_cache:
                success = True
        return jsonify({'build_instrument_list': success}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Support only route.
# (toc_rds)
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_toc_rds
@api.route('/build_toc_rds')
def build_toc_reference_designators():
    """ Build 'toc_reference_designators' cache.
    """
    from ooiservices.app.uframe.toc_tools import compile_toc_reference_designators
    try:
        data = compile_toc_reference_designators()
        if data is None:
            data = []
        return jsonify(toc=data)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return internal_server_error(message)


# Support only route.
# (large_format) Build 'large_format' files.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_large_format_files
@api.route('/build_large_format_files', methods=['GET'])
def build_uframe_large_format_files():
    """ Index all various types of large format files from data server. Returns true for success.
    """
    from ooiservices.app.uframe.image_tools import _compile_large_format_files
    success = False
    try:
        data = _compile_large_format_files()
        if data and data is not None:
            success = True
        print '\n Number of items in large_format files(%d): %s' % (len(data.keys()), data.keys())
        return jsonify({'build_large_format_files': success}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Support only route.
# (large_format_inx) Returns list of reference designators from raw data server index.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_large_format_index
@api.route('/build_large_format_index', methods=['GET'])
def build_large_format_index():
    from ooiservices.app.uframe.image_tools import _compile_large_format_index
    try:
        large_format_index = _compile_large_format_index()
        return jsonify({'large_format_index': large_format_index}), 200
    except Exception as err:
        message = 'Failed to build_large_format_index; %s.' % str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Support only route.
# (cam_images) Build thumbnails for camera images.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_cam_images
@api.route('/build_cam_images', methods=['GET'])
def build_cam_images():
    """ Build thumbnail images.
    """
    from ooiservices.app.uframe.image_tools import _build_cam_images
    try:
        data = _build_cam_images()
        return jsonify({"build_cam_images": data})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Support only route.
# (uid_digests)
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_uid_digests
@api.route('/build_uid_digests')
def build_uid_digests():
    """ Force uid_digests build. (Generally build once overnight, deployment focused and takes some time to complete.)
    Responses:
        Success:
        { "build_uid_digests": true}

        Failure:
        { "build_uid_digests": false}
    """
    from ooiservices.app.uframe.status_tools import get_uid_digests
    success = False
    try:
        uid_digests_cache = get_uid_digests(refresh=True)
        if uid_digests_cache and uid_digests_cache is not None and 'error' not in uid_digests_cache:
            uid_digests = cache.get('uid_digests')
            if uid_digests and uid_digests is not None and 'error' not in uid_digests:
                success = True
        return jsonify({'build_uid_digests': success}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
