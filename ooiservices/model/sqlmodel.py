#!/usr/bin/env python

'''
    ooiservices.model.base.py
    
    The class for the BaseModel
    
    '''

#TODO: import SQLiteAdapter will need to be externalized in the config file.
import ooiservices.config as config
from ooiservices.model.adaptor import SQLiteAdaptor as SQL
from ooiservices.model.base import BaseModel

class SqlModel(BaseModel):
    
    sql = SQL(config.dbName)
    
    def __init__(self, tableName=None, whereParam='id', reformatOutput=False):
        '''
            Instantiates new base model
            '''
        # A really obscure bug that causes a severe headache down the road
        BaseModel.__init__(self)
        self.tbl = tableName
        self.whereParam = whereParam
        self.reformatOutput = reformatOutput
    
    #CRUD methods
    def create(self, obj):
        columns = ', '.join(obj.keys())
        placeholders = ':'+', :'.join(obj.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s);' % (self.tbl, columns, placeholders)
        feedback = self.sql.perform(query, obj)
        return feedback
    
    def read(self, obj_id=None):
        '''
        Modified to (temporarily) support interim UI specification for output
        '''
        if obj_id:
            query = 'SELECT * FROM %s WHERE %s=\'%s\';' % (self.tbl, self.whereParam, obj_id)
        else:
            query = 'SELECT * FROM %s ORDER BY %s;' % (self.tbl, self.whereParam)
        answer = self.sql.perform(query)
        if self.reformatOutput:
            feedback = self.filter_ooi_platforms(answer)
        else:
            feedback = answer

        return feedback
    
    def update(self, obj):
        obj_id = obj.get('id')
        #Don't want to include the id in the data set to update.
        del obj['id']
        update_set = ', '.join('%s=%r' % (key, val) for (key, val) in obj.items())
        query = 'UPDATE %s SET %s WHERE %s=\'%s\';' % (self.tbl, update_set, self.whereParam, obj_id)
        feedback = self.sql.perform(query)
        return feedback
    
    def delete(self, obj_id):
        query = 'DELETE FROM %s WHERE %s=\'%s\';' % (self.tbl, self.whereParam, obj_id)
        feedback = self.sql.perform(query)
        return feedback

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


