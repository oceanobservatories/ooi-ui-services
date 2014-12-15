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
    minconn  = None
    maxconn  = None
    def __init__(self, database=None, username=None, password=None, host=None, port=None):
        object.__init__(self)
        self.database = database
        self.username = username
        self.password = password
        self.host     = host
        self.port     = port
        self.minconn  = 1
        self.maxconn  = 10
        self.pool     = self._getpool()
    def _getpool(self):
        '''
        create simple connection pool
        '''
        try:
            pool = psycopg2.pool.SimpleConnectionPool(self.minconn,self.maxconn,database=self.database, user=self.username, password=self.password, host=self.host, port=self.port)
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> getpool failed (check config settings): %s: ' % e)
        except:
            raise Exception('<PostgresAdaptor> getpool (check config settings)')
        return pool
    @contextmanager
    def _getcursor(self):
        '''
        get a connection from connection pool, yield cursor, perform commit if successful
        (rollback if exception); finally return connection to the pool.
        '''
        conn = self.pool.getconn()
        try:
            yield conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            conn.commit()
        except:
            conn.rollback()
        finally:
            self.pool.putconn(conn)
    def perform(self, query, *args):
        '''
        Get cursor factory (to return dictionary), execute query and return result
        '''
        try:
            with self._getcursor() as cursor:
                for item in args:
                    cursor.execute(query, (AsIs(item),))
                result = cursor.fetchall()
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> perform failed: %s: ' % e)
        return result