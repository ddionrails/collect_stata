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

    input_path = pathlib.Path("tests/input")
    output_path = pathlib.Path(str(tmpdir.mkdir("subdir")))

    # The test.dta file is encoded in Latin-1 or Windows-1252

    stata_to_json = StataToJson(
        study_name="soep-core",
        input_path=input_path,
        output_path=output_path,
        latin1=True,
    )
    stata_to_json.parallel_run()

    with open(output_path.joinpath("test.json")) as json_file:
        result = json.load(json_file)

    validate(instance=result, schema=dataset_schema)
