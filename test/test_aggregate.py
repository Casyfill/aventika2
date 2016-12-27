import unittest
import pandas as pd

class TestAggregateMethods(unittest.TestCase):

    def test_aggregate_assim(self):
        from code.iteration import agg_results

        p = pd.DataFrame({'score':[1,2,3,4]})
        r = pd.DataFrame({'score':[1,2,3]})
        self.assertEqual(agg_results(p, r), (2,6))

    def test_aggregate_rNone(self):
        from code.iteration import agg_results

        p = pd.DataFrame({'score':[1,2,3,4]})
        r = None
        self.assertEqual(agg_results(p, r), (3,4))

    def test_aggregate_pNone(self):
        from code.iteration import agg_results

        p = None
        r = pd.DataFrame({'score':[1,2,3,4]})
        self.assertEqual(agg_results(p, r), (3,4))

    def test_aggregate_pEmpty(self):
        from code.iteration import agg_results

        p = pd.DataFrame({'score':[]})
        r = pd.DataFrame({'score':[1,2,3,4]})
        self.assertEqual(agg_results(p, r), (3,4))

    def test_aggregate_allEmpty(self):
        from code.iteration import agg_results

        p = pd.DataFrame({'score':[]})
        r = pd.DataFrame({'score':[]})
        
        with self.assertRaises(IOError):
            agg_results(p, r)

    def test_aggregate_allNone(self):
        from code.iteration import agg_results

        p = None
        r = None
        
        with self.assertRaises(IOError):
            agg_results(p, r)
    

suite = unittest.TestLoader().loadTestsFromTestCase(TestAggregateMethods)
unittest.TextTestRunner(verbosity=2).run(suite)