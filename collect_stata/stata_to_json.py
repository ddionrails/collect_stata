"""Read stata files and write out json files.
"""
__author__ = "Marius Pahl"

from .dataset import Dataset


def stata_to_json(study_name: str, input_path: str, output_path: str):
    """Method that reads all stata files from input path and
    writes out json files

    Args:
        study_name: Name of the study.
        input_path: Path to input folder.
        output_path: Path to output folder.
    """

    for file in input_path.glob("*.dta"):
        dataset = Dataset()
        fname = file.stem
        dataset.read_stata(str(file))
        dataset.write_json(str(output_path) + "/" + fname + ".json", study=study_name)
