# Host: 127.0.0.1  (Version 5.7.13-log)
# Date: 2017-01-20 15:26:47
# Generator: MySQL-Front 5.4  (Build 4.23)
# Internet: http://www.mysqlfront.de/

/*!40101 SET NAMES utf8 */;

#
# Structure for table "users"
#

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `passwd` varchar(40) NOT NULL,
  `email` varchar(40) NOT NULL,
  `join_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
