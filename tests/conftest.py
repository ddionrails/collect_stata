""" Fixtures for unit tests """

import json
from typing import Dict

import pytest


@pytest.fixture(scope="session")
def dataset_schema() -> Dict:
    """ A fixture containing a JSON Schema for describing datasets """
    with open("tests/dataset_schema.json", "r") as file:
        return json.load(file)
