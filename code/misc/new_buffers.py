import geopandas as gp
import pandas as pd
import logging
LOGGER = logging.getLogger('root')

idx = pd.IndexSlice
# from shapely.geometry.polygon import Polygon

def shyReduction(x, y):
    '''tryies to substract, drop if failed'''
    try:
        return unary_union(x['geometry']).difference(unary_union(y))
    except Exception as inst:
        LOGGER.info('buffer {bid}: Dropped because of error: {inst}'.format(bid=x.name[1], inst=inst))
        return None


def get_fc(buff, slctd_foot):
    '''adds a third type of buffer
    one where foot distance is already covered,
    but stepless is not. pois and regions here
    will add a score=difference between foot and stepless

    Args:
        buff: current buffs
        slctd_step: stepless buffer for selected office
    Returns:
        buff: buff with new buPffers adder
    '''

    fs = buff.loc[idx['stepless', :], :].copy()
    fs = fs[pd.notnull(fs['geometry'])]

    if fs.loc[:, 'geometry'].intersects(slctd_foot).any():
        fs.loc[:, 'geometry'] = fs.loc[:, 'geometry'].intersection(slctd_foot)
        fs.index = pd.MultiIndex.from_tuples(
            [('foot_to_step', i) for _, i in fs.index.tolist()])
        fs = fs[~fs['geometry'].is_empty]
        if not fs.empty:
            LOGGER.info('defined foot-too-step')
            return pd.concat([buff, fs]).sort_index()
    return buff


def update_buff(buff, bid):
    '''update buff by removing
    and substracting
    buffers for chosen office

    Args:
        buff: buffers
        bid(int): id of chosen office
    '''
    # print buff, bid?
    slctd_step = None
    slctd_foot = None

    buff = buff[pd.notnull(buff['geometry'])]
    buff = buff[~buff.geometry.is_empty]
    # buff = buff[buff.area >= 4000] ## remove small ones

    slct = buff.loc[idx[:, bid], :]  # selected Office
    buff = buff[buff.index.get_level_values(1) != bid]

    # if buff.empty:
    #     return None

    # if 'foot' in slct.index.get_level_values(0):
    #     slctd_foot = slct.loc[idx['foot', bid], 'geometry']
    #     # print type(slctd_foot)
    #     if isinstance(slctd_foot, gp.geoseries.GeoSeries):
    #         slctd_foot = slctd_foot.iloc[0]
    #     tmp = buff.loc[
    #         idx['foot', :], 'geometry'].difference(slctd_foot)

    #     buff.loc[idx['foot', :], 'geometry'] = tmp

    # if 'stepless' in slct.index.get_level_values(0):
    #     slctd_step = slct.loc[idx['stepless', bid], 'geometry']
    #     # print type(slctd_step)
    #     if isinstance(slctd_step, gp.geoseries.GeoSeries):
    #         slctd_step = slctd_step.iloc[0]
    #     tmp = buff.loc[idx['stepless', :], 'geometry'].difference(slctd_step)
    #     buff.loc[idx['stepless', :], 'geometry'] = tmp

    # # foot to step
    # if 'foot_to_step' in buff.index.get_level_values(0) and slctd_step:
    #     tmp = buff.loc[
    #         idx['foot_to_step', :], 'geometry'].difference(slctd_step)

    #     buff.loc[idx['foot_to_step', :], 'geometry'] = tmp

    # buff = buff[~buff['geometry'].is_empty]
    # if slctd_foot:
    #     buff = get_fc(buff, slctd_foot)

    return buff
