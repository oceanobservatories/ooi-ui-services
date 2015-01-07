--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

--
-- Name: instrumentnames; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

SET search_path = public, pg_catalog;

CREATE FUNCTION f_concat_rd(array_type text, array_name text, site text, platform text, assembly text, instrument_name text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF assembly IS NOT NULL AND instrument_name IS NOT NULL THEN
        RETURN concat(array_type, ' ', array_name, ' ', site, ' ', platform, ' - ', assembly, ' - ', instrument_name);
    ELSIF assembly IS NOT NULL AND instrument_name IS NULL THEN
        RETURN concat(array_type, ' ', array_name, ' ', site, ' ', platform, ' - ', assembly);
    ELSE
        RETURN concat(array_type, ' ', array_name, ' ', site, ' ', platform);
    END IF;
END
$$;

--
-- Name: f_display_name(text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION f_display_name(reference_designator text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
DECLARE
    p_n platformnames%rowtype;
    i_n instrumentnames%rowtype;
    assy TEXT;
    inst TEXT;
    platform_text TEXT;
    rd_len INT;
BEGIN
    rd_len := char_length(reference_designator);

    IF NOT reference_designator ~ 'MOAS' THEN
        SELECT * INTO p_n FROM platformnames WHERE platformnames.reference_designator ~ SUBSTRING($1 FROM 0 FOR 15) LIMIT 1;
    ELSE 
        SELECT * INTO p_n FROM platformnames WHERE platformnames.reference_designator ~ SUBSTRING($1 FROM 0 FOR 9) LIMIT 1;
    END IF;

    IF NOT FOUND THEN
        RETURN reference_designator;
    END IF;

    IF rd_len = 8 THEN
        RETURN f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, NULL, NULL);
    ELSIF rd_len = 14 THEN
        assy := SUBSTRING(reference_designator FROM 10 FOR 5);

        IF assy ~ 'AV[0-9]{3}' THEN
            platform_text := 'AUV ' || SUBSTRING(assy FROM 4 FOR 3);
        ELSIF assy ~ 'GL[0-9]{3}' THEN
            platform_text := 'Glider ' || SUBSTRING(assy FROM 4 FOR 3);
        ELSE
            platform_text := p_n.assembly;
        END IF;
        
        RETURN f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, platform_text, NULL);
    ELSIF rd_len = 27 THEN
        inst := SUBSTRING(reference_designator FROM 19 FOR 5);
        assy := SUBSTRING(reference_designator FROM 10 FOR 5);
        IF assy ~ 'AV[0-9]{3}' THEN
            platform_text := 'AUV ' || SUBSTRING(assy FROM 4 FOR 3);
        ELSIF assy ~ 'GL[0-9]{3}' THEN
            platform_text := 'Glider ' || SUBSTRING(assy FROM 4 FOR 3);
        ELSE
            platform_text := p_n.assembly;
        END IF;

        SELECT * INTO i_n FROM instrumentnames WHERE instrumentnames.instrument_class = inst;
        IF NOT FOUND THEN
            RETURN f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, platform_text, inst);
        END IF;
        RETURN f_concat_rd(p_n.array_type, p_n.array_name, p_n.site, p_n.platform, platform_text, i_n.display_name);
    END IF;

    RETURN NULL;

END
$_$;

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE instrumentnames (
    id integer NOT NULL,
    instrument_class text,
    display_name text
);


--
-- Name: instrumentnames_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE instrumentnames_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: instrumentnames_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE instrumentnames_id_seq OWNED BY instrumentnames.id;


--
-- Name: platformnames; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE platformnames (
    id integer NOT NULL,
    reference_designator text,
    array_type text,
    array_name text,
    site text,
    platform text,
    assembly text
);


