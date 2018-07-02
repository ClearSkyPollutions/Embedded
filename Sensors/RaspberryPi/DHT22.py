import Adafruit_DHT
from Sensor import Sensor

from time import sleep
from datetime import datetime

sensor = Adafruit_DHT.DHT22

# TODO : Replace with config files
TABLE_NAME = "DHT22"
COL = ["date","temperature", "humidity"]

class DHT22(Sensor):


    def __init__(self, database, logger, gpio_pin = 4):
        super().__init__(database, logger)
        self.gpio_pin = gpio_pin
        self.vals = []

    def setup(self, frequency = 30):
        """Check that the sensor is working by reading once
            Check the database connection
            then configure frequency, averaging and database settings

        Arguments:
            frequency {double} -- Frequency for reading data, in data/min. Must be less than 30
                                    (default: {30})

        Exceptions:
            ValueError, RuntimeError, TypeError --  Sensor is disconnected
                                                    DB access impossible
                                                    Wrong table or columns names, wrong frequency
        """

        # Check sensor is working
        try:
            _1, _2 = Adafruit_DHT.read_retry(sensor, self.gpio_pin, 3, 2)
            if not _1 and not _2:
                raise RuntimeError("Error setting up connection : couldn't read data in 15 tries")
        except (ValueError, RuntimeError):
            self.logger.exception("")
            raise

        # Sensor configuration
        if (frequency > 30):
            raise ValueError("Frequency cannot be greater than 30 readings per minute")
        else :
            self.frequency = frequency

        self.logger.debug("Sensor is setup")

    def read(self):
        """Try to read from the sensor once, returning with the value of temperature and humidity
        
        Returns:
            (Double, Double) -- temperature,humidity or None,None if reading failed (failing happens)

        Exceptions:
            ValueError, RuntimeError -- Sensor is disconnected
        """

        try:
            humidity, temperature = Adafruit_DHT.read(sensor, self.gpio_pin)
        except (ValueError, RuntimeError):
            self.logger.exception("")
            raise
        # Note that sometimes you won't get a reading and the results will be null (because Linux can't
        # guarantee the timing of calls to read the sensor). If this happens try again!
        if humidity is not None and temperature is not None:
            self.logger.info('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
            self.vals.append([self.getdate(), temperature, humidity])
            return temperature, humidity
        else:
            self.logger.warning('Failed to get reading.')

    # TODO: probably doesn't belong in this class : 
    def insert(self):
        """Insert into the DB the last values read since the last call to this function
        """

        try:
            self.database.insert_data_bulk(TABLE_NAME, COL, self.vals)
        finally:
            self.vals = []