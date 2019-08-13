"""stata_to_json.py"""
__author__ = "Marius Pahl"

import glob
import os

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
    files_path = glob.glob(input_path + "/*.dta")

    for file in files_path:
        dataset_1 = Dataset()
        fname = os.path.splitext(os.path.basename(file))[0]
        try:
            dataset_1.read_stata(file)
        except IOError:
            print("[ERROR]: file not found")
            continue

        dataset_1.write_json(output_path + fname + ".json", study=study_name)
