#!/usr/bin/env python
'''
ooiservices.model.parameter.py

ParameterModel
'''
__author__ = "Matt Campbell"

from ooiservices.model.interface.sqlmodel import SqlModel

class Parameter(SqlModel):
    def __init__(self):
        SqlModel.__init__(self, table_name='stream_parameters')