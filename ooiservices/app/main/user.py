#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import User, UserScope, UserScopeLink, UserRole
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

        try:
            role = UserRole.query.filter(UserRole.id==data['role_id']).first()
            if role:
                scope_ids = [s.user_scope.id for s in role.scopes]
                for scope_id in scope_ids:
                    scope = UserScopeLink(user_id=new_user.id, scope_id=scope_id)
                    db.session.add(scope)
                db.session.commit()

        except Exception as e:
            print e.message
            return jsonify(error="Invalid Role Selection"), 409



    except ValidationError as e:
        return jsonify(error=e.message), 409
    return jsonify(new_user.to_json()), 201

@api.route('/user_roles')
@auth.login_required
def get_user_roles():
    user_roles = UserRole.query.all()
    return jsonify( {'user_roles' : [user_role.to_json() for user_role in user_roles] })
