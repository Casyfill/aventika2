import geopandas as gp
import pandas as pd
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


def data_preload(settings, src='data_path', mode='refined'):
    '''data preloader
    '''
    source = settings[src].format(city=settings[u'city'])
    print source

    modetypes = ('atm', 'office', None)
    bank_mode = settings.get('bank_mode', None)

    if bank_mode not in modetypes:
        raise IOError(
            'Mode should be in {0}, instead got {1}'.format(modetypes, mode))

    path = os.getcwd()
    path = path.replace('/code', '')
    dpath = path + source

    poi_path = dpath + settings['files'][mode]['poi']
    poi = gp.read_file(
        poi_path)[['geometry', 'score',
                   'pid', 'disability']].to_crs(epsg=32637)  # MOSCOW
    poi['score'] = poi['score'].astype(float)
    poi['fs'] = False

    LOGGER.info('loaded {n} POIs from {p}'.format(n=len(poi), p=poi_path))
    buff_path = dpath + \
        settings['files'][mode]['buffers'].format(mode=bank_mode)
    buff = gp.read_file(buff_path)
    buff['bank_type'] = bank_mode
    buff.set_index(['type', 'office_id'], inplace=1)

    buff = buff.sort_index().to_crs(epsg=32637)
    buff['priority'] = None
    LOGGER.info('loaded {n} BUFFs from {p}'.format(n=len(buff), p=buff_path))

    if settings['reg_geom']:
        reg_path = dpath + settings['files'][mode]['regions']
        reg = gp.read_file(reg_path).to_crs(epsg=32637)
        reg['fs'] = False
        reg['reg_area'] = reg.area
        reg['disabled'] = reg['disabled'].astype(float)
        LOGGER.info(
            'loaded {n} REGIONSs from {p}'.format(n=len(reg), p=reg_path))
    else:
        reg = None

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
    if len(sys.argv) > 2:
        city = sys.argv[1]
    else:
        city = 'SPB'
    print 'CITY: {}'.format(city)

    settings = getSettings()
    start = datetime.now()  # start of the calculations

    # settings['limit'] = LIMIT
    settings['city'] = city
    path = os.getcwd().replace('/code', '') + \
        settings['results'].format(city=city, bank_mode=settings['bank_mode'])
    result_path = start.strftime(path)

    timestamp = start.strftime('%Y_%m_%d')
    LOGGER.info('{ts}: start logging'.format(ts=timestamp))

    poi, buff, reg = data_preload(settings, src='data_path', mode='refined')
    buff, poi, reg = prepare(buff, poi, reg, settings)

    # iterate(buff, poi, reg,
    #         filename=result_path,
    #         settings=settings)
    print 'Done!'
