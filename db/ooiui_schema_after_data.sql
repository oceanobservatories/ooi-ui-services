-- OOI UI Schema
-- Note: Execute after bulk insert of data

-- START HEADER DEFINITIONS
--
SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = ooiui, public, pg_catalog;
--
-- END HEADER DEFINITIONS

-- Definition for index arrays_pkey (OID = 19238):
ALTER TABLE ONLY arrays
    ADD CONSTRAINT arrays_pkey PRIMARY KEY (id);
-- Definition for index deployments_pkey (OID = 19240):
ALTER TABLE ONLY deployments
    ADD CONSTRAINT deployments_pkey PRIMARY KEY (id);
-- Definition for index instrument_deployments_pkey (OID = 19242):
ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_pkey PRIMARY KEY (id);
-- Definition for index instruments_pkey (OID = 19244):
ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_pkey PRIMARY KEY (id);
-- Definition for index platform_deployments_pkey (OID = 19246):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_pkey PRIMARY KEY (id);
-- Definition for index platforms_pkey (OID = 19248):
ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_pkey PRIMARY KEY (id);
-- Definition for index stream_parameters_pkey (OID = 19250):
ALTER TABLE ONLY stream_parameters
    ADD CONSTRAINT stream_parameters_pkey PRIMARY KEY (id);
-- Definition for index streams_pkey (OID = 19252):
ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_pkey PRIMARY KEY (id);
-- Definition for index instrument_deployments_instrument_id_fkey (OID = 19254):
ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);
-- Definition for index instrument_deployments_platform_deployment_id_fkey (OID = 19259):
ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_platform_deployment_id_fkey FOREIGN KEY (platform_deployment_id) REFERENCES platform_deployments(id);
-- Definition for index platform_deployments_array_id_fkey (OID = 19264):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_array_id_fkey FOREIGN KEY (array_id) REFERENCES arrays(id);
-- Definition for index platform_deployments_deployment_id_fkey (OID = 19269):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_deployment_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);
-- Definition for index platform_deployments_platform_id_fkey (OID = 19274):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_platform_id_fkey FOREIGN KEY (platform_id) REFERENCES platforms(id);
-- Definition for index streams_instrument_id_fkey (OID = 19279):
ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);
-- Definition for index assets_pkey (OID = 19284):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);
-- Definition for index asset_types_pkey (OID = 19286):
ALTER TABLE ONLY asset_types
    ADD CONSTRAINT asset_types_pkey PRIMARY KEY (id);
-- Definition for index organizations_pkey (OID = 19288):
ALTER TABLE ONLY organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);
-- Definition for index assets_organization_id_organizations_id_fkey (OID = 19290):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_organization_id_organizations_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id);
-- Definition for index stream_parameter_link_pkey (OID = 19295):
ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_pkey PRIMARY KEY (id);
-- Definition for index installation_record_pkey (OID = 19297):
ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_pkey PRIMARY KEY (id);
-- Definition for index assemblies_pkey (OID = 19299):
ALTER TABLE ONLY assemblies
    ADD CONSTRAINT assemblies_pkey PRIMARY KEY (id);
-- Definition for index instrument_models_pkey (OID = 19301):
ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT instrument_models_pkey PRIMARY KEY (id);
-- Definition for index instruments_model_id.inst_models_id_fkey (OID = 19303):
ALTER TABLE ONLY instruments
    ADD CONSTRAINT "instruments_model_id.inst_models_id_fkey" FOREIGN KEY (model_id) REFERENCES instrument_models(id);
-- Definition for index inspection_status_pkey (OID = 19308):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_pkey PRIMARY KEY (id);
-- Definition for index files_pkey (OID = 19310):
ALTER TABLE ONLY files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);
-- Definition for index asset_file_link_pkey (OID = 19312):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_pkey PRIMARY KEY (id);
-- Definition for index drivers_pkey (OID = 19314):
ALTER TABLE ONLY drivers
    ADD CONSTRAINT drivers_pkey PRIMARY KEY (id);
-- Definition for index driver_stream_link_pkey (OID = 19316):
ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_pkey PRIMARY KEY (id);
-- Definition for index datasets_pkey (OID = 19318):
ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (id);
-- Definition for index dataset_keywords_pkey (OID = 19320):
ALTER TABLE ONLY dataset_keywords
    ADD CONSTRAINT dataset_keywords_pkey PRIMARY KEY (id);
-- Definition for index manufacturers_pkey (OID = 19322):
ALTER TABLE ONLY manufacturers
    ADD CONSTRAINT manufacturers_pkey PRIMARY KEY (id);
-- Definition for index platforms_manufacturer_id_manufacturers_id_fkey (OID = 19324):
ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_manufacturer_id_manufacturers_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);
-- Definition for index instruments_manufacturer_id_manufacturers_id_fkey (OID = 19329):
ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_manufacturer_id_manufacturers_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);
-- Definition for index inst_models_manufacturer_id_manufacturer_id_fkey (OID = 19334):
ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT inst_models_manufacturer_id_manufacturer_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);
-- Definition for index drivers_instrument_id_instruments_id_fkey (OID = 19339):
ALTER TABLE ONLY drivers
    ADD CONSTRAINT drivers_instrument_id_instruments_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);
