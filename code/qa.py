'''
quality assurance for collected metrics
'''
import json
import jsonschema
from sys import argv
import os
schema_dir = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..', 'schemas'))
SCHEMES = {}

with open(os.path.join(schema_dir, 'bank_schema.json'), 'r') as f:
    SCHEMES['bank'] = json.load(f)

with open(os.path.join(schema_dir, 'dummy_schema.json'), 'r') as f:
    SCHEMES['dummy'] = json.load(f)


def quality_assurance(data, mode='dummy'):
    '''checks if data dictionary follows the schema'''

    assert mode in SCHEMES.keys(), 'Mode should be in {}, received: {}'.format(
        SCHEMES.keys(), mode)
    scheme = SCHEMES[mode]

    try:
        jsonschema.validate(data, scheme)
    except jsonschema.ValidationError as e:
        raise Exception(e.message, e.validator,
                        e.validator_value, e.absolute_schema_path)


def quality_assurance_features(data, mode='dummy'):
    '''checks if data dictionary follows the schema'''

    assert mode in SCHEMES.keys(), 'Mode should be in {}, received: {}'.format(
        SCHEMES.keys(), mode)
    scheme = SCHEMES[mode]
    for feature in data['features']:
        try:
            jsonschema.validate(data, scheme['properties']['features']['items'])
        except jsonschema.ValidationError as e:
            raise Exception(e.message, e.validator,
                        e.validator_value, e.absolute_schema_path, feature['properties']["address"], feature['properties'].keys())    

    try:
        jsonschema.validate(data, scheme)
    except jsonschema.ValidationError as e:
        raise Exception(e.message, e.validator,
                        e.validator_value, e.absolute_schema_path)
    print("All Valid!")


def main(filepath, mode):
    assert os.path.isfile(filepath) and filepath.endswith(
        'json'), 'Not a json file'
    with open(filepath, 'r') as f:
        data = json.load(f)

    quality_assurance(data=data, mode=mode)
    print('{}: Validated!'.format(filepath))


if __name__ == '__main__':
    if len(argv) < 3:
        raise Exception('Need file to json path and mode')
    main(argv[1], argv[2])
