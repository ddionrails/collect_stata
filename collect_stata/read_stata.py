"""read_stata.py"""
__author__ = "Marius Pahl"

import logging
import pathlib
import re

import pandas as pd


def cat_values(varscale: dict, data) -> list:
    """Extract categorical metadata from stata files

    Args:
        varscale (dict): Dictionary of the scale of the variables.
        data (pandas StataReader): Imported dataset.

    Returns:
        cat_list (list): List of categorical variables with labels.
    """

    cat_list = list()
    label_dict = data.value_labels()

    for label in data.lbllist:
        if label == varscale["name"]:
            value_labels = label_dict[label]

    for value, label in value_labels.items():
        cat_list.append(dict(value=int(value), label=label))

    return cat_list


def scale_var(var: str, varscale: dict, datatable) -> str:
    """Select vartype

    Args:
        var (string): Name of the variable.
        varscale (dict): Dictionary of the scale of the variables.
        datatable (pandas DataFrame): Imported dataset.

    Returns:
        var_type (string): Returns the type of the variable, either cat, number or string.
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


def generate_tdp(data, stata_name: str):
    """Generate tabular data package file

    Args:
        stata_name (string): Name of the stata file.
        data (pandas StataReader): Raw data.

    Returns:
        datatable (pandas DataFrame): Readable data.
        metadata (dict): Meta information for the data.
    """

    variables = data.varlist
    varlabels = data.variable_labels()
    datatable = data.read()
    dataset_name = pathlib.Path(stata_name).stem
    metadata = {}
    fields = []
    varscales = [
        dict(name=varscale, sn=number) for number, varscale in enumerate(data.lbllist)
    ]

    for var, varscale in zip(variables, varscales):
        scale = scale_var(var, varscale, datatable)
        meta = dict(name=var, label=varlabels[var], type=scale)
        if scale == "cat":
            meta["values"] = cat_values(varscale, data)

        fields.append(meta)

    schema = dict(fields=fields)
    resources = [dict(path=stata_name, schema=schema)]
    metadata.update(dict(name=dataset_name, resources=resources))

    return datatable, metadata


def read_stata(stata_name):
    """Logging and reading stata files

    Args:
        stata_name (string): Name of the stata file.

    Returns:
        datatable (pandas DataFrame): Readable data.
        metadata (dict): Meta information for the data.
    """

    logging.info('read "%s"', stata_name)
    data = pd.read_stata(stata_name, iterator=True, convert_categoricals=False)
    datatable, metadata = generate_tdp(data, stata_name)

    return datatable, metadata
