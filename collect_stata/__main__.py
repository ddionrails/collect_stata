"""__main__.py"""
__author__ = "Marius Pahl"

import argparse
import logging
import pathlib
import sys

from collect_stata.stata_to_json import stata_to_json


def main():
    """The main routine."""
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
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    study = args.study if args.study else ""
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    stata_to_json(study_name=study, input_path=input_path, output_path=output_path)


if __name__ == "__main__":
    main()
