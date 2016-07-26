
__author__ = 'M@Campbell'

from ooiservices.app import create_celery_app
from flask.globals import current_app
from flask.ext.cache import Cache


CACHE_TIMEOUT = 172800

'''
Create the celery app, and configure it to talk to the redis broker.
Then initialize it.
'''

celery = create_celery_app('PRODUCTION')
celery.config_from_object('ooiservices.app.celeryconfig')

"""
Define the list of processes to run either on a heartbeat or simply waiting for
Caches created/utilized:

For data visualization:
  stream_list
  cam_images*
  large_format*

For vocabulary:
  vocab_dict
  vocab_codes

For Command and Control (C2):
  c2_toc

Deprecated:
  event_list

Disabled for now:
  glider_tracks

Remove (For assets):
  asset_list
  assets_dict
  asset_types
  asset_rds
  rd_assets
  bad_asset_list

* not yet covered in verify cache

vocab_dict
vocab_codes
stream_list

"""

from ooiservices.app.uframe.controller import dfs_streams
from ooiservices.app.uframe.controller import _compile_cam_images
from ooiservices.app.uframe.controller import _compile_large_format_files
from ooiservices.app.main.c2 import _compile_c2_toc
from ooiservices.app.uframe.vocab import compile_vocab


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

# - - - - - - - - - - - - - - - - - - - - -
"""
import requests

#from ooiservices.app.uframe.assetController import _compile_assets, _compile_bad_assets
#from ooiservices.app.uframe.asset_tools import _compile_asset_rds, get_assets_dict_from_list, _compile_rd_assets
from ooiservices.app.uframe.controller import _compile_glider_tracks
from ooiservices.app.uframe.assetController import _compile_events
"""
'''
'get-rd-assets': {
        'task': 'tasks.compile_rd_asset',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
'get-assets-rd': {
        'task': 'tasks.compile_asset_rds',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-assets': {
        'task': 'tasks.compile_assets',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },
    'get-bad-assets': {
        'task': 'tasks.compile_bad_assets',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': (),
        },

@celery.task(name='tasks.compile_assets')
def compile_assets():
    try:
        print '\n debug - *** tasks - compile_assets()'
        with current_app.test_request_context():
            print "[+] Starting asset cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % ('asset')
            payload = requests.get(url)
            if payload.status_code is 200:

                # Cache assets_list
                data = payload.json()
                assets, asset_rds = _compile_assets(data)
                if "error" not in assets:
                    cache.set('asset_list', assets, timeout=CACHE_TIMEOUT)
                    print "[+] Asset list cache reset"

                    # Cache assets_dict (based on success of _compile_assets returning assets)
                    assets_dict = get_assets_dict_from_list(assets)
                    if not assets_dict:
                        message = 'Warning: get_assets_dict_from_list returned empty assets_dict.'
                        print '\n debug -- message: ', message
                        current_app.logger.info(message)
                    if isinstance(assets_dict, dict):
                        cache.set('assets_dict', assets_dict, timeout=CACHE_TIMEOUT)
                        print "[+] Assets dictionary cache reset"
                    else:
                        print "[-] Error in Assets dictionary cache update"
                else:
                    print "[-] Error in asset_list and asset_dict cache update"

                # Cache assets_rd
                if asset_rds:
                    cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
                    print "[+] Asset reference designators cache reset..."
                    print '\n len(asset_rds): ', len(asset_rds)
                else:
                    print "[-] Error in asset_rds cache update"

            else:
                print "[-] Error in cache update"
    except Exception as err:
        message = 'compile_assets exception: %s' % err.message
        current_app.logger.warning(message)
        raise Exception(message)


@celery.task(name='tasks.compile_asset_rds')
def compile_assets_rd():
    try:
        asset_rds = {}
        rds_wo_assets = []
        rds = []
        with current_app.test_request_context():
            print "[+] Starting asset reference designators cache reset..."

            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            try:
                asset_rds, rds_wo_assets, rds = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

        if asset_rds:
            cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
            print "[+] Asset reference designators cache reset..."
        else:
            print "[-] Error in cache update"

        """
        # List of reference designators [in toc i.e./sensor/inv/toc] but without associated asset id(s). TODO Remove this...
        if rds_wo_assets:
            cache.set('rds_wo_assets', rds_wo_assets, timeout=CACHE_TIMEOUT)
            print "[+] Reference designators with assets cache reset..."
        else:
            print "[-] Error in rds_wo_assets cache update..."
        """

        """
        # List of reference designators [in toc]. TODO Remove this...
        if rds:
            cache.set('toc_rds', rds, timeout=CACHE_TIMEOUT)
            print "[+] Reference designators (in toc) cache reset..."
        else:
            print "[-] Error in toc_rds cache update..."
        """

    except Exception as err:
        message = 'compile_asset_rds exception: %s' % err.message
        current_app.logger.warning(message)
        raise Exception(message)
'''
'''
@celery.task(name='tasks.compile_bad_assets')
def compile_bad_assets():
    try:
        with current_app.test_request_context():
            print "[+] Starting bad asset cache reset..."
            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            url = current_app.config['UFRAME_ASSETS_URL'] + '/assets'
            payload = requests.get(url)
            if payload.status_code is 200:
                data = payload.json()
                bad_assets = _compile_bad_assets(data)
                if "error" not in bad_assets:
                    cache.set('bad_asset_list', bad_assets, timeout=CACHE_TIMEOUT)
                    print "[+] Bad asset cache reset"
                else:
                    print "[-] Error in cache update"
    except Exception as err:
        message = 'compile_bad_assets exception: %s' % err.message
        current_app.logger.warning(message)
'''
'''
@celery.task(name='tasks.compile_rd_assets')
def compile_rd_assets():
    """ Get 'rd_assets' dictionary.
    Key: reference designator, returns associated asset ids and deployments map.
    """
    try:
        rd_assets = {}
        with current_app.test_request_context():
            print "[+] Starting reference designators assets cache reset..."

            cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
            cache.init_app(current_app)
            try:
                rd_assets  = _compile_rd_assets()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                current_app.logger.warning(message)

        if rd_assets:
            cache.set('rd_assets', rd_assets, timeout=CACHE_TIMEOUT)
            print "[+] Reference designators asset cache reset..."
        else:
            print "[-] Error in cache update"

    except Exception as err:
        message = 'compile_rd_assets exception: %s' % err.message
        current_app.logger.warning(message)
        raise Exception(message)
'''

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

'''
#deprecated: events
'get-events': {
        'task': 'tasks.compile_events',
        'schedule': crontab(minute=0, hour='*/10'),
        'args': (),
        },

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
'''



