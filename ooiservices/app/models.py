#!/usr/bin/env python
'''
OOI Models
'''

__author__ = 'M@Campbell'

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy.sql import expression
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.sqlalchemy import BaseQuery
from ooiservices.app import db, login_manager
from flask.ext.security import UserMixin, RoleMixin
from flask_security.utils import encrypt_password, verify_password as fs_verify_password
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import ValidationError
from geoalchemy2.types import Geometry

from sqlalchemy_utils.types import TSVectorType
from datetime import datetime
import geoalchemy2.functions as func
import json

#--------------------------------------------------------------------------------

from collections import OrderedDict

class DictSerializableMixin(object):
    def serialize(self):
        return self._asdict()

    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = self._pytype(getattr(self, key))
        return result

    def _pytype(self, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v


#--------------------------------------------------------------------------------

class QueryMixin(BaseQuery, SearchQueryMixin):
    pass

#--------------------------------------------------------------------------------

__schema__ = 'ooiui'

class Annotation(db.Model, DictSerializableMixin):
    __tablename__ = 'annotations'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    reference_designator = db.Column(db.Text)
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)
    created_time = db.Column(db.DateTime(True), nullable=False, server_default=db.text("now()"))
    start_time = db.Column(db.DateTime(True), nullable=False)
    end_time = db.Column(db.DateTime(True), nullable=False)
    retired = db.Column(db.Boolean, server_default=expression.false())
    # Because we rely on uFrame, there won't be any sort of consistency checks.
    # We will be doing application level JOINs and if the stream_name doesn't
    # match a value from uFrame the record will be unaccounted for.
    stream_name = db.Column(db.Text())
    description = db.Column(db.Text())
    stream_parameter_name = db.Column(db.Text())

    user = db.relationship(u'User')

    @classmethod
    def from_dict(cls,data):
        rdict = {}
        rdict['reference_designator'] = data.get('reference_designator')
        rdict['user_id'] = data.get('user_id')
        rdict['start_time'] = data.get('start_time')
        rdict['end_time'] = data.get('end_time')
        rdict['stream_parameter_name'] = data.get('stream_parameter_name')
        rdict['description'] = data.get('description')

        # We would prefer the database generate this
        if 'created_time' in data:
            rdict['created_time'] = data.get('created_time')

        rdict['stream_name'] = data.get('stream_name')
        instance = cls(**rdict)
        return instance


class Array(db.Model):
    __tablename__ = 'arrays'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer(), primary_key=True)
    array_code = db.Column(db.Text())
    description = db.Column(db.Text())
    geo_location = db.Column(Geometry(geometry_type='GEOMETRY', srid=-1, dimension=2, spatial_index=True, management=True))
    array_name = db.Column(db.Text())
    display_name = db.Column(db.Text())

    def to_json(self):
        geo_location = None
        if self.geo_location is not None:
            geo_location = json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geo_location)))
        json_array = {
            'id' : self.id,
            'array_code' : self.array_code,
            'description' : self.description,
            'geo_location' : geo_location,
            'array_name' : self.array_name,
            'display_name' : self.display_name
        }
        return json_array

    @staticmethod
    def from_json(json_post):
        array_code = json_post.get('array_code')
        description = json_post.get('description')
        geo_location = json_post.get('geo_location')
        array_name = json_post.get('array_name')
        display_name = json_post.get('display_name')
        return Array(array_code=array_code, description=description, \
        geo_location=geo_location, array_name=array_name, display_name=display_name)


class File(db.Model):
    __tablename__ = 'files'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    file_name = db.Column(db.Text, nullable=False)
    file_system_path = db.Column(db.Text)
    file_size = db.Column(db.Text)
    file_permissions = db.Column(db.Text)
    file_type = db.Column(db.Text)


