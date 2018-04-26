#!/usr/bin/python3
# coding=utf-8
# "DATASHEET": http://cl.ly/ekot
# https://gist.github.com/kadamski/92653913a53baf9dd1a8
from __future__ import print_function
import serial, struct, sys, time, json

DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1

ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

ser.open()
ser.flushInput()

byte, data = 0, ""

def process_data(d):
    pm25lowbyte = d[2]
    pm25highbyte = d[3]
    pm10lowbyte = d[4]
    pm10highbyte = d[5]
    pm25 = (pm25highbyte*256 + pm25lowbyte) / 10
    pm10 = (pm10highbyte*256 + pm10lowbyte) / 10
    checksum = sum(v for v in d[2:8])%256
    return [pm25, pm10, checksum, d[8], d[9]]

def read_response():
    byte = 0
    while byte != b'\xaa':
        byte = ser.read(size=1)

    d = ser.read(size=9)

    return byte + d

if __name__ == "__main__":
    while True:
        values = []
        for t in range(15):
            d = read_response()
            values = process_data(d)
            if values is not None:
                print("PM 2.5: {}μg/m^3  PM 10: {}μg/m^3 CHECKSUM={}".format(values[0], values[1],
                 "OK" if (values[2] == values[3] and values[4] == 0xab) else "NOK"))
