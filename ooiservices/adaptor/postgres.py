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
        self.get_db()

    def get_db(self):
        try:
            self.conn = psycopg2.connect(database=self.database, user=self.username, password=self.password, host=self.host, port=self.port)
            return self.conn
        except psycopg2.DatabaseError, e:
            raise Exception('<PostgresAdaptor> connect failed (check config): %s: ' % e)
        except:
            raise Exception('<PostgresAdaptor> get_db failed to connect; check config settings')

    def try_fetch(self, c):
        '''
        Returns either the result set OR None if there are no results to fetch in the case of DML
        '''
        try:
            result = c.fetchall()
        except psycopg2.DatabaseError as e:
            if 'no results to fetch' in e.message:
                return None
            raise
        return result


    def perform(self, query, arg_list=None):
        '''
        Executes the SQL Query
        '''
        try:

            cursor = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            if arg_list:
                cursor.execute(query, arg_list)
            else:
                cursor.execute(query)

            result = self.try_fetch(cursor)

            self.conn.commit()

        except psycopg2.DatabaseError as e:
            raise Exception('<PostgresAdaptor> perform failed: %s: ' % e)

        return result

    def close(self):
        '''
        Closes the database connection
        '''
        self.conn.close()
