#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import User, UserScope, UserScopeLink
import json
from wtforms import ValidationError

@api.route('/user/<string:id>')
@auth.login_required
def get_user(id):
    user = User.query.filter_by(user_name=id).first_or_404()
    return jsonify(user.to_json())

@api.route('/user_scopes')
@auth.login_required
def get_user_scopes():
    user_scopes = UserScope.query.all()
    return jsonify( {'user_scopes' : [user_scope.to_json() for user_scope in user_scopes] })

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