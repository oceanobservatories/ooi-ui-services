#!/usr/bin/env python
'''
ooiservices.model.array.py

InstrumentModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class ArrayModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='arrays')