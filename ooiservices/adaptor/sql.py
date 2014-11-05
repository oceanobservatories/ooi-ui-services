#!/usr/bin/env python

'''
    ooiservices.model.base.py
    
    The class for the BaseModel
    
    '''

#TODO: import SQLiteAdapter will need to be externalized in the config file.
import ooiservices.config as config
from ooiservices.model.adaptor import SQLiteAdaptor as SQL
from ooiservices.model.base import BaseModel

class SQLModel(BaseModel):
    
    sql = SQL(config.dbName)
    
    def __init__(self, tableName=None):
        '''
            Instantiates new base model
            '''
        # A really obscure bug that causes a severe headache down the road
        BaseModel.__init__(self)
        self.tbl = tableName
    
    #CRUD methods
    def create(self, obj):
        columns = ', '.join(obj.keys())
        placeholders = ':'+', :'.join(obj.keys())
        query = 'INSERT INTO %s (%s) VALUES (%s);' % (self.tbl, columns, placeholders)
        feedback = self.sql.perform(query, obj)
        return feedback
    
    def read(self, obj_id=None):
        if obj_id:
            query = 'SELECT * FROM %s WHERE id=\'%s\';' % (self.tbl, obj_id)
        else:
            query = 'SELECT * FROM %s;' % (self.tbl)
        answer = self.sql.perform(query)
        return answer
    
    def update(self, obj):
        obj_id = obj.get('id')
        #Don't want to include the id in the data set to update.
        del obj['id']
        update_set = ', '.join('%s=%r' % (key, val) for (key, val) in obj.items())
        query = 'UPDATE %s SET %s WHERE id=\'%s\';' % (self.tbl, update_set, obj_id)
        feedback = self.sql.perform(query)
        return feedback
    
    def delete(self, obj_id):
        query = 'DELETE FROM %s WHERE id=\'%s\';' % (self.tbl, obj_id)
        feedback = self.sql.perform(query)
        return feedback
