import unittest
import logging
import sys

from SDS011 import SDS011
from Database import Database

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
log = logging.getLogger()
log.setLevel("DEBUG")
log.addHandler(handler)


class Test_SDS011_setup(unittest.TestCase):

    def setUp(self):
        self.db = Database("capteur_multi_pollutions", "Sensor",
                           "Sensor", "192.168.2.118", 4071, log)
        self.db.connection()

    def tearDown(self):
        self.db.disconnection()

    def test_SDS011_setup(self):
        capteur = SDS011(self.db, log)
        capteur.setup(port="/dev/ttyUSB0")
        r = capteur._read_data()
        self.assertIn(b'\xAA', r)
        self.assertIn(b'\xC0', r)
        self.assertIn(b'\xAB', r)
        capteur.close()

    def test_SDS011_setup_wrong_dev(self):
        with self.assertRaises(RuntimeError):
            capteur = SDS011(self.db, log)
            capteur.setup(port="/dev/ttyUSB1")

    def test_SDS011_read(self):
        capteur = SDS011(self.db, log)
        capteur.setup(port="/dev/ttyUSB0")
        capteur.read()
        self.assertEqual(type(capteur.vals[1]), float)
        self.assertEqual(type(capteur.vals[2]), float)
        self.assertTrue(capteur.vals[1] > 0 and capteur.vals[1]
                        < 200 and capteur.vals[2] > 0 and capteur.vals[2] < 200)
