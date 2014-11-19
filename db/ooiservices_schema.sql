/* __author__ = 'Matt Campbell'
    Requires: postgis
*/

CREATE TABLE arrays (
    id          VARCHAR(30) NOT NULL,
    geography   BOX,

    PRIMARY KEY (id)
);

CREATE TABLE platforms (
    id          VARCHAR(30) NOT NULL,
    array_id    VARCHAR(30) NOT NULL,
    geography   geography(POINT,4326),

    PRIMARY KEY (id),
    FOREIGN KEY (array_id) REFERENCES arrays(id)
);

CREATE TABLE instruments (
    id          VARCHAR(30) NOT NULL,
    platform_id VARCHAR(30) NOT NULL,
    geography   geography(POINT,4326),

    PRIMARY KEY (id),
    FOREIGN KEY (platform_id) REFERENCES platforms(id)
);