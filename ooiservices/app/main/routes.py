#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, make_response
from ooiservices.app.main import api
from ooiservices.app import db, cache
from authentication import auth
from ooiservices.app.models import PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname
import json
import yaml
from wtforms import ValidationError
# from netCDF4 import num2date, date2index

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

def get_display_name_by_rd(reference_designator):

    #this is a dirty hack....
    glider_hack = False
    number = ""
    if "MOAS-GL" in reference_designator:
        splits = reference_designator.split("MOAS-GL")
        number = splits[-1]
        reference_designator = splits[0]+"MOAS-GL"+"001"
        glider_hack= True

    if len(reference_designator) <= 14:
        platform_deployment_filtered = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
        if platform_deployment_filtered is None:
            return None
        display_name = platform_deployment_filtered.proper_display_name
    elif len(reference_designator) == 27:
        instrument_class = reference_designator[18:18+5]
        instrument_name = Instrumentname.query.filter_by(instrument_class=instrument_class).first()
        if 'ENG' in instrument_class or instrument_class == '00000':
            instrument_name = 'Engineering'
        elif instrument_name is None:
            instrument_name = reference_designator[18:]
        else:
            instrument_name = instrument_name.display_name

        display_name = instrument_name
    else:
        return None

    if glider_hack:
        display_name = display_name.replace('001',number)

    return display_name

def get_long_display_name_by_rd(reference_designator):
    if len(reference_designator) <= 14:
        platform_deployment_filtered = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first()
        if platform_deployment_filtered is None:
            return None
        display_name = platform_deployment_filtered.proper_display_name
    elif len(reference_designator) == 27:
        platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator[:14]).first()
        if platform_deployment is None:
            return None
        platform_display_name = platform_deployment.proper_display_name
        instrument_class = reference_designator[18:18+5]
        instrument_name = Instrumentname.query.filter_by(instrument_class=instrument_class).first()
        if 'ENG' in instrument_class or instrument_class == '00000':
            instrument_name = 'Engineering'
        elif instrument_name is None:
            instrument_name = reference_designator[18:]
        else:
            instrument_name = instrument_name.display_name

        display_name = ' - '.join([platform_display_name, instrument_name])
    else:
        return None
    return display_name

def get_platform_display_name_by_rd(reference_designator):
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator[:14]).first()
    if platform_deployment is None:
        return None
    platform_display_name = platform_deployment.proper_display_name

    return platform_display_name
@api.route('/display_name', methods=['GET'])
def get_display_name():
    # 'CE01ISSM-SBD17'
    reference_designator = request.args.get('reference_designator')
    if not reference_designator:
        return '{}', 204

    display_name = get_display_name_by_rd(reference_designator)
    if not display_name:
        return '{}', 204

    return jsonify({ 'proper_display_name' : display_name })
