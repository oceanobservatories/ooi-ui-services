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
        SqlModel.__init__(self, tableName='ooi_platforms', whereParam='array_code')

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

        '''
        CP02PMUI-WFP01

        CP   = array_code
        02   = site_prefix
        PMUI = site_suffix
        WFP  = node_type_code
        01   = node_site_seq
        '''

        array_code     = row['array_code']
        site_prefix    = row['site_prefix']
        site_suffix    = row['site_suffix']
        lat            = row['latitude']
        lon            = row['longitude']
        site_id        = row['site_prefix']
        node_type_code = row['node_type_code']
        node_site_seq  = row['node_site_sequence']
        port_num       = row['port_number']


        platform = array_code + site_prefix.zfill(2) + site_suffix + '-' + node_type_code + node_site_seq
        app.logger.info(platform)
        instr = array_code + site_suffix + '-' + node_type_code + node_site_seq + '-' + port_num + '-' + instr_constant

        if array_code not in doc:
            doc[array_code] = {}

        if platform not in doc[array_code]:
            doc[array_code][platform] = {}
            doc[array_code][platform]['lat'] = lat
            doc[array_code][platform]['lon'] = lon
            doc[array_code][platform]['site_id'] = site_id
            doc[array_code][platform]['instruments'] = []
            doc[array_code][platform]['status'] = 'na'

