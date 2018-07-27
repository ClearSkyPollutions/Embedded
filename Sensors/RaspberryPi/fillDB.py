import logging
import sys
import mysql.connector
from Database import Database

conn = mysql.connector.connect(host="192.168.2.118", port=7001, user="Sensor", password="Sensor", database="capteur_multi_pollutions")
cursor = conn.cursor(dictionary=False)
query = "SELECT date, temperature, humidity from AVG_YEAR"
cursor.execute(query)
dataDHT = cursor.fetchall()
query = "SELECT date, temperature, humidity from AVG_YEAR"
cursor.execute(query)
dataSDS = cursor.fetchall()

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
log = logging.getLogger()
log.setLevel("DEBUG")
log.addHandler(handler)


db = Database("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.118", 4001, log)
db.connection()

db.insert_data_bulk("DHT22", ["date", "temperature", "humidity"], ["°C", "%"], dataDHT)
db.insert_data_bulk("SDS011", ["date", "pm25","pm10"], ["µg/m^3", "µg/m^3"], dataSDS)