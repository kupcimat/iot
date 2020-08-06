import os.path

import yamale


def validate_yaml(schema_file: str, data_file: str):
    if not os.path.isfile(schema_file):
        raise RuntimeError(f"Schema yaml file is missing: {schema_file}")
    if not os.path.isfile(data_file):
        raise RuntimeError(f"Data yaml file is missing: {data_file}")

    schema = yamale.make_schema(schema_file)
    data = yamale.make_data(data_file)
    yamale.validate(schema, data)