-- Definition for index driver_stream_link_driver_id_drivers_id_fkey (OID = 19344):
ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_driver_id_drivers_id_fkey FOREIGN KEY (driver_id) REFERENCES drivers(id);
-- Definition for index driver_stream_link_stream_id_streams_id_fkey (OID = 19349):
ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);
-- Definition for index datasets_deployment_id_deployments_id_fkey (OID = 19354):
ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_deployment_id_deployments_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);
-- Definition for index datasets_stream_id_streams_id_fkey (OID = 19359):
ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);
-- Definition for index stream_parameter_link_stream_id_streams_id_fkey (OID = 19364):
ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);
-- Definition for index stream_parameter_link_parameter_id_parameters_id_fkey (OID = 19369):
ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_parameter_id_parameters_id_fkey FOREIGN KEY (parameter_id) REFERENCES stream_parameters(id);
-- Definition for index dataset_keywords_dataset_id_datasets_id_fkey (OID = 19374):
ALTER TABLE ONLY dataset_keywords
    ADD CONSTRAINT dataset_keywords_dataset_id_datasets_id_fkey FOREIGN KEY (dataset_id) REFERENCES datasets(id);
-- Definition for index installation_record_assembly_id_assemblies_id_fkey (OID = 19379):
ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_assembly_id_assemblies_id_fkey FOREIGN KEY (assembly_id) REFERENCES assemblies(id);
-- Definition for index installation_record_file_id_files_id_fkey (OID = 19384):
ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index installation_record_asset_id_assets_id_fkey (OID = 19389):
ALTER TABLE ONLY installation_records
    ADD CONSTRAINT installation_record_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index inspection_status_asset_id_assets_id_fkey (OID = 19394):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index assets_asset_type_id_asset_types_id_fkey (OID = 19399):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_asset_type_id_asset_types_id_fkey FOREIGN KEY (asset_type_id) REFERENCES asset_types(id);
-- Definition for index asset_file_link_asset_id_assets_id_fkey (OID = 19404):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index asset_file_link_file_id_files_id_fkey (OID = 19409):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index inspection_status_file_id_files_id_fkey (OID = 19414):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index instruments_asset_id_assets_id_fkey (OID = 20939):
ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index platforms_asset_id_assets_id_fkey (OID = 20944):
ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index users_pkey (OID = 20958):
ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
-- Definition for index user_scopes_pkey (OID = 20969):
ALTER TABLE ONLY user_scopes
    ADD CONSTRAINT user_scopes_pkey PRIMARY KEY (id);
-- Definition for index user_scope_link_pkey (OID = 20977):
ALTER TABLE ONLY user_scope_link
    ADD CONSTRAINT user_scope_link_pkey PRIMARY KEY (id);
-- Definition for index user_scope_link_user_id_fkey (OID = 20980):
ALTER TABLE ONLY user_scope_link
    ADD CONSTRAINT user_scope_link_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
-- Definition for index user_scope_link_user_scopes_id_fkey (OID = 20985):
ALTER TABLE ONLY user_scope_link
    ADD CONSTRAINT user_scope_link_user_scopes_id_fkey FOREIGN KEY (scope_id) REFERENCES user_scopes(id);
-- Definition for index foreign_key01 (OID = 20998):
ALTER TABLE ONLY users
    ADD CONSTRAINT foreign_key01 FOREIGN KEY (organization_id) REFERENCES organizations(id);
-- Definition for index annotations_pkey (OID = 21028):
ALTER TABLE ONLY annotations
    ADD CONSTRAINT annotations_pkey PRIMARY KEY (id);
-- Definition for index annotations_user_id_users_id_fkey (OID = 21030):
ALTER TABLE ONLY annotations
    ADD CONSTRAINT annotations_user_id_users_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
COMMENT ON SCHEMA public IS 'standard public schema';
ALTER TABLE ONLY user_roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);
-- Definition for index user_role_link_pkey (OID = 31548):
ALTER TABLE ONLY user_role_user_scope_link
    ADD CONSTRAINT user_role_link_pkey PRIMARY KEY (id);
-- Definition for index user_scope_id_user_scopes_id_fkey (OID = 31566):
ALTER TABLE ONLY user_role_user_scope_link
    ADD CONSTRAINT user_scope_id_user_scopes_id_fkey FOREIGN KEY (user_scope_id) REFERENCES user_scopes(id);
-- Definition for index user_role_id_user_roles_id_fkey (OID = 31571):
ALTER TABLE ONLY user_role_user_scope_link
    ADD CONSTRAINT user_role_id_user_roles_id_fkey FOREIGN KEY (user_role_id) REFERENCES user_roles(id);
--
-- Comments
--
COMMENT ON COLUMN assets.deployment_id IS 'Current deployment';
COMMENT ON COLUMN files.file_size IS 'MB';
