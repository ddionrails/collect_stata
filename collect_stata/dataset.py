"""Read stata files and write out json files.

Read_stata and write_json are imported.
The class variables dataset and metadata are filled by the
read in data of read_stata and are used to write out the json file.

Example:
    dataset = Dataset()
    dataset.read_stata("../input/dataset.dta")
    dataset.write_json("../output/dataset.json")
"""
__author__ = "Marius Pahl"

from .read_stata import read_stata
from .write_json import write_json


class Dataset:
    """
    Dataset allows the user to read, test and export data in different formats.

    Attributes:
        dataset: Contains the data in tabular format.
        metadata: Contains the metadata in json format.
    """

    def __init__(self):
        self.dataset = None
        self.metadata = None

    def read_stata(self, dta_name: str):
        """Method to read data in stata format.

        Args:
            dta_name (str): Name of the data in stata format.

        Example:
            dataset.read_stata("../input/dataset.dta")
        """

        self.dataset, self.metadata = read_stata(dta_name)

    def write_json(self, output_name: str, study: str):
        """
        Method to write statistics from data in json/html format.

        Args:
            output_name (str): Name of the output file.
            study (str): Name of the study.

        Example:
            dataset.write_json("../output/dataset.html")
        """

        write_json(self.dataset, self.metadata, output_name, study=study)
