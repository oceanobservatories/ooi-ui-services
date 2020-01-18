
__author__ = 'M@Campbell'

from ooiservices.app import create_celery_app
from flask.globals import current_app
from flask_caching import Cache
from ooiservices.app.uframe.config import get_cache_timeout


"""
Create the celery app, and configure it to talk to the redis broker.
Then initialize it.
"""

celery = create_celery_app('PRODUCTION')
celery.config_from_object('ooiservices.app.celeryconfig')


from ooiservices.app.main.c2 import _compile_c2_toc
from ooiservices.app.uframe.vocab import compile_vocab
from ooiservices.app.uframe.stream_tools import (get_stream_list, get_instrument_list)
from ooiservices.app.uframe.status_tools import get_uid_digests
from ooiservices.app.uframe.asset_tools import verify_cache
from ooiservices.app.uframe.toc_tools import compile_toc_reference_designators
from ooiservices.app.uframe.image_tools import (_compile_cam_images, _compile_large_format_files,
                                                _compile_large_format_index)


# 'cam_images'
@celery.task(name='tasks.compile_cam_images')
def compile_cam_images():
    """ Create thumbnail images for UI, updating 'cam_images' cache.
    """
    try:
        with current_app.test_request_context():
            print '[+] Starting cam images cache reset...'
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            cam_images = _compile_cam_images()
            if cam_images and cam_images is not None and 'error' not in cam_images:
                print '[+] cam images cache reset.'
            else:
                print '[-] Error in cache update'
    except Exception as err:
        message = 'compile_cam_images exception: %s' % err.message
        current_app.logger.warning(message)


# large_format
@celery.task(name='tasks.compile_large_format_files')
def compile_large_format_files():
    """ Create data server index for various file types, updating 'large_format' cache.
    """
    try:
        with current_app.test_request_context():
            print '[+] Starting large format file cache reset...'
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            data = _compile_large_format_files()
            if data and data is not None and 'error' not in data:
                print '[+] large format files updated.'
            else:
                print '[-] Error in large file format update'
    except Exception as err:
        message = 'compile_large_format_files exception: %s' % str(err)
        current_app.logger.warning(message)


@celery.task(name='tasks.compile_large_format_index')
def compile_large_format_index():
    """ Create data server index for various file types..
    """
    try:
        with current_app.test_request_context():
            print '[+] Starting large format index cache reset...'
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            data = _compile_large_format_index()
            if data and data is not None and 'error' not in data:
                print '[+] Large format index updated.'
            else:
                print '[-] Error in large file index update.'
    except Exception as err:
        message = 'compile_large_format_index exception: %s' % str(err)
        current_app.logger.warning(message)


# (c2_toc)
@celery.task(name='tasks.compile_c2_toc')
def compile_c2_toc():
    try:
        c2_toc = None
        with current_app.test_request_context():
            print '[+] Starting c2 toc cache reset...'
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            try:
                c2_toc = _compile_c2_toc()
            except Exception as err:
                message = 'Error processing compile_c2_toc: ', err.message
                current_app.logger.warning(message)
            if c2_toc and c2_toc is not None and 'error' not in c2_toc:
                cache.delete('c2_toc')
                cache.set('c2_toc', c2_toc, timeout=get_cache_timeout())
                print '[+] C2 toc cache reset.'
            else:
                print '[-] Error in cache update.'

    except Exception as err:
        message = 'Exception: compile_c2_toc: ', str(err)
        current_app.logger.warning(message)


