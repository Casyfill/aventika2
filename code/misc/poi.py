#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import geopandas as gp
import pandas as pd
import multiprocessing as mp
from functools import partial
from misc import chunker_eq
from geopandas.tools import sjoin

idx = pd.IndexSlice
POOL = None


def joiner(poi, buff):
    return sjoin(buff, poi, how='inner', op='contains')


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
    global POOL  # global pull of processes
    buff = buff.reset_index()

    partial_joiner = partial(joiner, buff=buff)

    if WORKERS > 1:
        try:
            if POOL is None:
                POOL = mp.Pool(processes=WORKERS)
                settings['logger'].info('   Pool:{} workers'.format(WORKERS))

            poi_chunks = chunker_eq(poi, WORKERS)

            results = POOL.map(partial_joiner, poi_chunks)
            x = pd.concat(results)

        except Exception as inst:
            POOL.close()
            POOL.join()
            raise Exception(inst)

    else:
        x = joiner(poi, buff)

    return x[pd.notnull(x['score'])]


def adjustScore(poi, settings, mode='poi'):
    '''multiply point score by
    correspoinding buffers type coeff

    Return:
        adjusted poi results
    '''
    key = {'poi':'pid', 'reg':'reg_id'}[mode]
    log_string = '{p}: koefficient {k} applied'
    kf = settings['koefficients']
    poic = poi.copy()  # just in case

    for tp in kf.keys():
        poic.loc[poi['type'] == tp, 'score'] *= kf[tp]
        pois = poic.loc[poi['type'] == tp, key].tolist()

        settings['logger'].info(log_string.format(p=pois, k=kf[tp]))

    return poic


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
    x = adjustScore(x, settings, mode='poi')

    # .sort_values('SCORE', ascending=False)
    result_score = x.groupby('office_id').agg({'score': 'sum'})
    result_poi = x.groupby('office_id').agg({'pid': lambda x: list(x)})
    return result_score, result_poi
