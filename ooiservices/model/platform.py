#!/usr/bin/env python
'''
ooiservices.model.platform.py

PlatformModel
'''

from ooiservices import app
from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class PlatformModel(SqlModel):
    table_name = 'platforms'
    where_params = ['id']

