#!/usr/bin/env python

"""
Support functions for ooi-ui-services data management.
"""
__author__ = 'Edna Donoughe'


from flask import (jsonify, current_app)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import (bad_request)
import json

#==================================================================
# Support only route.
# (large_format) Build cache for OSMOI files on raw data server.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_rds_files_osmoi
@api.route('/build_rds_files_osmoi', methods=['GET'])
def build_rds_files_OSMOI():
    """ Index OSMOI files from raw data server. Returns true for success.
    """
    from ooiservices.app.uframe.image_tools import _compile_rds_files_OSMOI
    try:
        data = _compile_rds_files_OSMOI()
        if not data:
            data = None
        print '\n Number of items in large_format files(%d): %s' % (len(data), data.keys())
        return jsonify({'build_rds_files_OSMOI': data}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_rds_list
@api.route('/build_rds_list', methods=['GET'])
def build_rds_list():
    """
    Sample response:
    {
      "rds_streams": [
        {
          "array_name": "Coastal Endurance",
          "assembly_name": "Low-Power JBox (LJ01D)",
          "depth": 81.0,
          "display_name": "Broadband Acoustic Receiver (Hydrophone)",
          "end": "2016-12-28T00:00:00.000Z",
          "latitude": 44.63704,
          "long_display_name": "Coastal Endurance Oregon Shelf Cabled Benthic Experiment Package - Low-Power JBox (LJ01D) - Broadband Acoustic Receiver (Hydrophone)",
          "longitude": -124.30586,
          "platform_name": "Oregon Shelf Cabled Benthic Experiment Package",
          "rds_enabled": true,
          "rds_link": "https://rawdata.oceanobservatories.org/files/CE02SHBP/LJ01D/11-HYDBBA106",
          "reference_designator": "CE02SHBP-LJ01D-11-HYDBBA106",
          "site_name": "Oregon Shelf Cabled Benthic Experiment Package",
          "start": "2016-01-04T00:00:00.000Z",
          "stream": null,
          "stream_dataset": "",
          "stream_display_name": null,
          "stream_method": null,
          "stream_name": null,
          "stream_type": null,
          "water_depth": 81.0
        },
        . . .
      ]
    }
    """
    debug = False
    from ooiservices.app.uframe.stream_tools_rds import (build_rds_streams)
    try:
        if debug: print '\n-- Build rds streams...'
        rds_streams = build_rds_streams()
        if debug: print '\n-- New RDS streams: %d' % len(rds_streams)

        return jsonify({'rds_streams': rds_streams}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_rds_caches
#@api.route('/build_large_format_files', methods=['GET'])
@api.route('/build_rds_caches', methods=['GET'])
def build_rds_caches():
    """
    Constructs [partitioned] cache by sensor and returns a list of harvested reference designators.
    (Same as build_large_format_files.)
    """
    debug = False
    from ooiservices.app.uframe.image_tools import (drive_rds_cache_builds)
    try:
        if debug: print '\n-- Build rds caches...'
        result = drive_rds_cache_builds()
        if debug: print '\n-- Reference designators(%d):\n%s' % (len(result.keys()), json.dumps(result, indent=4, sort_keys=True))
        return jsonify({'reference_designators': result.keys()}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/get_cache/<string:sensor_type>
@api.route('/get_cache/<string:sensor_type>', methods=['GET'])
def get_rds_cache_by_sensor_type(sensor_type):
    """
    Constructs cache by sensor and returns a list of harvested reference designators.
    localhost:4000/uframe/get_cache/-CAMDS
    localhost:4000/uframe/get_cache/CAMDS
    localhost:4000/uframe/get_cache/HYD
    localhost:4000/uframe/get_cache/ZPL
    localhost:4000/uframe/get_cache/OSMOI
    """
    debug = False
    from ooiservices.app.uframe.image_tools import (get_cache_by_sensor_type)
    try:
        if debug: print '\n-- Get %s cache...' % sensor_type
        cache_data = get_cache_by_sensor_type(sensor_type)
        if debug:
            keys = cache_data.keys()
            keys.sort()
            print '   -- Reference designators(%d):%s\n' % (len(keys), keys)
        return jsonify({'cache': cache_data}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/get_cache_index/<string:sensor_type>
@api.route('/get_cache_index/<string:sensor_type>', methods=['GET'])
def get_rds_cache_index_by_sensor_type(sensor_type):
    """
    Constructs cache by sensor and returns a list of harvested reference designators.
    localhost:4000/uframe/get_cache_index/-CAMDS
    localhost:4000/uframe/get_cache_index/CAMDS
    localhost:4000/uframe/get_cache_index/HYD
    localhost:4000/uframe/get_cache_index/ZPL
    localhost:4000/uframe/get_cache_index/OSMOI
    """
    debug = False
    from ooiservices.app.uframe.image_tools import (get_index_from_cache)
    try:
        if debug: print '\n-- Build rds caches...'
        cache_index = get_index_from_cache(sensor_type)

        if debug: print '\n-- Reference designators(%d):\n%s' % (len(cache_index.keys()), json.dumps(cache_index, indent=4, sort_keys=True))
        return jsonify({'cache_index': cache_index}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/build_cache_index
#@api.route('/build_large_format_index', methods=['GET'])
@api.route('/build_cache_index', methods=['GET'])
def build_complete_rds_cache_index():
    """
    Constructs cache index for all supported sensors by utilizing rds_[SENSORTYPE] caches.
    (Same as build_large_format_index)
    """
    debug = False
    from ooiservices.app.uframe.image_tools import (build_complete_rds_cache_index)
    try:
        if debug: print '\n-- Build all rds caches...'
        cache_index = build_complete_rds_cache_index()
        if debug: print '\n-- Reference designators(%d):\n%s' % (len(cache_index.keys()), cache_index.keys())
        return jsonify({'complete_cache_index': cache_index}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Cache Management development tools.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/get_cache/key/assets_dict
@api.route('/get_cache/key/<string:key>', methods=['GET'])
def get_cache_by_key(key):
    """
    Returns cache for key provided.

    Valid keys defined as:
    ['asset_list', 'assets_dict',  'large_format_inx', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'toc_rds', 'vocab_dict', 'vocab_codes',
     'rds_HYD', 'rds_CAMDS', 'rds_OSMOI', 'rds_ZPL',
     'cam_images']

    """
    from ooiservices.app import cache
    debug = False
    valid_cache_keys = ['assets_dict', 'asset_list', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'vocab_dict', 'vocab_codes', 'toc_rds',
     'large_format_inx', 'rds_ZPL', 'rds_HYD', 'rds_CAMDS', 'rds_OSMOI',
     'cam_images']
    try:
        if debug: print '\n-- Get %s cache...' % key

        # Verify key requested is a valid cache key.
        if key not in valid_cache_keys:
            message = 'Invalid key provided: \'%s\'' % key
            return jsonify({'error': message}), 409

        # Get cache data for key.
        cache_data = cache.get(key)
        if not cache_data or cache_data is None or 'error' in cache_data:
            if debug: print '\n No \'%s\' cache available.' % key
            return jsonify({key: {}}), 200

        return jsonify({key: cache_data}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Cache Management development tools.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/store_cache/key/assets_dict
@api.route('/store_cache/key/<string:key>', methods=['GET'])
def store_cache_by_key(key):
    """
    Stores cache as a file in ./cache; Returns cache for key provided.

    Valid keys defined as:
    ['asset_list', 'assets_dict',  'large_format_inx', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'toc_rds', 'vocab_dict', 'vocab_codes',
     'rds_HYD', 'rds_CAMDS', 'rds_OSMOI', 'rds_ZPL',
     'cam_images']

    """
    from ooiservices.app import cache
    from ooiservices.app.uframe.config import get_cache_timeout
    debug = False
    valid_cache_keys = ['assets_dict', 'asset_list', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'vocab_dict', 'vocab_codes', 'toc_rds',
     'large_format_inx', 'rds_ZPL', 'rds_HYD', 'rds_CAMDS', 'rds_OSMOI',
     'cam_images']
    try:
        if debug: print '\n-- Store %s cache in file...' % key

        # Verify key requested is a valid cache key.
        if key not in valid_cache_keys:
            message = 'Invalid key provided: \'%s\'' % key
            return jsonify({'error': message}), 409

        cache_data = cache.get(key)
        if not cache_data or cache_data is None or 'error' in cache_data:
            if debug: print '\n No \'%s\' cache available.' % key
            return jsonify({key: {}}), 200

        # Dump cache contents to string/buffer, write to file.
        str_cache_data = json.dumps(cache_data)
        write_store(key, str_cache_data)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify contents returned from new file, prepare to set new cache or return contents.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Read cache content from file store.
        result = read_store(key)
        new_cache_data = json.loads(result)

        # Verify file contents can be loaded into cache, '*' tag on cache element name.
        # Set cache contents from file contents
        new_key = key #+ '*'
        cache.set(new_key, new_cache_data, timeout=get_cache_timeout())

        # Get cache contents from file
        test_cache_data = cache.get(new_key)

        return jsonify({key: test_cache_data}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


def read_store(filename):
    """
    Open filename, read data, close file and return data
    """
    debug = False
    import os
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    cache_path = os.path.join(APP_ROOT, '..', '..', 'cache')
    try:
        tmp = "/".join([cache_path, filename])
        if debug: print '\n debug -- read path: ', tmp
        f = open(tmp, 'rb')
        data = f.read()
        f.close()
        return data
    except Exception as err:
        #current_app.logger.info(err.message)
        return None


def write_store(filename, data):
    """
    Open filename, read data, close file and return data
    """
    debug = False
    import os
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    cache_path = os.path.join(APP_ROOT, '..', '..', 'cache')
    try:
        tmp = "/".join([cache_path, filename])
        if debug: print '\n debug -- write path: ', tmp
        f = open(tmp, 'wb')
        data = f.write(data)
        f.close()
        return data
    except Exception as err:
        raise Exception('%s' % err.message)


# Cache Management development tools.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/load_cache/key/assets_dict
@api.route('/load_cache/key/<string:key>', methods=['GET'])
def load_cache_by_key(key):
    """
    Loads cache for key from ./cache file contents and returns cache for key provided.

    Valid keys defined as:
    ['assets_dict', 'asset_list', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'vocab_dict', 'vocab_codes', 'toc_rds',
     'large_format_inx', 'rds_ZPL', 'rds_HYD', 'rds_CAMDS', 'rds_OSMOI',
     'cam_images']

    """
    from ooiservices.app import cache
    from ooiservices.app.uframe.config import get_cache_timeout
    debug = False
    valid_cache_keys = ['assets_dict', 'asset_list', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'vocab_dict', 'vocab_codes', 'toc_rds',
     'large_format_inx', 'rds_ZPL', 'rds_HYD', 'rds_CAMDS', 'rds_OSMOI',
     'cam_images']
    try:
        if debug: print '\n-- Load cache for %s...' % key

        # Verify key requested is a valid cache key.
        if key not in valid_cache_keys:
            message = 'Invalid key provided: \'%s\'' % key
            return jsonify({'error': message}), 409

        # Read cache content from file store.
        result = read_store(key)
        if result is None:
            message = 'No cache file available for: \'%s\'' % key
            return jsonify({'error': message}), 409

        # Prepare data for cache
        new_cache_data = json.loads(result)

        # Set cache contents from file contents
        new_key = key #+ '*'
        cache.set(new_key, new_cache_data, timeout=get_cache_timeout())

        # Get cache contents from file
        test_cache_data = cache.get(new_key)
        return jsonify({key: test_cache_data}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/load_all_cache_from_files
@api.route('/load_all_cache_from_files', methods=['GET'])
def load_all_cache_from_files():
    """
    Loads all cache from available ./cache files.

    Valid keys defined as:
    ['assets_dict', 'asset_list', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'vocab_dict', 'vocab_codes', 'toc_rds',
     'large_format_inx', 'rds_ZPL', 'rds_HYD', 'rds_CAMDS', 'rds_OSMOI',
     'cam_images']

    """
    debug = False
    from ooiservices.app import cache
    from ooiservices.app.uframe.config import get_cache_timeout
    valid_cache_keys = ['assets_dict', 'asset_list', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'vocab_dict', 'vocab_codes', 'toc_rds',
     'large_format_inx', 'rds_ZPL', 'rds_HYD', 'rds_CAMDS', 'rds_OSMOI',
     'cam_images']
    result = False
    try:
        if debug: print '\n-- Load all cache from files...'
        test_cache_data = None
        tmp_key = None

        # Process all valid cache keys.
        for key in valid_cache_keys:
            tmp_key = key
            test_cache_data = None

            # Read cache content from file store; if none available for key, continue.
            result = read_store(key)
            if result is None:
                message = ' ** No cache file available for: \'%s\'' % key
                print message
                continue

            print ' -- Load %s cache from file...' % key
            # Prepare data for cache
            new_cache_data = json.loads(result)

            # Set cache contents from file contents
            new_key = key #+ '*'
            cache.set(new_key, new_cache_data, timeout=get_cache_timeout())

            # Get cache contents from file
            test_cache_data = cache.get(new_key)
        result = True
        print '\n'
        return jsonify({'result': result}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Cache Management development tools.
# curl -H "Content-Type: application/json" -X GET localhost:4000/uframe/store_all_cache_as_files
@api.route('/store_all_cache_as_files', methods=['GET'])
def store_all_cache_in_files():
    """
    Stores all cache items as a files in ./cache..

    Valid keys defined as:
    ['asset_list', 'assets_dict',  'large_format_inx', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'toc_rds', 'vocab_dict', 'vocab_codes',
     'rds_HYD', 'rds_CAMDS', 'rds_OSMOI', 'rds_ZPL',
     'cam_images']

    """
    from ooiservices.app import cache
    debug = False
    valid_cache_keys = ['assets_dict', 'asset_list', 'rd_digests', 'uid_digests', 'rd_digests_dict',
     'stream_list', 'vocab_dict', 'vocab_codes', 'toc_rds',
     'large_format_inx', 'rds_ZPL', 'rds_HYD', 'rds_CAMDS', 'rds_OSMOI',
     'cam_images']
    result = False
    try:
        print '\n-- Store all cache from files...'
        # Verify key requested is a valid cache key.
        # Process all valid cache keys, writing cache contents to a file with same name as cache.
        for key in valid_cache_keys:

            cache_data = cache.get(key)
            if not cache_data or cache_data is None or 'error' in cache_data:
                if debug: print '\n No \'%s\' cache available.' % key
                continue

            # Dump cache contents to string/buffer, write to file.
            str_cache_data = json.dumps(cache_data)
            write_store(key, str_cache_data)
            print '\t -- Store %s cache in file...' % key
        print '\n'
        result = True
        return jsonify({'result': result}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
