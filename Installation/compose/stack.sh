#!/bin/bash
#Purpose : Help manage docker-compose

function usage

{
		echo "usage: $0 [build] [start] [stop]"
}

if [ $# -le 0 ]
then
	usage
else
	for cmd in $* 
	do
		docker-compose -f /home/msf/Embedded/Installation/compose/stack.yml $cmd
	done
fi

