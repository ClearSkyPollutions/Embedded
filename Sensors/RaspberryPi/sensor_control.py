from Database import Database
import logging
import sys
import json
from time import sleep
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

    db = Database("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.69", "8001", log)

    config = get_config()

    #Setup Base de Donnee
    connection_status = db.connection()
    if connection_status == "Connection failed":
        return connection_status

    log.info("Setting up sensors...")
    
    tmp_s = DHT22(db, logger=log)
    if tmp_s.setup():
        sensors.append(tmp_s)
    tmp_s = SDS011(db, logger=log)
    if tmp_s.setup():
        sensors.append(tmp_s)

    log.info("Starting acquisition...\n")
    
    for _ in range (0,int(config['Frequency']*config['Duration'])):
        for i in sensors :
            i.read()
        sleep(60/config['Frequency']-0.5)
        if _ and _%int(config['Frequency']/config['DBAccess']) == 0:
            for j in sensors :
                j.insert()

    # Save last data and stop
    for i in sensors :
        i.insert()
        i.stop()

    db.disconnection()

acq()