"""write_json.py"""
__author__ = "Marius Pahl"

import json
from collections import Counter, OrderedDict

import numpy as np
import pandas as pd


def sorting_dataframe(values, labels, missings, frequencies):
    """Method to sort values and labels and return sorted dict"""
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

    stata_missings = {
        "4294967287": "-9",
        "4294967288": "-8",
        "4294967289": "-7",
        "4294967290": "-6",
        "4294967291": "-5",
        "4294967292": "-4",
        "4294967293": "-3",
        "4294967294": "-2",
        "4294967295": "-1",
    }

    value_count = file_csv[elem["name"]].value_counts()
    for value in elem["values"]:
        try:
            frequencies.append(int(value_count[value["value"]]))
        except KeyError:
            frequencies.append(0)
        labels.append(value["label"])

        var_value = str(value["value"])

        if int(value["value"]) >= 0 and var_value not in stata_missings:
            missings.append(False)
            values.append(var_value)
        else:
            missings.append(True)
            if var_value in stata_missings:
                values.append(stata_missings[var_value])
            else:
                values.append(var_value)

    cat_dict = sorting_dataframe(values, labels, missings, frequencies)

    return cat_dict


def uni_string():
    """Generate dict with frequencies for nominal variables

    Output:
    string_dict: OrderedDict
    """

    string_dict = OrderedDict()

    string_dict["frequencies"] = []
    string_dict["labels"] = []
    string_dict["missings"] = []
    string_dict["values"] = []

    return string_dict


def uni_number():
    """Generate dict with frequencies for numerical variables

    Output:
    number_dict: OrderedDict
    """
    number_dict = OrderedDict()

    number_dict["frequencies"] = []
    number_dict["labels"] = []
    number_dict["missings"] = []
    number_dict["values"] = []
    number_dict["labels_de"] = []

    return number_dict


def stats_cat(elem, file_csv):
    """Generate dict with statistics for categorical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    names = ["valid", "invalid"]
    values = []

    total = int(file_csv[elem["name"]].size)
    invalid = int(file_csv[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in file_csv[elem["name"]])
    )
    valid = total - invalid

    value_names = [valid, invalid]

    for value_name in value_names:
        values.append(str(value_name))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics


def stats_string(elem, file_csv):
    """Generate dict with statistics for nominal variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    names = ["valid", "invalid"]
    values = []

    int(file_csv[elem["name"]].size)
    valid = int(file_csv[elem["name"]].value_counts().sum())
    invalid = int(file_csv[elem["name"]].isnull().sum())
    for i in file_csv[elem["name"]]:
        if i in ("", "."):
            valid = valid - 1
            invalid = invalid + 1

    value_names = [valid, invalid]

    for value_name in value_names:
        values.append(str(value_name))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics


def stats_number(elem, file_csv):
    """Generate dict with statistics for numerical variables

    Input:
    elem: dict
    file_csv: pandas DataFrame

    Output:
    statistics: OrderedDict
    """

    data_wm = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]

    names = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max.", "valid", "invalid"]
    values = []

    mid = int(len(sorted(data_wm)) / 2)
    first_q = np.median(sorted(data_wm)[:mid])
    if len(sorted(data_wm)) % 2 == 0:
        third_q = np.median(sorted(data_wm)[mid:])
    else:
        third_q = np.median(sorted(data_wm)[mid + 1 :])

    total = int(file_csv[elem["name"]].size)
    invalid = int(file_csv[elem["name"]].isnull().sum()) + int(
        sum(n < 0 for n in file_csv[elem["name"]])
    )
    valid = total - invalid

    value_names = [
        min(data_wm),
        first_q,
        np.median(data_wm),
        np.mean(data_wm),
        third_q,
        max(data_wm),
        valid,
        invalid,
    ]

    for value_name in value_names:
        values.append(str(value_name))

    statistics = OrderedDict([("names", names), ("values", values)])

    return statistics


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

    if elem["type"] == "cat":
        cat_dict = uni_cat(elem, file_csv)

        statistics.update(cat_dict)

    elif elem["type"] == "string":

        string_dict = uni_string()

        statistics.update(string_dict)

    elif elem["type"] == "number":

        number_dict = uni_number()

        statistics.update(number_dict)

    else:
        pass

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
    meta_dict["dataset"] = file_json["name"].lower()
    meta_dict["name"] = elem["name"]
    meta_dict["label"] = elem["label"]
    meta_dict["scale"] = scale
    meta_dict["categories"] = uni(elem, file_csv)

    # For 10 or less values the statistics aren't shown.

    if elem["type"] == "number" or elem["type"] == "cat":
        data_wm = file_csv[file_csv[elem["name"]] >= 0][elem["name"]]
        if sum(Counter(data_wm.values).values()) > 10:
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

    i = 1
    for elem in elements:
        print(str(i) + "/" + str(elements_length))
        i = i + 1
        try:
            stat.append(stat_dict(elem, data, metadata, study))
        except KeyError as exception:
            print(exception)

    return stat


def write_json(data, metadata, filename, study=""):
    """Main function to write json.

    Input:
    data: pandas DataFrame (later called file_csv)
    metadata: dict (later called file_json)
    filename: string
    study: string
    """

    stat = generate_stat(data, metadata, study)

    print('write "' + filename + '"')
    with open(filename, "w") as json_file:
        json.dump(stat, json_file, indent=2)
