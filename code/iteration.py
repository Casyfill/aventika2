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
import logging
LOGGER = logging.getLogger('root')
    
idx = pd.IndexSlice
BANKS = []

priority_string = 'Priority {0}: bank office {1}, score: {2}'


# ITERATION
def iterate(buff, poi, reg, filename, settings):
    '''traverse through banks
    '''
    cntr = 1  # iteration counter
    global LOGGER

    # buffers of newly adopted offices will be added here iteratively
    bound = settings['limit']
    
    LOGGER.info('Started iteration')

    while True:
        if bound is not None:  # check if we're over the LIMIT
	    print 'STEP:', cntr
            if cntr > bound:
                print 'LIMIT achieved!!!'
                break

        LOGGER.info(log_pois_string.format(i=cntr, n=len(poi)))

        bid, score, reg_score, f_pois, s_pois, f_regs, s_regs = iteration(cntr, buff, poi, reg, settings)

        # update information
        row = {'priority': cntr,
               'office_id': bid,
               'score': score,
               'reg_score': reg_score,
               'f_pois': '|'.join([str(x) for x in f_pois]),
               's_pois': '|'.join([str(x) for x in s_pois])
               }

        writerow(row, filename, cntr < 2)
        
        LOGGER.info(log_row_string.format(
            i=cntr, bid=row['office_id'], s=row['score']))
        cntr += 1
        
        if score and score > 0:
            buff, poi, reg = update_data(buff, poi, reg, bid, s_pois, s_regs, f_pois, f_regs)
            if buff is None:
                return None

            # with open('../data/dumps/dump.pkl', 'wb') as f:
            #     cPickle.dump({'buff':buff, 'poi':poi}, f)
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

    

    if sum(pd.isnull(buff['priority'])) == 0:
        LOGGER.info('none unassigned banks, Iteration complete')
        return None, None, None, [], []

    # get Scores
    buff = buff[pd.notnull(buff['geometry'])]
    buff = buff[~buff.geometry.is_empty]

    poi_score, poi_counted = getPoiScore(buff, poi, settings)
    reg_score, reg_counted = getRegScore(buff, reg, settings)
    # print reg_score
    bid, score = agg_results(poi_score, reg_score, get_max=True)
    # print 'BID:', bid
    if bid is None or math.isnan(bid):
        if len(buff.index.get_level_values(1).unique()) == 1:
            return buff.index.get_level_values(1).tolist()[0], None, None, [], []
        else:
            LOGGER.info('Iteration complete, none unassigned banks')
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

    try:
        stepless_regs = regs_counted.loc[bid, 'stepless_reg']
        if type(stepless_regs) != list:
            stepless_regs = []
    except:
        stepless_regs = []

    try:
        foot_regs = regs_counted.loc[bid, 'foot_reg']
        if type(foot_regs) != list:
            foot_regs = []
    except:
        foot_regs = []

    LOGGER.info(priority_string.format(i, bid, score))

    return bid, score, r_score, foot_pois, stepless_pois, foot_regs, stepless_regs


# Aggregation
def agg_results(p=None, r=None, get_max=True):
    '''summs results from POI and regions'''
    if (p is None and r is None):
        raise IOError('No information at all')
    if p is None :
        LOGGER.info('no poi score')
        result = r
    elif r is None:
        LOGGER.info('no regions score')
        result = p
    else:
        tmp = pd.DataFrame({'reg_score':r['score'],
                            'poi_score':p['score']})

        if tmp.empty:
            raise IOError('No information at all')
        tmp['score'] = tmp.sum(1)
        result = tmp[['score']]

    if len(result['score']) == 0:
        return None, None
    
    return result['score'].argmax(), result['score'].max()


def update_data(buff, poi, reg, bid, s_pois, s_regs, f_pois, f_regs):
    '''update dataset with regard to the newly chosen office

    Args:
        buff: current set of buffers
        poi: current set of points
        bid: selected office's office_id
        s_pois: selected pois
    '''
    global LOGGER
    buff = update_buff(buff, bid)

    lp = len(poi)
    lr = len(reg)
    poi = poi[~poi['pid'].isin(s_pois)]  # remove stepless pois
    reg = reg[~reg['reg_id'].isin(s_regs)]

    poi.loc[poi['pid'].isin(f_pois), 'fs'] = True
    reg.loc[reg['reg_id'].isin(f_regs), 'fs'] = True

    LOGGER.info('Removed {0} poi, {1} regions'.format(lp - len(poi), lr - len(reg)))
    return buff, poi, reg


def writerow(row, filename, header):
    with open(filename, 'a') as csvfile:
        fieldnames = row.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if header:
            writer.writeheader()
        writer.writerow(row)
