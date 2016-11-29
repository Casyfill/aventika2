from poi import adjustScore
from shapely.ops import unary_union
from shapely.ops import cascaded_union
import geopandas as gp
#####################################################   Region

def getReg(u, reg):
    '''calculate adjusted Reg score for each bank'''
    cols = ['name','office_id','type','disabled', 'reg_area', 'geometry']
    u_reg = gp.overlay(u, reg, how='intersection')[cols]
    u_reg['score'] =  u_reg['disabled'] * (u_reg.area / u_reg['reg_area'])
    return u_reg


def getRegScore(buffers, reg):
    '''calculate adjusted POI score for each bank'''
    u = buffers.copy().reset_index()
    #u['geometry'] = u.geometry.map(lambda x: unary_union(x))

    x = getReg(u, reg)
    x = adjustScore(x)
    x['score'] = x['score'].astype(int)
    return x.groupby('office_id').agg({'score':'sum'}).sort_values('score', ascending=False)



def getReg2(reg):
    '''calculate adjusted Reg score for each bank'''
    return reg[['office_id','score']].groupby(['office_id']).agg({'score':sum})


def getRegScore2(COVERED, reg, reg_centroids):
    '''from the interlayed, remove those with convered centroids, group others'''
    
    if COVERED['foot'] is not None:
        c = cascaded_union(COVERED.values())
        reg = reg[~reg_centroids.within(c)]
    
    return getReg2(reg)

