#!/usr/bin/env python
'''
ooiservices.model.stream.py

StreamModel
'''
__author__ = "Matt Campbell"

from ooiservices.model.interface.sqlmodel import SqlModel

class StreamModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='streams', where_param='instrument_deployment_code')