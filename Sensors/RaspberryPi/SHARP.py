#!/usr/bin/python3
# coding=utf-8

import mysql.connector
import sys
from time import sleep
from Sensor import Sensor
from datetime import datetime
from ADS1256_definitions import *
from pipyadc import ADS1256

# TODO : Replace with config files
DB_ACCESS_PERIOD = 30
TABLE_NAME = "SHARP"
COL = ["date", "pm25"]


class SHARP(Sensor):

    frequency = 60 #readings/minute
    avg = False
    ads = None

    def __init__(self, database, user, password, host, port, logger):
        super(SHARP, self).__init__(TABLE_NAME,
            database, user, password, host, port, logger)
        self.sensor_name = "SHARP"

    def led_on(self):
        self.ads.gpio = self.ads.gpio[0] & 0xFE | 0x01

    def led_off(self):
        self.ads.gpio = self.ads.gpio[0] & 0xFE| 0x00

    def waitmicroseconds(self, deltatime: int):
        sleep(deltatime/1000000.0)    

    def _read_data(self):
        """Read the voltage from the analog output of the sensor. 
            
        Returns:
            float -- 0-5V 
        """        
        channel = POS_AIN0|NEG_AINCOM
        
        self.led_on()
        self.waitmicroseconds(280)
        raw_channel = self.ads.read_and_next_is(channel)
        voltage = raw_channel * self.ads.v_per_digit
        self.waitmicroseconds(40)
        self.led_off()
        self.waitmicroseconds(9680)

        return voltage

    def _process_data(self, v):
        """Get and return the particulate matter concentration
             from the output voltage sent by the sensor.        
        Arguments:
            v : float  -- [Data returned by the sensor]
        
        Returns:
            float -- pm25 concentration or 0 for a negative result
        """

        pm25 = (v*0.15 - 0.05) * 1000
        if (pm25 < 0):
            pm25 = 0
        return pm25


    def setup(self, frequency, averaging = False):
        """Configure ADS1256 ADC converter

        Arguments:
            frequency {double} -- Frequency for reading data, in data/min. 

        Keyword Arguments:
            averaging {boolean} -- If True, data will be read every 2 seconds, but returned averaged every 1/frequency 
                                    (default: {False})
        """
        # ---------------------------------------------------------------
        # ADS Configuration
        # ---------------------------------------------------------------
        try:
            ads = ADS1256()
            ads.cal_self()
            self.ads = ads
        except Exception as e:
            self.logger.error("Error setting up ads1256 ADC converter : " + str(e))
            return False
        
        self.frequency = frequency
        self.avg = averaging

        #Setup Base de Donnee
        connection_status = self.database.connection()
        if connection_status == "Connection failed":
            return connection_status

        table_status = self.database.create_table(TABLE_NAME,COL)
        if table_status == "Error date":
            return table_status

        self.logger.debug("Sensor is setup")
        return True

    def stop(self):
        self.logger.debug("Stopping acquisition")

        #MySQL Stop
        self.database.disconnection()

    def start(self):
        # ---------------------------------------------------------------
        # Data Reading & Data Storage
        # ---------------------------------------------------------------

        sums = 0

        while True:
            values = []
            counter = 0
            last_data = self.getdate()

            # Number of measurements between each server connection
            nb_data = int(DB_ACCESS_PERIOD*self.frequency/60) if not self.avg else DB_ACCESS_PERIOD

            # Reduce communication delays by sending multiple measurements at a time
            for i in range (0, nb_data):

                d = self._read_data()
                t = self.getdate()
                pm25 = self._process_data(d)
                
                # Log the received data
                self.logger.debug("PM 2.5: {}μg/m^3".format(pm25))

                # If no averaging, store it and wait for the next one
                if not self.avg :
                    values.append([t, pm25])
                    sleep(60.0/self.frequency)
                
                # If averaging, get every values then average depending on frequency
                else:
                    sums += pm25
                    counter += 1 
                    difftime = datetime.strptime(t, '%Y-%m-%d %H:%M:%S') - datetime.strptime(last_data, '%Y-%m-%d %H:%M:%S')

                    if difftime.total_seconds() > 60.0/self.frequency:
                        values.append([t, sums/counter])
                        sums = 0
                        counter = 0
                        last_data = t
                    sleep(0.5)

            # Send the data to the database
            if(len(values) != 0):       
                self.database.insert_data_bulk(values)
            else:
                print("Error: No valid data received for {} trials".format(
                    DB_ACCESS_PERIOD))
                sys.exit()

