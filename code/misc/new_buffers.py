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
    with open('buff_log.geojson', 'w') as f:
        f.write(buff.reset_index(drop=False).to_json())

    slct = buff.loc[idx[:, bid], :]  # selected Office
    buff = buff[buff.index.get_level_values(1) != bid]

    if 'foot' in slct.index.get_level_values(0):
        slctd_foot = buff.loc[idx['foot', bid], 'geometry']

        tmp = buff.loc[
            idx['foot', :], 'geometry'].difference(slctd_foot).difference(slctd_step)

        buff.loc[idx['foot', :], 'geometry'] = tmp[~tmp.is_empty]

    if 'stepless' in slct.index.get_level_values(0):
        slctd_step = buff.loc[idx['stepless', bid], 'geometry']
        tmp = buff.loc[idx['stepless', :], 'geometry'].difference(slctd_step)
        buff.loc[idx['stepless', :], 'geometry'] = tmp[~tmp.is_empty]

    if 'foot_to_step' in buff.index.get_level_values(0):
        tmp = buff.loc[
            idx['foot_to_step', :], 'geometry'].difference(slctd_step)

        buff.loc[idx['foot_to_step', :], 'geometry'] = tmp[~tmp.is_empty]

    buff = buff[~buff['geometry'].is_empty]
    buff2 = get_fc(buff, slctd_foot)

    return buff2
