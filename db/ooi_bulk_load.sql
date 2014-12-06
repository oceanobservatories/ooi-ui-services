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
-- Data for Name: arrays; Type: TABLE DATA; Schema: public; Owner: -
--

COPY arrays (id, array_code, description, geography, name) FROM stdin;
1	CP	\N	\N	Coastal Pioneer
\.


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('arrays_id_seq', 1, true);


--
-- Data for Name: deployments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY deployments (id, start_date, end_date, cruise_id) FROM stdin;
\.


--
-- Name: deployments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('deployments_id_seq', 1, false);


--
-- Data for Name: instrument_deployments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY instrument_deployments (id, display_name, start_date, end_date, platform_deployment_id, instrument_id, reference_designator, lat, lon, depth, deployment_id) FROM stdin;
1	Velocity Profiler (short range)	\N	\N	14	\N	CP02PMCI-RII01-02-ADCPTG000	40.2299995	70.8799973	\N	\N
2	Engineering Data	\N	\N	14	\N	CP02PMCI-RII01-00-ENG000000	40.2299995	70.8799973	\N	\N
3	Engineering Data	\N	\N	13	\N	CP02PMCI-SBS01-00-ENG000000	40.2299995	70.8799973	\N	\N
4	3-Axis Motion Package	\N	\N	13	\N	CP02PMCI-SBS01-01-MOPAK0000	40.2299995	70.8799973	\N	\N
5	Engineering Data	\N	\N	15	\N	CP02PMCI-WFP01-00-ENG000000	40.2299995	70.8799973	\N	\N
6	Photosynthetically Available Radiation	\N	\N	15	\N	CP02PMCI-WFP01-05-PARADK000	40.2299995	70.8799973	\N	\N
7	3-Wavelength Fluorometer	\N	\N	15	\N	CP02PMCI-WFP01-04-FLORTK000	40.2299995	70.8799973	\N	\N
8	CTD Profiler	\N	\N	15	\N	CP02PMCI-WFP01-03-CTDPFK000	40.2299995	70.8799973	\N	\N
9	Dissolved Oxygen Fast Response	\N	\N	15	\N	CP02PMCI-WFP01-02-DOFSTK000	40.2299995	70.8799973	\N	\N
10	3-D Single Point Velocity Meter	\N	\N	15	\N	CP02PMCI-WFP01-01-VEL3DK000	40.2299995	70.8799973	\N	\N
11	Velocity Profiler (short range)	\N	\N	17	\N	CP02PMCO-RII01-02-ADCPTG000	40.0999985	70.8799973	\N	\N
12	Engineering Data	\N	\N	17	\N	CP02PMCO-RII01-00-ENG000000	40.0999985	70.8799973	\N	\N
13	Engineering Data	\N	\N	16	\N	CP02PMCO-SBS01-00-ENG000000	40.0999985	70.8799973	\N	\N
14	3-Axis Motion Package	\N	\N	16	\N	CP02PMCO-SBS01-01-MOPAK0000	40.0999985	70.8799973	\N	\N
15	Dissolved Oxygen Fast Response	\N	\N	18	\N	CP02PMCO-WFP01-02-DOFSTK000	40.0999985	70.8799973	\N	\N
16	Engineering Data	\N	\N	18	\N	CP02PMCO-WFP01-00-ENG000000	40.0999985	70.8799973	\N	\N
17	3-D Single Point Velocity Meter	\N	\N	18	\N	CP02PMCO-WFP01-01-VEL3DK000	40.0999985	70.8799973	\N	\N
18	CTD Profiler	\N	\N	18	\N	CP02PMCO-WFP01-03-CTDPFK000	40.0999985	70.8799973	\N	\N
19	3-Wavelength Fluorometer	\N	\N	18	\N	CP02PMCO-WFP01-04-FLORTK000	40.0999985	70.8799973	\N	\N
20	Photosynthetically Available Radiation	\N	\N	18	\N	CP02PMCO-WFP01-05-PARADK000	40.0999985	70.8799973	\N	\N
21	Engineering Data	\N	\N	8	\N	CP02PMUI-RII01-00-ENG000000	40.3699989	70.7799988	\N	\N
22	Velocity Profiler (short range)	\N	\N	8	\N	CP02PMUI-RII01-02-ADCPTG000	40.3699989	70.7799988	\N	\N
23	3-Axis Motion Package	\N	\N	7	\N	CP02PMUI-SBS01-01-MOPAK0000	40.3699989	70.7799988	\N	\N
24	Engineering Data	\N	\N	7	\N	CP02PMUI-SBS01-00-ENG000000	40.3699989	70.7799988	\N	\N
25	Dissolved Oxygen Fast Response	\N	\N	9	\N	CP02PMUI-WFP01-02-DOFSTK000	40.3699989	70.7799988	\N	\N
26	Engineering Data	\N	\N	9	\N	CP02PMUI-WFP01-00-ENG000000	40.3699989	70.7799988	\N	\N
27	Photosynthetically Available Radiation	\N	\N	9	\N	CP02PMUI-WFP01-05-PARADK000	40.3699989	70.7799988	\N	\N
28	3-Wavelength Fluorometer	\N	\N	9	\N	CP02PMUI-WFP01-04-FLORTK000	40.3699989	70.7799988	\N	\N
29	CTD Profiler	\N	\N	9	\N	CP02PMUI-WFP01-03-CTDPFK000	40.3699989	70.7799988	\N	\N
30	3-D Single Point Velocity Meter	\N	\N	9	\N	CP02PMUI-WFP01-01-VEL3DK000	40.3699989	70.7799988	\N	\N
31	Velocity Profiler (short range)	\N	\N	11	\N	CP02PMUO-RII01-02-ADCPSL000	39.9399986	70.7799988	\N	\N
32	Engineering Data	\N	\N	11	\N	CP02PMUO-RII01-00-ENG000000	39.9399986	70.7799988	\N	\N
33	Engineering Data	\N	\N	10	\N	CP02PMUO-SBS01-00-ENG000000	39.9399986	70.7799988	\N	\N
34	3-Axis Motion Package	\N	\N	10	\N	CP02PMUO-SBS01-01-MOPAK0000	39.9399986	70.7799988	\N	\N
35	CTD Profiler	\N	\N	12	\N	CP02PMUO-WFP01-03-CTDPFK000	39.9399986	70.7799988	\N	\N
36	Engineering Data	\N	\N	12	\N	CP02PMUO-WFP01-00-ENG000000	39.9399986	70.7799988	\N	\N
37	3-Wavelength Fluorometer	\N	\N	12	\N	CP02PMUO-WFP01-04-FLORTK000	39.9399986	70.7799988	\N	\N
38	Photosynthetically Available Radiation	\N	\N	12	\N	CP02PMUO-WFP01-05-PARADK000	39.9399986	70.7799988	\N	\N
39	Dissolved Oxygen Fast Response	\N	\N	12	\N	CP02PMUO-WFP01-02-DOFSTK000	39.9399986	70.7799988	\N	\N
40	3-D Single Point Velocity Meter	\N	\N	12	\N	CP02PMUO-WFP01-01-VEL3DK000	39.9399986	70.7799988	\N	\N
41	Engineering Data	\N	\N	5	\N	CP04OSPM-SBS11-00-ENG000000	39.9399986	70.8799973	\N	\N
42	3-Axis Motion Package	\N	\N	5	\N	CP04OSPM-SBS11-02-MOPAK0000	39.9399986	70.8799973	\N	\N
43	3-D Single Point Velocity Meter	\N	\N	6	\N	CP04OSPM-WFP01-01-VEL3DK000	39.9399986	70.8799973	\N	\N
44	CTD Profiler	\N	\N	6	\N	CP04OSPM-WFP01-03-CTDPFK000	39.9399986	70.8799973	\N	\N
45	Engineering Data	\N	\N	6	\N	CP04OSPM-WFP01-00-ENG000000	39.9399986	70.8799973	\N	\N
46	3-Wavelength Fluorometer	\N	\N	6	\N	CP04OSPM-WFP01-04-FLORTK000	39.9399986	70.8799973	\N	\N
47	Photosynthetically Available Radiation	\N	\N	6	\N	CP04OSPM-WFP01-05-PARADK000	39.9399986	70.8799973	\N	\N
48	Dissolved Oxygen Fast Response	\N	\N	6	\N	CP04OSPM-WFP01-02-DOFSTK000	39.9399986	70.8799973	\N	\N
49	Engineering Data	\N	\N	25	\N	CP05MOAS-AV001-00-ENG000000	-999	-999	\N	\N
50	Photosynthetically Available Radiation	\N	\N	25	\N	CP05MOAS-AV001-06-PARADN000	-999	-999	\N	\N
51	Nitrate	\N	\N	25	\N	CP05MOAS-AV001-04-NUTNRN000	-999	-999	\N	\N
52	\N	\N	\N	25	\N	CP05MOAS-AV001-03-CTDAVN000	-999	-999	\N	\N
53	3-Wavelength Fluorometer	\N	\N	25	\N	CP05MOAS-AV001-01-FLORTN000	-999	-999	\N	\N
54	Dissolved Oxygen Stable Response	\N	\N	25	\N	CP05MOAS-AV001-02-DOSTAN000	-999	-999	\N	\N
55	Velocity Profiler (short range)	\N	\N	25	\N	CP05MOAS-AV001-05-ADCPAN000	-999	-999	\N	\N
56	3-Wavelength Fluorometer	\N	\N	26	\N	CP05MOAS-AV002-01-FLORTN000	-999	-999	\N	\N
57	\N	\N	\N	26	\N	CP05MOAS-AV002-03-CTDAVN000	-999	-999	\N	\N
58	Nitrate	\N	\N	26	\N	CP05MOAS-AV002-04-NUTNRN000	-999	-999	\N	\N
59	Velocity Profiler (short range)	\N	\N	26	\N	CP05MOAS-AV002-05-ADCPAN000	-999	-999	\N	\N
60	Photosynthetically Available Radiation	\N	\N	26	\N	CP05MOAS-AV002-06-PARADN000	-999	-999	\N	\N
61	Engineering Data	\N	\N	26	\N	CP05MOAS-AV002-00-ENG000000	-999	-999	\N	\N
62	Dissolved Oxygen Stable Response	\N	\N	26	\N	CP05MOAS-AV002-02-DOSTAN000	-999	-999	\N	\N
63	3-Wavelength Fluorometer	\N	\N	19	\N	CP05MOAS-GL001-02-FLORTM000	-999	-999	\N	\N
64	Engineering Data	\N	\N	19	\N	CP05MOAS-GL001-00-ENG000000	-999	-999	\N	\N
65	Photosynthetically Available Radiation	\N	\N	19	\N	CP05MOAS-GL001-05-PARADM000	-999	-999	\N	\N
66	Dissolved Oxygen Stable Response	\N	\N	19	\N	CP05MOAS-GL001-04-DOSTAM000	-999	-999	\N	\N
67	CTD Profiler	\N	\N	19	\N	CP05MOAS-GL001-03-CTDGVM000	-999	-999	\N	\N
68	Velocity Profiler (short range)	\N	\N	19	\N	CP05MOAS-GL001-01-ADCPAM000	-999	-999	\N	\N
69	Velocity Profiler (short range)	\N	\N	20	\N	CP05MOAS-GL002-01-ADCPAM000	-999	-999	\N	\N
70	Photosynthetically Available Radiation	\N	\N	20	\N	CP05MOAS-GL002-05-PARADM000	-999	-999	\N	\N
71	Dissolved Oxygen Stable Response	\N	\N	20	\N	CP05MOAS-GL002-04-DOSTAM000	-999	-999	\N	\N
72	CTD Profiler	\N	\N	20	\N	CP05MOAS-GL002-03-CTDGVM000	-999	-999	\N	\N
73	3-Wavelength Fluorometer	\N	\N	20	\N	CP05MOAS-GL002-02-FLORTM000	-999	-999	\N	\N
74	Engineering Data	\N	\N	20	\N	CP05MOAS-GL002-00-ENG000000	-999	-999	\N	\N
75	CTD Profiler	\N	\N	21	\N	CP05MOAS-GL003-03-CTDGVM000	-999	-999	\N	\N
76	Dissolved Oxygen Stable Response	\N	\N	21	\N	CP05MOAS-GL003-04-DOSTAM000	-999	-999	\N	\N
77	Velocity Profiler (short range)	\N	\N	21	\N	CP05MOAS-GL003-01-ADCPAM000	-999	-999	\N	\N
78	Engineering Data	\N	\N	21	\N	CP05MOAS-GL003-00-ENG000000	-999	-999	\N	\N
79	Photosynthetically Available Radiation	\N	\N	21	\N	CP05MOAS-GL003-05-PARADM000	-999	-999	\N	\N
80	3-Wavelength Fluorometer	\N	\N	21	\N	CP05MOAS-GL003-02-FLORTM000	-999	-999	\N	\N
81	Photosynthetically Available Radiation	\N	\N	22	\N	CP05MOAS-GL004-05-PARADM000	-999	-999	\N	\N
82	Velocity Profiler (short range)	\N	\N	22	\N	CP05MOAS-GL004-01-ADCPAM000	-999	-999	\N	\N
83	3-Wavelength Fluorometer	\N	\N	22	\N	CP05MOAS-GL004-02-FLORTM000	-999	-999	\N	\N
84	CTD Profiler	\N	\N	22	\N	CP05MOAS-GL004-03-CTDGVM000	-999	-999	\N	\N
85	Dissolved Oxygen Stable Response	\N	\N	22	\N	CP05MOAS-GL004-04-DOSTAM000	-999	-999	\N	\N
86	Engineering Data	\N	\N	22	\N	CP05MOAS-GL004-00-ENG000000	-999	-999	\N	\N
87	Photosynthetically Available Radiation	\N	\N	23	\N	CP05MOAS-GL005-05-PARADM000	-999	-999	\N	\N
88	Dissolved Oxygen Stable Response	\N	\N	23	\N	CP05MOAS-GL005-04-DOSTAM000	-999	-999	\N	\N
89	Engineering Data	\N	\N	23	\N	CP05MOAS-GL005-00-ENG000000	-999	-999	\N	\N
90	CTD Profiler	\N	\N	23	\N	CP05MOAS-GL005-03-CTDGVM000	-999	-999	\N	\N
91	3-Wavelength Fluorometer	\N	\N	23	\N	CP05MOAS-GL005-02-FLORTM000	-999	-999	\N	\N
92	Velocity Profiler (short range)	\N	\N	23	\N	CP05MOAS-GL005-01-ADCPAM000	-999	-999	\N	\N
93	3-Wavelength Fluorometer	\N	\N	24	\N	CP05MOAS-GL006-02-FLORTM000	-999	-999	\N	\N
94	Dissolved Oxygen Stable Response	\N	\N	24	\N	CP05MOAS-GL006-04-DOSTAM000	-999	-999	\N	\N
95	Photosynthetically Available Radiation	\N	\N	24	\N	CP05MOAS-GL006-05-PARADM000	-999	-999	\N	\N
96	Engineering Data	\N	\N	24	\N	CP05MOAS-GL006-00-ENG000000	-999	-999	\N	\N
97	CTD Profiler	\N	\N	24	\N	CP05MOAS-GL006-03-CTDGVM000	-999	-999	\N	\N
98	Velocity Profiler (short range)	\N	\N	24	\N	CP05MOAS-GL006-01-ADCPAM000	-999	-999	\N	\N
\.


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('instrument_deployments_id_seq', 98, true);


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY instruments (id, name, description, location, manufacturer, series, serial_number, display_name, model_id, asset_id, depth_rating) FROM stdin;
\.


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('instruments_id_seq', 1, false);


