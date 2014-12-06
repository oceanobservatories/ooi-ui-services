#!/usr/bin/env python
'''
ooiservices.model.array.py

InstrumentModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class ArrayModel(SqlModel):
    table_name = 'arrays'
    where_params = ['id', 'array_code']

