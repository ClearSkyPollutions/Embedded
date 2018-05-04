#!/use/bin/env python3
# -*- coding: utf-8 -*-

import abc
import logging
import sys
import datetime

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

    # Create table in database
    def create_table(self, t,  col = []):

        self.table = t
        if col [0] == "date" or col [0] == "Date":
            self.column = col
        else:
            self.logger.error("No date in row 0")
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
                self.logger.error(err.msg)
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
                self.logger.debug("Connected to MySQL database")
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
            self.logger.debug("Disconnected to MySQL")
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

    def getdate(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @abc.abstractmethod
    def setup(self):
        """Method to sensor setup"""

    @abc.abstractmethod
    def start(self):
        """Method to read data"""

    @abc.abstractmethod
    def stop(self):
        """Method to stop the program"""
    

