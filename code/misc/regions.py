from poi import adjustScore
# from shapely.ops import unary_union
# from shapely.ops import cascaded_union
import geopandas as gp
from geopandas.tools import sjoin
import pandas as pd


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


def getReg_overlayed(buffs, reg_overlayed):
    '''calculate overlay joint'''
    result = sjoin(buffs.reset_index(),
                   reg_overlayed,
                   how='left', op='contains')
    return result


def getRegScore(buffs, reg, settings):
    '''calculate adjusted POI score for each bank

    Args:
        buffs: buffers
        reg: regions with "density" and "reg_area" columns
        settings(dict): settings
    Returns:
        regions split with score for each bank office
    '''

    x = getReg_overlayed(buffs, reg)
    x = adjustScore(x, settings, mode='reg')

    x['score'] = x['score'].astype(int)
    return x.groupby('office_id').agg({'score': 'sum'})
