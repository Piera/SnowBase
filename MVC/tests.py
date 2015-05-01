from haversine import distance
import geohash
import unittest

class TestGeoModules(unittest.TestCase):

	def test_distance(self):
		seattle = (47.6097, -122.3331)
		paradise_rainier = (46.9153, -121.74)
		self.assertEqual(distance(seattle, paradise_rainier), 89.24660555660384)

	def test_geohash(self):
		self.assertEqual(geohash.encode(47.6097, -122.3331), 'c23nb5pf85m4')
		self.assertEqual(geohash.expand('c23'), ['c22', 'c26', 'c28', 'c29', 'c2d', 'c20', 'c21', 'c24', 'c23'])

if __name__ == '__main__':
    unittest.main()