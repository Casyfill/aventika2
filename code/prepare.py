from main import data_preload, getSettings
from misc.preparation import prepare
from misc.logger import getLogger
from datetime import datetime


def main():
    settings = getSettings()
    start = datetime.now()  # start of the calculations

    settings['logger'] = getLogger()

    timestamp = start.strftime('%Y_%m_%d')
    settings['logger'].info(
        '{ts}: start logging: PREPARATION'.format(ts=timestamp))

    poi, buff, reg = data_preload(settings, mode='raw')
    buff, poi, reg = prepare(buff, poi, reg, settings)

    r_poi_path = settings['data_path'] + settings['files']['refined']['poi']
    # r_buf_path = settings['data_path'] + settings['files']['refined']['poi']
    r_reg_path = settings['data_path'] + settings['files']['refined']['regions']

    with open(r_poi_path, 'w') as f:
        f.write(poi.to_json())

    with open(r_reg_path, 'w') as f:
        f.write(reg.to_json())

    print'Done'


if __name__ == '__main__':
    main()
