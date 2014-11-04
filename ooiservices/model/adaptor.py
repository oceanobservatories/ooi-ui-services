#!/usr/bin/env python
'''
ooiservices.model.adaptor

Definitions for the BaseAdaptor and the FileAdaptor mock
'''

import uuid
import os
import json
import sqlite3 as lite

class BaseAdaptor:
    '''
    Base class for adaptor implementations
    '''
    pass

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


class SQLiteAdaptor(object):
    __author__ = 'Matt Campbell'
    db = None

    def __init__(self,dbName):
        object.__init__(self)
        self.db = dbName

    def get_db(self):
        if self.db:
            conn = lite.connect(self.db)
            return conn

    def perform(self, query, obj=None):
        #Create a factory to return dictionary
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        conn = self.get_db()
        conn.row_factory = dict_factory
        c = conn.cursor()
        
        try:
            if lite.complete_statement(query):
                if obj:
                    c.execute(query, obj)
                else:
                    c.execute(query)

            result = c.fetchall()
            #possibly condition commit to only insert/update/delete.
            conn.commit()

        except lite.Error, e:
            result = '%s' % e.args[0]
            print query

        finally:
            if conn:
                conn.close()
        return result