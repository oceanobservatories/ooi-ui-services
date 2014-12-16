#!/usr/bin/env python
'''
ooiservices.model.instrument.py

InstrumentModel
'''

__author__ = "Matt Campbell"

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

class InstrumentModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='instruments', where_param='id')