#!/use/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector

conn = mysql.connector.connect(host="localhost",user="root")
cursor = conn.cursor()

cursor.execute("""CREATE USER 'Raspi'@'localhost' IDENTIFIED BY 'Raspi';""")
cursor.execute("""GRANT ALL PRIVILEGES ON *.* TO 'Raspi'@'localhost';""")

cursor.execute("""CREATE USER 'appAndroid'@'192.168.%' IDENTIFIED BY 'appAndroid';""")
cursor.execute("""GRANT ALL PRIVILEGES ON capteur_multi_pollutions.* TO 'appAndroid'@'192.168.%';""")

cursor.execute("""CREATE USER 'arduinoDUE'@'192.168.%' IDENTIFIED BY 'arduinoDUE';""")
cursor.execute("""GRANT ALL PRIVILEGES ON capteur_multi_pollutions.* TO 'arduinoDUE'@'192.168.%';""")

conn.commit()

cursor.close()
conn.close()
print("Users Raspi, appAndroid, arduinoDUE created")
