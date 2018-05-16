import Adafruit_DHT
from Sensor import Sensor

from time import sleep
from datetime import datetime

sensor = Adafruit_DHT.DHT22

# TODO : Replace with config files
TABLE_NAME = "DHT22"
COL = ["date","temperature", "humidity"]

class DHT22(Sensor):

    frequency = 30 #readings/minute
    avg = False

    def __init__(self, database, user, password, host, port, logger, gpio_pin = 4):
        super().__init__(TABLE_NAME, logger)
        self.gpio_pin = gpio_pin


    def setup(self, frequency, averaging = False):
        """Check that the sensor is working by reading once
            Check the database connection
            then configure frequency, averaging and database settings

        Arguments:
            frequency {double} -- Frequency for reading data, in data/min. Must be less than 30

        Keyword Arguments:
            averaging {boolean} -- If True, data will be read every 2 seconds, but returned averaged every 1/frequency 
                                    (default: {False})
        """

        # Check sensor is working
        try:
            Adafruit_DHT.read_retry(sensor, self.gpio_pin, 3, 2)
        except Exception as e:
            self.logger.error(str(e))
            return False

        # Setup config sensor
        if (frequency > 30):
            return False
        else :
            self.frequency = frequency
            self.avg = averaging

        table_status = self.database.create_table(TABLE_NAME,COL)
        if table_status == "Error date":
            return table_status

        self.logger.debug("Sensor is setup")


    def read(self):
            # Try to grab a sensor reading.  
            try:
                humidity, temperature = Adafruit_DHT.read(sensor, self.gpio_pin)
            except Exception as e:
                self.logger.error(str(e))
                return None
            # Note that sometimes you won't get a reading and the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor). If this happens try again!
            if humidity is not None and temperature is not None:
                self.logger.debug('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
                return temperature, humidity
            else:
                self.logger.warning('Failed to get reading.')


    def _read_data(self):
            # Try to grab a sensor reading.  Use the read_retry method which will retry up
            # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
            try:
                humidity, temperature = Adafruit_DHT.read_retry(sensor, self.gpio_pin)
            except Exception as e:
                self.logger.error(str(e))
                return False
            # Note that sometimes you won't get a reading and the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor). If this happens try again!
            if humidity is not None and temperature is not None:
                self.logger.debug('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
                return temperature, humidity
            else:
                self.logger.warning('Failed to get reading.')


    def start(self, duration = 0):
        start_time = self.getdate()
        last_data = ""
        sums = [0,0]
        counter = 0

        while True :

            # Get last data
            data = self._read_data()
            if not data:
                continue

            # If no averaging, send it and wait for the next one
            if not self.avg :
                self.database.insert_data(self.getdate(),*data)
                sleep(60.0/self.frequency)

            # If averaging, check whether to send it or not, and wait 2 sec (minimum) for next data
            else:
                sums[0] += data[0]
                sums[1] += data[1]
                counter += 1 
                t = self.getdate()
                difftime = datetime.strptime(t, '%Y-%m-%d %H:%M:%S') - datetime.strptime(last_data, '%Y-%m-%d %H:%M:%S')

                if difftime.total_seconds() > 60.0/self.frequency:
                    if self.database.insert_data(t, sums[0]/counter, sums[1]/counter) == "Insert data failed":
                        return "Insert data failed"
                    sums = [0,0]
                    counter = 0
                    last_data = t

                sleep(2)           
                
            # Stop if duration is reached
            if(duration != 0 and self.getdate() - start_time > duration):
                return


    def stop(self):
        self.logger.debug("Exiting main loop")

        #MySQL Stop
        return self.database.disconnection()