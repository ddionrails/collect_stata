"""stata_to_json.py"""
__author__ = "Marius Pahl"

from .dataset import Dataset


def stata_to_json(study_name, input_path, output_path):
    """
    Input:
    study_name: Name of the study
    input_path: path to data folder
    output_path: path to output folder

    This method reads stata file(s), transforms it in tabular data package.
    After this, it writes it out as csv and json files.
    """

    for file in input_path.glob("*.dta"):
        dataset = Dataset()
        fname = file.stem
        dataset.read_stata(str(file))
        dataset.write_json(str(output_path) + "/" + fname + ".json", study=study_name)
