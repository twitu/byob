import argparse
import sys
import os

from os.path import join
from generate_readables import generate_readables
from generate_csv import process_csv
from generate_doc import process_doc

parsing_modes = {
    'sparse': {
        'r_margin': 20,
        'c_margin': 10,
        'l_margin': 20,
        'm_margin': 20,
        'p_margin': 20
    },
    'dense': {
        'r_margin': 20,
        'c_margin': 10,
        'l_margin': 20,
        'm_margin': 10,
        'p_margin': 20
    },
    'standard':{
        'r_margin': 20,
        'c_margin': 10,
        'l_margin': 20,
        'm_margin': 15,
        'p_margin': 20
    }
}


def make_argument_parser():
    parser = argparse.ArgumentParser(description="Convert PDF to docs or profit and loss statements to CSV")
    parser.add_argument("-m", "--mode", help="set parsing mode, default value is standard", required=False, default="standard")
    path = parser.add_mutually_exclusive_group(required=True)
    path.add_argument("-f", "--file", help="convert given pdf")
    path.add_argument("-d", "--dir", help="convert all pdfs in given directory path")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--csv", help="store profit and loss table in csv", action="store_true")
    action.add_argument("--doc", help="convert file to doc", action="store_true")
    return parser


if __name__ == '__main__':
    args = make_argument_parser().parse_args()
    if args.mode not in parsing_modes:
        print("The entered mode is invalid. Possible modes are:")
        for mode_names in parsing_modes:
            print(" -", mode_names)
        exit()
    
    # either one of directory or file must be given
    if args.dir:
        if os.path.exists(args.dir) and os.path.isdir(args.dir):
            working_dir = args.dir
            # get all pdf files from given directory
            files = list(filter(lambda x: x.endswith(".pdf", os.listdir(working_dir))))
        else:
            print("given directory path is not valid")
            exit()
    else:
        if os.path.exists(args.file) and os.path.isfile(args.file):
            working_dir = os.path.dirname(args.file)
            files = [os.path.basename(args.file)]
        else:
            print("given file path is not valid")
            exit()

    # generate readable pdf ocr files and tehen convert them to parsable xml files
    generate_readables(working_dir, files)

    # either convert to doc or to csv
    for file_name in files:
        name = file_name.split(".")[0]
        if args.csv:
            print("generating csv from {}".format(file_name))
            process_csv(
                join(working_dir, "xml", name + ".xml"),
                join(working_dir, "csv", name + ".csv")
            )
        else:
            print("converting {} to doc".format(file_name))
            process_doc(
                join(working_dir, "xml", name + ".xml"),
                join(working_dir, "doc", name + ".doc"),
                parsing_modes[args.mode]
            )