class LogEntry(db.Model):
    query_class = QueryMixin
    __tablename__ = 'log_entries'
    __table_args__ = {u'schema':__schema__}

    id = db.Column(db.Integer, primary_key=True)
    log_entry_type = db.Column(db.Text, nullable=False)
    entry_time = db.Column(db.DateTime(True), nullable=False, server_default=db.text("now()"))
    entry_title = db.Column(db.Text, nullable=False)
    entry_description = db.Column(db.Text)
    retired = db.Column(db.Boolean, server_default=expression.false())
    search_vector = db.Column(TSVectorType('entry_title', 'entry_description'))
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)
    organization_id = db.Column(db.ForeignKey(u'' + __schema__ + '.organizations.id'), nullable=False)

    user = db.relationship(u'User')
    organization = db.relationship(u'Organization')

    def to_json(self):
        return {
            'id' : self.id,
            'log_entry_type' : self.log_entry_type,
            'entry_time' : self.entry_time.isoformat(),
            'entry_title' : self.entry_title,
            'entry_description' : self.entry_description,
            'user' : {
                'id' : self.user_id,
                'first_name' : self.user.first_name,
                'last_name' : self.user.last_name
            },
            'organization' : {
                'id' : self.organization_id,
                'name' : self.organization.organization_name,
                'long_name' : self.organization.organization_long_name
            }
        }

    @classmethod
    def from_dict(cls, data):
        entry = cls()
        entry.log_entry_type = data.get('log_entry_type', 'INFO')
        if 'entry_title' not in data:
            raise ValueError('entry_title required to create LogEntry')
        entry.entry_title = data.get('entry_title')
        if 'entry_time' in data:
            entry.entry_time = data.get('entry_time')
        entry.entry_description = data.get('entry_description')
        entry.user_id = data.get('user_id')
        entry.organization_id = data.get('organization_id')
        return entry


class LogEntryComment(db.Model):
    __tablename__ = 'log_entry_comments'
    __table_args__ = {u'schema':__schema__}

    id = db.Column(db.Integer, primary_key=True)
    comment_time = db.Column(db.DateTime(True), nullable=False, server_default=db.text("now()"))
    comment = db.Column(db.Text)
    retired = db.Column(db.Boolean, server_default=expression.false())
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)
    log_entry_id = db.Column(db.ForeignKey(u'' + __schema__ + '.log_entries.id'), nullable=False)

    user = db.relationship(u'User')
    log_entry = db.relationship(u'LogEntry')

    def to_json(self):
        return {
            'id': self.id,
            'comment_time' : self.comment_time.isoformat(),
            'comment' : self.comment,
            'user' : {
                'id' : self.user.id,
                'name' : ' '.join([self.user.first_name, self.user.last_name])
            },
            'log_entry_id' : self.log_entry_id
        }

    @classmethod
    def from_dict(cls, data):
        comment = cls()
        if 'comment_time' in data:
            comment.comment_time = data.get('comment_time')
        comment.comment = data.get('comment')
        comment.user_id = data.get('user_id')
        comment.log_entry_id = data.get('log_entry_id')
        return comment


class OperatorEventType(db.Model, DictSerializableMixin):
    __tablename__ = 'operator_event_types'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.Text, nullable=False)
    type_description = db.Column(db.Text)

    def to_json(self):
        json_operator_event_type_link = {
            'id' : self.id,
            'type_name' : self.type_name,
            'type_description' : self.type_description
        }
        return json_operator_event_type_link

    @staticmethod
    def insert_operator_event_types():
       event_info = OperatorEventType(type_name='INFO')
       event_info.type_description = 'General information event.'
       event_warn = OperatorEventType(type_name='WARN')
       event_warn.type_description = 'A warning has occurred.'
       event_error = OperatorEventType(type_name='ERROR')
       event_error.type_description = 'An error has occurred.'
       event_critical = OperatorEventType(type_name='CRITICAL')
       event_critical.type_description = 'A critical event has occurred.'
       event_start_watch = OperatorEventType(type_name='WATCH_START')
       event_start_watch.type_description = 'Watch has started.'
       event_end_watch = OperatorEventType(type_name='WATCH_END')
       event_end_watch.type_description = 'Watch has ended.'

       db.session.add_all([event_info, event_warn, event_error, event_critical, event_start_watch, event_end_watch])
       db.session.commit()


