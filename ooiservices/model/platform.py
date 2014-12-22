#!/usr/bin/env python
'''
ooiservices.model.interface.platform.py

PlatformModel
'''

from ooiservices import app
from ooiservices.model.interface.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class PlatformModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='platforms', where_param='id')