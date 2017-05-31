#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from get_buffers import get_buffers
from sys import argv
import geopandas as gp
import pandas as pd
import re
import codecs
import json
from qa import quality_assurance, quality_assurance_features
from misc import _get_paths

settings = {'concat': 4,
            'base': '../data/{city}/'}


DUMMY_PROPERTIES = {"info": None,
                    "sound": None,
                    "us_disabled": None,
                    "vis_rasmetka": None,
                    "us_visual": None,
                    "pandus": None,
                    "shop_intersect": None,
                    "visual": None,
                    "brail": None,
                    "dist_button": None,
                    "vsp": None,
                    "bankomat_adapt": None,
                    "office_id": None,
                    "type": None,
                    "disability": [],
                    "address": None,
                    "name": None,
                    "adapt": 0
                    }


def get_bank_dummy(path):
    paths = _get_paths(path + 'raw')  # get bank files

    banks = None
    for p in paths:
        with open(p, 'r') as f:
            b = json.load(f)

        # add type
        tp = re.findall(r"[^_]+(?=\.geojson)", p)[0]
        assert tp in ('atm', 'office'), "Wrong type of banks:{}".format(tp)
        for el in b['features']:
            el['properties']['type'] = tp  # add type

            for prop, v in DUMMY_PROPERTIES.items():
                if prop not in el['properties'].keys():
                    el['properties'][prop] = v
            el['properties'] = {k: v for k, v in el['properties'].items() if
                                k in DUMMY_PROPERTIES.keys()}

        if banks is None:
            banks = b
        else:
            banks['features'].extend(b['features'])

    # points = pd.concat(banks).reset_index(drop=True)

    # defines generated office id
    for i, el in enumerate(banks['features']):
        el['properties']['office_id'] = i + 1
        el['id'] = i + 1

    # print(banks.keys())
    quality_assurance_features(banks, mode='dummy')

    with open(path + 'processed/banksdummy.geojson', 'w') as f:
        json.dump(banks, f)


def get_all_buffers(path, concat, city):

    points = gp.read_file(path + 'processed/banksdummy.geojson')

    for tp in ('atm',):
        b = get_buffers(points[points['type'] == tp], concat, city)
        with open(path + 'processed/buffers_{}.geojson'.format(tp), 'w') as f:
            f.write(b.to_json())


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
