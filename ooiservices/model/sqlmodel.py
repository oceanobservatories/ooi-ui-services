#!/usr/bin/env python

'''
ooiservices.model.sqlmodel

SQLModel
'''


from ooiservices.config import DataSource
from ooiservices.adaptor.sqlite import SQLiteAdaptor as SQL
from ooiservices.model.base import BaseModel

class SqlModel(BaseModel):
    
    sql = SQL(DataSource['DBName'])
    
    def __init__(self, tableName=None, whereParam='id'):
        '''
        Instantiates new base model
        '''
        # A really obscure bug that causes a severe headache down the road
        BaseModel.__init__(self)
        self.tbl = tableName
        self.whereParam = whereParam
    
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
        return answer
    
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

