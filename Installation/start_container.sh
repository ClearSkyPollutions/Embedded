#!/bin/bash

function usage

{
	echo "usage: $0 PORT_HTTP PORT_DB CONTAINER_NAME"
}

if [ $# -ne 3 ]
then
	usage
else
	docker run  -dt --privileged -p $1:80 -p $2:3306 --name $3 server_dev
fi

