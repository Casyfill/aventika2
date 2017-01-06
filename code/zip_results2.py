    #!/usr/bin/env python
# -*- coding: utf-8 -*-

# zip results.csv and preporcessed banks,
# creating a final version of the geojson 
# with all scores and priorities

import os, glob, time, operator
import json
import pandas as pd
import codecs
import geopandas as gp
from geopandas.tools import sjoin
from datetime  import datetime
from pandas.util.testing import isiterable
import random


banks_path = '../data/preprocessed/banks.geojson'
pois_path = '../data/preprocessed/poi.geojson'
result_atm_path = '../data/results/2017_01_03_21:42:32_office_results.csv'
result_office_path = '../data/results/2017_01_04_18:27:08_atm_results.csv'

def get_oldest_file(files, _invert=False):
    """ Find and return the oldest file of input file names.
    Only one wins tie. Values based on time distance from present.
    Use of `_invert` inverts logic to make this a youngest routine,
    to be used more clearly via `get_youngest_file`.
    """
    gt = operator.lt if _invert else operator.gt
    # Check for empty list.
    if not files:
        return None
    # Raw epoch distance.
    now = time.time()
    # Select first as arbitrary sentinel file, storing name and age.
    oldest = files[0], now - os.path.getctime(files[0])
    # Iterate over all remaining files.
    for f in files[1:]:
        age = now - os.path.getctime(f)
        if gt(age, oldest[1]):
            # Set new oldest.
            oldest = f, age
    # Return just the name of oldest file.
    return oldest[0]


def get_youngest_file(files):
    return get_oldest_file(files, _invert=True)


def _classify(results, banks, k=['low', 'below-average', 'above-average', 'high' ] ):
    '''generate fisher_jehks bins
    for specific range'''
    
    # from pysal.esda.mapclassify import Fisher_Jenks as classyfyer
    from pysal.esda.mapclassify import Equal_Interval as classyfyer
    classes = pd.np.array(k)

    banks['score'] = results['score'].fillna(0)

    labels =  classyfyer(banks['score'], k=len(k)).yb
    return classes[labels]


def _classify2(scores, k=['low', 'below-average', 'above-average', 'high' ]):
	m = scores.max()

	return {'hight': .75 * m,
	 		'above-average': .5 * m ,
	 		'below-average': .25 * m,
	 		'low': 0
			}


def get_last_result():
	'''return youngest calculated result
	 as a dataframe
	'''
	# files = glob.glob(result_path + '*.csv')
	# file = get_youngest_file(files)
	
	result_atm = pd.read_csv(result_atm_path)
	result_bank = pd.read_csv(result_office_path)
	result = pd.concat([result_atm, result_bank])

	result['raw_score'] = result['score']
	result['score'] = (100 * result['score'] / result['score'].max()).round(2)

	for col in ('s_pois', 'f_pois'):
		result.loc[ pd.notnull(result[col]), col] = result.loc[ pd.notnull(result[col]), col].str.split('|').apply(lambda x: [int(i) for i in x])
		result.loc[ pd.isnull(result[col]), col] = result.loc[ pd.isnull(result[col]), col].apply(lambda x: [])
	
	result['pois'] = result.apply(lambda x: x['f_pois'] + x['s_pois'], 1)
	
	return result.set_index('office_id')

def get_banks():
	# banks = gp.read_file(banks_path)
	# banks['score'] = 0
	# return banks.set_index('office_id')
	with codecs.open(banks_path, 'r', encoding='utf-8') as f:
		banks = json.load(f)
		return banks

def get_pois():
	r = gp.read_file(pois_path)
	# print r['pid'].dtype
	r['pid'] = r['pid'].astype(int)
	return r.set_index('pid')

def getLabels(result):
	b2 = gp.read_file(banks_path).set_index('office_id')
	b2["idxColor"] = _classify(result, b2)
	return b2

def uset(l):
	if isiterable(l):
		return list(set(l))


def get_disabilities(pids, pois):
	try:
		if not isinstance(pids, list):
			r = ['general']
		elif len(pids) == 1:
			r = pois.loc[pids, 'disability'].iloc[0]
		else:
			r = pois.loc[pids, 'disability'].unique().tolist()

		if len(r)==0:
			r = ['general']
		
		return r
	except Exception as inst:
		print 'pids:', pids
		print inst


def main():
	banks = get_banks()
	result = get_last_result()
	pois = get_pois()
	print 'loaded everything'

	blabels = _classify2(result['score'])

	cntr = 0
	for b in banks['features']:
		bid = b['properties']['office_id'] # GET ID


		if bid in result.index:
			score = result.loc[bid, 'score']

			b['properties']['score'] = score
			b['properties']['raw_score'] = result.loc[bid, 'raw_score']
			b['properties']['reg_score'] = result.loc[bid, 'reg_score']
			b['properties']['pois'] = result.loc[bid, 'pois']
			b['properties']['priority'] = result.loc[bid, 'priority']

			d = get_disabilities(result.loc[bid, 'pois'], pois)
			
			b['properties']["disability"] = d


			if score >= blabels['hight']:
				b['properties']['idxColor'] = 'hight'
			elif score >= blabels['above-average']:
				b['properties']['idxColor'] = 'above-average'
			elif score >= blabels['below-average']:
				b['properties']['idxColor'] = 'below-average'
			else:
				b['properties']['idxColor'] = 'low'



		else:
			print 'bid not found, inferring: ', bid 
			cntr+=1
			b['properties']['score'] = 0
			b['properties']['idxColor'] = random.choice(('below-average', 'low'))
			b['properties']['priority'] = -1

	print 'Total inferred offices: {}'.format(cntr)
	with codecs.open('../data/zipped_banks.geojson', 'w', encoding="utf-8") as f:
		json.dump(banks, f, ensure_ascii=False)
		print('Done! Stored')

	



if __name__ == '__main__':
	main()

