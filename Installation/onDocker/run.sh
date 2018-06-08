#!/bin/sh
/usr/sbin/service apache2 start 
/usr/sbin/service mysql start 
/bin/sh /init_mysql.sh 
echo "Service apache2 started"
echo "Service mysql started"
while true; do date; sleep 5; done
