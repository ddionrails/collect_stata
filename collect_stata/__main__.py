"""__main__.py"""
__author__ = "Marius Pahl"

import argparse
import logging
import pathlib
import sys

from collect_stata.read_stata import read_stata
from collect_stata.write_json import write_json


def main():
    """ Implements cli argument parsing and initiates the data processing."""

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
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    study = args.study
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    stata_to_json(study_name=study, input_path=input_path, output_path=output_path)


def stata_to_json(study_name: str, input_path: pathlib.Path, output_path: pathlib.Path):
    """

    This method reads stata file(s),
    transforms it into a tabular data package.
    TODO: But why do we need a tabular datapackage?
    After this, it writes it out as csv and json files.

    Args:
        study_name: Name of the study that is being processed.
        input_path: Path to the folder, that contains the stata files.
        output_path: Folder path to write the output data to.
    """

    output_path.mkdir(parents=True, exist_ok=True)

    for file in input_path.glob("*.dta"):
        file_path = output_path.joinpath(file.stem).with_suffix(".json")

        dataset, metadata = read_stata(file)
        write_json(dataset, metadata, file_path, study=study_name)
