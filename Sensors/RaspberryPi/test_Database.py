import unittest
import logging
import sys

from Database import Database

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
log = logging.getLogger()
log.setLevel("DEBUG")
log.addHandler(handler)

class TestDBConnection(unittest.TestCase):

    def test_connection(self):
        db = Database("capteur_multi_pollutions", "Sensor",
                      "Sensor", "192.168.2.118", 4071, log)
        db.connection()
        self.assertEqual(db.sysId, 'testId')
        db.disconnection()

    def test_connection_wrong_db(self):
        with self.assertRaises(RuntimeError):
            db = Database("wrongDB", "Sensor", "Sensor",
                          "192.168.2.118", 4071, log)
            db.connection()

    def test_connection_wrong_userpwd(self):
        with self.assertRaises(RuntimeError):
            db = Database("capteur_multi_pollutions", "WrongUser",
                          "Sensor", "192.168.2.118", 4071, log)
            db.connection()

    def test_connection_wrong_address(self):
        with self.assertRaises(RuntimeError):
            db = Database("capteur_multi_pollutions", "Sensor",
                          "Sensor", "000.010.1.213", 4071, log)
            db.connection()


class testDBFunctions(unittest.TestCase):

    def setUp(self):
        self.db = Database("capteur_multi_pollutions", "Sensor",
                           "Sensor", "192.168.2.118", 4071, log)
        self.db.connection()

    def tearDown(self):
        self.db.disconnection()
        self.db = None

    def test_id(self):
        pollutants = ["pm25"]
        units = ["µg/m^3"]
        self.assertEqual(self.db.get_ids(
            "SDS011", pollutants, units)["pm25"], 2)

    def test_id_insert(self):
        pollutants = ["pollutantTest"]
        units = ["unitTest"]
        self.assertEqual(self.db.get_ids(
            "SensorTest", pollutants, units)["pollutantTest"], 5)

    def test_format_data(self):
        data = [["2018-07-03 12:00:00", 27, 12.0],
                ["2018-07-03 13:00:00", 28, 13.0]]
        transform = [("2018-07-03 12:00:00", 27, 1),
                     ("2018-07-03 12:00:00", 12.0, 2),
                     ("2018-07-03 13:00:00", 28, 1),
                     ("2018-07-03 13:00:00", 13.0, 2)]
        self.assertEqual(self.db._format_data(
            data, ["pm25", "pm10"], {"pm25": 1, "pm10": 2}), transform)