class OperatorEvent(db.Model, DictSerializableMixin):
    __tablename__ = 'operator_events'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    watch_id = db.Column(db.ForeignKey(u'' + __schema__ + '.watches.id'), nullable=False)
    operator_event_type_id = db.Column(db.ForeignKey(u'' + __schema__ + '.operator_event_types.id'), nullable=False)
    event_time = db.Column(db.DateTime(True), nullable=False, server_default=db.text("now()"))
    event_title = db.Column(db.Text, nullable=False)
    event_comment = db.Column(db.Text)

    operator_event_type = db.relationship(u'OperatorEventType')

    @staticmethod
    def from_json(json):
        watch_id = json.get('watch_id')
        operator_event_type_id = json.get('operator_event_type_id')
        event_time = json.get('event_time')
        event_title = json.get('event_title')
        event_comment = json.get('event_comment')

        #Return the OperatorEvent object ready to be stored.
        return OperatorEvent(watch_id=watch_id,
                             operator_event_type_id=operator_event_type_id,
                             event_time=event_time,
                             event_title=event_title,
                             event_comment=event_comment)


class Organization(db.Model, DictSerializableMixin):
    __tablename__ = 'organizations'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.Text, nullable=False)
    organization_long_name = db.Column(db.Text)
    image_url = db.Column(db.Text)

    users = db.relationship(u'User')

    @staticmethod
    def insert_org():
        org = Organization.query.filter(Organization.organization_name == 'RPS ASA').first()
        if org is None:
            org = Organization(organization_name = 'RPS ASA')
            db.session.add(org)
            db.session.commit()


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   DisabledStreams
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class DisabledStreams(db.Model):
    __tablename__ = 'disabledstreams'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    ref_des = db.Column(db.Text, unique=True, nullable=False)
    stream_name = db.Column(db.Text)
    disabled_by = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(True))

    def to_json(self):
        json_disabled_streams = {
            'id': self.id,
            'refDes': self.ref_des,
            'streamName': self.stream_name,
            'disabledBy': self.disabled_by,
            'timestamp': self.timestamp
            }
        return json_disabled_streams

    @staticmethod
    def from_json(json_post):
        ref_des = json_post.get('refDes')
        stream_name = json_post.get('streamName')
        disabled_by = json_post.get('disabledBy')
        return DisabledStreams(ref_des=ref_des, stream_name=stream_name, disabled_by=disabled_by)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Users Classes:
#   UserScopeLink
#   UserScope
#   RolesUsers
#   Role
#   User
#   Watch
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class UserScopeLink(db.Model):
    __tablename__ = 'user_scope_link'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)
    scope_id = db.Column(db.ForeignKey(u'' + __schema__ + '.user_scopes.id'), nullable=False)

    scope = db.relationship(u'UserScope')
    user = db.relationship(u'User')

    @staticmethod
    def insert_scope_link():
        usl = UserScopeLink(user_id='1')
        usl.scope_id = '1'
        db.session.add(usl)
        db.session.commit()

    def to_json(self):
        json_scope_link = {
            'id' : self.id,
            'user_id' : self.user_id,
            'scope_id' : self.scope_id,
        }
        return json_scope_link

    def __repr__(self):
        return '<User %r, Scope %r>' % (self.user_id, self.scope_id)


class UserScope(db.Model, DictSerializableMixin):
    __tablename__ = 'user_scopes'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    scope_name = db.Column(db.Text, nullable=False, unique=True)
    scope_description = db.Column(db.Text)

    @staticmethod
    def insert_scopes():
        scopes = {
            'redmine',
            'asset_manager',
            'user_admin',
            'annotate',
            'command_control',
            'organization',
            'sys_admin',
            'data_manager'
            }
        for s in scopes:
            scope = UserScope.query.filter_by(scope_name=s).first()
            if scope is None:
                scope = UserScope(scope_name=s)
            db.session.add(scope)
        db.session.commit()

    def to_json(self):
        json_scope = {
            'id' : self.id,
            'scope_name' : self.scope_name,
            'scope_description' : self.scope_description,
        }
        return json_scope

    def __repr__(self):
        return '<Scope ID: %r, Scope Name: %s>' % (self.id, self.scope_name)


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)
    role_id = db.Column(db.ForeignKey(u'' + __schema__ + '.roles.id'), nullable=False)

    roles = db.relationship(u'Role')
    users = db.relationship(u'User')


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # roles_users = db.relationship(u'RolesUsers')

