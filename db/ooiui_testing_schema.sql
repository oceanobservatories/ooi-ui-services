--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: ooiui_testing; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA ooiui_testing;


ALTER SCHEMA ooiui_testing OWNER TO postgres;

SET search_path = ooiui_testing, pg_catalog;

--
-- Name: annotations_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE annotations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.annotations_id_seq OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: annotations; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE annotations (
    id integer DEFAULT nextval('annotations_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    created_time timestamp with time zone NOT NULL,
    modified_time timestamp with time zone NOT NULL,
    reference_name text NOT NULL,
    reference_type text NOT NULL,
    reference_pk_id integer NOT NULL,
    title text NOT NULL,
    comment text
);


ALTER TABLE ooiui_testing.annotations OWNER TO postgres;

--
-- Name: arrays_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE arrays_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.arrays_id_seq OWNER TO postgres;

--
-- Name: arrays; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE arrays (
    id integer DEFAULT nextval('arrays_id_seq'::regclass) NOT NULL,
    array_code text,
    description text,
    geo_location public.geography(Polygon,4326),
    array_name text,
    display_name text
);


ALTER TABLE ooiui_testing.arrays OWNER TO postgres;

--
-- Name: asssemblies_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE asssemblies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.asssemblies_id_seq OWNER TO postgres;

--
-- Name: assemblies; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE assemblies (
    id integer DEFAULT nextval('asssemblies_id_seq'::regclass) NOT NULL,
    assembly_name text NOT NULL,
    description text
);


ALTER TABLE ooiui_testing.assemblies OWNER TO postgres;

--
-- Name: asset_file_link_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE asset_file_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.asset_file_link_id_seq OWNER TO postgres;

--
-- Name: asset_file_link; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE asset_file_link (
    id integer DEFAULT nextval('asset_file_link_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer NOT NULL
);


ALTER TABLE ooiui_testing.asset_file_link OWNER TO postgres;

--
-- Name: asset_types_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE asset_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.asset_types_id_seq OWNER TO postgres;

--
-- Name: asset_types; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE asset_types (
    id integer DEFAULT nextval('asset_types_id_seq'::regclass) NOT NULL,
    asset_type_name text NOT NULL
);


ALTER TABLE ooiui_testing.asset_types OWNER TO postgres;

--
-- Name: assets_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE assets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.assets_id_seq OWNER TO postgres;

--
-- Name: assets; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

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
);


ALTER TABLE ooiui_testing.assets OWNER TO postgres;

--
-- Name: COLUMN assets.deployment_id; Type: COMMENT; Schema: ooiui_testing; Owner: postgres
--

COMMENT ON COLUMN assets.deployment_id IS 'Current deployment';


--
-- Name: dataset_keywords_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE dataset_keywords_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.dataset_keywords_id_seq OWNER TO postgres;

--
-- Name: dataset_keywords; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE dataset_keywords (
    id integer DEFAULT nextval('dataset_keywords_id_seq'::regclass) NOT NULL,
    dataset_id integer NOT NULL,
    concept_name text,
    concept_description text
);


ALTER TABLE ooiui_testing.dataset_keywords OWNER TO postgres;

--
-- Name: datasets_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE datasets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.datasets_id_seq OWNER TO postgres;

--
-- Name: datasets; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE datasets (
    id integer DEFAULT nextval('datasets_id_seq'::regclass) NOT NULL,
    stream_id integer NOT NULL,
    deployment_id integer NOT NULL,
    process_level text,
    is_recovered boolean DEFAULT false NOT NULL
);


ALTER TABLE ooiui_testing.datasets OWNER TO postgres;

--
-- Name: deployments_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.deployments_id_seq OWNER TO postgres;

--
-- Name: deployments; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE deployments (
    id integer DEFAULT nextval('deployments_id_seq'::regclass) NOT NULL,
    start_date date,
    end_date date,
    cruise_id integer
);


ALTER TABLE ooiui_testing.deployments OWNER TO postgres;

--
-- Name: driver_stream_link_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE driver_stream_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.driver_stream_link_id_seq OWNER TO postgres;

--
-- Name: driver_stream_link; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE driver_stream_link (
    id integer DEFAULT nextval('driver_stream_link_id_seq'::regclass) NOT NULL,
    driver_id integer NOT NULL,
    stream_id integer NOT NULL
);


ALTER TABLE ooiui_testing.driver_stream_link OWNER TO postgres;

--
-- Name: drivers_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE drivers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.drivers_id_seq OWNER TO postgres;

--
-- Name: drivers; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE drivers (
    id integer DEFAULT nextval('drivers_id_seq'::regclass) NOT NULL,
    instrument_id integer,
    driver_name text NOT NULL,
    driver_version text,
    author text
);


ALTER TABLE ooiui_testing.drivers OWNER TO postgres;

--
-- Name: files_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.files_id_seq OWNER TO postgres;

--
-- Name: files; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE files (
    id integer DEFAULT nextval('files_id_seq'::regclass) NOT NULL,
    user_id integer,
    file_name text NOT NULL,
    file_system_path text,
    file_size text,
    file_permissions text,
    file_type text
);


ALTER TABLE ooiui_testing.files OWNER TO postgres;

--
-- Name: COLUMN files.file_size; Type: COMMENT; Schema: ooiui_testing; Owner: postgres
--

COMMENT ON COLUMN files.file_size IS 'MB';


--
-- Name: inspection_status_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE inspection_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.inspection_status_id_seq OWNER TO postgres;

--
-- Name: inspection_status; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE inspection_status (
    id integer DEFAULT nextval('inspection_status_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer,
    status text,
    technician_name text,
    comments text,
    inspection_date date,
    document text
);


ALTER TABLE ooiui_testing.inspection_status OWNER TO postgres;

--
-- Name: installation_record_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE installation_record_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.installation_record_id_seq OWNER TO postgres;

--
-- Name: installation_records; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE installation_records (
    id integer DEFAULT nextval('installation_record_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    assembly_id integer NOT NULL,
    date_installed date,
    date_removed date,
    technician_name text,
    comments text,
    file_id integer
);


ALTER TABLE ooiui_testing.installation_records OWNER TO postgres;

--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE instrument_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.instrument_deployments_id_seq OWNER TO postgres;

--
-- Name: instrument_deployments; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

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
);


ALTER TABLE ooiui_testing.instrument_deployments OWNER TO postgres;

--
-- Name: instrument_models_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE instrument_models_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.instrument_models_id_seq OWNER TO postgres;

--
-- Name: instrument_models; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE instrument_models (
    id integer DEFAULT nextval('instrument_models_id_seq'::regclass) NOT NULL,
    instrument_model_name text NOT NULL,
    series_name text,
    class_name text,
    manufacturer_id integer
);


ALTER TABLE ooiui_testing.instrument_models OWNER TO postgres;

--
-- Name: instruments_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE instruments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.instruments_id_seq OWNER TO postgres;

--
-- Name: instruments; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

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
);


ALTER TABLE ooiui_testing.instruments OWNER TO postgres;

--
-- Name: manufacturers_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE manufacturers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.manufacturers_id_seq OWNER TO postgres;

--
-- Name: manufacturers; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE manufacturers (
    id integer DEFAULT nextval('manufacturers_id_seq'::regclass) NOT NULL,
    manufacturer_name text NOT NULL,
    phone_number text,
    contact_name text,
    web_address text
);


ALTER TABLE ooiui_testing.manufacturers OWNER TO postgres;

--
-- Name: organizations_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE organizations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.organizations_id_seq OWNER TO postgres;

--
-- Name: organizations; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE organizations (
    id integer DEFAULT nextval('organizations_id_seq'::regclass) NOT NULL,
    organization_name text NOT NULL
);


ALTER TABLE ooiui_testing.organizations OWNER TO postgres;

--
-- Name: platform_deployments_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE platform_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.platform_deployments_id_seq OWNER TO postgres;

--
-- Name: platform_deployments; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

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
);


