from main import data_preload, getSettings
from misc.logger import getLogger
from datetime import datetime
import pandas as pd
import geopandas as gp

from sys import argv

PATH = '../data/{city}/{p}/{f}'
score_google_drive = 'https://docs.google.com/spreadsheets/d/13uqSLogm3Le5yIxaErv8FR3zxp27hbiU_rKDr7t0CS8/pub?gid=1543708971&single=true&output=csv'


def load_other(city):
    path = PATH.format(city=city,
                       p='raw',
                       f='poi_other.geojson')

    poi_other = gp.read_file(path)
    poi_other.columns = poi_other.columns.str.lower()
    poi_other = poi_other[["group", "address",
                           "field_16", "importance",
                           "name", 'subgroup', 'geometry']]

    return poi_other.rename(columns={'field_16': 'disability'})


def load_metro(city):
    path = PATH.format(city=city,
                       p='raw',
                       f='poi_metro.geojson')

    poi = gp.read_file(path)[['geometry', "name_ru"]]
    poi.columns = ['geometry', 'name']
    poi['group'] = 'transport'
    poi['subgroup'] = 'subway'
    return poi


def load_transport(city):
    path = PATH.format(city=city,
                       p='raw',
                       f='poi_ostanovki.geojson')

    poi = gp.read_file(path)[['geometry', "name"]]
    poi.columns = ['geometry', 'name']
    poi['group'] = 'transport'
    poi['subgroup'] = 'stops'
    return


def main(city):
    '''get pois and classify them so that'''

    group_scores = pd.read_csv(score_google_drive, encoding='utf8')
    
    print group_scores.columns

    others = load_other(city)
    transport = load_transport(city)
    metro = load_metro(city)

    df = gp.GeoDataFrame(pd.concat([others, transport, metro]))

    for col in ('group', 'subgroup'):
        group_scores[col] = group_scores[col].str.lower().str.strip()
        df[col] = df[col].str.lower().str.strip()

    df = df.merge(group_scores, on=['group', 'subgroup'], how='left')

    if pd.isnull(df['score']).any():
        x = df.loc[pd.isnull(df['score']), ['group', 'subgroup']].drop_duplicates()
        x.to_csv(PATH.format(city=city, p='raw', f='lacking_groups.csv'), encoding='utf8')
        print 'Lacking some groups/subgroups: \n'
        print x
    else:
        print 'Everything Matched!'

    df['pid'] = df.index + 1

    out_path = PATH.format(city=city,
                           p='processed',
                           f='poi.geojson')

    with open(out_path, 'w') as f:
        f.write(df.to_json())



if __name__ == '__main__':
    if len(argv) > 1:
        city = argv[1]
    else:
        city = 'MSC'

    main(city)
