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

    def _getpool(self):
        '''
        create simple connection pool
        '''
        try:
            pool = psycopg2.pool.SimpleConnectionPool(self.minconn,self.maxconn,database=self.database, user=self.username, password=self.password, host=self.host, port=self.port)
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> getpool failed (check config settings): %s: ' % e)
        return pool

    def perform(self, query, params):
        '''
        Get cursor factory (to return dictionary), execute query and return result
        '''
        pool = self._getpool()
        conn = pool.getconn()
        result = None
        try:
            cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            print "the param for query %s is %s" % (query, params)
            cursor.execute(query, params)
            conn.commit()
            result = cursor.fetchall()
        except:
            conn.rollback()
        finally:
            pool.putconn(conn)
        return result