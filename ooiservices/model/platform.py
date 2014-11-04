#!/usr/bin/env python
'''
ooiservices.model.platform.py

'''

from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class PlatformModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, 'platform')

        # work with UI modifications and sample data (use sample.db)
        #SqlModel.__init__(self, tableName='ooi_platforms', whereParam='array_code',reformatOutput=True)