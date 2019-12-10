"""test_write_json.py"""
__author__ = "Marius Pahl"

import json
import pathlib
import tempfile
import unittest
from collections import OrderedDict

import pandas as pd

from collect_stata.write_json import (
    generate_statistics,
    get_categorical_frequencies,
    get_categorical_statistics,
    get_nominal_statistics,
    get_numerical_statistics,
    get_univariate_statistics,
    get_value_counts_and_frequencies,
    write_json,
)


class TestWriteJson(unittest.TestCase):
    """
    Tests for all methods from write_json.py
    """

    def setUp(self):
        """
        Set a TemporaryDirectory for the json testfile
        """
        self.sandbox = tempfile.TemporaryDirectory()
        return super().setUp()

    @staticmethod
    def get_testdatatable():
        """
        Create a test dataframe
        """
        input_path = pathlib.Path("tests/input")
        test_data = pd.read_csv(input_path.joinpath("test_data.csv"))

        return test_data

    @staticmethod
    def get_testmetadata():
        """
        Create test metadata
        """
        input_path = pathlib.Path("tests/input")
        with open(input_path.joinpath("test_metadata.json")) as json_file:
            test_metadata = json.load(json_file)

        return test_metadata

    @staticmethod
    def get_teststudy():
        """
        Create a test study
        """

        return "teststudy"

    def test_get_categorical_frequencies(self):
        """
        Test for get_categorical_frequencies
        """
        metadata = self.get_testmetadata()

        element = next((var for var in metadata if var["name"] == "TESTCAT"), None)
        data = self.get_testdatatable()

        cat_dict = get_categorical_frequencies(element, data)

        assert cat_dict == {"frequencies": [2, 6, 6]}

    def test_get_categorical_statistics(self):
        """
        Test for get_categorical_statistics
        """
        metadata = self.get_testmetadata()
        element = next((var for var in metadata if var["name"] == "TESTCAT"), None)
        data = self.get_testdatatable()

        statistics = get_categorical_statistics(element, data)

        assert statistics == {"valid": 12, "invalid": 3}

    def test_get_nominal_statistics(self):
        """
        Test for get_nominal_statistics
        """
        metadata = self.get_testmetadata()
        element = next((var for var in metadata if var["name"] == "TESTSTRING"), None)
        data = self.get_testdatatable()

        statistics = get_nominal_statistics(element, data)

        assert statistics == {"valid": 9, "invalid": 6}

    def test_get_numerical_statistics(self):
        """
        Test for get_numerical_statistics
        """
        metadata = self.get_testmetadata()
        element = next((var for var in metadata if var["name"] == "TESTNUMBER"), None)
        data = self.get_testdatatable()

        statistics = get_numerical_statistics(element, data)

        assert statistics == {
            "Min.": 2.0,
            "1st Qu.": 4.5,
            "Median": 6.0,
            "Mean": 15.454545454545455,
            "3rd Qu.": 10.0,
            "Max.": 100.0,
            "valid": 11,
            "invalid": 4,
        }

    def test_get_univariate_statistics_cat(self):
        """
        Test for categorical variables in get_univariate_statistics
        """
        metadata = self.get_testmetadata()
        element = next((var for var in metadata if var["name"] == "TESTCAT"), None)
        data = self.get_testdatatable()

        statistics = get_univariate_statistics(element, data)

        assert statistics == {"valid": 12, "invalid": 3}

    def test_get_univariate_statistics_string(self):
        """
        Test for nominal variables in get_univariate_statistics
        """
        metadata = self.get_testmetadata()
        element = next((var for var in metadata if var["name"] == "TESTSTRING"), None)
        data = self.get_testdatatable()

        statistics = get_univariate_statistics(element, data)

        assert statistics == {"valid": 9, "invalid": 6}

    def test_get_univariate_statistics_number(self):
        """
        Test for numerical variables in get_univariate_statistics
        """
        metadata = self.get_testmetadata()
        element = next((var for var in metadata if var["name"] == "TESTNUMBER"), None)
        data = self.get_testdatatable()

        statistics = get_univariate_statistics(element, data)

        assert statistics == {
            "Min.": 2.0,
            "1st Qu.": 4.5,
            "Median": 6.0,
            "Mean": 15.454545454545455,
            "3rd Qu.": 10.0,
            "Max.": 100.0,
            "valid": 11,
            "invalid": 4,
        }

    def test_get_value_counts_and_frequencies_cat(self):
        """
        Test for categorical variables in get_value_counts_and_frequencies
        """
        metadata = self.get_testmetadata()
        element = next((var for var in metadata if var["name"] == "TESTCAT"), None)
        data = self.get_testdatatable()

        cat_dict = get_value_counts_and_frequencies(element, data)

        assert cat_dict == OrderedDict([("frequencies", [2, 6, 6])])

    def test_generate_statistics(self):
        """
        Test for generate_statistics
        """
        data = self.get_testdatatable()
        study = self.get_teststudy()
        metadata = self.get_testmetadata()

        generated_data = generate_statistics(data, metadata, study)

        assert generated_data == [
            {
                "name": "TESTCAT",
                "label": "test for categorical variable",
                "type": "category",
                "scale": "cat",
                "categories": {
                    "values": [-1, 1, 2],
                    "labels": ["missing", "a", "b"],
                    "missings": [True, False, False],
                    "frequencies": [2, 6, 6],
                },
                "study": "teststudy",
                "statistics": {"valid": 12, "invalid": 3},
            },
            {
                "name": "TESTSTRING",
                "label": "test for nominal variable",
                "type": "str",
                "scale": "string",
                "study": "teststudy",
                "statistics": {"valid": 9, "invalid": 6},
            },
            {
                "name": "TESTNUMBER",
                "label": "test for numerical variable",
                "type": "int",
                "scale": "number",
                "study": "teststudy",
                "statistics": {
                    "Min.": 2.0,
                    "1st Qu.": 4.5,
                    "Median": 6.0,
                    "Mean": 15.454545454545455,
                    "3rd Qu.": 10.0,
                    "Max.": 100.0,
                    "valid": 11,
                    "invalid": 4,
                },
            },
        ]

    def test_write_json(self):
        """
        Test for write_json
        """
        data = self.get_testdatatable()
        study = self.get_teststudy()
        metadata = self.get_testmetadata()

        filename = self.sandbox.name + "/test.json"

        write_json(data, metadata, filename, study)

        with open(filename) as json_file:
            output = json.load(json_file)

        assert output == [
            {
                "name": "TESTCAT",
                "label": "test for categorical variable",
                "type": "category",
                "scale": "cat",
                "categories": {
                    "values": [-1, 1, 2],
                    "labels": ["missing", "a", "b"],
                    "missings": [True, False, False],
                    "frequencies": [2, 6, 6],
                },
                "study": "teststudy",
                "statistics": {"valid": 12, "invalid": 3},
            },
            {
                "name": "TESTSTRING",
                "label": "test for nominal variable",
                "type": "str",
                "scale": "string",
                "study": "teststudy",
                "statistics": {"valid": 9, "invalid": 6},
            },
            {
                "name": "TESTNUMBER",
                "label": "test for numerical variable",
                "type": "int",
                "scale": "number",
                "study": "teststudy",
                "statistics": {
                    "Min.": 2.0,
                    "1st Qu.": 4.5,
                    "Median": 6.0,
                    "Mean": 15.454545454545455,
                    "3rd Qu.": 10.0,
                    "Max.": 100.0,
                    "valid": 11,
                    "invalid": 4,
                },
            },
        ]

    def tearDown(self):
        """
        Clean TemporaryDirectory
        """
        self.sandbox.cleanup()
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
