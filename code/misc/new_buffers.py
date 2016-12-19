import geopandas as gp
import pandas as pd

idx = pd.IndexSlice


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

    fs.loc[:, 'geometry'] = fs.loc[:, 'geometry'].intersection(slctd_foot)
    fs.index = pd.MultiIndex.from_tuples(
        [('foot_to_step', i) for _, i in fs.index.tolist()])
    fs = fs[~fs['geometry'].is_empty]

    return pd.concat([buff, fs]).sort_index()


def update_buff(buff, bid):
    '''update buff by removing
    and substracting
    buffers for chosen office

    Args:
        buff: buffers
        bid(int): id of chosen office
    '''
    buff = buff[pd.notnull(buff['geometry'])]
    buff = buff[~buff.geometry.is_empty]

    slct = buff.loc[idx[:, bid], :]  # selected Office
    buff = buff[buff.index.get_level_values(1) != bid]

    if 'foot' in slct.index.get_level_values(0):
        slctd_foot = slct.loc[idx['foot', bid], 'geometry'].iloc[0]

        tmp = buff.loc[
            idx['foot', :], 'geometry'].difference(slctd_foot)

        buff.loc[idx['foot', :], 'geometry'] = tmp

    if 'stepless' in slct.index.get_level_values(0):
        slctd_step = slct.loc[idx['stepless', bid], 'geometry'].iloc[0]
        tmp = buff.loc[idx['stepless', :], 'geometry'].difference(slctd_step)
        buff.loc[idx['stepless', :], 'geometry'] = tmp

    if all([x in buff.index.get_level_values(0) for x in ('foot_to_step', 'stepless')]):
        tmp = buff.loc[
            idx['foot_to_step', :], 'geometry'].difference(slctd_step)

        buff.loc[idx['foot_to_step', :], 'geometry'] = tmp

    buff = buff[~buff['geometry'].is_empty]
    if slctd_foot:
        buff = get_fc(buff, slctd_foot)

    return buff
