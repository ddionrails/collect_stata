# -*- coding: utf-8 -*-
"""Test cases for command line interface."""

import pathlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from collect_stata.__main__ import main, StataToJson


def test_cli_without_arguments() -> None:
    """Test main exits with code 1, when no arguments are given."""
    with patch.object(sys, "argv", ["__main__.py"]):
        with pytest.raises(SystemExit) as caught_exit:
            main()
    assert caught_exit.value.code == 1


def test_cli_with_required_arguments() -> None:
    """Test main calls stata_to_json with the given arguments."""
    _arguments = [
        "__main__.py",
        "-i",
        "input_path",
        "-o",
        "output_path",
        "-s",
        "some-study",
        "-m",
        "-l",
    ]
    with patch.object(sys, "argv", _arguments), patch(
        "collect_stata.__main__.StataToJson"
    ) as mocked_stata_to_json:
        main()
        expected_arguments = dict(
            study_name="some-study",
            input_path=pathlib.Path("input_path").absolute(),
            output_path=pathlib.Path("output_path").absolute(),
            input_de_path=None,
            latin1=True,
        )
        mocked_stata_to_json.assert_called_once_with(**expected_arguments)


class test_two_dataset_inputs(unittest.TestCase):
    def test_two_inputs(self):
        with TemporaryDirectory() as output_dir:
            output_path = Path(output_dir)
            study = "test-study"
            input_path = pathlib.Path("tests/input/en")
            input_de_path = pathlib.Path("tests/input/de")

            stata_to_json = StataToJson(
                study_name=study,
                input_path=input_path,
                input_de_path=input_de_path,
                output_path=output_path,
                latin1=True,
            )
            stata_to_json.single_process_run()

