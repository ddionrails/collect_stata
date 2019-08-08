""" Functional test """

from typing import Dict

from jsonschema import validate


def test_dataset_validates(dataset_schema: Dict):
    """ Functional test that validates a resulting dataset against a JSON Schema """
    # TODO: Create a result instance
    result = None
    validate(instance=result, schema=dataset_schema)
