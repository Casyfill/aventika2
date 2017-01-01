import unittest
import pandas as pd
import geopandas as gp
import logging
# from code.iteration import iterate, iteration, update_data
# from code.misc.logger import getLogger
# from code.misc.preparation import prepare
# from code.misc import *

class TestDataMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        from code.main import getSettings
        from code.misc.logger import getLogger
        self.settings = getSettings(path='settings.json')
        logging.disable(logging.CRITICAL)

    def test_preload(self):
    	from code.main import data_preload

        self.settings['bank_mode'] = 'office'
        poi, buff, reg = data_preload(self.settings, source='test_path')
        self.assertTrue(isinstance(poi, pd.DataFrame))
        self.assertTrue(isinstance(buff, pd.DataFrame))
        self.assertTrue(isinstance(reg, pd.DataFrame))


    def test_data_quality(self):
    	from code.main import data_preload

        self.settings['bank_mode'] = 'office'
        poi, buff, reg = data_preload(self.settings, source='test_path')
        self.assertFalse(poi['fs'].any())
        self.assertFalse(reg['fs'].any())
   

    def test_data_preload(self):
        from code.main import data_preload

        self.settings['bank_mode'] = 'office'
        x, buff, y = data_preload(self.settings, source='test_path')
        self.assertTrue(len(buff) == 4)

        self.settings['bank_mode'] = 'atm'
        x, buff, y = data_preload(self.settings, source='test_path')
        self.assertTrue(len(buff) == 2)

        self.settings['bank_mode'] = 'something_else'
        with self.assertRaises(IOError):
            x, buff, y = data_preload(self.settings, source='test_path')


    def test_poi_attributes(self):
    	from code.main import data_preload

        self.settings['bank_mode'] = 'office'
        poi, _, _ = data_preload(self.settings, source='test_path')

        self.assertFalse(poi['fs'].any())
        for c in ('pid', 'score', 'fs', 'disability'):
        	self.assertTrue(c in poi.columns)

    def test_reg_attributes(self):
    	from code.main import data_preload

        self.settings['bank_mode'] = 'office'
        _, _, reg = data_preload(self.settings, source='test_path')

        self.assertFalse(reg['fs'].any())
        for c in ('reg_id', 'score', 'fs'):
        	self.assertTrue(c in reg.columns)

        
suite = unittest.TestLoader().loadTestsFromTestCase(TestDataMethods)
unittest.TextTestRunner(verbosity=2).run(suite)