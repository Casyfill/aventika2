#!/usr/bin/env python
# -*- coding: utf-8 -*-

# zip results.csv and preporcessed banks,
# creating a final version of the geojson
# with all scores and priorities

import os
import glob
import time
import operator
import json
import pandas as pd
import codecs
import geopandas as gp
from geopandas.tools import sjoin
from datetime import datetime
from pandas.util.testing import isiterable
from sys import argv
import random
from qa import quality_assurance, quality_assurance_features


PATH = '../data/{city}/{p}/{f}'


INDEXER = {'MSC': 0,
           'SPB': 10000,
           'KZN': 20000,
           'EKB': 30000}


def _classify2(scores):
    m = scores.max()

    d = {'high': .75 * m,
         'above-average': .5 * m,
         'below-average': .25 * m,
         'low': 0
         }

    print(d)
    return d


def get_last_result(city):
    '''return youngest calculated result
     as a dataframe
    '''
    # files = glob.glob(result_path + '*.csv')
    # file = get_youngest_file(files)
    result_atm_path = PATH.format(city=city,
                                  p='results',
                                  f='atm_results.csv')

    result_office_path = PATH.format(city=city,
                                     p='results',
                                     f='office_results.csv')

    print('loading atms: {}'.format(result_atm_path))
    print('loading offices: {}'.format(result_office_path))

    result_atm = pd.read_csv(result_atm_path)
    result_bank = pd.read_csv(result_office_path)
    result = pd.concat([result_atm, result_bank])
    print('In total {} banks with scores loaded'.format(len(result)))
    result['reg_score'].fillna(0, inplace=1)
    result['raw_score'] = result['score'].astype(float).round(2)

    result['score'] = (100 * result['score'] / result['score'].max())
    result.loc[(result['raw_score'] != 0) & (
        result['score'] == 0), 'score'] = 1

    result['score'] = result['score'].round(2)
    result['reg_score'] = result['reg_score'].round(2)

    labels = ['low', 'below-average', 'above-average', 'high']
    result['label'] = pd.cut(result['score'], bins=len(labels), labels=labels)

    for col in ('s_pois', 'f_pois'):
        result.loc[pd.notnull(result[col]), col] = result.loc[pd.notnull(
            result[col]), col].str.split('|').apply(lambda x: [int(i) for i in x])
        result.loc[pd.isnull(result[col]), col] = result.loc[
            pd.isnull(result[col]), col].apply(lambda x: [])

    result['pois'] = result.apply(lambda x: x['f_pois'] + x['s_pois'], 1)

    return result.set_index('office_id')


def get_banks(city):
    # banks = gp.read_file(banks_path)
    # banks['score'] = 0
    # return banks.set_index('office_id')

    banks_path = PATH.format(city=city,
                             p='processed',
                             f='banksdummy.geojson')

    print('loading banks: {}'.format(banks_path))
    # with codecs.open(banks_path.format('atm'), 'r') as f:
    #     banks1 = json.load(f)

    # with codecs.open(banks_path.format('office'), 'r') as f:
    #     banks2 = json.load(f)

    # banks1['features'].extend(banks2['features'])
    with open(banks_path, 'r') as f:
        banks = json.load(f)

    typereplace = {'atm': 'Банкомат',
                   'office': 'Отделение'}
    for bank in banks['features']:
        bank['properties']['type'] = typereplace[bank['properties']['type']]

    return banks


def get_pois(city):

    pois_path = PATH.format(city=city,
                            p='processed',
                            f='poi.geojson')

    print('loading pois: {}'.format(pois_path))
    r = gp.read_file(pois_path)
    # print r['pid'].dtype
    r['pid'] = r['pid'].astype(int)
    return r.set_index('pid')


def getLabels(city, result):
    banks_path = PATH.format(city=city,
                             p='processed',
                             f='banks.geojson')

    b2 = gp.read_pickle(banks_path).set_index('office_id')
    b2["idxColor"] = _classify(result, b2)
    return b2


def uset(l):
    if isiterable(l):
        return list(set(l))


def get_disabilities(pids, pois):
    try:
        if not isinstance(pids, list):
            return ['general']
        else:
            r = [x for x in pois.loc[pids, 'disability'].unique().tolist() if not any([(x is None), pd.isnull(x)])] 
            if len(r) == 0:
                r = ['general']
            return r
    except Exception as inst:
        raise Exception(type(pids), inst)

def main(city):
    banks = get_banks(city)
    result = get_last_result(city)
    pois = get_pois(city)
    CITY_INDEX = INDEXER[city]

    blabels = _classify2(result['score'])

    cntr = 0
    for b in banks['features']:
        bid = b['properties']['office_id']  # GET ID

        b['properties']['office_id'] = bid + \
            CITY_INDEX  # make office id unique

        if bid in result.index:
            score = result.loc[bid, 'score']

            b['properties']['score'] = float(str(score))
            b['properties']['raw_score'] = float(
                str(result.loc[bid, 'raw_score']))
            b['properties']['reg_score'] = float(
                str(result.loc[bid, 'reg_score']))
            b['properties']['pois'] = [
                x + CITY_INDEX for x in list(set(result.loc[bid, 'pois']))]
            b['properties']['priority'] = int(result.loc[bid, 'priority'])

            d = get_disabilities(result.loc[bid, 'pois'], pois)

            b['properties']["disability"] = d
            b['properties']['idxColor'] = result.loc[bid, 'label']

        else:
            print('bid not found, inferring: ', bid)
            cntr += 1
            b['properties']['score'] = 0
            b['properties']['idxColor'] = 'low'
            b['properties']['priority'] = -1

    print('Total inferred offices: {}'.format(cntr))

    result_csv_path = PATH.format(city=city,
                                  p='results',
                                  f='{}_scored_banks.xlsx'.format(city))

    result_path = PATH.format(city=city,
                              p='results',
                              f='{}_scored_banks.geojson'.format(city))

    quality_assurance_features(banks, mode='bank')

    with open(result_path, 'w') as f:
        json.dump(banks, f)
        print('Storing at: {}'.format(result_path))

    # gp.read_file(result_path).drop(
    #     'geometry', axis=1).to_excel(result_csv_path)

    # now index buffers
    buffs_path = PATH.format(city=city,
                             p='processed',
                             f='buffers_all3.geojson')
    buffs = gp.read_file(buffs_path)
    buffs['office_id'] += CITY_INDEX

    with open(PATH.format(city=city,p='results', f='buffers.geojson'), 'w') as f:
        f.write(buffs.to_json())
    print('Done! Stored')

    #POI
    poi_path = PATH.format(city=city,
                             p='processed',
                             f='poi.geojson')
    poi = gp.read_file(poi_path)
    poi['pid'] += CITY_INDEX

    with open(PATH.format(city=city,p='results', f='poi.geojson'), 'w') as f:
        f.write(poi.to_json())
    print('Done! Stored')


if __name__ == '__main__':
    if len(argv) > 1:
        city = argv[1]
    else:
        city = 'SPB'

    main(city)
