CREATE TABLE ooi_platforms (
    id          VARCHAR(20) NOT NULL,
    array_code  VARCHAR(20) NOT NULL,
    site_name   VARCHAR(20) NOT NULL,
    node_name   VARCHAR(20) NOT NULL,

    /* geography geography(POINT, 4326), */

    PRIMARY KEY (id)
);

CREATE TABLE ooi_instruments (
    id          VARCHAR(20) NOT NULL,
    platform_id VARCHAR(20) NOT NULL,
    port        VARCHAR(20) NOT NULL,
    inst_class  VARCHAR(20) NOT NULL,
    inst_series VARCHAR(20) NOT NULL,
    inst_seq    VARCHAR(20) NOT NULL,

    PRIMARY KEY (id)
    /*FOREIGN KEY (platform_id) REFERENCES platforms(id)*/
);


INSERT INTO ooi_platforms VALUES ('AA#AAAA-AACCC', 'AA', '##AAAA', 'AACCC');
INSERT INTO ooi_instruments VALUES ('##-CCCCCA###', 'AA#AAAA-AACCC', '##', 'CCCCC', 'A', '###');