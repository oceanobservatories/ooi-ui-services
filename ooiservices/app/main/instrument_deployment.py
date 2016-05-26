#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import InstrumentDeployment, Instrumentname
from ooiservices.app.decorators import scope_required
from ooiservices.app import cache
import json

@cache.memoize(timeout=3600)
@api.route('/instrument_deployment', methods=['GET'])
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

@cache.memoize(timeout=3600)
@api.route('/instrument_deployment/<int:id>', methods=['GET'])
def get_instrument_deployment(id):
    instrument_deployment = InstrumentDeployment.query.get(id)
    if instrument_deployment is None:
        return jsonify(error="Instrument Deployment Not Found"), 404
    return jsonify(**instrument_deployment.to_json())

@auth.login_required
@api.route('/instrument_deployment', methods=['POST'])
def post_instrument_deployment():
    try:
        data = json.loads(request.data)
        new_deploy = InstrumentDeployment.from_json(data)
        db.session.add(new_deploy)
        db.session.commit()
    except Exception as e:
        return jsonify(error=e.message), 400
    return jsonify(**new_deploy.to_json()), 201

@auth.login_required
@api.route('/instrument_deployment/<int:id>', methods=['PUT'])
def put_instrument_deployment(id):
    try:
        data = json.loads(request.data or {})
        existingDeply = InstrumentDeployment.query.get(id)
        if existingDeply is None:
            return jsonify(error="Invalid ID, record not found"), 404
        existingDeply.display_name = data.get('display_name', existingDeply.display_name)
        existingDeply.start_date = data.get('start_date', existingDeply.start_date)
        existingDeply.end_date = data.get('end_date', existingDeply.end_date)
        existingDeply.platform_deployment_id = data.get('platform_deployment_id', existingDeply.platform_deployment_id)
        existingDeply.depth = data.get('depth', existingDeply.depth)
        existingDeply.geo_location = data.get('geo_location', existingDeply.geo_location)
        db.session.add(existingDeply)
        db.session.commit()
    except Exception as e:
        return jsonify(error=e.message), 400
    return jsonify(**existingDeply.to_json()), 200

@api.route('/instrument_deployment/<int:id>', methods=['DELETE'])
@auth.login_required
@scope_required('asset_manager')
def delete_instrument_deployment(id):
    deployment = InstrumentDeployment.query.get(id)
    if deployment is None:
        return jsonify(error="Instrument Deployment Not Found"), 404
    db.session.delete(deployment)
    db.session.commit()
    return jsonify(), 200
