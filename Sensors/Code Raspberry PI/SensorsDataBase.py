#!/use/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys

import mysql.connector
from mysql.connector import errorcode

class SensorsDatabase:

    cursor = None

    def __init__(self, database, user, password, host, port, logger):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.logger = logger

    def create_table(self, t,  col = []):

        self.table = t
        self.column = col

        try:
            self.cursor.execute("""CREATE TABLE {} (
                                id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                                {} DATETIME NOT NULL,.
                                {} DECIMAL(5,2) UNSIGNED NOT NULL,
                                {} DECIMAL(5,2) UNSIGNED NOT NULL,
                                PRIMARY KEY (id)
                                );
                                """.format(self.table,self.column[0],self.column[1],self.column[2]))
            self.logger.debug("Database Created")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.logger.error(err.msg)
            else:
                self.logger.error("Something went wrong: {}".format(err))
                raise
    
    def connection(self):

        try:
            self.conn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                        database=self.database)
            self.cursor = self.conn.cursor()
            if self.conn.is_connected():
                self.logger.debug("Connected to MySQL database")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.error("No database")
            elif err.errno == errorcode.ER_DBACCESS_DENIED_ERROR:
                self.logger.error("Access Denied : No database = %s" %self.database)
            elif err.errno == errorcode.ER_ACCESS_DENIED_NO_PASSWORD_ERROR:
                self.logger.error("Access Denied : No user = %s" %self.user)
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.logger.error("Access Denied : Password error")
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                self.logger.error("Access Denied : Host error or Port error = %s" %self.host + ":%s" %self.port)
            else:
                self.logger.error("Something went wrong: {}".format(err))
                raise

    def disconnection(self):

        self.cursor.close()
        self.conn.close()
        if self.conn.is_connected() != 1:
            self.logger.debug("Disconnected to MySQL")

    def insert_data(self, date, data = []):

        query = "INSERT INTO {}({},{})".format(self.table,self.column[0],','.join(self.column[1:])) + \
                "VALUES(\"{}\",{})".format(date,",".join(str(d) for d in data))
        
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.debug("Insert completed")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_FIELD_ERROR:
                self.logger.error(err.msg)
            elif err.errno == errorcode.ER_PARSE_ERROR:
                self.logger.error("Syntax Error : %s" % ",".join(str(d) for d in self.column))
            elif err.errno == errorcode.ER_WRONG_VALUE_COUNT_ON_ROW:
                self.logger.error(err.msg)
            else:
                self.logger.error("Something went wrong: {}".format(err))
                raise