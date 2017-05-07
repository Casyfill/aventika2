### made to resolve issue with galton-stored pickles
import geopandas as gp
import pandas as pd
import pickle

def _get_dummy(city):
	dummies = gp.read_file('../data/{}/processed/banksdummy.geojson'.format(city))[['office_id','type']]
	dummies.rename(columns={'type':'office_type'}, inplace=1)
	return dummies

def _buffers(city):
	with open('../data/{}/processed/buffers.pkl'.format(city), 'rb') as f:
		buf = pickle.load(f)
	buf = buf[pd.notnull(buf['geometry'])]
	buf = buf[~buf.is_empty]
	return buf

def main(city):
	dummies = _get_dummy(city)
	bufs = _buffers(city)

	for el in ('atm', 'office'):
		df = dummies.loc[dummies['office_type']==el,:]
		df_bufs = bufs.merge(df, how='left', on='office_id')
		df_bufs = df_bufs[pd.notnull(df_bufs['office_type'])].drop('office_type', axis=1)

		path = '../data/{city}/processed/buffers_{el}.pkl'.format(city=city, el=el)
		df_bufs.to_pickle(path)

		# print('data processed for {}'.format(el))
		# with open(path, 'w') as f:
		# 	f.write(df_bufs.to_json())

		print('Stored {el} in: {path}'.format(el=el, path=path))

if __name__ == '__main__':
	for city in ('SPB','EKB','KZN'):
		print(city)
		main(city)

