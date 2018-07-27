import logging
import sys
import unittest
import datetime
from decimal import Decimal

from Database import Database
from SDS011 import SDS011


class Test_SDS011_setup(unittest.TestCase):
    
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    log = logging.getLogger()
    log.setLevel("DEBUG")
    log.addHandler(handler)
    
    def setUp(self):
        self.db = Database("capteur_multi_pollutions", "Sensor",
                           "Sensor", "192.168.2.118", 4071, self.log)
        self.db.connection()

    def tearDown(self):
        self.db.disconnection()

    def test_SDS011_setup(self):
        capteur = SDS011(self.db, self.log)
        capteur.setup(dev="/dev/ttyUSB0")
        r = capteur._read_data()
        self.assertIn(b'\xAA', r)
        self.assertIn(b'\xC0', r)
        self.assertIn(b'\xAB', r)
        capteur.close()

    def test_SDS011_setup_wrong_dev(self):
        with self.assertRaises(RuntimeError):
            capteur = SDS011(self.db, self.log)
            capteur.setup(dev="/dev/ttyUSB1")

    def test_SDS011_read(self):
        capteur = SDS011(self.db, self.log)
        capteur.setup(dev="/dev/ttyUSB0")
        capteur.read()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(type(capteur.vals[0][1]), float)
        self.assertEqual(type(capteur.vals[0][2]), float)
        self.assertIn(now, capteur.vals[0][0])
        self.assertTrue(capteur.vals[0][1] > 0 and capteur.vals[0][1]
                        < 200 and capteur.vals[0][2] > 0 and capteur.vals[0][2] < 200)

    def test_SDS011_insertion(self):
        capteur = SDS011(self.db, self.log)
        capteur.setup(dev="/dev/ttyUSB0")
        mock = [['2018-07-04 17:01:14', 1.0, 2.0]]
        query = "SELECT * FROM AVG_HOUR WHERE date = \"{}\"".format(mock[0][0])

        capteur.vals = mock
        capteur.insert()

        expected_result = [
            {'systemId': 'testId', 'value': Decimal('2.00'),
             'date': datetime.datetime(2018, 7, 4, 17, 1, 14), 'typeId': 1},
            {'systemId': 'testId', 'value': Decimal('1.00'),
             'date': datetime.datetime(2018, 7, 4, 17, 1, 14), 'typeId': 2}]

        self.assertEqual(len(capteur.vals), 0)
        self.db.cursor.execute(query)
        self.assertEqual(self.db.cursor.fetchall(), expected_result)
