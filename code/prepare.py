from main import data_preload, getSettings
from misc.preparation import drop_poi, _bufferize, get_overlay, around
from misc.logger import getLogger
from datetime import datetime
import pandas as pd
import logging
import os
import sys
LOGGER = logging.getLogger('root')


def main(pm):

    settings = getSettings()
    settings['bank_mode'] = None
    settings['reg_geom'] = True

    start = datetime.now()  # start of the calculations

    timestamp = start.strftime('%Y_%m_%d')
    LOGGER.info(
        '{ts}: start logging: PREPARATION'.format(ts=timestamp))

    path = os.getcwd()
    path = path.replace('/code', '')
    r_poi_path = path + settings[pm].format(city=settings['city']) + settings['files']['refined']['poi']
    r_reg_path = path + settings[pm].format(city=settings['city']) + settings['files']['refined']['regions']
    r_buff_path = path +  settings[pm].format(city=settings['city']) + settings['files']['refined']['buffers']


    poi, buff, reg = data_preload(settings, src=pm, mode='raw')

    # poi = drop_poi(buff, poi, settings)
    
    # with open(r_poi_path, 'w') as f:
    #     f.write(poi.to_crs(epsg=4326).to_json())

    buff = _bufferize(buff)
    buff = buff[pd.notnull(buff['geometry'])]
    # buff.geometry= buff.geometry.apply(lambda x: around(x,2))


    reg['reg_id'] = reg.index + 1
    reg['reg_area']  = reg.area

    reg = _bufferize(reg)
    # reg.geometry = reg.geometry.apply(lambda x: around(x,2))

    # with open(r_buff_path, 'w') as f:
    #     f.write(buff.to_crs(epsg=4326).reset_index().to_json())
    LOGGER.info( '{ts}: AROUNDED BOTH, STARTING OVERLAY'.format(ts=timestamp))
    reg_overlay = get_overlay(buff, reg)
    reg_overlay.crs = buff.crs
    with open(r_reg_path, 'w') as f:
        f.write(reg_overlay.to_crs(epsg=4326).to_json())

    print'Done'


if __name__ == '__main__':
    if len(sys.argv)>1:
        path = sys.argv[1]
    else:
        path = 'data_path'
    main(path)
