#!/usr/bin/python
'''
Search routes.
'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, make_response
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import PlatformDeployment, Organization, User

@auth.login_required
@api.route('/search/platform_deployments')
def search_pds_display_name():
    if 'display_name' in request.args:
        platform_deployments = PlatformDeployment.query.whoosh_search(request.args['display_name'])
    else:
        return jsonify({ 'platform_deployments' : [{'search_fields': 'display_name', 'example': '/search/platform_deployments?display_name=Mooring'}]})
    return jsonify({ 'platform_deployments' : [platform_deployment.to_json() for platform_deployment in platform_deployments] })

@api.route('/search/organizations')
def search_orgs_display_name():
    if 'organization_name' in request.args:
        organizations = Organization.query.whoosh_search(request.args['organization_name'])
    else:
        return jsonify({ 'organizations' : [{'search_fields': 'organization_name', 'example': '/search/organizations?organization_name=ASA'}]})
    return jsonify({ 'organizations' : [organization.to_json() for organization in organizations] })

@api.route('/search/users')
def search_users_display_name():
    if 'user_name' in request.args:
        users = User.query.whoosh_search(request.args['user_name'])
    else:
        return jsonify({ 'users' : [{'search_fields': 'user_name', 'example': '/search/users?user_name=admin'}]})
    return jsonify({ 'users' : [user.to_json() for user in users] })