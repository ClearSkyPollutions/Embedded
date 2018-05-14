#!/usr/bin/python3
# coding=utf-8
# "DATASHEET": http://cl.ly/ekot
# https://gist.github.com/kadamski/92653913a53baf9dd1a8
from __future__ import print_function
import datetime, mysql.connector, sys, time
from ADS1256_definitions import *
from pipyadc import ADS1256

DB_ACCESS_FREQUENCY = 5
#---------------------------------------------------------------
# Sampling Methods
#---------------------------------------------------------------

def led_on(ads: ADS1256):
    ads.gpio = ads.gpio[0] & 0xFE | 0x01

def led_off(ads: ADS1256):
    ads.gpio = ads.gpio[0] & 0xFE| 0x00

def waitmicroseconds(deltatime: int):
    time.sleep(deltatime/1000000.0)    

def read_analog(ads: ADS1256):
    
    channel = POS_AIN0|NEG_AINCOM
    raw_channel = ads.read_and_next_is(channel)
    voltage   = raw_channel * ads.v_per_digit
    
    return voltage

#---------------------------------------------------------------
# Save data in mysql DATABASES.
#---------------------------------------------------------------
def save_data(data):
    try:
        n = 0
        query = "INSERT INTO Concentration_pm(date_mesure,pm2_5,pm10) VALUES "
        for i in range(0, DB_ACCESS_FREQUENCY - 2):
            query += "(\"{}\",{},{}), ".format(data[i][0], data[i][1], 0)
            n += 1
        query += "(\"{}\",{},{});".format(data[i][0], data[i][1], 0)
        cursor.execute(query)
        conn.commit()
    except KeyboardInterrupt:
        print("\nUser exit")
        sys.exit()
    except:
        print("Invalid insert request")
        sys.exit()        
#---------------------------------------------------------------
#Mysql Connection
#---------------------------------------------------------------
try:
    conn = mysql.connector.connect(host="192.168.2.69", port = "6000", user="Sensor",password="Sensor",database="capteur_multi_pollutions")
    cursor = conn.cursor()
except KeyboardInterrupt:
    print("\nUser exit")
    sys.exit()
except:
    print("Database connexion failure")
    sys.exit()

#---------------------------------------------------------------
#Data Reading & Data Storage
#---------------------------------------------------------------

try:
    ads = ADS1256()
    ads.cal_self()
    while True:
        values = []
        for i in range(DB_ACCESS_FREQUENCY):
            led_on(ads)
            waitmicroseconds(280)
            voMeasured =  read_analog(ads)
            waitmicroseconds(40)
            led_off(ads)
            waitmicroseconds(9680)
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pm25 = (voMeasured*0.15 - 0.2) * 1000
            values.append([date,pm25])
            print("%f µg/m^3" % pm25)
            time.sleep(1)
        save_data(values)   
except KeyboardInterrupt:
    led_off(ads)
    print("\nUser exit")
    sys.exit()