ALTER TABLE ooiui_testing.platform_deployments OWNER TO postgres;

--
-- Name: platforms_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE platforms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.platforms_id_seq OWNER TO postgres;

--
-- Name: platforms; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

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
);


ALTER TABLE ooiui_testing.platforms OWNER TO postgres;

--
-- Name: stream_parameter_link_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE stream_parameter_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.stream_parameter_link_id_seq OWNER TO postgres;

--
-- Name: stream_parameter_link; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE stream_parameter_link (
    id integer DEFAULT nextval('stream_parameter_link_id_seq'::regclass) NOT NULL,
    stream_id integer NOT NULL,
    parameter_id integer NOT NULL
);


ALTER TABLE ooiui_testing.stream_parameter_link OWNER TO postgres;

--
-- Name: stream_parameters_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE stream_parameters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.stream_parameters_id_seq OWNER TO postgres;

--
-- Name: stream_parameters; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE stream_parameters (
    id integer DEFAULT nextval('stream_parameters_id_seq'::regclass) NOT NULL,
    stream_parameter_name text,
    short_name text,
    long_name text,
    standard_name text,
    units text,
    data_type text
);


ALTER TABLE ooiui_testing.stream_parameters OWNER TO postgres;

--
-- Name: streams_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE streams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.streams_id_seq OWNER TO postgres;

