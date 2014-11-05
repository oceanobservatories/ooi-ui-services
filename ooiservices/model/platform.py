#!/usr/bin/env python
#!/usr/bin/env python
'''
ooiservices.model.platform.py

PlatformModel
'''

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
        arrays = []
        current_array = ''
        instr_constant = 'PHSENE002'
        for element in input:
            array_code = element['array_code']
            site_suffix = element['site_suffix']
            lat = element['latitude']
            lon = element['longitude']
            site_id = element['site_prefix']
            node_type_code = element['node_type_code']
            node_site_seq = element['node_site_sequence']
            port_num = element['port_number']
            instr = current_array + site_suffix + '-' + node_type_code + node_site_seq + '-' + port_num + '-' + instr_constant
            if current_array != array_code:
                if array_code not in arrays:
                    arrays.append(array_code)
                    current_array = array_code
                    doc[current_array] = {}
                    instruments = []
                    doc[current_array][site_suffix] = {}
                    doc[current_array][site_suffix]['lat'] = lat
                    doc[current_array][site_suffix]['lon'] = lon
                    doc[current_array][site_suffix]['site_id'] = site_id
                    instruments.append(instr)
                    doc[current_array][site_suffix]['instruments'] = instruments[:]
            else:
                if site_suffix in doc[current_array]:
                    if 'instruments' in doc[current_array][site_suffix]:
                        instruments = doc[current_array][site_suffix]['instruments'][:]
                    if instr not in instruments:
                        instruments.append(instr)
                        doc[current_array][site_suffix]['instruments'] = instruments
                else:
                    doc[current_array][site_suffix] = {}
                    doc[current_array][site_suffix]['lat'] = lat
                    doc[current_array][site_suffix]['lon'] = lon
                    doc[current_array][site_suffix]['site_id'] = site_id
                    instruments = []
                    instruments.append(instr)
                    doc[current_array][site_suffix]['instruments'] = instruments
        '''
        # create summary (debug/test only)
        temp = {}
        total_arrays = len(arrays)
        temp['number_of_arrays'] = total_arrays
        for array in arrays:
        temp[array] = len(doc[array])
        for key, value in doc[array].iteritems():
        subtitle = array + ' - ' + key + ' instruments'
        temp[subtitle] = len(doc[array][key]['instruments'])
        doc['summary'] = temp
        '''
        return doc