#!/usr/bin/env python
'''
ooiservices.model.instrument.py

InstrumentModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class InstrumentModel(SqlModel):
    table_name = 'instruments'
    where_params = ['id']

