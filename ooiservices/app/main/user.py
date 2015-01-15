#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from . import api
from authentication import auth
from ..models import User, UserScope, UserScopeLink

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

@api.route('/user_scope_links')
@auth.login_required
def get_user_scope_links():
    user_scope_links = UserScopeLink.query.all()
    return jsonify( {'user_scope_links' : [user_scope_link.to_json() for user_scope_link in user_scope_links] })

@api.route('/user/', methods=['POST'])
@auth.login_required
def create_user():
    new_user = User.from_json(request.json)
    db.session.add(new_user)
    db.session.commit()
    return True