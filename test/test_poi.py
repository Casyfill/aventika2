import unittest
import pandas as pd
import geopandas as gp
import logging
# from code.iteration import iterate, iteration, update_data
# from code.misc.logger import getLogger
# from code.misc.preparation import prepare
# from code.misc import *

class TestPoiMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        from code.main import data_preload, getSettings
        from code.misc.logger import getLogger
        self.settings = getSettings(path='settings.json')
        
        self.poi, self.buff, self.reg = data_preload(self.settings, source='data_path')
        logging.disable(logging.INFO)

    def test_preload(self):
        self.assertTrue(isinstance(self.poi, pd.DataFrame))
        self.assertTrue(isinstance(self.buff, pd.DataFrame))
        self.assertTrue(isinstance(self.reg, pd.DataFrame))

    def test_data_quality(self):
        self.assertTrue(isinstance(self.poi['score'], pd.Series))
        self.assertTrue(isinstance(self.reg['score'], pd.Series))

    def test_poi_aquisition(self):
    	from code.misc.poi import getPOI
    	new_poi = getPOI(self.buff, self.poi, self.settings)
    	self.assertTrue(len(new_poi[new_poi['type']=='stepless'])==1)

    def test_poi_aquisition2(self):
    	from code.misc.poi import getPOI, adjustScore
    	new_poi = getPOI(self.buff, self.poi, self.settings)
    	new_poi_adj = adjustScore(new_poi, self.settings)

    	foot_r = new_poi.loc[new_poi['type']=='foot', 'score'] == .8 * new_poi_adj.loc[new_poi_adj['type']=='foot', 'score']

    	
    	self.assertTrue(foot_r.all())

    	step_r = new_poi.loc[new_poi['type']=='stepless', 'score'] ==  new_poi_adj.loc[new_poi_adj['type']=='stepless', 'score']

    	self.assertTrue(step_r.all())


suite = unittest.TestLoader().loadTestsFromTestCase(TestPoiMethods)
unittest.TextTestRunner(verbosity=2).run(suite)