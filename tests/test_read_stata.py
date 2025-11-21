"""Unittests for the collect_stata.read_stata module"""
import pathlib
import unittest
from typing import Dict, List
from unittest.mock import patch

import numpy
import pandas
from deepdiff import DeepDiff

from collect_stata.read_stata import StataDataExtractor
from collect_stata.types import Variable


class MockedStataReader:
    """Implement StataReader functions needed for tests; provide test data."""

    varlist: List[str] = ["variable_name"]
    dtypelist: List[object] = [numpy.int8]

    @staticmethod
    def value_labels() -> Dict[str, Dict[int, str]]:
        """Control what value labels are ingested during a test."""
        return {"variable_name": {-1: "[-1] invalid", 1: "[1] valid"}}

    @staticmethod
    def variable_labels() -> Dict[str, str]:
        """Control what variable labels are ingested during a test."""
        return {"variable_name": "variable_label"}

    lbllist: List[str] = ["variable_name"]

    @staticmethod
    def expected_metadata(dataset_name: str) -> List[Variable]:
        """Give the full metadata set which should be expected as test result."""
        return [
            {
                "name": "variable_name",
                "dataset": dataset_name,
                "label": "variable_label",
                "scale": "cat",
                "categories": {
                    "values": [-1, 1],
                    "labels": ["[-1] invalid", "[1] valid"],
                },
            }
        ]


class TestMetadataFunctions(unittest.TestCase):
    """Test functionality related to Metadata extraction."""

    def test_get_variable_metadata(self) -> None:
        """ Do we get desired metadata from the method?

        get_variable_metadata should return a list with a dictionary for every
        variable accessible through the stata reader.

        The expected keys should be as follow:
            * name: The name of the variable.
            * label: The label of the variable.
            * categories: A dictionary containing:

                + values: All values for the variable,
                          that have labels assigned to them.
                + labels: All labels for the variable values.
                          A label needs to be at the same index position as
                          its corresponding value inside the values list.
        """
        dataset_name = "test"
        dataset_path = pathlib.Path(dataset_name).with_suffix(".dta")
        dataset_path = pathlib.Path("/tmp").joinpath(dataset_path)
        with patch.object(pandas, attribute="read_stata", return_value=MockedStataReader):
            data_extractor = StataDataExtractor(dataset_path)
            result = data_extractor.get_variable_metadata()

        # We deepdiff both structures to ensure, that they contain the same content
        # even in the nested parts of the structure.
        # The diff should be empty, giving a {} that evaluates to False.
        # Otherwise it contains information about the difference which should be
        # usefull in the test output.
        diff = DeepDiff(MockedStataReader.expected_metadata(dataset_name), result)
        self.assertTrue(expr=(not diff), msg=str(diff))
