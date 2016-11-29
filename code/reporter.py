import pandas as pd
import geopandas as gp
from geopandas.tools import sjoin
from aventika import iteration, iterate, selfSubstract
from datetime import datetime
from misc.logger import getLogger

__appname__ = "AVENTIKA_PRIORITY"
__author__  = "Phipipp Kats (casyfill)"
__version__ = "0.9.2"

LIMIT = None

now = datetime.now().strftime('data/results/%Y_%m_%d_%H:%M:%S_results.csv')

if __name__ == '__main__':
    logger = getLogger()
    timestamp = datetime.now().strftime('%Y_%m_%d')
    logger.info('{ts}: start logging'.format(ts=timestamp))

    banks_path = './data/banks.geojson'
    banks = gp.read_file(banks_path).to_crs(epsg='32637')
    logger.info('loaded {n} banks from {p}'.format(n=len(banks), p=banks_path))
    
    poi_path = './data/poi9_1.geojson'
    poi = gp.read_file(poi_path)[['geometry', 'score', 'pid', 'disability']].to_crs(epsg='32637')
    logger.info('loaded {n} POIs from {p}'.format(n=len(poi), p=poi_path))
    
    buff_path = './data/circles.geojson'
    buff = gp.read_file(buff_path).set_index(['type','office_id']).drop('id', axis=1).sort_index().to_crs(epsg='32637')
    buff['priority'] = None
    logger.info('loaded {n} BUFFs from {p}'.format(n=len(buff), p=buff_path))

    reg_path = './data/intersected_regions.geojson'
    reg = gp.read_file(reg_path).drop('id', axis=1).to_crs(epsg='32637')
    
    logger.info('loaded {n} REGIONSs from {p}'.format(n=len(reg), p=reg_path))
    
    COVERED = {'foot':None, 'stepless':None} # buffers of newly adopted offices 

    buff = selfSubstract(buff)
    iterate(buff, poi, reg, logger=logger, filename=now, bound=LIMIT)
    
