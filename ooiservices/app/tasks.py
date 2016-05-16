
__author__ = 'M@Campbell'

from ooiservices.app import create_celery_app
from ooiservices.app.main.c2 import _compile_c2_toc
from flask.globals import current_app
import requests
from flask.ext.cache import Cache


CACHE_TIMEOUT = 172800

'''
Create the celery app, and configure it to talk to the redis broker.
Then intialize it.
'''

celery = create_celery_app('PRODUCTION')
celery.config_from_object('ooiservices.app.celeryconfig')

"""
Define the list of processes to run either on a heartbeat or simply waiting for

"""

from ooiservices.app.uframe.assetController import _compile_assets
from ooiservices.app.uframe.assetController import _compile_events
from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.controller import _compile_glider_tracks
from ooiservices.app.uframe.controller import _compile_cam_images
from ooiservices.app.uframe.controller import _compile_large_format_files


@celery.task(name='tasks.compile_assets')
def compile_assets():
    try:
        with current_app.test_request_context():
            print "[+] Starting asset cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            url = current_app.config['UFRAME_ASSETS_URL'] + '/assets'
            payload = requests.get(url)
            if payload.status_code is 200:
                data = payload.json()
                assets = _compile_assets(data)
                if "error" not in assets:
                    cache.set('asset_list', assets, timeout=CACHE_TIMEOUT)
                    print "[+] Asset cache reset"
                else:
                    print "[-] Error in cache update"
    except Exception as err:
        message = 'compile_assets exception: %s' % err.message
        current_app.logger.warning(message)


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


@celery.task(name='tasks.compile_events')
def compile_events():
    try:
        with current_app.test_request_context():
            print "[+] Starting events cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)

            url = current_app.config['UFRAME_ASSETS_URL'] + '/events'
            payload = requests.get(url)
            if payload.status_code is 200:
                data = payload.json()
                events = _compile_events(data)

                if "error" not in events:
                    cache.set('event_list', events, timeout=CACHE_TIMEOUT)
                    print "[+] Events cache reset."
                else:
                    print "[-] Error in cache update"
    except Exception as err:
        message = 'compile_cam_images exception: %s' % err.message
        current_app.logger.warning(message)


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

"""
'get-large-format-files-every': {
        'task': 'tasks.compile_large_format_files',
        'schedule': crontab(minute=0, hour='*/12'),
        'args': (),
        },
"""
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
