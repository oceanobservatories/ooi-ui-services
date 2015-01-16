-- OOI UI Schema
-- Note: Execute before bulk insert of data

-- START HEADER DEFINITIONS
--
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

CREATE SCHEMA ooiui;

ALTER SCHEMA ooiui OWNER TO postgres;

SET search_path = ooiui, public, pg_catalog;
--
-- END HEADER DEFINITIONS

-- Definition for sequence arrays_id_seq:
CREATE SEQUENCE arrays_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence deployments_id_seq:
CREATE SEQUENCE deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence instrument_deployments_id_seq (OID = 19045):
CREATE SEQUENCE instrument_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence instruments_id_seq (OID = 19047):
CREATE SEQUENCE instruments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence platform_deployments_id_seq (OID = 19049):
CREATE SEQUENCE platform_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence platforms_id_seq (OID = 19051):
CREATE SEQUENCE platforms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence stream_parameters_id_seq (OID = 19053):
CREATE SEQUENCE stream_parameters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence streams_id_seq (OID = 19055):
CREATE SEQUENCE streams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence assets_id_seq (OID = 19057):
CREATE SEQUENCE assets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence asset_types_id_seq (OID = 19059):
CREATE SEQUENCE asset_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence organizations_id_seq (OID = 19061):
CREATE SEQUENCE organizations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence stream_parameter_link_id_seq (OID = 19063):
CREATE SEQUENCE stream_parameter_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence installation_record_id_seq (OID = 19065):
CREATE SEQUENCE installation_record_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence assemblies_id_seq (OID = 19067):
CREATE SEQUENCE assemblies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence instrument_models_id_seq (OID = 19069):
CREATE SEQUENCE instrument_models_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence inspection_status_id_seq (OID = 19071):
CREATE SEQUENCE inspection_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence files_id_seq (OID = 19073):
CREATE SEQUENCE files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence asset_file_link_id_seq (OID = 19075):
CREATE SEQUENCE asset_file_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence drivers_id_seq (OID = 19077):
CREATE SEQUENCE drivers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence driver_stream_link_id_seq (OID = 19079):
CREATE SEQUENCE driver_stream_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence datasets_id_seq (OID = 19081):
CREATE SEQUENCE datasets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence dataset_keywords_id_seq (OID = 19083):
CREATE SEQUENCE dataset_keywords_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence manufacturers_id_seq (OID = 19085):
CREATE SEQUENCE manufacturers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table arrays (OID = 19088):
CREATE TABLE arrays (
    id integer DEFAULT nextval('arrays_id_seq'::regclass) NOT NULL,
    array_code text,
    description text,
    geo_location public.geography(Polygon,4326),
    array_name text,
    display_name text
) WITHOUT OIDS;
-- Structure for table deployments (OID = 19095):
CREATE TABLE deployments (
    id integer DEFAULT nextval('deployments_id_seq'::regclass) NOT NULL,
    start_date date,
    end_date date,
    cruise_id integer
) WITHOUT OIDS;
-- Structure for table instrument_deployments (OID = 19099):
CREATE TABLE instrument_deployments (
    id integer DEFAULT nextval('instrument_deployments_id_seq'::regclass) NOT NULL,
    display_name text,
    start_date date,
    end_date date,
    platform_deployment_id integer,
    instrument_id integer,
    reference_designator text,
    depth real,
    geo_location public.geography(Point,4326)
) WITHOUT OIDS;
-- Structure for table instruments (OID = 19106):
CREATE TABLE instruments (
    id integer DEFAULT nextval('instruments_id_seq'::regclass) NOT NULL,
    instrument_name text,
    description text,
    location_description text,
    instrument_series text,
    serial_number text,
    display_name text,
    model_id integer NOT NULL,
    asset_id integer NOT NULL,
    depth_rating real,
    manufacturer_id integer
) WITHOUT OIDS;
-- Structure for table platform_deployments (OID = 19113):
CREATE TABLE platform_deployments (
    id integer DEFAULT nextval('platform_deployments_id_seq'::regclass) NOT NULL,
    start_date date,
    end_date date,
    platform_id integer,
    reference_designator text NOT NULL,
    array_id integer,
    deployment_id integer,
    display_name text,
    geo_location public.geography(Point,4326)
) WITHOUT OIDS;
-- Structure for table platforms (OID = 19120):
CREATE TABLE platforms (
    id integer DEFAULT nextval('platforms_id_seq'::regclass) NOT NULL,
    platform_name text,
    description text,
    location_description text,
    platform_series text,
    is_mobile boolean NOT NULL,
    serial_no text,
    asset_id integer NOT NULL,
    manufacturer_id integer
) WITHOUT OIDS;
-- Structure for table stream_parameters (OID = 19127):
CREATE TABLE stream_parameters (
    id integer DEFAULT nextval('stream_parameters_id_seq'::regclass) NOT NULL,
    stream_parameter_name text,
    short_name text,
    long_name text,
    standard_name text,
    units text,
    data_type text
) WITHOUT OIDS;
-- Structure for table streams (OID = 19134):
CREATE TABLE streams (
    id integer DEFAULT nextval('streams_id_seq'::regclass) NOT NULL,
    stream_name text,
    instrument_id integer,
    description text
) WITHOUT OIDS;
-- Structure for table assets (OID = 19141):
CREATE TABLE assets (
    id integer DEFAULT nextval('assets_id_seq'::regclass) NOT NULL,
    asset_type_id integer NOT NULL,
    organization_id integer NOT NULL,
    supplier_id integer NOT NULL,
    deployment_id integer,
    asset_name text NOT NULL,
    model text,
    current_lifecycle_state text,
    part_number text,
    firmware_version text,
    geo_location public.geography(Point,4326)
) WITHOUT OIDS;
-- Structure for table asset_types (OID = 19148):
CREATE TABLE asset_types (
    id integer DEFAULT nextval('asset_types_id_seq'::regclass) NOT NULL,
    asset_type_name text NOT NULL
) WITHOUT OIDS;
-- Structure for table organizations (OID = 19155):
CREATE TABLE organizations (
    id integer DEFAULT nextval('organizations_id_seq'::regclass) NOT NULL,
    organization_name text NOT NULL
) WITHOUT OIDS;
-- Structure for table stream_parameter_link (OID = 19162):
CREATE TABLE stream_parameter_link (
    id integer DEFAULT nextval('stream_parameter_link_id_seq'::regclass) NOT NULL,
    stream_id integer NOT NULL,
    parameter_id integer NOT NULL
) WITHOUT OIDS;
-- Structure for table installation_records (OID = 19166):
CREATE TABLE installation_records (
    id integer DEFAULT nextval('installation_record_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    assembly_id integer NOT NULL,
    date_installed date,
    date_removed date,
    technician_name text,
    comments text,
    file_id integer
) WITHOUT OIDS;
-- Structure for table assemblies (OID = 19173):
CREATE TABLE assemblies (
    id integer DEFAULT nextval('assemblies_id_seq'::regclass) NOT NULL,
    assembly_name text NOT NULL,
    description text
) WITHOUT OIDS;
-- Structure for table instrument_models (OID = 19180):
CREATE TABLE instrument_models (
    id integer DEFAULT nextval('instrument_models_id_seq'::regclass) NOT NULL,
    instrument_model_name text NOT NULL,
    series_name text,
    class_name text,
    manufacturer_id integer
) WITHOUT OIDS;
-- Structure for table inspection_status (OID = 19187):
CREATE TABLE inspection_status (
    id integer DEFAULT nextval('inspection_status_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer,
    status text,
    technician_name text,
    comments text,
    inspection_date date,
    document text
) WITHOUT OIDS;
-- Structure for table files (OID = 19194):
CREATE TABLE files (
    id integer DEFAULT nextval('files_id_seq'::regclass) NOT NULL,
    user_id integer,
    file_name text NOT NULL,
    file_system_path text,
    file_size text,
    file_permissions text,
    file_type text
) WITHOUT OIDS;
-- Structure for table asset_file_link (OID = 19201):
CREATE TABLE asset_file_link (
    id integer DEFAULT nextval('asset_file_link_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer NOT NULL
) WITHOUT OIDS;
-- Structure for table drivers (OID = 19205):
CREATE TABLE drivers (
    id integer DEFAULT nextval('drivers_id_seq'::regclass) NOT NULL,
    instrument_id integer,
    driver_name text NOT NULL,
    driver_version text,
    author text
) WITHOUT OIDS;
-- Structure for table driver_stream_link (OID = 19212):
CREATE TABLE driver_stream_link (
    id integer DEFAULT nextval('driver_stream_link_id_seq'::regclass) NOT NULL,
    driver_id integer NOT NULL,
    stream_id integer NOT NULL
) WITHOUT OIDS;
-- Structure for table datasets (OID = 19216):
CREATE TABLE datasets (
    id integer DEFAULT nextval('datasets_id_seq'::regclass) NOT NULL,
    stream_id integer NOT NULL,
    deployment_id integer NOT NULL,
    process_level text,
    is_recovered boolean DEFAULT false NOT NULL
) WITHOUT OIDS;
-- Structure for table dataset_keywords (OID = 19224):
CREATE TABLE dataset_keywords (
    id integer DEFAULT nextval('dataset_keywords_id_seq'::regclass) NOT NULL,
    dataset_id integer NOT NULL,
    concept_name text,
    concept_description text
) WITHOUT OIDS;
-- Structure for table manufacturers (OID = 19231):
CREATE TABLE manufacturers (
    id integer DEFAULT nextval('manufacturers_id_seq'::regclass) NOT NULL,
    manufacturer_name text NOT NULL,
    phone_number text,
    contact_name text,
    web_address text
) WITHOUT OIDS;
-- Definition for sequence users_id_seq (OID = 20949):
CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table users (OID = 20951):
CREATE TABLE users (
    id integer DEFAULT nextval('users_id_seq'::regclass) NOT NULL,
    user_id text NOT NULL,
    pass_hash text,
    email text NOT NULL,
    user_name text,
    active boolean DEFAULT false NOT NULL,
    confirmed_at date,
    first_name text,
    last_name text,
    phone_primary text,
    phone_alternate text,
    organization_id integer
) WITHOUT OIDS;
-- Definition for sequence user_scopes_id_seq (OID = 20960):
CREATE SEQUENCE user_scopes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table user_scopes (OID = 20962):
CREATE TABLE user_scopes (
    id integer DEFAULT nextval('user_scopes_id_seq'::regclass) NOT NULL,
    scope_name text NOT NULL,
    scope_description text
) WITHOUT OIDS;
-- Definition for sequence user_scope_link_id_seq (OID = 20971):
CREATE SEQUENCE user_scope_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table user_scope_link (OID = 20973):
CREATE TABLE user_scope_link (
    id integer DEFAULT nextval('user_scope_link_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    scope_id integer NOT NULL
) WITHOUT OIDS;
-- Definition for sequence annotations_id_seq (OID = 21019):
CREATE SEQUENCE annotations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table annotations (OID = 21021):
CREATE TABLE annotations (
    id integer DEFAULT nextval('annotations_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    created_time timestamp with time zone NOT NULL,
    modified_time timestamp with time zone NOT NULL,
    reference_name text NOT NULL,
    reference_type text NOT NULL,
    reference_pk_id integer NOT NULL,
    stream_parameter_id_x integer,
    stream_parameter_value_x text,
    stream_parameter_id_y integer,
    stream_parameter_value_y text,
    ann_title text NOT NULL,
    ann_comment text
) WITHOUT OIDS;
-- Definition for sequence roles_id_seq (OID = 31531):
CREATE SEQUENCE roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table user_roles (OID = 31533):
CREATE TABLE user_roles (
    id integer DEFAULT nextval('roles_id_seq'::regclass) NOT NULL,
    role_name text NOT NULL
) WITHOUT OIDS;
-- Definition for sequence user_role_link_id_seq (OID = 31542):
CREATE SEQUENCE user_role_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table user_role_user_scope_link (OID = 31544):
CREATE TABLE user_role_user_scope_link (
    id integer DEFAULT nextval('user_role_link_id_seq'::regclass) NOT NULL,
    user_scope_id integer NOT NULL,
    user_role_id integer NOT NULL
) WITHOUT OIDS;

