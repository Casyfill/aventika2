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
        buff: buff with new buffers adder
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

    slctd_foot = buff.loc[idx['foot', bid], 'geometry']
    slctd_step = buff.loc[idx['stepless', bid], 'geometry']
    buff = buff[buff.index.get_level_values(1) != bid]

    with open('buffer_log.geojson', 'w') as f:
        f.write(buff.to_json())

    # normal reduction
    if 'foot' in buff.index.get_level_values(0):
        buff.loc[idx['foot', :], 'geometry'] = buff.loc[
            idx['foot', :], 'geometry'].difference(slctd_foot)
        buff.loc[idx['foot', :], 'geometry'] = buff.loc[
            idx['foot', :], 'geometry'].difference(slctd_step)

    if 'stepless' in buff.index.get_level_values(0):
        buff.loc[idx['stepless', :], 'geometry'] = buff.loc[
            idx['stepless', :], 'geometry'].difference(slctd_step)
    
  
    if 'foot_to_step' in buff.index.get_level_values(0):
        buff.loc[idx['foot_to_step', :], 'geometry'] = buff.loc[
            idx['foot_to_step', :], 'geometry'].difference(slctd_step)
 
    buff = buff[~buff['geometry'].is_empty]
    buff2 = get_fc(buff, slctd_foot)

    return buff2
