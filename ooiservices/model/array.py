#!/usr/bin/env python
'''
ooiservices.model.array.py

ArrayModel
'''
from ooiservices.model.interface.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class ArrayModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='arrays')