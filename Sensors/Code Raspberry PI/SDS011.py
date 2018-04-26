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

def construct_command(cmd, data=[]):
    assert len(data) <= 12
    data += [0,]*(12-len(data))
    checksum = (sum(data)+cmd-2)%256
    ret = "\xaa\xb4" + chr(cmd)
    ret += ''.join(chr(x) for x in data)
    ret += "\xff\xff" + chr(checksum) + "\xab"
    ret = ret.encode('utf-8')
    
    return ret

def process_data(d):
    pm25lowbyte = d[2]
    pm25highbyte = d[3]
    pm10lowbyte = d[4]
    pm10highbyte = d[5]
    pm25 = (pm25highbyte*256 + pm25lowbyte) / 10
    pm10 = (pm10highbyte*256 + pm10lowbyte) / 10
    checksum = sum(v for v in d[2:8])%256
    return [pm25, pm10, checksum, d[8], d[9]]

#def process_version(d):
#    checksum = sum(v for v in d[2:8])%256
#    print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]), "OK" if (checksum==d[8] and d[9]==0xab) else "NOK"))

def read_response():
    byte = 0
    while byte != b'\xaa':
        byte = ser.read(size=1)

    d = ser.read(size=9)

    return byte + d

def cmd_set_mode(mode=MODE_QUERY):
    ser.write(construct_command(CMD_MODE, [0x1, mode]))
    read_response()

def cmd_query_data():
    ser.write(construct_command(CMD_QUERY_DATA))
    d = read_response()
    values = []
    if d[1] == 192:
        values = process_data(d)
    return values

#def cmd_set_sleep(sleep=1):
#    mode = 0 if sleep else 1
#    ser.write(construct_command(CMD_SLEEP, [0x1, mode]))
#    read_response()

#def cmd_set_working_period(period):
#    ser.write(construct_command(CMD_WORKING_PERIOD, [0x1, period]))
#    read_response()

#def cmd_firmware_ver():
#    ser.write(construct_command(CMD_FIRMWARE))
#    d = read_response()
#    process_version(d)

#def cmd_set_id(id):
#    id_h = (id>>8) % 256
#    id_l = id % 256
#    ser.write(construct_command(CMD_DEVICE_ID, [0]*10+[id_l, id_h]))
#    read_response()

if __name__ == "__main__":
    while True:
#       cmd_set_sleep(0)
        cmd_set_mode(1)
        for t in range(15):
            values = cmd_query_data()
            if values is not None:
                print("PM 2.5: {}μg/m^3  PM 10: {}μg/m^3 CRC={}".format(values[0], values[1], "OK" if (values[2] == values[3] and values[4] == 0xab) else "NOK"))
                time.sleep(2)
        print("Going to sleep for 5min...")
        cmd_set_mode(0)
#       cmd_set_sleep()
        time.sleep(300)