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
    id          SERIAL PRIMARY KEY
    array_code  TEXT,
    description TEXT,
    geography   geography,
    PRIMARY KEY (id)
);
CREATE TABLE platforms (
    id          SERIAL PRIMARY KEY,
    name        TEXT,
    description TEXT,
    location    TEXT,
    manufacturer TEXT,
    series      TEXT,
    is_mobile   BOOLEAN NOT NULL,
    serial_no   TEXT,
    asset_id    INT NOT NULL
);
CREATE TABLE instruments (
    id          SERIAL PRIMARY KEY,
    name        TEXT,
    description TEXT,
    location    TEXT,
    manufacturer TEXT,
    series      TEXT,
    serial_number TEXT,
    display_name TEXT,
    model_id    INT NOT NULL,
    asset_id    INT NOT NULL,
    depth_rating REAL
);
CREATE TABLE deployments (
    id          SERIAL PRIMARY KEY,
    start_date  DATE,
    end_date    DATE,
    cruise_id   INT
);
CREATE TABLE platform_deployments (
    id          SERIAL PRIMARY KEY,
    start_date  DATE NOT NULL,
    end_date    DATE,
    platform_id INT REFERENCES platforms(id),
    reference_designator TEXT NOT NULL,
    lat         REAL,
    lon         REAL,
    array_id    INT REFERENCES arrays(id) NOT NULL,
    deployment_id INT REFERENCES deployments(id) NOT NULL,
    display_name TEXT,
);
CREATE TABLE instrument_deployments (
    id          SERIAL PRIMARY KEY,
    display_name TEXT,
    start_date  DATE,
    end_date    DATE,
    platform_deployment_id INT REFERENCES platform_deployments(id),
    instrument_id INT REFERENCES instruments(id),
    reference_designator TEXT,
    lat         REAL,
    lon         REAL,
    depth       REAL,
    deployment_id INT REFERENCES deployments(id),
);
CREATE TABLE streams (
    id          VARCHAR(30) NOT NULL,
    instrument_id VARCHAR(30) NOT NULL,
    description VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (instrument_id) REFERENCES instruments(id)
);
CREATE TABLE stream_parameters (
    id          VARCHAR(30) NOT NULL,
    stream_id   VARCHAR(30) NOT NULL,
    description VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (stream_id) REFERENCES streams(id)
);
