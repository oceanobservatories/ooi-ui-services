#!/usr/bin/env python
'''
uframe endpoints

'''
__author__ = 'Andy Bird'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname

from ooiservices.app.uframe.data import gen_data

import json
import datetime

'''
@api.route('/get_data')
def get_data():
    start_time = request.args.get('start_time', '2015-01-01')
    end_time = request.args.get('end_time', '2015-01-01T01:00')
    norm = request.args.get('norm', 13)
    std_dev = request.args.get('std', 3)
    sampling_rate = request.args.get('sampling_rate', 1)
    response = gen_data(start_time, end_time, sampling_rate, norm, std_dev)
    return jsonify(**response)
'''

def get_uframe_data():
    '''
    stub mock function to get some sample data
    '''
    json_data=open('ooiservices/tests/sampleData.json')
    data = json.load(json_data)
    return data

@api.route('/get_data')
def get_data():
    #get data from uframe
    data = get_uframe_data()
    #create the data fields,assumes the same data fields throughout
    d_row = data[0]
    data_fields = []
    some_data = []
    #time minus ()
    cosmo_constant = 2208988800
    time_idx = -1
    for field in d_row:
        if field == "preferred_timestamp" or field == u'stream_name' or field == u'driver_timestamp':
            pass
        else:
            data_fields.append(field)

    for d in data:
        r = []
        for field in data_fields:
            if field.endswith("_timestamp"):
                r.append(d[field] - cosmo_constant)
                if field == "internal_timestamp":
                    time_idx = len(r)-1
            else:
                r.append(d[field])
        some_data.append(r)

    #genereate dict for the data thing
    resp_data = {}
    resp_data['cols'] = data_fields
    resp_data['rows'] = some_data
    resp_data['size'] = len(some_data)
    resp_data['start_time'] = datetime.datetime.fromtimestamp((some_data[0][time_idx])).isoformat()
    resp_data['end_time'] = datetime.datetime.fromtimestamp((some_data[-1][time_idx])).isoformat()
    return jsonify(**resp_data)

@api.route('/platformlocation', methods=['GET'])
def get_platform_deployment_geojson_single():
    geo_locations = {}
    if len(request.args) > 0:
        if ('reference_designator' in request.args):
            if len(request.args['reference_designator']) < 100:
                reference_designator = request.args['reference_designator']
                geo_locations = PlatformDeployment.query.filter(PlatformDeployment.reference_designator == reference_designator).all()
    else:
        geo_locations = PlatformDeployment.query.all()
    if len(geo_locations) == 0:
        return '{}', 204
    return jsonify({ 'geo_locations' : [{'id' : geo_location.id, 'reference_designator' : geo_location.reference_designator, 'geojson' : geo_location.geojson} for geo_location in geo_locations] })

@api.route('/display_name', methods=['GET'])
def get_display_name():
    # 'CE01ISSM-SBD17'
    platform_deployment_filtered = None
    display_name = ''
    if len(request.args) > 0:
        if ('reference_designator' in request.args):
            if len(request.args['reference_designator']) < 100:
                reference_designator = request.args['reference_designator']
                platform_deployment_filtered = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
                display_name = platform_deployment_filtered.proper_display_name
    if platform_deployment_filtered is None:
        return '{}', 204
    return jsonify({ 'proper_display_name' : display_name })