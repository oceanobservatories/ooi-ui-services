-- OOI UI Schema
-- Note: Execute bulk insert of data

-- START HEADER DEFINITIONS
--
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = ooiui, public, pg_catalog;

-- user_event_notifications

-- Create two TEST system_event_definitions (for alert alarms processing)
-- Reference designator: CE01ISSP-XX099-01-CTDPFJ999
insert into system_event_definitions(uframe_filter_id, reference_designator, array_name, platform_name, instrument_name, instrument_parameter, instrument_parameter_pdid, operator, created_time, event_type, severity, active, description, high_value, low_value, stream, escalate_on, escalate_boundary) values (1,'CE01ISSP-XX099-01-CTDPFJ999','CE', 'CE01ISSP-XX099', 'CE01ISSP-XX099-01-CTDPFJ999','temperature', 'PD440', 'GREATER', '2015-03-31 21:23:31', 'alert', 3, True, 'Monitor water temp does not exceed upper limit', '31.0', '10.0', 'ctdpf_j_cspp_instrument', 5, 10);
insert into system_event_definitions(uframe_filter_id, reference_designator, array_name, platform_name, instrument_name, instrument_parameter, instrument_parameter_pdid, operator, created_time, event_type, severity, active, description, high_value, low_value, stream, escalate_on, escalate_boundary) values (2,'CE01ISSP-XX099-01-CTDPFJ999','CE', 'CE01ISSP-XX099', 'CE01ISSP-XX099-01-CTDPFJ999','temperature', 'PD440', 'GREATER', '2015-03-31 23:23:31', 'alarm', 2, True, 'Monitor water temp does not exceed upper limit', '31.0', '10.0', 'ctdpf_j_cspp_instrument', 5, 10);
insert into system_event_definitions(uframe_filter_id, reference_designator, array_name, platform_name, instrument_name, instrument_parameter, instrument_parameter_pdid, operator, created_time, event_type, severity, active, description, high_value, low_value, stream, escalate_on, escalate_boundary) values (3,'CE01ISSP-XX099-01-CTDPFJ999','CE', 'CE01ISSP-XX099', 'CE01ISSP-XX099-01-CTDPFJ999','temperature', 'PD440', 'GREATER', '2015-03-31 21:23:31', 'alert', 3, True, 'Monitor water temp does not exceed upper limit', '31.0', '10.0', 'ctdpf_j_cspp_instrument', 5, 10);

insert into user_event_notifications(system_event_definition_id, user_id, use_email, use_redmine, use_phone, use_log, use_sms) values (1, 1, False, True, False, False, False);
insert into user_event_notifications(system_event_definition_id, user_id, use_email, use_redmine, use_phone, use_log, use_sms) values (2, 1, True, True, True, True, True);
insert into user_event_notifications(system_event_definition_id, user_id, use_email, use_redmine, use_phone, use_log, use_sms) values (3, 1, False, True, False, False, False);
