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
import json, smtplib, string
import datetime as dt
import pycountry

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
    email_opt_in = data.get('email_opt_in')
    activating= User.query.get(id).active is False and active is True
    other_organization = data.get('other_organization')
    changed = False
    if other_organization is not None:
        user_account.other_organization = other_organization
        changed = True
    if scopes is not None:
        valid_scopes = UserScope.query.filter(UserScope.scope_name.in_(scopes)).all()
        user_account.scopes = valid_scopes
        changed = True
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
    except Exception as e:
        return jsonify(error=e.message), 409

    try:
        redmine = redmine_login()
        organization = new_user.organization.organization_name
        tmp = dt.datetime.now() + dt.timedelta(days=1)
        due_date = dt.datetime.strftime(tmp, "%Y-%m-%d")
        issue = redmine.issue.new()
        issue.project_id = current_app.config['REDMINE_PROJECT_ID']
        issue.subject = 'New User Registration for OOI UI: %s, %s' % (new_user.first_name, new_user.last_name)
        issue.description = 'A new user has requested access to the OOI User Interface. Please review the application for %s, their role in the organization %s is %s and email address is %s' % (new_user.first_name, organization, new_user.role, new_user.email)
        issue.priority_id = 1
        issue.due_date = due_date
        # Get the list of ticker Trackers
        trackers = list(redmine.tracker.all())
        # Find the REDMINE_TRACKER (like 'Support') and get the id
        # This make a difference for field validation and proper tracker assignment
        config_redmine_tracker = current_app.config['REDMINE_TRACKER']
        tracker_id = [tracker.id for tracker in trackers if tracker.name == config_redmine_tracker][0]
        issue.tracker_id = tracker_id
        issue.save()
    except Exception as e:
        current_app.logger.exception("Failed to generate redmine issue for new user")
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
    countries = [{"country_code" : country.alpha2.encode('utf8'), "country_name" : country.name.encode('utf8')} for country in pycountry.countries]
    return json.dumps(countries)


@api.route('/states/<string:country_code>')
def get_states(country_code):
    states = pycountry.subdivisions.get(country_code=country_code)
    states_json = [{"state_code" : state.code.encode('utf8'), "state_name" : state.name.encode('utf8')} for state in states]
    return json.dumps(states_json)

