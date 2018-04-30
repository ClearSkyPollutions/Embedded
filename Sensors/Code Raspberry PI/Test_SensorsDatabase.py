#!/use/bin/env python3
# -*- coding: utf-8 -*-

import sys
import datetime

import logging

from SensorsDataBase import SensorsDatabase

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

Sensor = SensorsDatabase("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.108", "4306", log)

Sensor.connection()

tab = ["date","pm25","pm10"]
Sensor.create_table("Essai",tab)

#date = datetime.datetime.now()
date = "2018-04-30 18:14:00"
data = [8,9.5]
Sensor.insert_data(date, data)

Sensor.disconnection()
