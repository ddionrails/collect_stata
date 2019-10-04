"""Process stata dta files with pandas StataReader."""
__author__ = "Marius Pahl"

import pathlib
import re
from typing import Dict, List

import pandas


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

    def __init__(self, file_name: pathlib.Path):
        self.file_name: pathlib.Path = file_name
        self.reader: pandas.io.stata.StataReader = pandas.read_stata(
            file_name, iterator=True, convert_categoricals=False
        )
        self.data: pandas.DataFrame = pandas.DataFrame()
        self.metadata: dict = dict()

    def parse_file(self):
        """Initiate reading of the data and metadata."""
        self.data = self.reader.read()
        self.metadata = self.extract_metadata()

    def extract_metadata(self) -> dict:
        """Get metadata information and return a dict.

        Returns:
            metadata: Contains datasetname, inputpath and var- and valuelabels
        """

        variables = self.reader.varlist

        varlabels = self.reader.variable_labels()

        varscales = [
            dict(name=varscale, sn=number)
            for number, varscale in enumerate(self.reader.lbllist)
        ]

        dataset_name = pathlib.Path(self.file_name).stem

        metadata = {}
        fields = []

        for var, varscale in zip(variables, varscales):
            scale = self.get_variable_type(var, varscale)
            meta = dict(name=var, label=varlabels[var], type=scale)
            if scale == "cat":
                meta["values"] = self.extract_category_value_labels(varscale)

            fields.append(meta)

        schema = dict(fields=fields)

        resources = [dict(path=self.file_name, schema=schema)]

        metadata.update(dict(name=dataset_name, resources=resources))

        return metadata

    def get_variable_type(self, variable_name: str, varscale: dict) -> str:
        """Exctract variable type and return it as string.

        Args:
            variable_name: Name of the variable.
            varscale: Dictionary of the scale of the variables.
        Returns:
            The type of the variable, either cat, number or string.
        """

        if varscale["name"] != "":
            return "cat"
        var_type = str(self.data[variable_name].dtype)
        match_float = re.search(r"float\d*", var_type)
        match_int = re.search(r"int\d*", var_type)
        if match_float or match_int:
            var_type = "number"
        if var_type == "object":
            var_type = "string"
        return var_type

    def extract_category_value_labels(self, varscale) -> List[Dict[str, str]]:
        """Extract categorical metadata from stata files.

        Args:
            varscale (dict): Dictionary of the scale of the variables.
        Returns:
            List of categorical variables with labels.
        """

        cat_list = list()

        label_dict = self.reader.value_labels()

        for label in self.reader.lbllist:
            if label == varscale["name"]:
                value_labels = label_dict[label]

        for value, label in value_labels.items():
            cat_list.append(dict(value=int(value), label=label))

        return cat_list
