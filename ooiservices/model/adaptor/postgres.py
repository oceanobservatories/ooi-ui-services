#!/usr/bin/env python
'''
ooiservices.adaptor.postgresadaptor

Definitions for the PostgresAdaptor
'''

__author__ = 'Edna Donoughe'

import psycopg2
import psycopg2.pool
import psycopg2.extras
from psycopg2.extensions import AsIs
from contextlib import contextmanager
class PostgresAdaptor(object):
    database = None
    username = None
    password = None
    host     = None
    port     = None
    def __init__(self, database=None, username=None, password=None, host=None, port=None):
        object.__init__(self)
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.pool = self._getpool()
    #Helper function to ensure the database connection.  Formerly getDB()
    def _getpool(self):
        try:
            pool = psycopg2.pool.SimpleConnectionPool(1,10,database=self.database, user=self.username, password=self.password, host=self.host, port=self.port)
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> getpool failed (check config settings): %s: ' % e)
        except:
            raise Exception('<PostgresAdaptor> getpool (check config settings)')
        return pool

    @contextmanager
    def _getcursor(self):
        con = self.pool.getconn()
        try:
            yield con.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        finally:
            self.pool.putconn(con)

    def perform(self, query, *args):
        #Create a cursor_factory to return dictionary
        try:
            with self._getcursor() as cursor:
                for item in args:
                    cursor.execute(query, (AsIs(item),))
                result = cursor.fetchall()
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> perform failed: %s: ' % e)

        return result