# -*- coding: utf-8 -*-
""" Functional test """

import json
import pathlib
from typing import Any, Dict

from _pytest import tmpdir as pytest_tmpdir
from jsonschema import validate

from collect_stata.__main__ import StataToJson


def test_dataset_validates(tmpdir: pytest_tmpdir, dataset_schema: Dict[str, Any]) -> None:
    """ Functional test that validates a resulting dataset against a JSON Schema """

    input_folder = pathlib.Path("tests/input")
    output_folder = pathlib.Path(str(tmpdir.mkdir("subdir")))

    # The test.dta file is encoded in Latin-1 or Windows-1252

    stata_to_json = StataToJson(
        study="soep-core",
        input_folder=input_folder,
        output_folder=output_folder,
        latin1=True,
    )
    stata_to_json.parallel_run()

    with open(output_folder.joinpath("test.json")) as json_file:
        result = json.load(json_file)

    validate(instance=result, schema=dataset_schema)
