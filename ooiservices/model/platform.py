#!/usr/bin/env python
'''
ooiservices.model.platform.py

'''

from ooiservices.model.sqlmodel import SQLModel

__author__ = "Matt Campbell"

class PlatformModel(SQLModel):

    def __init__(self):
        SQLModel.__init__(self, 'platform')
