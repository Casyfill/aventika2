import unittest
import pandas as pd
import geopandas as gp
import logging


class TestRegMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        from code.main import data_preload, getSettings
        from code.misc.logger import getLogger
        self.settings = getSettings(path='settings.json')
        
        self.poi, self.buff, self.reg = data_preload(self.settings, source='data_path')
        logging.disable(logging.CRITICAL)


# suite = unittest.TestLoader().loadTestsFromTestCase(TestRegMethods)
# unittest.TextTestRunner(verbosity=2).run(suite)