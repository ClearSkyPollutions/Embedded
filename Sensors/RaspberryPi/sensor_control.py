from Database import Database
import logging
import sys
import json
from time import sleep

import importlib
from DHT22 import DHT22
from SDS011 import SDS011

CONFIG_FILE = 'config.json'

LOG_LEVEL = 'INFO'

LOG_FMT_FILE = '%(asctime)s %(levelname)s %(message)s'
LOG_FMT_DATE = '%Y-%m-%d %H:%M:%S'

def get_config():
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    return cfg


def acq():
    sensors = []

    # Log to stdout.
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FMT_FILE, LOG_FMT_DATE))
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    log.addHandler(handler)

    #Setup Base de Donnee
    db = Database("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.69", "8001", log)

    try:
        config = get_config()
        db.connection()
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        log.error("Problem reading json file")
    except Exception:
        log.exception("")
        return

    log.info("Setting up sensors...")
    
    for i in config["Sensors"]:
        try:
            # Get the class named i in the python module name i :
            tmp_class = getattr(importlib.import_module(i),i)
            # Instanciate and setup
            tmp_s = tmp_class(db, logger=log)
            tmp_s.setup()
            sensors.append(tmp_s)
        except (ModuleNotFoundError, AttributeError):
            log.exception("")
        except Exception:
            log.error("Error setting up " + str(tmp_s.__class__.__name__))

    log.info("Starting acquisition...\n")
    
    for _ in range (0,int(config['Frequency']*config['Duration'])):
        for i in sensors :
            #Don't stop if the reading from one sensor failed
            # TODO : maybe add a counter and stop if too many errors ?
            try:
                i.read()
            except:
                pass
        sleep(60/config['Frequency']-0.5)
        if _ and _%int(config['Frequency']/config['DBAccess']) == 0:
            for j in sensors :
                try:
                    j.insert()
                except:
                    log.exception("")
                    raise

    # Save last data and stop
    for i in sensors :
        i.insert()
        i.stop()

    db.disconnection()

acq()