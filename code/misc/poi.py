#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import geopandas as gp
import pandas as pd
import multiprocessing as mp
from functools import partial
from misc import chunker_eq
from geopandas.tools import sjoin
import logging
idx = pd.IndexSlice
LOGGER = logging.getLogger('root')


def joiner(poi, buff):
    try:
        return sjoin(buff, poi, how='inner', op='contains')
    except ValueError:
        return None


def getPOI(buff, poi, settings):
    '''returns  all points within
    the corresponding buffer for each office,
    with the type of the buffer

    Args:
        buff: buffers
        poi: pois
        settings(dict): settings
    return:
        pd.Dataframe
    '''
    WORKERS = settings['mp_settings']['WORKERS']
    pool = settings.get('POOL', None)  # global pull of processes
    buff = buff.reset_index()

    partial_joiner = partial(joiner, buff=buff)

    if WORKERS > 1:
        try:
            if pool is None:
                pool = mp.Pool(processes=WORKERS)
                settings['POOL'] = pool
                LOGGER.info('   Pool:{} workers'.format(WORKERS))

            poi_chunks = chunker_eq(poi, WORKERS)
            results = pool.map(partial_joiner, poi_chunks)

            if all([r is None for r in results]):
                return None

            x = pd.concat(
                [r for r in results if r is not None]).reset_index(drop=True)

        except Exception as inst:
            pool.close()
            pool.join()
            raise Exception(inst)

    else:
        x = joiner(poi, buff)

    if x is not None:
        x.drop_duplicates(subset=['office_id', 'pid'], keep='last')
        # if Bank has poi both as foot and step element, keep only the former
        return x.loc[pd.notnull(x['score']), ['type', 'office_id', 'score', 'pid', 'fs']]
    return None


def adjustScore(poi, settings, mode='poi'):
    '''multiply point score by
    correspoinding buffers type coeff

    Return:
        adjusted poi results
    '''

    key = {'poi': 'pid', 'reg': 'reg_id'}[mode]
    log_string = '{p}: koefficient {k} applied'
    kf = settings['koefficients']

    poic = poi[~((poi['fs']) & (poi['type'] == 'foot'))]  # drop foot-fc

    for tp in kf.keys():
        poic.loc[poic['type'] == tp, 'score'] *= kf[tp]

        pois = poic.loc[poic['type'] == tp, key].tolist()
        # LOGGER.info(log_string.format(p=pois[:5], k=kf[tp]))

    return poic


def get_aquired_pois(pois):
    '''gets three types of pois,
    depending of "aquisition" buffer'''
    stepless_poi = pois[pois['type'] == 'stepless'].groupby(
        'office_id').agg({'pid': lambda x: list(x)}).unstack()
    foot_poi = pois[pois['type'] == 'foot'].groupby(
        'office_id').agg({'pid': lambda x: list(x)}).unstack()

    fc_poi = pois[pois['type'] == 'foot_to_step'].groupby(
        'office_id').agg({'pid': lambda x: list(x)}).unstack()

    pois = pd.DataFrame({'stepless_poi': stepless_poi,
                         'foot_poi': foot_poi,
                         'foot_to_step': fc_poi})

    pois.index = pois.index.get_level_values(1)
    return pois


def getPoiScore(buff, poi, settings):
    '''calculate adjusted POI score for each bank
    and returns both total POI score and POIS corresponding to each bank

    Args:
        buff: buffers
        poi: pois
        settings(dict): settings dict
    Returns:
        tuple: result_score pd.Series, result_poi pd.Series
    '''

    x = getPOI(buff, poi, settings)

    print 'POIS:', len(x), len(x['pid'].unique())
    if not x is None:
        x = adjustScore(x, settings, mode='poi')

        # .sort_values('SCORE', ascending=False)
        result_score = x.groupby('office_id').agg({'score': 'sum'})
        result_poi = get_aquired_pois(x)
        return result_score, result_poi
    else:
        return None, None
