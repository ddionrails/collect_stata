""" Functional test """
import json
import pathlib
from os import path
from typing import Dict

from jsonschema import validate

from collect_stata.stata_to_json import stata_to_json


def test_dataset_validates(tmpdir, dataset_schema: Dict):
    """ Functional test that validates a resulting dataset against a JSON Schema """

    input_path = pathlib.Path("tests/input")
    output_path = pathlib.Path(str(tmpdir.mkdir("subdir")))

    stata_to_json(study_name="soep-core", input_path=input_path, output_path=output_path)

    with open(path.join(output_path, "test.json")) as json_file:
        result = json.load(json_file)

    validate(instance=result, schema=dataset_schema)
