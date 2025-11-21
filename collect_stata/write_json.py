"""write_json.py"""
__author__ = "Marius Pahl"

import json
import logging
import pathlib
from collections import Counter
from typing import Dict, List, Optional, Union

import numpy
import pandas
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype

from collect_stata.types import Categories, Numeric, Variable


def get_categorical_frequencies(elem: Variable, data: pandas.DataFrame) -> Categories:
    """Generate dict with frequencies and labels for categorical variables

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    cat_dict: dict
    """
    pass


def get_categorical_statistics(
    elem: Variable, data: pandas.DataFrame
) -> Dict[str, Union[int, float]]:
    """Generate dict with statistics for categorical variables

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    dict
    """

    total = data[elem["name"]].size
    invalid = int(data[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in data[elem["name"]])
    )
    valid = total - invalid

    return {"valid": valid, "invalid": invalid}


def get_nominal_statistics(elem: Variable, data: pandas.DataFrame) -> Dict[str, Numeric]:
    """Generate dict with statistics for nominal variables

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    dict
    """

    frequencies = Counter(data[elem["name"]])
    string_missings = frequencies[""] + frequencies["."]
    valid = data[elem["name"]].value_counts().sum() - string_missings
    invalid = data[elem["name"]].isnull().sum() + string_missings

    return {"valid": int(valid), "invalid": int(invalid)}


def get_numerical_statistics(
    elem: Variable, data: pandas.DataFrame
) -> Dict[str, Union[float, int]]:
    """Generate dict with statistics for numerical variables

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    data_without_missings = data[data[elem["name"]] >= 0][elem["name"]]

    total = data[elem["name"]].size
    invalid = int(data[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in data[elem["name"]])
    )
    valid = total - invalid

    summary = data_without_missings.describe()
    return {
        "Min.": float(numpy.nan_to_num(summary["min"])),
        "1st Qu.": float(numpy.nan_to_num(summary["25%"])),
        "Median": float(numpy.nan_to_num(summary["50%"])),
        "Mean": float(numpy.nan_to_num(summary["mean"])),
        "3rd Qu.": float(numpy.nan_to_num(summary["75%"])),
        "Max.": float(numpy.nan_to_num(summary["max"])),
        "valid": int(numpy.nan_to_num(valid)),
        "invalid": int(numpy.nan_to_num(invalid)),
    }


def get_univariate_statistics(
    elem: Variable, data: pandas.DataFrame
) -> Dict[str, Union[int, float]]:
    """Call function to generate statistics depending on the variable type

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    if is_datetime64_any_dtype(data[elem["name"]]):
        data[elem["name"]] = data[elem["name"]].apply(str)
        elem["scale"] = "string"

    if elem["scale"] == "cat":
        statistics = get_categorical_statistics(elem, data)
    elif elem["scale"] == "string":
        statistics = get_nominal_statistics(elem, data)
    elif elem["scale"] == "number":
        try:
            statistics = get_numerical_statistics(elem, data)
        except TypeError:
            statistics = dict()
    else:
        statistics = dict()

    return statistics


def set_frequencies(variable_metadata: Variable, data: pandas.DataFrame) -> Variable:
    """Store frequencies of variable values in an equally ordered list

    Args:
        variable_metadata: A dictionary structure with metadata about a single
                           variable. Passed variable metadata is 
                           manipulated implicitly, since it is mutable and
                           returned explicitly.
        data:              The original dataset loaded by pandas.

    Returns:
        The variable metadata with added list at ["categories"]["frequencies"].
        List order is dependent on the list at ["categories"]["values"]
    """

    value_counts: pandas.Series = data[variable_metadata["name"]].value_counts()

    variable_metadata["categories"]["frequencies"] = [
        int(value_counts[value]) if value in value_counts else 0
        for value in variable_metadata["categories"]["values"]
    ]

    return variable_metadata


