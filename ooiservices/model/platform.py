#!/usr/bin/env python
#!/usr/bin/env python
'''
ooiservices.model.platform.py

PlatformModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class PlatformModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='ooi_platforms', where_param='array_code')

    def filter_ooi_platforms(self, input):
        '''
        interim helper to reformat query output to OOI UI input format
        '''
        doc = {}
        for row in input:
            self.read_row(doc, row)

        return doc

    def read_row(self, doc, row):
        '''
        Places the contents of the row into the json document
        '''
        
        instr_constant = 'PHSENE002'

        array_code     = row['array_code']
        site_suffix    = row['site_suffix']
        lat            = row['latitude']
        lon            = row['longitude']
        site_id        = row['site_prefix']
        node_type_code = row['node_type_code']
        node_site_seq  = row['node_site_sequence']
        port_num       = row['port_number']

        instr = array_code + site_suffix + '-' + node_type_code + node_site_seq + '-' + port_num + '-' + instr_constant

        if array_code not in doc:
            doc[array_code] = {}

        if site_suffix not in doc[array_code]:
            doc[array_code][site_suffix] = {}
            doc[array_code][site_suffix]['lat'] = lat
            doc[array_code][site_suffix]['lon'] = lon
            doc[array_code][site_suffix]['site_id'] = site_id
            doc[array_code][site_suffix]['instruments'] = []

        if instr not in doc[array_code][site_suffix]['instruments']:
            doc[array_code][site_suffix]['instruments'].append(instr)


