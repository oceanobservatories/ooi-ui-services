#!/usr/bin/env python
'''
API Authentication
'''

from flask import g, jsonify, request
from flask.ext.httpauth import HTTPBasicAuth
from ooiservices.app.models import User
from ooiservices.app.main import api
from ooiservices.app.main.errors import unauthorized, forbidden
from ooiservices.app.decorators import scope_required

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(user_name=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.route('/token')
@auth.login_required
def get_token():
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})

@api.route('/logged_in')
def logged_in():
    '''
    Checks the TOKEN not the user identity to see if it's current and valid.
    '''
    auth = request.authorization
    token, password = auth.username, auth.password
    if token and not password:
        user = User.verify_auth_token(token)
        return jsonify(valid=(user is not None))
    return jsonify(valid=False)
