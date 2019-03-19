from tkinter import *
from tkinter import filedialog
import argparse
import sys
import os

from os.path import join
from generate_readables import generate_readables
from generate_csv import process_csv
from generate_doc import process_doc
from functools import partial


# list of parsing modes
# line margin vertical margin for getting lines
# merge margin horizontal margin for clubbing words
# adj margin for vertical distance between lines for marking
# large cutoff ratio of line with page to call as para
# para margin to club lines into paragraphs
# column margin horizontal margin between columns
parsing_modes = {
    'standard': {
        'line_margin': 10,
        'merge_margin': 15,
        'adj_margin': 15,
        'large_cutoff': 0.6,
        'para_margin': 20,
        'column_margin': 20
    }
}


def make_argument_parser():
    parser = argparse.ArgumentParser(
        description="Convert PDF to docs or profit and loss statements to CSV")
    parser.add_argument("-m", "--mode", help="set parsing mode, default value is standard",
                        required=False, default="standard")
    parser.add_argument(
        "-p", "--path", help="give input path for file or directory", required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--csv", help="store profit and loss table in csv", action="store_true")
    action.add_argument("--doc", help="convert file to doc",
                        action="store_true")
    return parser


if __name__ == "__main__":

    # get parsing mode
    args = make_argument_parser().parse_args()
    if args.mode not in parsing_modes:
        print("The entered mode is invalid. Possible modes are:")
        for mode_names in parsing_modes:
            print(" -", mode_names)
        exit()

    # check given path and set working directory for making readable files
    input_path = args.path
    if os.path.exists(input_path) and os.path.isdir(input_path):
        working_dir = input_path
        files = list(filter(lambda x: x.endswith(
            ".pdf"), os.listdir(working_dir)))
    elif os.path.exists(input_path) and os.path.isfile(input_path):
        working_dir = os.path.dirname(input_path)
        files = [os.path.basename(input_path)]
    else:
        print("Status: Entered file / directory path is not valid")
        exit()

    # log files found
    print("Found the following files:")
    for file in files:
        print(file)

    # generate readable files from pdfs i.e. ocr pdf and xml
    generate_readables(working_dir, files)

    # call function to generate csv or doc
    for file_name in files:
        name = file_name.split(".")[0]
        if args.doc:
            print("Converting {} to Doc".format(name))
            process_doc(
                join(working_dir, "xml", name + ".xml"),
                join(working_dir, "doc", name + ".doc"),
                parsing_modes[args.mode],
            )
        else:
            print("Converting {} to CSV".format(name))
            process_csv(
                join(working_dir, "xml", name + ".xml"),
                join(working_dir, "csv", name + ".csv"),
                parsing_modes[args.mode],
            )

    print("SUCCESS: Files converted successfully")
