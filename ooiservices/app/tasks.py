
__author__ = 'M@Campbell'

from ooiservices.app import create_celery_app
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

'''
Define the list of processes to run either on a heartbeat or simply waiting for

'''

from ooiservices.app.uframe.assetController import _compile_assets
from ooiservices.app.uframe.assetController import _compile_events
from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.controller import _compile_glider_tracks


@celery.task(name='tasks.compile_assets')
def compile_assets():
    with current_app.test_request_context():
        print "[+] Starting asset cache reset..."
        cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
        cache.init_app(current_app)
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s' % ('assets')
        payload = requests.get(url)
        if payload.status_code is 200:
            data = payload.json()
            assets = _compile_assets(data)
            if "error" not in assets:
                cache.set('asset_list', assets, timeout=CACHE_TIMEOUT)
                print "[+] Asset cache reset"
            else:
                print "[-] Error in cache update"


@celery.task(name='tasks.compile_streams')
def compile_streams():
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


@celery.task(name='tasks.compile_events')
def compile_events():
    with current_app.test_request_context():
        print "[+] Starting events cache reset..."
        cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
        cache.init_app(current_app)

        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s' % ('events')
        payload = requests.get(url)
        if payload.status_code is 200:
            data = payload.json()
            events = _compile_events(data)

            if "error" not in events:
                cache.set('event_list', events, timeout=CACHE_TIMEOUT)
                print "[+] Events cache reset."
            else:
                print "[-] Error in cache update"


@celery.task(name='tasks.compile_glider_tracks')
def compile_glider_tracks():
    with current_app.test_request_context():
        print "[+] Starting glider tracks cache reset..."
        cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
        cache.init_app(current_app)

        glider_tracks = _compile_glider_tracks()

        if "error" not in glider_tracks:
            cache.set('glider_tracks', glider_tracks, timeout=CACHE_TIMEOUT)
            print "[+] Glider tracks cache reset."
        else:
            print "[-] Error in cache update"


@celery.task(name='tasks.compile_cam_images')
def compile_cam_images():
    with current_app.test_request_context():
        print "[+] Starting cam images cache reset..."
        cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
        cache.init_app(current_app)

        cam_images = []   #some imported function

        if "error" not in cam_images:
            cache.set('cam_images', cam_images, timeout=CACHE_TIMEOUT)
            print "[+] cam images cache reset."
        else:
            print "[-] Error in cache update"


