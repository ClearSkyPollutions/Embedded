from Database import Database
import logging
import sys
import json
from time import sleep

import importlib
from CentralDB import CentralDatabase
from uuid import uuid4
from DHT22 import DHT22
from SDS011 import SDS011
import os

CONFIG_FILE = '/var/www/html/config.json'
#CONFIG_FILE = 'config.json'
WIFI_CONFIG_FILE = '/etc/wpa_supplicant/wpa_supplicant.conf'
DB_ACCESS = 1

DB_IP = '192.168.2.118'
DB_PORT = 7001

LOG_LEVEL = 'INFO'

LOG_FMT_FILE = '%(asctime)s %(levelname)s %(message)s'
LOG_FMT_DATE = '%Y-%m-%d %H:%M:%S'

def get_config():
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    return cfg

def setup_log():
    # Log to stdout.
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FMT_FILE, LOG_FMT_DATE))
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    log.addHandler(handler)
    return log

def transmission():
    log = setup_log()
    #Setup Base de Donnee
    try:
        db = Database("capteur_multi_pollutions", "Sensor", "Sensor", DB_IP, DB_PORT, log)
        db.connection()
    except:
        log.error("Couldn't connect to Database at ")
        return

    c = CentralDatabase(db, log, "http://192.168.2.118:5000")
    data = c.getNewData('AVG_HOUR')
    # log.warning(data['pm10'])
    c.sendData('AVG_HOUR', data)

    db.disconnection()



def wifi_config(config):
    print('Starting wifi_config...')
    with open(WIFI_CONFIG_FILE) as f:
            in_file = f.readlines()
            f.close()

    out_file = []
    for line in in_file:
        if line.startswith('ssid'):
            line = 'ssid='+'"'+config['SSID']+'"'+'\n'
        elif line.startswith('psk'):
            line = 'psk='+'"'+config['Password']+'"'+'\n'
        elif line.startswith('key_mgmt'):
            line = 'key_mgmt='+config['SecurityType']+'\n'
        out_file.append(line)
    
    with open(WIFI_CONFIG_FILE,'w') as f:
       for line in out_file:
               f.write(line)
       f.close()

    cmd = "service networking restart"
    os.system(cmd)


def acq():
    sensors = []

    log = setup_log()

    # Get config from json file
    log.debug("Read config from {} file".format(CONFIG_FILE))
    try:
        config = get_config()
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        log.error("Problem reading json file")
    except Exception:
        log.exception("")
        return

    #Setup Wifi Config
    wifi_config(config)

    #Setup Base de Donnee
    try:
        db = Database("capteur_multi_pollutions", "Sensor", "Sensor", DB_IP, DB_PORT, log)
        db.connection()
    except:
        log.error("Couldn't connect to Database at ")
        return


    # Setup sensors
    setup(sensors, config, db, log)

    # Do acquisition if sensors have been set up correctly
    if sensors:
        log.info("Starting acquisition...\n")
        read_and_save(sensors, config, log)

        # Save last data and stop
        for i in sensors :
            i.insert()
            i.stop()
    else:
        log.info("No sensors detected, exiting")

    db.disconnection()

def setup(sensors, config, db, log):
    log.info("Setting up sensors...")
    for i in config["Sensors"]:
        try:
            if "MQ" in i:
                # Get the class MQ:
                tmp_class = getattr(importlib.import_module(i[:2]),i[:2])
                # Instanciate with proper type, and setup
                tmp_s = tmp_class(db, log, int(i[2:]))
            else:
                # Get the class named i in the python module name i :
                tmp_class = getattr(importlib.import_module(i),i)
                # Instanciate and setup
                tmp_s = tmp_class(db, log)
            tmp_s.setup()
            sensors.append(tmp_s)
        except (ImportError):
            log.error("Error importing class" + str(tmp_s.__class__.__name__))
            try:
                open(tmp_s.__class__.__name__ + ".py")
            except IOError:
                log.error("No file " + str(tmp_s.__class__.__name__) + ".py")
        except Exception:
            log.error("Error setting up " + str(tmp_s.__class__.__name__))

def read_and_save(sensors, config, log):
    cpt=0
    while(True):
        for i in sensors :
            #Don't stop if the reading from one sensor failed
            # TODO : maybe add a counter and stop if too many errors ?
            try:
                i.read()
            except:
                pass
        cpt+=1
        print(cpt)

        if (cpt == config['Frequency'] / DB_ACCESS ):
            for j in sensors :
                try:
                    j.insert()
                except:
                    log.exception("")
                    raise
            cpt = 0

        sleep(60/config['Frequency']-0.5)


transmission()
