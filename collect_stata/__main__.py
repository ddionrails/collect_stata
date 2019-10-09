"""Contains everything that enables cli usage of the package."""
__author__ = "Marius Pahl"

import argparse
import logging
import sys
import time
from multiprocessing import Process
from pathlib import Path

from collect_stata.read_stata import StataDataExtractor
from collect_stata.write_json import write_json


def main() -> None:
    """Provide cli argument parsing and initiate the data processing."""

    parser = argparse.ArgumentParser(
        description="Convert stata files to readable json files"
    )
    parser.add_argument("--input", "-i", help="Path to local stata files", required=True)
    parser.add_argument("--output", "-o", help="Path to output folder", required=True)
    parser.add_argument("--study", "-s", help="Study of the data", required=True)
    parser.add_argument(
        "--multiprocessing",
        "-m",
        action="store_true",
        help="Process stata files in parallel",
    )
    parser.add_argument(
        "--latin1",
        "-l",
        action="store_true",
        help=(
            "Set this if your source stata files "
            "are encoded with Latin-1 or  Windows-1252"
        ),
    )
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Set logging Level to DEBUG"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Set logging Level to INFO"
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args: argparse.Namespace = parser.parse_args()
    study = args.study
    input_path = Path(args.input)
    output_path = Path(args.output)
    run_parallel = args.multiprocessing
    latin1 = bool(args.latin1)

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    start_time = time.time()

    stata_to_json = StataToJson(
        study_name=study, input_path=input_path, output_path=output_path, latin1=latin1
    )

    if run_parallel:
        stata_to_json.parallel_run()
    else:
        stata_to_json.single_process_run()

    duration = time.time() - start_time
    logging.info("Duration {:.5f} seconds".format(duration))


class StataToJson:
    """Discover files to work on and handle top level data flow.

    Input:
    study_name: Name of the study
    input_path: path to data folder
    output_path: path to output folder

    This method reads stata file(s), transforms it in tabular data package.
    After this, it writes it out as csv and json files.
    """

    study: str
    input_path: Path
    output_path: Path
    latin1: bool

    def __init__(
        self, study_name: str, input_path: Path, output_path: Path, latin1: bool = False
    ) -> None:

        self.study = study_name
        self.input_path = input_path
        self.output_path = output_path
        self.latin1 = latin1

        output_path.mkdir(parents=True, exist_ok=True)

    def parallel_run(self) -> None:
        """Run processes per file in parallel."""
        # gather the processes
        processes = []
        for file in self.input_path.glob("*.dta"):
            process = Process(target=self._run, args=[file])
            processes.append(process)
            process.start()

        # complete the processes
        for process in processes:
            process.join()

    def single_process_run(self) -> None:
        """Run on files sequentially."""
        for file in self.input_path.glob("*.dta"):
            self._run(file=file)

    def _run(self, file: Path) -> None:
        """Encapsulate data processing run with multiprocessing."""
        output_file = self.output_path.joinpath(file.stem).with_suffix(".json")

        stata_data = StataDataExtractor(file)
        stata_data.parse_file()
        write_json(
            stata_data.data,
            stata_data.metadata,
            output_file,
            study=self.study,
            latin1=self.latin1,
        )


if __name__ == "__main__":
    main()
