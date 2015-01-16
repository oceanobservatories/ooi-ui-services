#!/usr/bin/env python
'''
OOI Models
'''

__author__ = 'M@Campbell'

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db, login_manager
from flask.ext.login import UserMixin
from wtforms import ValidationError

__schema__ = 'ooiui'

class Annotation(db.Model):
    __tablename__ = 'annotations'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(u'' + __schema__ + '.users.id'), nullable=False)
    created_time = db.Column(db.DateTime(True), nullable=False)
    modified_time = db.Column(db.DateTime(True), nullable=False)
    reference_name = db.Column(db.Text, nullable=False)
    reference_type = db.Column(db.Text, nullable=False)
    reference_pk_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text)

    user = db.relationship(u'User')

class Array(db.Model):
    __tablename__ = 'arrays'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer(), primary_key=True)
    array_code = db.Column(db.Text())
    description = db.Column(db.Text())
    geo_location = db.Column(db.Text())
    array_name = db.Column(db.Text())
    display_name = db.Column(db.Text())

    def to_json(self):
        json_array = {
            'id' : self.id,
            'array_code' : self.array_code,
            'description' : self.description,
            'geo_location' : self.geo_location,
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


class Assembly(db.Model):
    __tablename__ = 'assemblies'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    assembly_name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

class AssetFileLink(db.Model):
    __tablename__ = 'asset_file_link'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.ForeignKey(u'' + __schema__ + '.assets.id'), nullable=False)
    file_id = db.Column(db.ForeignKey(u'' + __schema__ + '.files.id'), nullable=False)

    asset = db.relationship(u'Asset')
    file = db.relationship(u'File')

class AssetType(db.Model):
    __tablename__ = 'asset_types'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    asset_type_name = db.Column(db.Text, nullable=False)

class Asset(db.Model):
    __tablename__ = 'assets'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    asset_type_id = db.Column(db.ForeignKey(u'' + __schema__ + '.asset_types.id'), nullable=False)
    organization_id = db.Column(db.ForeignKey(u'' + __schema__ + '.organizations.id'), nullable=False)
    supplier_id = db.Column(db.Integer, nullable=False)
    deployment_id = db.Column(db.Integer)
    asset_name = db.Column(db.Text, nullable=False)
    model = db.Column(db.Text)
    current_lifecycle_state = db.Column(db.Text)
    part_number = db.Column(db.Text)
    firmware_version = db.Column(db.Text)
    geo_location = db.Column(db.Text)

    asset_type = db.relationship(u'AssetType')
    organization = db.relationship(u'Organization')

class DatasetKeyword(db.Model):
    __tablename__ = 'dataset_keywords'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.ForeignKey(u'' + __schema__ + '.datasets.id'), nullable=False)
    concept_name = db.Column(db.Text)
    concept_description = db.Column(db.Text)

    dataset = db.relationship(u'Dataset')

class Dataset(db.Model):
    __tablename__ = 'datasets'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.ForeignKey(u'' + __schema__ + '.streams.id'), nullable=False)
    deployment_id = db.Column(db.ForeignKey(u'' + __schema__ + '.deployments.id'), nullable=False)
    process_level = db.Column(db.Text)
    is_recovered = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))

    deployment = db.relationship(u'Deployment')
    stream = db.relationship(u'Stream')

class Deployment(db.Model):
    __tablename__ = 'deployments'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cruise_id = db.Column(db.Integer)

class DriverStreamLink(db.Model):
    __tablename__ = 'driver_stream_link'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.ForeignKey(u'' + __schema__ + '.drivers.id'), nullable=False)
    stream_id = db.Column(db.ForeignKey(u'' + __schema__ + '.streams.id'), nullable=False)

    driver = db.relationship(u'Driver')
    stream = db.relationship(u'Stream')

class Driver(db.Model):
    __tablename__ = 'drivers'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    instrument_id = db.Column(db.ForeignKey(u'' + __schema__ + '.instruments.id'))
    driver_name = db.Column(db.Text, nullable=False)
    driver_version = db.Column(db.Text)
    author = db.Column(db.Text)

    instrument = db.relationship(u'Instrument')

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

class InspectionStatu(db.Model):
    __tablename__ = 'inspection_status'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.ForeignKey(u'' + __schema__ + '.assets.id'), nullable=False)
    file_id = db.Column(db.ForeignKey(u'' + __schema__ + '.files.id'))
    status = db.Column(db.Text)
    technician_name = db.Column(db.Text)
    comments = db.Column(db.Text)
    inspection_date = db.Column(db.Date)
    document = db.Column(db.Text)

    asset = db.relationship(u'Asset')
    file = db.relationship(u'File')

class InstallationRecord(db.Model):
    __tablename__ = 'installation_records'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.ForeignKey(u'' + __schema__ + '.assets.id'), nullable=False)
    assembly_id = db.Column(db.ForeignKey(u'' + __schema__ + '.assemblies.id'), nullable=False)
    date_installed = db.Column(db.Date)
    date_removed = db.Column(db.Date)
    technician_name = db.Column(db.Text)
    comments = db.Column(db.Text)
    file_id = db.Column(db.ForeignKey(u'' + __schema__ + '.files.id'))

    assembly = db.relationship(u'Assembly')
    asset = db.relationship(u'Asset')
    file = db.relationship(u'File')

