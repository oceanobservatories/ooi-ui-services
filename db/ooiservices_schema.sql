/* __author__ = 'Matt Campbell'
    Requires: postgis
*/

CREATE TABLE arrays (
    id          VARCHAR(20) NOT NULL,
    geography   BOX,

    PRIMARY KEY (id)
);

CREATE TABLE platforms (
    id          VARCHAR(20) NOT NULL,
    array_id    VARCHAR(20) NOT NULL,
    geography   geography(POINT,4326),

    PRIMARY KEY (id),
    FOREIGN KEY (array_id) REFERENCES arrays(id)
);

CREATE TABLE instruments (
    id          VARCHAR(20) NOT NULL,
    platform_id VARCHAR(20) NOT NULL,
    geography   geography(POINT,4326),

    PRIMARY KEY (id),
    FOREIGN KEY (platform_id) REFERENCES platforms(id)
);

/* sample content */
INSERT INTO arrays VALUES ('AA', (ST_MakeEnvelope(41.45373, -71.47099, 41.45541, -71.47041, 4326)));
INSERT INTO platforms VALUES ('AA00AAAA-AACCC', 'AA', ST_Point(41.45443, -71.47041));
INSERT INTO instruments VALUES ('00-CCCCCA000', 'AA00AAAA-AACCC', ST_Point(41.45443, -71.47041));