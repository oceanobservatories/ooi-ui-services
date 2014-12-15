#!/usr/bin/env python
'''
ooiservices.model.instrument.py

InstrumentModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class InstrumentModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='instruments', where_param='id')

    class InstrumentDeployment(SqlModel):

        def __init__(self):
            SqlModel.__init__(self, table_name='instrument_deployments', where_param='id')