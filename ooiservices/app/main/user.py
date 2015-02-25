#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth, verify_auth
from ooiservices.app.models import User, UserScope, UserScopeLink
from ooiservices.app.decorators import scope_required
from ooiservices.app.redmine.routes import redmine_login
import json
from wtforms import ValidationError
#from base64 import b64encode
#import requests
from redmine import Redmine

@api.route('/user/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    user = User.query.filter_by(id=id).first_or_404()
    return jsonify(user.to_json())

@api.route('/user/<int:id>', methods=['PUT'])
@auth.login_required
@scope_required(u'user_admin')
def put_user(id):
    user_account = User.query.get(id)
    data = json.loads(request.data)
    scopes = data.get('scopes')
    active = data.get('active')
    changed = False
    if scopes is not None:
        valid_scopes = UserScope.query.filter(UserScope.scope_name.in_(scopes)).all()
        user_account.scopes = valid_scopes
        changed = True
    if active is not None:
        user_account.active = bool(active)
        changed = True
    if changed:
        db.session.add(user_account)
        db.session.commit()
    return jsonify(**user_account.to_json()), 201

@api.route('/user_scopes')
@auth.login_required
@scope_required(u'user_admin')
def get_user_scopes():
    user_scopes = UserScope.query.all()
    return jsonify( {'user_scopes' : [user_scope.to_json() for user_scope in user_scopes] })

@api.route('/current_user', methods=['GET'])
@auth.login_required
def get_current_user():
    '''
    Returns the currently logged in user
    '''
    doc = g.current_user.to_json()
    return jsonify(**doc)

@api.route('/user', methods=['POST'])
def create_user():
    '''
    Requires either a CSRF token shared between the UI and the Services OR an
    authenticated request from a valid user.
    '''
    csrf_token = request.headers.get('X-Csrf-Token')
    if not csrf_token or csrf_token != current_app.config['UI_API_KEY']:
        auth = False
        if request.authorization:
            auth = verify_auth(request.authorization['username'], request.authorization['password'])
        if not auth:
            return jsonify(error="Invalid Authentication"), 401
    data = json.loads(request.data)
    #add user to db
    role_mapping = {
        1: ['annotate', 'asset_manager', 'user_admin', 'redmine'], # Administrator
        2: ['annotate', 'asset_manager'],                          # Marine Operator
        3: []                                                      # Science User
    }
    role_scopes = role_mapping[data['role_id']]
    valid_scopes = UserScope.query.filter(UserScope.scope_name.in_(role_scopes)).all()

    try:
        new_user = User.from_json(data)
        new_user.scopes = valid_scopes
        db.session.add(new_user)
        db.session.commit()
    except ValidationError as e:
        return jsonify(error=e.message), 409

    try:
        redmine = redmine_login()
        organization = new_user.organization.organization_name
        issue = redmine.issue.new()
        issue.project_id = current_app.config['REDMINE_PROJECT_ID']
        issue.subject = 'New User Registration for OOI UI: %s, %s' % (new_user.first_name, new_user.last_name)
        issue.description = 'A new user has requested access to the OOI User Interface. Please review the application for %s, their role in the organization %s is %s and email address is %s' % (new_user.first_name, organization, new_user.role, new_user.email)
        issue.priority_id = 1
        issue.save()
    except:
        current_app.logger.exception("Failed to generate redmine issue for new user")

    return jsonify(new_user.to_json()), 201

@api.route('/user_roles')
def get_user_roles():
    user_roles = {"user_roles": [{"id": 1, "role_name": "Administrator"}, {"id": 2, "role_name": "Marine Operator"}, {"id": 3, "role_name": "Science User"}]}
    return jsonify(user_roles)

@api.route('/user')
@auth.login_required
@scope_required(u'user_admin')
def get_users():
    users = [u.to_json() for u in User.query.all()]
    return jsonify(users=users)
