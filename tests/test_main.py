# -*- coding: utf-8 -*-
"""Test cases for command line interface."""

import pathlib
import sys
from unittest.mock import patch

import pytest

from collect_stata.__main__ import main


def test_cli_without_arguments():
    """Test main exits with code 2, when no arguments are given."""
    with pytest.raises(SystemExit) as caught_exit:
        main()
    assert caught_exit.value.code == 2


def test_cli_with_required_arguments():
    """Test main calls stata_to_json with the given arguments."""
    _arguments = [
        "__main__.py",
        "-i",
        "input_path",
        "-o",
        "output_path",
        "-s",
        "some-study",
    ]
    with patch.object(sys, "argv", _arguments), patch(
        "collect_stata.__main__.stata_to_json"
    ) as mocked_stata_to_json:
        main()
    expected_arguments = dict(
        input_path=pathlib.Path("input_path"),
        output_path=pathlib.Path("output_path"),
        study_name="some-study",
    )
    mocked_stata_to_json.assert_called_once_with(**expected_arguments)
