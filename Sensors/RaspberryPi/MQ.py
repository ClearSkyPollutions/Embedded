#!/usr/bin/python3
# coding=utf-8

import mysql.connector
import sys
import math
from time import sleep
from Sensor import Sensor
from datetime import datetime
from ADS1256_definitions import *
from pipyadc import ADS1256

# TODO : Replace with config files
DB_ACCESS_PERIOD = 30
TABLE_NAME = "MQ"
COL = ["date", "val"]


class MQ(Sensor):

    read_sample_interval = 50   # define how many samples you are going to take in normal operation
    read_sample_times = 5        # define the time interal(in milisecond) between each samples in normal operation

    frequency = 60 #readings/minute
    avg = False
    ads = None

    def __init__(self, database, logger):
        super().__init__(database, logger)
        self.vals = []

    def setup(self, frequency = 30, averaging = False):
        """Configure ADS1256 ADC converter

        Arguments:
            frequency {double} -- Frequency for reading data, in data/min. 
                                    (default: {30})

        Keyword Arguments:
            averaging {boolean} -- If True, data will be read every second, but returned averaged every 1/frequency 
                                    (default: {False})
        """

        try:
            # ADS Configuration
            ads = ADS1256()
            ads.cal_self()
            self.ads = ads
            # DB config for this sensor
            self.database.create_table(TABLE_NAME,COL)
        except (IOError, mysql.connector.Error):
            self.logger.exception("")
            raise
        
        self.frequency = frequency
        self.avg = averaging

        self.logger.debug("Sensor is setup")

    def read(self):
        
        rs = 0.0

        # Average measurements to get the sensor resistance 
        for i in range(self.read_sample_times):
            d = self._read_data()
            rs += self._process_data(d)
            sleep(self.read_sample_interval/1000.0)

        rs = rs/self.read_sample_times

        # Get the value from the graph in datasheet @TODO Calibration


    # TODO: probably doesn't belong in this class : 
    def insert(self):
        self.database.insert_data_bulk(TABLE_NAME, COL, self.vals)
        self.vals = []

    def _read_data(self):
        """Read the voltage from the analog output of the sensor. 
            
        Returns:
            float -- 0-5V 
        """        
        channel = POS_AIN0|NEG_AINCOM
        
        raw_channel = self.ads.read_and_next_is(channel)
        voltage = raw_channel * self.ads.v_per_digit

        return voltage

    #########################  MQGetPercentage #################################
    # Input:   rs_ro_ratio - Rs divided by Ro
    #          pcurve      - pointer to the curve of the target gas
    # Output:  ppm of the target gas
    # Remarks: By using the slope and a point of the line. The x(logarithmic value of ppm) 
    #          of the line could be derived if y(rs_ro_ratio) is provided. As it is a 
    #          logarithmic coordinate, power of 10 is used to convert the result to non-logarithmic 
    #          value.
    ############################################################################ 
    def MQGetPercentage(self, rs_ro_ratio, pcurve):
        """Concentration in ppm function of the rs/ro ration is a log of a linear function
        This function computes this value using a point of the curve and the slope
        
        Arguments:
            rs_ro_ratio {Double} -- Ration Resistance :
            q:
            pcurve {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """

        res = math.log(rs_ro_ratio) - pcurve[1]
        return (math.pow(10,( ((math.log(rs_ro_ratio)-pcurve[1])/ pcurve[2]) + pcurve[0])))


    def _process_data(self, v):
        """Calculate the sensor resistance rs from the raw data
        
        Arguments:
            v {Double} -- Raw data read from the mq sensor (returned by _read_data)
        
        Returns: @TODO:
            float : Value of the concentration in ... -- [description]
        """

        rs = 0.0

        for i in range(self.read_sample_times):
            rs += self._resistance_calculation(v)
            sleep(self.read_sample_interval/1000.0)

        rs = rs/self.read_sample_times

        return rs

    def stop(self):
        self.logger.debug("Stopping acquisition")

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

