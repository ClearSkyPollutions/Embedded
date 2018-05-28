#!/usr/bin/python3
# coding=utf-8

import serial
import mysql.connector
from Sensor import Sensor

from time import sleep
from datetime import datetime

# TODO : Replace with config files
DB_ACCESS_PERIOD = 90
TABLE_NAME = "SDS011"
COL = ["date", "pm25", "pm10"]


class SDS011(Sensor):

    frequency = 60 #readings/minute
    avg = False

    def __init__(self, database, logger):
        super().__init__(database, logger)
        self.ser = None
        self.vals = []

    def setup(self, frequency = 30, averaging = False, dev = "/dev/ttyUSB0"):
        """Configure serial connection
            Check the database connection
            then configure frequency, averaging and database settings

        Keyword Arguments:
            frequency {double} -- Frequency for reading data, in data/min. Must be less than 30
            averaging {boolean} -- If True, data will be read every 2 seconds, but returned averaged every 1/frequency 
                                    (default: {False})
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
                timeout=0.5
            )
        except (ValueError,serial.SerialException):
            self.logger.exception("")
            raise RuntimeError("Error setting up serial connection")
        
        # Setup config sensor
        self.frequency = frequency
        self.avg = averaging

        #Setup Base de Donnee
        self.database.create_table(TABLE_NAME,COL)

        self.logger.debug("Sensor is setup")

    def read(self):
        d = self._read_data()
        pm25, pm10 = self._process_data(d)
        self.logger.info('pm2.5={0:0.1f}µg/m^3  pm10={1:0.1f}µg/m^3'.format(pm25, pm10))
        if pm25 is not None and pm10 is not None:
            self.vals.append([self.getdate(), pm25, pm10])

    # TODO: probably doesn't belong in this class : 
    def insert(self):
        try:
            self.database.insert_data_bulk(TABLE_NAME, COL, self.vals)
        finally:
            self.vals = []

    def _read_data(self):
        """Read data from the sensor. 
            Wait for the start byte, read 10 bytes and return them
        
        Returns:
            int -- concatenation of the 10 bytes
        """

        byte = 0
        while byte != b'\xaa':
            byte = self.ser.read(size=1)

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

    def stop(self):
        self.logger.debug("Stopping SDS011... Done (serial connection stopped)")

        #Serial stop
        self.ser.close()

    def start(self):
        # ---------------------------------------------------------------
        # Data Reading & Data Storage
        # ---------------------------------------------------------------

        sums = [0,0]

        while True:

            values = []
            counter = 0
            last_data = self.getdate()

            # Prevent data stacking up in the buffer during communication with the server
            self.ser.reset_input_buffer()

            # Number of measurements between each server connection
            nb_data = int(DB_ACCESS_PERIOD*self.frequency/60) if not self.avg else DB_ACCESS_PERIOD

            # Reduce communication delays by sending multiple measurements at a time
            for i in range (0, nb_data):
                
                # Get last data
                d = self._read_data()
                t = self.getdate()
                pm25, pm10 = self._process_data(d)
                if not pm25 or not pm10:
                    continue
                
                # Log the received data
                self.logger.debug("PM 2.5: {}μg/m^3  PM 10: {}μg/m^3 CHECKSUM={}"
                        .format(pm25, pm10, "OK"))

                # If no averaging, store it and wait for the next one
                if not self.avg :
                    values.append([t, pm25, pm10])
                    sleep(60.0/self.frequency)
                    self.ser.reset_input_buffer()
                
                # If averaging, get every values then average depending on frequency
                else:
                    sums[0] += pm25
                    sums[1] += pm10

                    counter += 1 
                    difftime = datetime.strptime(t, '%Y-%m-%d %H:%M:%S') - datetime.strptime(last_data, '%Y-%m-%d %H:%M:%S')

                    if difftime.total_seconds() > 60.0/self.frequency:
                        values.append([t, sums[0]/counter, sums[1]/counter])
                        self.logger.debug(values)
                        sums = [0,0]
                        counter = 0
                        last_data = t
                    sleep(0.5)

            # Send the data to the database
            if(len(values) != 0):  
                self.database.insert_data_bulk(TABLE_NAME, COL, values)
            else:
                print("Error: No valid data received for {} trials".format(
                    DB_ACCESS_PERIOD))
                raise Exception

