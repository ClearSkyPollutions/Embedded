#!/usr/bin/python3
# coding=utf-8

import sys, argparse, pprint
from datetime import datetime, timedelta 
from random import uniform
from Database import Database

import logging

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
log.setLevel('INFO')
log.addHandler(handler)

def returnJourSec(x):
    jour = int(1/x)
    sec = int(24*3600/x - 24*3600*jour)
    return jour,sec
    
def setupParse():
    parser = argparse.ArgumentParser()
    parser.add_argument("p",type=int,help="Port MySQL")
    parser.add_argument("d",type=int,help="Nb of day")
    parser.add_argument("f",type=float,help="Frequency par day")
    parser.add_argument("--maxPM",type=int,help="Max values for PM",default=30)
    parser.add_argument("--minPM",type=int,help="Min values for PM",default=10)
    parser.add_argument("--maxTemp",type=int,help="Max values for Temperature",default=25)
    parser.add_argument("--minTemp",type=int,help="Min values for Temperature",default=10)
    parser.add_argument("--maxHum",type=int,help="Max values for Humidity",default=45)
    parser.add_argument("--minHum",type=int,help="Min values for Humidity",default=35)
    args = parser.parse_args()
    return args.p, args.d, args.f, args.maxPM, args.minPM, args.maxTemp, args.minTemp, args.maxHum, args.minHum

if __name__ == "__main__":
    
    port, duration, freq, maxPM, minPM, maxTemp, minTemp, maxHum, minHum = setupParse()
    log.debug(port, duration, freq, maxPM, minPM,maxTemp, minTemp, maxHum, minHum) 
    database = Database("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.69", port, logger=log)
    database.connection()
    tab_names = ["SDS011","DHT22"]
    tab_col = [["date","pm25","pm10"],["date","temperature","humidity"]]

    for i in range(0, len(tab_names)):
        database.create_table(tab_names[i],tab_col[i])
    
    date = datetime(2017,1,1)
    delta = timedelta(*returnJourSec(freq))
    pm25_f = uniform(minPM, maxPM)
    pm10_f = uniform(minPM, maxPM)
    temp_f = uniform(minTemp, maxTemp)
    hum_f = uniform(minHum, maxHum)
    ConcPM = []
    DHT22 = []
    ConcPM.append([date.strftime('%Y-%m-%d %H:%M:%S'),pm25_f,pm10_f]) 
    DHT22.append([date.strftime('%Y-%m-%d %H:%M:%S'),temp_f,hum_f])

    for i in range(int(duration * freq)):
        date += delta
        pm25 = pm25_f * uniform(0.9, 1.1)
        pm10 = pm10_f * uniform(0.9, 1.1)
        temp = temp_f * uniform(0.9, 1.1)
        hum  = hum_f * uniform(0.9, 1.1)

        ConcPM.append([date.strftime('%Y-%m-%d %H:%M:%S'),pm25,pm10]) 
        DHT22.append([date.strftime('%Y-%m-%d %H:%M:%S'),temp,hum])
    
    tab_data = [ConcPM,DHT22]
    for i in range(0, len(tab_data)):
        database.insert_data_bulk(tab_names[i],tab_col[i],tab_data[i])
    
    database.disconnection()