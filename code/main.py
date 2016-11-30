import geopandas as gp
from iteration import iterate
from datetime import datetime
import json
from misc.logger import getLogger

__appname__ = "AVENTIKA_PRIORITY"
__author__ = "Phipipp Kats (casyfill)"
__version__ = "0.9.6.01 testing"

LIMIT = None  # manual execution bound


def data_preload(settings, logger):
    '''data preloader
    '''

    dpath = settings['data_path']
    # banks_path = dpath + settings['files']['banks']
    # banks = gp.read_file(banks_path).to_crs(epsg='32637')
    # logger.info('loaded {n} banks'.format(n=len(banks), p=banks_path))

    poi_path = dpath + settings['files']['poi']
    poi = gp.read_file(
        poi_path)[['geometry', 'score',
                   'pid', 'disability']].to_crs(epsg='32637')

    logger.info('loaded {n} POIs from {p}'.format(n=len(poi), p=poi_path))

    buff_path = dpath + settings['files']['buffers']
    buff = gp.read_file(buff_path).set_index(['type', 'office_id'])
    buff = buff.sort_index().to_crs(epsg='32637')
    buff['priority'] = None
    logger.info('loaded {n} BUFFs from {p}'.format(n=len(buff), p=buff_path))

    reg_path = './data/intersected_regions.geojson'
    reg = gp.read_file(reg_path).drop('id', axis=1).to_crs(epsg='32637')
    logger.info('loaded {n} REGIONSs from {p}'.format(n=len(reg), p=reg_path))

    return poi, buff, reg


if __name__ == '__main__':

    try:
        with open('../settings.json') as f:
            settings = json.load(f)
    except Exception as inst:
        print 'Failed to read settings, check the file'
        raise Exception(inst)

    start = datetime.now()  # start of the calculations

    logger = getLogger()
    settings['limit'] = LIMIT
    settings['logger'] = logger
    result_path = datetime.now().strftime(start.strftime(settings['results']))

    timestamp = start.strftime('%Y_%m_%d')
    logger.info('{ts}: start logging'.format(ts=timestamp))

    poi, buff, reg = data_preload(settings, logger)

    iterate(buff, poi, reg,
            filename=result_path,
            settings=settings)
