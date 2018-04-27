#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import sys
import time

import mysql.connector

import serial

#GPIO wired to RESET line of PMS5003, must be already exported and set to output.
PMS5003_RESET_GPIO = '/sys/class/gpio/gpio17'

# Make several reads, then calculate the average.
AVERAGE_READS = 30

# Seconds to sleep before repeating averaged read. Use -1 to exit.
AVERAGE_READS_SLEEP = -1

# Attempt a sensor reset after some errors.
RESET_ON_FRAME_ERRORS = 2
# Abort the averaged read after too many errors.
MAX_FRAME_ERRORS = 10

# Sensor settling after wakeup requires at least 30 seconds (sensor sepcifications).
WAIT_AFTER_WAKEUP = 40
# Total Response Time is 10 seconds (sensor specifications).
MAX_TOTAL_RESPONSE_TIME = 12

# Normal data frame length.
DATA_FRAME_LENGTH = 28
# Command response frame length.
CMD_FRAME_LENGTH = 4

# Serial read timeout value in seconds.
SERIAL_TIMEOUT = 2.0

# Calculate average on this output data.
AVERAGE_FIELDS = ['data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10', 'data11', 'data12']

# Log to stdout or to file/syslog.
LOG_TO_STDOUT = sys.stdin.isatty()
# False for syslog logging, filename for file logging.
LOG_TO_FILE = False
LOG_FMT_SYSLOG = '%(module)s: %(levelname)s %(message)s'
LOG_FMT_FILE   = '%(asctime)s %(levelname)s %(message)s'
LOG_FMT_DATE   = '%Y-%m-%d %H:%M:%S'

#---------------------------------------------------------------
# PMS5003 Commands for Passive Mode.
#---------------------------------------------------------------
CMD_SLEEP  = b'\x42' + b'\x4d' + b'\xe4' + b'\x00' + b'\x00'
CMD_WAKEUP = b'\x42' + b'\x4d' + b'\xe4' + b'\x00' + b'\x01'

#---------------------------------------------------------------
# Convert a two bytes string into a 16 bit integer.
#---------------------------------------------------------------
def int16bit(b):
    return (ord(b[0]) << 8) + ord(b[1])

#---------------------------------------------------------------
# Return the hex dump of a buffer of bytes.
#---------------------------------------------------------------
def buff2hex(b):
    return " ".join("0x{:02x}".format(ord(c)) for c in b)

#---------------------------------------------------------------
# Make a list of averaged reads: (datetime, float, float, ...)
#---------------------------------------------------------------
def make_average(reads_list):
    average = []
    average.append(datetime.datetime.utcnow())
    for k in AVERAGE_FIELDS:
        average.append(float(sum(r[k] for r in reads_list)) / len(reads_list))
    return average

#---------------------------------------------------------------
# Convert the list created by make_average() to a string.
#---------------------------------------------------------------
def average2str(a):
    s = a[0].strftime('%Y-%m-%dT%H:%M:%SZ')
    for f in a[1:]:
        s += ' %0.2f' % (f)
    return s

#---------------------------------------------------------------
# Send a RESET signal to sensor.
#---------------------------------------------------------------
def sensor_reset():
    print("Sending RESET signal to sensor")
    try:
        gpio_direction = None
        if not os.path.isdir(PMS5003_RESET_GPIO):
            print(u'GPIO for sensor RESET is not exported: %s' % (PMS5003_RESET_GPIO,))
            return
        else:
            with open(os.path.join(PMS5003_RESET_GPIO, 'direction'), 'r') as f:
                gpio_direction = f.read().strip()
        if gpio_direction != 'out':
            print(u'GPIO for sensor RESET is not set to output')
            return
        else:
            print(u'Setting GPIO line to LOW for a short time')
            with open(os.path.join(PMS5003_RESET_GPIO, 'value'), 'w') as f:
                f.write("0\n")
            time.sleep(0.5)
            with open(os.path.join(PMS5003_RESET_GPIO, 'value'), 'w') as f:
                f.write("1\n")
            time.sleep(1.0)
    except Exception:
        print(u'PMS5003 sensor RESET via GPIO line: Exception ' )
    except KeyboardInterrupt:
        sys.exit(1)
    return

#---------------------------------------------------------------
# Enter sensor sleep state.
#---------------------------------------------------------------
def sensor_sleep(_port):
    print("Sending sleep command")
    send_buffer(CMD_SLEEP, _port)
    _port.flushInput()

#---------------------------------------------------------------
# Exit from sleep state and wait sensor to settle.
#---------------------------------------------------------------
def sensor_wakeup(_port):
    print("Sending wakeup command")
    response = send_buffer(CMD_WAKEUP, _port)
    if not response:
        print('No response to wakeup command')
        sensor_reset()
        print('Sending wakeup command again')
        response = send_buffer(CMD_WAKEUP, _port)
        if not response:
            print('No response to repeated wakeup command')
    print("Waiting %d seconds for sensor to settle" % (WAIT_AFTER_WAKEUP,))
    time.sleep(WAIT_AFTER_WAKEUP)
    _port.flushInput()

