"""Contains everything that enables cli usage of the package."""
__author__ = "Marius Pahl"

import argparse
import logging
import os
import pathlib
import sys
import time
from multiprocessing import Process
from typing import Optional

from collect_stata.read_stata import StataDataExtractor
from collect_stata.write_json import write_json


def main() -> None:
    """Provide cli argument parsing and initiate the data processing."""

    parser = argparse.ArgumentParser(
        description="Convert stata files to readable json files"
    )
    parser.add_argument("--input", "-i", help="Path to local english stata files")
    parser.add_argument("--input_german", "-g", help="Path to local german stata files")
    parser.add_argument("--output", "-o", help="Path to output folder", required=True)
    parser.add_argument("--study", "-s", help="Study of the data", required=True)
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Set logging Level to DEBUG"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Set logging Level to INFO"
    )
    parser.add_argument(
        "--multiprocessing",
        "-m",
        action="store_true",
        help="Process stata files in parallel",
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.input is None and args.input_german is None:
        parser.error("At least one input required")
    study = args.study
    input_path = pathlib.Path(args.input) if args.input is not None else None
    input_german_path = (
        pathlib.Path(args.input_german) if args.input_german is not None else None
    )
    output_path = pathlib.Path(args.output)
    run_parallel = args.multiprocessing

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    stata_to_json(
        study_name=study,
        input_path=input_path,
        input_german_path=input_german_path,
        output_path=output_path,
        run_parallel=run_parallel,
    )


def stata_to_json(
    study_name: str,
    input_path: Optional[pathlib.Path],
    input_german_path: Optional[pathlib.Path],
    output_path: pathlib.Path,
    run_parallel: bool = True,
) -> None:
    """Discover files to work on and handle top level data flow.

    Input:
    study_name: Name of the study
    input_path: path to english data folder
    input_german_path: path to german data folder
    output_path: path to output folder

    This method reads stata file(s), transforms it in tabular data package.
    After this, it writes it out as csv and json files.
    """

    output_path.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    if run_parallel:
        # gather the processes
        processes = []
        if input_path is None and input_german_path is not None:
            for file_de in input_german_path.glob("*.dta"):
                process = Process(
                    target=_run, args=(None, file_de, output_path, study_name)
                )
                processes.append(process)
                process.start()
        if input_german_path is None and input_path is not None:
            for file in input_path.glob("*.dta"):
                process = Process(target=_run, args=(file, None, output_path, study_name))
                processes.append(process)
                process.start()
        if input_path is not None and input_german_path is not None:
            for file in input_path.glob("*.dta"):
                file_de = pathlib.Path(
                    str(input_german_path) + "/" + os.path.basename(str(file))
                )
                process = Process(
                    target=_run, args=(file, file_de, output_path, study_name)
                )
                processes.append(process)
                process.start()

        # complete the processes
        for process in processes:
            process.join()
    else:
        if input_path is None and input_german_path is not None:
            for file_de in input_german_path.glob("*.dta"):
                _run(
                    file=None,
                    file_de=file_de,
                    output_path=output_path,
                    study_name=study_name,
                )
        if input_german_path is None and input_path is not None:
            for file in input_path.glob("*.dta"):
                _run(
                    file=file,
                    file_de=None,
                    output_path=output_path,
                    study_name=study_name,
                )
        if input_path is not None and input_german_path is not None:
            for file in input_path.glob("*.dta"):
                file_de = pathlib.Path(
                    str(input_german_path) + "/" + os.path.basename(str(file))
                )
                _run(
                    file=file,
                    file_de=file_de,
                    output_path=output_path,
                    study_name=study_name,
                )

    duration = time.time() - start_time
    logging.info("Duration {:.5f} seconds".format(duration))


def _run(
    file: Optional[pathlib.Path],
    file_de: Optional[pathlib.Path],
    output_path: pathlib.Path,
    study_name: str,
) -> None:
    """Encapsulate data processing run with multiprocessing."""
    if file is None:
        file_path = output_path.joinpath(file_de.stem).with_suffix(".json")
        stata_data_de = StataDataExtractor(file_de)
        stata_data_de.parse_file()
        data = stata_data_de.data
        metadata_english = None
        metadata_german = stata_data_de.metadata

    if file is not None:
        file_path = output_path.joinpath(file.stem).with_suffix(".json")
        stata_data = StataDataExtractor(file)
        stata_data.parse_file()
        data = stata_data.data
        metadata_english = stata_data.metadata
        metadata_german = None
        if file_de is not None:
            stata_data_de = StataDataExtractor(file_de)
            metadata_german = stata_data_de.get_variable_metadata()

    write_json(
        data, metadata_english, metadata_german, file_path, study=study_name,
    )


if __name__ == "__main__":
    main()