import string
import random
def id_generator(size=14, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    _password = db.Column(db.String(255), nullable=False)
    user_name = db.Column(db.Text, unique=True, nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    phone_primary = db.Column(db.Text)
    phone_alternate = db.Column(db.Text)
    role = db.Column(db.Text)
    email_opt_in = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    organization_id = db.Column(db.ForeignKey(u'' + __schema__ + '.organizations.id'), nullable=False)
    scopes = db.relationship(u'UserScope', secondary=UserScopeLink.__table__)
    organization = db.relationship(u'Organization')
    watches = db.relationship(u'Watch')
    other_organization = db.Column(db.Text)
    vocation = db.Column(db.Text)
    country = db.Column(db.Text)
    state = db.Column(db.Text)
    roles = db.relationship(u'Role', secondary=RolesUsers.__table__, backref=db.backref('users', lazy='dynamic'))
    api_user_name = db.Column(db.Text)
    api_user_token = db.Column(db.Text)

    def to_json(self):
        json_user = {
            'id' : self.id,
            'user_id' : self.user_id,
            'email' : self.email,
            'active' : self.active,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
            'phone_primary' : self.phone_primary,
            'phone_alternate' : self.phone_alternate,
            'role' : self.role,
            'organization_id' : self.organization_id,
            'scopes' : [s.scope_name for s in self.scopes],
            'user_name' : self.user_name,
            'email_opt_in' : self.email_opt_in,
            'other_organization' : self.other_organization,
            'vocation' : self.vocation,
            'country' : self.country,
            'state' : self.state,
            'api_user_name' : self.api_user_name,
            'api_user_token' : self.api_user_token
        }
        if self.organization:
            json_user['organization'] = self.organization.organization_name
        return json_user

    @staticmethod
    def from_json(json):
        email = json.get('email')
        password = json.get('password')
        password2 = json.get('repeatPassword')
        phone_primary = json.get('phone_primary')
        phone_alternate = json.get('phone_alternate')
        first_name = json.get('first_name')
        last_name = json.get('last_name')
        role = json.get('role_name')
        organization_id = json.get('organization_id')
        email_opt_in = json.get('email_opt_in')
        other_organization = json.get('other_organization')
        vocation = json.get('vocation')
        country = json.get('country')
        state = json.get('state')
        api_user_name = json.get('api_user_name')
        api_user_token = json.get('api_user_token')

        #Validate some of the field.
        new_user = User()
        new_user.validate_email(email)
        new_user.validate_password(password, password2)

        #All passes, return the User object ready to be stored.
        return User(email=email,
                    password=password,
                    phone_primary=phone_primary,
                    phone_alternate=phone_alternate,
                    user_name=email,
                    user_id=email,
                    first_name=first_name,
                    last_name=last_name,
                    organization_id=organization_id,
                    role=role,
                    email_opt_in=email_opt_in,
                    other_organization=other_organization,
                    vocation=vocation,
                    country=country,
                    state=state,
                    api_user_name=api_user_name,
                    api_user_token=api_user_token)


    @staticmethod
    def insert_user(username='admin',
                    password=None,
                    first_name='First',
                    last_name='Last',
                    email='FirstLast@somedomain.com',
                    org_name='RPS ASA',
                    phone_primary='8001234567',
                    other_organization=None,
                    api_user_name=None,
                    api_user_token=None):
        try:
            user = User()
            user.password = password
            user.validate_username(username)
            user.validate_email(email)
            user.user_name = username
            user.email = email
            user.user_id = username
            user.first_name = first_name
            user.last_name = last_name
            user.phone_primary = phone_primary
            user.active = True
            user.email_opt_in = True
            org = Organization.query.filter(Organization.organization_name == org_name).first()
            user.organization_id = org.id
            if org.id == 9:
                user.other_organization = other_organization
            if api_user_name:
                user.api_user_name = api_user_name
            else:
                user.api_user_name = 'OOIAPI-'+id_generator()
            if api_user_token:
                user.api_user_token = api_user_token
            else:
                user.api_user_token = id_generator()
            db.session.add(user)
            db.session.commit()
            current_app.logger.info('[+] New user created: %s' % user.email)
            return user
        except Exception as e:
            current_app.logger.info('[!] Error inserting user!')
            current_app.logger.info('[!] %s' % e)
            db.session.rollback()
            raise

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, plaintext):
        self._password = encrypt_password(plaintext)

    def verify_password(self, password):
        try:
            return check_password_hash(self._password, password)
        except TypeError:
            return fs_verify_password(password, self._password)

    @staticmethod
    def api_verify_token(api_user_name, api_user_token):
        if User.query.filter_by(api_user_name=api_user_name, api_user_token=api_user_token).first():
            return True

    def validate_email(self, field):
        if User.query.filter_by(email=field).first():
            raise ValidationError('Email already in use.')

    def validate_username(self, field):
        if User.query.filter_by(user_name=field).first():
            raise ValidationError('User name already taken.')

    def validate_password(self, password, password2):
        temp_hash = User(password=password)
        if not temp_hash.verify_password(password2):
            raise ValidationError('Passwords do not match')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def can(self, scope):
        #db.session.query
        return scope in [s.scope_name for s in self.scopes]

    def __repr__(self):
        return '<User: %r, ID: %r>' % (self.user_name, self.id)


class Watch(db.Model, DictSerializableMixin):
    __tablename__ = 'watches'
    __table_args__ = {u'schema' : __schema__}

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)

    user = db.relationship(u'User')
    operator_events = db.relationship(u'OperatorEvent')

    def to_json(self):
        data = self.serialize()
        del data['user_id']
        data['user'] = {
            'first_name': self.user.first_name,
            'last_name' : self.user.last_name,
            'email' : self.user.email
        }
        return data

    @staticmethod
    def from_json(json_post):
        id = json_post.get('id')
        start_time = json_post.get('start_time')
        end_time = json_post.get('end_time')
        user_id = json_post.get('user_id')
        return Watch(id=id, start_time=start_time, end_time=end_time, user_id=user_id)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Alerts and Alarms Classes:
