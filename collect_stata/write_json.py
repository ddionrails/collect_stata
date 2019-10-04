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


def uni_cat(elem, file_csv):
    """Generate dict with frequencies and labels for categorical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    cat_dict: dict
    """

    frequencies = []
    values = []
    missings = []
    labels = []

    value_count = file_csv[elem["name"]].value_counts()
    for value in elem["values"]:
        try:
            frequencies.append(int(value_count[value["value"]]))
        except KeyError:
            frequencies.append(0)
        labels.append(value["label"])

        var_value = value["value"]

        if value["value"] >= 0:
            missings.append(False)
        else:
            missings.append(True)
        values.append(var_value)

    return sorting_dataframe(values, labels, missings, frequencies)


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


def stats_cat(elem, file_csv):
    """Generate dict with statistics for categorical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    dict
    """

    total = file_csv[elem["name"]].size
    invalid = int(file_csv[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in file_csv[elem["name"]])
    )
    valid = total - invalid

    return {"valid": valid, "invalid": invalid}


def stats_string(elem, file_csv):
    """Generate dict with statistics for nominal variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    dict
    """
    frequencies = Counter(file_csv[elem["name"]])
    string_missings = frequencies[""] + frequencies["."]
    valid = file_csv[elem["name"]].value_counts().sum() - string_missings
    invalid = file_csv[elem["name"]].isnull().sum() + string_missings

    return {"valid": int(valid), "invalid": int(invalid)}


def stats_number(elem, file_csv):
    """Generate dict with statistics for numerical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    data_withoutmissings = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]

    total = file_csv[elem["name"]].size
    invalid = int(file_csv[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in file_csv[elem["name"]])
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


def uni_statistics(elem, file_csv):
    """Call function to generate statistics depending on the variable type

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    if elem["type"] == "cat":

        statistics = stats_cat(elem, file_csv)

    elif elem["type"] == "string":

        statistics = stats_string(elem, file_csv)

    elif elem["type"] == "number":

        statistics = stats_number(elem, file_csv)

    else:
        statistics = dict()

    return statistics


def uni(elem, file_csv):
    """Call function to generate frequencies depending on the variable type

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    statistics = OrderedDict()
    _type = elem["type"]
    type_functions = {"string": uni_string, "number": uni_number}

    if _type == "cat":
        statistics.update(uni_cat(elem, file_csv))
    # We change this to else, if no other types exist
    elif _type in type_functions:
        statistics.update(type_functions[_type]())

    return statistics


def stat_dict(elem, file_csv, file_json, study):
    """Fill variables with metadata of the dataset.

    Input:
    elem: dict
    file_csv: pandas DataFrame
    file_json: dict
    study: string

    Output:
    meta_dict: OrderedDict
    """

    scale = elem["type"][0:3]

    meta_dict = OrderedDict()

    meta_dict["study"] = study
    meta_dict["dataset"] = file_json["name"]
    meta_dict["name"] = elem["name"]
    meta_dict["label"] = elem["label"]
    meta_dict["scale"] = scale
    meta_dict["categories"] = uni(elem, file_csv)

    # For 10 or less values the statistics aren't shown.

    if elem["type"] in ("number", "cat"):
        data_withoutmissings = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]
        if sum(Counter(data_withoutmissings.values).values()) > 10:
            meta_dict["statistics"] = uni_statistics(elem, file_csv)
    else:
        meta_dict["statistics"] = uni_statistics(elem, file_csv)

    return meta_dict


def generate_stat(data, metadata, study):
    """Prepare statistics for every variable

    Input:
    data: pandas DataFrame (later called file_csv)
    metadata: dict (later called file_json)
    study: string

    Output:
    stat: OrderedDict
    """

    stat = list()
    elements = list()
    for elem in metadata["resources"][0]["schema"]["fields"]:
        elements.append(elem)
    elements_length = len(elements)

    for i, elem in enumerate(elements):
        logging.info("%s/%s", str(i + 1), str(elements_length))
        stat.append(stat_dict(elem, data, metadata, study))

    return stat


def write_json(data, metadata, filename, study=""):
    """Main function to write json.

    TODO: this function should be able to handel a list as metadata input.
    This list will contain a dictionary for ever variable of a dataset.
    Example:
        .. code-block:: python

            [
                    {
                        "name": "variable_name",
                        "label": "variable_label",
                        "type": "category"
                        "categories": {
                            "values": [-1, 1],
                            "labels": ["[-1] invalid", "[1] valid"],
                        },
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
