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
COL = ["date", "LPG", "CO", "SMOKE"]

# Number of samples for each readings, and interval between them (in ms)
READ_SAMPLE_NUMBER = 50
READ_SAMPLE_INTERVAL = 5 

R0_CLEAN_AIR_FACTOR = 10

class MQ(Sensor):
    frequency = 60 #readings/minute
    avg = False
    ads = None

    def __init__(self, database, logger, mqType):
        super().__init__(database, logger)
        self.vals = []
        self.type(mqType)

    def type(self, mqType):
        if mqType is 2:
            self.gas =  {'GAS_LPG' : [2.3,0.21,-0.47], 'GAS_CO' : [2.3,0.72,-0.34], 'GAS_SMOKE' : [2.3,0.53,-0.44]}
            self.r0 = 12 #kOhm
            self.rlValue = 5
        else:
            raise RuntimeError("MQ type not supported")

    def setup(self, adsPin = 0,  frequency = 30, averaging = False):

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

        if adsPin < 0 or adsPin > 8:
            raise TypeError("Wrong ADS channel number")
        self.adsPin = adsPin

        self.logger.debug("Sensor is setup")

    def read(self):
        gas_val = []
        rs = 0.0

        # Average measurements to get the sensor resistance 
        for i in range(0, READ_SAMPLE_NUMBER):
            d = self._read_data()
            rs += self.resistanceCalculation(d)
            sleep(READ_SAMPLE_INTERVAL/1000.0)
        rs = rs/float(READ_SAMPLE_NUMBER)

        ratio = rs/self.r0


        for _, curve in self.gas.items():
            gas_val.append(self.getGasPercentage(ratio, curve))
            
        self.vals.append([self.getdate(), *gas_val])
        


        # Get the value from the graph in datasheet @TODO Calibration

    def getGasPercentage(self, rs_ro_ratio, pcurve):
        """Find the Concentration using the graph in the documentation
        
        Arguments:
            rs_ro_ratio {float} -- Ratio between the sensor resistance Rs and the ref resistance Ro
            pcurve {[float, float, float]} -- Define the curve in the graph with a point and the slope
                                                [x, y, slope]
        
        Returns:
            float -- Concentration in ppm
        """

        return (math.pow(10,( ((math.log(rs_ro_ratio)-pcurve[1])/ pcurve[2]) + pcurve[0])))


    # TODO: probably doesn't belong in this class : 
    def insert(self):
        self.database.insert_data_bulk(TABLE_NAME, COL, self.vals)
        # print(TABLE_NAME + " : " + COL + str(self.vals[0][1]))
        
        self.vals = []

    def _read_data(self):
        """Read the digital value from the output of the sensor. 
        This value is not transformed into a voltage
            
        Returns:
            float -- 0-5V 
        """        
        channel = (self.adsPin << 4)|NEG_AINCOM
        raw_channel = self.ads.read_and_next_is(channel)

        return raw_channel


    def resistanceCalculation(self, raw_adc):
        """Calculates the sensor resistance from the voltage divider
        Voltage divider : RS = RL * (Vin - Vout) / Vin
        
        Arguments:
            raw_adc {int} -- Raw digital output of the AD/DA converter
        
        Returns:
            float -- The resistance of the sensor
        """
        
        # ADS1256 is a 24-bit converter, so max value is 2**24 - 1
        return float(self.rlValue*((2**23 - 1)-raw_adc)/float(raw_adc));

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

