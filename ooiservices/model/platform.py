#!/usr/bin/env python
'''
ooiservices.model.platform.py

'''

from ooiservices.model.base import BaseModel

__author__ = "Matt Campbell"

class PlatformModel(BaseModel):

    def __init__(self):
        BaseModel.__init__(self, 'platform')