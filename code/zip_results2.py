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
from sys import argv
import random

PATH = '../data/{city}/{p}/{f}'


def _classify2(scores):
	m = scores.max()

	d = {'high': .75 * m,
	 		'above-average': .5 * m ,
	 		'below-average': .25 * m,
	 		'low': 0
			}

	print d
	return  d


def get_last_result(city):
	'''return youngest calculated result
	 as a dataframe
	'''
	# files = glob.glob(result_path + '*.csv')
	# file = get_youngest_file(files)
	result_atm_path = PATH.format(city=city, 
								  p='results',
								  f='1_atm_results.csv')

	result_office_path = PATH.format(city=city, 
								  p='results',
								  f='1_office_results.csv')
	

	print('loading atms: {}'.format(result_atm_path))
	print('loading offices: {}'.format(result_office_path))

	result_atm = pd.read_csv(result_atm_path)
	result_bank = pd.read_csv(result_office_path)
	result = pd.concat([result_atm, result_bank])

	result['reg_score'].fillna(0, inplace=1)
	result['raw_score'] = result['score'].round(2)
	
	result['score'] = (100 * result['score'] / result['score'].max())
	result.loc[(result['raw_score']!=0) & (result['score']==0),'score'] = 1
	
	result['score'] = result['score'].round(2)
	result['reg_score'] = result['reg_score'].round(2)

	labels = ['low', 'below-average', 'above-average', 'high']
	result['label'] = pd.cut(result['score'], bins=len(labels), labels = labels)

	for col in ('s_pois', 'f_pois'):
		result.loc[ pd.notnull(result[col]), col] = result.loc[ pd.notnull(result[col]), col].str.split('|').apply(lambda x: [int(i) for i in x])
		result.loc[ pd.isnull(result[col]), col] = result.loc[ pd.isnull(result[col]), col].apply(lambda x: [])
	
	result['pois'] = result.apply(lambda x: x['f_pois'] + x['s_pois'], 1)
	
	return result.set_index('office_id')

def get_banks(city):
	# banks = gp.read_file(banks_path)
	# banks['score'] = 0
	# return banks.set_index('office_id')

	banks_path = PATH.format(city=city, 
							 p='out',
							 f='banks.geojson')

	print('loading banks: {}'.format(banks_path))


	with codecs.open(banks_path, 'r', encoding='utf-8') as f:
		banks = json.load(f)
		return banks


def get_pois(city):

	pois_path = PATH.format(city=city, 
			                p='out',
			                f='poi.geojson')

	print('loading pois: {}'.format(pois_path))
	r = gp.read_file(pois_path)
	# print r['pid'].dtype
	r['pid'] = r['pid'].astype(int)
	return r.set_index('pid')


def getLabels(city, result):
	banks_path = PATH.format(city=city, 
							 p='out',
							 f='banks.geojson')

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


def main(city):
	banks = get_banks(city)
	result = get_last_result(city)
	pois = get_pois(city)
	print 'loaded everything'

	# blabels = _classify2(result['score'])

	cntr = 0
	for b in banks['features']:
		bid = b['properties']['office_id'] # GET ID


		if bid in result.index:
			score = result.loc[bid, 'score']

			b['properties']['score'] = float(str(score))
			b['properties']['raw_score'] = float(str(result.loc[bid, 'raw_score']))
			b['properties']['reg_score'] = float(str(result.loc[bid, 'reg_score']))
			b['properties']['pois'] = list(set(result.loc[bid, 'pois']))
			b['properties']['priority'] = result.loc[bid, 'priority']

			d = get_disabilities(result.loc[bid, 'pois'], pois)
			
			b['properties']["disability"] = d
			b['properties']['idxColor'] = result.loc[bid, 'label']

		else:
			print 'bid not found, inferring: ', bid 
			cntr+=1
			b['properties']['score'] = 0
			b['properties']['idxColor'] = 'low'
			b['properties']['priority'] = -1

	print 'Total inferred offices: {}'.format(cntr)

	result_csv_path = PATH.format(city=city,
							  p='out',
							  f='scored_banks.xlsx')
	

	result_path = PATH.format(city=city,
							  p='out',
							  f='scored_banks.geojson')
	print 'Storing at: {}'.format(result_path)

	with codecs.open(result_path, 'w', encoding="utf-8") as f:
		json.dump(banks, f, ensure_ascii=False)

	gp.read_file(result_path).drop('geometry', axis=1).to_excel(result_csv_path)
	print('Done! Stored')



	



if __name__ == '__main__':
	if len(argv)>1:
		city = argv[1]
	else:
		city = 'MSC'

	main(city)

