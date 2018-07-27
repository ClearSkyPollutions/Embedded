#!/use/bin/env python3
# -*- coding: utf-8 -*-

import abc
import datetime
from Database import Database


class Sensor:

    sensor_name = ""
    pollutants = []
    units = []

    def __init__(self, database, logger):
        if not database.cursor:
            raise ValueError('No cursor in object database')
        self.database = database
        self.logger = logger
        self.vals = []

    @abc.abstractmethod
    def setup(self):
        """Method to setup sensor"""

    def getdate(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def insert(self):
        """Insert into the DB the last values read since the last call to this function
        """
        try:
            self.database.insert_data_bulk(self.sensor_name, self.pollutants, self.units, self.vals)
        finally:
            self.vals = []
