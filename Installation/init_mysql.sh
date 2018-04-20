mysql -uroot -e "CREATE DATABASE capteur_multi_pollutions"
mysql -uroot -e "CREATE USER 'Raspi'@'localhost' IDENTIFIED BY 'Raspi'"
mysql -uroot -e "GRANT ALL PRIVILEGES ON * . * TO 'Raspi'@'localhost' WITH GRANT OPTION"
mysql -uroot -e "CREATE USER 'Admin'@'%' IDENTIFIED BY 'Admin'"
mysql -uroot -e "GRANT ALL PRIVILEGES ON * . * TO 'Admin'@'%' WITH GRANT OPTION"
mysql -uroot -e "CREATE USER 'AppAndroid'@'%' IDENTIFIED BY 'AppAndroid'"
mysql -uroot -e "GRANT ALL PRIVILEGES ON capteur_multi_pollutions.* TO 'AppAndroid'@'%'"
mysql -uroot -e "CREATE USER 'Sensor'@'%' IDENTIFIED BY 'Sensor'"
mysql -uroot -e "GRANT ALL PRIVILEGES ON capteur_multi_pollutions.* TO 'Sensor'@'%'"
mysql -uroot capteur_multi_pollutions -e "DROP TABLE IF EXISTS Concentration_pm"
mysql -uroot capteur_multi_pollutions -e "CREATE TABLE Concentration_pm (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    date_mesure DATETIME NOT NULL,
    pm2_5 DECIMAL(5,2) UNSIGNED NOT NULL,
    pm10 DECIMAL(5,2) UNSIGNED NOT NULL,
    PRIMARY KEY (id)
)"
mysql -uroot capteur_multi_pollutions -e "INSERT INTO Concentration_pm (date_mesure, pm2_5, pm10) VALUES (\"2018-04-20 14:50:00\", '120', '240')"
