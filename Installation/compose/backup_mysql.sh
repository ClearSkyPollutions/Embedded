#!/bin/bash

# Database
user="Server"
password="Server"
host="localhost"
db_name="capteur_multi_pollutions"

# Other options
backup_path="backup/mysql"
DATE=$(date + "%d-%b-%Y")

# Set default flie permissions
umask 177

# Dump database
mysqldump --user=$user --password=$password $db_name > $backup_path/$db_name-$DATE.sql

# Delete files older than 30 days
# find $backup_path/* -mtime +30 -exec rm {} \;
