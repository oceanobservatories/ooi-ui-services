#!/usr/bin/env python
'''
ooiservices.model.platform.py

'''

from ooiservices.model.sqlmodel import SqlModel

__author__ = "Matt Campbell"

class PlatformModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, 'platforms')


    def read(self):
        #TODO: this isn't working quite right, it's not gouping by platform id
        query = 'SELECT arrays.name, nodes.name, sites.name, subsites.name FROM arrays, nodes, sites, subsites, platforms WHERE arrays.id=platforms.array AND nodes.id=platforms.node AND sites.id=platforms.node AND subsites.id=platforms.subsite ORDER BY platforms.id;'
        answer = self.sql.perform(query)
        return answer