#!/usr/bin/env python
'''
ooiservices.adaptor.file

Definitions for the FileAdaptor mock
'''


from ooiservices.adaptor.base import BaseAdaptor

import uuid
import os
import json
import sqlite3 as lite

class FileAdaptor(BaseAdaptor):
    '''
    An adaptor that manages a file system of json documents
    '''
    directory = None
    def __init__(self, directory):
        self.directory = directory

    def _get_file_handle(self, doc_id):
        '''
        returns the file path for a given document
        '''
        filename = doc_id + '.json'
        filepath = os.path.join(self.directory, filename)
        return filepath

    def create(self, doc):
        '''
        Creates the document and persists it to the file system
        '''
        doc_id = doc.get('id', uuid.uuid4().hex)
        doc['id'] = doc_id
        filepath = self._get_file_handle(doc_id)
        if os.path.exists(filepath):
            raise IOError("Document already exists with id %s" % doc_id)
        with open(filepath, 'w') as f:
            f.write(json.dumps(doc))
        return doc_id

    def read(self, doc_id):
        '''
        Reads the document from the file system
        '''
        filepath = self._get_file_handle(doc_id)
        with open(filepath, 'r') as f:
            buf = f.read() # TODO: may have problems with documents larger than max_buf
        doc = json.loads(buf)
        return doc

    def update(self, doc):
        '''
        Updates the specified document
        '''
        doc_id = doc.get('id', uuid.uuid4().hex)
        filepath = self._get_file_handle(doc_id)
        with open(filepath, 'w') as f:
            f.write(json.dumps(doc))
        return doc_id

    def delete(self, doc_id):
        '''
        Deletes the specified document from the file system
        '''
        filepath = self._get_file_handle(doc_id)
        os.unlink(filepath)
        return True

