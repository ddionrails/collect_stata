"""stata_to_json.py"""
__author__ = "Marius Pahl"

import logging
import time
from multiprocessing import Process
from pathlib import Path

from .dataset import Dataset


def run(file: Path, output_path: Path, study_name: str) -> None:
    """Helper function that runs in parallel."""
    dataset = Dataset()
    dataset.read_stata(str(file))
    dataset.write_json(
        output_path.joinpath(file.stem).with_suffix(".json"), study=study_name
    )


def stata_to_json(study_name, input_path, output_path):
    """
    Input:
    study_name: Name of the study
    input_path: path to data folder
    output_path: path to output folder

    This method reads stata file(s), transforms it in tabular data package.
    After this, it writes it out as csv and json files.
    """

    # gather the processes
    start_time = time.time()
    processes = []
    for file in input_path.glob("*.dta"):
        process = Process(target=run, args=(file, output_path, study_name))
        processes.append(process)
        process.start()

    # complete the processes
    for process in processes:
        process.join()

    duration = time.time() - start_time
    logging.info(f"Duration {duration:.5f} seconds")
