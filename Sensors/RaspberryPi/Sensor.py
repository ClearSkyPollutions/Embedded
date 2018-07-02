#!/use/bin/env python3
# -*- coding: utf-8 -*-

import abc
import datetime
from Database import Database


class Sensor:

    def __init__(self, database, logger):
        if not database.cursor:
            raise ValueError('No cursor in object database')
        self.database = database
        self.sensor_name = self.__class__.__name__
        self.logger = logger
    
    @abc.abstractmethod
    def setup(self):
        """Method to setup sensor"""

    @abc.abstractmethod
    def start(self):
        """Method to read data"""

    @abc.abstractmethod
    def stop(self):
        """Method to stop the program"""
    
    def getdate(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
