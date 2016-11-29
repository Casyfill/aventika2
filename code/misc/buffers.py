import geopandas as gp
import pandas as pd
########  BUFFER_PROCESSING
def cure_geom(bufs, tolerance=.001):
    '''simpligy geom to cure it'''
    bufs['geometry'] = bufs.simplify(tolerance, preserve_topology=False)
    return bufs


def intersectStepless(buff, tolerance=.001):
    '''simplify geometry and intersect stepless'''
    xs = buff.copy()
    
    
    s = xs.loc[idx['stepless', :], ]
    f = xs.loc[idx['foot', :], ]


    cl = s.reset_index(drop=True).intersection(f.reset_index(drop=True))
    cl.index = s.index
    xs.loc[idx['stepless', :], 'geometry'] = cl
    return xs


def selfSubstract(buff):
    '''return buffers with inner part removed'''
    idx = pd.IndexSlice
    xs =buff.copy()
    
    idx = pd.IndexSlice
    f, s = (xs.loc[idx[tp, :],: ] for  tp in ('foot', 'stepless'))
    
    #cn = c.reset_index(drop=True).difference(f.reset_index(drop=True))
    fn = f.reset_index(drop=True).difference(s.reset_index(drop=True))
    
    fn.index = f.index
    #cn.index = c.index
    
    #xs.loc[idx['car', :], 'geometry'] = cn
    xs.loc[idx['foot', :], 'geometry'] = fn
    
    return xs[xs.area>=0.0] # filter empty


def getCurrentCoverage_sql(buffs, c):
    '''return joint multipoligons of all adopted 
    buffers for each type of buffer, SQL version
    '''

    selected = [str(x) for x in buffs[pd.notnull(buffs['priority'])].index.get_level_values(1).unique().tolist()]
    u = "SELECT ST_Multi(ST_Collect(geom)) as geom FROM buffers WHERE type = '{type}' AND office_id IN ( {office_id}) ;"
    d = {}
    for t in ('foot', 'stepless'):
        query = u.format(type=t, selected = ', '.join(selected))
        d[t] = gp.read_postgis(query, c).loc[0, 'geom']
    
    return  d, gp.GeoDataFrame(buffs[pd.isnull(buffs['priority'])])
    
    
def getCurrentCoverage(buffs):
    '''return joint multipoligons of all adopted 
    buffers for each type of buffer
    
    Here we have an assumption that priority for 
    all non-adobted elements at the iteration is None
    
    Args:
        buffs(gp.GeoDataFrame): dataset of all buffers
    Returns:
        gp.GeoDataFrame: set of current union of all buffers for all adopted objects
        gp.GeoDataFrame: all unprioritized 
        
    '''
    
    idx = pd.IndexSlice
    b = gp.GeoDataFrame(buffs[pd.notnull(buffs['priority'])]) # except those already assigned
    
    for name, b in b.groupby(b.index.get_level_values('type')):
        d[name]= b.geometry.unary_union.buffer(0)
        
    return d, gp.GeoDataFrame(buffs[pd.isnull(buffs['priority'])]) # return assigned as merged Dict, not assigned


def removeCovered(u, covered, bl=1):
    '''substract current coverage of the matching type from each polygon'''
    idx = pd.IndexSlice  
    
    for n, g in covered.iteritems():
        try:
            u.loc[idx[n, :], 'geometry'] = u.loc[idx[n, :], 'geometry'].difference(g)
        except:
            u.loc[idx[n, :], 'geometry'] = u.loc[idx[n, :], 'geometry'].buffer(bl).buffer(-1*bl).difference(g)
        
        
    return u

def _cleanGeom(b):
    mask = b['geometry'].apply(lambda x: x.is_empty)        
    return b[~mask]

def _fixGeom(b):
    mask = b['geometry'].apply(lambda x: not x.is_valid)
    if sum(mask) > 0:
        b.loc[mask, 'geometry'] = b.loc[mask, 'geometry'].buffer(0)

    return b

def processBuffers(buff):
    '''update coverage, remove covered, selfsubstract'''
    
    #c, u = getCurrentCoverage(buff)
    #u = gp.GeoDataFrame(buffs[pd.isnull(buffs['priority'])])
    
    global COVERED
    
    u = removeCovered(buff, COVERED)
    u = _cleanGeom(u)
    
    
    return u #gp.GeoDataFrame(u)

