#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, make_response
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname
import json
import yaml
from wtforms import ValidationError

@api.route('/platform_deployments')
def get_platform_deployments():
    if 'array_id' in request.args:
        platform_deployments = \
        PlatformDeployment.query.filter_by(array_id=request.args['array_id']).order_by(PlatformDeployment.reference_designator).all()
    elif 'search' in request.args:
        platform_deployments = PlatformDeployment.query.whoosh_search(request.args['search'])
    else:
        platform_deployments = PlatformDeployment.query.all()
    return jsonify({ 'platform_deployments' : [platform_deployment.to_json() for platform_deployment in platform_deployments] })

@api.route('/platform_deployments/<string:id>')
def get_platform_deployment(id):
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=id).first_or_404()
    return jsonify(platform_deployment.to_json())

@api.route('/streams')
def get_streams():
    streams = Stream.query.all()
    return jsonify({ 'streams' : [stream.to_json() for stream in streams] })

@api.route('/streams/<string:id>')
def get_stream(id):
    stream = Stream.query.filter_by(stream_name=id).first_or_404()
    return jsonify(stream.to_json())

@api.route('/parameters')
def get_parameters():
    parameters = StreamParameter.query.all()
    return jsonify({ 'parameters' : [parameter.to_json() for parameter in parameters] })

@api.route('/parameters/<string:id>')
def get_parameter(id):
    parameter = StreamParameter.query.filter_by(stream_parameter_name=id).first_or_404()
    return jsonify(parameter.to_json())

@api.route('/organization', methods=['GET'])
def get_organizations():
    organizations = [o.serialize() for o in Organization.query.all()]
    return jsonify(organizations=organizations)

@api.route('/organization/<int:id>', methods=['GET'])
def get_organization_by_id(id):
    org = Organization.query.filter(Organization.id==id).first()
    if not org:
        return '{}', 204
    response = org.serialize()
    return jsonify(**response)

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

@api.route('/plotdemo', methods=['GET'])
def plotdemo():
    import matplotlib
    import matplotlib.pyplot as plt
    import io
    import numpy as np
    import time

    t0 = time.time()
    data = np.array([[2,2],
                     [8,8],
                     [1,3],
                     [2,4]])
    x = data[:,0]
    y = data[:,1]

    plt.title('SVG Plot')
    plt.xlabel('X/Time')
    plt.ylabel('Y/Value')
    plt.scatter(x, y)
    buf = io.BytesIO()

    plt.savefig(buf, format='svg')
    buf.seek(0)

    t1 = time.time()
    print "Response took %s seconds" % (t1 - t0)
    return buf.read(), 200, {'Content-Type':'image/svg+xml'}

    