#   SystemEventDefinition
#   SystemEvent
#   UserEventNotification
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SystemEventDefinition(db.Model):
    """
    Stores the definition for a single Alert or Alarm.

    operator:           Valid uframe values: 'GREATER', 'LESS', 'BETWEEN_EXCLUSIVE', 'OUTSIDE_EXCLUSIVE'
    retired:            boolean, defaults to False; variable set programmatically - not by user interface
    escalate_on:        amt of time, after the first alert occurred, to create a redmine ticket; units: seconds
    escalate_boundary:  amt of time, after ts_escalated, to create another red mine ticket (reissue) (units: seconds)

    Proposed:
    eventReceiptDelta: (int) used (by admin) to provide control to throttle excess uframe topic generation (jms issue)
    """
    __tablename__ = 'system_event_definitions'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    uframe_filter_id = db.Column(db.Integer, nullable=False)
    reference_designator = db.Column(db.Text, nullable=False)
    array_name = db.Column(db.Text, nullable=False)
    platform_name = db.Column(db.Text, nullable=False)
    instrument_name = db.Column(db.Text, nullable=False)
    instrument_parameter = db.Column(db.Text, nullable=False)
    instrument_parameter_pdid = db.Column(db.Text, nullable=False)
    operator = db.Column(db.Text, nullable=False)
    created_time = db.Column(db.DateTime(True), nullable=False)
    event_type = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    description = db.Column(db.Text, nullable=True)
    high_value = db.Column(db.Text, nullable=False)
    low_value = db.Column(db.Text, nullable=False)
    severity = db.Column(db.Integer, nullable=False)
    stream = db.Column(db.Text, nullable=False)
    retired = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    ts_retired = db.Column(db.DateTime(True), nullable=True)
    escalate_on = db.Column(db.Float, nullable=False)
    escalate_boundary = db.Column(db.Float, nullable=False)
    event_receipt_delta = db.Column(db.Integer, nullable=False, server_default=db.text("0"))

    @staticmethod
    def delete_system_event_definition(system_event_definition_id):
        status = None
        try:
            if system_event_definition_id is None:
                message = 'system_event_definition id provided is None.'
                raise Exception(message)
            definition = db.session.query.get(system_event_definition_id)
            if definition is None:
                message = 'Failed to delete system_event_definition for id provided (id: None)'
                raise Exception(message)

            notification = UserEventNotification.query.filter_by(system_event_definition_id=definition.id).first()
            if notification is not None:
                db.session.delete(notification)
                db.session.commit()
            db.session.delete(definition)
            db.session.commit()
            return status
        except:
            raise

    def to_json(self):
        tmp = self.stream
        if '_' in self.stream:
            tmp = self.stream.replace('_', '-')
        json_system_event_definition = {
            'id' : self.id,
            'uframe_filter_id': self.uframe_filter_id,
            'reference_designator': self.reference_designator,
            'array_name': self.array_name,
            'platform_name': self.platform_name,
            'instrument_name': self.instrument_name,
            'instrument_parameter': self.instrument_parameter,
            'instrument_parameter_pdid': self.instrument_parameter_pdid,
            'operator': self.operator,
            'created_time': self.created_time,
            'event_type': self.event_type,
            'active': self.active,
            'description': self.description,
            'high_value': self.high_value,
            'low_value': self.low_value,
            'severity': self.severity,
            'stream': tmp, #self.stream,
            'retired': self.retired,
            'escalate_on': self.escalate_on,
            'escalate_boundary': self.escalate_boundary,
            'event_receipt_delta': self.event_receipt_delta
        }
        if self.created_time is not None:
            json_system_event_definition['created_time'] = self._pytype(self.created_time)
        if self.ts_retired is not None:
            json_system_event_definition['ts_retired'] = self._pytype(self.ts_retired)
        return json_system_event_definition

    def _pytype(self,v):
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)


