import geopandas as gp
import pandas as pd

idx = pd.IndexSlice


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


def getCurrentCoverage(buffs):
    '''return joint multipoligons of all adopted
    buffers for each type of buffer

    Here we have an assumption that priority for
    all non-adobted elements at the iteration is None

    Args:
        buffs(gp.GeoDataFrame): dataset of all buffers
    Returns:
        gp.GeoDataFrame: set of current union of all buffers
                         for all adopted objects
        gp.GeoDataFrame: all unprioritized
    '''

    b = gp.GeoDataFrame(buffs[pd.notnull(buffs['priority'])])

    d = {}

    for name, b in b.groupby(b.index.get_level_values('type')):
        d[name] = b.geometry.unary_union.buffer(0)

    unassigned = gp.GeoDataFrame(buffs[pd.isnull(buffs['priority'])])
    return d, unassigned  # return assigned as merged Dict, not assigned


def removeCovered(u, covered, bl=1):
    '''substract current coverage of the matching type from each polygon'''

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

