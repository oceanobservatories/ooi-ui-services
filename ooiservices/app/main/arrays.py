#!/usr/bin/env python
'''
Arrays endpoints

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import Array
from ooiservices.app.main.errors import conflict
from ooiservices.app.decorators import scope_required
import json

#List all arrays
@api.route('/arrays')
def get_arrays():
    arrays = Array.query.all()
    return jsonify( {'arrays' : [array.to_json() for array in arrays] })

#List a single array
@api.route('/arrays/<string:id>')
def get_array(id):
    array = Array.query.filter_by(array_code=id).first_or_404()
    return jsonify(array.to_json())

#Add a new array
@api.route('/arrays/', methods=['POST'])
@auth.login_required
def create_array():
    try:
        array = Array.from_json(request.json)
        db.session.add(array)
        db.session.commit()
        return jsonify(array.to_json()), 201
    except:
        return conflict('Insufficient data, or bad data format')

#Edit an existing array
@api.route('/arrays/<int:id>', methods=['PUT'])
@auth.login_required
def update_array(id):
    try:
        array = Array.query.get_or_404(id)
        array.array_code = request.json.get('array_code', array.array_code)
        array.description = request.json.get('description', array.description)
        array.geo_location = request.json.get('geo_location', array.geo_location)
        array.array_name = request.json.get('array_name', array.array_name)
        array.display_name = request.json.get('display_name', array.display_name)
        db.session.add(array)
        db.session.commit()
        return jsonify(array.to_json())
    except:
        return conflict('Insufficient data, or bad data format')

#Delete an existing array
@api.route('/arrays/<int:id>', methods=['DELETE'])
@auth.login_required
@scope_required('administrator')
def delete_array(id):
    array = Array.query.get_or_404(id)
    db.session.delete(array)
    db.session.commit()
    return jsonify({'message': 'Array deleted!', 'id': id})