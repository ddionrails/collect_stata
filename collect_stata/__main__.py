"""Contains everything that enables cli usage of the package."""
__author__ = "Marius Pahl"

import argparse
import logging
import pathlib
import sys
import time
from multiprocessing import Process

from collect_stata.read_stata import StataDataExtractor
from collect_stata.write_json import write_json


def main():
    """Provide cli argument parsing and initiate the data processing."""

    parser = argparse.ArgumentParser(
        description="Convert stata files to readable json files"
    )
    parser.add_argument("--input", "-i", help="Path to local stata files", required=True)
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
    study = args.study
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)
    run_parallel = args.multiprocessing

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    stata_to_json(
        study_name=study,
        input_path=input_path,
        output_path=output_path,
        run_parallel=run_parallel,
    )


def stata_to_json(study_name, input_path, output_path, run_parallel=True):
    """Discover files to work on and handle top level data flow.

    Input:
    study_name: Name of the study
    input_path: path to data folder
    output_path: path to output folder

    This method reads stata file(s), transforms it in tabular data package.
    After this, it writes it out as csv and json files.
    """

    output_path.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    if run_parallel:
        # gather the processes
        processes = []
        for file in input_path.glob("*.dta"):
            process = Process(target=_run, args=(file, output_path, study_name))
            processes.append(process)
            process.start()

        # complete the processes
        for process in processes:
            process.join()
    else:
        for file in input_path.glob("*.dta"):
            _run(file=file, output_path=output_path, study_name=study_name)

    duration = time.time() - start_time
    logging.info("Duration {:.5f} seconds".format(duration))


def _run(file: pathlib.Path, output_path: pathlib.Path, study_name: str) -> None:
    """Encapsulate data processing run with multiprocessing."""
    file_path = output_path.joinpath(file.stem).with_suffix(".json")

    stata_data = StataDataExtractor(file)
    stata_data.parse_file()
    write_json(stata_data.data, stata_data.metadata, file_path, study=study_name)


if __name__ == "__main__":
    main()
