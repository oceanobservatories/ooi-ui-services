#!/usr/bin/env python
'''
tests.model.sql_model_mixin

Mixin for SQL Model testing
'''

from ooiservices.config import DataSource
from ooiservices.exceptions import ModelException
from ooiservices.model.sqlmodel import SqlModel
from tests.services_test_case import ServicesTestCase
from ooiservices.util.breakpoint import breakpoint
import random
import pytest

class TestModel(SqlModel):
    table_name = 'test'
    where_params = ['id', 'reference_id']

class SQLModelMixin(object):
    def test_creation(self):
        '''
        Tests that documents can be created, an id is assigned and read back
        '''

        sql_model = TestModel()
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})
        assert 'id' in retval
        doc = sql_model.read({'id': retval['id']})[0]
        assert doc['reference_id'] == retval['reference_id']

    def test_proper_query_params(self):
        '''
        Tests that a document can be retrieved with an arbitrary where parameter
        '''

        sql_model = TestModel()
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})
        assert 'id' in retval

        doc = sql_model.read({'reference_id' : retval['reference_id']})[0]
        assert doc['reference_id'] == retval['reference_id']

        with pytest.raises(ModelException):
            doc = sql_model.read({'blah' : 'doesnt exist'})

    def test_update(self):
        sql_model = TestModel()
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})

        retval = sql_model.update({'id' : retval['id'], 'value' : 'different'})
        assert retval['value'] == 'different'

        retval = sql_model.read({'id' : retval['id']})[0]
        assert retval['value'] == 'different'

    def test_delete(self):
        sql_model = TestModel()
        retval = sql_model.create({'value' : 'hi', 'reference_id' : random.randint(0,100)})
        sql_model.delete(retval['id'])

        result = sql_model.read({'id' : retval['id']})
        assert len(result) == 0
