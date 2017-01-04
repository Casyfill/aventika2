import unittest
import pandas as pd
import geopandas as gp
import logging
from datetime import datetime
import os
# from code.iteration import iterate, iteration, update_data
# from code.misc.logger import getLogger
# from code.misc.preparation import prepare
# from code.misc import *

class TestProcessMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        from code.main import getSettings, data_preload
        from code.misc.logger import getLogger
        self.settings = getSettings(path='settings.json')
        self.settings['bank_mode'] = 'office'
        self.settings['limit'] = None

        self.poi, self.buff, self.reg = data_preload(self.settings, source='test_path')
        
 
        logging.disable(logging.CRITICAL)


    # def test_iteration(self):
    #     from code.iteration import iteration
    #     cntr = 1

    #     bid, score, reg_score, f_pois, s_pois, f_regs, s_regs = iteration(cntr, self.buff, self.poi,
    #                                                       self.reg, self.settings)

    #     # print '{0}:BID {1}'.format(cntr, bid)
    #     reg_k = self.settings['koefficients']['region']
    #     self.assertTrue(bid==1)


    def test_poijoin(self):
        from code.misc.poi import getPOI
        from shapely.geometry import Point
        from geopandas.tools import sjoin
        
        p = self.poi.copy()
        poi_r = sjoin(self.buff.reset_index(), p, how='inner', op='contains')
        self.assertTrue(len(poi_r) == len(self.poi))


    def test_empty_poijoin(self):
        from code.misc.poi import getPOI
        from shapely.geometry import Point
        from geopandas.tools import sjoin
        
        p = self.poi.copy()
        p['geometry'] = pd.Series([Point(-100, -100)]*len(p))

        p = gp.GeoDataFrame(p, crs= self.poi.crs)
        print p
        
        pois = getPOI(self.buff, p, self.settings)
        
        self.assertTrue(pois is None)

        
suite = unittest.TestLoader().loadTestsFromTestCase(TestProcessMethods)
unittest.TextTestRunner(verbosity=2).run(suite)