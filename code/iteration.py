#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
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

    buff, poi, reg, reg_centroids = prepare(buff, poi, reg)

    # buffers of newly adopted offices will be added here iteratively
    bound = settings['limit']
    logger = settings['logger']
    COVERED = {'foot': None, 'stepless': None}
    logger.info('Started iteration')

    while True:
        if bound is not None:  # check if we're over the LIMIT
            if cntr > bound:
                break

        logger.info(log_pois_string.format(i=cntr, n=len(poi)))

        bid, score, reg_score, f_pois, s_pois = iteration(cntr, buff, poi,
                                                          reg, settings)

        # update information
        buff, poi, region, COVERED = update_data(buff, poi, region,
                                                 bid, s_pois, COVERED)

        logger.info(
            '{i}: After iteration, pois: {n}'.format(i=cntr, n=len(poi)))

        if math.isnan(bid) or bid is None:
            break
        else:
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
        return None, None, None, None

    # get Scores
    poi_score, poi_counted = getPoiScore(buff, poi, settings)
    reg_score = getRegScore(buff, reg, settings)

    bid, score = agg_results(poi_score, reg_score, get_max=True)

    if bid is None or math.isnan(bid):
        logger.info('Iteration complete, none unassigned banks')
        return None, None, None, None

    foot_pois = poi_counted.loc[bid, 'foot_poi']
    stepless_pois = poi_counted.loc[bid, 'stepless_poi']

    print reg_score, bid
    try:
        reg_score.iloc[bid]  # get reg_score for chosen object

        logger.info(priority_string.format(i, bid, score))

        return bid, score, r_score, foot_pois, stepless_pois
    except:
        return reg_score, bid


# Aggregation
def agg_results(p=None, r=None, get_max=True):
    '''summs results from POI and regions'''
    if p is None and r is None:
        raise IOError('No information at all')
    elif p is None:
        result = r
    elif r is None:
        result = p
    else:
        result = p + r

    if len(result['score']) == 0:
        return None, None

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


def writerow(row, filename, header):
    with open(filename, 'a') as csvfile:
        fieldnames = row.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if header:
            writer.writeheader()
        writer.writerow(row)
