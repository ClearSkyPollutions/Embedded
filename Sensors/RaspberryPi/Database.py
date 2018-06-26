#!/use/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import datetime

import mysql.connector
from mysql.connector import errorcode


class Database:

    cursor = None
    sysId = None

    def __init__(self, database, user, password, host, port, logger):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.logger = logger

    def add_type(self, sensor_name, pollutant, unit):
        query = "INSERT INTO POLLUTANT(name, unit, sensor) VALUES(%s, %s, %s)"
        try:
            self.cursor.execute(query, (pollutant, unit, sensor_name))
            self.conn.commit()
            self.logger.debug(
                "Inserted new type in POLLUTANT for : " + pollutant)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.logger.debug(err.msg)
            else:
                self.logger.exception()
                raise RuntimeError("Error creating table")

    # Create table in database
    def get_ids(self, sensor_name, pollutants, units):
        res = {}
        query = "SELECT id FROM POLLUTANT WHERE sensor = \"{}\" and name = %s".format(
            sensor_name)
        for i, j in zip(pollutants, units):
            try:
                # execute needs a param un tuple form, -> (i,)
                self.cursor.execute(query, (i,))
                res[i] = self.cursor.fetchone()["id"]
                self.logger.debug("Get pollutant id :" + res[i])
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.debug(err.msg)
                else:
                    self.logger.exception()
                    raise RuntimeError("Error creating table")
            except TypeError:
                self.add_type(sensor_name, i, j)
        return res

    # Create table in database
    def create_table(self, t,  col=[]):

        self.table = t
        if "date" in col[0] or "Date" in col[0]:
            self.column = col
        else:
            self.logger.error("No date in column 0")
            raise TypeError("First column is not date")

        query = "CREATE TABLE {} (id INT UNSIGNED NOT NULL AUTO_INCREMENT,{} DATETIME NOT NULL,".format(
            self.table, self.column[0])

        for i in range(1, len(col)):
            query += "{} DECIMAL(5,2) UNSIGNED NOT NULL,".format(
                self.column[i])

        query += "PRIMARY KEY (id));"
        self.logger.debug("Query : %s" % query)

        try:
            self.cursor.execute(query)
            self.logger.debug("Table created")

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.logger.debug(err.msg)
            else:
                self.logger.exception()
                raise RuntimeError("Error creating table")

    # Connection to MySQL
    def connection(self):

        try:
            self.conn = mysql.connector.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                                database=self.database)
            self.cursor = self.conn.cursor(dictionary=True)
            if self.conn.is_connected():
                self.logger.info("Connected to MySQL database")

            # Get the system ID
            # @TODO: Error management, centralDB verification
            query = "SELECT id FROM SYSTEM"
            self.cursor.execute(query)
            self.sysId = self.cursor.fetchone()["id"]

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.error("No database")
            elif err.errno == errorcode.ER_DBACCESS_DENIED_ERROR:
                self.logger.error(
                    "Access Denied : No database = %s" % self.database)
            elif err.errno == errorcode.ER_ACCESS_DENIED_NO_PASSWORD_ERROR:
                self.logger.error("Access Denied : No user = %s" % self.user)
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.logger.error("Access Denied : Password error")
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                self.logger.error(
                    "Access Denied : Host error or Port error = %s" % self.host + ":%s" % self.port)
            else:
                self.logger.error("Something went wrong: {}".format(err))
            raise RuntimeError("Error accessing DB")

    # Disconnection to MySQL
    def disconnection(self):
        self.cursor.close()
        self.conn.close()
        if self.conn.is_connected() != 1:
            self.logger.info("Disconnected to MySQL")
            return "Disconnected to MySQL"
        else:
            return "Disconnection failed"

    def get_new_data(self, table, last_date):
        try:
            query = "SELECT * FROM {0} WHERE date > \"{1}\"".format(
                table, last_date)
        except (TypeError, IndexError):
            self.logger.error(
                "Failed to build query, check table and columns name, and size of data")
            self.logger.exception()

        self.logger.info("Query  :\n" + query)

        # Send it to remote DB
        try:
            self.cursor.execute(query)
            return self.cursor.column_names, self.cursor.fetchall()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_FIELD_ERROR:
                self.logger.error(err.msg)
            elif err.errno == errorcode.ER_PARSE_ERROR:
                self.logger.error("Syntax Error")
            elif err.errno == errorcode.ER_WRONG_VALUE_COUNT_ON_ROW:
                self.logger.error(err.msg)
            else:
                self.logger.error("Something went wrong: {}".format(err))
            raise RuntimeError("Error inserting data")

    # Insert data in database
    def insert_data(self, date, *data):

        query = "INSERT INTO {}({},{})".format(self.table, self.column[0], ','.join(self.column[1:])) + \
                "VALUES(\"{}\",{})".format(
                    date, ",".join(str(d) for d in data))
        self.logger.debug("Query : %s" % query)
        try:
            self.cursor.execute(query)
            self.conn.commit()
            self.logger.debug("Insert data completed")
            return "Insert data completed"
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_FIELD_ERROR:
                self.logger.error(err.msg)
            elif err.errno == errorcode.ER_PARSE_ERROR:
                self.logger.error("Syntax Error : %s" %
                                  ",".join(str(d) for d in self.column))
            elif err.errno == errorcode.ER_WRONG_VALUE_COUNT_ON_ROW:
                self.logger.error(err.msg)
            else:
                self.logger.error("Something went wrong: {}".format(err))
                raise
            return "Insert data failed"

    def _format_data(self, data, col, ids):
        """Build an array of tuple of type (Date,Value,TypeID)
           using the data sent by a sensor
        
        Arguments:
            data {Array} -- [[Date, polluant1, polluant2,...],...]
            col {Array} --  ["Date", "Nom_polluant1", "Nom_polluant2",...]
            ids {Dict} --   {"Nom_polluant1" : ID1, "Nom_polluant2" : ID2}
        """
        format_data = []
        for d in data:
            for index,v in enumerate(d[1:]):
                format_data.append((d[0], v, ids[col[index+1]]))
        return format_data


    def insert_data_bulk(self, table, col, units, data):

        if not data:
            return "No data"

        # Build the SQL query
        try:

            ids = self.get_ids(table, col, units)
            data = self._format_data(data, col, ids)
                    
            query = "INSERT INTO MEASUREMENTS(systemId,date,value,typeId) VALUES (\"{}\", %s, %s, %s)".format(self.sysId)
            self.cursor.executemany(query, data)
            self.conn.commit()
            self.logger.debug(
                "Succesfully inserted {} records into the Database".format(len(data)))
        except (TypeError, IndexError):
            self.logger.error(
                "Failed to build query, check table and columns name, and size of data")
            self.logger.exception()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_FIELD_ERROR:
                self.logger.error(err.msg)
            elif err.errno == errorcode.ER_PARSE_ERROR:
                self.logger.error("Syntax Error : %s" %
                                  ",".join(str(d) for d in self.column))
            elif err.errno == errorcode.ER_WRONG_VALUE_COUNT_ON_ROW:
                self.logger.error(err.msg)
            else:
                self.logger.error("Something went wrong: {}".format(err))
            raise RuntimeError("Error inserting data")
