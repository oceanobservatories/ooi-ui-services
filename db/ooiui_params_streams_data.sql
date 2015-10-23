--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = ooiui, pg_catalog;

--
-- Data for Name: organizations; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY organizations (id, organization_name, organization_long_name, image_url) FROM stdin;
1	RPS ASA	\N	\N
\.


--
-- Data for Name: annotations; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY annotations (id, reference_designator, user_id, created_time, start_time, end_time, retired, stream_name, description, stream_parameter_name) FROM stdin;
\.


--
-- Name: annotations_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('annotations_id_seq', 1, false);


--
-- Data for Name: arrays; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY arrays (id, array_code, description, array_name, display_name, geo_location) FROM stdin;
\.


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('arrays_id_seq', 1, false);


--
-- Data for Name: assemblies; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY assemblies (id, assembly_name, description) FROM stdin;
\.


--
-- Name: assemblies_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('assemblies_id_seq', 1, false);


--
-- Data for Name: asset_types; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY asset_types (id, asset_type_name) FROM stdin;
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY assets (id, asset_type_id, organization_id, supplier_id, deployment_id, asset_name, model, current_lifecycle_state, part_number, firmware_version, geo_location) FROM stdin;
\.


--
-- Data for Name: files; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY files (id, user_id, file_name, file_system_path, file_size, file_permissions, file_type) FROM stdin;
\.


--
-- Data for Name: asset_file_link; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY asset_file_link (id, asset_id, file_id) FROM stdin;
\.


--
-- Name: asset_file_link_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('asset_file_link_id_seq', 1, false);


--
-- Name: asset_types_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('asset_types_id_seq', 1, false);


--
-- Name: assets_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('assets_id_seq', 1, false);


--
-- Data for Name: deployments; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY deployments (id, start_date, end_date, cruise_id) FROM stdin;
\.


--
-- Data for Name: manufacturers; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY manufacturers (id, manufacturer_name, phone_number, contact_name, web_address) FROM stdin;
\.


--
-- Data for Name: instrument_models; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY instrument_models (id, instrument_model_name, series_name, class_name, manufacturer_id) FROM stdin;
\.


--
-- Data for Name: instruments; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY instruments (id, instrument_name, description, location_description, instrument_series, serial_number, display_name, model_id, asset_id, depth_rating, manufacturer_id) FROM stdin;
\.


--
-- Data for Name: streams; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY streams (id, stream, delivery_method, data_type, content, stream_description, concatenated_name, instrument_id) FROM stdin;
1	Stream	Delivery Method	Data Type	Content	Stream Description	Concatenated Name	\N
2	adcp_ancillary_system_data	Streamed	Engineering	Data	Streamed Engineering Data	 Ancillary System Data    	\N
3	adcp_compass_calibration	Streamed	Calibration	Data	Streamed Calibration Data	 Compass Calibration     	\N
4	adcp_pd0_beam_parsed	Streamed	Science	Data Products	Streamed Science Data Products	TRDI Binary PD0 Data Format Beam Parsed	\N
5	adcp_pd0_earth_parsed	Streamed	Science	Data Products	Streamed Science Data Products	TRDI Binary PD0 Data Format Earth Parsed	\N
6	adcp_system_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 System Configuration     	\N
7	adcp_transmit_path	Streamed	Engineering	Data	Streamed Engineering Data	 Transmit Path     	\N
8	adcpa_m_glider_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series M Glider Instrument    	\N
9	adcpa_m_glider_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series M Glider Recovered    	\N
10	adcps_jln_instrument	Recovered	Science	Data Products	Recovered Science Data Products	 Series J L N Instrument     	\N
11	adcps_jln_sio_mule_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series J L N SIO Controller  Instrument   	\N
12	adcps_jln_stc_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series J L N STC Controller Instrument    	\N
13	adcps_jln_stc_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series J L N STC Controller Instrument Recovered   	\N
14	adcps_jln_stc_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series J L N STC Controller Metadata    	\N
15	adcps_jln_stc_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series J L N STC Controller Metadata Recovered   	\N
16	adcpt_acfgm_pd0_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	Series A C F G M TRDI Binary PD0 Data Format Data Concentrator Logger Instrument	\N
17	adcpt_acfgm_pd0_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	Series A C F G M TRDI Binary PD0 Data Format Data Concentrator Logger Instrument Recovered	\N
18	adcpt_acfgm_pd8_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	Series A C F G M PD8 Data Format Data Concentrator Logger Instrument	\N
19	adcpt_acfgm_pd8_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	Series A C F G M PD8 Data Format Data Concentrator Logger Instrument Recovered	\N
20	adcpt_m_instrument_dspec_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series M Instrument  Recovered   	\N
21	adcpt_m_instrument_fcoeff_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series M Instrument  Recovered   	\N
22	adcpt_m_instrument_log9_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series M Instrument  Recovered   	\N
23	adcpt_m_wvs_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series M  Recovered    	\N
24	botpt_heat_sample	Streamed	Science	HEAT Sensor Data Products	Streamed Science HEAT Sensor Data Products	 Heat Sample     	\N
25	botpt_iris_sample	Streamed	Science	IRIS Sensor Data Products	Streamed Science IRIS Sensor Data Products	 Iris Sample     	\N
26	botpt_lily_leveling	Streamed	Calibration	Data	Streamed Calibration Data	  Leveling     	\N
27	botpt_lily_sample	Streamed	Science	LILY Sensor Data Products	Streamed Science LILY Sensor Data Products	  Sample     	\N
28	botpt_nano_sample	Streamed	Science	NANO Sensor Data Products	Streamed Science NANO Sensor Data Products	  Sample     	\N
29	botpt_status	Streamed	Engineering	Data	Streamed Engineering Data	 Status      	\N
30	calibration_status	Streamed	Engineering	Data	Streamed Engineering Data	 Status      	\N
31	camds_disk_status	Streamed	Engineering	Data	Streamed Engineering Data	 Disk Status     	\N
32	camds_health_status	Streamed	Engineering	Data	Streamed Engineering Data	 Health Status     	\N
33	camds_image_metadata	Streamed	Engineering	Data	Streamed Engineering Data	 Image Metadata     	\N
34	camds_video	Streamed	Science	Data Products	Streamed Science Data Products	 Video      	\N
35	cg_cpm_eng_cpm	Telemetered	Engineering	Data	Telemetered Engineering Data	  Engineering     	\N
36	cg_cpm_eng_cpm_recovered	Recovered	Engineering	Data	Recovered Engineering Data	  Engineering  Recovered   	\N
37	cg_dcl_eng_dcl_cpu_uptime	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger    	\N
38	cg_dcl_eng_dcl_cpu_uptime_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger   Recovered 	\N
39	cg_dcl_eng_dcl_dlog_aarm	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger    	\N
40	cg_dcl_eng_dcl_dlog_aarm_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger   Recovered 	\N
41	cg_dcl_eng_dcl_dlog_mgr	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger    	\N
42	cg_dcl_eng_dcl_dlog_mgr_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger   Recovered 	\N
43	cg_dcl_eng_dcl_dlog_status	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger  Status  	\N
44	cg_dcl_eng_dcl_dlog_status_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger  Status Recovered 	\N
45	cg_dcl_eng_dcl_error	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger Error   	\N
46	cg_dcl_eng_dcl_error_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger Error Recovered  	\N
47	cg_dcl_eng_dcl_gps	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger    	\N
48	cg_dcl_eng_dcl_gps_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger  Recovered  	\N
49	cg_dcl_eng_dcl_msg_counts	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger  Counts  	\N
50	cg_dcl_eng_dcl_msg_counts_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger  Counts Recovered 	\N
51	cg_dcl_eng_dcl_pps	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger    	\N
52	cg_dcl_eng_dcl_pps_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger  Recovered  	\N
53	cg_dcl_eng_dcl_status	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger Status   	\N
54	cg_dcl_eng_dcl_status_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger Status Recovered  	\N
55	cg_dcl_eng_dcl_superv	Telemetered	Engineering	Data	Telemetered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger    	\N
56	cg_dcl_eng_dcl_superv_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Data Concentrator Logger Engineering Data Concentrator Logger  Recovered  	\N
57	cg_stc_eng_stc	Telemetered	Engineering	Data	Telemetered Engineering Data	  Engineering STC Controller    	\N
58	cg_stc_eng_stc_recovered	Recovered	Engineering	Data	Recovered Engineering Data	  Engineering STC Controller Recovered   	\N
59	cspp_eng_cspp_dbg_pdbg_batt_eng	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler    Engineering 	\N
60	cspp_eng_cspp_dbg_pdbg_batt_eng_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler    Engineering Recovered	\N
61	cspp_eng_cspp_dbg_pdbg_gps_eng	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler    Engineering 	\N
62	cspp_eng_cspp_dbg_pdbg_gps_eng_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler    Engineering Recovered	\N
63	cspp_eng_cspp_dbg_pdbg_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata  	\N
64	cspp_eng_cspp_dbg_pdbg_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata Recovered 	\N
65	cspp_eng_cspp_wc_hmr_eng	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Engineering  	\N
66	cspp_eng_cspp_wc_hmr_eng_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Engineering Recovered 	\N
67	cspp_eng_cspp_wc_hmr_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata  	\N
68	cspp_eng_cspp_wc_hmr_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata Recovered 	\N
69	cspp_eng_cspp_wc_sbe_eng	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Engineering  	\N
70	cspp_eng_cspp_wc_sbe_eng_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Engineering Recovered 	\N
71	cspp_eng_cspp_wc_sbe_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata  	\N
72	cspp_eng_cspp_wc_sbe_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata Recovered 	\N
73	cspp_eng_cspp_wc_wm_eng	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Engineering  	\N
74	cspp_eng_cspp_wc_wm_eng_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Engineering Recovered 	\N
75	cspp_eng_cspp_wc_wm_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata  	\N
76	cspp_eng_cspp_wc_wm_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Coastal Surface Piercing Profiler Engineering Coastal Surface Piercing Profiler   Metadata Recovered 	\N
77	ctdbp_cdef_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series C D E F Data Concentrator Logger Instrument    	\N
78	ctdbp_cdef_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series C D E F Data Concentrator Logger Instrument Recovered   	\N
79	ctdbp_cdef_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series C D E F Instrument Recovered    	\N
80	ctdbp_no_calibration_coefficients	Streamed	Calibration	Data	Streamed Calibration Data	  Calibration Coefficients    	\N
81	ctdbp_no_configuration	Streamed	Engineering	Data	Streamed Engineering Data	  Configuration     	\N
82	ctdbp_no_hardware	Streamed	Engineering	Data	Streamed Engineering Data	  Hardware     	\N
83	ctdbp_no_optode_settings	Streamed	Engineering	Data	Streamed Engineering Data	  Optode Settings    	\N
84	ctdbp_no_sample	Streamed	Science	Data Products	Streamed Science Data Products	  Sample     	\N
85	ctdbp_no_status	Streamed	Engineering	Data	Streamed Engineering Data	  Status     	\N
86	ctdbp_p_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series P Data Concentrator Logger Instrument    	\N
87	ctdbp_p_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series P Data Concentrator Logger Instrument Recovered   	\N
88	ctdgv_m_glider_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series M Glider Instrument    	\N
89	ctdgv_m_glider_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series M Glider Instrument Recovered   	\N
90	ctdmo_ghqr_imodem_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series G H Q R  Instrument    	\N
91	ctdmo_ghqr_imodem_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series G H Q R  Instrument Recovered   	\N
92	ctdmo_ghqr_imodem_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series G H Q R  Metadata    	\N
93	ctdmo_ghqr_imodem_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series G H Q R  Metadata Recovered   	\N
94	ctdmo_ghqr_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series G H Q R Instrument Recovered    	\N
95	ctdmo_ghqr_offset_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series G H Q R Offset Recovered    	\N
96	ctdmo_ghqr_sio_mule_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series G H Q R SIO Controller  Instrument   	\N
97	ctdmo_ghqr_sio_offset	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series G H Q R SIO Controller Offset    	\N
98	ctdpf_ckl_wfp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series K L Wire Following Profiler Instrument    	\N
99	ctdpf_ckl_wfp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series K L Wire Following Profiler Instrument Recovered   	\N
100	ctdpf_ckl_wfp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series K L Wire Following Profiler Metadata    	\N
101	ctdpf_ckl_wfp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series K L Wire Following Profiler Metadata Recovered   	\N
102	ctdpf_ckl_wfp_sio_mule_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series K L Wire Following Profiler SIO Controller  Metadata  	\N
103	ctdpf_j_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument    	\N
104	ctdpf_j_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument Recovered   	\N
105	ctdpf_j_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata    	\N
106	ctdpf_j_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata Recovered   	\N
107	ctdpf_optode_calibration_coefficients	Streamed	Calibration	Data	Streamed Calibration Data	 Optode Calibration Coefficients    	\N
108	ctdpf_optode_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 Optode Configuration     	\N
109	ctdpf_optode_hardware	Streamed	Engineering	Data	Streamed Engineering Data	 Optode Hardware     	\N
110	ctdpf_optode_sample	Streamed	Science	Data Products	Streamed Science Data Products	 Optode Sample     	\N
111	ctdpf_optode_settings	Streamed	Engineering	Data	Streamed Engineering Data	 Optode Settings     	\N
112	ctdpf_optode_status	Streamed	Engineering	Data	Streamed Engineering Data	 Optode Status     	\N
113	ctdpf_sbe43_calibration_coefficients	Streamed	Calibration	Data	Streamed Calibration Data	  Calibration Coefficients    	\N
114	ctdpf_sbe43_configuration	Streamed	Engineering	Data	Streamed Engineering Data	  Configuration     	\N
115	ctdpf_sbe43_hardware	Streamed	Engineering	Data	Streamed Engineering Data	  Hardware     	\N
116	ctdpf_sbe43_sample	Streamed	Science	Data Products	Streamed Science Data Products	  Sample     	\N
117	ctdpf_sbe43_status	Streamed	Engineering	Data	Streamed Engineering Data	  Status     	\N
118	dofst_k_wfp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series K Wire Following Profiler Instrument    	\N
119	dofst_k_wfp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series K Wire Following Profiler Instrument Recovered   	\N
120	dofst_k_wfp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series K Wire Following Profiler Metadata    	\N
121	dofst_k_wfp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series K Wire Following Profiler Metadata Recovered   	\N
122	dosta_abcdjm_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C D J M Coastal Surface Piercing Profiler Instrument    	\N
123	dosta_abcdjm_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B C D J M Coastal Surface Piercing Profiler Instrument Recovered   	\N
124	dosta_abcdjm_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C D J M Coastal Surface Piercing Profiler Metadata    	\N
125	dosta_abcdjm_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C D J M Coastal Surface Piercing Profiler Metadata Recovered   	\N
126	dosta_abcdjm_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C D J M Data Concentrator Logger Instrument    	\N
127	dosta_abcdjm_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B C D J M Data Concentrator Logger Instrument Recovered   	\N
128	dosta_abcdjm_glider_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C D J M Glider Instrument    	\N
129	dosta_abcdjm_glider_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B C D J M Glider Recovered    	\N
130	dosta_abcdjm_sio_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C D J M SIO Controller Instrument    	\N
131	dosta_abcdjm_sio_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C D J M SIO Controller Metadata    	\N
132	dosta_abcdjm_sio_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C D J M SIO Controller Metadata Recovered   	\N
133	dosta_ln_wfp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series L N Wire Following Profiler Instrument    	\N
134	dosta_ln_wfp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series L N Wire Following Profiler Instrument Recovered   	\N
135	dpc_acm_instrument	Streamed	Science	Data Products	Streamed Science Data Products	  Instrument     	\N
136	dpc_acs_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	  Instrument Recovered    	\N
137	dpc_ctd_instrument	Streamed	Science	Data Products	Streamed Science Data Products	  Instrument     	\N
138	dpc_flcdrtd_instrument	Streamed	Science	Data Products	Streamed Science Data Products	  Instrument     	\N
139	dpc_flnturtd_instrument	Streamed	Science	Data Products	Streamed Science Data Products	  Instrument     	\N
140	dpc_mmp_instrument	Streamed	Engineering	Data	Streamed Engineering Data	  Instrument     	\N
141	dpc_optode_instrument	Streamed	Science	Data Products	Streamed Science Data Products	 Optode Instrument     	\N
142	echo_sounding	Streamed	Science	Data Products	Streamed Science Data Products	 Sounding      	\N
143	fdchp_a_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A Data Concentrator Logger Instrument    	\N
144	fdchp_a_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A Data Concentrator Logger Instrument Recovered   	\N
145	fdchp_a_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A Instrument Recovered    	\N
146	flord_l_wfp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series L Wire Following Profiler Instrument    	\N
147	flord_l_wfp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series L Wire Following Profiler Instrument Recovered   	\N
148	flord_m_glider_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series M Glider Instrument    	\N
149	flord_m_glider_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series M Glider Instrument Recovered   	\N
150	flort_d_data_record	Streamed	Science	Data Products	Streamed Science Data Products	  Data Record    	\N
151	flort_d_status	Streamed	Calibration	Data	Streamed Calibration Data	  Status     	\N
152	flort_dj_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series D J Coastal Surface Piercing Profiler Instrument    	\N
153	flort_dj_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series D J Coastal Surface Piercing Profiler Instrument Recovered   	\N
154	flort_dj_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series D J Coastal Surface Piercing Profiler Metadata    	\N
155	flort_dj_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series D J Coastal Surface Piercing Profiler Metadata Recovered   	\N
156	flort_dj_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series D J Data Concentrator Logger Instrument    	\N
157	flort_dj_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series D J Data Concentrator Logger Instrument Recovered   	\N
158	flort_dj_sio_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series D J SIO Controller Instrument    	\N
159	flort_dj_sio_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series D J SIO Controller Instrument Recovered   	\N
160	flort_kn_stc_imodem_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series K STC Controller  Instrument   	\N
161	flort_kn_stc_imodem_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series K STC Controller  Instrument Recovered  	\N
162	flort_m_glider_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series M Glider Instrument    	\N
163	flort_m_glider_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series M Glider Recovered    	\N
164	fuelcell_eng_dcl_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Engineering Data Concentrator Logger Recovered    	\N
165	fuelcell_eng_dcl_telemetered	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering Data Concentrator Logger Telemetered    	\N
166	glider_eng_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering Metadata     	\N
167	glider_eng_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Engineering Metadata Recovered    	\N
168	glider_eng_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Engineering Recovered     	\N
169	glider_eng_sci_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Engineering Science Recovered    	\N
170	glider_eng_sci_telemetered	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering Science Telemetered    	\N
171	glider_eng_telemetered	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering Telemetered     	\N
172	horizontal_electric_field	Streamed	Science	Data Products	Streamed Science Data Products	 Electric Field     	\N
173	hpies_status	Streamed	Engineering	Data	Streamed Engineering Data	 Status      	\N
174	hyd_o_dcl_instrument	Telemetered	Engineering	Data	Telemetered Engineering Data	Hydrogen Sensor  Data Concentrator Logger Instrument    	\N
175	hyd_o_dcl_instrument_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Hydrogen Sensor  Data Concentrator Logger Instrument Recovered   	\N
176	ies_status	Streamed	Engineering	Data	Streamed Engineering Data	 Status      	\N
177	massp_mcu_status	Streamed	Engineering	Data	Streamed Engineering Data	  Status     	\N
178	massp_rga_sample	Streamed	Science	Data Products	Streamed Science Data Products	  Sample     	\N
179	massp_rga_status	Streamed	Engineering	Data	Streamed Engineering Data	  Status     	\N
180	massp_turbo_status	Streamed	Engineering	Data	Streamed Engineering Data	 Turbo Status     	\N
181	metbk_a_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A Data Concentrator Logger Instrument    	\N
182	metbk_a_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A Data Concentrator Logger Instrument Recovered   	\N
183	metbk_hourly	Telemetered	Science	Hourly Averaged Data Products	Telemetered Science Hourly Averaged Data Products	 Hourly      	\N
184	mopak_o_dcl_accel	Telemetered	Engineering	Data	Telemetered Engineering Data	  Data Concentrator Logger Acceleration    	\N
185	mopak_o_dcl_accel_recovered	Recovered	Engineering	Data	Recovered Engineering Data	  Data Concentrator Logger Acceleration Recovered   	\N
186	mopak_o_dcl_rate	Telemetered	Engineering	Data	Telemetered Engineering Data	  Data Concentrator Logger Rate    	\N
187	mopak_o_dcl_rate_recovered	Recovered	Engineering	Data	Recovered Engineering Data	  Data Concentrator Logger Rate Recovered   	\N
188	motor_current	Streamed	Engineering	Data	Streamed Engineering Data	 Current      	\N
189	nutnr_a_sample	Streamed	Science	Data Products	Streamed Science Data Products	  Sample     	\N
190	nutnr_a_status	Streamed	Engineering	Data	Streamed Engineering Data	  Status     	\N
191	nutnr_a_test	Streamed	Engineering	Data	Streamed Engineering Data	  Test     	\N
192	nutnr_b_dark_instrument_recovered	Recovered	Calibration	Data	Recovered Calibration Data	 Series B Dark Instrument Recovered   	\N
193	nutnr_b_dcl_conc_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series B Data Concentrator Logger Concentration Instrument   	\N
194	nutnr_b_dcl_conc_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series B Data Concentrator Logger Concentration Instrument Recovered  	\N
195	nutnr_b_dcl_conc_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series B Data Concentrator Logger Concentration Metadata   	\N
196	nutnr_b_dcl_conc_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series B Data Concentrator Logger Concentration Metadata Recovered  	\N
197	nutnr_b_dcl_dark_conc_instrument	Telemetered	Calibration	Data	Telemetered Calibration Data	 Series B Data Concentrator Logger Dark Concentration Instrument  	\N
198	nutnr_b_dcl_dark_conc_instrument_recovered	Recovered	Calibration	Data	Recovered Calibration Data	 Series B Data Concentrator Logger Dark Concentration Instrument Recovered 	\N
199	nutnr_b_dcl_dark_full_instrument	Telemetered	Calibration	Data	Telemetered Calibration Data	 Series B Data Concentrator Logger Dark Full Instrument  	\N
200	nutnr_b_dcl_dark_full_instrument_recovered	Recovered	Calibration	Data	Recovered Calibration Data	 Series B Data Concentrator Logger Dark Full Instrument Recovered 	\N
201	nutnr_b_dcl_full_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series B Data Concentrator Logger Full Instrument   	\N
202	nutnr_b_dcl_full_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series B Data Concentrator Logger Full Instrument Recovered  	\N
203	nutnr_b_dcl_full_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series B Data Concentrator Logger Full Metadata   	\N
204	nutnr_b_dcl_full_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series B Data Concentrator Logger Full Metadata Recovered  	\N
205	nutnr_b_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series B Instrument Recovered    	\N
206	nutnr_b_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series B Metadata Recovered    	\N
207	nutnr_j_cspp_dark_instrument	Telemetered	Calibration	Data	Telemetered Calibration Data	 Series J Coastal Surface Piercing Profiler Dark Instrument   	\N
208	nutnr_j_cspp_dark_instrument_recovered	Recovered	Calibration	Data	Recovered Calibration Data	 Series J Coastal Surface Piercing Profiler Dark Instrument Recovered  	\N
209	nutnr_j_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument    	\N
210	nutnr_j_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument Recovered   	\N
211	nutnr_j_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata    	\N
212	nutnr_j_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata Recovered   	\N
213	nutnr_m_dark_instrument_recovered	Recovered	Calibration	Data	Recovered Calibration Data	  Dark Instrument Recovered   	\N
214	nutnr_m_glider_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	  Glider Instrument    	\N
215	nutnr_m_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	  Instrument Recovered    	\N
216	optaa_dj_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series D J Coastal Surface Piercing Profiler Instrument    	\N
217	optaa_dj_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series D J Coastal Surface Piercing Profiler Instrument Recovered   	\N
218	optaa_dj_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series D J Coastal Surface Piercing Profiler Metadata    	\N
219	optaa_dj_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series D J Coastal Surface Piercing Profiler Metadata Recovered   	\N
220	optaa_dj_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series D J Data Concentrator Logger Instrument    	\N
221	optaa_dj_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series D J Data Concentrator Logger Instrument Recovered   	\N
222	optaa_dj_dcl_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series D J Data Concentrator Logger Metadata    	\N
223	optaa_dj_dcl_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series D J Data Concentrator Logger Metadata Recovered   	\N
224	optaa_sample	Streamed	Science	Data Products	Streamed Science Data Products	 Sample      	\N
225	optaa_status	Streamed	Engineering	Data	Streamed Engineering Data	 Status      	\N
226	parad_j_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument    	\N
227	parad_j_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument Recovered   	\N
228	parad_j_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata    	\N
229	parad_j_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata Recovered   	\N
230	parad_k__stc_imodem_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series K  STC Controller  Instrument  	\N
231	parad_k__stc_imodem_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series K  STC Controller  Instrument Recovered 	\N
232	parad_m_glider_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series M Glider Instrument    	\N
233	parad_m_glider_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series M Glider Recovered    	\N
234	parad_sa_config	Streamed	Engineering	Data	Streamed Engineering Data	       	\N
235	parad_sa_sample	Streamed	Science	Data Products	Streamed Science Data Products	  Sample     	\N
236	pco2a_a_dcl_instrument_air	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A Data Concentrator Logger Instrument Air   	\N
237	pco2a_a_dcl_instrument_air_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A Data Concentrator Logger Instrument Air Recovered  	\N
238	pco2a_a_dcl_instrument_water	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A Data Concentrator Logger Instrument Water   	\N
239	pco2a_a_dcl_instrument_water_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A Data Concentrator Logger Instrument Water Recovered  	\N
240	pco2w_a_battery_voltage	Streamed	Engineering	Data	Streamed Engineering Data	 Series A Battery Voltage    	\N
241	pco2w_a_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 Series A Configuration     	\N
242	pco2w_a_regular_status	Streamed	Engineering	Data	Streamed Engineering Data	 Series A Regular Status    	\N
243	pco2w_a_sami_data_record	Streamed	Science	Data Products	Streamed Science Data Products	 Series A  Data Record   	\N
244	pco2w_a_sami_data_record_cal	Streamed	Calibration	Data	Streamed Calibration Data	 Series A  Data Record   	\N
245	pco2w_a_thermistor_voltage	Streamed	Engineering	Data	Streamed Engineering Data	 Series A Thermistor Voltage    	\N
246	pco2w_abc_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C Data Concentrator Logger Instrument    	\N
247	pco2w_abc_dcl_instrument_blank	Telemetered	Calibration	Data	Telemetered Calibration Data	 Series A B C Data Concentrator Logger Instrument    	\N
248	pco2w_abc_dcl_instrument_blank_recovered	Recovered	Calibration	Data	Recovered Calibration Data	 Series A B C Data Concentrator Logger Instrument  Recovered  	\N
249	pco2w_abc_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B C Data Concentrator Logger Instrument Recovered   	\N
250	pco2w_abc_dcl_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C Data Concentrator Logger Metadata    	\N
251	pco2w_abc_dcl_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C Data Concentrator Logger Metadata Recovered   	\N
252	pco2w_abc_dcl_power	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C Data Concentrator Logger Power    	\N
253	pco2w_abc_dcl_power_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C Data Concentrator Logger Power Recovered   	\N
254	pco2w_abc_imodem_control	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C  Control    	\N
255	pco2w_abc_imodem_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C  Instrument    	\N
256	pco2w_abc_imodem_instrument_blank	Telemetered	Calibration	Data	Telemetered Calibration Data	 Series A B C  Instrument    	\N
257	pco2w_abc_imodem_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C  Metadata    	\N
258	pco2w_abc_imodem_power	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C  Power    	\N
259	pco2w_abc_instrument	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B C Instrument     	\N
260	pco2w_abc_instrument_blank	Recovered	Calibration	Data	Recovered Calibration Data	 Series A B C Instrument Blank    	\N
261	pco2w_abc_metadata	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C Metadata     	\N
262	pco2w_abc_power	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C Power     	\N
263	pco2w_b_battery_voltage	Streamed	Engineering	Data	Streamed Engineering Data	  Battery Voltage    	\N
264	pco2w_b_configuration	Streamed	Engineering	Data	Streamed Engineering Data	  Configuration     	\N
265	pco2w_b_dev1_data_record	Streamed	Engineering	Data	Streamed Engineering Data	   Data Record   	\N
266	pco2w_b_regular_status	Streamed	Engineering	Data	Streamed Engineering Data	  Regular Status    	\N
267	pco2w_b_sami_data_record	Streamed	Science	Data Products	Streamed Science Data Products	   Data Record   	\N
268	pco2w_b_sami_data_record_cal	Streamed	Calibration	Data	Streamed Calibration Data	   Data Record   	\N
269	pco2w_b_thermistor_voltage	Streamed	Engineering	Data	Streamed Engineering Data	  Thermistor Voltage    	\N
270	phsen_abcdef_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C D E F Data Concentrator Logger Instrument    	\N
271	phsen_abcdef_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B C D E F Data Concentrator Logger Instrument Recovered   	\N
272	phsen_abcdef_dcl_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C D E F Data Concentrator Logger Metadata    	\N
273	phsen_abcdef_dcl_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C D E F Data Concentrator Logger Metadata Recovered   	\N
274	phsen_abcdef_imodem_control	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C D E F  Control    	\N
275	phsen_abcdef_imodem_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C D E F  Instrument    	\N
276	phsen_abcdef_imodem_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C D E F  Metadata    	\N
277	phsen_abcdef_instrument	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B C D E F Instrument     	\N
278	phsen_abcdef_metadata	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B C D E F Metadata     	\N
279	phsen_abcdef_sio_mule_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B C D E F SIO Controller  Instrument   	\N
280	phsen_abcdef_sio_mule_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B C D E F SIO Controller  Metadata   	\N
281	phsen_battery_voltage	Streamed	Engineering	Data	Streamed Engineering Data	 Battery Voltage     	\N
282	phsen_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 Configuration      	\N
283	phsen_data_record	Streamed	Science	Data Products	Streamed Science Data Products	 Data Record     	\N
284	phsen_regular_status	Streamed	Engineering	Data	Streamed Engineering Data	 Regular Status     	\N
285	phsen_thermistor_voltage	Streamed	Engineering	Data	Streamed Engineering Data	 Thermistor Voltage     	\N
286	presf_abc_dcl_tide_measurement	Telemetered	Science	Tide Measurement Data Products	Telemetered Science Tide Measurement Data Products	 Series A B C Data Concentrator Logger Tide Measurement   	\N
287	presf_abc_dcl_tide_measurement_recovered	Recovered	Science	Tide Measurement Data Products	Recovered Science Tide Measurement Data Products	 Series A B C Data Concentrator Logger Tide Measurement Recovered  	\N
288	presf_abc_dcl_wave_burst	Telemetered	Science	Wave Burst Data Products	Telemetered Science Wave Burst Data Products	 Series A B C Data Concentrator Logger Wave Burst   	\N
289	presf_abc_dcl_wave_burst_recovered	Recovered	Science	Wave Burst Data Products	Recovered Science Wave Burst Data Products	 Series A B C Data Concentrator Logger Wave Burst Recovered  	\N
290	prest_configuration_data	Streamed	Engineering	Data	Streamed Engineering Data	 Configuration Data     	\N
291	prest_device_status	Streamed	Engineering	Data	Streamed Engineering Data	 Device Status     	\N
292	prest_event_counter	Streamed	Engineering	Data	Streamed Engineering Data	 Event Counter     	\N
293	prest_hardware_data	Streamed	Engineering	Data	Streamed Engineering Data	 Hardware Data     	\N
294	prest_real_time	Streamed	Science	Data Products	Streamed Science Data Products	 Real Time     	\N
295	prest_reference_oscillator	Streamed	Engineering	Data	Streamed Engineering Data	 Reference Oscillator     	\N
296	rte_o_dcl_instrument	Telemetered	Engineering	Data	Telemetered Engineering Data	Radar Target Enhancer  Data Concentrator Logger Instrument    	\N
297	rte_o_dcl_instrument_recovered	Recovered	Engineering	Data	Recovered Engineering Data	Radar Target Enhancer  Data Concentrator Logger Instrument Recovered   	\N
298	sio_eng_control_status	Telemetered	Engineering	Data	Telemetered Engineering Data	SIO Controller Engineering Control Status    	\N
299	sio_eng_control_status_recovered	Recovered	Engineering	Data	Recovered Engineering Data	SIO Controller Engineering Control Status Recovered   	\N
300	spkir_a_configuration_record	Streamed	Engineering	Data	Streamed Engineering Data	  Configuration Record    	\N
301	spkir_abj_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B J Coastal Surface Piercing Profiler Instrument    	\N
302	spkir_abj_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B J Coastal Surface Piercing Profiler Instrument Recovered   	\N
303	spkir_abj_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B J Coastal Surface Piercing Profiler Metadata    	\N
304	spkir_abj_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B J Coastal Surface Piercing Profiler Metadata Recovered   	\N
305	spkir_abj_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B J Data Concentrator Logger Instrument    	\N
306	spkir_abj_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B J Data Concentrator Logger Instrument Recovered   	\N
307	spkir_data_record	Streamed	Science	Data Products	Streamed Science Data Products	 Data Record     	\N
308	stm_timestamp	Streamed	Engineering	Data	Streamed Engineering Data	 Timestamp      	\N
309	thsph_sample	Streamed	Science	Data Products	Streamed Science Data Products	 Sample      	\N
310	tmpsf_engineering	Streamed	Engineering	Data	Streamed Engineering Data	 Engineering      	\N
311	tmpsf_sample	Streamed	Science	Data Products	Streamed Science Data Products	 Sample      	\N
312	trhph_sample	Streamed	Science	Data Products	Streamed Science Data Products	 Sample      	\N
313	trhph_status	Streamed	Engineering	Data	Streamed Engineering Data	 Status      	\N
314	vadcp_4beam_system_configuration	Streamed	Engineering	Data	Streamed Engineering Data	  System Configuration    	\N
315	vadcp_5thbeam_compass_calibration	Streamed	Calibration	Data	Streamed Calibration Data	5th Beam Compass Calibration	\N
316	vadcp_5thbeam_pd0_beam_parsed	Streamed	Science	Data Products	Streamed Science Data Products	5th Beam TRDI Binary PD0 Data Format Beam Parsed	\N
317	vadcp_5thbeam_pd0_earth_parsed	Streamed	Science	Data Products	Streamed Science Data Products	5th Beam TRDI Binary PD0 Data Format Earth Parsed	\N
318	vadcp_5thbeam_system_configuration	Streamed	Engineering	Data	Streamed Engineering Data	5th Beam System Configuration	\N
319	vadcp_ancillary_system_data	Streamed	Engineering	Data	Streamed Engineering Data	 Ancillary System Data    	\N
320	vadcp_pd0_beam_parsed	Streamed	Science	Data Products	Streamed Science Data Products	TRDI Binary PD0 Data Format Beam Parsed	\N
321	vadcp_transmit_path	Streamed	Engineering	Data	Streamed Engineering Data	 Transmit Path     	\N
322	vel3d_b_engineering	Streamed	Engineering	Data	Streamed Engineering Data	  Engineering     	\N
323	vel3d_b_sample	Streamed	Science	Data Products	Streamed Science Data Products	  Sample     	\N
324	vel3d_cd_battery_voltage	Streamed	Engineering	Data	Streamed Engineering Data	 Series C D Battery Voltage    	\N
325	vel3d_cd_data_header	Streamed	Engineering	Data	Streamed Engineering Data	 Series C D Data Header    	\N
326	vel3d_cd_dcl_data_header	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series C D Data Concentrator Logger Data Header   	\N
327	vel3d_cd_dcl_data_header_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series C D Data Concentrator Logger Data Header Recovered  	\N
328	vel3d_cd_dcl_hardware_configuration	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series C D Data Concentrator Logger Hardware Configuration   	\N
329	vel3d_cd_dcl_hardware_configuration_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series C D Data Concentrator Logger Hardware Configuration Recovered  	\N
330	vel3d_cd_dcl_head_configuration	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series C D Data Concentrator Logger Head Configuration   	\N
331	vel3d_cd_dcl_head_configuration_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series C D Data Concentrator Logger Head Configuration Recovered  	\N
332	vel3d_cd_dcl_system_data	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series C D Data Concentrator Logger System Data   	\N
333	vel3d_cd_dcl_system_data_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series C D Data Concentrator Logger System Data Recovered  	\N
334	vel3d_cd_dcl_user_configuration	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series C D Data Concentrator Logger User Configuration   	\N
335	vel3d_cd_dcl_user_configuration_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series C D Data Concentrator Logger User Configuration Recovered  	\N
336	vel3d_cd_dcl_velocity_data	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series C D Data Concentrator Logger Velocity Data   	\N
337	vel3d_cd_dcl_velocity_data_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series C D Data Concentrator Logger Velocity Data Recovered  	\N
338	vel3d_cd_hardware_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 Series C D Hardware Configuration    	\N
339	vel3d_cd_head_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 Series C D Head Configuration    	\N
340	vel3d_cd_identification_string	Streamed	Engineering	Data	Streamed Engineering Data	 Series C D Identification String    	\N
341	vel3d_cd_system_data	Streamed	Engineering	Data	Streamed Engineering Data	 Series C D System Data    	\N
342	vel3d_cd_user_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 Series C D User Configuration    	\N
343	vel3d_cd_velocity_data	Streamed	Science	Data Products	Streamed Science Data Products	 Series C D Velocity Data    	\N
344	vel3d_clock_data	Streamed	Engineering	Data	Streamed Engineering Data	 Clock Data     	\N
345	vel3d_k_wfp_instrument	Recovered	Science	Data Products	Recovered Science Data Products	 Series K Wire Following Profiler Instrument    	\N
346	vel3d_k_wfp_metadata	Recovered	Engineering	Data	Recovered Engineering Data	 Series K Wire Following Profiler Metadata    	\N
347	vel3d_k_wfp_stc_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series K Wire Following Profiler STC Controller Instrument   	\N
348	vel3d_k_wfp_stc_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series K Wire Following Profiler STC Controller Metadata   	\N
349	vel3d_k_wfp_string	Recovered	Engineering	Data	Recovered Engineering Data	 Series K Wire Following Profiler String    	\N
350	vel3d_l_wfp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series L Wire Following Profiler Instrument    	\N
351	vel3d_l_wfp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series L Wire Following Profiler Instrument Recovered   	\N
352	vel3d_l_wfp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series L Wire Following Profiler Metadata Recovered   	\N
353	vel3d_l_wfp_sio_mule_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series L Wire Following Profiler SIO Controller  Metadata  	\N
354	velpt_ab_dcl_diagnostics	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B Data Concentrator Logger Diagnostics    	\N
355	velpt_ab_dcl_diagnostics_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series A B Data Concentrator Logger Diagnostics Metadata   	\N
356	velpt_ab_dcl_diagnostics_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B Data Concentrator Logger Diagnostics Metadata Recovered  	\N
357	velpt_ab_dcl_diagnostics_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B Data Concentrator Logger Diagnostics Recovered   	\N
358	velpt_ab_dcl_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series A B Data Concentrator Logger Instrument    	\N
359	velpt_ab_dcl_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B Data Concentrator Logger Instrument Recovered   	\N
360	velpt_ab_diagnostics_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B Diagnostics Metadata Recovered   	\N
361	velpt_ab_diagnostics_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B Diagnostics Recovered    	\N
362	velpt_ab_instrument_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series A B Instrument Metadata Recovered   	\N
363	velpt_ab_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series A B Instrument Recovered    	\N
364	velpt_battery_voltage	Streamed	Engineering	Data	Streamed Engineering Data	 Battery Voltage     	\N
365	velpt_clock_data	Streamed	Engineering	Data	Streamed Engineering Data	 Clock Data     	\N
366	velpt_hardware_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 hardware Configuration     	\N
367	velpt_head_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 Head Configuration     	\N
368	velpt_identification_string	Streamed	Engineering	Data	Streamed Engineering Data	 Identification String     	\N
369	velpt_j_cspp_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument    	\N
370	velpt_j_cspp_instrument_recovered	Recovered	Science	Data Products	Recovered Science Data Products	 Series J Coastal Surface Piercing Profiler Instrument Recovered   	\N
371	velpt_j_cspp_metadata	Telemetered	Engineering	Data	Telemetered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata    	\N
372	velpt_j_cspp_metadata_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Series J Coastal Surface Piercing Profiler Metadata Recovered   	\N
373	velpt_user_configuration	Streamed	Engineering	Data	Streamed Engineering Data	 User Configuration     	\N
374	velpt_velocity_data	Streamed	Science	Data Products	Streamed Science Data Products	 Velocity Data     	\N
375	wavss_a_dcl_fourier	Telemetered	Science	Fourier Data Products	Telemetered Science Fourier Data Products	 Series A Data Concentrator Logger Fourier    	\N
376	wavss_a_dcl_fourier_recovered	Recovered	Science	Fourier Data Products	Recovered Science Fourier Data Products	 Series A Data Concentrator Logger Fourier Recovered   	\N
377	wavss_a_dcl_mean_directional	Telemetered	Science	Mean Directional Data Products	Telemetered Science Mean Directional Data Products	 Series A Data Concentrator Logger Mean Directional   	\N
378	wavss_a_dcl_mean_directional_recovered	Recovered	Science	Mean Directional Data Products	Recovered Science Mean Directional Data Products	 Series A Data Concentrator Logger Mean Directional Recovered  	\N
379	wavss_a_dcl_motion	Telemetered	Science	Motion Data Products	Telemetered Science Motion Data Products	 Series A Data Concentrator Logger Motion    	\N
380	wavss_a_dcl_motion_recovered	Recovered	Science	Motion Data Products	Recovered Science Motion Data Products	 Series A Data Concentrator Logger Motion Recovered   	\N
381	wavss_a_dcl_non_directional	Telemetered	Science	Non Directional Data Products	Telemetered Science Non Directional Data Products	 Series A Data Concentrator Logger  Directional   	\N
382	wavss_a_dcl_non_directional_recovered	Recovered	Science	Non Directional Data Products	Recovered Science Non Directional Data Products	 Series A Data Concentrator Logger  Directional Recovered  	\N
383	wavss_a_dcl_statistics	Telemetered	Science	Statistics Data Products	Telemetered Science Statistics Data Products	 Series A Data Concentrator Logger Statistics    	\N
384	wavss_a_dcl_statistics_recovered	Recovered	Science	Statistics Data Products	Recovered Science Statistics Data Products	 Series A Data Concentrator Logger Statistics Recovered   	\N
385	wfp_eng_stc_imodem_engineering	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering STC Controller  Engineering   	\N
386	wfp_eng_stc_imodem_engineering_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Engineering STC Controller  Engineering Recovered  	\N
387	wfp_eng_stc_imodem_start_time	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering STC Controller  Start Time  	\N
388	wfp_eng_stc_imodem_start_time_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Engineering STC Controller  Start Time Recovered 	\N
389	wfp_eng_stc_imodem_status	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering STC Controller  Status   	\N
390	wfp_eng_stc_imodem_status_recovered	Recovered	Engineering	Data	Recovered Engineering Data	 Engineering STC Controller  Status Recovered  	\N
391	wfp_eng_wfp_sio_mule_engineering	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering Wire Following Profiler SIO Controller  Engineering  	\N
392	wfp_eng_wfp_sio_mule_start_time	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering Wire Following Profiler SIO Controller  Start Time 	\N
393	wfp_eng_wfp_sio_mule_status	Telemetered	Engineering	Data	Telemetered Engineering Data	 Engineering Wire Following Profiler SIO Controller  Status  	\N
394	zplsc_c_instrument	Telemetered	Science	Data Products	Telemetered Science Data Products	 Series C Instrument     	\N
395	zplsc_metadata	Streamed	Engineering	Data	Streamed Engineering Data	 Metadata      	\N
396	zplsc_status	Streamed	Engineering	Data	Streamed Engineering Data	 Status      	\N
\.


--
-- Data for Name: datasets; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY datasets (id, stream_id, deployment_id, process_level, is_recovered) FROM stdin;
\.


--
-- Data for Name: dataset_keywords; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY dataset_keywords (id, dataset_id, concept_name, concept_description) FROM stdin;
\.


--
-- Name: dataset_keywords_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('dataset_keywords_id_seq', 1, false);


--
-- Name: datasets_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('datasets_id_seq', 1, false);


--
-- Name: deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('deployments_id_seq', 1, false);


--
-- Data for Name: drivers; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY drivers (id, instrument_id, driver_name, driver_version, author) FROM stdin;
\.


--
-- Data for Name: driver_stream_link; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY driver_stream_link (id, driver_id, stream_id) FROM stdin;
\.


--
-- Name: driver_stream_link_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('driver_stream_link_id_seq', 1, false);


--
-- Name: drivers_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('drivers_id_seq', 1, false);


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('files_id_seq', 1, false);


--
-- Data for Name: inspection_status; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY inspection_status (id, asset_id, file_id, status, technician_name, comments, inspection_date, document) FROM stdin;
\.


--
-- Name: inspection_status_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('inspection_status_id_seq', 1, false);


--
-- Data for Name: installation_records; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY installation_records (id, asset_id, assembly_id, date_installed, date_removed, technician_name, comments, file_id) FROM stdin;
\.


--
-- Name: installation_records_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('installation_records_id_seq', 1, false);


--
-- Data for Name: platforms; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY platforms (id, platform_name, description, location_description, platform_series, is_mobile, serial_no, asset_id, manufacturer_id) FROM stdin;
\.


--
-- Data for Name: platform_deployments; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY platform_deployments (id, start_date, end_date, platform_id, reference_designator, array_id, deployment_id, display_name, geo_location) FROM stdin;
\.


--
-- Data for Name: instrument_deployments; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY instrument_deployments (id, display_name, start_date, end_date, platform_deployment_id, instrument_id, reference_designator, depth, geo_location) FROM stdin;
\.


--
-- Name: instrument_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('instrument_deployments_id_seq', 1, false);


--
-- Name: instrument_models_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('instrument_models_id_seq', 1, false);


--
-- Data for Name: instrumentnames; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY instrumentnames (id, instrument_class, display_name) FROM stdin;
\.


--
-- Name: instrumentnames_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('instrumentnames_id_seq', 1, false);


--
-- Name: instruments_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('instruments_id_seq', 1, false);


--
-- Data for Name: log_entries; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY log_entries (id, log_entry_type, entry_time, entry_title, entry_description, retired, search_vector, user_id, organization_id) FROM stdin;
\.


--
-- Name: log_entries_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('log_entries_id_seq', 1, false);


--
-- Data for Name: log_entry_comments; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY log_entry_comments (id, comment_time, comment, retired, user_id, log_entry_id) FROM stdin;
\.


--
-- Name: log_entry_comments_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('log_entry_comments_id_seq', 1, false);


--
-- Name: manufacturers_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('manufacturers_id_seq', 1, false);


--
-- Data for Name: operator_event_types; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY operator_event_types (id, type_name, type_description) FROM stdin;
\.


--
-- Name: operator_event_types_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('operator_event_types_id_seq', 1, false);


--
-- Data for Name: watches; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY watches (id, start_time, end_time, user_id) FROM stdin;
\.


--
-- Data for Name: operator_events; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY operator_events (id, watch_id, operator_event_type_id, event_time, event_title, event_comment) FROM stdin;
\.


--
-- Name: operator_events_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('operator_events_id_seq', 1, false);


--
-- Name: organizations_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('organizations_id_seq', 1, true);


--
-- Name: platform_deployments_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('platform_deployments_id_seq', 1, false);


--
-- Data for Name: platformnames; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY platformnames (id, reference_designator, array_type, array_name, site, platform, assembly) FROM stdin;
\.


--
-- Name: platformnames_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('platformnames_id_seq', 1, false);


--
-- Name: platforms_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('platforms_id_seq', 1, false);


--
-- Data for Name: stream_parameters; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY stream_parameters (id, stream_parameter_name, short_name, long_name, standard_name, units, data_type) FROM stdin;
1	conductivity_quantity_float32_S_m_1	conductivity	\N	Conductivity, S m-1	S m-1	\N
2	pressure_quantity_float32_dbar	pressure	\N	Pressure (Depth), dbar	dbar	\N
3	salinity_quantity_float32_1	salinity	\N	Practical Salinity	1	\N
4	salinity_quantity_float32_g_kg_1	salinity	\N	Absolute Salinity	g kg-1	\N
5	density_quantity_float32_kg_m_3	density	\N	Density, kg m-3	kg m-3	\N
6	temp_quantity_float32_deg_C	temp	\N	Temperature	deg_C	\N
7	time_quantity_float64_seconds_since_1900_01_01	time	\N	Time, UTC	seconds since 1900-01-01	\N
8	lat_quantity_float32_degree_north	lat	\N	Latitude, degrees North	degree_north	\N
9	lon_quantity_float32_degree_east	lon	\N	Longitude, degrees East	degree_east	\N
10	port_timestamp_quantity_float64_seconds_since_1900_01_01	port_timestamp	\N	Port Timestamp, UTC	seconds since 1900-01-01	\N
11	driver_timestamp_quantity_float64_seconds_since_1900_01_01	driver_timestamp	\N	Driver Timestamp, UTC	seconds since 1900-01-01	\N
12	internal_timestamp_quantity_float64_seconds_since_1900_01_01	internal_timestamp	\N	Internal Timestamp, UTC	seconds since 1900-01-01	\N
13	counts_quantity_uint64_counts	counts	\N	\N	counts	\N
14	checksum_quantity_int32_1	checksum	\N	Checksum	1	\N
15	preferred_timestamp_quantity_string_1	preferred_timestamp	\N	Preferred Timestamp	1	\N
16	quality_flag_array_	quality_flag	\N	\N	\N	\N
17	viz_timestamp_quantity_float64_seconds_since_1900_01_01	viz_timestamp	\N	Timestamp, UTC	seconds since 1900-01-01	\N
18	viz_product_type_array_	viz_product_type	\N	\N	\N	\N
19	image_obj_array_	image_obj	\N	Image object	\N	\N
20	image_name_array_	image_name	\N	Image name	\N	\N
21	content_type_array_	content_type	\N	Content type	\N	\N
22	google_dt_components_record_	google_dt_components	\N	\N	\N	\N
23	mpl_graph_record_	mpl_graph	\N	\N	\N	\N
24	dummy_quantity_int64_	dummy	\N	\N	\N	\N
25	raw_array_quantity_opaque_1	raw	\N	raw data	1	\N
26	input_voltage_quantity_float64_volts	input_voltage	\N	Input voltage	volts	\N
27	elapsed_time_quantity_float64_s	elapsed_time	\N	Time since reset, seconds	s	\N
28	pressure_temp_quantity_float32_deg_C	pressure_temp	\N	Internal temperature at the pressure sensor, deg C	deg_C	\N
29	sample_param_quantity_uint16_shouldnt_work_	sample_param	\N	\N	shouldnt work 	\N
30	condwat_glblrng_qc_boolean_int8_1	condwat_glblrng_qc	\N	Conductivity global range QC	1	\N
31	condwat_loclrng_qc_boolean_int8_1	condwat_loclrng_qc	\N	Conductivity local range QC	1	\N
32	condwat_spketst_qc_boolean_int8_1	condwat_spketst_qc	\N	Conductivity spike test QC	1	\N
33	condwat_stuckvl_qc_boolean_int8_1	condwat_stuckvl_qc	\N	Conductivity Stuck Value QC	1	\N
34	condwat_sptl_gradtst_qc_boolean_int8_1	condwat_sptl_gradtst_qc	\N	Conductivity spatial gradient QC	1	\N
35	condwat_tmpl_gradtst_qc_boolean_int8_1	condwat_tmpl_gradtst_qc	\N	Conductivity temporal gradient QC	1	\N
36	preswat_glblrng_qc_boolean_int8_1	preswat_glblrng_qc	\N	Pressure global range QC 	1	\N
37	preswat_loclrng_qc_boolean_int8_1	preswat_loclrng_qc	\N	Pressure local range QC	1	\N
38	preswat_spketst_qc_boolean_int8_1	preswat_spketst_qc	\N	Pressure spike test QC	1	\N
39	preswat_stuckvl_qc_boolean_int8_1	preswat_stuckvl_qc	\N	Pressure Stuck Value QC	1	\N
40	preswat_sptl_gradtst_qc_boolean_int8_1	preswat_sptl_gradtst_qc	\N	Pressure spatial gradient QC	1	\N
41	preswat_tmpl_gradtst_qc_boolean_int8_1	preswat_tmpl_gradtst_qc	\N	Pressure temporal gradient QC	1	\N
42	tempwat_glblrng_qc_boolean_int8_1	tempwat_glblrng_qc	\N	Temperature global range QC	1	\N
43	tempwat_loclrng_qc_boolean_int8_1	tempwat_loclrng_qc	\N	Temperature local range QC	1	\N
44	tempwat_spketst_qc_boolean_int8_1	tempwat_spketst_qc	\N	Temperature spike test QC	1	\N
45	tempwat_stuckvl_qc_boolean_int8_1	tempwat_stuckvl_qc	\N	Temperature Stuck Value QC	1	\N
46	tempwat_sptl_gradtst_qc_boolean_int8_1	tempwat_sptl_gradtst_qc	\N	Temperature spatial gradient QC	1	\N
47	tempwat_tmpl_gradtst_qc_boolean_int8_1	tempwat_tmpl_gradtst_qc	\N	Temperature temporal gradient QC	1	\N
48	pracsal_glblrng_qc_boolean_int8_1	pracsal_glblrng_qc	\N	Practical salinity global range QC	1	\N
49	pracsal_loclrng_qc_boolean_int8_1	pracsal_loclrng_qc	\N	Practical salinity local range QC	1	\N
50	pracsal_spketst_qc_boolean_int8_1	pracsal_spketst_qc	\N	Practical salinity spike test QC	1	\N
51	pracsal_stuckvl_qc_boolean_int8_1	pracsal_stuckvl_qc	\N	Practical salinity Stuck Value QC	1	\N
52	pracsal_sptl_gradtst_qc_boolean_int8_1	pracsal_sptl_gradtst_qc	\N	Practical salinity spatial gradient QC	1	\N
53	pracsal_tmpl_gradtst_qc_boolean_int8_1	pracsal_tmpl_gradtst_qc	\N	Practical salinity temporal gradient QC	1	\N
54	density_glblrng_qc_boolean_int8_1	density_glblrng_qc	\N	Density global range QC	1	\N
55	density_loclrng_qc_boolean_int8_1	density_loclrng_qc	\N	Density local range QC	1	\N
56	density_spketst_qc_boolean_int8_1	density_spketst_qc	\N	Density spike test QC	1	\N
57	density_stuckvl_qc_boolean_int8_1	density_stuckvl_qc	\N	Density Stuck Value QC	1	\N
58	density_sptl_gradtst_qc_boolean_int8_1	density_sptl_gradtst_qc	\N	Density spatial gradient QC	1	\N
59	density_tmpl_gradtst_qc_boolean_int8_1	density_tmpl_gradtst_qc	\N	Density temporal gradient QC	1	\N
60	Resistivity5_quantity_float32_V	Resistivity5	\N	Resistivity/5	V	\N
61	ResistivityX1_quantity_float32_V	ResistivityX1	\N	Resistivity X1	V	\N
62	ResistivityX5_quantity_float32_V	ResistivityX5	\N	x	V	\N
63	Hydrogen5_quantity_float32_V	Hydrogen5	\N	Hydrogen/5	V	\N
64	HydrogenX1_quantity_float32_V	HydrogenX1	\N	Hydrogen X1	V	\N
65	HydrogenX5_quantity_float32_V	HydrogenX5	\N	Hydrogen X5	V	\N
66	EhSensor_quantity_float32_V	EhSensor	\N	Eh Sensor        	V	\N
67	RefTempVolts_quantity_float32_V	RefTempVolts	\N	Reference Temp Volts     	V	\N
68	RefTempDegC_quantity_float32_deg_C	RefTempDegC	\N	Reference Temp Deg C     	deg_C	\N
69	ResistivityTempVolts_quantity_float32_V	ResistivityTempVolts	\N	Resistivity Temp Volts   	V	\N
70	ResistivityTempDegC_quantity_float32_deg_C	ResistivityTempDegC	\N	Resistivity Temp Deg C   	deg_C	\N
71	BatteryVoltage_quantity_float32_V	BatteryVoltage	\N	Battery Voltage  	V	\N
72	sample_number_quantity_int32_count	sample_number	\N	 sample number = xxxxxxxx	count	\N
73	sample_type_quantity_string_1	sample_type	\N	Sample Type From Instrument	1	\N
74	InstTime_quantity_string_1	InstTime	\N	Time (Moored mode MM only) seconds since January 1, 2000 = ssssssss	1	\N
75	timestamp_quantity_string_1	timestamp	\N	timestamp	1	\N
76	error_quantity_int32_C	error	\N	error code	C	\N
77	analog1_quantity_int32_C	analog1	\N	analog input 1	C	\N
78	battery_voltage_quantity_int32_C	battery_voltage	\N	battery voltage (0.1 V)	C	\N
79	sound_speed_analog2_quantity_int32_C	sound_speed_analog2	\N	speed of sound (0.1 m/s) or analog input 2	C	\N
80	heading_quantity_int32_degrees	heading	\N	compass heading (0.1°)	degrees	\N
81	pitch_quantity_int32_degrees	pitch	\N	compass pitch (0.1°)	degrees	\N
82	roll_quantity_int32_degrees	roll	\N	compass roll (0.1°)	degrees	\N
83	status_array_quantity_int8_	status	\N	status code	\N	\N
84	temperature_quantity_int32_deg_C	temperature	\N	temperature (0.01 °C)	deg_C	\N
85	velocity_beam1_quantity_int32_C	velocity_beam1	\N	velocity beam1 or X or East coordinates (mm/s)	C	\N
86	velocity_beam2_quantity_int32_C	velocity_beam2	\N	velocity beam2 or Y or North coordinates (mm/s)	C	\N
87	velocity_beam3_quantity_int32_C	velocity_beam3	\N	velocity beam3 or Z or Up coordinates (mm/s)	C	\N
88	amplitude_beam1_quantity_int32_counts	amplitude_beam1	\N	amplitude beam1 (counts)	counts	\N
89	amplitude_beam2_quantity_int32_counts	amplitude_beam2	\N	amplitude beam2 (counts)	counts	\N
90	amplitude_beam3_quantity_int32_counts	amplitude_beam3	\N	amplitude beam3 (counts)	counts	\N
91	date_time_string_quantity_string_1	date_time_string	\N	Date and Time String	1	\N
92	absolute_pressure_quantity_float32_psi	absolute_pressure	\N	Seafloor Pressure, psi	psi	\N
93	seawater_temperature_quantity_float32_deg_C	seawater_temperature	\N	Temperature	deg_C	\N
94	seafloor_pressure_quantity_float32_dbar	seafloor_pressure	\N	Seafloor Pressure, dbar	dbar	\N
95	ptemp_frequency_quantity_float32_Hz	ptemp_frequency	\N	Pressure Temperature Frequency	Hz	\N
96	n_avg_band_quantity_int16_1	n_avg_band	\N	Number of Averaging Bands	1	\N
97	ass_total_variance_quantity_float32_m_2	ass_total_variance	\N	Auto-Spectrum Statistics - Total Variance	m^2	\N
98	ass_total_energy_quantity_float32_J_m_1	ass_total_energy	\N	Auto-Spectrum Statistics - Total Energy	J m-1	\N
99	ass_sig_wave_period_quantity_float32_s	ass_sig_wave_period	\N	Auto-Spectrum Statistics - Significant Wave Period	s	\N
100	ass_sig_wave_height_quantity_float32_m	ass_sig_wave_height	\N	Auto-Spectrum Statistics - Significant Wave Height	m	\N
101	tss_wave_integration_time_quantity_int16_s	tss_wave_integration_time	\N	Time Series Statistics - Wave Burst Duration	s	\N
102	tss_number_of_waves_quantity_int16_1	tss_number_of_waves	\N	Time Series Statistics - Number of Waves	1	\N
103	tss_total_variance_quantity_float32_m_2	tss_total_variance	\N	Time Series Statistics - Total Variance	m^2	\N
104	tss_total_energy_quantity_float32_J_m_2	tss_total_energy	\N	Time Series Statistics - Total Energy	J m-2	\N
105	tss_avg_wave_height_quantity_float32_m	tss_avg_wave_height	\N	Time Series Statistics - Average Wave Height	m	\N
106	tss_avg_wave_period_quantity_float32_s	tss_avg_wave_period	\N	Time Series Statistics - Average Wave Period	s	\N
107	tss_max_wave_height_quantity_float32_m	tss_max_wave_height	\N	Time Series Statistics - Maximum Wave Height	m	\N
108	tss_sig_wave_height_quantity_float32_m	tss_sig_wave_height	\N	Time Series Statistics - Significant Wave Height	m	\N
109	tss_sig_wave_period_quantity_float32_s	tss_sig_wave_period	\N	Time Series Statistics - Significant Wave Period	s	\N
110	tss_10_wave_height_quantity_float32_m	tss_10_wave_height	\N	Time Series Statistics - Average Height of Highest 10% of Waves	m	\N
111	tss_1_wave_height_quantity_float32_m	tss_1_wave_height	\N	Time Series Statistics - Average Height of Highest 1% of Waves	m	\N
112	firmware_version_quantity_string_1	firmware_version	\N	Firmware Version	1	\N
113	user_info_quantity_string_1	user_info	\N	User Info	1	\N
114	quartz_pressure_sensor_serial_number_quantity_string_1	quartz_pressure_sensor_serial_number	\N	Quartz Pressure Sensor Serial Number	1	\N
115	pressure_sensor_range_quantity_int16_psi	pressure_sensor_range	\N	Pressure Sensor Range	psi	\N
116	external_temperature_sensor_boolean_int8_1	external_temperature_sensor	\N	Use External Temperature	1	\N
117	external_conductivity_sensor_boolean_int8_1	external_conductivity_sensor	\N	Use External Conductivity	1	\N
118	operational_current_quantity_float32_mA	operational_current	\N	Operational Current	mA	\N
119	battery_voltage_main_quantity_float32_V	battery_voltage_main	\N	Main Battery Voltage	V	\N
120	battery_voltage_lithium_quantity_float32_V	battery_voltage_lithium	\N	Lithium Battery Voltage	V	\N
121	last_sample_absolute_press_quantity_float32_psi	last_sample_absolute_press	\N	Last Measured Absolute Pressure	psi	\N
122	last_sample_temp_quantity_float32_deg_C	last_sample_temp	\N	Last Measured Temperature	deg_C	\N
123	last_sample_saln_quantity_float32_1	last_sample_saln	\N	Last Measured Salinity	1	\N
124	tide_measurement_interval_quantity_int16_min	tide_measurement_interval	\N	Tide Sampling Interval	min	\N
125	tide_measurement_duration_quantity_int16_s	tide_measurement_duration	\N	Tide Sampling Duration	s	\N
126	wave_samples_between_tide_measurements_quantity_int16_1	wave_samples_between_tide_measurements	\N	Sample Waves every N Tide Samples	1	\N
127	wave_samples_per_burst_quantity_int16_1	wave_samples_per_burst	\N	Wave Samples per Burst	1	\N
128	wave_samples_scans_per_second_quantity_float32_1	wave_samples_scans_per_second	\N	Scans per Second	1	\N
129	wave_samples_duration_quantity_float32_s	wave_samples_duration	\N	Wave Sampling Duration	s	\N
130	logging_start_time_quantity_string_1	logging_start_time	\N	Logging Start Time	1	\N
131	logging_stop_time_quantity_string_1	logging_stop_time	\N	Logging Stop Time	1	\N
132	tide_samples_per_day_quantity_int16_count	tide_samples_per_day	\N	Number of Tide Samples per Day	count	\N
133	wave_bursts_per_day_quantity_int16_count	wave_bursts_per_day	\N	Number of Wave Bursts per Day	count	\N
134	memory_endurance_quantity_float32_days	memory_endurance	\N	Expected Memory Endurance	days	\N
135	nominal_alkaline_battery_endurance_quantity_float32_days	nominal_alkaline_battery_endurance	\N	Expected Battery Endurance	days	\N
136	total_recorded_tide_measurements_quantity_int32_count	total_recorded_tide_measurements	\N	Total Recorded Tide Measurements	count	\N
137	total_recorded_wave_bursts_quantity_int32_count	total_recorded_wave_bursts	\N	Total Recorded Wave Bursts	count	\N
138	tide_measurements_since_last_start_quantity_int32_count	tide_measurements_since_last_start	\N	Tide Measurements Since Last Start	count	\N
139	wave_bursts_since_last_start_quantity_int32_count	wave_bursts_since_last_start	\N	Wave Bursts Since Last Start	count	\N
140	tx_tide_samples_boolean_int8_1	tx_tide_samples	\N	Transmit Tide Records in Realtime	1	\N
141	tx_wave_bursts_boolean_int8_1	tx_wave_bursts	\N	Transmit Wave Records in Realtime	1	\N
142	tx_wave_stats_boolean_int8_1	tx_wave_stats	\N	Transmit Wave Statistics in Realtime	1	\N
143	num_wave_samples_per_burst_for_wave_statistics_quantity_int16_count	num_wave_samples_per_burst_for_wave_statistics	\N	Number of Wave Samples per Burst	count	\N
144	use_measured_temp_and_cond_for_density_calc_boolean_int8_1	use_measured_temp_and_cond_for_density_calc	\N	Use Measure Temperature and Conductivity for Density Calculation	1	\N
145	avg_water_temp_above_pressure_sensor_quantity_float32_deg_C	avg_water_temp_above_pressure_sensor	\N	Average Temperature above Instrument	deg_C	\N
146	avg_salinity_above_pressure_sensor_quantity_float32_1	avg_salinity_above_pressure_sensor	\N	Average Salinity above Instrument	1	\N
147	pressure_sensor_height_from_bottom_quantity_float32_m	pressure_sensor_height_from_bottom	\N	Pressure Sensor Height Above Bottom	m	\N
148	num_spectral_estimates_for_each_frequency_band_quantity_int16_count	num_spectral_estimates_for_each_frequency_band	\N	Number of Spectral Estimates to Average	count	\N
149	min_allowable_attenuation_quantity_float32_1	min_allowable_attenuation 	\N	Minimum Allowable Attenuation	1	\N
150	min_period_in_auto_spectrum_quantity_float32_s	min_period_in_auto_spectrum 	\N	Minimum Allowable Period	s	\N
151	max_period_in_auto_spectrum_quantity_float32_s	max_period_in_auto_spectrum 	\N	Maximum Allowable Period	s	\N
152	hanning_window_cutoff_quantity_float32_1	hanning_window_cutoff 	\N	Hanning Window Cutoff	1	\N
153	show_progress_messages_boolean_int8_1	show_progress_messages 	\N	Show Progress Messages	1	\N
154	device_status_quantity_string_1	device_status	\N	Device Status	1	\N
155	logging_status_boolean_int8_1	logging_status	\N	Logging Status	1	\N
156	calibration_date_pressure_quantity_string_1	calibration_date_pressure	\N	Pressure Calibration Date	1	\N
157	press_coeff_pu0_quantity_float32_1	press_coeff_pu0	\N	Pressure Coefficient U0	1	\N
158	press_coeff_py1_quantity_float32_1	press_coeff_py1	\N	Pressure Coefficient Y1	1	\N
159	press_coeff_py2_quantity_float32_1	press_coeff_py2	\N	Pressure Coefficient Y2	1	\N
160	press_coeff_py3_quantity_float32_1	press_coeff_py3	\N	Pressure Coefficient Y3	1	\N
161	press_coeff_pc1_quantity_float32_1	press_coeff_pc1	\N	Pressure Coefficient C1	1	\N
162	press_coeff_pc2_quantity_float32_1	press_coeff_pc2	\N	Pressure Coefficient C2	1	\N
163	press_coeff_pc3_quantity_float32_1	press_coeff_pc3	\N	Pressure Coefficient C3	1	\N
164	press_coeff_pd1_quantity_float32_1	press_coeff_pd1	\N	Pressure Coefficient D1	1	\N
165	press_coeff_pd2_quantity_float32_1	press_coeff_pd2	\N	Pressure Coefficient D2	1	\N
166	press_coeff_pt1_quantity_float32_1	press_coeff_pt1	\N	Pressure Coefficient T1	1	\N
167	press_coeff_pt2_quantity_float32_1	press_coeff_pt2	\N	Pressure Coefficient T2	1	\N
168	press_coeff_pt3_quantity_float32_1	press_coeff_pt3	\N	Pressure Coefficient T3	1	\N
169	press_coeff_pt4_quantity_float32_1	press_coeff_pt4	\N	Pressure Coefficient T4	1	\N
170	press_coeff_m_quantity_float32_1	press_coeff_m	\N	Pressure Coefficient M	1	\N
171	press_coeff_b_quantity_float32_1	press_coeff_b	\N	Pressure Coefficient B	1	\N
172	press_coeff_poffset_quantity_float32_psi	press_coeff_poffset	\N	Pressure Coefficient Offset	psi	\N
173	calibration_date_temperature_quantity_string_1	calibration_date_temperature	\N	Temperature Calibration Date	1	\N
174	temp_coeff_ta0_quantity_float32_1	temp_coeff_ta0	\N	Temperature Coefficient A0	1	\N
175	temp_coeff_ta1_quantity_float32_1	temp_coeff_ta1	\N	Temperature Coefficient A1	1	\N
176	temp_coeff_ta2_quantity_float32_1	temp_coeff_ta2	\N	Temperature Coefficient A2	1	\N
177	temp_coeff_ta3_quantity_float32_1	temp_coeff_ta3	\N	Temperature Coefficient A3	1	\N
178	calibration_date_conductivity_quantity_string_1	calibration_date_conductivity	\N	Conductivity Calibration Date	1	\N
179	cond_coeff_cg_quantity_float32_1	cond_coeff_cg	\N	Conductivity Coefficient G	1	\N
180	cond_coeff_ch_quantity_float32_1	cond_coeff_ch	\N	Conductivity Coefficient H	1	\N
181	cond_coeff_ci_quantity_float32_1	cond_coeff_ci	\N	Conductivity Coefficient I	1	\N
182	cond_coeff_cj_quantity_float32_1	cond_coeff_cj	\N	Conductivity Coefficient J	1	\N
183	cond_coeff_ctcor_quantity_float32_1	cond_coeff_ctcor	\N	Conductivity Coefficient TCor	1	\N
184	cond_coeff_cpcor_quantity_float32_1	cond_coeff_cpcor	\N	Conductivity Coefficient PCor	1	\N
185	cond_coeff_cslope_quantity_float32_1	cond_coeff_cslope	\N	Conductivity Coefficient Slope	1	\N
186	par_quantity_int64_counts	par	\N	PAR A/D counts	counts	\N
187	par_coeff_imc_quantity_float32_1	par_coeff_imc	\N	PAR immersion coefficient	1	\N
188	par_biospherical_mobile_function_float32_umol_photons_m_2_s_1_count_1	par_biospherical_mobile	\N	PAR scaling factor	umol photons m-2 s-1 count-1	\N
189	par_coeff_a0_quantity_float32_count	par_coeff_a0	\N	PAR voltage offset	count	\N
190	par_counts_output_function_float32_umol_photons_m_2_s_1	par_counts_output	\N	Photosynthetic Active Radiation (PAR)	umol photons m-2 s-1	\N
191	temperature_quantity_int32_counts	temperature	\N	Temperature, A/D counts	counts	\N
192	conductivity_quantity_int32_counts	conductivity	\N	Conductivity, A/D counts	counts	\N
193	pressure_quantity_int32_counts	pressure	\N	Pressure, A/D counts	counts	\N
194	pressure_temp_quantity_int32_counts	pressure_temp	\N	Pressure Temperature Compensation, A/D counts	counts	\N
195	oxygen_quantity_int32_counts	oxygen	\N	Oxygen Concentration, counts	counts	\N
196	ctd_time_quantity_int32_seconds_since_2000_01_01	ctd_time	\N	Time, UTC	seconds since 2000-01-01	\N
197	pump_current_quantity_float32_mA	pump_current	\N	Pump current, mA	mA	\N
198	ext_v01_current_quantity_float32_mA	ext_v01_current	\N	Current from External Voltage Sensors 0 & 1, mA	mA	\N
199	serial_current_quantity_float32_mA	serial_current	\N	Auxiliary Serial Instrument Current, mA	mA	\N
200	logging_status_quantity_string_1	logging_status	\N	Logging Status Category	1	\N
201	num_samples_quantity_int32_counts	num_samples	\N	Number of Samples	counts	\N
202	mem_free_quantity_int32_bytes	mem_free	\N	Available Memory	bytes	\N
203	sample_interval_quantity_int16_s	sample_interval 	\N	Sampling Interval	s	\N
204	measurements_per_sample_quantity_int8_counts	measurements_per_sample 	\N	Number of Measurements per Sample	counts	\N
205	pump_mode_quantity_string_1	pump_mode	\N	CTD Pump Mode	1	\N
206	delay_before_sampling_quantity_float32_s	delay_before_sampling 	\N	Delay Before Sampling, seconds	s	\N
207	delay_after_sampling_quantity_float32_s	delay_after_sampling	\N	Delay After Sampling, seconds	s	\N
208	tx_real_time_boolean_int8_1	tx_real_time 	\N	Transmit in Real Time flag	1	\N
209	battery_cutoff_quantity_float32_V	battery_cutoff 	\N	Battery Cutoff Voltage	V	\N
210	pressure_sensor_type_quantity_string_1	pressure_sensor_type	\N	Pressure Sensor Type Category	1	\N
211	sbe38_boolean_int8_1	sbe38	\N	External SBE38 Flag	1	\N
212	sbe50_boolean_int8_1	sbe50	\N	External SBE50 Flag	1	\N
213	wetlabs_boolean_int8_1	wetlabs 	\N	External Wetlabs Flag	1	\N
214	optode_boolean_int8_1	optode 	\N	External Optode Flag	1	\N
215	gas_tension_device_boolean_int8_1	gas_tension_device 	\N	External Gas Tension Device Flag	1	\N
216	ext_volt_0_boolean_int8_1	ext_volt_0	\N	External Voltage 0 Sensor Flag	1	\N
217	ext_volt_1_boolean_int8_1	ext_volt_1	\N	External Voltage 1 Sensor Flag	1	\N
218	ext_volt_2_boolean_int8_1	ext_volt_2	\N	External Voltage 2 Sensor Flag	1	\N
219	ext_volt_3_boolean_int8_1	ext_volt_3	\N	External Voltage 3 Sensor Flag	1	\N
220	ext_volt_4_boolean_int8_1	ext_volt_4	\N	External Voltage 4 Sensor Flag	1	\N
221	ext_volt_5_boolean_int8_1	ext_volt_5	\N	External Voltage 5 Sensor Flag	1	\N
222	echo_characters_boolean_int8_1	echo_characters 	\N	Echo Characters Flag	1	\N
223	output_format_quantity_string_1	output_format 	\N	Data Output Format Category	1	\N
224	output_salinity_boolean_int8_1	output_salinity 	\N	Output Salinity Data Flag	1	\N
225	output_sound_velocity_boolean_int8_1	output_sound_velocity 	\N	Output Sound Velocity Data Flag	1	\N
226	serial_sync_mode_boolean_int8_1	serial_sync_mode 	\N	Serial Sync Mode	1	\N
227	temp_coeff_offset_quantity_float32_1	temp_coeff_offset	\N	Temperature Coefficient Offset	1	\N
228	press_coeff_pa0_quantity_float32_1	press_coeff_pa0	\N	Pressure Coefficient PA0	1	\N
229	press_coeff_pa1_quantity_float32_1	press_coeff_pa1	\N	Pressure Coefficient PA1	1	\N
230	press_coeff_pa2_quantity_float32_1	press_coeff_pa2	\N	Pressure Coefficient PA2	1	\N
231	press_coeff_ptempa0_quantity_float32_1	press_coeff_ptempa0	\N	Pressure Coefficient PTempA0	1	\N
232	press_coeff_ptempa1_quantity_float32_1	press_coeff_ptempa1	\N	Pressure Coefficient PTempA1	1	\N
233	press_coeff_ptempa2_quantity_float32_1	press_coeff_ptempa2	\N	Pressure Coefficient PTempA2	1	\N
234	press_coeff_ptca0_quantity_float32_1	press_coeff_ptca0	\N	Pressure Coefficient PTCA0	1	\N
235	press_coeff_ptca1_quantity_float32_1	press_coeff_ptca1	\N	Pressure Coefficient PTCA1	1	\N
236	press_coeff_ptca2_quantity_float32_1	press_coeff_ptca2	\N	Pressure Coefficient PTCA2	1	\N
237	press_coeff_ptcb0_quantity_float32_1	press_coeff_ptcb0	\N	Pressure Coefficient PTCB0	1	\N
238	press_coeff_ptcb1_quantity_float32_1	press_coeff_ptcb1	\N	Pressure Coefficient PTCB1	1	\N
239	press_coeff_ptcb2_quantity_float32_1	press_coeff_ptcb2	\N	Pressure Coefficient PTCB2	1	\N
240	ext_volt0_slope_quantity_float32_1	ext_volt0_slope	\N	External Voltage Sensor 0 Slope	1	\N
241	ext_volt0_offset_quantity_float32_1	ext_volt0_offset	\N	External Voltage Sensor 0 Offset	1	\N
242	ext_volt1_slope_quantity_float32_1	ext_volt1_slope	\N	External Voltage Sensor 1 Slope	1	\N
243	ext_volt1_offset_quantity_float32_1	ext_volt1_offset	\N	External Voltage Sensor 1 Offset	1	\N
244	ext_volt2_slope_quantity_float32_1	ext_volt2_slope	\N	External Voltage Sensor 2 Slope	1	\N
245	ext_volt2_offset_quantity_float32_1	ext_volt2_offset	\N	External Voltage Sensor 2 Offset	1	\N
246	ext_volt3_slope_quantity_float32_1	ext_volt3_slope	\N	External Voltage Sensor 3 Slope	1	\N
247	ext_volt3_offset_quantity_float32_1	ext_volt3_offset	\N	External Voltage Sensor 3 Offset	1	\N
248	ext_volt4_slope_quantity_float32_1	ext_volt4_slope	\N	External Voltage Sensor 4 Slope	1	\N
249	ext_volt4_offset_quantity_float32_1	ext_volt4_offset	\N	External Voltage Sensor 4 Offset	1	\N
250	ext_volt5_slope_quantity_float32_1	ext_volt5_slope	\N	External Voltage Sensor 5 Slope	1	\N
251	ext_volt5_offset_quantity_float32_1	ext_volt5_offset	\N	External Voltage Sensor 5 Offset	1	\N
252	ext_freq_sf_quantity_float32_1	ext_freq_sf	\N	External Frequency Channel	1	\N
253	press_coeff_pslope_quantity_float32_1	press_coeff_pslope	\N	Pressure Coefficient pslope	1	\N
254	temp_sensor_serial_number_quantity_string_1	temp_sensor_serial_number	\N	Temperature Sensor Serial Number	1	\N
255	cond_sensor_serial_number_quantity_string_1	cond_sensor_serial_number	\N	Conductivity Sensor Serial Number	1	\N
256	command_set_version_quantity_string_1	command_set_version	\N	Command Set Version	1	\N
257	paros_integration_quantity_float32_s	paros_integration	\N	Integration Time for Quartz Pressure Sensor, sec	s	\N
258	assembly_number_array_quantity_string_1	assembly_number	\N	PC Board Assembly Number	1	\N
259	output_sigmat_boolean_int8_1	output_sigmat	\N	Output Sigma T flag	1	\N
260	num_events_quantity_int32_counts	num_events	\N	Number of Events	counts	\N
261	samples_free_quantity_int32_counts	samples_free	\N	Number of Samples Free	counts	\N
262	sample_length_quantity_int32_bytes	sample_length	\N	Bytes per Sample	bytes	\N
263	headers_quantity_int32_counts	headers	\N	Headers	counts	\N
264	output_executed_tag_boolean_int8_1	output_executed_tag	\N	Output Executed Tag flag	1	\N
265	set_timeout_quantity_int32_ms	set_timeout	\N	Set Timeout, ms	ms	\N
266	set_timeout_max_quantity_int32_ms	set_timeout_max	\N	Set Timeout, Max, ms	ms	\N
267	set_timeout_icd_quantity_int32_ms	set_timeout_icd	\N	Set Timeout ICD, ms	ms	\N
268	reference_oscillator_freq_quantity_float64_Hz	reference_oscillator_freq	\N	Reference Oscillator Frequency, Hz	Hz	\N
269	pcb_thermistor_value_quantity_int32_counts	pcb_thermistor_value	\N	PCB Thermistor Value, counts	counts	\N
270	reference_error_quantity_float32_ppm	reference_error	\N	Reference Error, ppm	ppm	\N
271	device_type_quantity_string_1	device_type	\N	Device Type	1	\N
272	calibration_date_acq_crystal_quantity_string_1	calibration_date_acq_crystal	\N	Calibration Date, Acquisition Crystal	1	\N
273	acq_crystal_coeff_fra0_quantity_float32_1	acq_crystal_coeff_fra0	\N	Acq Crystal Coeff Fra0	1	\N
274	acq_crystal_coeff_fra1_quantity_float32_1	acq_crystal_coeff_fra1	\N	Acq Crystal Coeff Fra1	1	\N
275	acq_crystal_coeff_fra2_quantity_float32_1	acq_crystal_coeff_fra2	\N	Acq Crystal Coeff Fra2	1	\N
276	acq_crystal_coeff_fra3_quantity_float32_1	acq_crystal_coeff_fra3	\N	Acq Crystal Coeff Fra3	1	\N
277	pressure_sensor_serial_number_quantity_string_1	pressure_sensor_serial_number	\N	Pressure Sensor Serial Number	1	\N
278	pressure_sensor_range_quantity_float32_psi	pressure_sensor_range	\N	Pressure Sensor Range, psi	psi	\N
279	battery_type_category_int8_str_int8_1	battery_type	\N	Battery Type	1	\N
280	baud_rate_quantity_int32_Bd	baud_rate	\N	Baud Rate	Bd	\N
281	enable_alerts_boolean_int8_1	enable_alerts	\N	Enable Alerts	1	\N
282	upload_type_category_int8_str_int8_1	upload_type	\N	Upload Type	1	\N
283	sample_period_quantity_int32_s	sample_period 	\N	Sample Period, s	s	\N
284	version_quantity_string_1	version	\N	Version	1	\N
285	event_count_quantity_int32_count	event_count	\N	Event Count	count	\N
286	bytes_used_quantity_int32_1	bytes_used	\N	Bytes Used	1	\N
287	bytes_free_quantity_int32_1	bytes_free 	\N	Bytes Free 	1	\N
288	manufacturer_quantity_string_1	manufacturer	\N	Manufacturer	1	\N
289	firmware_date_quantity_string_1	firmware_date	\N	Firmware Date	1	\N
290	hardware_version_array_quantity_string_1	hardware_version	\N	Hardware Version	1	\N
291	pcb_serial_number_array_quantity_string_1	pcb_serial_number	\N	PCB Serial Number	1	\N
292	pcb_type_quantity_string_1	pcb_type	\N	PCB Type	1	\N
293	manufacture_date_quantity_string_1	manufacture_date 	\N	Manufacture Date 	1	\N
294	number_events_quantity_int32_1	number_events	\N	Number Events	1	\N
295	power_on_reset_quantity_int32_1	power_on_reset	\N	Power On Reset	1	\N
296	power_fail_reset_quantity_int32_1	power_fail_reset	\N	Power Fail Reset	1	\N
297	watchdog_reset_quantity_int32_1	watchdog_reset	\N	Watchdog Reset	1	\N
298	serial_byte_error_quantity_int32_1	serial_byte_error	\N	Serial Byte Error	1	\N
299	command_buffer_overflow_quantity_int32_1	command_buffer_overflow	\N	Command Buffer Overflow	1	\N
300	serial_receive_overflow_quantity_int32_1	serial_receive_overflow	\N	Serial Receive Overflow	1	\N
301	low_battery_quantity_int32_1	low_battery	\N	Low Battery	1	\N
302	out_of_memory_quantity_int32_1	out_of_memory	\N	Out of Memory	1	\N
303	signal_error_quantity_int32_1	signal_error	\N	Signal Error	1	\N
304	error_10_quantity_int32_1	error_10	\N	Error 10	1	\N
305	error_12_quantity_int32_1	error_12	\N	Error 12	1	\N
306	frame_header_quantity_string_1	frame_header	\N	\N	1	\N
307	frame_type_quantity_string_1	frame_type	\N	Frame Type	1	\N
308	serial_number_quantity_string_1	serial_number	\N	Serial Number	1	\N
309	date_of_sample_quantity_int32_1	date_of_sample	\N	Date of Sample	1	\N
310	time_of_sample_quantity_float64_h	time_of_sample	\N	Time of Sample	h	\N
311	nitrate_concentration_quantity_float32_uMol_L_1	nitrate_concentration	\N	Nitrate Concentration	uMol L-1	\N
312	aux_fitting_1_quantity_float32_1	aux_fitting_1	\N	Aux Fitting 1	1	\N
313	aux_fitting_2_quantity_float32_1	aux_fitting_2	\N	Aux Fitting 2	1	\N
314	aux_fitting_3_quantity_float32_1	aux_fitting_3	\N	\N	1	\N
315	rms_error_quantity_float32_uMol_L_1	rms_error	\N	\N	uMol L-1	\N
316	temp_interior_quantity_float32_deg_C	temp_interior	\N	Interior Temperature	deg_C	\N
317	temp_spectrometer_quantity_float32_deg_C	temp_spectrometer	\N	Spectrometer Temperature	deg_C	\N
318	temp_lamp_quantity_float32_deg_C	temp_lamp	\N	Lamp Temperature	deg_C	\N
319	humidity_quantity_float32_%	humidity	\N	Humidity	%	\N
320	voltage_lamp_quantity_float32_V	voltage_lamp	\N	Lamp Voltage	V	\N
321	voltage_analog_quantity_float32_V	voltage_analog	\N	\N	V	\N
322	voltage_main_quantity_float32_V	voltage_main	\N	Main Voltage	V	\N
323	ref_channel_average_quantity_float32_counts	ref_channel_average	\N	\N	counts	\N
324	ref_channel_variance_quantity_float32_1	ref_channel_variance	\N	\N	1	\N
325	sea_water_dark_quantity_float32_counts	sea_water_dark	\N	\N	counts	\N
326	spec_channel_average_quantity_float32_counts	spec_channel_average	\N	\N	counts	\N
327	spectral_channels_array_quantity_uint16_counts	spectral_channels	\N	Spectral Channels	counts	\N
328	checksum_quantity_uint8_1	checksum 	\N	Data Checksum.	1	\N
329	startup_time_quantity_int32_seconds_since_1970_01_01	startup_time	\N	Startup Time, UTC	seconds since 1970-01-01	\N
330	persistor_cf_card_quantity_string_1	persistor_cf_card	\N	\N	1	\N
331	persistor_bios_quantity_string_1	persistor_bios	\N	\N	1	\N
332	persistor_picodos_version_quantity_string_1	persistor_picodos_version	\N	\N	1	\N
333	persistor_picodos_bytes_used_quantity_int32_bytes	persistor_picodos_bytes_used	\N	\N	bytes	\N
334	cf_card_size_quantity_int32_bytes	cf_card_size	\N	\N	bytes	\N
335	cf_card_free_quantity_int32_bytes	cf_card_free	\N	\N	bytes	\N
336	previous_shutdown_code_quantity_string_1	previous_shutdown_code	\N	\N	1	\N
337	operating_mode_quantity_string_1	operating_mode	\N	\N	1	\N
338	use_shutter_darks_boolean_int8_1	use_shutter_darks	\N	\N	1	\N
339	lamp_time_quantity_int32_s	lamp_time	\N	Lamp Time, s	s	\N
340	spec_on_time_quantity_int32_seconds_since_1970_01_01	spec_on_time	\N	Spec on time, UTC	seconds since 1970-01-01	\N
341	spec_powered_time_quantity_int32_seconds_since_1970_01_01	spec_powered_time	\N	Spec Powered Time, UTC	seconds since 1970-01-01	\N
342	lamp_on_time_quantity_int32_seconds_since_1970_01_01	lamp_on_time	\N	Lamp On Time, UTC	seconds since 1970-01-01	\N
343	lamp_powered_time_quantity_int32_seconds_since_1970_01_01	lamp_powered_time	\N	Lamp Powered Time, UTC	seconds since 1970-01-01	\N
344	data_log_file_quantity_string_1	data_log_file	\N	\N	1	\N
345	unique_id_quantity_uint8_1	unique_id	\N	Instrument Unique ID	1	\N
346	record_length_quantity_uint8_1	record_length	\N	Record Length	1	\N
347	record_type_quantity_uint8_1	record_type	\N	Record Type	1	\N
348	record_time_quantity_int64_seconds_since_1904_01_01	record_time	\N	Record Time, UTC	seconds since 1904-01-01	\N
349	light_measurements_array_quantity_int16_counts	light_measurements	\N	Light Measurements, counts	counts	\N
350	voltage_battery_quantity_int16_counts	voltage_battery	\N	Voltage Battery, counts	counts	\N
351	thermistor_raw_quantity_int16_counts	thermistor_raw	\N	Thermistor Raw, counts	counts	\N
352	pump_on_boolean_int8_1	pump_on	\N	Pump On	1	\N
353	valve_on_boolean_int8_1	valve_on	\N	Valve On	1	\N
354	external_power_on_boolean_int8_1	external_power_on	\N	External Power On	1	\N
355	debug_led_boolean_int8_1	debug_led	\N	Debug LED	1	\N
356	debug_echo_boolean_int8_1	debug_echo 	\N	Debug Echo 	1	\N
357	elapsed_time_config_quantity_int64_s	elapsed_time_config	\N	Elapsed Time Since Configuration, s	s	\N
358	clock_active_boolean_int8_1	clock_active	\N	Clock Active	1	\N
359	recording_active_boolean_int8_1	recording_active	\N	Recording Active	1	\N
360	record_end_on_time_boolean_int8_1	record_end_on_time	\N	Record End On Time	1	\N
361	record_memory_full_boolean_int8_1	record_memory_full	\N	Record Memory Full	1	\N
362	record_end_on_error_boolean_int8_1	record_end_on_error	\N	Record End On Error	1	\N
363	data_download_ok_boolean_int8_1	data_download_ok	\N	Data Download Ok	1	\N
364	flash_memory_open_boolean_int8_1	flash_memory_open	\N	Flash Memory Open	1	\N
365	battery_low_prestart_boolean_int8_1	battery_low_prestart	\N	Battery Error Fatal	1	\N
366	battery_low_measurement_boolean_int8_1	battery_low_measurement	\N	Battery Low Measurement	1	\N
367	battery_low_bank_boolean_int8_1	battery_low_bank	\N	Battery Low Bank	1	\N
368	battery_low_external_boolean_int8_1	battery_low_external	\N	Battery Low External	1	\N
369	external_device1_fault_quantity_int8_1	external_device1_fault	\N	External Device Fault	1	\N
370	flash_erased_boolean_int8_1	flash_erased	\N	Flash Erased	1	\N
371	power_on_invalid_boolean_int8_1	power_on_invalid 	\N	Power On Invalid 	1	\N
372	launch_time_quantity_int64_seconds_since_1904_01_01	launch_time	\N	Launch Time, UTC	seconds since 1904-01-01	\N
373	start_time_offset_quantity_int32_s	start_time_offset	\N	Start Time Offset, s	s	\N
374	recording_time_quantity_int32_s	recording_time	\N	Recording Time, s	s	\N
375	pmi_sample_schedule_boolean_int8_1	pmi_sample_schedule	\N	PMI Sample Schedule	1	\N
376	sami_sample_schedule_boolean_int8_1	sami_sample_schedule	\N	SAMI Sample Schedule	1	\N
377	slot1_follows_sami_sample_boolean_int8_1	slot1_follows_sami_sample	\N	Slot1 Follows SAMI Sample	1	\N
378	slot1_independent_schedule_boolean_int8_1	slot1_independent_schedule	\N	Slot1 Independent Schedule	1	\N
379	slot2_follows_sami_sample_boolean_int8_1	slot2_follows_sami_sample	\N	Slot2 Follows SAMI Sample	1	\N
380	slot2_independent_schedule_boolean_int8_1	slot2_independent_schedule	\N	Slot2 Independent Schedule	1	\N
381	slot3_follows_sami_sample_boolean_int8_1	slot3_follows_sami_sample	\N	Slot3 Follows SAMI Sample	1	\N
382	slot3_independent_schedule_boolean_int8_1	slot3_independent_schedule	\N	Slot3 Independent Schedule	1	\N
383	timer_interval_sami_quantity_int32_s	timer_interval_sami	\N	Timer Interval SAMI, s	s	\N
384	driver_id_sami_quantity_int8_1	driver_id_sami	\N	Driver Id SAMI	1	\N
385	parameter_pointer_sami_quantity_int8_1	parameter_pointer_sami	\N	Parameter Pointer SAMI	1	\N
386	timer_interval_device1_quantity_int32_s	timer_interval_device1	\N	Timer Interval Device1, s	s	\N
387	driver_id_device1_quantity_int8_1	driver_id_device1	\N	Driver Id Device1	1	\N
388	parameter_pointer_device1_quantity_int8_1	parameter_pointer_device1	\N	Parameter Pointer Device1	1	\N
389	timer_interval_device2_quantity_int32_s	timer_interval_device2	\N	Timer Interval Device2, s	s	\N
390	driver_id_device2_quantity_int8_1	driver_id_device2	\N	Driver Id Device2	1	\N
391	parameter_pointer_device2_quantity_int8_1	parameter_pointer_device2	\N	Parameter Pointer Device2	1	\N
392	timer_interval_device3_quantity_int32_s	timer_interval_device3	\N	Timer Interval Device3, s	s	\N
393	driver_id_device3_quantity_int8_1	driver_id_device3	\N	Driver Id Device3	1	\N
394	parameter_pointer_device3_quantity_int8_1	parameter_pointer_device3	\N	Parameter Pointer Device3	1	\N
395	timer_interval_prestart_quantity_int32_s	timer_interval_prestart	\N	Timer Interval Prestart, s	s	\N
396	driver_id_prestart_quantity_int8_1	driver_id_prestart	\N	Driver Id Prestart	1	\N
397	parameter_pointer_prestart_quantity_int8_1	parameter_pointer_prestart	\N	Parameter Pointer Prestart	1	\N
398	use_baud_rate_57600_boolean_int8_1	use_baud_rate_57600	\N	Use Baud Rate 9600	1	\N
399	send_record_type_boolean_int8_1	send_record_type	\N	Send Record Type Early	1	\N
400	send_live_records_boolean_int8_1	send_live_records	\N	Send Live Records	1	\N
401	extend_global_config_boolean_int8_1	extend_global_config	\N	Extend Global Config	1	\N
402	pump_pulse_quantity_uint8_s	pump_pulse	\N	Pump Pulse, s	s	\N
403	pump_on_to_measure_quantity_uint8_s	pump_on_to_measure	\N	Pump On To Measure, s	s	\N
404	samples_per_measure_quantity_uint32_counts	samples_per_measure	\N	Samples Per Measure, counts	counts	\N
405	cycles_between_blanks_quantity_uint8_counts	cycles_between_blanks	\N	Cycles Between Blanks, counts	counts	\N
406	num_reagent_cycles_quantity_uint8_counts	num_reagent_cycles	\N	Num Reagent Cycles, counts	counts	\N
407	num_blank_cycles_quantity_uint8_counts	num_blank_cycles	\N	Num Blank Cycles, counts	counts	\N
408	flush_pump_interval_quantity_uint8_s	flush_pump_interval	\N	Flush Pump Interval, s	s	\N
409	disable_start_blank_flush_boolean_int8_1	disable_start_blank_flush	\N	Blank Flush On Start	1	\N
410	measure_after_pump_pulse_boolean_int8_1	measure_after_pump_pulse	\N	Pump Pulse Post Measure	1	\N
411	PD2929	VOID_num_extra_pump_cycles	\N	\N	counts	\N
412	VOID_cycle_interval_quantity_uint8_s	VOID_cycle_interval 	\N	\N	s	\N
413	resistivity_5_quantity_float32_V	resistivity_5	\N	Temperature Resistivity 1x gain, V	V	\N
414	resistivity_x1_quantity_float32_V	resistivity_x1	\N	Temperature Resistivity 5x gain, V	V	\N
415	resistivity_x5_quantity_float32_V	resistivity_x5	\N	Temperature Resistivity 25x gain, V	V	\N
416	hydrogen_5_quantity_float32_V	hydrogen_5	\N	Hydrogen Sensor 1x gain, V	V	\N
417	hydrogen_x1_quantity_float32_V	hydrogen_x1	\N	Hydrogen Sensor 5x gain, V	V	\N
418	hydrogen_x5_quantity_float32_V	hydrogen_x5	\N	Hydrogen Sensor 25x gain, V	V	\N
419	eh_sensor_quantity_float32_V	eh_sensor	\N	Raw Oxidation Reduction-Potential Voltage/Eh Sensor	V	\N
420	ref_temp_volts_quantity_float32_V	ref_temp_volts	\N	Reference Temp Volts     	V	\N
421	ref_temp_degc_quantity_float32_deg_C	ref_temp_degc	\N	Reference Temp Deg C     	deg_C	\N
422	resistivity_temp_volts_quantity_float32_V	resistivity_temp_volts	\N	Resistivity Temp Volts   	V	\N
423	resistivity_temp_degc_quantity_float32_deg_C	resistivity_temp_degc	\N	Resistivity Temp Deg C   	deg_C	\N
424	battery_voltage_quantity_float32_V	battery_voltage	\N	Battery Voltage  	V	\N
425	error_code_quantity_uint16_1	error_code	\N	Error Code	1	\N
426	analog1_quantity_uint16_1	analog1	\N	Analog 1	1	\N
427	sound_speed_analog2_quantity_float32_m_s_1	sound_speed_analog2	\N	Speed of Sound, m s-1	m s-1	\N
428	heading_quantity_float32_degrees	heading	\N	Instrument Heading, degrees	degrees	\N
429	roll_quantity_float32_degrees	roll	\N	Instrument Roll, degrees	degrees	\N
430	pitch_quantity_float32_degrees	pitch	\N	Instrument Pitch, degrees	degrees	\N
431	status_quantity_uint8_1	status	\N	Status	1	\N
432	temperature_quantity_float32_deg_C	temperature	\N	Temperature, deg_C	deg_C	\N
433	velocity_beam1_quantity_int16_mm_s_1	velocity_beam1	\N	Eastward Sea Velocity, mm s-1	mm s-1	\N
434	velocity_beam2_quantity_int16_mm_s_1	velocity_beam2	\N	Northward Sea Velocity, mm s-1	mm s-1	\N
435	velocity_beam3_quantity_int16_mm_s_1	velocity_beam3	\N	Upward Sea Velocity, mm s-1	mm s-1	\N
436	amplitude_beam1_quantity_uint8_counts	amplitude_beam1	\N	Amplitude, Beam 1, counts	counts	\N
437	amplitude_beam2_quantity_uint8_counts	amplitude_beam2	\N	Amplitude, Beam 2, counts	counts	\N
438	amplitude_beam3_quantity_uint8_counts	amplitude_beam3	\N	Amplitude, Beam 3, counts	counts	\N
439	records_to_follow_quantity_int16_1	records_to_follow	\N	Number of Records to Follow	1	\N
440	cell_number_diagnostics_quantity_int16_1	cell_number_diagnostics	\N	Cell Number Diagnostics	1	\N
441	noise_amplitude_beam1_quantity_int8_counts	noise_amplitude_beam1	\N	Noise Amplitude, Beam 1, counts	counts	\N
442	noise_amplitude_beam2_quantity_int8_counts	noise_amplitude_beam2	\N	Noise Amplitude, Beam 2, counts	counts	\N
443	noise_amplitude_beam3_quantity_int8_counts	noise_amplitude_beam3	\N	Noise Amplitude, Beam 3, counts	counts	\N
444	noise_amplitude_beam4_quantity_int8_counts	noise_amplitude_beam4	\N	Noise Amplitude, Beam 4, counts	counts	\N
445	processing_magnitude_beam1_quantity_int16_1	processing_magnitude_beam1	\N	Processing Magnitude, Beam 1	1	\N
446	processing_magnitude_beam2_quantity_int16_1	processing_magnitude_beam2	\N	Processing Magnitude, Beam 2	1	\N
447	processing_magnitude_beam3_quantity_int16_1	processing_magnitude_beam3	\N	Processing Magnitude, Beam 3	1	\N
448	processing_magnitude_beam4_quantity_int16_1	processing_magnitude_beam4	\N	Processing Magnitude, Beam 4	1	\N
449	distance_beam1_quantity_int16_1	distance_beam1	\N	Distance, Beam 1	1	\N
450	distance_beam2_quantity_int16_1	distance_beam2	\N	Distance, Beam 2	1	\N
451	distance_beam3_quantity_int16_1	distance_beam3	\N	Distance, Beam 3	1	\N
452	distance_beam4_quantity_int16_1	distance_beam4	\N	Distance, Beam 4	1	\N
453	instrmt_type_serial_number_quantity_string_1	instrmt_type_serial_number	\N	Instrument Type and Serial Number	1	\N
454	recorder_installed_boolean_int8_1	recorder_installed	\N	Recorder Installed	1	\N
455	compass_installed_boolean_int8_1	compass_installed	\N	Compass Installed	1	\N
456	board_frequency_quantity_int32_kHz	board_frequency	\N	Board Frequency KHz	kHz	\N
457	pic_version_quantity_int16_1	pic_version	\N	PIC Code Version Number	1	\N
458	hardware_revision_quantity_int16_1	hardware_revision	\N	Hardware Revision	1	\N
459	recorder_size_quantity_int32_bytes	recorder_size	\N	Recorder size (*65536 bytes)	bytes	\N
460	velocity_range_category_int8_str_int8_1	velocity_range	\N	Velocity Range	1	\N
461	pressure_sensor_boolean_int8_1	pressure_sensor	\N	Pressure Sensor	1	\N
462	magnetometer_sensor_boolean_int8_1	magnetometer_sensor	\N	Magnetometer Sensor	1	\N
463	tilt_sensor_boolean_int8_1	tilt_sensor	\N	Tilt Sensor	1	\N
464	tilt_sensor_mounting_category_int8_str_int8_1	tilt_sensor_mounting	\N	Tilt Sensor Mounting	1	\N
465	head_frequency_quantity_int16_kHz	head_frequency	\N	Head Frequency, KHz	kHz	\N
466	head_type_quantity_int16_1	head_type	\N	Head Type	1	\N
467	head_serial_number_quantity_string_1	head_serial_number	\N	Head Serial Number	1	\N
468	system_data_quantity_string_1	system_data	\N	System Data	1	\N
469	number_beams_quantity_int16_1	number_beams	\N	Number Beams	1	\N
470	transmit_pulse_length_quantity_uint16_counts	transmit_pulse_length	\N	Transmit Pulse Length, counts	counts	\N
471	blanking_distance_quantity_uint16_counts	blanking_distance	\N	Blanking Distance, counts	counts	\N
472	receive_length_quantity_uint16_counts	receive_length	\N	Receive Length, counts	counts	\N
473	time_between_pings_quantity_uint16_counts	time_between_pings	\N	Time Between Pings, counts	counts	\N
474	time_between_bursts_quantity_uint16_counts	time_between_bursts	\N	Time Between Bursts, counts	counts	\N
475	number_pings_quantity_int16_1	number_pings	\N	Number of Pings	1	\N
476	average_interval_quantity_int16_s	average_interval	\N	Average Interval, sec	s	\N
477	profile_type_category_int8_str_int8_1	profile_type	\N	Profile Type	1	\N
478	mode_type_category_int8_str_int8_1	mode_type	\N	Mode Type	1	\N
479	power_level_tcm1_quantity_int8_1	power_level_tcm1	\N	Power Level Tcm1	1	\N
480	power_level_tcm2_quantity_int8_1	power_level_tcm2	\N	Power Level Tcm2	1	\N
481	sync_out_position_category_int8_str_int8_1	sync_out_position	\N	Sync Out Position	1	\N
482	sample_on_sync_category_int8_str_int8_1	sample_on_sync	\N	Sample On Sync	1	\N
483	start_on_sync_category_int8_str_int8_1	start_on_sync	\N	Start On Sync	1	\N
484	power_level_pcr1_quantity_int8_1	power_level_pcr1	\N	Power Level Pcr1	1	\N
485	power_level_pcr2_quantity_int8_1	power_level_pcr2	\N	Power Level Pcr2	1	\N
486	compass_update_rate_quantity_int16_Hz	compass_update_rate	\N	Compass Update Rate, Hz	Hz	\N
487	coordinate_system_category_int8_str_int8_1	coordinate_system	\N	Coordinate System	1	\N
488	number_cells_quantity_int16_1	number_cells	\N	Number Cells	1	\N
489	cell_size_quantity_int16_m	cell_size	\N	Cell Size, m	m	\N
490	measurement_interval_quantity_int16_s	measurement_interval	\N	Measurement Interval, sec	s	\N
491	deployment_name_quantity_string_1	deployment_name	\N	Deployment Name	1	\N
492	wrap_mode_quantity_int16_1	wrap_mode	\N	Wrap Mode	1	\N
493	deployment_start_time_array_quantity_int8_1	deployment_start_time	\N	Deployment Start Time	1	\N
494	diagnostics_interval_quantity_int32_s	diagnostics_interval	\N	Diagnostics Interval, s	s	\N
495	use_specified_sound_speed_boolean_int8_1	use_specified_sound_speed	\N	Use Specified Sound Speed	1	\N
496	diagnostics_mode_enable_boolean_int8_1	diagnostics_mode_enable	\N	Diagnostics Mode Enable	1	\N
497	analog_output_enable_boolean_int8_1	analog_output_enable	\N	Analog Output Enable	1	\N
498	output_format_nortek_category_int8_str_int8_1	output_format_nortek	\N	Output Format Nortek	1	\N
499	scaling_category_int8_str_int8_1	scaling	\N	Scaling	1	\N
500	serial_output_enable_boolean_int8_1	serial_output_enable	\N	Serial Output Enable	1	\N
501	stage_enable_boolean_int8_1	stage_enable	\N	Stage Enable	1	\N
502	analog_power_output_boolean_int8_1	analog_power_output	\N	Analog Power Output	1	\N
503	sound_speed_adjust_factor_quantity_int16_m_s_1	sound_speed_adjust_factor	\N	Sound Speed Adjust Factor, m/s	m s-1	\N
504	number_diagnostics_samples_quantity_int16_1	number_diagnostics_samples	\N	Number Diagnostics Samples	1	\N
505	number_beams_per_cell_quantity_int16_1	number_beams_per_cell	\N	Number Beams Per Cell	1	\N
506	number_pings_diagnostic_quantity_int16_1	number_pings_diagnostic	\N	Number Pings Diagnostic	1	\N
507	use_dsp_filter_boolean_int8_1	use_dsp_filter	\N	Use Dsp Filter	1	\N
508	filter_data_output_category_int8_str_int8_1	filter_data_output	\N	Filter Data Output	1	\N
509	analog_input_address_quantity_int16_1	analog_input_address	\N	Analog Input Address	1	\N
510	software_version_quantity_int16_1	software_version	\N	Software Version	1	\N
511	velocity_adjustment_factor_quantity_string_1	velocity_adjustment_factor	\N	Velocity Adjustment Factor	1	\N
512	file_comments_quantity_string_1	file_comments	\N	File Comments	1	\N
513	wave_data_rate_category_int8_str_int8_Hz	wave_data_rate	\N	Wave Data Rate, Hz	Hz	\N
514	wave_cell_position_category_int8_str_int8_1	wave_cell_position	\N	Wave Cell Position	1	\N
515	dynamic_position_type_category_int8_str_int8_1	dynamic_position_type	\N	Dynamic Position Type	1	\N
516	percent_wave_cell_position_quantity_int32_1	percent_wave_cell_position	\N	Percent Wave Cell Position	1	\N
517	wave_transmit_pulse_quantity_int16_1	wave_transmit_pulse	\N	Wave Transmit Pulse	1	\N
518	fixed_wave_blanking_distance_quantity_uint16_counts	fixed_wave_blanking_distance	\N	Fixed Wave Blanking Distance, counts	counts	\N
519	wave_measurement_cell_size_quantity_uint16_m	wave_measurement_cell_size	\N	Wave Measurement Cell Size, m	m	\N
520	number_diagnostics_per_wave_quantity_uint16_1	number_diagnostics_per_wave	\N	Number Diagnostics Per Wave	1	\N
521	number_samples_per_burst_quantity_uint16_1	number_samples_per_burst	\N	Number Samples Per Burst	1	\N
522	analog_scale_factor_quantity_uint16_1	analog_scale_factor	\N	Analog Scale Factor	1	\N
523	correlation_threshold_quantity_int16_1	correlation_threshold	\N	Correlation Threshold	1	\N
524	filter_constants_quantity_string_1	filter_constants	\N	Filter Constants	1	\N
525	velocity_beam_a_quantity_int32_counts	velocity_beam_a	\N	MAVS Velocity Beam A, counts	counts	\N
526	velocity_beam_b_quantity_int32_counts	velocity_beam_b	\N	MAVS Velocity Beam B, counts	counts	\N
527	velocity_beam_c_quantity_int32_counts	velocity_beam_c	\N	MAVS Velocity Beam C, counts	counts	\N
528	velocity_beam_d_quantity_int32_counts	velocity_beam_d	\N	MAVS Velocity Beam D, counts	counts	\N
529	turbulent_velocity_east_quantity_float32_cm_s_1	turbulent_velocity_east	\N	Eastward Turbulent Sea Water velocity, cm s-1	cm s-1	\N
530	turbulent_velocity_north_quantity_float32_cm_s_1	turbulent_velocity_north	\N	Northward Turbulent Sea Water Velocity, cm s-1	cm s-1	\N
531	turbulent_velocity_up_quantity_float32_cm_s_1	turbulent_velocity_up	\N	Vertical Turbulent Sea Water Velocity, cm s-1	cm s-1	\N
532	mag_comp_x_quantity_float32_1	mag_comp_x	\N	Normalized Magnetic X Component	1	\N
533	mag_comp_y_quantity_float32_1	mag_comp_y	\N	Normalized Magnetic Y Component	1	\N
534	velocity_offsets_array_quantity_float32_cm_s_1	velocity_offsets	\N	Velocity Conversion Offsets, cm s-1	cm s-1	\N
535	compass_offsets_array_quantity_int32_1	compass_offsets	\N	Compass Conversion Offsets	1	\N
536	compass_scale_factor_array_quantity_float32_1	compass_scale_factor	\N	Compass Conversion Scale Factor	1	\N
537	tilt_offsets_array_quantity_int16_1	tilt_offsets	\N	Tilt Conversion Offsets	1	\N
538	thermistor_calibration_quantity_float32_deg_C	thermistor_calibration	\N	Themistor Calibration, deg C	deg_C	\N
539	sample_period_quantity_float32_s	sample_period	\N	Sample Period, s	s	\N
540	samples_per_burst_quantity_int32_counts	samples_per_burst	\N	Samples per Burst	counts	\N
541	burst_interval_quantity_string_1	burst_interval	\N	Burst Interval	1	\N
542	bin_to_si_conversion_quantity_float32_1	bin_to_si_conversion	\N	Binary to SI Conversion Factor	1	\N
543	analog_input_2_quantity_uint16_1	analog_input_2	\N	Analog Input 2	1	\N
544	ensemble_counter_quantity_int16_1	ensemble_counter	\N	Ensemble Counter	1	\N
545	seawater_pressure_quantity_float32_dbar	seawater_pressure	\N	Seawater Pressure, dbar	dbar	\N
546	analog_input_1_quantity_uint16_1	analog_input_1	\N	Analog Input 1	1	\N
547	turbulent_velocity_east_quantity_int16_mm_s_1	turbulent_velocity_east	\N	Velocity beam1 or X or East (mm/s)	mm s-1	\N
548	turbulent_velocity_north_quantity_int16_mm_s_1	turbulent_velocity_north	\N	Velocity beam2 or Y or North (mm/s)	mm s-1	\N
549	turbulent_velocity_vertical_quantity_int16_mm_s_1	turbulent_velocity_vertical	\N	Velocity beam3 or Z or Up (mm/s)	mm s-1	\N
550	amplitude_beam_1_quantity_int16_counts	amplitude_beam_1	\N	Beam 1 Amplitude, Counts	counts	\N
551	amplitude_beam_2_quantity_int16_counts	amplitude_beam_2	\N	Beam 2 Amplitude, Counts	counts	\N
552	amplitude_beam_3_quantity_int16_counts	amplitude_beam_3	\N	Beam 3 Amplitude, Counts	counts	\N
553	correlation_beam_1_quantity_int16_1	correlation_beam_1	\N	Beam 1 Correlation, Percentage	1	\N
554	correlation_beam_2_quantity_int16_1	correlation_beam_2	\N	Beam 2 Correlation, Percentage	1	\N
555	correlation_beam_3_quantity_int16_1	correlation_beam_3	\N	Beam 3 Correlation, Percentage	1	\N
556	speed_of_sound_quantity_float32_m_s_1	speed_of_sound	\N	Speed of Sound, m s-1	m s-1	\N
557	VOID_heading_quantity_float32_degrees	VOID_heading	\N	VOID Heading, Degrees	degrees	\N
558	VOID_pitch_quantity_float32_degrees	VOID_pitch	\N	VOID Pitch, Degrees	degrees	\N
559	VOID_roll_quantity_float32_degrees	VOID_roll	\N	VOID Roll, Degrees	degrees	\N
560	error_code_quantity_uint8_1	error_code	\N	Error Code	1	\N
561	status_code_quantity_uint8_1	status_code	\N	Status Code	1	\N
562	analog_input_quantity_uint16_1	analog_input	\N	Analog Input	1	\N
563	number_velocity_records_quantity_uint16_1	number_velocity_records	\N	Number of Velocity Records	1	\N
564	noise_amp_beam1_quantity_int16_counts	noise_amp_beam1	\N	Beam 1 Noise Amplitude, Counts	counts	\N
565	noise_amp_beam2_quantity_int16_counts	noise_amp_beam2	\N	Beam 2 Noise Amplitude, Counts	counts	\N
566	noise_amp_beam3_quantity_int16_counts	noise_amp_beam3	\N	Beam 3 Noise Amplitude, Counts	counts	\N
567	noise_correlation_beam1_quantity_int16_1	noise_correlation_beam1	\N	Beam 1 Noise Correlation, Percentage	1	\N
568	noise_correlation_beam2_quantity_int16_1	noise_correlation_beam2	\N	Beam 2 Noise Correlation, Percentage	1	\N
569	noise_correlation_beam3_quantity_int16_1	noise_correlation_beam3	\N	Beam 3 Noise Correlation, Percentage	1	\N
570	record_length_quantity_uint16_1	record_length	\N	Record Length	1	\N
571	packet_type_quantity_uint8_1	packet_type	\N	Packet Type	1	\N
572	meter_type_quantity_uint8_1	meter_type	\N	Meter Type	1	\N
573	a_reference_dark_counts_quantity_uint16_counts	a_reference_dark_counts	\N	Absorption Dark Reference, counts	counts	\N
574	pressure_counts_quantity_uint16_counts	pressure_counts	\N	Pressure, counts	counts	\N
575	a_signal_dark_counts_quantity_uint16_counts	a_signal_dark_counts	\N	Absorption Dark Signal, counts	counts	\N
576	external_temp_raw_quantity_uint16_counts	external_temp_raw	\N	Raw External Temperature, counts	counts	\N
577	internal_temp_raw_quantity_uint16_counts	internal_temp_raw	\N	Raw Internal Temperature, counts	counts	\N
578	c_reference_dark_counts_quantity_uint16_counts	c_reference_dark_counts	\N	Attenuation Dark Reference, counts	counts	\N
579	c_signal_dark_counts_quantity_uint16_counts	c_signal_dark_counts	\N	Attenuation Dark Signal, counts	counts	\N
580	elapsed_run_time_quantity_uint32_ms	elapsed_run_time	\N	Elapsed Run Time, ms	ms	\N
581	num_wavelengths_quantity_uint8_1	num_wavelengths	\N	Number of Wavelengths	1	\N
582	c_reference_counts_array_quantity_uint16_counts	c_reference_counts	\N	Reference Beam Attenuation, counts	counts	\N
583	a_reference_counts_array_quantity_uint16_counts	a_reference_counts	\N	Reference Absorption, counts	counts	\N
584	c_signal_counts_array_quantity_uint16_counts	c_signal_counts	\N	Signal Beam Attenuation, counts	counts	\N
585	a_signal_counts_array_quantity_uint16_counts_	a_signal_counts 	\N	Signal Absorption, counts	counts 	\N
586	persistor_cf_serial_number_quantity_string_1	persistor_cf_serial_number	\N	Persistor, CF Card Serial Number	1	\N
587	persistor_cf_bios_version_quantity_string_1	persistor_cf_bios_version	\N	Persistor, Bios Version	1	\N
588	persistor_cf_picodos_version_quantity_string_1	persistor_cf_picodos_version 	\N	Persistor, Picodos Version 	1	\N
589	temperature_array_quantity_float32_deg_C	temperature	\N	Temperature Array in Spatial Grid, deg C	deg_C	\N
590	tmpsf_cal_coeffs_array_quantity_float64_1	tmpsf_cal_coeffs	\N	TMPSF Calibration Coefficient Array	1	\N
591	header_id_quantity_uint8_1	header_id	\N	Header ID	1	\N
592	data_source_id_quantity_uint8_1	data_source_id	\N	Data Source ID	1	\N
593	num_bytes_quantity_uint16_1	num_bytes	\N	Number of Bytes	1	\N
594	num_data_types_quantity_uint16_1	num_data_types	\N	Number of Data Types	1	\N
595	offset_data_types_array_quantity_uint16_1	offset_data_types	\N	Offset Data Types	1	\N
596	fixed_leader_id_quantity_uint16_1	fixed_leader_id	\N	Fixed Leader ID	1	\N
597	firmware_version_quantity_uint8_1	firmware_version	\N	Firmware Version	1	\N
598	firmware_revision_quantity_uint8_1	firmware_revision	\N	Firmware Revision	1	\N
599	sysconfig_frequency_quantity_uint16_kHz	sysconfig_frequency	\N	Sysconfig Frequency, kHz	kHz	\N
600	sysconfig_beam_pattern_category_int8_str_int8_1	sysconfig_beam_pattern	\N	Sysconfig Beam Pattern	1	\N
601	sysconfig_sensor_config_quantity_uint8_1	sysconfig_sensor_config	\N	Sysconfig Sensor Config	1	\N
602	sysconfig_head_attached_boolean_int8_1	sysconfig_head_attached	\N	Sysconfig Head Attached	1	\N
603	sysconfig_vertical_orientation_category_int8_str_int8_1	sysconfig_vertical_orientation	\N	Sysconfig Vertical Orientation	1	\N
604	data_flag_quantity_uint8_1	data_flag	\N	Real/Simulated Data Flag	1	\N
605	lag_length_quantity_uint8_s	lag_length	\N	Lag Length, seconds	s	\N
606	num_beams_quantity_uint8_1	num_beams	\N	Number Beams	1	\N
607	num_cells_quantity_uint8_1	num_cells	\N	Number Cells	1	\N
608	pings_per_ensemble_quantity_uint16_1	pings_per_ensemble	\N	Pings Per Ensemble	1	\N
609	cell_length_quantity_uint16_cm	cell_length	\N	Cell Length, cm	cm	\N
610	blank_after_transmit_quantity_uint16_cm	blank_after_transmit	\N	Blank After Transmit Distance, cm	cm	\N
611	signal_processing_mode_quantity_uint8_1	signal_processing_mode	\N	Signal Processing Mode	1	\N
612	low_corr_threshold_quantity_uint8_counts	low_corr_threshold	\N	Low Correlation Threshold	counts	\N
613	num_code_repetitions_quantity_uint8_counts	num_code_repetitions	\N	Number of Code Repetitions	counts	\N
614	percent_good_min_quantity_uint8_percent	percent_good_min	\N	Percent Good Minimum	percent	\N
615	error_vel_threshold_quantity_uint16_mm_s_1	error_vel_threshold	\N	Error Velocity Threshold, mm s-1	mm s-1	\N
616	time_per_ping_minutes_quantity_uint8_min	time_per_ping_minutes	\N	Time Per Ping, minutes	min	\N
617	time_per_ping_seconds_quantity_float32_s	time_per_ping_seconds	\N	Time Per Ping, seconds	s	\N
618	coord_transform_type_quantity_uint8_1	coord_transform_type	\N	Coordinate Transform Type	1	\N
619	coord_transform_tilts_boolean_int8_1	coord_transform_tilts	\N	Coordinate Transform Tilts Boolean	1	\N
620	coord_transform_beams_boolean_int8_1	coord_transform_beams	\N	Coord Transform Beams Boolean	1	\N
621	coord_transform_mapping_boolean_int8_1	coord_transform_mapping	\N	Coord Transform Mapping	1	\N
622	heading_alignment_quantity_int16_cdegrees	heading_alignment	\N	Heading Alignment, cdegrees	cdegrees	\N
623	heading_bias_quantity_int16_cdegrees	heading_bias	\N	Heading Bias, cdegrees	cdegrees	\N
624	sensor_source_speed_boolean_int8_1	sensor_source_speed	\N	Sensor Source Speed	1	\N
625	sensor_source_depth_boolean_int8_1	sensor_source_depth	\N	Sensor Source Depth	1	\N
626	sensor_source_heading_boolean_int8_1	sensor_source_heading	\N	Sensor Source Heading	1	\N
627	sensor_source_pitch_boolean_int8_1	sensor_source_pitch	\N	Sensor Source Pitch	1	\N
628	sensor_source_roll_boolean_int8_1	sensor_source_roll	\N	Sensor Source Roll	1	\N
629	sensor_source_conductivity_boolean_int8_1	sensor_source_conductivity	\N	Sensor Source Conductivity	1	\N
630	sensor_source_temperature_boolean_int8_1	sensor_source_temperature	\N	Sensor Source Temperature	1	\N
631	sensor_available_depth_boolean_int8_1	sensor_available_depth	\N	Sensor Available Depth	1	\N
632	sensor_available_heading_boolean_int8_1	sensor_available_heading	\N	Sensor Available Heading	1	\N
633	sensor_available_pitch_boolean_int8_1	sensor_available_pitch	\N	Sensor Available Pitch	1	\N
634	sensor_available_roll_boolean_int8_1	sensor_available_roll	\N	Sensor Available Roll	1	\N
635	sensor_available_conductivity_boolean_int8_1	sensor_available_conductivity	\N	Sensor Available Conductivity	1	\N
636	sensor_available_temperature_boolean_int8_1	sensor_available_temperature	\N	Sensor Available Temperature	1	\N
637	bin_1_distance_quantity_uint16_cm	bin_1_distance	\N	Bin 1 Distance, cm	cm	\N
638	transmit_pulse_length_quantity_uint16_cm	transmit_pulse_length	\N	Transmit Pulse Length, cm	cm	\N
639	reference_layer_start_quantity_uint8_1	reference_layer_start	\N	Reference Layer Start	1	\N
640	reference_layer_stop_quantity_uint8_1	reference_layer_stop	\N	Reference Layer Stop	1	\N
641	false_target_threshold_quantity_uint8_counts	false_target_threshold	\N	False Target Threshold	counts	\N
642	low_latency_trigger_boolean_int8_1	low_latency_trigger	\N	Low Latency Trigger	1	\N
643	transmit_lag_distance_quantity_uint16_cm	transmit_lag_distance	\N	Transmit Lag Distance, cm	cm	\N
644	cpu_board_serial_number_quantity_string_1	cpu_board_serial_number	\N	CPU Board Serial Number	1	\N
645	system_bandwidth_quantity_uint8_1	system_bandwidth	\N	System Bandwidth	1	\N
646	system_power_quantity_uint16_1	system_power	\N	System Power	1	\N
647	beam_angle_quantity_uint8_degrees	beam_angle	\N	Beam Angle, degrees	degrees	\N
648	variable_leader_id_quantity_uint16_1	variable_leader_id	\N	Variable Leader ID	1	\N
649	ensemble_number_quantity_uint16_1	ensemble_number	\N	Ensemble Number	1	\N
650	ensemble_number_increment_quantity_uint8_1	ensemble_number_increment	\N	Ensemble Number Increment	1	\N
651	bit_result_demod_1_boolean_int8_1	bit_result_demod_1	\N	BIT Result, Demod 1	1	\N
652	bit_result_demod_0_boolean_int8_1	bit_result_demod_0	\N	BIT Result, Demod 0	1	\N
653	bit_result_timing_boolean_int8_1	bit_result_timing	\N	BIT Result, Timing	1	\N
654	speed_of_sound_quantity_uint16_m_s_1	speed_of_sound	\N	Speed Of Sound, m s-1	m s-1	\N
655	transducer_depth_quantity_uint16_dm	transducer_depth	\N	Transducer Depth, dm	dm	\N
656	heading_quantity_uint16_cdegrees	heading	\N	Heading, cdegrees	cdegrees	\N
657	pitch_quantity_int16_cdegrees	pitch	\N	Pitch, cdegrees	cdegrees	\N
658	roll_quantity_int16_cdegrees	roll	\N	Roll, cdegrees	cdegrees	\N
659	salinity_quantity_uint16_1	salinity	\N	Salinity	1	\N
660	temperature_quantity_int16_cdeg_C	temperature	\N	Temperature, cdeg C	cdeg_C	\N
661	mpt_minutes_quantity_uint8_min	mpt_minutes	\N	MPT, min	min	\N
662	mpt_seconds_quantity_float32_s	mpt_seconds	\N	MPT, sec	s	\N
663	heading_stdev_quantity_uint8_degrees	heading_stdev	\N	Heading Standard Deviation, degrees	degrees	\N
664	pitch_stdev_quantity_uint8_ddegrees	pitch_stdev	\N	Pitch Standard Deviation, ddegrees	ddegrees	\N
665	roll_stdev_quantity_uint8_ddegrees	roll_stdev	\N	Roll Standard Deviation, ddegrees	ddegrees	\N
666	adc_transmit_current_quantity_uint8_counts	adc_transmit_current	\N	ADC Transmit Current	counts	\N
667	adc_transmit_voltage_quantity_uint8_counts	adc_transmit_voltage	\N	ADC Transmit Voltage	counts	\N
668	adc_ambient_temp_quantity_uint8_counts	adc_ambient_temp	\N	ADC Ambient Temperature	counts	\N
669	adc_pressure_plus_quantity_uint16_counts	adc_pressure_plus	\N	ADC Pressure Plus	counts	\N
670	adc_pressure_minus_quantity_uint16_counts	adc_pressure_minus	\N	ADC Pressure Minus	counts	\N
671	adc_attitude_temp_quantity_uint8_counts	adc_attitude_temp	\N	ADC Attitude Temperature	counts	\N
672	adc_attitude_quantity_uint8_counts	adc_attitude	\N	ADC Attitiude	counts	\N
673	adc_contamination_sensor_quantity_uint8_counts	adc_contamination_sensor	\N	ADC Contamination Sensor	counts	\N
674	bus_error_exception_boolean_int8_1	bus_error_exception	\N	Bus Error Exception	1	\N
675	address_error_exception_boolean_int8_1	address_error_exception	\N	Address Error Exception	1	\N
676	illegal_instruction_exception_boolean_int8_1	illegal_instruction_exception	\N	Illegal Instruction Exception	1	\N
677	zero_divide_instruction_boolean_int8_1	zero_divide_instruction	\N	Zero Divide Instruction	1	\N
678	emulator_exception_boolean_int8_1	emulator_exception	\N	Emulator Exception	1	\N
679	unassigned_exception_boolean_int8_1	unassigned_exception	\N	Unassigned Exception	1	\N
680	watchdog_restart_occurred_boolean_int8_1	watchdog_restart_occurred	\N	Watchdog Restart Occurred	1	\N
681	battery_saver_power_boolean_int8_1	battery_saver_power	\N	Battery Saver Power	1	\N
682	pinging_boolean_int8_1	pinging	\N	Pinging	1	\N
683	cold_wakeup_occurred_boolean_int8_1	cold_wakeup_occurred	\N	Cold Wakeup Occurred	1	\N
684	unknown_wakeup_occurred_boolean_int8_1	unknown_wakeup_occurred	\N	Unknown Wakeup Occurred	1	\N
685	clock_read_error_boolean_int8_1	clock_read_error	\N	Clock Read Error	1	\N
686	unexpected_alarm_boolean_int8_1	unexpected_alarm	\N	Unexpected Alarm	1	\N
687	clock_jump_forward_boolean_int8_1	clock_jump_forward	\N	Clock Jump Forward	1	\N
688	clock_jump_backward_boolean_int8_1	clock_jump_backward	\N	Clock Jump Backward	1	\N
689	power_fail_boolean_int8_1	power_fail	\N	Power Fail	1	\N
690	spurious_dsp_interrupt_boolean_int8_1	spurious_dsp_interrupt	\N	Spurious DSP Interrupt	1	\N
691	spurious_uart_interrupt_boolean_int8_1	spurious_uart_interrupt	\N	Spurious UART Interrupt	1	\N
692	spurious_clock_interrupt_boolean_int8_1	spurious_clock_interrupt	\N	Spurious Clock Interrupt	1	\N
693	level_7_interrupt_boolean_int8_1	level_7_interrupt	\N	Level 7 Interrupt	1	\N
694	pressure_quantity_uint32_daPa	pressure	\N	Pressure, daPa	daPa	\N
695	pressure_variance_quantity_uint32_daPa	pressure_variance	\N	Pressure Variance, daPa	daPa	\N
696	velocity_data_id_quantity_uint16_1	velocity_data_id	\N	Velocity Data ID	1	\N
697	water_velocity_east_array_quantity_int16_mm_s_1	water_velocity_east	\N	Eastward Sea Water Velocity, mm s-1	mm s-1	\N
698	water_velocity_north_array_quantity_int16_mm_s_1	water_velocity_north	\N	Northward Sea Water Velocity, mm s-1	mm s-1	\N
699	water_velocity_up_array_quantity_int16_mm_s_1	water_velocity_up	\N	Upward Sea Water Velocity, mm s-1	mm s-1	\N
700	error_velocity_array_quantity_int16_mm_s_1	error_velocity	\N	Error Velocity, mm s-1	mm s-1	\N
701	correlation_magnitude_id_quantity_uint16_1	correlation_magnitude_id	\N	Correlation Magnitude ID	1	\N
702	correlation_magnitude_beam1_array_quantity_uint8_1	correlation_magnitude_beam1	\N	Correlation Magnitude Beam1	1	\N
703	correlation_magnitude_beam2_array_quantity_uint8_1	correlation_magnitude_beam2	\N	Correlation Magnitude Beam2	1	\N
704	correlation_magnitude_beam3_array_quantity_uint8_1	correlation_magnitude_beam3	\N	Correlation Magnitude Beam3	1	\N
705	correlation_magnitude_beam4_array_quantity_uint8_1	correlation_magnitude_beam4	\N	Correlation Magnitude Beam4	1	\N
706	echo_intensity_id_quantity_uint16_1	echo_intensity_id	\N	Echo Intensity ID	1	\N
707	echo_intensity_beam1_array_quantity_uint8_counts	echo_intensity_beam1	\N	Beam #1 Echo Intensity	counts	\N
708	echo_intensity_beam2_array_quantity_uint8_counts	echo_intensity_beam2	\N	Beam #2 Echo Intensity	counts	\N
709	echo_intensity_beam3_array_quantity_uint8_counts	echo_intensity_beam3	\N	Beam #3 Echo Intensity	counts	\N
710	echo_intensity_beam4_array_quantity_uint8_counts	echo_intensity_beam4	\N	Beam #4 Echo Intensity	counts	\N
711	percent_good_id_quantity_uint16_1	percent_good_id	\N	Percent Good ID	1	\N
712	percent_good_3beam_array_quantity_uint8_percent	percent_good_3beam	\N	Percent Good 3Beam	percent	\N
713	percent_transforms_reject_array_quantity_uint8_percent	percent_transforms_reject	\N	Percent Transforms Reject	percent	\N
714	percent_bad_beams_array_quantity_uint8_percent	percent_bad_beams	\N	Percent Bad Beams	percent	\N
715	percent_good_4beam_array_quantity_uint8_percent	percent_good_4beam	\N	Percent Good 4Beam	percent	\N
716	checksum_quantity_uint16_1	checksum	\N	Checksum	1	\N
717	wave_header_id_quantity_uint16_1	wave_header_id	\N	Wave Header ID	1	\N
718	checksum_offset_quantity_uint16_1	checksum_offset	\N	Checksum Offset	1	\N
719	offset_data_types_quantity_uint16_1	offset_data_types	\N	Offset Data Types	1	\N
720	first_leader_id_quantity_uint16_1	first_leader_id	\N	First Leader ID	1	\N
721	firmware_version_quantity_uint16_1	firmware_version	\N	Firmware Version	1	\N
722	configuration_quantity_uint16_1	configuration	\N	Configuration	1	\N
723	num_bins_quantity_uint16_1	num_bins	\N	Number of Bins	1	\N
724	samples_per_burst_quantity_uint16_1	samples_per_burst	\N	Samples Per Burst	1	\N
725	bin_length_quantity_uint8_cm	bin_length	\N	Bin Length	cm	\N
726	time_between_pings_quantity_uint16_cs	time_between_pings	\N	Time Between Pings, cs	cs	\N
727	time_between_bursts_quantity_uint16_s	time_between_bursts	\N	Time Between Bursts, s	s	\N
728	num_bins_out_quantity_uint8_1	num_bins_out	\N	Number Bins Out	1	\N
729	dws_bitmap_array_quantity_uint8_1	dws_bitmap	\N	DWS Bitmap	1	\N
730	velocity_bitmap_array_quantity_uint8_1	velocity_bitmap	\N	Velocity Bitmap	1	\N
731	burst_start_time_quantity_float64_seconds_since_1900_01_01	burst_start_time	\N	Burst Start Time, UTC	seconds since 1900-01-01	\N
732	burst_number_quantity_uint32_1	burst_number	\N	Burst Number	1	\N
733	wave_ping_id_quantity_uint16_1	wave_ping_id	\N	Wave Ping ID	1	\N
734	sample_number_quantity_uint16_1	sample_number	\N	Sample Number	1	\N
735	elapsed_time_quantity_uint32_cs	elapsed_time	\N	Elapsed Time, cs	cs	\N
736	VOID_pressure_quantity_uint32_daPa	VOID_pressure	\N	Void Pressure, daPa	daPa	\N
737	distance_surface_array_quantity_int32_mm	distance_surface	\N	Distance Surface, mm	mm	\N
738	beam_radial_velocity_array_quantity_int16_mm_s_1	beam_radial_velocity	\N	Beam Radial Velocity, mm s-1	mm s-1	\N
739	hpr_ping_id_quantity_uint16_1	hpr_ping_id	\N	HPR Ping ID	1	\N
740	VOID_heading_quantity_uint16_cdegrees	VOID_heading	\N	\N	cdegrees	\N
741	VOID_pitch_quantity_int16_cdegrees	VOID_pitch	\N	\N	cdegrees	\N
742	VOID_roll_quantity_int16_cdegrees	VOID_roll	\N	\N	cdegrees	\N
743	last_leader_id_quantity_uint16_1	last_leader_id	\N	Last Leader ID	1	\N
744	avg_depth_quantity_uint16_dm	avg_depth	\N	Avg Depth, dm	dm	\N
745	avg_speed_of_sound_quantity_uint16_m_s_1	avg_speed_of_sound	\N	Avg Speed Of Sound, m s-1	m s-1	\N
746	avg_temperature_quantity_uint16_cdeg_C	avg_temperature	\N	Avg Temperature, cdeg C	cdeg_C	\N
747	avg_heading_quantity_uint16_cdegrees	avg_heading	\N	Avg Heading, cdegrees	cdegrees	\N
748	stdev_heading_quantity_int16_cdegrees	stdev_heading	\N	Heading Standard Deviation, cdegrees	cdegrees	\N
749	avg_pitch_quantity_int16_cdegrees	avg_pitch	\N	Avg Pitch, cdegrees	cdegrees	\N
750	stdev_pitch_quantity_int16_cdegrees	stdev_pitch	\N	Pitch Standard Deviation, cdegrees	cdegrees	\N
751	avg_roll_quantity_int16_cdegrees	avg_roll	\N	Avg Roll, cdegrees	cdegrees	\N
752	stdev_roll_quantity_int16_cdegrees	stdev_roll	\N	Roll Standard Deviation, cdegrees	cdegrees	\N
753	pd12_packet_id_quantity_uint16_1	pd12_packet_id	\N	PD12 Packet ID	1	\N
754	ensemble_start_time_quantity_float64_seconds_since_1900_01_01	ensemble_start_time	\N	Ensemble Start Time, UTC	seconds since 1900-01-01	\N
755	VOID_temperature_quantity_int16_cdeg_C	VOID_temperature	\N	Void Temperature, cdeg C	cdeg_C	\N
756	velocity_po_error_flag_boolean_int8_1	velocity_po_error_flag	\N	Velocity PO Error Flag	1	\N
757	velocity_po_up_flag_boolean_int8_1	velocity_po_up_flag	\N	Velocity PO Up Flag	1	\N
758	velocity_po_north_flag_boolean_int8_1	velocity_po_north_flag	\N	Velocity PO North Flag	1	\N
759	velocity_po_east_flag_boolean_int8_1	velocity_po_east_flag	\N	Velocity PO East Flag	1	\N
760	subsampling_parameter_quantity_uint8_1	subsampling_parameter	\N	Subsampling Parameter	1	\N
761	start_bin_quantity_uint8_1	start_bin	\N	Start Bin	1	\N
762	num_bins_quantity_uint8_1	num_bins	\N	Number of Bins	1	\N
763	fluxgate_calibration_timestamp_quantity_float64_seconds_since_1900_01_01	fluxgate_calibration_timestamp	\N	Fluxgate Calibration Timestamp, UTC	seconds since 1900-01-01	\N
764	s_inverse_bx_array_quantity_float32_1	s_inverse_bx	\N	S Inverse Bx	1	\N
765	s_inverse_by_array_quantity_float32_1	s_inverse_by	\N	S Inverse By	1	\N
766	s_inverse_bz_array_quantity_float32_1	s_inverse_bz	\N	S Inverse Bz	1	\N
767	s_inverse_err_array_quantity_float32_1	s_inverse_err	\N	S Inverse Error	1	\N
768	coil_offset_array_quantity_float32_1	coil_offset	\N	Coil Offset	1	\N
769	electrical_null_quantity_float32_1	electrical_null	\N	Electrical Null	1	\N
770	tilt_calibration_timestamp_quantity_float64_seconds_since_1900_01_01	tilt_calibration_timestamp	\N	Tilt Calibration Timestamp, UTC	seconds since 1900-01-01	\N
771	roll_up_down_array_quantity_float32_1	roll_up_down	\N	Roll Up Down	1	\N
772	pitch_up_down_array_quantity_float32_1	pitch_up_down	\N	Pitch Up Down	1	\N
773	offset_up_down_array_quantity_float32_1	offset_up_down	\N	Offset Up Down	1	\N
774	tilt_null_quantity_float32_1	tilt_null	\N	Tilt Null	1	\N
775	transducer_frequency_quantity_uint32_Hz	transducer_frequency	\N	Transducer Frequency, Hz	Hz	\N
776	configuration_quantity_string_1	configuration	\N	Configuration	1	\N
777	match_layer_quantity_string_1	match_layer	\N	Match Layer	1	\N
778	beam_pattern_quantity_string_1	beam_pattern	\N	Beam Pattern	1	\N
779	orientation_quantity_string_1	orientation	\N	Orientation	1	\N
780	sensors_quantity_string_1	sensors	\N	Sensors	1	\N
781	pressure_coeff_c3_quantity_float32_1	pressure_coeff_c3	\N	Pressure Coefficient C3	1	\N
782	pressure_coeff_c2_quantity_float32_1	pressure_coeff_c2	\N	Pressure Coefficient C2	1	\N
783	pressure_coeff_c1_quantity_float32_1	pressure_coeff_c1	\N	Pressure Coefficient C1	1	\N
784	pressure_coeff_offset_quantity_float32_1	pressure_coeff_offset	\N	Pressure Coefficient Offset	1	\N
785	temperature_sensor_offset_quantity_float32_deg_C	temperature_sensor_offset	\N	Temperature Sensor Offset	deg_C	\N
786	cpu_firmware_quantity_string_1	cpu_firmware	\N	CPU Firmware	1	\N
787	boot_code_required_quantity_string_1	boot_code_required	\N	Boot Code Required	1	\N
788	boot_code_actual_quantity_string_1	boot_code_actual	\N	Boot Code Actual	1	\N
789	demod_1_version_quantity_string_1	demod_1_version	\N	Demod 1 Version	1	\N
790	demod_1_type_quantity_string_1	demod_1_type	\N	Demod 1 Type	1	\N
791	demod_2_version_quantity_string_1	demod_2_version	\N	Demod 2 Version	1	\N
792	demod_2_type_quantity_string_1	demod_2_type	\N	Demod 2 Type	1	\N
793	power_timing_version_quantity_string_1	power_timing_version	\N	Power Timing Version	1	\N
794	power_timing_type_quantity_string_1	power_timing_type	\N	Power Timing Type	1	\N
795	board_serial_numbers_quantity_string_1	board_serial_numbers	\N	Board Serial Numbers	1	\N
796	date_time_array_array_quantity_int8_1	date_time_array	\N	Date Time Array	1	\N
797	date_time_stamp_quantity_float64_seconds_since_1900_01_01	date_time_stamp	\N	Date and Time Stamp	seconds since 1900-01-01	\N
798	battery_voltage_mv_quantity_int32_mV	battery_voltage_mv	\N	Battery Voltage, mV	mV	\N
799	identification_string_quantity_string_1	identification_string	\N	Identification String	1	\N
800	absolute_pressure_burst_array_quantity_float32_psi	absolute_pressure_burst	\N	Absolute Pressure, psi	psi	\N
801	seafloor_pressure_burst_array_quantity_float32_dbar	seafloor_pressure_burst	\N	Total Seafloor Pressure, dbar	dbar	\N
802	oxy_calphase_quantity_int32_counts	oxy_calphase	\N	Calibrated phase	counts	\N
803	oxy_temp_quantity_int32_counts	oxy_temp	\N	DOSTA Temperature	counts	\N
804	sensor_id_quantity_string_1	sensor_id	\N	Sensor ID	1	\N
805	time_sync_flag_quantity_string_1	time_sync_flag	\N	Time Sync Flag	1	\N
806	lily_x_tilt_quantity_float32_urad	lily_x_tilt	\N	Tilt in X, urad	urad	\N
807	lily_y_tilt_quantity_float32_urad	lily_y_tilt	\N	Tilt in Y, urad	urad	\N
808	compass_direction_quantity_float32_degrees	compass_direction	\N	Compass Direction, degrees	degrees	\N
809	supply_voltage_quantity_float32_V	supply_voltage	\N	Supply Voltage, V	V	\N
810	press_trans_temp_quantity_float64_deg_C	press_trans_temp	\N	Nano-resolution Pressure Transducer Temperature, deg C	deg_C	\N
811	heat_x_tilt_quantity_int16_degrees	heat_x_tilt	\N	Tilt in X, degrees	degrees	\N
812	heat_y_tilt_quantity_int16_degrees	heat_y_tilt	\N	Tilt in Y, degrees	degrees	\N
813	iris_x_tilt_quantity_float32_degrees	iris_x_tilt	\N	Tilt in X, degrees	degrees	\N
814	iris_y_tilt_quantity_float32_degrees	iris_y_tilt	\N	Tilt in Y, degrees	degrees	\N
815	bottom_pressure_quantity_float32_psia	bottom_pressure	\N	Nano-resolution Bottom Pressure, psia	psia	\N
816	lily_temp_quantity_float32_deg_C	lily_temp	\N	Temperature, Degrees C	deg_C	\N
817	iris_temp_quantity_float32_deg_C	iris_temp	\N	Temperature, Degrees C	deg_C	\N
818	heat_temp_quantity_int16_deg_C	heat_temp	\N	Temperature, Degrees C	deg_C	\N
819	seafloor_tilt_magnitude_quantity_float32_urad	seafloor_tilt_magnitude	\N	Seafloor Tilt Magnitude	urad	\N
820	seafloor_tilt_direction_quantity_float32_degrees	seafloor_tilt_direction	\N	Seafloor Tilt Direction	degrees	\N
821	_	\N	\N	\N	\N	\N
822	TEMPWAT_L0_quantity_float64_deg_C	TEMPWAT_L0	\N	\N	deg_C	\N
823	CONDWAT_L0_quantity_float64_	CONDWAT_L0	\N	\N	\N	\N
824	PRESWAT_L0_quantity_float64_	PRESWAT_L0	\N	\N	\N	\N
825	TEMPWAT_L1_function_float64_deg_C	TEMPWAT_L1	\N	\N	deg_C	\N
826	CONDWAT_L1_function_float64_	CONDWAT_L1	\N	\N	\N	\N
827	PRESWAT_L1_function_float64_	PRESWAT_L1	\N	\N	\N	\N
828	PRACSAL_L2_function_float64_	PRACSAL_L2	\N	\N	\N	\N
829	absolute_salinity_function_float64_	absolute_salinity	\N	\N	\N	\N
830	rho_function_float64_	rho	\N	\N	\N	\N
831	ingestion_timestamp_quantity_float64_seconds_since_1900_01_01	ingestion_timestamp	\N	Ingestion Timestamp, UTC	seconds since 1900-01-01	\N
832	conductivity_L1_function_float32_mS_cm_1	conductivity_L1	\N	\N	mS cm-1	\N
833	pressure_L1_function_float32_dbar	pressure_L1	\N	\N	dbar	\N
834	temp_L1_function_float32_deg_C	temp_L1	\N	\N	deg_C	\N
835	salinity_function_float32_	salinity	\N	\N	\N	\N
836	density_function_float32_	density	\N	\N	\N	\N
837	beam_1_velocity_array_quantity_int16_mm_s_1	beam_1_velocity	\N	Beam 1 Velocity Profiles, mm s-1	mm s-1	\N
838	beam_2_velocity_array_quantity_int16_mm_s_1	beam_2_velocity	\N	Beam 2 Velocity Profiles, mm s-1	mm s-1	\N
839	beam_3_velocity_array_quantity_int16_mm_s_1	beam_3_velocity	\N	Beam 3 Velocity Profiles, mm s-1	mm s-1	\N
840	beam_4_velocity_array_quantity_int16_mm_s_1	beam_4_velocity	\N	Beam 4 Velocity Profiles, mm s-1	mm s-1	\N
841	percent_good_beam1_array_quantity_uint8_percent	percent_good_beam1	\N	Percent Good Beam 1	percent	\N
842	percent_good_beam2_array_quantity_uint8_percent	percent_good_beam2	\N	Percent Good Beam 2	percent	\N
843	percent_good_beam3_array_quantity_uint8_percent	percent_good_beam3	\N	Percent Good Beam 3	percent	\N
844	percent_good_beam4_array_quantity_uint8_percent	percent_good_beam4	\N	Percent Good Beam 4	percent	\N
845	real_time_clock_array_quantity_int16_1	real_time_clock	\N	Real Time Clock Array	1	\N
846	eastward_turbulent_velocity_function_float32_m_s_1	eastward_turbulent_velocity	\N	Eastward Turbulent Sea Water Velocity, m s-1	m s-1	\N
847	northward_turbulent_velocity_function_float32_m_s_1	northward_turbulent_velocity	\N	Northward Turbulent Sea Water Velocity, m s-1	m s-1	\N
848	upward_turbulent_velocity_function_float32_m_s_1	upward_turbulent_velocity	\N	Upward Turbulent Sea Water Velocity, m s-1	m s-1	\N
849	calibration_temp_quantity_float32_deg_C	calibration_temp	\N	Calibration Temperature, deg C	deg_C	\N
850	absorption_coefficient_quantity_float32_m_1	absorption_coefficient	\N	Optical Absorption Coefficient, m-1	m-1	\N
851	input_voltage_quantity_float32_V	input_voltage	\N	Input Voltage, V	V	\N
852	input_bus_current_quantity_float32_A	input_bus_current	\N	Input Bus Current, A	A	\N
853	mvpc_temperature_quantity_float32_deg_C	mvpc_temperature	\N	MVPC Temperature, deg C	deg_C	\N
854	mvpc_pressure_1_quantity_float32_psi	mvpc_pressure_1	\N	MVPC Pressure 1, psi	psi	\N
855	abs_oxygen_function_float32_um_kg_1	abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	um kg-1	\N
856	calibrated_temperature_function_float32_deg_C	calibrated_temperature	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	deg_C	\N
857	test_lookup_val_quantity_float32_1	test_lookup_val	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	1	\N
858	seafloor_pressure_function_float32_dbar	seafloor_pressure	\N	Seafloor Pressure, dbar	dbar	\N
859	explicit_lookup_function_float32_	explicit_lookup	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	\N	\N
860	extended_calibrated_temperature_function_float32_	extended_calibrated_temperature	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	\N	\N
861	qc_temp_global_range_function_float32_1	qc_temp_global_range	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	1	\N
862	qc_pressure_global_range_function_float32_1	qc_pressure_global_range	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	1	\N
863	qc_conductivity_global_range_function_float32_1	qc_conductivity_global_range	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	1	\N
864	lookup_density_function_float32_kg_m_3	lookup_density	\N	YOU SHOULD NEVER SEE THIS VARIABLE, FOR TESTS ONLY	kg m-3	\N
865	qc_temp_grt_min_value_quantity_float32_	qc_temp_grt_min_value	\N	VOID	\N	\N
866	qc_local_range_datlimz_tempwat_array_	qc_local_range_datlimz_tempwat	\N	VOID	\N	\N
867	eastward_beam_seawater_velocity_function_float32_m_s_1	eastward_beam_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
868	northward_beam_seawater_velocity_function_float32_m_s_1	northward_beam_seawater_velocity	\N	Northward Beam Sea Water Velocity, m s-1	m s-1	\N
869	upward_seawater_velocity_function_float32_m_s_1	upward_seawater_velocity	\N	Upward Beam Sea Water Velocity, m s-1	m s-1	\N
870	beam_error_velocity_function_float32_m_s_1	beam_error_velocity	\N	Beam Error Velocity, m s-1	m s-1	\N
871	reference_designator_array_	reference_designator	\N	\N	\N	\N
872	seawater_temperature_function_float32_deg_C	seawater_temperature	\N	Sea Water Temperature, deg_C	deg_C	\N
873	seawater_pressure_function_float32_dbar	seawater_pressure	\N	Sea Water Pressure, dbar	dbar	\N
874	seawater_conductivity_function_float32_S_m_1	seawater_conductivity	\N	Sea Water Conductivity, S m-1	S m-1	\N
875	practical_salinity_function_float32_1	practical_salinity	\N	Sea Water Practical Salinity	1	\N
876	seawater_density_function_float32_kg_m_3	seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
877	VelA_quantity_uint16_1	VelA	\N	\N	1	\N
878	VelB_quantity_uint16_1	VelB	\N	\N	1	\N
879	VelC_quantity_uint16_1	VelC	\N	\N	1	\N
880	VelD_quantity_uint16_1	VelD	\N	\N	1	\N
881	Mx_quantity_uint16_1	Mx	\N	\N	1	\N
882	My_quantity_uint16_1	My	\N	\N	1	\N
883	Mz_quantity_uint16_1	Mz	\N	\N	1	\N
884	Pitch_quantity_uint16_1	Pitch	\N	\N	1	\N
885	Roll_quantity_uint16_1	Roll	\N	\N	1	\N
886	upload_time_quantity_float64_seconds_since_1900_01_01	upload_time	\N	Time, UTC	seconds since 1900-01-01	\N
887	oxygen_quantity_uint16_Hz	oxygen	\N	Oxygen, Hz	Hz	\N
888	salinity_function_float32_1	salinity	\N	Practical Salinity	1	\N
889	density_function_float32_kg_m_3	density	\N	Density, kg m-3	kg m-3	\N
890	cycle_rate_quantity_uint8_s	cycle_rate	\N	Cycle Rate, s	s	\N
891	absorbance_ratio_434_function_float32_counts	absorbance_ratio_434	\N	Absorbance Ratio at 434 nm, counts	counts	\N
892	absorbance_ratio_620_function_float32_counts	absorbance_ratio_620	\N	Absorbance Ratio at 620 nm, counts	counts	\N
893	absorbance_blank_434_function_float32_1	absorbance_blank_434	\N	Absorbance Blank at 434 nm	1	\N
894	absorbance_blank_620_function_float32_1	absorbance_blank_620	\N	Absorbance Blank at 620 nm	1	\N
895	pco2w_thermistor_temperature_function_float32_deg_C	pco2w_thermistor_temperature	\N	Thermistor Temperature, deg_C\n	deg_C	\N
896	pco2_seawater_function_float32_uatm	pco2_seawater	\N	Partial Pressure of CO2 in Water, uatm	uatm	\N
897	thermistor_start_quantity_int16_counts	thermistor_start	\N	Thermistor Resistivity at Start of Measurement, counts	counts	\N
898	reference_light_measurements_array_quantity_int16_counts	reference_light_measurements	\N	Array of Reference Light Measurements, counts	counts	\N
899	thermistor_end_quantity_int16_counts	thermistor_end	\N	Thermistor Resistivity at End of Measurement, counts	counts	\N
900	signal_intensity_434_function_float32_counts	signal_intensity_434	\N	Signal Intensity at 434 nm, counts	counts	\N
901	signal_intensity_578_function_float32_counts	signal_intensity_578	\N	Signal Intensity at 578 nm, counts	counts	\N
902	phsen_thermistor_temperature_function_float32_deg_C	phsen_thermistor_temperature	\N	Thermistor Temperature at End of Measurement cycle, deg_C\n	deg_C	\N
903	ph_seawater_function_float32_1	ph_seawater	\N	pH of Seawater	1	\N
966	partial_pressure_co2_atm_function_float32_uatm	partial_pressure_co2_atm	\N	Partial Pressure of CO2 in Air, uatm	uatm	\N
904	estimated_oxygen_concentration_quantity_float32_umol_L_1	estimated_oxygen_concentration	\N	Temperature Compensated Dissolved Oxygen Concentration, umol/L	umol L-1	\N
905	estimated_oxygen_saturation_quantity_float32_percent	estimated_oxygen_saturation	\N	Air Saturation, percent	percent	\N
906	optode_temperature_quantity_float32_deg_C	optode_temperature	\N	Oxygen Sensor Temperature, deg C	deg_C	\N
907	calibrated_phase_quantity_float32_degrees	calibrated_phase	\N	Calibrated Phase Difference, degrees	degrees	\N
908	temp_compensated_phase_quantity_float32_degrees	temp_compensated_phase	\N	Temperature Compensated Phase, degrees	degrees	\N
909	blue_phase_quantity_float32_degrees	blue_phase	\N	Blue Light Phase, degrees	degrees	\N
910	red_phase_quantity_float32_degrees	red_phase	\N	Red Light Phase, degrees	degrees	\N
911	blue_amplitude_quantity_float32_mV	blue_amplitude	\N	Blue Light Amplitude, mV	mV	\N
912	red_amplitude_quantity_float32_mV	red_amplitude	\N	Red Light Amplitude, mV	mV	\N
913	raw_temperature_quantity_float32_mV	raw_temperature	\N	Thermistor Voltage, mV	mV	\N
914	svu_cal_coefs_array_quantity_float32_1	svu_cal_coefs	\N	Stern-Volmer-Uchida Calibration Coefficients (csv)	1	\N
915	svu_cal_coef2_quantity_float32_1	svu_cal_coef2	\N	Stern-Volmer-Uchida Calibration Coefficient 2 (csv2)	1	\N
916	svu_cal_coef3_quantity_float32_1	svu_cal_coef3	\N	Stern-Volmer-Uchida Calibration Coefficient 3 (csv3)	1	\N
917	svu_cal_coef4_quantity_float32_1	svu_cal_coef4	\N	Stern-Volmer-Uchida Calibration Coefficient 4 (csv4)	1	\N
918	svu_cal_coef5_quantity_float32_1	svu_cal_coef5	\N	Stern-Volmer-Uchida Calibration Coefficient 5 (csv5)	1	\N
919	svu_cal_coef6_quantity_float32_1	svu_cal_coef6	\N	Stern-Volmer-Uchida Calibration Coefficient 6 (csv6)	1	\N
920	svu_cal_coef7_quantity_float32_1	svu_cal_coef7	\N	Stern-Volmer-Uchida Calibration Coefficient 7 (csv7)	1	\N
921	tc_oxygen_function_float32_umol_L_1	tc_oxygen	\N	Temperature Compensated Dissolved Oxygen Concentration, umol/L	umol L-1	\N
922	eastward_earth_seawater_velocity_function_float32_m_s_1	eastward_earth_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
923	northward_earth_seawater_velocity_function_float32_m_s_1	northward_earth_seawater_velocity	\N	Northward Earth Sea Water Velocity, m s-1	m s-1	\N
924	upward_earth_seawater_velocity_function_float32_m_s_1	upward_earth_seawater_velocity	\N	Upward Earth Sea Water Velocity, m s-1	m s-1	\N
925	earth_error_velocity_function_float32_m_s_1	earth_error_velocity	\N	Earth Error Velocity, m s-1	m s-1	\N
926	beam_attenuation_function_float32_m_1	beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
927	optical_absorption_function_float32_m_1	optical_absorption	\N	Optical Absorption, m-1	m-1	\N
928	ctd_tc_oxygen_function_float32_umol_L_1	ctd_tc_oxygen	\N	Temperature Compensated Dissolved Oxygen Concentration, umol/L	umol L-1	\N
929	vent_fluid_temperaure_function_float32_deg_C	vent_fluid_temperaure	\N	Vent Fluid Temperature from TRHPH, deg_C	deg_C	\N
930	vent_fluid_chloride_conc_function_float32_mmol_kg_1	vent_fluid_chloride_conc	\N	Vent Fluid Chloride Concentration from TRHPH, mmol kg-1	mmol kg-1	\N
931	vent_fluid_orp_function_float32_mV	vent_fluid_orp	\N	Vent Fluid Oxidation-Reduction Potential from TRHPH, mV	mV	\N
932	fractional_second_quantity_float32_s	fractional_second	\N	\N	s	\N
933	velocity_offset_a_quantity_int_counts	velocity_offset_a	\N	Beam A velocity offset	counts	\N
934	velocity_offset_b_quantity_int32_counts	velocity_offset_b	\N	Beam B velocity offset	counts	\N
935	velocity_offset_c_quantity_int32_counts	velocity_offset_c	\N	Beam C velocity offset	counts	\N
936	velocity_offset_d_quantity_int32_counts	velocity_offset_d	\N	Beam D velocity offset	counts	\N
937	compass_offset_0_quantity_int32_1	compass_offset_0	\N	Compass offset 0	1	\N
938	compass_offset_1_quantity_int32_1	compass_offset_1	\N	Compass offset 1	1	\N
939	compass_offset_2_quantity_int32_1	compass_offset_2	\N	Compass offset 2	1	\N
940	compass_scale_factor_0_quantity_float32_1	compass_scale_factor_0	\N	Compass scale factor 0	1	\N
941	compass_scale_factor_1_quantity_float32_1	compass_scale_factor_1	\N	Compass scale factor 1	1	\N
942	compass_scale_factor_2_quantity_float32_1	compass_scale_factor_2	\N	Compass scale factor 2	1	\N
943	tilt_offset_pitch_quantity_int16_mV	tilt_offset_pitch	\N	Pitch offset	mV	\N
944	tilt_offset_roll_quantity_int16_mV	tilt_offset_roll	\N	Roll offset	mV	\N
945	burst_interval_days_quantity_int16_d	burst_interval_days	\N	Burst interval days	d	\N
946	burst_interval_hours_quantity_int16_h	burst_interval_hours	\N	Burst interval hours	h	\N
947	burst_interval_minutes_quantity_int16_min	burst_interval_minutes	\N	Burst interval minutes	min	\N
948	burst_interval_seconds_quantity_int16_s	burst_interval_seconds	\N	Burst interval seconds	s	\N
949	conductivity_ctd_l1_function_float32_S_m_1	conductivity_ctd_l1	\N	Conductivity	S m-1	\N
950	temperature_ctd_l1_function_float32_deg_C	temperature_ctd_l1	\N	Temperature	deg_C	\N
951	pressure_ctd_l1_function_float32_dbar	pressure_ctd_l1	\N	Pressure	dbar	\N
952	ctd_abs_oxygen_function_float32_umol_kg_1	ctd_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
953	salinity_ctd_l2_function_float32_g_kg_1	salinity_ctd_l2	\N	Salinity	g kg-1	\N
954	density_ctd_l2_function_float32_kg_m_3	density_ctd_l2	\N	Density	kg m-3	\N
955	begin_measurement_constant_str_string_1	begin_measurement	\N	Begin Measurement	1	\N
956	zero_a2d_quantity_int32_counts	zero_a2d	\N	Zero A/D, counts	counts	\N
957	current_a2d_quantity_int32_counts	current_a2d	\N	Current A/D, counts	counts	\N
958	measured_air_co2_quantity_float32_ppm	measured_air_co2	\N	CO2 Mole Fraction in Air, ppm	ppm	\N
959	measured_water_co2_quantity_float32_ppm	measured_water_co2	\N	CO2 Mole Fraction in Surface Seawater, ppm	ppm	\N
960	avg_irga_temperature_quantity_float32_deg_C	avg_irga_temperature	\N	Average IRGA Temperature, deg_C	deg_C	\N
961	humidity_quantity_float32_mbar	humidity	\N	Humidity, mbar	mbar	\N
962	humidity_temperature_quantity_float32_deg_C	humidity_temperature	\N	Humidity Sensor Temperature, deg_C	deg_C	\N
963	gas_stream_pressure_quantity_int16_mbar	gas_stream_pressure	\N	Gas Stream Pressure, gas tension	mbar	\N
964	irga_detector_temperature_quantity_float32_deg_C	irga_detector_temperature	\N	IRGA Detector Instrument, deg_C	deg_C	\N
965	irga_source_temperature_quantity_float32_deg_C	irga_source_temperature	\N	IRGA Source Temperature, deg_C	deg_C	\N
2021	db_array_quantity_int32_counts	db	\N	DB pointer, list of ints	counts	\N
967	partial_pressure_co2_ssw_function_float32_uatm	partial_pressure_co2_ssw	\N	Partial Pressure of CO2 in Surface Seawater, uatm	uatm	\N
968	product_name_quantity_string_1	product_name	\N	Product Name	1	\N
969	product_number_quantity_uint16_1	product_number	\N	Product Number	1	\N
970	software_id_quantity_uint32_1	software_id	\N	Software ID	1	\N
971	software_version_array_quantity_int8_1	software_version	\N	Software Version (Major, Minor, Build)	1	\N
972	node_description_quantity_string_1	node_description	\N	Node Description	1	\N
973	owner_description_quantity_string_1	owner_description	\N	Owner	1	\N
974	salinity_comp_quantity_float32_1	salinity_comp	\N	Compensation Salinity	1	\N
975	phase_coef_array_quantity_float32_1	phase_coef	\N	Phase Coefficients	1	\N
976	foil_id_quantity_string_1	foil_id	\N	Foil ID	1	\N
977	foil_coef_a_array_quantity_float32_1	foil_coef_a	\N	Foil Coefficients A	1	\N
978	foil_coef_b_array_quantity_float32_1	foil_coef_b	\N	Foil Coefficients B	1	\N
979	foil_poly_deg_t_array_quantity_int8_1	foil_poly_deg_t	\N	Foil Polynomial Temperature Exponent Coefficients	1	\N
980	foil_poly_deg_o_array_quantity_int8_1	foil_poly_deg_o	\N	Foil Polynomial Oxygen Exponent Coefficients	1	\N
981	conc_coefs_array_quantity_float32_1	conc_coefs	\N	Concentration Coefficients	1	\N
982	nom_air_press_quantity_float32_hPa	nom_air_press	\N	Nominal Air Pressure	hPa	\N
983	nom_air_mix_quantity_float32_hPa	nom_air_mix	\N	Nominal Air Mix	hPa	\N
984	cal_data_sat_array_quantity_float32_degrees	cal_data_sat	\N	Calibration Data for 100% Saturation	degrees	\N
985	cal_data_air_press_quantity_float32_hPa	cal_data_air_press	\N	Calibration Data for Air Pressure	hPa	\N
986	cal_data_zero_array_quantity_float32_degrees	cal_data_zero	\N	Calibration Data for 0% Saturation	degrees	\N
987	red_reference_boolean_int8_1	red_reference	\N	Enable Red Reference	1	\N
988	red_ref_interval_quantity_int8_1	red_ref_interval	\N	Red Reference Interval	1	\N
989	operation_mode_quantity_string_1	operation_mode	\N	Mode	1	\N
990	sleep_mode_boolean_int8_1	sleep_mode	\N	Enable Sleep Mode	1	\N
991	polled_mode_boolean_int8_1	polled_mode	\N	Enable Polled Mode	1	\N
992	enable_text_boolean_int8_1	enable_text	\N	Enable Text	1	\N
993	decimal_format_boolean_int8_1	decimal_format	\N	Enable Decimal Format	1	\N
994	temp_limits_array_quantity_float32_deg_C	temp_limits	\N	Analog Temperature Limits	deg_C	\N
995	conc_limits_array_quantity_float32_umol_L_1	conc_limits	\N	Analog Oxygen Concentration Limits	umol L-1	\N
996	sat_limits_array_quantity_float32_%	sat_limits	\N	Analog Saturation Limits	%	\N
997	phase_limits_array_quantity_float32_degrees	phase_limits	\N	Analog Phase Limits	degrees	\N
998	analog_output_quantity_string_1	analog_output	\N	Analog Output	1	\N
999	analog_1_coefs_array_quantity_float32_1	analog_1_coefs	\N	Analog Channel 1 Trim Coefficients	1	\N
1000	analog_2_coefs_array_quantity_float32_1	analog_2_coefs	\N	Analog Channel 2 Trim Coefficients	1	\N
1001	air_saturation_boolean_int8_1	air_saturation	\N	Enable Air Saturation	1	\N
1002	enable_raw_data_boolean_int8_1	enable_raw_data	\N	Enable Raw Data	1	\N
1003	enable_temp_boolean_int8_1	enable_temp	\N	Enable Temperature	1	\N
1004	humidity_comp_boolean_int8_1	humidity_comp	\N	Enable Humidity Compensation	1	\N
1005	enable_svu_boolean_int8_1	enable_svu	\N	Enable Stern-Volmer-Uchida Formula	1	\N
1006	sampling_interval_quantity_float32_s	sampling_interval	\N	Sampling Interval	s	\N
1007	location_description_quantity_string_1	location_description	\N	Location	1	\N
1008	geographic_position_description_quantity_string_1	geographic_position_description	\N	Geographic Position	1	\N
1009	vertical_position_description_quantity_float32_1	vertical_position_description	\N	Vertical Position	1	\N
1010	reference_description_quantity_string_1	reference_description	\N	Reference	1	\N
1011	temperature1_quantity_float32_deg_C	temperature1	\N	Temperature 1	deg_C	\N
1012	temperature2_quantity_float32_deg_C	temperature2	\N	Temperature 2	deg_C	\N
1013	temperature3_quantity_float32_deg_C	temperature3	\N	Temperature 3	deg_C	\N
1014	barometric_pressure_quantity_float32_mbar	barometric_pressure	\N	Barometric Pressure, mbar	mbar	\N
1015	relative_humidity_quantity_float32_%	relative_humidity	\N	Relative Humidity, %	%	\N
1016	air_temperature_quantity_float32_deg_C	air_temperature	\N	Air Temperature	deg_C	\N
1017	longwave_irradiance_quantity_float32_W_m_2	longwave_irradiance	\N	Longwave Irradiance	W m-2	\N
1018	precipitation_quantity_float32_mm	precipitation	\N	Precipitation Level	mm	\N
1019	sea_surface_temperature_quantity_float32_deg_C	sea_surface_temperature	\N	Sea Surface Temperature	deg_C	\N
1020	sea_surface_conductivity_quantity_float32_S_m_1	sea_surface_conductivity	\N	Sea Surface Conductivity	S m-1	\N
1021	shortwave_irradiance_quantity_float32_W_m_2	shortwave_irradiance	\N	Shorwave Irradiance	W m-2	\N
1022	eastward_wind_velocity_quantity_float32_m_s_1	eastward_wind_velocity	\N	Eastward Wind Velocity relative to Magnetic North	m s-1	\N
1023	northward_wind_velocity_quantity_float32_m_s_1	northward_wind_velocity	\N	Northward Wind Velocity relative to Magnetic North	m s-1	\N
1024	instrument_model_quantity_string_1	instrument_model	\N	Instrument Model	1	\N
1025	calibration_date_quantity_string_1	calibration_date	\N	Calibration Date	1	\N
1026	logging_interval_quantity_uint16_s	logging_interval	\N	Logging interval	s	\N
1027	current_tick_quantity_uint16_s	current_tick	\N	Current Second of Logging Interval	s	\N
1028	recent_record_interval_quantity_uint8_min	recent_record_interval	\N	Recent Record Interval (R-interval)	min	\N
1029	flash_card_presence_boolean_int8_1	flash_card_presence	\N	Flash Card Presence	1	\N
1030	ptt_id1_quantity_string_1	ptt_id1	\N	PPT ID#1 Hex message	1	\N
1031	ptt_id2_quantity_string_1	ptt_id2	\N	PPT ID#2 Hex message	1	\N
1032	ptt_id3_quantity_string_1	ptt_id3	\N	PPT ID#3 Hex message	1	\N
1033	failure_messages_quantity_string_1	failure_messages	\N	Failure messages	1	\N
1034	sampling_state_quantity_string_1	sampling_state	\N	Sampling Status	1	\N
1035	barometric_pressure_l1_function_float32_Pa	barometric_pressure_l1	\N	Barometric Pressure, Pa	Pa	\N
1036	eastward_wind_velocity_l1_function_float32_m_s_1	eastward_wind_velocity_l1	\N	Eastward Wind Velocity relative to True North	m s-1	\N
2022	dfile_quantity_string_1	dfile	\N	Data File	1	\N
1037	northward_wind_velocity_l1_function_float32_m_s_1	northward_wind_velocity_l1	\N	Northward Wind Velocity relative to True North	m s-1	\N
1038	port_number_quantity_int8_1	port_number	\N	Port Number	1	\N
1039	commanded_volume_quantity_int16_mL	commanded_volume	\N	Commanded Volume to Pump	mL	\N
1040	commanded_flowrate_quantity_int8_mL_min_1	commanded_flowrate	\N	Commanded Flowrate to Pump	mL min-1	\N
1041	commanded_min_flowrate_quantity_int8_mL_min_1	commanded_min_flowrate	\N	Commanded Minimum Flowrate	mL min-1	\N
1042	commanded_timelimit_quantity_int8_min	commanded_timelimit	\N	Commanded Time Limit to Pump	min	\N
1043	cumulative_volume_quantity_float32_mL	cumulative_volume	\N	Cumulative Volume	mL	\N
1044	flowrate_quantity_float32_mL_min_1	flowrate	\N	Flowrate	mL min-1	\N
1045	minimum_flowrate_quantity_float32_mL_min_1	minimum_flowrate	\N	Minimum Flowrate	mL min-1	\N
1046	elapsed_time_quantity_int16_s	elapsed_time	\N	Elapsed Time since start of sample, s	s	\N
1047	sampling_status_code_quantity_int8_1	sampling_status_code	\N	Sampling Status Code	1	\N
1048	vel3d_c_eastward_turbulent_velocity_function_float32_m_s_1	vel3d_c_eastward_turbulent_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
1049	vel3d_c_northward_turbulent_velocity_function_float32_m_s_1	vel3d_c_northward_turbulent_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
1050	vel3d_c_upward_turbulent_velocity_function_float32_m_s_1	vel3d_c_upward_turbulent_velocity	\N	Upward Turbulent Velocity, m s-1	m s-1	\N
1051	transmit_pulse_length_2nd_quantity_uint16_counts	transmit_pulse_length_2nd	\N	Transmit Pulse Length, counts	counts	\N
1052	instrument_id_quantity_string_1	instrument_id	\N	Instrument ID	1	\N
1053	timer_quantity_float64_s	timer	\N	Elapsed Time since Initialization, s	s	\N
1054	sample_delay_quantity_int16_ms	sample_delay	\N	Sample delay, ms	ms	\N
1055	spkir_samples_array_quantity_uint32_counts	spkir_samples	\N	A/D Counts for Optical Channels 1-7: 1 = 412nm, 2 = 443nm, 3 = 490nm, 4 = 510nm, 5 = 555nm, 6 = 620nm, 7 = 683nm.	counts	\N
1056	channel_2_quantity_uint32_counts	channel_2	\N	A/D Counts for Optical Channel 2	counts	\N
1057	channel_3_quantity_uint32_counts	channel_3	\N	A/D Counts for Optical Channel 3	counts	\N
1058	channel_4_quantity_uint32_counts	channel_4	\N	A/D Counts for Optical Channel 4	counts	\N
1059	channel_5_quantity_uint32_counts	channel_5	\N	A/D Counts for Optical Channel 5	counts	\N
1060	channel_6_quantity_uint32_counts	channel_6	\N	A/D Counts for Optical Channel 6	counts	\N
1061	channel_7_quantity_uint32_counts	channel_7	\N	A/D Counts for Optical Channel 7	counts	\N
1062	vin_sense_quantity_uint16_counts	vin_sense	\N	Regulated Supply Voltage, counts	counts	\N
1063	va_sense_quantity_uint16_counts	va_sense	\N	Analog Rail Voltage, counts	counts	\N
1064	internal_temperature_quantity_uint16_counts	internal_temperature	\N	Internal Instrument Temperature, counts	counts	\N
1065	frame_counter_quantity_uint16_counts	frame_counter	\N	Frame Counter, counts	counts	\N
1066	telemetry_baud_rate_quantity_uint32_bps	telemetry_baud_rate	\N	Telemetry Baud Rate, bps	bps	\N
1067	max_frame_rate_quantity_string_Hz	max_frame_rate	\N	Frame Rate, Hz	Hz	\N
1068	initialize_silent_mode_boolean_int8_1	initialize_silent_mode	\N	Initialize Silent Mode	1	\N
1069	initialize_power_down_boolean_int8_1	initialize_power_down	\N	Initialize Power Down	1	\N
1070	initialize_auto_telemetry_boolean_int8_1	initialize_auto_telemetry	\N	Initialize Auto Telemetry	1	\N
1071	network_mode_boolean_int8_1	network_mode	\N	Enable Network Mode	1	\N
1072	network_address_quantity_uint8_1	network_address	\N	Network Address	1	\N
1073	network_baud_rate_quantity_uint32_bps	network_baud_rate	\N	Network Baud Rate, bps	bps	\N
1074	external_device2_fault_boolean_int8_1	external_device2_fault	\N	External Fault, Device 2	1	\N
1075	external_device3_fault_boolean_int8_1	external_device3_fault	\N	External Fault, Device 3	1	\N
1076	num_data_records_quantity_int32_1	num_data_records	\N	Number of Data Records	1	\N
1077	num_error_records_quantity_int32_1	num_error_records	\N	Number of Error Records	1	\N
1078	num_bytes_stored_quantity_int32_bytes	num_bytes_stored	\N	Number of Bytes Stored, bytes	bytes	\N
1079	external_pump_setting_quantity_uint8_1	external_pump_setting	\N	External Pump (Device 1) Setting	1	\N
1080	number_samples_averaged_quantity_uint8_counts	number_samples_averaged	\N	Number of Samples	counts	\N
1081	number_flushes_quantity_uint8_counts	number_flushes	\N	Number of Flushes	counts	\N
1082	pump_on_flush_quantity_uint8_counts	pump_on_flush	\N	Pump On Flush	counts	\N
1083	pump_off_flush_quantity_uint8_counts	pump_off_flush	\N	Pump Off Flush	counts	\N
1084	number_reagent_pumps_quantity_uint8_counts	number_reagent_pumps	\N	Number of Reagent Pumps	counts	\N
1085	valve_delay_quantity_uint8_counts	valve_delay	\N	Valve Delay	counts	\N
1086	pump_on_ind_quantity_uint8_counts	pump_on_ind	\N	Pump On Ind	counts	\N
1087	pv_off_ind_quantity_uint8_counts	pv_off_ind	\N	Pump Off Ind	counts	\N
1088	number_blanks_quantity_uint8_counts	number_blanks	\N	PV Off	counts	\N
1089	pump_measure_t_quantity_uint8_counts	pump_measure_t	\N	Number of Blanks	counts	\N
1090	pump_off_to_measure_quantity_uint8_counts	pump_off_to_measure	\N	Pump Off To Measure	counts	\N
1091	measure_to_pump_on_quantity_uint8_counts	measure_to_pump_on	\N	Pump To Pump On	counts	\N
1092	number_measurements_quantity_uint8_counts	number_measurements	\N	Number of Measurements	counts	\N
1093	salinity_delay_quantity_uint8_counts	salinity_delay	\N	Salinity Delay	counts	\N
1094	corrected_compass_direction_function_float32_degrees	corrected_compass_direction	\N	Corrected Compass Direction, degrees	degrees	\N
1095	seafloor_tilt_magnitude_function_float32_urad	seafloor_tilt_magnitude	\N	Seafloor Tilt Magnitude, urad	urad	\N
1096	seafloor_tilt_direction_function_float32_degrees	seafloor_tilt_direction	\N	Seafloor Tilt Direction, degrees	degrees	\N
1097	date_string_quantity_string_1	date_string	\N	Measurement Date, UTC	1	\N
1098	time_string_quantity_string_1	time_string	\N	Measurement Time, UTC	1	\N
1099	measurement_wavelength_beta_quantity_uint16_nm	measurement_wavelength_beta	\N	Measurement Wavelength, Scattering, nm	nm	\N
1100	raw_signal_beta_quantity_uint16_counts	raw_signal_beta	\N	Raw Scattering Measurement, counts	counts	\N
1101	measurement_wavelength_chl_quantity_uint16_nm	measurement_wavelength_chl	\N	Measurement Wavelength, Chlorophyll, nm	nm	\N
1102	raw_signal_chl_quantity_uint16_counts	raw_signal_chl	\N	Raw Chlorophyll Measurement, counts	counts	\N
1103	measurement_wavelength_cdom_quantity_uint16_nm	measurement_wavelength_cdom	\N	Measurement Wavelength, CDOM, nm	nm	\N
1104	raw_signal_cdom_quantity_uint16_counts	raw_signal_cdom	\N	Raw CDOM Measurement, counts	counts	\N
1105	raw_internal_temp_quantity_uint16_counts	raw_internal_temp	\N	Raw Internal Temperature, counts	counts	\N
1106	signal_1_scale_factor_quantity_float32_m_1_sr_1_counts_1	signal_1_scale_factor	\N	Signal 1 (Scattering) Scale Factor, m-1 sr-1 counts-1	m-1 sr-1 counts-1	\N
1107	signal_1_offset_quantity_uint16_counts	signal_1_offset	\N	Signal 1 (Scattering) Offset, counts	counts	\N
1108	signal_2_scale_factor_quantity_float32_ug_L_1_counts_1	signal_2_scale_factor	\N	Signal 2 (Chlorophyll) Scale Factor, ug L-1 counts-1	ug L-1 counts-1	\N
1109	signal_2_offset_quantity_uint16_counts	signal_2_offset	\N	Signal 2 (Chlorophyll) Offset, counts	counts	\N
1110	signal_3_scale_factor_quantity_float32_ppb_counts_1	signal_3_scale_factor	\N	Signal 3 (CDOM) Scale Factor, ppb counts-1	ppb counts-1	\N
1111	signal_3_offset_quantity_uint16_counts	signal_3_offset	\N	Signal 3 (CDOM) Offset, counts	counts	\N
1112	total_volume_scattering_coefficient_function_float32_m_1_sr_1	total_volume_scattering_coefficient	\N	Total Volume Scattering Coefficient (Beta(117,700)), m-1 sr-1	m-1 sr-1	\N
1113	fluorometric_chlorophyll_a_function_float32_ug_L_1	fluorometric_chlorophyll_a	\N	Fluorometric Chlorophyll a Concentration, ug L-1	ug L-1	\N
1114	fluorometric_cdom_function_float32_ppb	fluorometric_cdom	\N	Fluorometric CDOM Concentration, ppb	ppb	\N
1115	eastward_velocity_function_float32_m_s_1	eastward_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
1116	northward_velocity_function_float32_m_s_1	northward_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
1117	upward_velocity_function_float32_m_s_1	upward_velocity	\N	Upward Turbulent Velocity, m s-1	m s-1	\N
1118	ensemble_start_time_2_quantity_float64_seconds_since_1900_01_01	ensemble_start_time_2	\N	Ensemble Start Time, UTC	seconds since 1900-01-01	\N
1119	real_time_clock_2_array_quantity_int16_1	real_time_clock_2	\N	Real Time Clock Array	1	\N
1120	bottom_track_id_quantity_uint16_1	bottom_track_id	\N	Bottom Track (BT) ID	1	\N
1121	bt_pings_per_ensemble_quantity_uint16_1	bt_pings_per_ensemble	\N	BT Pings per Ensemble	1	\N
1122	bt_delay_before_reacquire_quantity_uint16_1	bt_delay_before_reacquire	\N	BT Delay before Reacquire	1	\N
1123	bt_corr_magnitude_min_quantity_uint8_counts	bt_corr_magnitude_min	\N	BT Minimum Correlation Magnitude, counts	counts	\N
1124	bt_eval_magnitude_min_quantity_uint8_counts	bt_eval_magnitude_min	\N	BT Minimum Evaluation Amplitude, counts	counts	\N
1125	bt_percent_good_min_quantity_uint8_percent	bt_percent_good_min	\N	BT Minimum Percent Good, percent	percent	\N
1126	bt_mode_quantity_uint8_1	bt_mode	\N	BT Mode	1	\N
1127	bt_error_velocity_max_quantity_uint16_mm_s_1	bt_error_velocity_max	\N	BT Maximum Error Velocity, mm s-1	mm s-1	\N
1128	bt_beam1_range_quantity_uint32_cm	bt_beam1_range	\N	BT Beam 1 Range, cm	cm	\N
1129	bt_beam2_range_quantity_uint32_cm	bt_beam2_range	\N	BT Beam 2 Range, cm	cm	\N
1130	bt_beam3_range_quantity_uint32_cm	bt_beam3_range	\N	BT Beam 3 Range, cm	cm	\N
1131	bt_beam4_range_quantity_uint32_cm	bt_beam4_range	\N	BT Beam 4 Range, cm	cm	\N
1132	bt_eastward_velocity_quantity_int16_mm_s_1	bt_eastward_velocity	\N	BT Bottom Eastward Velocity, mm s-1	mm s-1	\N
1133	bt_northward_velocity_quantity_int16_mm_s_1	bt_northward_velocity	\N	BT Bottom Northward Velocity, mm s-1	mm s-1	\N
1134	bt_upward_velocity_quantity_int16_mm_s_1	bt_upward_velocity	\N	BT Bottom Upward Velocity, mm s-1	mm s-1	\N
1135	bt_error_velocity_quantity_int16_mm_s_1	bt_error_velocity	\N	BT Bottom Error Velocity, mm s-1	mm s-1	\N
1136	bt_beam1_correlation_quantity_uint8_counts	bt_beam1_correlation	\N	BT Bottom Beam 1 Correlation, counts	counts	\N
1137	bt_beam2_correlation_quantity_uint8_counts	bt_beam2_correlation	\N	BT Bottom Beam 2 Correlation, counts	counts	\N
1138	bt_beam3_correlation_quantity_uint8_counts	bt_beam3_correlation	\N	BT Bottom Beam 3 Correlation, counts	counts	\N
1139	bt_beam4_correlation_quantity_uint8_counts	bt_beam4_correlation	\N	BT Bottom Beam 4 Correlation, counts	counts	\N
1140	bt_beam1_eval_amp_quantity_uint8_counts	bt_beam1_eval_amp	\N	BT Bottom Beam 1 Evaluation Amplitude, counts	counts	\N
1141	bt_beam2_eval_amp_quantity_uint8_counts	bt_beam2_eval_amp	\N	BT Bottom Beam 2 Evaluation Amplitude, counts	counts	\N
1142	bt_beam3_eval_amp_quantity_uint8_counts	bt_beam3_eval_amp	\N	BT Bottom Beam 3 Evaluation Amplitude, counts	counts	\N
1143	bt_beam4_eval_amp_quantity_uint8_counts	bt_beam4_eval_amp	\N	BT Bottom Beam 4 Evaluation Amplitude, counts	counts	\N
1144	bt_beam1_percent_good_quantity_uint8_percent	bt_beam1_percent_good	\N	BT Bottom Beam 1 Percent Good, percent	percent	\N
1145	bt_beam2_percent_good_quantity_uint8_percent	bt_beam2_percent_good	\N	BT Bottom Beam 2 Percent Good, percent	percent	\N
1146	bt_beam3_percent_good_quantity_uint8_percent	bt_beam3_percent_good	\N	BT Bottom Beam 3 Percent Good, percent	percent	\N
1147	bt_beam4_percent_good_quantity_uint8_percent	bt_beam4_percent_good	\N	BT Bottom Beam 4 Percent Good, percent	percent	\N
1148	bt_ref_layer_min_quantity_uint16_dm	bt_ref_layer_min	\N	BT Reference Layer Minimum Size, dm	dm	\N
1149	bt_ref_layer_near_quantity_uint16_dm	bt_ref_layer_near	\N	BT Reference Layer Near Boundary, dm	dm	\N
1150	bt_ref_layer_far_quantity_uint16_dm	bt_ref_layer_far	\N	BT Reference Layer Far Boundary, dm	dm	\N
1151	bt_eastward_ref_layer_velocity_quantity_int16_mm_s_1	bt_eastward_ref_layer_velocity	\N	BT Reference Layer Eastward Velocity, mm s-1	mm s-1	\N
1152	bt_northward_ref_layer_velocity_quantity_int16_mm_s_1	bt_northward_ref_layer_velocity	\N	BT Reference Layer Northward Velocity, mm s-1	mm s-1	\N
1153	bt_upward_ref_layer_velocity_quantity_int16_mm_s_1	bt_upward_ref_layer_velocity	\N	BT Reference Layer Upward Velocity, mm s-1	mm s-1	\N
1154	bt_error_ref_layer_velocity_quantity_int16_mm_s_1	bt_error_ref_layer_velocity	\N	BT Reference Layer Error Velocity, mm s-1	mm s-1	\N
1155	bt_beam1_ref_correlation_quantity_uint8_counts	bt_beam1_ref_correlation	\N	BT Reference Layer Beam 1 Correlation, counts	counts	\N
1156	bt_beam2_ref_correlation_quantity_uint8_counts	bt_beam2_ref_correlation	\N	BT Reference Layer Beam 2 Correlation, counts	counts	\N
1157	bt_beam3_ref_correlation_quantity_uint8_counts	bt_beam3_ref_correlation	\N	BT Reference Layer Beam 3 Correlation, counts	counts	\N
1158	bt_beam4_ref_correlation_quantity_uint8_counts	bt_beam4_ref_correlation	\N	BT Reference Layer Beam 4 Correlation, counts	counts	\N
1159	bt_beam1_ref_intensity_quantity_uint8_counts	bt_beam1_ref_intensity	\N	BT Reference Layer Beam 1 Evaluation Amplitude, counts	counts	\N
1160	bt_beam2_ref_intensity_quantity_uint8_counts	bt_beam2_ref_intensity	\N	BT Reference Layer Beam 2 Evaluation Amplitude, counts	counts	\N
1161	bt_beam3_ref_intensity_quantity_uint8_counts	bt_beam3_ref_intensity	\N	BT Reference Layer Beam 3 Evaluation Amplitude, counts	counts	\N
1162	bt_beam4_ref_intensity_quantity_uint8_counts	bt_beam4_ref_intensity	\N	BT Reference Layer Beam 4 Evaluation Amplitude, counts	counts	\N
1163	bt_beam1_ref_percent_good_quantity_uint8_percent	bt_beam1_ref_percent_good	\N	BT Reference Layer Beam 1 Percent Good, percent	percent	\N
1164	bt_beam2_ref_percent_good_quantity_uint8_percent	bt_beam2_ref_percent_good	\N	BT Reference Layer Beam 2 Percent Good, percent	percent	\N
1165	bt_beam3_ref_percent_good_quantity_uint8_percent	bt_beam3_ref_percent_good	\N	BT Reference Layer Beam 3 Percent Good, percent	percent	\N
1166	bt_beam4_ref_percent_good_quantity_uint8_percent	bt_beam4_ref_percent_good	\N	BT Reference Layer Beam 4 Percent Good, percent	percent	\N
1167	bt_max_depth_quantity_uint16_dm	bt_max_depth	\N	BT Maximum Tracking Depth, dm	dm	\N
1168	bt_beam1_rssi_amplitude_quantity_uint8_counts	bt_beam1_rssi_amplitude	\N	BT Beam 1 RSSI Amplitude, counts	counts	\N
1169	bt_beam2_rssi_amplitude_quantity_uint8_counts	bt_beam2_rssi_amplitude	\N	BT Beam 2 RSSI Amplitude, counts	counts	\N
1170	bt_beam3_rssi_amplitude_quantity_uint8_counts	bt_beam3_rssi_amplitude	\N	BT Beam 3 RSSI Amplitude, counts	counts	\N
1171	bt_beam4_rssi_amplitude_quantity_uint8_counts	bt_beam4_rssi_amplitude	\N	BT Beam 4 RSSI Amplitude, counts	counts	\N
1172	bt_gain_quantity_uint8_1	bt_gain	\N	BT Gain Level	1	\N
1173	ensemble_number_quantity_uint32_1	ensemble_number	\N	Ensemble Number	1	\N
1174	unit_id_quantity_uint8_1	unit_id	\N	Unit ID	1	\N
1175	c_air_pump_quantity_int8_1	c_air_pump	\N	Air Pump	1	\N
1176	c_ballast_pumped_quantity_float32_mL	c_ballast_pumped	\N	Commanded Ballast Pumped, mL	mL	\N
1177	c_battpos_quantity_float32_in	c_battpos	\N	Commanded Battery Position, inches	in	\N
1178	c_battroll_quantity_float32_rad	c_battroll	\N	Battroll, rad	rad	\N
1179	c_bsipar_on_quantity_float32_s	c_bsipar_on	\N	Bsipar On, s	s	\N
1180	c_de_oil_vol_quantity_float32_mL	c_de_oil_vol	\N	Deep Engine Oil Volumn, mL	mL	\N
1181	c_dvl_on_quantity_float32_s	c_dvl_on	\N	Commanded doppler velocity logger ensemble start interval, Seconds	s	\N
1182	c_flbbcd_on_quantity_float32_s	c_flbbcd_on	\N	Flbbcd On, s	s	\N
1183	c_heading_quantity_float32_rad	c_heading	\N	Heading, rad	rad	\N
1184	c_oxy3835_wphase_on_quantity_float32_s	c_oxy3835_wphase_on	\N	Oxy3835 Wphase On, s	s	\N
1185	c_pitch_quantity_float32_rad	c_pitch	\N	Pitch, rad	rad	\N
1186	c_profile_on_quantity_float32_s	c_profile_on	\N	Profile On,s	s	\N
1187	c_wpt_lat_quantity_float32_degrees	c_wpt_lat	\N	Commanded Waypoint Position: Latitude, degrees	degrees	\N
1188	c_wpt_lon_quantity_float32_degrees	c_wpt_lon	\N	Commanded Waypoint Position: Longitude, degrees	degrees	\N
1189	m_1meg_persistor_quantity_int8_1	m_1meg_persistor	\N	1meg Persistor	1	\N
1190	m_aground_water_depth_quantity_float32_m	m_aground_water_depth	\N	Aground Water Depth, m	m	\N
1191	m_air_fill_quantity_int8_1	m_air_fill	\N	Air Fill	1	\N
1192	m_air_pump_quantity_int8_1	m_air_pump	\N	Air Pump	1	\N
1193	m_altimeter_status_quantity_int8_1	m_altimeter_status	\N	Altimeter Status	1	\N
1194	m_altimeter_voltage_quantity_float32_V	m_altimeter_voltage	\N	Altimeter Voltage, V	V	\N
1195	m_altitude_quantity_float32_m	m_altitude	\N	Altitude, m	m	\N
1196	m_altitude_rate_quantity_float32_m_s_1	m_altitude_rate	\N	Altitude Rate, m s-1	m s-1	\N
1197	m_appear_to_be_at_surface_quantity_int8_1	m_appear_to_be_at_surface	\N	Appear To Be At Surface	1	\N
1198	m_argos_is_xmitting_quantity_int8_1	m_argos_is_xmitting	\N	Argos Is Xmitting	1	\N
1199	m_argos_on_quantity_int8_1	m_argos_on	\N	Argos On	1	\N
1200	m_argos_sent_data_quantity_int8_1	m_argos_sent_data	\N	Argos Sent Data	1	\N
1201	m_argos_timestamp_quantity_float64_seconds_since_1970_01_01	m_argos_timestamp	\N	Argos Timestamp, UTC	seconds since 1970-01-01	\N
1202	m_at_risk_depth_quantity_float32_m	m_at_risk_depth	\N	At Risk Depth, m	m	\N
1203	m_avbot_enable_quantity_int8_1	m_avbot_enable	\N	Avbot Enable	1	\N
1204	m_avbot_power_quantity_int8_1	m_avbot_power	\N	Avbot Power	1	\N
1205	m_avg_climb_rate_quantity_float32_m_s_1	m_avg_climb_rate	\N	Average Climb Rate, m s-1	m s-1	\N
1206	m_avg_depth_rate_quantity_float32_m_s_1	m_avg_depth_rate	\N	Average Depth Rate, m s-1	m s-1	\N
1207	m_avg_dive_rate_quantity_float32_m_s_1	m_avg_dive_rate	\N	Average Dive Rate, m s-1	m s-1	\N
1208	m_avg_downward_inflection_time_quantity_float32_s	m_avg_downward_inflection_time	\N	Average Downward Inflection Time, s	s	\N
1209	m_avg_speed_quantity_float32_m_s_1	m_avg_speed	\N	Average Speed, m s-1	m s-1	\N
1210	m_avg_system_clock_lags_gps_quantity_float32_s	m_avg_system_clock_lags_gps	\N	Average System Clock Lags Gps, s	s	\N
1211	m_avg_upward_inflection_time_quantity_float32_s	m_avg_upward_inflection_time	\N	Average Upward Inflection Time,s	s	\N
1212	m_avg_yo_time_quantity_float32_s	m_avg_yo_time	\N	Average Yo Time, s	s	\N
1213	m_ballast_pumped_quantity_float32_mL	m_ballast_pumped	\N	Measured Ballast Pumped, mL	mL	\N
1214	m_ballast_pumped_energy_quantity_float32_J	m_ballast_pumped_energy	\N	Ballast Pumped Energy, J	J	\N
1215	m_ballast_pumped_vel_quantity_float32_mL_s_1	m_ballast_pumped_vel	\N	Ballast Pumped Velocity, mL s-1	mL s-1	\N
1216	m_battery_quantity_float32_V	m_battery	\N	Battery, V	V	\N
1217	m_battery_inst_quantity_float32_V	m_battery_inst	\N	Battery Inst, V	V	\N
1218	m_battpos_quantity_float32_in	m_battpos	\N	Measured Battery Position, inches	in	\N
1219	m_battpos_vel_quantity_float32_in_s_1	m_battpos_vel	\N	Battery Position Velocity, in s-1	in s-1	\N
1220	m_battroll_quantity_float32_rad	m_battroll	\N	Battery Roll, rad	rad	\N
1221	m_battroll_vel_quantity_float32_rad_s_1	m_battroll_vel	\N	Battery Roll Velocity, rad s-1	rad s-1	\N
1222	m_bpump_fault_bit_quantity_int8_1	m_bpump_fault_bit	\N	Bit Pump Fault Status	1	\N
1223	m_certainly_at_surface_quantity_int8_1	m_certainly_at_surface	\N	Certainly At Surface	1	\N
1224	m_chars_tossed_by_abend_quantity_float32_1	m_chars_tossed_by_abend	\N	Chars Tossed By Abend	1	\N
1225	m_chars_tossed_with_cd_off_quantity_float32_1	m_chars_tossed_with_cd_off	\N	Chars Tossed With CD Off	1	\N
1226	m_chars_tossed_with_power_off_quantity_float32_1	m_chars_tossed_with_power_off	\N	Chars Tossed With Power Off	1	\N
2023	pf_quantity_string_1	pf	\N	Parameter File	1	\N
1227	m_climb_tot_time_quantity_float32_s	m_climb_tot_time	\N	Time To Complete Climb, s	s	\N
1228	m_console_cd_quantity_int8_1	m_console_cd	\N	State Of RF Modem Carrier Detect	1	\N
1229	m_console_on_quantity_int8_1	m_console_on	\N	Power State Of RF Modem	1	\N
1230	m_cop_tickle_quantity_int8_1	m_cop_tickle	\N	COP Is Tickled	1	\N
1231	m_coulomb_amphr_quantity_float32_amp_h	m_coulomb_amphr	\N	Measured Integrated current, amp-h	amp-h	\N
1232	m_coulomb_amphr_raw_quantity_float32_1	m_coulomb_amphr_raw	\N	m_coulomb_amphr_raw	1	\N
1233	m_coulomb_amphr_total_quantity_float32_amp_h	m_coulomb_amphr_total	\N	Measured Total Persistant amp-hours, Ah	amp-h	\N
1234	m_coulomb_current_quantity_float32_amp	m_coulomb_current	\N	Measured Instantaneous Current, A	amp	\N
1235	m_coulomb_current_raw_quantity_float32_1	m_coulomb_current_raw	\N	Raw Coulomb Current	1	\N
1236	m_cycle_number_quantity_float32_1	m_cycle_number	\N	Measured cycle number	1	\N
1237	m_depth_quantity_float32_m	m_depth	\N	Measured Depth, m	m	\N
1238	m_depth_rate_quantity_float32_m_s_1	m_depth_rate	\N	Rate Of Change Of Depth, m s-1	m s-1	\N
1239	m_depth_rate_avg_final_quantity_float32_m_s_1	m_depth_rate_avg_final	\N	Final Value Of Change Of Depth, m s-1	m s-1	\N
1240	m_depth_rate_running_avg_quantity_float32_m_s_1	m_depth_rate_running_avg	\N	Running Average of Depth Rate Change, m s-1	m s-1	\N
1241	m_depth_rate_running_avg_n_quantity_int8_1	m_depth_rate_running_avg_n	\N	Data Sample of #n of Depth Rate Change	1	\N
1242	m_depth_rate_subsampled_quantity_float32_m_s_1	m_depth_rate_subsampled	\N	Subsampled Depth Rate Measurement, m s-1	m s-1	\N
1243	m_depth_rejected_quantity_int8_1	m_depth_rejected	\N	Depth Measure is Rejected	1	\N
1244	m_depth_state_quantity_int8_1	m_depth_state	\N	Depth State	1	\N
1245	m_depth_subsampled_quantity_float32_m	m_depth_subsampled	\N	Subsampled Depth Measurement, m	m	\N
1246	m_device_drivers_called_abnormally_quantity_float32_1	m_device_drivers_called_abnormally	\N	Device Drivers Called Abnormally	1	\N
1247	m_device_error_quantity_float32_1	m_device_error	\N	Device Error	1	\N
1248	m_device_oddity_quantity_float32_1	m_device_oddity	\N	Device Oddity	1	\N
1249	m_device_warning_quantity_float32_1	m_device_warning	\N	Device Warning	1	\N
1250	m_de_oil_vol_quantity_float32_mL	m_de_oil_vol	\N	Measured Deep Electric Oil Volume, mL	mL	\N
1251	m_de_oil_vol_pot_voltage_quantity_float32_V	m_de_oil_vol_pot_voltage	\N	De Oil Vol PotVoltage, V	V	\N
1252	m_de_pump_fault_count_quantity_float32_1	m_de_pump_fault_count	\N	De Pump FaultCount	1	\N
1253	m_digifin_cmd_done_quantity_float32_1	m_digifin_cmd_done	\N	Digifin Commad Done	1	\N
1254	m_digifin_cmd_error_quantity_float32_1	m_digifin_cmd_error	\N	Digifin Command Error	1	\N
1255	m_digifin_leakdetect_reading_quantity_float32_1	m_digifin_leakdetect_reading	\N	Digifin Leak Detect Reading	1	\N
1256	m_digifin_motorstep_counter_quantity_float32_1	m_digifin_motorstep_counter	\N	Digifin Motor Step Counter	1	\N
1257	m_digifin_resp_data_quantity_float32_1	m_digifin_resp_data	\N	Digifin Respond Data	1	\N
1258	m_digifin_status_quantity_float32_1	m_digifin_status	\N	Digifin Status	1	\N
1259	m_disk_free_quantity_float32_Mbytes	m_disk_free	\N	Disk Free, mb	Mbytes	\N
1260	m_disk_usage_quantity_float32_Mbytes	m_disk_usage	\N	Disk Usage, mb	Mbytes	\N
1261	m_dist_to_wpt_quantity_float32_m	m_dist_to_wpt	\N	m_dist_to_wpt	m	\N
1262	m_dive_depth_quantity_float32_m	m_dive_depth	\N	Dive Depth	m	\N
1263	m_dive_tot_time_quantity_float32_s	m_dive_tot_time	\N	Amount Of Time To Complete Dive	s	\N
1264	m_dr_fix_time_quantity_float32_s	m_dr_fix_time	\N	Surface Drift Fix Time	s	\N
1265	m_dr_postfix_time_quantity_float32_s	m_dr_postfix_time	\N	Surface Drift Post Fix Time, s	s	\N
1266	m_dr_surf_x_lmc_quantity_float32_m	m_dr_surf_x_lmc	\N	m_dr_surf_x_lmc	m	\N
1267	m_dr_surf_y_lmc_quantity_float32_m	m_dr_surf_y_lmc	\N	m_dr_surf_y_lmc	m	\N
1268	m_dr_time_quantity_float32_s	m_dr_time	\N	m_dr_time	s	\N
1269	m_dr_x_actual_err_quantity_float32_m	m_dr_x_actual_err	\N	m_dr_x_actual_err	m	\N
1270	m_dr_x_ini_err_quantity_float32_m	m_dr_x_ini_err	\N	m_dr_x_ini_err	m	\N
1271	m_dr_x_postfix_drift_quantity_float32_m	m_dr_x_postfix_drift	\N	m_dr_x_postfix_drift	m	\N
1272	m_dr_x_ta_postfix_drift_quantity_float32_m	m_dr_x_ta_postfix_drift	\N	m_dr_x_ta_postfix_drift	m	\N
1273	m_dr_y_actual_err_quantity_float32_m	m_dr_y_actual_err	\N	m_dr_y_actual_err	m	\N
1274	m_dr_y_ini_err_quantity_float32_m	m_dr_y_ini_err	\N	m_dr_y_ini_err	m	\N
1275	m_dr_y_postfix_drift_quantity_float32_m	m_dr_y_postfix_drift	\N	m_dr_y_postfix_drift	m	\N
1276	m_dr_y_ta_postfix_drift_quantity_float32_m	m_dr_y_ta_postfix_drift	\N	m_dr_y_ta_postfix_drift	m	\N
1277	m_est_time_to_surface_quantity_float32_s	m_est_time_to_surface	\N	Estimate Time To Surface, s	s	\N
1278	m_fin_quantity_float32_rad	m_fin	\N	Measured Fin Angle, Radians	rad	\N
1279	m_final_water_vx_quantity_float32_m_s_1	m_final_water_vx	\N	Final Water VX, m s-1	m s-1	\N
1280	m_final_water_vy_quantity_float32_m_s_1	m_final_water_vy	\N	Final Water VY, m s-1	m s-1	\N
1281	m_fin_vel_quantity_float32_rad_s_1	m_fin_vel	\N	Measured Motor Velocity, rad s-1	rad s-1	\N
1282	m_fluid_pumped_quantity_float32_mL	m_fluid_pumped	\N	m_fluid_pumped	mL	\N
1283	m_fluid_pumped_aft_hall_voltage_quantity_float32_V	m_fluid_pumped_aft_hall_voltage	\N	Voltage From Aft Hall Sensor, V	V	\N
1284	m_fluid_pumped_fwd_hall_voltage_quantity_float32_V	m_fluid_pumped_fwd_hall_voltage	\N	Voltage From Forward Hall Sensor, V	V	\N
1285	m_fluid_pumped_vel_quantity_float32_mL_s_1	m_fluid_pumped_vel	\N	Measured Fluid Pumped Velocity, mL s-1	mL s-1	\N
1286	m_free_heap_quantity_float32_bytes	m_free_heap	\N	Free Heap, bytes	bytes	\N
1287	m_gps_dist_from_dr_quantity_float32_m	m_gps_dist_from_dr	\N	Distance From Dead Reckoned Position, m	m	\N
1288	m_gps_fix_x_lmc_quantity_float32_m	m_gps_fix_x_lmc	\N	GPS Fix X Imc, m	m	\N
1289	m_gps_fix_y_lmc_quantity_float32_m	m_gps_fix_y_lmc	\N	GPS Fix Y lmc, m	m	\N
1290	m_gps_full_status_quantity_int8_1	m_gps_full_status	\N	GPS Full Status	1	\N
1291	m_gps_heading_quantity_float32_rad	m_gps_heading	\N	GPS Heading, rad	rad	\N
1292	m_gps_ignored_lat_quantity_float64_degrees	m_gps_ignored_lat	\N	GPS Ignored Latitude, degrees	degrees	\N
1293	m_gps_ignored_lon_quantity_float64_degrees	m_gps_ignored_lon	\N	GPS Ignored Longitude, degrees	degrees	\N
1294	m_gps_invalid_lat_quantity_float64_degrees	m_gps_invalid_lat	\N	GPS Invalid Latitude, degrees	degrees	\N
1295	m_gps_invalid_lon_quantity_float64_degrees	m_gps_invalid_lon	\N	GPS Invalid Longitude, degrees	degrees	\N
1296	m_gps_lat_quantity_float32_degrees	m_gps_lat	\N	Measured GPS Latitude, degrees	degrees	\N
1297	m_gps_lon_quantity_float32_degrees	m_gps_lon	\N	Measured GPS Longitude, degrees	degrees	\N
1298	m_gps_mag_var_quantity_float32_rad	m_gps_mag_var	\N	GPS Mag Var, rad	rad	\N
1299	m_gps_num_satellites_quantity_float32_1	m_gps_num_satellites	\N	GPS Number of Satellites	1	\N
1300	m_gps_on_quantity_int8_1	m_gps_on	\N	GPS On	1	\N
1301	m_gps_postfix_x_lmc_quantity_float32_m	m_gps_postfix_x_lmc	\N	GPS Postfix X  Imc, m	m	\N
1302	m_gps_postfix_y_lmc_quantity_float32_m	m_gps_postfix_y_lmc	\N	GPS _Postfix Y Imc	m	\N
1303	m_gps_speed_quantity_float32_m_s_1	m_gps_speed	\N	GPS Speed, m s-1	m s-1	\N
1304	m_gps_status_quantity_int8_1	m_gps_status	\N	GPS Status	1	\N
1305	m_gps_toofar_lat_quantity_float64_degrees	m_gps_toofar_lat	\N	GPS Too Far Latitude, degrees	degrees	\N
1306	m_gps_toofar_lon_quantity_float64_degrees	m_gps_toofar_lon	\N	GPS Too Far Longitude, degrees	degrees	\N
1307	m_gps_uncertainty_quantity_float32_1	m_gps_uncertainty	\N	GPS Uncertainty	1	\N
1308	m_gps_utc_day_quantity_int8_bytes	m_gps_utc_day	\N	GPS UTC Day	bytes	\N
1309	m_gps_utc_hour_quantity_int8_bytes	m_gps_utc_hour	\N	GPS UTC Hour	bytes	\N
1310	m_gps_utc_minute_quantity_int8_bytes	m_gps_utc_minute	\N	GPS UTC Minute	bytes	\N
1311	m_gps_utc_month_quantity_int8_bytes	m_gps_utc_month	\N	GPS UTC Month	bytes	\N
1312	m_gps_utc_second_quantity_float32_1	m_gps_utc_second	\N	GPS UTC Second	1	\N
1313	m_gps_utc_year_quantity_int8_bytes	m_gps_utc_year	\N	GPS UTC Year	bytes	\N
1314	m_gps_x_lmc_quantity_float32_m	m_gps_x_lmc	\N	GPS X lmc, m	m	\N
1315	m_gps_y_lmc_quantity_float32_m	m_gps_y_lmc	\N	GPS Y lmc, m	m	\N
1316	m_hdg_derror_quantity_float32_rad_s_1	m_hdg_derror	\N	HDG Delt Error, rad s-1	rad s-1	\N
1317	m_hdg_error_quantity_float32_rad	m_hdg_error	\N	HDG Error, rad	rad	\N
1318	m_hdg_ierror_quantity_float32_rad_sec	m_hdg_ierror	\N	HDG Integrated Error, rad-sec	rad-sec	\N
1319	m_hdg_rate_quantity_float32_rad_s_1	m_hdg_rate	\N	HDG Rate, rad s-1	rad s-1	\N
1320	m_heading_quantity_float32_rad	m_heading	\N	Measured Heading, rad	rad	\N
1321	m_initial_water_vx_quantity_float32_m_s_1	m_initial_water_vx	\N	Initial Water VX, m s-1	m s-1	\N
1322	m_initial_water_vy_quantity_float32_m_s_1	m_initial_water_vy	\N	Initial Water VY, m s-1	m s-1	\N
1323	m_iridium_attempt_num_quantity_float32_1	m_iridium_attempt_num	\N	Iridium Attempt Num	1	\N
1324	m_iridium_call_num_quantity_float32_1	m_iridium_call_num	\N	Iridium Call Num	1	\N
1325	m_iridium_connected_quantity_int8_1	m_iridium_connected	\N	Iridium Connected	1	\N
1326	m_iridium_console_on_quantity_int8_1	m_iridium_console_on	\N	Iridium Console On	1	\N
1327	m_iridium_dialed_num_quantity_float32_1	m_iridium_dialed_num	\N	Iridium Dialed Num	1	\N
1328	m_iridium_on_quantity_int8_1	m_iridium_on	\N	Iridium On	1	\N
1329	m_iridium_redials_quantity_float32_1	m_iridium_redials	\N	Iridium Redials	1	\N
1330	m_iridium_signal_strength_quantity_float32_1	m_iridium_signal_strength	\N	Iridium Signal Strength	1	\N
1331	m_iridium_status_quantity_int8_1	m_iridium_status	\N	Iridium Status	1	\N
1332	m_iridium_waiting_redial_delay_quantity_int8_1	m_iridium_waiting_redial_delay	\N	Iridium Waiting RedialDelay	1	\N
1333	m_iridium_waiting_registration_quantity_int8_1	m_iridium_waiting_registration	\N	Iridium Waiting Registration	1	\N
1334	m_is_ballast_pump_moving_quantity_int8_1	m_is_ballast_pump_moving	\N	Is Ballast Pump Moving	1	\N
1335	m_is_battpos_moving_quantity_int8_1	m_is_battpos_moving	\N	Is Battpos Moving	1	\N
1336	m_is_battroll_moving_quantity_int8_1	m_is_battroll_moving	\N	Is Battroll Moving	1	\N
1337	m_is_de_pump_moving_quantity_int8_1	m_is_de_pump_moving	\N	Is De Pump Moving	1	\N
1338	m_is_fin_moving_quantity_int8_1	m_is_fin_moving	\N	Is Fin Moving	1	\N
1339	m_is_fpitch_pump_moving_quantity_int8_1	m_is_fpitch_pump_moving	\N	Is Fpitch Pump Moving	1	\N
1340	m_is_speed_estimated_quantity_int8_1	m_is_speed_estimated	\N	Is Speed Estimated	1	\N
1341	m_is_thermal_valve_moving_quantity_int8_1	m_is_thermal_valve_moving	\N	Is Thermal Value Moving	1	\N
1342	m_last_yo_time_quantity_float32_s	m_last_yo_time	\N	Last Yo Time, s	s	\N
1343	m_lat_quantity_float32_degrees	m_lat	\N	Derived latitude, degrees	degrees	\N
1344	m_leak_quantity_int8_1	m_leak	\N	m_leak	1	\N
1345	m_leakdetect_voltage_quantity_float32_V	m_leakdetect_voltage	\N	Leak Detect Voltage, V	V	\N
1346	m_leakdetect_voltage_forward_quantity_float32_V	m_leakdetect_voltage_forward	\N	Leak Detect Voltage Forward, V	V	\N
1347	m_leak_forward_quantity_int8_1	m_leak_forward	\N	Leak Forward	1	\N
1348	m_lithium_battery_relative_charge_quantity_float32_%	m_lithium_battery_relative_charge	\N	Lithium Battery Relative Charge, %	%	\N
1349	m_lithium_battery_status_quantity_float32_1	m_lithium_battery_status	\N	Lithium Battery Status	1	\N
1350	m_lithium_battery_time_to_charge_quantity_float32_min	m_lithium_battery_time_to_charge	\N	Lithium Battery Time to Charge, min	min	\N
1351	m_lithium_battery_time_to_discharge_quantity_float32_min	m_lithium_battery_time_to_discharge	\N	Lithium Battery Time to Discharge, min	min	\N
1352	m_lon_quantity_float32_degrees	m_lon	\N	Derived longitude, degrees	degrees	\N
1353	m_min_free_heap_quantity_float32_bytes	m_min_free_heap	\N	Minimun Free Heap, bytes	bytes	\N
1354	m_min_spare_heap_quantity_float32_bytes	m_min_spare_heap	\N	Minimun Spare Heap, bytes	bytes	\N
1355	m_mission_avg_speed_climbing_quantity_float32_m_s_1	m_mission_avg_speed_climbing	\N	Mission Avgerage Speed Climbing, m s-1	m s-1	\N
1356	m_mission_avg_speed_diving_quantity_float32_m_s_1	m_mission_avg_speed_diving	\N	Mission Avgerage Speed Diving, m s-1	m s-1	\N
1357	m_mission_start_time_quantity_float64_seconds_since_1970_01_01	m_mission_start_time	\N	Mission Start Time, UTC	seconds since 1970-01-01	\N
1358	m_num_half_yos_in_segment_quantity_float32_1	m_num_half_yos_in_segment	\N	m_num_half_yos_in_segment	1	\N
1359	m_pitch_quantity_float32_rad	m_pitch	\N	Measured Pitch, Radians	rad	\N
1360	m_pitch_energy_quantity_float32_J	m_pitch_energy	\N	Pitch Energy, J	J	\N
1361	m_pitch_error_quantity_float32_rad	m_pitch_error	\N	Pitch Error, rad	rad	\N
1362	m_present_secs_into_mission_quantity_float32_s	m_present_secs_into_mission	\N	Elapsed mission time, Secs	s	\N
1433	sci_bsipar_supply_volts_quantity_float32_V	sci_bsipar_supply_volts	\N	Bsipar Supply Volts, V	V	\N
1363	m_present_time_quantity_float64_seconds_since_1970_01_01	m_present_time	\N	Time at the start of the cycle, UTC	seconds since 1970-01-01	\N
1364	m_pressure_quantity_float32_bar	m_pressure	\N	Pressure, bar	bar	\N
1365	m_pressure_raw_voltage_sample0_quantity_float32_V	m_pressure_raw_voltage_sample0	\N	Pressure Raw Voltage Sample 0, V	V	\N
1366	m_pressure_raw_voltage_sample19_quantity_float32_V	m_pressure_raw_voltage_sample19	\N	Pressure Raw Voltage Sample19, V	V	\N
1367	m_pressure_voltage_quantity_float32_V	m_pressure_voltage	\N	Pressure Voltage, V	V	\N
1368	m_raw_altitude_quantity_float32_m	m_raw_altitude	\N	Raw Altitude, m	m	\N
1369	m_raw_altitude_rejected_quantity_int8_1	m_raw_altitude_rejected	\N	Raw Altitude Rejected	1	\N
1370	m_roll_quantity_float32_rad	m_roll	\N	Roll, deg	rad	\N
1371	m_science_clothesline_lag_quantity_float32_s	m_science_clothesline_lag	\N	Science Clothesline Lag, s	s	\N
1372	m_science_on_quantity_int8_1	m_science_on	\N	Science On	1	\N
1373	m_science_ready_for_consci_quantity_int8_1	m_science_ready_for_consci	\N	Clothesline Ready For Consci	1	\N
1374	m_science_sent_some_data_quantity_float32_1	m_science_sent_some_data	\N	Science Sent Some Data	1	\N
1375	m_science_sync_time_quantity_float64_seconds_since_1970_01_01	m_science_sync_time	\N	Science Sync Time, UTC	seconds since 1970-01-01	\N
1376	m_science_unreadiness_for_consci_quantity_int8_1	m_science_unreadiness_for_consci	\N	Science Unreadiness For Consci	1	\N
1377	m_spare_heap_quantity_float32_bytes	m_spare_heap	\N	Spare Heap, bytes	bytes	\N
1378	m_speed_quantity_float32_m_s_1	m_speed	\N	Measured Speed, m/s	m s-1	\N
1379	m_stable_comms_quantity_int8_1	m_stable_comms	\N	Commands are Stable	1	\N
1380	m_strobe_ctrl_quantity_int8_1	m_strobe_ctrl	\N	Strobe Light	1	\N
1381	m_surface_est_cmd_quantity_float32_1	m_surface_est_cmd	\N	Commanded To Surface	1	\N
1382	m_surface_est_ctd_quantity_float32_1	m_surface_est_ctd	\N	Ctd Pressure	1	\N
1383	m_surface_est_fw_quantity_float32_1	m_surface_est_fw	\N	FreewaveHas Carrier	1	\N
1384	m_surface_est_gps_quantity_float32_1	m_surface_est_gps	\N	GPS Talking To Satellite	1	\N
1385	m_surface_est_irid_quantity_float32_1	m_surface_est_irid	\N	Iridium Has Carrier	1	\N
1386	m_surface_est_total_quantity_float32_1	m_surface_est_total	\N	Sum Of Surface Estimate	1	\N
1387	m_system_clock_lags_gps_quantity_float32_s	m_system_clock_lags_gps	\N	System Clock Lags GPS,s	s	\N
1388	m_tcm3_is_calibrated_quantity_int8_1	m_tcm3_is_calibrated	\N	Compass Calibration Status Flag	1	\N
1389	m_tcm3_magbearth_quantity_float32_uT	m_tcm3_magbearth	\N	Earth's Magnetic Field, uT	uT	\N
1390	m_tcm3_poll_time_quantity_float32_ms	m_tcm3_poll_time	\N	TCM3 Poll Time, ms	ms	\N
1391	m_tcm3_recv_start_time_quantity_float32_ms	m_tcm3_recv_start_time	\N	TCM3 Recv Start Time, ms	ms	\N
1392	m_tcm3_recv_stop_time_quantity_float32_ms	m_tcm3_recv_stop_time	\N	TCM3 Recv Stop Time, ms	ms	\N
1393	m_tcm3_stddeverr_quantity_float32_uT	m_tcm3_stddeverr	\N	TCM3 Standard Deviation Error, uT	uT	\N
1394	m_tcm3_xcoverage_quantity_float32_%	m_tcm3_xcoverage	\N	TCM3 X Coverage, %	%	\N
1395	m_tcm3_ycoverage_quantity_float32_%	m_tcm3_ycoverage	\N	TCM3 Y Coverage, %	%	\N
1396	m_tcm3_zcoverage_quantity_float32_%	m_tcm3_zcoverage	\N	TCM3 Z Coverage, %	%	\N
1397	m_thermal_acc_pres_quantity_float32_bar	m_thermal_acc_pres	\N	m_thermal_acc_pres	bar	\N
1398	m_thermal_acc_pres_voltage_quantity_float32_V	m_thermal_acc_pres_voltage	\N	m_thermal_acc_pres_voltage	V	\N
1399	m_thermal_acc_vol_quantity_float32_mL	m_thermal_acc_vol	\N	m_thermal_acc_vol	mL	\N
1400	m_thermal_enuf_acc_vol_quantity_int8_1	m_thermal_enuf_acc_vol	\N	m_thermal_enuf_acc_vol	1	\N
1401	m_thermal_pump_quantity_int8_1	m_thermal_pump	\N	m_thermal_pump	1	\N
1402	m_thermal_updown_quantity_int8_1	m_thermal_updown	\N	m_thermal_updown	1	\N
1403	m_thermal_valve_quantity_int8_1	m_thermal_valve	\N	m_thermal_valve	1	\N
1404	m_time_til_wpt_quantity_float32_s	m_time_til_wpt	\N	m_time_til_wpt	s	\N
1405	m_tot_ballast_pumped_energy_quantity_float32_kJ	m_tot_ballast_pumped_energy	\N	Ballast Pumped Energy, kJ	kJ	\N
1406	m_tot_horz_dist_quantity_float32_km	m_tot_horz_dist	\N	Horizontal DIstance, km	km	\N
1407	m_tot_num_inflections_quantity_float32_1	m_tot_num_inflections	\N	Number of Inflections	1	\N
1408	m_tot_on_time_quantity_float32_d	m_tot_on_time	\N	Powered On Time, d	d	\N
1409	m_vacuum_quantity_float32_inHg	m_vacuum	\N	Vacuum, inHg	inHg	\N
1410	m_vehicle_temp_quantity_float32_deg_C	m_vehicle_temp	\N	Vehicle Temperature, deg_C	deg_C	\N
1411	m_veh_overheat_quantity_int8_1	m_veh_overheat	\N	Vehicle Over Heat	1	\N
1412	m_veh_temp_quantity_float32_deg_C	m_veh_temp	\N	Veh Temperture, deg_C	deg_C	\N
1413	m_vmg_to_wpt_quantity_float32_m_s_1	m_vmg_to_wpt	\N	m_vmg_to_wpt	m s-1	\N
1414	m_vx_lmc_quantity_float32_m_s_1	m_vx_lmc	\N	m_vx_lmc	m s-1	\N
1415	m_vy_lmc_quantity_float32_m_s_1	m_vy_lmc	\N	m_vy_lmc	m s-1	\N
1416	m_water_cond_quantity_float32_S_m_1	m_water_cond	\N	Water Conductivity, S m-1	S m-1	\N
1417	m_water_delta_vx_quantity_float32_m_s_1	m_water_delta_vx	\N	Water Delta VX, m s-1	m s-1	\N
1418	m_water_delta_vy_quantity_float32_m_s_1	m_water_delta_vy	\N	Water Delta VY, m s-1	m s-1	\N
1419	m_water_depth_quantity_float32_m	m_water_depth	\N	Water Depth, m	m	\N
1420	m_water_pressure_quantity_float32_bar	m_water_pressure	\N	Water Pressure, bar	bar	\N
1421	m_water_temp_quantity_float32_deg_C	m_water_temp	\N	Water Temperature, deg_C	deg_C	\N
1422	m_water_vx_quantity_float32_m_s_1	m_water_vx	\N	Measured Water Velocity: X, m/s	m s-1	\N
1423	m_water_vy_quantity_float32_m_s_1	m_water_vy	\N	Measured Water Velocity: Y, m/s	m s-1	\N
1424	m_why_started_quantity_int8_1	m_why_started	\N	How GliderDos Started	1	\N
1425	m_x_lmc_quantity_float32_m	m_x_lmc	\N	m_x_lmc	m	\N
1426	m_y_lmc_quantity_float32_m	m_y_lmc	\N	m_y_lmc	m	\N
1427	x_last_wpt_lat_quantity_float32_degrees	x_last_wpt_lat	\N	x_last_wpt_lat	degrees	\N
1428	x_last_wpt_lon_quantity_float32_degrees	x_last_wpt_lon	\N	x_last_wpt_lon	degrees	\N
1429	x_system_clock_adjusted_quantity_float32_s	x_system_clock_adjusted	\N	System Clock Adjusted, s	s	\N
1430	sci_bsipar_is_installed_quantity_int8_1	sci_bsipar_is_installed	\N	Bsipar IS Installed	1	\N
1431	sci_bsipar_par_quantity_float32_umol_photons_m_2_s_1	sci_bsipar_par	\N	Photosynthetic Active Radiation (PAR), uEinsteins m-2 s-1	umol photons m-2 s-1	\N
1432	sci_bsipar_sensor_volts_quantity_float32_V	sci_bsipar_sensor_volts	\N	Bsipar Sensor Volts, V	V	\N
1434	sci_bsipar_temp_quantity_float32_deg_C	sci_bsipar_temp	\N	Bsipar Temperature, deg_C	deg_C	\N
1435	sci_bsipar_timestamp_quantity_float64_seconds_since_1970_01_01	sci_bsipar_timestamp	\N	Bsipar Timestamp, UTC	seconds since 1970-01-01	\N
1436	sci_ctd41cp_is_installed_quantity_int8_1	sci_ctd41cp_is_installed	\N	Ctd41cp is Installed	1	\N
1437	sci_ctd41cp_timestamp_quantity_float64_seconds_since_1970_01_01	sci_ctd41cp_timestamp	\N	Ctd41cp Timestamp, UTC	seconds since 1970-01-01	\N
1438	sci_flbbcd_bb_ref_quantity_float32_1	sci_flbbcd_bb_ref	\N	sci_flbbcd_bb_ref	1	\N
1439	sci_flbbcd_bb_sig_quantity_float32_1	sci_flbbcd_bb_sig	\N	sci_flbbcd_bb_sig	1	\N
1440	sci_flbbcd_bb_units_quantity_float32_m_1_sr_1	sci_flbbcd_bb_units	\N	Volume Scattering Function, Beta(117,650), m-1 sr-1	m-1 sr-1	\N
1441	sci_flbbcd_cdom_ref_quantity_float32_1	sci_flbbcd_cdom_ref	\N	thermistor Temperature Counts	1	\N
1442	sci_flbbcd_cdom_sig_quantity_float32_1	sci_flbbcd_cdom_sig	\N	sci_flbbcd_cdom_sig	1	\N
1443	sci_flbbcd_cdom_units_quantity_float32_ppb	sci_flbbcd_cdom_units	\N	Fluorometric CDOM Concentration, ppb	ppb	\N
1444	sci_flbbcd_chlor_ref_quantity_float32_1	sci_flbbcd_chlor_ref	\N	sci_flbbcd_chlor_ref	1	\N
1445	sci_flbbcd_chlor_sig_quantity_float32_1	sci_flbbcd_chlor_sig	\N	sci_flbbcd_chlor_sig	1	\N
1446	sci_flbbcd_chlor_units_quantity_float32_ug_L_1	sci_flbbcd_chlor_units	\N	Estimated Chlorophyll, ug L-1	ug L-1	\N
1447	sci_flbbcd_is_installed_quantity_int8_1	sci_flbbcd_is_installed	\N	FLORD/FLORT is Installed	1	\N
1448	sci_flbbcd_therm_quantity_float32_1	sci_flbbcd_therm	\N	sci_flbbcd_therm	1	\N
1449	sci_flbbcd_timestamp_quantity_float64_seconds_since_1970_01_01	sci_flbbcd_timestamp	\N	sci_flbbcd_timestamp, UTC	seconds since 1970-01-01	\N
1450	sci_m_disk_free_quantity_float32_Mbytes	sci_m_disk_free	\N	Disk Space Currently Free on Science, Mbytes	Mbytes	\N
1451	sci_m_disk_usage_quantity_float32_Mbytes	sci_m_disk_usage	\N	Disk Space Currently Used on Science, Mbytes	Mbytes	\N
1452	sci_m_free_heap_quantity_float32_bytes	sci_m_free_heap	\N	sci_m_free_heap	bytes	\N
1453	sci_m_min_free_heap_quantity_float32_bytes	sci_m_min_free_heap	\N	sci_m_min_free_heap	bytes	\N
1454	sci_m_min_spare_heap_quantity_float32_bytes	sci_m_min_spare_heap	\N	sci_m_min_spare_heap	bytes	\N
1455	sci_m_present_secs_into_mission_quantity_float32_s	sci_m_present_secs_into_mission	\N	Elapsed mission time based on science derived start time, Secs	s	\N
1456	sci_m_present_time_quantity_float64_seconds_since_1970_01_01	sci_m_present_time	\N	Science derived time at the start of the cycle, UTC	seconds since 1970-01-01	\N
1457	sci_m_science_on_quantity_int8_1	sci_m_science_on	\N	sci_m_science_on	1	\N
1458	sci_m_spare_heap_quantity_float32_bytes	sci_m_spare_heap	\N	sci_m_spare_heap	bytes	\N
1459	sci_oxy3835_wphase_bamp_quantity_float32_1	sci_oxy3835_wphase_bamp	\N	sci_oxy3835_wphase_bamp	1	\N
1460	sci_oxy3835_wphase_bphase_quantity_float32_1	sci_oxy3835_wphase_bphase	\N	sci_oxy3835_wphase_bphase	1	\N
1461	sci_oxy3835_wphase_bpot_quantity_float32_1	sci_oxy3835_wphase_bpot	\N	sci_oxy3835_wphase_bpot	1	\N
1462	sci_oxy3835_wphase_dphase_quantity_float32_1	sci_oxy3835_wphase_dphase	\N	sci_oxy3835_wphase_dphase	1	\N
1463	sci_oxy3835_wphase_is_installed_quantity_int8_1	sci_oxy3835_wphase_is_installed	\N	DOSTA is Installed	1	\N
1464	sci_oxy3835_wphase_oxygen_quantity_float32_mL_L_1	sci_oxy3835_wphase_oxygen	\N	sci_oxy3835_wphase_oxygen	mL L-1	\N
1465	sci_oxy3835_wphase_ramp_quantity_float32_1	sci_oxy3835_wphase_ramp	\N	sci_oxy3835_wphase_ramp	1	\N
1466	sci_oxy3835_wphase_rawtemp_quantity_float32_1	sci_oxy3835_wphase_rawtemp	\N	sci_oxy3835_wphase_rawtemp	1	\N
1467	sci_oxy3835_wphase_rphase_quantity_float32_1	sci_oxy3835_wphase_rphase	\N	sci_oxy3835_wphase_rphase	1	\N
1468	sci_oxy3835_wphase_saturation_quantity_float32_%	sci_oxy3835_wphase_saturation	\N	sci_oxy3835_wphase_saturation	%	\N
1469	sci_oxy3835_wphase_temp_quantity_float32_1	sci_oxy3835_wphase_temp	\N	sci_oxy3835_wphase_temp	1	\N
1470	sci_oxy3835_wphase_timestamp_quantity_float64_seconds_since_1970_01_01	sci_oxy3835_wphase_timestamp	\N	sci_oxy3835_wphase_timestamp, UTC	seconds since 1970-01-01	\N
1471	sci_oxy4_c1amp_quantity_float32_1	sci_oxy4_c1amp	\N	Sci Oxy4330f C1 Amp	1	\N
1472	sci_oxy4_c1rph_quantity_float32_1	sci_oxy4_c1rph	\N	Sci Oxy4330f C1 Rph	1	\N
1473	sci_oxy4_c2amp_quantity_float32_1	sci_oxy4_c2amp	\N	Sci Oxy4330f C2 Amp	1	\N
1474	sci_oxy4_c2rph_quantity_float32_1	sci_oxy4_c2rph	\N	Sci Oxy4330f C2 Rph	1	\N
1475	sci_oxy4_calphase_quantity_float32_degrees	sci_oxy4_calphase	\N	Sci Oxy4330f Calibration Phase	degrees	\N
1476	sci_oxy4_is_installed_quantity_int8_1	sci_oxy4_is_installed	\N	Sci Oxy4330f Is Installed	1	\N
1477	sci_oxy4_oxygen_quantity_float32_umol_L_1	sci_oxy4_oxygen	\N	Estimated Oxygen Concentration, umol/L	umol L-1	\N
1478	sci_oxy4_rawtemp_quantity_float32_1	sci_oxy4_rawtemp	\N	Oxy4330f Raw Temperature	1	\N
1479	sci_oxy4_saturation_quantity_float32_%	sci_oxy4_saturation	\N	Estimated Percentage Oxygen Saturation, % 	%	\N
1480	sci_oxy4_tcphase_quantity_float32_1	sci_oxy4_tcphase	\N	Sci Oxy4330f TC Phase	1	\N
1481	sci_oxy4_temp_quantity_float32_1	sci_oxy4_temp	\N	Sci Oxy4330f Temperature	1	\N
1482	sci_oxy4_timestamp_quantity_float64_1	sci_oxy4_timestamp	\N	Sci Oxy4330f Timestamp	1	\N
1483	sci_reqd_heartbeat_quantity_float32_s	sci_reqd_heartbeat	\N	Reqd Heartbeat	s	\N
1484	sci_software_ver_quantity_float32_1	sci_software_ver	\N	Sci Software Version	1	\N
1485	sci_wants_comms_quantity_int8_1	sci_wants_comms	\N	Science Computer Wants Direct Comms	1	\N
1486	sci_wants_surface_quantity_int8_1	sci_wants_surface	\N	Science Wants to Surface	1	\N
1487	sci_water_cond_quantity_float32_S_m_1	sci_water_cond	\N	Conductivity, S/m	S m-1	\N
1488	sci_water_pressure_quantity_float32_bar	sci_water_pressure	\N	Pressure, bars	bar	\N
1489	sci_water_temp_quantity_float32_deg_C	sci_water_temp	\N	Temperature, degrees C	deg_C	\N
1490	sci_x_disk_files_removed_quantity_float32_1	sci_x_disk_files_removed	\N	sci_x_disk_files_removed	1	\N
1491	sci_x_sent_data_files_quantity_float32_1	sci_x_sent_data_files	\N	Number of Log Files Sent Via Last Zmodem Batch	1	\N
1492	sci_flbb_bb_units_quantity_float32_m_1_sr_1	sci_flbb_bb_units	\N	Volume Scattering Function, Beta(117,650), m-1 sr-1	m-1 sr-1	\N
1493	sci_flbb_chlor_units_quantity_float32_ug_L_1	sci_flbb_chlor_units	\N	Estimated Chlorophyll, ug L-1	ug L-1	\N
1494	x_low_power_status_quantity_float32_1	x_low_power_status	\N	Low Power Status	1	\N
1495	thermistor_temperature_quantity_float32_counts	thermistor_temperature	\N	Thermistor Temperature Counts	counts	\N
1496	sbe16_tempwat_function_float32_deg_C	sbe16_tempwat	\N	ctd_sbe16plus_tempwat	deg_C	\N
1497	sci_dvl_is_installed_quantity_int8_1	sci_dvl_is_installed	\N	sci_dvl_is_installed	1	\N
1498	sbe16_preswat_function_float32_dbar	sbe16_preswat	\N	ctd_sbe16plus_preswat	dbar	\N
1499	sbe16_condwat_function_float32_S_m_1	sbe16_condwat	\N	ctd_sbe16plus_condwat	S m-1	\N
1500	sbe16_pracsal_function_float32_1	sbe16_pracsal	\N	ctd_sbe16plus_pracsal	1	\N
1501	sbe16_density_function_float32_kg_m_3	sbe16_density	\N	ctd_sbe16plus_density	kg m-3	\N
1502	raw_velocity_a_quantity_float32_counts	raw_velocity_a	\N	Raw Velocity A	counts	\N
1503	raw_velocity_b_quantity_float32_counts	raw_velocity_b	\N	Raw Velocity B	counts	\N
1504	raw_velocity_c_quantity_float32_counts	raw_velocity_c	\N	Raw Velocity C	counts	\N
1505	raw_velocity_d_quantity_float32_counts	raw_velocity_d	\N	Raw Velocity D	counts	\N
1506	velocity_east_quantity_float32_cm_s_1	velocity_east	\N	Corrected East velocity component in earth coordinates, in cm/s	cm s-1	\N
1507	velocity_north_quantity_float32_cm_s_1	velocity_north	\N	Corrected North velocity component in earth coordinates, in cm/s	cm s-1	\N
1508	velocity_up_quantity_float32_cm_s_1	velocity_up	\N	Corrected Up velocity component in earth coordinates, in cm/s	cm s-1	\N
1509	corr_velocity_east_function_float32_m_s_1	corr_velocity_east	\N	East components of velocity, corrected for magnetic\nvariation, in m/s	m s-1	\N
1510	corr_velocity_north_function_float32_m_s_1	corr_velocity_north	\N	North components of velocity, corrected for magnetic\nvariation, in m/s	m s-1	\N
1511	corr_velocity_up_function_float32_m_s_1	corr_velocity_up	\N	Up components of velocity, corrected for magnetic\nvariation, in m/s	m s-1	\N
1512	oxygen_quantity_float64_Hz	oxygen	\N	Oxygen, Hz	Hz	\N
1513	conductivity_quantity_float32_mS_cm_1	conductivity	\N	Conductivity, mS cm-1	mS cm-1	\N
1514	sparse_float_quantity_float32_1	sparse_float	\N	Sparse Value	1	\N
1515	sparse_double_quantity_float64_1	sparse_double	\N	Sparse Double	1	\N
1516	sparse_int_quantity_int64_1	sparse_int	\N	Sparse Integer	1	\N
1517	lat_quantity_float64_degree_north	lat	\N	Latitude	degree_north	\N
1518	lon_quantity_float64_degree_east	lon	\N	Longitude	degree_east	\N
1519	inductive_id_quantity_uint8_1	inductive_id	\N	Inductive ID	1	\N
1520	record_time_1904_uint32_quantity_uint32_seconds_since_1904_01_01	record_time_1904_uint32	\N	Record Time, seconds since 1904-01-01	seconds since 1904-01-01	\N
1521	sci_water_pracsal_function_float32_1	sci_water_pracsal	\N	Practical Salinity (seawater salinity, PSS-78) [unitless]	1	\N
1522	ctdmo_sci_water_pracsal_function_float32_1	ctdmo_sci_water_pracsal	\N	Practical Salinity (seawater salinity, PSS-78) [unitless]	1	\N
1523	adcps_pd12_eastward_seawater_velocity_function_float32_m_s_1	adcps_pd12_eastward_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
1524	adcps_pd12_northward_seawater_velocity_function_float32_m_s_1	adcps_pd12_northward_seawater_velocity	\N	Northward Sea Water Velocity, m s-1	m s-1	\N
1525	adcps_pd12_upward_seawater_velocity_function_float32_m_s_1	adcps_pd12_upward_seawater_velocity	\N	Upward Sea Water Velocity, m s-1	m s-1	\N
1526	adcps_pd12_error_velocity_function_float32_m_s_1	adcps_pd12_error_velocity	\N	Error Velocity, m s-1	m s-1	\N
1527	mflm_fluorometric_cdom_function_float32_ppb	mflm_fluorometric_cdom	\N	Fluorometric CDOM Concentration, ppb	ppb	\N
1528	wfp_time_on_quantity_uint32_seconds_since_1970_01_01	wfp_time_on	\N	Time On, UTC	seconds since 1970-01-01	\N
1529	wfp_time_off_quantity_uint32_seconds_since_1970_01_01	wfp_time_off	\N	Time Off, UTC	seconds since 1970-01-01	\N
1530	wfp_profile_number_quantity_uint32_counts	wfp_profile_number	\N	Profile Number, counts	counts	\N
1531	wfp_number_samples_quantity_uint32 _counts	wfp_number_samples	\N	Number Samples, counts	counts	\N
1532	par_val_v_quantity_float32_mV	par_val_v	\N	PARAD Voltage, mV	mV	\N
1533	wfp_sensor_start_quantity_uint32_seconds_since_1970_01_01	wfp_sensor_start	\N	Sensor Start Time, UTC	seconds since 1970-01-01	\N
1534	wfp_profile_start_quantity_uint32_seconds_since_1970_01_01	wfp_profile_start	\N	Profile Start Time, UTC	seconds since 1970-01-01	\N
1535	wfp_indicator_quantity_int32_1	wfp_indicator	\N	Message Type Indicator, value	1	\N
1536	wfp_ramp_status_quantity_int16_1	wfp_ramp_status	\N	Ramp Status, value	1	\N
1537	wfp_profile_status_quantity_int16_1	wfp_profile_status	\N	Profile Status, value	1	\N
1538	wfp_sensor_stop_quantity_uint32_seconds_since_1970_01_01	wfp_sensor_stop	\N	Sensor Stop Time, UTC	seconds since 1970-01-01	\N
1539	wfp_profile_stop_quantity_uint32_seconds_since_1970_01_01	wfp_profile_stop	\N	Profile Stop Time, UTC	seconds since 1970-01-01	\N
1540	wfp_prof_current_quantity_float32_mA	wfp_prof_current	\N	Profile Current, mA	mA	\N
1541	wfp_prof_voltage_quantity_float32_V	wfp_prof_voltage	\N	Profile Voltage, V	V	\N
1542	wfp_prof_pressure_quantity_float32_dbar	wfp_prof_pressure	\N	Profile Pressure, dbar	dbar	\N
1543	rte_coulombs_quantity_float32_C	rte_coulombs	\N	Coulombs, C	C	\N
1544	rte_avg_q_current_quantity_float32_A	rte_avg_q_current	\N	Average q  Current, A	A	\N
1545	rte_avg_voltage_quantity_float32_V	rte_avg_voltage	\N	Average  Voltage, V	V	\N
1546	rte_avg_supply_voltage_quantity_float32_V	rte_avg_supply_voltage	\N	Average Supply Voltage, V	V	\N
1547	rte_hits_quantity_uint16_counts	rte_hits	\N	Hits, counts	counts	\N
1548	rte_state_quantity_int16_1	rte_state	\N	State, 1=Active, 0=NotActive	1	\N
1549	mopak_accelx_quantity_float32_g0	mopak_accelx	\N	Acceleration x, g0	g0	\N
1550	mopak_accely_quantity_float32_g0	mopak_accely	\N	Acceleration y, g0	g0	\N
1551	mopak_accelz_quantity_float32_g0	mopak_accelz	\N	Acceleration z, g0	g0	\N
1552	mopak_ang_ratex_quantity_float32_rad_s_1	mopak_ang_ratex	\N	Angular Rate x, rad s-1	rad s-1	\N
1553	mopak_ang_ratey_quantity_float32_rad_s_1	mopak_ang_ratey	\N	Angular Rate y.rad s-1	rad s-1	\N
1554	mopak_ang_ratez_quantity_float32_rad_s_1	mopak_ang_ratez	\N	Angular Rate z, rad s-1	rad s-1	\N
1555	mopak_magx_quantity_float32_Gs	mopak_magx	\N	Magnetometer Vector x, Gs	Gs	\N
1556	mopak_magy_quantity_float32_Gs	mopak_magy	\N	Magnetometer Vector y, Gs	Gs	\N
1557	mopak_magz_quantity_float32_Gs	mopak_magz	\N	Magnetometer Vector z, Gs	Gs	\N
1558	mopak_timer_quantity_uint32_counts	mopak_timer	\N	Timer, counts	counts	\N
1559	mopak_roll_quantity_float32_degrees	mopak_roll	\N	Roll, deg	degrees	\N
1560	mopak_pitch_quantity_float32_degrees	mopak_pitch	\N	Pitch, deg	degrees	\N
1561	mopak_yaw_quantity_float32_degrees	mopak_yaw	\N	Yaw, deg	degrees	\N
1562	vel3d_k_temp_c_quantity_int16_cdeg_C	vel3d_k_temp_c	\N	Temperature, centidegrees Celsius	cdeg_C	\N
1563	vel3d_k_heading_quantity_uint16_ddegrees	vel3d_k_heading	\N	Heading, decidegrees	ddegrees	\N
1564	vel3d_k_pitch_quantity_int16_ddegrees	vel3d_k_pitch	\N	Pitch, decidegrees	ddegrees	\N
1565	vel3d_k_roll_quantity_int16_ddegrees	vel3d_k_roll	\N	Roll, decidegrees	ddegrees	\N
1566	vel3d_k_v_scale_quantity_int8_counts	vel3d_k_v_scale	\N	Velocity Scale, counts	counts	\N
1567	vel3d_k_vel0_quantity_int16_counts	vel3d_k_vel0	\N	Raw Velocity 0, counts	counts	\N
1568	vel3d_k_vel1_quantity_int16_counts	vel3d_k_vel1	\N	Raw Velocity 1, counts	counts	\N
1569	vel3d_k_vel2_quantity_int16_counts	vel3d_k_vel2	\N	Raw Velocity 2, counts	counts	\N
1570	vel3d_k_amp0_quantity_uint8_counts	vel3d_k_amp0	\N	Amplitude0, counts	counts	\N
1571	vel3d_k_amp1_quantity_uint8_counts	vel3d_k_amp1	\N	Amplitude1, counts	counts	\N
1572	vel3d_k_amp2_quantity_uint8_counts	vel3d_k_amp2	\N	Amplitude2, counts	counts	\N
1573	vel3d_k_number_of_records_quantity_uint16_counts	vel3d_k_number_of_records	\N	Number of Records, counts	counts	\N
1574	vel3d_k_time_on_quantity_uint32_s	vel3d_k_time_on	\N	Time Sensor Start, seconds	s	\N
1575	vel3d_k_time_off_quantity_uint32_s	vel3d_k_time_off	\N	Time Sensor Stop, seconds	s	\N
1576	wfp_timestamp_quantity_uint32_seconds_since_1970_01_01	wfp_timestamp	\N	Wire Following Profiler Timestamp, UTC	seconds since 1970-01-01	\N
1577	adcps_jln_record_quantity_uint64_1	adcps_jln_record	\N	Record Number, count	1	\N
1578	adcps_jln_number_quantity_uint32_1	adcps_jln_number	\N	Ensemble Number, count	1	\N
1579	adcps_jln_unit_id_quantity_uint8_1	adcps_jln_unit_id	\N	Unit ID, count	1	\N
1580	adcps_jln_fw_vers_quantity_uint8_1	adcps_jln_fw_vers	\N	CPU Firmware Version, counts	1	\N
1581	adcps_jln_fw_rev_quantity_uint8_1	adcps_jln_fw_rev	\N	CPU Firmware Revision, counts	1	\N
1582	adcps_jln_year_quantity_uint16_year	adcps_jln_year	\N	Year	year	\N
1583	adcps_jln_month_quantity_uint8_month	adcps_jln_month	\N	Month	month	\N
1584	adcps_jln_day_quantity_uint8_day	adcps_jln_day	\N	Day	day	\N
1585	adcps_jln_hour_quantity_uint8_hour	adcps_jln_hour	\N	Hour	hour	\N
1586	adcps_jln_minute_quantity_uint8_minute	adcps_jln_minute	\N	Minute	minute	\N
1587	adcps_jln_second_quantity_uint8_sec	adcps_jln_second	\N	Second	sec	\N
1588	adcps_jln_hsec_quantity_uint8_csec	adcps_jln_hsec	\N	Hundredths of Seconds	csec	\N
1589	adcps_jln_heading_quantity_uint16_cdegree	adcps_jln_heading	\N	Heading, centidegrees	cdegree	\N
1590	adcps_jln_pitch_quantity_int16_cdegree	adcps_jln_pitch	\N	Pitch, centidegrees	cdegree	\N
1591	adcps_jln_roll_quantity_int16_cdegree	adcps_jln_roll	\N	Roll, centidegrees	cdegree	\N
1592	adcps_jln_temp_quantity_int16_cdeg_C	adcps_jln_temp	\N	Temperature, centidegree C	cdeg_C	\N
1593	adcps_jln_pressure_quantity_int32_daPa	adcps_jln_pressure	\N	Pressure, decaPascal	daPa	\N
1594	adcps_jln_startbin_quantity_uint8_1	adcps_jln_startbin	\N	Starting BIN Number, counts	1	\N
1595	adcps_jln_bins_quantity_uint8_1	adcps_jln_bins	\N	Bins, counts	1	\N
1596	adcps_jln_component1_array_quantity_int16_counts	adcps_jln_component1	\N	Velocity Data - Error, counts	counts	\N
1597	adcps_jln_component2_array_quantity_int16_counts	adcps_jln_component2	\N	Velocity Data - Up, counts	counts	\N
1598	adcps_jln_component3_array_quantity_int16_counts	adcps_jln_component3	\N	Velocity Data - North, counts	counts	\N
1599	adcps_jln_component4_array_quantity_int16_counts	adcps_jln_component4	\N	Velocity Data - East, counts	counts	\N
1600	adcps_jln_timestamp_quantity_string_1	adcps_jln_timestamp	\N	Timestamp, seconds	1	\N
1601	adcps_jln_id_quantity_uint16_1	adcps_jln_id	\N	ID Number, counts	1	\N
1602	adcps_jln_volts_quantity_float32_V	adcps_jln_volts	\N	Voltage, V	V	\N
1603	adcps_jln_records_quantity_uint32_1	adcps_jln_records	\N	Number of Records, counts	1	\N
1604	adcps_jln_length_quantity_uint32_1	adcps_jln_length	\N	Length, bytes	1	\N
1605	adcps_jln_events_quantity_uint32_1	adcps_jln_events	\N	Number of Event, counts	1	\N
1606	adcps_jln_samples_written_quantity_uint32_1	adcps_jln_samples_written	\N	Samples Written, counts	1	\N
1607	flort_k_total_volume_scattering_coefficient_function_float32_m_1_sr_1	flort_k_total_volume_scattering_coefficient	\N	Total Volume Scattering Coefficient (Beta(117,700)), m-1 sr-1	m-1 sr-1	\N
1608	fluorometric_chlorophyll_a_function_float32_ug_L_1	fluorometric_chlorophyll_a	\N	Fluorometric Chlorophyll a Concentration, ug L-1	ug L-1	\N
1609	fluorometric_cdom_function_float32_ppb	fluorometric_cdom	\N	Fluorometric CDOM Concentration, ppb	ppb	\N
1610	parad_k_par_function_float32_umol_photons_m_2_s_1	parad_k_par	\N	Photosynthetic Active Radiation (PAR), umol photons m-2 s-1	umol photons m-2 s-1	\N
1611	rte_time_quantity_string_1	rte_time	\N	Measurement Date, UTC	1	\N
1612	cg_eng_platform_time_quantity_string_1	cg_eng_platform_time	\N	cg eng platform time	1	\N
1613	cg_eng_platform_utime_quantity_float64_s	cg_eng_platform_utime	\N	cg eng platform utime	s	\N
1614	cg_eng_msg_cnts_c_gps_quantity_int32_counts	cg_eng_msg_cnts_c_gps	\N	cg eng msg cnts c gps	counts	\N
1615	cg_eng_msg_cnts_c_ntp_quantity_int32_counts	cg_eng_msg_cnts_c_ntp	\N	cg eng msg cnts c ntp	counts	\N
1616	cg_eng_msg_cnts_c_pps_quantity_int32_counts	cg_eng_msg_cnts_c_pps	\N	cg eng msg cnts c pps	counts	\N
1617	cg_eng_msg_cnts_c_power_sys_quantity_int32_counts	cg_eng_msg_cnts_c_power_sys	\N	cg eng msg cnts c power sys	counts	\N
1618	cg_eng_msg_cnts_c_superv_quantity_int32_counts	cg_eng_msg_cnts_c_superv	\N	cg eng msg cnts c superv	counts	\N
1619	cg_eng_msg_cnts_c_telem_quantity_int32_counts	cg_eng_msg_cnts_c_telem	\N	cg eng msg cnts c telem	counts	\N
1620	cg_eng_err_c_gps_quantity_int32_counts	cg_eng_err_c_gps	\N	cg eng err c gps	counts	\N
1621	cg_eng_err_c_pps_quantity_int32_counts	cg_eng_err_c_pps	\N	cg eng err c pps	counts	\N
1622	cg_eng_err_c_ctl_quantity_int32_counts	cg_eng_err_c_ctl	\N	cg eng err c ctl	counts	\N
1623	cg_eng_err_c_status_quantity_int32_counts	cg_eng_err_c_status	\N	cg eng err c status	counts	\N
1624	cg_eng_err_superv_quantity_int32_counts	cg_eng_err_superv	\N	cg eng err superv	counts	\N
1625	cg_eng_err_c_power_sys_quantity_int32_counts	cg_eng_err_c_power_sys	\N	cg eng err c power sys	counts	\N
1626	cg_eng_err_c_telem_sys_quantity_int32_counts	cg_eng_err_c_telem_sys	\N	cg eng err c telem sys	counts	\N
1627	cg_eng_err_c_irid_quantity_int32_counts	cg_eng_err_c_irid	\N	cg eng err c irid	counts	\N
1628	cg_eng_err_c_imm_quantity_int32_counts	cg_eng_err_c_imm	\N	cg eng err c imm	counts	\N
1629	cg_eng_err_cpm1_quantity_int32_counts	cg_eng_err_cpm1	\N	cg eng err cpm1	counts	\N
1630	cg_eng_err_d_ctl_quantity_int32_counts	cg_eng_err_d_ctl	\N	cg eng err d ctl	counts	\N
1631	cg_eng_err_d_status_quantity_int32_counts	cg_eng_err_d_status	\N	cg eng err d status	counts	\N
1632	cg_eng_err_dlog_mgr_quantity_int32_counts	cg_eng_err_dlog_mgr	\N	cg eng err dlog mgr	counts	\N
1633	cg_eng_err_dlogp1_quantity_int32_counts	cg_eng_err_dlogp1	\N	cg eng err dlogp1	counts	\N
1634	cg_eng_err_dlogp2_quantity_int32_counts	cg_eng_err_dlogp2	\N	cg eng err dlogp2	counts	\N
1635	cg_eng_err_dlogp3_quantity_int32_counts	cg_eng_err_dlogp3	\N	cg eng err dlogp3	counts	\N
1636	cg_eng_err_dlogp4_quantity_int32_counts	cg_eng_err_dlogp4	\N	cg eng err dlogp4	counts	\N
1637	cg_eng_err_dlogp5_quantity_int32_counts	cg_eng_err_dlogp5	\N	cg eng err dlogp5	counts	\N
1638	cg_eng_err_dlogp6_quantity_int32_counts	cg_eng_err_dlogp6	\N	cg eng err dlogp6	counts	\N
1639	cg_eng_err_dlogp7_quantity_int32_counts	cg_eng_err_dlogp7	\N	cg eng err dlogp7	counts	\N
1640	cg_eng_err_dlogp8_quantity_int32_counts	cg_eng_err_dlogp8	\N	cg eng err dlogp8	counts	\N
1641	cg_eng_err_rcmd_quantity_int32_counts	cg_eng_err_rcmd	\N	cg eng err rcmd	counts	\N
1642	cg_eng_err_bcmd_quantity_int32_counts	cg_eng_err_bcmd	\N	cg eng err bcmd	counts	\N
1643	cg_eng_errmsg_c_gps_quantity_string_1	cg_eng_errmsg_c_gps	\N	cg eng errmsg c gps	1	\N
1644	cg_eng_errmsg_c_pps_quantity_string_1	cg_eng_errmsg_c_pps	\N	cg eng errmsg c pps	1	\N
1645	cg_eng_errmsg_c_ctl_quantity_string_1	cg_eng_errmsg_c_ctl	\N	cg eng errmsg c ctl	1	\N
1646	cg_eng_errmsg_c_status_quantity_string_1	cg_eng_errmsg_c_status	\N	cg eng errmsg c status	1	\N
1647	cg_eng_errmsg_superv_quantity_string_1	cg_eng_errmsg_superv	\N	cg eng errmsg superv	1	\N
1648	cg_eng_errmsg_c_power_sys_quantity_string_1	cg_eng_errmsg_c_power_sys	\N	cg eng errmsg c power sys	1	\N
1649	cg_eng_errmsg_c_telem_sys_quantity_string_1	cg_eng_errmsg_c_telem_sys	\N	cg eng errmsg c telem sys	1	\N
1650	cg_eng_errmsg_c_irid_quantity_string_1	cg_eng_errmsg_c_irid	\N	cg eng errmsg c irid	1	\N
1651	cg_eng_errmsg_c_imm_quantity_string_1	cg_eng_errmsg_c_imm	\N	cg eng errmsg c imm	1	\N
1652	cg_eng_errmsg_cpm1_quantity_string_1	cg_eng_errmsg_cpm1	\N	cg eng errmsg cpm1	1	\N
1653	cg_eng_errmsg_d_ctl_quantity_string_1	cg_eng_errmsg_d_ctl	\N	cg eng errmsg d ctl	1	\N
1654	cg_eng_errmsg_d_status_quantity_string_1	cg_eng_errmsg_d_status	\N	cg eng errmsg d status	1	\N
1655	cg_eng_errmsg_dlog_mgr_quantity_string_1	cg_eng_errmsg_dlog_mgr	\N	cg eng errmsg dlog mgr	1	\N
1656	cg_eng_errmsg_dlogp1_quantity_string_1	cg_eng_errmsg_dlogp1	\N	cg eng errmsg dlogp1	1	\N
1657	cg_eng_errmsg_dlogp2_quantity_string_1	cg_eng_errmsg_dlogp2	\N	cg eng errmsg dlogp2	1	\N
1658	cg_eng_errmsg_dlogp3_quantity_string_1	cg_eng_errmsg_dlogp3	\N	cg eng errmsg dlogp3	1	\N
1659	cg_eng_errmsg_dlogp4_quantity_string_1	cg_eng_errmsg_dlogp4	\N	cg eng errmsg dlogp4	1	\N
1660	cg_eng_errmsg_dlogp5_quantity_string_1	cg_eng_errmsg_dlogp5	\N	cg eng errmsg dlogp5	1	\N
1661	cg_eng_errmsg_dlogp6_quantity_string_1	cg_eng_errmsg_dlogp6	\N	cg eng errmsg dlogp6	1	\N
1662	cg_eng_errmsg_dlogp7_quantity_string_1	cg_eng_errmsg_dlogp7	\N	cg eng errmsg dlogp7	1	\N
1663	cg_eng_errmsg_dlogp8_quantity_string_1	cg_eng_errmsg_dlogp8	\N	cg eng errmsg dlogp8	1	\N
1664	cg_eng_errmsg_rcmd_quantity_string_1	cg_eng_errmsg_rcmd	\N	cg eng errmsg rcmd	1	\N
1665	cg_eng_errmsg_bcmd_quantity_string_1	cg_eng_errmsg_bcmd	\N	cg eng errmsg bcmd	1	\N
1666	cg_eng_cpu_uptime_quantity_string_1	cg_eng_cpu_uptime	\N	cg eng cpu uptime	1	\N
1667	cg_eng_cpu_load1_quantity_float32_counts	cg_eng_cpu_load1	\N	cg eng cpu load1	counts	\N
1668	cg_eng_cpu_load5_quantity_float32_counts	cg_eng_cpu_load5	\N	cg eng cpu load5	counts	\N
1669	cg_eng_cpu_load15_quantity_float32_counts	cg_eng_cpu_load15	\N	cg eng cpu load15	counts	\N
1670	cg_eng_memory_ram_quantity_uint32_kbytes	cg_eng_memory_ram	\N	cg eng memory ram	kbytes	\N
1671	cg_eng_memory_free_quantity_uint32_kbytes	cg_eng_memory_free	\N	cg eng memory free	kbytes	\N
1672	cg_eng_nproc_quantity_uint16_counts	cg_eng_nproc	\N	cg eng nproc	counts	\N
1673	cg_eng_mpic_eflag_quantity_uint32_counts	cg_eng_mpic_eflag	\N	cg eng mpic eflag	counts	\N
1674	cg_eng_mpic_main_v_quantity_float32_V	cg_eng_mpic_main_v	\N	cg eng mpic main v	V	\N
1675	cg_eng_mpic_main_c_quantity_float32_mA	cg_eng_mpic_main_c	\N	cg eng mpic main c	mA	\N
1676	cg_eng_mpic_bat_v_quantity_float32_V	cg_eng_mpic_bat_v	\N	cg eng mpic bat v	V	\N
1677	cg_eng_mpic_bat_c_quantity_float32_mA	cg_eng_mpic_bat_c	\N	cg eng mpic bat c	mA	\N
1678	cg_eng_mpic_temp1_quantity_float32_deg_C	cg_eng_mpic_temp1	\N	cg eng mpic temp1	deg_C	\N
1679	cg_eng_mpic_temp2_quantity_float32_deg_C	cg_eng_mpic_temp2	\N	cg eng mpic temp2	deg_C	\N
1680	cg_eng_mpic_humid_quantity_float32_%	cg_eng_mpic_humid	\N	cg eng mpic humd	%	\N
1681	cg_eng_mpic_press_quantity_float32_psi	cg_eng_mpic_press	\N	cg eng mpic press	psi	\N
1682	cg_eng_mpic_gf_ena_quantity_int32_1	cg_eng_mpic_gf_ena	\N	cg eng mpic gf ena	1	\N
1683	cg_eng_mpic_gflt1_quantity_float32_uA	cg_eng_mpic_gflt1	\N	cg eng mpic gflt1	uA	\N
1684	cg_eng_mpic_gflt2_quantity_float32_uA	cg_eng_mpic_gflt2	\N	cg eng mpic gflt2	uA	\N
1685	cg_eng_mpic_gflt3_quantity_float32_uA	cg_eng_mpic_gflt3	\N	cg eng mpic gflt3	uA	\N
1686	cg_eng_mpic_gflt4_quantity_float32_uA	cg_eng_mpic_gflt4	\N	cg eng mpic gflt4	uA	\N
1687	cg_eng_mpic_ld_ena_quantity_int32_counts	cg_eng_mpic_ld_ena	\N	cg eng mpic ld ena	counts	\N
1688	cg_eng_mpic_ldet1_quantity_float32_mV	cg_eng_mpic_ldet1	\N	cg eng mpic ldet1	mV	\N
1689	cg_eng_mpic_ldet2_quantity_float32_mV	cg_eng_mpic_ldet2	\N	cg eng mpic ldet2	mV	\N
1690	cg_eng_mpic_wsrc_quantity_int32_counts	cg_eng_mpic_wsrc	\N	cg eng mpic wsrc	counts	\N
1691	cg_eng_mpic_irid_quantity_int32_counts	cg_eng_mpic_irid	\N	cg eng mpic irid	counts	\N
1692	cg_eng_mpic_irid_v_quantity_float32_V	cg_eng_mpic_irid_v	\N	cg eng mpic irid v	V	\N
1693	cg_eng_mpic_irid_c_quantity_float32_mA	cg_eng_mpic_irid_c	\N	cg eng mpic irid c	mA	\N
1694	cg_eng_mpic_irid_e_quantity_int32_counts	cg_eng_mpic_irid_e	\N	cg eng mpic irid e	counts	\N
1695	cg_eng_mpic_fw_wifi_quantity_int32_counts	cg_eng_mpic_fw_wifi	\N	cg eng mpic fw wifi	counts	\N
1696	cg_eng_mpic_fw_wifi_v_quantity_float32_V	cg_eng_mpic_fw_wifi_v	\N	cg eng mpic fw wifi v	V	\N
1697	cg_eng_mpic_fw_wifi_c_quantity_float32_mA	cg_eng_mpic_fw_wifi_c	\N	cg eng mpic fw wifi c	mA	\N
1698	cg_eng_mpic_fw_wifi_e_quantity_int32_counts	cg_eng_mpic_fw_wifi_e	\N	cg eng mpic fw wifi e	counts	\N
1699	cg_eng_mpic_gps_quantity_int32_counts	cg_eng_mpic_gps	\N	cg eng mpic gps	counts	\N
1700	cg_eng_mpic_sbd_quantity_int32_counts	cg_eng_mpic_sbd	\N	cg eng mpic sbd	counts	\N
1701	cg_eng_mpic_sbd_ce_msg_quantity_int32_counts	cg_eng_mpic_sbd_ce_msg	\N	cg eng mpic sbd ce msg	counts	\N
1702	cg_eng_mpic_pps_quantity_int32_counts	cg_eng_mpic_pps	\N	cg eng mpic pps	counts	\N
1703	cg_eng_mpic_dcl_quantity_uint32_counts	cg_eng_mpic_dcl	\N	cg eng mpic dcl	counts	\N
1704	cg_eng_mpic_esw_quantity_uint32_counts	cg_eng_mpic_esw	\N	cg eng mpic esw	counts	\N
1705	cg_eng_mpic_dsl_quantity_uint32_counts	cg_eng_mpic_dsl	\N	cg eng mpic dsl	counts	\N
1706	cg_eng_mpic_hbeat_enable_quantity_int32_counts	cg_eng_mpic_hbeat_enable	\N	cg eng mpic hbeat enable	counts	\N
1707	cg_eng_mpic_hbeat_dtime_quantity_int32_s	cg_eng_mpic_hbeat_dtime	\N	cg eng mpic hbeat dtime	s	\N
1708	cg_eng_mpic_hbeat_threshold_quantity_int32_counts	cg_eng_mpic_hbeat_threshold	\N	cg eng mpic hbeat threshold	counts	\N
1709	cg_eng_mpic_wake_cpm_quantity_int32_ns	cg_eng_mpic_wake_cpm	\N	cg eng mpic wake cpm	ns	\N
1710	cg_eng_mpic_wpc_quantity_int32_counts	cg_eng_mpic_wpc	\N	cg eng mpic wpc	counts	\N
1711	cg_eng_mpic_eflag2_quantity_uint32_counts	cg_eng_mpic_eflag2	\N	cg eng mpic eflag2	counts	\N
1712	cg_eng_mpic_last_update_quantity_float32_ms	cg_eng_mpic_last_update	\N	cg eng mpic last update	ms	\N
1713	cg_eng_gps_msg_date_quantity_string_1	cg_eng_gps_msg_date	\N	cg eng gps msg date	1	\N
1714	cg_eng_gps_msg_time_quantity_string_1	cg_eng_gps_msg_time	\N	cg eng gps msg time	1	\N
1715	cg_eng_gps_date_quantity_uint32_counts	cg_eng_gps_date	\N	cg eng gps date	counts	\N
1716	cg_eng_gps_time_quantity_uint32_counts	cg_eng_gps_time	\N	cg eng gps time	counts	\N
1717	cg_eng_gps_latstr_quantity_string_1	cg_eng_gps_latstr	\N	cg eng gps latstr	1	\N
1718	cg_eng_gps_lonstr_quantity_string_1	cg_eng_gps_lonstr	\N	cg eng gps lonstr	1	\N
1719	cg_eng_gps_lat_quantity_float64_degree_north	cg_eng_gps_lat	\N	cg eng gps lat	degree_north	\N
1720	cg_eng_gps_lon_quantity_float64_degree_east	cg_eng_gps_lon	\N	cg eng gps lon	degree_east	\N
1721	cg_eng_gps_spd_quantity_float32_Knots	cg_eng_gps_spd	\N	cg eng gps spd	Knots	\N
1722	cg_eng_gps_cog_quantity_float32_degrees	cg_eng_gps_cog	\N	cg eng gps cog	degrees	\N
1723	cg_eng_gps_fix_quantity_int32_counts	cg_eng_gps_fix	\N	cg eng gps fix	counts	\N
1724	cg_eng_gps_nsat_quantity_int32_counts	cg_eng_gps_nsat	\N	cg eng gps nsat	counts	\N
1725	cg_eng_gps_hdop_quantity_float32_counts	cg_eng_gps_hdop	\N	cg eng gps hdop	counts	\N
1726	cg_eng_gps_alt_quantity_float32_m	cg_eng_gps_alt	\N	cg eng gps alt	m	\N
1727	cg_eng_gps_last_update_quantity_float64_s	cg_eng_gps_last_update	\N	cg eng gps last update	s	\N
1728	cg_eng_ntp_refid_quantity_string_1	cg_eng_ntp_refid	\N	cg eng ntp refid	1	\N
1729	cg_eng_ntp_offset_quantity_float32_ms	cg_eng_ntp_offset	\N	cg eng ntp offset	ms	\N
1730	cg_eng_ntp_jitter_quantity_float32_ms	cg_eng_ntp_jitter	\N	cg eng ntp jitter	ms	\N
1731	cg_eng_pps_lock_quantity_string_1	cg_eng_pps_lock	\N	cg eng pps lock	1	\N
1732	cg_eng_pps_delta_quantity_int32_us	cg_eng_pps_delta	\N	cg eng pps delta	us	\N
1733	cg_eng_pps_deltamin_quantity_int32_us	cg_eng_pps_deltamin	\N	cg eng pps deltamin	us	\N
1734	cg_eng_pps_deltamax_quantity_int32_us	cg_eng_pps_deltamax	\N	cg eng pps deltamax	us	\N
1735	cg_eng_pps_bad_pulse_quantity_int32_counts	cg_eng_pps_bad_pulse	\N	cg eng pps bad pulse	counts	\N
1736	cg_eng_pps_timestamp_quantity_string_1	cg_eng_pps_timestamp	\N	cg eng pps timestamp	1	\N
1737	cg_eng_pps_last_update_quantity_float64_s	cg_eng_pps_last_update	\N	cg eng pps last update	s	\N
1738	cg_eng_loadshed_status_quantity_string_1	cg_eng_loadshed_status	\N	cg eng loadshed status	1	\N
1739	cg_eng_loadshed_last_update_quantity_float64_s	cg_eng_loadshed_last_update	\N	cg eng loadshed last update	s	\N
1740	cg_eng_sbc_eth0_quantity_int16_counts	cg_eng_sbc_eth0	\N	cg eng sbc eth0	counts	\N
1741	cg_eng_sbc_eth1_quantity_int16_counts	cg_eng_sbc_eth1	\N	cg eng sbc eth1	counts	\N
1742	cg_eng_sbc_led0_quantity_int16_counts	cg_eng_sbc_led0	\N	cg eng sbc led0	counts	\N
1743	cg_eng_sbc_led1_quantity_int16_counts	cg_eng_sbc_led1	\N	cg eng sbc led1	counts	\N
1744	cg_eng_sbc_led2_quantity_int16_counts	cg_eng_sbc_led2	\N	cg eng sbc led2	counts	\N
1745	cg_eng_sbc_gpo0_quantity_int16_counts	cg_eng_sbc_gpo0	\N	cg eng sbc gpo0	counts	\N
1746	cg_eng_sbc_gpo1_quantity_int16_counts	cg_eng_sbc_gpo1	\N	cg eng sbc gpo1	counts	\N
1747	cg_eng_sbc_gpo2_quantity_int16_counts	cg_eng_sbc_gpo2	\N	cg eng sbc gpo2	counts	\N
1748	cg_eng_sbc_gpo3_quantity_int16_counts	cg_eng_sbc_gpo3	\N	cg eng sbc gpo3	counts	\N
1749	cg_eng_sbc_gpo4_quantity_int16_counts	cg_eng_sbc_gpo4	\N	cg eng sbc gpo4	counts	\N
1750	cg_eng_sbc_gpio0_quantity_int16_counts	cg_eng_sbc_gpio0	\N	cg eng sbc gpio0	counts	\N
1751	cg_eng_sbc_gpio1_quantity_int16_counts	cg_eng_sbc_gpio1	\N	cg eng sbc gpio1	counts	\N
1752	cg_eng_sbc_gpio2_quantity_int16_counts	cg_eng_sbc_gpio2	\N	cg eng sbc gpio2	counts	\N
1753	cg_eng_sbc_gpio3_quantity_int16_counts	cg_eng_sbc_gpio3	\N	cg eng sbc gpio3	counts	\N
1754	cg_eng_sbc_gpio4_quantity_int16_counts	cg_eng_sbc_gpio4	\N	cg eng sbc gpio4	counts	\N
1755	cg_eng_sbc_gpio5_quantity_int16_counts	cg_eng_sbc_gpio5	\N	cg eng sbc gpio5	counts	\N
1756	cg_eng_sbc_fb1_quantity_int16_counts	cg_eng_sbc_fb1	\N	cg eng sbc fb1	counts	\N
1757	cg_eng_sbc_fb2_quantity_int16_counts	cg_eng_sbc_fb2	\N	cg eng sbc fb2	counts	\N
1758	cg_eng_sbc_ce_led_quantity_int16_counts	cg_eng_sbc_ce_led	\N	cg eng sbc ce led	counts	\N
1759	cg_eng_sbc_wdt_quantity_int32_counts	cg_eng_sbc_wdt	\N	cg eng sbc wdt	counts	\N
1760	cg_eng_sbc_bid_quantity_int32_counts	cg_eng_sbc_bid	\N	cg eng sbc bid	counts	\N
1761	cg_eng_sbc_bstr_quantity_int32_counts	cg_eng_sbc_bstr	\N	cg eng sbc bstr	counts	\N
1762	cg_eng_msg_cnts_d_gps_quantity_int32_counts	cg_eng_msg_cnts_d_gps	\N	cg eng msg cnts d gps	counts	\N
1763	cg_eng_msg_cnts_d_ntp_quantity_int32_counts	cg_eng_msg_cnts_d_ntp	\N	cg eng msg cnts d ntp	counts	\N
1764	cg_eng_msg_cnts_d_pps_quantity_int32_counts	cg_eng_msg_cnts_d_pps	\N	cg eng msg cnts d pps	counts	\N
1765	cg_eng_msg_cnts_d_superv_quantity_int32_counts	cg_eng_msg_cnts_d_superv	\N	cg eng msg cnts d superv	counts	\N
1766	cg_eng_msg_cnts_d_dlog_ngr_quantity_int32_counts	cg_eng_msg_cnts_d_dlog_ngr	\N	cg eng msg cnts d dlog ngr	counts	\N
1767	cg_eng_dclp1_enable_quantity_int32_counts	cg_eng_dclp1_enable	\N	cg eng dclp1 enable	counts	\N
1768	cg_eng_dclp1_volt_quantity_float32_V	cg_eng_dclp1_volt	\N	cg eng dclp1 volt	V	\N
1769	cg_eng_dclp1_current_quantity_float32_mA	cg_eng_dclp1_current	\N	cg eng dclp1 current	mA	\N
1770	cg_eng_dclp1_eflag_quantity_int32_counts	cg_eng_dclp1_eflag	\N	cg eng dclp1 eflag	counts	\N
1771	cg_eng_dclp1_vsel_quantity_int32_counts	cg_eng_dclp1_vsel	\N	cg eng dclp1 vsel	counts	\N
1772	cg_eng_dclp1_clim_quantity_int32_counts	cg_eng_dclp1_clim	\N	cg eng dclp1 clim	counts	\N
1773	cg_eng_dclp1_prot_quantity_int32_counts	cg_eng_dclp1_prot	\N	cg eng dclp1 prot	counts	\N
1774	cg_eng_dclp2_enable_quantity_int32_counts	cg_eng_dclp2_enable	\N	cg eng dclp2 enable	counts	\N
1775	cg_eng_dclp2_volt_quantity_float32_V	cg_eng_dclp2_volt	\N	cg eng dclp2 volt	V	\N
1776	cg_eng_dclp2_current_quantity_float32_mA	cg_eng_dclp2_current	\N	cg eng dclp2 current	mA	\N
1777	cg_eng_dclp2_eflag_quantity_int32_counts	cg_eng_dclp2_eflag	\N	cg eng dclp2 eflag	counts	\N
1778	cg_eng_dclp2_vsel_quantity_int32_counts	cg_eng_dclp2_vsel	\N	cg eng dclp2 vsel	counts	\N
1779	cg_eng_dclp2_clim_quantity_int32_counts	cg_eng_dclp2_clim	\N	cg eng dclp2 clim	counts	\N
1780	cg_eng_dclp2_prot_quantity_int32_counts	cg_eng_dclp2_prot	\N	cg eng dclp2 prot	counts	\N
1781	cg_eng_dclp3_enable_quantity_int32_counts	cg_eng_dclp3_enable	\N	cg eng dclp3 enable	counts	\N
1782	cg_eng_dclp3_volt_quantity_float32_V	cg_eng_dclp3_volt	\N	cg eng dclp3 volt	V	\N
1783	cg_eng_dclp3_current_quantity_float32_mA	cg_eng_dclp3_current	\N	cg eng dclp3 current	mA	\N
1784	cg_eng_dclp3_eflag_quantity_int32_counts	cg_eng_dclp3_eflag	\N	cg eng dclp3 eflag	counts	\N
1785	cg_eng_dclp3_vsel_quantity_int32_counts	cg_eng_dclp3_vsel	\N	cg eng dclp3 vsel	counts	\N
1786	cg_eng_dclp3_clim_quantity_int32_counts	cg_eng_dclp3_clim	\N	cg eng dclp3 clim	counts	\N
1787	cg_eng_dclp3_prot_quantity_int32_counts	cg_eng_dclp3_prot	\N	cg eng dclp3 prot	counts	\N
1788	cg_eng_dclp4_enable_quantity_int32_counts	cg_eng_dclp4_enable	\N	cg eng dclp4 enable	counts	\N
1789	cg_eng_dclp4_volt_quantity_float32_V	cg_eng_dclp4_volt	\N	cg eng dclp4 volt	V	\N
1790	cg_eng_dclp4_current_quantity_float32_mA	cg_eng_dclp4_current	\N	cg eng dclp4 current	mA	\N
1791	cg_eng_dclp4_eflag_quantity_int32_counts	cg_eng_dclp4_eflag	\N	cg eng dclp4 eflag	counts	\N
1792	cg_eng_dclp4_vsel_quantity_int32_counts	cg_eng_dclp4_vsel	\N	cg eng dclp4 vsel	counts	\N
1793	cg_eng_dclp4_clim_quantity_int32_counts	cg_eng_dclp4_clim	\N	cg eng dclp4 clim	counts	\N
1794	cg_eng_dclp4_prot_quantity_int32_counts	cg_eng_dclp4_prot	\N	cg eng dclp4 prot	counts	\N
1795	cg_eng_dclp5_enable_quantity_int32_counts	cg_eng_dclp5_enable	\N	cg eng dclp5 enable	counts	\N
1796	cg_eng_dclp5_volt_quantity_float32_V	cg_eng_dclp5_volt	\N	cg eng dclp5 volt	V	\N
1797	cg_eng_dclp5_current_quantity_float32_mA	cg_eng_dclp5_current	\N	cg eng dclp5 current	mA	\N
1798	cg_eng_dclp5_eflag_quantity_int32_counts	cg_eng_dclp5_eflag	\N	cg eng dclp5 eflag	counts	\N
1799	cg_eng_dclp5_vsel_quantity_int32_counts	cg_eng_dclp5_vsel	\N	cg eng dclp5 vsel	counts	\N
1800	cg_eng_dclp5_clim_quantity_int32_counts	cg_eng_dclp5_clim	\N	cg eng dclp5 clim	counts	\N
1801	cg_eng_dclp5_prot_quantity_int32_counts	cg_eng_dclp5_prot	\N	cg eng dclp5 prot	counts	\N
1802	cg_eng_dclp6_enable_quantity_int32_counts	cg_eng_dclp6_enable	\N	cg eng dclp6 enable	counts	\N
1803	cg_eng_dclp6_volt_quantity_float32_V	cg_eng_dclp6_volt	\N	cg eng dclp6 volt	V	\N
1804	cg_eng_dclp6_current_quantity_float32_mA	cg_eng_dclp6_current	\N	cg eng dclp6 current	mA	\N
1805	cg_eng_dclp6_eflag_quantity_int32_counts	cg_eng_dclp6_eflag	\N	cg eng dclp6 eflag	counts	\N
1806	cg_eng_dclp6_vsel_quantity_int32_counts	cg_eng_dclp6_vsel	\N	cg eng dclp6 vsel	counts	\N
1807	cg_eng_dclp6_clim_quantity_int32_counts	cg_eng_dclp6_clim	\N	cg eng dclp6 clim	counts	\N
1808	cg_eng_dclp6_prot_quantity_int32_counts	cg_eng_dclp6_prot	\N	cg eng dclp6 prot	counts	\N
1809	cg_eng_dclp7_enable_quantity_int32_counts	cg_eng_dclp7_enable	\N	cg eng dclp7 enable	counts	\N
1810	cg_eng_dclp7_volt_quantity_float32_V	cg_eng_dclp7_volt	\N	cg eng dclp7 volt	V	\N
1811	cg_eng_dclp7_current_quantity_float32_mA	cg_eng_dclp7_current	\N	cg eng dclp7 current	mA	\N
1812	cg_eng_dclp7_eflag_quantity_int32_counts	cg_eng_dclp7_eflag	\N	cg eng dclp7 eflag	counts	\N
1813	cg_eng_dclp7_vsel_quantity_int32_counts	cg_eng_dclp7_vsel	\N	cg eng dclp7 vsel	counts	\N
1814	cg_eng_dclp7_clim_quantity_int32_counts	cg_eng_dclp7_clim	\N	cg eng dclp7 clim	counts	\N
1815	cg_eng_dclp7_prot_quantity_int32_counts	cg_eng_dclp7_prot	\N	cg eng dclp7 prot	counts	\N
1816	cg_eng_dclp8_enable_quantity_int32_counts	cg_eng_dclp8_enable	\N	cg eng dclp8 enable	counts	\N
1817	cg_eng_dclp8_volt_quantity_float32_V	cg_eng_dclp8_volt	\N	cg eng dclp8 volt	V	\N
1818	cg_eng_dclp8_current_quantity_float32_mA	cg_eng_dclp8_current	\N	cg eng dclp8 current	mA	\N
1819	cg_eng_dclp8_eflag_quantity_int32_counts	cg_eng_dclp8_eflag	\N	cg eng dclp8 eflag	counts	\N
1820	cg_eng_dclp8_vsel_quantity_int32_counts	cg_eng_dclp8_vsel	\N	cg eng dclp8 vsel	counts	\N
1821	cg_eng_dclp8_clim_quantity_int32_counts	cg_eng_dclp8_clim	\N	cg eng dclp8 clim	counts	\N
1822	cg_eng_dclp8_prot_quantity_int32_counts	cg_eng_dclp8_prot	\N	cg eng dclp8 prot	counts	\N
1823	cg_eng_dcl_port_status_quantity_float32_ms	cg_eng_dcl_port_status	\N	cg eng dcl port status	ms	\N
1824	cg_eng_port_dlog1_name_quantity_string_1	cg_eng_port_dlog1_name	\N	cg eng port dlog1 name	1	\N
1825	cg_eng_port_dlog1_state_quantity_string_1	cg_eng_port_dlog1_state	\N	cg eng port dlog1 state	1	\N
1826	cg_eng_port_dlog1_tx_quantity_uint64_counts	cg_eng_port_dlog1_tx	\N	cg eng port dlog1 tx	counts	\N
1827	cg_eng_port_dlog1_rx_quantity_uint64_counts	cg_eng_port_dlog1_rx	\N	cg eng port dlog1 rx	counts	\N
1828	cg_eng_port_dlog1_log_quantity_uint64_counts	cg_eng_port_dlog1_log	\N	cg eng port dlog1 log	counts	\N
1829	cg_eng_port_dlog1_good_quantity_uint64_counts	cg_eng_port_dlog1_good	\N	cg eng port dlog1 good	counts	\N
1830	cg_eng_port_dlog1_bad_quantity_uint64_counts	cg_eng_port_dlog1_bad	\N	cg eng port dlog1 bad	counts	\N
1831	cg_eng_port_dlog1_bb_quantity_uint64_counts	cg_eng_port_dlog1_bb	\N	cg eng port dlog1 bb	counts	\N
1832	cg_eng_port_dlog1_ld_quantity_int64_s	cg_eng_port_dlog1_ld	\N	cg eng port dlog1 ld	s	\N
1833	cg_eng_port_dlog1_lu_quantity_float64_s	cg_eng_port_dlog1_lu	\N	cg eng port dlog1 lu	s	\N
1834	cg_eng_port_dlog2_name_quantity_string_1	cg_eng_port_dlog2_name	\N	cg eng port dlog2 name	1	\N
1835	cg_eng_port_dlog2_state_quantity_string_1	cg_eng_port_dlog2_state	\N	cg eng port dlog2 state	1	\N
1836	cg_eng_port_dlog2_tx_quantity_uint64_counts	cg_eng_port_dlog2_tx	\N	cg eng port dlog2 tx	counts	\N
1837	cg_eng_port_dlog2_rx_quantity_uint64_counts	cg_eng_port_dlog2_rx	\N	cg eng port dlog2 rx	counts	\N
1838	cg_eng_port_dlog2_log_quantity_uint64_counts	cg_eng_port_dlog2_log	\N	cg eng port dlog2 log	counts	\N
1839	cg_eng_port_dlog2_good_quantity_uint64_counts	cg_eng_port_dlog2_good	\N	cg eng port dlog2 good	counts	\N
1840	cg_eng_port_dlog2_bad_quantity_uint64_counts	cg_eng_port_dlog2_bad	\N	cg eng port dlog2 bad	counts	\N
1841	cg_eng_port_dlog2_bb_quantity_uint64_counts	cg_eng_port_dlog2_bb	\N	cg eng port dlog2 bb	counts	\N
1842	cg_eng_port_dlog2_ld_quantity_int64_s	cg_eng_port_dlog2_ld	\N	cg eng port dlog2 ld	s	\N
1843	cg_eng_port_dlog2_lu_quantity_float64_s	cg_eng_port_dlog2_lu	\N	cg eng port dlog2 lu	s	\N
1844	cg_eng_port_dlog3_name_quantity_string_1	cg_eng_port_dlog3_name	\N	cg eng port dlog3 name	1	\N
1845	cg_eng_port_dlog3_state_quantity_string_1	cg_eng_port_dlog3_state	\N	cg eng port dlog3 state	1	\N
1846	cg_eng_port_dlog3_tx_quantity_uint64_counts	cg_eng_port_dlog3_tx	\N	cg eng port dlog3 tx	counts	\N
1847	cg_eng_port_dlog3_rx_quantity_uint64_counts	cg_eng_port_dlog3_rx	\N	cg eng port dlog3 rx	counts	\N
1848	cg_eng_port_dlog3_log_quantity_uint64_counts	cg_eng_port_dlog3_log	\N	cg eng port dlog3 log	counts	\N
1849	cg_eng_port_dlog3_good_quantity_uint64_counts	cg_eng_port_dlog3_good	\N	cg eng port dlog3 good	counts	\N
1850	cg_eng_port_dlog3_bad_quantity_uint64_counts	cg_eng_port_dlog3_bad	\N	cg eng port dlog3 bad	counts	\N
1851	cg_eng_port_dlog3_bb_quantity_uint64_counts	cg_eng_port_dlog3_bb	\N	cg eng port dlog3 bb	counts	\N
1852	cg_eng_port_dlog3_ld_quantity_int64_s	cg_eng_port_dlog3_ld	\N	cg eng port dlog3 ld	s	\N
1853	cg_eng_port_dlog3_lu_quantity_float64_s	cg_eng_port_dlog3_lu	\N	cg eng port dlog3 lu	s	\N
1854	cg_eng_port_dlog4_name_quantity_string_1	cg_eng_port_dlog4_name	\N	cg eng port dlog4 name	1	\N
1855	cg_eng_port_dlog4_state_quantity_string_1	cg_eng_port_dlog4_state	\N	cg eng port dlog4 state	1	\N
1856	cg_eng_port_dlog4_tx_quantity_uint64_counts	cg_eng_port_dlog4_tx	\N	cg eng port dlog4 tx	counts	\N
1857	cg_eng_port_dlog4_rx_quantity_uint64_counts	cg_eng_port_dlog4_rx	\N	cg eng port dlog4 rx	counts	\N
1858	cg_eng_port_dlog4_log_quantity_uint64_counts	cg_eng_port_dlog4_log	\N	cg eng port dlog4 log	counts	\N
1859	cg_eng_port_dlog4_good_quantity_uint64_counts	cg_eng_port_dlog4_good	\N	cg eng port dlog4 good	counts	\N
1860	cg_eng_port_dlog4_bad_quantity_uint64_counts	cg_eng_port_dlog4_bad	\N	cg eng port dlog4 bad	counts	\N
1861	cg_eng_port_dlog4_bb_quantity_uint64_counts	cg_eng_port_dlog4_bb	\N	cg eng port dlog4 bb	counts	\N
1862	cg_eng_port_dlog4_ld_quantity_int64_s	cg_eng_port_dlog4_ld	\N	cg eng port dlog4 ld	s	\N
1863	cg_eng_port_dlog4_lu_quantity_float64_s	cg_eng_port_dlog4_lu	\N	cg eng port dlog4 lu	s	\N
1864	cg_eng_port_dlog5_name_quantity_string_1	cg_eng_port_dlog5_name	\N	cg eng port dlog5 name	1	\N
1865	cg_eng_port_dlog5_state_quantity_string_1	cg_eng_port_dlog5_state	\N	cg eng port dlog5 state	1	\N
1866	cg_eng_port_dlog5_tx_quantity_uint64_counts	cg_eng_port_dlog5_tx	\N	cg eng port dlog5 tx	counts	\N
1867	cg_eng_port_dlog5_rx_quantity_uint64_counts	cg_eng_port_dlog5_rx	\N	cg eng port dlog5 rx	counts	\N
1868	cg_eng_port_dlog5_log_quantity_uint64_counts	cg_eng_port_dlog5_log	\N	cg eng port dlog5 log	counts	\N
1869	cg_eng_port_dlog5_good_quantity_uint64_counts	cg_eng_port_dlog5_good	\N	cg eng port dlog5 good	counts	\N
1870	cg_eng_port_dlog5_bad_quantity_uint64_counts	cg_eng_port_dlog5_bad	\N	cg eng port dlog5 bad	counts	\N
1871	cg_eng_port_dlog5_bb_quantity_uint64_counts	cg_eng_port_dlog5_bb	\N	cg eng port dlog5 bb	counts	\N
1872	cg_eng_port_dlog5_ld_quantity_int64_s	cg_eng_port_dlog5_ld	\N	cg eng port dlog5 ld	s	\N
1873	cg_eng_port_dlog5_lu_quantity_float64_s	cg_eng_port_dlog5_lu	\N	cg eng port dlog5 lu	s	\N
1874	cg_eng_port_dlog6_name_quantity_string_1	cg_eng_port_dlog6_name	\N	cg eng port dlog6 name	1	\N
1875	cg_eng_port_dlog6_state_quantity_string_1	cg_eng_port_dlog6_state	\N	cg eng port dlog6 state	1	\N
1876	cg_eng_port_dlog6_tx_quantity_uint64_counts	cg_eng_port_dlog6_tx	\N	cg eng port dlog6 tx	counts	\N
1877	cg_eng_port_dlog6_rx_quantity_uint64_counts	cg_eng_port_dlog6_rx	\N	cg eng port dlog6 rx	counts	\N
1878	cg_eng_port_dlog6_log_quantity_uint64_counts	cg_eng_port_dlog6_log	\N	cg eng port dlog6 log	counts	\N
1879	cg_eng_port_dlog6_good_quantity_uint64_counts	cg_eng_port_dlog6_good	\N	cg eng port dlog6 good	counts	\N
1880	cg_eng_port_dlog6_bad_quantity_uint64_counts	cg_eng_port_dlog6_bad	\N	cg eng port dlog6 bad	counts	\N
1881	cg_eng_port_dlog6_bb_quantity_uint64_counts	cg_eng_port_dlog6_bb	\N	cg eng port dlog6 bb	counts	\N
1882	cg_eng_port_dlog6_ld_quantity_int64_s	cg_eng_port_dlog6_ld	\N	cg eng port dlog6 ld	s	\N
1883	cg_eng_port_dlog6_lu_quantity_float64_s	cg_eng_port_dlog6_lu	\N	cg eng port dlog6 lu	s	\N
1884	cg_eng_port_dlog7_name_quantity_string_1	cg_eng_port_dlog7_name	\N	cg eng port dlog7 name	1	\N
1885	cg_eng_port_dlog7_state_quantity_string_1	cg_eng_port_dlog7_state	\N	cg eng port dlog7 state	1	\N
1886	cg_eng_port_dlog7_tx_quantity_uint64_counts	cg_eng_port_dlog7_tx	\N	cg eng port dlog7 tx	counts	\N
1887	cg_eng_port_dlog7_rx_quantity_uint64_counts	cg_eng_port_dlog7_rx	\N	cg eng port dlog7 rx	counts	\N
1888	cg_eng_port_dlog7_log_quantity_uint64_counts	cg_eng_port_dlog7_log	\N	cg eng port dlog7 log	counts	\N
1889	cg_eng_port_dlog7_good_quantity_uint64_counts	cg_eng_port_dlog7_good	\N	cg eng port dlog7 good	counts	\N
1890	cg_eng_port_dlog7_bad_quantity_uint64_counts	cg_eng_port_dlog7_bad	\N	cg eng port dlog7 bad	counts	\N
1891	cg_eng_port_dlog7_bb_quantity_uint64_counts	cg_eng_port_dlog7_bb	\N	cg eng port dlog7 bb	counts	\N
1892	cg_eng_port_dlog7_ld_quantity_int64_s	cg_eng_port_dlog7_ld	\N	cg eng port dlog7 ld	s	\N
1893	cg_eng_port_dlog7_lu_quantity_float64_s	cg_eng_port_dlog7_lu	\N	cg eng port dlog7 lu	s	\N
1894	cg_eng_port_dlog8_name_quantity_string_1	cg_eng_port_dlog8_name	\N	cg eng port dlog8 name	1	\N
1895	cg_eng_port_dlog8_state_quantity_string_1	cg_eng_port_dlog8_state	\N	cg eng port dlog8 state	1	\N
1896	cg_eng_port_dlog8_tx_quantity_uint64_counts	cg_eng_port_dlog8_tx	\N	cg eng port dlog8 tx	counts	\N
1897	cg_eng_port_dlog8_rx_quantity_uint64_counts	cg_eng_port_dlog8_rx	\N	cg eng port dlog8 rx	counts	\N
1898	cg_eng_port_dlog8_log_quantity_uint64_counts	cg_eng_port_dlog8_log	\N	cg eng port dlog8 log	counts	\N
1899	cg_eng_port_dlog8_good_quantity_uint64_counts	cg_eng_port_dlog8_good	\N	cg eng port dlog8 good	counts	\N
1900	cg_eng_port_dlog8_bad_quantity_uint64_counts	cg_eng_port_dlog8_bad	\N	cg eng port dlog8 bad	counts	\N
1901	cg_eng_port_dlog8_bb_quantity_uint64_counts	cg_eng_port_dlog8_bb	\N	cg eng port dlog8 bb	counts	\N
1902	cg_eng_port_dlog8_ld_quantity_int64_s	cg_eng_port_dlog8_ld	\N	cg eng port dlog8 ld	s	\N
1903	cg_eng_port_dlog8_lu_quantity_float64_s	cg_eng_port_dlog8_lu	\N	cg eng port dlog8 lu	s	\N
1904	cg_eng_dmgrstatus_date_quantity_string_1	cg_eng_dmgrstatus_date	\N	cg eng dmgrstatus date	1	\N
1905	cg_eng_dmgrstatus_time_quantity_string_1	cg_eng_dmgrstatus_time	\N	cg eng dmgrstatus time	1	\N
1906	cg_eng_dmgrstatus_active_quantity_int32_counts	cg_eng_dmgrstatus_active	\N	cg eng dmgrstatus active	counts	\N
1907	cg_eng_dmgrstatus_started_quantity_int32_counts	cg_eng_dmgrstatus_started	\N	cg eng dmgrstatus started	counts	\N
1908	cg_eng_dmgrstatus_halted_quantity_int32_counts	cg_eng_dmgrstatus_halted	\N	cg eng dmgrstatus halted	counts	\N
1909	cg_eng_dmgrstatus_failed_quantity_int32_counts	cg_eng_dmgrstatus_failed	\N	cg eng dmgrstatus failed	counts	\N
1910	cg_eng_dmgrstatus_map_quantity_string_1	cg_eng_dmgrstatus_map	\N	cg eng dmgrstatus map	1	\N
1911	cg_eng_dmgrstatus_update_quantity_float32_s	cg_eng_dmgrstatus_update	\N	cg eng dmgrstatus update	s	\N
1912	ctdpf_ckl_seawater_pressure_function_float32_dbar	ctdpf_ckl_seawater_pressure	\N	Sea Water Pressure, dBar	dbar	\N
1913	ctdpf_ckl_seawater_temperature_function_float32_deg_C	ctdpf_ckl_seawater_temperature	\N	Sea Water Temperature, Degrees Celsius	deg_C	\N
1914	ctdpf_ckl_seawater_conductivity_function_float32_S_m_1	ctdpf_ckl_seawater_conductivity	\N	Sea Water Conductivity, S m-1	S m-1	\N
1915	ctdpf_ckl_sci_water_pracsal_function_float32_1	ctdpf_ckl_sci_water_pracsal	\N	Practical Salinity (seawater salinity, PSS-78) [unitless]	1	\N
1916	ctdpf_ckl_seawater_density_function_float32_kg_m_3	ctdpf_ckl_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
1917	dofst_k_oxygen_quantity_uint32_Hz	dofst_k_oxygen	\N	Oxygen Concentration, Hz	Hz	\N
1918	dofst_k_oxygen_l2_function_float32_umol_L_1	dofst_k_oxygen_l2	\N	Estimated Oxygen Concentration, uMol	umol L-1	\N
1919	vel3d_k_eastward_turbulent_velocity_function_float32_m_s_1	vel3d_k_eastward_turbulent_velocity	\N	Eastward Turbulent Sea Water Velocity, m s-1	m s-1	\N
1920	vel3d_k_northward_turbulent_velocity_function_float32_m_s_1	vel3d_k_northward_turbulent_velocity	\N	Northward Turbulent Sea Water Velocity, m s-1	m s-1	\N
1921	vel3d_k_upward_turbulent_velocity_function_float32_m_s_1	vel3d_k_upward_turbulent_velocity	\N	Upward Turbulent Sea Water Velocity, m s-1	m s-1	\N
1922	cg_eng_port_dlog1_lc_quantity_int64_s	cg_eng_port_dlog1_lc	\N	cg eng port dlog1 ld	s	\N
1923	cg_eng_port_dlog2_lc_quantity_int64_s	cg_eng_port_dlog2_lc	\N	cg eng port dlog2 ld	s	\N
1924	cg_eng_port_dlog3_lc_quantity_int64_s	cg_eng_port_dlog3_lc	\N	cg eng port dlog3 ld	s	\N
1925	cg_eng_port_dlog4_lc_quantity_int64_s	cg_eng_port_dlog4_lc	\N	cg eng port dlog4 ld	s	\N
1926	cg_eng_port_dlog5_lc_quantity_int64_s	cg_eng_port_dlog5_lc	\N	cg eng port dlog5 ld	s	\N
1927	cg_eng_port_dlog6_lc_quantity_int64_s	cg_eng_port_dlog6_lc	\N	cg eng port dlog6 ld	s	\N
1928	cg_eng_port_dlog7_lc_quantity_int64_s	cg_eng_port_dlog7_lc	\N	cg eng port dlog7 ld	s	\N
1929	cg_eng_port_dlog8_lc_quantity_int64_s	cg_eng_port_dlog8_lc	\N	cg eng port dlog8 ld	s	\N
1930	gps_lat_external_float32_degree_north	gps_lat	\N	GPS Observed Latitude	degree_north	\N
1931	gps_lon_external_float32_degree_east	gps_lon	\N	GPS Observed Longitude	degree_east	\N
1932	dr_lat_external_float32_degree_north	dr_lat	\N	Dead Reckoning Latitude from Platform	degree_north	\N
1933	dr_lon_external_float32_degree_east	dr_lon	\N	Dead Reckoning Longitude from Platform	degree_east	\N
1934	adcps_jln_sysconfig_beam_angle_quantity_uint8_counts	adcps_jln_sysconfig_beam_angle	\N	Beam Angle, type	counts	\N
1935	adcps_jln_sysconfig_beam_config_quantity_uint8_counts	adcps_jln_sysconfig_beam_config	\N	Beam Configuration, type	counts	\N
1936	adcps_jln_real_time_clock_2_quantity_int16_array_	adcps_jln_real_time_clock_2	\N	Array of Real-time Clock	array<>	\N
1937	adcps_jln_ensemble_start_time_2_quantity_float64_seconds_since_1900_01_01	adcps_jln_ensemble_start_time_2	\N	Ensemble start time in seconds since Jan 01, 1900	seconds since 1900-01-01	\N
1938	vel3d_k_id_quantity_uint8_1	vel3d_k_id	\N	VEL3D Record ID	1	\N
1939	vel3d_k_version_quantity_uint8_counts	vel3d_k_version	\N	Version Number of Data Record	counts	\N
1940	vel3d_k_serial_quantity_uint32_counts	vel3d_k_serial	\N	VEL3D Serial Number	counts	\N
1941	vel3d_k_configuration_quantity_uint16_counts	vel3d_k_configuration	\N	Configuration Bit Mask	counts	\N
1942	vel3d_k_micro_second_quantity_uint16_counts	vel3d_k_micro_second	\N	Micro Second	counts	\N
1943	vel3d_k_speed_sound_quantity_uint16_counts	vel3d_k_speed_sound	\N	Speed of Sound	counts	\N
1944	vel3d_k_pressure_quantity_uint32_dbar	vel3d_k_pressure	\N	Pressure, dbar	dbar	\N
1945	vel3d_k_error_quantity_uint16_counts	vel3d_k_error	\N	Error	counts	\N
1946	vel3d_k_status_quantity_uint16_counts	vel3d_k_status	\N	Status	counts	\N
1947	vel3d_k_beams_coordinate_quantity_uint16_bit_mask	vel3d_k_beams_coordinate	\N	Beams & Coordinate system	bit mask	\N
1948	vel3d_k_cell_size_quantity_uint16_counts	vel3d_k_cell_size	\N	Cell Size, mm	counts	\N
1949	vel3d_k_blanking_quantity_uint16_counts	vel3d_k_blanking	\N	Blanking, mm	counts	\N
1950	vel3d_k_velocity_range_quantity_uint16_counts	vel3d_k_velocity_range	\N	Velocity Range, mm/s	counts	\N
1951	vel3d_k_battery_voltage_quantity_uint16_counts	vel3d_k_battery_voltage	\N	Battery Boltage, Volts	counts	\N
1952	vel3d_k_mag_x_quantity_int16_counts	vel3d_k_mag_x	\N	Magnetometer x-axis, Raw	counts	\N
1953	vel3d_k_mag_y_quantity_int16_counts	vel3d_k_mag_y	\N	Magnetometer y-axis, Raw	counts	\N
1954	vel3d_k_mag_z_quantity_int16_counts	vel3d_k_mag_z	\N	Magnetometer z-axis, Raw	counts	\N
1955	vel3d_k_acc_x_quantity_int16_counts	vel3d_k_acc_x	\N	Accelerometer x-axis, Raw	counts	\N
1956	vel3d_k_acc_y_quantity_int16_counts	vel3d_k_acc_y	\N	Accelerometer y-axis, Raw	counts	\N
1957	vel3d_k_acc_z_quantity_int16_counts	vel3d_k_acc_z	\N	Accelerometer z-axis, Raw	counts	\N
1958	vel3d_k_ambiguity_quantity_int16_counts	vel3d_k_ambiguity	\N	Ambiguity Velocity, mm/s	counts	\N
1959	vel3d_k_data_set_description_array_quantity_uint16_bit_mask	vel3d_k_data_set_description	\N	Data set description, Bit Mask	bit mask	\N
1960	vel3d_k_transmit_energy_quantity_uint16_counts	vel3d_k_transmit_energy	\N	Transmit Energy	counts	\N
1961	vel3d_k_power_level_quantity_int8_counts	vel3d_k_power_level	\N	Power Level, dB	counts	\N
1962	vel3d_k_corr0_quantity_int8_counts	vel3d_k_corr0	\N	Correlation 0, 0-100	counts	\N
1963	vel3d_k_corr1_quantity_int8_counts	vel3d_k_corr1	\N	Correlation 0, 0-100	counts	\N
1964	vel3d_k_corr2_quantity_int8_counts	vel3d_k_corr2	\N	Correlation 0, 0-100	counts	\N
1965	vel3d_k_str_id_quantity_uint8_counts	vel3d_k_str_id	\N	String ID, 0-15	counts	\N
1966	vel3d_k_string_quantity_string_1	vel3d_k_string	\N	String	1	\N
1967	cgl_eng_filename_quantity_string_1	cgl_eng_filename	\N	Source File Name, str	1	\N
1968	cgl_eng_mission_name_quantity_string_1	cgl_eng_mission_name	\N	Mission Name, str	1	\N
1969	cgl_eng_fileopen_time_quantity_string_1	cgl_eng_fileopen_time	\N	File Open Time, str	1	\N
1970	sensor_available_speed_boolean_int8_1	sensor_available_speed	\N	Sensor Available Speed	1	\N
1971	dosta_ln_optode_oxygen_quantity_float32_uM	dosta_ln_optode_oxygen	\N	Oxygen Reading	uM	\N
1972	dosta_ln_optode_temperature_quantity_float32_deg_C	dosta_ln_optode_temperature	\N	Temperature	deg_C	\N
1973	flord_wfp_chlorophyll_quantity_uint16_counts	flord_wfp_chlorophyll	\N	Raw Chlorophyll Measurement, counts	counts	\N
1974	flord_wfp_turbidity_quantity_uint16_counts	flord_wfp_turbidity	\N	Raw Turbidity Measurement, counts	counts	\N
1975	flord_wfp_temperature_quantity_uint16_counts	flord_wfp_temperature	\N	Raw Temperature Measurement, counts	counts	\N
1976	wfp_decimation_factor_quantity_uint16_1	wfp_decimation_factor	\N	Decimation Factor	1	\N
1977	trhph_system_info_quantity_string_1	trhph_system_info	\N	High Level System Information, str	1	\N
1978	trhph_eprom_status_boolean_int8_1	trhph_eprom_status	\N	Eprom Memory Status (0=not ready, 1 = ready to use)	1	\N
1979	trhph_cycle_time_quantity_int8_counts	trhph_cycle_time	\N	Cycle Time, counts	counts	\N
1980	trhph_cycle_time_units_category_int8_str_int8_1	trhph_cycle_time_units	\N	Cycle Time Units, str	1	\N
1981	trhph_power_control_word_quantity_int8_counts	trhph_power_control_word	\N	Power Control Word, counts	counts	\N
1982	trhph_res_power_status_boolean_int8_1	trhph_res_power_status	\N	Resistivity Sensor Power Status (0 = Off, 1 = On)	1	\N
1983	trhph_thermo_hydro_amp_power_status_boolean_int8_1	trhph_thermo_hydro_amp_power_status	\N	Instrumentation Amp Power Status (0 = Off, 1 = On)	1	\N
1984	trhph_eh_amp_power_status_boolean_int8_1	trhph_eh_amp_power_status	\N	eH Isolation Amp Power Status (0 = Off, 1 = On)	1	\N
1985	trhph_hydro_sensor_power_status_boolean_int8_1	trhph_hydro_sensor_power_status	\N	Hydrogen Sensor Power Status (0 = Off, 1 = On)	1	\N
1986	trhph_ref_temp_power_status_boolean_int8_1	trhph_ref_temp_power_status	\N	Reference Temperature Sensor Power Status (0 = Off, 1 = On)	1	\N
1987	trhph_metadata_on_powerup_boolean_int8_1	trhph_metadata_on_powerup	\N	Metadata at Startup (0 = No Print on Powerup, 1 = Print)	1	\N
1988	trhph_metadata_on_restart_boolean_int8_1	trhph_metadata_on_restart	\N	Metadata at Restart (0 = No Print on Powerup, 1 = Print)	1	\N
1989	spkir_a_firmware_version_quantity_string_1	spkir_a_firmware_version	\N	Firmware Version, str	1	\N
1990	number_measurements_per_reported_value_quantity_uint16_counts	number_measurements_per_reported_value	\N	Number of Measurements per Value, counts	counts	\N
1991	number_of_reported_values_per_packet_quantity_uint16_counts	number_of_reported_values_per_packet	\N	Number of Values per Packet, counts	counts	\N
1992	measurement_1_dark_count_value_quantity_uint16_counts	measurement_1_dark_count_value	\N	Measurement 1 (Scattering) Dark Count Value	counts	\N
1993	measurement_2_dark_count_value_quantity_uint16_counts	measurement_2_dark_count_value	\N	Measurement 2 (Chlorophyll) Dark Count Value	counts	\N
1994	measurement_3_dark_count_value_quantity_uint16_counts	measurement_3_dark_count_value	\N	Measurement 3 (CDOM) Dark Count Value	counts	\N
1995	measurement_1_slope_value_quantity_float32_m_1_sr_1_counts_1	measurement_1_slope_value	\N	Measurement 1 (Scattering) Scale Factor, m-1 sr-1 counts-1	m-1 sr-1 counts-1	\N
1996	measurement_2_slope_value_quantity_float32_ug_L_1_counts_1	measurement_2_slope_value	\N	Measurement 2 (Chlorophyll) Scale Factor, ug L-1 counts-1	ug L-1 counts-1	\N
1997	measurement_3_slope_value_quantity_float32_ppb_counts_1	measurement_3_slope_value	\N	Measurement 3 (CDOM) Scale Factor, ppb counts-1	ppb counts-1	\N
1998	predefined_output_sequence_quantity_uint16_counts	predefined_output_sequence	\N	Predefined Output Sequence	counts	\N
1999	baud_rate_quantity_uint16_Bd	baud_rate	\N	Baud Rate	Bd	\N
2000	number_of_packets_per_set_quantity_uint16_counts	number_of_packets_per_set	\N	Number of Packets per Set	counts	\N
2001	recording_mode_quantity_uint16_1	recording_mode	\N	Recording Mode	1	\N
2002	manual_mode_quantity_uint16_1	manual_mode	\N	Manual Mode	1	\N
2003	sampling_interval_quantity_string_1	sampling_interval	\N	Sampling Interval, str	1	\N
2004	date_quantity_string_1	date	\N	Date, str	1	\N
2005	clock_quantity_string_1	clock	\N	Time, str	1	\N
2006	manual_start_time_quantity_string_1	manual_start_time	\N	Manual Start Time, str	1	\N
2007	internal_memory_quantity_uint16_bytes	internal_memory	\N	Internal Memory	bytes	\N
2008	pco2w_battery_voltage_quantity_uint16_counts	pco2w_battery_voltage	\N	Battery Voltage, V	counts	\N
2009	pco2w_thermistor_voltage_quantity_uint16_counts	pco2w_thermistor_voltage	\N	Thermistor Voltage, V	counts	\N
2010	glider_eng_filename_quantity_string_1	glider_eng_filename	\N	Name of the source file for the glider	1	\N
2011	glider_mission_name_quantity_string_1	glider_mission_name	\N	Mission the glider was executing at the time the file was logged	1	\N
2012	glider_eng_fileopen_time_quantity_string_1	glider_eng_fileopen_time	\N	Time the file was opened	1	\N
2013	sensor_source_temperature_eu_boolean_int8_1	sensor_source_temperature_eu	\N	Transducer Temperature Sensor Source	1	\N
2014	sensor_available_temperature_eu_boolean_int8_1	sensor_available_temperature_eu	\N	Temperature sensor installed	1	\N
2015	bit_error_number_quantity_int8_1	bit_error_number	\N	BIT Error Number	1	\N
2016	bit_error_count_quantity_int8_counts	bit_error_count	\N	Number of BIT errors	counts	\N
2017	sysconfig_beam_angle_category_int8_str_int8_1	sysconfig_beam_angle	\N	Beam Angle, type	1	\N
2018	sysconfig_beam_config_category_int8_str_int8_1	sysconfig_beam_config	\N	Beam Configuration, type	1	\N
2019	id_quantity_int32_counts	id	\N	Identification	counts	\N
2020	channels_array_quantity_int32_counts	channels	\N	List of Channel Dicts	counts	\N
2024	srcname_quantity_string_1	srcname	\N	Source Name Parts	1	\N
2025	string_quantity_string_1	string	\N	Arbitrary String Data	1	\N
2026	packet_time_quantity_float64_counts	packet_time	\N	Packet Timestamp	counts	\N
2027	type_quantity_string_1	type	\N	Packet Type	1	\N
2028	version_quantity_int32_counts	version	\N	Packet Version	counts	\N
2029	calib_quantity_float64_counts	calib	\N	Calibration	counts	\N
2030	calper_quantity_float64_counts	calper	\N	Calper	counts	\N
2031	chan_quantity_string_1	chan	\N	Channel code	1	\N
2032	cuser1_quantity_string_1	cuser1	\N	User-defined Field 1, string	1	\N
2033	cuser2_quantity_string_1	cuser2	\N	User-defined Field 2, string	1	\N
2034	data_array_quantity_float32_counts	data	\N	Data, first element determines type	counts	\N
2035	duser1_quantity_float64_counts	duser1	\N	User-defined Field 1, float32	counts	\N
2036	duser2_quantity_float64_counts	duser2	\N	User-defined Field 2, float32	counts	\N
2037	iuser1_quantity_int32_counts	iuser1	\N	User-defined Field 1, int32	counts	\N
2038	iuser2_quantity_int32_counts	iuser2	\N	User-defined Field 2, int32	counts	\N
2039	iuser3_quantity_int32_counts	iuser3	\N	User-defined Field 3, int32	counts	\N
2040	loc_quantity_string_1	loc	\N	Location Code	1	\N
2041	net_quantity_string_1	net	\N	Network Code	1	\N
2042	nsamp_quantity_int32_counts	nsamp	\N	Number of Samples	counts	\N
2043	samprate_quantity_float64_counts	samprate	\N	Sample Rate	counts	\N
2044	segtype_quantity_string_1	segtype	\N	Segment Type	1	\N
2045	sta_quantity_string_1	sta	\N	Station Code	1	\N
2046	channel_time_quantity_float64_counts	channel_time	\N	Channel Timestamp	counts	\N
2047	suffix_quantity_string_1	suffix	\N	Suffix code	1	\N
2048	subcode_quantity_int32_counts	subcode	\N	Subcode	counts	\N
2049	joined_quantity_string_1	joined	\N	Fields joined by delimiter	1	\N
2050	content_quantity_int32_counts	content	\N	Content	counts	\N
2051	name_quantity_string_1	name	\N	Name	1	\N
2052	hdrcode_quantity_string_1	hdrcode	\N	HDR code	1	\N
2053	bodycode_quantity_uint32_counts	bodycode	\N	Body code	counts	\N
2054	desc_quantity_uint32_counts	desc	\N	Description	counts	\N
2055	sio_controller_id_quantity_uint32_1	sio_controller_id	\N	sio controller id	1	\N
2056	sio_controller_timestamp_quantity_uint32_seconds_since_1970_01_01	sio_controller_timestamp	\N	sio controller timestamp, seconds since 1970-01-01	seconds since 1970-01-01	\N
2057	sio_eng_voltage_quantity_float32_V	sio_eng_voltage	\N	sio eng voltage, V	V	\N
2058	sio_eng_temperature_quantity_float32_deg_C	sio_eng_temperature	\N	sio eng temperature, degrees Celsius	deg_C	\N
2059	sio_eng_on_time_quantity_uint32_s	sio_eng_on_time	\N	sio eng on time, seconds	s	\N
2060	sio_eng_number_of_wakeups_quantity_uint32_1	sio_eng_number_of_wakeups	\N	sio eng number of wakeups	1	\N
2061	sio_eng_clock_drift_quantity_int32_s	sio_eng_clock_drift	\N	sio eng clock drift, seconds	s	\N
2062	adcp_ambient_temp_quantity_float32_deg_C	adcp_ambient_temp	\N	Ambient Temperature, degC	deg_C	\N
2063	adcp_attitude_temp_quantity_float32_deg_C	adcp_attitude_temp	\N	Attitude Temperature, degC	deg_C	\N
2064	adcp_internal_moisture_quantity_string_1	adcp_internal_moisture	\N	Internal Moisture	1	\N
2065	adcp_transmit_current_quantity_float32_Amps	adcp_transmit_current	\N	Transmit Current, Amps	Amps	\N
2066	adcp_transmit_voltage_quantity_float32_V	adcp_transmit_voltage	\N	Transmit Voltage, V	V	\N
2067	adcp_transmit_impedance_quantity_float32_Ohms	adcp_transmit_impedance	\N	Transmit Impedance, Ohms	Ohms	\N
2068	adcp_transmit_test_results_quantity_string_1	adcp_transmit_test_results	\N	Transmit Test Results	1	\N
2069	lily_out_of_range_boolean_int8_1	lily_out_of_range	\N	LILY tilt sensor out of range (0=FALSE, 1=TRUE)	1	\N
2070	lily_leveling_status_quantity_string_1	lily_leveling_status	\N	LILY re-level status	1	\N
2071	botpt_iris_status_01_quantity_string_1	botpt_iris_status_01	\N	Iris Status 1	1	\N
2072	botpt_iris_status_02_quantity_string_1	botpt_iris_status_02	\N	Iris Status 2	1	\N
2073	botpt_lily_status_01_quantity_string_1	botpt_lily_status_01	\N	Lily Status 1	1	\N
2074	botpt_lily_status_02_quantity_string_1	botpt_lily_status_02	\N	Lily Status 2	1	\N
2075	botpt_nano_status_quantity_string_1	botpt_nano_status	\N	Nano Status	1	\N
2076	ctd_time_offset_quantity_int32_s	ctd_time_offset	\N	CTD Time Correction Offset, secs	s	\N
2077	passed_checksum_boolean_int8_1	passed_checksum	\N	Passed the checksum, False or True.	1	\N
2078	vel3d_l_date_time_array_array_quantity_uint16_1	vel3d_l_date_time_array	\N	Date Time Array, yyyy, mm, dd, hh, mm, ss	1	\N
2079	vel3d_l_heading_quantity_float32_degrees	vel3d_l_heading	\N	Instrument Heading, degrees	degrees	\N
2080	vel3d_l_tx_quantity_float32_degrees	vel3d_l_tx	\N	X component of Tilt, degrees	degrees	\N
2081	vel3d_l_ty_quantity_float32_degrees	vel3d_l_ty	\N	Y component of Tilt, degrees	degrees	\N
2082	vel3d_l_hx_quantity_float32_1	vel3d_l_hx	\N	Compass X	1	\N
2083	vel3d_l_hy_quantity_float32_1	vel3d_l_hy	\N	Compass Y	1	\N
2084	vel3d_l_hz_quantity_float32_1	vel3d_l_hz	\N	Compass Z	1	\N
2085	vel3d_l_vp1_quantity_float32_cm_s_1	vel3d_l_vp1	\N	Path Velocity 1, cm/sec	cm s-1	\N
2086	vel3d_l_vp2_quantity_float32_cm_s_1	vel3d_l_vp2	\N	Path Velocity 2, cm/sec	cm s-1	\N
2087	vel3d_l_vp3_quantity_float32_cm_s_1	vel3d_l_vp3	\N	Path Velocity 3, cm/sec	cm s-1	\N
2088	vel3d_l_vp4_quantity_float32_cm_s_1	vel3d_l_vp4	\N	Path Velocity 4,, cm/sec	cm s-1	\N
2089	vel3d_l_number_of_records_quantity_uint16_counts	vel3d_l_number_of_records	\N	Number of records in the file	counts	\N
2090	vel3d_l_time_on_quantity_uint32_seconds_since_1970_01_01	vel3d_l_time_on	\N	Time Sensor Start, Seconds since Jan 1 1970 UTC	seconds since 1970-01-01	\N
2091	vel3d_l_time_off_quantity_uint32_seconds_since_1970_01_01	vel3d_l_time_off	\N	Time Sensor Stop, Seconds since Jan 1 1970 UTC	seconds since 1970-01-01	\N
2092	vel3d_l_decimation_factor_quantity_uint16_1	vel3d_l_decimation_factor	\N	Full Decimation Factor	1	\N
2093	vel3d_l_controller_timestamp_quantity_uint32_seconds_since_1970_01_01	vel3d_l_controller_timestamp	\N	Controller timestamp, Seconds since Jan 1 1970 UTC	seconds since 1970-01-01	\N
2094	raw_time_seconds_quantity_uint32_seconds_since_1970_01_01	raw_time_seconds	\N	Seconds since 1/1/1970	seconds since 1970-01-01	\N
2095	raw_time_microseconds_quantity_uint32_us	raw_time_microseconds	\N	Microsecond portion of seconds since 1/1/1970	us	\N
2096	vel3d_a_va_quantity_float64_cm_s_1	vel3d_a_va	\N	Path Velocity axis A, cm/sec	cm s-1	\N
2097	vel3d_a_vb_quantity_float64_cm_s_1	vel3d_a_vb	\N	Path Velocity  axis B, cm/sec	cm s-1	\N
2098	vel3d_a_vc_quantity_float64_cm_s_1	vel3d_a_vc	\N	Path Velocity  axis C, cm/sec	cm s-1	\N
2099	vel3d_a_vd_quantity_float64_cm_s_1	vel3d_a_vd	\N	Path Velocity axis D, cm/sec	cm s-1	\N
2100	vel3d_a_hx_quantity_float64_1	vel3d_a_hx	\N	Normalized X component of the magnetic flux	1	\N
2101	vel3d_a_hy_quantity_float64_1	vel3d_a_hy	\N	Normalized Y component of the magnetic flux	1	\N
2102	vel3d_a_hz_quantity_float64_1	vel3d_a_hz	\N	Normalized Z component of the magnetic flux	1	\N
2103	vel3d_a_tx_quantity_float64_degrees	vel3d_a_tx	\N	X component of the instrument tilt, degrees	degrees	\N
2104	vel3d_a_ty_quantity_float64_degrees	vel3d_a_ty	\N	Y component of the instrument tilt, degrees	degrees	\N
2105	cdomflo_quantity_uint32_counts	cdomflo	\N	Raw Chlorophyll Measurement, counts	counts	\N
2106	chlaflo_quantity_uint32_counts	chlaflo	\N	Raw Chlorophyll Measurement, counts	counts	\N
2107	ntuflo_quantity_uint32_counts	ntuflo	\N	Raw Turbidity/Scattering Measurement, counts	counts	\N
2108	thsph_hie1_quantity_int16_counts	thsph_hie1	\N	High Impedance Electrode 1 for pH, counts	counts	\N
2109	thsph_hie2_quantity_int16_counts	thsph_hie2	\N	High Impedance Electrode 2 for pH, counts	counts	\N
2110	thsph_h2electrode_quantity_int16_counts	thsph_h2electrode	\N	H2 electrode, counts	counts	\N
2111	thsph_s2electrode_quantity_int16_counts	thsph_s2electrode	\N	Sulfide Electrode, counts	counts	\N
2112	thsph_thermocouple1_quantity_int16_counts	thsph_thermocouple1	\N	Type E thermocouple 1-high, counts	counts	\N
2113	thsph_thermocouple2_quantity_int16_counts	thsph_thermocouple2	\N	Type E thermocouple 2-low, counts	counts	\N
2114	thsph_rthermistor_quantity_int16_counts	thsph_rthermistor	\N	Reference Thermistor, counts	counts	\N
2115	thsph_bthermistor_quantity_int16_counts	thsph_bthermistor	\N	Board Thermistor, counts	counts	\N
2116	adcps_jln_upward_seawater_velocity2_function_float32_m_s_1	adcps_jln_upward_seawater_velocity2	\N	Upward Sea Water Velocity, m s-1	m s-1	\N
2117	adcps_jln_error_velocity2_function_float32_m_s_1	adcps_jln_error_velocity2	\N	Error Velocity, m s-1	m s-1	\N
2118	adcps_jln_eastward_seawater_velocity2_function_float32_m_s_1	adcps_jln_eastward_seawater_velocity2	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
2119	adcps_jln_northward_seawater_velocity2_function_float32_m_s_1	adcps_jln_northward_seawater_velocity2	\N	Northward Sea Water Velocity, m s-1	m s-1	\N
2120	strain_pressure_sensor_serial_number_quantity_string_1	strain_pressure_sensor_serial_number	\N	Strain Pressure Sensor Serial Number	1	\N
2121	volt0_type_quantity_string_1	volt0_type	\N	Volt 0 Type	1	\N
2122	volt0_serial_number_quantity_string_1	volt0_serial_number	\N	Volt 0 Serial Number	1	\N
2123	volt1_type_quantity_string_1	volt1_type	\N	Volt 1 Type	1	\N
2124	volt1_serial_number_quantity_string_1	volt1_serial_number	\N	Volt 1 Serial Number	1	\N
2125	profiles_quantity_int32_counts	profiles	\N	Profiles	counts	\N
2126	scans_to_average_quantity_int16_counts	scans_to_average	\N	Scans to Average	counts	\N
2127	min_cond_freq_quantity_int16_counts	min_cond_freq	\N	Minimum Conductivity Frequency	counts	\N
2128	pump_delay_quantity_int16_counts	pump_delay	\N	Pump Delay	counts	\N
2129	auto_run_boolean_int8_1	auto_run	\N	Auto Run	1	\N
2130	ignore_switch_boolean_int8_1	ignore_switch	\N	Ignore Switch	1	\N
2131	battery_type_quantity_string_1	battery_type	\N	Battery Type	1	\N
2132	sbe63_boolean_int8_1	sbe63	\N	SBE63 pressure sensor flag	1	\N
2133	calphase_quantity_float32_degrees	calphase	\N	Calibrated Phase	degrees	\N
2134	enable_temperature_boolean_int8_	enable_temperature	\N	Inclusion of Temperature in the output	 	\N
2135	enable_humiditycomp_boolean_int8_	enable_humiditycomp	\N	Enable humidity compensation for vapor pressure	 	\N
2136	enable_airsaturation_boolean_int8_	enable_airsaturation	\N	Enable Air Saturation	 	\N
2137	enable_rawdata_boolean_int8_	enable_rawdata	\N	Enable Raw Data	 	\N
2138	analog_output_quantity_string_1	analog_output	\N	Analog Output	1	\N
2139	interval_quantity_float32_seconds	interval	\N	Interval	 seconds	\N
2140	ext_volt0_quantity_int32_counts	ext_volt0	\N	External Voltage Reading from Oxygen Sensor	counts	\N
2141	profiler_timestamp_quantity_float64_seconds_since_1970_01_01	profiler_timestamp	\N	Surface-Piercing Profiler Timestamp, UTC	seconds since 1970-01-01	\N
2142	last_character_controller_id_quantity_string_1	last_character_controller_id	\N	Last character controller id	1	\N
2143	day_of_year_number_quantity_uint16_1	day_of_year_number	\N	Day of year number	1	\N
2144	fraction_of_day_quantity_uint16_1	fraction_of_day	\N	Fraction of day	1	\N
2145	source_file_quantity_string_1	source_file	\N	Source file	1	\N
2146	processing_time_quantity_string_1	processing_time	\N	Processing time	1	\N
2147	preprocessing_software_version_quantity_string_1	preprocessing_software_version	\N	Preprocessing software version	1	\N
2148	start_date_quantity_string_1	start_date	\N	Start date	1	\N
2149	channel_array_array_quantity_uint32_counts	channel_array	\N	A/D Counts for All 7 Optical Channels: 1 = 412nm, 2 = 443nm, 3 = 490nm, 4 = 510nm, 5 = 555nm, 6 = 620nm, 7 = 683nm.	counts	\N
2150	nutnr_nitrogen_in_nitrate_quantity_float32_mg/l	nutnr_nitrogen_in_nitrate	\N	Nitrogen in Nitrate	mg/l	\N
2151	nutnr_absorbance_at_254_nm_quantity_float32_1	nutnr_absorbance_at_254_nm	\N	Absorbance at 254 nm	1	\N
2152	nutnr_absorbance_at_350_nm_quantity_float32_1	nutnr_absorbance_at_350_nm	\N	Absorbance at 350 nm	1	\N
2153	nutnr_bromide_trace_quantity_float32_mg/l	nutnr_bromide_trace	\N	Bromide Trace	mg/l	\N
2154	nutnr_spectrum_average_quantity_uint16_1	nutnr_spectrum_average	\N	Spectrum Average	1	\N
2155	nutnr_dark_value_used_for_fit_quantity_uint16_1	nutnr_dark_value_used_for_fit	\N	Dark Value Used for Fit	1	\N
2156	nutnr_integration_time_factor_quantity_uint8 _1	nutnr_integration_time_factor	\N	Integration Time Factor	1	\N
2157	nutnr_voltage_int_quantity_float32_V	nutnr_voltage_int	\N	Internal Power Supply Voltage	V	\N
2158	nutnr_current_main_quantity_float32_mA	nutnr_current_main	\N	Main Current	mA	\N
2159	nutnr_fit_base_1_quantity_float32_1	nutnr_fit_base_1	\N	Fit Base 1	1	\N
2160	nutnr_fit_base_2_quantity_float32_1	nutnr_fit_base_2	\N	Fit Base 2	1	\N
2161	nutnr_fit_rmse_quantity_float32_1	nutnr_fit_rmse	\N	Fit RMSE	1	\N
2162	nutnr_sensor_type_quantity_string_1	nutnr_sensor_type	\N	Sensor Type	1	\N
2163	nutnr_sensor_version_quantity_string_1	nutnr_sensor_version	\N	Sensor Version	1	\N
2164	nutnr_integrated_wiper _quantity_string_1	nutnr_integrated_wiperÂ 	\N	Integrated Wiper 	1	\N
2165	nutnr_ext_power_port _quantity_string_1	nutnr_ext_power_portÂ 	\N	External Power Port 	1	\N
2166	nutnr_lamp_shutter_quantity_string_1	nutnr_lamp_shutter	\N	Lamp Shutter	1	\N
2167	nutnr_reference_detector _quantity_string_1	nutnr_reference_detectorÂ 	\N	Reference Detector 	1	\N
2168	nutnr_wiper_protector_quantity_string_1	nutnr_wiper_protector	\N	Wiper Protector	1	\N
2169	nutnr_super_capacitors_quantity_string_1	nutnr_super_capacitors	\N	Super Capacitors	1	\N
2170	nutnr_psb_supervisor_quantity_string_1	nutnr_psb_supervisor	\N	PCB Supervisor	1	\N
2171	nutnr_usb_communication_quantity_string_1	nutnr_usb_communication	\N	USB Communication	1	\N
2172	nutnr_relay_module_quantity_string_1	nutnr_relay_module	\N	Relay Module	1	\N
2173	nutnr_sdi12_interface_quantity_string_1	nutnr_sdi12_interface	\N	SDI-12 Interface	1	\N
2174	nutnr_analog_output_quantity_string_1	nutnr_analog_output	\N	Analog Output	1	\N
2175	nutnr_int_data_logging_quantity_string_1	nutnr_int_data_logging	\N	Internal Data Logging	1	\N
2176	nutnr_apf_interface_quantity_string_1	nutnr_apf_interface	\N	APF Interface	1	\N
2177	nutnr_scheduling_quantity_string_1	nutnr_scheduling	\N	Scheduling	1	\N
2178	nutnr_lamp_fan_quantity_string_1	nutnr_lamp_fan	\N	Lamp Fan	1	\N
2179	nutnr_sensor_address_lamp_temp_quantity_string_1	nutnr_sensor_address_lamp_temp	\N	Address of Lamp Temperature Sensor	1	\N
2180	nutnr_sensor_address_spec_temp _quantity_string_1	nutnr_sensor_address_spec_tempÂ 	\N	Address of Spectrometer Temperature Sensor	1	\N
2181	nutnr_sensor_address_hous_temp_quantity_string_1	nutnr_sensor_address_hous_temp	\N	Address of Housing Temperature Sensor	1	\N
2182	nutnr_serial_number_spec_quantity_string_1	nutnr_serial_number_spec	\N	Spectrometer Serial Number	1	\N
2183	nutnr_serial_number_lamp_quantity_string_1	nutnr_serial_number_lamp	\N	Lamp Serial Number	1	\N
2184	nutnr_stupstus_quantity_string_1	nutnr_stupstus	\N	Setup Status	1	\N
2185	nutnr_brnhours_quantity_uint16_	nutnr_brnhours	\N	Brn Hours Counter	\N	\N
2186	nutnr_brnnumbr_quantity_uint16_	nutnr_brnnumbr	\N	Brn Number Counter	\N	\N
2187	nutnr_drkhours_quantity_uint16_	nutnr_drkhours	\N	Dark Hours Counter	\N	\N
2188	nutnr_output_dark_frame_quantity_string_1	nutnr_output_dark_frame	\N	Output Dark Frame	1	\N
2189	nutnr_logging_dark_frame_quantity_string_1	nutnr_logging_dark_frame	\N	Logging Dark Frame	1	\N
2190	nutnr_timeresl_quantity_string_1	nutnr_timeresl	\N	Time Resolution	1	\N
2191	nutnr_log_file_type_quantity_string_1	nutnr_log_file_type	\N	Log File Type	1	\N
2192	nutnr_acqcount_quantity_uint16_counts	nutnr_acqcount	\N	Acquisition Counter	counts	\N
2193	nutnr_cntcount_quantity_uint16_counts	nutnr_cntcount	\N	Continuous Counter	counts	\N
2194	nutnr_dac_nitrate_min_quantity_float32_uMol	nutnr_dac_nitrate_min	\N	DAC Minimum Nitrate	uMol 	\N
2195	nutnr_dac_nitrate_max_quantity_float32_uMol	nutnr_dac_nitrate_max	\N	DAC Maximum Nitrate	uMol 	\N
2196	nutnr_data_wavelength_low_quantity_float32_nm	nutnr_data_wavelength_low	\N	Data Wavelength Low	nm	\N
2197	nutnr_drknumbr_quantity_uint16_counts	nutnr_drknumbr	\N	Dark Number Counter	counts	\N
2198	nutnr_chrldura_quantity_uint16_s	nutnr_chrldura	\N	Light Duration Counter	s	\N
2199	nutnr_chrddura_quantity_uint16_s	nutnr_chrddura	\N	Dark Duration Counter	s	\N
2200	nutnr_msg_level_quantity_string_1	nutnr_msg_level	\N	Message Level	1	\N
2201	nutnr_msg_file_size_quantity_uint8 _MB	nutnr_msg_file_size	\N	Message File Size	MB	\N
2202	nutnr_data_file_size_quantity_uint8 _MB	nutnr_data_file_size	\N	Data File Size	MB	\N
2203	nutnr_output_frame_type_quantity_string_1	nutnr_output_frame_type	\N	Output Frame Type	1	\N
2204	nutnr_logging_frame_type_quantity_string_1	nutnr_logging_frame_type	\N	Logging Frame Type	1	\N
2205	nutnr_data_wavelength_high_quantity_float32_nm	nutnr_data_wavelength_high	\N	Data Wavelength High	nm	\N
2206	nutnr_sdi12_address_quantity_uint16_1	nutnr_sdi12_address	\N	SDI 12 Address	1	\N
2207	nutnr_data_mode_quantity_string_1	nutnr_data_mode	\N	Data Mode	1	\N
2208	nutnr_operating_mode_quantity_string_1	nutnr_operating_mode	\N	Operation Mode	1	\N
2209	nutnr_operation_ctrl_quantity_string_1	nutnr_operation_ctrl	\N	Operation Control	1	\N
2210	nutnr_extl_dev_quantity_string_1	nutnr_extl_dev	\N	External Device	1	\N
2211	nutnr_ext_dev_prerun_time_quantity_uint8 _s	nutnr_ext_dev_prerun_time	\N	External Device Pre-run time	s	\N
2212	nutnr_ext_dev_during_acq_quantity_string_1	nutnr_ext_dev_during_acq	\N	External Device During Acq.	1	\N
2213	nutnr_watchdog_timer_quantity_string_1	nutnr_watchdog_timer	\N	Wachdog Timer	1	\N
2214	nutnr_countdown_quantity_uint16_s	nutnr_countdown	\N	Countdown	s	\N
2215	nutnr_fixed_time_duration_quantity_uint32_s	nutnr_fixed_time_duration	\N	Fixed time duration	s	\N
2216	nutnr_periodic_interval_quantity_string_1	nutnr_periodic_interval	\N	Periodic interval	1	\N
2217	nutnr_periodic_offset_quantity_uint16_counts	nutnr_periodic_offset	\N	Periodic offset	counts	\N
2218	nutnr_periodic_duration_quantity_uint8 _s	nutnr_periodic_duration	\N	Periodic duration	s	\N
2219	nutnr_periodic_samples_quantity_uint8 _counts	nutnr_periodic_samples	\N	Periodic samples	counts	\N
2220	nutnr_polled_timeout_quantity_uint32_s	nutnr_polled_timeout	\N	Polled Timeout	s	\N
2221	nutnr_apf_timeout_quantity_float32_s	nutnr_apf_timeout	\N	APF timeout	s	\N
2222	nutnr_lamp_stability_time_quantity_uint8 _s	nutnr_lamp_stability_time	\N	Lamp Stability Time	s	\N
2223	nutnr_ref_min_lamp_on_quantity_uint16_s	nutnr_ref_min_lamp_on	\N	Reference Minute at Lamp-On	s	\N
2224	nutnr_skip_sleep_quantity_string_1	nutnr_skip_sleep	\N	Skip Sleep at Start	1	\N
2225	nutnr_lamp_switchoff_temp_quantity_uint8_deg_C	nutnr_lamp_switchoff_temp	\N	Lamp Switch-Off Temperature	deg_C	\N
2226	nutnr_spec_integration_period_quantity_uint16_ms	nutnr_spec_integration_period	\N	Spectrometer Integration Period	ms	\N
2227	nutnr_dark_avg_quantity_uint8 _1	nutnr_dark_avg	\N	Dark Averages	1	\N
2228	nutnr_light_avg_quantity_uint8 _1	nutnr_light_avg	\N	Light Averages	1	\N
2229	nutnr_reference_samples_quantity_uint16_1	nutnr_reference_samples	\N	Reference Samples	1	\N
2230	nutnr_dark_samples_quantity_uint16_1	nutnr_dark_samples	\N	Dark Samples	1	\N
2231	nutnr_light_samples_quantity_uint16_1	nutnr_light_samples	\N	Light Samples	1	\N
2232	nutnr_dark_duration_quantity_uint16_s	nutnr_dark_duration	\N	Dark Duration	s	\N
2233	nutnr_light_duration_quantity_uint16_s	nutnr_light_duration	\N	Light Duration	s	\N
2234	nutnr_temp_comp_quantity_string_1	nutnr_temp_comp	\N	Temperature Compensation	1	\N
2235	nutnr_salinity_fit_quantity_string_1	nutnr_salinity_fit	\N	Salinity Fitting	1	\N
2236	nutnr_bromide_tracing_quantity_string_1	nutnr_bromide_tracing	\N	Bromide Tracing	1	\N
2237	nutnr_baseline_order_quantity_uint8 _1	nutnr_baseline_order	\N	Baseline Order	1	\N
2238	nutnr_concentrations_fit_quantity_uint8 _1	nutnr_concentrations_fit	\N	Concentrations to Fit	1	\N
2239	nutnr_dark_corr_method_quantity_string_1	nutnr_dark_corr_method	\N	Dark Correction Method	1	\N
2240	nutnr_dark_coefs_quantity_string_1	nutnr_dark_coefs	\N	Dark Coefficients	1	\N
2241	nutnr_davgprm0_quantity_float32_1	nutnr_davgprm0	\N	Dark Correction 0	1	\N
2242	nutnr_davgprm1_quantity_float32_1	nutnr_davgprm1	\N	Dark Correction 1	1	\N
2243	nutnr_davgprm2_quantity_float32_1	nutnr_davgprm2	\N	Dark Correction 2	1	\N
2244	nutnr_davgprm3_quantity_float32_1	nutnr_davgprm3	\N	Dark Correction 3	1	\N
2245	nutnr_absorbance_cutoff_quantity_float32_1	nutnr_absorbance_cutoff	\N	Absorbance Cutoff	1	\N
2246	nutnr_int_time_adj_quantity_string_1	nutnr_int_time_adj	\N	Integration Time Adjustment	1	\N
2247	nutnr_int_time_factor_quantity_uint8 _s	nutnr_int_time_factor	\N	Integration Time Factor	s	\N
2248	nutnr_int_time_step_quantity_uint8 _s	nutnr_int_time_step	\N	Integration Time Step	s	\N
2249	nutnr_int_time_max_quantity_uint8 _s	nutnr_int_time_max	\N	Integration Time Max	s	\N
2250	nutnr_fit_wavelength_low_quantity_float32_nm	nutnr_fit_wavelength_low	\N	Fit Wavelength Low	nm	\N
2251	nutnr_fit_wavelength_high_quantity_float32_nm	nutnr_fit_wavelength_high	\N	Fit Wavelength High	nm	\N
2252	nutnr_lamp_time_quantity_int32_s	nutnr_lamp_time	\N	Total Lamp on-time	s	\N
2253	nutnr_activecalfile _quantity_string_1	nutnr_activecalfileÂ 	\N	Active calibration file	1	\N
2254	nutnr_external_disk_size_quantity_uint32_MB	nutnr_external_disk_size	\N	External Disk Size	MB	\N
2255	nutnr_external_disk_free_quantity_uint32_MB	nutnr_external_disk_free	\N	External Disk Free	MB	\N
2256	nutnr_internal_disk_size_quantity_uint32_MB	nutnr_internal_disk_size	\N	Internal Disk Size	MB	\N
2257	nutnr_internal_disk_free_quantity_uint32_MB	nutnr_internal_disk_free	\N	Internal Disk Free	MB	\N
2258	nutnr_electrical_mn_quantity_float32_V	nutnr_electrical_mn	\N	Electrical Mn	V	\N
2259	nutnr_electrical_bd_quantity_float32_V	nutnr_electrical_bd	\N	Electrical Bd	V	\N
2260	nutnr_electrical_pr_quantity_float32_V	nutnr_electrical_pr	\N	Electrical Pr	V	\N
2261	nutnr_electrical_c_quantity_float32_mA	nutnr_electrical_c	\N	Electrical C	mA	\N
2262	nutnr_lamp_power_quantity_uint16 _mW	nutnr_lamp_power	\N	Lamp Power	mW	\N
2263	nutnr_spec_dark_av_quantity_uint16 _counts	nutnr_spec_dark_av	\N	Spectrometer Dark Average	counts	\N
2264	nutnr_spec_dark_sd_quantity_uint16 _counts	nutnr_spec_dark_sd	\N	Spectrometer Dark Std	counts	\N
2265	nutnr_spec_dark_mi_quantity_uint16 _counts	nutnr_spec_dark_mi	\N	Spectrometer Dark Min	counts	\N
2266	nutnr_spec_dark_ma_quantity_uint16 _counts	nutnr_spec_dark_ma	\N	Spectrometer Dark Max	counts	\N
2267	nutnr_spec_lght_av_quantity_uint16 _counts	nutnr_spec_lght_av	\N	Spectrometer Light Average	counts	\N
2268	nutnr_spec_lght_sd_quantity_uint16 _counts	nutnr_spec_lght_sd	\N	Spectrometer Light Std	counts	\N
2269	nutnr_spec_lght_mi_quantity_uint16 _counts	nutnr_spec_lght_mi	\N	Spectrometer Light Min	counts	\N
2270	nutnr_spec_lght_ma_quantity_uint16 _counts	nutnr_spec_lght_ma	\N	Spectrometer Light Max	counts	\N
2271	nutnr_test_result_quantity_string_1	nutnr_test_result	\N	Test Result	1	\N
2272	temp_sal_corrected_nitrate_function_float32_uMol_L_1	temp_sal_corrected_nitrate	\N	Temperature Salinity Corrected Nitrate	uMol L-1	\N
2273	botpt_syst_status_quantity_string_1	botpt_syst_status	\N	Syst Status	1	\N
2274	massp_rga_current_quantity_int16_A	massp_rga_current	\N	RGA current	A	\N
2275	massp_turbo_current_quantity_int16_A	massp_turbo_current	\N	Turbo Pump current	A	\N
2276	massp_heater_current_quantity_int16_A	massp_heater_current	\N	Heaters current	A	\N
2277	massp_roughing_current_quantity_int16_A	massp_roughing_current	\N	Roughing pump combined current	A	\N
2278	massp_fan_current_quantity_int16_A	massp_fan_current	\N	Fans combined current	A	\N
2279	massp_sbe_current_quantity_int16_A	massp_sbe_current	\N	CTD SBE pump current	A	\N
2280	massp_converter_24v_main_quantity_int16_1	massp_converter_24v_main	\N	24V main DC/DC converter	1	\N
2281	massp_converter_12v_main_quantity_int16_1	massp_converter_12v_main	\N	12V main DC/DC converter	1	\N
2282	massp_converter_24v_sec_quantity_int16_1	massp_converter_24v_sec	\N	24V secondary DC/DC converter	1	\N
2283	massp_converter_12v_sec_quantity_int16_1	massp_converter_12v_sec	\N	12V secondary DC/DC converter	1	\N
2284	massp_valve_current_quantity_int16_A	massp_valve_current	\N	Water sample routing module current	A	\N
2285	massp_pressure_p1_quantity_int16_kPa	massp_pressure_p1	\N	Pressure from sensor P1	kPa	\N
2286	massp_pressure_p2_quantity_int16_kPa	massp_pressure_p2	\N	Pressure from sensor P2	kPa	\N
2287	massp_pressure_p3_quantity_int16_kPa	massp_pressure_p3	\N	Pressure from sensor P3	kPa	\N
2288	massp_pressure_p4_quantity_int16_kPa	massp_pressure_p4	\N	Pressure from sensor P4	kPa	\N
2289	massp_housing_pressure_quantity_int16_kPa	massp_housing_pressure	\N	Pressure in the housing	kPa	\N
2290	massp_housing_humidity_quantity_int16_%	massp_housing_humidity	\N	Humidity in the housing	%	\N
2291	massp_temp_main_control_quantity_int16_degrees_C	massp_temp_main_control	\N	Temperature of the main control board	degrees C	\N
2292	massp_temp_main_rough_quantity_int16_degrees_C	massp_temp_main_rough	\N	Temperature of the main roughing pump	degrees C	\N
2293	massp_temp_sec_rough_quantity_int16_degrees_C	massp_temp_sec_rough	\N	Temperature of the secondary roughing pump	degrees C	\N
2294	massp_temp_main_24v_quantity_int16_degrees_C	massp_temp_main_24v	\N	Temperature of the main 24V DC/DC converter	degrees C	\N
2295	massp_temp_sec_24v_quantity_int16_degrees_C	massp_temp_sec_24v	\N	Temperature of the secondary 24V DC/DC converter	degrees C	\N
2296	massp_temp_analyzer_quantity_int16_degrees_C	massp_temp_analyzer	\N	Temperature of the analyzer	degrees C	\N
2297	massp_temp_nafion_quantity_int16_degrees_C	massp_temp_nafion	\N	Temperature of the nafion drier thermal insulation	degrees C	\N
2298	massp_temp_ion_quantity_int16_degrees_C	massp_temp_ion	\N	Temperature of the ionisation chamber	degrees C	\N
2299	massp_ph_meter_value_quantity_int16_1	massp_ph_meter_value	\N	pH meter value	1	\N
2300	massp_inlet_temp_value_quantity_int16_degrees_C	massp_inlet_temp_value	\N	external temperature at the inlet	degrees C	\N
2301	massp_ph_meter_status_quantity_int16_1	massp_ph_meter_status	\N	status of the pH analog signal	1	\N
2302	massp_inlet_temp_status_quantity_int16_1	massp_inlet_temp_status	\N	status of the external temperature microLAN	1	\N
2303	massp_power_relay_turbo_quantity_int8_1	massp_power_relay_turbo	\N	Turbo pump power relay status	1	\N
2304	massp_power_relay_rga_quantity_int8_1	massp_power_relay_rga	\N	RGA power relay status	1	\N
2305	massp_power_relay_main_rough_quantity_int8_1	massp_power_relay_main_rough	\N	Main roughing ﻿pump power relay status	1	\N
2306	massp_power_relay_sec_rough_quantity_int8_1	massp_power_relay_sec_rough	\N	Secondary roughing pump power relay status	1	\N
2307	massp_power_relay_fan1_quantity_int8_1	massp_power_relay_fan1	\N	Fan1 power relay status	1	\N
2308	massp_power_relay_fan2_quantity_int8_1	massp_power_relay_fan2	\N	Fan2 power relay status	1	\N
2309	massp_power_relay_fan3_quantity_int8_1	massp_power_relay_fan3	\N	Fan3 power relay status	1	\N
2310	massp_power_relay_fan4_quantity_int8_1	massp_power_relay_fan4	\N	Fan4 power relay status	1	\N
2311	massp_power_relay_aux2_quantity_int8_1	massp_power_relay_aux2	\N	AUX2 solenoid power relay status	1	\N
2312	massp_power_relay_ph_quantity_int8_1	massp_power_relay_ph	\N	pH meter power relay status	1	\N
2313	massp_power_relay_pump_quantity_int8_1	massp_power_relay_pump	\N	CTD SBE external water pump power relay status	1	\N
2314	massp_power_relay_heaters_quantity_int8_1	massp_power_relay_heaters	\N	Heaters power relay status	1	\N
2315	massp_power_relay_aux1_quantity_int8_1	massp_power_relay_aux1	\N	AUX1 solenoid power relay status	1	\N
2316	massp_sample_valve1_quantity_int8_1	massp_sample_valve1	\N	Sampling routing valve 1 status	1	\N
2317	massp_sample_valve2_quantity_int8_1	massp_sample_valve2	\N	Sampling routing valve 2 status	1	\N
2318	massp_sample_valve3_quantity_int8_1	massp_sample_valve3	\N	Sampling routing valve 3 status	1	\N
2319	massp_sample_valve4_quantity_int8_1	massp_sample_valve4	\N	Sampling routing valve 4 status	1	\N
2320	massp_ground_relay_status_quantity_int8_1	massp_ground_relay_status	\N	Status of the ground relay of all external valves	1	\N
2321	massp_external_valve1_status_quantity_int8_1	massp_external_valve1_status	\N	Status of the +24V relay for external valve 1	1	\N
2322	massp_external_valve2_status_quantity_int8_1	massp_external_valve2_status	\N	Status of the +24V relay for external valve 2	1	\N
2323	massp_external_valve3_status_quantity_int8_1	massp_external_valve3_status	\N	Status of the +24V relay for external valve 3	1	\N
2324	massp_external_valve4_status_quantity_int8_1	massp_external_valve4_status	\N	Status of the +24V relay for external valve 4	1	\N
2325	massp_cal_bag1_minutes_quantity_int16_minutes	massp_cal_bag1_minutes	\N	Total time calibration bag 1 has been used	minutes	\N
2326	massp_cal_bag2_minutes_quantity_int16_minutes	massp_cal_bag2_minutes	\N	Total time calibration bag 2 has been used	minutes	\N
2327	massp_cal_bag3_minutes_quantity_int16_minutes	massp_cal_bag3_minutes	\N	Total time calibration bag 3 has been used	minutes	\N
2328	massp_nafion_heater_status_quantity_int8_1	massp_nafion_heater_status	\N	Nafion heater settings	1	\N
2329	massp_nafion_heater1_power_quantity_int8_1	massp_nafion_heater1_power	\N	Nafion heater1 power setting	1	\N
2330	massp_nafion_heater2_power_quantity_int8_1	massp_nafion_heater2_power	\N	Nafion heater2 power setting	1	\N
2331	massp_nafion_core_temp_quantity_int8_degress_C	massp_nafion_core_temp	\N	Nafion core temperature	degress C	\N
2332	massp_nafion_elapsed_time_quantity_int16_seconds	massp_nafion_elapsed_time	\N	Nafion regeneration time elapsed	seconds	\N
2333	massp_ion_chamber_heater_status_quantity_int8_1	massp_ion_chamber_heater_status	\N	Ion chamber heater settings	1	\N
2334	massp_ion_chamber_heater1_status_quantity_int8_1	massp_ion_chamber_heater1_status	\N	Ion chamber heater1 status	1	\N
2335	massp_ion_chamber_heater2_status_quantity_int8_1	massp_ion_chamber_heater2_status	\N	Ion chamber heater2 status	1	\N
2336	massp_turbo_drive_current_quantity_int16_cA	massp_turbo_drive_current	\N	Current used by turbopump motor	cA	\N
2337	massp_turbo_drive_voltage_quantity_int16_cV	massp_turbo_drive_voltage	\N	Voltage at turbopump motor	cV	\N
2338	massp_turbo_bearing_temperature_quantity_int16_degrees_C	massp_turbo_bearing_temperature	\N	Temperature of turbopump bearing	degrees C	\N
2339	massp_turbo_motor_temperature_quantity_int16_degrees_C	massp_turbo_motor_temperature	\N	Temperature of turbopump bearing	degrees C	\N
2340	massp_turbo_rotation_speed_quantity_int16_rpm	massp_turbo_rotation_speed	\N	Rotational speed of the turbopump	rpm	\N
2341	massp_rga_device_id_quantity_string_1	massp_rga_device_id	\N	RGA ID String	1	\N
2342	massp_rga_electron_energy_quantity_int8_eV	massp_rga_electron_energy	\N	Electron Energy	eV	\N
2343	massp_rga_ion_energy_quantity_int8_1	massp_rga_ion_energy	\N	Ion Energy	1	\N
2344	massp_rga_focus_voltage_quantity_int16_V	massp_rga_focus_voltage	\N	Focus Plate Voltage	V	\N
2345	massp_rga_filament_emission_set_quantity_float32_mA	massp_rga_filament_emission_set	\N	Electron Emission Current	mA	\N
2346	massp_rga_filament_emission_actual_quantity_float32_mA	massp_rga_filament_emission_actual	\N	Actual Electron Emission Current	mA	\N
2347	massp_rga_high_voltage_cdem_quantity_int16_V	massp_rga_high_voltage_cdem	\N	High Voltage CDEM	V	\N
2348	massp_rga_noise_floor_quantity_int8_1	massp_rga_noise_floor	\N	Noise Floor	1	\N
2349	massp_rga_error_status_quantity_int8_1	massp_rga_error_status	\N	Status Byte	1	\N
2350	massp_rga_steps_per_amu_quantity_int8_count	massp_rga_steps_per_amu	\N	Steps per AMU	count	\N
2351	massp_rga_initial_mass_quantity_int16_amu	massp_rga_initial_mass	\N	Initial Mass	amu	\N
2352	massp_rga_final_mass_quantity_int16_amu	massp_rga_final_mass	\N	Final Mass	amu	\N
2353	massp_rga_readings_per_scan_quantity_int16_count	massp_rga_readings_per_scan	\N	Analog Scan Points	count	\N
2354	massp_scan_data_array_quantity_int32_10e_16_Amps	massp_scan_data	\N	Array of measurements representing one scan of the RGA	10e-16 Amps	\N
2355	hpies_data_valid_boolean_uint8_1	hpies_data_valid	\N	Data Valid	1	\N
2356	hpies_ver_quantity_uint8_1	hpies_ver	\N	Version Number	1	\N
2357	hpies_type_quantity_string_1	hpies_type	\N	Data Type	1	\N
2358	hpies_dest_quantity_string_1	hpies_dest	\N	Pinched Tube	1	\N
2359	hpies_ibeg_quantity_uint16_1	hpies_ibeg	\N	Index Begin	1	\N
2360	hpies_iend_quantity_uint16_1	hpies_iend	\N	Index End	1	\N
2361	hpies_hcno_quantity_uint16_1	hpies_hcno	\N	Half Cycle Number	1	\N
2362	hpies_secs_quantity_uint64_seconds	hpies_secs	\N	Time	seconds	\N
2363	hpies_tics_quantity_uint16_1	hpies_tics	\N	Tics	1	\N
2364	hpies_navg_mot_quantity_uint8_1	hpies_navg_mot	\N	Motor Samples Sum	1	\N
2365	hpies_navg_ef_quantity_uint8_1	hpies_navg_ef	\N	EF ADC Samples Sum	1	\N
2366	hpies_navg_cal_quantity_uint8_1	hpies_navg_cal	\N	Calibration ADC Samples Sum	1	\N
2367	hpies_stm_timestamp_quantity_uint64_seconds	hpies_stm_timestamp	\N	STM Timestamp	seconds	\N
2368	hpies_eindex_quantity_uint16_1	hpies_eindex	\N	Electric Field Sample Index	1	\N
2369	hpies_e1c_quantity_uint16_counts	hpies_e1c	\N	E1c Channel Counts	counts	\N
2370	hpies_e1a_quantity_uint16_counts	hpies_e1a	\N	E1a Channel Counts	counts	\N
2371	hpies_e1b_quantity_uint16_counts	hpies_e1b	\N	E1b Channel Counts	counts	\N
2372	hpies_e2c_quantity_uint16_counts	hpies_e2c	\N	E2c Channel Counts	counts	\N
2373	hpies_e2a_quantity_uint16_counts	hpies_e2a	\N	E2a Channel Counts	counts	\N
2374	hpies_e2b_quantity_uint16_counts	hpies_e2b	\N	E2b Channel Counts	counts	\N
2375	hpies_mindex_quantity_uint8_1	hpies_mindex	\N	Motor Sample Index	1	\N
2376	hpies_motor_current_quantity_uint16_counts	hpies_motor_current	\N	Motor Current Counts	counts	\N
2377	hpies_cindex_quantity_uint8_1	hpies_cindex	\N	Calibration Sample Index	1	\N
2378	hpies_c1c_quantity_uint16_counts	hpies_c1c	\N	E1c Channel Counts	counts	\N
2379	hpies_c1a_quantity_uint16_counts	hpies_c1a	\N	E1a Channel Counts	counts	\N
2380	hpies_c1b_quantity_uint16_counts	hpies_c1b	\N	E1b Channel Counts	counts	\N
2381	hpies_c2c_quantity_uint16_counts	hpies_c2c	\N	E2c Channel Counts	counts	\N
2382	hpies_c2a_quantity_uint16_counts	hpies_c2a	\N	E2a Channel Counts	counts	\N
2383	hpies_c2b_quantity_uint16_counts	hpies_c2b	\N	E2b Channel Counts	counts	\N
2384	hpies_hcno_quantity_uint8_1	hpies_hcno	\N	Half Cycle Number	1	\N
2385	hpies_hcno_last_cal_quantity_uint8_1	hpies_hcno_last_cal	\N	Half Cycle Number Last Calibration	1	\N
2386	hpies_hcno_last_comp_quantity_uint8_1	hpies_hcno_last_comp	\N	Half Cycle Number Last Compass Value	1	\N
2387	hpies_ofile_quantity_string_1	hpies_ofile	\N	Current Output Filename	1	\N
2388	hpies_ifok_quantity_string_1	hpies_ifok	\N	File Write Status	1	\N
2389	hpies_compass_fwrite_attempted_quantity_uint8_1	hpies_compass_fwrite_attempted	\N	Compass Records	1	\N
2390	hpies_compass_fwrite_ofp_null_quantity_uint8_1	hpies_compass_fwrite_ofp_null	\N	Compass Write Attempts OFile Corrupt	1	\N
2391	hpies_mot_pwr_count_quantity_uint8_1	hpies_mot_pwr_count	\N	Motor Power Count	1	\N
2392	hpies_start_motor_count_quantity_uint32_1	hpies_start_motor_count	\N	Start Motor Count	1	\N
2393	hpies_compass_port_open_errs_quantity_uint8_1	hpies_compass_port_open_errs	\N	Compass Port Open Failures	1	\N
2394	hpies_compass_port_nerr_quantity_uint8_1	hpies_compass_port_nerr	\N	Compass Port Read Decode Errors	1	\N
2395	hpies_tuport_compass_null_count_quantity_uint8_1	hpies_tuport_compass_null_count	\N	Compass Port Closed Count	1	\N
2396	hpies_irq2_count_quantity_uint8_1	hpies_irq2_count	\N	IRQ2 Interrupt Count	1	\N
2397	hpies_spurious_count_quantity_uint8_1	hpies_spurious_count	\N	Spurious Count	1	\N
2398	hpies_spsr_unknown_count_quantity_uint8_1	hpies_spsr_unknown_count	\N	SPSR Unknown Count	1	\N
2399	hpies_pitperiod_zero_count_quantity_uint8_1	hpies_pitperiod_zero_count	\N	PITperiod Zero Count	1	\N
2400	hpies_adc_raw_overflow_count_quantity_uint8_1	hpies_adc_raw_overflow_count	\N	ADC Raw Overflow Count	1	\N
2401	hpies_max7317_add_queue_errs_quantity_uint8_1	hpies_max7317_add_queue_errs	\N	Max7317 Add Queue Errors	1	\N
2402	hpies_wsrun_rtc_pinch_end_nerr_quantity_uint8_1	hpies_wsrun_rtc_pinch_end_nerr	\N	Water Switch Pinch Timing Errors	1	\N
2403	hpies_ies_timestamp_quantity_uint64_seconds	hpies_ies_timestamp	\N	IES Timestamp	seconds	\N
2404	hpies_n_travel_times_quantity_uint8_1	hpies_n_travel_times	\N	Number of Travel Times	1	\N
2405	hpies_travel_time1_quantity_uint32_10_μseconds	hpies_travel_time1	\N	Travel Time1, 10 μseconds	10 μseconds	\N
2406	hpies_travel_time2_quantity_uint32_10_μseconds	hpies_travel_time2	\N	Travel Time2, 10 μseconds	10 μseconds	\N
2407	hpies_travel_time3_quantity_uint32_10_μseconds	hpies_travel_time3	\N	Travel Time3, 10 μseconds	10 μseconds	\N
2408	hpies_travel_time4_quantity_uint32_10_μseconds	hpies_travel_time4	\N	Travel Time4, 10 μseconds	10 μseconds	\N
2409	hpies_pressure_quantity_uint32_1/1000_dbar	hpies_pressure	\N	Pressure, 1/1000 dbar	1/1000 dbar	\N
2410	hpies_temperature_quantity_uint32_millidegrees_Celsius	hpies_temperature	\N	Temperature, millidegrees Celsius	millidegrees Celsius	\N
2411	hpies_bliley_temperature_quantity_uint32_millidegrees_Celsius	hpies_bliley_temperature	\N	Bliley Temperature, millidegrees Celsius	millidegrees Celsius	\N
2412	hpies_bliley_frequency_quantity_float32_Hz	hpies_bliley_frequency	\N	Bliley Frequency, Hz	Hz	\N
2413	hpies_data_validity_boolean_uint8_1	hpies_data_validity	\N	Data Validity	1	\N
2414	hpies_status_travel_times_array_quantity_uint32_10_μseconds	hpies_status_travel_times	\N	Status Travel Times	10 μseconds	\N
2415	hpies_status_pressures_array_quantity_uint16_0.001_dbars	hpies_status_pressures	\N	Status Pressures	0.001 dbars	\N
2416	hpies_status_temperatures_array_quantity_uint16_0.001º_Celsius	hpies_status_temperatures	\N	Status Temperatures	0.001º Celsius	\N
2417	hpies_status_pressure_frequencies_array_quantity_uint32_mHz	hpies_status_pressure_frequencies	\N	Status Pressure Frequencies	mHz	\N
2418	hpies_status_temperature_frequencies_array_quantity_uint32_mHz	hpies_status_temperature_frequencies	\N	Status Temperature Frequencies	mHz	\N
2419	hpies_backup_battery_voltage_quantity_float32_V	hpies_backup_battery_voltage	\N	Backup Battery Voltage	V	\N
2420	hpies_release_drain_quantity_float32_mAmp	hpies_release_drain	\N	Release Battery Drain	mAmp	\N
2421	hpies_system_drain_quantity_float32_mAmp	hpies_system_drain	\N	System Battery Drain	mAmp	\N
2422	hpies_release_battery_voltage_quantity_float32_V	hpies_release_battery_voltage	\N	Release Battery Voltage	V	\N
2423	hpies_system_battery_voltage_quantity_float32_V	hpies_system_battery_voltage	\N	System Battery Voltage	V	\N
2424	hpies_release_system_voltage_quantity_float32_V	hpies_release_system_voltage	\N	Release System Voltage	V	\N
2425	hpies_internal_temperature_quantity_float32_ºC	hpies_internal_temperature	\N	Internal Temperature	ºC	\N
2426	hpies_average_travel_time_quantity_float32_10_μseconds	hpies_average_travel_time	\N	Average Travel Time	10 μseconds	\N
2427	hpies_average_pressure_quantity_uint16_0.001_dbar	hpies_average_pressure	\N	Average Pressure	0.001 dbar	\N
2428	hpies_average_temperature_quantity_uint16_0.001º_Celsius	hpies_average_temperature	\N	Average Temperature	0.001º Celsius	\N
2429	hpies_last_pressure_quantity_float32_Hz	hpies_last_pressure	\N	Last Pressure	Hz	\N
2430	hpies_last_temperature_quantity_float32_Hz	hpies_last_temperature	\N	Last Temperature	Hz	\N
2431	hpies_ies_clock_error_quantity_float32_Hz	hpies_ies_clock_error	\N	IES Clock Error	Hz	\N
2432	hpies_rsn_timestamp_quantity_uint64_seconds	hpies_rsn_timestamp	\N	RSN Timestamp	seconds	\N
2433	dcl_controller_timestamp_quantity_string_1	dcl_controller_timestamp	\N	DCL controller timestamp	1	\N
2434	pressure_depth_quantity_float32_dbar	pressure_depth	\N	Pressure from Depth parameter, dbar	dbar	\N
2435	velpt_pressure_quantity_float32_dbar	velpt_pressure	\N	VELPT Pressure, dbar	dbar	\N
2436	velocity_beam1_m_s_quantity_float32_m_s_1	velocity_beam1_m_s	\N	velocity beam1 or X or East coordinates (m/s)	m s-1	\N
2437	velocity_beam2_m_s_quantity_float32_m_s_1	velocity_beam2_m_s	\N	velocity beam2 or Y or North coordinates (m/s)	m s-1	\N
2438	velocity_beam3_m_s_quantity_float32_m_s_1	velocity_beam3_m_s	\N	velocity beam3 or Z or Up coordinates (m/s)	m s-1	\N
2439	on_seconds_quantity_float32_s	on_seconds	\N	Powered On Time, s	s	\N
2440	year_quantity_uint16_year	year	\N	Year	year	\N
2441	day_of_year_quantity_uint16_1	day_of_year	\N	Day of year number	1	\N
2442	ctd_time_uint32_quantity_uint32_seconds_since_1970_01_01	ctd_time_uint32	\N	Time, UTC	seconds since 1970-01-01	\N
2443	ctd_psu_quantity_float32_1	ctd_psu	\N	Practical Salinity	1	\N
2444	ctd_temp_quantity_float32_deg_C	ctd_temp	\N	Temperature	deg_C	\N
2445	ctd_dbar_quantity_float32_dbar	ctd_dbar	\N	Pressure (Depth), dbar	dbar	\N
2446	suspect_timestamp_boolean_int8_1	suspect_timestamp	\N	Suspect Timestamp, Flag	1	\N
2447	trhph_thermistor_temp_function_float32_deg_C	trhph_thermistor_temp	\N	Thermistor Reference Temperature, deg_C	deg_C	\N
2448	thsph_temp_th_function_float32_deg_C	thsph_temp_th	\N	Final Temperature at Position H	deg_C	\N
2449	thsph_temp_tl_function_float32_deg_C	thsph_temp_tl	\N	Final Temperature at Position L	deg_C	\N
2450	thsph_temp_tch_function_float32_deg_C	thsph_temp_tch	\N	Intermediate Thermocouple Temperature at Position H	deg_C	\N
2451	thsph_temp_tcl_function_float32_deg_C	thsph_temp_tcl	\N	Intermediate Thermocouple Temperature at Position L	deg_C	\N
2452	thsph_temp_int_function_float32_deg_C	thsph_temp_int	\N	Internal Board Thermistor Temperature	deg_C	\N
2453	thsph_temp_ref_function_float32_deg_C	thsph_temp_ref	\N	Reference Thermistor Temperature	deg_C	\N
2454	thsph_ph_function_float32_1	thsph_ph	\N	Vent Fluid pH	1	\N
2455	thsph_ph_acl_function_float32_1	thsph_ph_acl	\N	Vent Fluid pH AgCl	1	\N
2456	thsph_ph_noref_function_float32_1	thsph_ph_noref	\N	Vent Fluid pH No Reference	1	\N
2457	thsph_ph_noref_acl_function_float32_1	thsph_ph_noref_acl	\N	Vent Fluid pH No Reference AgCl	1	\N
2458	thsph_sulfide_function_float32_mmol/kg	thsph_sulfide	\N	Hydrogen Sulfide Concentration	mmol/kg	\N
2459	thsph_hydrogen_function_float32_mmol/kg	thsph_hydrogen	\N	Hydrogen Concentration	mmol/kg	\N
2460	phsen_battery_volts_function_float32_V	phsen_battery_volts	\N	Battery Voltage (from counts to Volts)	V	\N
2461	parad_telbaud_quantity_int32_bps	parad_telbaud	\N	Telemetry Baud Rate	bps	\N
2462	parad_maxrate_quantity_float32_Hz	parad_maxrate	\N	Max Sampling Rate	Hz	\N
2463	parad_firmware_quantity_string_1	parad_firmware	\N	Instrument Firmware	1	\N
2464	parad_type_quantity_string_1	parad_type	\N	Instrument Type	1	\N
2465	battery_number_uint8_quantity_uint8_1	battery_number_uint8	\N	Battery number	1	\N
2466	battery_voltage_flt32_quantity_float32_V	battery_voltage_flt32	\N	Battery Voltage, volts	V	\N
2467	gps_adjustment_quantity_int32_1	gps_adjustment	\N	GPS Adjustment Value	1	\N
2468	velocity_flt32_quantity_float32_m_s_1	velocity_flt32	\N	Velocity, m/s	m s-1	\N
2469	spkir_downwelling_vector_function_float32_uW/cm_2/nm	spkir_downwelling_vector	\N	Downwelling Spectral Irradiance, uW/cm^2/nm: 1 = 412nm, 2 = 443nm, 3 = 490nm, 4 = 510nm, 5 = 555nm, 6 = 620nm, 7 = 683nm.	uW/cm^2/nm	\N
2470	encoder_counts_quantity_int32_counts	encoder_counts	\N	Encoder counts	counts	\N
2471	current_flt32_quantity_float32_A	current_flt32	\N	Winch Current, amp	A	\N
2472	winch_velocity_quantity_float32_counts_s_1	winch_velocity	\N	Winch Velocity, counts/s	counts s-1	\N
2473	voltage_flt32_quantity_float32_V	voltage_flt32	\N	Winch Voltage, volts	V	\N
2474	time_counts_quantity_int32_counts	time_counts	\N	Time counts	counts	\N
2475	discharge_counts_quantity_int32_counts	discharge_counts	\N	Discharge counts	counts	\N
2476	rope_on_drum_quantity_float32_m	rope_on_drum	\N	Rope on drum, meters	m	\N
2477	vadcp_eastward_seawater_velocity_function_float32_m_s_1	vadcp_eastward_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
2478	vadcp_northward_seawater_velocity_function_float32_m_s_1	vadcp_northward_seawater_velocity	\N	Northward Sea Water Velocity, m s-1	m s-1	\N
2479	vadcp_upward_seawater_velocity_est_function_float32_m_s_1	vadcp_upward_seawater_velocity_est	\N	Upward Sea Water Velocity Estimated, m s-1	m s-1	\N
2480	vadcp_upward_seawater_velocity_tru_function_float32_m_s_1	vadcp_upward_seawater_velocity_tru	\N	Upward Sea Water Velocity True, m s-1	m s-1	\N
2481	vadcp_beam_error_function_float32_m_s_1	vadcp_beam_error	\N	Error Velocity, m s-1	m s-1	\N
2482	hc_data_array_	hc_data	\N	\N	\N	\N
2483	camds_pan_position_quantity_int8_degrees	camds_pan_position	\N	Pan Position	degrees	\N
2484	camds_tilt_position_quantity_int8_degrees	camds_tilt_position	\N	Tilt Position	degrees	\N
2485	camds_focus_position_quantity_int8_1	camds_focus_position	\N	Focus Position	1	\N
2486	camds_zoom_position_quantity_int8_1	camds_zoom_position	\N	Zoom Position	1	\N
2487	camds_iris_position_quantity_int8_1	camds_iris_position	\N	Iris Position	1	\N
2488	camds_gain_quantity_int8_1	camds_gain	\N	Gain	1	\N
2489	camds_resolution_quantity_int8_1	camds_resolution	\N	Resolution	1	\N
2490	camds_brightness_quantity_int8_1	camds_brightness	\N	Brightness	1	\N
2491	camds_temp_quantity_int8_DegreesC	camds_temp	\N	Temperature	DegreesC	\N
2492	camds_humidity_quantity_int8_%	camds_humidity	\N	Humidity	%	\N
2493	camds_error_quantity_int8_1	camds_error	\N	Error	1	\N
2494	camds_disk_size_quantity_int16_MB	camds_disk_size	\N	Disk Size	MB	\N
2495	camds_disk_remaining_quantity_int8_%	camds_disk_remaining	\N	Disk Remaining	%	\N
2496	camds_images_remaining_quantity_int16_counts	camds_images_remaining	\N	Images Remaining	counts	\N
2497	camds_images_on_disk_quantity_int16_counts	camds_images_on_disk	\N	Images On Disk	counts	\N
2498	zplsc_connected_boolean_int8_	zplsc_connected	\N	Connected	 	\N
2499	zplsc_active_38k_mode_quantity_string_	zplsc_active_38k_mode	\N	Active 38k Mode	\N	\N
2500	zplsc_active_38k_power_quantity_float32_W	zplsc_active_38k_power	\N	Active 38k Power	W	\N
2501	zplsc_active_38k_pulse_length_quantity_float32_sec	zplsc_active_38k_pulse_length	\N	Active 38k Pulse Length	sec	\N
2502	zplsc_active_38k_sample_interval_quantity_float32_sec	zplsc_active_38k_sample_interval	\N	Active 38k Sample Interval	sec	\N
2503	zplsc_active_120k_mode_quantity_string_	zplsc_active_120k_mode	\N	Active 120k Mode	\N	\N
2504	zplsc_active_120k_power_quantity_float32_W	zplsc_active_120k_power	\N	Active 120k Power	W	\N
2505	zplsc_active_120k_pulse_length_quantity_float32_sec	zplsc_active_120k_pulse_length	\N	Active 120k Pulse Length	sec	\N
2506	zplsc_active_120k_sample_interval_quantity_float32_sec	zplsc_active_120k_sample_interval	\N	Active 120k Sample Interval	sec	\N
2507	zplsc_active_200k_mode_quantity_string_	zplsc_active_200k_mode	\N	Active 200k Mode	\N	\N
2508	zplsc_active_200k_power_quantity_float32_W	zplsc_active_200k_power	\N	Active 200k Power	W	\N
2509	zplsc_active_200k_pulse_length_quantity_float32_sec	zplsc_active_200k_pulse_length	\N	Active 200k Pulse Length	sec	\N
2510	zplsc_active_200k_sample_interval_quantity_float32_sec	zplsc_active_200k_sample_interval	\N	Active 200k Sample Interval	sec	\N
2511	zplsc_current_utc_time_quantity_string_	zplsc_current_utc_time	\N	Current UTC Time	\N	\N
2512	zplsc_executable_quantity_string_	zplsc_executable	\N	Executable	\N	\N
2513	zplsc_fs_root_quantity_string_	zplsc_fs_root	\N	FS Root	\N	\N
2514	zplsc_next_scheduled_interval_quantity_string_	zplsc_next_scheduled_interval	\N	Next Scheduled Interval	\N	\N
2515	zplsc_host_quantity_string_	zplsc_host	\N	Host	\N	\N
2516	zplsc_pid_quantity_string_	zplsc_pid	\N	PID	\N	\N
2517	zplsc_port_quantity_int16_	zplsc_port	\N	Port	\N	\N
2518	zplsc_current_raw_filename_quantity_string_	zplsc_current_raw_filename	\N	Current Raw Filename	\N	\N
2519	zplsc_current_raw_filesize_quantity_int32_bytes	zplsc_current_raw_filesize	\N	Current Raw Filesize	bytes	\N
2520	zplsc_file_path_quantity_string_	zplsc_file_path	\N	File Path	\N	\N
2521	zplsc_file_prefix_quantity_string_	zplsc_file_prefix	\N	File Prefix	\N	\N
2522	zplsc_max_file_size_quantity_int32_	zplsc_max_file_size	\N	Max File Size	\N	\N
2523	zplsc_sample_range_quantity_float32_	zplsc_sample_range	\N	Sample Range	\N	\N
2524	zplsc_save_bottom_boolean_int8_	zplsc_save_bottom	\N	Save Bottom	\N	\N
2525	zplsc_save_index_boolean_int8_	zplsc_save_index	\N	Save Index	\N	\N
2526	zplsc_save_raw_boolean_int8_	zplsc_save_raw	\N	Save Raw	\N	\N
2527	zplsc_scheduled_intervals_remaining_quantity_int16_	zplsc_scheduled_intervals_remaining	\N	Scheduled Intervals Remaining	\N	\N
2528	zplsc_gpts_enabled_boolean_int8_	zplsc_gpts_enabled	\N	GPTS Enabled	\N	\N
2529	zplsc_schedule_filename_quantity_string_	zplsc_schedule_filename	\N	Schedule Filename	 	\N
2530	raw_binary_	raw	\N	Live Video	\N	\N
2531	startup_time_string_quantity_string_1	startup_time_string	\N	Startup Time, UTC	1	\N
2532	ph_light_measurements_array_quantity_int16_counts	ph_light_measurements	\N	Array of PH Light Measurements, counts	counts	\N
2533	dcl_controller_start_timestamp_quantity_string_1	dcl_controller_start_timestamp	\N	DCL Controller Start Timestamp	1	\N
2534	dcl_controller_end_timestamp_quantity_string_1	dcl_controller_end_timestamp	\N	DCL Controller End Timestamp	1	\N
2535	operating_current_quantity_float32_mA	operating_current	\N	Operating Current, mA	mA	\N
2536	blank_light_measurements_array_quantity_int16_counts	blank_light_measurements	\N	Blank Light Measurements, counts	counts	\N
2537	temperature01_quantity_float32_deg_C	temperature01	\N	Temperature01 in Spatial Grid, deg C	deg_C	\N
2538	temperature02_quantity_float32_deg_C	temperature02	\N	Temperature02 in Spatial Grid, deg C	deg_C	\N
2539	temperature03_quantity_float32_deg_C	temperature03	\N	Temperature03 in Spatial Grid, deg C	deg_C	\N
2540	temperature04_quantity_float32_deg_C	temperature04	\N	Temperature04 in Spatial Grid, deg C	deg_C	\N
2541	temperature05_quantity_float32_deg_C	temperature05	\N	Temperature05 in Spatial Grid, deg C	deg_C	\N
2542	temperature06_quantity_float32_deg_C	temperature06	\N	Temperature06 in Spatial Grid, deg C	deg_C	\N
2543	temperature07_quantity_float32_deg_C	temperature07	\N	Temperature07 in Spatial Grid, deg C	deg_C	\N
2544	temperature08_quantity_float32_deg_C	temperature08	\N	Temperature08 in Spatial Grid, deg C	deg_C	\N
2545	temperature09_quantity_float32_deg_C	temperature09	\N	Temperature09 in Spatial Grid, deg C	deg_C	\N
2546	temperature10_quantity_float32_deg_C	temperature10	\N	Temperature10 in Spatial Grid, deg C	deg_C	\N
2547	temperature11_quantity_float32_deg_C	temperature11	\N	Temperature11 in Spatial Grid, deg C	deg_C	\N
2548	temperature12_quantity_float32_deg_C	temperature12	\N	Temperature12 in Spatial Grid, deg C	deg_C	\N
2549	temperature13_quantity_float32_deg_C	temperature13	\N	Temperature13 in Spatial Grid, deg C	deg_C	\N
2550	temperature14_quantity_float32_deg_C	temperature14	\N	Temperature14 in Spatial Grid, deg C	deg_C	\N
2551	temperature15_quantity_float32_deg_C	temperature15	\N	Temperature15 in Spatial Grid, deg C	deg_C	\N
2552	temperature16_quantity_float32_deg_C	temperature16	\N	Temperature16 in Spatial Grid, deg C	deg_C	\N
2553	temperature17_quantity_float32_deg_C	temperature17	\N	Temperature17 in Spatial Grid, deg C	deg_C	\N
2554	temperature18_quantity_float32_deg_C	temperature18	\N	Temperature18 in Spatial Grid, deg C	deg_C	\N
2555	temperature19_quantity_float32_deg_C	temperature19	\N	Temperature19 in Spatial Grid, deg C	deg_C	\N
2556	temperature20_quantity_float32_deg_C	temperature20	\N	Temperature20 in Spatial Grid, deg C	deg_C	\N
2557	temperature21_quantity_float32_deg_C	temperature21	\N	Temperature21 in Spatial Grid, deg C	deg_C	\N
2558	temperature22_quantity_float32_deg_C	temperature22	\N	Temperature22 in Spatial Grid, deg C	deg_C	\N
2559	temperature23_quantity_float32_deg_C	temperature23	\N	Temperature23 in Spatial Grid, deg C	deg_C	\N
2560	temperature24_quantity_float32_deg_C	temperature24	\N	Temperature24 in Spatial Grid, deg C	deg_C	\N
2561	adcps_jln_echo_intensity_beam1_function_float32_dB	adcps_jln_echo_intensity_beam1	\N	Beam #1 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2562	adcps_jln_echo_intensity_beam2_function_float32_dB	adcps_jln_echo_intensity_beam2	\N	Beam #2 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2563	adcps_jln_echo_intensity_beam3_function_float32_dB	adcps_jln_echo_intensity_beam3	\N	Beam #3 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2564	adcps_jln_echo_intensity_beam4_function_float32_dB	adcps_jln_echo_intensity_beam4	\N	Beam #4 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2565	adcpa_m_upward_seawater_velocity_function_float32_m_s_1	adcpa_m_upward_seawater_velocity	\N	Upward Sea Water Velocity, m s-1	m s-1	\N
2566	adcpa_m_error_velocity_function_float32_m_s_1	adcpa_m_error_velocity	\N	Error Velocity, m s-1	m s-1	\N
2567	adcpa_m_eastward_seawater_velocity_function_float32_m_s_1	adcpa_m_eastward_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
2568	adcpa_m_northward_seawater_velocity_function_float32_m_s_1	adcpa_m_northward_seawater_velocity	\N	Northward Sea Water Velocity, m s-1	m s-1	\N
2569	adcpa_m_echo_intensity_beam1_function_float32_dB	adcpa_m_echo_intensity_beam1	\N	Beam #1 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2570	adcpa_m_echo_intensity_beam2_function_float32_dB	adcpa_m_echo_intensity_beam2	\N	Beam #2 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2571	adcpa_m_echo_intensity_beam3_function_float32_dB	adcpa_m_echo_intensity_beam3	\N	Beam #3 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2572	adcpa_m_echo_intensity_beam4_function_float32_dB	adcpa_m_echo_intensity_beam4	\N	Beam #4 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2573	sci_seawater_density_function_float32_kg_m_3	sci_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
2574	sci_abs_oxygen_function_float32_umol_kg_1	sci_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
2575	sci_flbb_timestamp_quantity_float64_seconds_since_1970_01_01	sci_flbb_timestamp	\N	sci_flbb_timestamp, UTC	seconds since 1970-01-01	\N
2576	sci_flbb_bb_ref_quantity_float32_1	sci_flbb_bb_ref	\N	sci_flbb_bb_ref	1	\N
2577	sci_flbb_bb_sig_quantity_float32_1	sci_flbb_bb_sig	\N	sci_flbb_bb_sig	1	\N
2578	sci_flbb_chlor_ref_quantity_float32_1	sci_flbb_chlor_ref	\N	sci_flbb_chlor_ref	1	\N
2579	sci_flbb_chlor_sig_quantity_float32_1	sci_flbb_chlor_sig	\N	sci_flbb_chlor_sig	1	\N
2580	sci_flbb_therm_quantity_float32_1	sci_flbb_therm	\N	sci_flbb_therm	1	\N
2581	flord_m_bback_total_function_float32_m_1	flord_m_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
2582	flord_m_scat_seawater_function_float32_m_1	flord_m_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
2583	flort_m_bback_total_function_float32_m_1	flort_m_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
2584	flort_m_scat_seawater_function_float32_m_1	flort_m_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
2585	nutnr_b_temp_sal_corrected_nitrate_function_float32_uMol_L_1	nutnr_b_temp_sal_corrected_nitrate	\N	Temperature Salinity Corrected Nitrate	uMol L-1	\N
2586	flort_dj_dcl_bback_total_function_float32_m_1	flort_dj_dcl_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
2587	flort_kn_bback_total_function_float32_m_1	flort_kn_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
2588	scat_seawater_function_float32_m_1	scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
2589	dcl_controller_starting_timestamp_quantity_string_1	dcl_controller_starting_timestamp	\N	DCL controller starting timestamp	1	\N
2590	spkir_abj_cspp_downwelling_vector_function_float32_uW/cm_2/nm	spkir_abj_cspp_downwelling_vector	\N	Downwelling Spectral Irradiance, uW/cm^2/nm: 1 = 412nm, 2 = 443nm, 3 = 490nm, 4 = 510nm, 5 = 555nm, 6 = 620nm, 7 = 683nm.	uW/cm^2/nm	\N
2591	phsen_abcdef_ph_seawater_function_float32_1	phsen_abcdef_ph_seawater	\N	pH of Seawater	1	\N
2592	scaled_tidal_seafloor_pressure_function_float32_dbar	scaled_tidal_seafloor_pressure	\N	Seafloor Pressure from tidal record, dbar	dbar	\N
2593	corrected_echo_intensity_beam1_function_float32_dB	corrected_echo_intensity_beam1	\N	Beam #1 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2594	corrected_echo_intensity_beam2_function_float32_dB	corrected_echo_intensity_beam2	\N	Beam #2 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2595	corrected_echo_intensity_beam3_function_float32_dB	corrected_echo_intensity_beam3	\N	Beam #3 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2596	corrected_echo_intensity_beam4_function_float32_dB	corrected_echo_intensity_beam4	\N	Beam #4 Relative Echo Intensity (ECHOINT_L1), dB	dB	\N
2597	number_zero_crossings_quantity_int32_counts	number_zero_crossings	\N	Number of Zero Crossings, counts	counts	\N
2598	average_wave_height_quantity_float32_m	average_wave_height	\N	Average Wave Height, meters	m	\N
2599	mean_spectral_period_quantity_float32_sec	mean_spectral_period	\N	Mean Spectral Period, seconds	sec	\N
2600	max_wave_height_quantity_float32_m	max_wave_height	\N	Max Wave Height, meters	m	\N
2601	significant_wave_height_quantity_float32_m	significant_wave_height	\N	Significant Wave Height, meters	m	\N
2602	significant_period_quantity_float32_sec	significant_period	\N	Significant Period, seconds	sec	\N
2603	wave_height_10_quantity_float32_m	wave_height_10	\N	Wave Height 10, meters	m	\N
2604	wave_period_10_quantity_float32_sec	wave_period_10	\N	Wave Period 10, seconds	sec	\N
2605	mean_wave_period_quantity_float32_sec	mean_wave_period	\N	Mean Wave Period, seconds	sec	\N
2606	peak_wave_period_quantity_float32_sec	peak_wave_period	\N	Peak Wave Period, seconds	sec	\N
2607	wave_period_tp5_quantity_float32_sec	wave_period_tp5	\N	Wave Period Tp5, seconds	sec	\N
2608	wave_height_hmo_quantity_float32_m	wave_height_hmo	\N	Wave Height HMO, meters	m	\N
2609	mean_direction_quantity_float32_degrees	mean_direction	\N	Mean Direction, degrees	degrees	\N
2610	mean_spread_quantity_float32_degrees	mean_spread	\N	Mean Spread, degrees	degrees	\N
2611	number_bands_quantity_int32_1	number_bands	\N	Number Bands	1	\N
2612	initial_frequency_quantity_float32_Hz	initial_frequency	\N	Initial Frequency, Hz	Hz	\N
2613	frequency_spacing_quantity_float32_Hz	frequency_spacing	\N	Frequency Spacing, Hz	Hz	\N
2614	psd_non_directional_array_quantity_float32_m2_Hz_1	psd_non_directional	\N	PSD Non Directional, square meters per Hertz	m2 Hz-1	\N
2615	psd_mean_directional_array_quantity_float32_m2_Hz_1	psd_mean_directional	\N	PSD Mean Directional, square meters per Hertz	m2 Hz-1	\N
2616	mean_direction_array_array_quantity_float32_degrees	mean_direction_array	\N	Mean Direction Array, degrees	degrees	\N
2617	directional_spread_array_array_quantity_float32_degrees	directional_spread_array	\N	Directional Spread Array, degrees	degrees	\N
2618	number_time_samples_quantity_int32_1	number_time_samples	\N	Number Time Samples	1	\N
2619	initial_time_quantity_float32_sec	initial_time	\N	Initial Time, seconds	sec	\N
2620	time_spacing_quantity_float32_sec	time_spacing	\N	Time Spacing, seconds	sec	\N
2621	solution_found_quantity_int32 _1	solution_found	\N	Solution Found	1	\N
2622	heave_offset_array_array_quantity_float32_m	heave_offset_array	\N	Heave Offset Array, meters	m	\N
2623	north_offset_array_array_quantity_float32_m	north_offset_array	\N	North Offset Array, meters	m	\N
2624	east_offset_array_array_quantity_float32_m	east_offset_array	\N	East Offset Array, meters	m	\N
2625	number_directional_bands_quantity_int32  _1	number_directional_bands	\N	Number Directional Bands	1	\N
2626	initial_directional_frequency_quantity_float32_Hz	initial_directional_frequency	\N	Initial Directional Frequency, Hz	Hz	\N
2627	directional_frequency_spacing_quantity_float32_Hz	directional_frequency_spacing	\N	Directional Frequency Spacing, Hz	Hz	\N
2628	fourier_coefficient_2d_array_array_quantity_float32_1	fourier_coefficient_2d_array	\N	Fourier Coefficient 2D Array	1	\N
2629	pco2_co2flux_function_float32_mol_m_2_s_1	pco2_co2flux	\N	Estimated Flux of CO2 from Ocean to Atmosphere, mol m-2 s-1	mol m-2 s-1	\N
2630	pressure_range_quantity_int32_psia	pressure_range	\N	Pressure Range, psia	psia	\N
2631	instrument_timestamp_quantity_string_1	instrument_timestamp	\N	Timestamp provided by the instrument 	1	\N
2632	water_direction_array_quantity_float32_degrees	water_direction	\N	Direction (calculated from VLE, VLN corrected for EH heading)	degrees	\N
2633	water_velocity_array_quantity_float32_mm_d_1	water_velocity	\N	Velocity (calculated from VLE, VLN, VLU)	mm d-1	\N
2634	scaled_wave_burst_seafloor_pressure_function_float32_dbar	scaled_wave_burst_seafloor_pressure	\N	Seafloor Pressure from tidal record, dbar	dbar	\N
2635	optaa_dj_beam_attenuation_function_float32_m_1	optaa_dj_beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
2636	optaa_dj_optical_absorption_function_float32_m_1	optaa_dj_optical_absorption	\N	Optical Absorption, m-1	m-1	\N
2637	mode_quantity_string_1	mode	\N	Mode	1	\N
2638	spread_direction_quantity_float32_degrees	spread_direction	\N	Spread Direction, degrees	degrees	\N
2639	adcpt_acfgm_upward_seawater_velocity_function_float32_m_s_1	adcpt_acfgm_upward_seawater_velocity	\N	Upward Sea Water Velocity, m s-1	m s-1	\N
2640	adcpt_acfgm_error_velocity_function_float32_m_s_1	adcpt_acfgm_error_velocity	\N	Error Velocity, m s-1	m s-1	\N
2641	adcpt_acfgm_eastward_seawater_velocity_function_float32_m_s_1	adcpt_acfgm_eastward_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
2642	adcpt_acfgm_northward_seawater_velocity_function_float32_m_s_1	adcpt_acfgm_northward_seawater_velocity	\N	Northward Sea Water Velocity, m s-1	m s-1	\N
2643	ctdbp_seawater_temperature_function_float32_deg_C	ctdbp_seawater_temperature	\N	Sea Water Temperature, deg_C	deg_C	\N
2644	ctdbp_seawater_pressure_function_float32_dbar	ctdbp_seawater_pressure	\N	Sea Water Pressure, dbar	dbar	\N
2645	ctdbp_seawater_conductivity_function_float32_S_m_1	ctdbp_seawater_conductivity	\N	Sea Water Conductivity, S m-1	S m-1	\N
2646	ctdbp_practical_salinity_function_float32_1	ctdbp_practical_salinity	\N	Sea Water Practical Salinity	1	\N
2647	ctdbp_seawater_density_function_float32_kg_m_3	ctdbp_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
2648	wavss_a_directional_frequency_function_float32_Hz	wavss_a_directional_frequency	\N	Directional wave spectral bins (WAVSTAT-FDS_L1) [Hz]	Hz	\N
2649	wavss_a_non_directional_frequency_function_float32_Hz	wavss_a_non_directional_frequency	\N	Non-directional wave spectral bins (WAVSTAT-FND_L1) [Hz]	Hz	\N
2650	wavss_a_buoymotion_time_function_float32_seconds_since_1900_01_01	wavss_a_buoymotion_time	\N	Buoy displacement data measurements NTP times(WAVSTAT-MOTT_L1)	seconds since 1900-01-01	\N
2651	wavss_a_corrected_mean_wave_direction_function_float32_deg	wavss_a_corrected_mean_wave_direction	\N	Mean wave direction corrected for magnetic declination (WAVSTAT-D_L2) [deg, [0 360)].	deg	\N
2652	wavss_a_corrected_directional_wave_direction_function_float32_deg	wavss_a_corrected_directional_wave_direction	\N	Directional waves' directions corrected for magnetic declination (WAVSTAT-DDS_L2) [deg, [0 360)].	deg	\N
2653	wavss_a_magcor_buoymotion_x_function_float32_m	wavss_a_magcor_buoymotion_x	\N	East displacement of the buoy on which the WAVSS is mounted, corrected for magnetic declination (WAVSTAT-MOTX_L1) [m]	m	\N
2654	wavss_a_magcor_buoymotion_y_function_float32_m	wavss_a_magcor_buoymotion_y	\N	North displacement of the buoy on which the WAVSS is mounted, corrected for magnetic declination (WAVSTAT-MOTY_L1) [m]	m	\N
2655	velpt_ab_eastward_velocity_function_float32_m_s_1	velpt_ab_eastward_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
2656	velpt_ab_northward_velocity_function_float32_m_s_1	velpt_ab_northward_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
2657	velpt_ab_upward_velocity_function_float32_m_s_1	velpt_ab_upward_velocity	\N	Upward Turbulent Velocity, m s-1	m s-1	\N
2658	battery_low_blank_boolean_int8_1	battery_low_blank	\N	Battery Low during Blank Cycle	1	\N
2659	ctdbp_cdef_dcl_ce_abs_oxygen_function_float32_umol_kg_1	ctdbp_cdef_dcl_ce_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
2660	adcpt_acfgm_dcl_eastward_earth_seawater_velocity_function_float32_m_s_1	adcpt_acfgm_dcl_eastward_earth_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
2661	adcpt_acfgm_dcl_northward_earth_seawater_velocity_function_float32_m_s_1	adcpt_acfgm_dcl_northward_earth_seawater_velocity	\N	Northward Earth Sea Water Velocity, m s-1	m s-1	\N
2662	adcpt_acfgm_dcl_eastward_beam_seawater_velocity_function_float32_m_s_1	adcpt_acfgm_dcl_eastward_beam_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
2663	adcpt_acfgm_dcl_northward_beam_seawater_velocity_function_float32_m_s_1	adcpt_acfgm_dcl_northward_beam_seawater_velocity	\N	Northward Beam Sea Water Velocity, m s-1	m s-1	\N
2664	ctdbp_cdef_ce_abs_oxygen_function_float32_umol_kg_1	ctdbp_cdef_ce_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
2665	ctdbp_cdef_dcl_ce_density_function_float32_kg_m_3	ctdbp_cdef_dcl_ce_density	\N	Density, kg m-3	kg m-3	\N
2666	ctdpf_j_density_function_float32_kg_m_3	ctdpf_j_density	\N	Density, kg m-3	kg m-3	\N
2667	dosta_abcdjm_cspp_tc_oxygen_function_float32_umol_L_1	dosta_abcdjm_cspp_tc_oxygen	\N	Temperature Compensated Dissolved Oxygen Concentration, umol/L	umol L-1	\N
2668	xdosta_abcdjm_cspp_abs_oxygen_function_float32_umol_kg_1	xdosta_abcdjm_cspp_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
2669	xdosta_ln_wfp_abs_oxygen_function_float32_umol_kg_1	xdosta_ln_wfp_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
2670	flcdr_x_mmp_cds_fluorometric_cdom_function_float32_ppb	flcdr_x_mmp_cds_fluorometric_cdom	\N	Fluorometric CDOM Concentration, ppb	ppb	\N
2671	flntu_x_mmp_cds_total_volume_scattering_coefficient_function_float32_m_1_sr_1	flntu_x_mmp_cds_total_volume_scattering_coefficient	\N	Total Volume Scattering Coefficient (Beta(117,700)), m-1 sr-1	m-1 sr-1	\N
2672	flntu_x_mmp_cds_fluorometric_chlorophyll_a_function_float32_ug_L_1	flntu_x_mmp_cds_fluorometric_chlorophyll_a	\N	Fluorometric Chlorophyll a Concentration, ug L-1	ug L-1	\N
2673	flntu_x_mmp_cds_bback_total_function_float32_m_1	flntu_x_mmp_cds_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
2674	cg_eng_alarm_sys_array_quantity_string_1	cg_eng_alarm_sys	\N	alarm sys	1	\N
2675	cg_eng_alarm_ts _array_quantity_string_1	cg_eng_alarm_tsÂ 	\N	alarm ts 	1	\N
2676	cg_eng_alarm_severity_array_quantity_string_1	cg_eng_alarm_severity	\N	alarm severity	1	\N
2677	cg_eng_alarm_at_array_quantity_int16_1	cg_eng_alarm_at	\N	alarm at	1	\N
2678	cg_eng_alarm_pc_array_quantity_int16_1	cg_eng_alarm_pc	\N	alarm pc	1	\N
2679	cg_eng_alarm_err_array_quantity_string_1	cg_eng_alarm_err	\N	alarm err	1	\N
2680	cg_eng_pwrsys_main_v_quantity_float32_1	cg_eng_pwrsys_main_v	\N	pwrsys main v	1	\N
2681	cg_eng_pwrsys_main_c_quantity_float32_1	cg_eng_pwrsys_main_c	\N	pwrsys main c	1	\N
2682	cg_eng_pwrsys_b_chg_quantity_float32_1	cg_eng_pwrsys_b_chg	\N	pwrsys b chg	1	\N
2683	cg_eng_pwrsys_override_quantity_uint16_1	cg_eng_pwrsys_override	\N	pwrsys override	1	\N
2684	cg_eng_pwrsys_eflag1_quantity_uint32_1	cg_eng_pwrsys_eflag1	\N	pwrsys eflag1	1	\N
2685	cg_eng_pwrsys_eflag2_quantity_uint32_1	cg_eng_pwrsys_eflag2	\N	pwrsys eflag2	1	\N
2686	cg_eng_pwrsys_eflag3_quantity_uint32_1	cg_eng_pwrsys_eflag3	\N	pwrsys eflag3	1	\N
2687	cg_eng_pwrsys_b1_0_quantity_float32_1	cg_eng_pwrsys_b1_0	\N	pwrsys b1 0	1	\N
2688	cg_eng_pwrsys_b1_1_quantity_float32_1	cg_eng_pwrsys_b1_1	\N	pwrsys b1 1	1	\N
2689	cg_eng_pwrsys_b1_2_quantity_float32_1	cg_eng_pwrsys_b1_2	\N	pwrsys b1 2	1	\N
2690	cg_eng_pwrsys_b2_0_quantity_float32_1	cg_eng_pwrsys_b2_0	\N	pwrsys b2 0	1	\N
2691	cg_eng_pwrsys_b2_1_quantity_float32_1	cg_eng_pwrsys_b2_1	\N	pwrsys b2 1	1	\N
2692	cg_eng_pwrsys_b2_2_quantity_float32_1	cg_eng_pwrsys_b2_2	\N	pwrsys b2 2	1	\N
2693	cg_eng_pwrsys_b3_0_quantity_float32_1	cg_eng_pwrsys_b3_0	\N	pwrsys b3 0	1	\N
2694	cg_eng_pwrsys_pv2_2_quantity_float32_1	cg_eng_pwrsys_pv2_2	\N	pwrsys pv2 2	1	\N
2695	cg_eng_pwrsys_pv3_0_quantity_float32_1	cg_eng_pwrsys_pv3_0	\N	pwrsys pv3 0	1	\N
2696	cg_eng_pwrsys_pv3_1_quantity_float32_1	cg_eng_pwrsys_pv3_1	\N	pwrsys pv3 1	1	\N
2697	cg_eng_pwrsys_pv3_2_quantity_float32_1	cg_eng_pwrsys_pv3_2	\N	pwrsys pv3 2	1	\N
2698	cg_eng_pwrsys_pv4_0_quantity_float32_1	cg_eng_pwrsys_pv4_0	\N	pwrsys pv4 0	1	\N
2699	cg_eng_pwrsys_pv4_1_quantity_float32_1	cg_eng_pwrsys_pv4_1	\N	pwrsys pv4 1	1	\N
2700	cg_eng_pwrsys_pv4_2_quantity_float32_1	cg_eng_pwrsys_pv4_2	\N	pwrsys pv4 2	1	\N
2701	cg_eng_pwrsys_wt1_0_quantity_float32_1	cg_eng_pwrsys_wt1_0	\N	pwrsys wt1 0	1	\N
2702	cg_eng_pwrsys_wt1_1_quantity_float32_1	cg_eng_pwrsys_wt1_1	\N	pwrsys wt1 1	1	\N
2703	cg_eng_pwrsys_wt1_2_quantity_float32_1	cg_eng_pwrsys_wt1_2	\N	pwrsys wt1 2	1	\N
2704	cg_eng_pwrsys_wt2_0_quantity_float32_1	cg_eng_pwrsys_wt2_0	\N	pwrsys wt2 0	1	\N
2705	cg_eng_pwrsys_wt2_1_quantity_float32_1	cg_eng_pwrsys_wt2_1	\N	pwrsys wt2 1	1	\N
2706	cg_eng_pwrsys_wt2_2_quantity_float32_1	cg_eng_pwrsys_wt2_2	\N	pwrsys wt2 2	1	\N
2707	cg_eng_pwrsys_fc1_0_quantity_float32_1	cg_eng_pwrsys_fc1_0	\N	pwrsys fc1 0	1	\N
2708	cg_eng_pwrsys_fc1_1_quantity_float32_1	cg_eng_pwrsys_fc1_1	\N	pwrsys fc1 1	1	\N
2709	cg_eng_pwrsys_fc1_2_quantity_float32_1	cg_eng_pwrsys_fc1_2	\N	pwrsys fc1 2	1	\N
2710	cg_eng_pwrsys_fc2_0_quantity_float32_1	cg_eng_pwrsys_fc2_0	\N	pwrsys fc2 0	1	\N
2711	cg_eng_pwrsys_fc2_1_quantity_float32_1	cg_eng_pwrsys_fc2_1	\N	pwrsys fc2 1	1	\N
2712	cg_eng_pwrsys_fc2_2_quantity_float32_1	cg_eng_pwrsys_fc2_2	\N	pwrsys fc2 2	1	\N
2713	cg_eng_pwrsys_temp_quantity_float32_1	cg_eng_pwrsys_temp	\N	pwrsys temp	1	\N
2714	cg_eng_pwrsys_fc_level_quantity_float32_1	cg_eng_pwrsys_fc_level	\N	pwrsys fc level	1	\N
2715	cg_eng_pwrsys_swg_0_quantity_float32_1	cg_eng_pwrsys_swg_0	\N	pwrsys swg 0	1	\N
2716	cg_eng_pwrsys_swg_1_quantity_float32_1	cg_eng_pwrsys_swg_1	\N	pwrsys swg 1	1	\N
2717	cg_eng_pwrsys_swg_2_quantity_float32_1	cg_eng_pwrsys_swg_2	\N	pwrsys swg 2	1	\N
2718	cg_eng_pwrsys_cvt_0_quantity_float32_1	cg_eng_pwrsys_cvt_0	\N	pwrsys cvt 0	1	\N
2719	cg_eng_pwrsys_cvt_1_quantity_float32_1	cg_eng_pwrsys_cvt_1	\N	pwrsys cvt 1	1	\N
2720	cg_eng_pwrsys_cvt_2_quantity_float32_1	cg_eng_pwrsys_cvt_2	\N	pwrsys cvt 2	1	\N
2721	cg_eng_pwrsys_cvt_3_quantity_float32_1	cg_eng_pwrsys_cvt_3	\N	pwrsys cvt 3	1	\N
2722	cg_eng_pwrsys_cvt_4_quantity_float32_1	cg_eng_pwrsys_cvt_4	\N	pwrsys cvt 4	1	\N
2723	cg_eng_pwrsys_last_update_quantity_float64_1	cg_eng_pwrsys_last_update	\N	pwrsys last update	1	\N
2724	cg_eng_sched_sys_array_quantity_string_1	cg_eng_sched_sys	\N	sched sys	1	\N
2725	cg_eng_sched_type_array_quantity_string_1	cg_eng_sched_type	\N	sched type	1	\N
2726	cg_eng_sched_status_array_quantity_string_1	cg_eng_sched_status	\N	sched status	1	\N
2727	cg_eng_sched_status_val_array_quantity_int16_1	cg_eng_sched_status_val	\N	sched status val	1	\N
2728	cg_eng_sched_num1_array_quantity_int16_1	cg_eng_sched_num1	\N	sched num1	1	\N
2729	cg_eng_sched_num2_array_quantity_int16_1	cg_eng_sched_num2	\N	sched num2	1	\N
2730	cg_eng_sched_num3_array_quantity_int16_1	cg_eng_sched_num3	\N	sched num3	1	\N
2731	cg_eng_sched_num4_array_quantity_int16_1	cg_eng_sched_num4	\N	sched num4	1	\N
2732	cg_eng_sched_num5_array_quantity_int16_1	cg_eng_sched_num5	\N	sched num5	1	\N
2733	cg_eng_sched_num6_array_quantity_int16_1	cg_eng_sched_num6	\N	sched num6	1	\N
2734	cg_eng_sched_num7_array_quantity_int16_1	cg_eng_sched_num7	\N	sched num7	1	\N
2735	cg_eng_sched_time_array_quantity_string_1	cg_eng_sched_time	\N	sched time	1	\N
2736	cg_eng_sched_remaining_array_quantity_int32_sec	cg_eng_sched_remaining	\N	sched remaining	sec	\N
2737	cg_eng_sched_last_update_quantity_float32_1	cg_eng_sched_last_update	\N	sched last update	1	\N
2738	cg_eng_pwrsys_b3_1_quantity_float32_1	cg_eng_pwrsys_b3_1	\N	pwrsys b3 1	1	\N
2739	cg_eng_pwrsys_b3_2_quantity_float32_1	cg_eng_pwrsys_b3_2	\N	pwrsys b3 2	1	\N
2740	cg_eng_pwrsys_b4_0_quantity_float32_1	cg_eng_pwrsys_b4_0	\N	pwrsys b4 0	1	\N
2741	cg_eng_pwrsys_b4_1_quantity_float32_1	cg_eng_pwrsys_b4_1	\N	pwrsys b4 1	1	\N
2742	cg_eng_pwrsys_b4_2_quantity_float32_1	cg_eng_pwrsys_b4_2	\N	pwrsys b4 2	1	\N
2743	cg_eng_pwrsys_pv1_0_quantity_float32_1	cg_eng_pwrsys_pv1_0	\N	pwrsys pv1 0	1	\N
2744	cg_eng_pwrsys_pv1_1_quantity_float32_1	cg_eng_pwrsys_pv1_1	\N	pwrsys pv1 1	1	\N
2745	cg_eng_pwrsys_pv1_2_quantity_float32_1	cg_eng_pwrsys_pv1_2	\N	pwrsys pv1 2	1	\N
2746	cg_eng_pwrsys_pv2_0_quantity_float32_1	cg_eng_pwrsys_pv2_0	\N	pwrsys pv2 0	1	\N
2747	cg_eng_pwrsys_pv2_1_quantity_float32_1	cg_eng_pwrsys_pv2_1	\N	pwrsys pv2 1	1	\N
2748	max_stack_quantity_float32_1	max_stack	\N	Max Stack	1	\N
2749	date_time_str_quantity_string_1	date_time_str	\N	Date and Time String	1	\N
2750	ctdmo_seawater_pressure_function_float32_dbar	ctdmo_seawater_pressure	\N	Sea Water Pressure, dBar	dbar	\N
2751	ctdmo_seawater_temperature_function_float32_deg_C	ctdmo_seawater_temperature	\N	Sea Water Temperature, deg_C	deg_C	\N
2752	ctdmo_seawater_conductivity_function_float32_S_m_1	ctdmo_seawater_conductivity	\N	Sea Water Conductivity, S m-1	S m-1	\N
2753	ctdmo_practical_salinity_function_float32_1	ctdmo_practical_salinity	\N	Practical Salinity (seawater salinity, PSS-78) [unitless]	1	\N
2754	ctdmo_seawater_density_function_float32_kg_m_3	ctdmo_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
2755	number_of_beam_sequences_quantity_int16_counts	number_of_beam_sequences	\N	Number of beam sequences per burst, counts	counts	\N
2756	number_of_beams_in_diagnostics_mode_quantity_int16_counts	number_of_beams_in_diagnostics_mode	\N	Number of beams in diagnostics mode, counts	counts	\N
2757	reserved_bit_easyq_boolean_int8_1	reserved_bit_easyq	\N	Reserved Bit - EasyQ	1	\N
2758	conductivity_millisiemens_quantity_float32_mS_m_1	conductivity_millisiemens	\N	Conductivity, mS m-1	mS m-1	\N
2759	header_timestamp_quantity_string_1	header_timestamp	\N	Controller Timestamp	1	\N
2760	gps_counts_quantity_int32_counts	gps_counts	\N	GPS Message Counts counts	counts	\N
2761	ntp_counts_quantity_int32_counts	ntp_counts	\N	NTP Message Counts	counts	\N
2762	pps_counts_quantity_int32_counts	pps_counts	\N	PPS Message Counts	counts	\N
2763	superv_counts_quantity_int32_counts	superv_counts	\N	SUPERV Message Counts	counts	\N
2764	dlog_mgr_counts_quantity_int32_counts	dlog_mgr_counts	\N	DLOG Mgr Message Counts	counts	\N
2765	uptime_string_quantity_string_1	uptime_string	\N	CPU Uptime	1	\N
2766	load_val_1_quantity_float32_counts	load_val_1	\N	CPU Loading Value	counts	\N
2767	load_val_2_quantity_float32_counts	load_val_2	\N	CPU Loading Value	counts	\N
2768	load_val_3_quantity_float32_counts	load_val_3	\N	CPU Loading Value	counts	\N
2769	mem_free_quantity_int32_kbytes	mem_free	\N	Free Memory, kbytes	kbytes	\N
2770	num_processes_quantity_int16_counts	num_processes	\N	Number of Processes	counts	\N
2771	log_type_quantity_string_1	log_type	\N	Log Type	1	\N
2772	message_text_quantity_string_1	message_text	\N	Message Text	1	\N
2773	message_sent_timestamp_quantity_string_1	message_sent_timestamp	\N	Timestamp when the message was sent	1	\N
2774	latitude_quantity_float32_degrees	latitude	\N	Latitude, degrees	degrees	\N
2775	longitude_quantity_float32_degrees	longitude	\N	Longitude, degrees	degrees	\N
2776	gps_speed_quantity_float32_knots	gps_speed	\N	Speed, knots	knots	\N
2777	gps_true_course_quantity_float32_degrees	gps_true_course	\N	True Course, degrees	degrees	\N
2778	gps_quality_quantity_int8_1	gps_quality	\N	GPS Quality Indicator	1	\N
2779	gps_num_satellites_quantity_int8_counts	gps_num_satellites	\N	Number of Satellites	counts	\N
2780	gps_hdop_quantity_float32_1	gps_hdop	\N	Horizontal dilution of precision	1	\N
2781	gps_altitude_quantity_float32_meters	gps_altitude	\N	Altitude, meters	meters	\N
2782	date_of_fix_quantity_string_1	date_of_fix	\N	Date of the GPS Fix	1	\N
2783	time_of_fix_quantity_string_1	time_of_fix	\N	Time of the GPS Fix	1	\N
2784	latitude_alt_format_quantity_string_1	latitude_alt_format	\N	Latitude Decimal Minutes	1	\N
2785	longitude_alt_format_quantity_string_1	longitude_alt_format	\N	Longitude Decimal Minutes	1	\N
2786	nmea_lock_quantity_int8_1	nmea_lock	\N	PPS (Pulse Per Second) Locked to GPS	1	\N
2787	delta_quantity_int32_ms	delta	\N	Time in ms pulse is off, ms	ms	\N
2788	delta_min_quantity_int32_ms	delta_min	\N	Min time the pulse has been off in latest reporting period, ms	ms	\N
2789	delta_max_quantity_int32_ms	delta_max	\N	Max time the pulse has been off in latest reporting period, ms	ms	\N
2790	bad_pulses_quantity_int32_counts	bad_pulses	\N	Bad Pulses	counts	\N
2791	board_type_quantity_string_1	board_type	\N	Controller Board Type, ex: dcl	1	\N
2792	vmain_backplane_bus_voltage_quantity_float32_volts	vmain_backplane_bus_voltage	\N	Vmain backplane bus voltage @ DCL Input	volts	\N
2793	imain_current_quantity_float32_ma	imain_current	\N	Imain, current, ma, @ DCL Input	ma	\N
2794	error_vmain_out_tolerance_quantity_int8_1	error_vmain_out_tolerance	\N	Vmain out of tolerance	1	\N
2795	error_imain_out_tolerance_quantity_int8_1	error_imain_out_tolerance	\N	Imain out of tolerance	1	\N
2796	error_dcl_iso_swgf_lim_exceeded_quantity_int8_1	error_dcl_iso_swgf_lim_exceeded	\N	DCL_ISO_3V3 SWGF limit exceeded	1	\N
2797	error_dcl_rtn_swfg_lim_exceeded_quantity_int8_1	error_dcl_rtn_swfg_lim_exceeded	\N	DCL_RTN_CPM SWGF limit exceeded	1	\N
2798	error_vmain_swgf_lim_exceeded_quantity_int8_1	error_vmain_swgf_lim_exceeded	\N	VMAIN SWGF limit exceeded	1	\N
2799	error_gmain_swgf_lim_exceeded_quantity_int8_1	error_gmain_swgf_lim_exceeded	\N	GNAUB SWGF limit exceeded	1	\N
2800	error_sensor_iso_swgf_lim_exceeded_quantity_int8_1	error_sensor_iso_swgf_lim_exceeded	\N	SENSOR_ISO_12V/SENSOR_ISO_24V SWGF limit exceeded	1	\N
2801	error_snsr_com_swgf_lim_exceeded_quantity_int8_1	error_snsr_com_swgf_lim_exceeded	\N	SNSR_COM SWGF limit exceeded	1	\N
2802	error_leak_detect_c1_lim_exceeded_quantity_int8_1	error_leak_detect_c1_lim_exceeded	\N	Leak-detect channel 1 exceeded limit	1	\N
2803	error_leak_detect_c2_lim_exceeded_quantity_int8_1	error_leak_detect_c2_lim_exceeded	\N	Lead-detect channel 2 exceeded limit	1	\N
2804	error_channel_overcurrent_fault_quantity_int8_1	error_channel_overcurrent_fault	\N	Channel-PIC overcurrent fault (any active channel)	1	\N
2805	error_channel_1_not_responding_quantity_int8_1	error_channel_1_not_responding	\N	Channel 1 not responding	1	\N
2806	error_channel_2_not_responding_quantity_int8_1	error_channel_2_not_responding	\N	Channel 2 not responding	1	\N
2807	error_channel_3_not_responding_quantity_int8_1	error_channel_3_not_responding	\N	Channel 3 not responding	1	\N
2808	error_channel_4_not_responding_quantity_int8_1	error_channel_4_not_responding	\N	Channel 4 not responding	1	\N
2809	error_channel_5_not_responding_quantity_int8_1	error_channel_5_not_responding	\N	Channel 5 not responding	1	\N
2810	error_channel_6_not_responding_quantity_int8_1	error_channel_6_not_responding	\N	Channel 6 not responding	1	\N
2811	error_channel_7_not_responding_quantity_int8_1	error_channel_7_not_responding	\N	Channel 7 not responding	1	\N
2812	error_channel_8_not_responding_quantity_int8_1	error_channel_8_not_responding	\N	Channel 8 not responding	1	\N
2813	error_i2c_error_quantity_int8_1	error_i2c_error	\N	I2C error	1	\N
2814	error_uart_error_quantity_int8_1	error_uart_error	\N	UART error	1	\N
2815	error_brown_out_reset_quantity_int8_1	error_brown_out_reset	\N	Brown out reset detected	1	\N
2816	bmp085_temp_quantity_float32_degrees_C	bmp085_temp	\N	BMP085 Temperature (Pressure Sensor), degrees C	degrees C	\N
2817	sht25_temp_quantity_float32_degrees_C	sht25_temp	\N	SHT25 Temperature (Humidity Sensor), degrees C	degrees C	\N
2818	murata_12v_temp_quantity_float32_degrees_C	murata_12v_temp	\N	12V Murata Temperature, degrees C	degrees C	\N
2819	murata_24v_temp_quantity_float32_degrees_C	murata_24v_temp	\N	24V Murata Temperature, degrees C	degrees C	\N
2820	vicor_12v_bcm_temp_quantity_float32_degrees_C	vicor_12v_bcm_temp	\N	12V Vicor BCM Temperature, degrees C	degrees C	\N
2821	sht25_humidity_quantity_float32_%relative	sht25_humidity	\N	SHT25 Humidity, %relative	%relative	\N
2822	bmp085_pressure_quantity_float32_psia	bmp085_pressure	\N	BMP085 pressure, psia	psia	\N
2823	active_swgf_channels_quantity_int8_1	active_swgf_channels	\N	Active SWGF channels (bitmask); ‘7’ = all 3 enabled	1	\N
2824	swgf_c1_max_leakage_quantity_float32_1	swgf_c1_max_leakage	\N	SWGF channel 1 maximum leakage (console to CPM, uA) positive -> DCL_RTN_CPM wet, negative -> DCL_ISO_3v3 wet	1	\N
2825	swgf_c2_max_leakage_quantity_float32_1	swgf_c2_max_leakage	\N	SWGF channel 2 maximum leakage (Vmain/Gmain), uAmp, Vmain/Gmain; positive -> Vmain wet, negative -> Gmain wet	1	\N
2826	swgf_c3_max_leakage_quantity_float32_1	swgf_c3_max_leakage	\N	SWGF channel 3 maximum leakage (isolated instrument 12/24V), uAmp, sensor 12v/24v & SNSR_COM,; positive -> sensor 12 and/or 24V wet, negative -> SNSR_COM wet	1	\N
2827	active_leak_detect_channels_quantity_int8_1	active_leak_detect_channels	\N	Active leak-detect channels (bitmask)	1	\N
2828	leak_detect_c1_v_quantity_int32_volts	leak_detect_c1_v	\N	Leak-detect channel 1 voltage; 0-.250 = leak, 1100-1300 = dry, 2000-2600 = open, volts	volts	\N
2829	leak_detect_c2_v_quantity_int32_volts	leak_detect_c2_v	\N	Leak-detect channel 2 voltage; 0-.250 = leak, 1100-1300 = dry, 2000-2600 = open, volts	volts	\N
2830	channel_state_array_quantity_int8_1	channel_state	\N	8 element Array of Channel state, 0 = off, 1 = on	1	\N
2831	channel_v_array_quantity_float32_volts	channel_v	\N	8 element Array of Channel Voltage, volts	volts	\N
2832	channel_i_array_quantity_float32_ma	channel_i	\N	8 element Array of Channel Current, ma	ma	\N
2833	channel_error_status_array_quantity_int8_1	channel_error_status	\N	8 element Array of Channel Error Status; 0 = OK	1	\N
2834	pwr_board_mode_quantity_int8_1	pwr_board_mode	\N	Power Board Mode:0=off, 1=lo pwr enable, 2=hi pwr enable, 3=both enabled	1	\N
2835	dpb_mode_quantity_int8_1	dpb_mode	\N	dpb mode: 0=off, 1=gpio (legacy mode, either hi or lo pwr enabled, not both)	1	\N
2836	dpb_voltage_mode_quantity_int8_1	dpb_voltage_mode	\N	Dpb voltage mode: 0=off, 1=lp12, 2=lp12 & 24, 3=hp12, 4=hp12 & 24	1	\N
2837	vmain_dpb_in_quantity_float32_volts	vmain_dpb_in	\N	Vmain @ DPB input, volts	volts	\N
2838	imain_dpb_in_quantity_float32_ma	imain_dpb_in	\N	Imain @ DPB input, ma	ma	\N
2839	out_12v_v_quantity_float32_volts	out_12v_v	\N	12V output, V, volts	volts	\N
2840	out_12v_i_quantity_float32_ma	out_12v_i	\N	12V output, I, ma	ma	\N
2841	out_24v_v_quantity_float32_volts	out_24v_v	\N	24V output, V, volts	volts	\N
2842	out_24v_i_quantity_float32_ma	out_24v_i	\N	24V output, I, ma	ma	\N
2843	datalogger_timestamp_quantity_string_1	datalogger_timestamp	\N	Datalogger timestamp	1	\N
2844	dlog_mgr_act_quantity_int8_1	dlog_mgr_act	\N	Number of data loggers active for this DCL	1	\N
2845	dlog_mgr_str_quantity_int8_1	dlog_mgr_str	\N	Number of data loggers started for this DCL	1	\N
2846	dlog_mgr_hlt_quantity_int8_1	dlog_mgr_hlt	\N	Number of data loggers stopped for this DCL	1	\N
2847	dlog_mgr_fld_quantity_int8_1	dlog_mgr_fld	\N	Number of data loggers failed for this DCL	1	\N
2848	dlog_mgr_map_quantity_string_1	dlog_mgr_map	\N	Map of the state of what is running on each port	1	\N
2849	instrument_identifier_quantity_string_1	instrument_identifier	\N	Identifier for the instrument	1	\N
2850	datalogger_state_quantity_string_1	datalogger_state	\N	Datalogger state	1	\N
2851	bytes_sent_quantity_int32_counts	bytes_sent	\N	Bytes sent to instrument	counts	\N
2852	bytes_received_quantity_int32_counts	bytes_received	\N	Bytes received from instrument	counts	\N
2853	bytes_logged_quantity_int32_counts	bytes_logged	\N	Bytes logged to file	counts	\N
2854	good_records_quantity_int32_counts	good_records	\N	Number of good data records	counts	\N
2855	bad_records_quantity_int32_counts	bad_records	\N	Number of bad data records	counts	\N
2856	bad_bytes_quantity_int32_counts	bad_bytes	\N	Number of bad bytes	counts	\N
2857	time_received_last_data_quantity_int64_s	time_received_last_data	\N	Linux time got last data, s	s	\N
2858	time_last_communicated_quantity_int64_s	time_last_communicated	\N	Linux time last communicated with instrument, s	s	\N
2859	message_sent_type_quantity_string_1	message_sent_type	\N	Message sent type	1	\N
2860	sync_type_quantity_string_1	sync_type	\N	Type of synchronization	1	\N
2861	ntp_offset_quantity_float32_ms	ntp_offset	\N	Offset, ms	ms	\N
2862	ntp_jitter_quantity_float32_ms	ntp_jitter	\N	Jitter, ms	ms	\N
2863	burst_start_time_array_quantity_uint8_1	burst_start_time	\N	Burst Start Time	1	\N
2864	peak_wave_direction_quantity_float32_degrees	peak_wave_direction	\N	Peak Wave Direction, degrees	degrees	\N
2865	tp_sea_quantity_float32_seconds	tp_sea	\N	Tp Sea, seconds	seconds	\N
2866	dp_sea_quantity_float32_degrees	dp_sea	\N	Dp Sea, degrees	degrees	\N
2867	hs_sea_quantity_float32_meters	hs_sea	\N	Hs Sea, meters	meters	\N
2868	tp_swell_quantity_float32_seconds	tp_swell	\N	Tp Swell, seconds	seconds	\N
2869	dp_swell_quantity_float32_degrees	dp_swell	\N	Dp Swell, degrees	degrees	\N
2870	hs_swell_quantity_float32_meters	hs_swell	\N	Hs Swell, meters	meters	\N
2871	depth_water_level_quantity_float32_millimeters	depth_water_level	\N	Depth Water Level, millimeters	millimeters	\N
2872	h_max_quantity_float32_meters	h_max	\N	H Max, meters	meters	\N
2873	t_max_quantity_float32_seconds	t_max	\N	T Max, seconds	seconds	\N
2874	h_1_3_quantity_float32_meters	h_1_3	\N	H 1 3, meters	meters	\N
2875	t_1_3_quantity_float32_seconds	t_1_3	\N	T 1 3, seconds	seconds	\N
2876	h_mean_quantity_float32_meters	h_mean	\N	H Mean, meters	meters	\N
2877	t_mean_quantity_float32_seconds	t_mean	\N	T Mean, seconds	seconds	\N
2878	h_1_10_quantity_float32_meters	h_1_10	\N	H 1 10, meters	meters	\N
2879	t_1_10_quantity_float32_seconds	t_1_10	\N	T 1 10, seconds	seconds	\N
2880	d_mean_quantity_float32_degrees	d_mean	\N	Mean Peak Wave Direction, degrees	degrees	\N
2881	num_bins_quantity_uint8_counts	num_bins	\N	Number of bins, counts	counts	\N
2882	depth_level_magnitude_array_quantity_float32_m_s_1	depth_level_magnitude	\N	Depth Level Magnitude, m/s	m s-1	\N
2883	depth_level_direction_array_quantity_int16_deg	depth_level_direction	\N	Depth Level Direction, deg	deg	\N
2884	file_time_quantity_string_1	file_time	\N	Timestamp from the filename	1	\N
2885	num_dir_quantity_uint16_counts	num_dir	\N	Number of calculated Directions for Spectrum, counts	counts	\N
2886	num_freq_quantity_uint16_counts	num_freq	\N	Number of Frequency bands, counts	counts	\N
2887	freq_w_band_quantity_float64_hz	freq_w_band	\N	Width of Frequency bands, hz	hz	\N
2888	freq_0_quantity_float64_hz	freq_0	\N	Center frequency of first Frequency band, hz	hz	\N
2889	start_dir_quantity_float64_degrees	start_dir	\N	Starting Direction of (NumDir) Directions, degrees	degrees	\N
2890	directional_surface_spectrum_array_quantity_uint32_mm2_hz_1	directional_surface_spectrum	\N	Directional Surface Spectrum, mm2/hz	mm2 hz-1	\N
2891	met_barpres_function_float32_Pa	met_barpres	\N	Barometric Pressure, Pa	Pa	\N
2892	met_windavg_mag_corr_east_function_float32_m_s_1	met_windavg_mag_corr_east	\N	Eastward Wind Velocity relative to True North	m s-1	\N
2893	met_windavg_mag_corr_north_function_float32_m_s_1	met_windavg_mag_corr_north	\N	Northward Wind Velocity relative to True North	m s-1	\N
2894	met_current_direction_function_float32_degrees	met_current_direction	\N	Current Direction, degrees	degrees	\N
2895	met_current_speed_function_float32_m_s_1	met_current_speed	\N	Current Speed, m/s	m s-1	\N
2896	met_relwind_direction_function_float32_degrees	met_relwind_direction	\N	Relative Wind Direction, degrees	degrees	\N
2897	met_relwind_speed_function_float32_m_s_1	met_relwind_speed	\N	Relative Wind Speed, m/s	m s-1	\N
2898	met_timeflx_function_float32_seconds_since_01_01_1900	met_timeflx	\N	Hourly Averaged Timestamp, seconds since 01-01-1900	seconds since 01-01-1900	\N
2899	met_netsirr_function_float32_W_m_2	met_netsirr	\N	Net Shortwave Radiation, W/m2	W m-2	\N
2900	met_rainrte_function_float32_mm_hr_1	met_rainrte	\N	Rain Rate, mm/hr	mm hr-1	\N
2901	met_salsurf_function_float32_1	met_salsurf	\N	Sea Surface Practical Salinity, unitless	1	\N
2902	met_spechum_function_float32_g_kg_1	met_spechum	\N	Air Specific Humidity, g/kg	g kg-1	\N
2903	met_buoyfls_function_float32_W_m_2	met_buoyfls	\N	Sonic Buoyancy Flux, W/m2	W m-2	\N
2904	met_buoyflx_function_float32_W_m_2	met_buoyflx	\N	Buoyancy Flux, W/m2	W m-2	\N
2905	met_frshflx_function_float32_mm_hr_1	met_frshflx	\N	Freshwater Upward Flux, mm/hr	mm hr-1	\N
2906	met_heatflx_function_float32_W_m_2	met_heatflx	\N	Total Net Upward Heat Flux, W/m2	W m-2	\N
2907	met_latnflx_function_float32_W_m_2	met_latnflx	\N	Upward Latent Heat Flux, W/m2	W m-2	\N
2908	met_mommflx_function_float32_N_m_2	met_mommflx	\N	Wind Stress Tau (Absolute Value of the Momentum Flux), N/m2	N m-2	\N
2909	met_netlirr_function_float32_W_m_2	met_netlirr	\N	Net Upward Longwave Irradiance, W/m2	W m-2	\N
2910	met_rainflx_function_float32_W_m_2	met_rainflx	\N	Net Upward Rain Heat Flux, W/m2	W m-2	\N
2911	met_sensflx_function_float32_W_m_2	met_sensflx	\N	Net Upward Sensible Heat Flux, W/m2	W m-2	\N
2912	met_sphum2m_function_float32_g_kg_1	met_sphum2m	\N	Modelled Specific Humidity, g/kg	g kg-1	\N
2913	met_stablty_function_float32_1	met_stablty	\N	Monin-Obukhov Stability, unitless	1	\N
2914	met_tempa2m_function_float32_degC	met_tempa2m	\N	Modelled Air Temperature, degrees C	degC	\N
2915	met_tempskn_function_float32_degC	met_tempskn	\N	Skin Sea Temperature, degrees C	degC	\N
2916	met_wind10m_function_float32_m_s_1	met_wind10m	\N	Modelled Windspeed, m/s	m s-1	\N
2917	num_fields_quantity_uint16_counts	num_fields	\N	Num Fields, counts	counts	\N
2918	frequency_band_array_quantity_float64_hz	frequency_band	\N	Frequency Band, hz	hz	\N
2919	bandwidth_band_array_quantity_float64_hz	bandwidth_band	\N	Bandwidth Band, hz	hz	\N
2920	energy_density_band_array_quantity_float64_m2_hz_1	energy_density_band	\N	Energy Density Band, m2/hz	m2 hz-1	\N
2921	direction_band_array_quantity_float64_degrees	direction_band	\N	Direction Band, degrees	degrees	\N
2922	a1_band_array_quantity_float64_1	a1_band	\N	A1 Band	1	\N
2923	b1_band_array_quantity_float64_1	b1_band	\N	B1 Band	1	\N
2924	a2_band_array_quantity_float64_1	a2_band	\N	A2 Band	1	\N
2925	b2_band_array_quantity_float64_1	b2_band	\N	B2 Band	1	\N
2926	check_factor_band_array_quantity_float64_1	check_factor_band	\N	Check Factor Band	1	\N
2927	acceleration_x_quantity_float32_gravity	acceleration_x	\N	Acceleration X, g	gravity	\N
2928	acceleration_y_quantity_float32_gravity	acceleration_y	\N	Acceleration Y, g	gravity	\N
2929	acceleration_z_quantity_float32_gravity	acceleration_z	\N	Acceleration Z, g	gravity	\N
2930	angular_rate_x_quantity_float32_rad_s_1	angular_rate_x	\N	Angular Rate X, rad/s	rad s-1	\N
3013	ps_std_quantity_uint32_1	ps_std	\N	Ps Std	1	\N
2931	angular_rate_y_quantity_float32_rad_s_1	angular_rate_y	\N	Angular Rate Y, rad/s	rad s-1	\N
2932	angular_rate_z_quantity_float32_rad_s_1	angular_rate_z	\N	Angular Rate Z, rad/s	rad s-1	\N
2933	magnetometer_x_quantity_float32_Gauss	magnetometer_x	\N	Magnetometer X, Gauss	Gauss	\N
2934	magnetometer_y_quantity_float32_Gauss	magnetometer_y	\N	Magnetometer Y, Gauss	Gauss	\N
2935	magnetometer_z_quantity_float32_Gauss	magnetometer_z	\N	Magnetometer Z, Gauss	Gauss	\N
2936	tic_counter_quantity_float32_sec	tic_counter	\N	Tic Counter, s	sec	\N
2937	sequence_number_quantity_uint16_1	sequence_number	\N	Sequence Number	1	\N
2938	file_mode_quantity_uint8_1	file_mode	\N	File Mode	1	\N
2939	rec_time_series_quantity_uint8_1	rec_time_series	\N	Rec Time Series	1	\N
2940	rec_spectra_quantity_uint8_1	rec_spectra	\N	Rec Spectra	1	\N
2941	rec_dir_spec_quantity_uint8_1	rec_dir_spec	\N	Rec Dir Spec	1	\N
2942	samples_per_burst_quantity_uint16_counts	samples_per_burst	\N	Samples Per Burst, counts	counts	\N
2943	time_between_samples_quantity_uint16_centiSec	time_between_samples	\N	Time Between Samples, 1/100 s	centiSec	\N
2944	time_between_bursts_sec_quantity_uint16_s	time_between_bursts_sec	\N	Time Between Bursts, s	s	\N
2945	bin_size_quantity_uint16_cm	bin_size	\N	Bin Size, cm	cm	\N
2946	bin_1_middle_quantity_uint16_cm	bin_1_middle	\N	Bin 1 Middle, cm	cm	\N
2947	num_range_bins_quantity_uint8_counts	num_range_bins	\N	Num Range Bins, counts	counts	\N
2948	num_vel_bins_quantity_uint8_counts	num_vel_bins	\N	Num Vel Bins, counts	counts	\N
2949	num_int_bins_quantity_uint8_counts	num_int_bins	\N	Num Int Bins, counts	counts	\N
2950	num_beams_quantity_uint8_counts	num_beams	\N	Num Beams, counts	counts	\N
2951	beam_conf_quantity_uint8_degrees	beam_conf	\N	Beam Conf, degrees	degrees	\N
2952	wave_param_source_quantity_uint8_1	wave_param_source	\N	Wave Param Source	1	\N
2953	nfft_samples_quantity_uint16_counts	nfft_samples	\N	Nfft Samples, counts	counts	\N
2954	num_directional_slices_quantity_uint16_counts	num_directional_slices	\N	Num Directional Slices, counts	counts	\N
2955	num_freq_bins_quantity_uint16_counts	num_freq_bins	\N	Num Freq Bins, counts	counts	\N
2956	window_type_quantity_uint16_1	window_type	\N	Window Type	1	\N
2957	use_press_4_depth_quantity_uint8_1	use_press_4_depth	\N	Use Press 4 Depth	1	\N
2958	use_strack_4_depth_quantity_uint8_1	use_strack_4_depth	\N	Use Strack 4 Depth	1	\N
2959	strack_spec_quantity_uint8_1	strack_spec	\N	Strack Spec	1	\N
2960	press_spec_quantity_uint8_1	press_spec	\N	Press Spec	1	\N
2961	vel_min_quantity_int16_mm_s_1	vel_min	\N	Vel Min, mm/s	mm s-1	\N
2962	vel_max_quantity_int16_mm_s_1	vel_max	\N	Vel Max, mm/s	mm s-1	\N
2963	vel_std_quantity_uint8_mm_s_1	vel_std	\N	Vel Std, mm/s	mm s-1	\N
2964	vel_max_change_quantity_uint16_mm_s_1	vel_max_change	\N	Vel Max Change, mm/s	mm s-1	\N
2965	vel_pct_gd_quantity_uint8_0	vel_pct_gd	\N	Vel Pct Gd, %	0%	\N
2966	surf_min_quantity_int32_mm	surf_min	\N	Surf Min, mm	mm	\N
2967	surf_max_quantity_int32_mm	surf_max	\N	Surf Max, mm	mm	\N
2968	surf_std_quantity_uint8_mm	surf_std	\N	Surf Std, mm	mm	\N
2969	surf_max_chng_quantity_int32_mm	surf_max_chng	\N	Surf Max Chng, mm	mm	\N
2970	surf_pct_gd_quantity_uint8_0	surf_pct_gd	\N	Surf Pct Gd, %	0%	\N
2971	tbe_max_dev_quantity_uint16_1/110ths_s	tbe_max_dev	\N	Tbe Max Dev, 1/110ths s	1/110ths s	\N
2972	h_max_dev_quantity_uint16_deg	h_max_dev	\N	H Max Dev, deg	deg	\N
2973	pr_max_dev_quantity_uint8_deg	pr_max_dev	\N	Pr Max Dev, deg	deg	\N
2974	nom_depth_quantity_uint32_cm	nom_depth	\N	Nom Depth, cm	cm	\N
2975	cal_press_quantity_uint8_1	cal_press	\N	Cal Press	1	\N
2976	depth_offset_quantity_int32_mm	depth_offset	\N	Depth Offset, mm	mm	\N
2977	currents_quantity_uint8_1	currents	\N	Currents	1	\N
2978	small_wave_freq_quantity_uint16_centiHz	small_wave_freq	\N	Small Wave Freq, 1/100 Hz	centiHz	\N
2979	small_wave_thresh_quantity_int16_mm	small_wave_thresh	\N	Small Wave Thresh, mm	mm	\N
2980	tilts_quantity_uint8_1	tilts	\N	Tilts	1	\N
2981	fixed_pitch_quantity_int16_deg	fixed_pitch	\N	Fixed Pitch, deg	deg	\N
2982	fixed_roll_quantity_int16_deg	fixed_roll	\N	Fixed Roll, deg	deg	\N
2983	bottom_slope_x_quantity_int16_m	bottom_slope_x	\N	Bottom Slope X, m	m	\N
2984	bottom_slope_y_quantity_int16_m	bottom_slope_y	\N	Bottom Slope Y, m	m	\N
2985	down_quantity_uint8_1	down	\N	Down	1	\N
2986	trans_v2_surf_quantity_uint8_1	trans_v2_surf	\N	Trans V2 Surf	1	\N
2987	scale_spec_quantity_uint8_1	scale_spec	\N	Scale Spec	1	\N
2988	sample_rate_quantity_float32_s	sample_rate	\N	Sample Rate, s	s	\N
2989	freq_thresh_quantity_float32_hz	freq_thresh	\N	Freq Thresh, hz	hz	\N
2990	dummy_surf_quantity_uint8_1	dummy_surf	\N	Dummy Surf	1	\N
2991	remove_bias_quantity_uint8_1	remove_bias	\N	Remove Bias	1	\N
2992	dir_cutoff_quantity_uint16_Hz	dir_cutoff	\N	Dir Cutoff, Hz	Hz	\N
2993	heading_variation_quantity_int16_centidegrees	heading_variation	\N	Heading Variation, 1/100 deg	centidegrees	\N
2994	soft_rev_quantity_uint8_1	soft_rev	\N	Soft Rev	1	\N
2995	clip_pwr_spec_quantity_uint8_1	clip_pwr_spec	\N	Clip Pwr Spec	1	\N
2996	dir_p2_quantity_uint8_1	dir_p2	\N	Dir P2	1	\N
2997	horizontal_quantity_uint8_1	horizontal	\N	Horizontal	1	\N
2998	start_time_array_quantity_uint8_1	start_time	\N	Start Time	1	\N
2999	stop_time_array_quantity_uint8_1	stop_time	\N	Stop Time	1	\N
3000	freq_lo_quantity_uint16_milliHz	freq_lo	\N	Freq Lo, 1/1000th Hz	milliHz	\N
3001	average_depth_quantity_uint32_mm	average_depth	\N	Average Depth, mm	mm	\N
3002	altitude_quantity_uint32_cm	altitude	\N	Altitude, cm	cm	\N
3003	bin_map_array_quantity_uint8_1	bin_map	\N	Bin Map	1	\N
3004	disc_flag_quantity_uint8_1	disc_flag	\N	Disc Flag	1	\N
3005	pct_gd_press_quantity_uint8_0	pct_gd_press	\N	Pct Gd Press, %	0%	\N
3006	avg_ss_quantity_uint16_m_s_1	avg_ss	\N	Avg Ss, m/s	m s-1	\N
3007	avg_temp_quantity_uint16_deg_C	avg_temp	\N	Avg Temp, deg C	deg C	\N
3008	pct_gd_surf_quantity_uint8_0	pct_gd_surf	\N	Pct Gd Surf, %	0%	\N
3009	pct_gd_vel_quantity_uint8_0	pct_gd_vel	\N	Pct Gd Vel, %	0%	\N
3010	heading_offset_quantity_int16_deg	heading_offset	\N	Heading Offset, deg	deg	\N
3011	hs_std_quantity_uint32_1	hs_std	\N	Hs Std	1	\N
3012	vs_std_quantity_uint32_1	vs_std	\N	Vs Std	1	\N
3014	ds_freq_hi_quantity_uint32_centiHz	ds_freq_hi	\N	Ds Freq Hi, 1/100 Hz	centiHz	\N
3015	vs_freq_hi_quantity_uint32_centiHz	vs_freq_hi	\N	Vs Freq Hi, 1/100 Hz	centiHz	\N
3016	ps_freq_hi_quantity_uint32_centiHz	ps_freq_hi	\N	Ps Freq Hi, 1/100 Hz	centiHz	\N
3017	ss_freq_hi_quantity_uint32_centiHz	ss_freq_hi	\N	Ss Freq Hi, 1/100 Hz	centiHz	\N
3018	x_vel_quantity_int16_mm_s_1	x_vel	\N	X Vel, mm/s	mm s-1	\N
3019	y_vel_quantity_int16_mm_s_1	y_vel	\N	Y Vel, mm/s	mm s-1	\N
3020	avg_pitch_quantity_int16_centidegrees	avg_pitch	\N	Avg Pitch, 1/100th deg	centidegrees	\N
3021	avg_roll_quantity_int16_centidegrees	avg_roll	\N	Avg Roll, 1/100th deg	centidegrees	\N
3022	avg_heading_quantity_int16_centidegrees	avg_heading	\N	Avg Heading, 1/100th deg	centidegrees	\N
3023	samples_collected_quantity_int16_counts	samples_collected	\N	Samples Collected, counts	counts	\N
3024	vspec_pct_measured_quantity_int16_0	vspec_pct_measured	\N	Vspec Pct Measured, %	0%	\N
3025	vspec_num_freq_quantity_uint16_counts	vspec_num_freq	\N	Vspec Num Freq, counts	counts	\N
3026	vspec_dat_array_quantity_int32_mm_sqrt(Hz)_1	vspec_dat	\N	Vspec Dat, mm/sqrt(Hz)	mm sqrt(Hz)-1	\N
3027	sspec_num_freq_quantity_uint16_counts	sspec_num_freq	\N	Sspec Num Freq, counts	counts	\N
3028	sspec_dat_array_quantity_int32_mm_sqrt(Hz)_1	sspec_dat	\N	Sspec Dat, mm/sqrt(Hz)	mm sqrt(Hz)-1	\N
3029	pspec_num_freq_quantity_uint16_counts	pspec_num_freq	\N	Pspec Num Freq, counts	counts	\N
3030	pspec_dat_array_quantity_int32_mm_sqrt(Hz)_1	pspec_dat	\N	Pspec Dat, mm/sqrt(Hz)	mm sqrt(Hz)-1	\N
3031	dspec_num_freq_quantity_uint16_counts	dspec_num_freq	\N	Dspec Num Freq, counts	counts	\N
3032	dspec_num_dir_quantity_uint16_counts	dspec_num_dir	\N	Dspec Num Dir, counts	counts	\N
3033	dspec_good_quantity_uint16_counts	dspec_good	\N	Dspec Good, counts	counts	\N
3034	dspec_dat_array_quantity_uint32_(mm_sqrt(Hz)_1)_deg_1	dspec_dat	\N	Dspec Dat, mm/sqrt(Hz)/deg	(mm sqrt(Hz)-1) deg-1	\N
3035	wave_hs1_quantity_int16_mm	wave_hs1	\N	Wave Hs1, mm	mm	\N
3036	wave_tp1_quantity_int16_dsec	wave_tp1	\N	Wave Tp1, 1/10 s	dsec	\N
3037	wave_dp1_quantity_int16_deg	wave_dp1	\N	Wave Dp1, deg	deg	\N
3038	wave_hs2_quantity_int16_mm	wave_hs2	\N	Wave Hs2, mm	mm	\N
3039	wave_tp2_quantity_int16_dsec	wave_tp2	\N	Wave Tp2, 1/10 s	dsec	\N
3040	wave_dp2_quantity_int16_deg	wave_dp2	\N	Wave Dp2, deg	deg	\N
3041	wave_dm_quantity_int16_deg	wave_dm	\N	Wave Dm, deg	deg	\N
3042	hpr_num_samples_quantity_uint16_counts	hpr_num_samples	\N	Hpr Num Samples, counts	counts	\N
3043	beam_angle_quantity_uint16_deg	beam_angle	\N	Beam Angle, deg	deg	\N
3044	heading_time_series_array_quantity_int16_centidegrees	heading_time_series	\N	Heading Time Series, 1/100th deg	centidegrees	\N
3045	pitch_time_series_array_quantity_int16_centidegrees	pitch_time_series	\N	Pitch Time Series, 1/100th deg	centidegrees	\N
3046	roll_time_series_array_quantity_int16_centidegrees	roll_time_series	\N	Roll Time Series, 1/100th deg	centidegrees	\N
3047	vel3d_k_beams_quantity_uint8_1	vel3d_k_beams	\N	Number of Beams	1	\N
3048	flort_dj_bback_total_function_float32_m_1	flort_dj_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
3049	flort_dj_scat_seawater_function_float32_m_1	flort_dj_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
3050	dosta_ln_wfp_abs_oxygen_function_float32_umol_kg_1	dosta_ln_wfp_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3051	dosta_abcdjm_cspp_abs_oxygen_function_float32_umol_kg_1	dosta_abcdjm_cspp_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3052	flort_d_bback_total_function_float32_m_1	flort_d_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
3053	flort_d_scat_seawater_function_float32_m_1	flort_d_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
3054	velpt_d_eastward_velocity_function_float32_m_s_1	velpt_d_eastward_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
3055	velpt_d_northward_velocity_function_float32_m_s_1	velpt_d_northward_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
3056	velpt_d_upward_velocity_function_float32_m_s_1	velpt_d_upward_velocity	\N	Upward Turbulent Velocity, m s-1	m s-1	\N
3057	vel3d_k_eastward_velocity_function_float32_m_s_1	vel3d_k_eastward_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
3058	vel3d_k_northward_velocity_function_float32_m_s_1	vel3d_k_northward_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
3059	vel3d_k_upward_velocity_function_float32_m_s_1	vel3d_k_upward_velocity	\N	Upward Turbulent Velocity, m s-1	m s-1	\N
3060	parad_j_par_counts_output_function_float32_umol_photons_m_2_s_1	parad_j_par_counts_output	\N	Photosynthetic Active Radiation (PAR)	umol photons m-2 s-1	\N
3061	optaa_dj_cspp_beam_attenuation_function_float32_m_1	optaa_dj_cspp_beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
3062	optaa_dj_cspp_optical_absorption_function_float32_m_1	optaa_dj_cspp_optical_absorption	\N	Optical Absorption, m-1	m-1	\N
3063	optaa_dj_dcl_beam_attenuation_function_float32_m_1	optaa_dj_dcl_beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
3064	optaa_dj_dcl_optical_absorption_function_float32_m_1	optaa_dj_dcl_optical_absorption	\N	Optical Absorption, m-1	m-1	\N
3065	dosta_abcdjm_dcl_abs_oxygen_function_float32_umol_kg_1	dosta_abcdjm_dcl_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3066	battery_voltage_dv_quantity_uint16_dV	battery_voltage_dv	\N	Battery voltage (0.1 V)	dV	\N
3067	sound_speed_dms_quantity_uint16_dm_s_1	sound_speed_dms	\N	Speed of sound (0.1 m/s) or analog input 2	dm s-1	\N
3068	heading_decidegree_quantity_int16_deci_degrees	heading_decidegree	\N	compass heading (0.1°)	deci-degrees	\N
3069	roll_decidegree_quantity_int16_deci_degrees	roll_decidegree	\N	compass pitch (0.1°)	deci-degrees	\N
3070	pitch_decidegree_quantity_int16_deci_degrees	pitch_decidegree	\N	compass roll (0.1°)	deci-degrees	\N
3071	temperature_centidegree_quantity_int16_cdeg_C	temperature_centidegree	\N	temperature (0.01 °C)	cdeg_C	\N
3072	pressure_mbar_quantity_int32_0.001_dbar	pressure_mbar	\N	pressure (0.001 dbar)	0.001 dbar	\N
3073	seawater_pressure_mbar_quantity_int32_0.001_dbar	seawater_pressure_mbar	\N	Seawater Pressure, (0.001 dbar)	0.001 dbar	\N
3074	abs_seafloor_pressure_function_float32_dbar	abs_seafloor_pressure	\N	Seafloor Pressure, dbar	dbar	\N
3075	datalog_manager_version_quantity_string_1	datalog_manager_version	\N	datalog manager version	1	\N
3076	system_software_version_quantity_string_1	system_software_version	\N	system software version	1	\N
3077	total_run_time_quantity_int64_Secs	total_run_time	\N	total run time, Secs	Secs	\N
3078	fuel_cell_voltage_quantity_int32_mV	fuel_cell_voltage	\N	fuel cell voltage, mV	mV	\N
3079	fuel_cell_current_quantity_int32_mA	fuel_cell_current	\N	fuel cell current, mA	mA	\N
3080	reformer_temperature_quantity_int32_ddeg_C	reformer_temperature	\N	reformer temperature, decidegrees C	ddeg_C	\N
3081	fuel_cell_h2_pressure_quantity_int32_mPSI	fuel_cell_h2_pressure	\N	fuel cell h2 pressure, mPSI	mPSI	\N
3082	fuel_cell_temperature_quantity_int32_ddeg_C	fuel_cell_temperature	\N	fuel cell temperature, decidegrees C	ddeg_C	\N
3083	reformer_fuel_pressure_quantity_int32_mPSI	reformer_fuel_pressure	\N	reformer fuel pressure, mPSI	mPSI	\N
3084	fuel_pump_pwm_drive_percent_quantity_int32_%	fuel_pump_pwm_drive_percent	\N	fuel pump pwm drive percent	%	\N
3085	air_pump_pwm_drive_percent_quantity_int32_%	air_pump_pwm_drive_percent	\N	air pump pwm drive percent	%	\N
3086	coolant_pump_pwm_drive_percent_quantity_int32_%	coolant_pump_pwm_drive_percent	\N	coolant pump pwm drive percent	%	\N
3087	air_pump_tach_count_quantity_int32_Counts	air_pump_tach_count	\N	air pump tach count	Counts	\N
3088	fuel_cell_state_quantity_int32_1	fuel_cell_state	\N	fuel cell state	1	\N
3089	fuel_remaining_quantity_int32_mL	fuel_remaining	\N	fuel remaining, mL	mL	\N
3090	power_to_battery1_quantity_int32_mW	power_to_battery1	\N	power to battery1, mW	mW	\N
3091	battery1_converter_temperature_quantity_int32_ddeg_C	battery1_converter_temperature	\N	battery1 converter temperature, decidegrees C	ddeg_C	\N
3092	power_to_battery2_quantity_int32_mW	power_to_battery2	\N	power to battery2, mW	mW	\N
3093	battery2_converter_temperature_quantity_int32_ddeg_C	battery2_converter_temperature	\N	battery2 converter temperature, decidegrees C	ddeg_C	\N
3094	balance_of_plant_power_quantity_int32_mW	balance_of_plant_power	\N	balance of plant power, mW	mW	\N
3095	balance_of_plant_converter_temperature_quantity_int32_ddeg_C	balance_of_plant_converter_temperature	\N	balance of plant converter temperature, decidegrees C	ddeg_C	\N
3096	power_board_temperature_quantity_int32_ddeg_C	power_board_temperature	\N	power board temperature, decidegrees C	ddeg_C	\N
3097	control_board_temperature_quantity_int32_ddeg_C	control_board_temperature	\N	control board temperature, decidegrees C	ddeg_C	\N
3098	power_manager_status_quantity_int64_1	power_manager_status	\N	power manager status	1	\N
3099	power_manager_error_mask_quantity_int32_1	power_manager_error_mask	\N	power manager error mask	1	\N
3100	reformer_error_mask_quantity_int64_1	reformer_error_mask	\N	reformer error mask	1	\N
3101	fuel_cell_error_mask_quantity_int64_1	fuel_cell_error_mask	\N	fuel cell error mask	1	\N
3102	zplsc_timestamp_quantity_string_1	zplsc_timestamp	\N	Timestamp from the .raw file name	1	\N
3103	zplsc_transducer_depth_array_quantity_float32_m	zplsc_transducer_depth	\N	Transducer depth	m	\N
3104	zplsc_frequency_array_quantity_uint32_Hz	zplsc_frequency	\N	Frequency	Hz	\N
3105	zplsc_transmit_power_array_quantity_uint16_W	zplsc_transmit_power	\N	Transmit power	W	\N
3106	zplsc_pulse_length_array_quantity_float32_sec	zplsc_pulse_length	\N	Pulse length	sec	\N
3107	zplsc_bandwidth_array_quantity_float32_Hz	zplsc_bandwidth	\N	Bandwidth	Hz	\N
3108	zplsc_sample_interval_array_quantity_float32_sec	zplsc_sample_interval	\N	Sample interval	sec	\N
3109	zplsc_sound_velocity_array_quantity_float32_m_s_1	zplsc_sound_velocity	\N	Sound velocity	m s-1	\N
3110	zplsc_absorption_coeff_array_quantity_float32_dB_m_1	zplsc_absorption_coeff	\N	Absorption coefficient	dB m-1	\N
3111	zplsc_temperature_array_quantity_float32_deg_C	zplsc_temperature	\N	Temperature	deg_C	\N
3112	zplsc_echogram_array_quantity_string_1	zplsc_echogram	\N	Generated echogram file location	1	\N
3113	instrument_start_timestamp_quantity_string_1	instrument_start_timestamp	\N	Instrument Power On Timestamp, yyyy/mm/dd hh:mm:ss.sss	1	\N
3114	time_datacollection_quantity_float64_sec	time_datacollection	\N	Data collection start time	sec	\N
3115	v_num_datacollection_quantity_float32_1	v_num_datacollection	\N	Version number of FDCHP	1	\N
3116	status_datacollection_quantity_string_1	status_datacollection	\N	Status (WRAOCF)	1	\N
3117	wind_u_avg_quantity_float32_m_s_1	wind_u_avg	\N	Average wind speed, x-axis	m s-1	\N
3118	wind_v_avg_quantity_float32_m_s_1	wind_v_avg	\N	Average wind speed, y-axis	m s-1	\N
3119	wind_w_avg_quantity_float32_m_s_1	wind_w_avg	\N	Average wind speed, z-axis	m s-1	\N
3120	speed_of_sound_avg_quantity_float32_m_s_1	speed_of_sound_avg	\N	Speed of Sound	m s-1	\N
3121	wind_u_std_quantity_float32_m_s_1	wind_u_std	\N	Standard deviation of wind speed, x-axis	m s-1	\N
3122	wind_v_std_quantity_float32_m_s_1	wind_v_std	\N	Standard deviation of wind speed, y-axis	m s-1	\N
3123	wind_w_std_quantity_float32_m_s_1	wind_w_std	\N	Standard deviation of wind speed, z-axis	m s-1	\N
3124	speed_of_sound_std_quantity_float32_m_s_1	speed_of_sound_std	\N	Standard deviation of Speed of Sound	m s-1	\N
3125	wind_u_max_quantity_float32_m_s_1	wind_u_max	\N	Maximum of wind speed, x-axis	m s-1	\N
3126	wind_v_max_quantity_float32_m_s_1	wind_v_max	\N	Maximum of wind speed, y-axis	m s-1	\N
3127	wind_w_max_quantity_float32_m_s_1	wind_w_max	\N	Maximum of wind speed, z-axis	m s-1	\N
3128	speed_of_sound_max_quantity_float32_m_s_1	speed_of_sound_max	\N	Maximum of Speed of Sound	m s-1	\N
3129	wind_u_min_quantity_float32_m_s_1	wind_u_min	\N	Minimum of wind speed, x-axis	m s-1	\N
3130	wind_v_min_quantity_float32_m_s_1	wind_v_min	\N	Minimum of wind speed, y-axis	m s-1	\N
3131	wind_w_min_quantity_float32_m_s_1	wind_w_min	\N	Minimum of wind speed, z-axis	m s-1	\N
3132	speed_of_sound_min_quantity_float32_m_s_1	speed_of_sound_min	\N	Minimum of Speed of Sound	m s-1	\N
3133	x_accel_quantity_float32_m_s_2	x_accel	\N	Average observed acceleration, x axis	m s-2	\N
3134	y_accel_quantity_float32_m_s_2	y_accel	\N	Average observed acceleration, y axis	m s-2	\N
3135	z_accel_quantity_float32_m_s_2	z_accel	\N	Average observed acceleration, z axis	m s-2	\N
3136	x_accel_std_quantity_float32_m_s_2	x_accel_std	\N	Standard deviation of X Acceleration	m s-2	\N
3137	y_accel_std_quantity_float32_m_s_2	y_accel_std	\N	Standard deviation of Y Acceleration	m s-2	\N
3138	z_accel_std_quantity_float32_m_s_2	z_accel_std	\N	Standard deviation of Z Acceleration	m s-2	\N
3139	x_accel_max_quantity_float32_m_s_2	x_accel_max	\N	Maximum X Acceleration	m s-2	\N
3140	y_accel_max_quantity_float32_m_s_2	y_accel_max	\N	Maximum Y Acceleration	m s-2	\N
3141	z_accel_max_quantity_float32_m_s_2	z_accel_max	\N	Maximum Z Acceleration	m s-2	\N
3142	x_accel_min_quantity_float32_m_s_2	x_accel_min	\N	Minimum X Acceleration	m s-2	\N
3143	y_accel_min_quantity_float32_m_s_2	y_accel_min	\N	Minimum Y Acceleration	m s-2	\N
3144	z_accel_min_quantity_float32_m_s_2	z_accel_min	\N	Minimum Z Acceleration	m s-2	\N
3145	x_ang_rate_quantity_float32_rad_s_1	x_ang_rate	\N	Average observed angular rate, x-axis	rad s-1	\N
3146	y_ang_rate_quantity_float32_rad_s_1	y_ang_rate	\N	Average observed angular rate, y-axis	rad s-1	\N
3147	z_ang_rate_quantity_float32_rad_s_1	z_ang_rate	\N	Average observed angular rate, z-axis	rad s-1	\N
3148	x_ang_rate_std_quantity_float32_rad_s_1	x_ang_rate_std	\N	Standard deviation of X angular rate	rad s-1	\N
3149	y_ang_rate_std_quantity_float32_rad_s_1	y_ang_rate_std	\N	Standard deviation of Y angular rate	rad s-1	\N
3150	z_ang_rate_std_quantity_float32_rad_s_1	z_ang_rate_std	\N	Standard deviation of Z angular rate	rad s-1	\N
3151	x_ang_rate_max_quantity_float32_rad_s_1	x_ang_rate_max	\N	Maximum X angular rate	rad s-1	\N
3152	y_ang_rate_max_quantity_float32_rad_s_1	y_ang_rate_max	\N	Maximum Y angular rate	rad s-1	\N
3153	z_ang_rate_max_quantity_float32_rad_s_1	z_ang_rate_max	\N	Maximum Z angular rate	rad s-1	\N
3154	x_ang_rate_min_quantity_float32_rad_s_1	x_ang_rate_min	\N	Minimum X angular rate	rad s-1	\N
3155	y_ang_rate_min_quantity_float32_rad_s_1	y_ang_rate_min	\N	Minimum Y angular rate	rad s-1	\N
3156	z_ang_rate_min_quantity_float32_rad_s_1	z_ang_rate_min	\N	Minimum Z angular rate	rad s-1	\N
3157	heading_std_quantity_float32_rad	heading_std	\N	Standard deviation of Heading	rad	\N
3158	pitch_std_quantity_float32_rad	pitch_std	\N	Standard deviation of Pitch	rad	\N
3159	roll_std_quantity_float32_rad	roll_std	\N	Standard deviation of Roll	rad	\N
3160	heading_max_quantity_float32_rad	heading_max	\N	Maximum Heading	rad	\N
3161	pitch_max_quantity_float32_rad	pitch_max	\N	Maximum Pitch	rad	\N
3162	roll_max_quantity_float32_rad	roll_max	\N	Maximum Roll	rad	\N
3163	heading_min_quantity_float32_rad	heading_min	\N	Minimum Heading	rad	\N
3164	pitch_min_quantity_float32_rad	pitch_min	\N	Minimum Pitch	rad	\N
3165	roll_min_quantity_float32_rad	roll_min	\N	Minimum Roll	rad	\N
3166	u_corr_quantity_float32_m_s_1	u_corr	\N	Motion-corrected Northerly wind speed	m s-1	\N
3167	v_corr_quantity_float32_m_s_1	v_corr	\N	Motion-corrected Westerly wind speed	m s-1	\N
3168	w_corr_quantity_float32_m_s_1	w_corr	\N	Motion-corrected vertical wind speed	m s-1	\N
3169	u_corr_std_quantity_float32_m_s_1	u_corr_std	\N	Standard deviation of along-wind	m s-1	\N
3170	v_corr_std_quantity_float32_m_s_1	v_corr_std	\N	Standard deviation of cross-wind	m s-1	\N
3171	w_corr_std_quantity_float32_m_s_1	w_corr_std	\N	Standard deviation of vertical wind	m s-1	\N
3172	wind_speed_quantity_float32_m_s_1	wind_speed	\N	Motion-corrected wind speed relative to ground	m s-1	\N
3173	uw_momentum_flux_quantity_float32_m2_s_2	uw_momentum_flux	\N	Along-wind component of momentum flux	m2 s-2	\N
3174	vw_momentum_flux_quantity_float32_m2_s_2	vw_momentum_flux	\N	Cross-wind component of momentum flux	m2 s-2	\N
3175	buoyance_flux_quantity_float32_m_s_1_K	buoyance_flux	\N	Buoyancy Flux	m s-1 K	\N
3176	eng_wave_motion_quantity_float32_1	eng_wave_motion	\N	Approximate significant wave height	1	\N
3177	adcps_jln_eastward_earth_seawater_velocity_function_float32_m_s_1	adcps_jln_eastward_earth_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
3178	adcps_jln_northward_earth_seawater_velocity_function_float32_m_s_1	adcps_jln_northward_earth_seawater_velocity	\N	Northward Earth Sea Water Velocity, m s-1	m s-1	\N
3179	zplsc_channel_array_quantity_uint8_1	zplsc_channel	\N	Transducer channel number	1	\N
3180	adcps_jln_recovered_eastward_seawater_velocity_function_float32_m_s_1	adcps_jln_recovered_eastward_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
3181	adcps_jln_recovered_northward_seawater_velocity_function_float32_m_s_1	adcps_jln_recovered_northward_seawater_velocity	\N	Northward Sea Water Velocity, m s-1	m s-1	\N
3182	adcps_jln_recovered_eastward_beam_seawater_velocity_function_float32_m_s_1	adcps_jln_recovered_eastward_beam_seawater_velocity	\N	Eastward Sea Water Velocity, m s-1	m s-1	\N
3183	adcps_jln_recovered_northward_beam_seawater_velocity_function_float32_m_s_1	adcps_jln_recovered_northward_beam_seawater_velocity	\N	Northward Beam Sea Water Velocity, m s-1	m s-1	\N
3184	start_time_quantity_string_1	start_time	\N	Start Time	1	\N
3185	stop_time_quantity_string_1	stop_time	\N	Stop Time	1	\N
3186	acidity_quantity_float64_mmol/kg	acidity	\N	Acidity at 25 degrees Celsius, mmol/kg	mmol/kg	\N
3187	alkalinity_quantity_float64_mmol/kg	alkalinity	\N	Alkalinity, mmol/kg	mmol/kg	\N
3188	hydrogen_sulfide_concentration_quantity_float64_mmol/kg	hydrogen_sulfide_concentration	\N	Hydrogen Sulfide, mmol/kg	mmol/kg	\N
3189	silicon_concentration_quantity_float64_mmol/kg	silicon_concentration	\N	Silicon, mmol/kg	mmol/kg	\N
3190	ammonia_concentration_quantity_float64_mmol/kg	ammonia_concentration	\N	Ammonia, mmol/kg	mmol/kg	\N
3191	chloride_concentration_quantity_float64_mmol/kg	chloride_concentration	\N	Chloride, mmol/kg	mmol/kg	\N
3192	sulfate_concentration_quantity_float64_mmol/kg	sulfate_concentration	\N	Sulfate, mmol/kg	mmol/kg	\N
3193	sodium_concentration_quantity_float64_mmol/kg	sodium_concentration	\N	Sodium, mmol/kg	mmol/kg	\N
3194	potassium_concentration_quantity_float64_mmol/kg	potassium_concentration	\N	Potassium, mmol/kg	mmol/kg	\N
3195	magnesium_concentration_quantity_float64_mmol/kg	magnesium_concentration	\N	Magnesium, mmol/kg	mmol/kg	\N
3196	calcium_concentration_quantity_float64_mmol/kg	calcium_concentration	\N	Calcium, mmol/kg	mmol/kg	\N
3197	bromide_concentration_quantity_float64_umol/kg	bromide_concentration	\N	Bromide, umol/kg	umol/kg	\N
3198	iron_concentration_quantity_float64_umol/kg	iron_concentration	\N	Iron, umol/kg	umol/kg	\N
3199	manganese_concentration_quantity_float64_umol/kg	manganese_concentration	\N	Manganese, umol/kg	umol/kg	\N
3200	lithium_concentration_quantity_float64_umol/kg	lithium_concentration	\N	Lithium, umol/kg	umol/kg	\N
3201	strontium_icpaes_concentration_quantity_float64_umol/kg	strontium_icpaes_concentration	\N	Strontium/ICPAES, umol/kg	umol/kg	\N
3202	boron_concentration_quantity_float64_umol/kg	boron_concentration	\N	Boron, umol/kg	umol/kg	\N
3203	rubidium_concentration_quantity_float64_umol/kg	rubidium_concentration	\N	Rubidium, umol/kg	umol/kg	\N
3204	cesium_concentration_quantity_float64_nmol/kg	cesium_concentration	\N	Caesium, nmol/kg	nmol/kg	\N
3205	strontium_icpms_concentration_quantity_float64_nmol/kg	strontium_icpms_concentration	\N	Strontium/ICPMS, nmol/kg	nmol/kg	\N
3206	barium_concentration_quantity_float64_nmol/kg	barium_concentration	\N	Barium, nmol/kg	nmol/kg	\N
3207	cobalt_concentration_quantity_float64_nmol/kg	cobalt_concentration	\N	Cobalt, nmol/kg	nmol/kg	\N
3208	nickel_concentration_quantity_float64_nmol/kg	nickel_concentration	\N	Nickel, nmol/kg	nmol/kg	\N
3209	copper_concentration_quantity_float64_nmol/kg	copper_concentration	\N	Copper, nmol/kg	nmol/kg	\N
3210	zinc_concentration_quantity_float64_nmol/kg	zinc_concentration	\N	Zinc, nmol/kg	nmol/kg	\N
3211	molybdenum_concentration_quantity_float64_nmol/kg	molybdenum_concentration	\N	Molybdenum, nmol/kg	nmol/kg	\N
3212	silver_concentration_quantity_float64_nmol/kg	silver_concentration	\N	Silver, nmol/kg	nmol/kg	\N
3213	cadmium_concentration_quantity_float64_nmol/kg	cadmium_concentration	\N	Cadmium, nmol/kg	nmol/kg	\N
3214	titanium_concentration_quantity_float64_nmol/kg	titanium_concentration	\N	Titanium, nmol/kg	nmol/kg	\N
3215	aluminum_concentration_quantity_float64_nmol/kg	aluminum_concentration	\N	Aluminum, nmol/kg	nmol/kg	\N
3216	lead_concentration_quantity_float64_nmol/kg	lead_concentration	\N	Lead, nmol/kg	nmol/kg	\N
3217	vanadium_concentration_quantity_float64_nmol/kg	vanadium_concentration	\N	Vanadium, nmol/kg	nmol/kg	\N
3218	uranium_concentration_quantity_float64_nmol/kg	uranium_concentration	\N	Uranium, nmol/kg	nmol/kg	\N
3219	yttrium_concentration_quantity_float64_nmol/kg	yttrium_concentration	\N	Yttrium, nmol/kg	nmol/kg	\N
3220	gadolinium_concentration_quantity_float64_nmol/kg	gadolinium_concentration	\N	Gadolinium, nmol/kg	nmol/kg	\N
3221	volume_pumped_quantity_float64_mL	volume_pumped	\N	Volume Pumped, mL	mL	\N
3222	hyd_raw_quantity_float32_counts	hyd_raw	\N	Raw Hydrogen Count	counts	\N
3223	hyd_percent_quantity_float32_percentage	hyd_percent	\N	Hydrogen Percentage	percentage	\N
3224	ncbi_sequence_read_archive_url_quantity_string_1	ncbi_sequence_read_archive_url	\N	NCBI Sequence Read Archive        	1	\N
3225	fasta_url_quantity_string_1	fasta_url	\N	OOI Processed FASTA	1	\N
3226	vamps_url_quantity_string_1	vamps_url	\N	VAMPS Processed FASTA	1	\N
3227	tracking_id_quantity_string_1	tracking_id	\N	Tracking Id	1	\N
3228	sample_time_quantity_string_1	sample_time	\N	Sample Time	1	\N
3229	tracer_concentration_quantity_float64_g/L	tracer_concentration	\N	Tracer concentration, g/L	g/L	\N
3230	flow_rate_quantity_float64_cm/yr	flow_rate	\N	Flow Rate, cm/yr	cm/yr	\N
3231	ambient_temperature_quantity_float64_deg_C	ambient_temperature	\N	Ambient Temperature	deg C	\N
3232	barium_concentration_um_quantity_float64_uM	barium_concentration_um	\N	Barium Concentration, uM	uM	\N
3233	sulfur_concentration_quantity_float64_mM	sulfur_concentration	\N	Sulfure Concentration, mM	mM	\N
3234	strontium_concentration_quantity_float64_mM	strontium_concentration	\N	Strontium Concentration, mM	mM	\N
3235	tracer_percent_quantity_float64_percentage	tracer_percent	\N	Tracer percentage, %	percentage	\N
3236	auv_latitude_quantity_float64_deg	auv_latitude	\N	Latitude, Degrees	deg	\N
3237	auv_longitude_quantity_float64_deg	auv_longitude	\N	Longitude, Degrees	deg	\N
3238	altitude_quantity_float32_m	altitude	\N	Vehicle Altitude, meters	m	\N
3239	altitude_track_range_beam_1_quantity_float32_m	altitude_track_range_beam_1	\N	Altitude Track Range Beam 1. meters	m	\N
3240	altitude_track_range_beam_2_quantity_float32_m	altitude_track_range_beam_2	\N	Altitude Track Range Beam 2, meters	m	\N
3241	altitude_track_range_beam_3_quantity_float32_m	altitude_track_range_beam_3	\N	Altitude Track Range Beam 3, meters	m	\N
3242	altitude_track_range_beam_4_quantity_float32_m	altitude_track_range_beam_4	\N	Altitude Track Range Beam 4, meters	m	\N
3243	forward_velocity_quantity_float32_m_s_1	forward_velocity	\N	Forward Velocity, m/s	m s-1	\N
3244	starboard_velocity_quantity_float32_m_s_1	starboard_velocity	\N	Starboard Velocity, m/s	m s-1	\N
3245	vertical_velocity_quantity_float32_m_s_1	vertical_velocity	\N	Vertical Velocity, m/s	m s-1	\N
3246	adcpa_n_auv_error_velocity_quantity_float32_mm_s_1	adcpa_n_auv_error_velocity	\N	Error Velocity, mm s-1	mm s-1	\N
3247	binary_velocity_data_1_quantity_int16_mm_s_1	binary_velocity_data_1	\N	Binary Velocity Data 1, mm/s	mm s-1	\N
3248	binary_velocity_data_2_quantity_int16_mm_s_1	binary_velocity_data_2	\N	Binary Velocity Data 2, mm/s	mm s-1	\N
3249	binary_velocity_data_3_quantity_int16_mm_s_1	binary_velocity_data_3	\N	Binary Velocity Data 3, mm/s	mm s-1	\N
3250	binary_velocity_data_4_quantity_int16_mm_s_1	binary_velocity_data_4	\N	Binary Velocity Data 4, mm/s	mm s-1	\N
3251	coordinates_transformation_quantity_int16_1	coordinates_transformation	\N	Coordinates Transformation, mask	1	\N
3252	average_current_quantity_float32_m_s_1	average_current	\N	Average Current, m/s	m s-1	\N
3253	average_direction_quantity_float32_deg	average_direction	\N	Average Direction, Degrees	deg	\N
3254	mission_epoch_quantity_uint32_seconds_since_1970_01_01	mission_epoch	\N	mission time, unix / posix time	seconds since 1970-01-01	\N
3255	mission_time_quantity_uint32_milliseconds	mission_time	\N	mission time, ms	milliseconds	\N
3256	device_id_quantity_int8_1	device_id	\N	Device ID	1	\N
3257	device_count_quantity_int8_1	device_count	\N	Device Count	1	\N
3258	parameter_name_quantity_string_1	parameter_name	\N	Parameter Name	1	\N
3259	parameter_unit_quantity_string_1	parameter_unit	\N	Parameter Unit	1	\N
3260	parameter_id_quantity_uint8_1	parameter_id	\N	Parameter ID	1	\N
3261	eco_data_offset_quantity_uint8_1	eco_data_offset	\N	Eco Data Offset	1	\N
3262	html_plot_quantity_uint8_1	html_plot	\N	Html Plot	1	\N
3263	parameter_type_quantity_int8_1	parameter_type	\N	Parameter Type. 0 == Raw, 1 == MX+B (Linear)	1	\N
3264	mx_quantity_float32_1	mx	\N	Mx	1	\N
3265	b_quantity_float32_1	b	\N	B	1	\N
3266	sensor_name_quantity_string_1	sensor_name	\N	Sensor Name	1	\N
3267	device_count_quantity_int8_counts	device_count	\N	Number Of Devices, Counts	counts	\N
3268	version_quantity_int8_1	version	\N	Version	1	\N
3269	parameter_0_quantity_float32_1	parameter_0	\N	Parameter 0 Value	1	\N
3270	parameter_1_quantity_float32_1	parameter_1	\N	Parameter 1 Value	1	\N
3271	parameter_2_quantity_float32_1	parameter_2	\N	Parameter 2 Value	1	\N
3272	parameter_3_quantity_float32_1	parameter_3	\N	Parameter 3 Value	1	\N
3273	parameter_4_quantity_float32_1	parameter_4	\N	Parameter 4 Value	1	\N
3274	parameter_5_quantity_float32_1	parameter_5	\N	Parameter 5 Value	1	\N
3275	parameter_6_quantity_float32_1	parameter_6	\N	Parameter 6 Value	1	\N
3276	parameter_7_quantity_float32_1	parameter_7	\N	Parameter 7 Value	1	\N
3277	parameter_8_quantity_float32_1	parameter_8	\N	Parameter 8 Value	1	\N
3278	parameter_9_quantity_float32_1	parameter_9	\N	Parameter 9 Value	1	\N
3279	b_pot_quantity_float32_mV	b_pot	\N	b_pot, mV	mV	\N
3280	calculated_oxygen_concentration_quantity_float32_uM	calculated_oxygen_concentration	\N	Calculated dissolved oxygen concentration, uM	uM	\N
3281	calculated_oxygen_saturation_quantity_float32_%	calculated_oxygen_saturation	\N	Calculated oxygen saturation, Percent	%	\N
3282	external_temperature_quantity_float32_deg_c	external_temperature	\N	External temperature, Degrees Celsius	deg_c	\N
3283	ctdav_n_auv_conductivity_quantity_float32_mS_cm_1	ctdav_n_auv_conductivity	\N	Conductivity, mS/cm	mS cm-1	\N
3284	dissolved_oxygen_quantity_float32_ml_L_1	dissolved_oxygen	\N	Dissolved Oxygen, ml/L	ml L-1	\N
3285	powered_on_quantity_uint8_1	powered_on	\N	Powered On Indicator, 0 = Off, 1 = On.	1	\N
3286	biospherical_mobile_sensor_voltage_quantity_float32_V	biospherical_mobile_sensor_voltage	\N	Sensor Voltage, V	V	\N
3287	sensor_temperature_quantity_float32_deg_C	sensor_temperature	\N	Sensor Temperature, Degrees Celsius	deg_C	\N
3288	parad_n_auv_supply_voltage_quantity_float32_V	parad_n_auv_supply_voltage	\N	Supply Voltage, V	V	\N
3289	month_quantity_uint8_month	month	\N	Month	month	\N
3290	day_quantity_uint8_day	day	\N	Day	day	\N
3291	hour_quantity_uint8_hour	hour	\N	Hour	hour	\N
3292	minute_quantity_uint8_minute	minute	\N	Minute	minute	\N
3293	second_quantity_uint8_second	second	\N	Second	second	\N
3294	millisecond_quantity_uint16_millisecond	millisecond	\N	millisecond	millisecond	\N
3295	fdchp_wind_x_quantity_int16_cm_s_1	fdchp_wind_x	\N	Wind speed, x-axis, cm/s	cm s-1	\N
3296	fdchp_wind_y_quantity_int16_cm_s_1	fdchp_wind_y	\N	Wind speed, y-axis, cm/s	cm s-1	\N
3297	fdchp_wind_z_quantity_int16_cm_s_1	fdchp_wind_z	\N	Wind speed, z-axis, cm/s	cm s-1	\N
3298	fdchp_speed_of_sound_sonic_quantity_uint16_cm_s_1	fdchp_speed_of_sound_sonic	\N	Sonic speed of sound, cm/s	cm s-1	\N
3299	fdchp_x_accel_g_quantity_float32_g0	fdchp_x_accel_g	\N	Observed acceleration, x axis, g0	g0	\N
3300	fdchp_y_accel_g_quantity_float32_g0	fdchp_y_accel_g	\N	Observed acceleration, y axis, g0	g0	\N
3301	fdchp_z_accel_g_quantity_float32_g0	fdchp_z_accel_g	\N	Observed acceleration, z axis, g0	g0	\N
3302	fdchp_roll_quantity_float32_deg	fdchp_roll	\N	Instrument Roll, degrees	deg	\N
3303	fdchp_pitch_quantity_float32_deg	fdchp_pitch	\N	Instrument Pitch, degrees	deg	\N
3304	fdchp_heading_quantity_float32_deg	fdchp_heading	\N	Instrument Heading, degrees	deg	\N
3305	fdchp_status_1_quantity_uint8_1	fdchp_status_1	\N	fdchp status 1	1	\N
3306	fdchp_status_2_quantity_uint8_1	fdchp_status_2	\N	fdchp status 2	1	\N
3307	vel3d_a_eastward_velocity_function_float32_m_s_1	vel3d_a_eastward_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
3308	vel3d_a_northward_velocity_function_float32_m_s_1	vel3d_a_northward_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
3309	vel3d_a_upward_velocity_ascending_function_float32_m_s_1	vel3d_a_upward_velocity_ascending	\N	Upward Turbulent Velocity - Ascending, m s-1	m s-1	\N
3310	vel3d_a_upward_velocity_descending_function_float32_m_s_1	vel3d_a_upward_velocity_descending	\N	Upward Turbulent Velocity - Ascending, m s-1	m s-1	\N
3311	vel3d_l_eastward_velocity_function_float32_m_s_1	vel3d_l_eastward_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
3312	vel3d_l_northward_velocity_function_float32_m_s_1	vel3d_l_northward_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
3313	vel3d_l_upward_velocity_ascending_function_float32_m_s_1	vel3d_l_upward_velocity_ascending	\N	Upward Turbulent Velocity - Ascending, m s-1	m s-1	\N
3314	vel3d_l_upward_velocity_descending_function_float32_m_s_1	vel3d_l_upward_velocity_descending	\N	Upward Turbulent Velocity - Ascending, m s-1	m s-1	\N
3315	range_setting_quantity_int16_m	range_setting	\N	Range Setting, m	m	\N
3316	auv_state_voltage_quantity_float32_V	auv_state_voltage	\N	Voltage, V	V	\N
3317	look_down_angle_quantity_float32_degree	look_down_angle	\N	Look Down Angle, degree	degree	\N
3318	sonar_range_quantity_float32_m	sonar_range	\N	Sonar Range, m	m	\N
3319	roll_deg_quantity_float32_degree	roll_deg	\N	Roll, degree	degree	\N
3320	sonar_range_minimum_quantity_float32_m	sonar_range_minimum	\N	Sonar Range Minimum, m	m	\N
3321	estimated_range_quantity_float32_m_s_1	estimated_range	\N	Estimated Range, m/s	m s-1	\N
3322	estimated_rate_quantity_float32_m_s_1	estimated_rate	\N	Estimated Rate, m/s	m s-1	\N
3323	obstacle_range_rate_minimum_quantity_float32_m	obstacle_range_rate_minimum	\N	Obstacle Range Rate Minimum, m	m	\N
3324	obstacle_range_maximum_quantity_float32_m	obstacle_range_maximum	\N	Obstacle Range Maximum, m	m	\N
3325	obstacle_range_critical_quantity_float32_m_s_1	obstacle_range_critical	\N	Obstacle Range Critical, m/s	m s-1	\N
3326	obstacle_range_rate_critical_quantity_float32_m_s_1	obstacle_range_rate_critical	\N	Obstacle Range Rate Critical, m/s	m s-1	\N
3327	pings_quantity_uint32_counts	pings	\N	Pings, counts	counts	\N
3328	status_quantity_uint8_mask	status	\N	Status, mask	mask	\N
3329	median_filter_range_quantity_float32_m	median_filter_range	\N	Median Filter Range, m	m	\N
3330	compass_true_heading_quantity_float32_degree	compass_true_heading	\N	Compass True Heading, degree	degree	\N
3331	auv_speed_of_sound_quantity_float32_m_s_1	auv_speed_of_sound	\N	Auv Speed Of Sound, m/s	m s-1	\N
3332	reserved_quantity_float32_1	reserved	\N	Reserved	1	\N
3333	range_minimum_quantity_float32_m	range_minimum	\N	Range Minimum, m	m	\N
3334	range_maximum_quantity_float32_m	range_maximum	\N	Range Maximum, m	m	\N
3335	latency_quantity_float32_ms	latency	\N	Latency, ms	ms	\N
3336	x_angle_quantity_float32_degree	x_angle	\N	X Angle, degree	degree	\N
3337	y_angle_quantity_float32_degree	y_angle	\N	Y Angle, degree	degree	\N
3338	range_quantity_float32_m	range	\N	Range, m	m	\N
3339	gain_1_quantity_int16_decibel	gain_1	\N	Gain 1, decibel	decibel	\N
3340	gain_2_quantity_int16_decibel	gain_2	\N	Gain 2, decibel	decibel	\N
3341	array_sound_speed_quantity_int16_m_s_1	array_sound_speed	\N	Array Sound Speed, m/s	m s-1	\N
3342	reason_quantity_int16_mask	reason	\N	Reason, mask	mask	\N
3343	x_center_quantity_int8_degree	x_center	\N	X Center, degree	degree	\N
3344	y_center_quantity_int8_degree	y_center	\N	Y Center, degree	degree	\N
3345	inband_snr_quantity_uint8_decibel	inband_snr	\N	Inband Snr, decibel	decibel	\N
3346	outband_snr_quantity_uint8_decible	outband_snr	\N	Outband Snr, decible	decible	\N
3347	transponder_table_index_quantity_uint8_counts	transponder_table_index	\N	Transponder Table Index, counts	counts	\N
3348	fin_count_quantity_int8_counts	fin_count	\N	Fin Count, counts	counts	\N
3349	fin_pitch_position_quantity_int8_percentage	fin_pitch_position	\N	Pitch Position, percentage	percentage	\N
3350	fin_rudder_position_quantity_int8_percentage	fin_rudder_position	\N	Rudder Position, percentage	percentage	\N
3351	fin_roll_position_quantity_int8_percentage	fin_roll_position	\N	Roll Position, percentage	percentage	\N
3352	fin_pitch_command_quantity_float32_degree	fin_pitch_command	\N	Pitch Command, degree	degree	\N
3353	fin_rudder_command_quantity_float32_degree	fin_rudder_command	\N	Rudder Command, degree	degree	\N
3354	fin_roll_command_quantity_float32_degree	fin_roll_command	\N	Roll Command, degree	degree	\N
3355	fin_command_data_1_quantity_float32_degree	fin_command_data_1	\N	Command Data 1, degree	degree	\N
3356	fin_position_data_1_quantity_float32_percentage	fin_position_data_1	\N	Position Data 1, percentage	percentage	\N
3357	fin_command_data_2_quantity_float32_degree	fin_command_data_2	\N	Command Data 2, degree	degree	\N
3358	fin_position_data_2_quantity_float32_percentage	fin_position_data_2	\N	Position Data 2, percentage	percentage	\N
3359	fin_command_data_3_quantity_float32_degree	fin_command_data_3	\N	Command Data 3, degree	degree	\N
3360	fin_position_data_3_quantity_float32_percentage	fin_position_data_3	\N	Position Data 3, percentage	percentage	\N
3361	fin_command_data_4_quantity_float32_degree	fin_command_data_4	\N	Command Data 4, degree	degree	\N
3362	fin_position_data_4_quantity_float32_percentage	fin_position_data_4	\N	Position Data 4, percentage	percentage	\N
3363	fin_command_data_5_quantity_float32_degree	fin_command_data_5	\N	Command Data 5, degree	degree	\N
3364	fin_position_data_5_quantity_float32_percentage	fin_position_data_5	\N	Position Data 5, percentage	percentage	\N
3365	fin_command_data_6_quantity_float32_degree	fin_command_data_6	\N	Command Data 6, degree	degree	\N
3366	fin_position_data_6_quantity_float32_percentage	fin_position_data_6	\N	Position Data 6, percentage	percentage	\N
3367	fin_yaw_translation_command_quantity_float32_degree	fin_yaw_translation_command	\N	Yaw Translation Command, degree	degree	\N
3368	fin_depth_translation_command_quantity_float32_degree	fin_depth_translation_command	\N	Depth Translation Command, degree	degree	\N
3369	fin_yaw_translation_position_quantity_int8_percentage	fin_yaw_translation_position	\N	Yaw Translation Position, percentage	percentage	\N
3370	fin_depth_translation_position_quantity_int8_percentage	fin_depth_translation_position	\N	Depth Translation Position, percentage	percentage	\N
3371	board_voltage_quantity_float32_V	board_voltage	\N	Board Voltage, V	V	\N
3372	status_quantity_uint16_mask	status	\N	Status, mask	mask	\N
3373	descent_status_quantity_int8_counts	descent_status	\N	Descent Status, counts	counts	\N
3374	ascent_status_quantity_int8_counts	ascent_status	\N	Ascent Status, counts	counts	\N
3375	pickup_status_quantity_int8_counts	pickup_status	\N	Pickup Status, counts	counts	\N
3376	descent_continuity_quantity_uint8_counts	descent_continuity	\N	Descent Continuity, counts	counts	\N
3377	ascent_continuity_quantity_uint8_counts	ascent_continuity	\N	Ascent Continuity, counts	counts	\N
3378	pickup_continuity_quantity_uint8_counts	pickup_continuity	\N	Pickup Continuity, counts	counts	\N
3379	secondary_status_quantity_uint32_mask	secondary_status	\N	Secondary Status, mask	mask	\N
3380	raw_value_quantity_int16_counts	raw_value	\N	Raw Value, counts	counts	\N
3381	oil_level_quantity_float32_percentage	oil_level	\N	Oil Level, percentage	percentage	\N
3382	oil_location_quantity_uint8_1	oil_location	\N	Oil Location, 1	1	\N
3383	flags_quantity_int8_mask	flags	\N	Flags, mask	mask	\N
3384	battery_index_quantity_int8_counts	battery_index	\N	Battery Index, counts	counts	\N
3385	battery_count_quantity_int8_counts	battery_count	\N	Battery Count, counts	counts	\N
3386	address_mask_quantity_int8_mask	address_mask	\N	Address Mask, mask	mask	\N
3387	smart_battery_voltage_quantity_uint16_mV	smart_battery_voltage	\N	Voltage, mV	mV	\N
3388	end_of_discharge_quantity_int16_mV	end_of_discharge	\N	End Of Discharge, mV	mV	\N
3389	average_current_quantity_int16_mA	average_current	\N	Average Current, mA	mA	\N
3390	temperature_one_tenth_quantity_uint16_deg_K	temperature_one_tenth	\N	Temperature One Tenth, deg_K	deg_K	\N
3391	full_charge_capacity_quantity_uint16_mA_h_1	full_charge_capacity	\N	Full Charge Capacity, mA/h	mA h-1	\N
3392	remaining_capacity_quantity_uint16_mA_h_1	remaining_capacity	\N	Remaining Capacity, mA/h	mA h-1	\N
3393	desired_charge_rate_quantity_uint16_mA	desired_charge_rate	\N	Desired Charge Rate, mA	mA	\N
3394	serial_quantity_uint16_counts	serial	\N	Serial, counts	counts	\N
3395	battery_status_quantity_uint16_mask	battery_status	\N	Battery Status, mask	mask	\N
3396	battery_flags_quantity_uint16_mask	battery_flags	\N	Battery Flags, mask	mask	\N
3397	cycle_count_quantity_uint16_counts	cycle_count	\N	Cycle Count, counts	counts	\N
3398	available_power_quantity_float32_watt	available_power	\N	Available Power, watt	watt	\N
3399	auv_temperature_quantity_float32_deg_C	auv_temperature	\N	Auv Temperature, deg_C	deg_C	\N
3400	pressure_mbar_quantity_float32_mBar	pressure_mbar	\N	Pressure, mBar	mBar	\N
3401	pic_charge_value_quantity_uint8_counts	pic_charge_value	\N	Pic Charge Value, counts	counts	\N
3402	pic_balance_enabled_quantity_uint8_mask	pic_balance_enabled	\N	Pic Balance Enabled, mask	mask	\N
3403	pic_fet_state_quantity_uint8_mask	pic_fet_state	\N	Pic Fet State, mask	mask	\N
3404	pic_faults_quantity_uint8_mask	pic_faults	\N	Pic Faults, mask	mask	\N
3405	pic_cell_voltage_1_quantity_uint16_V	pic_cell_voltage_1	\N	Pic Cell Voltage 1, Volts	V	\N
3406	pic_cell_voltage_2_quantity_uint16_V	pic_cell_voltage_2	\N	Pic Cell Voltage 2, Volts	V	\N
3407	pic_cell_voltage_3_quantity_uint16_V	pic_cell_voltage_3	\N	Pic Cell Voltage 3, Volts	V	\N
3408	pic_cell_voltage_4_quantity_uint16_V	pic_cell_voltage_4	\N	Pic Cell Voltage 4, Volts	V	\N
3409	pic_cell_voltage_5_quantity_uint16_V	pic_cell_voltage_5	\N	Pic Cell Voltage 5, Volts	V	\N
3410	pic_cell_voltage_6_quantity_uint16_V	pic_cell_voltage_6	\N	Pic Cell Voltage 6, Volts	V	\N
3411	pic_cell_voltage_7_quantity_uint16_V	pic_cell_voltage_7	\N	Pic Cell Voltage 7, Volts	V	\N
3412	battery_temperature_quantity_float32_deg_K	battery_temperature	\N	Battery Temperature, Degrees Kelvin	deg_K	\N
3413	transponder_table_index_1_quantity_int8_counts	transponder_table_index_1	\N	Transponder Table Index 1, counts	counts	\N
3414	transponder_table_index_2_quantity_int8_counts	transponder_table_index_2	\N	Transponder Table Index 2, counts	counts	\N
3415	inband_channel_1_snr_quantity_uint8_decibel	inband_channel_1_snr	\N	Inband Channel 1 Snr, decibel	decibel	\N
3416	inband_channel_2_snr_quantity_uint8_decibel	inband_channel_2_snr	\N	Inband Channel 2 Snr, decibel	decibel	\N
3417	interrogate_channel_1_snr_quantity_int8_decibel	interrogate_channel_1_snr	\N	Interrogate Channel 1 Snr, decibel	decibel	\N
3418	interrogate_channel_2_snr_quantity_int8_decibel	interrogate_channel_2_snr	\N	Interrogate Channel 2 Snr, decibel	decibel	\N
3419	receive_channel_1_quantity_int8_counts	receive_channel_1	\N	Receive Channel 1, counts	counts	\N
3420	receive_channel_2_quantity_int8_counts	receive_channel_2	\N	Receive Channel 2, counts	counts	\N
3421	range_1_quantity_float32_m	range_1	\N	Range 1, m	m	\N
3422	range_2_quantity_float32_m	range_2	\N	Range 2, m	m	\N
3423	reply_age_1_quantity_uint32_ms	reply_age_1	\N	Reply Age 1, ms	ms	\N
3424	reply_age_2_quantity_uint32_ms	reply_age_2	\N	Reply Age 2, ms	ms	\N
3425	fail_flag_quantity_uint16_mask	fail_flag	\N	Fail Flag, mask	mask	\N
3426	received_bits_quantity_int8_mask	received_bits	\N	Received Bits, mask	mask	\N
3427	outband_channel_1_snr_quantity_uint8_decibel	outband_channel_1_snr	\N	Outband Channel 1 Snr, decibel	decibel	\N
3428	outband_channel_2_snr_quantity_uint8_decibel	outband_channel_2_snr	\N	Outband Channel 2 Snr, decibel	decibel	\N
3429	filename_quantity_string_1	filename	\N	Filename	1	\N
3430	line_quantity_int16_counts	line	\N	Line, counts	counts	\N
3431	message_quantity_string_1	message	\N	Message	1	\N
3432	software_version_quantity_uint8_counts	software_version	\N	Software Version, counts	counts	\N
3433	heading_rate_quantity_float32_degree	heading_rate	\N	Heading Rate, degree	degree	\N
3434	depth_goal_quantity_float32_m	depth_goal	\N	Depth Goal, m	m	\N
3435	obs_quantity_float32_1	obs	\N	Obs	1	\N
3436	auv_current_quantity_float32_A	auv_current	\N	Current, Amperes	A	\N
3437	gfi_quantity_float32_percentage	gfi	\N	GFI, percentage	percentage	\N
3438	pitch_deg_quantity_float32_degree	pitch_deg	\N	Pitch, degree	degree	\N
3439	pitch_goal_quantity_float32_degree	pitch_goal	\N	Pitch Goal, degree	degree	\N
3440	thruster_quantity_int16_rpm	thruster	\N	Thruster, rpm	rpm	\N
3441	thruster_goal_quantity_int16_rpm	thruster_goal	\N	Thruster Goal, rpm	rpm	\N
3442	heading_goal_quantity_float32_degree	heading_goal	\N	Heading Goal, degree	degree	\N
3443	days_since_1970_quantity_uint16_counts	days_since_1970	\N	Days Since 1970, counts	counts	\N
3444	dr_latitude_quantity_float32_degree	dr_latitude	\N	Dr Latitude, degree	degree	\N
3445	dr_longitude_quantity_float32_degree	dr_longitude	\N	Dr Longitude, degree	degree	\N
3446	goal_latitude_quantity_float32_degree	goal_latitude	\N	Goal Latitude, degree	degree	\N
3447	goal_longitude_quantity_float32_degree	goal_longitude	\N	Goal Longitude, degree	degree	\N
3448	estimated_velocity_quantity_float32_m_s_1	estimated_velocity	\N	Estimated Velocity, m/s	m s-1	\N
3449	heading_offset_quantity_float32_degree	heading_offset	\N	Heading Offset, degree	degree	\N
3450	flags_quantity_uint16_mask	flags	\N	Flags, mask	mask	\N
3451	thruster_command_quantity_int8_counts	thruster_command	\N	Thruster Command, counts	counts	\N
3452	pitch_command_quantity_int8_counts	pitch_command	\N	Pitch Command, counts	counts	\N
3453	rudder_command_quantity_int8_counts	rudder_command	\N	Rudder Command, counts	counts	\N
3454	pitch_fin_position_quantity_int8_counts	pitch_fin_position	\N	Pitch Fin Position, counts	counts	\N
3455	rudder_fin_position_quantity_int8_counts	rudder_fin_position	\N	Rudder Fin Position, counts	counts	\N
3456	total_objectives_quantity_uint8_counts	total_objectives	\N	Total Objectives, counts	counts	\N
3457	current_objective_quantity_uint8_counts	current_objective	\N	Current Objective, counts	counts	\N
3458	cpu_usage_quantity_uint8_percentage	cpu_usage	\N	Cpu Usage, percentage	percentage	\N
3459	objective_index_quantity_uint8_counts	objective_index	\N	Objective Index, counts	counts	\N
3460	leg_number_quantity_uint16_counts	leg_number	\N	Leg Number, counts	counts	\N
3461	spare_slider_quantity_float32_counts	spare_slider	\N	Spare Slider, counts	counts	\N
3462	roll_rate_quantity_float32_degree_s_1	roll_rate	\N	Roll Rate, degree/s	degree s-1	\N
3463	pitch_rate_quantity_float32_degree_s_1	pitch_rate	\N	Pitch Rate, degree/s	degree s-1	\N
3464	faults_quantity_uint32_mask	faults	\N	Faults, mask	mask	\N
3465	navigation_mode_quantity_uint8_1	navigation_mode	\N	Navigation Mode, 1	1	\N
3466	secondary_faults_quantity_uint16_mask	secondary_faults	\N	Secondary Faults, mask	mask	\N
3467	sample_time_quantity_float64_1	sample_time	\N	Sample Time, <hours>.<decimated seconds>	1	\N
3468	nutnr_spectral_avg_last_dark_quantity_uint16_1	nutnr_spectral_avg_last_dark	\N	Spectral average of the last dark frame	1	\N
3469	lamp_state_category_uint8_str_uint8_1	lamp_state	\N	State of the lamp, on or off	1	\N
3470	lamp_time_cumulative_quantity_uint32_s	lamp_time_cumulative	\N	Cumulative Lamp Time, seconds	s	\N
3471	ctdbp_no_seawater_pressure_function_float32_dbar	ctdbp_no_seawater_pressure	\N	Sea Water Pressure, dbar	dbar	\N
3472	ctdbp_no_seawater_conductivity_function_float32_S_m_1	ctdbp_no_seawater_conductivity	\N	Sea Water Conductivity, S m-1	S m-1	\N
3473	ctdbp_no_practical_salinity_function_float32_1	ctdbp_no_practical_salinity	\N	Sea Water Practical Salinity	1	\N
3474	ctdbp_no_seawater_density_function_float32_kg_m_3	ctdbp_no_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
3475	ctdbp_no_abs_oxygen_function_float32_umol_kg_1	ctdbp_no_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3476	velpt_j_eastward_velocity_function_float32_m_s_1	velpt_j_eastward_velocity	\N	Eastward Turbulent Velocity, m s-1	m s-1	\N
3477	velpt_j_northward_velocity_function_float32_m_s_1	velpt_j_northward_velocity	\N	Northward Turbulent Velocity, m s-1	m s-1	\N
3478	velpt_j_upward_velocity_function_float32_m_s_1	velpt_j_upward_velocity	\N	Upward Turbulent Velocity, m s-1	m s-1	\N
3479	botsflu_time15s_function_float32_sec_since_01_01_1900	botsflu_time15s	\N	TIME15S-AUX, sec since 01-01-1900	sec since 01-01-1900	\N
3480	botsflu_meanpres_function_float32_psi	botsflu_meanpres	\N	BOTSFLU-MEANPRES_L2, psi	psi	\N
3481	botsflu_meandepth_function_float32_m	botsflu_meandepth	\N	BOTSFLU-MEANDEPTH_L2, m	m	\N
3482	botsflu_5minrate_function_float32_cm_min_1	botsflu_5minrate	\N	BOTSFLU-5MINRATE_L2, cm/min	cm min-1	\N
3483	botsflu_10minrate_function_float32_cm_hr_1	botsflu_10minrate	\N	BOTSFLU-10MINRATE_L2, cm/hr	cm hr-1	\N
3484	botsflu_time24h_function_float32_sec_since_01_01_1900	botsflu_time24h	\N	TIME24H-AUX, sec since 01-01-1900	sec since 01-01-1900	\N
3485	botsflu_daydepth_function_float32_m	botsflu_daydepth	\N	BOTSFLU-DAYDEPTH_L2, m	m	\N
3486	botsflu_4wkrate_function_float32_cm_yr_1	botsflu_4wkrate	\N	BOTSFLU-4WKRATE_L2, cm/yr	cm yr-1	\N
3487	botsflu_8wkrate_function_float32_cm_yr_1	botsflu_8wkrate	\N	BOTSFLU-8WKRATE_L2, cm/yr	cm yr-1	\N
3488	botsflu_predtide_function_float32_m	botsflu_predtide	\N	BOTSFLU-PREDTIDE_L2, m	m	\N
3489	dosta_abcdjm_sio_abs_oxygen_function_float32_umol_kg_1	dosta_abcdjm_sio_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3490	ctdpf_ckl_mmp_cds_seawater_conductivity_function_float32_S_m_1	ctdpf_ckl_mmp_cds_seawater_conductivity	\N	Sea Water Conductivity, S m-1	S m-1	\N
3491	ctdpf_ckl_mmp_cds_water_pracsal_function_float32_1	ctdpf_ckl_mmp_cds_water_pracsal	\N	Practical Salinity (seawater salinity, PSS-78) [unitless]	1	\N
3492	ctdpf_ckl_mmp_cds_seawater_density_function_float32_kg_m_3	ctdpf_ckl_mmp_cds_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
3493	water_velocity_forward_array_quantity_int16_mm_s_1	water_velocity_forward	\N	Water Velocity Forward, mm/s	mm s-1	\N
3494	water_velocity_starboard_array_quantity_int16_mm_s_1	water_velocity_starboard	\N	Water Velocity Starboard, mm/s	mm s-1	\N
3495	water_velocity_vertical_array_quantity_int16_mm_s_1	water_velocity_vertical	\N	Water Velocity Vertical, mm/s	mm s-1	\N
3496	bt_forward_velocity_quantity_int16_mm_s_1	bt_forward_velocity	\N	Bt Forward Velocity, mm/s	mm s-1	\N
3497	bt_starboard_velocity_quantity_int16_mm_s_1	bt_starboard_velocity	\N	Bt Starboard Velocity, mm/s	mm s-1	\N
3498	bt_vertical_velocity_quantity_int16_mm_s_1	bt_vertical_velocity	\N	Bt Vertical Velocity, mm/s	mm s-1	\N
3499	bt_forward_ref_layer_velocity_quantity_int16_mm_s_1	bt_forward_ref_layer_velocity	\N	Bt Forward Ref Layer Velocity, mm/s	mm s-1	\N
3500	bt_starboard_ref_layer_velocity_quantity_int16_mm_s_1	bt_starboard_ref_layer_velocity	\N	Bt Starboard Ref Layer Velocity, mm/s	mm s-1	\N
3501	bt_vertical_ref_layer_velocity_quantity_int16_mm_s_1	bt_vertical_ref_layer_velocity	\N	Bt Vertical Ref Layer Velocity, mm/s	mm s-1	\N
3502	ctdmo_imodem_seawater_pressure_function_float32_dbar	ctdmo_imodem_seawater_pressure	\N	Sea Water Pressure, dBar	dbar	\N
3503	ctdmo_imodem_practical_salinity_function_float32_1	ctdmo_imodem_practical_salinity	\N	Practical Salinity (seawater salinity, PSS-78) [unitless]	1	\N
3504	ctdmo_imodem_seawater_density_function_float32_kg_m_3	ctdmo_imodem_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
3505	dosta_abcdjm_dcl_metbk_abs_oxygen_function_float32_umol_kg_1	dosta_abcdjm_dcl_metbk_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3506	dosta_abcdjm_dcl_ctdbp_abs_oxygen_function_float32_umol_kg_1	dosta_abcdjm_dcl_ctdbp_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3507	flort_d_dcl_metbk_bback_total_function_float32_m_1	flort_d_dcl_metbk_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
3508	flort_d_dcl_metbk_scat_seawater_function_float32_m_1	flort_d_dcl_metbk_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
3509	flort_d_dcl_ctdbp_bback_total_function_float32_m_1	flort_d_dcl_ctdbp_bback_total	\N	Total Optical Backscatter (FLUBSCT_L2) [m-1]	m-1	\N
3510	flort_d_dcl_ctdbp_scat_seawater_function_float32_m_1	flort_d_dcl_ctdbp_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
3511	optaa_dj_dcl_metbk_beam_attenuation_function_float32_m_1	optaa_dj_dcl_metbk_beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
3512	optaa_dj_dcl_metbk_optical_absorption_function_float32_m_1	optaa_dj_dcl_metbk_optical_absorption	\N	Optical Absorption, m-1	m-1	\N
3513	optaa_dj_dcl_ctdbp_beam_attenuation_function_float32_m_1	optaa_dj_dcl_ctdbp_beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
3514	optaa_dj_dcl_ctdbp_optical_absorption_function_float32_m_1	optaa_dj_dcl_ctdbp_optical_absorption	\N	Optical Absorption, m-1	m-1	\N
3515	phsen_abcdef_signal_intensity_434_function_float32_counts	phsen_abcdef_signal_intensity_434	\N	Signal Intensity at 434 nm, counts	counts	\N
3516	phsen_abcdef_signal_intensity_578_function_float32_counts	phsen_abcdef_signal_intensity_578	\N	Signal Intensity at 578 nm, counts	counts	\N
3517	dosta_abcdjm_mmp_cds_abs_oxygen_function_float32_umol_kg_1	dosta_abcdjm_mmp_cds_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3518	winch_date_quantity_string_1	winch_date	\N	Winch's Date, YYYY-MM-DD	1	\N
3519	winch_time_quantity_string_1	winch_time	\N	Winch's Time, HH-MM-SS.SSS	1	\N
3520	winch_state_quantity_string_1	winch_state	\N	Winch's State	1	\N
3521	winch_speed_quantity_int32_cm_s_1	winch_speed	\N	Winch's Speed, cm/sec	cm s-1	\N
3522	winch_payout_quantity_int32_cm	winch_payout	\N	Winch's Payout, cm	cm	\N
3523	winch_current_draw_quantity_float32_A	winch_current_draw	\N	Winch's Current Draw, amp	A	\N
3524	sensor_current_draw_quantity_float32_A	sensor_current_draw	\N	Sensor's Current Draw, amp	A	\N
3525	winch_status_quantity_string_1	winch_status	\N	Winch's Status	1	\N
3526	sci_suna_timestamp_quantity_float64_seconds_since_1970_01_01	sci_suna_timestamp	\N	Timestamp of sample, seconds since 1970-01-01	seconds since 1970-01-01	\N
3527	sci_suna_record_offset_quantity_uint32_B	sci_suna_record_offset	\N	message byte count for open disk file, bytes	B	\N
3528	sci_suna_nitrate_um_quantity_float32_µmol/L	sci_suna_nitrate_um	\N	Nitrate concentration, uMol/L	µmol/L	\N
3529	sci_suna_nitrate_mg_quantity_float32_mg/L	sci_suna_nitrate_mg	\N	Nitrate concentration, mg/L	mg/L	\N
3530	dpc_ctd_seawater_conductivity_function_float32_S_m_1	dpc_ctd_seawater_conductivity	\N	Sea Water Conductivity, S m-1	S m-1	\N
3531	dpc_ctd_water_pracsal_function_float32_1	dpc_ctd_water_pracsal	\N	Practical Salinity (seawater salinity, PSS-78) [unitless]	1	\N
3532	dpc_ctd_seawater_density_function_float32_kg_m_3	dpc_ctd_seawater_density	\N	Sea Water Density, kg m-3	kg m-3	\N
3533	dpc_optode_abs_oxygen_function_float32_umol_kg_1	dpc_optode_abs_oxygen	\N	Salinity Corrected Dissolved Oxygen Concentration, umol/kg	umol kg-1	\N
3534	dpc_acs_beam_attenuation_function_float32_m_1	dpc_acs_beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
3535	dpc_acs_optical_absorption_function_float32_m_1	dpc_acs_optical_absorption	\N	Optical Absorption, m-1	m-1	\N
3536	nutnr_j_cspp_temp_sal_corrected_nitrate_function_float32_uMol_L_1	nutnr_j_cspp_temp_sal_corrected_nitrate	\N	Temperature Salinity Corrected Nitrate	uMol L-1	\N
3537	optaa_ac_mmp_cds_beam_attenuation_function_float32_m_1	optaa_ac_mmp_cds_beam_attenuation	\N	Beam Attenuation, m-1	m-1	\N
3538	optaa_ac_mmp_cds_optical_absorption_function_float32_m_1	optaa_ac_mmp_cds_optical_absorption	\N	Optical Absorption, m-1	m-1	\N
3539	flntu_x_mmp_cds_scat_seawater_function_float32_m_1	flntu_x_mmp_cds_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
3540	fdchp_a_tmpatur_function_float32_deg_C	fdchp_a_tmpatur	\N	Sonic Temperature [degrees Celsius]	deg_C	\N
3541	fdchp_a_windtur_north_function_float32_m_s_1	fdchp_a_windtur_north	\N	Windspeed North WINDTUR-VLN_L1 [m/s]	m s-1	\N
3542	fdchp_a_windtur_up_function_float32_m_s_1	fdchp_a_windtur_up	\N	Windspeed UP WINDTUR-VLU_L1 [m/s]	m s-1	\N
3543	fdchp_a_windtur_west_function_float32_m_s_1	fdchp_a_windtur_west	\N	Windspeed West WINDTUR-VLW_L1 [m/s]	m s-1	\N
3544	fdchp_a_fluxhot_function_float32_m_s_1_*_K	fdchp_a_fluxhot	\N	Sonic buoyancy flux FLUXHOT_L2 [m/s * K]	m s-1 * K	\N
3545	fdchp_a_fluxmom_alongwind_function_float32_m2_s_2	fdchp_a_fluxmom_alongwind	\N	Along-wind component of the momentum flux FLUXMOM-U_L2 [m^2/s^2]	m2 s-2	\N
3546	fdchp_a_fluxmom_crosswind_function_float32_m2_s_2	fdchp_a_fluxmom_crosswind	\N	Cross-wind component of the momentum flux FLUXMOM-V_L2 [m^2/s^2]	m2 s-2	\N
3547	fdchp_a_time_L1_function_float32_s	fdchp_a_time_L1	\N	Ttimestamps associated with the L1 data products [seconds since 1900-01-01]	s	\N
3548	fdchp_a_time_L2_function_float32_s	fdchp_a_time_L2	\N	Timestamps associated with the L2 data products [seconds since 1900-01-01]	s	\N
3549	nutnr_m_temp_sal_corrected_nitrate_function_float32_uMol_L_1	nutnr_m_temp_sal_corrected_nitrate	\N	Temperature Salinity Corrected Nitrate	uMol L-1	\N
3550	par_auv_biospherical_mobile_function_float32_umol_photons_m_2_s_1_count_1	par_auv_biospherical_mobile	\N	PAR scaling factor	umol photons m-2 s-1 count-1	\N
3551	pco2w_seawater_function_float32_uatm	pco2w_seawater	\N	Partial Pressure of CO2 in Water, uatm	uatm	\N
3552	zplsc_c_transmission_timestamp_quantity_string_1	zplsc_c_transmission_timestamp	\N	Timestamp, "@Dyyyymmddhhmmss!"	1	\N
3553	zplsc_c_phase_quantity_int16_1	zplsc_c_phase	\N	Phase	1	\N
3554	zplsc_c_number_of_frequencies_quantity_int8_1	zplsc_c_number_of_frequencies	\N	Number of stored frequencies (1- 4)	1	\N
3555	zplsc_c_number_of_bins_frequency_1_quantity_int32_1	zplsc_c_number_of_bins_frequency_1	\N	Number of bins for frequency 1	1	\N
3556	zplsc_c_number_of_bins_frequency_2_quantity_int32_1	zplsc_c_number_of_bins_frequency_2	\N	Number of bins for frequency 2	1	\N
3557	zplsc_c_number_of_bins_frequency_3_quantity_int32_1	zplsc_c_number_of_bins_frequency_3	\N	Number of bins for frequency 3	1	\N
3558	zplsc_c_number_of_bins_frequency_4_quantity_int32_1	zplsc_c_number_of_bins_frequency_4	\N	Number of bins for frequency 4	1	\N
3559	zplsc_c_min_value_channel_1_quantity_uint32_counts	zplsc_c_min_value_channel_1	\N	Minimum value in the data subtracted out for channel 1	counts	\N
3560	zplsc_c_min_value_channel_2_quantity_uint32_counts	zplsc_c_min_value_channel_2	\N	Minimum value in the data subtracted out for channel 2	counts	\N
3561	zplsc_c_min_value_channel_3_quantity_uint32_counts	zplsc_c_min_value_channel_3	\N	Minimum value in the data subtracted out for channel 3	counts	\N
3562	zplsc_c_min_value_channel_4_quantity_uint32_counts	zplsc_c_min_value_channel_4	\N	Minimum value in the data subtracted out for channel 4	counts	\N
3563	zplsc_c_date_of_burst_quantity_string_1	zplsc_c_date_of_burst	\N	Date of burst, YYMMDDHHMMSSHH	1	\N
3564	zplsc_c_tilt_x_quantity_float32_deg	zplsc_c_tilt_x	\N	Tilt in X direction	deg	\N
3565	zplsc_c_tilt_y_quantity_float32_deg	zplsc_c_tilt_y	\N	Tilt in Y direction	deg	\N
3566	zplsc_c_battery_voltage_quantity_float32_volt	zplsc_c_battery_voltage	\N	Voltage of the main battery pack	volt	\N
3567	zplsc_c_temperature_quantity_float32_degC	zplsc_c_temperature	\N	Temperature, degress Celcius	degC	\N
3568	zplsc_c_pressure_quantity_float32_dBar	zplsc_c_pressure	\N	Pressure, dbar	dBar	\N
3569	zplsc_c_board_number_channel_1_quantity_string_1	zplsc_c_board_number_channel_1	\N	Channel 1 board number always 0	1	\N
3570	zplsc_c_frequency_channel_1_quantity_string_kHz	zplsc_c_frequency_channel_1	\N	Channel 1 frequency	kHz	\N
3571	zplsc_c_values_channel_1_array_quantity_uint64_counts	zplsc_c_values_channel_1	\N	Channel 1 values minus minimum value	counts	\N
3572	zplsc_c_board_number_channel_2_quantity_string_1	zplsc_c_board_number_channel_2	\N	Channel 2 board number always 1	1	\N
3573	zplsc_c_frequency_channel_2_quantity_string_kHz	zplsc_c_frequency_channel_2	\N	Channel 2 frequency	kHz	\N
3574	zplsc_c_values_channel_2_array_quantity_uint64_counts	zplsc_c_values_channel_2	\N	Channel 2 values minus minimum value	counts	\N
3575	zplsc_c_board_number_channel_3_quantity_string_1	zplsc_c_board_number_channel_3	\N	Channel 3 board number always 2	1	\N
3576	zplsc_c_frequency_channel_3_quantity_string_kHz	zplsc_c_frequency_channel_3	\N	Channel 3 frequency	kHz	\N
3577	zplsc_c_values_channel_3_array_quantity_uint64_counts	zplsc_c_values_channel_3	\N	Channel 3 values minus minimum value	counts	\N
3578	zplsc_c_board_number_channel_4_quantity_string_1	zplsc_c_board_number_channel_4	\N	Channel 4 board number always 3	1	\N
3579	zplsc_c_frequency_channel_4_quantity_string_kHz	zplsc_c_frequency_channel_4	\N	Channel 4 frequency	kHz	\N
3580	zplsc_c_values_channel_4_array_quantity_uint64_counts	zplsc_c_values_channel_4	\N	Channel 4 values minus minimum value	counts	\N
3581	camhd_pan_position_quantity_float32_degrees	camhd_pan_position	\N	Pan	degrees	\N
3582	camhd_tilt_position_quantity_float32_degrees	camhd_tilt_position	\N	Tilt	degrees	\N
3583	camhd_heading_quantity_float32_degrees	camhd_heading	\N	Heading	degrees	\N
3584	camhd_pitch_quantity_float32_degrees	camhd_pitch	\N	Pitch	degrees	\N
3585	camhd_light1_intensity_quantity_int8_Percent	camhd_light1_intensity	\N	Light 1 Intensity	Percent	\N
3586	camhd_light2_intensity_quantity_int8_Percent	camhd_light2_intensity	\N	Light 2 Intensity	Percent	\N
3587	camhd_zoom_quantity_int8_1	camhd_zoom	\N	Zoom level	1	\N
3588	camhd_laser_quantity_boolean_1	camhd_laser	\N	Laser On/Off	1	\N
3589	camhd_channel_name_array_quantity_string_1	camhd_channel_name	\N	Array of channel names	1	\N
3590	camhd_channel_value_array_quantity_float32_1	camhd_channel_value	\N	Array of channel values	1	\N
3591	camhd_value_units_array_quantity_string_1	camhd_value_units	\N	Array of value units	1	\N
3592	voltage_compensated_time_series_function_float32_V	voltage_compensated_time_series	\N	Time-series voltage compensated for external gain and wav format scaling [Volts] (HYDAPBB_L1)	V	\N
3593	low_frequency_acoustic_pressure_waves_function_float32_V	low_frequency_acoustic_pressure_waves	\N	Time-series of low frequency acoustic pressure waves [V] (HYDAPLF_L1)	V	\N
3594	ocean_bottom_seismic_signal_velocity_function_float32_m_s_1	ocean_bottom_seismic_signal_velocity	\N	Time-series of ocean bottom seismic signal [m/s] (GRNDVEL_L1)	m s-1	\N
3595	ocean_bottom_seismic_signal_acceleration_function_float32_m_s_2	ocean_bottom_seismic_signal_acceleration	\N	Time-series of ocean bottom seismic signal [m/s^2] (GRNDACC_L1)	m s-2	\N
3596	short_period_ocean_bottom_seismic_signal_velocity_function_float32_m_s_1	short_period_ocean_bottom_seismic_signal_velocity	\N	Time-series of ocean bottom seismic signal [m/s] (SGRDVEL_L1)	m s-1	\N
3597	flort_dj_cspp_bback_total_function_float32_m_1	flort_dj_cspp_bback_total	\N	Total Optical Backscatter (FLUBSCT-BBACK_L1) [m-1]	m-1	\N
3598	flort_dj_cspp_scat_seawater_function_float32_m_1	flort_dj_cspp_scat_seawater	\N	Total Scattering Coefficient of Pure Seawater [m-1]	m-1	\N
3599	corrected_dissolved_oxygen_function_float32_micro_mole/kg	corrected_dissolved_oxygen	\N	Corrected Dissolved oxygen	micro-mole/kg	\N
3600	pco2w_a_absorbance_blank_434_function_float32_1	pco2w_a_absorbance_blank_434	\N	Absorbance Blank at 434 nm	1	\N
3601	pco2w_a_absorbance_blank_620_function_float32_1	pco2w_a_absorbance_blank_620	\N	Absorbance Blank at 620 nm	1	\N
3602	hpies_travel_time1_L1_function_float32_seconds	hpies_travel_time1_L1	\N	Travel Time1, Seconds	seconds	\N
3603	hpies_travel_time2_L1_function_float32_seconds	hpies_travel_time2_L1	\N	Travel Time2, Seconds	seconds	\N
3604	hpies_travel_time3_L1_function_float32_seconds	hpies_travel_time3_L1	\N	Travel Time3, Seconds	seconds	\N
3605	hpies_travel_time4_L1_function_float32_seconds	hpies_travel_time4_L1	\N	Travel Time4, Seconds	seconds	\N
3606	hpies_bliley_temperature_L1_function_float32_degrees_Celsius	hpies_bliley_temperature_L1	\N	Bliley Temperature, degrees Celsius	degrees Celsius	\N
3607	hpies_pressure_L1_function_float32_dbar	hpies_pressure_L1	\N	Pressure, dbar	dbar	\N
3608	hpies_temperature_function_float32_degrees_Celsius	hpies_temperature	\N	Temperature, degrees Celsius	degrees Celsius	\N
3609	pco2w_b_seawater_function_float32_uatm	pco2w_b_seawater	\N	Partial Pressure of CO2 in Water, uatm	uatm	\N
3610	pco2w_b_absorbance_blank_434_function_float32_1	pco2w_b_absorbance_blank_434	\N	Absorbance Blank at 434 nm	1	\N
3611	pco2w_b_absorbance_blank_620_function_float32_1	pco2w_b_absorbance_blank_620	\N	Absorbance Blank at 620 nm	1	\N
3612	oxy_calphase_volts_quantity_float32_V	oxy_calphase_volts	\N	Calibrated Phase Difference, Volts	V	\N
3613	oxy_temp_volts_quantity_float32_V	oxy_temp_volts	\N	Oxygen Sensor Temperature, Volts	V	\N
3614	dosta_analog_calibrated_phase_function_float32_degrees	dosta_analog_calibrated_phase	\N	Calibrated Phase Difference, degrees	degrees	\N
3615	dosta_analog_optode_temperature_function_float32_deg_C	dosta_analog_optode_temperature	\N	Oxygen Sensor Temperature, deg C	deg_C	\N
3616	dosta_analog_tc_oxygen_function_float32_umol_L_1	dosta_analog_tc_oxygen	\N	Temperature Compensated Dissolved Oxygen Concentration, umol/L	umol L-1	\N
3617	raw_signal_beta_volts_quantity_float32_V	raw_signal_beta_volts	\N	Raw Scattering Measurement, Volts	V	\N
3618	raw_signal_chl_volts_quantity_float32_V	raw_signal_chl_volts	\N	Raw Chlorophyll Measurement, Volts	V	\N
3619	flor_analog_total_volume_scattering_coefficient_function_float32_m_1_sr_1	flor_analog_total_volume_scattering_coefficient	\N	Total Volume Scattering Coefficient (Beta(117,700)), m-1 sr-1	m-1 sr-1	\N
3620	flor_analog_fluorometric_chlorophyll_a_function_float32_ug_L_1	flor_analog_fluorometric_chlorophyll_a	\N	Fluorometric Chlorophyll a Concentration, ug L-1	ug L-1	\N
3621	dark_frame_spectral_channels_array_quantity_uint16_counts	dark_frame_spectral_channels	\N	Spectral Channels	counts	\N
3622	antelope_network_quantity_string_1	antelope_network	\N	Network	1	\N
3623	antelope_station_quantity_string_1	antelope_station	\N	Station	1	\N
3624	antelope_location_quantity_string_1	antelope_location	\N	Location	1	\N
3625	antelope_channel_quantity_string_1	antelope_channel	\N	Channel Id	1	\N
3626	antelope_starttime_quantity_float64_seconds_since_1900_01_01	antelope_starttime	\N	Start Time	seconds since 1900-01-01	\N
3627	antelope_endtime_quantity_float64_seconds_since_1900_01_01	antelope_endtime	\N	End Time	seconds since 1900-01-01	\N
3628	antelope_sampling_rate_quantity_int32_Hz	antelope_sampling_rate	\N	Sampling Rate	Hz	\N
3629	antelope_num_samples_quantity_int32_1	antelope_num_samples	\N	Number of Samples	1	\N
3630	antelope_filename_quantity_string_1	antelope_filename	\N	Filename	1	\N
3631	beam_attenuation_ctdbp_no_function_float32_m_1	beam_attenuation_ctdbp_no	\N	Beam Attenuation, m-1	m-1	\N
3632	optical_absorption_ctdbp_no_function_float32_m_1	optical_absorption_ctdbp_no	\N	Optical Absorption, m-1	m-1	\N
3633	sn_ambient_temperature_quantity_float32_degC	sn_ambient_temperature	\N	Ambient Temperature	degC	\N
3634	sn_cib_5v_current_quantity_float32_A	sn_cib_5v_current	\N	CIB 5V Current	A	\N
3635	sn_cib_board_state_quantity_int32_1	sn_cib_board_state	\N	CIB Board State	1	\N
3636	sn_cib_error_state_quantity_int32_1	sn_cib_error_state	\N	CIB Error State	1	\N
3637	sn_cib_hotel_current_quantity_float32_A	sn_cib_hotel_current	\N	CIB Hotel Current	A	\N
3638	sn_cib_hotel_voltage_quantity_float32_V	sn_cib_hotel_voltage	\N	CIB Hotel Voltage	V	\N
3639	sn_internal_pressure_quantity_float32_Pascal	sn_internal_pressure	\N	Internal Pressure	Pascal	\N
3640	sn_relative_humidity_quantity_float32_percent	sn_relative_humidity	\N	Relative Humidity	percent	\N
3641	sn_pitch_quantity_float32_deg	sn_pitch	\N	Pitch	deg	\N
3642	sn_roll_quantity_float32_deg	sn_roll	\N	Roll	deg	\N
3643	sn_tilt_x_quantity_float32_g	sn_tilt_x	\N	Tilt_X	g	\N
3644	sn_tilt_y_quantity_float32_g	sn_tilt_y	\N	Tilt_Y	g	\N
3645	sn_tilt_z_quantity_float32_g	sn_tilt_z	\N	Tilt_Z	g	\N
3646	sn_hpb_error_state_quantity_int32_1	sn_hpb_error_state	\N	HPB Error State	1	\N
3647	sn_hpb_input_voltage_quantity_float32_V	sn_hpb_input_voltage	\N	HPB Input Voltage	V	\N
3648	sn_hpb_hotel_current_quantity_float32_A	sn_hpb_hotel_current	\N	HPB Hotel Current	A	\N
3649	sn_hpb_hotel_temperature_quantity_float32_degC	sn_hpb_hotel_temperature	\N	HPB Hotel Temperature	degC	\N
3650	sn_hpg_375_gfd_high_quantity_float32_microA	sn_hpg_375_gfd_high	\N	HPB 375 GFD High	microA	\N
3651	sn_hpb_375_gfd_low_quantity_float32_microA	sn_hpb_375_gfd_low	\N	HPB 375 GFD Low	microA	\N
3652	sn_port_output_current_quantity_float32_A	sn_port_output_current	\N	Current	A	\N
3653	sn_port_output_voltage_quantity_float32_V	sn_port_output_voltage	\N	Voltage	V	\N
3654	sn_port_unit_temperature_quantity_float32_degC	sn_port_unit_temperature	\N	Temperature	degC	\N
3655	sn_port_gfd_high_quantity_float32_microA	sn_port_gfd_high	\N	GFD High	microA	\N
3656	sn_port_gfd_low_quantity_float32_microA	sn_port_gfd_low	\N	GFD Low	microA	\N
3657	sn_port_error_state_quantity_int32_1	sn_port_error_state	\N	Error State	1	\N
3658	sn_port_gpio_state_quantity_int32_1	sn_port_gpio_state	\N	GPOI Bits	1	\N
3659	sn_port_ocd_current_quantity_float32_A	sn_port_ocd_current	\N	Over Current Threshold, A	A	\N
3660	sn_port_ocd_time_const_quantity_float32_milliSec	sn_port_ocd_time_const	\N	Over Current Threshold, ms	milliSec	\N
3661	sn_port_power_state_quantity_int32_1	sn_port_power_state	\N	Power State	1	\N
3662	sn_port_board_state_category_int8_str_int8_1	sn_port_board_state	\N	secondary node port board state	1	\N
3663	sn_hpb_hotel_voltage_quantity_float32_V	sn_hpb_hotel_voltage	\N	secondary node hpb hotel voltage	V	\N
3664	sn_hpb_board_state_category_int8_str_int8_1	sn_hpb_board_state	\N	secondary node hpb board state	1	\N
3665	dp_dock_12_v_current_quantity_float32_A	dp_dock_12_v_current	\N	Current, A	A	\N
3666	dp_dock_ambient_temperature_quantity_float32_A	dp_dock_ambient_temperature	\N	Temperature, deg C	A	\N
3667	dp_dock_heat_sink_temperature_quantity_float32_degC	dp_dock_heat_sink_temperature	\N	Temperature, deg C	degC	\N
3668	dp_dock_ips_status_control_quantity_int32_1	dp_dock_ips_status_control	\N	IPS Status	1	\N
3669	dp_dock_relative_humidity_quantity_float32_percent	dp_dock_relative_humidity	\N	Rel Humidity, Percent	percent	\N
3670	dp_mobile_profiler_battery_energy_quantity_float32_wHrs	dp_mobile_profiler_battery_energy	\N	Battery Energy, Watt Hours	wHrs	\N
3671	dp_mobile_profiler_pressure_quantity_float32_deciBars	dp_mobile_profiler_pressure	\N	Pressure, deciBars	deciBars	\N
3672	dp_mobile_profiler_profile_number_quantity_int32_counts	dp_mobile_profiler_profile_number	\N	Profile Number	counts	\N
3673	dp_mobile_profiler_state_quantity_int32_1	dp_mobile_profiler_state	\N	State	1	\N
3674	dp_mobile_profiler_temperature_1_quantity_float32_degC	dp_mobile_profiler_temperature_1	\N	Temperature, deg C	degC	\N
3675	dp_mobile_profiler_temperature_2_quantity_float32_degC	dp_mobile_profiler_temperature_2	\N	Temperature, deg C	degC	\N
3676	dp_mobile_profiler_temperature_3_quantity_float32_degC	dp_mobile_profiler_temperature_3	\N	Temperature, deg C	degC	\N
3677	dp_mobile_profiler_current_quantity_float32_A	dp_mobile_profiler_current	\N	Current, A	A	\N
3678	dp_mobile_profiler_voltage_quantity_float32_V	dp_mobile_profiler_voltage	\N	Voltage, V	V	\N
3679	dp_mobile_profiler_relative_humidity_quantity_float32_percent	dp_mobile_profiler_relative_humidity	\N	Rel Humidity, Percent	percent	\N
3680	ups_system_up_time_quantity_int32_sec	ups_system_up_time	\N	System Up Time	sec	\N
3681	ups_battery_current_quantity_int32_A	ups_battery_current	\N	Battery Current	A	\N
3682	ups_battery_status_quantity_string_1	ups_battery_status	\N	Battery Status	1	\N
3683	ups_battery_voltage_quantity_int32_V	ups_battery_voltage	\N	Battery Voltage	V	\N
3684	ups_estimated_charge_remaining_quantity_int32_percent	ups_estimated_charge_remaining	\N	Percent Charge Remaining	percent	\N
3685	ups_estimated_minutes_remaining_quantity_int32_minutes	ups_estimated_minutes_remaining	\N	Estimated Minutes Remaining	minutes	\N
3686	ups_input_line_bads_quantity_int32_count	ups_input_line_bads	\N	Number of Input Drops	count	\N
3687	ups_input_num_lines_quantity_int32_count	ups_input_num_lines	\N	Number of Input Lines	count	\N
3688	ups_output_frequency_quantity_int32_hz	ups_output_frequency	\N	Output Frequency	hz	\N
3689	ups_output_num_lines_quantity_int32_count	ups_output_num_lines	\N	Number of Output Lines	count	\N
3690	ups_output_source_quantity_string_1	ups_output_source	\N	Output Source	1	\N
3691	ups_seconds_on_battery_quantity_int32_seconds	ups_seconds_on_battery	\N	Seconds Running on Battery	seconds	\N
3692	ups_line_input_current_quantity_int32_A	ups_line_input_current	\N	Input Current	A	\N
3693	ups_line_input_frequency_quantity_int32_hz	ups_line_input_frequency	\N	Input Frequency	hz	\N
3694	ups_line_input_voltage_quantity_int32_V	ups_line_input_voltage	\N	Input Voltage	V	\N
3695	ups_line_output_current_quantity_int32_A	ups_line_output_current	\N	Output Current	A	\N
3696	ups_line_output_percent_load_quantity_int32_percent	ups_line_output_percent_load	\N	Output Percent Load	percent	\N
3697	ups_line_output_power_quantity_int32_W	ups_line_output_power	\N	Output Power	W	\N
3698	ups_line_output_voltage_quantity_int32_V	ups_line_output_voltage	\N	Output Voltage	V	\N
3699	sp_mc_engineering_mode_on_quantity_int32_bool	sp_mc_engineering_mode_on	\N	Engineering Mode On	bool	\N
3700	sp_mc_mc_event_quantity_int32_1	sp_mc_mc_event	\N	Mission Control Event	1	\N
3701	sp_mc_mission_is_active_quantity_int32_bool	sp_mc_mission_is_active	\N	Mission Is Active	bool	\N
3702	sp_mc_scipod_is_docked_quantity_int32_bool	sp_mc_scipod_is_docked	\N	SciPod Is Docked	bool	\N
3703	sp_mc_scipod_is_idle_quantity_int32_bool	sp_mc_scipod_is_idle	\N	SciPod Is Idle	bool	\N
3704	sp_mc_sp_timestamp_microsec_component_quantity_int32_microseconds	sp_mc_sp_timestamp_microsec_component	\N	SP Timestamp MicroSec Component	microseconds	\N
3705	sp_nav_accel_x_quantity_float32_g	sp_nav_accel_x	\N	Accel-X	g	\N
3706	sp_nav_accel_y_quantity_float32_g	sp_nav_accel_y	\N	Accel-Y	g	\N
3707	sp_nav_accel_z_quantity_float32_g	sp_nav_accel_z	\N	Accel-Z	g	\N
3708	sp_nav_magnetic_flux_density_x_quantity_float32_Gauss	sp_nav_magnetic_flux_density_x	\N	Magnetic Flux Density X	Gauss	\N
3709	sp_nav_magnetic_flux_density_y_quantity_float32_Gauss	sp_nav_magnetic_flux_density_y	\N	Magnetic Flux Density Y	Gauss	\N
3710	sp_nav_magnetic_flux_density_z_quantity_float32_Gauss	sp_nav_magnetic_flux_density_z	\N	Magnetic Flux Density Z	Gauss	\N
3711	sp_nav_mission_control_event_quantity_int32_1	sp_nav_mission_control_event	\N	Mission Control Event	1	\N
3712	sp_nav_navdata_timestamp_microsec_component_quantity_float32_microseconds	sp_nav_navdata_timestamp_microsec_component	\N	NavData Timestamp MicroSec Component	microseconds	\N
3713	sp_nav_pitch_quantity_float32_deg	sp_nav_pitch	\N	Pitch	deg	\N
3714	sp_nav_pitch_rate_quantity_float32_deg/sec	sp_nav_pitch_rate	\N	Pitch Rate	deg/sec	\N
3715	sp_nav_roll_quantity_float32_deg	sp_nav_roll	\N	Roll	deg	\N
3716	sp_nav_roll_rate_quantity_float32_deg/sec	sp_nav_roll_rate	\N	Roll Rate	deg/sec	\N
3717	sp_nav_yaw_quantity_float32_deg	sp_nav_yaw	\N	Yaw	deg	\N
3718	sp_nav_yaw_rate_quantity_float32_deg/sec	sp_nav_yaw_rate	\N	Yaw Rate	deg/sec	\N
3719	sp_science_pod_depth_quantity_float32_meters	sp_science_pod_depth	\N	Depth	meters	\N
3720	sp_science_pod_direction_quantity_int32_up0_Down1_Hold2	sp_science_pod_direction	\N	Direction	up0_Down1_Hold2	\N
3721	sp_science_pod_mission_control_event_quantity_int32_1	sp_science_pod_mission_control_event	\N	Mission Control Event	1	\N
3722	sp_science_pod_speed_quantity_float32_meters/second	sp_science_pod_speed	\N	Speed	meters/second	\N
3723	sp_science_pod_wave_height_quantity_float32_meters	sp_science_pod_wave_height	\N	Wave Height	meters	\N
3724	sp_wc_cable_out_quantity_float32_meters	sp_wc_cable_out	\N	Cable Out	meters	\N
3725	sp_wc_is_bottom_layer_quantity_int32_bool	sp_wc_is_bottom_layer	\N	Is Bottom Layer	bool	\N
3726	sp_wc_mission_control_event_quantity_int32_1	sp_wc_mission_control_event	\N	Mission Control Event	1	\N
3727	sp_wc_winch_cable_wrap_index_quantity_int32_index	sp_wc_winch_cable_wrap_index	\N	Winch Cable Wrap Index	index	\N
3728	sp_wc_winch_cable_wrap_layer_quantity_int32_index	sp_wc_winch_cable_wrap_layer	\N	Winch Cable Wrap Layer	index	\N
3729	sp_wc_winch_position_at_last_drum_index_quantity_int32_revs	sp_wc_winch_position_at_last_drum_index	\N	Winch Position at Last Drum Index	revs	\N
3730	sp_wc_winch_revs_quantity_int32_revs	sp_wc_winch_revs	\N	Winch Revs	revs	\N
3731	sp_wc_winch_speed_quantity_int32_rpm	sp_wc_winch_speed	\N	Winch Speed	rpm	\N
3732	sp_wc_winch_vfd_board_temp_quantity_float32_degC	sp_wc_winch_vfd_board_temp	\N	Winch VFD Board Temp	degC	\N
3733	sp_wc_winch_vfd_sink_temp_quantity_float32_degC	sp_wc_winch_vfd_sink_temp	\N	Winch VFD Sink Temp	degC	\N
3734	sp_wcler_based_xml_rpc_data_server_mission_control_event_quantity_int32_1	sp_wcler_based_xml_rpc_data_server_mission_control_event	\N	Mission Control Event	1	\N
3735	sp_wc_levelwind_cart_direction_quantity_int32_Left0_Rt1_Hld2	sp_wc_levelwind_cart_direction	\N	Cart Direction	Left0_Rt1_Hld2	\N
3736	sp_wc_levelwind_direction_quantity_int32_Clockwise0_CounterCw1_Hld2	sp_wc_levelwind_direction	\N	Levelwind Direction	Clockwise0_CounterCw1_Hld2	\N
3737	sp_wc_levelwind_direction_is_clockwise_quantity_int32_bool	sp_wc_levelwind_direction_is_clockwise	\N	Levelwind Direction Is Clockwise	bool	\N
3738	sp_wc_levelwind_one_way_strokes_quantity_int32_strokes	sp_wc_levelwind_one_way_strokes	\N	Levelwind One-Way Strokes	strokes	\N
3739	sp_wc_levelwind_position_at_last_reverse_index_quantity_int32_revs	sp_wc_levelwind_position_at_last_reverse_index	\N	Levelwind Position at Last Reverse Index	revs	\N
3740	sp_wc_levelwind_speed_quantity_int32_rpm	sp_wc_levelwind_speed	\N	levelwind Speed	rpm	\N
3741	sp_wc_levelwind_vfd_board_temperature_quantity_float32_degC	sp_wc_levelwind_vfd_board_temperature	\N	Levelwind VFD Board Temperature	degC	\N
3742	sp_wc_levelwind_vfd_sink_temperature_quantity_float32_degC	sp_wc_levelwind_vfd_sink_temperature	\N	Levelwind VFD Sink Temperature	degC	\N
3743	sp_wc_levelwind_mission_control_event_quantity_int32_1	sp_wc_levelwind_mission_control_event	\N	Mission Control Event	1	\N
3744	pfe_hvps1_on_quantity_string_1	pfe_hvps1_on	\N	HVPS1 On	1	\N
3745	pfe_hvps2_on_quantity_string_1	pfe_hvps2_on	\N	HVPS2 On	1	\N
3746	pfe_i_gnd_quantity_float32_A	pfe_i_gnd	\N	Ground Current	A	\N
3747	pfe_i_ncbl_quantity_float32_A	pfe_i_ncbl	\N	Current North Cable LIne	A	\N
3748	pfe_i_scbl_quantity_float32_A	pfe_i_scbl	\N	Current South Cable Line	A	\N
3749	pfe_i_phasea_quantity_float32_A	pfe_i_phasea	\N	Current Phase A	A	\N
3750	pfe_i_phaseb_quantity_float32_A	pfe_i_phaseb	\N	Current Phase B	A	\N
3751	pfe_i_phasec_quantity_float32_A	pfe_i_phasec	\N	Current Phase C	A	\N
3752	pfe_imon_1_quantity_float32_A	pfe_imon_1	\N	Current Monitor 1	A	\N
3753	pfe_imon_2_quantity_float32_A	pfe_imon_2	\N	Current Monitor 2	A	\N
3754	pfe_mode_quantity_string_1	pfe_mode	\N	PFE Mode	1	\N
3755	pfe_p_hvps1_quantity_float32_kWatts	pfe_p_hvps1	\N	Power HVPS 1	kWatts	\N
3756	pfe_p_hvps2_quantity_float32_kWatts	pfe_p_hvps2	\N	Power HVPS 2	kWatts	\N
3757	pfe_p_ncbl_quantity_float32_kWatts	pfe_p_ncbl	\N	Power North Cable Line	kWatts	\N
3758	pfe_p_scbl_quantity_float32_kWatts	pfe_p_scbl	\N	Power South Cable Line	kWatts	\N
3759	pfe_v_gnd_quantity_float32_V	pfe_v_gnd	\N	Ground Voltage	V	\N
3760	pfe_v_ncbl_quantity_float32_V	pfe_v_ncbl	\N	Voltage North Cable Line	V	\N
3761	pfe_v_scbl_quantity_float32_V	pfe_v_scbl	\N	Voltage South Cable Line	V	\N
3762	pfe_v_phasea_quantity_float32_V	pfe_v_phasea	\N	Voltage Phase A	V	\N
3763	pfe_v_phaseb_quantity_float32_V	pfe_v_phaseb	\N	Voltage Phase B	V	\N
3764	pfe_v_phasec_quantity_float32_V	pfe_v_phasec	\N	Voltage Phase C	V	\N
3765	pfe_vmon_1_quantity_float32_V	pfe_vmon_1	\N	Voltage Monitor 1	V	\N
3766	pfe_vmon_2_quantity_float32_V	pfe_vmon_2	\N	Voltage Monitor 2	V	\N
3767	pn_currentsustainingload_quantity_string_1	pn_currentsustainingload	\N	CSL State	1	\N
3768	pn_currentsustainingloadimbalancecurrent_quantity_float32_mA	pn_currentsustainingloadimbalancecurrent	\N	CSL Imbalance Current	mA	\N
3769	pn_currentsustainingloadportcurrent_quantity_float32_A	pn_currentsustainingloadportcurrent	\N	CSL Current	A	\N
3770	pn_hotelcurrent_quantity_float32_A	pn_hotelcurrent	\N	Hotle Current	A	\N
3771	pn_inputbuscurrent_quantity_float32_A	pn_inputbuscurrent	\N	Input Bus Current	A	\N
3772	pn_inputearthleakage_quantity_float32_mA	pn_inputearthleakage	\N	Input Earth Leakage	mA	\N
3773	pn_inputvoltage_quantity_float32_V	pn_inputvoltage	\N	Input Voltage	V	\N
3774	pn_mvpcexpansionport1current_quantity_float32_A	pn_mvpcexpansionport1current	\N	MVPC Expansion Port 1 Current	A	\N
3775	pn_mvpcexpansionport2current_quantity_float32_A	pn_mvpcexpansionport2current	\N	MVPC Expansion Port 2 Current	A	\N
3776	pn_mvpcinputcurrent_quantity_float32_A	pn_mvpcinputcurrent	\N	MVPC Input Current	A	\N
3777	pn_mvpcinputvoltage_quantity_float32_V	pn_mvpcinputvoltage	\N	MVPC Input Voltage	V	\N
3778	pn_mvpcpressure1_quantity_float32_PSI	pn_mvpcpressure1	\N	MVPC Pressure 1	PSI	\N
3779	pn_mvpcpressure2_quantity_float32_PSI	pn_mvpcpressure2	\N	MVPC Pressure 2	PSI	\N
3780	pn_mvpctemperature_quantity_float32_degC	pn_mvpctemperature	\N	MVPC Temperature	degC	\N
3781	pn_monitoringboardhumidity_quantity_float32_percent	pn_monitoringboardhumidity	\N	MVPC Humidity	percent	\N
3782	pn_monitoringboardtemperature_quantity_float32_degC	pn_monitoringboardtemperature	\N	MVPC Tempeature 2	degC	\N
3783	pn_pitch_quantity_float32_deg	pn_pitch	\N	Pitch	deg	\N
3784	pn_primaryoobtemperature_quantity_float32_degC	pn_primaryoobtemperature	\N	OOB Temperature	degC	\N
3785	pn_primarypowermoduletemperature_quantity_float32_degC	pn_primarypowermoduletemperature	\N	Primary Power Temperature	degC	\N
3786	pn_primaryswtemperature_quantity_float32_degC	pn_primaryswtemperature	\N	Primary SW Temperature	degC	\N
3787	pn_roll_quantity_float32_deg	pn_roll	\N	Roll	deg	\N
3788	pn_scienceport1_status_quantity_string_1	pn_scienceport1_status	\N	Science Port 1 State	1	\N
3789	pn_scienceport1_current_quantity_float32_A	pn_scienceport1_current	\N	Science Port 1 Current	A	\N
3790	pn_scienceport1_imbalancecurrent_quantity_float32_mA	pn_scienceport1_imbalancecurrent	\N	Science Port 1 Imbalance Current	mA	\N
3791	pn_scienceport2_status_quantity_string_1	pn_scienceport2_status	\N	Science Port 2 State	1	\N
3792	pn_scienceport2_current_quantity_float32_A	pn_scienceport2_current	\N	Science Port 2 Current	A	\N
3793	pn_scienceport2_imbalancecurrent_quantity_float32_mA	pn_scienceport2_imbalancecurrent	\N	Science Port 2 Imbalance Current	mA	\N
3794	pn_scienceport3_status_quantity_string_1	pn_scienceport3_status	\N	Science Port 3 State	1	\N
3795	pn_scienceport3_current_quantity_float32_A	pn_scienceport3_current	\N	Science Port 3 Current	A	\N
3796	pn_scienceport3_imbalancecurrent_quantity_float32_mA	pn_scienceport3_imbalancecurrent	\N	Science Port 3 Imbalance Current	mA	\N
3797	pn_scienceport4_status_quantity_string_1	pn_scienceport4_status	\N	Science Port 4 State	1	\N
3798	pn_scienceport4_current_quantity_float32_A	pn_scienceport4_current	\N	Science Port 4 Current	A	\N
3799	pn_scienceport4_imbalancecurrent_quantity_float32_mA	pn_scienceport4_imbalancecurrent	\N	Science Port 4 Imbalance Current	mA	\N
3800	pn_scienceport5_status_quantity_string_1	pn_scienceport5_status	\N	Science Port 5 State	1	\N
3801	pn_scienceport5_current_quantity_float32_A	pn_scienceport5_current	\N	Science Port 5 Current	A	\N
3802	pn_scienceport5_imbalancecurrent_quantity_float32_mA	pn_scienceport5_imbalancecurrent	\N	Science Port 5 Imbalance Current	mA	\N
3803	pn_scienceport6_status_quantity_string_1	pn_scienceport6_status	\N	Science Port 6 State	1	\N
3804	pn_scienceport6_current_quantity_float32_A	pn_scienceport6_current	\N	Science Port 6 Current	A	\N
3805	pn_scienceport6_imbalancecurrent_quantity_float32_mA	pn_scienceport6_imbalancecurrent	\N	Science Port 6 Imbalance Current	mA	\N
3806	pn_scienceport7_status_quantity_string_1	pn_scienceport7_status	\N	Science Port 7 State	1	\N
3807	pn_scienceport7_current_quantity_float32_A	pn_scienceport7_current	\N	Science Port 7 Current	A	\N
3808	pn_scienceport7_imbalancecurrent_quantity_float32_mA	pn_scienceport7_imbalancecurrent	\N	Science Port 7 Imbalance Current	mA	\N
3809	pn_secondaryoobtemperature_quantity_float32_degC	pn_secondaryoobtemperature	\N	Voltage Monitor 2	degC	\N
3810	pn_secondarypowermoduletemperature_quantity_float32_degC	pn_secondarypowermoduletemperature	\N	Voltage Monitor 2	degC	\N
3811	pn_secondaryswtemperature_quantity_float32_degC	pn_secondaryswtemperature	\N	Voltage Monitor 2	degC	\N
3812	pn_oob_sfp_enabled_quantity_string_1	pn_oob_sfp_enabled	\N	SFP Enabled	1	\N
3813	pn_oob_sfp_inpackets_quantity_int32_count	pn_oob_sfp_inpackets	\N	In Packets	count	\N
3814	pn_oob_sfp_linkdownstate_quantity_string_1	pn_oob_sfp_linkdownstate	\N	Link Down	1	\N
3815	pn_oob_sfp_outpackets_quantity_int32_count	pn_oob_sfp_outpackets	\N	Out Packets	count	\N
3816	pn_oob_sfp_rxerrors_quantity_int32_count	pn_oob_sfp_rxerrors	\N	Rx Error Count	count	\N
3817	pn_oob_sfp_current_quantity_float32_A	pn_oob_sfp_current	\N	SFP Current	A	\N
3818	pn_oob_sfp_rxpower_quantity_float32_dBm	pn_oob_sfp_rxpower	\N	Rx Power	dBm	\N
3819	pn_oob_sfp_temp_quantity_float32_degC	pn_oob_sfp_temp	\N	Temperature	degC	\N
3820	pn_oob_sfp_txpower_quantity_float32_dBm	pn_oob_sfp_txpower	\N	Tx Power	dBm	\N
3821	pn_oob_sfp_voltage_quantity_float32_V	pn_oob_sfp_voltage	\N	Voltage	V	\N
3822	pn_oob_sfp_timeoutstate_quantity_string_1	pn_oob_sfp_timeoutstate	\N	Timeout State	1	\N
3823	otn_ifadminstatusdata_quantity_string_1	otn_ifadminstatusdata	\N	Admin Status	1	\N
3824	otn_ifoperstatusdata_quantity_string_1	otn_ifoperstatusdata	\N	Operational Status	1	\N
3825	otn_sfpdiagmoduletemperaturedegreescsfp_quantity_float32_degC	otn_sfpdiagmoduletemperaturedegreescsfp	\N	Temperature	degC	\N
3826	otn_sfpdiagrxinputpowerdbmsfp_quantity_float32_dBm	otn_sfpdiagrxinputpowerdbmsfp	\N	Rx Power	dBm	\N
3827	otn_sfpdiagrxlasertemperaturedegreescsfp_quantity_float32_degC	otn_sfpdiagrxlasertemperaturedegreescsfp	\N	Laser Temperature	degC	\N
3828	otn_sfpdiagtxoutputpowerdbmsfp_quantity_float32_dBm	otn_sfpdiagtxoutputpowerdbmsfp	\N	Tx Power	dBm	\N
3829	otn_slotnconfigoperationmode_quantity_string_1	otn_slotnconfigoperationmode	\N	Configuration Operation Mode	1	\N
3830	otn_slotnpmfecqfactorfe_quantity_float32_db	otn_slotnpmfecqfactorfe	\N	Q Factor Far End	db	\N
3831	otn_slotnpmfecqfactorne_quantity_float32_db	otn_slotnpmfecqfactorne	\N	Q Factor Near End	db	\N
3832	otn_ifadminstatussfp_quantity_string_1	otn_ifadminstatussfp	\N	Admin Status	1	\N
3833	otn_ifoperstatussfp_quantity_string_1	otn_ifoperstatussfp	\N	Operational Status	1	\N
3834	otn_sfpdiagmoduletemperaturesfp_quantity_float32_degC	otn_sfpdiagmoduletemperaturesfp	\N	Temperature	degC	\N
3835	otn_sfpdiagrxinputpowersfp_quantity_float32_uWatts	otn_sfpdiagrxinputpowersfp	\N	Rx Power	uWatts	\N
3836	otn_sfpdiagrxlasertemperaturesfp_quantity_float32_degC	otn_sfpdiagrxlasertemperaturesfp	\N	Laser Temperature	degC	\N
3837	otn_sfpdiagrxmeasuredwavelengthsfp_quantity_float32_nM	otn_sfpdiagrxmeasuredwavelengthsfp	\N	Wavelength	nM	\N
3838	otn_sfpdiagsupplyvoltagesfp_quantity_float32_V	otn_sfpdiagsupplyvoltagesfp	\N	Supply Voltage	V	\N
3839	otn_sfpdiagtxbiassfp_quantity_float32_uA	otn_sfpdiagtxbiassfp	\N	Bias Current	uA	\N
3840	otn_sfpdiagtxoutputpowerdbmsfp_quantity_float32_dBm	otn_sfpdiagtxoutputpowerdbmsfp	\N	Tx Power	dBm	\N
3841	otn_sfpdiagtxoutputpowersfp_quantity_string_uWatts	otn_sfpdiagtxoutputpowersfp	\N	Tx Power	uWatts	\N
3842	f10_ifadminstatus_quantity_string_1	f10_ifadminstatus	\N	Admin Status	1	\N
3843	f10_ifindiscards_quantity_int32_count	f10_ifindiscards	\N	In Discards	count	\N
3844	f10_ifinerrors_quantity_int32_count	f10_ifinerrors	\N	In Errors	count	\N
3845	f10_ifinnucastpkts_quantity_int32_count	f10_ifinnucastpkts	\N	In nu Cast Pkts	count	\N
3846	f10_ifinoctets_quantity_int32_count	f10_ifinoctets	\N	In Octets	count	\N
3847	f10_ifinucastpkts_quantity_int32_count	f10_ifinucastpkts	\N	In u Cast Pkts	count	\N
3848	f10_ifinunknownprotos_quantity_int32_count	f10_ifinunknownprotos	\N	In Unknown Protocol	count	\N
3849	f10_ifoperstatus_quantity_string_1	f10_ifoperstatus	\N	Operational Status	1	\N
3850	f10_ifoutdiscards_quantity_int32_count	f10_ifoutdiscards	\N	Out Discards	count	\N
3851	f10_ifouterrors_quantity_int32_count	f10_ifouterrors	\N	Out Errors	count	\N
3852	f10_ifoutnucastpkts_quantity_int32_count	f10_ifoutnucastpkts	\N	Out nu Cast Pkts	count	\N
3853	f10_ifoutoctets_quantity_int32_count	f10_ifoutoctets	\N	Out Octets	count	\N
3854	f10_ifoutucastpkts_quantity_int32_count	f10_ifoutucastpkts	\N	Out u Cast Pkts	count	\N
3855	f10_ifspeed_quantity_int32_count	f10_ifspeed	\N	Out Unknown Protocol	count	\N
3856	ts_fault_aux_reference_clock_lock_quantity_int32_1	ts_fault_aux_reference_clock_lock	\N	Fault Aux Reference Clock Lock	1	\N
3857	ts_fault_digital_to_audio_converter_quantity_int32_1	ts_fault_digital_to_audio_converter	\N	Fault DAC Converter	1	\N
3858	ts_fault_first_time_locking_quantity_int32_1	ts_fault_first_time_locking	\N	Fault First Time Locking	1	\N
3859	ts_fault_irig_lock_quantity_int32_1	ts_fault_irig_lock	\N	Fault IRIG Locking	1	\N
3860	ts_fault_lpn_pll_quantity_int32_1	ts_fault_lpn_pll	\N	Fault LPN PLL	1	\N
3861	ts_fault_pll_synthesizer_quantity_int32_1	ts_fault_pll_synthesizer	\N	Fault PLL Synthesizer	1	\N
3862	ts_fault_primary_power_quantity_int32_1	ts_fault_primary_power	\N	Fault Primary Power	1	\N
3863	ts_fault_primary_ref_clk_quantity_int32_1	ts_fault_primary_ref_clk	\N	Fault Primary Reference Clock	1	\N
3864	ts_fault_rubidium_oscillator_quantity_int32_1	ts_fault_rubidium_oscillator	\N	Fault Rubidium Osc	1	\N
3865	ts_fault_secondary_power_quantity_int32_1	ts_fault_secondary_power	\N	Fault Secondary Power	1	\N
3866	ts_fault_secondary_ref_clk_quantity_int32_1	ts_fault_secondary_ref_clk	\N	Fault Secondary Reference Clock	1	\N
3867	ts_fault_time_error_quantity_int32_1	ts_fault_time_error	\N	Fault Time Error	1	\N
3868	ts_fault_timeout_quantity_int32_1	ts_fault_timeout	\N	Fault Timeout	1	\N
3869	ts_ntp_auth_fail_quantity_int32_1	ts_ntp_auth_fail	\N	NTP Auth Fail	1	\N
3870	ts_ntp_in_errors_quantity_int32_1	ts_ntp_in_errors	\N	NTP In Errors	1	\N
3871	ts_ntp_in_pkts_quantity_int32_1	ts_ntp_in_pkts	\N	NTP In Packets	1	\N
3872	ts_ntp_out_pkts_quantity_int32_1	ts_ntp_out_pkts	\N	NTP Out Packets	1	\N
3873	ts_status_aux_ref_clock_quantity_string_1	ts_status_aux_ref_clock	\N	Status Aux Reference Clock	1	\N
3874	ts_status_clock_quantity_string_1	ts_status_clock	\N	Status Clock Quantity	1	\N
3875	ts_status_clock_source_quantity_string_1	ts_status_clock_source	\N	Status Clock Source	1	\N
3876	ts_status_digital_to_audio_converter_quantity_string_1	ts_status_digital_to_audio_converter	\N	Status DAC	1	\N
3877	ts_status_first_time_locking_quantity_string_1	ts_status_first_time_locking	\N	Status First Time Locking	1	\N
3878	ts_status_irig_lock_quantity_string_1	ts_status_irig_lock	\N	Status IRIG Lock	1	\N
3879	ts_status_lpn_pll_quantity_string_1	ts_status_lpn_pll	\N	Status LPN PLL	1	\N
3880	ts_status_pll_synthesizer_quantity_string_1	ts_status_pll_synthesizer	\N	Status PLL Synthesizer	1	\N
3881	ts_status_primary_power_quantity_string_1	ts_status_primary_power	\N	Status Primary Power	1	\N
3882	ts_status_primary_reference_clock_quantity_string_1	ts_status_primary_reference_clock	\N	Status Primary Reference Clock	1	\N
3883	ts_status_rubidium_oscillator_quantity_string_1	ts_status_rubidium_oscillator	\N	Status Rubidium Osc	1	\N
3884	ts_status_secondary_power_quantity_string_1	ts_status_secondary_power	\N	Status Secondary Power	1	\N
3885	ts_status_secondary_reference_clock_quantity_string_1	ts_status_secondary_reference_clock	\N	Status Secondary Reference Clock	1	\N
3886	ts_status_time_error_quantity_string_1	ts_status_time_error	\N	Status Time Error Quantity	1	\N
3887	ts_status_timeout_error_quantity_string_1	ts_status_timeout_error	\N	Status Timout Error	1	\N
3888	ts_system_up_time_quantity_int32_count	ts_system_up_time	\N	System Up Time	count	\N
\.


--
-- Data for Name: stream_parameter_link; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY stream_parameter_link (id, stream_id, parameter_id) FROM stdin;
\.


--
-- Name: stream_parameter_link_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('stream_parameter_link_id_seq', 1, false);


--
-- Name: stream_parameters_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('stream_parameters_id_seq', 1, false);


--
-- Name: streams_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('streams_id_seq', 1, false);


--
-- Data for Name: system_event_definitions; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY system_event_definitions (id, uframe_filter_id, reference_designator, array_name, platform_name, instrument_name, instrument_parameter, instrument_parameter_pdid, operator, created_time, event_type, active, description, high_value, low_value, severity, stream, retired, ts_retired, escalate_on, escalate_boundary, event_receipt_delta) FROM stdin;
\.


--
-- Name: system_event_definitions_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('system_event_definitions_id_seq', 1, false);


--
-- Data for Name: system_events; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY system_events (id, system_event_definition_id, uframe_event_id, uframe_filter_id, event_time, event_type, event_response, method, deployment, acknowledged, ack_by, ts_acknowledged, ticket_id, escalated, ts_escalated, "timestamp", ts_start, resolved, resolved_comment) FROM stdin;
\.


--
-- Name: system_events_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('system_events_id_seq', 1, false);


--
-- Data for Name: user_event_notifications; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY user_event_notifications (id, system_event_definition_id, user_id, use_email, use_redmine, use_phone, use_log, use_sms) FROM stdin;
\.


--
-- Name: user_event_notifications_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('user_event_notifications_id_seq', 1, false);


--
-- Data for Name: user_scopes; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY user_scopes (id, scope_name, scope_description) FROM stdin;
1	user_admin	\N
2	annotate	\N
3	asset_manager	\N
4	command_control	\N
5	redmine	\N
6	organization	\N
\.


--
-- Data for Name: user_scope_link; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

COPY user_scope_link (id, user_id, scope_id) FROM stdin;
1	1	1
2	1	5
\.


--
-- Name: user_scope_link_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('user_scope_link_id_seq', 2, true);


--
-- Name: user_scopes_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('user_scopes_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('users_id_seq', 1, true);


--
-- Name: watches_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('watches_id_seq', 1, false);


SET search_path = public, pg_catalog;

--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: mjc
--

COPY spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

