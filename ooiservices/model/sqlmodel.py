#!/usr/bin/env python

'''
ooiservices.model.sqlmodel

SQLModel
'''
#Wrapper functions for jsonp output
from ooiservices.exceptions import ModelException
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

    def __init__(self):
        '''
        Instantiates new base model
        '''
        from ooiservices import get_db
        # A really obscure bug that causes a severe headache down the road
        BaseModel.__init__(self)
        self.sql = get_db()
        if (DataSource['DBType'] == 'sqlite'):
            self.holder = '?'
        elif (DataSource['DBType'] == 'psql'):
            self.holder = '%s'
        else:
            raise ModelException('Unsupported Database: %s' % DataSource['DBType'])

    '''
        mjc - Trying this out for the read method.
        Acquired from:
        http://flask.pocoo.org/snippets/79/
        on:
        12/09/2014
    '''
    #CRUD methods
    def create(self, obj):
        '''
        Inserts a new row into the table based on the obj should be a
        dictionary like where the keys are the column headers.
        '''
        columns = ', '.join(obj.keys())
        placeholders = ':'+', :'.join(obj.keys())
        query = 'INSERT INTO ' + self.tbl + ' ( ' + columns + ' ) VALUES ( ' + self.holder + ' );'
        feedback = self.sql.perform(query, placeholders)
        return feedback

    def read(self, query_params=None):
        '''
        Modified to (temporarily) support interim UI specification for output
        '''
        if obj_id:
            query = 'SELECT * FROM ' + self.tbl + ' WHERE %s = ' + self.holder + ';' % (self.where_param)
            answer = self.sql.perform(query, obj_id)
        else:
            query = 'SELECT * FROM ' + self.tbl + ';'
            answer = self.sql.perform(query, None)

        return answer

    def update(self, obj):
        '''
        Updates a single document
        '''
        obj_id = obj.get('id')
        #Don't want to include the id in the data set to update.
        del obj['id']
        update_set = ', '.join('%s=%r' % (key, val) for (key, val) in obj.items())
        query = 'UPDATE ' + self.tbl + ' SET ' + update_set + ' WHERE %s =' + self.holder + ';' % (self.where_param)
        feedback = self.sql.perform(query, obj_id)
        return feedback

    def delete(self, obj_id):
        query = 'DELETE FROM ' + self.tbl + ' WHERE %s =' +self.holder + ';' % (self.where_param)
        feedback = self.sql.perform(query, obj_id)
        return feedback