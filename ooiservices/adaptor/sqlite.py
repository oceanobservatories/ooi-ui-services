#!/usr/bin/env python
'''
ooiservices.adaptor.sqlite

Definitions for the SQLiteAdaptor
'''

__author__ = 'Matt Campbell'

import sqlite3 as lite

class SQLiteAdaptor(object):
    '''
    An adaptor for a SQLite conncetion
    '''

    def __init__(self, db_name):
        '''
        Initializes the SQLite Adaptor and makes a persistent database
        connection
        '''
        object.__init__(self)
        self.db = db_name
        self.conn = None
        self.get_db()

    def get_db(self):
        '''
        Returns an initialized connection
        '''
        if self.conn is None:
            self.conn = lite.connect(self.db)
        return self.conn

    def try_fetch(self, cursor):
        '''
        Attempts a fetch or result rows
        '''
        try:
            result = cursor.fetchall()
        except lite.Error:
            raise
        return result




    def perform(self, query, obj=None):
        '''
        Performs the SQL query
        '''
        self.conn.row_factory = dict_factory
        cursor = self.conn.cursor()

        try:
            if obj:
                cursor.execute(query, obj)
            else:
                cursor.execute(query)

            result = self.try_fetch(cursor)
            #possibly condition commit to only insert/update/delete.
            self.conn.commit()

        except lite.Error:
            raise

        return result

    def close(self):
        '''
        Closes the database connection
        '''
        self.conn.close()

def dict_factory(cursor, row):
    '''
    Factory method for the cursor
    '''
    doc = {}
    for idx, col in enumerate(cursor.description):
        doc[col[0]] = row[idx]
    return doc
