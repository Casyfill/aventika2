from poi import adjustScore
# from shapely.ops import unary_union
# from shapely.ops import cascaded_union
import geopandas as gp
from geopandas.tools import sjoin
import pandas as pd
import logging
LOGGER = logging.getLogger('root')


def getReg(buff, reg):
    '''calculate adjusted Reg score for each bank
    Args:
        buff(gp.GeoDataFrame): buffers
        reg(gp.GeoDataFrame): regions
    '''

    cols = ['type', 'geometry', 'disabled', 'office_id', 'reg_id', 'reg_area']

    rs = []
    for n, g in buff.reset_index().groupby('office_id'):
        r = gp.overlay(g, reg, how='intersection')
        rs.append(r)

    result = gp.GeoDataFrame(pd.concat(rs))[cols]
    result['score'] = result['disabled'] * (result.area / result['reg_area'])
    return result


def getReg_overlayed(buffs, reg_overlayed, settings):
    '''calculate overlay joint'''
    result = sjoin(buffs.reset_index(),
                   reg_overlayed,
                   how='left', op='contains')

    return result[['office_id', 'score']].groupby('office_id').sum()



def joiner(reg, buff):
    return sjoin(buff, reg, how='inner', op='contains')


def getReg_overlayed_mp(buff, reg_overlayed, settings):
    '''returns  all points within
    the corresponding buffer for each office,
    with the type of the buffer

    Args:
        buff: buffers
        poi: pois
        settings(dict): settings
    return:
        pd.Dataframe
    '''
    WORKERS = settings['mp_settings']['WORKERS']
    global POOL  # global pull of processes
    
    partial_joiner = partial(joiner, buff=buff.reset_index())

    if WORKERS > 1:
        try:
            if POOL is None:
                POOL = mp.Pool(processes=WORKERS)
                LOGGER.info('   Pool:{} workers'.format(WORKERS))
            
            reg_chunks = chunker_eq(reg_overlayed, WORKERS)
            results = POOL.map(partial_joiner, reg_chunks)

            x = pd.concat(results)

        except Exception as inst:
            print buff
            POOL.close()
            POOL.join()
            raise Exception(inst)

    else:
        x = joiner(poi, buff)

    return x.loc[pd.notnull(x['score']), ['type', 'office_id', 'score']]

def getRegScore(buffs, reg, settings):
    '''calculate adjusted POI score for each bank

    Args:
        buffs: buffers
        reg: regions with "density" and "reg_area" columns
        settings(dict): settings
    Returns:
        regions split with score for each bank office
    '''

    x = getReg_overlayed_mp(buffs, reg, settings)
    x = adjustScore(x, settings, mode='reg')

    x['score'] = x['score'].astype(int)
    return x.groupby('office_id').agg({'score': 'sum'})