--
-- Name: streams; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE streams (
    id integer DEFAULT nextval('streams_id_seq'::regclass) NOT NULL,
    stream_name text,
    instrument_id integer,
    description text
);


ALTER TABLE ooiui_testing.streams OWNER TO postgres;

--
-- Name: user_scope_link_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE user_scope_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.user_scope_link_id_seq OWNER TO postgres;

--
-- Name: user_scope_link; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE user_scope_link (
    id integer DEFAULT nextval('user_scope_link_id_seq'::regclass) NOT NULL,
    user_id integer NOT NULL,
    scope_id integer NOT NULL
);


ALTER TABLE ooiui_testing.user_scope_link OWNER TO postgres;

--
-- Name: user_scopes_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE user_scopes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.user_scopes_id_seq OWNER TO postgres;

--
-- Name: user_scopes; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

CREATE TABLE user_scopes (
    id integer DEFAULT nextval('user_scopes_id_seq'::regclass) NOT NULL,
    scope_name text NOT NULL,
    scope_description text
);


ALTER TABLE ooiui_testing.user_scopes OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: ooiui_testing; Owner: postgres
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ooiui_testing.users_id_seq OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

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
);


ALTER TABLE ooiui_testing.users OWNER TO postgres;

--
-- Name: annotations_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY annotations
    ADD CONSTRAINT annotations_pkey PRIMARY KEY (id);


--
-- Name: arrays_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY arrays
    ADD CONSTRAINT arrays_pkey PRIMARY KEY (id);


--
-- Name: asset_file_link_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_pkey PRIMARY KEY (id);


--
-- Name: asset_types_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY asset_types
    ADD CONSTRAINT asset_types_pkey PRIMARY KEY (id);


--
-- Name: assets_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: asssemblies_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY assemblies
    ADD CONSTRAINT asssemblies_pkey PRIMARY KEY (id);


--
-- Name: dataset_keywords_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY dataset_keywords
    ADD CONSTRAINT dataset_keywords_pkey PRIMARY KEY (id);


--
-- Name: datasets_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (id);


--
-- Name: deployments_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY deployments
    ADD CONSTRAINT deployments_pkey PRIMARY KEY (id);


--
-- Name: driver_stream_link_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_pkey PRIMARY KEY (id);


--
-- Name: drivers_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY drivers
    ADD CONSTRAINT drivers_pkey PRIMARY KEY (id);


--
-- Name: files_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: inspection_status_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_pkey PRIMARY KEY (id);


--
-- Name: installation_record_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_pkey PRIMARY KEY (id);


--
-- Name: instrument_deployments_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_pkey PRIMARY KEY (id);


--
-- Name: instrument_models_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT instrument_models_pkey PRIMARY KEY (id);


--
-- Name: instruments_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_pkey PRIMARY KEY (id);


--
-- Name: manufacturers_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY manufacturers
    ADD CONSTRAINT manufacturers_pkey PRIMARY KEY (id);


--
-- Name: organizations_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: platform_deployments_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_pkey PRIMARY KEY (id);


--
-- Name: platforms_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_pkey PRIMARY KEY (id);


--
-- Name: stream_parameter_link_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_pkey PRIMARY KEY (id);


--
-- Name: stream_parameters_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY stream_parameters
    ADD CONSTRAINT stream_parameters_pkey PRIMARY KEY (id);


--
-- Name: streams_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_pkey PRIMARY KEY (id);


--
-- Name: user_scope_link_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY user_scope_link
    ADD CONSTRAINT user_scope_link_pkey PRIMARY KEY (id);


