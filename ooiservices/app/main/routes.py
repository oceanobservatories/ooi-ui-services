#!/usr/bin/env python
"""
API v1.0 List
"""
__author__ = 'M@Campbell'

from flask import jsonify
from ooiservices.app.main import api
from ooiservices.app.models import Organization


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Organization
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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