def generate_statistics(
    data: pandas.DataFrame, metadata: List[Variable], study: str
) -> List[Variable]:
    """Prepare statistics for every variable

    Input:
    data: pandas DataFrame
    metadata: dict
    study: string

    Output:
    stat: OrderedDict
    """

    logging.info("Processing {} variables for", len(metadata))
    for variable_metadata in metadata:
        variable_metadata["study"] = study
        variable_metadata["statistics"] = get_univariate_statistics(
            variable_metadata, data
        )
        variable_metadata["categories"]["missings"] = [
            -200 <= value < 0 for value in variable_metadata["categories"]["values"]
        ]
        variable_metadata = set_frequencies(variable_metadata, data)

    return metadata


def update_metadata(
    metadata: List[Variable], metadata_de: Optional[List[Variable]]
) -> List[Variable]:
    """Get information of german and english metadata and create a new metadata variable

    Input:
    metadata: Metadata of the main (english if possible) imported data.
    metadata_de: Metadata of the german imported data.

    Output:
    metadata: Metadata variable with german and english labels if given.
    """

    if metadata and not metadata_de:
        for main_variable in metadata:
            main_variable["label_de"] = [""] * len(main_variable["label"])
    elif metadata and metadata_de:
        for main_variable, variable_de in zip(metadata, metadata_de):
            main_variable["label_de"] = variable_de["label"]
            if main_variable.get("categories", {}).get("labels", []):
                main_variable["categories"]["labels_de"] = variable_de["categories"][
                    "labels"
                ]

    return metadata


def write_json(  # pylint: disable=too-many-arguments
    data: pandas.DataFrame,
    metadata: List[Variable],
    metadata_de: Optional[List[Variable]],
    filename: pathlib.Path,
    study: str,
    latin1: bool,
) -> None:
    """Main function to write json.

    metadata_test = [
        {
            "name": "HKIND",
            "label": "test for categorical var",
            "type": "category",
            "scale": "cat",
            "categories": {
                "values": [-1, 1, 2],
                "labels": ["missing", "yes", "no"],
                "missings": [True, False, False],
            },
        },
        {
            "name": "HM04",
            "label": "test for numerical var",
            "type": "int",
            "scale": "number",
        },
        {
            "name": "HKGEBA",
            "label": "test for string var",
            "type": "str",
            "scale": "string",
        }
    ]

    metadata_de_test = [
        {
            "name": "HKIND",
            "label": "Test für kategoriale Variablen",
            "type": "category",
            "scale": "cat",
            "categories": {
                "values": [-1, 1, 2],
                "labels": ["missing", "ja", "nein"],
                "missings": [True, False, False],
            },
        },
        {
            "name": "HM04",
            "label": "Test für numerische Variablen",
            "type": "int",
            "scale": "number",
        },
        {
            "name": "HKGEBA",
            "label": "Test für nominale Variablen",
            "type": "str",
            "scale": "string",
        }
    ]

    Args:
        data: Datatable of imported data.
        metadata_en: Metadata of the english imported data.
        metadata_de: Metadata of the german imported data.
        filename: Name of the output json file.
        study: Name of the study.
    """

    metadata = update_metadata(metadata, metadata_de)

    stat = generate_statistics(data, metadata, study)

    logging.info('write "%s"', filename)
    # Pandas decodes data with Latin-1
    # The source will be decoded incorrectly,
    # if the source files are UTF-8 or anything other than Latin-1.
    # The data is encoded back to Latin-1 here
    # to minimize en/decoding errors.
    # This decode encode circle will most likely leave the original encoding intact.
    # If the source is actually a real Latin-1 encoded file, writing it back into Latin-1
    # will also make the output a Latin-1 file. We do not want this.
    # But since, in this case, the source was correctly decoded by pandas, we can just
    # write the file with UTF-8 encoding.
    # TL;DR: if the source is Latin-1 encoded we can safely use utf-8 for writing output.
    encoding = "utf-8" if latin1 else "latin1"
    with open(filename, "w", encoding=encoding) as json_file:
        json.dump(stat, json_file, indent=2, ensure_ascii=False)
