"""test_write_json.py"""
__author__ = "Marius Pahl"

import json
import pathlib
import tempfile
import unittest
from collections import OrderedDict
from os import path

import pandas as pd

from collect_stata.write_json import (
    generate_stat,
    stat_dict,
    stats_cat,
    stats_number,
    stats_string,
    uni,
    uni_cat,
    uni_statistics,
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
        test_data = pd.read_csv(path.join(input_path, "test_data.csv"))

        return test_data

    @staticmethod
    def get_testmetadata():
        """
        Create test metadata
        """
        input_path = pathlib.Path("tests/input")
        with open(path.join(input_path, "test_metadata.json")) as json_file:
            test_metadata = json.load(json_file)

        return test_metadata

    @staticmethod
    def get_teststudy():
        """
        Create a test study
        """
        study = dict()

        study["study"] = "teststudy"

        return study

    def test_uni_cat(self):
        """
        Test for uni_cat
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        cat_dict = uni_cat(element, file_csv)

        assert cat_dict == {
            "frequencies": [2, 6, 6],
            "values": [-1, 1, 2],
            "missings": [True, False, False],
            "labels": ["missing", "a", "b"],
        }

    def test_stats_cat(self):
        """
        Test for stats_cat
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = stats_cat(element, file_csv)

        assert statistics == {"valid": 12, "invalid": 3}

    def test_stats_string(self):
        """
        Test for stats_string
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTSTRING"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = stats_string(element, file_csv)

        assert statistics == {"valid": 9, "invalid": 6}

    def test_stats_number(self):
        """
        Test for stats_number
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTNUMBER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = stats_number(element, file_csv)

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

    def test_uni_statistics_cat(self):
        """
        Test for categorical variables in uni_statistics
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

        assert statistics == {"valid": 12, "invalid": 3}

    def test_uni_statistics_string(self):
        """
        Test for nominal variables in uni_statistics
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTSTRING"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

        assert statistics == {"valid": 9, "invalid": 6}

    def test_uni_statistics_number(self):
        """
        Test for numerical variables in uni_statistics
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTNUMBER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

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

    def test_uni_statistics_other(self):
        """
        Test for other variables in uni_statistics
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTOTHER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        statistics = uni_statistics(element, file_csv)

        assert statistics == {"invalid": 1, "valid": 14}

    def test_uni_testcat(self):
        """
        Test for categorical variables in uni
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        cat_dict = uni(element, file_csv)

        assert cat_dict == OrderedDict(
            [
                ("values", [-1, 1, 2]),
                ("labels", ["missing", "a", "b"]),
                ("missings", [True, False, False]),
                ("frequencies", [2, 6, 6]),
            ]
        )

    def test_uni_teststring(self):
        """
        Test for nominal variables in uni
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTSTRING"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        string_dict = uni(element, file_csv)

        assert string_dict == OrderedDict(
            [
                ("frequencies", []),
                ("labels", []),
                ("labels_de", []),
                ("missings", []),
                ("values", []),
            ]
        )

    def test_uni_testnumber(self):
        """
        Test for numerical variables in uni
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTNUMBER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        number_dict = uni(element, file_csv)

        assert number_dict == OrderedDict(
            [
                ("frequencies", []),
                ("labels", []),
                ("labels_de", []),
                ("missings", []),
                ("values", []),
            ]
        )

    def test_uni_testother(self):
        """
        Test for other variables in uni
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTOTHER"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        other_dict = uni(element, file_csv)

        assert other_dict == dict()

    def test_stat_dict(self):
        """
        Test for stat_dict
        """
        metadata = self.get_testmetadata()
        element = next(
            (
                var
                for var in metadata["resources"][0]["schema"]["fields"]
                if var["name"] == "TESTCAT"
            ),
            None,
        )
        file_csv = self.get_testdatatable()

        study_information = self.get_teststudy()
        file_json = self.get_testmetadata()

        study = study_information["study"]

        generated_data = stat_dict(element, file_csv, file_json, study)

        assert generated_data == OrderedDict(
            [
                ("study", "teststudy"),
                ("dataset", "teststudy"),
                ("name", "TESTCAT"),
                ("label", "label for testcat"),
                ("scale", "cat"),
                (
                    "categories",
                    OrderedDict(
                        [
                            ("values", [-1, 1, 2]),
                            ("labels", ["missing", "a", "b"]),
                            ("missings", [True, False, False]),
                            ("frequencies", [2, 6, 6]),
                        ]
                    ),
                ),
                ("statistics", {"invalid": 3, "valid": 12}),
            ]
        )

    def test_generate_stat(self):
        """
        Test for generate_stat
        """
        data = self.get_testdatatable()
        study_information = self.get_teststudy()
        file_json = self.get_testmetadata()

        study = study_information["study"]

        generated_data = generate_stat(data, file_json, study)

        assert generated_data == [
            OrderedDict(
                [
                    ("study", "teststudy"),
                    ("dataset", "teststudy"),
                    ("name", "TESTCAT"),
                    ("label", "label for testcat"),
                    ("scale", "cat"),
                    (
                        "categories",
                        OrderedDict(
                            [
                                ("values", [-1, 1, 2]),
                                ("labels", ["missing", "a", "b"]),
                                ("missings", [True, False, False]),
                                ("frequencies", [2, 6, 6]),
                            ]
                        ),
                    ),
                    ("statistics", {"invalid": 3, "valid": 12}),
                ]
            ),
            OrderedDict(
                [
                    ("study", "teststudy"),
                    ("dataset", "teststudy"),
                    ("name", "TESTSTRING"),
                    ("label", "label for teststring"),
                    ("scale", "str"),
                    (
                        "categories",
                        OrderedDict(
                            [
                                ("frequencies", []),
                                ("labels", []),
                                ("labels_de", []),
                                ("missings", []),
                                ("values", []),
                            ]
                        ),
                    ),
                    ("statistics", {"invalid": 6, "valid": 9}),
                ]
            ),
            OrderedDict(
                [
                    ("study", "teststudy"),
                    ("dataset", "teststudy"),
                    ("name", "TESTNUMBER"),
                    ("label", "label for testnumber"),
                    ("scale", "num"),
                    (
                        "categories",
                        OrderedDict(
                            [
                                ("frequencies", []),
                                ("labels", []),
                                ("labels_de", []),
                                ("missings", []),
                                ("values", []),
                            ]
                        ),
                    ),
                    (
                        "statistics",
                        {
                            "Min.": 2.0,
                            "1st Qu.": 4.5,
                            "Median": 6.0,
                            "Mean": 15.454545454545455,
                            "3rd Qu.": 10.0,
                            "Max.": 100.0,
                            "valid": 11,
                            "invalid": 4,
                        },
                    ),
                ]
            ),
            OrderedDict(
                [
                    ("study", "teststudy"),
                    ("dataset", "teststudy"),
                    ("name", "TESTOTHER"),
                    ("label", "label for other test type"),
                    ("scale", ""),
                    ("categories", OrderedDict()),
                    ("statistics", {"invalid": 1, "valid": 14}),
                ]
            ),
        ]

    def test_write_json(self):
        """
        Test for write_json
        """
        data = self.get_testdatatable()
        study_information = self.get_teststudy()
        metadata = self.get_testmetadata()

        study = study_information["study"]

        filename = self.sandbox.name + "/test.json"

        write_json(data, metadata, filename, study)

        with open(filename) as json_file:
            output = json.load(json_file)

        assert output == [
            {
                "study": "teststudy",
                "dataset": "teststudy",
                "name": "TESTCAT",
                "label": "label for testcat",
                "scale": "cat",
                "categories": {
                    "values": [-1, 1, 2],
                    "labels": ["missing", "a", "b"],
                    "missings": [True, False, False],
                    "frequencies": [2, 6, 6],
                },
                "statistics": {"valid": 12, "invalid": 3},
            },
            {
                "study": "teststudy",
                "dataset": "teststudy",
                "name": "TESTSTRING",
                "label": "label for teststring",
                "scale": "str",
                "categories": {
                    "frequencies": [],
                    "labels": [],
                    "labels_de": [],
                    "missings": [],
                    "values": [],
                },
                "statistics": {"valid": 9, "invalid": 6},
            },
            {
                "study": "teststudy",
                "dataset": "teststudy",
                "name": "TESTNUMBER",
                "label": "label for testnumber",
                "scale": "num",
                "categories": {
                    "frequencies": [],
                    "labels": [],
                    "labels_de": [],
                    "missings": [],
                    "values": [],
                },
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
            {
                "study": "teststudy",
                "dataset": "teststudy",
                "name": "TESTOTHER",
                "label": "label for other test type",
                "scale": "",
                "categories": {},
                "statistics": {"invalid": 1, "valid": 14},
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
