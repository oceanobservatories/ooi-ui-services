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
@api.route('/search/platform_deployments/display_name/<string:id>')
def search_pds_display_name(id):
    platform_deployments = PlatformDeployment.query.whoosh_search(id)
    return jsonify({ 'search_results' : [platform_deployment.to_json() for platform_deployment in platform_deployments] })

@auth.login_required
@api.route('/search/organizations/organization_name/<string:id>')
def search_orgs_display_name(id):
    organizations = Organization.query.whoosh_search(id)
    return jsonify({ 'search_results' : [organization.to_json() for organization in organizations] })

@auth.login_required
@api.route('/search/users/<string:id>')
def search_users_display_name(id):
    users = User.query.whoosh_search(id)
    return jsonify({ 'search_results' : [user.to_json() for user in users] })
