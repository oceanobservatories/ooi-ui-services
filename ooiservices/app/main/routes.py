#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname
import json
import yaml
from wtforms import ValidationError


@api.route('/arrays')
def get_arrays():
    arrays = Array.query.all()
    return jsonify( {'arrays' : [array.to_json() for array in arrays] })

@api.route('/arrays/', methods=['POST'])
@auth.login_required
def set_array():
    array = Array.from_json(request.json)
    db.session.add(array)
    db.session.commit()
    return jsonify(array.to_json())

@api.route('/arrays/<string:id>')
def get_array(id):
    array = Array.query.filter_by(array_code=id).first_or_404()
    return jsonify(array.to_json())

@api.route('/platform_deployments')
def get_platform_deployments():
    if 'array_id' in request.args:
        platform_deployments = \
        PlatformDeployment.query.filter_by(array_id=request.args['array_id']).order_by(PlatformDeployment.reference_designator).all()
    else:
        platform_deployments = PlatformDeployment.query.all()
    return jsonify({ 'platform_deployments' : [platform_deployment.to_json() for platform_deployment in platform_deployments] })

@api.route('/platform_deployments/<string:id>')
def get_platform_deployment(id):
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=id).first_or_404()
    return jsonify(platform_deployment.to_json())

@api.route('/instrument_deployments', methods=['GET'])
def get_instrument_deployments():
    if 'platform_deployment_id' in request.args:
        instrument_deployments = \
        InstrumentDeployment.query.filter_by(platform_deployment_id=request.args['platform_deployment_id']).all()
        # TODO: Actually link the tables
        for i_d in instrument_deployments:
            instrument_name = Instrumentname.query.filter(Instrumentname.instrument_class == i_d.display_name).first()
            if instrument_name:
                i_d.display_name = instrument_name.display_name
    else:
        instrument_deployments = InstrumentDeployment.query.all()
    return jsonify({ 'instrument_deployments' : [instrument_deployment.to_json() for instrument_deployment in instrument_deployments] })

@api.route('/instrument_deployments/<string:id>', methods=['GET'])
def get_instrument_deployment(id):
    instrument_deployment = InstrumentDeployment.query.filter_by(reference_designator=id).first_or_404()
    return jsonify(instrument_deployment.to_json())

@api.route('/instrument_deployments', methods=['POST'])
@api.route('/instrument_deployments', methods=['PUT'])
def submit_deployment():
    '''
    Acts as a pass-thru proxy to to the services
    '''
    #csrf_token = session.pop('_csrf_token', None)
    #data = json.loads(request.data)
    #removes unicode
    data = yaml.load(request.data)

    # check for delete for delete
    #temp
    if 'delete' in data:
        try:
            existingDeply = InstrumentDeployment.query.filter_by(id=data['id']).first_or_404()
            db.session.delete(existingDeply)
            db.session.commit()
        except ValidationError as e:
            return jsonify(error=e.message), 409
    # check for existing id for edit
    elif 'id' in data:
        try:
            existingDeply = InstrumentDeployment.query.filter_by(id=data['id']).first_or_404()
            existingDeply.display_name = data['display_name']
            existingDeply.start_date = data['start_date']
            existingDeply.end_date = data['end_date']
            existingDeply.platform_deployment_id = data['platform_deployment_id']
            existingDeply.depth = data['depth']
            existingDeply.geo_location = data['geo_location']        
            db.session.commit()
        except ValidationError as e:
            return jsonify(error=e.message), 409
    else:
        #if not csrf_token or csrf_token != data['_csrf_token']:
        #    return jsonify(error="CSRF Error"), 401
        #api_key = app.config['UI_API_KEY']
        try:
            new_deploy = InstrumentDeployment.from_json(data)
            db.session.add(new_deploy)
            db.session.commit()
        except ValidationError as e:
            return jsonify(error=e.message), 409

    return "success", 204

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
