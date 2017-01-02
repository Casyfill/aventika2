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

class TestDataMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        from code.main import getSettings, data_preload
        from code.misc.logger import getLogger
        self.settings = getSettings(path='settings.json')
        self.settings['bank_mode'] = 'office'
        self.settings['limit'] = None

        self.poi, self.buff, self.reg = data_preload(self.settings, source='test_path')
        
 
        logging.disable(logging.CRITICAL)


    def test_iteration(self):
        from code.iteration import iteration
        cntr = 1

        bid, score, reg_score, f_pois, s_pois, f_regs, s_regs = iteration(cntr, self.buff, self.poi,
                                                          self.reg, self.settings)

        # print '{0}:BID {1}'.format(cntr, bid)
        reg_k = self.settings['koefficients']['region']
        self.assertTrue(bid==1)
        self.assertTrue(reg_score == 1974*reg_k)
        self.assertEqual(score, 3494.0)