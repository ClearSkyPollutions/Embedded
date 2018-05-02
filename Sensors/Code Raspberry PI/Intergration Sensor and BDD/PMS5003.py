#!/use/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import time
import sys
import os

import serial

from SensorsDatabase import SensorsDatabase

#GPIO wired to RESET line of PMS5003, must be already exported and set to output.
PMS5003_RESET_GPIO = '/sys/class/gpio/gpio17'
# Seconds to sleep before repeating averaged read. Use -1 to exit.
AVERAGE_READS_SLEEP = -1
# Attempt a sensor reset after some errors.
RESET_ON_FRAME_ERRORS = 2
# Abort the averaged read after too many errors.
MAX_FRAME_ERRORS = 10
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
# PMS5003 Commands for Passive Mode
CMD_SLEEP  = b'\x42' + b'\x4d' + b'\xe4' + b'\x00' + b'\x00' + b'\x01' + b'\x73' # Cmd Sleep and directly checksum
CMD_WAKEUP = b'\x42' + b'\x4d' + b'\xe4' + b'\x00' + b'\x01' + b'\x01' + b'\x74' # Cmd wakeup and directly checksum

PMS5003_port = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate = 9600,
    parity   = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout  = SERIAL_TIMEOUT
)

class PMS5003(SensorsDatabase):

    def __init__(self, database, user, password, host, port, logger, average_reads, wait_after_wakeup):
        
        super(PMS5003,self).__init__(database, user, password, host, port, logger)
        # Make several reads, then calculate the average.
        self.Average_Reads = average_reads
        # Sensor settling after wakeup requires at least 30 seconds (sensor sepcifications).
        self.WAIT_AFTER_WAKEUP = wait_after_wakeup

        connection_status = self.connection()
        if connection_status == "Connection failed":
            sys.exit(connection_status)

        table_status = self.create_table("PMS5003", ["date","PM1","PM25","PM10"])
        if table_status == "Error date":
            sys.exit(table_status)

    # Convert a two bytes string into a 16 bit integer.
    def _int16bit(self, _b):
        return (_b[0] << 8) + _b[1]

    # Return the hex dump of a buffer of bytes.
    def _buff2hex(self, _b):
        return " ".join("0x{:02x}".format(c) for c in _b)

    # Make a list of averaged reads: (datetime, float, float, ...)
    def _make_average(self, _reads_list):
        average = []
        average.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        for k in AVERAGE_FIELDS:
            average.append(float(sum(r[k] for r in _reads_list)) / len(_reads_list))
        return average

    # Convert the list created by make_average() to a string.   
    def _average2str(self, _a):
        s = _a[0]
        for f in _a[1:]:
            s += ' %0.2f' % (f)
        return s

    # Send a RESET signal to sensor.
    def _sensor_reset(self):
        self.logger.info("Sending RESET signal to sensor")
        try:
            gpio_direction = None
            if not os.path.isdir(PMS5003_RESET_GPIO):
                self.logger.error(u'GPIO for sensor RESET is not exported: %s' % (PMS5003_RESET_GPIO,))
                return
            else:
                with open(os.path.join(PMS5003_RESET_GPIO, 'direction'), 'r') as f:
                    gpio_direction = f.read().strip()
            if gpio_direction != 'out':
                self.logger.error(u'GPIO for sensor RESET is not set to output')
                return
            else:
                self.logger.info(u'Setting GPIO line to LOW for a short time')
                with open(os.path.join(PMS5003_RESET_GPIO, 'value'), 'w') as f:
                    f.write("0\n")
                time.sleep(0.5)
                with open(os.path.join(PMS5003_RESET_GPIO, 'value'), 'w') as f:
                    f.write("1\n")
                time.sleep(1.0)
        except Exception:
            self.logger.error(u'PMS5003 sensor RESET via GPIO line: Exception ' )
        except KeyboardInterrupt:
            sys.exit(1)
        return
    # Enter sensor sleep state.
    def _sensor_sleep(self, _port):
        self.logger.info("Sending sleep command")
        self._send_buffer(CMD_SLEEP, _port)
        _port.flushInput()

    # Exit from sleep state and wait sensor to settle.
    def _sensor_wakeup(self, _port):
        self.logger.info("Sending wakeup command")
        response = self._send_buffer(CMD_WAKEUP, _port)
        if not response:
            self.logger.error('No response to wakeup command')
            self._sensor_reset()
            self.logger.info('Sending wakeup command again')
            response = self._send_buffer(CMD_WAKEUP, _port)
            if not response:
                self.logger.error('No response to repeated wakeup command')
        self.logger.info("Waiting %d seconds for sensor to settle" % (self.WAIT_AFTER_WAKEUP,))
        time.sleep(self.WAIT_AFTER_WAKEUP)
        _port.flushInput()

    #---------------------------------------------------------------
    # Send a command buffer to the serial port, with checksum.
    # Return the response frame, if any.
    #---------------------------------------------------------------
    def _send_buffer(self, _b, _port):
        self.logger.debug("Using passive mode to send buffer: %s" % (self._buff2hex(_b),))
        _port.flushInput()
        written = _port.write(_b)
        if written != len(_b):
            self.logger.warning("Short write, sent %d bytes instead of %d" % (written, len(_b)))
            response = None
        else:
            # Get a response frame (if any). Examples:
            # Wakeup CMD: 0x42 0x4d 0xe4 0x00 0x01
            #   Response: 0x42 0x4d 0x00 0x1c ...(full data frame)
            # Sleep CMD:  0x42 0x4d 0xe4 0x00 0x00
            #   Response: 0x42 0x4d 0x00 0x04 0xe4 0x00
            response = self._read_pms5003(_port)
        return response

    #---------------------------------------------------------------
    # Read a data frame from serial port, the first 4 bytes are:
    # 0x42, 0x4d, frame lenght (16 bit integer).
    # and last two bytes are : checksum
    # Return None on errors.
    #---------------------------------------------------------------
    def _read_pms5003(self, _port):
        data = b''
        start_time = datetime.datetime.utcnow()
        while True:
            start_charac_1 = _port.read()
            if start_charac_1 != b'':
                self.logger.debug('Got char %s from serial read()' % start_charac_1[2:])
            else:
                self.logger.debug('Timeout on serial read()')
            if start_charac_1 == b'\x42':
                start_charac_2 = _port.read()
                if start_charac_2 == b'\x4d':
                    frame_len_high = _port.read()
                    frame_len_low  = _port.read()
                    frame_len = ord(frame_len_high) * 256 + ord(frame_len_low)
                    if frame_len == DATA_FRAME_LENGTH:
                        #Normal Data
                        data += start_charac_1 + start_charac_2 + frame_len_high + frame_len_low
                        data += _port.read(frame_len-2)
                        check_high = _port.read()
                        check_low  = _port.read()
                        check = ord(check_high) * 256 + ord(check_low)
                        data += check_high + check_low
                        #Verify lenght of data
                        if (len(data) - 4) != frame_len:
                            self.logger.error("Short read, expected %d bytes, got %d" % (frame_len, len(data) - 4))
                            return None
                        # Verify checksum (last two bytes).
                        checksum = 0
                        for i in range(0, len(data) - 2):
                            checksum += data[i]
                        if checksum != check:
                            self.logger.error("Checksum mismatch: %d, check %d" % (checksum, check))
                            return None
                        self.logger.debug("Received data frame = %s" % (self._buff2hex(data),))
                        return data
                    elif frame_len == CMD_FRAME_LENGTH:
                        # Command response frame.
                        data += start_charac_1 + start_charac_2 + frame_len_high + frame_len_low
                        data += _port.read(frame_len)
                        self.logger.debug("Received command response frame = %s" % (self._buff2hex(data),))
                        return data
                    else:
                        # Unexpected frame.
                        self.logger.error("Unexpected data length = %d" % (frame_len))
                        time.sleep(MAX_TOTAL_RESPONSE_TIME)
                        _port.flushInput()
                        return None
            if (datetime.datetime.utcnow() - start_time).seconds >= MAX_TOTAL_RESPONSE_TIME:
                self.logger.error("Timeout waiting data-frame signature")
                return None
    
    # Return the data frame in a verbose format.
    def _data_frame_verbose(self, _f):
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
                    _f['timestamp'],  _f['data1'],  _f['data2'],
                    _f['data3'],  _f['data4'],  _f['data5'],
                    _f['data6'],  _f['data7'],  _f['data8'],
                    _f['data9'],  _f['data10'], _f['data11'],
                    _f['data12'], _f['reserved'], _f['checksum']))
    
    # Main Program, sensor wakeup, read data, average data, save data in database and sensor sleep
    def begin(self):
        try:
            self._sensor_wakeup(PMS5003_port)
        except KeyboardInterrupt:
            sys.exit(1)

        reads_list = []
        error_count = 0
        error_total = 0
        while True:
            try:
                rcv = self._read_pms5003(PMS5003_port)
                # Manage data-frame errors.
                if rcv == None:
                    error_count += 1
                    error_total += 1
                    if error_count >= RESET_ON_FRAME_ERRORS:
                        self.logger.warning("Repeated read errors, attempting sensor reset")
                        self._sensor_reset()
                        error_count = 0
                        continue
                    if error_total >= MAX_FRAME_ERRORS:
                        if (AVERAGE_READS_SLEEP >= 0):
                            self.logger.error("Too many read errors, sleeping a while")
                            time.sleep(AVERAGE_READS_SLEEP)
                            error_total = 0
                            continue
                        else:
                            self.logger.error("Too many read errors, exiting")
                            break

                # Skip non-output data-frames.
                if (rcv == None) or ((len(rcv) - 4) != DATA_FRAME_LENGTH):
                    continue

                # Got a valid data-frame.
                res = {'timestamp': datetime.datetime.now(),
                    'data1':     self._int16bit(rcv[4:]),
                    'data2':     self._int16bit(rcv[6:]),
                    'data3':     self._int16bit(rcv[8:]),
                    'data4':     self._int16bit(rcv[10:]),
                    'data5':     self._int16bit(rcv[12:]),
                    'data6':     self._int16bit(rcv[14:]),
                    'data7':     self._int16bit(rcv[16:]),
                    'data8':     self._int16bit(rcv[18:]),
                    'data9':     self._int16bit(rcv[20:]),
                    'data10':    self._int16bit(rcv[22:]),
                    'data11':    self._int16bit(rcv[24:]),
                    'data12':    self._int16bit(rcv[26:]),
                    'reserved':  self._buff2hex(rcv[28:30]),
                    'checksum':  self._int16bit(rcv[30:])
                    }
                self.logger.debug("Got valid data frame:\n" + self._data_frame_verbose(res))
                reads_list.append(res)

                if len(reads_list) >= self.Average_Reads:
                    # Calculate the average of each measured data.
                    self.logger.info("Got %d valid readings, calculating average" % (len(reads_list)))
                    average = self._make_average(reads_list)
                    average_str = self._average2str(average)
                    self.logger.info("Average data: %s" % (average_str,))

                    date = average [0]; pm1 = average [4]; pm25 = average [5]; pm10 = average [6]

                    insert_status = self.insert_data(date,pm1,pm25,pm10)
                    if insert_status == "Insert data failed":
                        sys.exit(insert_status)

                    del reads_list[:]
                    if AVERAGE_READS_SLEEP < 0:
                        break
                    if AVERAGE_READS_SLEEP > (self.WAIT_AFTER_WAKEUP * 3):
                        # If sleep time is long enough, enter sensor sleep state.
                        self._sensor_sleep(PMS5003_port)
                        self.logger.info("Waiting %d seconds before new read" % (AVERAGE_READS_SLEEP,))
                        time.sleep(AVERAGE_READS_SLEEP)
                        self._sensor_wakeup(PMS5003_port)
                    else:
                        # Keep sensor awake and wait for next reads.
                        self.logger.info("Waiting %d seconds before new read" % (AVERAGE_READS_SLEEP,))
                        time.sleep(AVERAGE_READS_SLEEP)
                        PMS5003_port.flushOutput()
                        PMS5003_port.flushInput()

            except KeyboardInterrupt:
                break

        try:
            self.logger.info("Exiting main loop")
            self._sensor_sleep(PMS5003_port)
            PMS5003_port.close()
            disconnection_status =self.disconnection()
            if disconnection_status == "Disconnection failed":
                sys.exit(disconnection_status)
            sys.exit(0)
        except KeyboardInterrupt:
            pass
