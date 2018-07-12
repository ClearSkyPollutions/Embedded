from Database import Database
import logging
import sys
import json
import time

import importlib
from CentralDB import CentralDatabase
from uuid import uuid4
import os

#CONFIG_FILE = '/var/www/html/config.json'
CONFIG_FILE = 'config.json'
DB_ACCESS = 1

#Local database
DB_IP = 'localhost'
DB_PORT = 3306

#Remote database (central server)
REMOTE_IP = 'localhost'
REMOTE_PORT = 5001

LOG_LEVEL = 'DEBUG'

LOG_FMT_FILE = '%(asctime)s %(levelname)s %(message)s'
LOG_FMT_DATE = '%Y-%m-%d %H:%M:%S'

def get_config():
    """Use the config file in the server directory
    
    Returns:
        Dict -- JSON dictionary containing the config
    """

    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    return cfg

#@TODO: Gerer les fichiers de logs
def setup_log():
    """Setup a logger used throughout the program
    
    Returns:
        logging.logger -- Logger
    """

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FMT_FILE, LOG_FMT_DATE))
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    log.addHandler(handler)
    return log


def transmission():
    """Connect to the remote server and send the latest data found in the local DB
    """

    log = setup_log()
    #Setup Base de Donnee
    try:
        db = Database("capteur_multi_pollutions", "Sensor", "Sensor", DB_IP, DB_PORT, log)
        db.connection()
    except:
        log.error("Couldn't connect to Database at ")
        return

    c = CentralDatabase(db, log, "http://" + REMOTE_IP + ":"str(REMOTE_PORT))

    tables = ["AVG_HOUR", "AVG_DAY", "AVG_MONTH", "AVG_YEAR"]
    for t in tables :
        data = c.getNewData(t)
        c.sendData(t, data)

    db.disconnection()


def setup(sensors, config, db, log):
    """Try to setup each sensor
    
    Arguments:
        sensors {string[]} -- Array of sensor name corresponding to module & class name of the driver
        config {dict} -- Dictionnary of configuration:value pairs (found in config.json)
        db {Database} -- Database Object representing local DB
        log {logging.logger} -- logger
    """

    log.info("Setting up sensors...")
    for i in config["Sensors"]:
        print(i)
    for i in config["Sensors"]:
        log.info(i)
        tmp_s = ""
        try:
            log.debug("Setting up sensor " + i + "...")
            if "MQ" in i:
                # Get the class MQ:
                tmp_class = getattr(importlib.import_module(i[:2]),i[:2])
                # Instanciate with proper type, and setup
                tmp_s = tmp_class(db, log, int(i[2:]))
            else:
                # Get the class named i in the python module name i :
                tmp_class = getattr(importlib.import_module(i),i)
                log.info(tmp_class)
                # Instanciate and setup
                tmp_s = tmp_class(db, log)
                log.info("2")
            tmp_s.setup()
            log.info("3")
            sensors.append(tmp_s)
            log.debug(i + " setup")
        except (ImportError):
            log.error("Error importing class " + str(tmp_s.__class__.__name__))
            try:
                open(tmp_s.__class__.__name__ + ".py")
            except IOError:
                log.error("No file " + str(tmp_s.__class__.__name__) + ".py")
        except Exception:
            log.error("Error setting up " + str(tmp_s.__class__.__name__))
    log.info("Setting up sensors - Done")

def read_and_save(sensors, config, log):
    """Read continuously from the setup sensors
    Store in DB the values every DB_ACCESS minutes
    
    Arguments:
        sensors {string[]} -- Array of sensor name corresponding to module & class name of the driver
        config {dict} -- Dictionnary of configuration:value pairs (found in config.json)
        log {logging.logger} -- logger
    """

    t = time.time()
    while(True):
        for i in sensors :
            #Don't stop if the reading from one sensor failed
            # TODO: maybe add a counter and stop if too many errors ?
            try:
                i.read()
            except:
                pass

        if ((time.time() - t)/60.0 > DB_ACCESS ):
            for j in sensors :
                try:
                    j.insert()
                except:
                    log.exception("")
                    raise
            t = time.time()
            transmission()

        time.sleep(60.0/config['Frequency']-0.3)

def acq():
    """Get configuration and logger, then connect to the local DB and set it up.
    Setup each sensor found in configuration, or discard them if setup failed.
    Start acquisition by reading from all of them repeatedly.
    Store in DB in regular intervals
    """

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

    #Setup Base de Donnee
    try:
        db = Database("capteur_multi_pollutions", "Sensor", "Sensor", DB_IP, DB_PORT, log)
        db.connection()
    except:
        log.error("Couldn't connect to Database at ")
        return

    # Setup sensors
    setup(sensors, config, db, log)

    # Do acquisition if sensors have been set up properly
    if sensors:
        log.info("Starting acquisition...\n")
        read_and_save(sensors, config, log)
    else:
        log.info("No sensors detected, exiting")

    db.disconnection()

acq()