class InstrumentDeployment(db.Model):
    __tablename__ = 'instrument_deployments'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    platform_deployment_id = db.Column(db.ForeignKey(u'' + __schema__ + '.platform_deployments.id'))
    instrument_id = db.Column(db.ForeignKey(u'' + __schema__ + '.instruments.id'))
    reference_designator = db.Column(db.Text)
    depth = db.Column(db.Float)
    geo_location = db.Column(db.Text)

    instrument = db.relationship(u'Instrument')
    platform_deployment = db.relationship(u'PlatformDeployment')

    def to_json(self):
        json_inst_deploy = {
            'id' : self.id,
            'ref_designator' : self.reference_designator,
            'platform_deployment_id' : self.platform_deployment_id,
            'display_name' : self.display_name,
            'start_date' : self.start_date,
            'end_date' : self.end_date,
            'depth' : self.depth,
            'geo_location' : self.geo_location
        }
        return json_inst_deploy


class InstrumentModel(db.Model):
    __tablename__ = 'instrument_models'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    instrument_model_name = db.Column(db.Text, nullable=False)
    series_name = db.Column(db.Text)
    class_name = db.Column(db.Text)
    manufacturer_id = db.Column(db.ForeignKey(u'' + __schema__ + '.manufacturers.id'))

    manufacturer = db.relationship(u'Manufacturer')

class Instrument(db.Model):
    __tablename__ = 'instruments'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    instrument_name = db.Column(db.Text)
    description = db.Column(db.Text)
    location_description = db.Column(db.Text)
    instrument_series = db.Column(db.Text)
    serial_number = db.Column(db.Text)
    display_name = db.Column(db.Text)
    model_id = db.Column(db.ForeignKey(u'' + __schema__ + '.instrument_models.id'), nullable=False)
    asset_id = db.Column(db.ForeignKey(u'' + __schema__ + '.assets.id'), nullable=False)
    depth_rating = db.Column(db.Float)
    manufacturer_id = db.Column(db.ForeignKey(u'' + __schema__ + '.manufacturers.id'))

    asset = db.relationship(u'Asset')
    manufacturer = db.relationship(u'Manufacturer')
    model = db.relationship(u'InstrumentModel')

class Manufacturer(db.Model):
    __tablename__ = 'manufacturers'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    manufacturer_name = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.Text)
    contact_name = db.Column(db.Text)
    web_address = db.Column(db.Text)

class Organization(db.Model):
    __tablename__ = 'organizations'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    organization_name = db.Column(db.Text, nullable=False)

class PlatformDeployment(db.Model):
    __tablename__ = 'platform_deployments'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    platform_id = db.Column(db.ForeignKey(u'' + __schema__ + '.platforms.id'))
    reference_designator = db.Column(db.Text, nullable=False)
    array_id = db.Column(db.ForeignKey(u'' + __schema__ + '.arrays.id'))
    deployment_id = db.Column(db.ForeignKey(u'' + __schema__ + '.deployments.id'))
    display_name = db.Column(db.Text)
    geo_location = db.Column(db.Text)

    array = db.relationship(u'Array')
    deployment = db.relationship(u'Deployment')
    platform = db.relationship(u'Platform')

    def to_json(self):
        json_platform_deployment = {
            'id' : self.id,
            'ref_designator' : self.reference_designator,
            'array_id' : self.array_id,
            'display_name' : self.display_name,
            'start_date' : self.start_date,
            'end_date' : self.end_date,
            'geo_location' : self.geo_location
        }
        return json_platform_deployment


class Platform(db.Model):
    __tablename__ = 'platforms'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.Text)
    description = db.Column(db.Text)
    location_description = db.Column(db.Text)
    platform_series = db.Column(db.Text)
    is_mobile = db.Column(db.Boolean, nullable=False)
    serial_no = db.Column(db.Text)
    asset_id = db.Column(db.ForeignKey(u'' + __schema__ + '.assets.id'), nullable=False)
    manufacturer_id = db.Column(db.ForeignKey(u'' + __schema__ + '.manufacturers.id'))

    asset = db.relationship(u'Asset')
    manufacturer = db.relationship(u'Manufacturer')

class StreamParameterLink(db.Model):
    __tablename__ = 'stream_parameter_link'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.ForeignKey(u'' + __schema__ + '.streams.id'), nullable=False)
    parameter_id = db.Column(db.ForeignKey(u'' + __schema__ + '.stream_parameters.id'), nullable=False)

    parameter = db.relationship(u'StreamParameter')
    stream = db.relationship(u'Stream')

class StreamParameter(db.Model):
    __tablename__ = 'stream_parameters'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    stream_parameter_name = db.Column(db.Text)
    short_name = db.Column(db.Text)
    long_name = db.Column(db.Text)
    standard_name = db.Column(db.Text)
    units = db.Column(db.Text)
    data_type = db.Column(db.Text)

    def to_json(self):
        json_parameter = {
            'id' : self.id,
            'parameter_name' : self.stream_parameter_name,
            'short_name' : self.short_name,
            'long_name' : self.long_name,
            'standard_name' : self.standard_name,
            'units' : self.units,
            'data_type' : self.data_type
        }
        return json_parameter


