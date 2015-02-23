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
from ooiservices.app.decorators import json

@api.route('/search/platform_deployments/<string:id>')
@auth.login_required
@json
def search_pds_display_name(id):
    platform_deployments = PlatformDeployment.query.whoosh_search(id)
    return { 'search_results' : [platform_deployment.to_json() for platform_deployment in platform_deployments] }

@api.route('/search/organizations/<string:id>')
@auth.login_required
@json
def search_orgs_display_name(id):
    organizations = Organization.query.whoosh_search(id)
    return { 'search_results' : [organization.to_json() for organization in organizations] }

@api.route('/search/users/<string:id>')
@auth.login_required
@json
def search_users_display_name(id):
    users = User.query.whoosh_search(id)
    return { 'search_results' : [user.to_json() for user in users] }
