#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gp
import math
# from geopandas.tools import sjoin
# from shapely.geometry import Point

from shapely.ops import cascaded_union
import sys, os
import csv
# import multiprocessing as mp
# from functools import partial
from misc import *


BANKS = [] 

idx = pd.IndexSlice
#########################################################    ITERATION

def iterate(buff, poi, reg, logger, filename='results.csv', bound=None):
    '''traverse through banks'''
    cntr = 1
    # global BANKS
    
    # DROP POI OUTSIDE OF LOOP
    buff, poi, reg, reg_centroids = prepare(buff, poi, reg)
    COVERED = {'foot':None, 'stepless':None} # buffers of newly adopted offices will be added here iteratively
    logger.info('Started iteration')

    ### START ITERATION
    print('START ITERATION')
    
    while True:
        if bound is not None:
            if cntr > bound:
                break
        
        
        logger.info('{i}: Pois at the start of the loop: {n}'.format(i=cntr, n=len(poi)))
        
        buff, bid, score, reg_score, pois, COVERED = iteration(cntr, buff, poi, reg, reg_centroids, COVERED)
        
        poi = gp.GeoDataFrame(poi[~poi['pid'].isin(pois)])
        logger.info('{i}: After iteration, pois: {n}'.format(i=cntr, n=len(poi)))
    
        if bid is None:
            print '....Done!'
            break
        else:
            row = {'priority':cntr,
                   'office_id':bid,
                   'score':score,
                   'reg_score':reg_score,
                   'pois': '|'.join([str(x) for x in pois])}

            writerow(row, filename, cntr<2)
            logger.info('{i}: row stored, results: office_id:{bid} |score: {s}'.format(i=cntr, bid=row['office_id'], s=row['score']))
            cntr+=1
        



    return None #pd.DataFrame(BANKS)



def iteration(i, buff, poi=None, reg=None, reg_centroids=None, COVERED={}, mode='a'):
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
        tuple: (buff, bid, score) - updated buffers, office with max score, and it's score
    '''
    
    #print 'Iteration N{}. banks left:{}'.format(i, sum(pd.isnull(buff['priority']))/3)
    
   
    if sum(pd.isnull(buff['priority']))==0:
        print('Iteration complete, none unassigned banks')
        return None, None, None, None

    #print '    processing Buffers'
    #u = processBuffers(buff)
    u = buff

    #print '    getting POI score'
    
    poi_score, poi_counted = getPoiScore(u, poi)
    #print '    getting REG score'
    reg_score = getRegScore2(COVERED, reg, reg_centroids)
    
    #print '    agg Scores'
    
    bid, score = agg_results(poi_score, reg_score, get_max=True)
    
    
    if bid is None or math.isnan(bid):
        print('Iteration complete, none unassigned banks')
        return None, None, None, None

    pois = poi_counted.loc[bid, 'pid'] #.tolist()[0]

    try:
        r_score = reg_score.iloc[bid] # get reg_score for chosen object
    except: 
        r_score = None
    
    print 'Priority {0}: bank office {1}, score: {2}'.format(i, bid, score)
    
    
    for t in COVERED.keys():
        if COVERED[t] is None:
            COVERED[t] = buff.loc[idx[t,bid], 'geometry']
        else:
            try:
                # add a new buffer to that
                COVERED[t] =  cascaded_union([COVERED[t], buff.loc[idx[t,bid], 'geometry']])
            except:
                pass  

    #u = u.loc[idx[:,bid], :]
    


    return u.ix[u.index.get_level_values(1) != bid,:], bid, score, r_score, pois, COVERED



#####################################################   Aggregation
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
    
    if len(result['score'])==0:
        return None, None
    
    return result['score'].argmax(), result['score'].max()




def writerow(row, filename, header):
    with open(filename, 'a') as csvfile:
        fieldnames = row.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if header:
             writer.writeheader()
        writer.writerow(row)