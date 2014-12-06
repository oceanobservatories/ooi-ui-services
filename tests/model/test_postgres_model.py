#!/usr/bin/env python
'''
tests.model.test_postgres_model

Tests for the Postgres SqlModel
'''

from ooiservices.config import DataSource
from ooiservices.adaptor.postgres import PostgresAdaptor as PSQL
from ooiservices.adaptor.sqlite import SQLiteAdaptor as SQL
from tests.services_test_case import ServicesTestCase
from tests.model.sql_model_mixin import SQLModelMixin
from ooiservices.util.breakpoint import breakpoint
import random
import pytest

postgres = pytest.mark.postgres

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