class SystemEvent(db.Model):
    """
    Stores the Alert/Alarm instances from uFrame; reference Alert/Alarm definition.

    uframe_event_id:    uframe instance id
    uframe_filter_id:   uframe filter id
    event_time:         uframe create time; time uframe indicates actual alert or alarm was detected.
    ticket_id:          default = 0; key for redmine ticket; unique identifier to CRUD red mine item.
    escalated:          true when escalate_on time has been reached; once true always true)
    ts_escalated:       datetime when first red mine ticket is created
    """
    __tablename__ = 'system_events'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    system_event_definition_id = db.Column(db.ForeignKey(u'' + __schema__ + '.system_event_definitions.id'), nullable=False)
    uframe_event_id = db.Column(db.Integer, nullable=False)
    uframe_filter_id = db.Column(db.Integer, nullable=False)
    event_time = db.Column(db.DateTime(True), nullable=False)
    event_type = db.Column(db.Text, nullable=False)
    event_response = db.Column(db.Text, nullable=False)
    method = db.Column(db.Text, nullable=False)
    deployment = db.Column(db.Integer, nullable=False)
    acknowledged = db.Column(db.Boolean, nullable=False)
    ack_by = db.Column(db.Integer, nullable=True)
    ts_acknowledged = db.Column(db.DateTime(True), nullable=True)
    ticket_id = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    escalated = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    ts_escalated = db.Column(db.DateTime(False), nullable=True)
    timestamp = db.Column(db.DateTime(True), nullable=False)
    ts_start = db.Column(db.DateTime(True), nullable=True)
    resolved = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    resolved_comment = db.Column(db.Text, nullable=True)

    event = db.relationship(u'SystemEventDefinition')

    @staticmethod
    def update_alert_alarm_escalation(id, ticket_id, escalated, ts_escalated):
        try:
            event = SystemEvent.query.get(id)
            if event is None:
                raise Exception('Invalid alert_alarm id, no record found.')
            event.ticket_id = ticket_id
            event.escalated = escalated
            event.ts_escalated = ts_escalated
            db.session.add(event)
            db.session.commit()
            db.session.flush()
            return
        except Exception as err:
            raise

    def to_json(self):
        json_system_event = {
            'id' : self.id,
            'uframe_event_id': self.uframe_event_id,
            'uframe_filter_id': self.uframe_filter_id,
            'system_event_definition_id': self.system_event_definition_id,
            'event_time': self.event_time,
            'event_type': self.event_type,
            'event_response': self.event_response,
            'method': self.method,
            'deployment': self.deployment,
            'acknowledged': self.acknowledged,
            'ack_by': self.ack_by,
            'ticket_id': self.ticket_id,
            'escalated': self.escalated,
            'resolved': self.resolved,
            'resolved_comment': self.resolved_comment
        }
        if self.event_time is not None:
            json_system_event['event_time'] = self._pytype(self.event_time)
        if self.ts_acknowledged is not None:
            json_system_event['ts_acknowledged'] = self._pytype(self.ts_acknowledged)
        if self.ts_escalated is not None:
            json_system_event['ts_escalated'] = self._pytype(self.ts_escalated)
        if self.timestamp is not None:
            json_system_event['timestamp'] = self._pytype(self.timestamp)
        if self.ts_start is not None:
            json_system_event['ts_start'] = self._pytype(self.ts_start)
        else:
            json_system_event['ts_start'] = None
        return json_system_event

    def _pytype(self,v):
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)


