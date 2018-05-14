#!/usr/bin/python3
# coding=utf-8
# "DATASHEET": http://cl.ly/ekot
# https://gist.github.com/kadamski/92653913a53baf9dd1a8
from __future__ import print_function
import serial, datetime, mysql.connector, sys
from time import sleep

DB_ACCESS_FREQUENCY = 30

#---------------------------------------------------------------
# Read data bytes sent by SDS011 sensor
#---------------------------------------------------------------
def read_sds011():
    byte = 0
    while byte != b'\xaa':
        byte = ser.read(size=1)

    d = ser.read(size=9)
    return byte + d

#---------------------------------------------------------------
# Return PM values, datetime and checksum
#---------------------------------------------------------------

def process_data(d):
    pm25lowbyte = d[2]
    pm25highbyte = d[3]
    pm10lowbyte = d[4]
    pm10highbyte = d[5]
    received_checksum = d[8]
    lastbyte = d[9]
    pm25 = (pm25highbyte*256 + pm25lowbyte) / 10
    pm10 = (pm10highbyte*256 + pm10lowbyte) / 10
    checksum = sum(v for v in d[2:8])%256
    return [pm25, pm10, checksum, received_checksum, lastbyte]

#---------------------------------------------------------------
# Save data in mysql DATABASES.
#---------------------------------------------------------------
def save_data(data):
    i = 0
    query = "INSERT INTO Concentration_pm(date_mesure,pm2_5,pm10) VALUES "
    for i in range(0, DB_ACCESS_FREQUENCY - 1):
        query += "(\"{}\",{},{}), ".format(data[i][0], data[i][1], data[i][2])
    i += 1
    query += "(\"{}\",{},{});".format(data[i][0], data[i][1], data[i][2])
    cursor.execute(query)
    conn.commit()

#---------------------------------------------------------------
# Serial Connection
#---------------------------------------------------------------
try :
    ser = serial.Serial(
    port = '/dev/ttyUSB0',
    baudrate = 9600,
    parity   = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout  = 0.5
    )
except KeyboardInterrupt:
    print("\nUser exit")
    sys.exit()
except : 
    print("No sensor plug in USB : /dev/ttyUSB0")
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
        while True:      
            ser.reset_input_buffer()
            values = []
            i = 0
            while( i < DB_ACCESS_FREQUENCY):       
                i += 1
                d = read_sds011()
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                pm25, pm10, checksum, received_checksum, lastbyte = process_data(d)
                if (checksum == received_checksum and lastbyte == 0xab):
                    values.append([date, pm25, pm10])
                    print("PM 2.5: {}μg/m^3  PM 10: {}μg/m^3 CHECKSUM={}".format(pm25, pm10, "OK"))
                else:
                    print("Warning: Corrupted data has been received!")
            if(len(values) != 0):       
                save_data(values)                
            else:       
                print("Error: No valid data received for {} trials".format(DB_ACCESS_FREQUENCY))
                sys.exit()
except KeyboardInterrupt:
    print("\nUser exit")
    sys.exit()

            
