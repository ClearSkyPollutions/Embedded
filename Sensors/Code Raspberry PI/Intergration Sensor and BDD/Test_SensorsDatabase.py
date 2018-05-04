#!/use/bin/env python3
# -*- coding: utf-8 -*-

import sys
import datetime

import logging

from SensorsDatabase import SensorsDatabase

# Log to stdout or to file/syslog.
LOG_TO_STDOUT = sys.stdin.isatty()
# False for syslog logging, filename for file logging.
LOG_TO_FILE = False
LOG_FMT_SYSLOG = '%(module)s: %(levelname)s %(message)s'
LOG_FMT_FILE = '%(asctime)s %(levelname)s %(message)s'
LOG_FMT_DATE = '%Y-%m-%d %H:%M:%S'

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

Sensor = SensorsDatabase("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.69", "4306", log)

connection_status = Sensor.connection()
if connection_status == "Connection failed":
    sys.exit(connection_status)

tab = ["pm1","pm25","pm10","pm522","pm824","pm557"]

table_status = Sensor.create_table("Essai5",tab)
if table_status == "Error date":
    sys.exit(table_status)

#date = datetime.datetime.now() #Raspi 
date = "2018-05-02 10:16:00"    #Test
data = [4,3,5,5,8,6]

pm1 = data[0]; pm25 = data[1]; pm10 = data[2]; pm522 = data[3]; pm824 = data[4]; pm557 = data[5]

insert_status = Sensor.insert_data(date, pm1, pm25, pm10, pm522, pm824, pm557)
if insert_status == "Insert data failed":
    sys.exit(insert_status)

disconnection_status = Sensor.disconnection()
if disconnection_status == "Disconnection failed":
    sys.exit(disconnection_status)
