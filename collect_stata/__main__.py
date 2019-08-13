"""__main__.py"""
__author__ = "Marius Pahl"

import argparse
import sys

from collect_stata.stata_to_json import stata_to_json


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
        print(args)

    parser = argparse.ArgumentParser(description="Get input and output information")
    parser.add_argument("--i", "--input", help="get input path")
    parser.add_argument("--o", "--output", help="get output path")
    args = parser.parse_args()

    stata_to_json(study_name="soep-core", input_path=args.i, output_path=args.o)


if __name__ == "__main__":
    main()
