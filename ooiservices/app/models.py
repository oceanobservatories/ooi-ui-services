#!/usr/bin/env python
'''
OOI Models
'''

__author__ = 'M@Campbell'

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from ooiservices.app import db, login_manager
from flask.ext.login import UserMixin
from wtforms import ValidationError
from geoalchemy2.types import Geometry
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
import geoalchemy2.functions as func
import json

#--------------------------------------------------------------------------------

#from sqlalchemy.types import UserDefinedType
#from sqlalchemy import func

# class Geometry(UserDefinedType):
#     def get_col_spec(self):
#         return "GEOMETRY"
#
#     def bind_expression(self, bindvalue):
#         return func.ST_GeomFromText(bindvalue, type_=self)
#
#     def column_expression(self, col):
#         return func.ST_AsText(col, type_=self)


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
    geo_location = db.Column(Geometry(geometry_type='GEOMETRY', srid=-1, dimension=2, spatial_index=True, management=True))

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
    geo_location = db.Column(Geometry(geometry_type='GEOMETRY', srid=-1, dimension=2, spatial_index=True, management=True))

    instrument = db.relationship(u'Instrument')
    platform_deployment = db.relationship(u'PlatformDeployment')

    def to_json(self):
        geo_location = None
        if self.geo_location is not None:
            json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geo_location)))
        json_inst_deploy = {
            'id' : self.id,
            'reference_designator' : self.reference_designator,
            'platform_deployment_id' : self.platform_deployment_id,
            'display_name' : self.display_name,
            'start_date' : self.start_date,
            'end_date' : self.end_date,
            'depth' : self.depth,
            'geo_location' : geo_location
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

class Instrumentname(db.Model):
    __tablename__ = 'instrumentnames'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    instrument_class = db.Column(db.Text)
    display_name = db.Column(db.Text)

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
    users = db.relationship(u'User')

class PlatformDeployment(db.Model, DictSerializableMixin):
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
    geo_location = db.Column(Geometry(geometry_type='GEOMETRY', srid=-1, dimension=2, spatial_index=True, management=True))

    array = db.relationship(u'Array')
    deployment = db.relationship(u'Deployment')
    platform = db.relationship(u'Platform')

    @hybrid_property
    def geojson(self):
        return json.loads(db.session.scalar(func.ST_AsGeoJSON(self.geo_location)))

    @hybrid_property
    def proper_display_name(self):
        return self._get_display_name(reference_designator=self.reference_designator)

    def to_json(self):
        geo_location = None
        if self.geo_location is not None:
            loc = db.session.scalar(func.ST_AsGeoJSON(self.geo_location))
            geo_location = json.loads(loc)
        json_platform_deployment = {
            'id' : self.id,
            'reference_designator' : self.reference_designator,
            'array_id' : self.array_id,
            'display_name' : self.proper_display_name,
            'start_date' : self.start_date,
            'end_date' : self.end_date,
            'geo_location' : geo_location
        }
        return json_platform_deployment

    def _f_concat_rd(self, array_type, array_name, site, platform, assembly, instrument_name):

        if assembly is not None and instrument_name is not None:
            return array_type + ' ' + array_name + ' ' + site + ' ' + platform + ' - ' + assembly + ' - ' + instrument_name
        elif assembly is not None and instrument_name is None:
            return array_type + ' ' + array_name + ' ' + site + ' ' + platform + ' - ' + assembly
        else:
            return array_type + ' ' + array_name + ' ' + site + ' ' + platform

    def _get_display_name(self, reference_designator):

        '''
        sample reference_designators for tests:
            'CP02PMUO-SBS01-01-MOPAK0000'
            'GP05MOAS-GL002-03-ACOMMM000'
            'CE05MOAS-GL005'
            'CP05MOAS-AV001'
            'CP02PMUO-SBS01'

        curl -X GET http://localhost:4000/display_name?reference_designator=CP05MOAS-AV001
        '''

        import re
        if not reference_designator:
            return None

        rd_len = len(reference_designator)

        p_n = Platformname.query.filter(Platformname.reference_designator == reference_designator[:14]).first()
        if not p_n:
            return reference_designator

        if rd_len == 8:
            return self._f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, None, None)

        elif rd_len == 14:
            assy = reference_designator[9:14]
            if re.match('AV[0-9]{3}', assy):
                platform_text = 'AUV ' + assy[2:5]
            elif re.match('GL[0-9]{3}', assy):
                platform_text = 'Glider ' + assy[2:5]
            else:
                platform_text = p_n.assembly

            return self._f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, platform_text, None)

        elif rd_len == 27:
            inst = reference_designator[18:23]
            assy = reference_designator[9:14]
            if re.match('AV[0-9]{3}', assy):
                platform_text = 'AUV ' + assy[2:5]
            elif re.match('GL[0-9]{3}', assy):
                platform_text = 'Glider ' + assy[2:5]
            else:
                platform_text = p_n.assembly

            i_n = Instrumentname.query.filter(Instrumentname.instrument_class == inst).first()
            if not i_n:
                return self._f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, platform_text, inst)

            return self._f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, platform_text, i_n.display_name)
        return None


