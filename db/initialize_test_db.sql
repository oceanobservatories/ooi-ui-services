
BEGIN;
CREATE TABLE arrays (
    id integer NOT NULL,
    array_code text,
    description text,
    name text
);

CREATE TABLE deployments (
    id integer NOT NULL,
    start_date date,
    end_date date,
    cruise_id integer
);



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
CREATE TABLE streams (
    id integer NOT NULL,
    name text,
    instrument_id integer,
    description text
);

INSERT INTO arrays VALUES (1, 'CP', NULL, 'Coastal Pioneer');


INSERT INTO instrument_deployments VALUES (1, 'Velocity Profiler (short range)', NULL, NULL, 14, NULL, 'CP02PMCI-RII01-02-ADCPTG000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (2, 'Engineering Data', NULL, NULL, 14, NULL, 'CP02PMCI-RII01-00-ENG000000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (3, 'Engineering Data', NULL, NULL, 13, NULL, 'CP02PMCI-SBS01-00-ENG000000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (4, '3-Axis Motion Package', NULL, NULL, 13, NULL, 'CP02PMCI-SBS01-01-MOPAK0000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (5, 'Engineering Data', NULL, NULL, 15, NULL, 'CP02PMCI-WFP01-00-ENG000000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (6, 'Photosynthetically Available Radiation', NULL, NULL, 15, NULL, 'CP02PMCI-WFP01-05-PARADK000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (7, '3-Wavelength Fluorometer', NULL, NULL, 15, NULL, 'CP02PMCI-WFP01-04-FLORTK000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (8, 'CTD Profiler', NULL, NULL, 15, NULL, 'CP02PMCI-WFP01-03-CTDPFK000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (9, 'Dissolved Oxygen Fast Response', NULL, NULL, 15, NULL, 'CP02PMCI-WFP01-02-DOFSTK000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (10, '3-D Single Point Velocity Meter', NULL, NULL, 15, NULL, 'CP02PMCI-WFP01-01-VEL3DK000', 40.2299995, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (11, 'Velocity Profiler (short range)', NULL, NULL, 17, NULL, 'CP02PMCO-RII01-02-ADCPTG000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (12, 'Engineering Data', NULL, NULL, 17, NULL, 'CP02PMCO-RII01-00-ENG000000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (13, 'Engineering Data', NULL, NULL, 16, NULL, 'CP02PMCO-SBS01-00-ENG000000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (14, '3-Axis Motion Package', NULL, NULL, 16, NULL, 'CP02PMCO-SBS01-01-MOPAK0000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (15, 'Dissolved Oxygen Fast Response', NULL, NULL, 18, NULL, 'CP02PMCO-WFP01-02-DOFSTK000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (16, 'Engineering Data', NULL, NULL, 18, NULL, 'CP02PMCO-WFP01-00-ENG000000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (17, '3-D Single Point Velocity Meter', NULL, NULL, 18, NULL, 'CP02PMCO-WFP01-01-VEL3DK000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (18, 'CTD Profiler', NULL, NULL, 18, NULL, 'CP02PMCO-WFP01-03-CTDPFK000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (19, '3-Wavelength Fluorometer', NULL, NULL, 18, NULL, 'CP02PMCO-WFP01-04-FLORTK000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (20, 'Photosynthetically Available Radiation', NULL, NULL, 18, NULL, 'CP02PMCO-WFP01-05-PARADK000', 40.0999985, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (21, 'Engineering Data', NULL, NULL, 8, NULL, 'CP02PMUI-RII01-00-ENG000000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (22, 'Velocity Profiler (short range)', NULL, NULL, 8, NULL, 'CP02PMUI-RII01-02-ADCPTG000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (23, '3-Axis Motion Package', NULL, NULL, 7, NULL, 'CP02PMUI-SBS01-01-MOPAK0000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (24, 'Engineering Data', NULL, NULL, 7, NULL, 'CP02PMUI-SBS01-00-ENG000000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (25, 'Dissolved Oxygen Fast Response', NULL, NULL, 9, NULL, 'CP02PMUI-WFP01-02-DOFSTK000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (26, 'Engineering Data', NULL, NULL, 9, NULL, 'CP02PMUI-WFP01-00-ENG000000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (27, 'Photosynthetically Available Radiation', NULL, NULL, 9, NULL, 'CP02PMUI-WFP01-05-PARADK000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (28, '3-Wavelength Fluorometer', NULL, NULL, 9, NULL, 'CP02PMUI-WFP01-04-FLORTK000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (29, 'CTD Profiler', NULL, NULL, 9, NULL, 'CP02PMUI-WFP01-03-CTDPFK000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (30, '3-D Single Point Velocity Meter', NULL, NULL, 9, NULL, 'CP02PMUI-WFP01-01-VEL3DK000', 40.3699989, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (31, 'Velocity Profiler (short range)', NULL, NULL, 11, NULL, 'CP02PMUO-RII01-02-ADCPSL000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (32, 'Engineering Data', NULL, NULL, 11, NULL, 'CP02PMUO-RII01-00-ENG000000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (33, 'Engineering Data', NULL, NULL, 10, NULL, 'CP02PMUO-SBS01-00-ENG000000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (34, '3-Axis Motion Package', NULL, NULL, 10, NULL, 'CP02PMUO-SBS01-01-MOPAK0000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (35, 'CTD Profiler', NULL, NULL, 12, NULL, 'CP02PMUO-WFP01-03-CTDPFK000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (36, 'Engineering Data', NULL, NULL, 12, NULL, 'CP02PMUO-WFP01-00-ENG000000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (37, '3-Wavelength Fluorometer', NULL, NULL, 12, NULL, 'CP02PMUO-WFP01-04-FLORTK000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (38, 'Photosynthetically Available Radiation', NULL, NULL, 12, NULL, 'CP02PMUO-WFP01-05-PARADK000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (39, 'Dissolved Oxygen Fast Response', NULL, NULL, 12, NULL, 'CP02PMUO-WFP01-02-DOFSTK000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (40, '3-D Single Point Velocity Meter', NULL, NULL, 12, NULL, 'CP02PMUO-WFP01-01-VEL3DK000', 39.9399986, 70.7799988, NULL, NULL);
INSERT INTO instrument_deployments VALUES (41, 'Engineering Data', NULL, NULL, 5, NULL, 'CP04OSPM-SBS11-00-ENG000000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (42, '3-Axis Motion Package', NULL, NULL, 5, NULL, 'CP04OSPM-SBS11-02-MOPAK0000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (43, '3-D Single Point Velocity Meter', NULL, NULL, 6, NULL, 'CP04OSPM-WFP01-01-VEL3DK000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (44, 'CTD Profiler', NULL, NULL, 6, NULL, 'CP04OSPM-WFP01-03-CTDPFK000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (45, 'Engineering Data', NULL, NULL, 6, NULL, 'CP04OSPM-WFP01-00-ENG000000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (46, '3-Wavelength Fluorometer', NULL, NULL, 6, NULL, 'CP04OSPM-WFP01-04-FLORTK000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (47, 'Photosynthetically Available Radiation', NULL, NULL, 6, NULL, 'CP04OSPM-WFP01-05-PARADK000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (48, 'Dissolved Oxygen Fast Response', NULL, NULL, 6, NULL, 'CP04OSPM-WFP01-02-DOFSTK000', 39.9399986, 70.8799973, NULL, NULL);
INSERT INTO instrument_deployments VALUES (49, 'Engineering Data', NULL, NULL, 25, NULL, 'CP05MOAS-AV001-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (50, 'Photosynthetically Available Radiation', NULL, NULL, 25, NULL, 'CP05MOAS-AV001-06-PARADN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (51, 'Nitrate', NULL, NULL, 25, NULL, 'CP05MOAS-AV001-04-NUTNRN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (52, NULL, NULL, NULL, 25, NULL, 'CP05MOAS-AV001-03-CTDAVN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (53, '3-Wavelength Fluorometer', NULL, NULL, 25, NULL, 'CP05MOAS-AV001-01-FLORTN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (54, 'Dissolved Oxygen Stable Response', NULL, NULL, 25, NULL, 'CP05MOAS-AV001-02-DOSTAN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (55, 'Velocity Profiler (short range)', NULL, NULL, 25, NULL, 'CP05MOAS-AV001-05-ADCPAN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (56, '3-Wavelength Fluorometer', NULL, NULL, 26, NULL, 'CP05MOAS-AV002-01-FLORTN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (57, NULL, NULL, NULL, 26, NULL, 'CP05MOAS-AV002-03-CTDAVN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (58, 'Nitrate', NULL, NULL, 26, NULL, 'CP05MOAS-AV002-04-NUTNRN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (59, 'Velocity Profiler (short range)', NULL, NULL, 26, NULL, 'CP05MOAS-AV002-05-ADCPAN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (60, 'Photosynthetically Available Radiation', NULL, NULL, 26, NULL, 'CP05MOAS-AV002-06-PARADN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (61, 'Engineering Data', NULL, NULL, 26, NULL, 'CP05MOAS-AV002-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (62, 'Dissolved Oxygen Stable Response', NULL, NULL, 26, NULL, 'CP05MOAS-AV002-02-DOSTAN000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (63, '3-Wavelength Fluorometer', NULL, NULL, 19, NULL, 'CP05MOAS-GL001-02-FLORTM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (64, 'Engineering Data', NULL, NULL, 19, NULL, 'CP05MOAS-GL001-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (65, 'Photosynthetically Available Radiation', NULL, NULL, 19, NULL, 'CP05MOAS-GL001-05-PARADM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (66, 'Dissolved Oxygen Stable Response', NULL, NULL, 19, NULL, 'CP05MOAS-GL001-04-DOSTAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (67, 'CTD Profiler', NULL, NULL, 19, NULL, 'CP05MOAS-GL001-03-CTDGVM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (68, 'Velocity Profiler (short range)', NULL, NULL, 19, NULL, 'CP05MOAS-GL001-01-ADCPAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (69, 'Velocity Profiler (short range)', NULL, NULL, 20, NULL, 'CP05MOAS-GL002-01-ADCPAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (70, 'Photosynthetically Available Radiation', NULL, NULL, 20, NULL, 'CP05MOAS-GL002-05-PARADM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (71, 'Dissolved Oxygen Stable Response', NULL, NULL, 20, NULL, 'CP05MOAS-GL002-04-DOSTAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (72, 'CTD Profiler', NULL, NULL, 20, NULL, 'CP05MOAS-GL002-03-CTDGVM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (73, '3-Wavelength Fluorometer', NULL, NULL, 20, NULL, 'CP05MOAS-GL002-02-FLORTM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (74, 'Engineering Data', NULL, NULL, 20, NULL, 'CP05MOAS-GL002-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (75, 'CTD Profiler', NULL, NULL, 21, NULL, 'CP05MOAS-GL003-03-CTDGVM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (76, 'Dissolved Oxygen Stable Response', NULL, NULL, 21, NULL, 'CP05MOAS-GL003-04-DOSTAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (77, 'Velocity Profiler (short range)', NULL, NULL, 21, NULL, 'CP05MOAS-GL003-01-ADCPAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (78, 'Engineering Data', NULL, NULL, 21, NULL, 'CP05MOAS-GL003-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (79, 'Photosynthetically Available Radiation', NULL, NULL, 21, NULL, 'CP05MOAS-GL003-05-PARADM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (80, '3-Wavelength Fluorometer', NULL, NULL, 21, NULL, 'CP05MOAS-GL003-02-FLORTM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (81, 'Photosynthetically Available Radiation', NULL, NULL, 22, NULL, 'CP05MOAS-GL004-05-PARADM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (82, 'Velocity Profiler (short range)', NULL, NULL, 22, NULL, 'CP05MOAS-GL004-01-ADCPAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (83, '3-Wavelength Fluorometer', NULL, NULL, 22, NULL, 'CP05MOAS-GL004-02-FLORTM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (84, 'CTD Profiler', NULL, NULL, 22, NULL, 'CP05MOAS-GL004-03-CTDGVM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (85, 'Dissolved Oxygen Stable Response', NULL, NULL, 22, NULL, 'CP05MOAS-GL004-04-DOSTAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (86, 'Engineering Data', NULL, NULL, 22, NULL, 'CP05MOAS-GL004-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (87, 'Photosynthetically Available Radiation', NULL, NULL, 23, NULL, 'CP05MOAS-GL005-05-PARADM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (88, 'Dissolved Oxygen Stable Response', NULL, NULL, 23, NULL, 'CP05MOAS-GL005-04-DOSTAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (89, 'Engineering Data', NULL, NULL, 23, NULL, 'CP05MOAS-GL005-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (90, 'CTD Profiler', NULL, NULL, 23, NULL, 'CP05MOAS-GL005-03-CTDGVM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (91, '3-Wavelength Fluorometer', NULL, NULL, 23, NULL, 'CP05MOAS-GL005-02-FLORTM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (92, 'Velocity Profiler (short range)', NULL, NULL, 23, NULL, 'CP05MOAS-GL005-01-ADCPAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (93, '3-Wavelength Fluorometer', NULL, NULL, 24, NULL, 'CP05MOAS-GL006-02-FLORTM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (94, 'Dissolved Oxygen Stable Response', NULL, NULL, 24, NULL, 'CP05MOAS-GL006-04-DOSTAM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (95, 'Photosynthetically Available Radiation', NULL, NULL, 24, NULL, 'CP05MOAS-GL006-05-PARADM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (96, 'Engineering Data', NULL, NULL, 24, NULL, 'CP05MOAS-GL006-00-ENG000000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (97, 'CTD Profiler', NULL, NULL, 24, NULL, 'CP05MOAS-GL006-03-CTDGVM000', -999, -999, NULL, NULL);
INSERT INTO instrument_deployments VALUES (98, 'Velocity Profiler (short range)', NULL, NULL, 24, NULL, 'CP05MOAS-GL006-01-ADCPAM000', -999, -999, NULL, NULL);




INSERT INTO platform_deployments VALUES (5, NULL, NULL, NULL, 'CP04OSPM-SBS11', 39.9333344, -70.8784332, 1, NULL, 'Pioneer Offshore Profiler Mooring - Surface Buoy');
INSERT INTO platform_deployments VALUES (6, NULL, NULL, NULL, 'CP04OSPM-WFP01', 39.9333344, -70.8784332, 1, NULL, 'Pioneer Offshore Profiler Mooring - Wire-Following Profiler');
INSERT INTO platform_deployments VALUES (7, NULL, NULL, NULL, 'CP02PMUI-SBS01', 40.8973999, -70.6860123, 1, NULL, 'Pioneer Upstream Inshore Profiler Mooring - Surface Buoy');
INSERT INTO platform_deployments VALUES (8, NULL, NULL, NULL, 'CP02PMUI-RII01', 40.8973999, -70.6860123, 1, NULL, 'Pioneer Upstream Inshore Profiler Mooring - Mooring Riser');
INSERT INTO platform_deployments VALUES (9, NULL, NULL, NULL, 'CP02PMUI-WFP01', 40.8973999, -70.6860123, 1, NULL, 'Pioneer Upstream Inshore Profiler Mooring - Wire-Following Profiler');
INSERT INTO platform_deployments VALUES (10, NULL, NULL, NULL, 'CP02PMUO-SBS01', 39.9430199, -70.7700119, 1, NULL, 'Pioneer Upstream Offshore Profiler Mooring - Surface Buoy');
INSERT INTO platform_deployments VALUES (11, NULL, NULL, NULL, 'CP02PMUO-RII01', 39.9430199, -70.7700119, 1, NULL, 'Pioneer Upstream Offshore Profiler Mooring - Surface Buoy');
INSERT INTO platform_deployments VALUES (12, NULL, NULL, NULL, 'CP02PMUO-WFP01', 39.9430199, -70.7700119, 1, NULL, 'Pioneer Upstream Offshore Profiler Mooring - Wire-Following Profiler');
INSERT INTO platform_deployments VALUES (13, NULL, NULL, NULL, 'CP02PMCI-SBS01', 40.226532, -70.8779526, 1, NULL, 'Pioneer Central Inshore Profiler Mooring - Surface Buoy');
INSERT INTO platform_deployments VALUES (14, NULL, NULL, NULL, 'CP02PMCI-RII01', 40.226532, -70.8779526, 1, NULL, 'Pioneer Central Inshore Profiler Mooring - Mooring Riser');
INSERT INTO platform_deployments VALUES (15, NULL, NULL, NULL, 'CP02PMCI-WFP01', 40.226532, -70.8779526, 1, NULL, 'Pioneer Central Inshore Profiler Mooring - Wire-Following Profiler');
INSERT INTO platform_deployments VALUES (16, NULL, NULL, NULL, 'CP02PMCO-SBS01', 40.1012344, -70.8876801, 1, NULL, 'Pioneer Central Offshore Profiler Mooring - Surface Buoy');
INSERT INTO platform_deployments VALUES (17, NULL, NULL, NULL, 'CP02PMCO-RII01', 40.1012344, -70.8876801, 1, NULL, 'Pioneer Central Offshore Profiler Mooring - Mooring Riser');
INSERT INTO platform_deployments VALUES (18, NULL, NULL, NULL, 'CP02PMCO-WFP01', 40.1012344, -70.8876801, 1, NULL, 'Pioneer Central Offshore Profiler Mooring - Wire-Following Profiler');
INSERT INTO platform_deployments VALUES (19, NULL, NULL, NULL, 'CP05MOAS-GL001', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile Coastal Glider #1');
INSERT INTO platform_deployments VALUES (20, NULL, NULL, NULL, 'CP05MOAS-GL002', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile Coastal Glider #2');
INSERT INTO platform_deployments VALUES (21, NULL, NULL, NULL, 'CP05MOAS-GL003', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile Coastal Glider #3');
INSERT INTO platform_deployments VALUES (22, NULL, NULL, NULL, 'CP05MOAS-GL004', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile Coastal Glider #4');
INSERT INTO platform_deployments VALUES (23, NULL, NULL, NULL, 'CP05MOAS-GL005', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile Coastal Glider #5');
INSERT INTO platform_deployments VALUES (24, NULL, NULL, NULL, 'CP05MOAS-GL006', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile Coastal Glider #6');
INSERT INTO platform_deployments VALUES (25, NULL, NULL, NULL, 'CP05MOAS-AV001', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile AUV #1');
INSERT INTO platform_deployments VALUES (26, NULL, NULL, NULL, 'CP05MOAS-AV002', 40.0833015, -70.25, 1, NULL, 'Pioneer Mobile AUV #2');
END;
