/*
this script is for initializing the DB
it creates a DB and user for connecting to the DB

it should be run in a MariaDB/ MySQL environment as admin


THIS SCRIPT DOES NOT CREATE THE TABLES FOR THE MODELS!
THAT'S DONE IN configDB.sql, which doesn't need admin
and is executed through the new user
*/

CREATE DATABASE 'SCIENCE_FAIR';
CREATE USER 'FAIRY' IDENTIFIED BY '123456789';
GRANT USAGE ON *.* TO 'FAIRY'@'%' IDENTIFIED BY '123456789';
GRANT ALL privileges ON 'SCIENCE_FAIR' TO 'FAIRY'@'%';
FLUSH PRIVILEGES;