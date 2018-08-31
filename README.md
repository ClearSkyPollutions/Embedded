# Embedded

Code source for the ClearSky IoT system for multi-pollution detection.

## Getting started

* Clone the project in a Raspberry Pi
* Depending on the sensors you wish to connect, use one of our sensor python file to drive it, or create a file implementing Sensor.py
* Use our Docker images, build our docker image, or install a standard LAMP stack
  * The Installation folder has information and help regarding the setup of the apache2 server and the MariaDB database
* Follow the instructions on the android application to finalize the system setup

## Cloud service

If you choose to share your data, your data will be send regularly to a VPS owned by Sogeti High Tech at 51.38.38.251.
Your position will be blurred so that you may not be identified by your location
