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
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: arrays; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE arrays (
    id integer NOT NULL,
    array_code text,
    description text,
    geography geography(Polygon,4326),
    name text
);


--
-- Name: arrays_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE arrays_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: arrays_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE arrays_id_seq OWNED BY arrays.id;


--
-- Name: deployments; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE deployments (
    id integer NOT NULL,
    start_date date,
    end_date date,
    cruise_id integer
);


--
-- Name: deployments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: deployments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE deployments_id_seq OWNED BY deployments.id;


--
-- Name: instrument_deployments; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE instrument_deployments (
    id integer NOT NULL,
    display_name text,
    start_date date,
    end_date date,
    platform_deployment_id integer,
    instrument_id integer,
    reference_designator text,
    lat real,
    lon real,
    depth real,
    deployment_id integer
);


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE instrument_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE instrument_deployments_id_seq OWNED BY instrument_deployments.id;


--
-- Name: instruments; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE instruments (
    id integer NOT NULL,
    name text,
    description text,
    location text,
    manufacturer text,
    series text,
    serial_number text,
    display_name text,
    model_id integer NOT NULL,
    asset_id integer NOT NULL,
    depth_rating real
);


--
-- Name: instruments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE instruments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: instruments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE instruments_id_seq OWNED BY instruments.id;


--
-- Name: platform_deployments; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE platform_deployments (
    id integer NOT NULL,
    start_date date,
    end_date date,
    platform_id integer,
    reference_designator text NOT NULL,
    lat real,
    lon real,
    array_id integer,
    deployment_id integer,
    display_name text
);


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE platform_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE platform_deployments_id_seq OWNED BY platform_deployments.id;


--
-- Name: platforms; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE platforms (
    id integer NOT NULL,
    name text,
    description text,
    location text,
    manufacturer text,
    series text,
    is_mobile boolean NOT NULL,
    serial_no text,
    asset_id integer NOT NULL
);


--
-- Name: platforms_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE platforms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: platforms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE platforms_id_seq OWNED BY platforms.id;


--
-- Name: stream_parameters; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE stream_parameters (
    id integer NOT NULL,
    stream_id integer,
    name text,
    short_name text,
    long_name text,
    standard_name text,
    units text,
    data_type text
);


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE stream_parameters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE stream_parameters_id_seq OWNED BY stream_parameters.id;


--
-- Name: streams; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE streams (
    id integer NOT NULL,
    name text,
    instrument_id integer,
    description text
);


--
-- Name: streams_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE streams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: streams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE streams_id_seq OWNED BY streams.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY arrays ALTER COLUMN id SET DEFAULT nextval('arrays_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY deployments ALTER COLUMN id SET DEFAULT nextval('deployments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY instrument_deployments ALTER COLUMN id SET DEFAULT nextval('instrument_deployments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY instruments ALTER COLUMN id SET DEFAULT nextval('instruments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY platform_deployments ALTER COLUMN id SET DEFAULT nextval('platform_deployments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY platforms ALTER COLUMN id SET DEFAULT nextval('platforms_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY stream_parameters ALTER COLUMN id SET DEFAULT nextval('stream_parameters_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY streams ALTER COLUMN id SET DEFAULT nextval('streams_id_seq'::regclass);


--
-- Name: arrays_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY arrays
    ADD CONSTRAINT arrays_pkey PRIMARY KEY (id);


--
-- Name: deployments_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY deployments
    ADD CONSTRAINT deployments_pkey PRIMARY KEY (id);


--
-- Name: instrument_deployments_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_pkey PRIMARY KEY (id);


--
-- Name: instruments_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_pkey PRIMARY KEY (id);


--
-- Name: platform_deployments_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_pkey PRIMARY KEY (id);


--
-- Name: platforms_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_pkey PRIMARY KEY (id);


--
-- Name: stream_parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY stream_parameters
    ADD CONSTRAINT stream_parameters_pkey PRIMARY KEY (id);


--
-- Name: streams_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_pkey PRIMARY KEY (id);


--
-- Name: instrument_deployments_deployment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_deployment_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);


--
-- Name: instrument_deployments_instrument_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);


--
-- Name: instrument_deployments_platform_deployment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_platform_deployment_id_fkey FOREIGN KEY (platform_deployment_id) REFERENCES platform_deployments(id);


--
-- Name: platform_deployments_array_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_array_id_fkey FOREIGN KEY (array_id) REFERENCES arrays(id);


--
-- Name: platform_deployments_deployment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_deployment_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);


--
-- Name: platform_deployments_platform_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_platform_id_fkey FOREIGN KEY (platform_id) REFERENCES platforms(id);


--
-- Name: stream_parameters_stream_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY stream_parameters
    ADD CONSTRAINT stream_parameters_stream_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);


--
-- Name: streams_instrument_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM luke;
GRANT ALL ON SCHEMA public TO luke;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