class UserEventNotification(db.Model):
    """
    User notification of Alerts/Alarms from uFrame
    """
    __tablename__ = 'user_event_notifications'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    system_event_definition_id = db.Column(db.ForeignKey(u'' + __schema__ + '.system_event_definitions.id'), nullable=False)
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)
    use_email = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    use_redmine = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    use_phone = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    use_log = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    use_sms = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))

    system_event_definition = db.relationship(u'SystemEventDefinition')
    user = db.relationship(u'User')

    def to_json(self):
        json_user_notification = {
            'id': self.id,
            'use_email': self.use_email,
            'use_redmine': self.use_redmine,
            'use_phone': self.use_phone,
            'use_log': self.use_log,
            'use_sms': self.use_sms
        }
        if self.user:
            json_user_notification['user_id'] = self.user.id
        if self.system_event_definition:
            json_user_notification['system_event_definition_id'] = self.system_event_definition.id
        return json_user_notification

    @staticmethod
    def insert_user_event_notification(system_event_definition_id, user_id, use_email, use_redmine, use_phone,
                                        use_log, use_sms):
        try:
            tmp = SystemEventDefinition.query.get(system_event_definition_id)
            if tmp is None:
                message = 'Invalid ID, system_event_definition_id record not found.'
                raise Exception(message)

            new_user_event_notification = UserEventNotification()
            new_user_event_notification.system_event_definition_id = system_event_definition_id
            new_user_event_notification.user_id = user_id
            new_user_event_notification.use_email = use_email
            new_user_event_notification.use_redmine = use_redmine
            new_user_event_notification.use_phone = use_phone
            new_user_event_notification.use_log = use_log
            new_user_event_notification.use_sms = use_sms
            try:
                db.session.add(new_user_event_notification)
                db.session.commit()
            except Exception as err:
                db.session.rollback()
                message = 'Failed to insert user_event_notification; %s' % err.message
                raise Exception(message)
            user_event_id = new_user_event_notification.id
            return user_event_id
        except:
            raise

    @staticmethod
    def update_user_event_notification(id, system_event_definition_id, user_id,
                                       use_email, use_redmine, use_phone, use_log, use_sms):
        try:
            user_event_notification = UserEventNotification.query.get(id)
            if user_event_notification is None:
                message = 'Invalid ID, user_event_notification record not found.'
                raise Exception(message)
            user_event_notification.system_event_definition_id = system_event_definition_id
            user_event_notification.user_id = user_id
            user_event_notification.use_email = use_email
            user_event_notification.use_redmine = use_redmine
            user_event_notification.use_phone = use_phone
            user_event_notification.use_log = use_log
            user_event_notification.use_sms = use_sms
            db.session.add(user_event_notification)
            db.session.commit()
            return
        except:
            db.session.rollback()
            message = 'Failed to update_user_event_notification.'
            raise Exception(message)
