CREATE TABLE SYSTEM (
	id varchar(40) PRIMARY KEY,
	name varchar(15),
	latitude varchar(20),
	longitude varchar(20)
);

CREATE TABLE POLLUTANT (
	id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name varchar(15) NOT NULL,
	unit varchar(15) NOT NULL,
	sensor varchar(30) NOT NULL,
	UNIQUE (name, unit, sensor)
);

CREATE TABLE AVG_HOUR (
	systemId varchar(40) NOT NULL,
	date DATETIME NOT NULL,
	value DECIMAL(5,2) NOT NULL,
	typeId INT UNSIGNED,
	FOREIGN KEY(typeId) REFERENCES POLLUTANT(id),
	FOREIGN KEY(systemId) REFERENCES SYSTEM(id),
	PRIMARY KEY (systemId, date, typeId)
);

CREATE TABLE AVG_DAY (
	systemId varchar(40) NOT NULL,
	date DATETIME NOT NULL,
	value DECIMAL(5,2) NOT NULL,
	typeId INT UNSIGNED,
	FOREIGN KEY(typeId) REFERENCES POLLUTANT(id),
	FOREIGN KEY(systemId) REFERENCES SYSTEM(id),
	PRIMARY KEY (systemId, date, typeId)
);

CREATE TABLE AVG_MONTH (
	systemId varchar(40) NOT NULL,
	date DATETIME NOT NULL,
	value DECIMAL(5,2) NOT NULL,
	typeId INT UNSIGNED,
	FOREIGN KEY(typeId) REFERENCES POLLUTANT(id),
	FOREIGN KEY(systemId) REFERENCES SYSTEM(id),
	PRIMARY KEY (systemId, date, typeId)
);

CREATE TABLE AVG_YEAR (
	systemId varchar(40) NOT NULL,
	date DATETIME NOT NULL,
	value DECIMAL(5,2) NOT NULL,
	typeId INT UNSIGNED,
	FOREIGN KEY(typeId) REFERENCES POLLUTANT(id),
	FOREIGN KEY(systemId) REFERENCES SYSTEM(id),
	PRIMARY KEY (systemId, date, typeId)
);

INSERT INTO POLLUTANT(name, unit, sensor) VALUES("pm10", "µg/m^3", "SDS011"),("pm25", "µg/m^3", "SDS011"),("temperature", "°C", "DHT22"),("humidity", "%", "DHT22");

/* View containing last data from all systems */
create view MAP as 
SELECT 
	t1.date, t1.value, t2.name as pollutant, t2.unit, t2.sensor,  t3.name as system, t3.latitude, t3.longitude
FROM
	AVG_HOUR t1
inner join 
	POLLUTANT t2 ON t2.id = t1.typeId 
inner join
	SYSTEM t3 ON t3.id = t1.systemid
WHERE
	(t1.date,t1.systemId) IN (SELECT max(date),systemId FROM AVG_HOUR GROUP BY systemId);

