#!/usr/bin/python3
# coding=utf-8
# "DATASHEET": http://cl.ly/ekot
# https://gist.github.com/kadamski/92653913a53baf9dd1a8
from __future__ import print_function
import serial, datetime, mysql.connector
from time import sleep

DB_ACCESS_FREQUENCY = 30

DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.5
)

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
    pm25 = (pm25highbyte*256 + pm25lowbyte) / 10
    pm10 = (pm10highbyte*256 + pm10lowbyte) / 10
    checksum = sum(v for v in d[2:8])%256
    return [pm25, pm10, checksum, d[8], d[9]]

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
    print(query)
    cursor.execute(query)
    conn.commit()

#---------------------------------------------------------------
#Mysql Connector
#---------------------------------------------------------------
conn = mysql.connector.connect(host="192.168.2.108", port = "8001", user="Sensor",password="Sensor",database="capteur_multi_pollutions")
cursor = conn.cursor()


if __name__ == "__main__":
    while True:
        # Flush the data received during DB and network operations
        ser.reset_input_buffer()

        values = []
        while(len(values) < DB_ACCESS_FREQUENCY):
            d = read_sds011()
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #Need to do checksum
            pm25, pm10, *_ = process_data(d)
            values.append([date, pm25, pm10])
        # Send 30 data points at the same time
        save_data(values)
            
