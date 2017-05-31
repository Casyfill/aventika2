import pandas as pd
import geopandas as gp
from shapely.geometry import Point
from glob import glob


# MISC
def toGDF(data, lat='lat', lon='lon', crs=4326):
    '''csv to gdf converter'''
    crs = {'init': 'epsg:{0}'.format(crs), 'no_defs': True}
    geometry = [Point(xy) for xy in zip(data[lon], data[lat])]
    return gp.GeoDataFrame(data, crs=crs, geometry=geometry)


def _get_paths(folder):
    '''get office files in folder'''
    r = glob(folder + '/bank_*.geojson')
    print([x.split('/')[-1] for x in r])
    assert(len(r) == 2)
    return r


def chunker(df, l):
    '''split dataframe into set of relatively equal chanks'''
    return (chunk for g, chunk in df.groupby(pd.np.arange(len(df)) / l))


def chunker_eq(df, n):
    '''split into definet number of ecual chunks'''
    return pd.np.array_split(df, n)
