#!/bin/bash

function usage

{
	echo "Kill all stopped containers"
}

if [ $# -ne 0 ]
then
	usage
else
	docker rm $(docker ps -a -q)
fi

