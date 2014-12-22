--PostgreSQL Maestro 14.5.0.1
------------------------------------------
--Host     : ooiui-dev.cvyc5bvl5zzs.us-east-1.rds.amazonaws.com
--Database : ooiuidev


-- Definition for sequence assets_id_seq (OID = 18676):
SET SESSION AUTHORIZATION 'oceanzus';
SET search_path = asset_management_nodata, public, pg_catalog;
CREATE SEQUENCE assets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table assets (OID = 18678):
CREATE TABLE assets (
    id integer DEFAULT nextval('assets_id_seq'::regclass) NOT NULL,
    asset_type_id integer NOT NULL,
    organization_id integer NOT NULL,
    supplier_id integer NOT NULL,
    deployment_id integer,
    asset_name text NOT NULL,
    current_lifecycle_state text,
    part_number text,
    firmware_version text,
    geo_location geography(Point,4326),
    instrument_model_id integer NOT NULL
) WITHOUT OIDS;
-- Definition for sequence asset_types_id_seq (OID = 18687):
CREATE SEQUENCE asset_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table asset_types (OID = 18689):
CREATE TABLE asset_types (
    id integer DEFAULT nextval('asset_types_id_seq'::regclass) NOT NULL,
    asset_type_name text NOT NULL
) WITHOUT OIDS;
-- Definition for sequence organizations_id_seq (OID = 18708):
CREATE SEQUENCE organizations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table organizations (OID = 18710):
CREATE TABLE organizations (
    id integer DEFAULT nextval('organizations_id_seq'::regclass) NOT NULL,
    organization_name text NOT NULL
) WITHOUT OIDS;
-- Definition for sequence installation_record_id_seq (OID = 18743):
CREATE SEQUENCE installation_record_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table installation_record (OID = 18745):
CREATE TABLE installation_record (
    id integer DEFAULT nextval('installation_record_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    assembly_id integer NOT NULL,
    date_installed date,
    date_removed date,
    technician_name text,
    comments text,
    file_id integer
) WITHOUT OIDS;
-- Definition for sequence asssemblies_id_seq (OID = 18760):
CREATE SEQUENCE asssemblies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table asssemblies (OID = 18762):
CREATE TABLE asssemblies (
    id integer DEFAULT nextval('asssemblies_id_seq'::regclass) NOT NULL,
    assembly_name text NOT NULL,
    description text
) WITHOUT OIDS;
-- Definition for sequence instrument_models_id_seq (OID = 18776):
CREATE SEQUENCE instrument_models_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table instrument_models (OID = 18778):
CREATE TABLE instrument_models (
    id integer DEFAULT nextval('instrument_models_id_seq'::regclass) NOT NULL,
    instrument_model_name text NOT NULL,
    series_name text,
    class_name text,
    manufacturer_id integer
) WITHOUT OIDS;
-- Definition for sequence inspection_status_id_seq (OID = 18792):
CREATE SEQUENCE inspection_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table inspection_status (OID = 18794):
CREATE TABLE inspection_status (
    id integer DEFAULT nextval('inspection_status_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer,
    status text,
    technician_name text,
    comments text,
    inspection_date date,
    document text
) WITHOUT OIDS;
-- Definition for sequence files_id_seq (OID = 18808):
CREATE SEQUENCE files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table files (OID = 18810):
CREATE TABLE files (
    id integer DEFAULT nextval('files_id_seq'::regclass) NOT NULL,
    user_id integer,
    file_name text NOT NULL,
    file_system_path text,
    file_size text,
    file_permissions text,
    file_type text
) WITHOUT OIDS;
-- Definition for sequence asset_file_link_id_seq (OID = 18829):
CREATE SEQUENCE asset_file_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table asset_file_link (OID = 18831):
CREATE TABLE asset_file_link (
    id integer DEFAULT nextval('asset_file_link_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer NOT NULL
) WITHOUT OIDS;
-- Definition for sequence manufacturers_id_seq (OID = 18931):
CREATE SEQUENCE manufacturers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table manufacturers (OID = 18933):
CREATE TABLE manufacturers (
    id integer DEFAULT nextval('manufacturers_id_seq'::regclass) NOT NULL,
    manufacturer_name text NOT NULL,
    phone_number text,
    contact_name text,
    web_address text
) WITHOUT OIDS;
-- Definition for sequence suppliers_id_seq (OID = 20347):
CREATE SEQUENCE suppliers_id_seq
    START WITH 1
    INCREMENT BY 1
    MAXVALUE 2147483647
    NO MINVALUE
    CACHE 1;
-- Structure for table suppliers (OID = 20157):
CREATE TABLE suppliers (
    id integer DEFAULT nextval(('public.suppliers_id_seq'::text)::regclass) NOT NULL,
    supplier_name text NOT NULL
) WITHOUT OIDS;
-- Definition for index assets_pkey (OID = 18685):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);
-- Definition for index asset_types_pkey (OID = 18696):
ALTER TABLE ONLY asset_types
    ADD CONSTRAINT asset_types_pkey PRIMARY KEY (id);
-- Definition for index organizations_pkey (OID = 18717):
ALTER TABLE ONLY organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);
-- Definition for index assets_organization_id_organizations_id_fkey (OID = 18719):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_organization_id_organizations_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id);
-- Definition for index installation_record_pkey (OID = 18752):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_pkey PRIMARY KEY (id);
-- Definition for index asssemblies_pkey (OID = 18769):
ALTER TABLE ONLY asssemblies
    ADD CONSTRAINT asssemblies_pkey PRIMARY KEY (id);
