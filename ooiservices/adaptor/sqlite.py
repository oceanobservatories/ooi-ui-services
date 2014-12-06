#!/usr/bin/env python
'''
ooiservices.adaptor.sqlite

Definitions for the SQLiteAdaptor
'''

__author__ = 'Matt Campbell'

import sqlite3 as lite

class SQLiteAdaptor(object):
    db = None

    def __init__(self,dbName):
        object.__init__(self)
        self.db = dbName

    def get_db(self):
        if self.db:
            conn = lite.connect(self.db)
            return conn

    def try_fetch(self, c):
        try:
            result = c.fetchall()
        except lite.Error as e:
            raise
        return result



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
            if obj:
                c.execute(query, obj)
            else:
                c.execute(query)

            result = self.try_fetch(c)
            #possibly condition commit to only insert/update/delete.
            conn.commit()

        except lite.Error, e:
            raise

        finally:
            if conn:
                conn.close()
        return result
