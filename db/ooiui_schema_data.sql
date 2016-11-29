--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = ooiui, public, pg_catalog;

--
-- Data for Name: organizations; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

INSERT INTO organizations VALUES (1, 'RPS ASA', 'Applied Science Associates', NULL);
INSERT INTO organizations VALUES (2, 'Rutgers', 'University of Rutgers', NULL);
INSERT INTO organizations VALUES (3, 'WHOI', 'Woods Hole Oceanographic Institution', NULL);
INSERT INTO organizations VALUES (4, 'OSU', 'Oregon State University', NULL);
INSERT INTO organizations VALUES (5, 'COL', 'Consortium of Ocean Leadership', NULL);
INSERT INTO organizations VALUES (6, 'NSF', 'National Science Foundation', NULL);
INSERT INTO organizations VALUES (7, 'SIO', 'Scripps Institution of Oceanography', NULL);
INSERT INTO organizations VALUES (8, 'UW', 'Univeristy of Washington', NULL);
INSERT INTO organizations VALUES (9, 'Other', 'Other', NULL);


--
-- Data for Name: annotations; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--



--
-- Name: annotations_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('annotations_id_seq', 1, false);


--
-- Data for Name: arrays; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

INSERT INTO arrays VALUES (1, 'CE', 'Coastal-Scale Node Surface buoys, profilers, benthic nodes and gliders will provide near real time data from the air-sea interface to the sea floor.', 'Endurance', 'Coastal Endurance', '0103000020E610000001000000050000008FC2F5285C2F4640CDCCCCCCCC3C5FC08FC2F5285C2F4640CDCCCCCCCC3C5FC08FC2F5285C2F4640CDCCCCCCCC3C5FC08FC2F5285C2F4640CDCCCCCCCC3C5FC08FC2F5285C2F4640CDCCCCCCCC3C5FC0');
INSERT INTO arrays VALUES (2, 'GP', '', 'Station Papa', 'Global Station Papa', '0103000020E610000001000000050000004C37894160FD4840E3A59BC4200862C04C37894160FD4840E3A59BC4200862C04C37894160FD4840E3A59BC4200862C04C37894160FD4840E3A59BC4200862C04C37894160FD4840E3A59BC4200862C0');
INSERT INTO arrays VALUES (3, 'CP', '', 'Pioneer', 'Coastal Pioneer', '0103000020E61000000100000005000000CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0CDCCCCCCCC0C4440B81E85EB51B851C0');
INSERT INTO arrays VALUES (4, 'GA', '', 'Argentine Basin', 'Global Argentine Basin', '0103000020E6100000010000000500000062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C062A1D634EF4045C0448B6CE7FB7145C0');
INSERT INTO arrays VALUES (5, 'GI', 'The Global Irminger sensor network, located in the Argentine Basin in the South Atlantic, supports sensors for measurement of air-sea fluxes of heat, moisture and momentum, and physical, biological and chemical properties throughout the water column.', 'Irminger Sea', 'Global Irminger Sea', '0103000020E610000001000000050000007B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C07B832F4CA63A4E4071AC8BDB683843C0');
INSERT INTO arrays VALUES (6, 'GS', '', 'Southern Ocean', 'Global Southern Ocean', '0103000020E610000001000000050000007CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C07CF2B0506B0A4BC0265305A3926A56C0');
INSERT INTO arrays VALUES (7, 'RS', '', 'Cabled Array', 'Cabled Array', '0103000020E61000000100000005000000F4FDD478E94646404A0C022B87565FC0F4FDD478E94646404A0C022B87565FC0F4FDD478E94646404A0C022B87565FC0F4FDD478E94646404A0C022B87565FC0F4FDD478E94646404A0C022B87565FC0');


--
-- Name: arrays_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('arrays_id_seq', 7, true);


--
-- Data for Name: files; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--


--
-- Name: files_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('files_id_seq', 1, false);


--
-- Data for Name: operator_event_types; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--

INSERT INTO operator_event_types VALUES (1, 'INFO', 'General information event.');
INSERT INTO operator_event_types VALUES (2, 'WARN', 'A warning has occurred.');
INSERT INTO operator_event_types VALUES (3, 'ERROR', 'An error has occurred.');
INSERT INTO operator_event_types VALUES (4, 'CRITICAL', 'A critical event has occurred.');
INSERT INTO operator_event_types VALUES (5, 'WATCH_START', 'Watch has started.');
INSERT INTO operator_event_types VALUES (6, 'WATCH_END', 'Watch has ended.');


--
-- Name: operator_event_types_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('operator_event_types_id_seq', 6, true);


--
-- Data for Name: watches; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--



--
-- Data for Name: operator_events; Type: TABLE DATA; Schema: ooiui; Owner: postgres
--



--
-- Name: operator_events_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('operator_events_id_seq', 1, false);


--
-- Name: organizations_id_seq; Type: SEQUENCE SET; Schema: ooiui; Owner: postgres
--

SELECT pg_catalog.setval('organizations_id_seq', 9, true);

