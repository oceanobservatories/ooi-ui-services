#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request
from ooiservices.app.main import api
from ooiservices.app.models import PlatformDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization
# from netCDF4 import num2date, date2index


@api.route('/platform_deployments')
def get_platform_deployments():
    if 'array_id' in request.args:
        platform_deployments = \
            PlatformDeployment.query.filter_by(array_id=request.args['array_id'])\
            .order_by(PlatformDeployment.reference_designator).all()
    elif 'search' in request.args:
        platform_deployments = PlatformDeployment\
            .query.whoosh_search(request.args['search'])
    else:
        platform_deployments = PlatformDeployment.query.all()
    return jsonify({'platform_deployments': [platform_deployment.to_json()
                    for platform_deployment in platform_deployments]})


@api.route('/platform_deployments/<string:id>')
def get_platform_deployment(id):
    platform_deployment = PlatformDeployment.\
        query.filter_by(reference_designator=id).first_or_404()
    return jsonify(platform_deployment.to_json())


@api.route('/organization', methods=['GET'])
def get_organizations():
    organizations = [o.serialize() for o in Organization.query.all()]
    return jsonify(organizations=organizations)


@api.route('/organization/<int:id>', methods=['GET'])
def get_organization_by_id(id):
    org = Organization.query.filter(Organization.id == id).first()
    if not org:
        return '{}', 204
    response = org.serialize()
    return jsonify(**response)


# todo review
@api.route('/streams')
def get_streams():
    streams = Stream.query.all()
    return jsonify({'streams': [stream.to_json() for stream in streams]})


@api.route('/streams/<string:id>')
def get_stream(id):
    stream = Stream.query.filter_by(stream_name=id).first_or_404()
    return jsonify(stream.to_json())


@api.route('/parameters')
def get_parameters():
    parameters = StreamParameter.query.all()
    return jsonify({'parameters': [parameter.to_json()
                    for parameter in parameters]})


@api.route('/parameters/<string:id>')
def get_parameter(id):
    parameter = StreamParameter.\
        query.filter_by(stream_parameter_name=id).first_or_404()
    return jsonify(parameter.to_json())
