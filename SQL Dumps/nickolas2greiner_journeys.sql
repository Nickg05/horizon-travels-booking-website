CREATE DATABASE  IF NOT EXISTS `nickolas2greiner` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `nickolas2greiner`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: nickolas2greiner
-- ------------------------------------------------------
-- Server version	8.0.41-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `journeys`
--

DROP TABLE IF EXISTS `journeys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journeys` (
  `JourneyID` int NOT NULL,
  `departure` varchar(45) DEFAULT NULL,
  `arrival` varchar(45) DEFAULT NULL,
  `price` int DEFAULT NULL,
  `departure_time` time DEFAULT NULL,
  `arrival_time` time DEFAULT NULL,
  `fare` decimal(10,2) NOT NULL DEFAULT '100.00',
  PRIMARY KEY (`JourneyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journeys`
--

LOCK TABLES `journeys` WRITE;
/*!40000 ALTER TABLE `journeys` DISABLE KEYS */;
INSERT INTO `journeys` VALUES (1,'Newcastle','Bristol',90,'17:45:00','19:00:00',90.00),(2,'Bristol','Newcastle',90,'09:00:00','10:15:00',90.00),(3,'Cardiff','Edinburgh',90,'07:00:00','08:30:00',90.00),(4,'Bristol','Manchester',80,'06:20:00','07:20:00',80.00),(5,'Manchester','Bristol',80,'18:25:00','19:30:00',80.00),(6,'Bristol','London',80,'07:40:00','08:20:00',80.00),(7,'London','Manchester',100,'13:00:00','14:00:00',100.00),(8,'Manchester','Glasgow',100,'12:20:00','13:30:00',100.00),(9,'Bristol','Glasgow',110,'08:40:00','09:45:00',110.00),(10,'Glasgow','Newcastle',100,'14:30:00','15:45:00',100.00),(11,'Newcastle','Manchester',100,'16:15:00','17:05:00',100.00),(12,'Manchester','Bristol',80,'18:25:00','19:30:00',80.00),(13,'Bristol','Manchester',80,'06:20:00','07:20:00',80.00),(14,'Portsmouth','Dundee',120,'12:00:00','14:00:00',120.00),(15,'Dundee','Portsmouth',120,'10:00:00','12:00:00',120.00),(16,'Edinburgh','Cardiff',90,'18:30:00','20:00:00',90.00),(17,'Southampton','Manchester',90,'12:00:00','13:30:00',100.00),(18,'Manchester','Southampton',90,'19:00:00','20:30:00',90.00),(19,'Birmingham','Newcastle',100,'17:00:00','17:45:00',100.00),(20,'Newcastle','Birmingham',100,'07:00:00','07:45:00',100.00),(21,'Aberdeen','Portsmouth',100,'08:00:00','09:30:00',100.00);
/*!40000 ALTER TABLE `journeys` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-02 15:51:01
