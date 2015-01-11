'''
API v1.0 List

'''
__author__ = 'M.Campbell'

from flask import jsonify, request, current_app, url_for
from . import api
from ..models import Array, PlatformDeployment, InstrumentDeployment, Stream, StreamParameter


@api.route('/arrays/')
def get_arrays():
    arrays = Array.query.all()
    return jsonify( {'arrays' : [array.to_json() for array in arrays] })

@api.route('/arrays/<string:id>')
def get_array(id):
    array = Array.query.filter_by(array_code=id).first_or_404()
    return jsonify(array.to_json())

@api.route('/platform_deployments/')
def get_platform_deployments():
    platform_deployments = PlatformDeployment.query.all()
    return jsonify({ 'platform_deployments' : [platform_deployment.to_json() for platform_deployment in platform_deployments] })

@api.route('/platform_deployments/<string:id>')
def get_platform_deployment(id):
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=id).first_or_404()
    return jsonify(platform_deployment.to_json())

@api.route('/instrument_deployments/')
def get_instrument_deployments():
    instrument_deployments = InstrumentDeployment.query.all()
    return jsonify({ 'instrument_deployments' : [instrument_deployment.to_json() for platform_deployment in instrument_deployments] })

@api.route('/instrument_deployments/<string:id>')
def get_instrument_deployment(id):
    instrument_deployment = InstrumentDeployment.query.filter_by(reference_designator=id).first_or_404()
    return jsonify(instrument_deployment.to_json())

@api.route('/streams/')
def get_streams():
    streams = Stream.query.all()
    return jsonify({ 'streams' : [stream.to_json() for stream in streams] })

@api.route('/streams/<string:id>')
def get_stream(id):
    stream = Stream.query.filter_by(stream_name=id).first_or_404()
    return jsonify(stream.to_json())

@api.route('/parameters/')
def get_parameters():
    parameters = StreamParameter.query.all()
    return jsonify({ 'parameters' : [parameter.to_json() for parameter in parameters] })

@api.route('/parameters/<string:id>')
def get_parameter(id):
    parameter = StreamParameter.query.filter_by(parameter_name=id).first_or_404()
    return jsonify(parameter.to_json())