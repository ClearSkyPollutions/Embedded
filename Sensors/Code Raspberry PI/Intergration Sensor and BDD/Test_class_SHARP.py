#!/use/bin/env python3
# -*- coding: utf-8 -*-

import sys
import datetime

import logging

from SHARP import SHARP
from pipyadc import ADS1256

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

SHARP = SHARP("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.69", "6000", logger=log)

ave_read = 30
wait_a_wakeup = 30
wait_a_aver = 300 # -1 for no continue

setup_status = SHARP.setup(30, False)

if setup_status == "Connection failed":
    log.error("Connection to MySQL database failed")
    sys.exit(0)
elif setup_status == "Error date":
    log.error("Error to creating MySQL Table")
    sys.exit(0)
elif setup_status == "Sensor wakeup failed":
    log.error("Sensor SDS011 wakeup failed")
    sys.exit(0)
elif setup_status == "KeyboardInterrupt":
    log.error("Keyboard Interrupt")


start_status = SHARP.start()

if start_status == "Too many read errors, exiting":
    log.error("Too many read errors, exiting, please reload program")
    sys.exit(0)
elif start_status == "Stop Read":
    log.info("First average insert and wait_after_average = -1")
elif start_status == "KeyboardInterrupt":
    log.error("Keyboard Interrupt")
    #sys.exit(0)

stop_status = SHARP.stop()

if stop_status == "Sensor sleep failed":
    log.error("Sensor sleep failed")
    sys.exit(0)
elif stop_status == "Disconnection failed":
    log.error("Disconnection to MySQL database failed")
    sys.exit(0)