-- Definition for index instrument_models_pkey (OID = 18785):
ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT instrument_models_pkey PRIMARY KEY (id);
-- Definition for index inspection_status_pkey (OID = 18801):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_pkey PRIMARY KEY (id);
-- Definition for index files_pkey (OID = 18817):
ALTER TABLE ONLY files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);
-- Definition for index asset_file_link_pkey (OID = 18835):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_pkey PRIMARY KEY (id);
-- Definition for index manufacturers_pkey (OID = 18940):
ALTER TABLE ONLY manufacturers
    ADD CONSTRAINT manufacturers_pkey PRIMARY KEY (id);
-- Definition for index inst_models_manufacturer_id_manufacturer_id_fkey (OID = 18952):
ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT inst_models_manufacturer_id_manufacturer_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);
-- Definition for index installation_record_assembly_id_assemblies_id_fkey (OID = 18997):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_assembly_id_assemblies_id_fkey FOREIGN KEY (assembly_id) REFERENCES asssemblies(id);
-- Definition for index installation_record_file_id_files_id_fkey (OID = 19002):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index installation_record_asset_id_assets_id_fkey (OID = 19007):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index inspection_status_asset_id_assets_id_fkey (OID = 19012):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index assets_asset_type_id_asset_types_id_fkey (OID = 19017):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_asset_type_id_asset_types_id_fkey FOREIGN KEY (asset_type_id) REFERENCES asset_types(id);
-- Definition for index asset_file_link_asset_id_assets_id_fkey (OID = 19022):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index asset_file_link_file_id_files_id_fkey (OID = 19027):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index inspection_status_file_id_files_id_fkey (OID = 19032):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index assets_instrument_model_id_instrument_models_id_fkey (OID = 20152):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_instrument_model_id_instrument_models_id_fkey FOREIGN KEY (instrument_model_id) REFERENCES instrument_models(id);
-- Definition for index suppliers_pkey (OID = 20163):
ALTER TABLE ONLY suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);
-- Definition for index assets_supplier_id_suppliers_id_fkey (OID = 20165):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_supplier_id_suppliers_id_fkey FOREIGN KEY (supplier_id) REFERENCES suppliers(id);
--
-- Comments
--
COMMENT ON COLUMN assets.deployment_id IS 'Current deployment';
COMMENT ON COLUMN files.file_size IS 'MB';
