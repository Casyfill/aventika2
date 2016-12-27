import geopandas as gp
from iteration import iterate
from datetime import datetime
import json
from misc.logger import getLogger
from misc.preparation import prepare
import sys
import os
__appname__ = "AVENTIKA_PRIORITY"
__author__ = "Phipipp Kats (casyfill)"
__version__ = "0.9.7.01 testing"

LIMIT = None  # manual execution bound
LOGGER = getLogger()

def data_preload(settings, source='data_path', mode='refined'):
    '''data preloader
    '''
    logger = settings.get('logger', None)
    

    path = os.getcwd()
    path = path.replace('code/', '')
    dpath = path + settings[source]
    # banks_path = dpath + settings['files']['banks']
    # banks = gp.read_file(banks_path).to_crs(epsg=32637)
    # logger.info('loaded {n} banks'.format(n=len(banks), p=banks_path))

    poi_path = dpath + settings['files'][mode]['poi']
    poi = gp.read_file(
        poi_path)[['geometry', 'score',
                   'pid', 'disability']].to_crs(epsg=32637)
    poi['score'] = poi['score'].astype(float)
    if logger:
        logger.info('loaded {n} POIs from {p}'.format(n=len(poi), p=poi_path))

    buff_path = dpath + settings['files'][mode]['buffers']
    buff = gp.read_file(buff_path).set_index(['type', 'office_id'])
    buff = buff.sort_index().to_crs(epsg=32637)
    buff['priority'] = None
    if logger:
        logger.info('loaded {n} BUFFs from {p}'.format(n=len(buff), p=buff_path))

    reg_path = dpath + settings['files'][mode]['regions']
    reg = gp.read_file(reg_path).to_crs(epsg=32637)
    # reg['reg_area'] = reg.area
    # reg['disabled'] = reg['disabled'].astype(float)
    if logger:
        logger.info('loaded {n} REGIONSs from {p}'.format(n=len(reg), p=reg_path))

    #d =  {'init': 'epsg:32637', 'no_defs': True}
    #poi.crs = d
    #buff.crs = d
    #reg.crs = d
    #print "remember_ CRS pervertion!"
    return poi, buff, reg


def getSettings(path='../settings.json', mode='test'):
    try:
        with open(path) as f:
            settings = json.load(f)
            settings['mode'] = mode
    except Exception as inst:
        print 'Failed to read settings, check the file'
        raise Exception(inst)

    return settings


if __name__ == '__main__':
    # flag = sys.argv[1] == 'pkl' # if get data from pickle
    settings = getSettings()
    start = datetime.now()  # start of the calculations

    settings['limit'] = LIMIT
    
    result_path = datetime.now().strftime(start.strftime(settings['results']))

    timestamp = start.strftime('%Y_%m_%d')
    LOGGER.info('{ts}: start logging'.format(ts=timestamp))

    poi, buff, reg = data_preload(settings)
    # buff, poi, reg = prepare(buff, poi, reg, settings)

    iterate(buff, poi, reg,
            filename=result_path,
            settings=settings)
    print 'Done!'
