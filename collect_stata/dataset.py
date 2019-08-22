"""dataset.py"""
__author__ = "Marius Pahl"

from .read_stata import read_stata
from .write_json import write_json


class Dataset:
    """
    Dataset allows the user to read, test and export data in different formats.

    Example:

        dataset = Dataset()
        dataset.read_stata("../input/dataset.dta")
        dataset.write_json("../output/dataset.json")
    """

    def __init__(self):
        self.dataset = None
        self.metadata = None

    def read_stata(self, dta_name):
        """
        Function to read data in stata format.

        Parameter:

        dta_name: Name of the data in stata format

        Example:

        dataset.read_stata("../input/dataset.dta")
        """
        self.dataset, self.metadata = read_stata(dta_name)

    def write_json(self, output_name, study=""):
        """
        Function to write statistics from data in json/html format.

        Parameter:

        output_name: Name of the output file

        Example:

        dataset.write_json("../output/dataset.html")
        """
        write_json(self.dataset, self.metadata, output_name, study=study)