#---------------------------------------------------------------
# Send a command buffer to the serial port, with checksum.
# Return the response frame, if any.
#---------------------------------------------------------------
def send_buffer(b, _port):
    checksum = 0
    for i in range(0, len(b)):
        checksum += ord(b[i])
    b += chr(checksum / 256) + chr(checksum % 256)
    print("Using passive mode to send buffer: %s" % (buff2hex(b),))
    _port.flushInput()
    written = _port.write(b)
    if written != len(b):
        print("Short write, sent %d bytes instead of %d" % (written, len(b)))
        response = None
    else:
        # Get a response frame (if any). Examples:
        # Wakeup CMD: 0x42 0x4d 0xe4 0x00 0x01
        #   Response: 0x42 0x4d 0x00 0x1c ...(full data frame)
        # Sleep CMD:  0x42 0x4d 0xe4 0x00 0x00
        #   Response: 0x42 0x4d 0x00 0x04 0xe4 0x00
        response = read_pms5003(_port)
    return response

#---------------------------------------------------------------
# Read a data frame from serial port, the first 4 bytes are:
# 0x42, 0x4d, frame lenght (16 bit integer).
# and last two bytes are : checksum
# Return None on errors.
#---------------------------------------------------------------
def read_pms5003(port):

    data = b''
    start_time = datetime.datetime.utcnow()

    while True:

        start_charac_1 = port.read()
        if start_charac_1 != '':
            print('Got char 0x%x from serial read()' % (ord(start_charac_1),))
        else:
            print('Timeout on serial read()')
        
        
        if start_charac_1 == b'\x42':
            start_charac_2 = port.read()
            if start_charac_2 == b'\x4d':
                frame_len_high = port.read()
                frame_len_low  = port.read()
                frame_len = ord(frame_len_high) * 256 + ord(frame_len_low)
                
                if frame_len == DATA_FRAME_LENGTH:

                    #Normal Data
                    data += start_charac_1 + start_charac_2 + frame_len_high + frame_len_low
                    data += port.read(frame_len-2)
                    check_high = port.read()
                    check_low  = port.read()
                    check = ord(check_high) * 256 + ord(check_low)
                    data += check_high + check_low

                    #Verify lenght of data
                    if (len(data) - 4) != frame_len:
                        print("Short read, expected %d bytes, got %d" % (frame_len, len(data) - 4))
                        return None
                    
                    # Verify checksum (last two bytes).
                    checksum = 0
                    for i in range(0, len(data) - 2):
                        checksum += ord(data[i])
                    if checksum != check:
                        print("Checksum mismatch: %d, check %d" % (checksum, check))
                        return None
                    print("Received data frame = %s" % (buff2hex(data),))
                    return data

                elif frame_len == CMD_FRAME_LENGTH:

                    # Command response frame.
                    data += start_charac_1 + start_charac_2 + frame_len_high + frame_len_low
                    data += port.read(frame_len)
                    print("Received command response frame = %s" % (buff2hex(data),))
                    return data

                else:

                    # Unexpected frame.
                    print("Unexpected data length = %d" % (frame_len))
                    time.sleep(MAX_TOTAL_RESPONSE_TIME)
                    port.flushInput()
                    return None


        if (datetime.datetime.utcnow() - start_time).seconds >= MAX_TOTAL_RESPONSE_TIME:
            print("Timeout waiting data-frame signature")
            return None

#---------------------------------------------------------------
# Return the data frame in a verbose format.
#---------------------------------------------------------------
def data_frame_verbose(f):
    return (' Date: {};\n'
            ' PM1.0 (CF=1) μg/m³: {};\n'
            ' PM2.5 (CF=1) μg/m³: {};\n'
            ' PM10  (CF=1) μg/m³: {};\n'
            ' PM1.0 (STD)  μg/m³: {};\n'
            ' PM2.5 (STD)  μg/m³: {};\n'
            ' PM10  (STD)  μg/m³: {};\n'
            ' Particles >  0.3 μm count: {};\n'
            ' Particles >  0.5 μm count: {};\n'
            ' Particles >  1.0 μm count: {};\n'
            ' Particles >  2.5 μm count: {};\n'
            ' Particles >  5.0 μm count: {};\n'
            ' Particles > 10.0 μm count: {};\n'
            ' Reserved: {};\n'
            ' Checksum: {};'.format(
                f['timestamp'],  f['data1'],  f['data2'],
                f['data3'],  f['data4'],  f['data5'],
                f['data6'],  f['data7'],  f['data8'],
                f['data9'],  f['data10'], f['data11'],
                f['data12'], f['reserved'], f['checksum']))

