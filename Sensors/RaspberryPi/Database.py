#!/use/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import datetime

import mysql.connector
from mysql.connector import errorcode

class Database:
    
    cursor = None

    def __init__(self, database, user, password, host, port, logger):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.logger = logger


    # Create table in database
    def create_table(self, t,  col = []):
    
        self.table = t
        if "date" in col[0] or "Date" in col[0]:
            self.column = col
        else:
            self.logger.error("No date in column 0")
            return "Error date"
        
        query = "CREATE TABLE {} (id INT UNSIGNED NOT NULL AUTO_INCREMENT,{} DATETIME NOT NULL,".format(self.table,self.column[0])
        
        for i in range(1,len(col)):
            query += "{} DECIMAL(5,2) UNSIGNED NOT NULL,".format(self.column[i])
        
        query += "PRIMARY KEY (id));"
        self.logger.debug("Query : %s" %query)
        try:
            self.cursor.execute(query)
            self.logger.debug("Table created")
            return "Table created"
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.logger.debug(err.msg)
            else:
                self.logger.error("Something went wrong: {}".format(err))
                raise




    # Connection to MySQL
    def connection(self):

        try:
            self.conn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                        database=self.database)
            self.cursor = self.conn.cursor()
            if self.conn.is_connected():
                self.logger.info("Connected to MySQL database")
                return "Connected to MySQL database"
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
            return "Connection failed"

    # Disconnection to MySQL
    def disconnection(self):
        self.cursor.close()
        self.conn.close()
        if self.conn.is_connected() != 1:
            self.logger.info("Disconnected to MySQL")
            return "Disconnected to MySQL"
        else:
            return "Disconnection failed"

    # Insert data in database
    def insert_data(self, date, *data):

        query = "INSERT INTO {}({},{})".format(self.table,self.column[0],','.join(self.column[1:])) + \
                "VALUES(\"{}\",{})".format(date,",".join(str(d) for d in data))
        self.logger.debug("Query : %s" %query)
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.debug("Insert data completed")
            return "Insert data completed"
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
            return "Insert data failed"


    def insert_data_bulk(self, table, col, data):
        
        if not data:
            return "No data"
        # Build the SQL query
        i = 0
        query = "INSERT INTO {}({},{})".format(table,col[0],','.join(col[1:])) + " VALUES "
        for i in range(0, len(data) - 1):
            query += "(\"{}\",{}), ".format(data[i][0], ",".join(str(d) for d in data[i][1:]))
        query += "(\"{}\",{});".format(data[-1][0],  ",".join(str(d) for d in data[-1][1:]))

        self.logger.debug("Query  :\n" + query)

        # Send it to remote DB
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.debug("Succesfully inserted {} records into the Database".format(len(data)))
            return "Insert data completed"
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
            return "Insert data failed"