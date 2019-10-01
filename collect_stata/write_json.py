"""Write calculations and metadata out as a json file.
"""
__author__ = "Marius Pahl"

import json
import logging
from collections import Counter, OrderedDict

import pandas as pd


def sorting_dataframe(
    values: list, labels: list, missings: list, frequencies: list
) -> dict:
    """Function to sort values and labels and return sorted dict.

    Args:
        values: List of values.
        labels: List of labels.
        missings: List of missings.
        frequencies: List of frequencies.

    Returns:
        Sorted dictionary of categorical values.
    """

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


def uni_cat(elem: dict, data: pd.DataFrame) -> dict:
    """Generate dict with frequencies and labels for categorical variables.

    Args:
        elem: Name, label, type and values of categorical variables.
        data: Datatable of imported data.

    Returns:
        Values, labels, missings and frequencies of the categorical variable.
    """

    frequencies = []
    values = []
    missings = []
    labels = []

    value_count = data[elem["name"]].value_counts()
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


def uni_string() -> dict:
    """Generate dict with frequencies for nominal variables.

    Returns:
        Empty placeholder for frequencies, labels, labels_de,
        missings and values for nominal variables.
    """

    return dict(frequencies=[], labels=[], labels_de=[], missings=[], values=[])


def uni_number() -> dict:
    """Generate dict with frequencies for numerical variables.

    Returns:
        Empty placeholder for frequencies, labels, labels_de,
        missings and values for numerical variables.
    """

    return dict(frequencies=[], labels=[], labels_de=[], missings=[], values=[])


def stats_cat(elem: dict, data: pd.DataFrame) -> dict:
    """Generate dict with valid and invalid values for categorical variables.

    Args:
        elem: Name, label, type and values of categorical variables.
        data: Datatable of imported data.

    Returns:
        Number of valid and invalid values.
    """

    total = data[elem["name"]].size
    invalid = int(data[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in data[elem["name"]])
    )
    valid = total - invalid

    return {"valid": valid, "invalid": invalid}


def stats_string(elem: dict, data: pd.DataFrame) -> dict:
    """Generate dict with valid and invalid values for nominal variables.

    Args:
        elem: Name, label and type of nominal variables.
        data: Datatable of imported data.

    Returns:
        Number of valid and invalid values.
    """

    frequencies = Counter(data[elem["name"]])
    string_missings = frequencies[""] + frequencies["."]
    valid = data[elem["name"]].value_counts().sum() - string_missings
    invalid = data[elem["name"]].isnull().sum() + string_missings

    return {"valid": int(valid), "invalid": int(invalid)}


def stats_number(elem: dict, data: pd.DataFrame) -> dict:
    """Generate dict with statistics for numerical variables

    Args:
        elem: Name, label and type of numerical variables.
        data: Datatable of imported data.

    Returns:
        Calculations for numerical variables.
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


def uni_statistics(elem: dict, data: pd.DataFrame) -> dict:
    """Call function to generate statistics depending on the variable type.

    Args:
        elem: Contains information of one variable.
        data: Datatable of imported data.

    Returns:
        statistics: Statistics for either categorical, nominal or
                    numerical variables.
    """

    if elem["type"] == "cat":
        statistics = stats_cat(elem, data)
    elif elem["type"] == "string":
        statistics = stats_string(elem, data)
    elif elem["type"] == "number":
        statistics = stats_number(elem, data)
    else:
        statistics = dict()

    return statistics


def uni(elem: dict, data: pd.DataFrame) -> OrderedDict:
    """Call function to generate frequencies depending on the variable type.

    Args:
        elem: Contains information of one variable.
        data: Datatable of imported data.

    Returns:
        statistics: Statistics for either categorical, nominal or
                    numerical variables.
    """

    statistics = OrderedDict()
    _type = elem["type"]
    type_functions = {"string": uni_string, "number": uni_number}

    if _type == "cat":
        statistics.update(uni_cat(elem, data))
    # We change this to else, if no other types exist
    elif _type in type_functions:
        statistics.update(type_functions[_type]())

    return statistics


def stat_dict(elem: dict, data: pd.DataFrame, metadata: dict, study: str) -> OrderedDict:
    """Fill variables with metadata of the dataset.

    Args:
        elem: Contains information of one variable.
        data: Datatable of imported data.
        metadata: Metadata of the imported data.
        study: Name of the study.

    Returns:
        meta_dict: Combined calculations and meta information.
    """

    scale = elem["type"][0:3]

    meta_dict = OrderedDict(
        study=study,
        dataset=metadata["name"],
        name=elem["name"],
        label=elem["label"],
        scale=scale,
        categories=uni(elem, data),
    )

    # For 10 or less values the statistics aren't shown.
    if elem["type"] in ("number", "cat"):
        data_withoutmissings = data[data[elem["name"]] >= 0][elem["name"]]
        if sum(Counter(data_withoutmissings.values).values()) > 10:
            meta_dict["statistics"] = uni_statistics(elem, data)
    else:
        meta_dict["statistics"] = uni_statistics(elem, data)

    return meta_dict


def generate_stat(data: pd.DataFrame, metadata: dict, study: str) -> list:
    """Prepare statistics for every variable.

    Args:
        data: Datatable of imported data.
        metadata: Metadata of the imported data.
        study: Name of the study.

    Returns:
        stat: Combine calculations and meta information.
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


def write_json(data: pd.DataFrame, metadata: dict, filename: str, study: str):
    """Main function to write json.

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
