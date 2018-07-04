#!/use/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import datetime

import mysql.connector
from mysql.connector import errorcode

# @TODO: Creation and validity check of the Database, systemId errors


class Database:
    """Class interface between sensors and a Database.
    Manage connection, disconnection, validity check and insertion of data into the database
        
        Arguments:
            database {string} -- Name of the database
            user {string} -- Name of a DB user with read/write/create rights
            password {string} -- Password associated with the user
            host {string} -- IP address of the DB location
            port {int} -- Port of the DB for direct access (usually 3306)
            logger {logging.logger} -- Where to log warnings, errors...
        """

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
        """Add a pollutant to the Database
        
        Arguments:
            sensor_name {string} -- Name of the sensor doing the measurements
            pollutant {string} -- Name of the type of pollutant measured
            unit {string} -- Unit of the data
        
        Raises:
            RuntimeError -- Error while communicating with Database
        """

        query = "INSERT INTO POLLUTANT(name, unit, sensor) VALUES(%s, %s, %s)"
        try:
            self.cursor.execute(query, (pollutant, unit, sensor_name))
            self.conn.commit()
            self.logger.debug(
                "Inserted new type of POLLUTANT : " + pollutant)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                self.logger.debug(err.msg)
            else:
                self.logger.exception()
                raise RuntimeError("Error creating table")

    def get_ids(self, sensor_name, pollutants, units):
        """Get the id in the database of the pollutants with name [pollutants] in the table POLLUTANT   
        If the combination (pollutants, sensor_name) is not present in the table, creates a new record
        
        Arguments:
            sensor_name {string} -- Name of the sensor doing the measurements
            pollutants {string[]} -- Name of the pollutants searched
            units {string[]} -- Units of the pollutants searched 
        
        Raises:
            RuntimeError -- Error while communicating with Database
            TypeError -- Units and pollutants should be arrays of same size
        
        Returns:
            Dictionary -- {"pollutant1":"id1", "pollutant2":"id2"}
        """

        if len(pollutants) != len(units):
            raise TypeError("Non associated units/pollutants")
        if isinstance(pollutants, str):
            pollutants = [pollutants]
        if isinstance(units, str):
            units = [units]
            
        ids = {}
        query = "SELECT id FROM POLLUTANT WHERE sensor = \"{}\" and name = %s".format(
            sensor_name)

        for i, j in zip(pollutants, units):
            try:
                # cursor.execute parameters are tuples, i -> (i,)
                self.cursor.execute(query, (i,))
                ids[i] = self.cursor.fetchone()["id"]
                self.logger.debug("Found pollutant " + i +
                                  " id : " + str(ids[i]))
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.debug(err.msg)
                else:
                    self.logger.exception()
                    raise RuntimeError("Error creating table")
            except TypeError:
                self.add_type(sensor_name, i, j)
                self.cursor.execute(query, (i,))
                ids[i] = self.cursor.fetchone()["id"]
        return ids

    def connection(self):
        """Try to connect to mysql and fetch the system identifier
        Raise an error if connection fails
        
        Raises:
            RuntimeError -- Connection failed - Check log for detailed informations
        """

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

    def disconnection(self):
        """Disconnect from mysql database
        """

        self.cursor.close()
        self.conn.close()
        if self.conn.is_connected() != 1:
            self.logger.info("Disconnected to MySQL")
        else:
            self.logger.error("Disconnection failed")

    def _format_data(self, data, pollutants, ids):
        """Build an array of tuple of type (Date,Value,TypeID)
           using the data sent by a sensor
        
        Arguments:
            data {float[][]} -- [["Date", "polluant1", "polluant2",...],...]
            pollutants {string[]} --  ["Nom_polluant1", "Nom_polluant2",...]
            ids {Dict} --   {"Nom_polluant1" : ID1, "Nom_polluant2" : ID2}
        """
        format_data = []
        for d in data:
            for index, v in enumerate(d[1:]):
                format_data.append((d[0], v, ids[pollutants[index]]))
        return format_data

    # @TODO: rename to insert_data ?
    def insert_data_bulk(self, sensor, pollutants, units, data):
        """Insert in the table MEASUREMENTS the data sent by a sensor
        
        Arguments:
            sensor {string} -- Name of the sensor
            pollutants {string[]} -- Array of pollutant names
            units {string[]} -- Array of units of pollutants
            data {float[][]} -- [["Date", "polluant1", "polluant2",...],...]
        
        Raises:
            RuntimeError -- Problem with DB connection 
        """

        if not data:
            return "No data"

        # Build the SQL query
        try:

            ids = self.get_ids(sensor, pollutants, units)
        
            data = self._format_data(data, pollutants, ids)

            query = ("INSERT INTO AVG_YEAR(systemId,date,value,typeId) "
                     "VALUES (\"{}\", %s, %s, %s)".format(self.sysId))
            self.cursor.executemany(query, data)
            self.conn.commit()
            self.logger.debug(
                "Succesfully inserted {} records into the Database".format(len(data)))
        except (TypeError, IndexError):
            self.logger.error(
                "Failed to build query, check sensor and columns name, and size of data")
            self.logger.exception()
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


    # def get_new_data(self, table, last_date):
    #     """Fetch the data in the Database older than [last_date] and return them

    #     Arguments:
    #         table {[type]} -- [description]
    #         last_date {[type]} -- [description]

    #     Raises:
    #         RuntimeError -- [description]

    #     Returns:
    #         [type] -- [description]
    #     """

    #     try:
    #         query = "SELECT * FROM {0} WHERE date > \"{1}\"".format(
    #             table, last_date)
    #     except (TypeError, IndexError):
    #         self.logger.error(
    #             "Failed to build query, check table and columns name, and size of data")
    #         self.logger.exception()

    #     self.logger.info("Query  :\n" + query)

    #     # Send it to remote DB
    #     try:
    #         self.cursor.execute(query)
    #         return self.cursor.column_names, self.cursor.fetchall()
    #     except mysql.connector.Error as err:
    #         if err.errno == errorcode.ER_BAD_FIELD_ERROR:
    #             self.logger.error(err.msg)
    #         elif err.errno == errorcode.ER_PARSE_ERROR:
    #             self.logger.error("Syntax Error")
    #         elif err.errno == errorcode.ER_WRONG_VALUE_COUNT_ON_ROW:
    #             self.logger.error(err.msg)
    #         else:
    #             self.logger.error("Something went wrong: {}".format(err))
    #         raise RuntimeError("Error inserting data")