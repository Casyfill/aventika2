#!/usr/bin/env python
# -*- coding: utf-8 -*-
import geopandas as gp
import pandas as pd
import multiprocessing as mp
from functools import partial
from misc import chunker_eq
from geopandas.tools import sjoin
# from mpconfig import MP, WORKERS, POOL
MP = True
WORKERS = 8
POOL = None


def joiner(x, z):
    return sjoin(z, x, how='inner', op='contains')

#####################################################   POI
def getPOI(u, poi):
    '''for each buffer, get points within'''
    u.crs = poi.crs  # seriously?
    u = u.reset_index()
    

    global joiner
    partial_joiner = partial(joiner, z=u)
    
    global MP, WORKERS, POOL
    if MP:
        try:
            if POOL is None:
                POOL = mp.Pool(processes = WORKERS)
                print 'Now I have a Pool with {} workers'.format(WORKERS)
            
            poi_chunks = chunker_eq(poi, WORKERS)
            #zs = [z for x in xrange(WORKERS)]
            #print len(zs)
            print len(poi)
        
            results = POOL.map(partial_joiner, poi_chunks)
            x = pd.concat(results)

        except Exception as inst:
            POOL.close()
            POOL.join()
            raise Exception(inst)
    

        
    else:
        x = joiner(poi, z)
          
    
    result = x.loc[pd.notnull(x['score']),['office_id','score','disability','pid', 'type']]
    
    return result



def adjustScore(poi, kf={'stepless':1, 'foot':0.8, 'car':0.1}):
    '''multiply point score by 
    correspoinding buffers coeff
    
    return 
        summary result and PIDS per office
    '''
    
    idx = pd.IndexSlice  
    
    for tp in kf.keys():
        poi.loc[poi['type']==tp,'score'] *= kf[tp]

    # drop foot_acc for DISABLED to car (9 times)
    # poi.loc[(poi['disability']==u'опорники')&(poi['type']=='foot'), 'score'] *= kf['car']/kf['foot'] 

    return poi


def getPoiScore(u, poi):
    '''calculate adjusted POI score for each bank'''
    
    x = getPOI(u, poi)
    x = adjustScore(x)
    
    
    result_score = x.groupby('office_id').agg({'score':'sum'}) #.sort_values('SCORE', ascending=False)
    result_poi = x.groupby('office_id').agg({'pid': lambda x: list(x) })
    return result_score, result_poi


       
    

