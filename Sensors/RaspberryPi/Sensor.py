#!/use/bin/env python3
# -*- coding: utf-8 -*-

import abc
import datetime
from Database import Database


class Sensor:

    def __init__(self, sensor_name, database, user, password, host, port, logger):
        self.database = Database(database, user, password, host, port, logger)
        self.sensor_name = sensor_name
        self.logger = logger
    
    @abc.abstractmethod
    def setup(self):
        """Method to sensor setup"""

    @abc.abstractmethod
    def start(self):
        """Method to read data"""

    @abc.abstractmethod
    def stop(self):
        """Method to stop the program"""
    
    def getdate(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

