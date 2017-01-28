#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import geopandas as gp
import pandas as pd
# import json
from shapely.geometry import Polygon


COUNTER = 1
BASE = "http://galton.urbica.co/{city}/{type}/"
CITIES = ("amsterdam_netherlands", 
		  "barcelona_spain", 
		  "beijing_china", 
		  "berlin_germany", 
		  "moscow_russia", 
		  "saint-petersburg_russia",
		  "kyiv_ukraine", 
		  "madrid_spain", 
		  "london_england", 
		  "new-york_new-york", 
		  "paris_france", 
		  "prague_czech-republic", 
		  "san-francisco_california")

TYPES = ('foot', 'stepless') # 'car',
TOLERANCE = .001
CITY = CITIES[4]

def getIsochrone(point, type, city="moscow_russia", concat=3, intrvl=10):
	'''get isochrone curve
	
	return isochrone curve geometry

	'''
	burl = BASE.format(type=type, city=city)
	r = requests.get(burl, params = {'lng':point[0], 
									 "lat":point[1],
									 'intervals[]':intrvl,
									 'concavity':concat})
	
	r.raise_for_status()

	p = Polygon(r.json()['features'][0]['geometry']['coordinates'][0])
	global TOLERANCE

	return p.simplify(TOLERANCE, preserve_topology=False)

	

def ensureStepless(stepless, foot):
	'''ensures stepless is within foot distance
	in other words, get intersection of stepless, foot
	
	Args:
		stepless (shapely.geom.polygon): stepless buffer
		foor (shapely.geom.polygon): foot buffer
	Returns:
		shapely.geom.polygon : intersection
	'''
	return stepless.intersection(foot)


def _bufferize(p, concat):
	'''fenerate 3 buffers for point'''
	global TYPES, CITY, COUNTER

	intrvls = {'foot':10, "car":10, 'stepless':8}
	
	print '{0}. Getting buffer for: {1}, {2}'.format(COUNTER, p.geometry.x, p.geometry.y)
    
	triple = [{'office_id':p.office_id, 
			   'type':tp, 
			   'geometry':getIsochrone((p.geometry.x, p.geometry.y), 
			   							tp, CITY, intrvl=intrvls[tp], concat=concat)
			   } for tp in TYPES]
    
	COUNTER +=1


	try: # ensure stepless is smaller or equal to foot
		triple[2]['geometry'] = triple[2]['geometry'].intersection(triple[1]['geometry'])
	except:
		pass


	return triple


def process_points(points, concat=2):
	'''get 3 buffers for each point'''
	buffers = []
	
	points.apply(lambda p: buffers.extend(_bufferize(p, concat)), 1)
	buffs = gp.GeoDataFrame(pd.DataFrame(buffers))
	buffs['priority'] = None
	
	return buffs



def main():
	
	points = gp.read_file('../data/real/raw/banks.geojson').loc[:, ['geometry', 'office_id', 'type']]
	buffs = process_points(points)
	buffs = buffs[ pd.notnull(buffs['geometry'])]

	path = '../data/real/raw/tuned_buffers.json'
	

	with open(path, 'w') as f:
		f.write(buffs.to_json())
	print 'Done! Generated buffers for {0} points to: {1}'.format(len(buffs)/3, path)


if __name__ == '__main__':
	main()

	