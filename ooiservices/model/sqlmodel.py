#!/usr/bin/env python

'''
ooiservices.model.sqlmodel

SQLModel
'''

from ooiservices.exceptions import ModelException
from ooiservices.config import DataSource
from ooiservices.adaptor.postgres import PostgresAdaptor as PSQL
from ooiservices.adaptor.sqlite import SQLiteAdaptor as SQL
from ooiservices.model.base import BaseModel

class SqlModel(BaseModel):


    def __init__(self):
        '''
        Instantiates new base model
        '''
        # A really obscure bug that causes a severe headache down the road
        BaseModel.__init__(self)
        if (DataSource['DBType'] == 'sqlite'):
            self.sql = SQL(DataSource['DBName'])
            self.holder = '?'
        elif (DataSource['DBType'] == 'psql'):
            self.sql = PSQL(DataSource['DBName'], DataSource['user'],DataSource['password'], DataSource['host'], DataSource['port'])
            self.holder = '%s'
        else:
            raise ModelException('Unsupported Database: %s' % DataSource['DBType'])

    #CRUD methods
    def create(self, obj):
        '''
        Inserts a new row into the table based on the obj should be a
        dictionary like where the keys are the column headers.
        '''

        if 'id' not in obj:
            obj['id'] = self._get_latest_id() + 1

        columns = ', '.join(obj.keys())
        empties = ', '.join([self.holder for col in obj])
        query = 'INSERT INTO ' + self.table_name + ' (' + columns + ') VALUES (' + empties + ');'
        feedback = self.sql.perform(query, obj.values())


        return obj


    def read(self, query_params=None):
        '''
        Modified to (temporarily) support interim UI specification for output
        '''
        query_params = query_params or {}

        if query_params:
            where_clause, query_items = self._build_where_clause(query_params)
            query = 'SELECT * FROM ' + self.table_name + ' WHERE ' + where_clause
            answer = self.sql.perform(query, query_items)
        else:
            query = 'SELECT * FROM %s;' % (self.table_name)

            answer = self.sql.perform(query)

        return answer

    def update(self, obj):
        '''
        Updates a single document
        '''
        obj_id = obj.get('id')
        #Don't want to include the id in the data set to update.
        del obj['id']
        update_clause, query_params = self._build_update_clause(obj)
        query = 'UPDATE ' + self.table_name + ' SET ' + update_clause + ' WHERE id=' + str(obj_id) + ';'
        feedback = self.sql.perform(query, query_params)
        return self.read({'id' : obj_id})[0]

    def delete(self, obj_id):
        '''
        Deletes a single document
        '''
        query = 'DELETE FROM ' + self.table_name + ' WHERE id=' + self.holder
        feedback = self.sql.perform(query, (obj_id,))
        return feedback
    
    def _build_where_clause(self, query_params):
        '''
        Returns the WHERE clause and the tuple of items to pass in with the
        string
        '''
        raw_clauses = []
        query_items = []

        for field, value in query_params.iteritems():
            if field in self.where_params:
                raw_clauses.append(field + '=' + self.holder)
                query_items.append(value)
            else:
                raise ModelException("%s is not a valid where parameter" % field)
        raw_clause = ' AND '.join(raw_clauses)
        return raw_clause, query_items

    def _build_update_clause(self, obj):
        '''
        Returns a tuple of the key/value part of the UPDATE clause and the
        query params
        '''
        raw_clauses = []
        for field, value in obj.iteritems():
            raw_clauses.append(field + '=' + self.holder)
        raw_clause = ', '.join(raw_clauses)
        return raw_clause, obj.values()


    def _get_latest_id(self):
        query = 'SELECT id FROM ' + self.table_name + ' ORDER BY id DESC LIMIT 1'
        results = self.sql.perform(query)
        if not results:
            return 0 # the very first
        return results[0]['id']

