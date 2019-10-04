"""write_json.py"""
__author__ = "Marius Pahl"

import json
import logging
from collections import Counter, OrderedDict

import pandas as pd


def sorting_dataframe(values, labels, missings, frequencies):
    """Function to sort values and labels and return sorted dict"""
    dataframe = pd.DataFrame(
        {
            "values": values,
            "labels": labels,
            "missings": missings,
            "frequencies": frequencies,
        }
    )
    dataframe["labels"] = dataframe["labels"].astype(str)
    dataframe["values"] = pd.to_numeric(dataframe["values"])
    dataframe.sort_values(by="values", inplace=True)
    return dataframe.to_dict("list")


def uni_cat(elem, data):
    """Generate dict with frequencies and labels for categorical variables

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    cat_dict: dict
    """

    frequencies = []

    value_count = data[elem["name"]].value_counts()
    for value in elem["categories"]["values"]:
        try:
            frequencies.append(int(value_count[value]))
        except KeyError:
            frequencies.append(0)

    return {"frequencies": frequencies}


def uni_string():
    """Generate dict with frequencies for nominal variables

    Output:
    OrderedDict
    """

    return OrderedDict(frequencies=[], labels=[], labels_de=[], missings=[], values=[])


def uni_number():
    """Generate dict with frequencies for numerical variables

    Output:
    OrderedDict
    """

    return OrderedDict(frequencies=[], labels=[], labels_de=[], missings=[], values=[])


def stats_cat(elem, data):
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


def stats_string(elem, data):
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


def stats_number(elem, data):
    """Generate dict with statistics for numerical variables

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    data_withoutmissings = data[data[elem["name"]] >= 0][elem["name"]]

    total = data[elem["name"]].size
    invalid = int(data[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in data[elem["name"]])
    )
    valid = total - invalid

    summary = data_withoutmissings.describe()
    return {
        "Min.": summary["min"],
        "1st Qu.": summary["25%"],
        "Median": summary["50%"],
        "Mean": summary["mean"],
        "3rd Qu.": summary["75%"],
        "Max.": summary["max"],
        "valid": valid,
        "invalid": invalid,
    }


def uni_statistics(elem, data):
    """Call function to generate statistics depending on the variable type

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    if elem["scale"] == "cat":

        statistics = stats_cat(elem, data)

    elif elem["scale"] == "string":

        statistics = stats_string(elem, data)

    elif elem["scale"] == "number":

        statistics = stats_number(elem, data)

    else:
        statistics = dict()

    return statistics


def uni(elem, data):
    """Call function to generate frequencies depending on the variable type

    Input:
    elem: dict
    data: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    statistics = OrderedDict()
    _scale = elem["scale"]
    scale_functions = {"string": uni_string, "number": uni_number}

    if _scale == "cat":
        statistics.update(uni_cat(elem, data))
    # We change this to else, if no other types exist
    elif _scale in scale_functions:
        statistics.update(scale_functions[_scale]())

    return statistics


def generate_stat(data, metadata, study):
    """Prepare statistics for every variable

    Input:
    data: pandas DataFrame (later called data)
    metadata: dict (later called file_json)
    study: string

    Output:
    stat: OrderedDict
    """

    for i, elem in enumerate(metadata):
        logging.info("%s/%s", str(i + 1), str(len(metadata)))
        metadata[i]["study"] = study
        metadata[i].update({"statistics": uni_statistics(elem, data)})
        if elem["scale"] == "cat":
            metadata[i]["categories"].update(uni(elem, data))

    return metadata


def write_json(data, metadata, filename, study):
    """Main function to write json.

    TODO: this function should be able to handel a list as metadata input.
    This list will contain a dictionary for ever variable of a dataset.
    Example:
        .. code-block:: python

            [
                    {
                        "name": "variable_name",
                        "label": "variable_label",
                        "type": "category",
                        "scale": "cat",
                        "categories": {
                            "values": [-1, 1],
                            "labels": ["[-1] invalid", "[1] valid"],
                        },
                    }
            ]

        metadata_new = [
            {
                "name": "HKIND",
                "label": "Kinder",
                "type": "category",
                "scale": "cat",
                "categories": {
                    "values": [-1, 1, 2],
                    "labels": ["keine Antwort", "Ja", "Nein"],
                    "missings": [True, False, False],
                },
            },
            {
                "name": "HM04",
                "label": "Miete in Euro",
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

    Args:
        data: Datatable of imported data.
        metadata: Metadata of the imported data.
        filename: Name of the output json file.
        study: Name of the study.
    """

    stat = generate_stat(data, metadata, study)

    logging.info('write "%s"', filename)
    with open(filename, "w") as json_file:
        json.dump(stat, json_file, indent=2)