#---------------------------------------------------------------
# Save averaged data in mysql DATABASES.
#---------------------------------------------------------------
def save_data(data):
    cursor.execute(query,data)
    conn.commit()

#---------------------------------------------------------------
#Mysql Connector
#---------------------------------------------------------------
conn = mysql.connector.connect(host="192.168.2.108",user="Sensor",password="Sensor",database="capteur_multi_pollutions",port="4306")
cursor = conn.cursor()
query = "INSERT INTO Concentration_pm(date_mesure,pm2_5,pm10)"\
        "VALUES(\"%s\",%.2f,%.2f)"

#---------------------------------------------------------------
# Main program.
#---------------------------------------------------------------
if LOG_TO_STDOUT:
    # Log to stdout.
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FMT_FILE, LOG_FMT_DATE))
elif LOG_TO_FILE:
    # Log to file.
    handler = logging.FileHandler(filename=LOG_TO_FILE)
    handler.setFormatter(logging.Formatter(LOG_FMT_FILE, LOG_FMT_DATE))
else:
    # Log to syslog.
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    handler.setFormatter(logging.Formatter(LOG_FMT_SYSLOG, LOG_FMT_DATE))
log = logging.getLogger()
log.setLevel('DEBUG')
log.addHandler(handler)

PMS5003 = serial.Serial(
 port='/dev/ttyAMA0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)

try:
    sensor_wakeup(PMS5003)
except KeyboardInterrupt:
    sys.exit(1)

reads_list = []
error_count = 0
error_total = 0
while True:
    try:

        rcv = read_pms5003(PMS5003)

        # Manage data-frame errors.
        if rcv == None:
            error_count += 1
            error_total += 1
            if error_count >= RESET_ON_FRAME_ERRORS:
                logging.warning("Repeated read errors, attempting sensor reset")
                sensor_reset()
                error_count = 0
                continue
            if error_total >= MAX_FRAME_ERRORS:
                if (AVERAGE_READS_SLEEP >= 0):
                    logging.error("Too many read errors, sleeping a while")
                    time.sleep(AVERAGE_READS_SLEEP)
                    error_total = 0
                    continue
                else:
                    logging.error("Too many read errors, exiting")
                    break

        # Skip non-output data-frames.
        if (rcv == None) or ((len(rcv) - 4) != DATA_FRAME_LENGTH):
            continue

        # Got a valid data-frame.
        res = {'timestamp': datetime.datetime.now(),
               'data1':     int16bit(rcv[4:]),
               'data2':     int16bit(rcv[6:]),
               'data3':     int16bit(rcv[8:]),
               'data4':     int16bit(rcv[10:]),
               'data5':     int16bit(rcv[12:]),
               'data6':     int16bit(rcv[14:]),
               'data7':     int16bit(rcv[16:]),
               'data8':     int16bit(rcv[18:]),
               'data9':     int16bit(rcv[20:]),
               'data10':    int16bit(rcv[22:]),
               'data11':    int16bit(rcv[24:]),
               'data12':    int16bit(rcv[26:]),
               'reserved':  buff2hex(rcv[28:30]),
               'checksum':  int16bit(rcv[30:])
               }
        logging.debug("Got valid data frame:\n" + data_frame_verbose(res))

        reads_list.append(res)
        if len(reads_list) >= AVERAGE_READS:
            # Calculate the average of each measured data.
            logging.info("Got %d valid readings, calculating average" % (len(reads_list)))
            average = make_average(reads_list)
            average_str = average2str(average)
            logging.info("Average data: %s" % (average_str,))
            save_data(average_str)
            del reads_list[:]
            if AVERAGE_READS_SLEEP < 0:
                break
            if AVERAGE_READS_SLEEP > (WAIT_AFTER_WAKEUP * 3):
                # If sleep time is long enough, enter sensor sleep state.
                sensor_sleep(PMS5003)
                logging.info("Waiting %d seconds before new read" % (AVERAGE_READS_SLEEP,))
                time.sleep(AVERAGE_READS_SLEEP)
                sensor_wakeup(PMS5003)
            else:
                # Keep sensor awake and wait for next reads.
                logging.info("Waiting %d seconds before new read" % (AVERAGE_READS_SLEEP,))
                time.sleep(AVERAGE_READS_SLEEP)
                PMS5003.flushOutput()
                PMS5003.flushInput()

    except KeyboardInterrupt:
        break

try:
    logging.info("Exiting main loop")
    sensor_sleep(PMS5003)
    PMS5003.close()
    cursor.close()
    conn.close()
    sys.exit(0)
except KeyboardInterrupt:
    pass
