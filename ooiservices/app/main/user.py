#!/usr/bin/env python
'''
User API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, g
from ooiservices.app.main import api
from ooiservices.app import db, security
from ooiservices.app.main.authentication import auth, verify_auth
from ooiservices.app.models import User, UserScope, UserScopeLink, AuditTable
from ooiservices.app.decorators import scope_required
from ooiservices.app.redmine.routes import redmine_login
import json, smtplib, string
import datetime as dt
import pycountry
from operator import itemgetter
import string
import random

@api.route('/user/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    user = User.query.filter_by(id=id).first_or_404()
    return jsonify(user.to_json())

@api.route('/user/<int:id>', methods=['PUT'])
@auth.login_required
# @scope_required(u'user_admin')
def put_user(id):
    user_account = User.query.get(id)
    data = json.loads(request.data)
    user_name = data.get('user_name')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_primary = data.get('phone_primary')
    phone_alternate = data.get('phone_alternate')
    scopes = data.get('scopes')
    active = data.get('active')
    email_opt_in = data.get('email_opt_in')
    activating= User.query.get(id).active is False and active is True
    other_organization = data.get('other_organization')
    vocation = data.get('vocation')
    country = data.get('country')
    state = data.get('state')
    api_user_name = data.get('api_user_name')
    api_user_token = data.get('api_user_token')
    changed = False
    if first_name is not None:
        user_account.first_name = first_name
        changed = True
    if last_name is not None:
        user_account.last_name = last_name
        changed = True
    if phone_primary is not None:
        user_account.phone_primary = phone_primary
        changed = True
    if phone_alternate is not None:
        user_account.phone_alternate = phone_alternate
        changed = True
    if other_organization is not None:
        user_account.other_organization = other_organization
        changed = True
    if vocation is not None:
        user_account.vocation = vocation
        changed = True
    if country is not None:
        user_account.country = country
        changed = True
    if state is not None:
        user_account.state = state
        changed = True
    if api_user_name is not None:
        user_account.api_user_name = api_user_name
        changed = True
    if api_user_token is not None:
        user_account.api_user_token = api_user_token
        changed = True
        current_app.logger.info('User %s API token changed to %s by %s'%(user_name, user_account.api_user_token, g.current_user))
    if scopes is not None:
        valid_scopes = UserScope.query.filter(UserScope.scope_name.in_(scopes)).all()
        user_account.scopes = valid_scopes
        changed = True
        scope_change_info = 'User %s scope(s) changed to %s by %s'%(user_name, user_account.scopes, g.current_user)
        AuditTable.insert_audit_entry(audit_type=1, audit_user=g.current_user.id, audit_description=scope_change_info)
        current_app.logger.info('User %s scope(s) changed to %s by %s'%(user_name, user_account.scopes, g.current_user))

    if active is not None:
        user_account.active = bool(active)
        changed = True
        if activating is True:
            send_activate_email(data["email"])
    if email_opt_in is not None:
        user_account.email_opt_in = bool(email_opt_in)
        changed = True
    if changed:
        db.session.add(user_account)
        db.session.commit()
    return jsonify(**user_account.to_json()), 201

def send_activate_email(to):
    sender="help@ooi.rutgers.edu"
    subject="OOI Registration Complete"
    message=string.join(("From: %s" % sender,
                         "To: %s" % current_app.config["TOEMAIL"] if current_app.config["ENVIORNMENT"]=="LOCAL_DEVELOPMENT" else to,
                         "Subject: %s" % subject,
                         "Your registration to the Ocean Observatories Initiative WebPortal has been completed.",
                         " ",
                         " ",
                         "Please visit http://%s to login to the system" % current_app.config["SERVER_DNS"]),"\r\n")

    try:
        smtpObj=smtplib.SMTP("localhost")
        smtpObj.sendmail(sender,to,message)

    except:
        print "error sending mail"


def id_generator(size=14, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@api.route('/user_scopes')
@auth.login_required
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
        1: ['annotate', 'asset_manager', 'user_admin', 'redmine', 'annotate_admin', 'ingest', 'ingest_calibration'], # Administrator
        2: ['annotate', 'asset_manager'],                          # Marine Operator
        3: []                                                      # Science User
    }
    role_scopes = role_mapping[data['role_id']]
    valid_scopes = UserScope.query.filter(UserScope.scope_name.in_(role_scopes)).all()

    try:
        new_user = User.from_json(data)
        new_user.scopes = valid_scopes
        new_user.active = True
        new_user.api_user_name = 'OOIAPI-'+id_generator()
        new_user.api_user_token = 'TEMP-TOKEN-'+id_generator()
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify(error=e.message), 409

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


@api.route('/countries')
def get_countries():
    try:
        countries = [{"country_code" : country.alpha2.encode('utf8'), "country_name" : country.name.encode('utf8')} for country in pycountry.countries]
    except Exception:
        print 'unexpected'
        return json.dumps([{"country_code" : "US", "country_name" : "United States"}])

    # Sort
    try:
        countries = sorted(countries, key=itemgetter('country_name'))
    except Exception:
        pass

    return json.dumps(countries)

@api.route('/states/<string:country_code>')
def get_states(country_code):
    try:
        states = pycountry.subdivisions.get(country_code=country_code)
        states_json = [{"state_code" : state.code.encode('utf8'), "state_name" : state.name.encode('utf8')} for state in states]
    except Exception:
        current_app.logger.exception("Failed get states")
        return json.dumps([{"state_code" : "RI", "state_name" : "Rhode Island"}])

    # Sort
    try:
        states_json = sorted(states_json, key=itemgetter('state_name'))
    except Exception:
        pass

    return json.dumps(states_json)


@api.route('/user/xpassword', methods=['PUT'])
def put_password():

    try:
        data = json.loads(request.data)
        user_account = User.query.filter_by(user_name=data.get('_reset_email')).first_or_404()
        password = data.get('password')

        if password is not None:
            user_account.password = password
            db.session.add(user_account)
            db.session.commit()

        return jsonify(**user_account.to_json()), 201
    except Exception as ex:
        current_app.logger.exception("Error setting password." + ex.message)
        return


@api.route('/user/check_valid_email', methods=['GET'])
def check_valid_email():
    try:
        # print request.args.get('email')
        user_account = User.query.filter_by(user_name=request.args.get('email')).first_or_404()
        # print user_account
        user_id = user_account.user_id
        # print user_id
        if user_id is not None:
            return json.dumps({'email': user_id})

    except Exception as ex:
        # current_app.logger.exception("Error checking valid email." + ex.message)
        return json.dumps({'email': ''})