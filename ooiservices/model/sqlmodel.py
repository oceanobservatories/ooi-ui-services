#!/usr/bin/env python

'''
ooiservices.model.sqlmodel

SQLModel
'''

from ooiservices.config import DataSource
from ooiservices.adaptor.postgres import PostgresAdaptor as PSQL
from ooiservices.adaptor.sqlite import SQLiteAdaptor as SQL
from ooiservices.model.base import BaseModel

class SqlModel(BaseModel):

    if (DataSource['DBType'] == 'sqlite'):
        sql = SQL(DataSource['DBName'])
    elif (DataSource['DBType'] == 'psql'):
        sql = PSQL(DataSource['DBName'], DataSource['userName'],DataSource['password'], DataSource['host'], DataSource['port'])
    else:
        raise 'DB Unsupported'

    def __init__(self, table_name=None, where_param='id'):
        '''
        Instantiates new base model
        '''
        # A really obscure bug that causes a severe headache down the road
        BaseModel.__init__(self)
        self.tbl = table_name
        self.where_param = where_param

    #CRUD methods
    def create(self, obj):
        '''
        Inserts a new row into the table based on the obj should be a
        dictionary like where the keys are the column headers.
        '''

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
            query = 'SELECT * FROM %s WHERE %s=\'%s\';' % (self.tbl, self.where_param, obj_id)
        else:
            query = 'SELECT * FROM %s;' % (self.tbl)

        answer = self.sql.perform(query)

        return answer

    def update(self, obj):
        obj_id = obj.get('id')
        #Don't want to include the id in the data set to update.
        del obj['id']
        update_set = ', '.join('%s=%r' % (key, val) for (key, val) in obj.items())
        query = 'UPDATE %s SET %s WHERE %s=\'%s\';' % (self.tbl, update_set, self.where_param, obj_id)
        feedback = self.sql.perform(query)
        return feedback

    def delete(self, obj_id):
        query = 'DELETE FROM %s WHERE %s=\'%s\';' % (self.tbl, self.where_param, obj_id)
        feedback = self.sql.perform(query)
        return feedback