#!/usr/bin/env python
'''
ooiservices.util.generate_json_from_db

'''

import sqlite3
import json
from ooiservices.util.parse_erddap_endpoints import getStreamIdsForRef, getAttribsForRef
from ooiservices.config import DataSource

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
    refdes_db = DataSource['DBName']


    conn = sqlite3.connect(refdes_db)
    doc = {}
    

    c = conn.cursor()
    # I use a list because I needed to make more SQL executions in the iteration
    for row in list(c.execute('SELECT * FROM ooi_instruments ORDER BY ref_code;')):
        parse_row(doc, row, c)

    with open('ooiservices/static/expected_platforms.json', 'w') as f:
        f.write(json.dumps(doc))

    return doc

def parse_row(doc, row, c):
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
    display_name      = row[12]
    site = array_code + site_prefix.zfill(2) + site_suffix

    if site not in VALID_SITES:
        return

    platform = array_code + site_prefix.zfill(2) + site_suffix + '-' + node_type_code + node_site_seq.zfill(3)
    response = list(c.execute('SELECT * FROM ooi_platforms WHERE ref_code=?', (platform,)))
    if response:
        platform_display_name = response[0][-1]
    else:
        platform_display_name = 'Unknown'

    if array_code not in doc:
        doc[array_code] = {}

    if site in SITES:
        lat = SITES[site]['lat']
        lon = SITES[site]['lon']
    elif site == 'CP05MOAS' and 'GL' in node_type_code:
        lat = 40.0833
        lon = -70.25
    else:
        lat = -999
        lon = -999

    if platform not in doc[array_code]:
        doc[array_code][platform] = {
            'instruments' : {},
            'status' : 'na',
            'display_name' : platform_display_name,
            'lat' : lat,
            'lon' : lon
        }

    erddap_ref_code = array_code + site_prefix.zfill(2) + site_suffix + '_' + node_type_code + node_site_seq.zfill(3) + '_' + port_number.zfill(2) + '_' + instrument_class + instrument_series + instrument_req.zfill(3)
    stream_doc = get_streams(erddap_ref_code)
    doc[array_code][platform]['instruments'][ref_code] = {"streams": stream_doc, "display_name" : display_name}

def get_streams(ref_code):
    stream_doc = {}
    stream_list = getStreamIdsForRef(ref_code) 
    for stream in stream_list:
        varnames = getAttribsForRef(ref_code, stream)
        if varnames:
            stream_doc[stream] = varnames
    return stream_doc

if __name__ == '__main__':
    generate()

