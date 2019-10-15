"""Process stata dta files with pandas StataReader."""
__author__ = "Marius Pahl"

import pathlib
import re
import warnings
from typing import Dict, List, Union

import pandas
import pandas.io.stata
from pandas.api.types import is_numeric_dtype


class StataDataExtractor:
    """Extract metadata and data from a stata file

    Args:
        file_name: The location of the stata file to be processed.

    Attributes:
        file_name: The location of the stata file to be processed.
        reader: The reader object created withe the stata file.
                Metadata is obtained from this object. Actual data is
                read from it into a pandas.DataFrame.
        data: The actual data parsed from the stata file. Is initiated empty.
                To parse the data, the method parse_file() has to be called.
        metadata: The metadata obtained from the reader. Is initiated empty.
                    To parse the data, the method parse_file() has to be called.
    """

    file_name: pathlib.Path
    reader: pandas.io.stata.StataReader
    data: pandas.DataFrame
    metadata: List[Dict[str, Union[str, Dict[str, List]]]]

    def __init__(self, file_name: pathlib.Path):
        self.file_name = file_name
        self.reader = pandas.read_stata(
            file_name, iterator=True, convert_categoricals=False
        )
        self.data = pandas.DataFrame()
        self.metadata = list()

    def parse_file(self):
        """Initiate reading of the data and metadata."""
        self.data = self.reader.read()
        self.metadata = self.get_variable_metadata()

    def get_variable_metadata(self) -> List[Dict[str, Union[str, Dict[str, List]]]]:
        """Gather metadata about variables in the data.

        Stores computed metadata in the attribute metadata.
        If metadata was already filled by a previous run, the metadata will not
        be collected again. Instead it will return metadata.

        Returns:
            A list with a dictionary for every variable.
            For a detailed description of the dictionary see the test documentation
            for this at collect_stata.tests.test_read_stata
        """

        if self.metadata:
            return self.metadata

        dataset = pathlib.Path(self.file_name).stem

        variable_labels = self.reader.variable_labels()
        value_labels = self.reader.value_labels()
        for variable in self.reader.varlist:
            variable_meta = dict()
            variable_meta["name"] = variable
            variable_meta["dataset"] = dataset
            variable_meta["label"] = variable_labels.get(variable, None)
            variable_meta["categories"] = {"values": [], "labels": []}
            for value, label in value_labels.get(variable, dict()).items():
                # At the moment if a variable has value labels attached, it is
                # interpretet as being on a categorical scale.
                variable_meta["scale"] = "cat"

                variable_meta["categories"]["values"].append(value)
                variable_meta["categories"]["labels"].append(label)

            if "scale" not in variable_meta:
                variable_meta["scale"] = self.get_variable_scale(
                    self.reader.varlist.index(variable)
                )
            self.metadata.append(variable_meta)

        return self.metadata

    def get_variable_scale(self, variable_index: int) -> str:
        """Guess a variables scale.

        At this point it is unclear what could be used to identify the
        scale of a variable.
        The implementation here follows the old method to identify scales that
        are not categorical ("cat"), with the exception, that the datatype is
        identified by using the pandas.io.stata.StataReader generator instead of
        reading the whole data into a pandas DataFrame first.

        Args:
            variable_index: Index of a variable from the list returned by
            StataReader.variable_labels(). This index is used to retrieve the
            datatype from the same index position in the StataReader.dtypelist.

        Returns:
            str: [description]
        """
        warnings.warn(
            "This method uses a questionable way of determining a variables scale.",
            DeprecationWarning,
        )
        variable_dtype = self.reader.dtyplist[variable_index]
        if is_numeric_dtype(variable_dtype):
            return "number"
        if variable_dtype == "object":
            return "string"
        return str(variable_dtype)

    def generate_tdp(self):
        """
        Generate tabular data package file

        Input:
        datatable: pandas DataFrame
        stata_name: string
        data: pandas StataReader

        Output:
        tdp: dict
        """
        warnings.warn(
            "This method creates an old datastructure and will be deprecated.",
            DeprecationWarning,
        )

        variables = self.reader.varlist

        varlabels = self.reader.variable_labels()

        varscales = [
            dict(name=varscale, sn=number)
            for number, varscale in enumerate(self.reader.lbllist)
        ]

        dataset_name = pathlib.Path(self.file_name).stem

        tdp = {}
        fields = []

        for var, varscale in zip(variables, varscales):
            scale = self.cat_val(var, varscale)
            meta = dict(name=var, label=varlabels[var], type=scale)
            if scale == "cat":
                meta["values"] = self.extract_category_value_labels(varscale)

            fields.append(meta)

        schema = dict(fields=fields)

        resources = [dict(path=self.file_name, schema=schema)]

        tdp.update(dict(name=dataset_name, resources=resources))

        return tdp

    def cat_val(self, var: str, varscale: dict):
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
        var_type = str(self.data[var].dtype)
        match_float = re.search(r"float\d*", var_type)
        match_int = re.search(r"int\d*", var_type)
        if match_float or match_int:
            var_type = "number"
        if var_type == "object":
            var_type = "string"
        return var_type

    def extract_category_value_labels(self, varscale):
        """
        Extract categorical metadata from stata files

        Input:
        varscale: dict
        data: pandas StataReader

        Output:
        cat_list: list
        """

        cat_list = list()

        label_dict = self.reader.value_labels()

        for label in self.reader.lbllist:
            if label == varscale["name"]:
                value_labels = label_dict[label]

        for value, label in value_labels.items():
            cat_list.append(dict(value=int(value), label=label))

        return cat_list
