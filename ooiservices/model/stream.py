#!/usr/bin/env python
'''
ooiservices.model.stream.py

StreamModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class StreamModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='streams')

    class Parameter(SqlModel):
        def __init__(self):
            SqlModel.__init__(self, table_name='stream_parameters')