# coding: utf-8
import geopandas as gp
import pickle
import pandas as pd
path = "../data/{}/processed/buffers_{}.pkl"
SPB_path = path.format('SPB', 'atm')
with open(SPB_path, 'rb') as f:
    d = pickle.load(f_
    )
("")
with open(SPB_path, 'rb') as f:
    d = pickle.load(f)
    
d
d.head(2)
d = gp.GeoDataFrame(d)
with open(SPB_path.replace('.pkl', '3.geojson'), 'w') as f: 
    f.write(d.to_json())
    
def _concat_n_store(city):
        data = pd.concat([pd.read_pickle(path.format(city, mode)) for mode in ('atm', 'buffer')])
        data = gp.GeoDataFrame(data)
    
with open(path.format(city, 'all').replace('.pkl', '3.geojson'), 'w') as f:
        f.write(data.to_json())
def _concat_n_store(city):
        data = pd.concat([pd.read_pickle(path.format(city, mode)) for mode in ('atm', 'buffer')])
        data = gp.GeoDataFrame(data)
    
with open(path.format(city, 'all').replace('.pkl', '3.geojson'), 'w') as f:



("")
def _concat_n_store(city):
    	data = pd.concat([pd.read_pickle(path.format(city, mode)) for mode in ('atm', 'buffer')])
    	data = gp.GeoDataFrame(data)
    
with open(path.format(city, 'all').replace('.pkl', '3.geojson'), 'w') as f:
    		f.write(data.to_json())
    
defaults write com.googlecode.iterm2 A
def _concat_n_store(city):
    	data = pd.concat([pd.read_pickle(path.format(city, mode)) for mode in ('atm', 'buffer')])
    	data = gp.GeoDataFrame(data)
    
with open(path.format(city, 'all').replace('.pkl', '3.geojson'), 'w') as f:
    		f.write(data.to_json())
    
def _concat_n_store(city):
    	data = pd.concat([pd.read_pickle(path.format(city, mode)) for mode in ('atm', 'buffer')])
    	data = gp.GeoDataFrame(data)
    	with open(path.format(city, 'all').replace('.pkl', '3.geojson'), 'w') as f:
        		f.write(data.to_json())
        
_concat_n_store('SPB')
path
def _concat_n_store(city):
    	data = pd.concat([pd.read_pickle(path.format(city, mode)) for mode in ('atm', 'office')])
    	data = gp.GeoDataFrame(data)
    	with open(path.format(city, 'all').replace('.pkl', '3.geojson'), 'w') as f:
        		f.write(data.to_json())
        
_concat_n_store('SPB')
_concat_n_store('EKB')
_concat_n_store('KZN')
get_ipython().magic(u"save 'restoring_buffers_to_json' 1-28")
