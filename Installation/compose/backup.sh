#!bin/bash
#Purpose : Backup of mysql container data
DATE=$(date +"%d-%b-%Y")
lrztar /var/lib/docker/volumes/compose_db-data/_data/
mv _data.tar.lrz backup/$DATE.tar.lrz
