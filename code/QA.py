# import geojson
import json
from os import path
from sys import argv


FP_schema = {  #"vsp": {'dtype':str},
               # "vis_rasmetka": {'dtype':int},
               # "brail": {'dtype':int},
               # "bankomat_adapt": {'dtype':int},
                # "reg_score": {'dtype':float},
                # "disability": {'dtype':list, 'child_dtype':str},
                "priority": {'dtype':int},
                "score": {'dtype':float},
                "type": {'dtype':str},
                # "sound": {'dtype':int},
                "idxColor": {'dtype':str},
                # "us_visual": {'dtype':int},
                # "pois": {'dtype':list, 'child_dtype':int},
                # "shop_intersect": {'dtype':bool},
                # "pandus": {'dtype':int},
                # "visual": {'dtype':int},
                # "raw_score": {'dtype':float},
                # "address": {'dtype':str},
                #"dist_button": {'dtype':int},
                #"info": {'dtype':int},
                #"us_disabled": {'dtype':int},
                #"name": {'dtype':str},
                # "office_id": {'dtype':int}
			}


def assert_properties(feature):
	P = feature['properties']
	for key, v in FP_schema.items():
		assert isinstance(P[key], v['dtype']) or v is None, (key, P['office_id'])
		if v['dtype'] in (list, tuple) and len(v)>0:
			for el in P[key]:
				assert isinstance(el, FP_schema[key]['dtype']['child_dtype']) or el is None

def main(file_path):

	assert path.isfile(file_path)
	assert file_path.endswith('json')

	with open(file_path, 'r') as f:
		J = json.load(f)

	# validation = geojson.is_valid(J)
	# assert validation['valid'] == 'yes', validation['message']

	for feature in J['features']:
		assert_properties(feature)

	print('Looks fine!')




if __name__ == '__main__':
    if len(argv) > 1:
        file_path = argv[1]
    else:
        raise Exception('File path requred')

    main(file_path)