--
-- Data for Name: platform_deployments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY platform_deployments (id, start_date, end_date, platform_id, reference_designator, lat, lon, array_id, deployment_id, display_name) FROM stdin;
5	\N	\N	\N	CP04OSPM-SBS11	39.9333344	-70.8784332	1	\N	Pioneer Offshore Profiler Mooring - Surface Buoy
6	\N	\N	\N	CP04OSPM-WFP01	39.9333344	-70.8784332	1	\N	Pioneer Offshore Profiler Mooring - Wire-Following Profiler
7	\N	\N	\N	CP02PMUI-SBS01	40.8973999	-70.6860123	1	\N	Pioneer Upstream Inshore Profiler Mooring - Surface Buoy
8	\N	\N	\N	CP02PMUI-RII01	40.8973999	-70.6860123	1	\N	Pioneer Upstream Inshore Profiler Mooring - Mooring Riser
9	\N	\N	\N	CP02PMUI-WFP01	40.8973999	-70.6860123	1	\N	Pioneer Upstream Inshore Profiler Mooring - Wire-Following Profiler
10	\N	\N	\N	CP02PMUO-SBS01	39.9430199	-70.7700119	1	\N	Pioneer Upstream Offshore Profiler Mooring - Surface Buoy
11	\N	\N	\N	CP02PMUO-RII01	39.9430199	-70.7700119	1	\N	Pioneer Upstream Offshore Profiler Mooring - Surface Buoy
12	\N	\N	\N	CP02PMUO-WFP01	39.9430199	-70.7700119	1	\N	Pioneer Upstream Offshore Profiler Mooring - Wire-Following Profiler
13	\N	\N	\N	CP02PMCI-SBS01	40.226532	-70.8779526	1	\N	Pioneer Central Inshore Profiler Mooring - Surface Buoy
14	\N	\N	\N	CP02PMCI-RII01	40.226532	-70.8779526	1	\N	Pioneer Central Inshore Profiler Mooring - Mooring Riser
15	\N	\N	\N	CP02PMCI-WFP01	40.226532	-70.8779526	1	\N	Pioneer Central Inshore Profiler Mooring - Wire-Following Profiler
16	\N	\N	\N	CP02PMCO-SBS01	40.1012344	-70.8876801	1	\N	Pioneer Central Offshore Profiler Mooring - Surface Buoy
17	\N	\N	\N	CP02PMCO-RII01	40.1012344	-70.8876801	1	\N	Pioneer Central Offshore Profiler Mooring - Mooring Riser
18	\N	\N	\N	CP02PMCO-WFP01	40.1012344	-70.8876801	1	\N	Pioneer Central Offshore Profiler Mooring - Wire-Following Profiler
19	\N	\N	\N	CP05MOAS-GL001	40.0833015	-70.25	1	\N	Pioneer Mobile Coastal Glider #1
20	\N	\N	\N	CP05MOAS-GL002	40.0833015	-70.25	1	\N	Pioneer Mobile Coastal Glider #2
21	\N	\N	\N	CP05MOAS-GL003	40.0833015	-70.25	1	\N	Pioneer Mobile Coastal Glider #3
22	\N	\N	\N	CP05MOAS-GL004	40.0833015	-70.25	1	\N	Pioneer Mobile Coastal Glider #4
23	\N	\N	\N	CP05MOAS-GL005	40.0833015	-70.25	1	\N	Pioneer Mobile Coastal Glider #5
24	\N	\N	\N	CP05MOAS-GL006	40.0833015	-70.25	1	\N	Pioneer Mobile Coastal Glider #6
25	\N	\N	\N	CP05MOAS-AV001	40.0833015	-70.25	1	\N	Pioneer Mobile AUV #1
26	\N	\N	\N	CP05MOAS-AV002	40.0833015	-70.25	1	\N	Pioneer Mobile AUV #2
\.


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('platform_deployments_id_seq', 26, true);


--
-- Data for Name: platforms; Type: TABLE DATA; Schema: public; Owner: -
--

COPY platforms (id, name, description, location, manufacturer, series, is_mobile, serial_no, asset_id) FROM stdin;
\.


--
-- Name: platforms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('platforms_id_seq', 1, false);


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: -
--

COPY spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: stream_parameters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY stream_parameters (id, stream_id, name, short_name, long_name, standard_name, units, data_type) FROM stdin;
\.


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('stream_parameters_id_seq', 1, false);


--
-- Data for Name: streams; Type: TABLE DATA; Schema: public; Owner: -
--

COPY streams (id, name, instrument_id, description) FROM stdin;
\.


--
-- Name: streams_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('streams_id_seq', 1, false);


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