--
-- Name: platformnames_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE platformnames_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: platformnames_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE platformnames_id_seq OWNED BY platformnames.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY instrumentnames ALTER COLUMN id SET DEFAULT nextval('instrumentnames_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY platformnames ALTER COLUMN id SET DEFAULT nextval('platformnames_id_seq'::regclass);


--
-- Data for Name: instrumentnames; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO instrumentnames VALUES (1, 'ADCPA', 'Velocity Profiler (short range) for mobile assets');
INSERT INTO instrumentnames VALUES (2, 'ADCPS', 'Velocity Profiler (long range)');
INSERT INTO instrumentnames VALUES (3, 'ADCPT', 'Velocity Profiler (short range)');
INSERT INTO instrumentnames VALUES (4, 'BOTPT', 'Bottom Pressure and Tilt');
INSERT INTO instrumentnames VALUES (5, 'CAMDS', 'Digital Still Camera with Strobes');
INSERT INTO instrumentnames VALUES (6, 'CAMHD', 'HD Digital Video Camera with Strobes');
INSERT INTO instrumentnames VALUES (7, 'CTDAV', 'CTD AUV');
INSERT INTO instrumentnames VALUES (8, 'CTDBP', 'CTD Pumped');
INSERT INTO instrumentnames VALUES (9, 'CTDGV', 'CTD Glider');
INSERT INTO instrumentnames VALUES (10, 'CTDMO', 'CTD Mooring (Inductive)');
INSERT INTO instrumentnames VALUES (11, 'CTDPF', 'CTD Profiler');
INSERT INTO instrumentnames VALUES (12, 'DOFST', 'Dissolved Oxygen Fast Response');
INSERT INTO instrumentnames VALUES (13, 'DOSTA', 'Dissolved Oxygen Stable Response');
INSERT INTO instrumentnames VALUES (14, 'FDCHP', 'Direct Covariance Flux');
INSERT INTO instrumentnames VALUES (15, 'FLOBN', 'Benthic Fluid Flow');
INSERT INTO instrumentnames VALUES (16, 'FLORD', '2-Wavelength Fluorometer');
INSERT INTO instrumentnames VALUES (17, 'FLORT', '3-Wavelength Fluorometer');
INSERT INTO instrumentnames VALUES (18, 'HPIES', 'Horizontal Electric Field, Pressure and Inverted Echo Sounder');
INSERT INTO instrumentnames VALUES (19, 'HYDBB', 'Broadband Acoustic Receiver (Hydrophone)');
INSERT INTO instrumentnames VALUES (20, 'HYDLF', 'Low Frequency Broadband Acoustic Receiver (Hydrophone) on Seafloor');
INSERT INTO instrumentnames VALUES (21, 'MASSP', 'Mass Spectrometer');
INSERT INTO instrumentnames VALUES (22, 'METBK', 'Bulk Meteorology Instrument Package');
INSERT INTO instrumentnames VALUES (23, 'NUTNR', 'Nitrate');
INSERT INTO instrumentnames VALUES (24, 'OBSBB', 'Broadband Ocean Bottom Seismometer');
INSERT INTO instrumentnames VALUES (25, 'OBSBK', 'Broadband Ocean Bottom Seismometer');
INSERT INTO instrumentnames VALUES (26, 'OBSSP', 'Short-Period Ocean Bottom Seismometer');
INSERT INTO instrumentnames VALUES (27, 'OPTAA', 'Absorption Spectrophotometer');
INSERT INTO instrumentnames VALUES (28, 'OSMOI', 'Osmosis-Based Water Sampler');
INSERT INTO instrumentnames VALUES (29, 'PARAD', 'Photosynthetically Available Radiation');
INSERT INTO instrumentnames VALUES (30, 'PCO2A', 'pCO2 Air-Sea');
INSERT INTO instrumentnames VALUES (31, 'PCO2W', 'pCO2 Water');
INSERT INTO instrumentnames VALUES (32, 'PHSEN', 'Seawater pH');
INSERT INTO instrumentnames VALUES (33, 'PPSDN', 'Particulate DNA Sampler');
INSERT INTO instrumentnames VALUES (34, 'PRESF', 'Seafloor Pressure');
INSERT INTO instrumentnames VALUES (35, 'PREST', 'Tidal Seafloor Pressure');
INSERT INTO instrumentnames VALUES (36, 'RASFL', 'Hydrothermal Vent Fluid Interactive Sampler');
INSERT INTO instrumentnames VALUES (37, 'SPKIR', 'Spectral Irradiance');
INSERT INTO instrumentnames VALUES (38, 'THSPH', 'Hydrothermal Vent Fluid In-situ Chemistry');
INSERT INTO instrumentnames VALUES (39, 'TMPSF', 'Diffuse Vent Fluid 3-D Temperature Array');
INSERT INTO instrumentnames VALUES (40, 'TRHPH', 'Hydrothermal Vent Fluid Temperature and Resistivity');
INSERT INTO instrumentnames VALUES (41, 'VADCP', '5-Beam, 600 kHz Acoustic Doppler Current Profiler (= 50 m range)');
INSERT INTO instrumentnames VALUES (42, 'VEL3D', '3-D Single Point Velocity Meter');
INSERT INTO instrumentnames VALUES (43, 'VELPT', 'Single Point Velocity Meter');
INSERT INTO instrumentnames VALUES (44, 'WAVSS', 'Surface Wave Spectra');
INSERT INTO instrumentnames VALUES (45, 'ZPLSC', 'Bio-acoustic Sonar (Coastal)');
INSERT INTO instrumentnames VALUES (46, 'ZPLSG', 'Bio-acoustic Sonar (Global)');
INSERT INTO instrumentnames VALUES (47, 'ENG00', 'Engineering Data');
INSERT INTO instrumentnames VALUES (48, 'STCEN', 'Engineering Data');
INSERT INTO instrumentnames VALUES (49, 'MOPAK', '3-Axis Motion Pack');


--
-- Name: instrumentnames_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('instrumentnames_id_seq', 49, true);


--
-- Data for Name: platformnames; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO platformnames VALUES (108, 'CE01ISSM', 'Coastal', 'Endurance', 'OR Inshore', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (109, 'CE01ISSM-SBD17', 'Coastal', 'Endurance', 'OR Inshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (110, 'CE01ISSM-RID16', 'Coastal', 'Endurance', 'OR Inshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (111, 'CE01ISSM-MFD35', 'Coastal', 'Endurance', 'OR Inshore', 'Surface Mooring', 'MFN Base/Anchor');
INSERT INTO platformnames VALUES (112, 'CE01ISSM-MFD37', 'Coastal', 'Endurance', 'OR Inshore', 'Surface Mooring', 'MFN Base/Anchor');
INSERT INTO platformnames VALUES (113, 'CE01ISSM-MFD00', 'Coastal', 'Endurance', 'OR Inshore', 'Surface Mooring', 'MFN Base/Anchor');
INSERT INTO platformnames VALUES (114, 'CE01ISSP', 'Coastal', 'Endurance', 'OR Inshore', 'Surface-Piercing Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (115, 'CE01ISSP-SP001', 'Coastal', 'Endurance', 'OR Inshore', 'Surface-Piercing Profiler Mooring', 'Surface-Piercing Profiler');
INSERT INTO platformnames VALUES (116, 'CE02SHBP', 'Coastal', 'Endurance', 'OR Shelf', 'Benthic Experiment Package', NULL);
INSERT INTO platformnames VALUES (117, 'CE02SHBP-MJ01C', 'Coastal', 'Endurance', 'OR Shelf', 'Benthic Experiment Package', 'Junction Box');
INSERT INTO platformnames VALUES (118, 'CE02SHBP-LJ01D', 'Coastal', 'Endurance', 'OR Shelf', 'Benthic Experiment Package', 'Junction Box');
INSERT INTO platformnames VALUES (119, 'CE02SHSM', 'Coastal', 'Endurance', 'OR Shelf', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (120, 'CE02SHSM-SBD11', 'Coastal', 'Endurance', 'OR Shelf', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (121, 'CE02SHSM-SBD12', 'Coastal', 'Endurance', 'OR Shelf', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (122, 'CE02SHSM-RID26', 'Coastal', 'Endurance', 'OR Shelf', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (123, 'CE02SHSM-RID27', 'Coastal', 'Endurance', 'OR Shelf', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (124, 'CE02SHSP', 'Coastal', 'Endurance', 'OR Shelf', 'Surface-Piercing Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (125, 'CE02SHSP-SP001', 'Coastal', 'Endurance', 'OR Shelf', 'Surface-Piercing Profiler Mooring', 'Surface-Piercing Profiler');
INSERT INTO platformnames VALUES (126, 'CE04OOPI', 'Coastal', 'Endurance', 'OR Offshore', 'Primary Node', NULL);
INSERT INTO platformnames VALUES (127, 'CE04OOPI-PN01C', 'Coastal', 'Endurance', 'OR Offshore', 'Primary Node', 'Primary Node');
INSERT INTO platformnames VALUES (128, 'CE04OSBP', 'Coastal', 'Endurance', 'OR Offshore', 'Benthic Experiment Package', NULL);
INSERT INTO platformnames VALUES (129, 'CE04OSBP-LV01C', 'Coastal', 'Endurance', 'OR Offshore', 'Benthic Experiment Package', 'Junction Box');
INSERT INTO platformnames VALUES (130, 'CE04OSBP-LJ01C', 'Coastal', 'Endurance', 'OR Offshore', 'Benthic Experiment Package', 'Junction Box');
INSERT INTO platformnames VALUES (131, 'CE04OPS', 'Coastal', 'Endurance', 'OR Offshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (132, 'CE04OSPS-PC01B', 'Coastal', 'Endurance', 'OR Offshore', 'Profiler Mooring', 'Interface Controller');
INSERT INTO platformnames VALUES (133, 'CE04OSPS-SC03A', 'Coastal', 'Endurance', 'OR Offshore', 'Profiler Mooring', 'Profiler Controller');
INSERT INTO platformnames VALUES (134, 'CE04OSPS-SF01B', 'Coastal', 'Endurance', 'OR Offshore', 'Profiler Mooring', 'Profiler');
INSERT INTO platformnames VALUES (135, 'CE04OSPD', 'Coastal', 'Endurance', 'OR Offshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (136, 'CE04OSPD-PD01B', 'Coastal', 'Endurance', 'OR Offshore', 'Profiler Mooring', 'Profiler Dock');
INSERT INTO platformnames VALUES (137, 'CE04OSPD-DP01B', 'Coastal', 'Endurance', 'OR Offshore', 'Profiler Mooring', 'Profiler');
INSERT INTO platformnames VALUES (138, 'CE04OSPI', 'Cabled', 'Endurance', 'OR Shelf', 'Primary Node', NULL);
INSERT INTO platformnames VALUES (139, 'CE04OSPI-PN01D', 'Cabled', 'Endurance', 'OR Shelf', 'Primary Node', 'Primary Node');
INSERT INTO platformnames VALUES (140, 'CE04OSSM', 'Coastal', 'Endurance', 'OR Offshore', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (141, 'CE04OSSM-SBD11', 'Coastal', 'Endurance', 'OR Offshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (142, 'CE04OSSM-SBD12', 'Coastal', 'Endurance', 'OR Offshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (143, 'CE04OSSM-RID26', 'Coastal', 'Endurance', 'OR Offshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (144, 'CE04OSSM-RID27', 'Coastal', 'Endurance', 'OR Offshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (146, 'CE06ISSM', 'Coastal', 'Endurance', 'WA Inshore', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (147, 'CE06ISSM-SBD17', 'Coastal', 'Endurance', 'WA Inshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (148, 'CE06ISSM-RID16', 'Coastal', 'Endurance', 'WA Inshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (149, 'CE06ISSM-MFD35', 'Coastal', 'Endurance', 'WA Inshore', 'Surface Mooring', 'MFN Base/Anchor');
INSERT INTO platformnames VALUES (150, 'CE06ISSM-MFD37', 'Coastal', 'Endurance', 'WA Inshore', 'Surface Mooring', 'MFN Base/Anchor');
INSERT INTO platformnames VALUES (151, 'CE06ISSM-MFD00', 'Coastal', 'Endurance', 'WA Inshore', 'Surface Mooring', 'MFN Base/Anchor');
INSERT INTO platformnames VALUES (152, 'CE06ISSP', 'Coastal', 'Endurance', 'WA Inshore', 'Surface-Piercing Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (153, 'CE06ISSP-SP001', 'Coastal', 'Endurance', 'WA Inshore', 'Surface-Piercing Profiler Mooring', 'Surface-Piercing Profiler');
INSERT INTO platformnames VALUES (154, 'CE07SHSM', 'Coastal', 'Endurance', 'WA Shelf', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (155, 'CE07SHSM-SBD11', 'Coastal', 'Endurance', 'WA Shelf', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (156, 'CE07SHSM-SBD12', 'Coastal', 'Endurance', 'WA Shelf', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (157, 'CE07SHSM-RID26', 'Coastal', 'Endurance', 'WA Shelf', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (158, 'CE07SHSM-RID27', 'Coastal', 'Endurance', 'WA Shelf', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (159, 'CE07SHSP', 'Coastal', 'Endurance', 'WA Shelf', 'Surface-Piercing Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (160, 'CE07SHSP-SP001', 'Coastal', 'Endurance', 'WA Shelf', 'Surface-Piercing Profiler Mooring', 'Surface-Piercing Profiler');
INSERT INTO platformnames VALUES (161, 'CE09OSPM', 'Coastal', 'Endurance', 'WA Offshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (162, 'CE09OSPM-WF001', 'Coastal', 'Endurance', 'WA Offshore', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (163, 'CE09OSSM', 'Coastal', 'Endurance', 'WA Offshore', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (164, 'CE09OSSM-SBD11', 'Coastal', 'Endurance', 'WA Offshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (165, 'CE09OSSM-SBD12', 'Coastal', 'Endurance', 'WA Offshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (166, 'CE09OSSM-RID26', 'Coastal', 'Endurance', 'WA Offshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (167, 'CE09OSSM-RID27', 'Coastal', 'Endurance', 'WA Offshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (168, 'CP01CNSM', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (169, 'CP01CNSM-SBD11', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (170, 'CP01CNSM-SBD12', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (171, 'CP01CNSM-RID26', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (172, 'CP01CNSM-RID27', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (173, 'CP01CNSM-MFD35', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (174, 'CP01CNSM-MFD37', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (175, 'CP01CNSM-MFD00', 'Coastal', 'Pioneer', 'Central', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (176, 'CP01CNSP', 'Coastal', 'Pioneer', 'Central', 'Surface-Piercing Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (177, 'CP01CNSP-SP001', 'Coastal', 'Pioneer', 'Central', 'Surface-Piercing Profiler Mooring', 'Surface-Piercing Profiler');
INSERT INTO platformnames VALUES (178, 'CP02PMCI', 'Coastal', 'Pioneer', 'Central Inshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (179, 'CP02PMCI-SBS01', 'Coastal', 'Pioneer', 'Central Inshore', 'Profiler Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (180, 'CP02PMCI-RII01', 'Coastal', 'Pioneer', 'Central Inshore', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (181, 'CP02PMCI-WFP01', 'Coastal', 'Pioneer', 'Central Inshore', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (182, 'CP02PMCO', 'Coastal', 'Pioneer', 'Central Offshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (183, 'CP02PMCO-SBS01', 'Coastal', 'Pioneer', 'Central Offshore', 'Profiler Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (321, 'CE05MOAS', 'Coastal', 'Pioneer', 'Mobile', '(Coastal)', 'Glider');
INSERT INTO platformnames VALUES (184, 'CP02PMCO-RII01', 'Coastal', 'Pioneer', 'Central Offshore', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (185, 'CP02PMCO-WFP01', 'Coastal', 'Pioneer', 'Central Offshore', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (186, 'CP02PMUI', 'Coastal', 'Pioneer', 'Upstream Inshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (187, 'CP02PMUI-SBS01', 'Coastal', 'Pioneer', 'Upstream Inshore', 'Profiler Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (188, 'CP02PMUI-RII01', 'Coastal', 'Pioneer', 'Upstream Inshore', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (189, 'CP02PMUI-WFP01', 'Coastal', 'Pioneer', 'Upstream Inshore', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (190, 'CP02PMUO', 'Coastal', 'Pioneer', 'Upstream Offshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (191, 'CP02PMUO-SBS01', 'Coastal', 'Pioneer', 'Upstream Offshore', 'Profiler Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (192, 'CP02PMUO-RII01', 'Coastal', 'Pioneer', 'Upstream Offshore', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (193, 'CP02PMUO-WFP01', 'Coastal', 'Pioneer', 'Upstream Offshore', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (194, 'CP03ISSM', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (195, 'CP03ISSM-SBD11', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (196, 'CP03ISSM-SBD12', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (197, 'CP03ISSM-RID26', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (198, 'CP03ISSM-RID27', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (199, 'CP03ISSM-MFD35', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (200, 'CP03ISSM-MFD37', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (201, 'CP03ISSM-MFD00', 'Coastal', 'Pioneer', 'Inshore', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (202, 'CP03ISSP', 'Coastal', 'Pioneer', 'Inshore', 'Surface-Piercing Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (203, 'CP03ISSP-SP001', 'Coastal', 'Pioneer', 'Inshore', 'Surface-Piercing Profiler Mooring', 'Surface-Piercing Profiler');
INSERT INTO platformnames VALUES (204, 'CP04OSPM', 'Coastal', 'Pioneer', 'Offshore', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (205, 'CP04OSPM-SBS11', 'Coastal', 'Pioneer', 'Offshore', 'Profiler Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (206, 'CP04OSPM-WFP01', 'Coastal', 'Pioneer', 'Offshore', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (207, 'CP04OSSM', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (208, 'CP04OSSM-SBD11', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (209, 'CP04OSSM-SBD12', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (210, 'CP04OSSM-RID26', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (211, 'CP04OSSM-RID27', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (212, 'CP04OSSM-MFD35', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (213, 'CP04OSSM-MFD37', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (322, 'CP05MOAS', 'Coastal', 'Pioneer', 'Mobile', '(Coastal)', 'Glider/AUV');
INSERT INTO platformnames VALUES (323, 'GA05MOAS', 'Global', 'Argentine Basin', 'Mobile', '(Open Ocean)', 'Glider');
INSERT INTO platformnames VALUES (324, 'GI05MOAS', 'Global', 'Irminger Sea', 'Mobile', '(Open Ocean)', 'Glider');
INSERT INTO platformnames VALUES (325, 'GP05MOAS', 'Global', 'Station Papa', 'Mobile', '(Open Ocean)', 'Glider');
INSERT INTO platformnames VALUES (326, 'GS05MOAS', 'Global', 'Southern Ocean', 'Mobile', '(Open Ocean)', 'Glider');
INSERT INTO platformnames VALUES (327, 'RS00ENGC-XX00X', 'Cabled', 'or', 'Testing', 'Platform', NULL);
INSERT INTO platformnames VALUES (328, 'RS01BATH-XX00X', 'Cabled', 'Bathtub', 'Testing', 'Platform', NULL);
INSERT INTO platformnames VALUES (214, 'CP04OSSM-MFD00', 'Coastal', 'Pioneer', 'Offshore', 'Surface Mooring', 'Multi-Function Node');
INSERT INTO platformnames VALUES (215, 'RS01HSPI', 'Cabled', 'Continental Margin', 'Slope Base', 'Primary Node', NULL);
INSERT INTO platformnames VALUES (216, 'RS01HSPI-PN01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Primary Node', 'Primary Node');
INSERT INTO platformnames VALUES (217, 'RS01SBPS', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (218, 'RS01SBPS-LV01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', 'Junction Box');
INSERT INTO platformnames VALUES (219, 'RS01SBPS-PC01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', 'Interface Controller');
INSERT INTO platformnames VALUES (220, 'RS01SBPS-SC01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', 'Profiler Controller');
INSERT INTO platformnames VALUES (221, 'RS01SBPS-SF01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', 'Profiler');
INSERT INTO platformnames VALUES (222, 'RS01SBPS-LJ01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', 'Junction Box');
INSERT INTO platformnames VALUES (223, 'RS01SBPD', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (224, 'RS01SBPD-PD01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', 'Profiler Dock');
INSERT INTO platformnames VALUES (225, 'RS01SBPD-DP01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Profiler Mooring', 'Profiler');
INSERT INTO platformnames VALUES (226, 'RS01SLBS', 'Cabled', 'Continental Margin', 'Slope Base', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (227, 'RS01SLBS-MJ01A', 'Cabled', 'Continental Margin', 'Slope Base', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (228, 'RS01SUM1', 'Cabled', 'Continental Margin', 'Southern Hydrate Ridge Summit', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (229, 'RS01SUM1-LV01B', 'Cabled', 'Continental Margin', 'Southern Hydrate Ridge Summit', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (230, 'RS01SUM1-LJ01B', 'Cabled', 'Continental Margin', 'Southern Hydrate Ridge Summit', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (231, 'RS01SUM2', 'Cabled', 'Continental Margin', 'Southern Hydrate Ridge Summit', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (232, 'RS01SUM2-MJ01B', 'Cabled', 'Continental Margin', 'Southern Hydrate Ridge Summit', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (233, 'RS02HRPI', 'Cabled', 'Continental Margin', 'Hydrate Ridge', 'Primary Node', NULL);
INSERT INTO platformnames VALUES (234, 'RS02HRPI-PN01B', 'Cabled', 'Continental Margin', 'Hydrate Ridge', 'Primary Node', 'Primary Node');
INSERT INTO platformnames VALUES (235, 'RS03ABPI', 'Cabled', 'Axial Seamount', 'Axial Base', 'Primary Node', NULL);
INSERT INTO platformnames VALUES (236, 'RS03ABPI-PN03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Primary Node', 'Primary Node');
INSERT INTO platformnames VALUES (237, 'RS03ASHS', 'Cabled', 'Axial Seamount', 'ASHES', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (238, 'RS03ASHS-MJ03B', 'Cabled', 'Axial Seamount', 'ASHES', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (239, 'RS03ASHS-ID03A', 'Cabled', 'Axial Seamount', 'ASHES', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (240, 'RS03AXBS', 'Cabled', 'Axial Seamount', 'Axial Base', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (241, 'RS03AXBS-MJ03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (242, 'RS03AXPS', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (243, 'RS03AXPS-LV03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', 'Junction Box');
INSERT INTO platformnames VALUES (244, 'RS03AXPS-PC03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', 'Interface Controller');
INSERT INTO platformnames VALUES (245, 'RS03AXPS-SC03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', 'Profiler Controller');
INSERT INTO platformnames VALUES (246, 'RS03AXPS-SF03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', 'Profiler');
INSERT INTO platformnames VALUES (247, 'RS03AXPS-LJ03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', 'Junction Box');
INSERT INTO platformnames VALUES (248, 'RS03AXPD', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (249, 'RS03AXPD-PD03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', 'Profiler Dock');
INSERT INTO platformnames VALUES (250, 'RS03AXPD-DP03A', 'Cabled', 'Axial Seamount', 'Axial Base', 'Profiler Mooring', 'Profiler');
INSERT INTO platformnames VALUES (251, 'RS03CCAL', 'Cabled', 'Axial Seamount', 'Central Caldera', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (252, 'RS03CCAL-MJ03F', 'Cabled', 'Axial Seamount', 'Central Caldera', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (253, 'RS03ECAL', 'Cabled', 'Axial Seamount', 'Eastern Caldera', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (254, 'RS03ECAL-MJ03E', 'Cabled', 'Axial Seamount', 'Eastern Caldera', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (255, 'RS03INT1', 'Cabled', 'Axial Seamount', 'International District', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (256, 'RS03INT1-MJ03C', 'Cabled', 'Axial Seamount', 'International District', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (257, 'RS03INT2', 'Cabled', 'Axial Seamount', 'International District', 'Junction Box', NULL);
INSERT INTO platformnames VALUES (258, 'RS03INT2-MJ03D', 'Cabled', 'Axial Seamount', 'International District', 'Junction Box', 'Junction Box');
INSERT INTO platformnames VALUES (259, 'RS04ASPI', 'Cabled', 'Axial Seamount', 'Axial Summit', 'Primary Node', NULL);
INSERT INTO platformnames VALUES (260, 'RS04ASPI-PN03B', 'Cabled', 'Axial Seamount', 'Axial Summit', 'Primary Node', 'Primary Node');
INSERT INTO platformnames VALUES (261, 'RS05MPPI', 'Cabled', 'Mid Plate', 'Primary Infrastructure', 'Primary Node', NULL);
INSERT INTO platformnames VALUES (262, 'RS05MPPI-PN05A', 'Cabled', 'Mid Plate', 'Primary Infrastructure', 'Primary Node', 'Primary Node');
INSERT INTO platformnames VALUES (263, 'GA01SUMO', 'Global', 'Argentine Basin', 'Apex', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (264, 'GA01SUMO-SBD11', 'Global', 'Argentine Basin', 'Apex', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (265, 'GA01SUMO-SBD12', 'Global', 'Argentine Basin', 'Apex', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (266, 'GA01SUMO-RID16', 'Global', 'Argentine Basin', 'Apex', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (267, 'GA01SUMO-RII11', 'Global', 'Argentine Basin', 'Apex', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (268, 'GA02HYPM', 'Global', 'Argentine Basin', 'Apex', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (269, 'GA02HYPM-MPC04', 'Global', 'Argentine Basin', 'Apex', 'Profiler Mooring', 'Submerged Buoy');
INSERT INTO platformnames VALUES (270, 'GA02HYPM-RIS01', 'Global', 'Argentine Basin', 'Apex', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (271, 'GA02HYPM-WFP02', 'Global', 'Argentine Basin', 'Apex', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (272, 'GA02HYPM-WFP03', 'Global', 'Argentine Basin', 'Apex', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (273, 'GA03FLMA', 'Global', 'Argentine Basin', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (274, 'GA03FLMA-RIS01', 'Global', 'Argentine Basin', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (275, 'GA03FLMA-RIS02', 'Global', 'Argentine Basin', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (276, 'GA03FLMB', 'Global', 'Argentine Basin', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (277, 'GA03FLMB-RIS01', 'Global', 'Argentine Basin', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (278, 'GA03FLMB-RIS02', 'Global', 'Argentine Basin', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (279, 'GI01SUMO', 'Global', 'Irminger Sea', 'Apex', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (280, 'GI01SUMO-SBD11', 'Global', 'Irminger Sea', 'Apex', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (281, 'GI01SUMO-SBD12', 'Global', 'Irminger Sea', 'Apex', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (282, 'GI01SUMO-RID16', 'Global', 'Irminger Sea', 'Apex', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (283, 'GI01SUMO-RII11', 'Global', 'Irminger Sea', 'Apex', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (284, 'GI02HYPM', 'Global', 'Irminger Sea', 'Apex', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (285, 'GI02HYPM-MPC04', 'Global', 'Irminger Sea', 'Apex', 'Profiler Mooring', 'Submerged Buoy');
INSERT INTO platformnames VALUES (286, 'GI02HYPM-RIS01', 'Global', 'Irminger Sea', 'Apex', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (287, 'GI02HYPM-WFP02', 'Global', 'Irminger Sea', 'Apex', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (288, 'GI03FLMA', 'Global', 'Irminger Sea', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (289, 'GI03FLMA-RIS01', 'Global', 'Irminger Sea', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (290, 'GI03FLMA-RIS02', 'Global', 'Irminger Sea', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (291, 'GI03FLMB', 'Global', 'Irminger Sea', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (292, 'GI03FLMB-RIS01', 'Global', 'Irminger Sea', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (293, 'GI03FLMB-RIS02', 'Global', 'Irminger Sea', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (294, 'GP02HYPM', 'Global', 'Station Papa', 'Apex', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (295, 'GP02HYPM-MPC04', 'Global', 'Station Papa', 'Apex', 'Profiler Mooring', 'Submerged Buoy');
INSERT INTO platformnames VALUES (296, 'GP02HYPM-RIS01', 'Global', 'Station Papa', 'Apex', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (297, 'GP02HYPM-WFP02', 'Global', 'Station Papa', 'Apex', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (298, 'GP02HYPM-WFP03', 'Global', 'Station Papa', 'Apex', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (299, 'GP03FLMA', 'Global', 'Station Papa', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (300, 'GP03FLMA-RIS01', 'Global', 'Station Papa', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (301, 'GP03FLMA-RIS02', 'Global', 'Station Papa', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (302, 'GP03FLMB', 'Global', 'Station Papa', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (303, 'GP03FLMB-RIS01', 'Global', 'Station Papa', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (304, 'GP03FLMB-RIS02', 'Global', 'Station Papa', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (305, 'GS01SUMO', 'Global', 'Southern Ocean', 'Apex', 'Surface Mooring', NULL);
INSERT INTO platformnames VALUES (306, 'GS01SUMO-SBD11', 'Global', 'Southern Ocean', 'Apex', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (307, 'GS01SUMO-SBD12', 'Global', 'Southern Ocean', 'Apex', 'Surface Mooring', 'Surface Buoy');
INSERT INTO platformnames VALUES (308, 'GS01SUMO-RID16', 'Global', 'Southern Ocean', 'Apex', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (309, 'GS01SUMO-RII11', 'Global', 'Southern Ocean', 'Apex', 'Surface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (310, 'GS02HYPM', 'Global', 'Southern Ocean', 'Apex', 'Profiler Mooring', NULL);
INSERT INTO platformnames VALUES (311, 'GS02HYPM-MPC04', 'Global', 'Southern Ocean', 'Apex', 'Profiler Mooring', 'Submerged Buoy');
INSERT INTO platformnames VALUES (312, 'GS02HYPM-RIS01', 'Global', 'Southern Ocean', 'Apex', 'Profiler Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (313, 'GS02HYPM-WFP02', 'Global', 'Southern Ocean', 'Apex', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (314, 'GS02HYPM-WFP03', 'Global', 'Southern Ocean', 'Apex', 'Profiler Mooring', 'Wire-Following Profiler');
INSERT INTO platformnames VALUES (315, 'GS03FLMA', 'Global', 'Southern Ocean', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (316, 'GS03FLMA-RIS01', 'Global', 'Southern Ocean', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (317, 'GS03FLMA-RIS02', 'Global', 'Southern Ocean', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (318, 'GS03FLMB', 'Global', 'Southern Ocean', 'Flanking', 'Subsurface Mooring', NULL);
INSERT INTO platformnames VALUES (319, 'GS03FLMB-RIS01', 'Global', 'Southern Ocean', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');
INSERT INTO platformnames VALUES (320, 'GS03FLMB-RIS02', 'Global', 'Southern Ocean', 'Flanking', 'Subsurface Mooring', 'Mooring Riser');


--
-- Name: platformnames_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('platformnames_id_seq', 328, true);


--
-- Name: instrumentnames_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY instrumentnames
    ADD CONSTRAINT instrumentnames_pkey PRIMARY KEY (id);


--
-- Name: platformnames_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY platformnames
    ADD CONSTRAINT platformnames_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

