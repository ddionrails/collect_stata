"""Process stata dta files with pandas StataReader."""
__author__ = "Marius Pahl"

import pathlib
import warnings
from typing import List

import pandas
import pandas.io.stata
from pandas.api.types import is_numeric_dtype

from collect_stata.types import Variable


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
    metadata: List[Variable]

    def __init__(self, file_name: pathlib.Path):
        self.file_name = file_name
        self.reader = pandas.read_stata(
            file_name, iterator=True, convert_categoricals=False
        )
        self.data = pandas.DataFrame()
        self.metadata = list()

    def parse_file(self) -> None:
        """Initiate reading of the data and metadata."""
        self.data = self.reader.read()
        self.metadata = self.get_variable_metadata()

    def get_variable_metadata(self) -> List[Variable]:
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
            variable_meta: Variable = Variable()
            variable_meta["name"] = variable
            variable_meta["dataset"] = dataset
            variable_meta["label"] = variable_labels.get(variable, None)
            variable_meta["categories"] = {"values": [], "labels": []}
            for value, label in value_labels.get(variable, dict()).items():
                # At the moment if a variable has value labels attached, it is
                # interpretet as being on a categorical scale.
                variable_meta["scale"] = "cat"

                variable_meta["categories"]["values"].append(int(value))
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
