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
DB_ACCESS_FREQUENCY = 90
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

    def _read_data(self, ads: ADS1256):
        """Read the voltage from the analog output of the sensor. 
            
        Returns:
            float -- 0-5V 
        """        
        channel = POS_AIN0|NEG_AINCOM
        raw_channel = ads.read_and_next_is(channel)
        voltage   = raw_channel * ads.v_per_digit
        
        return voltage

    def _process_data(self, v):
        """Get and return the particulate matter concentration
             from the output voltage sent by the sensor.        
        Arguments:
            v : float  -- [Data returned by the sensor]
        
        Returns:
            float -- pm25 concentration or 0 for a negative result
        """
        if (v < 0):
            v = 0
        else:
            v = (v*0.15 - 0.2) * 1000
        return v


    def setup(self, frequency, averaging):
        """Configure ADS1256 ADC converter

        Arguments:
            frequency {double} -- Frequency for reading data, in data/min. Must be less than 30

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
        
        # Setup config sensor
        if (frequency > 30):
            return False
        else :
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

            # Reduce communication delays by sending multiple measurements at a time
            for i in range (0, int(DB_ACCESS_FREQUENCY/self.frequency)):
                d = self._read_data(self.ads)
                t = self.getdate()
                pm25 = self._process_data(d)
                if not pm25:
                    continue
                
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
                self.database.insert_data_bulk2(values)
            else:
                print("Error: No valid data received for {} trials".format(
                    DB_ACCESS_FREQUENCY))
                sys.exit()

