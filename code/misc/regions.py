from poi import adjustScore
# from shapely.ops import unary_union
# from shapely.ops import cascaded_union
from functools import partial
import geopandas as gp
from geopandas.tools import sjoin
import pandas as pd
import logging
from misc import chunker_eq
LOGGER = logging.getLogger('root')


def get_aquired_regs(regs):
    '''gets three types of regs,
    depending of "aquisition" buffer'''
    stepless_reg = regs[regs['type'] == 'stepless'].groupby(
        'office_id').agg({'reg_id': lambda x: list(x)}).unstack()
    foot_reg = regs[regs['type'] == 'foot'].groupby(
        'office_id').agg({'reg_id': lambda x: list(x)}).unstack()

    fc_reg = regs[regs['type'] == 'foot_to_step'].groupby(
        'office_id').agg({'reg_id': lambda x: list(x)}).unstack()

    regs = pd.DataFrame({'stepless_reg': stepless_reg,
                         'foot_reg': foot_reg,
                         'foot_to_step': fc_reg})

    regs.index = regs.index.get_level_values(1)
    return regs


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
    try:
        return sjoin(buff, reg, how='inner', op='contains')
    except ValueError:
        return None


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
    pool = settings.get('POOL', None)  # global pull of processes

    partial_joiner = partial(joiner, buff=buff.reset_index())

    if WORKERS > 1:
        try:
            if pool is None:
                pool = mp.Pool(processes=WORKERS)
                LOGGER.info('   Pool:{} workers'.format(WORKERS))
                settings['POOL'] = pool

            reg_chunks = chunker_eq(reg_overlayed, WORKERS)
            results = pool.map(partial_joiner, reg_chunks)

            if all([r is None for r in results]):
                return None

            x = pd.concat(
                [r for r in results if not r is None]).reset_index(drop=True)

        except Exception as inst:
            pool.close()
            pool.join()
            raise Exception(inst)

    else:
        x = joiner(poi, buff)

    return x.loc[pd.notnull(x['score']), ['type', 'office_id', 'score', 'reg_id', 'fs']]


def getRegScore_area(buff, settings):
    '''calculate adj region score for each bank
    using buffer area and overal density score

    Args:
        buffs: buffers
        settings(dict): settings
    Returns:
        regions split with score for each bank office
    '''
    x = buff.reset_index()
    # print x.columns
    koeff = settings['koefficients']['region_density'][settings["city"]]
    d_koeff = settings['koefficients']['region']
    x['score'] = x.area * koeff * d_koeff
    for el in ("stepless", "foot", "foot_to_step"):
        k = settings['koefficients'][el]
        x.loc[x['type'] == el, 'score'] = x.loc[x['type'] == el, 'score'] * k
    return x.groupby('office_id').agg({'score': 'sum'}), None


def getRegScore_rayons(buffs, reg, settings):
    '''calculate adjusted POI score for each bank

    Args:
        buffs: buffers
        reg: regions with "density" and "reg_area" columns
        settings(dict): settings
    Returns:
        regions split with score for each bank office
    '''

    x = getReg_overlayed_mp(buffs, reg, settings)

    if x is not None:
        x = adjustScore(x, settings, mode='reg')
        x['score'] = x['score'].astype(int)

        scores = x.groupby('office_id').agg(
            {'score': 'sum'}) * settings['koefficients']['region']
        aq_regs = get_aquired_regs(x)

        return scores, aq_regs
    else:
        return None, None


def getRegScore(buffs, reg, settings):
    ''' switching the mode'''
    if settings["reg_geom"]:
        return getRegScore_rayons(buffs, reg, settings)
    else:
        return getRegScore_area(buffs, settings)
