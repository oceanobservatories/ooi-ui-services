#!/usr/bin/env python
'''
ooiservices.adaptor.postgresadaptor

Definitions for the PostgresAdaptor
'''

__author__ = 'Edna Donoughe'

import psycopg2
import psycopg2.extras

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
        if not (self.database and self.username and self.password and self.host and self.port):
            raise Exception('<PostgresAdaptor> required config setting empty')

    def get_db(self):
        try:
            conn = psycopg2.connect(database=self.database, user=self.username, password=self.password, host=self.host, port=self.port)
            return conn
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> connect failed (check config): %s: ' % e)
        except:
            raise Exception('<PostgresAdaptor> get_db failed to connect; check config settings')

    def perform(self, query, arg_list=None):
        #Create a cursor_factory to return dictionary
        conn = self.get_db()
        try:

            c = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            if arg_list:
                c.execute(query, arg_list)
            else:
                c.execute(query)

            result = c.fetchall()
            conn.commit()

        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> perform failed: %s: ' % e)

        finally:
            if conn:
                conn.close()

        return result