# (vocab_dict, vocab_codes)
@celery.task(name='tasks.compile_vocabulary')
def compile_vocabulary():
    try:
        with current_app.test_request_context():
            print '[+] Starting vocabulary cache reset...'
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            vocab_dict, vocab_codes = compile_vocab()
            if vocab_dict and vocab_dict is not None and 'error' not in vocab_dict and \
               vocab_codes and vocab_codes is not None and 'error' not in vocab_codes:
                cache.delete('vocab_dict')
                cache.set('vocab_dict', vocab_dict, timeout=get_cache_timeout())
                cache.delete('vocab_codes')
                cache.set('vocab_codes', vocab_codes, timeout=get_cache_timeout())
                print '[+] Vocabulary cache reset.'
            else:
                print '[-] Error in vocabulary cache update.'
    except Exception as err:
        message = 'compile_vocabulary exception: %s' % err.message
        current_app.logger.warning(message)


# (stream_list and instrument_list)
@celery.task(name='tasks.compile_streams')
def compile_streams():
    try:
        with current_app.test_request_context():
            print '[+] Starting stream cache reset...'
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)

            # Compile stream cache ('stream_list')
            streams = get_stream_list(refresh=True)
            if streams and streams is not None and 'error' not in streams:
                stream_cache = cache.get('stream_list')
                if stream_cache and stream_cache is not None and 'error' not in stream_cache:
                    print '[+] Stream cache reset.'
                else:
                    message = '[-] Failed to reset stream cache.\n'
                    print message
                    raise Exception(message)

            # Compile instruments cache ('instrument_list')
            instruments = get_instrument_list(refresh=True)
            if instruments and instruments is not None and 'error' not in instruments:
                instrument_cache = cache.get('instrument_list')
                if instrument_cache and instrument_cache is not None and 'error' not in instrument_cache:
                    print '[+] Instrument cache reset.'
                else:
                    message = '[-] Failed to reset instrument cache.\n'
                    print message
                    raise Exception(message)
    except Exception as err:
        message = 'Exception compiling instrument_list or stream_list cache: %s' % err.message
        current_app.logger.warning(message)


# (uid_digests)
@celery.task(name='tasks.compile_uid_digests')
def compile_uid_digests():
    try:
        with current_app.test_request_context():
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            uid_digests = get_uid_digests(refresh=True)
    except Exception as err:
        message = 'Exception compiling uframe uid digests: %s' % err.message
        current_app.logger.warning(message)
        raise Exception(message)


# (asset_list, assets_dict) Get asset information.
@celery.task(name='tasks.compile_asset_information')
def compile_asset_information():
    try:
        with current_app.test_request_context():
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            asset_list = verify_cache(refresh=True)
    except Exception as err:
        message = 'compile_assets exception: %s' % err.message
        current_app.logger.warning(message)
        raise Exception(message)


# Get toc reference designators
@celery.task(name='tasks.compile_toc_rds')
def compile_toc_rds():
    try:
        with current_app.test_request_context():
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            rds = compile_toc_reference_designators()
            if rds and rds is not None and 'error' not in rds:
                print '[+] TOC reference designators cache reset.'
            else:
                message = '[-] Failed to reset TOC reference designators cache.\n'
                print message
                raise Exception(message)
    except Exception as err:
        message = 'compile_toc_rds exception: %s' % err.message
        current_app.logger.warning(message)
        raise Exception(message)


# - - - - - - - - - - - - - - - - - - - - -
'''
# Disabled: glider_tracks
'get-glider-traks-every': {
        'task': 'tasks.compile_glider_tracks',
        'schedule': crontab(minute=0, hour='*/8'),
        'args': (),
        },

@celery.task(name='tasks.compile_glider_tracks')
def compile_glider_tracks():
    try:
        with current_app.test_request_context():
            print '[+] Starting glider tracks cache reset...'
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)

            glider_tracks = _compile_glider_tracks(True)

            if 'error' not in glider_tracks:
                cache.delete('glider_tracks')
                cache.set('glider_tracks', glider_tracks, timeout=get_cache_timeout())
                print '[+] Glider tracks cache reset.'
            else:
                print '[-] Error in cache update.'

    except Exception as err:
        message = 'compile_glider_tracks exception: %s' % err.message
        current_app.logger.warning(message)
'''

