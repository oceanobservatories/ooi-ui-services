/* __author__ = 'Matt Campbell'
Usage:
    Create the DB:
        psql -c 'create database <dbname>;' -U <username>
    Requires: postgis
        psql -U <username> <dbname> -c "create extension postgis;"
    Load the schema:
        psql <dbname> < <path_to>ooiservices_schema.sql
*/
CREATE TABLE arrays (
    id SERIAL NOT NULL,
    ref_id text UNIQUE NOT NULL,
    display_name text,
    geo_location geography(Polygon,4326),
    array_name text,
    description text,

    PRIMARY KEY (id)
);
CREATE TABLE platform_deployments (
    id SERIAL NOT NULL,
    start_date date,
    end_date date,
    platform_id integer,
    ref_id text UNIQUE NOT NULL,
    array_code text,
    deployment_id integer,
    display_name text,
    geo_location geography(Point,4326),

    PRIMARY KEY (id),
    FOREIGN KEY (array_code) REFERENCES arrays(ref_id)
);
CREATE TABLE instrument_deployments (
    id SERIAL NOT NULL,
    display_name text,
    start_date date,
    end_date date,
    platform_deployment_code text,
    instrument_id integer,
    ref_id text UNIQUE NOT NULL,
    depth real,
    geo_location geography,

    PRIMARY KEY (id),
    FOREIGN KEY (platform_deployment_code) REFERENCES platform_deployments(ref_id)
);
CREATE TABLE streams (
    id SERIAL NOT NULL,
    stream_name text,
    instrument_id integer,
    description text,
    instrument_deployment_code text,

    PRIMARY KEY (id),
    FOREIGN KEY (instrument_deployment_code) REFERENCES instrument_deployments(ref_id)
);
CREATE TABLE stream_parameters (
    id SERIAL NOT NULL,
    stream_parameter_name text,
    short_name text,
    long_name text,
    standard_name text,
    units text,
    data_type text,

    PRIMARY KEY (id)
);
CREATE TABLE stream_parameter_link (
    id SERIAL NOT NULL,
    stream_id integer NOT NULL,
    parameter_id integer NOT NULL,

    PRIMARY KEY (id)
);
CREATE TABLE datasets (
    id SERIAL NOT NULL,
    stream_id integer NOT NULL,
    deployment_id integer NOT NULL,
    process_level text,
    is_recovered boolean DEFAULT false NOT NULL,

    PRIMARY KEY (id)
);
CREATE TABLE dataset_keywords (
    id SERIAL NOT NULL,
    dataset_id integer NOT NULL,
    concept_name text,
    concept_description text,

    PRIMARY KEY (id)
);
CREATE TABLE drivers (
    id SERIAL NOT NULL,
    instrument_id integer,
    driver_name text NOT NULL,
    driver_version text,
    author text,

    PRIMARY KEY (id)
);
CREATE TABLE driver_stream_link (
    id SERIAL NOT NULL,
    driver_id integer NOT NULL,
    stream_id integer NOT NULL,

    PRIMARY KEY (id)
);
CREATE TABLE ooi_scopes (
	id text NOT NULL,

	PRIMARY KEY (id)
);
CREATE TABLE ooi_users (
	id text NOT NULL,
	pass_hash text NOT NULL,
    user_scope text,

	PRIMARY KEY (id),
	FOREIGN KEY (user_scope) REFERENCES ooi_scopes(id)
);