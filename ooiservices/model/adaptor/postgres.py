#!/usr/bin/env python
'''
ooiservices.adaptor.postgresadaptor

Definitions for the PostgresAdaptor
'''

__author__ = 'Edna Donoughe'

import psycopg2
import psycopg2.extras
from psycopg2.extensions import AsIs

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

    def get_db(self):
        try:
            conn = psycopg2.connect(database=self.database, user=self.username, password=self.password, host=self.host, port=self.port)
            return conn
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> connect failed (check config): %s: ' % e)
        except:
            raise Exception('<PostgresAdaptor> get_db failed to connect; check config settings')

    def perform(self, query, *args):
        #Create a cursor_factory to return dictionary
        conn = self.get_db()
        try:

            cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            print(query)
            for item in args:
                cursor.execute(query, (AsIs(item),))

            result = cursor.fetchall()
            conn.commit()

        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> perform failed: %s: ' % e)

        finally:
            if conn:
                conn.close()

        return result