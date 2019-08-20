"""__main__.py"""
__author__ = "Marius Pahl"

import argparse
import pathlib
import sys

from collect_stata.stata_to_json import stata_to_json


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Convert stata files to readable json files"
    )
    parser.add_argument("--input", "-i", help="Path to local stata files")
    parser.add_argument("--output", "-o", help="Path to output folder")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    stata_to_json(study_name="soep-core", input_path=input_path, output_path=output_path)


if __name__ == "__main__":
    main()