class Platformname(db.Model):
    __tablename__ = 'platformnames'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    reference_designator = db.Column(db.Text)
    array_type = db.Column(db.Text)
    array_name = db.Column(db.Text)
    site = db.Column(db.Text)
    platform = db.Column(db.Text)
    assembly = db.Column(db.Text)

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


class UserScopeLink(db.Model):
    __tablename__ = 'user_scope_link'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.ForeignKey(u'' + __schema__ + '.users.user_name'), nullable=False)
    scope_name = db.Column(db.ForeignKey(u'' + __schema__ + '.user_scopes.scope_name'), nullable=False)

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

    def __repr__(self):
        return '<User %r, Scope %r>' % (self.user_name, self.scope_name)



class UserScope(db.Model):
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
            'user_admin'
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
        return '<Scope %r>' % self.scope_name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {u'schema': __schema__}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text, unique=True, nullable=False)
    pass_hash = db.Column(db.Text)
    email = db.Column(db.Text, unique=True, nullable=False)
    user_name = db.Column(db.Text, unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    confirmed_at = db.Column(db.Date)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    phone_primary = db.Column(db.Text)
    phone_alternate = db.Column(db.Text)
    role = db.Column(db.Text)
    organization_id = db.Column(db.ForeignKey(u'' + __schema__ + '.organizations.id'))
    scopes = db.relationship(u'UserScopeLink')
    organization = db.relationship(u'Organization')
    watches = db.relationship(u'Watch')

   # def __init__(self, **kwargs):
   #     super(User, self).__init__(**kwargs)
   #         self.scope = Scope.query.filter_by(scope_name='user_admin').first()
   #         if self.scope is None:
   #             self.scope = Role.query.filter_by(default=True).first()

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
        phone_primary = json.get('primary_phone')
        user_name = json.get('username')
        first_name = json.get('first_name')
        last_name = json.get('last_name')
        role = json.get('role_name')
        organization_id = json.get('organization_id')

        #Validate some of the field.

        new_user = User()
        new_user.validate_email(email)
        new_user.validate_username(user_name)
        new_user.validate_password(password, password2)
        pass_hash = generate_password_hash(password)
        #All passes, return the User object ready to be stored.
        return User(email=email,
                    pass_hash=pass_hash,
                    phone_primary=phone_primary,
                    user_name=user_name,
                    user_id=user_name,
                    first_name=first_name,
                    last_name=last_name,
                    organization_id=organization_id,
                    role=role)


    @staticmethod
    def insert_user(password):
        user = User(user_id='admin')
        try:
            user.validate_username('admin')
        except ValidationError as e:
            admin_del = db.session.query(User).filter_by(user_name='admin').first()
            db.session.delete(admin_del)
            db.session.commit()
        user.first_name = 'Ad'
        user.last_name = 'Min'
        user.pass_hash = generate_password_hash(password)
        user.user_name = 'admin'
        user.active = True
        user.email = 'ooi@asascience.com'
        org = Organization.query.filter(Organization.organization_name == 'ASA').first()
        if org:
            user.organization_id = org.id
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

    def can(self, scope):
        #db.session.query
        return db.session.query(UserScopeLink).with_entities(UserScopeLink.user_name).filter_by(scope_name=scope).all()

    def __repr__(self):
        return '<User %r>' % self.user_name



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
