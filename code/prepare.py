from main import data_preload, getSettings
from misc.preparation import drop_poi, _bufferize, get_overlay
from misc.logger import getLogger
from datetime import datetime
import logging
LOGGER = logging.getLogger('root')


def main():
    settings = getSettings()
    start = datetime.now()  # start of the calculations


    timestamp = start.strftime('%Y_%m_%d')
    LOGGER.info(
        '{ts}: start logging: PREPARATION'.format(ts=timestamp))

    r_poi_path = settings['data_path'] + settings['files']['refined']['poi']
    r_reg_path = settings['data_path'] + settings['files']['refined']['regions']
    r_buff_path = settings['data_path'] + settings['files']['refined']['buffers']

    poi, buff, reg = data_preload(settings, mode='raw')

    poi = drop_poi(buff, poi, settings)
    with open(r_poi_path, 'w') as f:
        f.write(poi.to_crs(epsg=4326).to_json())

    buff = _bufferize(buff)
    reg['reg_area']  = reg.area
    reg = _bufferize(reg)

    with open(r_buff_path, 'w') as f:
        f.write(buff.to_crs(epsg=4326).reset_index().to_json())

    reg_overlay = get_overlay(buff, reg)
    reg_overlay.crs = buff.crs
    with open(r_reg_path, 'w') as f:
        f.write(reg_overlay.to_crs(epsg=4326).to_json())

    print'Done'


if __name__ == '__main__':
    main()
