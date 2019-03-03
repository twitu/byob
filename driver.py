import argparse
import sys
from generate_readables import generate_readables

parsing_modes = {
    'sparse': {
        'r_margin': 20,
        'c_margin': 10
        'l_margin': 20,
    },
    'dense': {
        'r_margin': 20,
        'c_margin': 10
        'l_margin': 20,
    },
    'default':{
        'r_margin': 20,
        'c_margin': 10
        'l_margin': 20,
    }
}


def make_argument_parser():
    parser = argparse.ArgumentParser(
        description="Extract Profit and Loss Tables from financial report PDFs")
    parser.add_argument(
        "-m", "--mode", help="set default parsing mode", required = False)
    parser.add_argument(
        "-d", "--dir-path", help="set directory path")
    return parser


if __name__ == '__main__':
    args = make_argument_parser().parse_args()
    if args.mode is not None:
        args.mode = args.mode.lower()
        if args.mode not in parsing_modes:
            print("The entered mode is invalid. Possible modes are:")
            for mode_names in parsing_modes:
                print(" -", mode_names)
            exit()
    else:
        args.mode = parsing_modes['default']
    
    if args.dir-path is None:
        print("Please enter file / directory path for the files to convert")
        exit()

    generate_readables(dir_path)
    # Call functions to convert to xml
    # Use arguments from parsing_modes['key']
