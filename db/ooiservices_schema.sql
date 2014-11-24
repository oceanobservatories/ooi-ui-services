/* __author__ = 'Matt Campbell'
    Requires: postgis
*/

CREATE TABLE arrays (
    id          VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    geography   geography,

    PRIMARY KEY (id)
);

CREATE TABLE platforms (
    id          VARCHAR(30) NOT NULL,
    array_id    VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    geography   geography,

    PRIMARY KEY (id),
    FOREIGN KEY (array_id) REFERENCES arrays(id)
);

CREATE TABLE instruments (
    id          VARCHAR(30) NOT NULL,
    platform_id VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    geography   geography,

    PRIMARY KEY (id),
    FOREIGN KEY (platform_id) REFERENCES platforms(id)
);