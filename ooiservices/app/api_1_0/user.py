#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'M.Campbell'

from flask import jsonify, request, current_app, url_for
from . import api
from authentication import auth
from ..models import User

@api.route('/user/<string:id>')
@auth.login_required
def get_user(id):
    user = User.query.filter_by(user_name=id).first_or_404()
    return jsonify(user.to_json())