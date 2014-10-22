#!/usr/bin/env python
'''
ooiservices.model.platform.py

Platform resource

'''

from model.base import BaseModel


__author__ = "Matt Campbell"

class PlatformModel(BaseModel):


    __cols__ = ['id']

    id = None

    def __init__(self):
        BaseModel.__init__(self)


    def _check(self):
        '''
        Will be used to check the parcel that the contents is worth using.
        '''
        pass

        '''
    External CRUD implementation from BaseModel
    '''
    def create(self, obj):
        createResult = adapter.create(obj)
        return createResult

    def read(self, id):
        readResult = adapter.read(id)
        return readResult

    def update(self, obj):
        updateResult = adapter.update(obj)
        return updateResult

    def delete(self, id):
        deleteResult = adapter.delete(id)
        return deleteResult