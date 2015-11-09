'''
Celery needs to have it's own Flask application in order to work correctly.

Create the new flask app, and use it to carry out the async tasks.
Other tasks that are added here may also need to initialize any
dependencies that it may need.

We cannot use the same config file for celery, as that would create a
circular import when trying to work with the main apps application
context.  All configuration should be placed here, so it does not
get confused with the main apps configuration.

This file should also maintain any cron tasks that may be needed.

In order to get results, access celery's result backend database using
the task id.

'''

__author__ = 'M@Campbell'

import os
import requests
from flask import Flask, request, url_for
from celery import Celery
from flask.ext.cache import Cache


'''
Import the application requirments
'''


from .uframe.assetController import convert_lat_lon
from .main.routes import\
    get_display_name_by_rd as get_dn_by_rd,\
    get_long_display_name_by_rd as get_ldn_by_rd,\
    get_assembly_by_rd

'''
Create the celery app, and configure it to talk to the redis broker.
Then intialize it.
'''
celery_app = Flask('__main__')

# Cache config
cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_DB': 0})
cache.init_app(celery_app)

# Celery configuration
celery_app.config['CELERY_BROKER_URL'] = os.environ.get('REDISCLOUD_URL') or \
    'redis://localhost:6379/0'
celery_app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDISCLOUD_URL') or \
    'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(celery_app.name, broker=celery_app.config['CELERY_BROKER_URL'])
celery.conf.update(celery_app.config)
celery.config_from_object('ooiservices.app.celeryconfig')

UFRAME_ASSETS_URL = 'http://ooiufs1.ooi.rutgers.edu:12573'
'''
Define the list of processes to run either on a heartbeat or simply waiting for

'''
def associate_events(id):
    '''
    When an individual asset is requested from GET(id) all the events for that
    asset need to be associated.  This is represented in a list of URIs, one
    for it's services endpoint and one for it's direct endpoint in uframe.
    '''
    uframe_url = UFRAME_ASSETS_URL + '/assets/%s/events' % (id)
    result = []
    payload = requests.get(uframe_url)
    if payload.status_code != 200:
        return [{ "error": "server responded with error code: %s" % payload.status_code }]

    json_data = payload.json()
    for row in json_data:
        try:
           
            d = {}
            # set up some static keys
            d['locationLonLat'] = []

            d['eventId'] = row['eventId']
            d['class'] = row['@class']
            d['notes'] = len(row['notes'])
            d['startDate'] = row['startDate']
            d['endDate'] = row['endDate']
            d['tense'] = row['tense']
            if d['class'] == '.CalibrationEvent':
                d['calibrationCoefficient'] = row['calibrationCoefficient']
                lon = 0.0
                lat = 0.0
                for cal_coef in d['calibrationCoefficient']:
                    if cal_coef['name'] == 'CC_lon':
                        lon = cal_coef['values']
                    if cal_coef['name'] == 'CC_lat':
                        lat = cal_coef['values']
                if lon is not None and lat is not None:
                    d['locationLonLat'] = convert_lat_lon(lat, lon)
            if d['class'] == '.DeploymentEvent':
                d['deploymentDepth'] = row['deploymentDepth']
                if row['locationLonLat']:
                    d['locationLonLat'] = convert_lat_lon(row['locationLonLat'][1], row['locationLonLat'][0])
                d['deploymentNumber'] = row['deploymentNumber']
        except KeyError:
            pass
        result.append(d)

	return result


@celery.task(name='tasks.compile_assets')
def compile_assets():
    with celery_app.app_context():
        url = UFRAME_ASSETS_URL + '/assets'
        payload = requests.get(url)

        data = payload.json()

        for row in data:
            latest_deployment = None
            lat = ""
            lon = ""
            ref_des = ""
            has_deployment_event = False
            deployment_number = ""
            try:
                row['id'] = row.pop('assetId')
                row['asset_class'] = row.pop('@class')
                row['events'] = associate_events(row['id'])
                if len(row['events']) == 0:
                    row['events'] = []
                row['tense'] = None
                if row['metaData'] is not None:
                    for meta_data in row['metaData']:
                        if meta_data['key'] == 'Latitude':
                            lat = meta_data['value']
                            coord = convert_lat_lon(lat, "")
                            meta_data['value'] = coord[0]
                        if meta_data['key'] == 'Longitude':
                            lon = meta_data['value']
                            coord = convert_lat_lon("", lon)
                            meta_data['value'] = coord[1]
                        if meta_data['key'] == 'Ref Des':
                            ref_des = meta_data['value']
                        if meta_data['key'] == 'Deployment Number':
                            deployment_number = meta_data['value']
                    row['ref_des'] = ref_des

                    if len(row['ref_des']) == 27:
                        row['asset_class'] = '.InstrumentAssetRecord'
                    if len(row['ref_des']) < 27:
                        row['asset_class'] = '.AssetRecord'

                    if deployment_number is not None:
                        row['deployment_number'] = deployment_number
                    for events in row['events']:
                        if events['class'] == '.DeploymentEvent':
                            has_deployment_event = True
                            if events['tense'] == 'PRESENT':
                                row['tense'] = events['tense']
                            else:
                                row['tense'] = 'PAST'
                        if latest_deployment is None and\
                                events['locationLonLat'] is not None and\
                                len(events['locationLonLat']) == 2:
                            latest_deployment = events['startDate']
                            lat = events['locationLonLat'][1]
                            lon = events['locationLonLat'][0]
                        if events['locationLonLat'] is not None and\
                                latest_deployment is not None and\
                                len(events['locationLonLat']) == 2 and\
                                events['startDate'] > latest_deployment:
                            latest_deployment = events['startDate']
                            lat = events['locationLonLat'][1]
                            lon = events['locationLonLat'][0]
                    row['hasDeploymentEvent'] = has_deployment_event
                    row['coordinates'] = convert_lat_lon(lat, lon)

                if (not(row['assetInfo'])):
                    row['assetInfo'] = {
                        'name': '',
                        'type': '',
                        'owner': '',
                        'description': ''
                    }

                # determine the asset name from the DB if there is none.
                if (not('name' in row['assetInfo']) and len(ref_des) > 0):
                    row['assetInfo']['name'] = get_dn_by_rd(ref_des) or ""
                    row['assetInfo']['longName'] = get_ldn_by_rd(ref_des)
                elif ('name' in row['assetInfo'] and len(ref_des) > 0):
                    row['assetInfo']['name'] = row['assetInfo']['name']\
                        or get_dn_by_rd(ref_des) or ""
                    row['assetInfo']['longName'] = get_ldn_by_rd(ref_des)
                else:
                    row['assetInfo']['name'] = ""
                    row['assetInfo']['longName'] = ""
                row['assetInfo']['array'] = get_dn_by_rd(ref_des[:2])
                row['assetInfo']['assembly'] = get_assembly_by_rd(ref_des)

            except Exception as e:
                print e
                continue

        print "setting cache..."
        cache.set('asset_list', data, timeout=3000)
        print cache.get('asset_list')
        return data
