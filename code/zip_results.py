    #!/usr/bin/env python
# -*- coding: utf-8 -*-

# zip results.csv and banks,
# creating a final version of the geojson 
# with all scores and priorities

import json
import pandas as pd
import codecs
import geopandas as gp
from geopandas.tools import sjoin
from datetime  import datetime

PATH = '../data/clean_data/'

def _classify(results, banks, k=['low', 'below-average', 'above-average', 'high' ] ):
    '''generate fisher_jehks bins
    for specific range'''
    
    # from pysal.esda.mapclassify import Fisher_Jenks as classyfyer
    from pysal.esda.mapclassify import Equal_Interval as classyfyer

    classes = pd.np.array(k)

    s = banks.merge(results.reset_index(), on='office_id', how='left')['score'].fillna(0)

    labels =  classyfyer(s, k=len(k)).yb
    return classes[labels]



def _correct_dis_type(pois):
    tr = {u'инвалиды':'general', u'опорники':'oporniki', 
          u'глухие_':'deaf', u'ментал_': 'psychic',
          u'слепые_':'vision', u'о,м':'general',
          None:'general','yes': 'general', 'no': 'general',
          'limited': 'general' }
    
    return pois_1['disability'].replace(tr)


def _drop_duplicates(pois):
    '''drop duplicates from geodataframe'''
    pois2 = pois[[x for x in pois.columns if x not in ('geometry')]].drop_duplicates(['name', 'address', 'description'])
    return gp.GeoDataFrame(pois2.merge(pois_1[['pid', 'geometry']], on='pid', how='left'))


def _prepare_POI():
    '''read and process POI'''
    
    pois = gp.read_file('{}poi.geojson'.format(PATH), encoding='utf8')
    try:
        pois.drop(['office_id','id', 'website'], axis=1, inplace=1)
    except Exception as inst:
        print(inst)
        pass
    
    pois['pid'] = pois.index + 1
    pois = _correct_dis_type(pois)
    
    try:
        pois_1['description'] = pois_1['description'] + pois_1['descr']
        pois_1.drop('descr', inplace=1, axis=1)
    except Exception as inst:
        print(inst)
        
    return _drop_dublicates(pois)
    
def read_results():
    results = pd.read_csv('{}results.csv'.format(PATH))
    results.set_index('office_id', inplace=1)
    results = results.drop_duplicates()
    
    results = results[~results['pois'].str.contains('pois')] # DROP MIXED HEADERS
    results.index = results.index.astype(int)
    return results
    
    
def mainLoop(banks, b2, POI, results, buffers, gen_pois=True):
    '''travers through banks and add results information'''
    count = 0
    ubanks = banks.copy()

    for b in ubanks['features']:
        
        for col in ("bankomat_adapt", "brail", "dist_button", "info", "pandus", "sound", "us_disabled", "us_visual", "vis_rasmetka", "visual"):
            b['properties'][col] = int(b['properties'][col])

        if b['properties']["shop_intersect"] == 'true':
            b['properties']["shop_intersect"] = True
        else:
            b['properties']["shop_intersect"] = False

        if b['properties']['type'] == u"Банкомат":
            b['properties'].pop('pandus', None)
            b['properties'].pop('dist_button', None)
    
        # for each bank office
        bid = b['properties']['office_id'] # GET ID
        b["geometry"]["coordinates"] = b["geometry"]["coordinates"][:2] # drop third coordinate if occurs
        
        if gen_pois:
            mask = POI.intersects(buffers.loc[buffers['office_id']==bid,'geometry'].unary_union)    
            b['properties']['pois'] = [int(x) for x in POI.loc[mask,'pid'].tolist()]
            b['properties']['disability'] =  list(set(POI.loc[mask,'disability'].tolist()))

        b['properties']['idxColor'] = b2.loc[b2['office_id']==bid, 'idxColor'].iloc[0]

        if bid in results.index:
            b['properties']['priority'] = int(results.ix[bid,'priority'])
            # b['properties']['score'] = float(results.ix[bid,'score'])
            b['properties']['score'] = float(results.ix[bid,'score_norm'])
        else:
            b['properties']['priority'] = None
            b['properties']['score'] = 0
            # b['properties']['score_norm'] = 0
            count+=1
            
    print('Done! {} banks were infered'.format(count))
    return ubanks

    
def main():
    '''xoxo'''
    print('loading buffers')
    buff = gp.read_file('{}buffers.geojson'.format(PATH), encoding='utf8')
    buffers = gp.GeoDataFrame(buff.groupby('office_id').agg({'geometry': lambda x: x.unary_union}).reset_index())
    
    print('loading pois')
    POI = gp.read_file('{}poi.geojson'.format(PATH))  #_prepare_POI()
    
    print('loading banks')
    with codecs.open('{}banks.geojson'.format(PATH), 'r', encoding='utf-8') as f:
        banks = json.load(f)

    b2 = gp.read_file('{}banks.geojson'.format(PATH))


    results = read_results()
    results['score_norm'] = (100.0 * results['score'] / results['score'].max()).round(2)
    # print 'First office:', results.loc[results.score_norm==100].index
    # b = pd.DataFrame([f['properties'] for f in banks['features']])
    
    b2['idxColor'] = _classify(results, b2, k=['low', 'below-average', 'above-average', 'high' ])

    
    print('starting the loop')
    ubanks = mainLoop(banks, b2, POI, results, buffers, gen_pois=True)

    
    
    with codecs.open('{path}/{ts}_banks_scored.json'.format(path=PATH, ts=datetime.now().strftime('%Y-%m-%d_%H:%M:%S')), 'w', encoding="utf-8") as f:
        json.dump(ubanks, f, ensure_ascii=False)
    print('Done! Stored in ')

if __name__ == '__main__':
    main()
    