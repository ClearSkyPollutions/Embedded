import unittest
import logging
import sys

from Database import Database


class TestDBConnection(unittest.TestCase):

    def setUp(self):
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
        self.log = logging.getLogger()
        self.log.setLevel("DEBUG")
        self.log.addHandler(handler)

    def test_connection(self):
        db = Database("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.118", 4071, self.log)
        db.connection()
        self.assertEqual(db.sysId, 'testId')
        db.disconnection()

    def test_connection_wrong_db(self):
        with self.assertRaises(RuntimeError):
            db = Database("wrongDB", "Sensor", "Sensor", "192.168.2.118", 4071, self.log)
            db.connection()

    def test_connection_wrong_userpwd(self):
        with self.assertRaises(RuntimeError):
            db = Database("capteur_multi_pollutions", "WrongUser", "Sensor", "192.168.2.118", 4071, self.log)
            db.connection()

    def test_connection_wrong_address(self):
        with self.assertRaises(RuntimeError):
            db = Database("capteur_multi_pollutions", "Sensor", "Sensor", "000.010.1.213", 4071, self.log)
            db.connection()

class testDBFunctions(unittest.TestCase):
    
    def setUp(self):
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
        self.log = logging.getLogger()
        self.log.setLevel("DEBUG")
        self.log.addHandler(handler)
        self.db = Database("capteur_multi_pollutions", "Sensor", "Sensor", "192.168.2.118", 4071, self.log)
        self.db.connection()

    def tearDown(self):
        self.db.disconnection()

    def test_id(self):
        pollutants = ["pm25"]
        units = ["µg/m^3"]
        self.assertEqual(self.db.get_ids("SDS011", pollutants, units)["pm25"], 2)

    def test_id_insert(self):
        pollutants = ["pollutantTest"]
        units = ["unitTest"]
        self.assertEqual(self.db.get_ids("SensorTest", pollutants, units)["pollutantTest"], 5)

    # def test_insert_data(self):
