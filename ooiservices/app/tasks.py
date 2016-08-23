
__author__ = 'M@Campbell'

from ooiservices.app import create_celery_app
from flask.globals import current_app
from flask.ext.cache import Cache


CACHE_TIMEOUT = 172800

"""
Create the celery app, and configure it to talk to the redis broker.
Then initialize it.
"""

celery = create_celery_app('PRODUCTION')
celery.config_from_object('ooiservices.app.celeryconfig')

from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.controller import _compile_cam_images
from ooiservices.app.uframe.controller import _compile_large_format_files
from ooiservices.app.main.c2 import _compile_c2_toc
from ooiservices.app.uframe.vocab import compile_vocab
from ooiservices.app.uframe.asset_tools import verify_cache

"""
Define the list of processes to run on a scheduled basis.
Caches created/utilized:
    For data visualization: stream_list, cam_images*, large_format*
    For vocabulary: vocab_dict, vocab_codes
    For Command and Control (C2): c2_toc
    For asset information: asset_list, assets_dict, asset_types, asset_rds, rd_assets, bad_asset_list

Disabled for now: glider_tracks

"""


# streams_list
@celery.task(name='tasks.compile_streams')
def compile_streams():
    try:
        with current_app.test_request_context():
            print "[+] Starting stream cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)

            streams = dfs_streams()

            if "error" not in streams:
                cache.set('stream_list', streams, timeout=CACHE_TIMEOUT)
                print "[+] Streams cache reset."
            else:
                print "[-] Error in cache update"
    except Exception as err:
        message = 'compile_streams exception: %s' % err.message
        current_app.logger.warning(message)


# cam_images
@celery.task(name='tasks.compile_cam_images')
def compile_cam_images():
    try:
        with current_app.test_request_context():
            print "[+] Starting cam images cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)

            cam_images = _compile_cam_images()

            if "error" not in cam_images:
                cache.set('cam_images', cam_images, timeout=CACHE_TIMEOUT)
                print "[+] cam images cache reset."
            else:
                print "[-] Error in cache update"
    except Exception as err:
        message = 'compile_cam_images exception: %s' % err.message
        current_app.logger.warning(message)


# c2_toc
@celery.task(name='tasks.compile_c2_toc')
def compile_c2_toc():
    try:
        c2_toc = {}
        with current_app.test_request_context():
            print "[+] Starting c2 toc cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            try:
                c2_toc = _compile_c2_toc()
            except Exception as err:
                message = 'Error processing compile_c2_toc: ', err.message
                current_app.logger.warning(message)

            if c2_toc is not None:
                cache.set('c2_toc', c2_toc, timeout=CACHE_TIMEOUT)
                print "[+] C2 toc cache reset..."
            else:
                print "[-] Error in cache update"

    except Exception as err:
        message = 'compile_c2_toc exception: ', err.message
        current_app.logger.warning(message)


# vocab_dict, vocab_codes
@celery.task(name='tasks.compile_vocabulary')
def compile_vocabulary():
    try:
        with current_app.test_request_context():
            print "[+] Starting vocabulary cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            vocab_dict, vocab_codes = compile_vocab()
            if "error" not in vocab_dict:
                cache.set('vocab_dict', vocab_dict, timeout=CACHE_TIMEOUT)
                cache.set('vocab_codes', vocab_codes, timeout=CACHE_TIMEOUT)
                print "[+] Vocabulary cache reset"
            else:
                print "[-] Error in cache update"
    except Exception as err:
        message = 'compile_vocabulary exception: %s' % err.message
        current_app.logger.warning(message)


# large_format
@celery.task(name='tasks.compile_large_format_files')
def compile_large_format_files():
    try:
        with current_app.test_request_context():
            print "[+] Starting large format file cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)

            data = _compile_large_format_files()

            if "error" not in data:
                cache.set('large_format', data, timeout=CACHE_TIMEOUT)
                print "[+] large format files updated."
            else:
                print "[-] Error in large file format update"
    except Exception as err:
        message = 'compile_large_format_files exception: %s' % err.message
        current_app.logger.warning(message)


# asset information: asset_list, assets_dict, asset_types, asset_rds, rd_assets, bad_asset_list
@celery.task(name='tasks.compile_asset_information')
def compile_asset_information():
    try:
        print '\n debug - *** tasks - compile_asset_information()'
        with current_app.test_request_context():

            asset_list = verify_cache(refresh=True)
            print '\n Completed compiling asset information.'
            print '\n Number of assets: ', len(asset_list)

    except Exception as err:
        message = 'compile_assets exception: %s' % err.message
        current_app.logger.warning(message)
        raise Exception(message)


# - - - - - - - - - - - - - - - - - - - - -
'''
# disabled: glider_tracks
'get-glider-traks-every': {
        'task': 'tasks.compile_glider_tracks',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (),
        },

@celery.task(name='tasks.compile_glider_tracks')
def compile_glider_tracks():
    try:
        with current_app.test_request_context():
            print "[+] Starting glider tracks cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)

            glider_tracks = _compile_glider_tracks(True)

            if "error" not in glider_tracks:
                cache.set('glider_tracks', glider_tracks, timeout=CACHE_TIMEOUT)
                print "[+] Glider tracks cache reset."
            else:
                print "[-] Error in cache update"

    except Exception as err:
        message = 'compile_glider_tracks exception: %s' % err.message
        current_app.logger.warning(message)
'''