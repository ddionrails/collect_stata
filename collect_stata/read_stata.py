"""read_stata.py"""
__author__ = "Marius Pahl"

import logging
import pathlib
import re

import pandas as pd


def cat_values(varscale, data):
    """
    Extract categorical metadata from stata files

    Input:
    varscale: dict
    data: pandas StataReader

    Output:
    cat_list: list
    """

    cat_list = list()

    label_dict = data.value_labels()

    for label in data.lbllist:
        if label == varscale["name"]:
            value_labels = label_dict[label]

    for value, label in value_labels.items():
        cat_list.append(dict(value=int(value), label=label))

    return cat_list


def scale_var(var, varscale, datatable):
    """
    Select vartype

    Input:
    var: string
    varscale: dict
    datatable: pandas DataFrame

    Output:
    var_type: string
    """

    if varscale["name"] != "":
        return "cat"
    var_type = str(datatable[var].dtype)
    match_float = re.search(r"float\d*", var_type)
    match_int = re.search(r"int\d*", var_type)
    if match_float or match_int:
        var_type = "number"
    if var_type == "object":
        var_type = "string"
    return var_type


def generate_tdp(datatable, stata_name, data):
    """
    Generate tabular data package file

    Input:
    datatable: pandas DataFrame
    stata_name: string
    data: pandas StataReader

    Output:
    tdp: dict
    """

    variables = data.varlist

    varlabels = data.variable_labels()

    varscales = [
        dict(name=varscale, sn=number) for number, varscale in enumerate(data.lbllist)
    ]

    dataset_name = pathlib.Path(stata_name).stem

    tdp = {}
    fields = []

    for var, varscale in zip(variables, varscales):
        scale = scale_var(var, varscale, datatable)
        meta = dict(name=var, label=varlabels[var], type=scale)
        if scale == "cat":
            meta["values"] = cat_values(varscale, data)

        fields.append(meta)

    schema = dict(fields=fields)

    resources = [dict(path=stata_name, schema=schema)]

    tdp.update(dict(name=dataset_name, resources=resources))

    return tdp


def parse_dataset(data, stata_name):
    """
    Create data and metadata

    Input:
    data: pandas StataReader
    stata_name: string

    Output:
    datatable: pandas DataFrame
    metadata: dict
    """

    datatable = data.read()

    metadata = generate_tdp(datatable, stata_name, data)

    return datatable, metadata


def read_stata(stata_name):
    """
    Read stata files (dta)

    Input:
    stata_name: string

    Output:
    datatable: pandas DataFrame
    metadata: dict
    """

    logging.info('read "%s"', stata_name)
    data = pd.read_stata(stata_name, iterator=True, convert_categoricals=False)
    datatable, metadata = parse_dataset(data, stata_name)

    return datatable, metadata