--
-- Name: user_scopes_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY user_scopes
    ADD CONSTRAINT user_scopes_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: ooiui_testing; Owner: postgres; Tablespace:
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: annotations_user_id_users_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY annotations
    ADD CONSTRAINT annotations_user_id_users_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: asset_file_link_asset_id_assets_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);


--
-- Name: asset_file_link_file_id_files_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);


--
-- Name: assets_asset_type_id_asset_types_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_asset_type_id_asset_types_id_fkey FOREIGN KEY (asset_type_id) REFERENCES asset_types(id);


--
-- Name: assets_organization_id_organizations_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_organization_id_organizations_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id);


--
-- Name: dataset_keywords_dataset_id_datasets_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY dataset_keywords
    ADD CONSTRAINT dataset_keywords_dataset_id_datasets_id_fkey FOREIGN KEY (dataset_id) REFERENCES datasets(id);


--
-- Name: datasets_deployment_id_deployments_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_deployment_id_deployments_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);


--
-- Name: datasets_stream_id_streams_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);


--
-- Name: driver_stream_link_driver_id_drivers_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_driver_id_drivers_id_fkey FOREIGN KEY (driver_id) REFERENCES drivers(id);


--
-- Name: driver_stream_link_stream_id_streams_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);


--
-- Name: drivers_instrument_id_instruments_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY drivers
    ADD CONSTRAINT drivers_instrument_id_instruments_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);


--
-- Name: foreign_key01; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT foreign_key01 FOREIGN KEY (organization_id) REFERENCES organizations(id);


--
-- Name: inspection_status_asset_id_assets_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);


--
-- Name: inspection_status_file_id_files_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);


--
-- Name: inst_models_manufacturer_id_manufacturer_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT inst_models_manufacturer_id_manufacturer_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);


--
-- Name: installation_record_assembly_id_assemblies_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_assembly_id_assemblies_id_fkey FOREIGN KEY (assembly_id) REFERENCES assemblies(id);


--
-- Name: installation_record_asset_id_assets_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);


--
-- Name: installation_record_file_id_files_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);


--
-- Name: instrument_deployments_instrument_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);


--
-- Name: instrument_deployments_platform_deployment_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_platform_deployment_id_fkey FOREIGN KEY (platform_deployment_id) REFERENCES platform_deployments(id);


--
-- Name: instruments_asset_id_assets_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);


--
-- Name: instruments_manufacturer_id_manufacturers_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_manufacturer_id_manufacturers_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);


--
-- Name: instruments_model_id.inst_models_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY instruments
    ADD CONSTRAINT "instruments_model_id.inst_models_id_fkey" FOREIGN KEY (model_id) REFERENCES instrument_models(id);


--
-- Name: platform_deployments_array_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_array_id_fkey FOREIGN KEY (array_id) REFERENCES arrays(id);


--
-- Name: platform_deployments_deployment_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_deployment_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);


--
-- Name: platform_deployments_platform_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_platform_id_fkey FOREIGN KEY (platform_id) REFERENCES platforms(id);


--
-- Name: platforms_asset_id_assets_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);


--
-- Name: platforms_manufacturer_id_manufacturers_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_manufacturer_id_manufacturers_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);


--
-- Name: stream_parameter_link_parameter_id_parameters_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_parameter_id_parameters_id_fkey FOREIGN KEY (parameter_id) REFERENCES stream_parameters(id);


--
-- Name: stream_parameter_link_stream_id_streams_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);


--
-- Name: streams_instrument_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);


--
-- Name: user_scope_link_user_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY user_scope_link
    ADD CONSTRAINT user_scope_link_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: user_scope_link_user_scopes_id_fkey; Type: FK CONSTRAINT; Schema: ooiui_testing; Owner: postgres
--

ALTER TABLE ONLY user_scope_link
    ADD CONSTRAINT user_scope_link_user_scopes_id_fkey FOREIGN KEY (scope_id) REFERENCES user_scopes(id);


--
-- Name: ooiui_testing; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA ooiui_testing FROM PUBLIC;
REVOKE ALL ON SCHEMA ooiui_testing FROM postgres;
GRANT ALL ON SCHEMA ooiui_testing TO postgres;
GRANT ALL ON SCHEMA ooiui_testing TO PUBLIC;


--
-- PostgreSQL database dump complete
--

