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
    id          VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    geography   geography,
    PRIMARY KEY (id)
);
CREATE TABLE platforms (
    id          VARCHAR(30) NOT NULL,
    array_id    VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    geography   geography,
    PRIMARY KEY (id),
    FOREIGN KEY (array_id) REFERENCES arrays(id)
);
CREATE TABLE platform_deployments (
    id          VARCHAR(30) NOT NULL,
    platform_id VARCHAR(30) NOT NULL,
    start_date  DATE NOT NULL,
    end_date    DATE,
    PRIMARY KEY(id),
    FOREIGN KEY (platform_id) REFERENCES platforms(id)
);
CREATE TABLE instruments (
    id          VARCHAR(30) NOT NULL,
    platform_id VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    geography   geography,
    PRIMARY KEY (id),
    FOREIGN KEY (platform_id) REFERENCES platforms(id)
);
CREATE TABLE instrument_deployments (
    id          VARCHAR(30) NOT NULL,
    instrument_id VARCHAR(30) NOT NULL,
    start_date  DATE NOT NULL,
    end_date    DATE,
    PRIMARY KEY(id),
    FOREIGN KEY (instrument_id) REFERENCES instruments(id)
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