
import os
import sys
from shapely.geometry import Polygon
import pandas as pd
import unittest
sys.path.append(os.path.abspath(os.path.join('../src')))
from data_fetcher import DataFetcher
# sys.path.append(os.path.abspath(os.path.join('../data')))



class DataFetcherTest(unittest.TestCase):
    def setUp(self) -> None:
        MINX, MINY, MAXX, MAXY = [-93.756155, 41.918015, -93.747334, 41.921429]
        polygon = Polygon(((MINX, MINY), (MINX, MAXY),
                           (MAXX, MAXY), (MAXX, MINY), (MINX, MINY)))

        self.df = DataFetcher(
            polygon=polygon, region="IA_FullState", epsg="4326")


    def test_check_region(self):
        self.assertEqual('IA_FullState', self.df.check_region('IA_FullState'))


if __name__ == "__main__":
    unittest.main()
