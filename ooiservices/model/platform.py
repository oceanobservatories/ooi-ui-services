#!/usr/bin/env python
'''
ooiservices.model.platform.py

'''

from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class PlatformModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, 'ooi_platforms')