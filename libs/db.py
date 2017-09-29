#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:   lizs
# Site:     http://alizs.cc
# Time:     8/30/17 2:21 PM

import MySQLdb
from common import get_config


class Db(object):
    def __init__(self, host=None, port=None, user=None, password=None, db=None):
        self.conn = None
        self.cursor = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        # database name
        self.db = db if db else ''
        # when connect to MySQL fail, the maximum times that can be connected
        self.max_connect_times = 5
        # the connect timeout of which connection
        self.connect_timeout = 5

    def connect(self):
        """Connect to MySQL."""
        connect_times = 0
        while connect_times < self.max_connect_times:
            try:
                self.close()
                self.conn = MySQLdb.connect(host=self.host, port=self.port,
                                            user=self.user, passwd=self.password,
                                            db=self.db, charset='utf8',
                                            connect_timeout=self.connect_timeout)
                self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
                return True
            except Exception, err:
                connect_times += 1
                print(str(err))
        return False

    def default_connect(self):
        """Connect to MySQL via the default config."""
        try:
            config = get_config('database')
            self.host = config['host']
            self.port = config['port']
            self.user = config['user']
            self.password = config['password']
            self.db = config['db']
            if self.connect():
                return self
        except Exception, err:
            print(str(err))
        return False

    def close(self):
        try:
            self.conn and self.conn.close()
            self.cursor and self.cursor.close()
        except Exception, err:
            if 'closing a closed connection' not in str(err):
                print(str(err))
        return True

    def execute(self, sql, args=None):
        if self.connect():
            self.cursor.execute(sql, args)
            self.conn.commit()
            return True
        return False

    def fetchone(self, sql, args=None):
        if self.execute(sql, args):
            return self.cursor.fetchone()
        return False

    def fetchall(self, sql, args=None):
        if self.execute(sql, args):
            return self.cursor.fetchall()
        return False

    def insert(self, sql=None, table=None, params=None, args=None):
        # insert data by sql
        if sql and not table and not params:
            self.execute(sql, args)
        # insert data by a mapping dictionary params
        if not sql and table and params:
            pass

    def batch_insert(self, table, params):
        """Batch insert data.

        - table: the table name
        - params: a dictionary of insert data.
        """
        count = 0
        max_count = 50
        insert_fields = []
        insert_values = []
        _, fields = params.popitem()
        for k, v in fields.items():
            insert_fields.append(r'`%s`' % k)
            insert_values.append(v)
        insert_fields_str = ', '.join(insert_fields)
        insert_values_str = '({})'.format(', '.join(['%s'] * len(insert_fields)))
        init_insert_sql = 'INSERT INTO `{}` ({}) VALUES '.format(table, insert_fields_str)
        insert_sql = init_insert_sql + insert_values_str
        for _, item in params.items():
            count += 1
            if count <= max_count:
                insert_sql += ', {}'.format(insert_values_str)
                insert_values.extend(list(item.values()))
            else:
                insert_sql += ';'
                self.execute(insert_sql, insert_values)
                count = 1
                insert_sql = init_insert_sql + insert_values_str
                insert_values = list(item.values())
        # insert the last items that less then 50
        if count <= max_count:
            insert_sql += ';'
            self.execute(insert_sql, insert_values)
        return True

