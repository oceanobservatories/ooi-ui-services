#!/usr/bin/env python
'''
ooiservices.model.platform.py

Platform resource

'''

from model.base import BaseModel


__author__ = "Matt Campbell"

class PlatformModel(BaseModel):

    '''
    At this point __cols__ is simply a model place holder.
    '''
    __cols__ = ['id']
    id = None

    def __init__(self):
        BaseModel.__init__(self)


    def _check(self):
        '''
        Will be used to check if the parcel's contents is worth using.
        '''
        pass

    '''
    External CRUD implementation from BaseModel
    '''
    def create(self, obj):
        createResult = {'id' : 'create method'}
        #createResult = adapter.create(obj)
        return createResult

    def read(self, id):
        readResult = {'id' : 'read method'}
        #readResult = adapter.read(id)
        return readResult

    def update(self, obj):
        updateResult = {'id' : 'update method'}
        #updateResult = adapter.update(obj)
        return updateResult

    def delete(self, id):
        deleteResult = {'id' : 'delete method'}
        #deleteResult = adapter.delete(id)
        return deleteResult