#!/usr/bin/python3
# coding=utf-8

import serial
import mysql.connector
from Sensor import Sensor

from time import sleep
from datetime import datetime

class SDS011(Sensor):

    def __init__(self, database, logger):
        super().__init__(database, logger)
        self.ser = None
        self.sensor_name = "SDS011"
        self.pollutants = ["pm25", "pm10"]
        self.units = ["µg/m^3","µg/m^3"]

    def setup(self, frequency=30, dev="/dev/ttyUSB0"):
        """Configure serial connection
            Check the database connection
            then configure frequency and database settings

        Keyword Arguments:
            frequency {double} -- Frequency for reading data, in data/min. Must be less than 30
            dev {string} -- Raspberry Pi port where the device is attached
                                    (default: "/dev/ttyUSB0")

        Raises:
            RuntimeError, TypeError -- Sensor is disconnected
                                        Wrong table or columns names
        """

        # Serial Connection
        try:
            self.ser = serial.Serial(
                port=dev,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.5,
                # To prevent the program from blocking if the device is unplugged during a write operation :
                write_timeout=1
            )
            self._read_data()
        except (ValueError, serial.SerialException, RuntimeError):
            self.logger.exception("")
            raise RuntimeError("Error setting up serial connection")

        self.frequency = frequency

        self.logger.debug("Sensor is setup")

    def read(self):
        """Get the next value from the sensor by reading and processing raw output
        """

        d = self._read_data()
        pm25, pm10 = self._process_data(d)
        self.logger.info(
            'pm2.5={0:0.1f}µg/m^3  pm10={1:0.1f}µg/m^3'.format(pm25, pm10))
        if pm25 is not None and pm10 is not None:
            self.vals.append([self.getdate(), pm25, pm10])

    def _read_data(self):
        """Read data from the sensor. 
            Wait for the start byte, read 10 bytes and return them
        
        Raises:
            RuntimeError -- No start byte found

        Returns:
            int -- concatenation of the 10 bytes
        """

        nb_try = 3 # nb of loop done waiting for start byte
        i = 0
        byte = 0
        while byte != b'\xaa' and i <= nb_try*10:
            byte = self.ser.read(size=1)
            i += 1

        if i == nb_try*10:
            raise RuntimeError("No start byte found")

        d = self.ser.read(size=9)
        return byte + d

    def _process_data(self, d):
        """Get and return the particulate matter concentration
             from the 10-bytes sent by the sensor.
           Check if the checksums are valid  
        
        Arguments:
            d {Bytes} -- [Data returned by the sensor]
        
        Returns:
            double, double -- pm25 and pm10 concentration, or None,None if the checksum is not valid
        """

        if len(d) != 10:
            return None, None
        pm25lowbyte = d[2]
        pm25highbyte = d[3]
        pm10lowbyte = d[4]
        pm10highbyte = d[5]
        received_checksum = d[8]
        lastbyte = d[9]
        pm25 = (pm25highbyte*256 + pm25lowbyte) / 10
        pm10 = (pm10highbyte*256 + pm10lowbyte) / 10
        checksum = sum(v for v in d[2:8]) % 256
        if (checksum == received_checksum and lastbyte == 0xab):
            return [pm25, pm10]
        self.logger.Warning("Wrong checksum, skipping this measurement")
        return None, None

    def close(self):
        self.ser.close()
