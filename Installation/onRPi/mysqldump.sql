-- MySQL dump 10.16  Distrib 10.1.23-MariaDB, for debian-linux-gnueabihf (armv7l)
--
-- Host: localhost    Database: capteur_multi_pollutions
-- ------------------------------------------------------
-- Server version	10.1.23-MariaDB-9+deb9u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `AVG_DAY`
--

DROP TABLE IF EXISTS `AVG_DAY`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `AVG_DAY` (
  `systemId` varchar(40) NOT NULL,
  `date` datetime NOT NULL,
  `value` decimal(5,2) NOT NULL,
  `typeId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`systemId`,`date`,`typeId`),
  KEY `typeId` (`typeId`),
  CONSTRAINT `AVG_DAY_ibfk_1` FOREIGN KEY (`typeId`) REFERENCES `POLLUTANT` (`id`),
  CONSTRAINT `AVG_DAY_ibfk_2` FOREIGN KEY (`systemId`) REFERENCES `SYSTEM` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AVG_DAY`
--

LOCK TABLES `AVG_DAY` WRITE;
/*!40000 ALTER TABLE `AVG_DAY` DISABLE KEYS */;
/*!40000 ALTER TABLE `AVG_DAY` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AVG_HOUR`
--

DROP TABLE IF EXISTS `AVG_HOUR`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `AVG_HOUR` (
  `systemId` varchar(40) NOT NULL,
  `date` datetime NOT NULL,
  `value` decimal(5,2) NOT NULL,
  `typeId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`systemId`,`date`,`typeId`),
  KEY `typeId` (`typeId`),
  CONSTRAINT `AVG_HOUR_ibfk_1` FOREIGN KEY (`typeId`) REFERENCES `POLLUTANT` (`id`),
  CONSTRAINT `AVG_HOUR_ibfk_2` FOREIGN KEY (`systemId`) REFERENCES `SYSTEM` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AVG_HOUR`
--

LOCK TABLES `AVG_HOUR` WRITE;
/*!40000 ALTER TABLE `AVG_HOUR` DISABLE KEYS */;
/*!40000 ALTER TABLE `AVG_HOUR` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AVG_MONTH`
--

DROP TABLE IF EXISTS `AVG_MONTH`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `AVG_MONTH` (
  `systemId` varchar(40) NOT NULL,
  `date` datetime NOT NULL,
  `value` decimal(5,2) NOT NULL,
  `typeId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`systemId`,`date`,`typeId`),
  KEY `typeId` (`typeId`),
  CONSTRAINT `AVG_MONTH_ibfk_1` FOREIGN KEY (`typeId`) REFERENCES `POLLUTANT` (`id`),
  CONSTRAINT `AVG_MONTH_ibfk_2` FOREIGN KEY (`systemId`) REFERENCES `SYSTEM` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AVG_MONTH`
--

LOCK TABLES `AVG_MONTH` WRITE;
/*!40000 ALTER TABLE `AVG_MONTH` DISABLE KEYS */;
/*!40000 ALTER TABLE `AVG_MONTH` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AVG_YEAR`
--

DROP TABLE IF EXISTS `AVG_YEAR`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `AVG_YEAR` (
  `systemId` varchar(40) NOT NULL,
  `date` datetime NOT NULL,
  `value` decimal(5,2) NOT NULL,
  `typeId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`systemId`,`date`,`typeId`),
  KEY `typeId` (`typeId`),
  CONSTRAINT `AVG_YEAR_ibfk_1` FOREIGN KEY (`typeId`) REFERENCES `POLLUTANT` (`id`),
  CONSTRAINT `AVG_YEAR_ibfk_2` FOREIGN KEY (`systemId`) REFERENCES `SYSTEM` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AVG_YEAR`
--

LOCK TABLES `AVG_YEAR` WRITE;
/*!40000 ALTER TABLE `AVG_YEAR` DISABLE KEYS */;
/*!40000 ALTER TABLE `AVG_YEAR` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary table structure for view `MAP`
--

DROP TABLE IF EXISTS `MAP`;
/*!50001 DROP VIEW IF EXISTS `MAP`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `MAP` (
  `date` tinyint NOT NULL,
  `value` tinyint NOT NULL,
  `pollutant` tinyint NOT NULL,
  `unit` tinyint NOT NULL,
  `sensor` tinyint NOT NULL,
  `system` tinyint NOT NULL,
  `latitude` tinyint NOT NULL,
  `longitude` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `MEASUREMENTS`
--

DROP TABLE IF EXISTS `MEASUREMENTS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `MEASUREMENTS` (
  `systemId` varchar(40) NOT NULL,
  `date` datetime NOT NULL,
  `value` decimal(5,2) NOT NULL,
  `typeId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`systemId`,`date`,`typeId`),
  KEY `typeId` (`typeId`),
  CONSTRAINT `MEASUREMENTS_ibfk_1` FOREIGN KEY (`typeId`) REFERENCES `POLLUTANT` (`id`),
  CONSTRAINT `MEASUREMENTS_ibfk_2` FOREIGN KEY (`systemId`) REFERENCES `SYSTEM` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MEASUREMENTS`
--

LOCK TABLES `MEASUREMENTS` WRITE;
/*!40000 ALTER TABLE `MEASUREMENTS` DISABLE KEYS */;
/*!40000 ALTER TABLE `MEASUREMENTS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `POLLUTANT`
--

DROP TABLE IF EXISTS `POLLUTANT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `POLLUTANT` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(15) NOT NULL,
  `unit` varchar(15) NOT NULL,
  `sensor` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`,`unit`,`sensor`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `POLLUTANT`
--

LOCK TABLES `POLLUTANT` WRITE;
/*!40000 ALTER TABLE `POLLUTANT` DISABLE KEYS */;
INSERT INTO `POLLUTANT` VALUES (4,'humidity','%','DHT22'),(1,'pm10','µg/m^3','SDS011'),(2,'pm25','µg/m^3','SDS011'),(3,'temperature','°C','DHT22');
/*!40000 ALTER TABLE `POLLUTANT` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SYSTEM`
--

DROP TABLE IF EXISTS `SYSTEM`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SYSTEM` (
  `id` varchar(40) NOT NULL,
  `name` varchar(15) DEFAULT NULL,
  `latitude` varchar(20) DEFAULT NULL,
  `longitude` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SYSTEM`
--

LOCK TABLES `SYSTEM` WRITE;
/*!40000 ALTER TABLE `SYSTEM` DISABLE KEYS */;
/*!40000 ALTER TABLE `SYSTEM` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `MAP`
--

/*!50001 DROP TABLE IF EXISTS `MAP`*/;
/*!50001 DROP VIEW IF EXISTS `MAP`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `MAP` AS select `t1`.`date` AS `date`,`t1`.`value` AS `value`,`t2`.`name` AS `pollutant`,`t2`.`unit` AS `unit`,`t2`.`sensor` AS `sensor`,`t3`.`name` AS `system`,`t3`.`latitude` AS `latitude`,`t3`.`longitude` AS `longitude` from ((`AVG_HOUR` `t1` join `POLLUTANT` `t2` on((`t2`.`id` = `t1`.`typeId`))) join `SYSTEM` `t3` on((`t3`.`id` = `t1`.`systemId`))) where (`t1`.`date`,`t1`.`systemId`) in (select max(`AVG_HOUR`.`date`),`AVG_HOUR`.`systemId` from `AVG_HOUR` group by `AVG_HOUR`.`systemId`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-06-27 14:45:30
