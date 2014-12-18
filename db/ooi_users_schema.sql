--PostgreSQL Maestro 14.5.0.1
------------------------------------------
--Host     : ooiui-dev.cvyc5bvl5zzs.us-east-1.rds.amazonaws.com
--Database : ooiuidev


-- Definition for sequence users_id_seq (OID = 20744):
SET search_path = user_management_nodata, pg_catalog;
CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table users (OID = 20746):
CREATE TABLE users (
    id integer DEFAULT nextval('users_id_seq'::regclass) NOT NULL,
    email text NOT NULL,
    passwd text,
    user_name text,
    active boolean DEFAULT false NOT NULL,
    confirmed_at date,
    roles text NOT NULL
) WITHOUT OIDS;
-- Definition for sequence roles_id_seq (OID = 20758):
CREATE SEQUENCE roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Structure for table roles (OID = 20760):
CREATE TABLE roles (
    id integer DEFAULT nextval('roles_id_seq'::regclass) NOT NULL,
    role_name text NOT NULL,
    description integer
) WITHOUT OIDS;
-- Definition for index users_pkey (OID = 20754):
ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
-- Definition for index users_idx_email01 (OID = 20756):
ALTER TABLE ONLY users
    ADD CONSTRAINT users_idx_email01 UNIQUE (email);
-- Definition for index roles_pkey (OID = 20767):
ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);
-- Definition for index roles_idx_role_name01 (OID = 20769):
ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_idx_role_name01 UNIQUE (role_name);
--
-- Comments
--
COMMENT ON COLUMN users.roles IS '[1,2,3]';
