#!/bin/bash
cp ./Installation/onRPi/html/* /var/www/html/
touch log.txt
python3 ./Sensors/RaspberryPi/sensor_control.py &
#PID=$(pidof python3 ./Sensors/RaspberryPi/sensor_control.py)
PID=$!
echo $PID
while true; do    
    RECEIVED=$(cat /var/www/html/clearSky.fifo)
    echo $RECEIVED
    EXPECTED="restart"
    if [[ "$RECEIVED" == "$EXPECTED" ]]
    then
        kill $PID
        python3 ./Sensors/RaspberryPi/sensor_control.py &
        PID=$(pidof python3 ./Sensors/RaspberryPi/sensor_control.py)
        echo $PID
    fi
done