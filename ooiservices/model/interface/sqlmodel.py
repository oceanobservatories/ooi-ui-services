#!/usr/bin/env python
'''
ooiservices.model.sqlmodel
SQLModel
'''
#Wrapper functions for jsonp output
from ooiservices.config import DataSource
from ooiservices.model.adaptor.postgres import PostgresAdaptor as PSQL
from ooiservices.model.adaptor.sqlite import SQLiteAdaptor as SQL
from ooiservices.model.base import BaseModel

class SqlModel(BaseModel):

    if (DataSource['DBType'] == 'sqlite'):
        sql = SQL(DataSource['DBName'])
        holder = '?'
    elif (DataSource['DBType'] == 'psql'):
        sql = PSQL(DataSource['DBName'], DataSource['userName'],DataSource['password'], DataSource['host'], DataSource['port'])
        holder = '%s'
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
        columns = ', '.join(obj.keys())
        #placeholders = ':'+', :'.join(obj.values())
        placeholders = ','.join([self.holder for _ in range(len(obj.values()))])
        query = 'INSERT INTO ' + self.tbl + ' ( ' + columns + ' ) VALUES ( ' + placeholders + ' );'
        #feedback = self.sql.perform(query, placeholders)
        feedback = self.sql.perform(query, obj.values())
        return feedback

    def read(self, obj_id=None):
        if obj_id:
            query = 'SELECT * FROM ' + self.tbl + ' WHERE ' + self.where_param + ' = ' + self.holder + ';'
            param_list = [obj_id]
            answer = self.sql.perform(query, param_list)
        else:
            query = 'SELECT * FROM ' + self.tbl + ';'
            answer = self.sql.perform(query, None)
        return answer

    def update(self, obj):
        param_list = [ obj.get('id') ]
        #Don't want to include the id in the data set to update.
        del obj['id']
        update_set = ', '.join('%s=%r' % (key, val) for (key, val) in obj.items())
        query = 'UPDATE ' + self.tbl + ' SET ' + update_set + ' WHERE ' + self.where_param + ' = ' + self.holder + ';'
        feedback = self.sql.perform(query, param_list)
        return feedback

    def delete(self, obj_id):
        param_list = [obj_id]
        query = 'DELETE FROM ' + self.tbl + ' WHERE %s =' + self.holder + ';' % (self.where_param)
        feedback = self.sql.perform(query, param_list)
        return feedback