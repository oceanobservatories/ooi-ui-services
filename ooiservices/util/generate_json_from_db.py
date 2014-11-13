#!/usr/bin/env python
'''
ooiservices.util.generate_json_from_db

'''

import sqlite3
import json
from ooiservices.util.parse_erddap_endpoints import getStreamIdsForRef, getAttribsForRef

VALID_SITES = [
    'CP02PMCI',
    'CP02PMCO',
    'CP02PMUI',
    'CP02PMUO',
    'CP04OSPM',
    'CP05MOAS'
]
SITES = {
    'CP02PMUO' : { 'lat' : 39.94302167, 'lon' : -70.77001333 },
    'CP02PMCI' : { 'lat' : 40.22653333, 'lon' : -70.87795 },
    'CP02PMCO' : { 'lat' : 40.10123333, 'lon' : -70.88768333 },
    'CP02PMUI' : { 'lat' : 40.8974, 'lon' : -70.68601167 },
    'CP04OSPM' : { 'lat' : 39.93333333, 'lon' : -70.87843333 }
}

def generate():
    refdes_db = 'notebooks/ref_des.db'


    conn = sqlite3.connect(refdes_db)
    doc = {}
    

    c = conn.cursor()
    for row in c.execute('SELECT * FROM ooi_instruments;'):
        parse_row(doc, row)

    with open('ooiservices/static/expected_platforms.json', 'w') as f:
        f.write(json.dumps(doc))

    return doc

def parse_row(doc, row):
    ref_code          = row[0]
    array_code        = row[1]
    site_prefix       = row[2]
    site_suffix       = row[3]
    node_type_code    = row[4]
    node_site_seq     = row[5]
    port_number       = row[6]
    instrument_class  = row[7]
    instrument_series = row[8]
    instrument_req    = row[9]
    site = array_code + site_prefix.zfill(2) + site_suffix

    if site not in VALID_SITES:
        return

    platform = array_code + site_prefix.zfill(2) + site_suffix + '-' + node_type_code + node_site_seq.zfill(3)
    if array_code not in doc:
        doc[array_code] = {}

    if site in SITES:
        lat = SITES[site]['lat']
        lon = SITES[site]['lon']
    else:
        lat = -999
        lon = -999

    if platform not in doc[array_code]:
        doc[array_code][platform] = {
            'instruments' : {},
            'status' : 'na',
            'lat' : lat,
            'lon' : lon
        }

    erddap_ref_code = array_code + site_prefix.zfill(2) + site_suffix + '_' + node_type_code + node_site_seq.zfill(3) + '_' + instrument_class + instrument_series + instrument_req
    stream_doc = get_streams(erddap_ref_code)
    doc[array_code][platform]['instruments'][ref_code] = stream_doc

def get_streams(ref_code):
    stream_doc = {}
    stream_list = getStreamIdsForRef(ref_code) 
    for stream in stream_list:
        stream_doc[stream] = getAttribsForRef(ref_code, stream)
    return stream_doc

if __name__ == '__main__':
    generate()