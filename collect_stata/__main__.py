"""Contains everything that enables cli usage of the package."""
__author__ = "Marius Pahl"

import argparse
import logging
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path
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

    if args.input is None and args.input_german is None:
        parser.error("At least one input required")
    study = args.study
    input_path = Path(args.input) if args.input is not None else None
    input_german_path = Path(args.input_german) if args.input_german is not None else None
    output_path = Path(args.output)

    run_parallel = args.multiprocessing
    latin1 = bool(args.latin1)

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    start_time = time.time()

    stata_to_json = StataToJson(
        study_name=study,
        input_path=input_path,
        input_german_path=input_german_path,
        output_path=output_path,
        latin1=latin1,
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
    input_path: path to english data folder
    input_german_path: path to german data folder
    output_path: path to output folder

    This method reads stata file(s), transforms it in tabular data package.
    After this, it writes it out as csv and json files.
    """

    study: str
    input_path: Optional[Path]
    input_german_path: Optional[Path]
    output_path: Path
    latin1: bool

    def __init__(  # pylint: disable=too-many-arguments
        self,
        study_name: str,
        input_path: Optional[Path],
        input_german_path: Optional[Path],
        output_path: Path,
        latin1: bool = False,
    ) -> None:

        self.study = study_name
        self.input_path = input_path
        self.input_german_path = input_german_path
        self.output_path = output_path
        self.latin1 = latin1

        output_path.mkdir(parents=True, exist_ok=True)

    def parallel_run(self) -> None:
        """Run processes per file in parallel."""
        # gather the processes
        processes = []
        if self.input_path is None and self.input_german_path is not None:
            for file_de in self.input_german_path.glob("*.dta"):
                process = Process(target=self._run, args=[None, file_de])
        elif self.input_german_path is None and self.input_path is not None:
            for file in self.input_path.glob("*.dta"):
                process = Process(target=self._run, args=[file, None])
        elif self.input_path is not None and self.input_german_path is not None:
            for file in self.input_path.glob("*.dta"):
                file_de = Path(
                    str(self.input_german_path) + "/" + os.path.basename(str(file))
                )
                process = Process(target=self._run, args=[file, file_de])

                processes.append(process)
                process.start()

        # complete the processes
        for process in processes:
            process.join()

    def single_process_run(self) -> None:
        """Run on files sequentially."""
        if self.input_path is None and self.input_german_path is not None:
            for file_de in self.input_german_path.glob("*.dta"):
                self._run(file=None, file_de=file_de)
        if self.input_german_path is None and self.input_path is not None:
            for file in self.input_path.glob("*.dta"):
                self._run(file=file, file_de=None)
        if self.input_path is not None and self.input_german_path is not None:
            for file in self.input_path.glob("*.dta"):
                file_de = Path(
                    str(self.input_german_path) + "/" + os.path.basename(str(file))
                )
                self._run(file=file, file_de=file_de)

    def _run(self, file: Optional[Path], file_de: Optional[Path]) -> None:
        """Encapsulate data processing run with multiprocessing."""
        if file is None:
            return None

        if file is not None:
            output_file = self.output_path.joinpath(file.stem).with_suffix(".json")
            stata_data = StataDataExtractor(file)
            stata_data.parse_file()
            data = stata_data.data
            metadata_english = stata_data.metadata
            metadata_german = None
            if file_de is not None:
                stata_data_de = StataDataExtractor(file_de)
                metadata_german = stata_data_de.get_variable_metadata()

        write_json(
            data,
            metadata_english,
            metadata_german,
            output_file,
            study=self.study,
            latin1=self.latin1,
        )
        return None


if __name__ == "__main__":
    main()