class Stream(db.Model):
    __tablename__ = 'streams'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    stream_name = db.Column(db.Text)
    instrument_id = db.Column(db.ForeignKey(u'' + __schema__ + '.instruments.id'))
    description = db.Column(db.Text)

    instrument = db.relationship(u'Instrument')

    def to_json(self):
        json_stream = {
            'id' : self.id,
            'stream_name' : self.stream_name,
            'instrument_id' : self.instrument_id,
            'description' : self.description
        }
        return json_stream


class UserRoleUserScopeLink(db.Model):
    __tablename__ = 'user_role_user_scope_link'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_scope_id = db.Column(db.ForeignKey(u'' + __schema__ + '.user_scopes.id'), nullable=False)
    user_role_id = db.Column(db.ForeignKey(u'' + __schema__ + '.user_roles.id'), nullable=False)

    user_role = db.relationship(u'UserRole')
    user_scope = db.relationship(u'UserScope')

    @staticmethod
    def insert_roles_scope():
        user_role_user_scope = UserRoleUserScopeLink()
        user_role_user_scope.user_role_id = 1
        user_role_user_scope.user_scope_id = 1
        db.session.add_all([user_role_user_scope])
        db.session.commit()


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.Text, nullable=False)

    def to_json(self):
        json_role_link = {
            'id' : self.id,
            'role_name' : self.role_name
        }
        return json_role_link

    @staticmethod
    def insert_roles():
        role_name_admin = UserRole(role_name='Administrator')
        role_name_marine_operator = UserRole(role_name='Marine Operator')
        role_name_science_user = UserRole(role_name='Science User')
        db.session.add_all([role_name_admin, role_name_marine_operator, role_name_science_user])
        db.session.commit()


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
        user = UserScopeLink(user_id='1')
        user.scope_id='4'
        db.session.add(user)
        db.session.commit()

    def to_json(self):
        json_scope_link = {
            'id' : self.id,
            'user_id' : self.user_id,
            'scope_id' : self.scope_id,
        }
        return json_scope_link


class UserScope(db.Model):
    __tablename__ = 'user_scopes'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    scope_name = db.Column(db.Text, nullable=False, unique=True)
    scope_description = db.Column(db.Text)

    @staticmethod
    def insert_scopes():
       scope_am = UserScope(scope_name='asset_management')
       scope_user_create = UserScope(scope_name='user_create')
       scope_user_read = UserScope(scope_name='user_read')
       scope_user_read_write = UserScope(scope_name='user_read_write')
       scope_am.description = 'Manage assets.'
       scope_user_create.description = 'Create users.'
       scope_user_read.description = 'Read from the list of users.'
       scope_user_read_write.description = 'Read and modify the users.'
       db.session.add_all([scope_am, scope_user_create, scope_user_read, scope_user_read_write])
       db.session.commit()

    def to_json(self):
        json_scope = {
            'id' : self.id,
            'scope_name' : self.scope_name,
            'scope_description' : self.scope_description,
        }
        return json_scope


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text, unique=True, nullable=False)
    pass_hash = db.Column(db.Text)
    email = db.Column(db.Text, unique=True, nullable=False)
    user_name = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    confirmed_at = db.Column(db.Date)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    phone_primary = db.Column(db.Text)
    phone_alternate = db.Column(db.Text)
    organization_id = db.Column(db.ForeignKey(u'' + __schema__ + '.organizations.id'))

    organization = db.relationship(u'Organization')

    def to_json(self):
        json_user = {
            'id' : self.id,
            'user_id' : self.user_id,
            'pass_hash' : self.pass_hash,
            'email' : self.email,
            'user_name' : self.user_name
        }
        return json_user

    @staticmethod
    def from_json(json):
        email = json.get('email')
        password = json.get('password')
        password2 = json.get('repeatPassword')
        phone_primary = json.get('phonenum')
        user_name = json.get('username')

        #Validate some of the field.

        new_user = User()
        new_user.validate_email(email)
        new_user.validate_username(user_name)
        new_user.validate_password(password, password2)
        pass_hash = generate_password_hash(password)
        #All passes, return the User object ready to be stored.
        return User(email=email, pass_hash=pass_hash, phone_primary=phone_primary, \
        user_name=user_name, user_id=user_name)


    @staticmethod
    def insert_user(password):
        user = User(user_id='admin')
        try:
            user.validate_username('admin')
        except ValidationError as e:
            admin_del = db.session.query(User).filter_by(user_name='admin').first()
            db.session.delete(admin_del)
            db.session.commit()
        user.pass_hash = generate_password_hash(password)
        user.user_name = 'admin'
        user.active = True
        user.email = 'ooi@asascience.com'
        db.session.add(user)
        db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    #Store the hashed password.
    @password.setter
    def password(self, password):
        self.pass_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pass_hash, password)

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
