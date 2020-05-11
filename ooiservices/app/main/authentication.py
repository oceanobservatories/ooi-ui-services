#!/usr/bin/env python
'''
API Authentication
'''

from flask import g, jsonify, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from flask_security import login_user
from ooiservices.app import db
from ooiservices.app.models import User
from ooiservices.app.main import api
from ooiservices.app.main.errors import unauthorized
from oauth import OAuthSignIn
import requests

auth = HTTPBasicAuth()

import uuid; str(uuid.uuid4().get_hex().upper()[0:6])


@auth.verify_password
def verify_password(email_or_token, password):
    return verify_auth(email_or_token, password)


def verify_auth(email_or_token, password):
    if email_or_token == '':
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter(User.user_name == email_or_token,
                             User.active == True).first()
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
    debug = False
    if debug:
        print('getting token')
        print(g.current_user)
        print(g.token_used)
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=86400), 'expiration': 86400})  # 24 hours


@api.route('/logged_in')
def logged_in():
    '''
    Checks the TOKEN not the user identity to see if it's current and valid.
    '''
    auth = request.authorization
    if not auth:
        return jsonify(valid=False)
    token, password = auth.username, auth.password
    if token and not password:
        user = User.verify_auth_token(token)
        return jsonify(valid=(user is not None))
    return jsonify(valid=False)


@api.route('/authorize/<provider>')
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@api.route('/callback/<provider>')
def oauth_callback(provider):
    debug = False
    # rand_pass will be a new password every time a user logs in
    # with oauth.
    temp_pass = str(uuid.uuid4())

    # lets create the oauth object that will issue the request.
    oauth = OAuthSignIn.get_provider(provider)

    # assign the response
    email, first_name, last_name, user_id, access_token = oauth.callback()
    if debug:
        print(email)
        print(access_token)
        email = None

    # TODO: CI Logon now says email, first and last name are optional,
    #  which means we need to prompt the user to enter and validate their email at this point...
    if email is None and user_id is None:
        print('Why did we get in here? Invalid credentials because no user_id or email was found.')
        return unauthorized('Invalid credentials')

    # see if this user already exists, and
    # and give the user a brand new password.
    if email is not None:
        user = User.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(user_id=user_id).first()
    if debug:
        print('user')
        print(user)
    
    # Find existing user account using the email address
    if user:
        # Assign temporary password
        user.password = temp_pass
        if email is None:
            # Assign the user_id given by CILogon if missing
            user.user_id = user_id
            user.user_name = user_id
    else:
        # This is a new user
        # Create a new one and setup
        # it's defaults and give it a new password.
        if email is None and user.email is None:
            # Using user_id to set up user since email wasn't supplied
            user = User.insert_user(password=temp_pass,
                                    username=user_id,
                                    email=user_id,
                                    user_id=user_id,
                                    first_name='Anonymous',
                                    last_name='Anonymous')
        else:
            user = User.insert_user(password=temp_pass,
                                    username=email,
                                    email=email,
                                    user_id=user_id,
                                    first_name=first_name,
                                    last_name=last_name)

    if email is None:
        login_user(user, True)
        return jsonify({'uuid': temp_pass, 'username': user_id, 'user_id': user_id, 'user_db_id': user.id})
    else:
        #login_user(user, True)
        return jsonify({'uuid': temp_pass, 'username': email, 'user_id': user_id})

