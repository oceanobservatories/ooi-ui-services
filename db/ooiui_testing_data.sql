--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = luke_dev, pg_catalog;

--
-- Data for Name: arrays; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY arrays (id, array_code, description, geography, name) FROM stdin;
1	CP	\N	\N	Coastal Pioneer
2	GP	\N	\N	Global Station Papa
\.


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('arrays_id_seq', 2, true);


--
-- Data for Name: deployments; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY deployments (id, start_date, end_date, cruise_id) FROM stdin;
\.


--
-- Name: deployments_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('deployments_id_seq', 1, false);


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY instruments (id, name, description, location, manufacturer, series, serial_number, display_name, model_id, asset_id, depth_rating) FROM stdin;
\.


--
-- Data for Name: platforms; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY platforms (id, name, description, location, manufacturer, series, is_mobile, serial_no, asset_id) FROM stdin;
\.


--
-- Data for Name: platform_deployments; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY platform_deployments (id, start_date, end_date, platform_id, reference_designator, lat, lon, array_id, deployment_id, display_name) FROM stdin;
5	\N	\N	\N	CP04OSPM-SBS11	39.9333	-70.8784027	1	\N	Pioneer Offshore Profiler Mooring - Surface Buoy
6	\N	\N	\N	CP04OSPM-WFP01	39.9333	-70.8784027	1	\N	Pioneer Offshore Profiler Mooring - Wire-Following Profiler
7	\N	\N	\N	CP02PMUI-SBS01	40.8973999	-70.685997	1	\N	Pioneer Upstream Inshore Profiler Mooring - Surface Buoy
8	\N	\N	\N	CP02PMUI-RII01	40.8973999	-70.685997	1	\N	Pioneer Upstream Inshore Profiler Mooring - Mooring Riser
9	\N	\N	\N	CP02PMUI-WFP01	40.8973999	-70.685997	1	\N	Pioneer Upstream Inshore Profiler Mooring - Wire-Following Profiler
10	\N	\N	\N	CP02PMUO-SBS01	39.9430008	-70.7699966	1	\N	Pioneer Upstream Offshore Profiler Mooring - Surface Buoy
11	\N	\N	\N	CP02PMUO-RII01	39.9430008	-70.7699966	1	\N	Pioneer Upstream Offshore Profiler Mooring - Surface Buoy
12	\N	\N	\N	CP02PMUO-WFP01	39.9430008	-70.7699966	1	\N	Pioneer Upstream Offshore Profiler Mooring - Wire-Following Profiler
13	\N	\N	\N	CP02PMCI-SBS01	40.2265015	-70.8779984	1	\N	Pioneer Central Inshore Profiler Mooring - Surface Buoy
14	\N	\N	\N	CP02PMCI-RII01	40.2265015	-70.8779984	1	\N	Pioneer Central Inshore Profiler Mooring - Mooring Riser
15	\N	\N	\N	CP02PMCI-WFP01	40.2265015	-70.8779984	1	\N	Pioneer Central Inshore Profiler Mooring - Wire-Following Profiler
16	\N	\N	\N	CP02PMCO-SBS01	40.1012001	-70.8877029	1	\N	Pioneer Central Offshore Profiler Mooring - Surface Buoy
17	\N	\N	\N	CP02PMCO-RII01	40.1012001	-70.8877029	1	\N	Pioneer Central Offshore Profiler Mooring - Mooring Riser
18	\N	\N	\N	CP02PMCO-WFP01	40.1012001	-70.8877029	1	\N	Pioneer Central Offshore Profiler Mooring - Wire-Following Profiler
19	\N	\N	\N	CP05MOAS-GL001	40.0833015	-70.25	1	\N	Pioneer Mobile Glider 001
20	\N	\N	\N	CP05MOAS-GL002	40.0833015	-70.25	1	\N	Pioneer Mobile Glider 002
21	\N	\N	\N	CP05MOAS-GL003	40.0833015	-70.25	1	\N	Pioneer Mobile Glider 003
22	\N	\N	\N	CP05MOAS-GL004	40.0833015	-70.25	1	\N	Pioneer Mobile Glider 004
23	\N	\N	\N	CP05MOAS-GL005	40.0833015	-70.25	1	\N	Pioneer Mobile Glider 005
24	\N	\N	\N	CP05MOAS-GL006	40.0833015	-70.25	1	\N	Pioneer Mobile Glider 006
25	\N	\N	\N	CP05MOAS-AV001	40.0833015	-70.25	1	\N	Pioneer Mobile AUV #1
26	\N	\N	\N	CP05MOAS-AV002	40.0833015	-70.25	1	\N	Pioneer Mobile AUV #2
27	\N	\N	\N	GP05MOAS-GL001	50.2289009	-144.348007	\N	\N	Station Papa Mobile Glider 001
31	\N	\N	\N	GP05MOAS-GL002	\N	\N	\N	\N	Station Papa Mobile Glider 002
32	\N	\N	\N	GP05MOAS-GL003	\N	\N	\N	\N	Station Papa Mobile Glider 003
33	\N	\N	\N	GI05MOAS-GL001	59.9300766	-39.3083687	\N	\N	Irminger Sea Mobile Glider 001
34	\N	\N	\N	GI05MOAS-GL002	59.8968544	-39.5404854	\N	\N	Irminger Sea Mobile Glider 002
35	\N	\N	\N	GI05MOAS-GL003	59.9926414	-39.3607292	\N	\N	Irminger Sea Mobile Glider 003
36	\N	\N	\N	CE05MOAS-GL320	\N	\N	\N	\N	Endurance Mobile Glider 320
37	\N	\N	\N	RS00ENGC-XX00X	\N	\N	\N	\N	Testing Platform
38	\N	\N	\N	CE05MOAS-GL381	\N	\N	\N	\N	Endurance Mobile Glider 381
39	\N	\N	\N	RS01BATH-XX00X	\N	\N	\N	\N	Cabled Bathtub Instrument
40	\N	\N	\N	CP04OSPM-SBS01	\N	\N	\N	\N	Pioneer Offshore Profiler Mooring - Surface Buoy
\.


--
-- Data for Name: instrument_deployments; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY instrument_deployments (id, display_name, start_date, end_date, platform_deployment_id, instrument_id, reference_designator, lat, lon, depth, deployment_id) FROM stdin;
173	Engineering Data	\N	\N	9	\N	CP02PMUI-WFP01-00-STCENG000	\N	\N	\N	\N
174	Engineering Data	\N	\N	33	\N	GI05MOAS-GL001-00-ENG000000	\N	\N	\N	\N
175	2-Wavelength Fluorometer	\N	\N	33	\N	GI05MOAS-GL001-01-FLORDM000	\N	\N	\N	\N
176	Dissolved Oxygen Stable Response	\N	\N	33	\N	GI05MOAS-GL001-02-DOSTAM000	\N	\N	\N	\N
177	CTD Profiler	\N	\N	33	\N	GI05MOAS-GL001-04-CTDGVM000	\N	\N	\N	\N
178	Engineering Data	\N	\N	35	\N	GI05MOAS-GL003-00-ENG000000	\N	\N	\N	\N
179	2-Wavelength Fluorometer	\N	\N	35	\N	GI05MOAS-GL003-01-FLORDM000	\N	\N	\N	\N
180	Dissolved Oxygen Stable Response	\N	\N	35	\N	GI05MOAS-GL003-02-DOSTAM000	\N	\N	\N	\N
181	CTD Profiler	\N	\N	35	\N	GI05MOAS-GL003-04-CTDGVM000	\N	\N	\N	\N
182	Engineering Data	\N	\N	13	\N	CP02PMCI-SBS01-00-STCENG000	\N	\N	\N	\N
183	Velocity Profiler (short range)	\N	\N	14	\N	CP02PMCI-RII01-01-ADCPTG000	\N	\N	\N	\N
184	Engineering Data	\N	\N	33	\N	GI05MOAS-GL001-00-ENG000000	\N	\N	\N	\N
185	2-Wavelength Fluorometer	\N	\N	33	\N	GI05MOAS-GL001-01-FLORDM000	\N	\N	\N	\N
186	Dissolved Oxygen Stable Response	\N	\N	33	\N	GI05MOAS-GL001-02-DOSTAM000	\N	\N	\N	\N
187	CTD Profiler	\N	\N	33	\N	GI05MOAS-GL001-04-CTDGVM000	\N	\N	\N	\N
188	Engineering Data	\N	\N	35	\N	GI05MOAS-GL003-00-ENG000000	\N	\N	\N	\N
189	2-Wavelength Fluorometer	\N	\N	35	\N	GI05MOAS-GL003-01-FLORDM000	\N	\N	\N	\N
190	Dissolved Oxygen Stable Response	\N	\N	35	\N	GI05MOAS-GL003-02-DOSTAM000	\N	\N	\N	\N
99	Engineering Data	\N	\N	36	\N	CE05MOAS-GL320-00-ENG000000	\N	\N	\N	\N
100	Engineering Data	\N	\N	36	\N	CE05MOAS-GL320-00-ENG000000	\N	\N	\N	\N
101	Engineering Data	\N	\N	36	\N	CE05MOAS-GL320-00-ENG000000	\N	\N	\N	\N
106	Engineering Data	\N	\N	38	\N	CE05MOAS-GL381-00-ENG000000	\N	\N	\N	\N
107	Engineering Data	\N	\N	38	\N	CE05MOAS-GL381-00-ENG000000	\N	\N	\N	\N
108	Engineering Data	\N	\N	38	\N	CE05MOAS-GL381-00-ENG000000	\N	\N	\N	\N
128	Engineering Data	\N	\N	40	\N	CP04OSPM-SBS01-00-STCENG000	\N	\N	\N	\N
115	Engineering Data	\N	\N	16	\N	CP02PMCO-SBS01-00-STCENG000	\N	\N	\N	\N
116	Engineering Data	\N	\N	18	\N	CP02PMCO-WFP01-00-STCENG000	\N	\N	\N	\N
117	Engineering Data	\N	\N	18	\N	CP02PMCO-WFP01-00-STCENG000	\N	\N	\N	\N
118	Engineering Data	\N	\N	18	\N	CP02PMCO-WFP01-00-STCENG000	\N	\N	\N	\N
121	Engineering Data	\N	\N	7	\N	CP02PMUI-SBS01-00-STCENG000	\N	\N	\N	\N
124	Engineering Data	\N	\N	10	\N	CP02PMUO-SBS01-00-STCENG000	\N	\N	\N	\N
125	Engineering Data	\N	\N	12	\N	CP02PMUO-WFP01-00-STCENG000	\N	\N	\N	\N
126	Engineering Data	\N	\N	12	\N	CP02PMUO-WFP01-00-STCENG000	\N	\N	\N	\N
127	Engineering Data	\N	\N	12	\N	CP02PMUO-WFP01-00-STCENG000	\N	\N	\N	\N
130	Engineering Data	\N	\N	6	\N	CP04OSPM-WFP01-00-STCENG000	\N	\N	\N	\N
131	Engineering Data	\N	\N	6	\N	CP04OSPM-WFP01-00-STCENG000	\N	\N	\N	\N
132	Engineering Data	\N	\N	6	\N	CP04OSPM-WFP01-00-STCENG000	\N	\N	\N	\N
137	Engineering Data	\N	\N	34	\N	GI05MOAS-GL002-00-ENG000000	\N	\N	\N	\N
138	Engineering Data	\N	\N	34	\N	GI05MOAS-GL002-00-ENG000000	\N	\N	\N	\N
142	Engineering Data	\N	\N	27	\N	GP05MOAS-GL001-00-ENG000000	\N	\N	\N	\N
143	Engineering Data	\N	\N	27	\N	GP05MOAS-GL001-00-ENG000000	\N	\N	\N	\N
146	Engineering Data	\N	\N	31	\N	GP05MOAS-GL002-00-ENG000000	\N	\N	\N	\N
147	Engineering Data	\N	\N	31	\N	GP05MOAS-GL002-00-ENG000000	\N	\N	\N	\N
151	Engineering Data	\N	\N	32	\N	GP05MOAS-GL003-00-ENG000000	\N	\N	\N	\N
152	Engineering Data	\N	\N	32	\N	GP05MOAS-GL003-00-ENG000000	\N	\N	\N	\N
1	Velocity Profiler (short range)	\N	\N	14	\N	CP02PMCI-RII01-02-ADCPTG000	\N	\N	\N	\N
3	Engineering Data	\N	\N	13	\N	CP02PMCI-SBS01-00-ENG000000	\N	\N	\N	\N
4	3-Axis Motion Package	\N	\N	13	\N	CP02PMCI-SBS01-01-MOPAK0000	\N	\N	\N	\N
5	Engineering Data	\N	\N	15	\N	CP02PMCI-WFP01-00-ENG000000	\N	\N	\N	\N
149	Dissolved Oxygen Stable Response	\N	\N	31	\N	GP05MOAS-GL002-02-DOSTAM000	\N	\N	\N	\N
154	Dissolved Oxygen Stable Response	\N	\N	32	\N	GP05MOAS-GL003-02-DOSTAM000	\N	\N	\N	\N
133	CTD Profiler	\N	\N	19	\N	CP05MOAS-GL001-03-CTDGV0000	\N	\N	\N	\N
134	CTD Profiler	\N	\N	21	\N	CP05MOAS-GL003-03-CTDGV0000	\N	\N	\N	\N
191	CTD Profiler	\N	\N	35	\N	GI05MOAS-GL003-04-CTDGVM000	\N	\N	\N	\N
192	Engineering Data	\N	\N	13	\N	CP02PMCI-SBS01-00-STCENG000	\N	\N	\N	\N
193	Velocity Profiler (short range)	\N	\N	14	\N	CP02PMCI-RII01-01-ADCPTG000	\N	\N	\N	\N
194	Engineering Data	\N	\N	15	\N	CP02PMCI-WFP01-00-STCENG000	\N	\N	\N	\N
135	CTD Profiler	\N	\N	22	\N	CP05MOAS-GL004-03-CTDGV0000	\N	\N	\N	\N
136	CTD Profiler	\N	\N	23	\N	CP05MOAS-GL005-03-CTDGV0000	\N	\N	\N	\N
139	2-Wavelength Fluorometer	\N	\N	34	\N	GI05MOAS-GL002-01-FLORDM000	\N	\N	\N	\N
148	2-Wavelength Fluorometer	\N	\N	31	\N	GP05MOAS-GL002-01-FLORDM000	\N	\N	\N	\N
153	2-Wavelength Fluorometer	\N	\N	32	\N	GP05MOAS-GL003-01-FLORDM000	\N	\N	\N	\N
141	CTD Profiler	\N	\N	34	\N	GI05MOAS-GL002-04-CTDGVM000	\N	\N	\N	\N
145	CTD Profiler	\N	\N	27	\N	GP05MOAS-GL001-04-CTDGVM000	\N	\N	\N	\N
150	CTD Profiler	\N	\N	31	\N	GP05MOAS-GL002-04-CTDGVM000	\N	\N	\N	\N
155	CTD Profiler	\N	\N	32	\N	GP05MOAS-GL003-04-CTDGVM000	\N	\N	\N	\N
113	Velocity Profiler (short range)	\N	\N	17	\N	CP02PMCO-RII01-01-ADCPTG000	\N	\N	\N	\N
114	Velocity Profiler (short range)	\N	\N	17	\N	CP02PMCO-RII01-01-ADCPTG000	\N	\N	\N	\N
119	Velocity Profiler (short range)	\N	\N	8	\N	CP02PMUI-RII01-01-ADCPTG000	\N	\N	\N	\N
120	Velocity Profiler (short range)	\N	\N	8	\N	CP02PMUI-RII01-01-ADCPTG000	\N	\N	\N	\N
122	Velocity Profiler (short range)	\N	\N	11	\N	CP02PMUO-RII01-01-ADCPSL000	\N	\N	\N	\N
123	Velocity Profiler (short range)	\N	\N	11	\N	CP02PMUO-RII01-01-ADCPSL000	\N	\N	\N	\N
52	CTD Profiler AUV	\N	\N	25	\N	CP05MOAS-AV001-03-CTDAVN000	\N	\N	\N	\N
57	CTD Profiler AUV	\N	\N	26	\N	CP05MOAS-AV002-03-CTDAVN000	\N	\N	\N	\N
6	Photosynthetically Available Radiation	\N	\N	15	\N	CP02PMCI-WFP01-05-PARADK000	\N	\N	\N	\N
7	3-Wavelength Fluorometer	\N	\N	15	\N	CP02PMCI-WFP01-04-FLORTK000	\N	\N	\N	\N
8	CTD Profiler	\N	\N	15	\N	CP02PMCI-WFP01-03-CTDPFK000	\N	\N	\N	\N
9	Dissolved Oxygen Fast Response	\N	\N	15	\N	CP02PMCI-WFP01-02-DOFSTK000	\N	\N	\N	\N
10	3-D Single Point Velocity Meter	\N	\N	15	\N	CP02PMCI-WFP01-01-VEL3DK000	\N	\N	\N	\N
11	Velocity Profiler (short range)	\N	\N	17	\N	CP02PMCO-RII01-02-ADCPTG000	\N	\N	\N	\N
13	Engineering Data	\N	\N	16	\N	CP02PMCO-SBS01-00-ENG000000	\N	\N	\N	\N
14	3-Axis Motion Package	\N	\N	16	\N	CP02PMCO-SBS01-01-MOPAK0000	\N	\N	\N	\N
15	Dissolved Oxygen Fast Response	\N	\N	18	\N	CP02PMCO-WFP01-02-DOFSTK000	\N	\N	\N	\N
16	Engineering Data	\N	\N	18	\N	CP02PMCO-WFP01-00-ENG000000	\N	\N	\N	\N
17	3-D Single Point Velocity Meter	\N	\N	18	\N	CP02PMCO-WFP01-01-VEL3DK000	\N	\N	\N	\N
18	CTD Profiler	\N	\N	18	\N	CP02PMCO-WFP01-03-CTDPFK000	\N	\N	\N	\N
19	3-Wavelength Fluorometer	\N	\N	18	\N	CP02PMCO-WFP01-04-FLORTK000	\N	\N	\N	\N
20	Photosynthetically Available Radiation	\N	\N	18	\N	CP02PMCO-WFP01-05-PARADK000	\N	\N	\N	\N
22	Velocity Profiler (short range)	\N	\N	8	\N	CP02PMUI-RII01-02-ADCPTG000	\N	\N	\N	\N
23	3-Axis Motion Package	\N	\N	7	\N	CP02PMUI-SBS01-01-MOPAK0000	\N	\N	\N	\N
24	Engineering Data	\N	\N	7	\N	CP02PMUI-SBS01-00-ENG000000	\N	\N	\N	\N
25	Dissolved Oxygen Fast Response	\N	\N	9	\N	CP02PMUI-WFP01-02-DOFSTK000	\N	\N	\N	\N
26	Engineering Data	\N	\N	9	\N	CP02PMUI-WFP01-00-ENG000000	\N	\N	\N	\N
27	Photosynthetically Available Radiation	\N	\N	9	\N	CP02PMUI-WFP01-05-PARADK000	\N	\N	\N	\N
28	3-Wavelength Fluorometer	\N	\N	9	\N	CP02PMUI-WFP01-04-FLORTK000	\N	\N	\N	\N
29	CTD Profiler	\N	\N	9	\N	CP02PMUI-WFP01-03-CTDPFK000	\N	\N	\N	\N
30	3-D Single Point Velocity Meter	\N	\N	9	\N	CP02PMUI-WFP01-01-VEL3DK000	\N	\N	\N	\N
31	Velocity Profiler (short range)	\N	\N	11	\N	CP02PMUO-RII01-02-ADCPSL000	\N	\N	\N	\N
33	Engineering Data	\N	\N	10	\N	CP02PMUO-SBS01-00-ENG000000	\N	\N	\N	\N
34	3-Axis Motion Package	\N	\N	10	\N	CP02PMUO-SBS01-01-MOPAK0000	\N	\N	\N	\N
35	CTD Profiler	\N	\N	12	\N	CP02PMUO-WFP01-03-CTDPFK000	\N	\N	\N	\N
172	Temp H2 H2S pH	\N	\N	39	\N	RS01BATH-XX00X-00-THSPHA100	\N	\N	\N	\N
168	Velocity Point	\N	\N	37	\N	RS00ENGC-XX00X-00-VELPTD001	\N	\N	\N	\N
169	Velocity Point	\N	\N	37	\N	RS00ENGC-XX00X-00-VELPTD001	\N	\N	\N	\N
170	Velocity Point	\N	\N	37	\N	RS00ENGC-XX00X-00-VELPTD001	\N	\N	\N	\N
171	Velocity Point	\N	\N	37	\N	RS00ENGC-XX00X-00-VELPTD001	\N	\N	\N	\N
36	Engineering Data	\N	\N	12	\N	CP02PMUO-WFP01-00-ENG000000	\N	\N	\N	\N
37	3-Wavelength Fluorometer	\N	\N	12	\N	CP02PMUO-WFP01-04-FLORTK000	\N	\N	\N	\N
102	Photosynthetically Available Radiation	\N	\N	36	\N	CE05MOAS-GL320-01-PARADM000	\N	\N	\N	\N
109	Photosynthetically Available Radiation	\N	\N	38	\N	CE05MOAS-GL381-01-PARADM000	\N	\N	\N	\N
103	3-Wavelength Fluorometer	\N	\N	36	\N	CE05MOAS-GL320-02-FLORTM000	\N	\N	\N	\N
110	3-Wavelength Fluorometer	\N	\N	38	\N	CE05MOAS-GL381-02-FLORTM000	\N	\N	\N	\N
104	Dissolved Oxygen Stable Response	\N	\N	36	\N	CE05MOAS-GL320-04-DOSTAM000	\N	\N	\N	\N
111	Dissolved Oxygen Stable Response	\N	\N	38	\N	CE05MOAS-GL381-04-DOSTAM000	\N	\N	\N	\N
105	CTD Profiler	\N	\N	36	\N	CE05MOAS-GL320-05-CTDGVM000	\N	\N	\N	\N
112	CTD Profiler	\N	\N	38	\N	CE05MOAS-GL381-05-CTDGVM000	\N	\N	\N	\N
129	3-Axis Motion Package	\N	\N	40	\N	CP04OSPM-SBS01-01-MOPAK0000	\N	\N	\N	\N
59	Velocity Profiler (short range)	\N	\N	26	\N	CP05MOAS-AV002-05-ADCPAN000	\N	\N	\N	\N
60	Photosynthetically Available Radiation	\N	\N	26	\N	CP05MOAS-AV002-06-PARADN000	\N	\N	\N	\N
61	Engineering Data	\N	\N	26	\N	CP05MOAS-AV002-00-ENG000000	\N	\N	\N	\N
62	Dissolved Oxygen Stable Response	\N	\N	26	\N	CP05MOAS-AV002-02-DOSTAN000	\N	\N	\N	\N
63	3-Wavelength Fluorometer	\N	\N	19	\N	CP05MOAS-GL001-02-FLORTM000	\N	\N	\N	\N
64	Engineering Data	\N	\N	19	\N	CP05MOAS-GL001-00-ENG000000	\N	\N	\N	\N
65	Photosynthetically Available Radiation	\N	\N	19	\N	CP05MOAS-GL001-05-PARADM000	\N	\N	\N	\N
38	Photosynthetically Available Radiation	\N	\N	12	\N	CP02PMUO-WFP01-05-PARADK000	\N	\N	\N	\N
39	Dissolved Oxygen Fast Response	\N	\N	12	\N	CP02PMUO-WFP01-02-DOFSTK000	\N	\N	\N	\N
40	3-D Single Point Velocity Meter	\N	\N	12	\N	CP02PMUO-WFP01-01-VEL3DK000	\N	\N	\N	\N
41	Engineering Data	\N	\N	5	\N	CP04OSPM-SBS11-00-ENG000000	\N	\N	\N	\N
42	3-Axis Motion Package	\N	\N	5	\N	CP04OSPM-SBS11-02-MOPAK0000	\N	\N	\N	\N
43	3-D Single Point Velocity Meter	\N	\N	6	\N	CP04OSPM-WFP01-01-VEL3DK000	\N	\N	\N	\N
44	CTD Profiler	\N	\N	6	\N	CP04OSPM-WFP01-03-CTDPFK000	\N	\N	\N	\N
45	Engineering Data	\N	\N	6	\N	CP04OSPM-WFP01-00-ENG000000	\N	\N	\N	\N
46	3-Wavelength Fluorometer	\N	\N	6	\N	CP04OSPM-WFP01-04-FLORTK000	\N	\N	\N	\N
47	Photosynthetically Available Radiation	\N	\N	6	\N	CP04OSPM-WFP01-05-PARADK000	\N	\N	\N	\N
48	Dissolved Oxygen Fast Response	\N	\N	6	\N	CP04OSPM-WFP01-02-DOFSTK000	\N	\N	\N	\N
49	Engineering Data	\N	\N	25	\N	CP05MOAS-AV001-00-ENG000000	\N	\N	\N	\N
50	Photosynthetically Available Radiation	\N	\N	25	\N	CP05MOAS-AV001-06-PARADN000	\N	\N	\N	\N
51	Nitrate	\N	\N	25	\N	CP05MOAS-AV001-04-NUTNRN000	\N	\N	\N	\N
53	3-Wavelength Fluorometer	\N	\N	25	\N	CP05MOAS-AV001-01-FLORTN000	\N	\N	\N	\N
54	Dissolved Oxygen Stable Response	\N	\N	25	\N	CP05MOAS-AV001-02-DOSTAN000	\N	\N	\N	\N
55	Velocity Profiler (short range)	\N	\N	25	\N	CP05MOAS-AV001-05-ADCPAN000	\N	\N	\N	\N
56	3-Wavelength Fluorometer	\N	\N	26	\N	CP05MOAS-AV002-01-FLORTN000	\N	\N	\N	\N
58	Nitrate	\N	\N	26	\N	CP05MOAS-AV002-04-NUTNRN000	\N	\N	\N	\N
66	Dissolved Oxygen Stable Response	\N	\N	19	\N	CP05MOAS-GL001-04-DOSTAM000	\N	\N	\N	\N
67	CTD Profiler	\N	\N	19	\N	CP05MOAS-GL001-03-CTDGVM000	\N	\N	\N	\N
68	Velocity Profiler (short range)	\N	\N	19	\N	CP05MOAS-GL001-01-ADCPAM000	\N	\N	\N	\N
69	Velocity Profiler (short range)	\N	\N	20	\N	CP05MOAS-GL002-01-ADCPAM000	\N	\N	\N	\N
70	Photosynthetically Available Radiation	\N	\N	20	\N	CP05MOAS-GL002-05-PARADM000	\N	\N	\N	\N
71	Dissolved Oxygen Stable Response	\N	\N	20	\N	CP05MOAS-GL002-04-DOSTAM000	\N	\N	\N	\N
72	CTD Profiler	\N	\N	20	\N	CP05MOAS-GL002-03-CTDGVM000	\N	\N	\N	\N
73	3-Wavelength Fluorometer	\N	\N	20	\N	CP05MOAS-GL002-02-FLORTM000	\N	\N	\N	\N
74	Engineering Data	\N	\N	20	\N	CP05MOAS-GL002-00-ENG000000	\N	\N	\N	\N
75	CTD Profiler	\N	\N	21	\N	CP05MOAS-GL003-03-CTDGVM000	\N	\N	\N	\N
76	Dissolved Oxygen Stable Response	\N	\N	21	\N	CP05MOAS-GL003-04-DOSTAM000	\N	\N	\N	\N
77	Velocity Profiler (short range)	\N	\N	21	\N	CP05MOAS-GL003-01-ADCPAM000	\N	\N	\N	\N
78	Engineering Data	\N	\N	21	\N	CP05MOAS-GL003-00-ENG000000	\N	\N	\N	\N
79	Photosynthetically Available Radiation	\N	\N	21	\N	CP05MOAS-GL003-05-PARADM000	\N	\N	\N	\N
80	3-Wavelength Fluorometer	\N	\N	21	\N	CP05MOAS-GL003-02-FLORTM000	\N	\N	\N	\N
81	Photosynthetically Available Radiation	\N	\N	22	\N	CP05MOAS-GL004-05-PARADM000	\N	\N	\N	\N
82	Velocity Profiler (short range)	\N	\N	22	\N	CP05MOAS-GL004-01-ADCPAM000	\N	\N	\N	\N
83	3-Wavelength Fluorometer	\N	\N	22	\N	CP05MOAS-GL004-02-FLORTM000	\N	\N	\N	\N
84	CTD Profiler	\N	\N	22	\N	CP05MOAS-GL004-03-CTDGVM000	\N	\N	\N	\N
85	Dissolved Oxygen Stable Response	\N	\N	22	\N	CP05MOAS-GL004-04-DOSTAM000	\N	\N	\N	\N
86	Engineering Data	\N	\N	22	\N	CP05MOAS-GL004-00-ENG000000	\N	\N	\N	\N
87	Photosynthetically Available Radiation	\N	\N	23	\N	CP05MOAS-GL005-05-PARADM000	\N	\N	\N	\N
156	CTD Bottom Pumped	\N	\N	37	\N	RS00ENGC-XX00X-00-CTDBPN001	\N	\N	\N	\N
157	CTD Bottom Pumped	\N	\N	37	\N	RS00ENGC-XX00X-00-CTDBPN001	\N	\N	\N	\N
158	CTD Bottom Pumped	\N	\N	37	\N	RS00ENGC-XX00X-00-CTDBPN001	\N	\N	\N	\N
159	CTD Bottom Pumped	\N	\N	37	\N	RS00ENGC-XX00X-00-CTDBPN001	\N	\N	\N	\N
160	CTD Bottom Pumped	\N	\N	37	\N	RS00ENGC-XX00X-00-CTDBPN001	\N	\N	\N	\N
161	CTD Bottom Pumped	\N	\N	37	\N	RS00ENGC-XX00X-00-CTDBPN001	\N	\N	\N	\N
165	Photosynthetically Available Radiation	\N	\N	37	\N	RS00ENGC-XX00X-00-PARADA001	\N	\N	\N	\N
166	Photosynthetically Available Radiation	\N	\N	37	\N	RS00ENGC-XX00X-00-PARADA001	\N	\N	\N	\N
162	3-Wavelength Fluorometer	\N	\N	37	\N	RS00ENGC-XX00X-00-FLORDD001	\N	\N	\N	\N
163	3-Wavelength Fluorometer	\N	\N	37	\N	RS00ENGC-XX00X-00-FLORDD001	\N	\N	\N	\N
164	3-Wavelength Fluorometer	\N	\N	37	\N	RS00ENGC-XX00X-00-FLORDD001	\N	\N	\N	\N
167	Temp H2 H2S pH	\N	\N	37	\N	RS00ENGC-XX00X-00-THSPHA001	\N	\N	\N	\N
88	Dissolved Oxygen Stable Response	\N	\N	23	\N	CP05MOAS-GL005-04-DOSTAM000	\N	\N	\N	\N
89	Engineering Data	\N	\N	23	\N	CP05MOAS-GL005-00-ENG000000	\N	\N	\N	\N
90	CTD Profiler	\N	\N	23	\N	CP05MOAS-GL005-03-CTDGVM000	\N	\N	\N	\N
91	3-Wavelength Fluorometer	\N	\N	23	\N	CP05MOAS-GL005-02-FLORTM000	\N	\N	\N	\N
92	Velocity Profiler (short range)	\N	\N	23	\N	CP05MOAS-GL005-01-ADCPAM000	\N	\N	\N	\N
93	3-Wavelength Fluorometer	\N	\N	24	\N	CP05MOAS-GL006-02-FLORTM000	\N	\N	\N	\N
94	Dissolved Oxygen Stable Response	\N	\N	24	\N	CP05MOAS-GL006-04-DOSTAM000	\N	\N	\N	\N
95	Photosynthetically Available Radiation	\N	\N	24	\N	CP05MOAS-GL006-05-PARADM000	\N	\N	\N	\N
96	Engineering Data	\N	\N	24	\N	CP05MOAS-GL006-00-ENG000000	\N	\N	\N	\N
97	CTD Profiler	\N	\N	24	\N	CP05MOAS-GL006-03-CTDGVM000	\N	\N	\N	\N
98	Velocity Profiler (short range)	\N	\N	24	\N	CP05MOAS-GL006-01-ADCPAM000	\N	\N	\N	\N
140	Dissolved Oxygen Stable Response	\N	\N	34	\N	GI05MOAS-GL002-02-DOSTAM000	\N	\N	\N	\N
144	Dissolved Oxygen Stable Response	\N	\N	27	\N	GP05MOAS-GL001-02-DOSTAM000	\N	\N	\N	\N
\.


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_deployments_id_seq', 194, true);


--
-- Data for Name: instrumentnames; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY instrumentnames (id, instrument_class, display_name) FROM stdin;
1	ADCPA	Velocity Profiler (short range) for mobile assets
2	ADCPS	Velocity Profiler (long range)
3	ADCPT	Velocity Profiler (short range)
4	BOTPT	Bottom Pressure and Tilt
5	CAMDS	Digital Still Camera with Strobes
6	CAMHD	HD Digital Video Camera with Strobes
7	CTDAV	CTD AUV
8	CTDBP	CTD Pumped
9	CTDGV	CTD Glider
10	CTDMO	CTD Mooring (Inductive)
11	CTDPF	CTD Profiler
12	DOFST	Dissolved Oxygen Fast Response
13	DOSTA	Dissolved Oxygen Stable Response
14	FDCHP	Direct Covariance Flux
15	FLOBN	Benthic Fluid Flow
16	FLORD	2-Wavelength Fluorometer
17	FLORT	3-Wavelength Fluorometer
18	HPIES	Horizontal Electric Field, Pressure and Inverted Echo Sounder
19	HYDBB	Broadband Acoustic Receiver (Hydrophone)
20	HYDLF	Low Frequency Broadband Acoustic Receiver (Hydrophone) on Seafloor
21	MASSP	Mass Spectrometer
22	METBK	Bulk Meteorology Instrument Package
23	NUTNR	Nitrate
24	OBSBB	Broadband Ocean Bottom Seismometer
25	OBSBK	Broadband Ocean Bottom Seismometer
26	OBSSP	Short-Period Ocean Bottom Seismometer
27	OPTAA	Absorption Spectrophotometer
28	OSMOI	Osmosis-Based Water Sampler
29	PARAD	Photosynthetically Available Radiation
30	PCO2A	pCO2 Air-Sea
31	PCO2W	pCO2 Water
32	PHSEN	Seawater pH
33	PPSDN	Particulate DNA Sampler
34	PRESF	Seafloor Pressure
35	PREST	Tidal Seafloor Pressure
36	RASFL	Hydrothermal Vent Fluid Interactive Sampler
37	SPKIR	Spectral Irradiance
38	THSPH	Hydrothermal Vent Fluid In-situ Chemistry
39	TMPSF	Diffuse Vent Fluid 3-D Temperature Array
40	TRHPH	Hydrothermal Vent Fluid Temperature and Resistivity
41	VADCP	5-Beam, 600 kHz Acoustic Doppler Current Profiler (= 50 m range)
42	VEL3D	3-D Single Point Velocity Meter
43	VELPT	Single Point Velocity Meter
44	WAVSS	Surface Wave Spectra
45	ZPLSC	Bio-acoustic Sonar (Coastal)
46	ZPLSG	Bio-acoustic Sonar (Global)
47	ENG00	Engineering Data
48	STCEN	Engineering Data
49	MOPAK	3-Axis Motion Pack
\.


--
-- Name: instrumentnames_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('instrumentnames_id_seq', 49, true);


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('instruments_id_seq', 1, false);


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('platform_deployments_id_seq', 40, true);


--
-- Data for Name: platformnames; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY platformnames (id, reference_designator, array_type, array_name, site, platform, assembly) FROM stdin;
108	CE01ISSM	Coastal	Endurance	OR Inshore	Surface Mooring	\N
109	CE01ISSM-SBD17	Coastal	Endurance	OR Inshore	Surface Mooring	Surface Buoy
110	CE01ISSM-RID16	Coastal	Endurance	OR Inshore	Surface Mooring	Mooring Riser
111	CE01ISSM-MFD35	Coastal	Endurance	OR Inshore	Surface Mooring	MFN Base/Anchor
112	CE01ISSM-MFD37	Coastal	Endurance	OR Inshore	Surface Mooring	MFN Base/Anchor
113	CE01ISSM-MFD00	Coastal	Endurance	OR Inshore	Surface Mooring	MFN Base/Anchor
114	CE01ISSP	Coastal	Endurance	OR Inshore	Surface-Piercing Profiler Mooring	\N
115	CE01ISSP-SP001	Coastal	Endurance	OR Inshore	Surface-Piercing Profiler Mooring	Surface-Piercing Profiler
116	CE02SHBP	Coastal	Endurance	OR Shelf	Benthic Experiment Package	\N
117	CE02SHBP-MJ01C	Coastal	Endurance	OR Shelf	Benthic Experiment Package	Junction Box
118	CE02SHBP-LJ01D	Coastal	Endurance	OR Shelf	Benthic Experiment Package	Junction Box
119	CE02SHSM	Coastal	Endurance	OR Shelf	Surface Mooring	\N
120	CE02SHSM-SBD11	Coastal	Endurance	OR Shelf	Surface Mooring	Surface Buoy
121	CE02SHSM-SBD12	Coastal	Endurance	OR Shelf	Surface Mooring	Surface Buoy
122	CE02SHSM-RID26	Coastal	Endurance	OR Shelf	Surface Mooring	Mooring Riser
123	CE02SHSM-RID27	Coastal	Endurance	OR Shelf	Surface Mooring	Mooring Riser
124	CE02SHSP	Coastal	Endurance	OR Shelf	Surface-Piercing Profiler Mooring	\N
125	CE02SHSP-SP001	Coastal	Endurance	OR Shelf	Surface-Piercing Profiler Mooring	Surface-Piercing Profiler
126	CE04OOPI	Coastal	Endurance	OR Offshore	Primary Node	\N
127	CE04OOPI-PN01C	Coastal	Endurance	OR Offshore	Primary Node	Primary Node
128	CE04OSBP	Coastal	Endurance	OR Offshore	Benthic Experiment Package	\N
129	CE04OSBP-LV01C	Coastal	Endurance	OR Offshore	Benthic Experiment Package	Junction Box
130	CE04OSBP-LJ01C	Coastal	Endurance	OR Offshore	Benthic Experiment Package	Junction Box
131	CE04OPS	Coastal	Endurance	OR Offshore	Profiler Mooring	\N
132	CE04OSPS-PC01B	Coastal	Endurance	OR Offshore	Profiler Mooring	Interface Controller
133	CE04OSPS-SC03A	Coastal	Endurance	OR Offshore	Profiler Mooring	Profiler Controller
134	CE04OSPS-SF01B	Coastal	Endurance	OR Offshore	Profiler Mooring	Profiler
135	CE04OSPD	Coastal	Endurance	OR Offshore	Profiler Mooring	\N
136	CE04OSPD-PD01B	Coastal	Endurance	OR Offshore	Profiler Mooring	Profiler Dock
137	CE04OSPD-DP01B	Coastal	Endurance	OR Offshore	Profiler Mooring	Profiler
138	CE04OSPI	Cabled	Endurance	OR Shelf	Primary Node	\N
139	CE04OSPI-PN01D	Cabled	Endurance	OR Shelf	Primary Node	Primary Node
140	CE04OSSM	Coastal	Endurance	OR Offshore	Surface Mooring	\N
141	CE04OSSM-SBD11	Coastal	Endurance	OR Offshore	Surface Mooring	Surface Buoy
142	CE04OSSM-SBD12	Coastal	Endurance	OR Offshore	Surface Mooring	Surface Buoy
143	CE04OSSM-RID26	Coastal	Endurance	OR Offshore	Surface Mooring	Mooring Riser
144	CE04OSSM-RID27	Coastal	Endurance	OR Offshore	Surface Mooring	Mooring Riser
146	CE06ISSM	Coastal	Endurance	WA Inshore	Surface Mooring	\N
147	CE06ISSM-SBD17	Coastal	Endurance	WA Inshore	Surface Mooring	Surface Buoy
148	CE06ISSM-RID16	Coastal	Endurance	WA Inshore	Surface Mooring	Mooring Riser
149	CE06ISSM-MFD35	Coastal	Endurance	WA Inshore	Surface Mooring	MFN Base/Anchor
150	CE06ISSM-MFD37	Coastal	Endurance	WA Inshore	Surface Mooring	MFN Base/Anchor
151	CE06ISSM-MFD00	Coastal	Endurance	WA Inshore	Surface Mooring	MFN Base/Anchor
152	CE06ISSP	Coastal	Endurance	WA Inshore	Surface-Piercing Profiler Mooring	\N
153	CE06ISSP-SP001	Coastal	Endurance	WA Inshore	Surface-Piercing Profiler Mooring	Surface-Piercing Profiler
154	CE07SHSM	Coastal	Endurance	WA Shelf	Surface Mooring	\N
155	CE07SHSM-SBD11	Coastal	Endurance	WA Shelf	Surface Mooring	Surface Buoy
156	CE07SHSM-SBD12	Coastal	Endurance	WA Shelf	Surface Mooring	Surface Buoy
157	CE07SHSM-RID26	Coastal	Endurance	WA Shelf	Surface Mooring	Mooring Riser
158	CE07SHSM-RID27	Coastal	Endurance	WA Shelf	Surface Mooring	Mooring Riser
159	CE07SHSP	Coastal	Endurance	WA Shelf	Surface-Piercing Profiler Mooring	\N
160	CE07SHSP-SP001	Coastal	Endurance	WA Shelf	Surface-Piercing Profiler Mooring	Surface-Piercing Profiler
161	CE09OSPM	Coastal	Endurance	WA Offshore	Profiler Mooring	\N
162	CE09OSPM-WF001	Coastal	Endurance	WA Offshore	Profiler Mooring	Wire-Following Profiler
163	CE09OSSM	Coastal	Endurance	WA Offshore	Surface Mooring	\N
164	CE09OSSM-SBD11	Coastal	Endurance	WA Offshore	Surface Mooring	Surface Buoy
165	CE09OSSM-SBD12	Coastal	Endurance	WA Offshore	Surface Mooring	Surface Buoy
166	CE09OSSM-RID26	Coastal	Endurance	WA Offshore	Surface Mooring	Mooring Riser
167	CE09OSSM-RID27	Coastal	Endurance	WA Offshore	Surface Mooring	Mooring Riser
168	CP01CNSM	Coastal	Pioneer	Central	Surface Mooring	\N
169	CP01CNSM-SBD11	Coastal	Pioneer	Central	Surface Mooring	Surface Buoy
170	CP01CNSM-SBD12	Coastal	Pioneer	Central	Surface Mooring	Surface Buoy
171	CP01CNSM-RID26	Coastal	Pioneer	Central	Surface Mooring	Mooring Riser
172	CP01CNSM-RID27	Coastal	Pioneer	Central	Surface Mooring	Mooring Riser
173	CP01CNSM-MFD35	Coastal	Pioneer	Central	Surface Mooring	Multi-Function Node
174	CP01CNSM-MFD37	Coastal	Pioneer	Central	Surface Mooring	Multi-Function Node
175	CP01CNSM-MFD00	Coastal	Pioneer	Central	Surface Mooring	Multi-Function Node
176	CP01CNSP	Coastal	Pioneer	Central	Surface-Piercing Profiler Mooring	\N
177	CP01CNSP-SP001	Coastal	Pioneer	Central	Surface-Piercing Profiler Mooring	Surface-Piercing Profiler
178	CP02PMCI	Coastal	Pioneer	Central Inshore	Profiler Mooring	\N
179	CP02PMCI-SBS01	Coastal	Pioneer	Central Inshore	Profiler Mooring	Surface Buoy
180	CP02PMCI-RII01	Coastal	Pioneer	Central Inshore	Profiler Mooring	Mooring Riser
181	CP02PMCI-WFP01	Coastal	Pioneer	Central Inshore	Profiler Mooring	Wire-Following Profiler
182	CP02PMCO	Coastal	Pioneer	Central Offshore	Profiler Mooring	\N
183	CP02PMCO-SBS01	Coastal	Pioneer	Central Offshore	Profiler Mooring	Surface Buoy
321	CE05MOAS	Coastal	Pioneer	Mobile	(Coastal)	Glider
184	CP02PMCO-RII01	Coastal	Pioneer	Central Offshore	Profiler Mooring	Mooring Riser
185	CP02PMCO-WFP01	Coastal	Pioneer	Central Offshore	Profiler Mooring	Wire-Following Profiler
186	CP02PMUI	Coastal	Pioneer	Upstream Inshore	Profiler Mooring	\N
187	CP02PMUI-SBS01	Coastal	Pioneer	Upstream Inshore	Profiler Mooring	Surface Buoy
188	CP02PMUI-RII01	Coastal	Pioneer	Upstream Inshore	Profiler Mooring	Mooring Riser
189	CP02PMUI-WFP01	Coastal	Pioneer	Upstream Inshore	Profiler Mooring	Wire-Following Profiler
190	CP02PMUO	Coastal	Pioneer	Upstream Offshore	Profiler Mooring	\N
191	CP02PMUO-SBS01	Coastal	Pioneer	Upstream Offshore	Profiler Mooring	Surface Buoy
192	CP02PMUO-RII01	Coastal	Pioneer	Upstream Offshore	Profiler Mooring	Mooring Riser
193	CP02PMUO-WFP01	Coastal	Pioneer	Upstream Offshore	Profiler Mooring	Wire-Following Profiler
194	CP03ISSM	Coastal	Pioneer	Inshore	Surface Mooring	\N
195	CP03ISSM-SBD11	Coastal	Pioneer	Inshore	Surface Mooring	Surface Buoy
196	CP03ISSM-SBD12	Coastal	Pioneer	Inshore	Surface Mooring	Surface Buoy
197	CP03ISSM-RID26	Coastal	Pioneer	Inshore	Surface Mooring	Mooring Riser
198	CP03ISSM-RID27	Coastal	Pioneer	Inshore	Surface Mooring	Mooring Riser
199	CP03ISSM-MFD35	Coastal	Pioneer	Inshore	Surface Mooring	Multi-Function Node
200	CP03ISSM-MFD37	Coastal	Pioneer	Inshore	Surface Mooring	Multi-Function Node
201	CP03ISSM-MFD00	Coastal	Pioneer	Inshore	Surface Mooring	Multi-Function Node
202	CP03ISSP	Coastal	Pioneer	Inshore	Surface-Piercing Profiler Mooring	\N
203	CP03ISSP-SP001	Coastal	Pioneer	Inshore	Surface-Piercing Profiler Mooring	Surface-Piercing Profiler
204	CP04OSPM	Coastal	Pioneer	Offshore	Profiler Mooring	\N
205	CP04OSPM-SBS11	Coastal	Pioneer	Offshore	Profiler Mooring	Surface Buoy
206	CP04OSPM-WFP01	Coastal	Pioneer	Offshore	Profiler Mooring	Wire-Following Profiler
207	CP04OSSM	Coastal	Pioneer	Offshore	Surface Mooring	\N
208	CP04OSSM-SBD11	Coastal	Pioneer	Offshore	Surface Mooring	Surface Buoy
209	CP04OSSM-SBD12	Coastal	Pioneer	Offshore	Surface Mooring	Surface Buoy
210	CP04OSSM-RID26	Coastal	Pioneer	Offshore	Surface Mooring	Mooring Riser
211	CP04OSSM-RID27	Coastal	Pioneer	Offshore	Surface Mooring	Mooring Riser
212	CP04OSSM-MFD35	Coastal	Pioneer	Offshore	Surface Mooring	Multi-Function Node
213	CP04OSSM-MFD37	Coastal	Pioneer	Offshore	Surface Mooring	Multi-Function Node
322	CP05MOAS	Coastal	Pioneer	Mobile	(Coastal)	Glider/AUV
323	GA05MOAS	Global	Argentine Basin	Mobile	(Open Ocean)	Glider
324	GI05MOAS	Global	Irminger Sea	Mobile	(Open Ocean)	Glider
325	GP05MOAS	Global	Station Papa	Mobile	(Open Ocean)	Glider
326	GS05MOAS	Global	Southern Ocean	Mobile	(Open Ocean)	Glider
327	RS00ENGC-XX00X	Cabled	or	Testing	Platform	\N
328	RS01BATH-XX00X	Cabled	Bathtub	Testing	Platform	\N
214	CP04OSSM-MFD00	Coastal	Pioneer	Offshore	Surface Mooring	Multi-Function Node
215	RS01HSPI	Cabled	Continental Margin	Slope Base	Primary Node	\N
216	RS01HSPI-PN01A	Cabled	Continental Margin	Slope Base	Primary Node	Primary Node
217	RS01SBPS	Cabled	Continental Margin	Slope Base	Profiler Mooring	\N
218	RS01SBPS-LV01A	Cabled	Continental Margin	Slope Base	Profiler Mooring	Junction Box
219	RS01SBPS-PC01A	Cabled	Continental Margin	Slope Base	Profiler Mooring	Interface Controller
220	RS01SBPS-SC01A	Cabled	Continental Margin	Slope Base	Profiler Mooring	Profiler Controller
221	RS01SBPS-SF01A	Cabled	Continental Margin	Slope Base	Profiler Mooring	Profiler
222	RS01SBPS-LJ01A	Cabled	Continental Margin	Slope Base	Profiler Mooring	Junction Box
223	RS01SBPD	Cabled	Continental Margin	Slope Base	Profiler Mooring	\N
224	RS01SBPD-PD01A	Cabled	Continental Margin	Slope Base	Profiler Mooring	Profiler Dock
225	RS01SBPD-DP01A	Cabled	Continental Margin	Slope Base	Profiler Mooring	Profiler
226	RS01SLBS	Cabled	Continental Margin	Slope Base	Junction Box	\N
227	RS01SLBS-MJ01A	Cabled	Continental Margin	Slope Base	Junction Box	Junction Box
228	RS01SUM1	Cabled	Continental Margin	Southern Hydrate Ridge Summit	Junction Box	\N
229	RS01SUM1-LV01B	Cabled	Continental Margin	Southern Hydrate Ridge Summit	Junction Box	Junction Box
230	RS01SUM1-LJ01B	Cabled	Continental Margin	Southern Hydrate Ridge Summit	Junction Box	Junction Box
231	RS01SUM2	Cabled	Continental Margin	Southern Hydrate Ridge Summit	Junction Box	\N
232	RS01SUM2-MJ01B	Cabled	Continental Margin	Southern Hydrate Ridge Summit	Junction Box	Junction Box
233	RS02HRPI	Cabled	Continental Margin	Hydrate Ridge	Primary Node	\N
234	RS02HRPI-PN01B	Cabled	Continental Margin	Hydrate Ridge	Primary Node	Primary Node
235	RS03ABPI	Cabled	Axial Seamount	Axial Base	Primary Node	\N
236	RS03ABPI-PN03A	Cabled	Axial Seamount	Axial Base	Primary Node	Primary Node
237	RS03ASHS	Cabled	Axial Seamount	ASHES	Junction Box	\N
238	RS03ASHS-MJ03B	Cabled	Axial Seamount	ASHES	Junction Box	Junction Box
239	RS03ASHS-ID03A	Cabled	Axial Seamount	ASHES	Junction Box	Junction Box
240	RS03AXBS	Cabled	Axial Seamount	Axial Base	Junction Box	\N
241	RS03AXBS-MJ03A	Cabled	Axial Seamount	Axial Base	Junction Box	Junction Box
242	RS03AXPS	Cabled	Axial Seamount	Axial Base	Profiler Mooring	\N
243	RS03AXPS-LV03A	Cabled	Axial Seamount	Axial Base	Profiler Mooring	Junction Box
244	RS03AXPS-PC03A	Cabled	Axial Seamount	Axial Base	Profiler Mooring	Interface Controller
245	RS03AXPS-SC03A	Cabled	Axial Seamount	Axial Base	Profiler Mooring	Profiler Controller
246	RS03AXPS-SF03A	Cabled	Axial Seamount	Axial Base	Profiler Mooring	Profiler
247	RS03AXPS-LJ03A	Cabled	Axial Seamount	Axial Base	Profiler Mooring	Junction Box
248	RS03AXPD	Cabled	Axial Seamount	Axial Base	Profiler Mooring	\N
249	RS03AXPD-PD03A	Cabled	Axial Seamount	Axial Base	Profiler Mooring	Profiler Dock
250	RS03AXPD-DP03A	Cabled	Axial Seamount	Axial Base	Profiler Mooring	Profiler
251	RS03CCAL	Cabled	Axial Seamount	Central Caldera	Junction Box	\N
252	RS03CCAL-MJ03F	Cabled	Axial Seamount	Central Caldera	Junction Box	Junction Box
253	RS03ECAL	Cabled	Axial Seamount	Eastern Caldera	Junction Box	\N
254	RS03ECAL-MJ03E	Cabled	Axial Seamount	Eastern Caldera	Junction Box	Junction Box
255	RS03INT1	Cabled	Axial Seamount	International District	Junction Box	\N
256	RS03INT1-MJ03C	Cabled	Axial Seamount	International District	Junction Box	Junction Box
257	RS03INT2	Cabled	Axial Seamount	International District	Junction Box	\N
258	RS03INT2-MJ03D	Cabled	Axial Seamount	International District	Junction Box	Junction Box
259	RS04ASPI	Cabled	Axial Seamount	Axial Summit	Primary Node	\N
260	RS04ASPI-PN03B	Cabled	Axial Seamount	Axial Summit	Primary Node	Primary Node
261	RS05MPPI	Cabled	Mid Plate	Primary Infrastructure	Primary Node	\N
262	RS05MPPI-PN05A	Cabled	Mid Plate	Primary Infrastructure	Primary Node	Primary Node
263	GA01SUMO	Global	Argentine Basin	Apex	Surface Mooring	\N
264	GA01SUMO-SBD11	Global	Argentine Basin	Apex	Surface Mooring	Surface Buoy
265	GA01SUMO-SBD12	Global	Argentine Basin	Apex	Surface Mooring	Surface Buoy
266	GA01SUMO-RID16	Global	Argentine Basin	Apex	Surface Mooring	Mooring Riser
267	GA01SUMO-RII11	Global	Argentine Basin	Apex	Surface Mooring	Mooring Riser
268	GA02HYPM	Global	Argentine Basin	Apex	Profiler Mooring	\N
269	GA02HYPM-MPC04	Global	Argentine Basin	Apex	Profiler Mooring	Submerged Buoy
270	GA02HYPM-RIS01	Global	Argentine Basin	Apex	Profiler Mooring	Mooring Riser
271	GA02HYPM-WFP02	Global	Argentine Basin	Apex	Profiler Mooring	Wire-Following Profiler
272	GA02HYPM-WFP03	Global	Argentine Basin	Apex	Profiler Mooring	Wire-Following Profiler
273	GA03FLMA	Global	Argentine Basin	Flanking	Subsurface Mooring	\N
274	GA03FLMA-RIS01	Global	Argentine Basin	Flanking	Subsurface Mooring	Mooring Riser
275	GA03FLMA-RIS02	Global	Argentine Basin	Flanking	Subsurface Mooring	Mooring Riser
276	GA03FLMB	Global	Argentine Basin	Flanking	Subsurface Mooring	\N
277	GA03FLMB-RIS01	Global	Argentine Basin	Flanking	Subsurface Mooring	Mooring Riser
278	GA03FLMB-RIS02	Global	Argentine Basin	Flanking	Subsurface Mooring	Mooring Riser
279	GI01SUMO	Global	Irminger Sea	Apex	Surface Mooring	\N
280	GI01SUMO-SBD11	Global	Irminger Sea	Apex	Surface Mooring	Surface Buoy
281	GI01SUMO-SBD12	Global	Irminger Sea	Apex	Surface Mooring	Surface Buoy
282	GI01SUMO-RID16	Global	Irminger Sea	Apex	Surface Mooring	Mooring Riser
283	GI01SUMO-RII11	Global	Irminger Sea	Apex	Surface Mooring	Mooring Riser
284	GI02HYPM	Global	Irminger Sea	Apex	Profiler Mooring	\N
285	GI02HYPM-MPC04	Global	Irminger Sea	Apex	Profiler Mooring	Submerged Buoy
286	GI02HYPM-RIS01	Global	Irminger Sea	Apex	Profiler Mooring	Mooring Riser
287	GI02HYPM-WFP02	Global	Irminger Sea	Apex	Profiler Mooring	Wire-Following Profiler
288	GI03FLMA	Global	Irminger Sea	Flanking	Subsurface Mooring	\N
289	GI03FLMA-RIS01	Global	Irminger Sea	Flanking	Subsurface Mooring	Mooring Riser
290	GI03FLMA-RIS02	Global	Irminger Sea	Flanking	Subsurface Mooring	Mooring Riser
291	GI03FLMB	Global	Irminger Sea	Flanking	Subsurface Mooring	\N
292	GI03FLMB-RIS01	Global	Irminger Sea	Flanking	Subsurface Mooring	Mooring Riser
293	GI03FLMB-RIS02	Global	Irminger Sea	Flanking	Subsurface Mooring	Mooring Riser
294	GP02HYPM	Global	Station Papa	Apex	Profiler Mooring	\N
295	GP02HYPM-MPC04	Global	Station Papa	Apex	Profiler Mooring	Submerged Buoy
296	GP02HYPM-RIS01	Global	Station Papa	Apex	Profiler Mooring	Mooring Riser
297	GP02HYPM-WFP02	Global	Station Papa	Apex	Profiler Mooring	Wire-Following Profiler
298	GP02HYPM-WFP03	Global	Station Papa	Apex	Profiler Mooring	Wire-Following Profiler
299	GP03FLMA	Global	Station Papa	Flanking	Subsurface Mooring	\N
300	GP03FLMA-RIS01	Global	Station Papa	Flanking	Subsurface Mooring	Mooring Riser
301	GP03FLMA-RIS02	Global	Station Papa	Flanking	Subsurface Mooring	Mooring Riser
302	GP03FLMB	Global	Station Papa	Flanking	Subsurface Mooring	\N
303	GP03FLMB-RIS01	Global	Station Papa	Flanking	Subsurface Mooring	Mooring Riser
304	GP03FLMB-RIS02	Global	Station Papa	Flanking	Subsurface Mooring	Mooring Riser
305	GS01SUMO	Global	Southern Ocean	Apex	Surface Mooring	\N
306	GS01SUMO-SBD11	Global	Southern Ocean	Apex	Surface Mooring	Surface Buoy
307	GS01SUMO-SBD12	Global	Southern Ocean	Apex	Surface Mooring	Surface Buoy
308	GS01SUMO-RID16	Global	Southern Ocean	Apex	Surface Mooring	Mooring Riser
309	GS01SUMO-RII11	Global	Southern Ocean	Apex	Surface Mooring	Mooring Riser
310	GS02HYPM	Global	Southern Ocean	Apex	Profiler Mooring	\N
311	GS02HYPM-MPC04	Global	Southern Ocean	Apex	Profiler Mooring	Submerged Buoy
312	GS02HYPM-RIS01	Global	Southern Ocean	Apex	Profiler Mooring	Mooring Riser
313	GS02HYPM-WFP02	Global	Southern Ocean	Apex	Profiler Mooring	Wire-Following Profiler
314	GS02HYPM-WFP03	Global	Southern Ocean	Apex	Profiler Mooring	Wire-Following Profiler
315	GS03FLMA	Global	Southern Ocean	Flanking	Subsurface Mooring	\N
316	GS03FLMA-RIS01	Global	Southern Ocean	Flanking	Subsurface Mooring	Mooring Riser
317	GS03FLMA-RIS02	Global	Southern Ocean	Flanking	Subsurface Mooring	Mooring Riser
318	GS03FLMB	Global	Southern Ocean	Flanking	Subsurface Mooring	\N
319	GS03FLMB-RIS01	Global	Southern Ocean	Flanking	Subsurface Mooring	Mooring Riser
320	GS03FLMB-RIS02	Global	Southern Ocean	Flanking	Subsurface Mooring	Mooring Riser
\.


--
-- Name: platformnames_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('platformnames_id_seq', 328, true);


--
-- Name: platforms_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('platforms_id_seq', 1, false);


--
-- Data for Name: streams; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY streams (id, name, instrument_id, description) FROM stdin;
\.


--
-- Data for Name: stream_parameters; Type: TABLE DATA; Schema: luke_dev; Owner: oceanzus
--

COPY stream_parameters (id, stream_id, name, short_name, long_name, standard_name, units, data_type) FROM stdin;
\.


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameters_id_seq', 1, false);


--
-- Name: streams_id_seq; Type: SEQUENCE SET; Schema: luke_dev; Owner: oceanzus
--

SELECT pg_catalog.setval('streams_id_seq', 1, false);


SET search_path = ooiui_dataload_testing, pg_catalog;

--
-- Data for Name: organizations; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY organizations (id, organization_name) FROM stdin;
1	ASA
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY users (id, user_id, pass_hash, email, user_name, active, confirmed_at, first_name, last_name, phone_primary, phone_alternate, organization_id) FROM stdin;
\.


--
-- Data for Name: annotations; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY annotations (id, user_id, created_time, modified_time, reference_name, reference_type, reference_pk_id, title, comment) FROM stdin;
\.


--
-- Name: annotations_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('annotations_id_seq', 1, false);


--
-- Data for Name: arrays; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY arrays (id, array_code, description, geo_location, array_name, display_name) FROM stdin;
1	CE		0103000020E610000001000000050000008FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC0	Endurance (CE)	Coastal Endurance
2	GP		0103000020E610000001000000050000004C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C0	PAPA (GP)	Global Station Papa
3	CP		0103000020E61000000100000005000000CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0	Pioneer (CP)	Coastal Pioneer
4	GA		0103000020E6100000010000000500000062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C0	Argentine (GA)	Argentine Basin
5	GI		0103000020E610000001000000050000007B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C0	Irminger (GI)	Irminger Sea
6	GS		0103000020E610000001000000050000007CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C0	55 S (GS)	Southern Ocean
\.


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('arrays_id_seq', 6, true);


--
-- Data for Name: assemblies; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY assemblies (id, assembly_name, description) FROM stdin;
1	Default Assembly	\N
\.


--
-- Data for Name: asset_types; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY asset_types (id, asset_type_name) FROM stdin;
1	Glider
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY assets (id, asset_type_id, organization_id, supplier_id, deployment_id, asset_name, model, current_lifecycle_state, part_number, firmware_version, geo_location) FROM stdin;
1	1	1	1	1	some glider	some model	DEPLOYED	pn-1	fw1.0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY files (id, user_id, file_name, file_system_path, file_size, file_permissions, file_type) FROM stdin;
\.


--
-- Data for Name: asset_file_link; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY asset_file_link (id, asset_id, file_id) FROM stdin;
\.


--
-- Name: asset_file_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_file_link_id_seq', 1, false);


--
-- Name: asset_types_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_types_id_seq', 1, true);


--
-- Name: assets_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('assets_id_seq', 1, true);


--
-- Name: asssemblies_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('asssemblies_id_seq', 1, true);


--
-- Data for Name: deployments; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY deployments (id, start_date, end_date, cruise_id) FROM stdin;
1	\N	\N	\N
\.


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY manufacturers (id, manufacturer_name, phone_number, contact_name, web_address) FROM stdin;
1	Aanderaa	937-767-7241		http://www.aanderaa.com
2	Axys Technologies	250-655-5850		http://axystechnologies.com/
3	Biospherical Instruments	619-686-1888		http://www.biospherical.com/
4	Falmouth Scientific	508-564-7640		http://www.falmouth.com
5	Guralp	44-118-981-9056		http://www.guralp.com/
6	HTI	541-917-3335		http://www.htiwater.com
7	Kongsberg	44-1224-226500		http://www.kongsberg.com/
8	Marv Lilley lab	206-543-0859	Marv Lilley	http://www.ocean.washington.edu/home/Marvin+Lilley
9	Nobska	508-289-2725		http://www.nobska.net/
10	Nortek	47-6717-4500		http://www.nortek-as.com/
11	Ocean Sonics	855-360-3003		http://oceansonics.com/
12	Pro-Oceanus	855-530-3550		http://www.pro-oceanus.com
13	RBR Global	613-599-8900		www.rbr-global.com/
14	Satlantic	902-492-4780		http://www.salantic.com
15	Sea-Bird	425-643-9866		www.seabird.com/
16	Star Engineering	508-316-1492		http://starengineeringinc.com/markets/marine-navigation/
17	SubC	709-702-0395		http://subcimaging.com
18	Sunburst Sensors	406-532-3246		www.sunburstsensors.com/
19	TLR, Inc.	831-236-7121		http://www.tlrinc.biz/index.html
20	Teledyne RDI	858-842-2600		www.rdinstruments.com/
21	WET Labs	401-783-1787		www.wetlabs.com/
22	WHOI	508-289-2508	Robert A. Weller	http://www.whoi.edu/hpb/viewPage.do?id=8176
23	non-commercial			
24	unknown			
\.


--
-- Data for Name: instrument_models; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY instrument_models (id, instrument_model_name, series_name, class_name, manufacturer_id) FROM stdin;
1	Optode 4831	D	DOSTA	1
2	Optode 4831	M	DOSTA	1
3	Optode 4330	N	DOSTA	1
4	Optode 4330	L	DOSTA	1
5	TRIAXYS	A	WAVSS	2
6	QSP-2150	N	PARAD	3
7	QSP-2155	M	PARAD	3
8	QSP-2200	K	PARAD	3
9	ACM-3D-MP	A	VEL3D	4
10	ACM-Plus	L	VEL3D	4
11	Guralp (CMG-1 sec)	A	OBSSP	5
12	CMG-1T/5T	A	OBSBK	5
13	CMG-1T/5T	A	OBSBB	5
14	90-U	A	HYDLF	6
15	Modified EK-60	B	ZPLSC	7
16	Modified OE14-408	C	CAMDS	7
17	Modified OE14-408	B	CAMDS	7
18	Modified OE14-408	A	CAMDS	7
19	MAVS-4	B	VEL3D	9
20	Aquadopp II	K	VEL3D	10
21	Aquadopp 3000m	B	VELPT	10
22	VECTOR	D	VEL3D	10
23	VECTOR	C	VEL3D	10
24	Aquadopp	J	VEL3D	10
25	Aquadopp	D	VELPT	10
26	Aquadopp 300m	A	VELPT	10
27	icListen HF	A	HYDBB	11
28	pCO2-pro	A	PCO2A	12
29	XR-420	A	TMPSF	13
30	ISUS	B	NUTNR	14
31	SUNA	N	NUTNR	14
32	Deep SUNA	A	NUTNR	14
33	OCR507 ICSW	B	SPKIR	14
34	OCR507 ICSW	A	SPKIR	14
35	digital PAR	A	PARAD	14
36	SBE 16plusV2	A	CTDBP	15
37	SBE 16plusV2	B	CTDBP	15
38	SBE 16plusV2	C	CTDBP	15
39	SBE 16plusV2	D	CTDBP	15
40	SBE 16plusV2	E	CTDBP	15
41	SBE 16plusV2	F	CTDBP	15
42	SBE 16plusV2	N	CTDBP	15
43	SBE 16plusV2	O	CTDBP	15
44	SBE 16plusV2	A	CTDPF	15
45	SBE Glider Payload CTD (GP-CTD)	N	CTDAV	15
46	SBE Glider Payload CTD (GP-CTD)	M	CTDAV	15
47	SBE Glider Payload CTD (GP-CTD)	M	CTDGV	15
48	SBE 54	A	PREST	15
49	SBE 54	B	PREST	15
50	SBE 52MP	K	CTDPF	15
51	SBE 52MP	L	CTDPF	15
52	SBE 43F	K	DOFST	15
53	SBE 26plus	A	PRESF	15
54	SBE 26plus	B	PRESF	15
55	SBE 26plus	C	PRESF	15
56	SBE 43	A	DOFST	15
57	SBE 37IM	Q	CTDMO	15
58	SBE 37IM	R	CTDMO	15
59	SBE 37IM	G	CTDMO	15
60	SBE 37IM	H	CTDMO	15
61	ASIMET	A	METBK	16
62	1Cam	A	CAMHD	17
63	SAMI-pH	D	PHSEN	18
64	SAMI-pH	E	PHSEN	18
65	SAMI-pH	F	PHSEN	18
66	SAMI-pH	A	PHSEN	18
67	SAMI-pCO2	B	PCO2W	18
68	SAMI-pCO2	A	PCO2W	18
69	OsmoSampler	A	OSMOI	19
70	Workhorse Navigator 600 kHz dual	N	ADCPA	20
71	Explorer DVL 600 kHz	M	ADCPA	20
72	WorkHorse LongRanger Monitor 75khz	K	ADCPS	20
73	WorkHorse LongRanger Monitor 75khz	I	ADCPS	20
74	WorkHorse LongRanger Sentinel 75khz	L	ADCPS	20
75	WorkHorse LongRanger Sentinel 75khz	J	ADCPS	20
76	WorkHorse LongRanger Sentinel 75khz	N	ADCPS	20
77	WorkHorse Monitor 300khz	B	ADCPT	20
78	WorkHorse Sentinel 300khz	C	ADCPT	20
79	WorkHorse Sentinel 600khz	A	ADCPT	20
80	WorkHorse Sentinel 600khz	M	ADCPT	20
81	WorkHorse Sentinel150khz	G	ADCPT	20
82	WorkHorse Sentinel150khz	F	ADCPT	20
83	Workhorse Quartermaster 150kHz	E	ADCPT	20
84	Workhorse Quartermaster 150kHz	D	ADCPT	20
85	Workhorse custom 600 kHz 5 Beam	A	VADCP	20
86	AC-S	D	OPTAA	21
87	AC-S	C	OPTAA	21
88	FLNTURTD (chlorophyll and backscatter), and FLCDRTD (CDOM)	A	FLORT	21
89	ECO Triplet-w	D	FLORT	21
90	ECO Triplet	K	FLORT	21
91	ECO Triplet	N	FLORT	21
92	ECO Puck FLBBCD-SLK	M	FLORT	21
93	ECO Puck FLBB-SLC	M	FLORD	21
94	FLBBRTD	L	FLORD	21
95	DCFS	A	FDCHP	22
96	non-commercial PPSDN	A	PPSDN	23
97	non-commercial RASFL	A	RASFL	23
98	non-commercial TRHPH	A	TRHPH	23
99	non-commercial BOTPT	A	BOTPT	23
100	non-commercial FLOBN	A	FLOBN	23
101	non-commercial HPIES	A	HPIES	23
102	non-commercial MASSP	A	MASSP	23
103	non-commercial THSPH	A	THSPH	23
104	unknown	0	ACOMM	24
105	unknown	M	ACOMM	24
106	unknown	0	MOPAK	24
107	unknown	P	CTDBP	24
108	unknown	G	FLORD	24
109	unknown	C	PCO2W	24
110	unknown	C	ZPLSC	24
111	unknown	A	ZPLSG	24
112	unknown	J	DOFST	24
113	unknown	J	PARAD	24
114	unknown	J	OPTAA	24
115	unknown	J	NUTNR	24
116	unknown	J	SPKIR	24
117	unknown	J	CTDPF	24
118	unknown	J	FLORT	24
119	unknown	J	VELPT	24
120	unknown	O	SPKIR	24
121	unknown	O	PCO2W	24
122	unknown	O	DOSTA	24
123	unknown	O	OPTAA	24
124	unknown	O	NUTNR	24
125	unknown	O	FLORD	24
126	unknown	O	CTDPF	24
127	unknown	M	OPTAA	24
128	unknown	J	DOSTA	24
129	unknown	M	NUTNR	24
\.


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY instruments (id, instrument_name, description, location_description, instrument_series, serial_number, display_name, model_id, asset_id, depth_rating, manufacturer_id) FROM stdin;
1	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	25	24
2	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	80	24
3	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	80	24
4	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
5	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
6	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	500	18
7	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	25	10
8	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	25	24
9	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	25	24
10	VEL3D	Velocity_point_3D_turb	Benthic Package (J Box)	C	\N	3-D Single Point Velocity Meter	23	1	500	10
11	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
12	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
13	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	A	\N	Velocity Profiler (short range)	79	1	5	20
14	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
15	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
16	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
17	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
18	ADCPT	Velocity_profile_short_range	MFN	M	\N	Velocity Profiler (short range)	80	1	25	20
19	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	80	24
20	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	500	21
21	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
22	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
23	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	5	18
24	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	25	24
25	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	80	21
26	PCO2W	pCO2_water	Benthic Package (J Box)	B	\N	pCO2 Water	67	1	80	18
27	HYDBB	Hydrophone_BB_passive	Benthic Package (J Box)	A	\N	Broadband Acoustic Receiver (Hydrophone)	27	1	80	11
28	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	25	21
29	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
30	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
31	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
32	DOSTA	oxygen_dissolved_stable	Benthic Package (J Box)	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
33	ADCPT	Velocity_profile_short_range	MFN	M	\N	Velocity Profiler (short range)	80	1	25	20
34	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	25	24
35	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
36	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	25	18
37	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
38	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	25	24
39	CAMDS	camera_digital_still_strobe	Benthic Package (J Box) - via wet/mate connector	B	\N	Digital Still Camera with Strobes	17	1	500	7
40	PCO2W	pCO2_water	Benthic Package (J Box)	B	\N	pCO2 Water	67	1	500	18
41	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
42	SPKIR	spectral_irradiance	shallow profiling body	A	\N	Spectral Irradiance	34	1	200	14
43	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
44	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	80	24
45	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
46	FLORT	Fluorometer_three_wavelength	shallow profiling body	D	\N	3-Wavelength Fluorometer	89	1	200	21
47	NUTNR	nutrient_Nitrate	shallow profiling body	A	\N	Nitrate	32	1	200	14
48	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
49	PRESF	pressure_SF	MFN	A	\N	Seafloor Pressure	53	1	25	15
50	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
51	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
52	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
53	CTDPF	CTD_profiler	shallow profiling body	A	\N	CTD Profiler	44	1	200	15
54	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
55	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
56	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
57	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
58	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
59	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
60	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	80	24
245	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
61	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
62	CTDBP	CTD_bottom_pumped	Benthic Package (J Box)	O	\N	CTD Pumped	43	1	500	15
63	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
64	HYDBB	Hydrophone_BB_passive	Benthic Package (J Box)	A	\N	Broadband Acoustic Receiver (Hydrophone)	27	1	500	11
65	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
66	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	25	24
67	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	25	24
68	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	25	18
69	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
70	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	25	18
71	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	80	24
72	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
73	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	25	24
74	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
75	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
76	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
77	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
78	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
79	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	80	18
80	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
81	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
82	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
83	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
84	OPTAA	attenuation_absorption_optical	Benthic Package (J Box)	C	\N	Absorption Spectrophotometer	87	1	500	21
85	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	25	24
86	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	25	24
87	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	500	15
88	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	25	24
89	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	25	24
90	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
91	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
92	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
93	ADCPS	Velocity_profile_long_range	MFN	J	\N	Velocity Profiler (long range)	75	1	500	20
94	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
95	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	80	24
96	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	80	24
97	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	80	7
98	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
99	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
100	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	C	\N	Velocity Profiler (short range)	78	1	5	20
101	CTDBP	CTD_bottom_pumped	MFN	E	\N	CTD Pumped	40	1	500	15
102	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	500	10
103	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
104	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	25	7
105	FLORT	Fluorometer_three_wavelength	deep profiling body	A	\N	3-Wavelength Fluorometer	88	1	500	21
106	ZPLSC	plankton_ZP_sonar_coastal	mid-water platform	B	\N	Bio-acoustic Sonar (Coastal)	15	1	200	7
107	PHSEN	pH_stable	Benthic Package (J Box)	D	\N	Seawater pH	63	1	500	18
108	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
109	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
110	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
111	DOSTA	oxygen_dissolved_stable	mid-water platform	D	\N	Dissolved Oxygen Stable Response	1	1	200	1
112	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
113	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
114	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
115	VELPT	Velocity_point	shallow profiling body	D	\N	Single Point Velocity Meter	25	1	200	10
116	PHSEN	pH_stable	Benthic Package (J Box)	D	\N	Seawater pH	63	1	80	18
117	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	80	24
118	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	25	1
119	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
120	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	80	24
121	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	80	24
122	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
123	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
124	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
125	PRESF	pressure_SF	MFN	A	\N	Seafloor Pressure	53	1	25	15
126	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
127	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	80	24
128	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
129	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
130	DOSTA	oxygen_dissolved_stable	deep profiling body	D	\N	Dissolved Oxygen Stable Response	1	1	500	1
131	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
132	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	500	18
133	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	500	1
134	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	25	24
135	OPTAA	attenuation_absorption_optical	Benthic Package (J Box)	D	\N	Absorption Spectrophotometer	86	1	80	21
136	PRESF	pressure_SF	MFN	B	\N	Seafloor Pressure	54	1	80	15
137	ADCPT	Velocity_profile_short_range	MFN	C	\N	Velocity Profiler (short range)	78	1	80	20
138	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
139	DOFST	oxygen_dissolved_fastresp	shallow profiling body	A	\N	Dissolved Oxygen Fast Response	56	1	200	15
140	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
141	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	80	24
142	OPTAA	attenuation_absorption_optical	shallow profiling body	D	\N	Absorption Spectrophotometer	86	1	200	21
143	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	500	15
144	CTDBP	CTD_bottom_pumped	Benthic Package (J Box)	N	\N	CTD Pumped	42	1	80	15
145	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	25	7
146	CAMDS	camera_digital_still_strobe	Benthic Package (J Box) - via wet/mate connector	B	\N	Digital Still Camera with Strobes	17	1	80	7
147	CTDPF	CTD_profiler	deep profiling body	L	\N	CTD Profiler	51	1	500	15
148	ADCPS	Velocity_profile_long_range	Benthic Package (J Box)	I	\N	Velocity Profiler (long range)	73	1	500	20
149	ADCPT	Velocity_profile_short_range	Benthic Package (J Box)	B	\N	Velocity Profiler (short range)	77	1	80	20
150	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	80	24
151	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
152	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	25	24
153	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
154	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
155	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	25	1
156	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
157	PHSEN	pH_stable	shallow profiling body	A	\N	Seawater pH	66	1	200	18
158	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	80	10
159	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
160	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
161	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
162	DOSTA	oxygen_dissolved_stable	Benthic Package (J Box)	D	\N	Dissolved Oxygen Stable Response	1	1	500	1
163	PHSEN	pH_stable	mid-water platform, upward-looking	A	\N	Seawater pH	66	1	200	18
164	FDCHP	flux_direct_cov_HP	Buoy Tower 3 M	A	\N	Direct Covariance Flux	95	1	3	22
165	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	80	24
166	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
167	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
168	PRESF	pressure_SF	MFN	C	\N	Seafloor Pressure	55	1	500	15
169	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
170	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
171	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
172	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
173	PARAD	PAR	shallow profiling body	A	\N	Photosynthetically Available Radiation	35	1	200	14
174	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
175	ZPLSC	plankton_ZP_sonar_coastal	LV-Node	B	\N	Bio-acoustic Sonar (Coastal)	15	1	80	7
176	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	80	24
177	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD Pumped	38	1	80	15
178	VEL3D	Velocity_point_3D_turb	Benthic Package (J Box)	C	\N	3-D Single Point Velocity Meter	23	1	80	10
179	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
180	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
181	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	80	24
182	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	25	24
183	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	25	24
184	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	25	21
185	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
186	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD Pumped	38	1	25	15
187	PCO2W	pCO2_water	shallow profiling body	A	\N	pCO2 Water	68	1	200	18
188	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
189	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	500	3
190	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
191	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	500	24
192	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
193	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
194	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	25	24
195	CTDPF	CTD_profiler	mid-water platform	A	\N	CTD Profiler	44	1	200	15
196	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
197	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD Pumped	38	1	25	15
198	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
199	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	25	10
200	OPTAA	attenuation_absorption_optical	MFN	C	\N	Absorption Spectrophotometer	87	1	500	21
201	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
202	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
203	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	25	18
204	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
205	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
206	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
207	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	80	24
208	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
209	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	25	24
210	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
211	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
212	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
213	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
214	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
215	PCO2W	pCO2_water	mid-water platform	A	\N	pCO2 Water	68	1	200	18
216	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
217	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
218	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
219	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	80	18
220	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
221	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	C	\N	Velocity Profiler (short range)	78	1	5	20
222	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
223	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
224	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
225	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	5	18
226	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
227	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
228	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	500	10
229	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	25	24
230	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
231	VEL3D	Velocity_point_3D_turb	deep profiling body	A	\N	3-D Single Point Velocity Meter	9	1	500	4
232	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	A	\N	Velocity Profiler (short range)	79	1	5	20
233	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	500	7
234	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
235	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
236	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	4000	1
237	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
238	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
239	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
240	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
241	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
242	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
243	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
244	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
246	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
247	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
248	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	4000	15
249	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
250	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
251	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
252	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
253	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
254	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	4000	4
255	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
256	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
257	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
258	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
259	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
260	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
261	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
262	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
263	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
264	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
265	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2100	21
266	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
267	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
268	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
269	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
270	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
271	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2100	15
272	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
273	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
274	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
275	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
276	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
277	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
278	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
279	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	4000	21
280	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
281	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
282	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
283	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2100	1
284	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
285	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
286	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
287	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
288	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
289	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
290	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
291	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
292	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
293	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
294	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
295	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
296	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2100	4
297	PARAD	PAR		N	\N	Photosynthetically Available Radiation	6	1	-1	3
298	PRESF	pressure_SF	MFN	B	\N	Seafloor Pressure	54	1	130	15
299	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
300	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
301	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	130	15
302	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	360	15
303	PARAD	PAR		N	\N	Photosynthetically Available Radiation	6	1	-1	3
304	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
305	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
306	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
307	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
308	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
309	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity Profiler (short range)	81	1	140	20
310	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
375	ADCPS	Velocity_profile_long_range	MFN	J	\N	Velocity Profiler (long range)	75	1	520	20
311	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	140	10
312	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	130	18
313	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
314	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	520	3
315	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	130	24
316	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
317	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	130	24
318	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
319	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	210	24
320	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
321	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
322	ADCPT	Velocity_profile_short_range	MFN	F	\N	Velocity Profiler (short range)	82	1	210	20
323	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
324	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	210	21
325	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
326	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
327	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
328	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	140	15
329	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	130	3
330	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
331	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
332	DOSTA	oxygen_dissolved_stable		N	\N	Dissolved Oxygen Stable Response	3	1	-1	1
333	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
334	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	210	24
335	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	140	3
336	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
337	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	130	24
338	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
339	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	520	18
340	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	520	15
341	CTDBP	CTD_bottom_pumped	MFN	D	\N	CTD Pumped	39	1	210	15
342	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	210	24
343	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
344	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	210	1
345	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
346	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	520	10
347	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
348	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
349	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	140	15
350	CTDBP	CTD_bottom_pumped	MFN	D	\N	CTD Pumped	39	1	130	15
351	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	520	10
352	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
353	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
354	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	210	18
355	VELPT	Velocity_point	MFN	B	\N	Single Point Velocity Meter	21	1	520	10
356	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
357	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	520	24
358	CTDAV	CTD_AUV		N	\N	CTD AUV	45	1	-1	15
359	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
360	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
361	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
362	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
363	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	520	15
364	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
365	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
366	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	210	18
367	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
368	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	520	18
369	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	520	1
370	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
371	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	130	24
372	ADCPA	Velocity_profile_mobile_asset		N	\N	Velocity Profiler (short range) for mobile assets	70	1	-1	20
373	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
374	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	130	24
376	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	210	24
377	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	520	21
378	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
379	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
380	CTDBP	CTD_bottom_pumped	MFN	E	\N	CTD Pumped	40	1	520	15
381	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
382	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
383	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
384	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
385	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
386	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	130	21
387	PRESF	pressure_SF	MFN	C	\N	Seafloor Pressure	55	1	520	15
388	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	520	3
389	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	210	24
390	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	210	24
391	ADCPT	Velocity_profile_short_range	MFN	F	\N	Velocity Profiler (short range)	82	1	130	20
392	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	130	10
393	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
394	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
395	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	360	21
396	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	130	18
397	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
398	ADCPA	Velocity_profile_mobile_asset		N	\N	Velocity Profiler (short range) for mobile assets	70	1	-1	20
399	CTDAV	CTD_AUV		N	\N	CTD AUV	45	1	-1	15
400	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
401	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
402	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	130	24
403	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	520	15
404	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	360	3
405	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	130	24
406	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity Profiler (short range)	81	1	130	20
407	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	520	21
408	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
409	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	210	24
410	FLORT	Fluorometer_three_wavelength		N	\N	3-Wavelength Fluorometer	91	1	-1	21
411	FDCHP	flux_direct_cov_HP	Buoy Tower 3 M	A	\N	Direct Covariance Flux	95	1	3	22
412	NUTNR	nutrient_Nitrate		N	\N	Nitrate	31	1	-1	14
413	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
414	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	360	15
415	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
416	FLORT	Fluorometer_three_wavelength		N	\N	3-Wavelength Fluorometer	91	1	-1	21
417	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
418	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
419	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
420	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
421	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	210	24
422	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
423	DOSTA	oxygen_dissolved_stable		N	\N	Dissolved Oxygen Stable Response	3	1	-1	1
424	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
425	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	140	21
426	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
427	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
428	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
429	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	210	24
430	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
431	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
432	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
433	VELPT	Velocity_point	MFN	A	\N	Single Point Velocity Meter	26	1	130	10
434	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
435	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity Profiler (short range)	81	1	360	20
436	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
437	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
438	ADCPS	Velocity_profile_long_range	Instrument Frame	L	\N	Velocity Profiler (long range)	74	1	520	20
439	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
440	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	520	21
441	NUTNR	nutrient_Nitrate		N	\N	Nitrate	31	1	-1	14
442	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
443	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	360	10
444	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	130	24
445	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
446	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	210	24
447	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	130	21
448	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	130	24
449	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	520	15
450	PRESF	pressure_SF	MFN	B	\N	Seafloor Pressure	54	1	210	15
451	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
452	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
453	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
454	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	130	15
455	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	130	24
456	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
457	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
458	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
459	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
460	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
461	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
462	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
463	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1500	15
464	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1000	15
465	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	750	15
466	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
467	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
468	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
469	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	80	24
470	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	80	24
471	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	Dissolved Oxygen Stable Response	1	1	1	1
472	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
473	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	40	24
474	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
475	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
476	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD Pumped	41	1	12	15
477	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
478	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
479	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
480	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	3-Wavelength Fluorometer	89	1	1	21
481	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
482	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2600	4
483	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	12	14
484	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	40	24
485	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
486	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
487	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
488	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	Spectral Irradiance	33	1	5	14
489	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
490	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
491	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
492	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
493	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
494	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	5000	4
495	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity Profiler (long range)	76	1	500	20
496	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
497	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
498	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
499	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	5000	21
500	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	20	15
501	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	100	15
502	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	60	15
503	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
504	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
505	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	180	15
506	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
507	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	12	24
508	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
509	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	12	14
510	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	5000	15
511	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	12	21
512	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
513	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
514	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
515	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
516	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	350	15
517	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	500	15
518	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	Absorption Spectrophotometer	86	1	1	21
519	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
520	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
521	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
522	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
523	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
524	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
525	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
526	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
527	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2600	21
528	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	130	24
529	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	20	18
530	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	100	18
531	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
532	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
533	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	40	24
534	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
535	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	12	10
536	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2600	1
537	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	12	18
538	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2600	15
539	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
540	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
541	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
542	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
543	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
544	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
545	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	12	1
546	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
547	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
548	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
549	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	5000	1
550	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
551	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	Nitrate	30	1	1	14
552	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
553	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
554	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	250	15
555	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
556	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
557	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	12	21
558	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	130	24
559	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	80	24
560	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
561	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	130	24
562	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
563	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
564	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	130	24
565	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
566	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
695	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
567	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	12	10
568	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
569	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2400	10
570	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
571	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	20	18
572	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	100	18
573	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	Dissolved Oxygen Stable Response	1	1	1	1
574	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	Spectral Irradiance	33	1	5	14
575	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
576	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2100	10
577	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
578	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	80	24
579	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
580	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
581	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	12	14
582	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
583	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
584	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
585	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
586	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	12	14
587	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2400	10
588	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2700	15
589	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2700	10
590	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
591	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	130	24
592	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	40	24
593	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
594	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
595	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	40	24
596	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	40	24
597	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	130	24
598	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
599	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
600	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	12	24
601	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	80	24
602	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	1800	10
603	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
604	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1500	15
605	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1000	15
606	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2100	15
607	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
608	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	750	15
609	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2600	4
610	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2400	15
611	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
612	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
613	FDCHP	flux_direct_cov_HP	Buoy Tower 5 M	A	\N	Direct Covariance Flux	95	1	5	22
614	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2100	15
615	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
616	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
617	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	12	18
618	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
619	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2600	15
620	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2100	10
621	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
622	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
623	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
624	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
625	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
626	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
627	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
628	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
629	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1800	15
630	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	12	21
631	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
632	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	Nitrate	30	1	1	14
633	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
634	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
635	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
636	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
637	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
638	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2700	15
639	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2600	1
640	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2400	15
641	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	80	24
642	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	12	21
643	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	3-Wavelength Fluorometer	89	1	1	21
644	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
645	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	Absorption Spectrophotometer	86	1	1	21
646	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1800	15
647	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
648	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
649	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
650	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
651	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
652	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
653	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	250	15
654	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	180	15
655	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD Pumped	41	1	12	15
656	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	20	15
657	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	100	15
658	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	60	15
659	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
660	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
661	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
662	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
663	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity Profiler (long range)	76	1	500	20
664	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
665	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2600	21
666	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
667	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
668	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
669	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
670	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
671	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
672	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2700	10
673	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	1800	10
674	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
675	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
676	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	12	1
677	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	350	15
678	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	500	15
679	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
680	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
681	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
682	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
683	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
684	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	12	21
685	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
686	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
687	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	130	24
688	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	3-Wavelength Fluorometer	89	1	1	21
689	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
690	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	40	24
691	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity Profiler (long range)	76	1	500	20
692	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
693	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2400	21
694	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
696	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
697	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
698	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	Absorption Spectrophotometer	86	1	1	21
699	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
700	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	4600	4
701	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
702	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	12	14
703	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
704	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
705	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2400	15
706	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
707	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
708	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
709	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
710	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	Nitrate	30	1	1	14
711	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
712	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
713	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	250	15
714	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	180	15
715	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	100	15
716	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	60	15
717	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
718	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	20	15
719	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
720	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
721	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
722	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	Dissolved Oxygen Stable Response	1	1	1	1
723	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
724	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
725	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	12	10
726	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	12	1
727	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
728	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	500	15
729	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	350	15
730	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
731	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
732	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2400	4
733	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
734	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	130	24
735	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
736	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
737	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
738	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
739	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
740	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	100	18
741	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
742	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	80	24
743	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	20	18
744	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
745	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
746	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
747	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
748	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
749	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
750	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	80	24
751	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD Pumped	41	1	12	15
752	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	12	24
753	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	130	24
754	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
755	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2400	1
756	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
757	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	4600	1
758	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
759	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
760	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
761	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
762	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	12	21
763	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	Spectral Irradiance	33	1	5	14
764	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	80	24
765	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
766	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
767	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
768	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
769	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
770	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
771	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
772	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	12	14
773	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	40	24
774	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
775	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	750	15
776	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1500	15
777	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1000	15
778	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	4600	21
779	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
780	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
781	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	12	18
782	FDCHP	flux_direct_cov_HP	Buoy Tower 5 M	A	\N	Direct Covariance Flux	95	1	5	22
783	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
784	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
785	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
786	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	4600	15
787	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
788	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	40	24
789	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
790	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
\.


--
-- Data for Name: streams; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY streams (id, stream_name, instrument_id, description) FROM stdin;
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY datasets (id, stream_id, deployment_id, process_level, is_recovered) FROM stdin;
\.


--
-- Data for Name: dataset_keywords; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY dataset_keywords (id, dataset_id, concept_name, concept_description) FROM stdin;
\.


--
-- Name: dataset_keywords_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('dataset_keywords_id_seq', 1, false);


--
-- Name: datasets_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('datasets_id_seq', 1, false);


--
-- Name: deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('deployments_id_seq', 1, true);


--
-- Data for Name: drivers; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY drivers (id, instrument_id, driver_name, driver_version, author) FROM stdin;
\.


--
-- Data for Name: driver_stream_link; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY driver_stream_link (id, driver_id, stream_id) FROM stdin;
\.


--
-- Name: driver_stream_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('driver_stream_link_id_seq', 1, false);


--
-- Name: drivers_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('drivers_id_seq', 1, false);


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('files_id_seq', 1, false);


--
-- Data for Name: inspection_status; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY inspection_status (id, asset_id, file_id, status, technician_name, comments, inspection_date, document) FROM stdin;
\.


--
-- Name: inspection_status_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('inspection_status_id_seq', 1, false);


--
-- Name: installation_record_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('installation_record_id_seq', 1, true);


--
-- Data for Name: installation_records; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY installation_records (id, asset_id, assembly_id, date_installed, date_removed, technician_name, comments, file_id) FROM stdin;
1	1	1	\N	\N	\N	\N	\N
\.


--
-- Data for Name: platforms; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY platforms (id, platform_name, description, location_description, platform_series, is_mobile, serial_no, asset_id, manufacturer_id) FROM stdin;
1	CE01ISSM-LM001	Endurance OR Inshore Surface Mooring	Endurance OR  (25 m) Inshore Surface Mooring		f		1	24
2	CE01ISSM-MFD00	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	24
3	CE01ISSM-MFD35	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	24
4	CE01ISSM-MFD37	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	24
5	CE01ISSM-RID16	Endurance OR Inshore Surface Mooring	Mooring Riser		f		1	24
6	CE01ISSM-SBD17	Endurance OR Inshore Surface Mooring	Surface Buoy		t		1	24
7	CE01ISSP-CP001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
8	CE01ISSP-PL001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
9	CE01ISSP-SP001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
10	CE02SHBP-BP001	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	24
11	CE02SHBP-LJ01D	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	24
12	CE02SHBP-MJ01C	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	24
13	CE02SHSM-RID26	Endurance OR Shelf Surface Mooring	Mooring Riser		f		1	24
14	CE02SHSM-RID27	Endurance OR Shelf Surface Mooring	Mooring Riser		f		1	24
15	CE02SHSM-SBD11	Endurance OR Shelf Surface Mooring	Surface Buoy		t		1	24
16	CE02SHSM-SBD12	Endurance OR Shelf Surface Mooring	Surface Buoy		t		1	24
17	CE02SHSM-SM001	Endurance OR Shelf Surface Mooring	Endurance OR Shelf  (80 m) Surface Mooring		f		1	24
18	CE02SHSP-CP001	Endurance OR Shelf Surface-Piercing Profiler Mooring	Endurance OR Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	24
19	CE02SHSP-SP001	Endurance OR Shelf Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
20	CE04OSBP-BP001	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	24
21	CE04OSBP-LJ01C	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	24
22	CE04OSBP-LV01C	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	24
23	CE04OSHY-DP01B	Endurance OR Offshore Hybrid Profiler Mooring	Deep Profiler		f		1	24
24	CE04OSHY-GP001	Endurance OR Offshore Hybrid Profiler Mooring	Endurance OR Offshore (500 m) Hybrid Profiler Mooring		f		1	24
25	CE04OSHY-PC01B	Endurance OR Offshore Hybrid Profiler Mooring	200m Platform		f		1	24
26	CE04OSHY-SF01B	Endurance OR Offshore Hybrid Profiler Mooring	Shallow Profiler		f		1	24
27	CE04OSSM-RID26	Endurance OR Offshore Surface Mooring	Mooring Riser		f		1	24
28	CE04OSSM-RID27	Endurance OR Offshore Surface Mooring	Mooring Riser		f		1	24
29	CE04OSSM-SBD11	Endurance OR Offshore Surface Mooring	Surface Buoy		t		1	24
30	CE04OSSM-SBD12	Endurance OR Offshore Surface Mooring	Surface Buoy		t		1	24
31	CE04OSSM-SM001	Endurance OR Offshore Surface Mooring	Endurance OR Offshore (500 m) Surface Mooring		f		1	24
32	CE05MOAS-GL001	Endurance Mobile Assets	Endurance Glider 1		t		1	24
33	CE05MOAS-GL002	Endurance Mobile Assets	Endurance Glider 2		t		1	24
34	CE05MOAS-GL003	Endurance Mobile Assets	Endurance Glider 3		t		1	24
35	CE05MOAS-GL004	Endurance Mobile Assets	Endurance Glider 4		t		1	24
36	CE05MOAS-GL005	Endurance Mobile Assets	Endurance Glider 5		t		1	24
37	CE05MOAS-GL006	Endurance Mobile Assets	Endurance Glider 6		t		1	24
38	CE06ISSM-LM001	Endurance WA Inshore Surface Mooring	Endurance WA Inshore (25 m) Surface Mooring		f		1	24
39	CE06ISSM-MFD00	Endurance WA Inshore Surface Mooring	MFN		f		1	24
40	CE06ISSM-MFD35	Endurance WA Inshore Surface Mooring	MFN		f		1	24
41	CE06ISSM-MFD37	Endurance WA Inshore Surface Mooring	MFN		f		1	24
42	CE06ISSM-RID16	Endurance WA Inshore Surface Mooring	Mooring Riser		f		1	24
43	CE06ISSM-SBD17	Endurance WA Inshore Surface Mooring	Surface Buoy		t		1	24
44	CE06ISSP-CP001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
45	CE06ISSP-PL001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
46	CE06ISSP-SP001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
47	CE07SHSM-HM001	Endurance WA Shelf Surface Mooring	Endurance WA Shelf (80 m) Surface Mooring		f		1	24
48	CE07SHSM-MFD00	Endurance WA Shelf Surface Mooring	MFN		f		1	24
49	CE07SHSM-MFD35	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
50	CE07SHSM-MFD37	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
51	CE07SHSM-RID26	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
52	CE07SHSM-RID27	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
53	CE07SHSM-SBD11	Endurance WA Shelf Surface Mooring	Surface Buoy		t		1	24
54	CE07SHSM-SBD12	Endurance WA Shelf Surface Mooring	Surface Buoy		t		1	24
55	CE07SHSP-CP001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	24
56	CE07SHSP-PL001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	24
57	CE07SHSP-SP001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
58	CE090SSM-MFD00	Endurance WA Offshore Surface Mooring	MFN		f		1	24
59	CE09OSPM-PM001	Endurance WA Offshore Profiling Mooring	Endurance WA Offshore (500 m) Profiler Mooring		f		1	24
60	CE09OSPM-WF001	Endurance WA Offshore Profiling Mooring	Wire-Following Profiler		f		1	24
61	CE09OSSM-HM001	Endurance WA Offshore Surface Mooring	Endurance WA Offshore (500 m) Surface Mooring		f		1	24
62	CE09OSSM-MFD00	Endurance WA Offshore Surface Mooring	MFN		f		1	24
63	CE09OSSM-MFD35	Endurance WA Offshore Surface Mooring	MFN		f		1	24
64	CE09OSSM-MFD37	Endurance WA Offshore Surface Mooring	MFN		f		1	24
65	CE09OSSM-RID26	Endurance WA Offshore Surface Mooring	Mooring Riser		f		1	24
66	CE09OSSM-RID27	Endurance WA Offshore Surface Mooring	Mooring Riser		f		1	24
67	CE09OSSM-SBD11	Endurance WA Offshore Surface Mooring	Surface Buoy		t		1	24
68	CE09OSSM-SBD12	Endurance WA Offshore Surface Mooring	Surface Buoy		t		1	24
69	GP02HYPM-GP001	PAPA Hybrid Mooring	Hybrid Mooring		f		1	24
70	GP02HYPM-MPC04	PAPA Hybrid Mooring	Mid-water Platform		f		1	24
71	GP02HYPM-RIS01	PAPA Hybrid Mooring	Mooring Riser		f		1	24
72	GP02HYPM-WFP02	PAPA Hybrid Mooring	Wire-Following Profiler #1		f		1	24
73	GP02HYPM-WFP03	PAPA Hybrid Mooring	Wire-Following Profiler #2		f		1	24
74	GP03FLMA-FM001	PAPA Flanking Moorings	Flanking Mooring A		f		1	24
75	GP03FLMA-RIS01	PAPA Flanking Moorings	Mooring Riser		f		1	24
76	GP03FLMA-RIS02	PAPA Flanking Moorings	Mooring Riser		f		1	24
77	GP03FLMB-FM001	PAPA Flanking Moorings	Flanking Mooring B		f		1	24
78	GP03FLMB-RIS01	PAPA Flanking Moorings	Mooring Riser		f		1	24
79	GP03FLMB-RIS02	PAPA Flanking Moorings	Mooring Riser		f		1	24
80	GP05MOAS-GL001	PAPA Mobile Assets	Glider 1		t		1	24
81	GP05MOAS-GL002	PAPA Mobile Assets	Glider 2		t		1	24
82	GP05MOAS-GL003	PAPA Mobile Assets	Glider 3		t		1	24
83	GP05MOAS-PG001	PAPA Mobile Assets	Global Profiling Glider 1		t		1	24
84	GP05MOAS-PG002	PAPA Mobile Assets	Global Profiling Glider 2		t		1	24
85	CP01CNSM-HM001	Pioneer Central P1 Surface Mooring	Pioneer Central P1 Surface Mooring		f		1	24
86	CP01CNSM-MFD00	Pioneer Central P1 Surface Mooring	MFN		f		1	24
87	CP01CNSM-MFD35	Pioneer Central P1 Surface Mooring	MFN		f		1	24
88	CP01CNSM-MFD37	Pioneer Central P1 Surface Mooring	MFN		f		1	24
89	CP01CNSM-RID26	Pioneer Central P1 Surface Mooring	Mooring Riser		f		1	24
90	CP01CNSM-RID27	Pioneer Central P1 Surface Mooring	Mooring Riser		f		1	24
91	CP01CNSM-SBD11	Pioneer Central P1 Surface Mooring	Surface Buoy		t		1	24
92	CP01CNSM-SBD12	Pioneer Central P1 Surface Mooring	Surface Buoy		t		1	24
93	CP01CNSP-CP001	Pioneer Central P1 Surface-Piercing Profiler	Pioneer Central P1 Surface-Piercing Profiler		f		1	24
94	CP01CNSP-PL001	Pioneer Central P1 Surface-Piercing Profiler	Pioneer Central P1 Surface-Piercing Profiler		f		1	24
95	CP01CNSP-SP001	Pioneer Central P1 Surface-Piercing Profiler	Surface-Piercing Profiler		f		1	24
96	CP02PMCI-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Central Inshore Wire-Following Profiler Mooring		f		1	24
97	CP02PMCI-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
98	CP02PMCI-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
99	CP02PMCI-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
100	CP02PMCO-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Central Offshore Wire-Following Profiler Mooring		f		1	24
101	CP02PMCO-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
102	CP02PMCO-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
103	CP02PMCO-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
104	CP02PMUI-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Upstream Inshore Wire-Following Profiler Mooring		f		1	24
105	CP02PMUI-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
106	CP02PMUI-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
107	CP02PMUI-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
108	CP02PMUO-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Upstream Offshore Wire-Following Profiler Mooring		f		1	24
109	CP02PMUO-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
110	CP02PMUO-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
111	CP02PMUO-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
112	CP03ISSM-HM001	Pioneer Inshore P3 Surface Mooring	Pioneer Inshore P3 Surface Mooring		f		1	24
113	CP03ISSM-MFD00	Pioneer Inshore P3 Surface Mooring	MFN		f		1	24
114	CP03ISSM-MFD35	Pioneer Inshore P3 Surface Mooring	MFN		f		1	24
115	CP03ISSM-MFD37	Pioneer Inshore P3 Surface Mooring	MFN		f		1	24
116	CP03ISSM-RID26	Pioneer Inshore P3 Surface Mooring	Mooring Riser		f		1	24
117	CP03ISSM-RID27	Pioneer Inshore P3 Surface Mooring	Mooring Riser		f		1	24
118	CP03ISSM-SBD11	Pioneer Inshore P3 Surface Mooring	Surface Buoy		t		1	24
119	CP03ISSM-SBD12	Pioneer Inshore P3 Surface Mooring	Surface Buoy		t		1	24
120	CP03ISSP-CP001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Pioneer Inshore P3 Surface-Piercing Profiler Mooring		f		1	24
121	CP03ISSP-PL001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Pioneer Inshore P3 Surface-Piercing Profiler Mooring		f		1	24
122	CP03ISSP-SP001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
123	CP04OSPM-PM001	Pioneer Offshore P4 Wire-Following Profiler Mooring	Pioneer Offshore Wire-Following Profiler Mooring		f		1	24
124	CP04OSPM-SBS11	Pioneer Offshore P4 Wire-Following Profiler Mooring	Surface Buoy		t		1	24
125	CP04OSPM-WFP01	Pioneer Offshore P4 Wire-Following Profiler Mooring	Wire-Following Profiler		f		1	24
126	CP04OSSM-HM001	Pioneer Offshore P4 Surface Mooring	Pioneer Offshore P4 Surface Mooring		f		1	24
127	CP04OSSM-MFD00	Pioneer Offshore P4 Surface Mooring	MFN		f		1	24
128	CP04OSSM-MFD35	Pioneer Offshore P4 Surface Mooring	MFN		f		1	24
129	CP04OSSM-MFD37	Pioneer Offshore P4 Surface Mooring	MFN		f		1	24
130	CP04OSSM-RID26	Pioneer Offshore P4 Surface Mooring	Mooring Riser		f		1	24
131	CP04OSSM-RID27	Pioneer Offshore P4 Surface Mooring	Mooring Riser		f		1	24
132	CP04OSSM-SBD11	Pioneer Offshore P4 Surface Mooring	Surface Buoy		t		1	24
133	CP04OSSM-SBD12	Pioneer Offshore P4 Surface Mooring	Surface Buoy		t		1	24
134	CP05MOAS-AV001	Pioneer Mobile Assets	Pioneer AUV 1		t		1	24
135	CP05MOAS-AV002	Pioneer Mobile Assets	Pioneer AUV 2		t		1	24
136	CP05MOAS-GL001	Pioneer Mobile Assets	Pioneer Glider 1		t		1	24
137	CP05MOAS-GL002	Pioneer Mobile Assets	Pioneer Glider 2		t		1	24
138	CP05MOAS-GL003	Pioneer Mobile Assets	Pioneer Glider 3		t		1	24
139	CP05MOAS-GL004	Pioneer Mobile Assets	Pioneer Glider 4		t		1	24
140	CP05MOAS-GL005	Pioneer Mobile Assets	Pioneer Glider 5		t		1	24
141	CP05MOAS-GL006	Pioneer Mobile Assets	Pioneer Glider 6		t		1	24
142	GA01SUMO-RID16	Argentine Surface Mooring	Mooring Riser		f		1	24
143	GA01SUMO-RII11	Argentine Surface Mooring	Mooring Riser		f		1	24
144	GA01SUMO-SBD11	Argentine Surface Mooring	Surface Buoy		t		1	24
145	GA01SUMO-SBD12	Argentine Surface Mooring	Surface Buoy		t		1	24
146	GA01SUMO-SM001	Argentine Surface Mooring	Surface Mooring		f		1	24
147	GA02HYPM-GP001	Argentine Hybrid Mooring	Hybrid Mooring		f		1	24
148	GA02HYPM-MPC04	Argentine Hybrid Mooring	Mid-water Platform		f		1	24
149	GA02HYPM-RIS01	Argentine Hybrid Mooring	Mooring Riser		f		1	24
150	GA02HYPM-WFP02	Argentine Hybrid Mooring	Wire-Following Profiler #1		f		1	24
151	GA02HYPM-WFP03	Argentine Hybrid Mooring	Wire-Following Profiler #2		f		1	24
152	GA03FLMA-FM001	Argentine Flanking Moorings	Flanking Mooring A		f		1	24
153	GA03FLMA-RIS01	Argentine Flanking Moorings	Mooring Riser		f		1	24
154	GA03FLMA-RIS02	Argentine Flanking Moorings	Mooring Riser		f		1	24
155	GA03FLMB-FM001	Argentine Flanking Moorings	Flanking Mooring B		f		1	24
156	GA03FLMB-RIS01	Argentine Flanking Moorings	Mooring Riser		f		1	24
157	GA03FLMB-RIS02	Argentine Flanking Moorings	Mooring Riser		f		1	24
158	GA05MOAS-GL001	Argentine Mobile Assets	Glider No. 1		t		1	24
159	GA05MOAS-GL002	Argentine Mobile Assets	Glider No. 2		t		1	24
160	GA05MOAS-GL003	Argentine Mobile Assets	Glider No. 3		t		1	24
161	GA05MOAS-PG001	Argentine Mobile Assets	Global Profiling Glider 1		t		1	24
162	GA05MOAS-PG002	Argentine Mobile Assets	Global Profiling Glider 2		t		1	24
163	GI01SUMO-RID16	Irminger Sea Surface Mooring	Mooring Riser		f		1	24
164	GI01SUMO-RII11	Irminger Sea Surface Mooring	Mooring Riser		f		1	24
165	GI01SUMO-SBD11	Irminger Sea Surface Mooring	Surface Buoy		t		1	24
166	GI01SUMO-SBD12	Irminger Sea Surface Mooring	Surface Buoy		t		1	24
167	GI01SUMO-SM001	Irminger Sea Surface Mooring	Surface Mooring		f		1	24
168	GI02HYPM-GP001	Irminger Sea Hybrid Mooring	Hybrid Mooring		f		1	24
169	GI02HYPM-MPC04	Irminger Sea Hybrid Mooring	Mid-water Platform		f		1	24
170	GI02HYPM-RIS01	Irminger Sea Hybrid Mooring	Mooring Riser		f		1	24
171	GI02HYPM-WFP02	Irminger Sea Hybrid Mooring	Wire-Following Profiler		f		1	24
172	GI03FLMA-FM001	Irminger Sea Flanking Moorings	Flanking Mooring A		f		1	24
173	GI03FLMA-RIS01	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
174	GI03FLMA-RIS02	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
175	GI03FLMB-FM001	Irminger Sea Flanking Moorings	Flanking Mooring B		f		1	24
176	GI03FLMB-RIS01	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
177	GI03FLMB-RIS02	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
178	GI05MOAS-GL001	Irminger Sea Mobile Assets	Glider No. 1		t		1	24
179	GI05MOAS-GL002	Irminger Sea Mobile Assets	Glider No. 2		t		1	24
180	GI05MOAS-GL003	Irminger Sea Mobile Assets	Glider No. 3		t		1	24
181	GI05MOAS-PG001	Irminger Sea Mobile Assets	Global Profiling Glider 1		t		1	24
182	GI05MOAS-PG002	Irminger Sea Mobile Assets	Global Profiling Glider 2		t		1	24
183	GS01SUMO-RID16	55S Surface Mooring	Mooring Riser		f		1	24
184	GS01SUMO-RII11	55S Surface Mooring	Mooring Riser		f		1	24
185	GS01SUMO-SBD11	55S Surface Mooring	Surface Buoy		t		1	24
186	GS01SUMO-SBD12	55S Surface Mooring	Surface Buoy		t		1	24
187	GS01SUMO-SM001	55S Surface Mooring	Surface Mooring		f		1	24
188	GS02HYPM-GP001	55S Hybrid Mooring	Hybrid Mooring		f		1	24
189	GS02HYPM-MPC04	55S Hybrid Mooring	Mid-water Platform		f		1	24
190	GS02HYPM-RIS01	55S Hybrid Mooring	Mooring Riser		f		1	24
191	GS02HYPM-WFP02	55S Hybrid Mooring	Wire-Following Profiler #1		f		1	24
192	GS02HYPM-WFP03	55S Hybrid Mooring	Wire-Following Profiler #2		f		1	24
193	GS03FLMA-FM001	55S Flanking Moorings	Flanking Mooring A		f		1	24
194	GS03FLMA-RIS01	55S Flanking Moorings	Mooring Riser		f		1	24
195	GS03FLMA-RIS02	55S Flanking Moorings	Mooring Riser		f		1	24
196	GS03FLMB-FM001	55S Flanking Moorings	Flanking Mooring B		f		1	24
197	GS03FLMB-RIS01	55S Flanking Moorings	Mooring Riser		f		1	24
198	GS03FLMB-RIS02	55S Flanking Moorings	Mooring Riser		f		1	24
199	GS05MOAS-GL001	55S Mobile Assets	Glider No. 1		t		1	24
200	GS05MOAS-GL002	55S Mobile Assets	Glider No. 2		t		1	24
201	GS05MOAS-GL003	55S Mobile Assets	Glider No. 3		t		1	24
202	GS05MOAS-PG001	55S Mobile Assets	Global Profiling Glider 1		t		1	24
203	GS05MOAS-PG002	55S Mobile Assets	Global Profiling Glider 2		t		1	24
\.


--
-- Data for Name: platform_deployments; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY platform_deployments (id, start_date, end_date, platform_id, reference_designator, array_id, deployment_id, display_name, geo_location) FROM stdin;
1	\N	\N	1	CE01ISSM-LM001	1	1	Endurance OR  (25 m) Inshore Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
2	\N	\N	2	CE01ISSM-MFD00	1	1	Multi-Function (Node)	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
3	\N	\N	3	CE01ISSM-MFD35	1	1	Multi-Function (Node)	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
4	\N	\N	4	CE01ISSM-MFD37	1	1	Multi-Function (Node)	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
5	\N	\N	5	CE01ISSM-RID16	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
6	\N	\N	6	CE01ISSM-SBD17	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
7	\N	\N	7	CE01ISSP-CP001	1	1	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
8	\N	\N	8	CE01ISSP-PL001	1	1	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
9	\N	\N	9	CE01ISSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
10	\N	\N	10	CE02SHBP-BP001	1	1	Endurance OR Shelf (80 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
11	\N	\N	11	CE02SHBP-LJ01D	1	1	Endurance OR Shelf (80 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
12	\N	\N	12	CE02SHBP-MJ01C	1	1	Endurance OR Shelf (80 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
13	\N	\N	13	CE02SHSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
14	\N	\N	14	CE02SHSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
15	\N	\N	15	CE02SHSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
16	\N	\N	16	CE02SHSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
17	\N	\N	17	CE02SHSM-SM001	1	1	Endurance OR Shelf  (80 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
18	\N	\N	18	CE02SHSP-CP001	1	1	Endurance OR Shelf (80 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
19	\N	\N	19	CE02SHSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
20	\N	\N	20	CE04OSBP-BP001	1	1	Endurance OR Offshore (500 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
21	\N	\N	21	CE04OSBP-LJ01C	1	1	Endurance OR Offshore (500 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
22	\N	\N	22	CE04OSBP-LV01C	1	1	Endurance OR Offshore (500 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
23	\N	\N	23	CE04OSHY-DP01B	1	1	Deep Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
24	\N	\N	24	CE04OSHY-GP001	1	1	Endurance OR Offshore (500 m) Hybrid Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
25	\N	\N	25	CE04OSHY-PC01B	1	1	200m Platform	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
26	\N	\N	26	CE04OSHY-SF01B	1	1	Shallow Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
27	\N	\N	27	CE04OSSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
28	\N	\N	28	CE04OSSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
29	\N	\N	29	CE04OSSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
30	\N	\N	30	CE04OSSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
31	\N	\N	31	CE04OSSM-SM001	1	1	Endurance OR Offshore (500 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
32	\N	\N	32	CE05MOAS-GL001	1	1	Endurance Glider 1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
33	\N	\N	33	CE05MOAS-GL002	1	1	Endurance Glider 2	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
34	\N	\N	34	CE05MOAS-GL003	1	1	Endurance Glider 3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
35	\N	\N	35	CE05MOAS-GL004	1	1	Endurance Glider 4	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
36	\N	\N	36	CE05MOAS-GL005	1	1	Endurance Glider 5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
37	\N	\N	37	CE05MOAS-GL006	1	1	Endurance Glider 6	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
38	\N	\N	38	CE06ISSM-LM001	1	1	Endurance WA Inshore (25 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
39	\N	\N	39	CE06ISSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
40	\N	\N	40	CE06ISSM-MFD35	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
41	\N	\N	41	CE06ISSM-MFD37	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
42	\N	\N	42	CE06ISSM-RID16	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
43	\N	\N	43	CE06ISSM-SBD17	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
44	\N	\N	44	CE06ISSP-CP001	1	1	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
45	\N	\N	45	CE06ISSP-PL001	1	1	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
46	\N	\N	46	CE06ISSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
47	\N	\N	47	CE07SHSM-HM001	1	1	Endurance WA Shelf (80 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
48	\N	\N	48	CE07SHSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
49	\N	\N	49	CE07SHSM-MFD35	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
50	\N	\N	50	CE07SHSM-MFD37	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
51	\N	\N	51	CE07SHSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
52	\N	\N	52	CE07SHSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
53	\N	\N	53	CE07SHSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
54	\N	\N	54	CE07SHSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
55	\N	\N	55	CE07SHSP-CP001	1	1	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
56	\N	\N	56	CE07SHSP-PL001	1	1	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
57	\N	\N	57	CE07SHSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
58	\N	\N	58	CE090SSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
59	\N	\N	59	CE09OSPM-PM001	1	1	Endurance WA Offshore (500 m) Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
60	\N	\N	60	CE09OSPM-WF001	1	1	Wire-Following Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
61	\N	\N	61	CE09OSSM-HM001	1	1	Endurance WA Offshore (500 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
62	\N	\N	62	CE09OSSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
63	\N	\N	63	CE09OSSM-MFD35	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
64	\N	\N	64	CE09OSSM-MFD37	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
65	\N	\N	65	CE09OSSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
66	\N	\N	66	CE09OSSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
67	\N	\N	67	CE09OSSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
68	\N	\N	68	CE09OSSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
69	\N	\N	69	GP02HYPM-GP001	2	1	Hybrid Mooring	0101000020E6100000E3A59BC4200862C04C37894160FD4840
70	\N	\N	70	GP02HYPM-MPC04	2	1	Mid-water Platform	0101000020E6100000E3A59BC4200862C04C37894160FD4840
71	\N	\N	71	GP02HYPM-RIS01	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
72	\N	\N	72	GP02HYPM-WFP02	2	1	Wire-Following Profiler #1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
73	\N	\N	73	GP02HYPM-WFP03	2	1	Wire-Following Profiler #2	0101000020E6100000E3A59BC4200862C04C37894160FD4840
74	\N	\N	74	GP03FLMA-FM001	2	1	Flanking Mooring A	0101000020E6100000E3A59BC4200862C04C37894160FD4840
75	\N	\N	75	GP03FLMA-RIS01	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
76	\N	\N	76	GP03FLMA-RIS02	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
77	\N	\N	77	GP03FLMB-FM001	2	1	Flanking Mooring B	0101000020E6100000E3A59BC4200862C04C37894160FD4840
78	\N	\N	78	GP03FLMB-RIS01	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
79	\N	\N	79	GP03FLMB-RIS02	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
80	\N	\N	80	GP05MOAS-GL001	2	1	Glider 1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
81	\N	\N	81	GP05MOAS-GL002	2	1	Glider 2	0101000020E6100000E3A59BC4200862C04C37894160FD4840
82	\N	\N	82	GP05MOAS-GL003	2	1	Glider 3	0101000020E6100000E3A59BC4200862C04C37894160FD4840
83	\N	\N	83	GP05MOAS-PG001	2	1	Global Profiling Glider 1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
84	\N	\N	84	GP05MOAS-PG002	2	1	Global Profiling Glider 2	0101000020E6100000E3A59BC4200862C04C37894160FD4840
85	\N	\N	85	CP01CNSM-HM001	3	1	Pioneer Central P1 Surface Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
86	\N	\N	86	CP01CNSM-MFD00	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
87	\N	\N	87	CP01CNSM-MFD35	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
88	\N	\N	88	CP01CNSM-MFD37	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
89	\N	\N	89	CP01CNSM-RID26	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
90	\N	\N	90	CP01CNSM-RID27	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
91	\N	\N	91	CP01CNSM-SBD11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
92	\N	\N	92	CP01CNSM-SBD12	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
93	\N	\N	93	CP01CNSP-CP001	3	1	Pioneer Central P1 Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
94	\N	\N	94	CP01CNSP-PL001	3	1	Pioneer Central P1 Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
95	\N	\N	95	CP01CNSP-SP001	3	1	Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
96	\N	\N	96	CP02PMCI-PM001	3	1	Pioneer Central Inshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
97	\N	\N	97	CP02PMCI-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
98	\N	\N	98	CP02PMCI-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
99	\N	\N	99	CP02PMCI-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
100	\N	\N	100	CP02PMCO-PM001	3	1	Pioneer Central Offshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
101	\N	\N	101	CP02PMCO-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
102	\N	\N	102	CP02PMCO-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
103	\N	\N	103	CP02PMCO-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
104	\N	\N	104	CP02PMUI-PM001	3	1	Pioneer Upstream Inshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
105	\N	\N	105	CP02PMUI-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
106	\N	\N	106	CP02PMUI-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
107	\N	\N	107	CP02PMUI-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
108	\N	\N	108	CP02PMUO-PM001	3	1	Pioneer Upstream Offshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
109	\N	\N	109	CP02PMUO-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
110	\N	\N	110	CP02PMUO-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
111	\N	\N	111	CP02PMUO-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
112	\N	\N	112	CP03ISSM-HM001	3	1	Pioneer Inshore P3 Surface Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
113	\N	\N	113	CP03ISSM-MFD00	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
114	\N	\N	114	CP03ISSM-MFD35	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
115	\N	\N	115	CP03ISSM-MFD37	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
116	\N	\N	116	CP03ISSM-RID26	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
117	\N	\N	117	CP03ISSM-RID27	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
118	\N	\N	118	CP03ISSM-SBD11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
119	\N	\N	119	CP03ISSM-SBD12	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
120	\N	\N	120	CP03ISSP-CP001	3	1	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
121	\N	\N	121	CP03ISSP-PL001	3	1	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
122	\N	\N	122	CP03ISSP-SP001	3	1	Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
123	\N	\N	123	CP04OSPM-PM001	3	1	Pioneer Offshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
124	\N	\N	124	CP04OSPM-SBS11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
125	\N	\N	125	CP04OSPM-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
126	\N	\N	126	CP04OSSM-HM001	3	1	Pioneer Offshore P4 Surface Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
127	\N	\N	127	CP04OSSM-MFD00	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
128	\N	\N	128	CP04OSSM-MFD35	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
129	\N	\N	129	CP04OSSM-MFD37	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
130	\N	\N	130	CP04OSSM-RID26	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
131	\N	\N	131	CP04OSSM-RID27	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
132	\N	\N	132	CP04OSSM-SBD11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
133	\N	\N	133	CP04OSSM-SBD12	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
134	\N	\N	134	CP05MOAS-AV001	3	1	Pioneer AUV 1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
135	\N	\N	135	CP05MOAS-AV002	3	1	Pioneer AUV 2	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
136	\N	\N	136	CP05MOAS-GL001	3	1	Pioneer Glider 1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
137	\N	\N	137	CP05MOAS-GL002	3	1	Pioneer Glider 2	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
138	\N	\N	138	CP05MOAS-GL003	3	1	Pioneer Glider 3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
139	\N	\N	139	CP05MOAS-GL004	3	1	Pioneer Glider 4	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
140	\N	\N	140	CP05MOAS-GL005	3	1	Pioneer Glider 5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
141	\N	\N	141	CP05MOAS-GL006	3	1	Pioneer Glider 6	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
142	\N	\N	142	GA01SUMO-RID16	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
143	\N	\N	143	GA01SUMO-RII11	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
144	\N	\N	144	GA01SUMO-SBD11	4	1	Surface Buoy	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
145	\N	\N	145	GA01SUMO-SBD12	4	1	Surface Buoy	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
146	\N	\N	146	GA01SUMO-SM001	4	1	Surface Mooring	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
147	\N	\N	147	GA02HYPM-GP001	4	1	Hybrid Mooring	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
148	\N	\N	148	GA02HYPM-MPC04	4	1	Mid-water Platform	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
149	\N	\N	149	GA02HYPM-RIS01	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
150	\N	\N	150	GA02HYPM-WFP02	4	1	Wire-Following Profiler #1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
151	\N	\N	151	GA02HYPM-WFP03	4	1	Wire-Following Profiler #2	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
152	\N	\N	152	GA03FLMA-FM001	4	1	Flanking Mooring A	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
153	\N	\N	153	GA03FLMA-RIS01	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
154	\N	\N	154	GA03FLMA-RIS02	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
155	\N	\N	155	GA03FLMB-FM001	4	1	Flanking Mooring B	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
156	\N	\N	156	GA03FLMB-RIS01	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
157	\N	\N	157	GA03FLMB-RIS02	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
158	\N	\N	158	GA05MOAS-GL001	4	1	Glider No. 1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
159	\N	\N	159	GA05MOAS-GL002	4	1	Glider No. 2	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
160	\N	\N	160	GA05MOAS-GL003	4	1	Glider No. 3	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
161	\N	\N	161	GA05MOAS-PG001	4	1	Global Profiling Glider 1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
162	\N	\N	162	GA05MOAS-PG002	4	1	Global Profiling Glider 2	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
163	\N	\N	163	GI01SUMO-RID16	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
164	\N	\N	164	GI01SUMO-RII11	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
165	\N	\N	165	GI01SUMO-SBD11	5	1	Surface Buoy	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
166	\N	\N	166	GI01SUMO-SBD12	5	1	Surface Buoy	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
167	\N	\N	167	GI01SUMO-SM001	5	1	Surface Mooring	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
168	\N	\N	168	GI02HYPM-GP001	5	1	Hybrid Mooring	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
169	\N	\N	169	GI02HYPM-MPC04	5	1	Mid-water Platform	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
170	\N	\N	170	GI02HYPM-RIS01	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
171	\N	\N	171	GI02HYPM-WFP02	5	1	Wire-Following Profiler	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
172	\N	\N	172	GI03FLMA-FM001	5	1	Flanking Mooring A	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
173	\N	\N	173	GI03FLMA-RIS01	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
174	\N	\N	174	GI03FLMA-RIS02	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
175	\N	\N	175	GI03FLMB-FM001	5	1	Flanking Mooring B	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
176	\N	\N	176	GI03FLMB-RIS01	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
177	\N	\N	177	GI03FLMB-RIS02	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
178	\N	\N	178	GI05MOAS-GL001	5	1	Glider No. 1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
179	\N	\N	179	GI05MOAS-GL002	5	1	Glider No. 2	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
180	\N	\N	180	GI05MOAS-GL003	5	1	Glider No. 3	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
181	\N	\N	181	GI05MOAS-PG001	5	1	Global Profiling Glider 1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
182	\N	\N	182	GI05MOAS-PG002	5	1	Global Profiling Glider 2	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
183	\N	\N	183	GS01SUMO-RID16	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
184	\N	\N	184	GS01SUMO-RII11	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
185	\N	\N	185	GS01SUMO-SBD11	6	1	Surface Buoy	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
186	\N	\N	186	GS01SUMO-SBD12	6	1	Surface Buoy	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
187	\N	\N	187	GS01SUMO-SM001	6	1	Surface Mooring	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
188	\N	\N	188	GS02HYPM-GP001	6	1	Hybrid Mooring	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
189	\N	\N	189	GS02HYPM-MPC04	6	1	Mid-water Platform	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
190	\N	\N	190	GS02HYPM-RIS01	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
191	\N	\N	191	GS02HYPM-WFP02	6	1	Wire-Following Profiler #1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
192	\N	\N	192	GS02HYPM-WFP03	6	1	Wire-Following Profiler #2	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
193	\N	\N	193	GS03FLMA-FM001	6	1	Flanking Mooring A	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
194	\N	\N	194	GS03FLMA-RIS01	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
195	\N	\N	195	GS03FLMA-RIS02	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
196	\N	\N	196	GS03FLMB-FM001	6	1	Flanking Mooring B	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
197	\N	\N	197	GS03FLMB-RIS01	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
198	\N	\N	198	GS03FLMB-RIS02	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
199	\N	\N	199	GS05MOAS-GL001	6	1	Glider No. 1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
200	\N	\N	200	GS05MOAS-GL002	6	1	Glider No. 2	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
201	\N	\N	201	GS05MOAS-GL003	6	1	Glider No. 3	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
202	\N	\N	202	GS05MOAS-PG001	6	1	Global Profiling Glider 1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
203	\N	\N	203	GS05MOAS-PG002	6	1	Global Profiling Glider 2	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
\.


--
-- Data for Name: instrument_deployments; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY instrument_deployments (id, display_name, start_date, end_date, platform_deployment_id, instrument_id, reference_designator, depth, geo_location) FROM stdin;
1	SPKIR	\N	\N	46	1	CE06ISSP-SP001-07-SPKIRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
2	CTDPF	\N	\N	57	2	CE07SHSP-SP001-08-CTDPFJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
3	DOSTA	\N	\N	19	3	CE02SHSP-SP001-01-DOSTAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
4	OPTAA	\N	\N	28	4	CE04OSSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
5	OPTAA	\N	\N	5	5	CE01ISSM-RID16-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
6	PCO2W	\N	\N	63	6	CE09OSSM-MFD35-05-PCO2WB000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
7	VEL3D	\N	\N	40	7	CE06ISSM-MFD35-01-VEL3DD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
8	ZPLSC	\N	\N	2	8	CE01ISSM-MFD00-00-ZPLSCC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
9	FLORT	\N	\N	9	9	CE01ISSP-SP001-08-FLORTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
10	VEL3D	\N	\N	21	10	CE04OSBP-LJ01C-07-VEL3DC107	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
11	PARAD	\N	\N	34	11	CE05MOAS-GL003-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
12	WAVSS	\N	\N	30	12	CE04OSSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
13	ADCPT	\N	\N	51	13	CE07SHSM-RID26-01-ADCPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
14	MOPAK	\N	\N	29	14	CE04OSSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
15	FLORT	\N	\N	32	15	CE05MOAS-GL001-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
16	FLORT	\N	\N	34	16	CE05MOAS-GL003-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
17	OPTAA	\N	\N	14	17	CE02SHSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
18	ADCPT	\N	\N	40	18	CE06ISSM-MFD35-04-ADCPTM000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
19	CTDPF	\N	\N	19	19	CE02SHSP-SP001-01-CTDPFJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
20	FLORT	\N	\N	60	20	CE09OSPM-WF001-04-FLORTK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
21	CTDBP	\N	\N	28	21	CE04OSSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
22	WAVSS	\N	\N	16	22	CE02SHSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
23	PCO2W	\N	\N	42	23	CE06ISSM-RID16-05-PCO2WB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
24	DOSTA	\N	\N	9	24	CE01ISSP-SP001-02-DOSTAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
25	OPTAA	\N	\N	50	25	CE07SHSM-MFD37-01-OPTAAD000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
26	PCO2W	\N	\N	11	26	CE02SHBP-LJ01D-09-PCO2WB103	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
27	HYDBB	\N	\N	11	27	CE02SHBP-LJ01D-11-HYDBBA106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
28	OPTAA	\N	\N	41	28	CE06ISSM-MFD37-01-OPTAAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
29	VELPT	\N	\N	27	29	CE04OSSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
30	VELPT	\N	\N	65	30	CE09OSSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
31	CTDGV	\N	\N	34	31	CE05MOAS-GL003-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
32	DOSTA	\N	\N	11	32	CE02SHBP-LJ01D-06-DOSTAD106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
33	ADCPT	\N	\N	3	33	CE01ISSM-MFD35-04-ADCPTM000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
34	ZPLSC	\N	\N	39	34	CE06ISSM-MFD00-00-ZPLSCC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
35	ACOMM	\N	\N	27	35	CE04OSSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
36	PCO2W	\N	\N	3	36	CE01ISSM-MFD35-05-PCO2WB000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
37	PHSEN	\N	\N	27	37	CE04OSSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
38	VELPT	\N	\N	46	38	CE06ISSP-SP001-05-VELPTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
39	CAMDS	\N	\N	22	39	CE04OSBP-LV01C-06-CAMDSB106	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
40	PCO2W	\N	\N	21	40	CE04OSBP-LJ01C-09-PCO2WB104	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
41	VELPT	\N	\N	13	41	CE02SHSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
42	SPKIR	\N	\N	26	42	CE04OSHY-SF01B-3D-SPKIRA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
43	PCO2A	\N	\N	68	43	CE09OSSM-SBD12-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
44	SPKIR	\N	\N	19	44	CE02SHSP-SP001-06-SPKIRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
45	PARAD	\N	\N	36	45	CE05MOAS-GL005-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
46	FLORT	\N	\N	26	46	CE04OSHY-SF01B-3A-FLORTD104	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
47	NUTNR	\N	\N	26	47	CE04OSHY-SF01B-4A-NUTNRA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
48	VELPT	\N	\N	15	48	CE02SHSM-SBD11-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
49	PRESF	\N	\N	40	49	CE06ISSM-MFD35-02-PRESFA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
50	MOPAK	\N	\N	15	50	CE02SHSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
51	VELPT	\N	\N	43	51	CE06ISSM-SBD17-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
52	ADCPA	\N	\N	36	52	CE05MOAS-GL005-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
53	CTDPF	\N	\N	26	53	CE04OSHY-SF01B-2A-CTDPFA107	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
54	DOSTA	\N	\N	52	54	CE07SHSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
55	CTDGV	\N	\N	35	55	CE05MOAS-GL004-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
56	CTDBP	\N	\N	5	56	CE01ISSM-RID16-03-CTDBPC001	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
57	MOPAK	\N	\N	53	57	CE07SHSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
58	VELPT	\N	\N	51	58	CE07SHSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
59	DOSTA	\N	\N	5	59	CE01ISSM-RID16-03-DOSTAD002	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
60	NUTNR	\N	\N	19	60	CE02SHSP-SP001-05-NUTNRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
61	OPTAA	\N	\N	42	61	CE06ISSM-RID16-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
62	CTDBP	\N	\N	21	62	CE04OSBP-LJ01C-06-CTDBPO108	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
63	MOPAK	\N	\N	67	63	CE09OSSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
64	HYDBB	\N	\N	21	64	CE04OSBP-LJ01C-11-HYDBBA105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
65	METBK	\N	\N	29	65	CE04OSSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
66	ACOMM	\N	\N	8	66	CE01ISSP-PL001-01-ACOMM0	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
67	OPTAA	\N	\N	46	67	CE06ISSP-SP001-04-OPTAAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
68	PHSEN	\N	\N	40	68	CE06ISSM-MFD35-06-PHSEND000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
69	PARAD	\N	\N	37	69	CE05MOAS-GL006-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
70	PHSEN	\N	\N	3	70	CE01ISSM-MFD35-06-PHSEND000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
71	FLORT	\N	\N	57	71	CE07SHSP-SP001-07-FLORTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
72	ACOMM	\N	\N	42	72	CE06ISSM-RID16-00-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
73	SPKIR	\N	\N	9	73	CE01ISSP-SP001-07-SPKIRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
74	WAVSS	\N	\N	54	74	CE07SHSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
75	FLORT	\N	\N	37	75	CE05MOAS-GL006-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
76	NUTNR	\N	\N	42	76	CE06ISSM-RID16-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
77	NUTNR	\N	\N	66	77	CE09OSSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
78	ACOMM	\N	\N	65	78	CE09OSSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
79	PHSEN	\N	\N	49	79	CE07SHSM-MFD35-06-PHSEND000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
80	VELPT	\N	\N	5	80	CE01ISSM-RID16-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
81	ACOMM	\N	\N	5	81	CE01ISSM-RID16-00-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
82	FLORT	\N	\N	42	82	CE06ISSM-RID16-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
83	DOSTA	\N	\N	33	83	CE05MOAS-GL002-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
84	OPTAA	\N	\N	21	84	CE04OSBP-LJ01C-08-OPTAAC104	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
85	NUTNR	\N	\N	9	85	CE01ISSP-SP001-06-NUTNRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
86	PARAD	\N	\N	9	86	CE01ISSP-SP001-10-PARADJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
87	DOFST	\N	\N	60	87	CE09OSPM-WF001-02-DOFSTK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
88	VELPT	\N	\N	9	88	CE01ISSP-SP001-05-VELPTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
89	CTDPF	\N	\N	46	89	CE06ISSP-SP001-09-CTDPFJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
90	ACOMM	\N	\N	51	90	CE07SHSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
91	DOSTA	\N	\N	28	91	CE04OSSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
92	WAVSS	\N	\N	68	92	CE09OSSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
93	ADCPS	\N	\N	63	93	CE09OSSM-MFD35-04-ADCPSJ000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
94	PARAD	\N	\N	33	94	CE05MOAS-GL002-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
95	DOSTA	\N	\N	57	95	CE07SHSP-SP001-01-DOSTAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
96	FLORT	\N	\N	19	96	CE02SHSP-SP001-07-FLORTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
97	CAMDS	\N	\N	48	97	CE07SHSM-MFD00-00-CAMDSA000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
98	FLORT	\N	\N	33	98	CE05MOAS-GL002-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
99	ADCPA	\N	\N	32	99	CE05MOAS-GL001-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
100	ADCPT	\N	\N	27	100	CE04OSSM-RID26-01-ADCPTC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
101	CTDBP	\N	\N	64	101	CE09OSSM-MFD37-03-CTDBPE000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
102	VEL3D	\N	\N	60	102	CE09OSPM-WF001-01-VEL3DK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
103	ADCPA	\N	\N	37	103	CE05MOAS-GL006-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
104	CAMDS	\N	\N	2	104	CE01ISSM-MFD00-00-CAMDSA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
105	FLORT	\N	\N	23	105	CE04OSHY-DP01B-04-FLORTA103	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
106	ZPLSC	\N	\N	25	106	CE04OSHY-PC01B-05-ZPLSCB102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
107	PHSEN	\N	\N	21	107	CE04OSBP-LJ01C-10-PHSEND107	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
108	NUTNR	\N	\N	28	108	CE04OSSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
109	ADCPA	\N	\N	33	109	CE05MOAS-GL002-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
110	FLORT	\N	\N	35	110	CE05MOAS-GL004-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
111	DOSTA	\N	\N	25	111	CE04OSHY-PC01B-4A-DOSTAD109	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
112	NUTNR	\N	\N	14	112	CE02SHSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
113	FLORT	\N	\N	14	113	CE02SHSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
114	METBK	\N	\N	67	114	CE09OSSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
115	VELPT	\N	\N	26	115	CE04OSHY-SF01B-4B-VELPTD106	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
116	PHSEN	\N	\N	11	116	CE02SHBP-LJ01D-10-PHSEND103	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
117	SPKIR	\N	\N	57	117	CE07SHSP-SP001-06-SPKIRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
118	DOSTA	\N	\N	41	118	CE06ISSM-MFD37-04-DOSTAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
119	DOSTA	\N	\N	35	119	CE05MOAS-GL004-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
120	NUTNR	\N	\N	57	120	CE07SHSP-SP001-05-NUTNRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
121	VELPT	\N	\N	57	121	CE07SHSP-SP001-02-VELPTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
122	PCO2A	\N	\N	53	122	CE07SHSM-SBD11-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
123	VELPT	\N	\N	67	123	CE09OSSM-SBD11-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
124	PHSEN	\N	\N	5	124	CE01ISSM-RID16-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
125	PRESF	\N	\N	3	125	CE01ISSM-MFD35-02-PRESFA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
126	MOPAK	\N	\N	6	126	CE01ISSM-SBD17-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
127	VELPT	\N	\N	19	127	CE02SHSP-SP001-02-VELPTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
128	METBK	\N	\N	15	128	CE02SHSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
129	CTDBP	\N	\N	52	129	CE07SHSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
130	DOSTA	\N	\N	23	130	CE04OSHY-DP01B-06-DOSTAD105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
131	SPKIR	\N	\N	66	131	CE09OSSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
132	PHSEN	\N	\N	63	132	CE09OSSM-MFD35-06-PHSEND000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
133	DOSTA	\N	\N	64	133	CE09OSSM-MFD37-04-DOSTAD000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
134	OPTAA	\N	\N	9	134	CE01ISSP-SP001-04-OPTAAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
135	OPTAA	\N	\N	11	135	CE02SHBP-LJ01D-08-OPTAAD106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
136	PRESF	\N	\N	49	136	CE07SHSM-MFD35-02-PRESFB000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
137	ADCPT	\N	\N	49	137	CE07SHSM-MFD35-04-ADCPTC000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
138	FLORT	\N	\N	28	138	CE04OSSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
139	DOFST	\N	\N	26	139	CE04OSHY-SF01B-2A-DOFSTA107	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
140	DOSTA	\N	\N	66	140	CE09OSSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
141	ACOMM	\N	\N	56	141	CE07SHSP-PL001-01-ACOMM0	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
142	OPTAA	\N	\N	26	142	CE04OSHY-SF01B-3B-OPTAAD105	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
143	CTDPF	\N	\N	60	143	CE09OSPM-WF001-03-CTDPFK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
144	CTDBP	\N	\N	11	144	CE02SHBP-LJ01D-06-CTDBPN106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
145	CAMDS	\N	\N	39	145	CE06ISSM-MFD00-00-CAMDSA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
146	CAMDS	\N	\N	12	146	CE02SHBP-MJ01C-08-CAMDSB107	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
147	CTDPF	\N	\N	23	147	CE04OSHY-DP01B-01-CTDPFL105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
148	ADCPS	\N	\N	21	148	CE04OSBP-LJ01C-05-ADCPSI103	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
149	ADCPT	\N	\N	11	149	CE02SHBP-LJ01D-05-ADCPTB104	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
150	PARAD	\N	\N	19	150	CE02SHSP-SP001-08-PARADJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
151	DOSTA	\N	\N	34	151	CE05MOAS-GL003-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
152	FLORT	\N	\N	46	152	CE06ISSP-SP001-08-FLORTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
153	CTDBP	\N	\N	66	153	CE09OSSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
154	OPTAA	\N	\N	52	154	CE07SHSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
155	DOSTA	\N	\N	4	155	CE01ISSM-MFD37-04-DOSTAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
156	SPKIR	\N	\N	5	156	CE01ISSM-RID16-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
157	PHSEN	\N	\N	26	157	CE04OSHY-SF01B-2B-PHSENA108	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
158	VEL3D	\N	\N	49	158	CE07SHSM-MFD35-01-VEL3DD000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
159	NUTNR	\N	\N	5	159	CE01ISSM-RID16-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
160	VELPT	\N	\N	54	160	CE07SHSM-SBD12-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
161	ACOMM	\N	\N	13	161	CE02SHSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
162	DOSTA	\N	\N	21	162	CE04OSBP-LJ01C-06-DOSTAD108	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
163	PHSEN	\N	\N	25	163	CE04OSHY-PC01B-4B-PHSENA106	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
164	FDCHP	\N	\N	16	164	CE02SHSM-SBD12-08-FDCHPA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
165	OPTAA	\N	\N	57	165	CE07SHSP-SP001-04-OPTAAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
166	PHSEN	\N	\N	51	166	CE07SHSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
167	NUTNR	\N	\N	52	167	CE07SHSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
168	PRESF	\N	\N	63	168	CE09OSSM-MFD35-02-PRESFC000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
169	VELPT	\N	\N	29	169	CE04OSSM-SBD11-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
170	PHSEN	\N	\N	13	170	CE02SHSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
171	PCO2A	\N	\N	16	171	CE02SHSM-SBD12-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
172	ADCPA	\N	\N	34	172	CE05MOAS-GL003-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
173	PARAD	\N	\N	26	173	CE04OSHY-SF01B-3C-PARADA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
174	FLORT	\N	\N	66	174	CE09OSSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
175	ZPLSC	\N	\N	12	175	CE02SHBP-MJ01C-07-ZPLSCB101	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
176	ZPLSC	\N	\N	48	176	CE07SHSM-MFD00-00-ZPLSCC000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
177	CTDBP	\N	\N	50	177	CE07SHSM-MFD37-03-CTDBPC000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
178	VEL3D	\N	\N	11	178	CE02SHBP-LJ01D-07-VEL3DC108	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
179	PARAD	\N	\N	35	179	CE05MOAS-GL004-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
180	PHSEN	\N	\N	65	180	CE09OSSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
181	OPTAA	\N	\N	19	181	CE02SHSP-SP001-04-OPTAAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
182	DOSTA	\N	\N	46	182	CE06ISSP-SP001-02-DOSTAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
183	PARAD	\N	\N	46	183	CE06ISSP-SP001-10-PARADJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
184	OPTAA	\N	\N	4	184	CE01ISSM-MFD37-01-OPTAAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
185	PARAD	\N	\N	32	185	CE05MOAS-GL001-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
186	CTDBP	\N	\N	4	186	CE01ISSM-MFD37-03-CTDBPC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
187	PCO2W	\N	\N	26	187	CE04OSHY-SF01B-4F-PCO2WA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
188	CTDGV	\N	\N	37	188	CE05MOAS-GL006-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
189	PARAD	\N	\N	60	189	CE09OSPM-WF001-05-PARADK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
190	CTDBP	\N	\N	14	190	CE02SHSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
191	ZPLSC	\N	\N	58	191	CE09OSSM-MFD37-00-ZPLSCC000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
192	DOSTA	\N	\N	50	192	CE07SHSM-MFD37-04-DOSTAD000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
193	CTDGV	\N	\N	36	193	CE05MOAS-GL005-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
194	CTDPF	\N	\N	9	194	CE01ISSP-SP001-09-CTDPFJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
195	CTDPF	\N	\N	25	195	CE04OSHY-PC01B-4A-CTDPFA109	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
196	DOSTA	\N	\N	42	196	CE06ISSM-RID16-03-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
197	CTDBP	\N	\N	41	197	CE06ISSM-MFD37-03-CTDBPC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
198	ADCPA	\N	\N	35	198	CE05MOAS-GL004-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
199	VEL3D	\N	\N	3	199	CE01ISSM-MFD35-01-VEL3DD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
200	OPTAA	\N	\N	64	200	CE09OSSM-MFD37-01-OPTAAC000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
201	FLORT	\N	\N	52	201	CE07SHSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
202	SPKIR	\N	\N	52	202	CE07SHSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
203	PCO2W	\N	\N	40	203	CE06ISSM-MFD35-05-PCO2WB000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
204	CTDBP	\N	\N	42	204	CE06ISSM-RID16-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
205	VELPT	\N	\N	6	205	CE01ISSM-SBD17-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
206	OPTAA	\N	\N	66	206	CE09OSSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
207	PARAD	\N	\N	57	207	CE07SHSP-SP001-09-PARADJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
208	SPKIR	\N	\N	14	208	CE02SHSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
209	NUTNR	\N	\N	46	209	CE06ISSP-SP001-06-NUTNRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
210	PHSEN	\N	\N	42	210	CE06ISSM-RID16-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
211	DOSTA	\N	\N	37	211	CE05MOAS-GL006-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
212	SPKIR	\N	\N	28	212	CE04OSSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
213	CTDGV	\N	\N	32	213	CE05MOAS-GL001-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
214	METBK	\N	\N	53	214	CE07SHSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
215	PCO2W	\N	\N	25	215	CE04OSHY-PC01B-4C-PCO2WA105	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
216	DOSTA	\N	\N	32	216	CE05MOAS-GL001-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
217	MOPAK	\N	\N	43	217	CE06ISSM-SBD17-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
218	DOSTA	\N	\N	36	218	CE05MOAS-GL005-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
219	PCO2W	\N	\N	49	219	CE07SHSM-MFD35-05-PCO2WB000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
220	FLORT	\N	\N	36	220	CE05MOAS-GL005-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
221	ADCPT	\N	\N	65	221	CE09OSSM-RID26-01-ADCPTC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
222	CTDGV	\N	\N	33	222	CE05MOAS-GL002-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
223	VELPT	\N	\N	42	223	CE06ISSM-RID16-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
224	DOSTA	\N	\N	14	224	CE02SHSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
225	PCO2W	\N	\N	5	225	CE01ISSM-RID16-05-PCO2WB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
226	PCO2A	\N	\N	30	226	CE04OSSM-SBD12-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
227	FLORT	\N	\N	5	227	CE01ISSM-RID16-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
228	VEL3D	\N	\N	63	228	CE09OSSM-MFD35-01-VEL3DD000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
229	ACOMM	\N	\N	45	229	CE06ISSP-PL001-01-ACOMM0	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
230	SPKIR	\N	\N	42	230	CE06ISSM-RID16-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
231	VEL3D	\N	\N	23	231	CE04OSHY-DP01B-02-VEL3DA105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
232	ADCPT	\N	\N	13	232	CE02SHSM-RID26-01-ADCPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
233	CAMDS	\N	\N	62	233	CE09OSSM-MFD00-00-CAMDSA000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
234	FLORD	\N	\N	84	234	GP05MOAS-PG002-02-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
235	ZPLSG	\N	\N	70	235	GP02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
236	DOSTA	\N	\N	73	236	GP02HYPM-WFP03-03-DOSTAL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
237	CTDMO	\N	\N	79	237	GP03FLMB-RIS02-06-CTDMOG	90	0101000020E6100000E3A59BC4200862C04C37894160FD4840
238	ACOMM	\N	\N	81	238	GP05MOAS-GL002-03-ACOMMM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
239	CTDGV	\N	\N	82	239	GP05MOAS-GL003-04-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
240	CTDMO	\N	\N	79	240	GP03FLMB-RIS02-04-CTDMOG	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
241	CTDMO	\N	\N	79	241	GP03FLMB-RIS02-03-CTDMOG	30	0101000020E6100000E3A59BC4200862C04C37894160FD4840
242	CTDMO	\N	\N	76	242	GP03FLMA-RIS02-08-CTDMOG	180	0101000020E6100000E3A59BC4200862C04C37894160FD4840
243	CTDMO	\N	\N	79	243	GP03FLMB-RIS02-08-CTDMOG	180	0101000020E6100000E3A59BC4200862C04C37894160FD4840
244	ACOMM	\N	\N	82	244	GP05MOAS-GL003-03-ACOMMM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
245	PARAD	\N	\N	84	245	GP05MOAS-PG002-04-PARADM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
246	DOSTA	\N	\N	78	246	GP03FLMB-RIS01-03-DOSTAD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
247	CTDMO	\N	\N	76	247	GP03FLMA-RIS02-07-CTDMOG	130	0101000020E6100000E3A59BC4200862C04C37894160FD4840
248	CTDPF	\N	\N	73	248	GP02HYPM-WFP03-04-CTDPFL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
249	NUTNR	\N	\N	83	249	GP05MOAS-PG001-03-NUTNRM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
250	DOSTA	\N	\N	83	250	GP05MOAS-PG001-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
251	CTDMO	\N	\N	76	251	GP03FLMA-RIS02-10-CTDMOG	350	0101000020E6100000E3A59BC4200862C04C37894160FD4840
252	CTDGV	\N	\N	83	252	GP05MOAS-PG001-01-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
253	CTDMO	\N	\N	76	253	GP03FLMA-RIS02-06-CTDMOG	90	0101000020E6100000E3A59BC4200862C04C37894160FD4840
254	VEL3D	\N	\N	73	254	GP02HYPM-WFP03-05-VEL3DL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
255	CTDMO	\N	\N	76	255	GP03FLMA-RIS02-14-CTDMOH	1500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
256	FLORT	\N	\N	78	256	GP03FLMB-RIS01-01-FLORTD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
257	CTDGV	\N	\N	84	257	GP05MOAS-PG002-01-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
258	CTDMO	\N	\N	76	258	GP03FLMA-RIS02-05-CTDMOG	60	0101000020E6100000E3A59BC4200862C04C37894160FD4840
259	ADCPS	\N	\N	79	259	GP03FLMB-RIS02-01-ADCPSL	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
260	DOSTA	\N	\N	81	260	GP05MOAS-GL002-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
261	CTDMO	\N	\N	71	261	GP02HYPM-RIS01-01-CTDMOG000	164	0101000020E6100000E3A59BC4200862C04C37894160FD4840
262	ACOMM	\N	\N	79	262	GP03FLMB-RIS02-02-ACOMM0	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
263	PHSEN	\N	\N	78	263	GP03FLMB-RIS01-02-PHSENE	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
264	CTDMO	\N	\N	76	264	GP03FLMA-RIS02-13-CTDMOH	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
265	FLORD	\N	\N	72	265	GP02HYPM-WFP02-01-FLORDL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
266	CTDMO	\N	\N	76	266	GP03FLMA-RIS02-11-CTDMOG	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
267	OPTAA	\N	\N	84	267	GP05MOAS-PG002-03-OPTAAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
268	ACOMM	\N	\N	80	268	GP05MOAS-GL001-03-ACOMMM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
269	CTDMO	\N	\N	79	269	GP03FLMB-RIS02-10-CTDMOG	350	0101000020E6100000E3A59BC4200862C04C37894160FD4840
270	DOSTA	\N	\N	80	270	GP05MOAS-GL001-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
271	CTDPF	\N	\N	72	271	GP02HYPM-WFP02-04-CTDPFL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
272	ACOMM	\N	\N	76	272	GP03FLMA-RIS02-02-ACOMM0	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
273	CTDMO	\N	\N	76	273	GP03FLMA-RIS02-12-CTDMOH	750	0101000020E6100000E3A59BC4200862C04C37894160FD4840
274	DOSTA	\N	\N	82	274	GP05MOAS-GL003-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
275	ADCPS	\N	\N	76	275	GP03FLMA-RIS02-01-ADCPSL	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
276	CTDMO	\N	\N	79	276	GP03FLMB-RIS02-09-CTDMOG	250	0101000020E6100000E3A59BC4200862C04C37894160FD4840
277	FLORT	\N	\N	75	277	GP03FLMA-RIS01-01-FLORTD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
278	DOSTA	\N	\N	75	278	GP03FLMA-RIS01-03-DOSTAD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
279	FLORD	\N	\N	73	279	GP02HYPM-WFP03-01-FLORDL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
280	CTDMO	\N	\N	76	280	GP03FLMA-RIS02-03-CTDMOG	30	0101000020E6100000E3A59BC4200862C04C37894160FD4840
281	CTDGV	\N	\N	80	281	GP05MOAS-GL001-04-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
282	CTDMO	\N	\N	76	282	GP03FLMA-RIS02-09-CTDMOG	250	0101000020E6100000E3A59BC4200862C04C37894160FD4840
283	DOSTA	\N	\N	72	283	GP02HYPM-WFP02-03-DOSTAL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
284	CTDGV	\N	\N	81	284	GP05MOAS-GL002-04-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
285	CTDMO	\N	\N	79	285	GP03FLMB-RIS02-13-CTDMOH	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
286	CTDMO	\N	\N	79	286	GP03FLMB-RIS02-14-CTDMOH	1500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
287	FLORD	\N	\N	81	287	GP05MOAS-GL002-01-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
288	FLORD	\N	\N	80	288	GP05MOAS-GL001-01-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
289	PHSEN	\N	\N	75	289	GP03FLMA-RIS01-02-PHSENE	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
290	CTDMO	\N	\N	79	290	GP03FLMB-RIS02-12-CTDMOH	750	0101000020E6100000E3A59BC4200862C04C37894160FD4840
291	CTDMO	\N	\N	79	291	GP03FLMB-RIS02-11-CTDMOG	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
292	CTDMO	\N	\N	79	292	GP03FLMB-RIS02-07-CTDMOG	130	0101000020E6100000E3A59BC4200862C04C37894160FD4840
293	CTDMO	\N	\N	79	293	GP03FLMB-RIS02-05-CTDMOG	60	0101000020E6100000E3A59BC4200862C04C37894160FD4840
294	FLORD	\N	\N	82	294	GP05MOAS-GL003-01-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
295	CTDMO	\N	\N	76	295	GP03FLMA-RIS02-04-CTDMOG	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
296	VEL3D	\N	\N	72	296	GP02HYPM-WFP02-05-VEL3DL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
297	PARAD	\N	\N	134	297	CP05MOAS-AV001-06-PARADN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
298	PRESF	\N	\N	114	298	CP03ISSM-MFD35-02-PRESFB000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
299	MOPAK	\N	\N	91	299	CP01CNSM-MFD35-04-VELPTA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
300	FLORT	\N	\N	137	300	CP05MOAS-GL002-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
301	DOFST	\N	\N	107	301	CP02PMUI-WFP01-02-DOFSTK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
302	CTDPF	\N	\N	103	302	CP02PMCO-WFP01-03-CTDPFK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
303	PARAD	\N	\N	135	303	CP05MOAS-AV002-06-PARADN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
304	CTDBP	\N	\N	131	304	CP04OSSM-RID27-03-CTDBPC000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
305	NUTNR	\N	\N	131	305	CP04OSSM-RID27-07-NUTNRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
306	METBK	\N	\N	92	306	CP01CNSM-SBD12-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
307	DOSTA	\N	\N	115	307	CP03ISSM-MFD37-04-DOSTAD000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
308	PARAD	\N	\N	136	308	CP05MOAS-GL001-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
309	ADCPT	\N	\N	97	309	CP02PMCI-RII01-02-ADCPTG000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
310	PCO2A	\N	\N	119	310	CP03ISSM-SBD12-04-PCO2AA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
311	VEL3D	\N	\N	99	311	CP02PMCI-WFP01-01-VEL3DK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
312	PHSEN	\N	\N	114	312	CP03ISSM-MFD35-06-PHSEND000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
313	DOSTA	\N	\N	139	313	CP05MOAS-GL004-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
314	PARAD	\N	\N	125	314	CP04OSPM-WFP01-05-PARADK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
315	OPTAA	\N	\N	122	315	CP03ISSP-SP001-02-OPTAAJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
316	SPKIR	\N	\N	117	316	CP03ISSM-RID27-08-SPKIRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
317	PARAD	\N	\N	122	317	CP03ISSP-SP001-10-PARADJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
318	MOPAK	\N	\N	118	318	CP03ISSM-SBD11-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
319	VELPT	\N	\N	95	319	CP01CNSP-SP001-05-VELPTJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
320	DOSTA	\N	\N	141	320	CP05MOAS-GL006-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
321	MOPAK	\N	\N	106	321	CP02PMUI-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
322	ADCPT	\N	\N	87	322	CP01CNSM-MFD35-01-ADCPTF000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
323	FLORT	\N	\N	139	323	CP05MOAS-GL004-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
324	OPTAA	\N	\N	88	324	CP01CNSM-MFD37-01-OPTAAD000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
325	PARAD	\N	\N	141	325	CP05MOAS-GL006-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
326	DOSTA	\N	\N	90	326	CP01CNSM-RID27-04-DOSTAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
327	ADCPA	\N	\N	140	327	CP05MOAS-GL005-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
328	DOFST	\N	\N	99	328	CP02PMCI-WFP01-02-DOFSTK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
329	PARAD	\N	\N	107	329	CP02PMUI-WFP01-05-PARADK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
330	ADCPA	\N	\N	139	330	CP05MOAS-GL004-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
331	PCO2A	\N	\N	133	331	CP04OSSM-SBD12-04-PCO2AA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
332	DOSTA	\N	\N	135	332	CP05MOAS-AV002-02-DOSTAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
333	CTDBP	\N	\N	90	333	CP01CNSM-RID27-03-CTDBPC000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
334	OPTAA	\N	\N	95	334	CP01CNSP-SP001-02-OPTAAJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
335	PARAD	\N	\N	99	335	CP02PMCI-WFP01-05-PARADK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
336	DOSTA	\N	\N	136	336	CP05MOAS-GL001-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
337	ZPLSC	\N	\N	113	337	CP03ISSM-MFD00-00-ZPLSCC000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
338	CTDGV	\N	\N	137	338	CP05MOAS-GL002-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
339	PCO2W	\N	\N	128	339	CP04OSSM-MFD35-05-PCO2WB000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
340	DOFST	\N	\N	111	340	CP02PMUO-WFP01-02-DOFSTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
341	CTDBP	\N	\N	88	341	CP01CNSM-MFD37-03-CTDBPD000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
342	ZPLSC	\N	\N	86	342	CP01CNSM-MFD00-00-ZPLSCC000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
343	PARAD	\N	\N	140	343	CP05MOAS-GL005-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
344	DOSTA	\N	\N	88	344	CP01CNSM-MFD37-04-DOSTAD000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
345	CTDGV	\N	\N	136	345	CP05MOAS-GL001-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
346	VEL3D	\N	\N	111	346	CP02PMUO-WFP01-01-VEL3DK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
347	DOSTA	\N	\N	137	347	CP05MOAS-GL002-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
348	PARAD	\N	\N	138	348	CP05MOAS-GL003-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
349	CTDPF	\N	\N	99	349	CP02PMCI-WFP01-03-CTDPFK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
350	CTDBP	\N	\N	115	350	CP03ISSM-MFD37-03-CTDBPD000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
351	VEL3D	\N	\N	125	351	CP04OSPM-WFP01-01-VEL3DK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
352	FLORT	\N	\N	90	352	CP01CNSM-RID27-02-FLORTD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
353	METBK	\N	\N	91	353	CP01CNSM-SBD11-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
354	PCO2W	\N	\N	87	354	CP01CNSM-MFD35-05-PCO2WB000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
355	VELPT	\N	\N	128	355	CP04OSSM-MFD35-04-VELPTB000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
356	FLORT	\N	\N	136	356	CP05MOAS-GL001-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
357	ZPLSC	\N	\N	127	357	CP04OSSM-MFD00-00-ZPLSCC000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
358	CTDAV	\N	\N	134	358	CP05MOAS-AV001-03-CTDAVN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
359	PCO2A	\N	\N	92	359	CP01CNSM-SBD12-04-PCO2AA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
360	FLORT	\N	\N	138	360	CP05MOAS-GL003-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
361	SPKIR	\N	\N	90	361	CP01CNSM-RID27-08-SPKIRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
362	FLORT	\N	\N	140	362	CP05MOAS-GL005-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
363	CTDPF	\N	\N	125	363	CP04OSPM-WFP01-03-CTDPFK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
364	PARAD	\N	\N	139	364	CP05MOAS-GL004-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
365	ACOMM	\N	\N	130	365	CP04OSSM-RID26-05-ACOMM0000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
366	PHSEN	\N	\N	87	366	CP01CNSM-MFD35-06-PHSEND000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
367	CTDGV	\N	\N	139	367	CP05MOAS-GL004-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
368	PHSEN	\N	\N	128	368	CP04OSSM-MFD35-06-PHSEND000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
369	DOSTA	\N	\N	129	369	CP04OSSM-MFD37-04-DOSTAD000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
370	SPKIR	\N	\N	131	370	CP04OSSM-RID27-08-SPKIRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
371	FLORT	\N	\N	122	371	CP03ISSP-SP001-09-FLORTJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
372	ADCPA	\N	\N	134	372	CP05MOAS-AV001-05-ADCPAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
373	ACOMM	\N	\N	89	373	CP01CNSM-RID26-05-ACOMM0000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
374	SPKIR	\N	\N	122	374	CP03ISSP-SP001-07-SPKIRJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
375	ADCPS	\N	\N	128	375	CP04OSSM-MFD35-01-ADCPSJ000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
376	PARAD	\N	\N	95	376	CP01CNSP-SP001-10-PARADJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
377	OPTAA	\N	\N	129	377	CP04OSSM-MFD37-01-OPTAAD000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
378	MOPAK	\N	\N	102	378	CP02PMCO-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
379	MOPAK	\N	\N	132	379	CP04OSSM-SBD11-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
380	CTDBP	\N	\N	129	380	CP04OSSM-MFD37-03-CTDBPE000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
381	VELPT	\N	\N	130	381	CP04OSSM-RID26-04-VELPTA000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
382	DOSTA	\N	\N	117	382	CP03ISSM-RID27-04-DOSTAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
383	CTDGV	\N	\N	140	383	CP05MOAS-GL005-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
384	MOPAK	\N	\N	110	384	CP02PMUO-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
385	NUTNR	\N	\N	90	385	CP01CNSM-RID27-07-NUTNRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
386	OPTAA	\N	\N	115	386	CP03ISSM-MFD37-01-OPTAAD000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
387	PRESF	\N	\N	128	387	CP04OSSM-MFD35-02-PRESFC000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
388	PARAD	\N	\N	111	388	CP02PMUO-WFP01-05-PARADK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
389	ACOMM	\N	\N	94	389	CP01CNSP-PL001-01-ACOMM0	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
390	NUTNR	\N	\N	95	390	CP01CNSP-SP001-03-NUTNRJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
391	ADCPT	\N	\N	114	391	CP03ISSM-MFD35-01-ADCPTF000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
392	VEL3D	\N	\N	107	392	CP02PMUI-WFP01-01-VEL3DK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
393	DOSTA	\N	\N	140	393	CP05MOAS-GL005-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
394	VELPT	\N	\N	89	394	CP01CNSM-RID26-04-VELPTA000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
395	FLORT	\N	\N	103	395	CP02PMCO-WFP01-04-FLORTK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
396	PCO2W	\N	\N	114	396	CP03ISSM-MFD35-05-PCO2WB000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
397	PHSEN	\N	\N	130	397	CP04OSSM-RID26-06-PHSEND000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
398	ADCPA	\N	\N	135	398	CP05MOAS-AV002-05-ADCPAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
399	CTDAV	\N	\N	135	399	CP05MOAS-AV002-03-CTDAVN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
400	FLORT	\N	\N	117	400	CP03ISSM-RID27-02-FLORTD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
401	FLORT	\N	\N	131	401	CP04OSSM-RID27-02-FLORTD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
402	CTDPF	\N	\N	122	402	CP03ISSP-SP001-08-CTDPFJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
403	DOFST	\N	\N	125	403	CP04OSPM-WFP01-02-DOFSTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
404	PARAD	\N	\N	103	404	CP02PMCO-WFP01-05-PARADK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
405	DOSTA	\N	\N	122	405	CP03ISSP-SP001-06-DOSTAJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
406	ADCPT	\N	\N	105	406	CP02PMUI-RII01-02-ADCPTG000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
407	FLORT	\N	\N	111	407	CP02PMUO-WFP01-04-FLORTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
408	CTDGV	\N	\N	141	408	CP05MOAS-GL006-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
409	FLORT	\N	\N	95	409	CP01CNSP-SP001-09-FLORTJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
410	FLORT	\N	\N	134	410	CP05MOAS-AV001-01-FLORTN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
411	FDCHP	\N	\N	92	411	CP01CNSM-SBD12-08-FDCHPA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
412	NUTNR	\N	\N	134	412	CP05MOAS-AV001-04-NUTNRN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
413	ADCPA	\N	\N	138	413	CP05MOAS-GL003-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
414	DOFST	\N	\N	103	414	CP02PMCO-WFP01-02-DOFSTK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
415	OPTAA	\N	\N	131	415	CP04OSSM-RID27-01-OPTAAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
416	FLORT	\N	\N	135	416	CP05MOAS-AV002-01-FLORTN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
417	ADCPA	\N	\N	141	417	CP05MOAS-GL006-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
418	PHSEN	\N	\N	116	418	CP03ISSM-RID26-06-PHSEND000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
419	NUTNR	\N	\N	117	419	CP03ISSM-RID27-07-NUTNRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
420	WAVSS	\N	\N	92	420	CP01CNSM-SBD12-05-WAVSSA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
421	DOSTA	\N	\N	95	421	CP01CNSP-SP001-06-DOSTAJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
422	METBK	\N	\N	132	422	CP04OSSM-SBD11-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
423	DOSTA	\N	\N	134	423	CP05MOAS-AV001-02-DOSTAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
424	VELPT	\N	\N	116	424	CP03ISSM-RID26-04-VELPTA000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
425	FLORT	\N	\N	99	425	CP02PMCI-WFP01-04-FLORTK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
426	OPTAA	\N	\N	90	426	CP01CNSM-RID27-01-OPTAAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
427	PARAD	\N	\N	137	427	CP05MOAS-GL002-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
428	MOPAK	\N	\N	124	428	CP04OSPM-SBS11-02-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
429	CTDPF	\N	\N	95	429	CP01CNSP-SP001-08-CTDPFJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
430	FLORT	\N	\N	141	430	CP05MOAS-GL006-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
431	CTDGV	\N	\N	138	431	CP05MOAS-GL003-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
432	MOPAK	\N	\N	98	432	CP02PMCI-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
433	VELPT	\N	\N	114	433	CP03ISSM-MFD35-04-VELPTA000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
434	METBK	\N	\N	118	434	CP03ISSM-SBD11-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
435	ADCPT	\N	\N	101	435	CP02PMCO-RII01-02-ADCPTG000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
436	ADCPA	\N	\N	137	436	CP05MOAS-GL002-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
437	CTDBP	\N	\N	117	437	CP03ISSM-RID27-03-CTDBPC000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
438	ADCPS	\N	\N	109	438	CP02PMUO-RII01-02-ADCPSL000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
439	PHSEN	\N	\N	89	439	CP01CNSM-RID26-06-PHSEND000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
440	FLORT	\N	\N	125	440	CP04OSPM-WFP01-04-FLORTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
441	NUTNR	\N	\N	135	441	CP05MOAS-AV002-04-NUTNRN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
442	ACOMM	\N	\N	116	442	CP03ISSM-RID26-05-ACOMM0000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
443	VEL3D	\N	\N	103	443	CP02PMCO-WFP01-01-VEL3DK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
444	VELPT	\N	\N	122	444	CP03ISSP-SP001-05-VELPTJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
445	ADCPA	\N	\N	136	445	CP05MOAS-GL001-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
446	SPKIR	\N	\N	95	446	CP01CNSP-SP001-07-SPKIRJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
447	FLORT	\N	\N	107	447	CP02PMUI-WFP01-04-FLORTK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
448	ACOMM	\N	\N	121	448	CP03ISSP-PL001-01-ACOMM0	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
449	CTDPF	\N	\N	111	449	CP02PMUO-WFP01-03-CTDPFK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
450	PRESF	\N	\N	87	450	CP01CNSM-MFD35-02-PRESFB000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
451	DOSTA	\N	\N	131	451	CP04OSSM-RID27-04-DOSTAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
452	OPTAA	\N	\N	117	452	CP03ISSM-RID27-01-OPTAAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
453	DOSTA	\N	\N	138	453	CP05MOAS-GL003-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
454	CTDPF	\N	\N	107	454	CP02PMUI-WFP01-03-CTDPFK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
455	NUTNR	\N	\N	122	455	CP03ISSP-SP001-03-NUTNRJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
456	CTDMO	\N	\N	157	456	GA03FLMB-RIS02-13-CTDMOH	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
457	DOSTA	\N	\N	160	457	GA05MOAS-GL003-02-DOSTAM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
458	CTDMO	\N	\N	157	458	GA03FLMB-RIS02-08-CTDMOG	180	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
459	DOSTA	\N	\N	158	459	GA05MOAS-GL001-02-DOSTAM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
460	CTDMO	\N	\N	154	460	GA03FLMA-RIS02-07-CTDMOG	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
461	PHSEN	\N	\N	156	461	GA03FLMB-RIS01-02-PHSENE	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
462	PHSEN	\N	\N	153	462	GA03FLMA-RIS01-02-PHSENE	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
463	CTDMO	\N	\N	143	463	GA01SUMO-RII11-02-CTDMOR015	1500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
464	CTDMO	\N	\N	143	464	GA01SUMO-RII11-02-CTDMOR014	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
465	CTDMO	\N	\N	143	465	GA01SUMO-RII11-02-CTDMOR013	750	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
466	MOPAK	\N	\N	144	466	GA01SUMO-SBD11-01-MOPAK0000	0	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
467	CTDMO	\N	\N	157	467	GA03FLMB-RIS02-07-CTDMOG	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
468	METBK	\N	\N	144	468	GA01SUMO-SBD11-06-METBKA000	5	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
469	CTDBP	\N	\N	143	469	GA01SUMO-RII11-02-CTDBPP201	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
470	FLORD	\N	\N	143	470	GA01SUMO-RII11-02-FLORDG203	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
471	DOSTA	\N	\N	144	471	GA01SUMO-SBD11-04-DOSTAD000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
472	DOSTA	\N	\N	143	472	GA01SUMO-RII11-02-DOSTAD302	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
473	PCO2W	\N	\N	143	473	GA01SUMO-RII11-02-PCO2WC104	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
474	CTDMO	\N	\N	157	474	GA03FLMB-RIS02-06-CTDMOG	90	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
475	PCO2A	\N	\N	145	475	GA01SUMO-SBD12-04-PCO2AA000	0	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
476	CTDBP	\N	\N	142	476	GA01SUMO-RID16-03-CTDBPF000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
477	CTDMO	\N	\N	154	477	GA03FLMA-RIS02-12-CTDMOH	750	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
478	CTDMO	\N	\N	157	478	GA03FLMB-RIS02-11-CTDMOG	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
479	METBK	\N	\N	145	479	GA01SUMO-SBD12-06-METBKA000	5	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
480	FLORT	\N	\N	145	480	GA01SUMO-SBD12-02-FLORTD000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
481	ZPLSG	\N	\N	148	481	GA02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
482	VEL3D	\N	\N	150	482	GA02HYPM-WFP02-05-VEL3DL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
483	SPKIR	\N	\N	142	483	GA01SUMO-RID16-08-SPKIRB000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
484	FLORD	\N	\N	143	484	GA01SUMO-RII11-02-FLORDG103	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
485	CTDMO	\N	\N	157	485	GA03FLMB-RIS02-12-CTDMOH	750	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
486	CTDGV	\N	\N	162	486	GA05MOAS-PG002-01-CTDGVM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
487	CTDMO	\N	\N	154	487	GA03FLMA-RIS02-09-CTDMOG	250	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
488	SPKIR	\N	\N	144	488	GA01SUMO-SBD11-05-SPKIRB000	5	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
489	DOSTA	\N	\N	156	489	GA03FLMB-RIS01-03-DOSTAD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
490	PARAD	\N	\N	162	490	GA05MOAS-PG002-04-PARADM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
491	CTDMO	\N	\N	154	491	GA03FLMA-RIS02-04-CTDMOG	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
492	NUTNR	\N	\N	161	492	GA05MOAS-PG001-03-NUTNRM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
493	ACOMM	\N	\N	160	493	GA05MOAS-GL003-03-ACOMMM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
494	VEL3D	\N	\N	151	494	GA02HYPM-WFP03-05-VEL3DL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
495	ADCPS	\N	\N	143	495	GA01SUMO-RII11-02-ADCPSN011	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
496	DOSTA	\N	\N	153	496	GA03FLMA-RIS01-03-DOSTAD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
497	ADCPS	\N	\N	154	497	GA03FLMA-RIS02-01-ADCPSL	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
498	CTDGV	\N	\N	161	498	GA05MOAS-PG001-01-CTDGVM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
499	FLORD	\N	\N	151	499	GA02HYPM-WFP03-01-FLORDL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
500	CTDMO	\N	\N	143	500	GA01SUMO-RII11-02-CTDMOQ001	20	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
501	CTDMO	\N	\N	143	501	GA01SUMO-RII11-02-CTDMOQ005	100	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
502	CTDMO	\N	\N	143	502	GA01SUMO-RII11-02-CTDMOQ004	60	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
503	CTDMO	\N	\N	157	503	GA03FLMB-RIS02-14-CTDMOH	1500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
504	CTDMO	\N	\N	154	504	GA03FLMA-RIS02-14-CTDMOH	1500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
505	CTDMO	\N	\N	143	505	GA01SUMO-RII11-02-CTDMOQ008	180	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
506	CTDMO	\N	\N	149	506	GA02HYPM-RIS01-01-CTDMOG000	164	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
507	ACOMM	\N	\N	142	507	GA01SUMO-RID16-00-ACOMM0000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
508	FLORD	\N	\N	162	508	GA05MOAS-PG002-02-FLORDM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
509	NUTNR	\N	\N	142	509	GA01SUMO-RID16-07-NUTNRB000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
510	CTDPF	\N	\N	151	510	GA02HYPM-WFP03-04-CTDPFL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
511	OPTAA	\N	\N	142	511	GA01SUMO-RID16-01-OPTAAD000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
512	CTDMO	\N	\N	154	512	GA03FLMA-RIS02-10-CTDMOG	350	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
513	CTDMO	\N	\N	154	513	GA03FLMA-RIS02-05-CTDMOG	60	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
514	CTDMO	\N	\N	157	514	GA03FLMB-RIS02-09-CTDMOG	250	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
515	DOSTA	\N	\N	161	515	GA05MOAS-PG001-02-DOSTAM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
516	CTDMO	\N	\N	143	516	GA01SUMO-RII11-02-CTDMOQ010	350	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
517	CTDMO	\N	\N	143	517	GA01SUMO-RII11-02-CTDMOQ012	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
518	OPTAA	\N	\N	145	518	GA01SUMO-SBD12-01-OPTAAD000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
519	DOSTA	\N	\N	159	519	GA05MOAS-GL002-02-DOSTAM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
520	DOSTA	\N	\N	143	520	GA01SUMO-RII11-02-DOSTAD102	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
521	FLORD	\N	\N	160	521	GA05MOAS-GL003-01-FLORDM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
522	FLORT	\N	\N	153	522	GA03FLMA-RIS01-01-FLORTD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
523	CTDMO	\N	\N	154	523	GA03FLMA-RIS02-08-CTDMOG	180	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
524	CTDMO	\N	\N	154	524	GA03FLMA-RIS02-06-CTDMOG	90	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
525	ACOMM	\N	\N	159	525	GA05MOAS-GL002-03-ACOMMM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
526	CTDGV	\N	\N	160	526	GA05MOAS-GL003-04-CTDGVM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
527	FLORD	\N	\N	150	527	GA02HYPM-WFP02-01-FLORDL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
528	PCO2W	\N	\N	143	528	GA01SUMO-RII11-02-PCO2WC304	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
529	PHSEN	\N	\N	143	529	GA01SUMO-RII11-02-PHSENE002	20	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
530	PHSEN	\N	\N	143	530	GA01SUMO-RII11-02-PHSENE006	100	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
531	CTDMO	\N	\N	154	531	GA03FLMA-RIS02-03-CTDMOG	30	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
532	ACOMM	\N	\N	157	532	GA03FLMB-RIS02-02-ACOMM0	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
533	CTDBP	\N	\N	143	533	GA01SUMO-RII11-02-CTDBPP003	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
534	CTDMO	\N	\N	157	534	GA03FLMB-RIS02-10-CTDMOG	350	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
535	VELPT	\N	\N	142	535	GA01SUMO-RID16-04-VELPTA000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
536	DOSTA	\N	\N	150	536	GA02HYPM-WFP02-03-DOSTAL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
537	PCO2W	\N	\N	142	537	GA01SUMO-RID16-05-PCO2WB000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
538	CTDPF	\N	\N	150	538	GA02HYPM-WFP02-04-CTDPFL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
539	CTDMO	\N	\N	157	539	GA03FLMB-RIS02-04-CTDMOG	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
540	FLORD	\N	\N	159	540	GA05MOAS-GL002-01-FLORDM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
541	OPTAA	\N	\N	162	541	GA05MOAS-PG002-03-OPTAAM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
542	CTDMO	\N	\N	157	542	GA03FLMB-RIS02-05-CTDMOG	60	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
543	FLORD	\N	\N	158	543	GA05MOAS-GL001-01-FLORDM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
544	CTDMO	\N	\N	154	544	GA03FLMA-RIS02-13-CTDMOH	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
545	DOSTA	\N	\N	142	545	GA01SUMO-RID16-03-DOSTAD000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
546	ADCPS	\N	\N	157	546	GA03FLMB-RIS02-01-ADCPSL	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
547	CTDMO	\N	\N	154	547	GA03FLMA-RIS02-11-CTDMOG	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
548	CTDMO	\N	\N	157	548	GA03FLMB-RIS02-03-CTDMOG	30	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
549	DOSTA	\N	\N	151	549	GA02HYPM-WFP03-03-DOSTAL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
550	DOSTA	\N	\N	143	550	GA01SUMO-RII11-02-DOSTAD202	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
551	NUTNR	\N	\N	144	551	GA01SUMO-SBD11-08-NUTNRB000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
552	CTDGV	\N	\N	158	552	GA05MOAS-GL001-04-CTDGVM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
553	FLORT	\N	\N	156	553	GA03FLMB-RIS01-01-FLORTD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
554	CTDMO	\N	\N	143	554	GA01SUMO-RII11-02-CTDMOQ009	250	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
555	ACOMM	\N	\N	154	555	GA03FLMA-RIS02-02-ACOMM0	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
556	WAVSS	\N	\N	145	556	GA01SUMO-SBD12-05-WAVSSA000	0	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
557	FLORT	\N	\N	142	557	GA01SUMO-RID16-02-FLORTD000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
558	CTDBP	\N	\N	143	558	GA01SUMO-RII11-02-CTDBPP007	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
559	PCO2W	\N	\N	143	559	GA01SUMO-RII11-02-PCO2WC204	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
560	ACOMM	\N	\N	158	560	GA05MOAS-GL001-03-ACOMMM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
561	FLORD	\N	\N	143	561	GA01SUMO-RII11-02-FLORDG303	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
562	CTDGV	\N	\N	159	562	GA05MOAS-GL002-04-CTDGVM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
563	DOSTA	\N	\N	173	563	GI03FLMA-RIS01-03-DOSTAD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
564	PCO2W	\N	\N	164	564	GI01SUMO-RII11-02-PCO2WC304	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
565	METBK	\N	\N	166	565	GI01SUMO-SBD12-06-METBKA000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
566	CTDMO	\N	\N	177	566	GI03FLMB-RIS02-10-CTDMOG	350	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
567	VELPT	\N	\N	163	567	GI01SUMO-RID16-04-VELPTA000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
568	FLORD	\N	\N	178	568	GI05MOAS-GL001-01-FLORDM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
569	VELPT	\N	\N	174	569	GI03FLMA-RIS02-21-VELPTB	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
570	CTDMO	\N	\N	177	570	GI03FLMB-RIS02-11-CTDMOG	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
571	PHSEN	\N	\N	164	571	GI01SUMO-RII11-02-PHSENE002	20	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
572	PHSEN	\N	\N	164	572	GI01SUMO-RII11-02-PHSENE006	100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
573	DOSTA	\N	\N	165	573	GI01SUMO-SBD11-04-DOSTAD000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
574	SPKIR	\N	\N	165	574	GI01SUMO-SBD11-05-SPKIRB000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
575	CTDGV	\N	\N	181	575	GI05MOAS-PG001-01-CTDGVM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
576	VELPT	\N	\N	177	576	GI03FLMB-RIS02-20-VELPTB	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
577	CTDGV	\N	\N	180	577	GI05MOAS-GL003-04-CTDGVM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
578	FLORD	\N	\N	164	578	GI01SUMO-RII11-02-FLORDG203	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
579	DOSTA	\N	\N	164	579	GI01SUMO-RII11-02-DOSTAD302	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
580	FLORD	\N	\N	180	580	GI05MOAS-GL003-01-FLORDM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
581	SPKIR	\N	\N	163	581	GI01SUMO-RID16-08-SPKIRB000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
582	DOSTA	\N	\N	179	582	GI05MOAS-GL002-02-DOSTAM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
583	ACOMM	\N	\N	179	583	GI05MOAS-GL002-03-ACOMMM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
584	CTDMO	\N	\N	177	584	GI03FLMB-RIS02-14-CTDMOH	1500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
585	CTDGV	\N	\N	178	585	GI05MOAS-GL001-04-CTDGVM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
586	NUTNR	\N	\N	163	586	GI01SUMO-RID16-07-NUTNRB000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
587	VELPT	\N	\N	177	587	GI03FLMB-RIS02-21-VELPTB	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
588	CTDMO	\N	\N	174	588	GI03FLMA-RIS02-18-CTDMOH	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
589	VELPT	\N	\N	177	589	GI03FLMB-RIS02-22-VELPTB	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
590	DOSTA	\N	\N	178	590	GI05MOAS-GL001-02-DOSTAM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
591	CTDBP	\N	\N	164	591	GI01SUMO-RII11-02-CTDBPP007	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
592	CTDBP	\N	\N	164	592	GI01SUMO-RII11-02-CTDBPP003	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
593	CTDMO	\N	\N	174	593	GI03FLMA-RIS02-03-CTDMOG	30	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
594	CTDGV	\N	\N	179	594	GI05MOAS-GL002-04-CTDGVM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
595	PCO2W	\N	\N	164	595	GI01SUMO-RII11-02-PCO2WC104	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
596	FLORD	\N	\N	164	596	GI01SUMO-RII11-02-FLORDG103	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
597	FLORD	\N	\N	164	597	GI01SUMO-RII11-02-FLORDG303	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
598	ACOMM	\N	\N	177	598	GI03FLMB-RIS02-02-ACOMM0	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
599	CTDMO	\N	\N	174	599	GI03FLMA-RIS02-04-CTDMOG	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
600	ACOMM	\N	\N	163	600	GI01SUMO-RID16-00-ACOMM0000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
601	PCO2W	\N	\N	164	601	GI01SUMO-RII11-02-PCO2WC204	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
602	VELPT	\N	\N	177	602	GI03FLMB-RIS02-19-VELPTB	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
603	CTDMO	\N	\N	174	603	GI03FLMA-RIS02-05-CTDMOG	60	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
604	CTDMO	\N	\N	164	604	GI01SUMO-RII11-02-CTDMOR015	1500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
605	CTDMO	\N	\N	164	605	GI01SUMO-RII11-02-CTDMOR014	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
606	CTDMO	\N	\N	174	606	GI03FLMA-RIS02-16-CTDMOH	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
607	PCO2A	\N	\N	166	607	GI01SUMO-SBD12-04-PCO2AA000	0	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
608	CTDMO	\N	\N	164	608	GI01SUMO-RII11-02-CTDMOR013	750	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
609	VEL3D	\N	\N	171	609	GI02HYPM-WFP02-05-VEL3DL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
610	CTDMO	\N	\N	177	610	GI03FLMB-RIS02-17-CTDMOH	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
611	PHSEN	\N	\N	176	611	GI03FLMB-RIS01-02-PHSENE	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
612	CTDMO	\N	\N	174	612	GI03FLMA-RIS02-09-CTDMOG	250	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
613	FDCHP	\N	\N	166	613	GI01SUMO-SBD12-08-FDCHPA000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
614	CTDMO	\N	\N	177	614	GI03FLMB-RIS02-16-CTDMOH	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
615	NUTNR	\N	\N	181	615	GI05MOAS-PG001-03-NUTNRM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
616	OPTAA	\N	\N	182	616	GI05MOAS-PG002-03-OPTAAM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
617	PCO2W	\N	\N	163	617	GI01SUMO-RID16-05-PCO2WB000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
618	METBK	\N	\N	165	618	GI01SUMO-SBD11-06-METBKA000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
619	CTDPF	\N	\N	171	619	GI02HYPM-WFP02-04-CTDPFL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
620	VELPT	\N	\N	174	620	GI03FLMA-RIS02-20-VELPTB	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
621	CTDMO	\N	\N	174	621	GI03FLMA-RIS02-12-CTDMOH	750	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
622	DOSTA	\N	\N	164	622	GI01SUMO-RII11-02-DOSTAD102	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
623	CTDMO	\N	\N	174	623	GI03FLMA-RIS02-13-CTDMOH	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
624	ACOMM	\N	\N	178	624	GI05MOAS-GL001-03-ACOMMM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
625	ADCPS	\N	\N	177	625	GI03FLMB-RIS02-01-ADCPSL	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
626	CTDMO	\N	\N	177	626	GI03FLMB-RIS02-04-CTDMOG	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
627	CTDMO	\N	\N	174	627	GI03FLMA-RIS02-08-CTDMOG	180	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
628	CTDMO	\N	\N	170	628	GI02HYPM-RIS01-01-CTDMOG000	164	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
629	CTDMO	\N	\N	174	629	GI03FLMA-RIS02-15-CTDMOH	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
630	OPTAA	\N	\N	163	630	GI01SUMO-RID16-01-OPTAAD000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
631	DOSTA	\N	\N	180	631	GI05MOAS-GL003-02-DOSTAM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
632	NUTNR	\N	\N	165	632	GI01SUMO-SBD11-08-NUTNRB000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
633	CTDMO	\N	\N	174	633	GI03FLMA-RIS02-14-CTDMOH	1500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
634	DOSTA	\N	\N	181	634	GI05MOAS-PG001-02-DOSTAM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
635	PHSEN	\N	\N	173	635	GI03FLMA-RIS01-02-PHSENE	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
636	CTDMO	\N	\N	177	636	GI03FLMB-RIS02-03-CTDMOG	30	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
637	ACOMM	\N	\N	180	637	GI05MOAS-GL003-03-ACOMMM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
638	CTDMO	\N	\N	177	638	GI03FLMB-RIS02-18-CTDMOH	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
639	DOSTA	\N	\N	171	639	GI02HYPM-WFP02-03-DOSTAL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
640	CTDMO	\N	\N	174	640	GI03FLMA-RIS02-17-CTDMOH	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
641	CTDBP	\N	\N	164	641	GI01SUMO-RII11-02-CTDBPP201	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
642	FLORT	\N	\N	163	642	GI01SUMO-RID16-02-FLORTD000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
643	FLORT	\N	\N	166	643	GI01SUMO-SBD12-02-FLORTD000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
644	ZPLSG	\N	\N	169	644	GI02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
645	OPTAA	\N	\N	166	645	GI01SUMO-SBD12-01-OPTAAD000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
646	CTDMO	\N	\N	177	646	GI03FLMB-RIS02-15-CTDMOH	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
647	WAVSS	\N	\N	166	647	GI01SUMO-SBD12-05-WAVSSA000	0	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
648	CTDMO	\N	\N	177	648	GI03FLMB-RIS02-12-CTDMOH	750	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
649	CTDMO	\N	\N	177	649	GI03FLMB-RIS02-13-CTDMOH	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
650	CTDMO	\N	\N	177	650	GI03FLMB-RIS02-09-CTDMOG	250	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
651	CTDGV	\N	\N	182	651	GI05MOAS-PG002-01-CTDGVM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
652	CTDMO	\N	\N	177	652	GI03FLMB-RIS02-07-CTDMOG	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
653	CTDMO	\N	\N	164	653	GI01SUMO-RII11-02-CTDMOQ009	250	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
654	CTDMO	\N	\N	164	654	GI01SUMO-RII11-02-CTDMOQ008	180	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
655	CTDBP	\N	\N	163	655	GI01SUMO-RID16-03-CTDBPF000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
656	CTDMO	\N	\N	164	656	GI01SUMO-RII11-02-CTDMOQ001	20	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
657	CTDMO	\N	\N	164	657	GI01SUMO-RII11-02-CTDMOQ005	100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
658	CTDMO	\N	\N	164	658	GI01SUMO-RII11-02-CTDMOQ004	60	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
659	DOSTA	\N	\N	164	659	GI01SUMO-RII11-02-DOSTAD202	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
660	CTDMO	\N	\N	177	660	GI03FLMB-RIS02-06-CTDMOG	90	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
661	CTDMO	\N	\N	177	661	GI03FLMB-RIS02-05-CTDMOG	60	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
662	CTDMO	\N	\N	174	662	GI03FLMA-RIS02-11-CTDMOG	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
663	ADCPS	\N	\N	164	663	GI01SUMO-RII11-02-ADCPSN011	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
664	CTDMO	\N	\N	177	664	GI03FLMB-RIS02-08-CTDMOG	180	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
665	FLORD	\N	\N	171	665	GI02HYPM-WFP02-01-FLORDL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
666	FLORD	\N	\N	182	666	GI05MOAS-PG002-02-FLORDM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
667	ADCPS	\N	\N	174	667	GI03FLMA-RIS02-01-ADCPSL	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
668	ACOMM	\N	\N	174	668	GI03FLMA-RIS02-02-ACOMM0	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
669	CTDMO	\N	\N	174	669	GI03FLMA-RIS02-06-CTDMOG	90	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
670	CTDMO	\N	\N	174	670	GI03FLMA-RIS02-07-CTDMOG	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
671	FLORT	\N	\N	176	671	GI03FLMB-RIS01-01-FLORTD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
672	VELPT	\N	\N	174	672	GI03FLMA-RIS02-22-VELPTB	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
673	VELPT	\N	\N	174	673	GI03FLMA-RIS02-19-VELPTB	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
674	DOSTA	\N	\N	176	674	GI03FLMB-RIS01-03-DOSTAD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
675	FLORT	\N	\N	173	675	GI03FLMA-RIS01-01-FLORTD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
676	DOSTA	\N	\N	163	676	GI01SUMO-RID16-03-DOSTAD000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
677	CTDMO	\N	\N	164	677	GI01SUMO-RII11-02-CTDMOQ010	350	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
678	CTDMO	\N	\N	164	678	GI01SUMO-RII11-02-CTDMOQ012	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
679	FLORD	\N	\N	179	679	GI05MOAS-GL002-01-FLORDM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
680	CTDMO	\N	\N	174	680	GI03FLMA-RIS02-10-CTDMOG	350	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
681	MOPAK	\N	\N	165	681	GI01SUMO-SBD11-01-MOPAK0000	0	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
682	PARAD	\N	\N	182	682	GI05MOAS-PG002-04-PARADM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
683	CTDMO	\N	\N	198	683	GS03FLMB-RIS02-11-CTDMOG	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
684	FLORT	\N	\N	183	684	GS01SUMO-RID16-02-FLORTD000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
685	CTDMO	\N	\N	198	685	GS03FLMB-RIS02-10-CTDMOG	350	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
686	OPTAA	\N	\N	203	686	GS05MOAS-PG002-03-OPTAAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
687	FLORD	\N	\N	184	687	GS01SUMO-RII11-02-FLORDG303	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
688	FLORT	\N	\N	186	688	GS01SUMO-SBD12-02-FLORTD000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
689	DOSTA	\N	\N	184	689	GS01SUMO-RII11-02-DOSTAD302	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
690	CTDBP	\N	\N	184	690	GS01SUMO-RII11-02-CTDBPP003	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
691	ADCPS	\N	\N	184	691	GS01SUMO-RII11-02-ADCPSN011	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
692	PHSEN	\N	\N	197	692	GS03FLMB-RIS01-02-PHSENE	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
693	FLORD	\N	\N	191	693	GS02HYPM-WFP02-01-FLORDL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
694	ADCPS	\N	\N	195	694	GS03FLMA-RIS02-01-ADCPSL	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
695	ACOMM	\N	\N	199	695	GS05MOAS-GL001-03-ACOMMM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
696	WAVSS	\N	\N	186	696	GS01SUMO-SBD12-05-WAVSSA000	0	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
697	CTDMO	\N	\N	198	697	GS03FLMB-RIS02-03-CTDMOG	30	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
698	OPTAA	\N	\N	186	698	GS01SUMO-SBD12-01-OPTAAD000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
699	ACOMM	\N	\N	201	699	GS05MOAS-GL003-03-ACOMMM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
700	VEL3D	\N	\N	192	700	GS02HYPM-WFP03-05-VEL3DL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
701	CTDMO	\N	\N	195	701	GS03FLMA-RIS02-05-CTDMOG	60	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
702	SPKIR	\N	\N	183	702	GS01SUMO-RID16-08-SPKIRB000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
703	PCO2A	\N	\N	186	703	GS01SUMO-SBD12-04-PCO2AA000	0	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
704	CTDMO	\N	\N	195	704	GS03FLMA-RIS02-07-CTDMOG	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
705	CTDPF	\N	\N	191	705	GS02HYPM-WFP02-04-CTDPFL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
706	CTDMO	\N	\N	198	706	GS03FLMB-RIS02-06-CTDMOG	90	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
707	CTDMO	\N	\N	190	707	GS02HYPM-RIS01-01-CTDMOG000	164	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
708	ZPLSG	\N	\N	189	708	GS02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
709	NUTNR	\N	\N	202	709	GS05MOAS-PG001-03-NUTNRM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
710	NUTNR	\N	\N	185	710	GS01SUMO-SBD11-08-NUTNRB000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
711	CTDMO	\N	\N	195	711	GS03FLMA-RIS02-11-CTDMOG	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
712	CTDMO	\N	\N	195	712	GS03FLMA-RIS02-10-CTDMOG	350	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
713	CTDMO	\N	\N	184	713	GS01SUMO-RII11-02-CTDMOQ009	250	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
714	CTDMO	\N	\N	184	714	GS01SUMO-RII11-02-CTDMOQ008	180	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
715	CTDMO	\N	\N	184	715	GS01SUMO-RII11-02-CTDMOQ005	100	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
716	CTDMO	\N	\N	184	716	GS01SUMO-RII11-02-CTDMOQ004	60	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
717	CTDMO	\N	\N	198	717	GS03FLMB-RIS02-13-CTDMOH	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
718	CTDMO	\N	\N	184	718	GS01SUMO-RII11-02-CTDMOQ001	20	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
719	METBK	\N	\N	185	719	GS01SUMO-SBD11-06-METBKA000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
720	METBK	\N	\N	186	720	GS01SUMO-SBD12-06-METBKA000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
721	CTDMO	\N	\N	198	721	GS03FLMB-RIS02-12-CTDMOH	750	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
722	DOSTA	\N	\N	185	722	GS01SUMO-SBD11-04-DOSTAD000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
723	CTDMO	\N	\N	195	723	GS03FLMA-RIS02-14-CTDMOH	1500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
724	CTDGV	\N	\N	199	724	GS05MOAS-GL001-04-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
725	VELPT	\N	\N	183	725	GS01SUMO-RID16-04-VELPTA000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
726	DOSTA	\N	\N	183	726	GS01SUMO-RID16-03-DOSTAD000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
727	CTDGV	\N	\N	201	727	GS05MOAS-GL003-04-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
728	CTDMO	\N	\N	184	728	GS01SUMO-RII11-02-CTDMOQ012	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
729	CTDMO	\N	\N	184	729	GS01SUMO-RII11-02-CTDMOQ010	350	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
730	FLORD	\N	\N	201	730	GS05MOAS-GL003-01-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
731	ACOMM	\N	\N	198	731	GS03FLMB-RIS02-02-ACOMM0	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
732	VEL3D	\N	\N	191	732	GS02HYPM-WFP02-05-VEL3DL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
733	DOSTA	\N	\N	184	733	GS01SUMO-RII11-02-DOSTAD102	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
734	CTDBP	\N	\N	184	734	GS01SUMO-RII11-02-CTDBPP007	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
735	CTDMO	\N	\N	198	735	GS03FLMB-RIS02-09-CTDMOG	250	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
736	CTDMO	\N	\N	195	736	GS03FLMA-RIS02-12-CTDMOH	750	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
737	DOSTA	\N	\N	202	737	GS05MOAS-PG001-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
738	CTDMO	\N	\N	198	738	GS03FLMB-RIS02-04-CTDMOG	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
739	DOSTA	\N	\N	197	739	GS03FLMB-RIS01-03-DOSTAD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
740	PHSEN	\N	\N	184	740	GS01SUMO-RII11-02-PHSENE006	100	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
741	FLORD	\N	\N	200	741	GS05MOAS-GL002-01-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
742	PCO2W	\N	\N	184	742	GS01SUMO-RII11-02-PCO2WC204	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
743	PHSEN	\N	\N	184	743	GS01SUMO-RII11-02-PHSENE002	20	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
744	CTDMO	\N	\N	195	744	GS03FLMA-RIS02-13-CTDMOH	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
745	CTDMO	\N	\N	198	745	GS03FLMB-RIS02-07-CTDMOG	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
746	CTDMO	\N	\N	195	746	GS03FLMA-RIS02-03-CTDMOG	30	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
747	ADCPS	\N	\N	198	747	GS03FLMB-RIS02-01-ADCPSL	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
748	CTDGV	\N	\N	200	748	GS05MOAS-GL002-04-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
749	DOSTA	\N	\N	184	749	GS01SUMO-RII11-02-DOSTAD202	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
750	FLORD	\N	\N	184	750	GS01SUMO-RII11-02-FLORDG203	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
751	CTDBP	\N	\N	183	751	GS01SUMO-RID16-03-CTDBPF000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
752	ACOMM	\N	\N	183	752	GS01SUMO-RID16-00-ACOMM0000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
753	PCO2W	\N	\N	184	753	GS01SUMO-RII11-02-PCO2WC304	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
754	FLORD	\N	\N	203	754	GS05MOAS-PG002-02-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
755	DOSTA	\N	\N	191	755	GS02HYPM-WFP02-03-DOSTAL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
756	CTDMO	\N	\N	195	756	GS03FLMA-RIS02-08-CTDMOG	180	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
757	DOSTA	\N	\N	192	757	GS02HYPM-WFP03-03-DOSTAL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
758	CTDGV	\N	\N	203	758	GS05MOAS-PG002-01-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
759	DOSTA	\N	\N	201	759	GS05MOAS-GL003-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
760	ACOMM	\N	\N	195	760	GS03FLMA-RIS02-02-ACOMM0	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
761	CTDMO	\N	\N	198	761	GS03FLMB-RIS02-08-CTDMOG	180	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
762	OPTAA	\N	\N	183	762	GS01SUMO-RID16-01-OPTAAD000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
763	SPKIR	\N	\N	185	763	GS01SUMO-SBD11-05-SPKIRB000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
764	CTDBP	\N	\N	184	764	GS01SUMO-RII11-02-CTDBPP201	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
765	ACOMM	\N	\N	200	765	GS05MOAS-GL002-03-ACOMMM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
766	CTDMO	\N	\N	195	766	GS03FLMA-RIS02-04-CTDMOG	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
767	DOSTA	\N	\N	200	767	GS05MOAS-GL002-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
768	DOSTA	\N	\N	199	768	GS05MOAS-GL001-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
769	FLORT	\N	\N	197	769	GS03FLMB-RIS01-01-FLORTD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
770	CTDGV	\N	\N	202	770	GS05MOAS-PG001-01-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
771	FLORT	\N	\N	194	771	GS03FLMA-RIS01-01-FLORTD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
772	NUTNR	\N	\N	183	772	GS01SUMO-RID16-07-NUTNRB000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
773	PCO2W	\N	\N	184	773	GS01SUMO-RII11-02-PCO2WC104	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
774	PARAD	\N	\N	203	774	GS05MOAS-PG002-04-PARADM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
775	CTDMO	\N	\N	184	775	GS01SUMO-RII11-02-CTDMOR013	750	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
776	CTDMO	\N	\N	184	776	GS01SUMO-RII11-02-CTDMOR015	1500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
777	CTDMO	\N	\N	184	777	GS01SUMO-RII11-02-CTDMOR014	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
778	FLORD	\N	\N	192	778	GS02HYPM-WFP03-01-FLORDL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
779	PHSEN	\N	\N	194	779	GS03FLMA-RIS01-02-PHSENE	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
780	DOSTA	\N	\N	194	780	GS03FLMA-RIS01-03-DOSTAD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
781	PCO2W	\N	\N	183	781	GS01SUMO-RID16-05-PCO2WB000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
782	FDCHP	\N	\N	186	782	GS01SUMO-SBD12-08-FDCHPA000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
783	CTDMO	\N	\N	198	783	GS03FLMB-RIS02-05-CTDMOG	60	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
784	FLORD	\N	\N	199	784	GS05MOAS-GL001-01-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
785	MOPAK	\N	\N	185	785	GS01SUMO-SBD11-01-MOPAK0000	0	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
786	CTDPF	\N	\N	192	786	GS02HYPM-WFP03-04-CTDPFL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
787	CTDMO	\N	\N	195	787	GS03FLMA-RIS02-09-CTDMOG	250	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
788	FLORD	\N	\N	184	788	GS01SUMO-RII11-02-FLORDG103	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
789	CTDMO	\N	\N	198	789	GS03FLMB-RIS02-14-CTDMOH	1500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
790	CTDMO	\N	\N	195	790	GS03FLMA-RIS02-06-CTDMOG	90	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
\.


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_deployments_id_seq', 790, true);


--
-- Name: instrument_models_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_models_id_seq', 129, true);


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('instruments_id_seq', 790, true);


--
-- Name: manufacturers_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('manufacturers_id_seq', 24, true);


--
-- Name: organizations_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('organizations_id_seq', 1, true);


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('platform_deployments_id_seq', 203, true);


--
-- Name: platforms_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('platforms_id_seq', 203, true);


--
-- Data for Name: stream_parameters; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY stream_parameters (id, stream_parameter_name, short_name, long_name, standard_name, units, data_type) FROM stdin;
\.


--
-- Data for Name: stream_parameter_link; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY stream_parameter_link (id, stream_id, parameter_id) FROM stdin;
\.


--
-- Name: stream_parameter_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameter_link_id_seq', 1, false);


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameters_id_seq', 1, false);


--
-- Name: streams_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('streams_id_seq', 1, false);


--
-- Data for Name: user_scopes; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY user_scopes (id, scope_name, scope_description) FROM stdin;
\.


--
-- Data for Name: user_scope_link; Type: TABLE DATA; Schema: ooiui_dataload_testing; Owner: oceanzus
--

COPY user_scope_link (id, user_id, scope_id) FROM stdin;
\.


--
-- Name: user_scope_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('user_scope_link_id_seq', 1, false);


--
-- Name: user_scopes_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('user_scopes_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: ooiui_dataload_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('users_id_seq', 1, false);


SET search_path = ooiui_dev_design, pg_catalog;

--
-- Data for Name: organizations; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY organizations (id, organization_name) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY users (id, user_id, pass_hash, email, user_name, active, confirmed_at, first_name, last_name, phone_primary, phone_alternate, organization_id) FROM stdin;
\.


--
-- Data for Name: annotations; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY annotations (id, user_id, created_time, modified_time, reference_name, reference_type, reference_pk_id, title, comment) FROM stdin;
\.


--
-- Name: annotations_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('annotations_id_seq', 1, false);


--
-- Data for Name: arrays; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY arrays (id, array_code, description, geo_location, array_name, display_name) FROM stdin;
\.


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('arrays_id_seq', 1, false);


--
-- Data for Name: assemblies; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY assemblies (id, assembly_name, description) FROM stdin;
\.


--
-- Data for Name: asset_types; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY asset_types (id, asset_type_name) FROM stdin;
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY assets (id, asset_type_id, organization_id, supplier_id, deployment_id, asset_name, model, current_lifecycle_state, part_number, firmware_version, geo_location) FROM stdin;
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY files (id, user_id, file_name, file_system_path, file_size, file_permissions, file_type) FROM stdin;
\.


--
-- Data for Name: asset_file_link; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY asset_file_link (id, asset_id, file_id) FROM stdin;
\.


--
-- Name: asset_file_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_file_link_id_seq', 1, false);


--
-- Name: asset_types_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_types_id_seq', 1, false);


--
-- Name: assets_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('assets_id_seq', 1, false);


--
-- Name: asssemblies_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('asssemblies_id_seq', 1, false);


--
-- Data for Name: deployments; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY deployments (id, start_date, end_date, cruise_id) FROM stdin;
\.


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY manufacturers (id, manufacturer_name, phone_number, contact_name, web_address) FROM stdin;
\.


--
-- Data for Name: instrument_models; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY instrument_models (id, instrument_model_name, series_name, class_name, manufacturer_id) FROM stdin;
\.


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY instruments (id, instrument_name, description, location_description, instrument_series, serial_number, display_name, model_id, asset_id, depth_rating, manufacturer_id) FROM stdin;
\.


--
-- Data for Name: streams; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY streams (id, stream_name, instrument_id, description) FROM stdin;
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY datasets (id, stream_id, deployment_id, process_level, is_recovered) FROM stdin;
\.


--
-- Data for Name: dataset_keywords; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY dataset_keywords (id, dataset_id, concept_name, concept_description) FROM stdin;
\.


--
-- Name: dataset_keywords_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('dataset_keywords_id_seq', 1, false);


--
-- Name: datasets_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('datasets_id_seq', 1, false);


--
-- Name: deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('deployments_id_seq', 1, false);


--
-- Data for Name: drivers; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY drivers (id, instrument_id, driver_name, driver_version, author) FROM stdin;
\.


--
-- Data for Name: driver_stream_link; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY driver_stream_link (id, driver_id, stream_id) FROM stdin;
\.


--
-- Name: driver_stream_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('driver_stream_link_id_seq', 1, false);


--
-- Name: drivers_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('drivers_id_seq', 1, false);


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('files_id_seq', 1, false);


--
-- Data for Name: inspection_status; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY inspection_status (id, asset_id, file_id, status, technician_name, comments, inspection_date, document) FROM stdin;
\.


--
-- Name: inspection_status_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('inspection_status_id_seq', 1, false);


--
-- Name: installation_record_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('installation_record_id_seq', 1, false);


--
-- Data for Name: installation_records; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY installation_records (id, asset_id, assembly_id, date_installed, date_removed, technician_name, comments, file_id) FROM stdin;
\.


--
-- Data for Name: platforms; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY platforms (id, platform_name, description, location_description, platform_series, is_mobile, serial_no, asset_id, manufacturer_id) FROM stdin;
\.


--
-- Data for Name: platform_deployments; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY platform_deployments (id, start_date, end_date, platform_id, reference_designator, array_id, deployment_id, display_name, geo_location) FROM stdin;
\.


--
-- Data for Name: instrument_deployments; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY instrument_deployments (id, display_name, start_date, end_date, platform_deployment_id, instrument_id, reference_designator, depth, geo_location) FROM stdin;
\.


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_deployments_id_seq', 1, false);


--
-- Name: instrument_models_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_models_id_seq', 1, false);


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('instruments_id_seq', 1, false);


--
-- Name: manufacturers_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('manufacturers_id_seq', 1, false);


--
-- Name: organizations_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('organizations_id_seq', 1, false);


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('platform_deployments_id_seq', 1, false);


--
-- Name: platforms_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('platforms_id_seq', 1, false);


--
-- Data for Name: stream_parameters; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY stream_parameters (id, stream_parameter_name, short_name, long_name, standard_name, units, data_type) FROM stdin;
\.


--
-- Data for Name: stream_parameter_link; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY stream_parameter_link (id, stream_id, parameter_id) FROM stdin;
\.


--
-- Name: stream_parameter_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameter_link_id_seq', 1, false);


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameters_id_seq', 1, false);


--
-- Name: streams_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('streams_id_seq', 1, false);


--
-- Data for Name: user_scopes; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY user_scopes (id, scope_name, scope_description) FROM stdin;
\.


--
-- Data for Name: user_scope_link; Type: TABLE DATA; Schema: ooiui_dev_design; Owner: oceanzus
--

COPY user_scope_link (id, user_id, scope_id) FROM stdin;
\.


--
-- Name: user_scope_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('user_scope_link_id_seq', 1, false);


--
-- Name: user_scopes_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('user_scopes_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: ooiui_dev_design; Owner: oceanzus
--

SELECT pg_catalog.setval('users_id_seq', 1, false);


SET search_path = ooiui_jdc1, pg_catalog;

--
-- Data for Name: arrays; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY arrays (id, array_code, description, geo_location, array_name) FROM stdin;
1	CE	Endurance (CE)	0103000020E610000001000000050000008FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC0	Endurance
2	GP	PAPA (GP)	0103000020E610000001000000050000004C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C0	PAPA
3	CP	Pioneer (CP)	0103000020E61000000100000005000000CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0	Pioneer
4	GA	Argentine (GA)	0103000020E6100000010000000500000062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C0	Argentine
5	GI	Irminger (GI)	0103000020E610000001000000050000007B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C0	Irminger
6	GS	55 S (GS)	0103000020E610000001000000050000007CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C0	55 S
\.


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('arrays_id_seq', 6, true);


--
-- Data for Name: asset_types; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY asset_types (id, asset_type_name) FROM stdin;
\.


--
-- Data for Name: organizations; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY organizations (id, organization_name) FROM stdin;
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY assets (id, asset_type_id, organization_id, supplier_id, deployment_id, asset_name, model, current_lifecycle_state, part_number, firmware_version, geo_location) FROM stdin;
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY files (id, user_id, file_name, file_system_path, file_size, file_permissions, file_type) FROM stdin;
\.


--
-- Data for Name: asset_file_link; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY asset_file_link (id, asset_id, file_id) FROM stdin;
\.


--
-- Name: asset_file_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_file_link_id_seq', 1, false);


--
-- Name: asset_types_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_types_id_seq', 1, false);


--
-- Name: assets_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('assets_id_seq', 1, false);


--
-- Data for Name: asssemblies; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY asssemblies (id, assembly_name, description) FROM stdin;
\.


--
-- Name: asssemblies_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('asssemblies_id_seq', 1, false);


--
-- Data for Name: deployments; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY deployments (id, start_date, end_date, cruise_id) FROM stdin;
1	\N	\N	1
\.


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY manufacturers (id, manufacturer_name, phone_number, contact_name, web_address) FROM stdin;
1	Undersea Widget Welders	800-888-8080	Dirk Pitt	http://www.uww.com
\.


--
-- Data for Name: instrument_models; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY instrument_models (id, instrument_model_name, series_name, class_name, manufacturer_id) FROM stdin;
1	Ocean Instrument	Mark 1	Enterprise	1
\.


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY instruments (id, instrument_name, description, location_description, instrument_series, serial_number, display_name, model_id, asset_id, depth_rating, manufacturer_id) FROM stdin;
1	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	spectral_irradiance	1	1	25	1
2	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD_profiler	1	1	80	1
3	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	oxygen_dissolved_stable	1	1	80	1
4	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
5	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
6	PCO2W	pCO2_water	MFN	B	\N	pCO2_water	1	1	500	1
7	VEL3D	Velocity_point_3D_turb	MFN	D	\N	Velocity_point_3D_turb	1	1	25	1
8	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	plankton_ZP_sonar_coastal	1	1	25	1
9	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	Fluorometer_three_wavelength	1	1	25	1
10	VEL3D	Velocity_point_3D_turb	Benthic Package (J Box)	C	\N	Velocity_point_3D_turb	1	1	500	1
11	PARAD	PAR	Glider Science Bay	M	\N	PAR	1	1	-1	1
12	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
13	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	A	\N	Velocity_profile_short_range	1	1	5	1
14	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
15	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	Fluorometer_three_wavelength	1	1	-1	1
16	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	Fluorometer_three_wavelength	1	1	-1	1
17	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
18	ADCPT	Velocity_profile_short_range	MFN	M	\N	Velocity_profile_short_range	1	1	25	1
19	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD_profiler	1	1	80	1
20	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	Fluorometer_three_wavelength	1	1	500	1
21	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
22	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
23	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2_water	1	1	5	1
24	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	oxygen_dissolved_stable	1	1	25	1
25	OPTAA	attenuation_absorption_optical	MFN	D	\N	attenuation_absorption_optical	1	1	80	1
26	PCO2W	pCO2_water	Benthic Package (J Box)	B	\N	pCO2_water	1	1	80	1
27	HYDBB	Hydrophone_BB_passive	Benthic Package (J Box)	A	\N	Hydrophone_BB_passive	1	1	80	1
28	OPTAA	attenuation_absorption_optical	MFN	D	\N	attenuation_absorption_optical	1	1	25	1
29	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
30	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
31	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD_glider	1	1	-1	1
32	DOSTA	oxygen_dissolved_stable	Benthic Package (J Box)	D	\N	oxygen_dissolved_stable	1	1	80	1
33	ADCPT	Velocity_profile_short_range	MFN	M	\N	Velocity_profile_short_range	1	1	25	1
34	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	plankton_ZP_sonar_coastal	1	1	25	1
35	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
36	PCO2W	pCO2_water	MFN	B	\N	pCO2_water	1	1	25	1
37	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
38	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Velocity_point	1	1	25	1
39	CAMDS	camera_digital_still_strobe	Benthic Package (J Box) - via wet/mate connector	B	\N	camera_digital_still_strobe	1	1	500	1
40	PCO2W	pCO2_water	Benthic Package (J Box)	B	\N	pCO2_water	1	1	500	1
41	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
42	SPKIR	spectral_irradiance	shallow profiling body	A	\N	spectral_irradiance	1	1	200	1
43	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
44	PCO2W	pCO2_water	Surface Piercing Profiler Body	0	\N	pCO2_water	1	1	25	1
45	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	spectral_irradiance	1	1	80	1
46	PARAD	PAR	Glider Science Bay	M	\N	PAR	1	1	-1	1
47	FLORT	Fluorometer_three_wavelength	shallow profiling body	D	\N	Fluorometer_three_wavelength	1	1	200	1
48	NUTNR	nutrient_Nitrate	shallow profiling body	A	\N	nutrient_Nitrate	1	1	200	1
49	VELPT	Velocity_point	Bottom of buoy	A	\N	Velocity_point	1	1	1	1
50	PRESF	pressure_SF	MFN	A	\N	pressure_SF	1	1	25	1
51	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
52	VELPT	Velocity_point	Bottom of buoy	A	\N	Velocity_point	1	1	1	1
53	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity_profile_mobile_asset	1	1	-1	1
54	CTDPF	CTD_profiler	shallow profiling body	A	\N	CTD_profiler	1	1	200	1
55	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
56	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD_glider	1	1	-1	1
57	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
58	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
59	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
60	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
61	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	nutrient_Nitrate	1	1	80	1
62	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
63	CTDBP	CTD_bottom_pumped	Benthic Package (J Box)	O	\N	CTD_bottom_pumped	1	1	500	1
64	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
65	HYDBB	Hydrophone_BB_passive	Benthic Package (J Box)	A	\N	Hydrophone_BB_passive	1	1	500	1
66	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
67	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem_acoustic	1	1	25	1
68	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	attenuation_absorption_optical	1	1	25	1
69	PHSEN	pH_stable	MFN	D	\N	pH_stable	1	1	25	1
70	PARAD	PAR	Glider Science Bay	M	\N	PAR	1	1	-1	1
71	PHSEN	pH_stable	MFN	D	\N	pH_stable	1	1	25	1
72	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	Fluorometer_three_wavelength	1	1	80	1
73	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
74	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	spectral_irradiance	1	1	25	1
75	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
76	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	Fluorometer_three_wavelength	1	1	-1	1
77	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
78	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
79	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
80	PHSEN	pH_stable	MFN	D	\N	pH_stable	1	1	80	1
81	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
82	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
83	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
84	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	oxygen_dissolved_stable	1	1	-1	1
85	OPTAA	attenuation_absorption_optical	Benthic Package (J Box)	C	\N	attenuation_absorption_optical	1	1	500	1
86	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	nutrient_Nitrate	1	1	25	1
87	PARAD	PAR	Surface Piercing Profiler Body	J	\N	PAR	1	1	25	1
88	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	oxygen_dissolved_fastresp	1	1	500	1
89	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Velocity_point	1	1	25	1
90	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD_profiler	1	1	25	1
91	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
92	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
93	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
94	ADCPS	Velocity_profile_long_range	MFN	J	\N	Velocity_profile_long_range	1	1	500	1
95	PARAD	PAR	Glider Science Bay	M	\N	PAR	1	1	-1	1
96	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	oxygen_dissolved_stable	1	1	80	1
97	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	Fluorometer_three_wavelength	1	1	80	1
98	CAMDS	camera_digital_still_strobe	MFN	A	\N	camera_digital_still_strobe	1	1	80	1
99	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	Fluorometer_three_wavelength	1	1	-1	1
100	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity_profile_mobile_asset	1	1	-1	1
101	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	C	\N	Velocity_profile_short_range	1	1	5	1
102	CTDBP	CTD_bottom_pumped	MFN	E	\N	CTD_bottom_pumped	1	1	500	1
103	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	Velocity_point_3D_turb	1	1	500	1
104	PCO2W	pCO2_water	Surface Piercing Profiler Body	0	\N	pCO2_water	1	1	80	1
105	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity_profile_mobile_asset	1	1	-1	1
106	CAMDS	camera_digital_still_strobe	MFN	A	\N	camera_digital_still_strobe	1	1	25	1
107	FLORT	Fluorometer_three_wavelength	deep profiling body	A	\N	Fluorometer_three_wavelength	1	1	500	1
108	ZPLSC	plankton_ZP_sonar_coastal	mid-water platform	B	\N	plankton_ZP_sonar_coastal	1	1	200	1
109	PHSEN	pH_stable	Benthic Package (J Box)	D	\N	pH_stable	1	1	500	1
110	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
111	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity_profile_mobile_asset	1	1	-1	1
112	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	Fluorometer_three_wavelength	1	1	-1	1
113	DOSTA	oxygen_dissolved_stable	mid-water platform	D	\N	oxygen_dissolved_stable	1	1	200	1
114	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
115	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
116	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
117	VELPT	Velocity_point	shallow profiling body	D	\N	Velocity_point	1	1	200	1
118	PHSEN	pH_stable	Benthic Package (J Box)	D	\N	pH_stable	1	1	80	1
119	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	spectral_irradiance	1	1	80	1
120	DOSTA	oxygen_dissolved_stable	MFN	D	\N	oxygen_dissolved_stable	1	1	25	1
121	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	oxygen_dissolved_stable	1	1	-1	1
122	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	nutrient_Nitrate	1	1	80	1
123	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Velocity_point	1	1	80	1
124	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
125	VELPT	Velocity_point	Bottom of buoy	A	\N	Velocity_point	1	1	1	1
126	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
127	PRESF	pressure_SF	MFN	A	\N	pressure_SF	1	1	25	1
128	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
129	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Velocity_point	1	1	80	1
130	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
131	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
132	DOSTA	oxygen_dissolved_stable	deep profiling body	D	\N	oxygen_dissolved_stable	1	1	500	1
133	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
134	PHSEN	pH_stable	MFN	D	\N	pH_stable	1	1	500	1
135	DOSTA	oxygen_dissolved_stable	MFN	D	\N	oxygen_dissolved_stable	1	1	500	1
136	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	attenuation_absorption_optical	1	1	25	1
137	PCO2W	pCO2_water	Surface Piercing Profiler Body	0	\N	pCO2_water	1	1	80	1
138	OPTAA	attenuation_absorption_optical	Benthic Package (J Box)	D	\N	attenuation_absorption_optical	1	1	80	1
139	PRESF	pressure_SF	MFN	B	\N	pressure_SF	1	1	80	1
140	ADCPT	Velocity_profile_short_range	MFN	C	\N	Velocity_profile_short_range	1	1	80	1
141	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
142	PCO2W	pCO2_water	Surface Piercing Profiler Body	0	\N	pCO2_water	1	1	25	1
143	DOFST	oxygen_dissolved_fastresp	shallow profiling body	A	\N	oxygen_dissolved_fastresp	1	1	200	1
144	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
145	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem_acoustic	1	1	80	1
146	OPTAA	attenuation_absorption_optical	shallow profiling body	D	\N	attenuation_absorption_optical	1	1	200	1
147	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD_profiler	1	1	500	1
148	CTDBP	CTD_bottom_pumped	Benthic Package (J Box)	N	\N	CTD_bottom_pumped	1	1	80	1
149	CAMDS	camera_digital_still_strobe	MFN	A	\N	camera_digital_still_strobe	1	1	25	1
150	CAMDS	camera_digital_still_strobe	Benthic Package (J Box) - via wet/mate connector	B	\N	camera_digital_still_strobe	1	1	80	1
151	CTDPF	CTD_profiler	deep profiling body	L	\N	CTD_profiler	1	1	500	1
152	ADCPS	Velocity_profile_long_range	Benthic Package (J Box)	I	\N	Velocity_profile_long_range	1	1	500	1
153	ADCPT	Velocity_profile_short_range	Benthic Package (J Box)	B	\N	Velocity_profile_short_range	1	1	80	1
154	PARAD	PAR	Surface Piercing Profiler Body	J	\N	PAR	1	1	80	1
155	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	oxygen_dissolved_stable	1	1	-1	1
156	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	Fluorometer_three_wavelength	1	1	25	1
157	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
158	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
159	DOSTA	oxygen_dissolved_stable	MFN	D	\N	oxygen_dissolved_stable	1	1	25	1
160	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
161	PHSEN	pH_stable	shallow profiling body	A	\N	pH_stable	1	1	200	1
162	VEL3D	Velocity_point_3D_turb	MFN	D	\N	Velocity_point_3D_turb	1	1	80	1
163	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
164	VELPT	Velocity_point	Bottom of buoy	A	\N	Velocity_point	1	1	1	1
165	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
166	DOSTA	oxygen_dissolved_stable	Benthic Package (J Box)	D	\N	oxygen_dissolved_stable	1	1	500	1
167	PHSEN	pH_stable	mid-water platform, upward-looking	A	\N	pH_stable	1	1	200	1
168	FDCHP	flux_direct_cov_HP	Buoy Tower 3 M	A	\N	flux_direct_cov_HP	1	1	3	1
169	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	attenuation_absorption_optical	1	1	80	1
170	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
171	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
172	PRESF	pressure_SF	MFN	C	\N	pressure_SF	1	1	500	1
173	VELPT	Velocity_point	Bottom of buoy	A	\N	Velocity_point	1	1	1	1
174	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
175	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
176	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity_profile_mobile_asset	1	1	-1	1
177	PARAD	PAR	shallow profiling body	A	\N	PAR	1	1	200	1
178	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
179	ZPLSC	plankton_ZP_sonar_coastal	LV-Node	B	\N	plankton_ZP_sonar_coastal	1	1	80	1
180	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	plankton_ZP_sonar_coastal	1	1	80	1
181	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD_bottom_pumped	1	1	80	1
182	VEL3D	Velocity_point_3D_turb	Benthic Package (J Box)	C	\N	Velocity_point_3D_turb	1	1	80	1
183	PARAD	PAR	Glider Science Bay	M	\N	PAR	1	1	-1	1
184	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
185	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	attenuation_absorption_optical	1	1	80	1
186	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	oxygen_dissolved_stable	1	1	25	1
187	PARAD	PAR	Surface Piercing Profiler Body	J	\N	PAR	1	1	25	1
188	OPTAA	attenuation_absorption_optical	MFN	D	\N	attenuation_absorption_optical	1	1	25	1
189	PARAD	PAR	Glider Science Bay	M	\N	PAR	1	1	-1	1
190	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD_bottom_pumped	1	1	25	1
191	PCO2W	pCO2_water	shallow profiling body	A	\N	pCO2_water	1	1	200	1
192	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD_glider	1	1	-1	1
193	PARAD	PAR	Wire Following Profiler Body	K	\N	PAR	1	1	500	1
194	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
195	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	plankton_ZP_sonar_coastal	1	1	500	1
196	DOSTA	oxygen_dissolved_stable	MFN	D	\N	oxygen_dissolved_stable	1	1	80	1
197	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD_glider	1	1	-1	1
198	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD_profiler	1	1	25	1
199	CTDPF	CTD_profiler	mid-water platform	A	\N	CTD_profiler	1	1	200	1
200	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
201	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD_bottom_pumped	1	1	25	1
202	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity_profile_mobile_asset	1	1	-1	1
203	VEL3D	Velocity_point_3D_turb	MFN	D	\N	Velocity_point_3D_turb	1	1	25	1
204	OPTAA	attenuation_absorption_optical	MFN	C	\N	attenuation_absorption_optical	1	1	500	1
205	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
206	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
207	PCO2W	pCO2_water	MFN	B	\N	pCO2_water	1	1	25	1
208	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
209	VELPT	Velocity_point	Bottom of buoy	A	\N	Velocity_point	1	1	1	1
210	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
211	PARAD	PAR	Surface Piercing Profiler Body	J	\N	PAR	1	1	80	1
212	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
213	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	nutrient_Nitrate	1	1	25	1
214	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
215	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	oxygen_dissolved_stable	1	1	-1	1
216	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
217	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD_glider	1	1	-1	1
218	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
219	PCO2W	pCO2_water	mid-water platform	A	\N	pCO2_water	1	1	200	1
220	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	oxygen_dissolved_stable	1	1	-1	1
221	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
222	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	oxygen_dissolved_stable	1	1	-1	1
223	PCO2W	pCO2_water	MFN	B	\N	pCO2_water	1	1	80	1
224	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	Fluorometer_three_wavelength	1	1	-1	1
225	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	C	\N	Velocity_profile_short_range	1	1	5	1
226	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD_glider	1	1	-1	1
227	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
228	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
229	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2_water	1	1	5	1
230	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
231	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
232	VEL3D	Velocity_point_3D_turb	MFN	D	\N	Velocity_point_3D_turb	1	1	500	1
233	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem_acoustic	1	1	25	1
234	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
235	VEL3D	Velocity_point_3D_turb	deep profiling body	A	\N	Velocity_point_3D_turb	1	1	500	1
236	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	A	\N	Velocity_profile_short_range	1	1	5	1
237	CAMDS	camera_digital_still_strobe	MFN	A	\N	camera_digital_still_strobe	1	1	500	1
238	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
239	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	plankton_ZP_sonar_global	1	1	-1	1
240	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	oxygen_dissolved_stable	1	1	4000	1
241	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
242	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	1000	1
243	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
244	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
245	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
246	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
247	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
248	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	1000	1
249	PARAD	PAR		M	\N	PAR	1	1	1000	1
250	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
251	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
252	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD_profiler	1	1	4000	1
253	NUTNR	nutrient_Nitrate		M	\N	nutrient_Nitrate	1	1	1000	1
254	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
255	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
256	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
257	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
258	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	Velocity_point_3D_turb	1	1	4000	1
259	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
260	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
261	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
262	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
263	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
264	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
265	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	164	1
266	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
267	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
268	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
269	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	Fluorometer_two_wavelength	1	1	2100	1
270	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
271	OPTAA	attenuation_absorption_optical		M	\N	attenuation_absorption_optical	1	1	1000	1
272	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	1000	1
273	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
274	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
275	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD_profiler	1	1	2100	1
276	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
277	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
278	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
279	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
280	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
281	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
282	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
283	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	Fluorometer_two_wavelength	1	1	4000	1
284	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
285	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
286	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
287	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	oxygen_dissolved_stable	1	1	2100	1
288	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
289	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
290	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
291	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
292	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
293	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
294	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
295	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
296	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
297	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
298	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
299	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
300	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	Velocity_point_3D_turb	1	1	2100	1
301	PARAD	PAR		N	\N	PAR	1	1	-1	1
302	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	oxygen_dissolved_fastresp	1	1	520	1
303	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	Motion pack	1	1	0	1
304	FLORT	Fluorometer_three_wavelength		M	\N	Fluorometer_three_wavelength	1	1	1000	1
305	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	oxygen_dissolved_fastresp	1	1	130	1
306	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD_profiler	1	1	360	1
307	PARAD	PAR		N	\N	PAR	1	1	-1	1
308	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
309	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
310	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
311	DOSTA	oxygen_dissolved_stable	MFN	D	\N	oxygen_dissolved_stable	1	1	130	1
312	PARAD	PAR		M	\N	PAR	1	1	1000	1
313	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity_profile_short_range	1	1	140	1
314	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
315	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	Velocity_point_3D_turb	1	1	140	1
316	PHSEN	pH_stable	MFN	D	\N	pH_stable	1	1	130	1
317	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
318	PARAD	PAR	Wire Following Profiler Body	K	\N	PAR	1	1	520	1
319	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	attenuation_absorption_optical	1	1	130	1
320	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
321	PARAD	PAR	Surface Piercing Profiler Body	J	\N	PAR	1	1	130	1
322	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	Motion pack	1	1	0	1
323	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Velocity_point	1	1	210	1
324	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
325	MOPAK	Motion pack	Buoy Well	0	\N	Motion pack	1	1	0	1
326	ADCPT	Velocity_profile_short_range	MFN	F	\N	Velocity_profile_short_range	1	1	210	1
327	FLORT	Fluorometer_three_wavelength		M	\N	Fluorometer_three_wavelength	1	1	1000	1
328	OPTAA	attenuation_absorption_optical	MFN	D	\N	attenuation_absorption_optical	1	1	210	1
329	PARAD	PAR		M	\N	PAR	1	1	1000	1
330	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
331	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity_profile_mobile_asset	1	1	1000	1
332	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	oxygen_dissolved_fastresp	1	1	140	1
333	PARAD	PAR	Wire Following Profiler Body	K	\N	PAR	1	1	130	1
334	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity_profile_mobile_asset	1	1	1000	1
335	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
336	DOSTA	oxygen_dissolved_stable		N	\N	oxygen_dissolved_stable	1	1	-1	1
337	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
338	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	attenuation_absorption_optical	1	1	210	1
339	PARAD	PAR	Wire Following Profiler Body	K	\N	PAR	1	1	140	1
340	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
341	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	plankton_ZP_sonar_coastal	1	1	130	1
342	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
343	PCO2W	pCO2_water	MFN	B	\N	pCO2_water	1	1	520	1
344	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	oxygen_dissolved_fastresp	1	1	520	1
345	CTDBP	CTD_bottom_pumped	MFN	D	\N	CTD_bottom_pumped	1	1	210	1
346	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	plankton_ZP_sonar_coastal	1	1	210	1
347	PARAD	PAR		M	\N	PAR	1	1	1000	1
348	DOSTA	oxygen_dissolved_stable	MFN	D	\N	oxygen_dissolved_stable	1	1	210	1
349	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
350	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	Velocity_point_3D_turb	1	1	520	1
351	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
352	PARAD	PAR		M	\N	PAR	1	1	1000	1
353	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD_profiler	1	1	140	1
354	CTDBP	CTD_bottom_pumped	MFN	D	\N	CTD_bottom_pumped	1	1	130	1
355	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	Velocity_point_3D_turb	1	1	520	1
356	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
357	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
358	PCO2W	pCO2_water	MFN	B	\N	pCO2_water	1	1	210	1
359	VELPT	Velocity_point	MFN	B	\N	Velocity_point	1	1	520	1
360	FLORT	Fluorometer_three_wavelength		M	\N	Fluorometer_three_wavelength	1	1	1000	1
361	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	plankton_ZP_sonar_coastal	1	1	520	1
362	CTDAV	CTD_AUV		N	\N	CTD_AUV	1	1	-1	1
363	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
364	FLORT	Fluorometer_three_wavelength		M	\N	Fluorometer_three_wavelength	1	1	1000	1
365	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
366	FLORT	Fluorometer_three_wavelength		M	\N	Fluorometer_three_wavelength	1	1	1000	1
367	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD_profiler	1	1	520	1
368	PARAD	PAR		M	\N	PAR	1	1	1000	1
369	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
370	PHSEN	pH_stable	MFN	D	\N	pH_stable	1	1	210	1
371	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
372	PHSEN	pH_stable	MFN	D	\N	pH_stable	1	1	520	1
373	DOSTA	oxygen_dissolved_stable	MFN	D	\N	oxygen_dissolved_stable	1	1	520	1
374	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	5	1
375	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	Fluorometer_three_wavelength	1	1	130	1
376	ADCPA	Velocity_profile_mobile_asset		N	\N	Velocity_profile_mobile_asset	1	1	-1	1
377	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
378	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	spectral_irradiance	1	1	130	1
379	ADCPS	Velocity_profile_long_range	MFN	J	\N	Velocity_profile_long_range	1	1	520	1
380	PARAD	PAR	Surface Piercing Profiler Body	J	\N	PAR	1	1	210	1
381	OPTAA	attenuation_absorption_optical	MFN	D	\N	attenuation_absorption_optical	1	1	520	1
382	MOPAK	Motion pack	Buoy Well	0	\N	Motion pack	1	1	0	1
383	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	Motion pack	1	1	0	1
384	CTDBP	CTD_bottom_pumped	MFN	E	\N	CTD_bottom_pumped	1	1	520	1
385	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
386	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
387	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
388	PCO2W	pCO2_water	Surface Piercing Profiler Body	0	\N	pCO2_water	1	1	210	1
389	MOPAK	Motion pack	Buoy Well	0	\N	Motion pack	1	1	0	1
390	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
391	OPTAA	attenuation_absorption_optical	MFN	D	\N	attenuation_absorption_optical	1	1	130	1
392	PRESF	pressure_SF	MFN	C	\N	pressure_SF	1	1	520	1
393	PARAD	PAR	Wire Following Profiler Body	K	\N	PAR	1	1	520	1
394	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem_acoustic	1	1	210	1
395	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	nutrient_Nitrate	1	1	210	1
396	ADCPT	Velocity_profile_short_range	MFN	F	\N	Velocity_profile_short_range	1	1	130	1
397	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	Velocity_point_3D_turb	1	1	130	1
398	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
399	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
400	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	Fluorometer_three_wavelength	1	1	360	1
401	PCO2W	pCO2_water	MFN	B	\N	pCO2_water	1	1	130	1
402	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
403	ADCPA	Velocity_profile_mobile_asset		N	\N	Velocity_profile_mobile_asset	1	1	-1	1
404	CTDAV	CTD_AUV		N	\N	CTD_AUV	1	1	-1	1
405	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
406	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	5	1
407	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD_profiler	1	1	130	1
408	PRESF	pressure_SF	MFN	B	\N	pressure_SF	1	1	130	1
409	PARAD	PAR	Wire Following Profiler Body	K	\N	PAR	1	1	360	1
410	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	oxygen_dissolved_stable	1	1	130	1
411	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity_profile_short_range	1	1	130	1
412	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	Fluorometer_three_wavelength	1	1	520	1
413	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
414	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	Fluorometer_three_wavelength	1	1	210	1
415	FLORT	Fluorometer_three_wavelength		N	\N	Fluorometer_three_wavelength	1	1	-1	1
416	FDCHP	flux_direct_cov_HP	Buoy Tower 3 M	A	\N	flux_direct_cov_HP	1	1	3	1
417	NUTNR	nutrient_Nitrate		N	\N	nutrient_Nitrate	1	1	-1	1
418	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity_profile_mobile_asset	1	1	1000	1
419	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	oxygen_dissolved_fastresp	1	1	360	1
420	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
421	FLORT	Fluorometer_three_wavelength		N	\N	Fluorometer_three_wavelength	1	1	-1	1
422	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity_profile_mobile_asset	1	1	1000	1
423	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
424	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	5	1
425	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
426	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	oxygen_dissolved_stable	1	1	210	1
427	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
428	DOSTA	oxygen_dissolved_stable		N	\N	oxygen_dissolved_stable	1	1	-1	1
429	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	5	1
430	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	Fluorometer_three_wavelength	1	1	140	1
431	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
432	PARAD	PAR		M	\N	PAR	1	1	1000	1
433	MOPAK	Motion pack	Buoy Well	0	\N	Motion pack	1	1	0	1
434	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD_profiler	1	1	210	1
435	FLORT	Fluorometer_three_wavelength		M	\N	Fluorometer_three_wavelength	1	1	1000	1
436	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
437	MOPAK	Motion pack	Buoy Well	0	\N	Motion pack	1	1	0	1
438	VELPT	Velocity_point	MFN	A	\N	Velocity_point	1	1	130	1
439	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Meteorology_bulk	1	1	3	1
440	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity_profile_short_range	1	1	360	1
441	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity_profile_mobile_asset	1	1	1000	1
442	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD_bottom_pumped	1	1	5	1
443	ADCPS	Velocity_profile_long_range	Instrument Frame	L	\N	Velocity_profile_long_range	1	1	520	1
444	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	pH_stable	1	1	5	1
445	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	Fluorometer_three_wavelength	1	1	520	1
446	NUTNR	nutrient_Nitrate		N	\N	nutrient_Nitrate	1	1	-1	1
447	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	5	1
448	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	Velocity_point_3D_turb	1	1	360	1
449	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Velocity_point	1	1	130	1
450	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity_profile_mobile_asset	1	1	1000	1
451	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	spectral_irradiance	1	1	210	1
452	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	Fluorometer_three_wavelength	1	1	130	1
453	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem_acoustic	1	1	130	1
454	PCO2W	pCO2_water	Surface Piercing Profiler Body	0	\N	pCO2_water	1	1	130	1
455	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD_profiler	1	1	520	1
456	PRESF	pressure_SF	MFN	B	\N	pressure_SF	1	1	210	1
457	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	5	1
458	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	5	1
459	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
460	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD_profiler	1	1	130	1
461	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	nutrient_Nitrate	1	1	130	1
462	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
463	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	-1	1
464	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
465	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	-1	1
466	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
467	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
468	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
469	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	1500	1
470	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	1000	1
471	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	750	1
472	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
473	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
474	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Meteorology_bulk	1	1	5	1
475	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	80	1
476	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	80	1
477	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	oxygen_dissolved_stable	1	1	1	1
478	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	130	1
479	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	40	1
480	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
481	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
482	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD_bottom_pumped	1	1	12	1
483	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
484	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
485	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Meteorology_bulk	1	1	5	1
486	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	Fluorometer_three_wavelength	1	1	1	1
487	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	plankton_ZP_sonar_global	1	1	-1	1
488	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	Velocity_point_3D_turb	1	1	2600	1
489	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	12	1
490	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	40	1
491	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
492	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
493	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
494	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	spectral_irradiance	1	1	5	1
495	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
496	PARAD	PAR		M	\N	PAR	1	1	1000	1
497	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
498	NUTNR	nutrient_Nitrate		M	\N	nutrient_Nitrate	1	1	1000	1
499	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	-1	1
500	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	Velocity_point_3D_turb	1	1	5000	1
501	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity_profile_long_range	1	1	500	1
502	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
503	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
504	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
505	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	Fluorometer_two_wavelength	1	1	5000	1
506	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	20	1
507	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	100	1
508	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	60	1
509	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
510	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
511	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	180	1
512	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	164	1
513	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	12	1
514	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
515	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	12	1
516	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD_profiler	1	1	5000	1
517	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	12	1
518	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
519	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
520	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
521	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
522	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	350	1
523	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	500	1
524	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	attenuation_absorption_optical	1	1	1	1
525	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	-1	1
526	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	40	1
527	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	-1	1
528	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
529	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
530	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
531	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	-1	1
532	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	-1	1
533	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	Fluorometer_two_wavelength	1	1	2600	1
534	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	130	1
535	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	pH_stable	1	1	20	1
536	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	pH_stable	1	1	100	1
537	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
538	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
539	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	40	1
540	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
541	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	12	1
542	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	oxygen_dissolved_stable	1	1	2600	1
543	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2_water	1	1	12	1
544	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD_profiler	1	1	2600	1
545	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
546	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	-1	1
547	OPTAA	attenuation_absorption_optical		M	\N	attenuation_absorption_optical	1	1	1000	1
548	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
549	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	-1	1
550	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
551	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	12	1
552	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
553	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
554	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
555	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	oxygen_dissolved_stable	1	1	5000	1
556	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	80	1
557	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	nutrient_Nitrate	1	1	1	1
558	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	-1	1
559	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
560	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	250	1
561	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
562	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
563	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	12	1
564	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	130	1
565	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	80	1
566	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	-1	1
567	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	130	1
568	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	-1	1
569	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
570	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	130	1
571	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Meteorology_bulk	1	1	5	1
572	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
573	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	12	1
574	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	-1	1
575	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	2400	1
576	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
577	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	pH_stable	1	1	20	1
578	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	pH_stable	1	1	100	1
579	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	oxygen_dissolved_stable	1	1	1	1
580	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	spectral_irradiance	1	1	5	1
581	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
582	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	2100	1
583	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	-1	1
584	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	80	1
585	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	130	1
586	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	-1	1
587	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	12	1
588	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	-1	1
589	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	-1	1
590	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
591	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	-1	1
592	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	12	1
593	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	2400	1
594	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	2700	1
595	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	2700	1
596	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	-1	1
597	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	130	1
598	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	40	1
599	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
600	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	-1	1
601	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	40	1
602	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	40	1
603	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	130	1
604	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
605	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
606	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	12	1
607	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	80	1
608	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	1800	1
609	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
610	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	1500	1
611	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	1000	1
612	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	2100	1
613	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
614	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	750	1
615	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	Velocity_point_3D_turb	1	1	2600	1
616	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	2400	1
617	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
618	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
619	FDCHP	flux_direct_cov_HP	Buoy Tower 5 M	A	\N	flux_direct_cov_HP	1	1	5	1
620	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	2100	1
621	NUTNR	nutrient_Nitrate		M	\N	nutrient_Nitrate	1	1	1000	1
622	OPTAA	attenuation_absorption_optical		M	\N	attenuation_absorption_optical	1	1	1000	1
623	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2_water	1	1	12	1
624	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Meteorology_bulk	1	1	5	1
625	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD_profiler	1	1	2600	1
626	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	2100	1
627	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
628	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	40	1
629	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
630	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	-1	1
631	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
632	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
633	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
634	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	164	1
635	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1800	1
636	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	12	1
637	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	-1	1
638	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	nutrient_Nitrate	1	1	1	1
639	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
640	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
641	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
642	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
643	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	-1	1
644	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	2700	1
645	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	oxygen_dissolved_stable	1	1	2600	1
646	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	2400	1
647	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	80	1
648	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	12	1
649	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	Fluorometer_three_wavelength	1	1	1	1
650	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	plankton_ZP_sonar_global	1	1	-1	1
651	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	attenuation_absorption_optical	1	1	1	1
652	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1800	1
653	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
654	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
655	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
656	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
657	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
658	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
659	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	250	1
660	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	180	1
661	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD_bottom_pumped	1	1	12	1
662	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	20	1
663	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	100	1
664	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	60	1
665	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	80	1
666	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
667	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
668	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
669	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity_profile_long_range	1	1	500	1
670	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
671	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	Fluorometer_two_wavelength	1	1	2600	1
672	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
673	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
674	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
675	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
676	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
677	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
678	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	2700	1
679	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Velocity_Point	1	1	1800	1
680	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
681	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
682	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	12	1
683	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	350	1
684	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	500	1
685	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	-1	1
686	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
687	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
688	PARAD	PAR		M	\N	PAR	1	1	1000	1
689	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
690	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	Fluorometer_three_wavelength	1	1	12	1
691	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
692	OPTAA	attenuation_absorption_optical		M	\N	attenuation_absorption_optical	1	1	1000	1
693	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	130	1
694	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	Fluorometer_three_wavelength	1	1	1	1
695	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	130	1
696	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	40	1
697	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity_profile_long_range	1	1	500	1
698	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
699	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	Fluorometer_two_wavelength	1	1	2400	1
700	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
701	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	1000	1
702	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	wave_spectra_surface	1	1	0	1
703	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
704	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	attenuation_absorption_optical	1	1	1	1
705	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	1000	1
706	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	Velocity_point_3D_turb	1	1	4600	1
707	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
708	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	spectral_irradiance	1	1	12	1
709	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2_air-sea	1	1	0	1
710	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
711	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD_profiler	1	1	2400	1
712	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
713	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	164	1
714	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	plankton_ZP_sonar_global	1	1	-1	1
715	NUTNR	nutrient_Nitrate		M	\N	nutrient_Nitrate	1	1	1000	1
716	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	nutrient_Nitrate	1	1	1	1
717	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	500	1
718	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	350	1
719	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	250	1
720	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	180	1
721	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	100	1
722	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	60	1
723	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
724	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	20	1
725	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Meteorology_bulk	1	1	5	1
726	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Meteorology_bulk	1	1	5	1
727	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
728	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	oxygen_dissolved_stable	1	1	1	1
729	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
730	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
731	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Velocity_point	1	1	12	1
732	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	oxygen_dissolved_stable	1	1	12	1
733	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
734	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	500	1
735	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD_mooring	1	1	350	1
736	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
737	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
738	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	Velocity_point_3D_turb	1	1	2400	1
739	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	40	1
740	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	130	1
741	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
742	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	750	1
743	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
744	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
745	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
746	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	pH_stable	1	1	100	1
747	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
748	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	80	1
749	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	pH_stable	1	1	20	1
750	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1000	1
751	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	130	1
752	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	30	1
753	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity_profile_long_range	1	1	500	1
754	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
755	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	oxygen_dissolved_stable	1	1	80	1
756	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	80	1
757	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD_bottom_pumped	1	1	12	1
758	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem_acoustic	1	1	12	1
759	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	130	1
760	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
761	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	oxygen_dissolved_stable	1	1	2400	1
762	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
763	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	oxygen_dissolved_stable	1	1	4600	1
764	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
765	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
766	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem_acoustic	1	1	40	1
767	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	180	1
768	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	attenuation_absorption_optical	1	1	12	1
769	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	spectral_irradiance	1	1	5	1
770	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD_bottom_pumped	1	1	80	1
771	ACOMM	Modem_acoustic		M	\N	Modem_acoustic	1	1	1000	1
772	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	40	1
773	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
774	DOSTA	oxygen_dissolved_stable		M	\N	oxygen_dissolved_stable	1	1	1000	1
775	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
776	CTDGV	CTD_glider		M	\N	CTD_glider	1	1	1000	1
777	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	Fluorometer_three_wavelength	1	1	40	1
778	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	nutrient_Nitrate	1	1	12	1
779	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2_water	1	1	40	1
780	PARAD	PAR		M	\N	PAR	1	1	1000	1
781	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	750	1
782	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	1500	1
783	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD_mooring	1	1	1000	1
784	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	Fluorometer_two_wavelength	1	1	4600	1
785	PHSEN	pH_stable	Sensor cage	E	\N	pH_stable	1	1	40	1
786	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	oxygen_dissolved_stable	1	1	40	1
787	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2_water	1	1	12	1
788	FDCHP	flux_direct_cov_HP	Buoy Tower 5 M	A	\N	flux_direct_cov_HP	1	1	5	1
789	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	60	1
790	FLORD	Fluorometer_two_wavelength		M	\N	Fluorometer_two_wavelength	1	1	1000	1
791	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	Motion Pack	1	1	0	1
792	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD_profiler	1	1	4600	1
793	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	250	1
794	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	Fluorometer_two_wavelength	1	1	40	1
795	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD_mooring	1	1	1500	1
796	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD_mooring	1	1	90	1
\.


--
-- Data for Name: streams; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY streams (id, stream_name, instrument_id, description) FROM stdin;
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY datasets (id, stream_id, deployment_id, process_level, is_recovered) FROM stdin;
\.


--
-- Data for Name: dataset_keywords; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY dataset_keywords (id, dataset_id, concept_name, concept_description) FROM stdin;
\.


--
-- Name: dataset_keywords_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('dataset_keywords_id_seq', 1, false);


--
-- Name: datasets_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('datasets_id_seq', 1, false);


--
-- Name: deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('deployments_id_seq', 1, false);


--
-- Data for Name: drivers; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY drivers (id, instrument_id, driver_name, driver_version, author) FROM stdin;
\.


--
-- Data for Name: driver_stream_link; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY driver_stream_link (id, driver_id, stream_id) FROM stdin;
\.


--
-- Name: driver_stream_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('driver_stream_link_id_seq', 1, false);


--
-- Name: drivers_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('drivers_id_seq', 1, false);


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('files_id_seq', 1, false);


--
-- Data for Name: inspection_status; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY inspection_status (id, asset_id, file_id, status, technician_name, comments, inspection_date, document) FROM stdin;
\.


--
-- Name: inspection_status_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('inspection_status_id_seq', 1, false);


--
-- Data for Name: installation_record; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY installation_record (id, asset_id, assembly_id, date_installed, date_removed, technician_name, comments, file_id) FROM stdin;
\.


--
-- Name: installation_record_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('installation_record_id_seq', 1, false);


--
-- Data for Name: platforms; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY platforms (id, platform_name, description, location_description, platform_series, is_mobile, serial_no, asset_id, manufacturer_id) FROM stdin;
1	CE01ISSM-LM001	Endurance OR Inshore Surface Mooring	Endurance OR  (25 m) Inshore Surface Mooring		f		1	1
2	CE01ISSM-MFD00	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	1
3	CE01ISSM-MFD35	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	1
4	CE01ISSM-MFD37	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	1
5	CE01ISSM-RID16	Endurance OR Inshore Surface Mooring	Mooring Riser		f		1	1
6	CE01ISSM-SBD17	Endurance OR Inshore Surface Mooring	Surface Buoy		f		1	1
7	CE01ISSP-CP001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	1
8	CE01ISSP-PL001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	1
9	CE01ISSP-SP001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	1
10	CE02SHBP-BP001	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	1
11	CE02SHBP-LJ01D	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	1
12	CE02SHBP-MJ01C	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	1
13	CE02SHSM-RID26	Endurance OR Shelf Surface Mooring	Mooring Riser		f		1	1
14	CE02SHSM-RID27	Endurance OR Shelf Surface Mooring	Mooring Riser		f		1	1
15	CE02SHSM-SBD11	Endurance OR Shelf Surface Mooring	Surface Buoy		f		1	1
16	CE02SHSM-SBD12	Endurance OR Shelf Surface Mooring	Surface Buoy		f		1	1
17	CE02SHSM-SM001	Endurance OR Shelf Surface Mooring	Endurance OR Shelf  (80 m) Surface Mooring		f		1	1
18	CE02SHSP-CP001	Endurance OR Shelf Surface-Piercing Profiler Mooring	Endurance OR Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	1
19	CE02SHSP-SP001	Endurance OR Shelf Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	1
20	CE04OSBP-BP001	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	1
21	CE04OSBP-LJ01C	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	1
22	CE04OSBP-LV01C	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	1
23	CE04OSHY-DP01B	Endurance OR Offshore Hybrid Profiler Mooring	Deep Profiler		f		1	1
24	CE04OSHY-GP001	Endurance OR Offshore Hybrid Profiler Mooring	Endurance OR Offshore (500 m) Hybrid Profiler Mooring		f		1	1
25	CE04OSHY-PC01B	Endurance OR Offshore Hybrid Profiler Mooring	200m Platform		f		1	1
26	CE04OSHY-SF01B	Endurance OR Offshore Hybrid Profiler Mooring	Shallow Profiler		f		1	1
27	CE04OSSM-RID26	Endurance OR Offshore Surface Mooring	Mooring Riser		f		1	1
28	CE04OSSM-RID27	Endurance OR Offshore Surface Mooring	Mooring Riser		f		1	1
29	CE04OSSM-SBD11	Endurance OR Offshore Surface Mooring	Surface Buoy		f		1	1
30	CE04OSSM-SBD12	Endurance OR Offshore Surface Mooring	Surface Buoy		f		1	1
31	CE04OSSM-SM001	Endurance OR Offshore Surface Mooring	Endurance OR Offshore (500 m) Surface Mooring		f		1	1
32	CE05MOAS-GL001	Endurance Mobile Assets	Endurance Glider 1		f		1	1
33	CE05MOAS-GL002	Endurance Mobile Assets	Endurance Glider 2		f		1	1
34	CE05MOAS-GL003	Endurance Mobile Assets	Endurance Glider 3		f		1	1
35	CE05MOAS-GL004	Endurance Mobile Assets	Endurance Glider 4		f		1	1
36	CE05MOAS-GL005	Endurance Mobile Assets	Endurance Glider 5		f		1	1
37	CE05MOAS-GL006	Endurance Mobile Assets	Endurance Glider 6		f		1	1
38	CE06ISSM-LM001	Endurance WA Inshore Surface Mooring	Endurance WA Inshore (25 m) Surface Mooring		f		1	1
39	CE06ISSM-MFD00	Endurance WA Inshore Surface Mooring	MFN		f		1	1
40	CE06ISSM-MFD35	Endurance WA Inshore Surface Mooring	MFN		f		1	1
41	CE06ISSM-MFD37	Endurance WA Inshore Surface Mooring	MFN		f		1	1
42	CE06ISSM-RID16	Endurance WA Inshore Surface Mooring	Mooring Riser		f		1	1
43	CE06ISSM-SBD17	Endurance WA Inshore Surface Mooring	Surface Buoy		f		1	1
44	CE06ISSP-CP001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	1
45	CE06ISSP-PL001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	1
46	CE06ISSP-SP001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	1
47	CE07SHSM-HM001	Endurance WA Shelf Surface Mooring	Endurance WA Shelf (80 m) Surface Mooring		f		1	1
48	CE07SHSM-MFD00	Endurance WA Shelf Surface Mooring	MFN		f		1	1
49	CE07SHSM-MFD35	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	1
50	CE07SHSM-MFD37	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	1
51	CE07SHSM-RID26	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	1
52	CE07SHSM-RID27	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	1
53	CE07SHSM-SBD11	Endurance WA Shelf Surface Mooring	Surface Buoy		f		1	1
54	CE07SHSM-SBD12	Endurance WA Shelf Surface Mooring	Surface Buoy		f		1	1
55	CE07SHSP-CP001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	1
56	CE07SHSP-PL001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	1
57	CE07SHSP-SP001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	1
58	CE090SSM-MFD00	Endurance WA Offshore Surface Mooring	MFN		f		1	1
59	CE09OSPM-PM001	Endurance WA Offshore Profiling Mooring	Endurance WA Offshore (500 m) Profiler Mooring		f		1	1
60	CE09OSPM-WF001	Endurance WA Offshore Profiling Mooring	Wire-Following Profiler		f		1	1
61	CE09OSSM-HM001	Endurance WA Offshore Surface Mooring	Endurance WA Offshore (500 m) Surface Mooring		f		1	1
62	CE09OSSM-MFD00	Endurance WA Offshore Surface Mooring	MFN		f		1	1
63	CE09OSSM-MFD35	Endurance WA Offshore Surface Mooring	MFN		f		1	1
64	CE09OSSM-MFD37	Endurance WA Offshore Surface Mooring	MFN		f		1	1
65	CE09OSSM-RID26	Endurance WA Offshore Surface Mooring	Mooring Riser		f		1	1
66	CE09OSSM-RID27	Endurance WA Offshore Surface Mooring	Mooring Riser		f		1	1
67	CE09OSSM-SBD11	Endurance WA Offshore Surface Mooring	Surface Buoy		f		1	1
68	CE09OSSM-SBD12	Endurance WA Offshore Surface Mooring	Surface Buoy		f		1	1
69	GP02HYPM-GP001	PAPA Hybrid Mooring	Hybrid Mooring		f		1	1
70	GP02HYPM-MPC04	PAPA Hybrid Mooring	Mid-water Platform		f		1	1
71	GP02HYPM-RIS01	PAPA Hybrid Mooring	Mooring Riser		f		1	1
72	GP02HYPM-WFP02	PAPA Hybrid Mooring	Wire-Following Profiler #1		f		1	1
73	GP02HYPM-WFP03	PAPA Hybrid Mooring	Wire-Following Profiler #2		f		1	1
74	GP03FLMA-FM001	PAPA Flanking Moorings	Flanking Mooring A		f		1	1
75	GP03FLMA-RIS01	PAPA Flanking Moorings	Mooring Riser		f		1	1
76	GP03FLMA-RIS02	PAPA Flanking Moorings	Mooring Riser		f		1	1
77	GP03FLMB-FM001	PAPA Flanking Moorings	Flanking Mooring B		f		1	1
78	GP03FLMB-RIS01	PAPA Flanking Moorings	Mooring Riser		f		1	1
79	GP03FLMB-RIS02	PAPA Flanking Moorings	Mooring Riser		f		1	1
80	GP05MOAS-GL001	PAPA Mobile Assets	Glider 1		f		1	1
81	GP05MOAS-GL002	PAPA Mobile Assets	Glider 2		f		1	1
82	GP05MOAS-GL003	PAPA Mobile Assets	Glider 3		f		1	1
83	GP05MOAS-PG001	PAPA Mobile Assets	Global Profiling Glider 1		f		1	1
84	GP05MOAS-PG002	PAPA Mobile Assets	Global Profiling Glider 2		f		1	1
85	CP01CNSM-HM001	Pioneer Central P1 Surface Mooring	Pioneer Central P1 Surface Mooring		f		1	1
86	CP01CNSM-MFD00	Pioneer Central P1 Surface Mooring	MFN		f		1	1
87	CP01CNSM-MFD35	Pioneer Central P1 Surface Mooring	MFN		f		1	1
88	CP01CNSM-MFD37	Pioneer Central P1 Surface Mooring	MFN		f		1	1
89	CP01CNSM-RID26	Pioneer Central P1 Surface Mooring	Mooring Riser		f		1	1
90	CP01CNSM-RID27	Pioneer Central P1 Surface Mooring	Mooring Riser		f		1	1
91	CP01CNSM-SBD11	Pioneer Central P1 Surface Mooring	Surface Buoy		f		1	1
92	CP01CNSM-SBD12	Pioneer Central P1 Surface Mooring	Surface Buoy		f		1	1
93	CP01CNSP-CP001	Pioneer Central P1 Surface-Piercing Profiler	Pioneer Central P1 Surface-Piercing Profiler		f		1	1
94	CP01CNSP-PL001	Pioneer Central P1 Surface-Piercing Profiler	Pioneer Central P1 Surface-Piercing Profiler		f		1	1
95	CP01CNSP-SP001	Pioneer Central P1 Surface-Piercing Profiler	Surface-Piercing Profiler		f		1	1
96	CP02PMCI-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Central Inshore Wire-Following Profiler Mooring		f		1	1
97	CP02PMCI-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
98	CP02PMCI-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
99	CP02PMCI-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	1
100	CP02PMCO-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Central Offshore Wire-Following Profiler Mooring		f		1	1
101	CP02PMCO-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
102	CP02PMCO-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
103	CP02PMCO-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	1
104	CP02PMUI-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Upstream Inshore Wire-Following Profiler Mooring		f		1	1
105	CP02PMUI-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
106	CP02PMUI-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
107	CP02PMUI-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	1
108	CP02PMUO-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Upstream Offshore Wire-Following Profiler Mooring		f		1	1
109	CP02PMUO-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
110	CP02PMUO-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	1
111	CP02PMUO-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	1
112	CP03ISSM-HM001	Pioneer Inshore P3 Surface Mooring	Pioneer Inshore P3 Surface Mooring		f		1	1
113	CP03ISSM-MFD00	Pioneer Inshore P3 Surface Mooring	MFN		f		1	1
114	CP03ISSM-MFD35	Pioneer Inshore P3 Surface Mooring	MFN		f		1	1
115	CP03ISSM-MFD37	Pioneer Inshore P3 Surface Mooring	MFN		f		1	1
116	CP03ISSM-RID26	Pioneer Inshore P3 Surface Mooring	Mooring Riser		f		1	1
117	CP03ISSM-RID27	Pioneer Inshore P3 Surface Mooring	Mooring Riser		f		1	1
118	CP03ISSM-SBD11	Pioneer Inshore P3 Surface Mooring	Surface Buoy		f		1	1
119	CP03ISSM-SBD12	Pioneer Inshore P3 Surface Mooring	Surface Buoy		f		1	1
120	CP03ISSP-CP001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Pioneer Inshore P3 Surface-Piercing Profiler Mooring		f		1	1
121	CP03ISSP-PL001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Pioneer Inshore P3 Surface-Piercing Profiler Mooring		f		1	1
122	CP03ISSP-SP001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	1
123	CP04OSPM-PM001	Pioneer Offshore P4 Wire-Following Profiler Mooring	Pioneer Offshore Wire-Following Profiler Mooring		f		1	1
124	CP04OSPM-SBS11	Pioneer Offshore P4 Wire-Following Profiler Mooring	Surface Buoy		f		1	1
125	CP04OSPM-WFP01	Pioneer Offshore P4 Wire-Following Profiler Mooring	Wire-Following Profiler		f		1	1
126	CP04OSSM-HM001	Pioneer Offshore P4 Surface Mooring	Pioneer Offshore P4 Surface Mooring		f		1	1
127	CP04OSSM-MFD00	Pioneer Offshore P4 Surface Mooring	MFN		f		1	1
128	CP04OSSM-MFD35	Pioneer Offshore P4 Surface Mooring	MFN		f		1	1
129	CP04OSSM-MFD37	Pioneer Offshore P4 Surface Mooring	MFN		f		1	1
130	CP04OSSM-RID26	Pioneer Offshore P4 Surface Mooring	Mooring Riser		f		1	1
131	CP04OSSM-RID27	Pioneer Offshore P4 Surface Mooring	Mooring Riser		f		1	1
132	CP04OSSM-SBD11	Pioneer Offshore P4 Surface Mooring	Surface Buoy		f		1	1
133	CP04OSSM-SBD12	Pioneer Offshore P4 Surface Mooring	Surface Buoy		f		1	1
134	CP05MOAS-AV001	Pioneer Mobile Assets	Pioneer AUV 1		f		1	1
135	CP05MOAS-AV002	Pioneer Mobile Assets	Pioneer AUV 2		f		1	1
136	CP05MOAS-GL001	Pioneer Mobile Assets	Pioneer Glider 1		f		1	1
137	CP05MOAS-GL002	Pioneer Mobile Assets	Pioneer Glider 2		f		1	1
138	CP05MOAS-GL003	Pioneer Mobile Assets	Pioneer Glider 3		f		1	1
139	CP05MOAS-GL004	Pioneer Mobile Assets	Pioneer Glider 4		f		1	1
140	CP05MOAS-GL005	Pioneer Mobile Assets	Pioneer Glider 5		f		1	1
141	CP05MOAS-GL006	Pioneer Mobile Assets	Pioneer Glider 6		f		1	1
142	GA01SUMO-RID16	Argentine Surface Mooring	Mooring Riser		f		1	1
143	GA01SUMO-RII11	Argentine Surface Mooring	Mooring Riser		f		1	1
144	GA01SUMO-SBD11	Argentine Surface Mooring	Surface Buoy		f		1	1
145	GA01SUMO-SBD12	Argentine Surface Mooring	Surface Buoy		f		1	1
146	GA01SUMO-SM001	Argentine Surface Mooring	Surface Mooring		f		1	1
147	GA02HYPM-GP001	Argentine Hybrid Mooring	Hybrid Mooring		f		1	1
148	GA02HYPM-MPC04	Argentine Hybrid Mooring	Mid-water Platform		f		1	1
149	GA02HYPM-RIS01	Argentine Hybrid Mooring	Mooring Riser		f		1	1
150	GA02HYPM-WFP02	Argentine Hybrid Mooring	Wire-Following Profiler #1		f		1	1
151	GA02HYPM-WFP03	Argentine Hybrid Mooring	Wire-Following Profiler #2		f		1	1
152	GA03FLMA-FM001	Argentine Flanking Moorings	Flanking Mooring A		f		1	1
153	GA03FLMA-RIS01	Argentine Flanking Moorings	Mooring Riser		f		1	1
154	GA03FLMA-RIS02	Argentine Flanking Moorings	Mooring Riser		f		1	1
155	GA03FLMB-FM001	Argentine Flanking Moorings	Flanking Mooring B		f		1	1
156	GA03FLMB-RIS01	Argentine Flanking Moorings	Mooring Riser		f		1	1
157	GA03FLMB-RIS02	Argentine Flanking Moorings	Mooring Riser		f		1	1
158	GA05MOAS-GL001	Argentine Mobile Assets	Glider No. 1		f		1	1
159	GA05MOAS-GL002	Argentine Mobile Assets	Glider No. 2		f		1	1
160	GA05MOAS-GL003	Argentine Mobile Assets	Glider No. 3		f		1	1
161	GA05MOAS-PG001	Argentine Mobile Assets	Global Profiling Glider 1		f		1	1
162	GA05MOAS-PG002	Argentine Mobile Assets	Global Profiling Glider 2		f		1	1
163	GI01SUMO-RID16	Irminger Sea Surface Mooring	Mooring Riser		f		1	1
164	GI01SUMO-RII11	Irminger Sea Surface Mooring	Mooring Riser		f		1	1
165	GI01SUMO-SBD11	Irminger Sea Surface Mooring	Surface Buoy		f		1	1
166	GI01SUMO-SBD12	Irminger Sea Surface Mooring	Surface Buoy		f		1	1
167	GI01SUMO-SM001	Irminger Sea Surface Mooring	Surface Mooring		f		1	1
168	GI02HYPM-GP001	Irminger Sea Hybrid Mooring	Hybrid Mooring		f		1	1
169	GI02HYPM-MPC04	Irminger Sea Hybrid Mooring	Mid-water Platform		f		1	1
170	GI02HYPM-RIS01	Irminger Sea Hybrid Mooring	Mooring Riser		f		1	1
171	GI02HYPM-WFP02	Irminger Sea Hybrid Mooring	Wire-Following Profiler		f		1	1
172	GI03FLMA-FM001	Irminger Sea Flanking Moorings	Flanking Mooring A		f		1	1
173	GI03FLMA-RIS01	Irminger Sea Flanking Moorings	Mooring Riser		f		1	1
174	GI03FLMA-RIS02	Irminger Sea Flanking Moorings	Mooring Riser		f		1	1
175	GI03FLMB-FM001	Irminger Sea Flanking Moorings	Flanking Mooring B		f		1	1
176	GI03FLMB-RIS01	Irminger Sea Flanking Moorings	Mooring Riser		f		1	1
177	GI03FLMB-RIS02	Irminger Sea Flanking Moorings	Mooring Riser		f		1	1
178	GI05MOAS-GL001	Irminger Sea Mobile Assets	Glider No. 1		f		1	1
179	GI05MOAS-GL002	Irminger Sea Mobile Assets	Glider No. 2		f		1	1
180	GI05MOAS-GL003	Irminger Sea Mobile Assets	Glider No. 3		f		1	1
181	GI05MOAS-PG001	Irminger Sea Mobile Assets	Global Profiling Glider 1		f		1	1
182	GI05MOAS-PG002	Irminger Sea Mobile Assets	Global Profiling Glider 2		f		1	1
183	GS01SUMO-RID16	55S Surface Mooring	Mooring Riser		f		1	1
184	GS01SUMO-RII11	55S Surface Mooring	Mooring Riser		f		1	1
185	GS01SUMO-SBD11	55S Surface Mooring	Surface Buoy		f		1	1
186	GS01SUMO-SBD12	55S Surface Mooring	Surface Buoy		f		1	1
187	GS01SUMO-SM001	55S Surface Mooring	Surface Mooring		f		1	1
188	GS02HYPM-GP001	55S Hybrid Mooring	Hybrid Mooring		f		1	1
189	GS02HYPM-MPC04	55S Hybrid Mooring	Mid-water Platform		f		1	1
190	GS02HYPM-RIS01	55S Hybrid Mooring	Mooring Riser		f		1	1
191	GS02HYPM-WFP02	55S Hybrid Mooring	Wire-Following Profiler #1		f		1	1
192	GS02HYPM-WFP03	55S Hybrid Mooring	Wire-Following Profiler #2		f		1	1
193	GS03FLMA-FM001	55S Flanking Moorings	Flanking Mooring A		f		1	1
194	GS03FLMA-RIS01	55S Flanking Moorings	Mooring Riser		f		1	1
195	GS03FLMA-RIS02	55S Flanking Moorings	Mooring Riser		f		1	1
196	GS03FLMB-FM001	55S Flanking Moorings	Flanking Mooring B		f		1	1
197	GS03FLMB-RIS01	55S Flanking Moorings	Mooring Riser		f		1	1
198	GS03FLMB-RIS02	55S Flanking Moorings	Mooring Riser		f		1	1
199	GS05MOAS-GL001	55S Mobile Assets	Glider No. 1		f		1	1
200	GS05MOAS-GL002	55S Mobile Assets	Glider No. 2		f		1	1
201	GS05MOAS-GL003	55S Mobile Assets	Glider No. 3		f		1	1
202	GS05MOAS-PG001	55S Mobile Assets	Global Profiling Glider 1		f		1	1
203	GS05MOAS-PG002	55S Mobile Assets	Global Profiling Glider 2		f		1	1
\.


--
-- Data for Name: platform_deployments; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY platform_deployments (id, start_date, end_date, platform_id, reference_designator, array_id, deployment_id, display_name, geo_location) FROM stdin;
1	\N	\N	1	OOIREF1	1	1	OOIREF1	\N
\.


--
-- Data for Name: instrument_deployments; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY instrument_deployments (id, display_name, start_date, end_date, platform_deployment_id, instrument_id, reference_designator, depth, geo_location) FROM stdin;
1	DEPLOYME	\N	\N	1	1	OOIREF1	\N	\N
\.


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_deployments_id_seq', 1, false);


--
-- Name: instrument_models_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_models_id_seq', 1, true);


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('instruments_id_seq', 796, true);


--
-- Name: manufacturers_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('manufacturers_id_seq', 1, true);


--
-- Name: organizations_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('organizations_id_seq', 1, false);


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('platform_deployments_id_seq', 1, false);


--
-- Name: platforms_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('platforms_id_seq', 203, true);


--
-- Data for Name: stream_parameters; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY stream_parameters (id, stream_parameter_name, short_name, long_name, standard_name, units, data_type) FROM stdin;
\.


--
-- Data for Name: stream_parameter_link; Type: TABLE DATA; Schema: ooiui_jdc1; Owner: oceanzus
--

COPY stream_parameter_link (id, stream_id, parameter_id) FROM stdin;
\.


--
-- Name: stream_parameter_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameter_link_id_seq', 1, false);


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameters_id_seq', 1, false);


--
-- Name: streams_id_seq; Type: SEQUENCE SET; Schema: ooiui_jdc1; Owner: oceanzus
--

SELECT pg_catalog.setval('streams_id_seq', 1, false);


SET search_path = ooiui_testing, pg_catalog;

--
-- Data for Name: organizations; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY organizations (id, organization_name) FROM stdin;
1	ASA
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY users (id, user_id, pass_hash, email, user_name, active, confirmed_at, first_name, last_name, phone_primary, phone_alternate, organization_id) FROM stdin;
\.


--
-- Data for Name: annotations; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY annotations (id, user_id, created_time, modified_time, reference_name, reference_type, reference_pk_id, title, comment) FROM stdin;
\.


--
-- Name: annotations_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('annotations_id_seq', 1, false);


--
-- Data for Name: arrays; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY arrays (id, array_code, description, geo_location, array_name, display_name) FROM stdin;
1	CE		0103000020E610000001000000050000008FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC08FC2F5285C2F46406666666666864BC0	Endurance (CE)	Coastal Endurance
2	GP		0103000020E610000001000000050000004C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C04C37894160FD4840746891ED7CDF41C0	PAPA (GP)	Global Station Papa
3	CP		0103000020E61000000100000005000000CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0	Pioneer (CP)	Coastal Pioneer
4	GA		0103000020E6100000010000000500000062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C0	Argentine (GA)	Argentine Basin
5	GI		0103000020E610000001000000050000007B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C0	Irminger (GI)	Irminger Sea
6	GS		0103000020E610000001000000050000007CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C0	55 S (GS)	Southern Ocean
\.


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('arrays_id_seq', 6, true);


--
-- Data for Name: assemblies; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY assemblies (id, assembly_name, description) FROM stdin;
1	Default Assembly	\N
\.


--
-- Data for Name: asset_types; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY asset_types (id, asset_type_name) FROM stdin;
1	Glider
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY assets (id, asset_type_id, organization_id, supplier_id, deployment_id, asset_name, model, current_lifecycle_state, part_number, firmware_version, geo_location) FROM stdin;
1	1	1	1	1	some glider	some model	DEPLOYED	pn-1	fw1.0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY files (id, user_id, file_name, file_system_path, file_size, file_permissions, file_type) FROM stdin;
\.


--
-- Data for Name: asset_file_link; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY asset_file_link (id, asset_id, file_id) FROM stdin;
\.


--
-- Name: asset_file_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_file_link_id_seq', 1, false);


--
-- Name: asset_types_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('asset_types_id_seq', 1, true);


--
-- Name: assets_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('assets_id_seq', 1, true);


--
-- Name: asssemblies_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('asssemblies_id_seq', 1, true);


--
-- Data for Name: deployments; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY deployments (id, start_date, end_date, cruise_id) FROM stdin;
1	\N	\N	\N
\.


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY manufacturers (id, manufacturer_name, phone_number, contact_name, web_address) FROM stdin;
1	Aanderaa	937-767-7241		http://www.aanderaa.com
2	Axys Technologies	250-655-5850		http://axystechnologies.com/
3	Biospherical Instruments	619-686-1888		http://www.biospherical.com/
4	Falmouth Scientific	508-564-7640		http://www.falmouth.com
5	Guralp	44-118-981-9056		http://www.guralp.com/
6	HTI	541-917-3335		http://www.htiwater.com
7	Kongsberg	44-1224-226500		http://www.kongsberg.com/
8	Marv Lilley lab	206-543-0859	Marv Lilley	http://www.ocean.washington.edu/home/Marvin+Lilley
9	Nobska	508-289-2725		http://www.nobska.net/
10	Nortek	47-6717-4500		http://www.nortek-as.com/
11	Ocean Sonics	855-360-3003		http://oceansonics.com/
12	Pro-Oceanus	855-530-3550		http://www.pro-oceanus.com
13	RBR Global	613-599-8900		www.rbr-global.com/
14	Satlantic	902-492-4780		http://www.salantic.com
15	Sea-Bird	425-643-9866		www.seabird.com/
16	Star Engineering	508-316-1492		http://starengineeringinc.com/markets/marine-navigation/
17	SubC	709-702-0395		http://subcimaging.com
18	Sunburst Sensors	406-532-3246		www.sunburstsensors.com/
19	TLR, Inc.	831-236-7121		http://www.tlrinc.biz/index.html
20	Teledyne RDI	858-842-2600		www.rdinstruments.com/
21	WET Labs	401-783-1787		www.wetlabs.com/
22	WHOI	508-289-2508	Robert A. Weller	http://www.whoi.edu/hpb/viewPage.do?id=8176
23	non-commercial			
24	unknown			
\.


--
-- Data for Name: instrument_models; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY instrument_models (id, instrument_model_name, series_name, class_name, manufacturer_id) FROM stdin;
1	Optode 4831	D	DOSTA	1
2	Optode 4831	M	DOSTA	1
3	Optode 4330	N	DOSTA	1
4	Optode 4330	L	DOSTA	1
5	TRIAXYS	A	WAVSS	2
6	QSP-2150	N	PARAD	3
7	QSP-2155	M	PARAD	3
8	QSP-2200	K	PARAD	3
9	ACM-3D-MP	A	VEL3D	4
10	ACM-Plus	L	VEL3D	4
11	Guralp (CMG-1 sec)	A	OBSSP	5
12	CMG-1T/5T	A	OBSBK	5
13	CMG-1T/5T	A	OBSBB	5
14	90-U	A	HYDLF	6
15	Modified EK-60	B	ZPLSC	7
16	Modified OE14-408	C	CAMDS	7
17	Modified OE14-408	B	CAMDS	7
18	Modified OE14-408	A	CAMDS	7
19	MAVS-4	B	VEL3D	9
20	Aquadopp II	K	VEL3D	10
21	Aquadopp 3000m	B	VELPT	10
22	VECTOR	D	VEL3D	10
23	VECTOR	C	VEL3D	10
24	Aquadopp	J	VEL3D	10
25	Aquadopp	D	VELPT	10
26	Aquadopp 300m	A	VELPT	10
27	icListen HF	A	HYDBB	11
28	pCO2-pro	A	PCO2A	12
29	XR-420	A	TMPSF	13
30	ISUS	B	NUTNR	14
31	SUNA	N	NUTNR	14
32	Deep SUNA	A	NUTNR	14
33	OCR507 ICSW	B	SPKIR	14
34	OCR507 ICSW	A	SPKIR	14
35	digital PAR	A	PARAD	14
36	SBE 16plusV2	A	CTDBP	15
37	SBE 16plusV2	B	CTDBP	15
38	SBE 16plusV2	C	CTDBP	15
39	SBE 16plusV2	D	CTDBP	15
40	SBE 16plusV2	E	CTDBP	15
41	SBE 16plusV2	F	CTDBP	15
42	SBE 16plusV2	N	CTDBP	15
43	SBE 16plusV2	O	CTDBP	15
44	SBE 16plusV2	A	CTDPF	15
45	SBE Glider Payload CTD (GP-CTD)	N	CTDAV	15
46	SBE Glider Payload CTD (GP-CTD)	M	CTDAV	15
47	SBE Glider Payload CTD (GP-CTD)	M	CTDGV	15
48	SBE 54	A	PREST	15
49	SBE 54	B	PREST	15
50	SBE 52MP	K	CTDPF	15
51	SBE 52MP	L	CTDPF	15
52	SBE 43F	K	DOFST	15
53	SBE 26plus	A	PRESF	15
54	SBE 26plus	B	PRESF	15
55	SBE 26plus	C	PRESF	15
56	SBE 43	A	DOFST	15
57	SBE 37IM	Q	CTDMO	15
58	SBE 37IM	R	CTDMO	15
59	SBE 37IM	G	CTDMO	15
60	SBE 37IM	H	CTDMO	15
61	ASIMET	A	METBK	16
62	1Cam	A	CAMHD	17
63	SAMI-pH	D	PHSEN	18
64	SAMI-pH	E	PHSEN	18
65	SAMI-pH	F	PHSEN	18
66	SAMI-pH	A	PHSEN	18
67	SAMI-pCO2	B	PCO2W	18
68	SAMI-pCO2	A	PCO2W	18
69	OsmoSampler	A	OSMOI	19
70	Workhorse Navigator 600 kHz dual	N	ADCPA	20
71	Explorer DVL 600 kHz	M	ADCPA	20
72	WorkHorse LongRanger Monitor 75khz	K	ADCPS	20
73	WorkHorse LongRanger Monitor 75khz	I	ADCPS	20
74	WorkHorse LongRanger Sentinel 75khz	L	ADCPS	20
75	WorkHorse LongRanger Sentinel 75khz	J	ADCPS	20
76	WorkHorse LongRanger Sentinel 75khz	N	ADCPS	20
77	WorkHorse Monitor 300khz	B	ADCPT	20
78	WorkHorse Sentinel 300khz	C	ADCPT	20
79	WorkHorse Sentinel 600khz	A	ADCPT	20
80	WorkHorse Sentinel 600khz	M	ADCPT	20
81	WorkHorse Sentinel150khz	G	ADCPT	20
82	WorkHorse Sentinel150khz	F	ADCPT	20
83	Workhorse Quartermaster 150kHz	E	ADCPT	20
84	Workhorse Quartermaster 150kHz	D	ADCPT	20
85	Workhorse custom 600 kHz 5 Beam	A	VADCP	20
86	AC-S	D	OPTAA	21
87	AC-S	C	OPTAA	21
88	FLNTURTD (chlorophyll and backscatter), and FLCDRTD (CDOM)	A	FLORT	21
89	ECO Triplet-w	D	FLORT	21
90	ECO Triplet	K	FLORT	21
91	ECO Triplet	N	FLORT	21
92	ECO Puck FLBBCD-SLK	M	FLORT	21
93	ECO Puck FLBB-SLC	M	FLORD	21
94	FLBBRTD	L	FLORD	21
95	DCFS	A	FDCHP	22
96	non-commercial PPSDN	A	PPSDN	23
97	non-commercial RASFL	A	RASFL	23
98	non-commercial TRHPH	A	TRHPH	23
99	non-commercial BOTPT	A	BOTPT	23
100	non-commercial FLOBN	A	FLOBN	23
101	non-commercial HPIES	A	HPIES	23
102	non-commercial MASSP	A	MASSP	23
103	non-commercial THSPH	A	THSPH	23
104	unknown	0	ACOMM	24
105	unknown	M	ACOMM	24
106	unknown	0	MOPAK	24
107	unknown	P	CTDBP	24
108	unknown	G	FLORD	24
109	unknown	C	PCO2W	24
110	unknown	C	ZPLSC	24
111	unknown	A	ZPLSG	24
112	unknown	J	DOFST	24
113	unknown	J	PARAD	24
114	unknown	J	OPTAA	24
115	unknown	J	NUTNR	24
116	unknown	J	SPKIR	24
117	unknown	J	CTDPF	24
118	unknown	J	FLORT	24
119	unknown	J	VELPT	24
120	unknown	O	SPKIR	24
121	unknown	O	PCO2W	24
122	unknown	O	DOSTA	24
123	unknown	O	OPTAA	24
124	unknown	O	NUTNR	24
125	unknown	O	FLORD	24
126	unknown	O	CTDPF	24
127	unknown	M	OPTAA	24
128	unknown	J	DOSTA	24
129	unknown	M	NUTNR	24
\.


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY instruments (id, instrument_name, description, location_description, instrument_series, serial_number, display_name, model_id, asset_id, depth_rating, manufacturer_id) FROM stdin;
1	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	25	24
2	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	80	24
3	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	80	24
4	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
5	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
6	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	500	18
7	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	25	10
8	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	25	24
9	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	25	24
10	VEL3D	Velocity_point_3D_turb	Benthic Package (J Box)	C	\N	3-D Single Point Velocity Meter	23	1	500	10
11	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
12	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
13	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	A	\N	Velocity Profiler (short range)	79	1	5	20
14	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
15	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
16	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
17	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
18	ADCPT	Velocity_profile_short_range	MFN	M	\N	Velocity Profiler (short range)	80	1	25	20
19	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	80	24
20	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	500	21
21	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
22	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
23	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	5	18
24	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	25	24
25	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	80	21
26	PCO2W	pCO2_water	Benthic Package (J Box)	B	\N	pCO2 Water	67	1	80	18
27	HYDBB	Hydrophone_BB_passive	Benthic Package (J Box)	A	\N	Broadband Acoustic Receiver (Hydrophone)	27	1	80	11
28	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	25	21
29	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
30	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
31	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
32	DOSTA	oxygen_dissolved_stable	Benthic Package (J Box)	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
33	ADCPT	Velocity_profile_short_range	MFN	M	\N	Velocity Profiler (short range)	80	1	25	20
34	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	25	24
35	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
36	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	25	18
37	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
38	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	25	24
39	CAMDS	camera_digital_still_strobe	Benthic Package (J Box) - via wet/mate connector	B	\N	Digital Still Camera with Strobes	17	1	500	7
40	PCO2W	pCO2_water	Benthic Package (J Box)	B	\N	pCO2 Water	67	1	500	18
41	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
42	SPKIR	spectral_irradiance	shallow profiling body	A	\N	Spectral Irradiance	34	1	200	14
43	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
44	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	80	24
45	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
46	FLORT	Fluorometer_three_wavelength	shallow profiling body	D	\N	3-Wavelength Fluorometer	89	1	200	21
47	NUTNR	nutrient_Nitrate	shallow profiling body	A	\N	Nitrate	32	1	200	14
48	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
49	PRESF	pressure_SF	MFN	A	\N	Seafloor Pressure	53	1	25	15
50	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
51	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
52	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
53	CTDPF	CTD_profiler	shallow profiling body	A	\N	CTD Profiler	44	1	200	15
54	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
55	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
56	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
57	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
58	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
59	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
60	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	80	24
245	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
61	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
62	CTDBP	CTD_bottom_pumped	Benthic Package (J Box)	O	\N	CTD Pumped	43	1	500	15
63	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
64	HYDBB	Hydrophone_BB_passive	Benthic Package (J Box)	A	\N	Broadband Acoustic Receiver (Hydrophone)	27	1	500	11
65	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
66	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	25	24
67	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	25	24
68	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	25	18
69	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
70	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	25	18
71	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	80	24
72	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
73	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	25	24
74	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
75	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
76	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
77	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
78	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
79	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	80	18
80	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
81	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
82	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
83	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
84	OPTAA	attenuation_absorption_optical	Benthic Package (J Box)	C	\N	Absorption Spectrophotometer	87	1	500	21
85	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	25	24
86	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	25	24
87	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	500	15
88	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	25	24
89	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	25	24
90	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
91	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
92	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
93	ADCPS	Velocity_profile_long_range	MFN	J	\N	Velocity Profiler (long range)	75	1	500	20
94	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
95	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	80	24
96	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	80	24
97	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	80	7
98	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
99	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
100	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	C	\N	Velocity Profiler (short range)	78	1	5	20
101	CTDBP	CTD_bottom_pumped	MFN	E	\N	CTD Pumped	40	1	500	15
102	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	500	10
103	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
104	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	25	7
105	FLORT	Fluorometer_three_wavelength	deep profiling body	A	\N	3-Wavelength Fluorometer	88	1	500	21
106	ZPLSC	plankton_ZP_sonar_coastal	mid-water platform	B	\N	Bio-acoustic Sonar (Coastal)	15	1	200	7
107	PHSEN	pH_stable	Benthic Package (J Box)	D	\N	Seawater pH	63	1	500	18
108	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
109	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
110	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
111	DOSTA	oxygen_dissolved_stable	mid-water platform	D	\N	Dissolved Oxygen Stable Response	1	1	200	1
112	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
113	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
114	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
115	VELPT	Velocity_point	shallow profiling body	D	\N	Single Point Velocity Meter	25	1	200	10
116	PHSEN	pH_stable	Benthic Package (J Box)	D	\N	Seawater pH	63	1	80	18
117	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	80	24
118	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	25	1
119	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
120	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	80	24
121	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	80	24
122	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
123	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
124	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
125	PRESF	pressure_SF	MFN	A	\N	Seafloor Pressure	53	1	25	15
126	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
127	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	80	24
128	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
129	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
130	DOSTA	oxygen_dissolved_stable	deep profiling body	D	\N	Dissolved Oxygen Stable Response	1	1	500	1
131	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
132	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	500	18
133	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	500	1
134	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	25	24
135	OPTAA	attenuation_absorption_optical	Benthic Package (J Box)	D	\N	Absorption Spectrophotometer	86	1	80	21
136	PRESF	pressure_SF	MFN	B	\N	Seafloor Pressure	54	1	80	15
137	ADCPT	Velocity_profile_short_range	MFN	C	\N	Velocity Profiler (short range)	78	1	80	20
138	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
139	DOFST	oxygen_dissolved_fastresp	shallow profiling body	A	\N	Dissolved Oxygen Fast Response	56	1	200	15
140	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
141	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	80	24
142	OPTAA	attenuation_absorption_optical	shallow profiling body	D	\N	Absorption Spectrophotometer	86	1	200	21
143	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	500	15
144	CTDBP	CTD_bottom_pumped	Benthic Package (J Box)	N	\N	CTD Pumped	42	1	80	15
145	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	25	7
146	CAMDS	camera_digital_still_strobe	Benthic Package (J Box) - via wet/mate connector	B	\N	Digital Still Camera with Strobes	17	1	80	7
147	CTDPF	CTD_profiler	deep profiling body	L	\N	CTD Profiler	51	1	500	15
148	ADCPS	Velocity_profile_long_range	Benthic Package (J Box)	I	\N	Velocity Profiler (long range)	73	1	500	20
149	ADCPT	Velocity_profile_short_range	Benthic Package (J Box)	B	\N	Velocity Profiler (short range)	77	1	80	20
150	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	80	24
151	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
152	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	25	24
153	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
154	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
155	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	25	1
156	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
157	PHSEN	pH_stable	shallow profiling body	A	\N	Seawater pH	66	1	200	18
158	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	80	10
159	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
160	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
161	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
162	DOSTA	oxygen_dissolved_stable	Benthic Package (J Box)	D	\N	Dissolved Oxygen Stable Response	1	1	500	1
163	PHSEN	pH_stable	mid-water platform, upward-looking	A	\N	Seawater pH	66	1	200	18
164	FDCHP	flux_direct_cov_HP	Buoy Tower 3 M	A	\N	Direct Covariance Flux	95	1	3	22
165	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	80	24
166	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
167	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
168	PRESF	pressure_SF	MFN	C	\N	Seafloor Pressure	55	1	500	15
169	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
170	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
171	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
172	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
173	PARAD	PAR	shallow profiling body	A	\N	Photosynthetically Available Radiation	35	1	200	14
174	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
175	ZPLSC	plankton_ZP_sonar_coastal	LV-Node	B	\N	Bio-acoustic Sonar (Coastal)	15	1	80	7
176	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	80	24
177	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD Pumped	38	1	80	15
178	VEL3D	Velocity_point_3D_turb	Benthic Package (J Box)	C	\N	3-D Single Point Velocity Meter	23	1	80	10
179	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
180	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
181	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	80	24
182	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	25	24
183	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	25	24
184	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	25	21
185	PARAD	PAR	Glider Science Bay	M	\N	Photosynthetically Available Radiation	7	1	-1	3
186	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD Pumped	38	1	25	15
187	PCO2W	pCO2_water	shallow profiling body	A	\N	pCO2 Water	68	1	200	18
188	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
189	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	500	3
190	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
191	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	500	24
192	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
193	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
194	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	25	24
195	CTDPF	CTD_profiler	mid-water platform	A	\N	CTD Profiler	44	1	200	15
196	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
197	CTDBP	CTD_bottom_pumped	MFN	C	\N	CTD Pumped	38	1	25	15
198	ADCPA	Velocity_profile_mobile_asset	Glider Science Bay	M	\N	Velocity Profiler (short range) for mobile assets	71	1	-1	20
199	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	25	10
200	OPTAA	attenuation_absorption_optical	MFN	C	\N	Absorption Spectrophotometer	87	1	500	21
201	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
202	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
203	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	25	18
204	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
205	VELPT	Velocity_point	Bottom of buoy	A	\N	Single Point Velocity Meter	26	1	1	10
206	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
207	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	80	24
208	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
209	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	25	24
210	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
211	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
212	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
213	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
214	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
215	PCO2W	pCO2_water	mid-water platform	A	\N	pCO2 Water	68	1	200	18
216	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
217	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
218	DOSTA	oxygen_dissolved_stable	Glider Science Bay	M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
219	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	80	18
220	FLORT	Fluorometer_three_wavelength	Glider Science Bay	M	\N	3-Wavelength Fluorometer	92	1	-1	21
221	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	C	\N	Velocity Profiler (short range)	78	1	5	20
222	CTDGV	CTD_glider	Glider Science Bay	M	\N	CTD Glider	47	1	-1	15
223	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
224	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
225	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	5	18
226	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
227	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
228	VEL3D	Velocity_point_3D_turb	MFN	D	\N	3-D Single Point Velocity Meter	22	1	500	10
229	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	25	24
230	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
231	VEL3D	Velocity_point_3D_turb	deep profiling body	A	\N	3-D Single Point Velocity Meter	9	1	500	4
232	ADCPT	Velocity_profile_short_range	Near Surface Instrument Frame	A	\N	Velocity Profiler (short range)	79	1	5	20
233	CAMDS	camera_digital_still_strobe	MFN	A	\N	Digital Still Camera with Strobes	18	1	500	7
234	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
235	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
236	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	4000	1
237	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
238	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
239	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
240	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
241	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
242	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
243	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
244	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
246	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
247	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
248	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	4000	15
249	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
250	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
251	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
252	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
253	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
254	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	4000	4
255	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
256	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
257	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
258	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
259	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
260	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
261	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
262	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
263	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
264	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
265	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2100	21
266	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
267	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
268	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
269	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
270	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
271	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2100	15
272	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
273	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
274	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
275	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
276	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
277	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
278	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
279	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	4000	21
280	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
281	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
282	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
283	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2100	1
284	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
285	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
286	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
287	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
288	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
289	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
290	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
291	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
292	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
293	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
294	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
295	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
296	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2100	4
297	PARAD	PAR		N	\N	Photosynthetically Available Radiation	6	1	-1	3
298	PRESF	pressure_SF	MFN	B	\N	Seafloor Pressure	54	1	130	15
299	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
300	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
301	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	130	15
302	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	360	15
303	PARAD	PAR		N	\N	Photosynthetically Available Radiation	6	1	-1	3
304	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
305	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
306	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
307	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
308	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
309	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity Profiler (short range)	81	1	140	20
310	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
375	ADCPS	Velocity_profile_long_range	MFN	J	\N	Velocity Profiler (long range)	75	1	520	20
311	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	140	10
312	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	130	18
313	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
314	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	520	3
315	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	130	24
316	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
317	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	130	24
318	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
319	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	210	24
320	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
321	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
322	ADCPT	Velocity_profile_short_range	MFN	F	\N	Velocity Profiler (short range)	82	1	210	20
323	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
324	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	210	21
325	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
326	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
327	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
328	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	140	15
329	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	130	3
330	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
331	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
332	DOSTA	oxygen_dissolved_stable		N	\N	Dissolved Oxygen Stable Response	3	1	-1	1
333	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
334	OPTAA	attenuation_absorption_optical	Surface Piercing Profiler Body	J	\N	Absorption Spectrophotometer	114	1	210	24
335	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	140	3
336	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
337	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	130	24
338	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
339	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	520	18
340	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	520	15
341	CTDBP	CTD_bottom_pumped	MFN	D	\N	CTD Pumped	39	1	210	15
342	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	210	24
343	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
344	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	210	1
345	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
346	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	520	10
347	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
348	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
349	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	140	15
350	CTDBP	CTD_bottom_pumped	MFN	D	\N	CTD Pumped	39	1	130	15
351	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	520	10
352	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
353	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
354	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	210	18
355	VELPT	Velocity_point	MFN	B	\N	Single Point Velocity Meter	21	1	520	10
356	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
357	ZPLSC	plankton_ZP_sonar_coastal	MFN	C	\N	Bio-acoustic Sonar (Coastal)	110	1	520	24
358	CTDAV	CTD_AUV		N	\N	CTD AUV	45	1	-1	15
359	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
360	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
361	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
362	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
363	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	520	15
364	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
365	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
366	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	210	18
367	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
368	PHSEN	pH_stable	MFN	D	\N	Seawater pH	63	1	520	18
369	DOSTA	oxygen_dissolved_stable	MFN	D	\N	Dissolved Oxygen Stable Response	1	1	520	1
370	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	5	14
371	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	130	24
372	ADCPA	Velocity_profile_mobile_asset		N	\N	Velocity Profiler (short range) for mobile assets	70	1	-1	20
373	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
374	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	130	24
376	PARAD	PAR	Surface Piercing Profiler Body	J	\N	Photosynthetically Available Radiation	113	1	210	24
377	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	520	21
378	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
379	MOPAK	Motion pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
380	CTDBP	CTD_bottom_pumped	MFN	E	\N	CTD Pumped	40	1	520	15
381	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
382	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
383	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
384	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
385	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
386	OPTAA	attenuation_absorption_optical	MFN	D	\N	Absorption Spectrophotometer	86	1	130	21
387	PRESF	pressure_SF	MFN	C	\N	Seafloor Pressure	55	1	520	15
388	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	520	3
389	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	210	24
390	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	210	24
391	ADCPT	Velocity_profile_short_range	MFN	F	\N	Velocity Profiler (short range)	82	1	130	20
392	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	130	10
393	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
394	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
395	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	360	21
396	PCO2W	pCO2_water	MFN	B	\N	pCO2 Water	67	1	130	18
397	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
398	ADCPA	Velocity_profile_mobile_asset		N	\N	Velocity Profiler (short range) for mobile assets	70	1	-1	20
399	CTDAV	CTD_AUV		N	\N	CTD AUV	45	1	-1	15
400	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
401	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	5	21
402	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	130	24
403	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	520	15
404	PARAD	PAR	Wire Following Profiler Body	K	\N	Photosynthetically Available Radiation	8	1	360	3
405	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	130	24
406	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity Profiler (short range)	81	1	130	20
407	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	520	21
408	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
409	FLORT	Fluorometer_three_wavelength	Surface Piercing Profiler Body	J	\N	3-Wavelength Fluorometer	118	1	210	24
410	FLORT	Fluorometer_three_wavelength		N	\N	3-Wavelength Fluorometer	91	1	-1	21
411	FDCHP	flux_direct_cov_HP	Buoy Tower 3 M	A	\N	Direct Covariance Flux	95	1	3	22
412	NUTNR	nutrient_Nitrate		N	\N	Nitrate	31	1	-1	14
413	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
414	DOFST	oxygen_dissolved_fastresp	Wire Following Profiler Body	K	\N	Dissolved Oxygen Fast Response	52	1	360	15
415	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
416	FLORT	Fluorometer_three_wavelength		N	\N	3-Wavelength Fluorometer	91	1	-1	21
417	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
418	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
419	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	5	14
420	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
421	DOSTA	oxygen_dissolved_stable	Surface Piercing Profiler Body	J	\N	Dissolved Oxygen Stable Response	128	1	210	24
422	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
423	DOSTA	oxygen_dissolved_stable		N	\N	Dissolved Oxygen Stable Response	3	1	-1	1
424	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	5	10
425	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	140	21
426	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
427	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
428	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
429	CTDPF	CTD_profiler	Surface Piercing Profiler Body	J	\N	CTD Profiler	117	1	210	24
430	FLORT	Fluorometer_three_wavelength		M	\N	3-Wavelength Fluorometer	92	1	1000	21
431	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
432	MOPAK	Motion pack	Buoy Well	0	\N	3-Axis Motion Pack	106	1	0	24
433	VELPT	Velocity_point	MFN	A	\N	Single Point Velocity Meter	26	1	130	10
434	METBK	Meteorology_bulk	Buoy Tower 3 M	A	\N	Bulk Meteorology Instrument Package	61	1	3	16
435	ADCPT	Velocity_profile_short_range	Instrument Frame	G	\N	Velocity Profiler (short range)	81	1	360	20
436	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
437	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	C	\N	CTD Pumped	38	1	5	15
438	ADCPS	Velocity_profile_long_range	Instrument Frame	L	\N	Velocity Profiler (long range)	74	1	520	20
439	PHSEN	pH_stable	Near Surface Instrument Frame	D	\N	Seawater pH	63	1	5	18
440	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	520	21
441	NUTNR	nutrient_Nitrate		N	\N	Nitrate	31	1	-1	14
442	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	5	24
443	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	K	\N	3-D Single Point Velocity Meter	20	1	360	10
444	VELPT	Velocity_point	Surface Piercing Profiler Body	J	\N	Single Point Velocity Meter	119	1	130	24
445	ADCPA	Velocity_profile_mobile_asset		M	\N	Velocity Profiler (short range) for mobile assets	71	1	1000	20
446	SPKIR	spectral_irradiance	Surface Piercing Profiler Body	J	\N	Spectral Irradiance	116	1	210	24
447	FLORT	Fluorometer_three_wavelength	Wire Following Profiler Body	K	\N	3-Wavelength Fluorometer	90	1	130	21
448	ACOMM	Modem_acoustic	Profiler Mooring Frame	0	\N	Modem acoustic	104	1	130	24
449	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	520	15
450	PRESF	pressure_SF	MFN	B	\N	Seafloor Pressure	54	1	210	15
451	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	5	1
452	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	5	21
453	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
454	CTDPF	CTD_profiler	Wire Following Profiler Body	K	\N	CTD Profiler	50	1	130	15
455	NUTNR	nutrient_Nitrate	Surface Piercing Profiler Body	J	\N	Nitrate	115	1	130	24
456	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
457	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
458	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
459	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
460	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
461	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
462	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
463	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1500	15
464	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1000	15
465	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	750	15
466	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
467	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
468	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
469	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	80	24
470	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	80	24
471	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	Dissolved Oxygen Stable Response	1	1	1	1
472	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
473	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	40	24
474	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
475	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
476	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD Pumped	41	1	12	15
477	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
478	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
479	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
480	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	3-Wavelength Fluorometer	89	1	1	21
481	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
482	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2600	4
483	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	12	14
484	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	40	24
485	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
486	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
487	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
488	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	Spectral Irradiance	33	1	5	14
489	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
490	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
491	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
492	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
493	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
494	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	5000	4
495	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity Profiler (long range)	76	1	500	20
496	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
497	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
498	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
499	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	5000	21
500	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	20	15
501	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	100	15
502	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	60	15
503	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
504	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
505	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	180	15
506	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
507	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	12	24
508	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
509	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	12	14
510	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	5000	15
511	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	12	21
512	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
513	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
514	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
515	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
516	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	350	15
517	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	500	15
518	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	Absorption Spectrophotometer	86	1	1	21
519	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
520	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
521	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
522	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
523	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
524	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
525	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
526	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
527	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2600	21
528	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	130	24
529	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	20	18
530	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	100	18
531	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
532	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
533	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	40	24
534	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
535	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	12	10
536	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2600	1
537	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	12	18
538	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2600	15
539	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
540	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
541	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
542	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
543	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
544	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
545	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	12	1
546	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
547	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
548	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
549	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	5000	1
550	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
551	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	Nitrate	30	1	1	14
552	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
553	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
554	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	250	15
555	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
556	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
557	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	12	21
558	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	130	24
559	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	80	24
560	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
561	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	130	24
562	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
563	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
564	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	130	24
565	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
566	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
695	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
567	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	12	10
568	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
569	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2400	10
570	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
571	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	20	18
572	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	100	18
573	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	Dissolved Oxygen Stable Response	1	1	1	1
574	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	Spectral Irradiance	33	1	5	14
575	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
576	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2100	10
577	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
578	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	80	24
579	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
580	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
581	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	12	14
582	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
583	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
584	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
585	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
586	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	12	14
587	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2400	10
588	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2700	15
589	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2700	10
590	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
591	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	130	24
592	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	40	24
593	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
594	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	-1	15
595	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	40	24
596	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	40	24
597	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	130	24
598	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
599	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
600	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	12	24
601	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	80	24
602	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	1800	10
603	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
604	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1500	15
605	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1000	15
606	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2100	15
607	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
608	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	750	15
609	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2600	4
610	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2400	15
611	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
612	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
613	FDCHP	flux_direct_cov_HP	Buoy Tower 5 M	A	\N	Direct Covariance Flux	95	1	5	22
614	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2100	15
615	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
616	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
617	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	12	18
618	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
619	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2600	15
620	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2100	10
621	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
622	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
623	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
624	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
625	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
626	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
627	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
628	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
629	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1800	15
630	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	12	21
631	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	-1	1
632	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	Nitrate	30	1	1	14
633	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
634	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
635	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
636	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
637	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	-1	24
638	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2700	15
639	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2600	1
640	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	2400	15
641	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	80	24
642	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	12	21
643	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	3-Wavelength Fluorometer	89	1	1	21
644	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
645	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	Absorption Spectrophotometer	86	1	1	21
646	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1800	15
647	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
648	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
649	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
650	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
651	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
652	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
653	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	250	15
654	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	180	15
655	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD Pumped	41	1	12	15
656	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	20	15
657	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	100	15
658	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	60	15
659	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
660	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
661	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
662	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
663	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity Profiler (long range)	76	1	500	20
664	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
665	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2600	21
666	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
667	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
668	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
669	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
670	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
671	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
672	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	2700	10
673	VELPT	Velocity_Point	Fixed on Inductive Wire	B	\N	Single Point Velocity Meter	21	1	1800	10
674	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
675	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
676	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	12	1
677	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	350	15
678	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	500	15
679	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	-1	21
680	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
681	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
682	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
683	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
684	FLORT	Fluorometer_three_wavelength	Near Surface Instrument Frame	D	\N	3-Wavelength Fluorometer	89	1	12	21
685	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
686	OPTAA	attenuation_absorption_optical		M	\N	Absorption Spectrophotometer	127	1	1000	24
687	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	130	24
688	FLORT	Fluorometer_three_wavelength	Bottom of buoy	D	\N	3-Wavelength Fluorometer	89	1	1	21
689	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	130	1
690	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	40	24
691	ADCPS	Velocity_profile_long_range	Instrument Frame	N	\N	Velocity Profiler (long range)	76	1	500	20
692	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
693	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	2400	21
694	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
696	WAVSS	wave_spectra_surface	Buoy Well, center of Mass	A	\N	Surface Wave Spectra	5	1	0	2
697	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
698	OPTAA	attenuation_absorption_optical	Bottom of buoy	D	\N	Absorption Spectrophotometer	86	1	1	21
699	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
700	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	4600	4
701	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
702	SPKIR	spectral_irradiance	Near Surface Instrument Frame	B	\N	Spectral Irradiance	33	1	12	14
703	PCO2A	pCO2_air-sea	Instrument in well, probe in air and one in water	A	\N	pCO2 Air-Sea	28	1	0	12
704	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
705	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	2400	15
706	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
707	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	164	15
708	ZPLSG	plankton_ZP_sonar_global	Mid-water Platform	A	\N	Bio-acoustic Sonar (Global)	111	1	-1	24
709	NUTNR	nutrient_Nitrate		M	\N	Nitrate	129	1	1000	24
710	NUTNR	nutrient_Nitrate	Bottom of buoy	B	\N	Nitrate	30	1	1	14
711	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	500	15
712	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	350	15
713	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	250	15
714	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	180	15
715	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	100	15
716	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	60	15
717	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
718	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	20	15
719	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
720	METBK	Meteorology_bulk	Buoy Tower 5 M	A	\N	Bulk Meteorology Instrument Package	61	1	5	16
721	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
722	DOSTA	oxygen_dissolved_stable	Bottom of buoy	D	\N	Dissolved Oxygen Stable Response	1	1	1	1
723	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
724	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
725	VELPT	Velocity_point	Near Surface Instrument Frame	A	\N	Single Point Velocity Meter	26	1	12	10
726	DOSTA	oxygen_dissolved_stable	Near Surface Instrument Frame	D	\N	Dissolved Oxygen Stable Response	1	1	12	1
727	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
728	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	500	15
729	CTDMO	CTD_mooring	Fixed on Inductive Wire	Q	\N	CTD Mooring (Inductive)	57	1	350	15
730	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
731	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
732	VEL3D	Velocity_point_3D_turb	Wire Following Profiler Body	L	\N	3-D Single Point Velocity Meter	10	1	2400	4
733	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
734	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	130	24
735	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
736	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	750	15
737	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
738	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
739	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
740	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	100	18
741	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
742	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	80	24
743	PHSEN	pH_stable	Fixed on Inductive Wire	E	\N	Seawater pH	64	1	20	18
744	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1000	15
745	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	130	15
746	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	30	15
747	ADCPS	Velocity_profile_long_range	ADCP Buoy	L	\N	Velocity Profiler (long range)	74	1	500	20
748	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
749	DOSTA	oxygen_dissolved_stable	Fixed on Inductive Wire	D	\N	Dissolved Oxygen Stable Response	1	1	80	1
750	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	80	24
751	CTDBP	CTD_bottom_pumped	Near Surface Instrument Frame	F	\N	CTD Pumped	41	1	12	15
752	ACOMM	Modem_acoustic	Near Surface Instrument Frame	0	\N	Modem acoustic	104	1	12	24
753	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	130	24
754	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
755	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	2400	1
756	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
757	DOSTA	oxygen_dissolved_stable	Wire Following Profiler Body	L	\N	Dissolved Oxygen Stable Response	4	1	4600	1
758	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
759	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
760	ACOMM	Modem_acoustic	Sensor cage	0	\N	Modem acoustic	104	1	40	24
761	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	180	15
762	OPTAA	attenuation_absorption_optical	Near Surface Instrument Frame	D	\N	Absorption Spectrophotometer	86	1	12	21
763	SPKIR	spectral_irradiance	Buoy Tower 5 M	B	\N	Spectral Irradiance	33	1	5	14
764	CTDBP	CTD_bottom_pumped	Fixed on Inductive Wire	P	\N	CTD Pumped	107	1	80	24
765	ACOMM	Modem_acoustic		M	\N	Modem acoustic	105	1	1000	24
766	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	40	15
767	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
768	DOSTA	oxygen_dissolved_stable		M	\N	Dissolved Oxygen Stable Response	2	1	1000	1
769	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
770	CTDGV	CTD_glider		M	\N	CTD Glider	47	1	1000	15
771	FLORT	Fluorometer_three_wavelength	Sensor cage	D	\N	3-Wavelength Fluorometer	89	1	40	21
772	NUTNR	nutrient_Nitrate	Near Surface Instrument Frame	B	\N	Nitrate	30	1	12	14
773	PCO2W	pCO2_water	Fixed on Inductive Wire	C	\N	pCO2 Water	109	1	40	24
774	PARAD	PAR		M	\N	Photosynthetically Available Radiation	7	1	1000	3
775	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	750	15
776	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1500	15
777	CTDMO	CTD_mooring	Fixed on Inductive Wire	R	\N	CTD Mooring (Inductive)	58	1	1000	15
778	FLORD	Fluorometer_two_wavelength	Wire Following Profiler Body	L	\N	2-Wavelength Fluorometer	94	1	4600	21
779	PHSEN	pH_stable	Sensor cage	E	\N	Seawater pH	64	1	40	18
780	DOSTA	oxygen_dissolved_stable	Sensor cage	D	\N	Dissolved Oxygen Stable Response	1	1	40	1
781	PCO2W	pCO2_water	Near Surface Instrument Frame	B	\N	pCO2 Water	67	1	12	18
782	FDCHP	flux_direct_cov_HP	Buoy Tower 5 M	A	\N	Direct Covariance Flux	95	1	5	22
783	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	60	15
784	FLORD	Fluorometer_two_wavelength		M	\N	2-Wavelength Fluorometer	93	1	1000	21
785	MOPAK	Motion Pack	Buoy Well, center of Mass	0	\N	3-Axis Motion Pack	106	1	0	24
786	CTDPF	CTD_profiler	Wire Following Profiler Body	L	\N	CTD Profiler	51	1	4600	15
787	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	250	15
788	FLORD	Fluorometer_two_wavelength	Fixed on Inductive Wire	G	\N	2-Wavelength Fluorometer	108	1	40	24
789	CTDMO	CTD_mooring	Fixed on Inductive Wire	H	\N	CTD Mooring (Inductive)	60	1	1500	15
790	CTDMO	CTD_mooring	Fixed on Inductive Wire	G	\N	CTD Mooring (Inductive)	59	1	90	15
\.


--
-- Data for Name: streams; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY streams (id, stream_name, instrument_id, description) FROM stdin;
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY datasets (id, stream_id, deployment_id, process_level, is_recovered) FROM stdin;
\.


--
-- Data for Name: dataset_keywords; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY dataset_keywords (id, dataset_id, concept_name, concept_description) FROM stdin;
\.


--
-- Name: dataset_keywords_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('dataset_keywords_id_seq', 1, false);


--
-- Name: datasets_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('datasets_id_seq', 1, false);


--
-- Name: deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('deployments_id_seq', 1, true);


--
-- Data for Name: drivers; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY drivers (id, instrument_id, driver_name, driver_version, author) FROM stdin;
\.


--
-- Data for Name: driver_stream_link; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY driver_stream_link (id, driver_id, stream_id) FROM stdin;
\.


--
-- Name: driver_stream_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('driver_stream_link_id_seq', 1, false);


--
-- Name: drivers_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('drivers_id_seq', 1, false);


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('files_id_seq', 1, false);


--
-- Data for Name: inspection_status; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY inspection_status (id, asset_id, file_id, status, technician_name, comments, inspection_date, document) FROM stdin;
\.


--
-- Name: inspection_status_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('inspection_status_id_seq', 1, false);


--
-- Name: installation_record_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('installation_record_id_seq', 1, true);


--
-- Data for Name: installation_records; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY installation_records (id, asset_id, assembly_id, date_installed, date_removed, technician_name, comments, file_id) FROM stdin;
1	1	1	\N	\N	\N	\N	\N
\.


--
-- Data for Name: platforms; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY platforms (id, platform_name, description, location_description, platform_series, is_mobile, serial_no, asset_id, manufacturer_id) FROM stdin;
1	CE01ISSM-LM001	Endurance OR Inshore Surface Mooring	Endurance OR  (25 m) Inshore Surface Mooring		f		1	24
2	CE01ISSM-MFD00	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	24
3	CE01ISSM-MFD35	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	24
4	CE01ISSM-MFD37	Endurance OR Inshore Surface Mooring	Multi-Function (Node)		f		1	24
5	CE01ISSM-RID16	Endurance OR Inshore Surface Mooring	Mooring Riser		f		1	24
6	CE01ISSM-SBD17	Endurance OR Inshore Surface Mooring	Surface Buoy		t		1	24
7	CE01ISSP-CP001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
8	CE01ISSP-PL001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
9	CE01ISSP-SP001	Endurance OR Inshore Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
10	CE02SHBP-BP001	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	24
11	CE02SHBP-LJ01D	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	24
12	CE02SHBP-MJ01C	Endurance OR Shelf Benthic Package	Endurance OR Shelf (80 m) Benthic Package		f		1	24
13	CE02SHSM-RID26	Endurance OR Shelf Surface Mooring	Mooring Riser		f		1	24
14	CE02SHSM-RID27	Endurance OR Shelf Surface Mooring	Mooring Riser		f		1	24
15	CE02SHSM-SBD11	Endurance OR Shelf Surface Mooring	Surface Buoy		t		1	24
16	CE02SHSM-SBD12	Endurance OR Shelf Surface Mooring	Surface Buoy		t		1	24
17	CE02SHSM-SM001	Endurance OR Shelf Surface Mooring	Endurance OR Shelf  (80 m) Surface Mooring		f		1	24
18	CE02SHSP-CP001	Endurance OR Shelf Surface-Piercing Profiler Mooring	Endurance OR Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	24
19	CE02SHSP-SP001	Endurance OR Shelf Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
20	CE04OSBP-BP001	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	24
21	CE04OSBP-LJ01C	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	24
22	CE04OSBP-LV01C	Endurance OR Offshore Benthic Package	Endurance OR Offshore (500 m) Benthic Package		f		1	24
23	CE04OSHY-DP01B	Endurance OR Offshore Hybrid Profiler Mooring	Deep Profiler		f		1	24
24	CE04OSHY-GP001	Endurance OR Offshore Hybrid Profiler Mooring	Endurance OR Offshore (500 m) Hybrid Profiler Mooring		f		1	24
25	CE04OSHY-PC01B	Endurance OR Offshore Hybrid Profiler Mooring	200m Platform		f		1	24
26	CE04OSHY-SF01B	Endurance OR Offshore Hybrid Profiler Mooring	Shallow Profiler		f		1	24
27	CE04OSSM-RID26	Endurance OR Offshore Surface Mooring	Mooring Riser		f		1	24
28	CE04OSSM-RID27	Endurance OR Offshore Surface Mooring	Mooring Riser		f		1	24
29	CE04OSSM-SBD11	Endurance OR Offshore Surface Mooring	Surface Buoy		t		1	24
30	CE04OSSM-SBD12	Endurance OR Offshore Surface Mooring	Surface Buoy		t		1	24
31	CE04OSSM-SM001	Endurance OR Offshore Surface Mooring	Endurance OR Offshore (500 m) Surface Mooring		f		1	24
32	CE05MOAS-GL001	Endurance Mobile Assets	Endurance Glider 1		t		1	24
33	CE05MOAS-GL002	Endurance Mobile Assets	Endurance Glider 2		t		1	24
34	CE05MOAS-GL003	Endurance Mobile Assets	Endurance Glider 3		t		1	24
35	CE05MOAS-GL004	Endurance Mobile Assets	Endurance Glider 4		t		1	24
36	CE05MOAS-GL005	Endurance Mobile Assets	Endurance Glider 5		t		1	24
37	CE05MOAS-GL006	Endurance Mobile Assets	Endurance Glider 6		t		1	24
38	CE06ISSM-LM001	Endurance WA Inshore Surface Mooring	Endurance WA Inshore (25 m) Surface Mooring		f		1	24
39	CE06ISSM-MFD00	Endurance WA Inshore Surface Mooring	MFN		f		1	24
40	CE06ISSM-MFD35	Endurance WA Inshore Surface Mooring	MFN		f		1	24
41	CE06ISSM-MFD37	Endurance WA Inshore Surface Mooring	MFN		f		1	24
42	CE06ISSM-RID16	Endurance WA Inshore Surface Mooring	Mooring Riser		f		1	24
43	CE06ISSM-SBD17	Endurance WA Inshore Surface Mooring	Surface Buoy		t		1	24
44	CE06ISSP-CP001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
45	CE06ISSP-PL001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring		f		1	24
46	CE06ISSP-SP001	Endurance WA Inshore Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
47	CE07SHSM-HM001	Endurance WA Shelf Surface Mooring	Endurance WA Shelf (80 m) Surface Mooring		f		1	24
48	CE07SHSM-MFD00	Endurance WA Shelf Surface Mooring	MFN		f		1	24
49	CE07SHSM-MFD35	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
50	CE07SHSM-MFD37	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
51	CE07SHSM-RID26	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
52	CE07SHSM-RID27	Endurance WA Shelf Surface Mooring	Mooring Riser		f		1	24
53	CE07SHSM-SBD11	Endurance WA Shelf Surface Mooring	Surface Buoy		t		1	24
54	CE07SHSM-SBD12	Endurance WA Shelf Surface Mooring	Surface Buoy		t		1	24
55	CE07SHSP-CP001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	24
56	CE07SHSP-PL001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring		f		1	24
57	CE07SHSP-SP001	Endurance WA Shelf Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
58	CE090SSM-MFD00	Endurance WA Offshore Surface Mooring	MFN		f		1	24
59	CE09OSPM-PM001	Endurance WA Offshore Profiling Mooring	Endurance WA Offshore (500 m) Profiler Mooring		f		1	24
60	CE09OSPM-WF001	Endurance WA Offshore Profiling Mooring	Wire-Following Profiler		f		1	24
61	CE09OSSM-HM001	Endurance WA Offshore Surface Mooring	Endurance WA Offshore (500 m) Surface Mooring		f		1	24
62	CE09OSSM-MFD00	Endurance WA Offshore Surface Mooring	MFN		f		1	24
63	CE09OSSM-MFD35	Endurance WA Offshore Surface Mooring	MFN		f		1	24
64	CE09OSSM-MFD37	Endurance WA Offshore Surface Mooring	MFN		f		1	24
65	CE09OSSM-RID26	Endurance WA Offshore Surface Mooring	Mooring Riser		f		1	24
66	CE09OSSM-RID27	Endurance WA Offshore Surface Mooring	Mooring Riser		f		1	24
67	CE09OSSM-SBD11	Endurance WA Offshore Surface Mooring	Surface Buoy		t		1	24
68	CE09OSSM-SBD12	Endurance WA Offshore Surface Mooring	Surface Buoy		t		1	24
69	GP02HYPM-GP001	PAPA Hybrid Mooring	Hybrid Mooring		f		1	24
70	GP02HYPM-MPC04	PAPA Hybrid Mooring	Mid-water Platform		f		1	24
71	GP02HYPM-RIS01	PAPA Hybrid Mooring	Mooring Riser		f		1	24
72	GP02HYPM-WFP02	PAPA Hybrid Mooring	Wire-Following Profiler #1		f		1	24
73	GP02HYPM-WFP03	PAPA Hybrid Mooring	Wire-Following Profiler #2		f		1	24
74	GP03FLMA-FM001	PAPA Flanking Moorings	Flanking Mooring A		f		1	24
75	GP03FLMA-RIS01	PAPA Flanking Moorings	Mooring Riser		f		1	24
76	GP03FLMA-RIS02	PAPA Flanking Moorings	Mooring Riser		f		1	24
77	GP03FLMB-FM001	PAPA Flanking Moorings	Flanking Mooring B		f		1	24
78	GP03FLMB-RIS01	PAPA Flanking Moorings	Mooring Riser		f		1	24
79	GP03FLMB-RIS02	PAPA Flanking Moorings	Mooring Riser		f		1	24
80	GP05MOAS-GL001	PAPA Mobile Assets	Glider 1		t		1	24
81	GP05MOAS-GL002	PAPA Mobile Assets	Glider 2		t		1	24
82	GP05MOAS-GL003	PAPA Mobile Assets	Glider 3		t		1	24
83	GP05MOAS-PG001	PAPA Mobile Assets	Global Profiling Glider 1		t		1	24
84	GP05MOAS-PG002	PAPA Mobile Assets	Global Profiling Glider 2		t		1	24
85	CP01CNSM-HM001	Pioneer Central P1 Surface Mooring	Pioneer Central P1 Surface Mooring		f		1	24
86	CP01CNSM-MFD00	Pioneer Central P1 Surface Mooring	MFN		f		1	24
87	CP01CNSM-MFD35	Pioneer Central P1 Surface Mooring	MFN		f		1	24
88	CP01CNSM-MFD37	Pioneer Central P1 Surface Mooring	MFN		f		1	24
89	CP01CNSM-RID26	Pioneer Central P1 Surface Mooring	Mooring Riser		f		1	24
90	CP01CNSM-RID27	Pioneer Central P1 Surface Mooring	Mooring Riser		f		1	24
91	CP01CNSM-SBD11	Pioneer Central P1 Surface Mooring	Surface Buoy		t		1	24
92	CP01CNSM-SBD12	Pioneer Central P1 Surface Mooring	Surface Buoy		t		1	24
93	CP01CNSP-CP001	Pioneer Central P1 Surface-Piercing Profiler	Pioneer Central P1 Surface-Piercing Profiler		f		1	24
94	CP01CNSP-PL001	Pioneer Central P1 Surface-Piercing Profiler	Pioneer Central P1 Surface-Piercing Profiler		f		1	24
95	CP01CNSP-SP001	Pioneer Central P1 Surface-Piercing Profiler	Surface-Piercing Profiler		f		1	24
96	CP02PMCI-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Central Inshore Wire-Following Profiler Mooring		f		1	24
97	CP02PMCI-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
98	CP02PMCI-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
99	CP02PMCI-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
100	CP02PMCO-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Central Offshore Wire-Following Profiler Mooring		f		1	24
101	CP02PMCO-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
102	CP02PMCO-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
103	CP02PMCO-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
104	CP02PMUI-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Upstream Inshore Wire-Following Profiler Mooring		f		1	24
105	CP02PMUI-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
106	CP02PMUI-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
107	CP02PMUI-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
108	CP02PMUO-PM001	Pioneer P2 Wire-Following Moorings	Pioneer Upstream Offshore Wire-Following Profiler Mooring		f		1	24
109	CP02PMUO-RII01	Pioneer P2 Wire-Following Moorings	Surface Buoy		f		1	24
110	CP02PMUO-SBS01	Pioneer P2 Wire-Following Moorings	Surface Buoy		t		1	24
111	CP02PMUO-WFP01	Pioneer P2 Wire-Following Moorings	Wire-Following Profiler		f		1	24
112	CP03ISSM-HM001	Pioneer Inshore P3 Surface Mooring	Pioneer Inshore P3 Surface Mooring		f		1	24
113	CP03ISSM-MFD00	Pioneer Inshore P3 Surface Mooring	MFN		f		1	24
114	CP03ISSM-MFD35	Pioneer Inshore P3 Surface Mooring	MFN		f		1	24
115	CP03ISSM-MFD37	Pioneer Inshore P3 Surface Mooring	MFN		f		1	24
116	CP03ISSM-RID26	Pioneer Inshore P3 Surface Mooring	Mooring Riser		f		1	24
117	CP03ISSM-RID27	Pioneer Inshore P3 Surface Mooring	Mooring Riser		f		1	24
118	CP03ISSM-SBD11	Pioneer Inshore P3 Surface Mooring	Surface Buoy		t		1	24
119	CP03ISSM-SBD12	Pioneer Inshore P3 Surface Mooring	Surface Buoy		t		1	24
120	CP03ISSP-CP001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Pioneer Inshore P3 Surface-Piercing Profiler Mooring		f		1	24
121	CP03ISSP-PL001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Pioneer Inshore P3 Surface-Piercing Profiler Mooring		f		1	24
122	CP03ISSP-SP001	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	Surface-Piercing Profiler		f		1	24
123	CP04OSPM-PM001	Pioneer Offshore P4 Wire-Following Profiler Mooring	Pioneer Offshore Wire-Following Profiler Mooring		f		1	24
124	CP04OSPM-SBS11	Pioneer Offshore P4 Wire-Following Profiler Mooring	Surface Buoy		t		1	24
125	CP04OSPM-WFP01	Pioneer Offshore P4 Wire-Following Profiler Mooring	Wire-Following Profiler		f		1	24
126	CP04OSSM-HM001	Pioneer Offshore P4 Surface Mooring	Pioneer Offshore P4 Surface Mooring		f		1	24
127	CP04OSSM-MFD00	Pioneer Offshore P4 Surface Mooring	MFN		f		1	24
128	CP04OSSM-MFD35	Pioneer Offshore P4 Surface Mooring	MFN		f		1	24
129	CP04OSSM-MFD37	Pioneer Offshore P4 Surface Mooring	MFN		f		1	24
130	CP04OSSM-RID26	Pioneer Offshore P4 Surface Mooring	Mooring Riser		f		1	24
131	CP04OSSM-RID27	Pioneer Offshore P4 Surface Mooring	Mooring Riser		f		1	24
132	CP04OSSM-SBD11	Pioneer Offshore P4 Surface Mooring	Surface Buoy		t		1	24
133	CP04OSSM-SBD12	Pioneer Offshore P4 Surface Mooring	Surface Buoy		t		1	24
134	CP05MOAS-AV001	Pioneer Mobile Assets	Pioneer AUV 1		t		1	24
135	CP05MOAS-AV002	Pioneer Mobile Assets	Pioneer AUV 2		t		1	24
136	CP05MOAS-GL001	Pioneer Mobile Assets	Pioneer Glider 1		t		1	24
137	CP05MOAS-GL002	Pioneer Mobile Assets	Pioneer Glider 2		t		1	24
138	CP05MOAS-GL003	Pioneer Mobile Assets	Pioneer Glider 3		t		1	24
139	CP05MOAS-GL004	Pioneer Mobile Assets	Pioneer Glider 4		t		1	24
140	CP05MOAS-GL005	Pioneer Mobile Assets	Pioneer Glider 5		t		1	24
141	CP05MOAS-GL006	Pioneer Mobile Assets	Pioneer Glider 6		t		1	24
142	GA01SUMO-RID16	Argentine Surface Mooring	Mooring Riser		f		1	24
143	GA01SUMO-RII11	Argentine Surface Mooring	Mooring Riser		f		1	24
144	GA01SUMO-SBD11	Argentine Surface Mooring	Surface Buoy		t		1	24
145	GA01SUMO-SBD12	Argentine Surface Mooring	Surface Buoy		t		1	24
146	GA01SUMO-SM001	Argentine Surface Mooring	Surface Mooring		f		1	24
147	GA02HYPM-GP001	Argentine Hybrid Mooring	Hybrid Mooring		f		1	24
148	GA02HYPM-MPC04	Argentine Hybrid Mooring	Mid-water Platform		f		1	24
149	GA02HYPM-RIS01	Argentine Hybrid Mooring	Mooring Riser		f		1	24
150	GA02HYPM-WFP02	Argentine Hybrid Mooring	Wire-Following Profiler #1		f		1	24
151	GA02HYPM-WFP03	Argentine Hybrid Mooring	Wire-Following Profiler #2		f		1	24
152	GA03FLMA-FM001	Argentine Flanking Moorings	Flanking Mooring A		f		1	24
153	GA03FLMA-RIS01	Argentine Flanking Moorings	Mooring Riser		f		1	24
154	GA03FLMA-RIS02	Argentine Flanking Moorings	Mooring Riser		f		1	24
155	GA03FLMB-FM001	Argentine Flanking Moorings	Flanking Mooring B		f		1	24
156	GA03FLMB-RIS01	Argentine Flanking Moorings	Mooring Riser		f		1	24
157	GA03FLMB-RIS02	Argentine Flanking Moorings	Mooring Riser		f		1	24
158	GA05MOAS-GL001	Argentine Mobile Assets	Glider No. 1		t		1	24
159	GA05MOAS-GL002	Argentine Mobile Assets	Glider No. 2		t		1	24
160	GA05MOAS-GL003	Argentine Mobile Assets	Glider No. 3		t		1	24
161	GA05MOAS-PG001	Argentine Mobile Assets	Global Profiling Glider 1		t		1	24
162	GA05MOAS-PG002	Argentine Mobile Assets	Global Profiling Glider 2		t		1	24
163	GI01SUMO-RID16	Irminger Sea Surface Mooring	Mooring Riser		f		1	24
164	GI01SUMO-RII11	Irminger Sea Surface Mooring	Mooring Riser		f		1	24
165	GI01SUMO-SBD11	Irminger Sea Surface Mooring	Surface Buoy		t		1	24
166	GI01SUMO-SBD12	Irminger Sea Surface Mooring	Surface Buoy		t		1	24
167	GI01SUMO-SM001	Irminger Sea Surface Mooring	Surface Mooring		f		1	24
168	GI02HYPM-GP001	Irminger Sea Hybrid Mooring	Hybrid Mooring		f		1	24
169	GI02HYPM-MPC04	Irminger Sea Hybrid Mooring	Mid-water Platform		f		1	24
170	GI02HYPM-RIS01	Irminger Sea Hybrid Mooring	Mooring Riser		f		1	24
171	GI02HYPM-WFP02	Irminger Sea Hybrid Mooring	Wire-Following Profiler		f		1	24
172	GI03FLMA-FM001	Irminger Sea Flanking Moorings	Flanking Mooring A		f		1	24
173	GI03FLMA-RIS01	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
174	GI03FLMA-RIS02	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
175	GI03FLMB-FM001	Irminger Sea Flanking Moorings	Flanking Mooring B		f		1	24
176	GI03FLMB-RIS01	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
177	GI03FLMB-RIS02	Irminger Sea Flanking Moorings	Mooring Riser		f		1	24
178	GI05MOAS-GL001	Irminger Sea Mobile Assets	Glider No. 1		t		1	24
179	GI05MOAS-GL002	Irminger Sea Mobile Assets	Glider No. 2		t		1	24
180	GI05MOAS-GL003	Irminger Sea Mobile Assets	Glider No. 3		t		1	24
181	GI05MOAS-PG001	Irminger Sea Mobile Assets	Global Profiling Glider 1		t		1	24
182	GI05MOAS-PG002	Irminger Sea Mobile Assets	Global Profiling Glider 2		t		1	24
183	GS01SUMO-RID16	55S Surface Mooring	Mooring Riser		f		1	24
184	GS01SUMO-RII11	55S Surface Mooring	Mooring Riser		f		1	24
185	GS01SUMO-SBD11	55S Surface Mooring	Surface Buoy		t		1	24
186	GS01SUMO-SBD12	55S Surface Mooring	Surface Buoy		t		1	24
187	GS01SUMO-SM001	55S Surface Mooring	Surface Mooring		f		1	24
188	GS02HYPM-GP001	55S Hybrid Mooring	Hybrid Mooring		f		1	24
189	GS02HYPM-MPC04	55S Hybrid Mooring	Mid-water Platform		f		1	24
190	GS02HYPM-RIS01	55S Hybrid Mooring	Mooring Riser		f		1	24
191	GS02HYPM-WFP02	55S Hybrid Mooring	Wire-Following Profiler #1		f		1	24
192	GS02HYPM-WFP03	55S Hybrid Mooring	Wire-Following Profiler #2		f		1	24
193	GS03FLMA-FM001	55S Flanking Moorings	Flanking Mooring A		f		1	24
194	GS03FLMA-RIS01	55S Flanking Moorings	Mooring Riser		f		1	24
195	GS03FLMA-RIS02	55S Flanking Moorings	Mooring Riser		f		1	24
196	GS03FLMB-FM001	55S Flanking Moorings	Flanking Mooring B		f		1	24
197	GS03FLMB-RIS01	55S Flanking Moorings	Mooring Riser		f		1	24
198	GS03FLMB-RIS02	55S Flanking Moorings	Mooring Riser		f		1	24
199	GS05MOAS-GL001	55S Mobile Assets	Glider No. 1		t		1	24
200	GS05MOAS-GL002	55S Mobile Assets	Glider No. 2		t		1	24
201	GS05MOAS-GL003	55S Mobile Assets	Glider No. 3		t		1	24
202	GS05MOAS-PG001	55S Mobile Assets	Global Profiling Glider 1		t		1	24
203	GS05MOAS-PG002	55S Mobile Assets	Global Profiling Glider 2		t		1	24
\.


--
-- Data for Name: platform_deployments; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY platform_deployments (id, start_date, end_date, platform_id, reference_designator, array_id, deployment_id, display_name, geo_location) FROM stdin;
1	\N	\N	1	CE01ISSM-LM001	1	1	Endurance OR  (25 m) Inshore Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
2	\N	\N	2	CE01ISSM-MFD00	1	1	Multi-Function (Node)	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
3	\N	\N	3	CE01ISSM-MFD35	1	1	Multi-Function (Node)	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
4	\N	\N	4	CE01ISSM-MFD37	1	1	Multi-Function (Node)	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
5	\N	\N	5	CE01ISSM-RID16	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
6	\N	\N	6	CE01ISSM-SBD17	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
7	\N	\N	7	CE01ISSP-CP001	1	1	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
8	\N	\N	8	CE01ISSP-PL001	1	1	Endurance OR Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
9	\N	\N	9	CE01ISSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
10	\N	\N	10	CE02SHBP-BP001	1	1	Endurance OR Shelf (80 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
11	\N	\N	11	CE02SHBP-LJ01D	1	1	Endurance OR Shelf (80 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
12	\N	\N	12	CE02SHBP-MJ01C	1	1	Endurance OR Shelf (80 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
13	\N	\N	13	CE02SHSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
14	\N	\N	14	CE02SHSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
15	\N	\N	15	CE02SHSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
16	\N	\N	16	CE02SHSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
17	\N	\N	17	CE02SHSM-SM001	1	1	Endurance OR Shelf  (80 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
18	\N	\N	18	CE02SHSP-CP001	1	1	Endurance OR Shelf (80 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
19	\N	\N	19	CE02SHSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
20	\N	\N	20	CE04OSBP-BP001	1	1	Endurance OR Offshore (500 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
21	\N	\N	21	CE04OSBP-LJ01C	1	1	Endurance OR Offshore (500 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
22	\N	\N	22	CE04OSBP-LV01C	1	1	Endurance OR Offshore (500 m) Benthic Package	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
23	\N	\N	23	CE04OSHY-DP01B	1	1	Deep Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
24	\N	\N	24	CE04OSHY-GP001	1	1	Endurance OR Offshore (500 m) Hybrid Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
25	\N	\N	25	CE04OSHY-PC01B	1	1	200m Platform	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
26	\N	\N	26	CE04OSHY-SF01B	1	1	Shallow Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
27	\N	\N	27	CE04OSSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
28	\N	\N	28	CE04OSSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
29	\N	\N	29	CE04OSSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
30	\N	\N	30	CE04OSSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
31	\N	\N	31	CE04OSSM-SM001	1	1	Endurance OR Offshore (500 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
32	\N	\N	32	CE05MOAS-GL001	1	1	Endurance Glider 1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
33	\N	\N	33	CE05MOAS-GL002	1	1	Endurance Glider 2	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
34	\N	\N	34	CE05MOAS-GL003	1	1	Endurance Glider 3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
35	\N	\N	35	CE05MOAS-GL004	1	1	Endurance Glider 4	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
36	\N	\N	36	CE05MOAS-GL005	1	1	Endurance Glider 5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
37	\N	\N	37	CE05MOAS-GL006	1	1	Endurance Glider 6	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
38	\N	\N	38	CE06ISSM-LM001	1	1	Endurance WA Inshore (25 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
39	\N	\N	39	CE06ISSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
40	\N	\N	40	CE06ISSM-MFD35	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
41	\N	\N	41	CE06ISSM-MFD37	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
42	\N	\N	42	CE06ISSM-RID16	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
43	\N	\N	43	CE06ISSM-SBD17	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
44	\N	\N	44	CE06ISSP-CP001	1	1	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
45	\N	\N	45	CE06ISSP-PL001	1	1	Endurance WA Inshore (25 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
46	\N	\N	46	CE06ISSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
47	\N	\N	47	CE07SHSM-HM001	1	1	Endurance WA Shelf (80 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
48	\N	\N	48	CE07SHSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
49	\N	\N	49	CE07SHSM-MFD35	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
50	\N	\N	50	CE07SHSM-MFD37	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
51	\N	\N	51	CE07SHSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
52	\N	\N	52	CE07SHSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
53	\N	\N	53	CE07SHSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
54	\N	\N	54	CE07SHSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
55	\N	\N	55	CE07SHSP-CP001	1	1	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
56	\N	\N	56	CE07SHSP-PL001	1	1	Endurance WA Shelf (80 m) Surface-Piercing Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
57	\N	\N	57	CE07SHSP-SP001	1	1	Surface-Piercing Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
58	\N	\N	58	CE090SSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
59	\N	\N	59	CE09OSPM-PM001	1	1	Endurance WA Offshore (500 m) Profiler Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
60	\N	\N	60	CE09OSPM-WF001	1	1	Wire-Following Profiler	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
61	\N	\N	61	CE09OSSM-HM001	1	1	Endurance WA Offshore (500 m) Surface Mooring	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
62	\N	\N	62	CE09OSSM-MFD00	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
63	\N	\N	63	CE09OSSM-MFD35	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
64	\N	\N	64	CE09OSSM-MFD37	1	1	MFN	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
65	\N	\N	65	CE09OSSM-RID26	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
66	\N	\N	66	CE09OSSM-RID27	1	1	Mooring Riser	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
67	\N	\N	67	CE09OSSM-SBD11	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
68	\N	\N	68	CE09OSSM-SBD12	1	1	Surface Buoy	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
69	\N	\N	69	GP02HYPM-GP001	2	1	Hybrid Mooring	0101000020E6100000E3A59BC4200862C04C37894160FD4840
70	\N	\N	70	GP02HYPM-MPC04	2	1	Mid-water Platform	0101000020E6100000E3A59BC4200862C04C37894160FD4840
71	\N	\N	71	GP02HYPM-RIS01	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
72	\N	\N	72	GP02HYPM-WFP02	2	1	Wire-Following Profiler #1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
73	\N	\N	73	GP02HYPM-WFP03	2	1	Wire-Following Profiler #2	0101000020E6100000E3A59BC4200862C04C37894160FD4840
74	\N	\N	74	GP03FLMA-FM001	2	1	Flanking Mooring A	0101000020E6100000E3A59BC4200862C04C37894160FD4840
75	\N	\N	75	GP03FLMA-RIS01	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
76	\N	\N	76	GP03FLMA-RIS02	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
77	\N	\N	77	GP03FLMB-FM001	2	1	Flanking Mooring B	0101000020E6100000E3A59BC4200862C04C37894160FD4840
78	\N	\N	78	GP03FLMB-RIS01	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
79	\N	\N	79	GP03FLMB-RIS02	2	1	Mooring Riser	0101000020E6100000E3A59BC4200862C04C37894160FD4840
80	\N	\N	80	GP05MOAS-GL001	2	1	Glider 1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
81	\N	\N	81	GP05MOAS-GL002	2	1	Glider 2	0101000020E6100000E3A59BC4200862C04C37894160FD4840
82	\N	\N	82	GP05MOAS-GL003	2	1	Glider 3	0101000020E6100000E3A59BC4200862C04C37894160FD4840
83	\N	\N	83	GP05MOAS-PG001	2	1	Global Profiling Glider 1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
84	\N	\N	84	GP05MOAS-PG002	2	1	Global Profiling Glider 2	0101000020E6100000E3A59BC4200862C04C37894160FD4840
85	\N	\N	85	CP01CNSM-HM001	3	1	Pioneer Central P1 Surface Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
86	\N	\N	86	CP01CNSM-MFD00	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
87	\N	\N	87	CP01CNSM-MFD35	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
88	\N	\N	88	CP01CNSM-MFD37	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
89	\N	\N	89	CP01CNSM-RID26	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
90	\N	\N	90	CP01CNSM-RID27	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
91	\N	\N	91	CP01CNSM-SBD11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
92	\N	\N	92	CP01CNSM-SBD12	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
93	\N	\N	93	CP01CNSP-CP001	3	1	Pioneer Central P1 Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
94	\N	\N	94	CP01CNSP-PL001	3	1	Pioneer Central P1 Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
95	\N	\N	95	CP01CNSP-SP001	3	1	Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
96	\N	\N	96	CP02PMCI-PM001	3	1	Pioneer Central Inshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
97	\N	\N	97	CP02PMCI-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
98	\N	\N	98	CP02PMCI-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
99	\N	\N	99	CP02PMCI-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
100	\N	\N	100	CP02PMCO-PM001	3	1	Pioneer Central Offshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
101	\N	\N	101	CP02PMCO-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
102	\N	\N	102	CP02PMCO-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
103	\N	\N	103	CP02PMCO-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
104	\N	\N	104	CP02PMUI-PM001	3	1	Pioneer Upstream Inshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
105	\N	\N	105	CP02PMUI-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
106	\N	\N	106	CP02PMUI-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
107	\N	\N	107	CP02PMUI-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
108	\N	\N	108	CP02PMUO-PM001	3	1	Pioneer Upstream Offshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
109	\N	\N	109	CP02PMUO-RII01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
110	\N	\N	110	CP02PMUO-SBS01	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
111	\N	\N	111	CP02PMUO-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
112	\N	\N	112	CP03ISSM-HM001	3	1	Pioneer Inshore P3 Surface Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
113	\N	\N	113	CP03ISSM-MFD00	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
114	\N	\N	114	CP03ISSM-MFD35	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
115	\N	\N	115	CP03ISSM-MFD37	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
116	\N	\N	116	CP03ISSM-RID26	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
117	\N	\N	117	CP03ISSM-RID27	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
118	\N	\N	118	CP03ISSM-SBD11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
119	\N	\N	119	CP03ISSM-SBD12	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
120	\N	\N	120	CP03ISSP-CP001	3	1	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
121	\N	\N	121	CP03ISSP-PL001	3	1	Pioneer Inshore P3 Surface-Piercing Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
122	\N	\N	122	CP03ISSP-SP001	3	1	Surface-Piercing Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
123	\N	\N	123	CP04OSPM-PM001	3	1	Pioneer Offshore Wire-Following Profiler Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
124	\N	\N	124	CP04OSPM-SBS11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
125	\N	\N	125	CP04OSPM-WFP01	3	1	Wire-Following Profiler	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
126	\N	\N	126	CP04OSSM-HM001	3	1	Pioneer Offshore P4 Surface Mooring	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
127	\N	\N	127	CP04OSSM-MFD00	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
128	\N	\N	128	CP04OSSM-MFD35	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
129	\N	\N	129	CP04OSSM-MFD37	3	1	MFN	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
130	\N	\N	130	CP04OSSM-RID26	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
131	\N	\N	131	CP04OSSM-RID27	3	1	Mooring Riser	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
132	\N	\N	132	CP04OSSM-SBD11	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
133	\N	\N	133	CP04OSSM-SBD12	3	1	Surface Buoy	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
134	\N	\N	134	CP05MOAS-AV001	3	1	Pioneer AUV 1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
135	\N	\N	135	CP05MOAS-AV002	3	1	Pioneer AUV 2	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
136	\N	\N	136	CP05MOAS-GL001	3	1	Pioneer Glider 1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
137	\N	\N	137	CP05MOAS-GL002	3	1	Pioneer Glider 2	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
138	\N	\N	138	CP05MOAS-GL003	3	1	Pioneer Glider 3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
139	\N	\N	139	CP05MOAS-GL004	3	1	Pioneer Glider 4	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
140	\N	\N	140	CP05MOAS-GL005	3	1	Pioneer Glider 5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
141	\N	\N	141	CP05MOAS-GL006	3	1	Pioneer Glider 6	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
142	\N	\N	142	GA01SUMO-RID16	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
143	\N	\N	143	GA01SUMO-RII11	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
144	\N	\N	144	GA01SUMO-SBD11	4	1	Surface Buoy	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
145	\N	\N	145	GA01SUMO-SBD12	4	1	Surface Buoy	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
146	\N	\N	146	GA01SUMO-SM001	4	1	Surface Mooring	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
147	\N	\N	147	GA02HYPM-GP001	4	1	Hybrid Mooring	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
148	\N	\N	148	GA02HYPM-MPC04	4	1	Mid-water Platform	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
149	\N	\N	149	GA02HYPM-RIS01	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
150	\N	\N	150	GA02HYPM-WFP02	4	1	Wire-Following Profiler #1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
151	\N	\N	151	GA02HYPM-WFP03	4	1	Wire-Following Profiler #2	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
152	\N	\N	152	GA03FLMA-FM001	4	1	Flanking Mooring A	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
153	\N	\N	153	GA03FLMA-RIS01	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
154	\N	\N	154	GA03FLMA-RIS02	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
155	\N	\N	155	GA03FLMB-FM001	4	1	Flanking Mooring B	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
156	\N	\N	156	GA03FLMB-RIS01	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
157	\N	\N	157	GA03FLMB-RIS02	4	1	Mooring Riser	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
158	\N	\N	158	GA05MOAS-GL001	4	1	Glider No. 1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
159	\N	\N	159	GA05MOAS-GL002	4	1	Glider No. 2	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
160	\N	\N	160	GA05MOAS-GL003	4	1	Glider No. 3	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
161	\N	\N	161	GA05MOAS-PG001	4	1	Global Profiling Glider 1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
162	\N	\N	162	GA05MOAS-PG002	4	1	Global Profiling Glider 2	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
163	\N	\N	163	GI01SUMO-RID16	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
164	\N	\N	164	GI01SUMO-RII11	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
165	\N	\N	165	GI01SUMO-SBD11	5	1	Surface Buoy	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
166	\N	\N	166	GI01SUMO-SBD12	5	1	Surface Buoy	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
167	\N	\N	167	GI01SUMO-SM001	5	1	Surface Mooring	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
168	\N	\N	168	GI02HYPM-GP001	5	1	Hybrid Mooring	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
169	\N	\N	169	GI02HYPM-MPC04	5	1	Mid-water Platform	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
170	\N	\N	170	GI02HYPM-RIS01	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
171	\N	\N	171	GI02HYPM-WFP02	5	1	Wire-Following Profiler	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
172	\N	\N	172	GI03FLMA-FM001	5	1	Flanking Mooring A	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
173	\N	\N	173	GI03FLMA-RIS01	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
174	\N	\N	174	GI03FLMA-RIS02	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
175	\N	\N	175	GI03FLMB-FM001	5	1	Flanking Mooring B	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
176	\N	\N	176	GI03FLMB-RIS01	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
177	\N	\N	177	GI03FLMB-RIS02	5	1	Mooring Riser	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
178	\N	\N	178	GI05MOAS-GL001	5	1	Glider No. 1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
179	\N	\N	179	GI05MOAS-GL002	5	1	Glider No. 2	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
180	\N	\N	180	GI05MOAS-GL003	5	1	Glider No. 3	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
181	\N	\N	181	GI05MOAS-PG001	5	1	Global Profiling Glider 1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
182	\N	\N	182	GI05MOAS-PG002	5	1	Global Profiling Glider 2	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
183	\N	\N	183	GS01SUMO-RID16	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
184	\N	\N	184	GS01SUMO-RII11	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
185	\N	\N	185	GS01SUMO-SBD11	6	1	Surface Buoy	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
186	\N	\N	186	GS01SUMO-SBD12	6	1	Surface Buoy	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
187	\N	\N	187	GS01SUMO-SM001	6	1	Surface Mooring	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
188	\N	\N	188	GS02HYPM-GP001	6	1	Hybrid Mooring	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
189	\N	\N	189	GS02HYPM-MPC04	6	1	Mid-water Platform	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
190	\N	\N	190	GS02HYPM-RIS01	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
191	\N	\N	191	GS02HYPM-WFP02	6	1	Wire-Following Profiler #1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
192	\N	\N	192	GS02HYPM-WFP03	6	1	Wire-Following Profiler #2	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
193	\N	\N	193	GS03FLMA-FM001	6	1	Flanking Mooring A	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
194	\N	\N	194	GS03FLMA-RIS01	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
195	\N	\N	195	GS03FLMA-RIS02	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
196	\N	\N	196	GS03FLMB-FM001	6	1	Flanking Mooring B	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
197	\N	\N	197	GS03FLMB-RIS01	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
198	\N	\N	198	GS03FLMB-RIS02	6	1	Mooring Riser	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
199	\N	\N	199	GS05MOAS-GL001	6	1	Glider No. 1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
200	\N	\N	200	GS05MOAS-GL002	6	1	Glider No. 2	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
201	\N	\N	201	GS05MOAS-GL003	6	1	Glider No. 3	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
202	\N	\N	202	GS05MOAS-PG001	6	1	Global Profiling Glider 1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
203	\N	\N	203	GS05MOAS-PG002	6	1	Global Profiling Glider 2	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
\.


--
-- Data for Name: instrument_deployments; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY instrument_deployments (id, display_name, start_date, end_date, platform_deployment_id, instrument_id, reference_designator, depth, geo_location) FROM stdin;
1	SPKIR	\N	\N	46	1	CE06ISSP-SP001-07-SPKIRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
2	CTDPF	\N	\N	57	2	CE07SHSP-SP001-08-CTDPFJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
3	DOSTA	\N	\N	19	3	CE02SHSP-SP001-01-DOSTAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
4	OPTAA	\N	\N	28	4	CE04OSSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
5	OPTAA	\N	\N	5	5	CE01ISSM-RID16-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
6	PCO2W	\N	\N	63	6	CE09OSSM-MFD35-05-PCO2WB000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
7	VEL3D	\N	\N	40	7	CE06ISSM-MFD35-01-VEL3DD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
8	ZPLSC	\N	\N	2	8	CE01ISSM-MFD00-00-ZPLSCC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
9	FLORT	\N	\N	9	9	CE01ISSP-SP001-08-FLORTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
10	VEL3D	\N	\N	21	10	CE04OSBP-LJ01C-07-VEL3DC107	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
11	PARAD	\N	\N	34	11	CE05MOAS-GL003-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
12	WAVSS	\N	\N	30	12	CE04OSSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
13	ADCPT	\N	\N	51	13	CE07SHSM-RID26-01-ADCPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
14	MOPAK	\N	\N	29	14	CE04OSSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
15	FLORT	\N	\N	32	15	CE05MOAS-GL001-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
16	FLORT	\N	\N	34	16	CE05MOAS-GL003-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
17	OPTAA	\N	\N	14	17	CE02SHSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
18	ADCPT	\N	\N	40	18	CE06ISSM-MFD35-04-ADCPTM000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
19	CTDPF	\N	\N	19	19	CE02SHSP-SP001-01-CTDPFJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
20	FLORT	\N	\N	60	20	CE09OSPM-WF001-04-FLORTK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
21	CTDBP	\N	\N	28	21	CE04OSSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
22	WAVSS	\N	\N	16	22	CE02SHSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
23	PCO2W	\N	\N	42	23	CE06ISSM-RID16-05-PCO2WB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
24	DOSTA	\N	\N	9	24	CE01ISSP-SP001-02-DOSTAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
25	OPTAA	\N	\N	50	25	CE07SHSM-MFD37-01-OPTAAD000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
26	PCO2W	\N	\N	11	26	CE02SHBP-LJ01D-09-PCO2WB103	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
27	HYDBB	\N	\N	11	27	CE02SHBP-LJ01D-11-HYDBBA106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
28	OPTAA	\N	\N	41	28	CE06ISSM-MFD37-01-OPTAAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
29	VELPT	\N	\N	27	29	CE04OSSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
30	VELPT	\N	\N	65	30	CE09OSSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
31	CTDGV	\N	\N	34	31	CE05MOAS-GL003-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
32	DOSTA	\N	\N	11	32	CE02SHBP-LJ01D-06-DOSTAD106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
33	ADCPT	\N	\N	3	33	CE01ISSM-MFD35-04-ADCPTM000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
34	ZPLSC	\N	\N	39	34	CE06ISSM-MFD00-00-ZPLSCC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
35	ACOMM	\N	\N	27	35	CE04OSSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
36	PCO2W	\N	\N	3	36	CE01ISSM-MFD35-05-PCO2WB000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
37	PHSEN	\N	\N	27	37	CE04OSSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
38	VELPT	\N	\N	46	38	CE06ISSP-SP001-05-VELPTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
39	CAMDS	\N	\N	22	39	CE04OSBP-LV01C-06-CAMDSB106	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
40	PCO2W	\N	\N	21	40	CE04OSBP-LJ01C-09-PCO2WB104	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
41	VELPT	\N	\N	13	41	CE02SHSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
42	SPKIR	\N	\N	26	42	CE04OSHY-SF01B-3D-SPKIRA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
43	PCO2A	\N	\N	68	43	CE09OSSM-SBD12-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
44	SPKIR	\N	\N	19	44	CE02SHSP-SP001-06-SPKIRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
45	PARAD	\N	\N	36	45	CE05MOAS-GL005-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
46	FLORT	\N	\N	26	46	CE04OSHY-SF01B-3A-FLORTD104	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
47	NUTNR	\N	\N	26	47	CE04OSHY-SF01B-4A-NUTNRA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
48	VELPT	\N	\N	15	48	CE02SHSM-SBD11-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
49	PRESF	\N	\N	40	49	CE06ISSM-MFD35-02-PRESFA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
50	MOPAK	\N	\N	15	50	CE02SHSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
51	VELPT	\N	\N	43	51	CE06ISSM-SBD17-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
52	ADCPA	\N	\N	36	52	CE05MOAS-GL005-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
53	CTDPF	\N	\N	26	53	CE04OSHY-SF01B-2A-CTDPFA107	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
54	DOSTA	\N	\N	52	54	CE07SHSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
55	CTDGV	\N	\N	35	55	CE05MOAS-GL004-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
56	CTDBP	\N	\N	5	56	CE01ISSM-RID16-03-CTDBPC001	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
57	MOPAK	\N	\N	53	57	CE07SHSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
58	VELPT	\N	\N	51	58	CE07SHSM-RID26-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
59	DOSTA	\N	\N	5	59	CE01ISSM-RID16-03-DOSTAD002	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
60	NUTNR	\N	\N	19	60	CE02SHSP-SP001-05-NUTNRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
61	OPTAA	\N	\N	42	61	CE06ISSM-RID16-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
62	CTDBP	\N	\N	21	62	CE04OSBP-LJ01C-06-CTDBPO108	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
63	MOPAK	\N	\N	67	63	CE09OSSM-SBD11-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
64	HYDBB	\N	\N	21	64	CE04OSBP-LJ01C-11-HYDBBA105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
65	METBK	\N	\N	29	65	CE04OSSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
66	ACOMM	\N	\N	8	66	CE01ISSP-PL001-01-ACOMM0	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
67	OPTAA	\N	\N	46	67	CE06ISSP-SP001-04-OPTAAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
68	PHSEN	\N	\N	40	68	CE06ISSM-MFD35-06-PHSEND000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
69	PARAD	\N	\N	37	69	CE05MOAS-GL006-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
70	PHSEN	\N	\N	3	70	CE01ISSM-MFD35-06-PHSEND000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
71	FLORT	\N	\N	57	71	CE07SHSP-SP001-07-FLORTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
72	ACOMM	\N	\N	42	72	CE06ISSM-RID16-00-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
73	SPKIR	\N	\N	9	73	CE01ISSP-SP001-07-SPKIRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
74	WAVSS	\N	\N	54	74	CE07SHSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
75	FLORT	\N	\N	37	75	CE05MOAS-GL006-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
76	NUTNR	\N	\N	42	76	CE06ISSM-RID16-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
77	NUTNR	\N	\N	66	77	CE09OSSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
78	ACOMM	\N	\N	65	78	CE09OSSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
79	PHSEN	\N	\N	49	79	CE07SHSM-MFD35-06-PHSEND000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
80	VELPT	\N	\N	5	80	CE01ISSM-RID16-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
81	ACOMM	\N	\N	5	81	CE01ISSM-RID16-00-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
82	FLORT	\N	\N	42	82	CE06ISSM-RID16-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
83	DOSTA	\N	\N	33	83	CE05MOAS-GL002-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
84	OPTAA	\N	\N	21	84	CE04OSBP-LJ01C-08-OPTAAC104	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
85	NUTNR	\N	\N	9	85	CE01ISSP-SP001-06-NUTNRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
86	PARAD	\N	\N	9	86	CE01ISSP-SP001-10-PARADJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
87	DOFST	\N	\N	60	87	CE09OSPM-WF001-02-DOFSTK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
88	VELPT	\N	\N	9	88	CE01ISSP-SP001-05-VELPTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
89	CTDPF	\N	\N	46	89	CE06ISSP-SP001-09-CTDPFJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
90	ACOMM	\N	\N	51	90	CE07SHSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
91	DOSTA	\N	\N	28	91	CE04OSSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
92	WAVSS	\N	\N	68	92	CE09OSSM-SBD12-05-WAVSSA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
93	ADCPS	\N	\N	63	93	CE09OSSM-MFD35-04-ADCPSJ000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
94	PARAD	\N	\N	33	94	CE05MOAS-GL002-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
95	DOSTA	\N	\N	57	95	CE07SHSP-SP001-01-DOSTAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
96	FLORT	\N	\N	19	96	CE02SHSP-SP001-07-FLORTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
97	CAMDS	\N	\N	48	97	CE07SHSM-MFD00-00-CAMDSA000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
98	FLORT	\N	\N	33	98	CE05MOAS-GL002-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
99	ADCPA	\N	\N	32	99	CE05MOAS-GL001-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
100	ADCPT	\N	\N	27	100	CE04OSSM-RID26-01-ADCPTC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
101	CTDBP	\N	\N	64	101	CE09OSSM-MFD37-03-CTDBPE000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
102	VEL3D	\N	\N	60	102	CE09OSPM-WF001-01-VEL3DK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
103	ADCPA	\N	\N	37	103	CE05MOAS-GL006-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
104	CAMDS	\N	\N	2	104	CE01ISSM-MFD00-00-CAMDSA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
105	FLORT	\N	\N	23	105	CE04OSHY-DP01B-04-FLORTA103	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
106	ZPLSC	\N	\N	25	106	CE04OSHY-PC01B-05-ZPLSCB102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
107	PHSEN	\N	\N	21	107	CE04OSBP-LJ01C-10-PHSEND107	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
108	NUTNR	\N	\N	28	108	CE04OSSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
109	ADCPA	\N	\N	33	109	CE05MOAS-GL002-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
110	FLORT	\N	\N	35	110	CE05MOAS-GL004-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
111	DOSTA	\N	\N	25	111	CE04OSHY-PC01B-4A-DOSTAD109	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
112	NUTNR	\N	\N	14	112	CE02SHSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
113	FLORT	\N	\N	14	113	CE02SHSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
114	METBK	\N	\N	67	114	CE09OSSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
115	VELPT	\N	\N	26	115	CE04OSHY-SF01B-4B-VELPTD106	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
116	PHSEN	\N	\N	11	116	CE02SHBP-LJ01D-10-PHSEND103	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
117	SPKIR	\N	\N	57	117	CE07SHSP-SP001-06-SPKIRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
118	DOSTA	\N	\N	41	118	CE06ISSM-MFD37-04-DOSTAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
119	DOSTA	\N	\N	35	119	CE05MOAS-GL004-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
120	NUTNR	\N	\N	57	120	CE07SHSP-SP001-05-NUTNRJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
121	VELPT	\N	\N	57	121	CE07SHSP-SP001-02-VELPTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
122	PCO2A	\N	\N	53	122	CE07SHSM-SBD11-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
123	VELPT	\N	\N	67	123	CE09OSSM-SBD11-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
124	PHSEN	\N	\N	5	124	CE01ISSM-RID16-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
125	PRESF	\N	\N	3	125	CE01ISSM-MFD35-02-PRESFA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
126	MOPAK	\N	\N	6	126	CE01ISSM-SBD17-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
127	VELPT	\N	\N	19	127	CE02SHSP-SP001-02-VELPTJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
128	METBK	\N	\N	15	128	CE02SHSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
129	CTDBP	\N	\N	52	129	CE07SHSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
130	DOSTA	\N	\N	23	130	CE04OSHY-DP01B-06-DOSTAD105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
131	SPKIR	\N	\N	66	131	CE09OSSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
132	PHSEN	\N	\N	63	132	CE09OSSM-MFD35-06-PHSEND000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
133	DOSTA	\N	\N	64	133	CE09OSSM-MFD37-04-DOSTAD000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
134	OPTAA	\N	\N	9	134	CE01ISSP-SP001-04-OPTAAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
135	OPTAA	\N	\N	11	135	CE02SHBP-LJ01D-08-OPTAAD106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
136	PRESF	\N	\N	49	136	CE07SHSM-MFD35-02-PRESFB000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
137	ADCPT	\N	\N	49	137	CE07SHSM-MFD35-04-ADCPTC000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
138	FLORT	\N	\N	28	138	CE04OSSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
139	DOFST	\N	\N	26	139	CE04OSHY-SF01B-2A-DOFSTA107	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
140	DOSTA	\N	\N	66	140	CE09OSSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
141	ACOMM	\N	\N	56	141	CE07SHSP-PL001-01-ACOMM0	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
142	OPTAA	\N	\N	26	142	CE04OSHY-SF01B-3B-OPTAAD105	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
143	CTDPF	\N	\N	60	143	CE09OSPM-WF001-03-CTDPFK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
144	CTDBP	\N	\N	11	144	CE02SHBP-LJ01D-06-CTDBPN106	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
145	CAMDS	\N	\N	39	145	CE06ISSM-MFD00-00-CAMDSA000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
146	CAMDS	\N	\N	12	146	CE02SHBP-MJ01C-08-CAMDSB107	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
147	CTDPF	\N	\N	23	147	CE04OSHY-DP01B-01-CTDPFL105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
148	ADCPS	\N	\N	21	148	CE04OSBP-LJ01C-05-ADCPSI103	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
149	ADCPT	\N	\N	11	149	CE02SHBP-LJ01D-05-ADCPTB104	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
150	PARAD	\N	\N	19	150	CE02SHSP-SP001-08-PARADJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
151	DOSTA	\N	\N	34	151	CE05MOAS-GL003-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
152	FLORT	\N	\N	46	152	CE06ISSP-SP001-08-FLORTJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
153	CTDBP	\N	\N	66	153	CE09OSSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
154	OPTAA	\N	\N	52	154	CE07SHSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
155	DOSTA	\N	\N	4	155	CE01ISSM-MFD37-04-DOSTAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
156	SPKIR	\N	\N	5	156	CE01ISSM-RID16-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
157	PHSEN	\N	\N	26	157	CE04OSHY-SF01B-2B-PHSENA108	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
158	VEL3D	\N	\N	49	158	CE07SHSM-MFD35-01-VEL3DD000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
159	NUTNR	\N	\N	5	159	CE01ISSM-RID16-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
160	VELPT	\N	\N	54	160	CE07SHSM-SBD12-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
161	ACOMM	\N	\N	13	161	CE02SHSM-RID26-05-ACOMM0000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
162	DOSTA	\N	\N	21	162	CE04OSBP-LJ01C-06-DOSTAD108	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
163	PHSEN	\N	\N	25	163	CE04OSHY-PC01B-4B-PHSENA106	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
164	FDCHP	\N	\N	16	164	CE02SHSM-SBD12-08-FDCHPA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
165	OPTAA	\N	\N	57	165	CE07SHSP-SP001-04-OPTAAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
166	PHSEN	\N	\N	51	166	CE07SHSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
167	NUTNR	\N	\N	52	167	CE07SHSM-RID27-07-NUTNRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
168	PRESF	\N	\N	63	168	CE09OSSM-MFD35-02-PRESFC000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
169	VELPT	\N	\N	29	169	CE04OSSM-SBD11-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
170	PHSEN	\N	\N	13	170	CE02SHSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
171	PCO2A	\N	\N	16	171	CE02SHSM-SBD12-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
172	ADCPA	\N	\N	34	172	CE05MOAS-GL003-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
173	PARAD	\N	\N	26	173	CE04OSHY-SF01B-3C-PARADA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
174	FLORT	\N	\N	66	174	CE09OSSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
175	ZPLSC	\N	\N	12	175	CE02SHBP-MJ01C-07-ZPLSCB101	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
176	ZPLSC	\N	\N	48	176	CE07SHSM-MFD00-00-ZPLSCC000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
177	CTDBP	\N	\N	50	177	CE07SHSM-MFD37-03-CTDBPC000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
178	VEL3D	\N	\N	11	178	CE02SHBP-LJ01D-07-VEL3DC108	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
179	PARAD	\N	\N	35	179	CE05MOAS-GL004-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
180	PHSEN	\N	\N	65	180	CE09OSSM-RID26-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
181	OPTAA	\N	\N	19	181	CE02SHSP-SP001-04-OPTAAJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
182	DOSTA	\N	\N	46	182	CE06ISSP-SP001-02-DOSTAJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
183	PARAD	\N	\N	46	183	CE06ISSP-SP001-10-PARADJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
184	OPTAA	\N	\N	4	184	CE01ISSM-MFD37-01-OPTAAD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
185	PARAD	\N	\N	32	185	CE05MOAS-GL001-01-PARADM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
186	CTDBP	\N	\N	4	186	CE01ISSM-MFD37-03-CTDBPC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
187	PCO2W	\N	\N	26	187	CE04OSHY-SF01B-4F-PCO2WA102	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
188	CTDGV	\N	\N	37	188	CE05MOAS-GL006-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
189	PARAD	\N	\N	60	189	CE09OSPM-WF001-05-PARADK000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
190	CTDBP	\N	\N	14	190	CE02SHSM-RID27-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
191	ZPLSC	\N	\N	58	191	CE09OSSM-MFD37-00-ZPLSCC000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
192	DOSTA	\N	\N	50	192	CE07SHSM-MFD37-04-DOSTAD000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
193	CTDGV	\N	\N	36	193	CE05MOAS-GL005-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
194	CTDPF	\N	\N	9	194	CE01ISSP-SP001-09-CTDPFJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
195	CTDPF	\N	\N	25	195	CE04OSHY-PC01B-4A-CTDPFA109	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
196	DOSTA	\N	\N	42	196	CE06ISSM-RID16-03-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
197	CTDBP	\N	\N	41	197	CE06ISSM-MFD37-03-CTDBPC000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
198	ADCPA	\N	\N	35	198	CE05MOAS-GL004-03-ADCPAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
199	VEL3D	\N	\N	3	199	CE01ISSM-MFD35-01-VEL3DD000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
200	OPTAA	\N	\N	64	200	CE09OSSM-MFD37-01-OPTAAC000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
201	FLORT	\N	\N	52	201	CE07SHSM-RID27-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
202	SPKIR	\N	\N	52	202	CE07SHSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
203	PCO2W	\N	\N	40	203	CE06ISSM-MFD35-05-PCO2WB000	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
204	CTDBP	\N	\N	42	204	CE06ISSM-RID16-03-CTDBPC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
205	VELPT	\N	\N	6	205	CE01ISSM-SBD17-04-VELPTA000	1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
206	OPTAA	\N	\N	66	206	CE09OSSM-RID27-01-OPTAAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
207	PARAD	\N	\N	57	207	CE07SHSP-SP001-09-PARADJ	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
208	SPKIR	\N	\N	14	208	CE02SHSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
209	NUTNR	\N	\N	46	209	CE06ISSP-SP001-06-NUTNRJ	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
210	PHSEN	\N	\N	42	210	CE06ISSM-RID16-06-PHSEND000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
211	DOSTA	\N	\N	37	211	CE05MOAS-GL006-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
212	SPKIR	\N	\N	28	212	CE04OSSM-RID27-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
213	CTDGV	\N	\N	32	213	CE05MOAS-GL001-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
214	METBK	\N	\N	53	214	CE07SHSM-SBD11-06-METBKA000	3	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
215	PCO2W	\N	\N	25	215	CE04OSHY-PC01B-4C-PCO2WA105	200	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
216	DOSTA	\N	\N	32	216	CE05MOAS-GL001-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
217	MOPAK	\N	\N	43	217	CE06ISSM-SBD17-01-MOPAK0000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
218	DOSTA	\N	\N	36	218	CE05MOAS-GL005-04-DOSTAM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
219	PCO2W	\N	\N	49	219	CE07SHSM-MFD35-05-PCO2WB000	80	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
220	FLORT	\N	\N	36	220	CE05MOAS-GL005-02-FLORTM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
221	ADCPT	\N	\N	65	221	CE09OSSM-RID26-01-ADCPTC000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
222	CTDGV	\N	\N	33	222	CE05MOAS-GL002-05-CTDGVM000	-1	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
223	VELPT	\N	\N	42	223	CE06ISSM-RID16-04-VELPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
224	DOSTA	\N	\N	14	224	CE02SHSM-RID27-04-DOSTAD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
225	PCO2W	\N	\N	5	225	CE01ISSM-RID16-05-PCO2WB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
226	PCO2A	\N	\N	30	226	CE04OSSM-SBD12-04-PCO2AA000	0	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
227	FLORT	\N	\N	5	227	CE01ISSM-RID16-02-FLORTD000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
228	VEL3D	\N	\N	63	228	CE09OSSM-MFD35-01-VEL3DD000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
229	ACOMM	\N	\N	45	229	CE06ISSP-PL001-01-ACOMM0	25	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
230	SPKIR	\N	\N	42	230	CE06ISSM-RID16-08-SPKIRB000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
231	VEL3D	\N	\N	23	231	CE04OSHY-DP01B-02-VEL3DA105	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
232	ADCPT	\N	\N	13	232	CE02SHSM-RID26-01-ADCPTA000	5	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
233	CAMDS	\N	\N	62	233	CE09OSSM-MFD00-00-CAMDSA000	500	0101000020E6100000CDCCCCCCCC3C5FC08FC2F5285C2F4640
234	FLORD	\N	\N	84	234	GP05MOAS-PG002-02-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
235	ZPLSG	\N	\N	70	235	GP02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E6100000E3A59BC4200862C04C37894160FD4840
236	DOSTA	\N	\N	73	236	GP02HYPM-WFP03-03-DOSTAL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
237	CTDMO	\N	\N	79	237	GP03FLMB-RIS02-06-CTDMOG	90	0101000020E6100000E3A59BC4200862C04C37894160FD4840
238	ACOMM	\N	\N	81	238	GP05MOAS-GL002-03-ACOMMM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
239	CTDGV	\N	\N	82	239	GP05MOAS-GL003-04-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
240	CTDMO	\N	\N	79	240	GP03FLMB-RIS02-04-CTDMOG	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
241	CTDMO	\N	\N	79	241	GP03FLMB-RIS02-03-CTDMOG	30	0101000020E6100000E3A59BC4200862C04C37894160FD4840
242	CTDMO	\N	\N	76	242	GP03FLMA-RIS02-08-CTDMOG	180	0101000020E6100000E3A59BC4200862C04C37894160FD4840
243	CTDMO	\N	\N	79	243	GP03FLMB-RIS02-08-CTDMOG	180	0101000020E6100000E3A59BC4200862C04C37894160FD4840
244	ACOMM	\N	\N	82	244	GP05MOAS-GL003-03-ACOMMM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
245	PARAD	\N	\N	84	245	GP05MOAS-PG002-04-PARADM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
246	DOSTA	\N	\N	78	246	GP03FLMB-RIS01-03-DOSTAD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
247	CTDMO	\N	\N	76	247	GP03FLMA-RIS02-07-CTDMOG	130	0101000020E6100000E3A59BC4200862C04C37894160FD4840
248	CTDPF	\N	\N	73	248	GP02HYPM-WFP03-04-CTDPFL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
249	NUTNR	\N	\N	83	249	GP05MOAS-PG001-03-NUTNRM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
250	DOSTA	\N	\N	83	250	GP05MOAS-PG001-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
251	CTDMO	\N	\N	76	251	GP03FLMA-RIS02-10-CTDMOG	350	0101000020E6100000E3A59BC4200862C04C37894160FD4840
252	CTDGV	\N	\N	83	252	GP05MOAS-PG001-01-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
253	CTDMO	\N	\N	76	253	GP03FLMA-RIS02-06-CTDMOG	90	0101000020E6100000E3A59BC4200862C04C37894160FD4840
254	VEL3D	\N	\N	73	254	GP02HYPM-WFP03-05-VEL3DL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
255	CTDMO	\N	\N	76	255	GP03FLMA-RIS02-14-CTDMOH	1500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
256	FLORT	\N	\N	78	256	GP03FLMB-RIS01-01-FLORTD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
257	CTDGV	\N	\N	84	257	GP05MOAS-PG002-01-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
258	CTDMO	\N	\N	76	258	GP03FLMA-RIS02-05-CTDMOG	60	0101000020E6100000E3A59BC4200862C04C37894160FD4840
259	ADCPS	\N	\N	79	259	GP03FLMB-RIS02-01-ADCPSL	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
260	DOSTA	\N	\N	81	260	GP05MOAS-GL002-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
261	CTDMO	\N	\N	71	261	GP02HYPM-RIS01-01-CTDMOG000	164	0101000020E6100000E3A59BC4200862C04C37894160FD4840
262	ACOMM	\N	\N	79	262	GP03FLMB-RIS02-02-ACOMM0	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
263	PHSEN	\N	\N	78	263	GP03FLMB-RIS01-02-PHSENE	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
264	CTDMO	\N	\N	76	264	GP03FLMA-RIS02-13-CTDMOH	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
265	FLORD	\N	\N	72	265	GP02HYPM-WFP02-01-FLORDL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
266	CTDMO	\N	\N	76	266	GP03FLMA-RIS02-11-CTDMOG	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
267	OPTAA	\N	\N	84	267	GP05MOAS-PG002-03-OPTAAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
268	ACOMM	\N	\N	80	268	GP05MOAS-GL001-03-ACOMMM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
269	CTDMO	\N	\N	79	269	GP03FLMB-RIS02-10-CTDMOG	350	0101000020E6100000E3A59BC4200862C04C37894160FD4840
270	DOSTA	\N	\N	80	270	GP05MOAS-GL001-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
271	CTDPF	\N	\N	72	271	GP02HYPM-WFP02-04-CTDPFL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
272	ACOMM	\N	\N	76	272	GP03FLMA-RIS02-02-ACOMM0	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
273	CTDMO	\N	\N	76	273	GP03FLMA-RIS02-12-CTDMOH	750	0101000020E6100000E3A59BC4200862C04C37894160FD4840
274	DOSTA	\N	\N	82	274	GP05MOAS-GL003-02-DOSTAM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
275	ADCPS	\N	\N	76	275	GP03FLMA-RIS02-01-ADCPSL	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
276	CTDMO	\N	\N	79	276	GP03FLMB-RIS02-09-CTDMOG	250	0101000020E6100000E3A59BC4200862C04C37894160FD4840
277	FLORT	\N	\N	75	277	GP03FLMA-RIS01-01-FLORTD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
278	DOSTA	\N	\N	75	278	GP03FLMA-RIS01-03-DOSTAD	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
279	FLORD	\N	\N	73	279	GP02HYPM-WFP03-01-FLORDL000	4000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
280	CTDMO	\N	\N	76	280	GP03FLMA-RIS02-03-CTDMOG	30	0101000020E6100000E3A59BC4200862C04C37894160FD4840
281	CTDGV	\N	\N	80	281	GP05MOAS-GL001-04-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
282	CTDMO	\N	\N	76	282	GP03FLMA-RIS02-09-CTDMOG	250	0101000020E6100000E3A59BC4200862C04C37894160FD4840
283	DOSTA	\N	\N	72	283	GP02HYPM-WFP02-03-DOSTAL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
284	CTDGV	\N	\N	81	284	GP05MOAS-GL002-04-CTDGVM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
285	CTDMO	\N	\N	79	285	GP03FLMB-RIS02-13-CTDMOH	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
286	CTDMO	\N	\N	79	286	GP03FLMB-RIS02-14-CTDMOH	1500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
287	FLORD	\N	\N	81	287	GP05MOAS-GL002-01-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
288	FLORD	\N	\N	80	288	GP05MOAS-GL001-01-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
289	PHSEN	\N	\N	75	289	GP03FLMA-RIS01-02-PHSENE	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
290	CTDMO	\N	\N	79	290	GP03FLMB-RIS02-12-CTDMOH	750	0101000020E6100000E3A59BC4200862C04C37894160FD4840
291	CTDMO	\N	\N	79	291	GP03FLMB-RIS02-11-CTDMOG	500	0101000020E6100000E3A59BC4200862C04C37894160FD4840
292	CTDMO	\N	\N	79	292	GP03FLMB-RIS02-07-CTDMOG	130	0101000020E6100000E3A59BC4200862C04C37894160FD4840
293	CTDMO	\N	\N	79	293	GP03FLMB-RIS02-05-CTDMOG	60	0101000020E6100000E3A59BC4200862C04C37894160FD4840
294	FLORD	\N	\N	82	294	GP05MOAS-GL003-01-FLORDM000	1000	0101000020E6100000E3A59BC4200862C04C37894160FD4840
295	CTDMO	\N	\N	76	295	GP03FLMA-RIS02-04-CTDMOG	40	0101000020E6100000E3A59BC4200862C04C37894160FD4840
296	VEL3D	\N	\N	72	296	GP02HYPM-WFP02-05-VEL3DL000	2100	0101000020E6100000E3A59BC4200862C04C37894160FD4840
297	PARAD	\N	\N	134	297	CP05MOAS-AV001-06-PARADN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
298	PRESF	\N	\N	114	298	CP03ISSM-MFD35-02-PRESFB000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
299	MOPAK	\N	\N	91	299	CP01CNSM-MFD35-04-VELPTA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
300	FLORT	\N	\N	137	300	CP05MOAS-GL002-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
301	DOFST	\N	\N	107	301	CP02PMUI-WFP01-02-DOFSTK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
302	CTDPF	\N	\N	103	302	CP02PMCO-WFP01-03-CTDPFK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
303	PARAD	\N	\N	135	303	CP05MOAS-AV002-06-PARADN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
304	CTDBP	\N	\N	131	304	CP04OSSM-RID27-03-CTDBPC000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
305	NUTNR	\N	\N	131	305	CP04OSSM-RID27-07-NUTNRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
306	METBK	\N	\N	92	306	CP01CNSM-SBD12-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
307	DOSTA	\N	\N	115	307	CP03ISSM-MFD37-04-DOSTAD000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
308	PARAD	\N	\N	136	308	CP05MOAS-GL001-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
309	ADCPT	\N	\N	97	309	CP02PMCI-RII01-02-ADCPTG000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
310	PCO2A	\N	\N	119	310	CP03ISSM-SBD12-04-PCO2AA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
311	VEL3D	\N	\N	99	311	CP02PMCI-WFP01-01-VEL3DK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
312	PHSEN	\N	\N	114	312	CP03ISSM-MFD35-06-PHSEND000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
313	DOSTA	\N	\N	139	313	CP05MOAS-GL004-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
314	PARAD	\N	\N	125	314	CP04OSPM-WFP01-05-PARADK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
315	OPTAA	\N	\N	122	315	CP03ISSP-SP001-02-OPTAAJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
316	SPKIR	\N	\N	117	316	CP03ISSM-RID27-08-SPKIRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
317	PARAD	\N	\N	122	317	CP03ISSP-SP001-10-PARADJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
318	MOPAK	\N	\N	118	318	CP03ISSM-SBD11-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
319	VELPT	\N	\N	95	319	CP01CNSP-SP001-05-VELPTJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
320	DOSTA	\N	\N	141	320	CP05MOAS-GL006-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
321	MOPAK	\N	\N	106	321	CP02PMUI-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
322	ADCPT	\N	\N	87	322	CP01CNSM-MFD35-01-ADCPTF000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
323	FLORT	\N	\N	139	323	CP05MOAS-GL004-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
324	OPTAA	\N	\N	88	324	CP01CNSM-MFD37-01-OPTAAD000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
325	PARAD	\N	\N	141	325	CP05MOAS-GL006-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
326	DOSTA	\N	\N	90	326	CP01CNSM-RID27-04-DOSTAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
327	ADCPA	\N	\N	140	327	CP05MOAS-GL005-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
328	DOFST	\N	\N	99	328	CP02PMCI-WFP01-02-DOFSTK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
329	PARAD	\N	\N	107	329	CP02PMUI-WFP01-05-PARADK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
330	ADCPA	\N	\N	139	330	CP05MOAS-GL004-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
331	PCO2A	\N	\N	133	331	CP04OSSM-SBD12-04-PCO2AA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
332	DOSTA	\N	\N	135	332	CP05MOAS-AV002-02-DOSTAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
333	CTDBP	\N	\N	90	333	CP01CNSM-RID27-03-CTDBPC000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
334	OPTAA	\N	\N	95	334	CP01CNSP-SP001-02-OPTAAJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
335	PARAD	\N	\N	99	335	CP02PMCI-WFP01-05-PARADK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
336	DOSTA	\N	\N	136	336	CP05MOAS-GL001-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
337	ZPLSC	\N	\N	113	337	CP03ISSM-MFD00-00-ZPLSCC000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
338	CTDGV	\N	\N	137	338	CP05MOAS-GL002-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
339	PCO2W	\N	\N	128	339	CP04OSSM-MFD35-05-PCO2WB000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
340	DOFST	\N	\N	111	340	CP02PMUO-WFP01-02-DOFSTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
341	CTDBP	\N	\N	88	341	CP01CNSM-MFD37-03-CTDBPD000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
342	ZPLSC	\N	\N	86	342	CP01CNSM-MFD00-00-ZPLSCC000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
343	PARAD	\N	\N	140	343	CP05MOAS-GL005-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
344	DOSTA	\N	\N	88	344	CP01CNSM-MFD37-04-DOSTAD000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
345	CTDGV	\N	\N	136	345	CP05MOAS-GL001-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
346	VEL3D	\N	\N	111	346	CP02PMUO-WFP01-01-VEL3DK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
347	DOSTA	\N	\N	137	347	CP05MOAS-GL002-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
348	PARAD	\N	\N	138	348	CP05MOAS-GL003-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
349	CTDPF	\N	\N	99	349	CP02PMCI-WFP01-03-CTDPFK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
350	CTDBP	\N	\N	115	350	CP03ISSM-MFD37-03-CTDBPD000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
351	VEL3D	\N	\N	125	351	CP04OSPM-WFP01-01-VEL3DK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
352	FLORT	\N	\N	90	352	CP01CNSM-RID27-02-FLORTD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
353	METBK	\N	\N	91	353	CP01CNSM-SBD11-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
354	PCO2W	\N	\N	87	354	CP01CNSM-MFD35-05-PCO2WB000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
355	VELPT	\N	\N	128	355	CP04OSSM-MFD35-04-VELPTB000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
356	FLORT	\N	\N	136	356	CP05MOAS-GL001-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
357	ZPLSC	\N	\N	127	357	CP04OSSM-MFD00-00-ZPLSCC000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
358	CTDAV	\N	\N	134	358	CP05MOAS-AV001-03-CTDAVN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
359	PCO2A	\N	\N	92	359	CP01CNSM-SBD12-04-PCO2AA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
360	FLORT	\N	\N	138	360	CP05MOAS-GL003-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
361	SPKIR	\N	\N	90	361	CP01CNSM-RID27-08-SPKIRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
362	FLORT	\N	\N	140	362	CP05MOAS-GL005-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
363	CTDPF	\N	\N	125	363	CP04OSPM-WFP01-03-CTDPFK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
364	PARAD	\N	\N	139	364	CP05MOAS-GL004-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
365	ACOMM	\N	\N	130	365	CP04OSSM-RID26-05-ACOMM0000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
366	PHSEN	\N	\N	87	366	CP01CNSM-MFD35-06-PHSEND000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
367	CTDGV	\N	\N	139	367	CP05MOAS-GL004-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
368	PHSEN	\N	\N	128	368	CP04OSSM-MFD35-06-PHSEND000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
369	DOSTA	\N	\N	129	369	CP04OSSM-MFD37-04-DOSTAD000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
370	SPKIR	\N	\N	131	370	CP04OSSM-RID27-08-SPKIRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
371	FLORT	\N	\N	122	371	CP03ISSP-SP001-09-FLORTJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
372	ADCPA	\N	\N	134	372	CP05MOAS-AV001-05-ADCPAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
373	ACOMM	\N	\N	89	373	CP01CNSM-RID26-05-ACOMM0000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
374	SPKIR	\N	\N	122	374	CP03ISSP-SP001-07-SPKIRJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
375	ADCPS	\N	\N	128	375	CP04OSSM-MFD35-01-ADCPSJ000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
376	PARAD	\N	\N	95	376	CP01CNSP-SP001-10-PARADJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
377	OPTAA	\N	\N	129	377	CP04OSSM-MFD37-01-OPTAAD000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
378	MOPAK	\N	\N	102	378	CP02PMCO-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
379	MOPAK	\N	\N	132	379	CP04OSSM-SBD11-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
380	CTDBP	\N	\N	129	380	CP04OSSM-MFD37-03-CTDBPE000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
381	VELPT	\N	\N	130	381	CP04OSSM-RID26-04-VELPTA000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
382	DOSTA	\N	\N	117	382	CP03ISSM-RID27-04-DOSTAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
383	CTDGV	\N	\N	140	383	CP05MOAS-GL005-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
384	MOPAK	\N	\N	110	384	CP02PMUO-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
385	NUTNR	\N	\N	90	385	CP01CNSM-RID27-07-NUTNRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
386	OPTAA	\N	\N	115	386	CP03ISSM-MFD37-01-OPTAAD000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
387	PRESF	\N	\N	128	387	CP04OSSM-MFD35-02-PRESFC000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
388	PARAD	\N	\N	111	388	CP02PMUO-WFP01-05-PARADK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
389	ACOMM	\N	\N	94	389	CP01CNSP-PL001-01-ACOMM0	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
390	NUTNR	\N	\N	95	390	CP01CNSP-SP001-03-NUTNRJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
391	ADCPT	\N	\N	114	391	CP03ISSM-MFD35-01-ADCPTF000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
392	VEL3D	\N	\N	107	392	CP02PMUI-WFP01-01-VEL3DK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
393	DOSTA	\N	\N	140	393	CP05MOAS-GL005-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
394	VELPT	\N	\N	89	394	CP01CNSM-RID26-04-VELPTA000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
395	FLORT	\N	\N	103	395	CP02PMCO-WFP01-04-FLORTK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
396	PCO2W	\N	\N	114	396	CP03ISSM-MFD35-05-PCO2WB000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
397	PHSEN	\N	\N	130	397	CP04OSSM-RID26-06-PHSEND000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
398	ADCPA	\N	\N	135	398	CP05MOAS-AV002-05-ADCPAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
399	CTDAV	\N	\N	135	399	CP05MOAS-AV002-03-CTDAVN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
400	FLORT	\N	\N	117	400	CP03ISSM-RID27-02-FLORTD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
401	FLORT	\N	\N	131	401	CP04OSSM-RID27-02-FLORTD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
402	CTDPF	\N	\N	122	402	CP03ISSP-SP001-08-CTDPFJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
403	DOFST	\N	\N	125	403	CP04OSPM-WFP01-02-DOFSTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
404	PARAD	\N	\N	103	404	CP02PMCO-WFP01-05-PARADK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
405	DOSTA	\N	\N	122	405	CP03ISSP-SP001-06-DOSTAJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
406	ADCPT	\N	\N	105	406	CP02PMUI-RII01-02-ADCPTG000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
407	FLORT	\N	\N	111	407	CP02PMUO-WFP01-04-FLORTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
408	CTDGV	\N	\N	141	408	CP05MOAS-GL006-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
409	FLORT	\N	\N	95	409	CP01CNSP-SP001-09-FLORTJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
410	FLORT	\N	\N	134	410	CP05MOAS-AV001-01-FLORTN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
411	FDCHP	\N	\N	92	411	CP01CNSM-SBD12-08-FDCHPA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
412	NUTNR	\N	\N	134	412	CP05MOAS-AV001-04-NUTNRN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
413	ADCPA	\N	\N	138	413	CP05MOAS-GL003-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
414	DOFST	\N	\N	103	414	CP02PMCO-WFP01-02-DOFSTK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
415	OPTAA	\N	\N	131	415	CP04OSSM-RID27-01-OPTAAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
416	FLORT	\N	\N	135	416	CP05MOAS-AV002-01-FLORTN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
417	ADCPA	\N	\N	141	417	CP05MOAS-GL006-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
418	PHSEN	\N	\N	116	418	CP03ISSM-RID26-06-PHSEND000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
419	NUTNR	\N	\N	117	419	CP03ISSM-RID27-07-NUTNRB000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
420	WAVSS	\N	\N	92	420	CP01CNSM-SBD12-05-WAVSSA000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
421	DOSTA	\N	\N	95	421	CP01CNSP-SP001-06-DOSTAJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
422	METBK	\N	\N	132	422	CP04OSSM-SBD11-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
423	DOSTA	\N	\N	134	423	CP05MOAS-AV001-02-DOSTAN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
424	VELPT	\N	\N	116	424	CP03ISSM-RID26-04-VELPTA000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
425	FLORT	\N	\N	99	425	CP02PMCI-WFP01-04-FLORTK000	140	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
426	OPTAA	\N	\N	90	426	CP01CNSM-RID27-01-OPTAAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
427	PARAD	\N	\N	137	427	CP05MOAS-GL002-05-PARADM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
428	MOPAK	\N	\N	124	428	CP04OSPM-SBS11-02-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
429	CTDPF	\N	\N	95	429	CP01CNSP-SP001-08-CTDPFJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
430	FLORT	\N	\N	141	430	CP05MOAS-GL006-02-FLORTM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
431	CTDGV	\N	\N	138	431	CP05MOAS-GL003-03-CTDGVM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
432	MOPAK	\N	\N	98	432	CP02PMCI-SBS01-01-MOPAK0000	0	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
433	VELPT	\N	\N	114	433	CP03ISSM-MFD35-04-VELPTA000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
434	METBK	\N	\N	118	434	CP03ISSM-SBD11-06-METBKA000	3	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
435	ADCPT	\N	\N	101	435	CP02PMCO-RII01-02-ADCPTG000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
436	ADCPA	\N	\N	137	436	CP05MOAS-GL002-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
437	CTDBP	\N	\N	117	437	CP03ISSM-RID27-03-CTDBPC000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
438	ADCPS	\N	\N	109	438	CP02PMUO-RII01-02-ADCPSL000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
439	PHSEN	\N	\N	89	439	CP01CNSM-RID26-06-PHSEND000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
440	FLORT	\N	\N	125	440	CP04OSPM-WFP01-04-FLORTK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
441	NUTNR	\N	\N	135	441	CP05MOAS-AV002-04-NUTNRN000	-1	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
442	ACOMM	\N	\N	116	442	CP03ISSM-RID26-05-ACOMM0000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
443	VEL3D	\N	\N	103	443	CP02PMCO-WFP01-01-VEL3DK000	360	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
444	VELPT	\N	\N	122	444	CP03ISSP-SP001-05-VELPTJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
445	ADCPA	\N	\N	136	445	CP05MOAS-GL001-01-ADCPAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
446	SPKIR	\N	\N	95	446	CP01CNSP-SP001-07-SPKIRJ	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
447	FLORT	\N	\N	107	447	CP02PMUI-WFP01-04-FLORTK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
448	ACOMM	\N	\N	121	448	CP03ISSP-PL001-01-ACOMM0	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
449	CTDPF	\N	\N	111	449	CP02PMUO-WFP01-03-CTDPFK000	520	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
450	PRESF	\N	\N	87	450	CP01CNSM-MFD35-02-PRESFB000	210	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
451	DOSTA	\N	\N	131	451	CP04OSSM-RID27-04-DOSTAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
452	OPTAA	\N	\N	117	452	CP03ISSM-RID27-01-OPTAAD000	5	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
453	DOSTA	\N	\N	138	453	CP05MOAS-GL003-04-DOSTAM000	1000	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
454	CTDPF	\N	\N	107	454	CP02PMUI-WFP01-03-CTDPFK000	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
455	NUTNR	\N	\N	122	455	CP03ISSP-SP001-03-NUTNRJ	130	0101000020E6100000B81E85EB51B851C0CDCCCCCCCC0C4440
456	CTDMO	\N	\N	157	456	GA03FLMB-RIS02-13-CTDMOH	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
457	DOSTA	\N	\N	160	457	GA05MOAS-GL003-02-DOSTAM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
458	CTDMO	\N	\N	157	458	GA03FLMB-RIS02-08-CTDMOG	180	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
459	DOSTA	\N	\N	158	459	GA05MOAS-GL001-02-DOSTAM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
460	CTDMO	\N	\N	154	460	GA03FLMA-RIS02-07-CTDMOG	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
461	PHSEN	\N	\N	156	461	GA03FLMB-RIS01-02-PHSENE	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
462	PHSEN	\N	\N	153	462	GA03FLMA-RIS01-02-PHSENE	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
463	CTDMO	\N	\N	143	463	GA01SUMO-RII11-02-CTDMOR015	1500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
464	CTDMO	\N	\N	143	464	GA01SUMO-RII11-02-CTDMOR014	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
465	CTDMO	\N	\N	143	465	GA01SUMO-RII11-02-CTDMOR013	750	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
466	MOPAK	\N	\N	144	466	GA01SUMO-SBD11-01-MOPAK0000	0	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
467	CTDMO	\N	\N	157	467	GA03FLMB-RIS02-07-CTDMOG	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
468	METBK	\N	\N	144	468	GA01SUMO-SBD11-06-METBKA000	5	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
469	CTDBP	\N	\N	143	469	GA01SUMO-RII11-02-CTDBPP201	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
470	FLORD	\N	\N	143	470	GA01SUMO-RII11-02-FLORDG203	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
471	DOSTA	\N	\N	144	471	GA01SUMO-SBD11-04-DOSTAD000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
472	DOSTA	\N	\N	143	472	GA01SUMO-RII11-02-DOSTAD302	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
473	PCO2W	\N	\N	143	473	GA01SUMO-RII11-02-PCO2WC104	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
474	CTDMO	\N	\N	157	474	GA03FLMB-RIS02-06-CTDMOG	90	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
475	PCO2A	\N	\N	145	475	GA01SUMO-SBD12-04-PCO2AA000	0	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
476	CTDBP	\N	\N	142	476	GA01SUMO-RID16-03-CTDBPF000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
477	CTDMO	\N	\N	154	477	GA03FLMA-RIS02-12-CTDMOH	750	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
478	CTDMO	\N	\N	157	478	GA03FLMB-RIS02-11-CTDMOG	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
479	METBK	\N	\N	145	479	GA01SUMO-SBD12-06-METBKA000	5	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
480	FLORT	\N	\N	145	480	GA01SUMO-SBD12-02-FLORTD000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
481	ZPLSG	\N	\N	148	481	GA02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
482	VEL3D	\N	\N	150	482	GA02HYPM-WFP02-05-VEL3DL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
483	SPKIR	\N	\N	142	483	GA01SUMO-RID16-08-SPKIRB000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
484	FLORD	\N	\N	143	484	GA01SUMO-RII11-02-FLORDG103	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
485	CTDMO	\N	\N	157	485	GA03FLMB-RIS02-12-CTDMOH	750	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
486	CTDGV	\N	\N	162	486	GA05MOAS-PG002-01-CTDGVM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
487	CTDMO	\N	\N	154	487	GA03FLMA-RIS02-09-CTDMOG	250	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
488	SPKIR	\N	\N	144	488	GA01SUMO-SBD11-05-SPKIRB000	5	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
489	DOSTA	\N	\N	156	489	GA03FLMB-RIS01-03-DOSTAD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
490	PARAD	\N	\N	162	490	GA05MOAS-PG002-04-PARADM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
491	CTDMO	\N	\N	154	491	GA03FLMA-RIS02-04-CTDMOG	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
492	NUTNR	\N	\N	161	492	GA05MOAS-PG001-03-NUTNRM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
493	ACOMM	\N	\N	160	493	GA05MOAS-GL003-03-ACOMMM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
494	VEL3D	\N	\N	151	494	GA02HYPM-WFP03-05-VEL3DL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
495	ADCPS	\N	\N	143	495	GA01SUMO-RII11-02-ADCPSN011	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
496	DOSTA	\N	\N	153	496	GA03FLMA-RIS01-03-DOSTAD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
497	ADCPS	\N	\N	154	497	GA03FLMA-RIS02-01-ADCPSL	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
498	CTDGV	\N	\N	161	498	GA05MOAS-PG001-01-CTDGVM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
499	FLORD	\N	\N	151	499	GA02HYPM-WFP03-01-FLORDL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
500	CTDMO	\N	\N	143	500	GA01SUMO-RII11-02-CTDMOQ001	20	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
501	CTDMO	\N	\N	143	501	GA01SUMO-RII11-02-CTDMOQ005	100	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
502	CTDMO	\N	\N	143	502	GA01SUMO-RII11-02-CTDMOQ004	60	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
503	CTDMO	\N	\N	157	503	GA03FLMB-RIS02-14-CTDMOH	1500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
504	CTDMO	\N	\N	154	504	GA03FLMA-RIS02-14-CTDMOH	1500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
505	CTDMO	\N	\N	143	505	GA01SUMO-RII11-02-CTDMOQ008	180	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
506	CTDMO	\N	\N	149	506	GA02HYPM-RIS01-01-CTDMOG000	164	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
507	ACOMM	\N	\N	142	507	GA01SUMO-RID16-00-ACOMM0000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
508	FLORD	\N	\N	162	508	GA05MOAS-PG002-02-FLORDM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
509	NUTNR	\N	\N	142	509	GA01SUMO-RID16-07-NUTNRB000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
510	CTDPF	\N	\N	151	510	GA02HYPM-WFP03-04-CTDPFL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
511	OPTAA	\N	\N	142	511	GA01SUMO-RID16-01-OPTAAD000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
512	CTDMO	\N	\N	154	512	GA03FLMA-RIS02-10-CTDMOG	350	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
513	CTDMO	\N	\N	154	513	GA03FLMA-RIS02-05-CTDMOG	60	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
514	CTDMO	\N	\N	157	514	GA03FLMB-RIS02-09-CTDMOG	250	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
515	DOSTA	\N	\N	161	515	GA05MOAS-PG001-02-DOSTAM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
516	CTDMO	\N	\N	143	516	GA01SUMO-RII11-02-CTDMOQ010	350	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
517	CTDMO	\N	\N	143	517	GA01SUMO-RII11-02-CTDMOQ012	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
518	OPTAA	\N	\N	145	518	GA01SUMO-SBD12-01-OPTAAD000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
519	DOSTA	\N	\N	159	519	GA05MOAS-GL002-02-DOSTAM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
520	DOSTA	\N	\N	143	520	GA01SUMO-RII11-02-DOSTAD102	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
521	FLORD	\N	\N	160	521	GA05MOAS-GL003-01-FLORDM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
522	FLORT	\N	\N	153	522	GA03FLMA-RIS01-01-FLORTD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
523	CTDMO	\N	\N	154	523	GA03FLMA-RIS02-08-CTDMOG	180	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
524	CTDMO	\N	\N	154	524	GA03FLMA-RIS02-06-CTDMOG	90	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
525	ACOMM	\N	\N	159	525	GA05MOAS-GL002-03-ACOMMM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
526	CTDGV	\N	\N	160	526	GA05MOAS-GL003-04-CTDGVM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
527	FLORD	\N	\N	150	527	GA02HYPM-WFP02-01-FLORDL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
528	PCO2W	\N	\N	143	528	GA01SUMO-RII11-02-PCO2WC304	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
529	PHSEN	\N	\N	143	529	GA01SUMO-RII11-02-PHSENE002	20	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
530	PHSEN	\N	\N	143	530	GA01SUMO-RII11-02-PHSENE006	100	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
531	CTDMO	\N	\N	154	531	GA03FLMA-RIS02-03-CTDMOG	30	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
532	ACOMM	\N	\N	157	532	GA03FLMB-RIS02-02-ACOMM0	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
533	CTDBP	\N	\N	143	533	GA01SUMO-RII11-02-CTDBPP003	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
534	CTDMO	\N	\N	157	534	GA03FLMB-RIS02-10-CTDMOG	350	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
535	VELPT	\N	\N	142	535	GA01SUMO-RID16-04-VELPTA000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
536	DOSTA	\N	\N	150	536	GA02HYPM-WFP02-03-DOSTAL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
537	PCO2W	\N	\N	142	537	GA01SUMO-RID16-05-PCO2WB000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
538	CTDPF	\N	\N	150	538	GA02HYPM-WFP02-04-CTDPFL000	2600	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
539	CTDMO	\N	\N	157	539	GA03FLMB-RIS02-04-CTDMOG	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
540	FLORD	\N	\N	159	540	GA05MOAS-GL002-01-FLORDM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
541	OPTAA	\N	\N	162	541	GA05MOAS-PG002-03-OPTAAM000	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
542	CTDMO	\N	\N	157	542	GA03FLMB-RIS02-05-CTDMOG	60	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
543	FLORD	\N	\N	158	543	GA05MOAS-GL001-01-FLORDM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
544	CTDMO	\N	\N	154	544	GA03FLMA-RIS02-13-CTDMOH	1000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
545	DOSTA	\N	\N	142	545	GA01SUMO-RID16-03-DOSTAD000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
546	ADCPS	\N	\N	157	546	GA03FLMB-RIS02-01-ADCPSL	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
547	CTDMO	\N	\N	154	547	GA03FLMA-RIS02-11-CTDMOG	500	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
548	CTDMO	\N	\N	157	548	GA03FLMB-RIS02-03-CTDMOG	30	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
549	DOSTA	\N	\N	151	549	GA02HYPM-WFP03-03-DOSTAL000	5000	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
550	DOSTA	\N	\N	143	550	GA01SUMO-RII11-02-DOSTAD202	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
551	NUTNR	\N	\N	144	551	GA01SUMO-SBD11-08-NUTNRB000	1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
552	CTDGV	\N	\N	158	552	GA05MOAS-GL001-04-CTDGVM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
553	FLORT	\N	\N	156	553	GA03FLMB-RIS01-01-FLORTD	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
554	CTDMO	\N	\N	143	554	GA01SUMO-RII11-02-CTDMOQ009	250	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
555	ACOMM	\N	\N	154	555	GA03FLMA-RIS02-02-ACOMM0	40	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
556	WAVSS	\N	\N	145	556	GA01SUMO-SBD12-05-WAVSSA000	0	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
557	FLORT	\N	\N	142	557	GA01SUMO-RID16-02-FLORTD000	12	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
558	CTDBP	\N	\N	143	558	GA01SUMO-RII11-02-CTDBPP007	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
559	PCO2W	\N	\N	143	559	GA01SUMO-RII11-02-PCO2WC204	80	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
560	ACOMM	\N	\N	158	560	GA05MOAS-GL001-03-ACOMMM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
561	FLORD	\N	\N	143	561	GA01SUMO-RII11-02-FLORDG303	130	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
562	CTDGV	\N	\N	159	562	GA05MOAS-GL002-04-CTDGVM000	-1	0101000020E6100000448B6CE7FB7145C062A1D634EF4045C0
563	DOSTA	\N	\N	173	563	GI03FLMA-RIS01-03-DOSTAD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
564	PCO2W	\N	\N	164	564	GI01SUMO-RII11-02-PCO2WC304	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
565	METBK	\N	\N	166	565	GI01SUMO-SBD12-06-METBKA000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
566	CTDMO	\N	\N	177	566	GI03FLMB-RIS02-10-CTDMOG	350	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
567	VELPT	\N	\N	163	567	GI01SUMO-RID16-04-VELPTA000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
568	FLORD	\N	\N	178	568	GI05MOAS-GL001-01-FLORDM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
569	VELPT	\N	\N	174	569	GI03FLMA-RIS02-21-VELPTB	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
570	CTDMO	\N	\N	177	570	GI03FLMB-RIS02-11-CTDMOG	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
571	PHSEN	\N	\N	164	571	GI01SUMO-RII11-02-PHSENE002	20	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
572	PHSEN	\N	\N	164	572	GI01SUMO-RII11-02-PHSENE006	100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
573	DOSTA	\N	\N	165	573	GI01SUMO-SBD11-04-DOSTAD000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
574	SPKIR	\N	\N	165	574	GI01SUMO-SBD11-05-SPKIRB000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
575	CTDGV	\N	\N	181	575	GI05MOAS-PG001-01-CTDGVM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
576	VELPT	\N	\N	177	576	GI03FLMB-RIS02-20-VELPTB	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
577	CTDGV	\N	\N	180	577	GI05MOAS-GL003-04-CTDGVM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
578	FLORD	\N	\N	164	578	GI01SUMO-RII11-02-FLORDG203	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
579	DOSTA	\N	\N	164	579	GI01SUMO-RII11-02-DOSTAD302	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
580	FLORD	\N	\N	180	580	GI05MOAS-GL003-01-FLORDM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
581	SPKIR	\N	\N	163	581	GI01SUMO-RID16-08-SPKIRB000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
582	DOSTA	\N	\N	179	582	GI05MOAS-GL002-02-DOSTAM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
583	ACOMM	\N	\N	179	583	GI05MOAS-GL002-03-ACOMMM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
584	CTDMO	\N	\N	177	584	GI03FLMB-RIS02-14-CTDMOH	1500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
585	CTDGV	\N	\N	178	585	GI05MOAS-GL001-04-CTDGVM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
586	NUTNR	\N	\N	163	586	GI01SUMO-RID16-07-NUTNRB000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
587	VELPT	\N	\N	177	587	GI03FLMB-RIS02-21-VELPTB	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
588	CTDMO	\N	\N	174	588	GI03FLMA-RIS02-18-CTDMOH	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
589	VELPT	\N	\N	177	589	GI03FLMB-RIS02-22-VELPTB	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
590	DOSTA	\N	\N	178	590	GI05MOAS-GL001-02-DOSTAM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
591	CTDBP	\N	\N	164	591	GI01SUMO-RII11-02-CTDBPP007	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
592	CTDBP	\N	\N	164	592	GI01SUMO-RII11-02-CTDBPP003	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
593	CTDMO	\N	\N	174	593	GI03FLMA-RIS02-03-CTDMOG	30	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
594	CTDGV	\N	\N	179	594	GI05MOAS-GL002-04-CTDGVM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
595	PCO2W	\N	\N	164	595	GI01SUMO-RII11-02-PCO2WC104	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
596	FLORD	\N	\N	164	596	GI01SUMO-RII11-02-FLORDG103	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
597	FLORD	\N	\N	164	597	GI01SUMO-RII11-02-FLORDG303	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
598	ACOMM	\N	\N	177	598	GI03FLMB-RIS02-02-ACOMM0	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
599	CTDMO	\N	\N	174	599	GI03FLMA-RIS02-04-CTDMOG	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
600	ACOMM	\N	\N	163	600	GI01SUMO-RID16-00-ACOMM0000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
601	PCO2W	\N	\N	164	601	GI01SUMO-RII11-02-PCO2WC204	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
602	VELPT	\N	\N	177	602	GI03FLMB-RIS02-19-VELPTB	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
603	CTDMO	\N	\N	174	603	GI03FLMA-RIS02-05-CTDMOG	60	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
604	CTDMO	\N	\N	164	604	GI01SUMO-RII11-02-CTDMOR015	1500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
605	CTDMO	\N	\N	164	605	GI01SUMO-RII11-02-CTDMOR014	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
606	CTDMO	\N	\N	174	606	GI03FLMA-RIS02-16-CTDMOH	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
607	PCO2A	\N	\N	166	607	GI01SUMO-SBD12-04-PCO2AA000	0	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
608	CTDMO	\N	\N	164	608	GI01SUMO-RII11-02-CTDMOR013	750	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
609	VEL3D	\N	\N	171	609	GI02HYPM-WFP02-05-VEL3DL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
610	CTDMO	\N	\N	177	610	GI03FLMB-RIS02-17-CTDMOH	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
611	PHSEN	\N	\N	176	611	GI03FLMB-RIS01-02-PHSENE	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
612	CTDMO	\N	\N	174	612	GI03FLMA-RIS02-09-CTDMOG	250	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
613	FDCHP	\N	\N	166	613	GI01SUMO-SBD12-08-FDCHPA000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
614	CTDMO	\N	\N	177	614	GI03FLMB-RIS02-16-CTDMOH	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
615	NUTNR	\N	\N	181	615	GI05MOAS-PG001-03-NUTNRM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
616	OPTAA	\N	\N	182	616	GI05MOAS-PG002-03-OPTAAM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
617	PCO2W	\N	\N	163	617	GI01SUMO-RID16-05-PCO2WB000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
618	METBK	\N	\N	165	618	GI01SUMO-SBD11-06-METBKA000	5	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
619	CTDPF	\N	\N	171	619	GI02HYPM-WFP02-04-CTDPFL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
620	VELPT	\N	\N	174	620	GI03FLMA-RIS02-20-VELPTB	2100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
621	CTDMO	\N	\N	174	621	GI03FLMA-RIS02-12-CTDMOH	750	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
622	DOSTA	\N	\N	164	622	GI01SUMO-RII11-02-DOSTAD102	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
623	CTDMO	\N	\N	174	623	GI03FLMA-RIS02-13-CTDMOH	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
624	ACOMM	\N	\N	178	624	GI05MOAS-GL001-03-ACOMMM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
625	ADCPS	\N	\N	177	625	GI03FLMB-RIS02-01-ADCPSL	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
626	CTDMO	\N	\N	177	626	GI03FLMB-RIS02-04-CTDMOG	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
627	CTDMO	\N	\N	174	627	GI03FLMA-RIS02-08-CTDMOG	180	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
628	CTDMO	\N	\N	170	628	GI02HYPM-RIS01-01-CTDMOG000	164	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
629	CTDMO	\N	\N	174	629	GI03FLMA-RIS02-15-CTDMOH	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
630	OPTAA	\N	\N	163	630	GI01SUMO-RID16-01-OPTAAD000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
631	DOSTA	\N	\N	180	631	GI05MOAS-GL003-02-DOSTAM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
632	NUTNR	\N	\N	165	632	GI01SUMO-SBD11-08-NUTNRB000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
633	CTDMO	\N	\N	174	633	GI03FLMA-RIS02-14-CTDMOH	1500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
634	DOSTA	\N	\N	181	634	GI05MOAS-PG001-02-DOSTAM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
635	PHSEN	\N	\N	173	635	GI03FLMA-RIS01-02-PHSENE	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
636	CTDMO	\N	\N	177	636	GI03FLMB-RIS02-03-CTDMOG	30	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
637	ACOMM	\N	\N	180	637	GI05MOAS-GL003-03-ACOMMM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
638	CTDMO	\N	\N	177	638	GI03FLMB-RIS02-18-CTDMOH	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
639	DOSTA	\N	\N	171	639	GI02HYPM-WFP02-03-DOSTAL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
640	CTDMO	\N	\N	174	640	GI03FLMA-RIS02-17-CTDMOH	2400	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
641	CTDBP	\N	\N	164	641	GI01SUMO-RII11-02-CTDBPP201	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
642	FLORT	\N	\N	163	642	GI01SUMO-RID16-02-FLORTD000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
643	FLORT	\N	\N	166	643	GI01SUMO-SBD12-02-FLORTD000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
644	ZPLSG	\N	\N	169	644	GI02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
645	OPTAA	\N	\N	166	645	GI01SUMO-SBD12-01-OPTAAD000	1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
646	CTDMO	\N	\N	177	646	GI03FLMB-RIS02-15-CTDMOH	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
647	WAVSS	\N	\N	166	647	GI01SUMO-SBD12-05-WAVSSA000	0	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
648	CTDMO	\N	\N	177	648	GI03FLMB-RIS02-12-CTDMOH	750	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
649	CTDMO	\N	\N	177	649	GI03FLMB-RIS02-13-CTDMOH	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
650	CTDMO	\N	\N	177	650	GI03FLMB-RIS02-09-CTDMOG	250	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
651	CTDGV	\N	\N	182	651	GI05MOAS-PG002-01-CTDGVM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
652	CTDMO	\N	\N	177	652	GI03FLMB-RIS02-07-CTDMOG	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
653	CTDMO	\N	\N	164	653	GI01SUMO-RII11-02-CTDMOQ009	250	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
654	CTDMO	\N	\N	164	654	GI01SUMO-RII11-02-CTDMOQ008	180	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
655	CTDBP	\N	\N	163	655	GI01SUMO-RID16-03-CTDBPF000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
656	CTDMO	\N	\N	164	656	GI01SUMO-RII11-02-CTDMOQ001	20	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
657	CTDMO	\N	\N	164	657	GI01SUMO-RII11-02-CTDMOQ005	100	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
658	CTDMO	\N	\N	164	658	GI01SUMO-RII11-02-CTDMOQ004	60	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
659	DOSTA	\N	\N	164	659	GI01SUMO-RII11-02-DOSTAD202	80	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
660	CTDMO	\N	\N	177	660	GI03FLMB-RIS02-06-CTDMOG	90	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
661	CTDMO	\N	\N	177	661	GI03FLMB-RIS02-05-CTDMOG	60	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
662	CTDMO	\N	\N	174	662	GI03FLMA-RIS02-11-CTDMOG	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
663	ADCPS	\N	\N	164	663	GI01SUMO-RII11-02-ADCPSN011	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
664	CTDMO	\N	\N	177	664	GI03FLMB-RIS02-08-CTDMOG	180	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
665	FLORD	\N	\N	171	665	GI02HYPM-WFP02-01-FLORDL000	2600	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
666	FLORD	\N	\N	182	666	GI05MOAS-PG002-02-FLORDM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
667	ADCPS	\N	\N	174	667	GI03FLMA-RIS02-01-ADCPSL	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
668	ACOMM	\N	\N	174	668	GI03FLMA-RIS02-02-ACOMM0	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
669	CTDMO	\N	\N	174	669	GI03FLMA-RIS02-06-CTDMOG	90	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
670	CTDMO	\N	\N	174	670	GI03FLMA-RIS02-07-CTDMOG	130	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
671	FLORT	\N	\N	176	671	GI03FLMB-RIS01-01-FLORTD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
672	VELPT	\N	\N	174	672	GI03FLMA-RIS02-22-VELPTB	2700	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
673	VELPT	\N	\N	174	673	GI03FLMA-RIS02-19-VELPTB	1800	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
674	DOSTA	\N	\N	176	674	GI03FLMB-RIS01-03-DOSTAD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
675	FLORT	\N	\N	173	675	GI03FLMA-RIS01-01-FLORTD	40	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
676	DOSTA	\N	\N	163	676	GI01SUMO-RID16-03-DOSTAD000	12	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
677	CTDMO	\N	\N	164	677	GI01SUMO-RII11-02-CTDMOQ010	350	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
678	CTDMO	\N	\N	164	678	GI01SUMO-RII11-02-CTDMOQ012	500	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
679	FLORD	\N	\N	179	679	GI05MOAS-GL002-01-FLORDM000	-1	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
680	CTDMO	\N	\N	174	680	GI03FLMA-RIS02-10-CTDMOG	350	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
681	MOPAK	\N	\N	165	681	GI01SUMO-SBD11-01-MOPAK0000	0	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
682	PARAD	\N	\N	182	682	GI05MOAS-PG002-04-PARADM000	1000	0101000020E610000071AC8BDB683843C07B832F4CA63A4E40
683	CTDMO	\N	\N	198	683	GS03FLMB-RIS02-11-CTDMOG	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
684	FLORT	\N	\N	183	684	GS01SUMO-RID16-02-FLORTD000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
685	CTDMO	\N	\N	198	685	GS03FLMB-RIS02-10-CTDMOG	350	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
686	OPTAA	\N	\N	203	686	GS05MOAS-PG002-03-OPTAAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
687	FLORD	\N	\N	184	687	GS01SUMO-RII11-02-FLORDG303	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
688	FLORT	\N	\N	186	688	GS01SUMO-SBD12-02-FLORTD000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
689	DOSTA	\N	\N	184	689	GS01SUMO-RII11-02-DOSTAD302	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
690	CTDBP	\N	\N	184	690	GS01SUMO-RII11-02-CTDBPP003	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
691	ADCPS	\N	\N	184	691	GS01SUMO-RII11-02-ADCPSN011	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
692	PHSEN	\N	\N	197	692	GS03FLMB-RIS01-02-PHSENE	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
693	FLORD	\N	\N	191	693	GS02HYPM-WFP02-01-FLORDL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
694	ADCPS	\N	\N	195	694	GS03FLMA-RIS02-01-ADCPSL	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
695	ACOMM	\N	\N	199	695	GS05MOAS-GL001-03-ACOMMM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
696	WAVSS	\N	\N	186	696	GS01SUMO-SBD12-05-WAVSSA000	0	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
697	CTDMO	\N	\N	198	697	GS03FLMB-RIS02-03-CTDMOG	30	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
698	OPTAA	\N	\N	186	698	GS01SUMO-SBD12-01-OPTAAD000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
699	ACOMM	\N	\N	201	699	GS05MOAS-GL003-03-ACOMMM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
700	VEL3D	\N	\N	192	700	GS02HYPM-WFP03-05-VEL3DL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
701	CTDMO	\N	\N	195	701	GS03FLMA-RIS02-05-CTDMOG	60	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
702	SPKIR	\N	\N	183	702	GS01SUMO-RID16-08-SPKIRB000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
703	PCO2A	\N	\N	186	703	GS01SUMO-SBD12-04-PCO2AA000	0	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
704	CTDMO	\N	\N	195	704	GS03FLMA-RIS02-07-CTDMOG	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
705	CTDPF	\N	\N	191	705	GS02HYPM-WFP02-04-CTDPFL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
706	CTDMO	\N	\N	198	706	GS03FLMB-RIS02-06-CTDMOG	90	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
707	CTDMO	\N	\N	190	707	GS02HYPM-RIS01-01-CTDMOG000	164	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
708	ZPLSG	\N	\N	189	708	GS02HYPM-MPC04-01-ZPLSGA000	-1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
709	NUTNR	\N	\N	202	709	GS05MOAS-PG001-03-NUTNRM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
710	NUTNR	\N	\N	185	710	GS01SUMO-SBD11-08-NUTNRB000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
711	CTDMO	\N	\N	195	711	GS03FLMA-RIS02-11-CTDMOG	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
712	CTDMO	\N	\N	195	712	GS03FLMA-RIS02-10-CTDMOG	350	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
713	CTDMO	\N	\N	184	713	GS01SUMO-RII11-02-CTDMOQ009	250	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
714	CTDMO	\N	\N	184	714	GS01SUMO-RII11-02-CTDMOQ008	180	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
715	CTDMO	\N	\N	184	715	GS01SUMO-RII11-02-CTDMOQ005	100	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
716	CTDMO	\N	\N	184	716	GS01SUMO-RII11-02-CTDMOQ004	60	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
717	CTDMO	\N	\N	198	717	GS03FLMB-RIS02-13-CTDMOH	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
718	CTDMO	\N	\N	184	718	GS01SUMO-RII11-02-CTDMOQ001	20	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
719	METBK	\N	\N	185	719	GS01SUMO-SBD11-06-METBKA000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
720	METBK	\N	\N	186	720	GS01SUMO-SBD12-06-METBKA000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
721	CTDMO	\N	\N	198	721	GS03FLMB-RIS02-12-CTDMOH	750	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
722	DOSTA	\N	\N	185	722	GS01SUMO-SBD11-04-DOSTAD000	1	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
723	CTDMO	\N	\N	195	723	GS03FLMA-RIS02-14-CTDMOH	1500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
724	CTDGV	\N	\N	199	724	GS05MOAS-GL001-04-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
725	VELPT	\N	\N	183	725	GS01SUMO-RID16-04-VELPTA000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
726	DOSTA	\N	\N	183	726	GS01SUMO-RID16-03-DOSTAD000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
727	CTDGV	\N	\N	201	727	GS05MOAS-GL003-04-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
728	CTDMO	\N	\N	184	728	GS01SUMO-RII11-02-CTDMOQ012	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
729	CTDMO	\N	\N	184	729	GS01SUMO-RII11-02-CTDMOQ010	350	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
730	FLORD	\N	\N	201	730	GS05MOAS-GL003-01-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
731	ACOMM	\N	\N	198	731	GS03FLMB-RIS02-02-ACOMM0	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
732	VEL3D	\N	\N	191	732	GS02HYPM-WFP02-05-VEL3DL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
733	DOSTA	\N	\N	184	733	GS01SUMO-RII11-02-DOSTAD102	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
734	CTDBP	\N	\N	184	734	GS01SUMO-RII11-02-CTDBPP007	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
735	CTDMO	\N	\N	198	735	GS03FLMB-RIS02-09-CTDMOG	250	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
736	CTDMO	\N	\N	195	736	GS03FLMA-RIS02-12-CTDMOH	750	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
737	DOSTA	\N	\N	202	737	GS05MOAS-PG001-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
738	CTDMO	\N	\N	198	738	GS03FLMB-RIS02-04-CTDMOG	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
739	DOSTA	\N	\N	197	739	GS03FLMB-RIS01-03-DOSTAD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
740	PHSEN	\N	\N	184	740	GS01SUMO-RII11-02-PHSENE006	100	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
741	FLORD	\N	\N	200	741	GS05MOAS-GL002-01-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
742	PCO2W	\N	\N	184	742	GS01SUMO-RII11-02-PCO2WC204	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
743	PHSEN	\N	\N	184	743	GS01SUMO-RII11-02-PHSENE002	20	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
744	CTDMO	\N	\N	195	744	GS03FLMA-RIS02-13-CTDMOH	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
745	CTDMO	\N	\N	198	745	GS03FLMB-RIS02-07-CTDMOG	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
746	CTDMO	\N	\N	195	746	GS03FLMA-RIS02-03-CTDMOG	30	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
747	ADCPS	\N	\N	198	747	GS03FLMB-RIS02-01-ADCPSL	500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
748	CTDGV	\N	\N	200	748	GS05MOAS-GL002-04-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
749	DOSTA	\N	\N	184	749	GS01SUMO-RII11-02-DOSTAD202	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
750	FLORD	\N	\N	184	750	GS01SUMO-RII11-02-FLORDG203	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
751	CTDBP	\N	\N	183	751	GS01SUMO-RID16-03-CTDBPF000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
752	ACOMM	\N	\N	183	752	GS01SUMO-RID16-00-ACOMM0000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
753	PCO2W	\N	\N	184	753	GS01SUMO-RII11-02-PCO2WC304	130	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
754	FLORD	\N	\N	203	754	GS05MOAS-PG002-02-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
755	DOSTA	\N	\N	191	755	GS02HYPM-WFP02-03-DOSTAL000	2400	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
756	CTDMO	\N	\N	195	756	GS03FLMA-RIS02-08-CTDMOG	180	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
757	DOSTA	\N	\N	192	757	GS02HYPM-WFP03-03-DOSTAL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
758	CTDGV	\N	\N	203	758	GS05MOAS-PG002-01-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
759	DOSTA	\N	\N	201	759	GS05MOAS-GL003-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
760	ACOMM	\N	\N	195	760	GS03FLMA-RIS02-02-ACOMM0	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
761	CTDMO	\N	\N	198	761	GS03FLMB-RIS02-08-CTDMOG	180	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
762	OPTAA	\N	\N	183	762	GS01SUMO-RID16-01-OPTAAD000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
763	SPKIR	\N	\N	185	763	GS01SUMO-SBD11-05-SPKIRB000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
764	CTDBP	\N	\N	184	764	GS01SUMO-RII11-02-CTDBPP201	80	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
765	ACOMM	\N	\N	200	765	GS05MOAS-GL002-03-ACOMMM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
766	CTDMO	\N	\N	195	766	GS03FLMA-RIS02-04-CTDMOG	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
767	DOSTA	\N	\N	200	767	GS05MOAS-GL002-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
768	DOSTA	\N	\N	199	768	GS05MOAS-GL001-02-DOSTAM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
769	FLORT	\N	\N	197	769	GS03FLMB-RIS01-01-FLORTD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
770	CTDGV	\N	\N	202	770	GS05MOAS-PG001-01-CTDGVM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
771	FLORT	\N	\N	194	771	GS03FLMA-RIS01-01-FLORTD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
772	NUTNR	\N	\N	183	772	GS01SUMO-RID16-07-NUTNRB000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
773	PCO2W	\N	\N	184	773	GS01SUMO-RII11-02-PCO2WC104	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
774	PARAD	\N	\N	203	774	GS05MOAS-PG002-04-PARADM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
775	CTDMO	\N	\N	184	775	GS01SUMO-RII11-02-CTDMOR013	750	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
776	CTDMO	\N	\N	184	776	GS01SUMO-RII11-02-CTDMOR015	1500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
777	CTDMO	\N	\N	184	777	GS01SUMO-RII11-02-CTDMOR014	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
778	FLORD	\N	\N	192	778	GS02HYPM-WFP03-01-FLORDL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
779	PHSEN	\N	\N	194	779	GS03FLMA-RIS01-02-PHSENE	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
780	DOSTA	\N	\N	194	780	GS03FLMA-RIS01-03-DOSTAD	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
781	PCO2W	\N	\N	183	781	GS01SUMO-RID16-05-PCO2WB000	12	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
782	FDCHP	\N	\N	186	782	GS01SUMO-SBD12-08-FDCHPA000	5	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
783	CTDMO	\N	\N	198	783	GS03FLMB-RIS02-05-CTDMOG	60	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
784	FLORD	\N	\N	199	784	GS05MOAS-GL001-01-FLORDM000	1000	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
785	MOPAK	\N	\N	185	785	GS01SUMO-SBD11-01-MOPAK0000	0	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
786	CTDPF	\N	\N	192	786	GS02HYPM-WFP03-04-CTDPFL000	4600	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
787	CTDMO	\N	\N	195	787	GS03FLMA-RIS02-09-CTDMOG	250	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
788	FLORD	\N	\N	184	788	GS01SUMO-RII11-02-FLORDG103	40	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
789	CTDMO	\N	\N	198	789	GS03FLMB-RIS02-14-CTDMOH	1500	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
790	CTDMO	\N	\N	195	790	GS03FLMA-RIS02-06-CTDMOG	90	0101000020E6100000265305A3926A56C07CF2B0506B0A4BC0
\.


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_deployments_id_seq', 790, true);


--
-- Name: instrument_models_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('instrument_models_id_seq', 129, true);


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('instruments_id_seq', 790, true);


--
-- Name: manufacturers_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('manufacturers_id_seq', 24, true);


--
-- Name: organizations_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('organizations_id_seq', 1, true);


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('platform_deployments_id_seq', 203, true);


--
-- Name: platforms_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('platforms_id_seq', 203, true);


--
-- Data for Name: stream_parameters; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY stream_parameters (id, stream_parameter_name, short_name, long_name, standard_name, units, data_type) FROM stdin;
\.


--
-- Data for Name: stream_parameter_link; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY stream_parameter_link (id, stream_id, parameter_id) FROM stdin;
\.


--
-- Name: stream_parameter_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameter_link_id_seq', 1, false);


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('stream_parameters_id_seq', 1, false);


--
-- Name: streams_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('streams_id_seq', 1, false);


--
-- Data for Name: user_scopes; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY user_scopes (id, scope_name, scope_description) FROM stdin;
\.


--
-- Data for Name: user_scope_link; Type: TABLE DATA; Schema: ooiui_testing; Owner: oceanzus
--

COPY user_scope_link (id, user_id, scope_id) FROM stdin;
\.


--
-- Name: user_scope_link_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('user_scope_link_id_seq', 1, false);


--
-- Name: user_scopes_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('user_scopes_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: ooiui_testing; Owner: oceanzus
--

SELECT pg_catalog.setval('users_id_seq', 1, false);


SET search_path = public, pg_catalog;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: asa
--

COPY alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: rdsadmin
--

COPY spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


SET search_path = tiger, pg_catalog;

--
-- Data for Name: geocode_settings; Type: TABLE DATA; Schema: tiger; Owner: rds_superuser
--

COPY geocode_settings (name, setting, unit, category, short_desc) FROM stdin;
debug_geocode_address	false	boolean	debug	outputs debug information in notice log such as queries when geocode_addresss is called if true
debug_geocode_intersection	false	boolean	debug	outputs debug information in notice log such as queries when geocode_intersection is called if true
debug_normalize_address	false	boolean	debug	outputs debug information in notice log such as queries and intermediate expressions when normalize_address is called if true
debug_reverse_geocode	false	boolean	debug	if true, outputs debug information in notice log such as queries and intermediate expressions when reverse_geocode
reverse_geocode_numbered_roads	0	integer	rating	For state and county highways, 0 - no preference in name, 1 - prefer the numbered highway name, 2 - prefer local state/county name
use_pagc_address_parser	false	boolean	normalize	If set to true, will try to use the pagc_address normalizer instead of tiger built one
\.


--
-- Data for Name: pagc_gaz; Type: TABLE DATA; Schema: tiger; Owner: rds_superuser
--

COPY pagc_gaz (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_lex; Type: TABLE DATA; Schema: tiger; Owner: rds_superuser
--

COPY pagc_lex (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_rules; Type: TABLE DATA; Schema: tiger; Owner: rds_superuser
--

COPY pagc_rules (id, rule, is_custom) FROM stdin;
\.


SET search_path = topology, pg_catalog;

--
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: rds_superuser
--

COPY layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: rds_superuser
--

COPY topology (id, name, srid, "precision", hasz) FROM stdin;
1	my_new_topo	26986	0.5	f
\.


--
-- PostgreSQL database dump complete
--

