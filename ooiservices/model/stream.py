#!/usr/bin/env python
'''
ooiservices.model.stream.py

StreamModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class StreamModel(SqlModel):
    table_name = 'streams'
    where_params = ['id']

class Parameter(SqlModel):
    table_name = 'parameters'
    where_params = ['id']
