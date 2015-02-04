#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import User, UserScope, UserScopeLink
from ooiservices.app.decorators import scope_required
import json
from wtforms import ValidationError

@api.route('/user/<string:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    user = User.query.filter_by(user_name=id).first_or_404()
    return jsonify(user.to_json())

@api.route('/user/<string:id>', methods=['PUT'])
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
def get_user_scopes():
    user_scopes = UserScope.query.all()
    return jsonify( {'user_scopes' : [user_scope.to_json() for user_scope in user_scopes] })

@api.route('/user', methods=['GET'])
@auth.login_required
def get_current_user():
    '''
    Returns the currently logged in user
    '''
    doc = g.current_user.to_json()
    return jsonify(**doc)

@api.route('/user', methods=['POST'])
@auth.login_required
def create_user():
    data = json.loads(request.data)
    try:
        new_user = User.from_json(data)
        db.session.add(new_user)
        db.session.commit()
    except ValidationError as e:
        return jsonify(error=e.message), 409
    return jsonify(new_user.to_json()), 201

@api.route('/user_roles')
@auth.login_required
def get_user_roles():
    user_roles = {"user_roles": [{"id": 1, "role_name": "Administrator"}, {"id": 2, "role_name": "Marine Operator"}, {"id": 3, "role_name": "Science User"}]}
    return jsonify(user_roles)

@api.route('/users')
@auth.login_required
@scope_required(u'user_admin')
def get_users():
    users = [u.to_json() for u in User.query.all()]
    return jsonify(users=users)
    
