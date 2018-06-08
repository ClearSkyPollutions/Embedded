#!/use/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector

conn = mysql.connector.connect(host="localhost",user="Raspi",password="Raspi",database="capteur_multi_pollutions")
cursor = conn.cursor()

cursor.execute("""DROP TABLE IF EXISTS Concentration_pm;""");

cursor.execute("""CREATE TABLE Concentration_pm (
		id INT UNSIGNED NOT NULL AUTO_INCREMENT,
		date_mesure DATETIME NOT NULL,
		pm2_5 DECIMAL(5,2) UNSIGNED NOT NULL,
		pm10 DECIMAL(5,2) UNSIGNED NOT NULL,
		PRIMARY KEY (id)
	);
""")

cursor.execute("""SELECT * FROM Concentration_pm""")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.commit()

cursor.close()
conn.close()
print("\nTable Créée ")
