#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
import os
from get_buffers import get_buffers
from sys import argv
import geopandas as gp
import pandas as pd
import re

settings = {'concat': 4,
			'base': '../data/{city}/'}


def _get_paths(folder):
	'''get office files in folder'''
	r = glob(folder + '/bank_*.geojson')
	print [x.split('/')[-1] for x in r]
	assert(len(r)==2)
	return r

def get_bank_dummy(path):
	paths = _get_paths(path  + 'raw') # get bank files

	banks = []
	for p in paths:
		points = gp.read_file(p)[['geometry']]
		points['type'] = re.findall(r"[^_]+(?=\.geojson)", p)[0]
		banks.append(points)

	points = pd.concat(banks).reset_index(drop=True)
	points['office_id'] = points.index + 1
	
	with open(path + 'processed/banksdummy.geojson', 'w') as f:
		f.write(points.to_json())


def get_all_buffers(path, concat, city):

	points = gp.read_file(path + 'processed/banksdummy.geojson')

	for tp in ('office', 'atm'):
		b = get_buffers(points[points['type']==tp], concat, city)
		with open(path + 'processed/buffers_{}.geojson'.format(tp), 'w') as f:
			f.write(b.to_json())

# def get_pois(path)

def main(city):
	path = settings['base'].format(city=city)
	if not os.path.exists(path):
		raise IOError('No such directory: {}'.format(path))

	get_bank_dummy(path)
	get_all_buffers(path, concat=settings['concat'], city=city)
	# get_pois(path)


if __name__ == '__main__':
	if len(argv)>1:
		city = argv[1]
	else:
		city = 'MSC'

	main(city)