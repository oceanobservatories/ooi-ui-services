#!/usr/bin/env python
'''
tests.model.test_sqlmodel

Tests for the SqlModel
'''

from ooiservices.config import DataSource
from ooiservices.exceptions import ModelException
from ooiservices.model.sqlmodel import SqlModel
from ooiservices.adaptor.postgres import PostgresAdaptor as PSQL
from ooiservices.adaptor.sqlite import SQLiteAdaptor as SQL
from tests.services_test_case import ServicesTestCase
from ooiservices.util.breakpoint import breakpoint
import random
import pytest

postgres = pytest.mark.postgres

class SQLModelMixin(object):
    def test_creation(self):
        '''
        Tests that documents can be created, an id is assigned and read back
        '''

        sql_model = SqlModel('test', ['id', 'reference_id'])
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})
        assert 'id' in retval
        doc = sql_model.read({'id': retval['id']})[0]
        assert doc['reference_id'] == retval['reference_id']

    def test_proper_query_params(self):
        '''
        Tests that a document can be retrieved with an arbitrary where parameter
        '''

        sql_model = SqlModel('test', ['id', 'reference_id'])
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})
        assert 'id' in retval

        doc = sql_model.read({'reference_id' : retval['reference_id']})[0]
        assert doc['reference_id'] == retval['reference_id']

        with pytest.raises(ModelException):
            doc = sql_model.read({'blah' : 'doesnt exist'})

    def test_update(self):
        sql_model = SqlModel('test', ['id', 'reference_id'])
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})

        retval = sql_model.update({'id' : retval['id'], 'value' : 'different'})
        assert retval['value'] == 'different'

        retval = sql_model.read({'id' : retval['id']})[0]
        assert retval['value'] == 'different'

    def test_delete(self):
        sql_model = SqlModel('test', ['id', 'reference_id'])
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})
        sql_model.delete(retval['id'])

        result = sql_model.read({'id' : retval['id']})
        assert len(result) == 0

        
            

class TestSQLModel(ServicesTestCase, SQLModelMixin):
    def setUp(self):
        '''
        Creates a test table to work with as a mock model
        '''
        ServicesTestCase.setUp(self)
        assert DataSource['DBType'] == 'sqlite'
        self.sql = SQL(DataSource['DBName'])

        self.sql.perform('CREATE TABLE IF NOT EXISTS test(id SERIAL PRIMARY KEY, value TEXT, reference_id INT);')

    def tearDown(self):
        '''
        Drops the table we created
        '''

        self.sql.perform('DROP TABLE IF EXISTS test;')

@postgres
class TestPostgresSQLModel(ServicesTestCase, SQLModelMixin):
    def setUp(self):
        '''
        Creates a test table to work with as a mock model
        '''
        ServicesTestCase.setUp(self)
        assert DataSource['DBType'] == 'psql'
        self.sql = PSQL(DataSource['DBName'], DataSource['user'],DataSource['password'], DataSource['host'], DataSource['port'])

        self.sql.perform('CREATE TABLE IF NOT EXISTS test(id SERIAL PRIMARY KEY, value TEXT, reference_id INT);')

    def tearDown(self):
        '''
        Drops the table we created
        '''

        self.sql.perform('DROP TABLE IF EXISTS test;')

