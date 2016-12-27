#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import cPickle
# import geopandas as gp
import math
# from shapely.ops import cascaded_union
import csv
from misc import *
from misc.logger import log_row_string, log_pois_string

idx = pd.IndexSlice
BANKS = []

priority_string = 'Priority {0}: bank office {1}, score: {2}'


# ITERATION
def iterate(buff, poi, reg, filename, settings):
    '''traverse through banks
    '''
    cntr = 1  # iteration counter

    # buffers of newly adopted offices will be added here iteratively
    bound = settings['limit']
    logger = settings['logger']
    logger.info('Started iteration')

    while True:
        if bound is not None:  # check if we're over the LIMIT
            if cntr > bound:
                break

        logger.info(log_pois_string.format(i=cntr, n=len(poi)))

        bid, score, reg_score, f_pois, s_pois = iteration(cntr, buff, poi,
                                                          reg, settings)

        # update information
        
        row = {'priority': cntr,
               'office_id': bid,
               'score': score,
               'reg_score': reg_score,
               'f_pois': '|'.join([str(x) for x in f_pois]),
               's_pois': '|'.join([str(x) for x in s_pois])
               }

        writerow(row, filename, cntr < 2)
        logger.info(log_row_string.format(
            i=cntr, bid=row['office_id'], s=row['score']))
        cntr += 1
        
        if score and score > 0:
            buff, poi = update_data(buff, poi, bid, s_pois)
            if buff is None:
                return None
                
            with open('../data/dumps/dump.pkl', 'wb') as f:
                cPickle.dump({'buff':buff, 'poi':poi}, f)
        else:
            return None

    return None


def iteration(i, buff, poi, reg, settings):
    '''iteration step.
    As a result, next prioritized bank office is selected,
    prioritization is added to the buff priority column.

    Args:
        i(int): index of iteration
        buff(gp.GeoDataFrame): current bank offices buffers
        poi(gp.GeoDataFrame): dataframe of POI's
        reg(gp.GeoDataFrame): dataframe of rayons
        mode(str): mode, a-all, p-only poi, r - only regions
    Returns:
        tuple: (buff, bid, score) - updated buffers,
                office with max score, it's score
    '''

    # print 'Iteration N{}. banks left:{}'.format(i,
    # sum(pd.isnull(buff['priority']))/3)

    logger = settings['logger']

    if sum(pd.isnull(buff['priority'])) == 0:
        logger.info('none unassigned banks, Iteration complete')
        return None, None, None, [], []

    # get Scores
    buff = buff[pd.notnull(buff['geometry'])]
    buff = buff[~buff.geometry.is_empty]

    poi_score, poi_counted = getPoiScore(buff, poi, settings)
    reg_score = getReg_overlayed(buff, reg, settings)
    # print reg_score
    bid, score = agg_results(poi_score, reg_score, logger, get_max=True)
    # print 'BID:', bid
    if bid is None or math.isnan(bid):
        if len(buff.index.get_level_values(1).unique()) == 1:
            return buff.index.get_level_values(1).tolist()[0], None, None, [], []
        else:
            logger.info('Iteration complete, none unassigned banks')
            return None, None, None, [], []

    try:
        foot_pois = poi_counted.loc[bid, 'foot_poi']
        if type(foot_pois) != list:
            foot_pois = []
    except:
        foot_pois = []

    try:
        stepless_pois = poi_counted.loc[bid, 'stepless_poi']
        if type(stepless_pois) != list:
            stepless_pois = []

    except:
        stepless_pois = []

    try:
        r_score = reg_score.loc[bid].iloc[0]  # get reg_score for chosen object
    except:
        r_score = None

    logger.info(priority_string.format(i, bid, score))


    return bid, score, r_score, foot_pois, stepless_pois


# Aggregation
def agg_results(p=None, r=None, logger=None, get_max=True):
    '''summs results from POI and regions'''
    if any( [(p is None and r is None),(p.empty and r.empty)]):
        raise IOError('No information at all')
    elif p is None or p.empty:
        
        logger.info('no poi score')
        result = r
    elif r is None or r.empty:
        
        logger.info('no regions score')
        result = p
    else:
        tmp = pd.DataFrame({'reg_score':r['score'],
                            'poi_score':p['score']})
        
        tmp['score'] = tmp.sum(1)
        result = tmp[['score']]

    if len(result['score']) == 0:
        return None, None
    print 'result:', p, r, result
    return result['score'].argmax(), result['score'].max()


def update_data(buff, poi, bid, s_pois):
    '''update dataset with regard to the newly chosen office

    Args:
        buff: current set of buffers
        poi: current set of points
        bid: selected office's office_id
        s_pois: selected pois
    '''
    buff = update_buff(buff, bid)

    poi = poi[~poi['pid'].isin(s_pois)]  # remove stepless pois

    return buff, poi


def writerow(row, filename, header):
    with open(filename, 'a') as csvfile:
        fieldnames = row.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if header:
            writer.writeheader()
        writer.writerow(row)
