#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
import os
from get_buffers import get_buffers
from sys import argv
import geopandas as gp
import pandas as pd
import re
import codecs
import json

settings = {'concat': 4,
            'base': '../data/{city}/'}


def _get_paths(folder):
    '''get office files in folder'''
    r = glob(folder + '/bank_*.geojson')
    print[x.split('/')[-1] for x in r]
    assert(len(r) == 2)
    return r


def get_bank_dummy(path):
    paths = _get_paths(path + 'raw')  # get bank files

    banks = None
    for p in paths:
        with codecs.open(p, 'r', encoding="utf-8") as f:
            b = json.load(f)

        tp = re.findall(r"[^_]+(?=\.geojson)", p)[0]
        for el in b['features']:
            el['properties']['type'] = tp

    if banks is None:
        banks = b
    else:
        banks['features'].extend(b['features'])

    # points = pd.concat(banks).reset_index(drop=True)

    for i, el in enumerate(b['features']):
            el['properties']['office_id'] = i + 1

    with codecs.open(path + 'processed/banksdummy.geojson', 'w') as f:
        json.dump(banks, f, ensure_ascii=False)
        # f.write(points.to_json())


def get_all_buffers(path, concat, city):

    points = gp.read_file(path + 'processed/banksdummy.geojson')

    for tp in ('atm',):
        b = get_buffers(points[points['type'] == tp], concat, city)
        with open(path + 'processed/buffers_{}.geojson'.format(tp), 'w') as f:
            f.write(b.to_json())

# def get_pois(path)


def main(city):
    path = settings['base'].format(city=city)
    if not os.path.exists(path):
        raise IOError('No such directory: {}'.format(path))

    get_bank_dummy(path)
    # get_all_buffers(path, concat=settings['concat'], city=city)
    # get_pois(path)


if __name__ == '__main__':
    if len(argv) > 1:
        city = argv[1]
    else:
        city = 'SPB'

    main(city)
