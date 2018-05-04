import Adafruit_DHT
from SensorsDatabase import SensorsDatabase as sens

class DHT22(sens)

    Adafruit_DHT.DHT22

    # Example using a Beaglebone Black with DHT sensor
    # connected to pin P8_11.
    #pin = 'P8_11'

    # Example using a Raspberry Pi with DHT sensor
    # connected to GPIO23.
    pin = 4

    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
    if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
    print('Failed to get reading. Try again!')