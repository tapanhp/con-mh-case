# ************************************************************
# Sequel Pro SQL dump
# Version 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: localhost (MySQL 5.6.35)
# Database: ohm_assessment
# Generation Time: 2017-04-17 16:30:27 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table rel_user
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rel_user`;

CREATE TABLE `rel_user` (
  `user_id` int(10) unsigned NOT NULL DEFAULT '0',
  `rel_lookup` varchar(128) NOT NULL DEFAULT '',
  `attribute` varchar(255) DEFAULT NULL,
  `create_transaction_id` int(10) unsigned DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`rel_lookup`),
  KEY `create_transaction_id` (`create_transaction_id`),
  KEY `rel_lookup` (`rel_lookup`),
  KEY `attribute` (`attribute`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table rel_user_multi
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rel_user_multi`;

CREATE TABLE `rel_user_multi` (
  `rum_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned DEFAULT NULL,
  `rel_lookup` varchar(255) DEFAULT NULL,
  `attribute` varchar(255) DEFAULT NULL,
  `create_transaction_id` int(10) unsigned DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rum_id`),
  UNIQUE KEY `user_id` (`user_id`,`rel_lookup`,`attribute`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table rel_user_text
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rel_user_text`;

CREATE TABLE `rel_user_text` (
  `rut_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `rel_lookup` varchar(255) DEFAULT NULL,
  `attribute` text,
  `create_transaction_id` int(11) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rut_id`),
  UNIQUE KEY `rut_constraint` (`user_id`,`rel_lookup`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table user
# ------------------------------------------------------------

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `user_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(128) DEFAULT NULL,
  `email_address` varchar(255) DEFAULT NULL,
  `display_name` varchar(50) DEFAULT NULL,
  `signup_date` date DEFAULT NULL,
  `enroll_status` varchar(50) NOT NULL DEFAULT 'PreValid',
  `enroll_complete` tinyint(1) DEFAULT '0',
  `tier` varchar(50) NOT NULL DEFAULT 'Carbon',
  `last_interaction_dttm` timestamp NULL DEFAULT NULL,
  `group_id` int(10) unsigned DEFAULT NULL,
  `current_ohm_service_id` int(10) unsigned DEFAULT NULL,
  `point_balance` double NOT NULL DEFAULT '0',
  `credit_balance` double NOT NULL DEFAULT '0',
  `donated_points` double NOT NULL DEFAULT '0',
  `lifetime_points` double NOT NULL DEFAULT '0',
  `create_transaction_id` int(10) unsigned DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user` (`username`),
  UNIQUE KEY `email_address` (`email_address`),
  KEY `point_balance` (`point_balance`),
  KEY `credit_balance` (`credit_balance`),
  KEY `donated_points` (`donated_points`),
  KEY `lifetime_points` (`lifetime_points`),
  KEY `enroll_complete` (`enroll_complete`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
