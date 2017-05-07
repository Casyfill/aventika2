#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import geopandas as gp
import pandas as pd
from sys import argv
# import json
from shapely.geometry import Polygon
from glob import glob
import re
import time
import cPickle as pickle

COUNTER = 1
BASE = "http://galton.urbica.co/{city}/{type}/"

CITIES = {'KZN': "kazan",
          'EKB': "yekaterinburg",
          'MSC': "moscow",
          'SPB': "saint_petersburg"}

# CITIES = ("amsterdam_netherlands",
#         "barcelona_spain",
#         "beijing_china",
#         "berlin_germany",
#         "moscow",
#         "saint-petersburg",
#         "kazan",
#         "yekaterinburg"
#         "kyiv_ukraine",
#         "madrid_spain",
#         "london_england",
#         "new-york_new-york",
#         "paris_france",
#         "prague_czech-republic",
#         "san-francisco_california")

TYPES = ('foot', 'stepless')  # 'car',
TOLERANCE = .001
# CITY = CITIES[4]


def getIsochrone(point, type, city="moscow_russia", concat=2, intrvl=5):
    '''get isochrone curve

    return isochrone curve geometry

    '''
    burl = BASE.format(type=type, city=city)
    # print burl
    r = requests.get(burl, params={'lng': point[0],
                                   "lat": point[1],
                                   'intervals[]': intrvl,
                                   'concavity': concat})
    # if r.status_code != 200:
    # print r.url
    r.raise_for_status()
    print '!'

    p = Polygon(r.json()['features'][0]['geometry']['coordinates'][0])
    global TOLERANCE
    time.sleep(.5)
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


def _bufferize(p, concat, city):
    '''fenerate 3 buffers for point'''
    global TYPES, CITIES, COUNTER

    intrvls = {'foot': 10, "car": 10, 'stepless': 8}

    print '{0}. Getting buffer for: {1}, {2}'.format(COUNTER, p.geometry.x, p.geometry.y)

    triple = [{'office_id': p.office_id,
               'type': tp,
               'geometry': getIsochrone((p.geometry.x, p.geometry.y),
                                        tp, city=CITIES[city], intrvl=intrvls[tp], concat=concat)
               } for tp in TYPES]

    COUNTER += 1

    try:  # ensure stepless is smaller or equal to foot
        triple[2]['geometry'] = triple[2][
            'geometry'].intersection(triple[1]['geometry'])
    except Exception:
        pass

    return triple


def process_points(points, concat=3, city='MSC'):
    '''get 2 buffers for each point'''
    buffers = []

    points.apply(lambda p: buffers.extend(
        _bufferize(p, concat=concat, city=city)), 1)
    buffs = gp.GeoDataFrame(pd.DataFrame(buffers))
    buffs['priority'] = None
    print(buffs.loc[pd.isnull(buffs['geometry']),'office_id'])
    print(buffs.loc[buffs.is_empty,'office_id'])

    return buffs


def get_buffers(points, concat, city):
    buffs = process_points(points, concat=concat, city=city)
    return buffs[pd.notnull(buffs['geometry'])]


def main(city):
    folder = '../data/{}/raw'.format(city)
    paths = _get_paths(folder)
    points = _prepare(paths)

    proc_folder = '/'.join(paths[0].split('/')[:-2] + ['processed'])

    with open(proc_folder + '/banksdummy.geojson', 'w') as f:
        f.write(points.to_json())

    buffs = process_points(points[['geometry', 'type', 'office_id']],
                           concat=3,
                           city=city)

    with open('../data/{c}/processed/buffers.pkl'.format(c=city), 'wb') as f:
        pickle.dump(buffs, f)

    issues = pd.isnull(buffs['geometry']).sum()
    issues += buffs.is_empty.sum()

    buffs = buffs[pd.notnull(buffs['geometry'])]
    buffs = buffs[~ buffs.is_empty]
    

    print '{} Empty buffers filtered'.format(issues)
    pc = proc_folder + '/buffers.geojson'
    with open(pc, 'w') as f:
        f.write(buffs.to_json())

    print 'Done! Generated buffers for {0} points to: {1}'.format(len(buffs) / 3, pc)


def _prepare(paths):
    banks = []
    for path in paths:
        points = gp.read_file(path) #[['geometry']]
        points['type'] = re.findall(r"[^_]+(?=\.geojson)", path)[0]
        banks.append(points)

    points = pd.concat(banks).reset_index(drop=True)
    points['office_id'] = points.index + 1
    return points


def _get_paths(folder):
    '''get office files in folder'''
    r = glob(folder + '/bank_*.geojson')
    print[x.split('/')[-1] for x in r]
    assert(len(r) == 2)
    return r


if __name__ == '__main__':
    if len(argv) > 1:
        city = argv[1]
    else:
        city = 'SPB'
    main(city)