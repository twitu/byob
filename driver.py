import argparse
import sys
from generate_readables import generate_readables
from parse_table import *

parsing_modes = {
    'sparse': {
        'r_margin': 20,
        'c_margin': 10
        'l_margin': 20,
        'm_margin': 20,
        'p_margin': 20
    },
    'dense': {
        'r_margin': 20,
        'c_margin': 10
        'l_margin': 20,
        'm_margin': 20,
        'p_margin': 20
    },
    'default':{
        'r_margin': 20,
        'c_margin': 10
        'l_margin': 20,
        'm_margin': 20,
        'p_margin': 20
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
        args.mode = 'default'
    
    if args.dir-path is None:
        print("Please enter file / directory path for the files to convert")
        exit()

    generate_readables(args.dir-path)

    if os.path.isdir(args.dir-path):
        files = os.listdir(args.dir-path)
    else:
        files = [args.dir-path]

    for file_name in files:
        document = Document()

        xml_file = tree.parse(file_name).getroot()
        for page in xml_file.getchildren():
            page_box = Rectangle(list(map(float, page.attrib["bbox"].split(","))))
            page_mid = (page_box.x1 + page_box.x2)/2
            page_width = page_box.x2 - page_box.x1
            lines = get_lines(page, parsing_modes[args.mode]['l_margin'])
            lines = merge_words(lines, parsing_modes[args.mode]['m_margin'])
            lines.sort(reverse=True)

            # filter and mark names with appropriate types
            filter_and_mark(lines, page_box)

            # group lines by type and print in docx
            for k, g in groupby(lines, key=lambda x: x.type):
                if k == LineType.CENTRE:
                    print_centre_text(list(g), document)
                elif k == LineType.PARA:
                    print_paragraph_text(list(g), document, page_box)
                elif k == LineType.TABLE:
                    print_table_text(list(g), document)

            # create new page break after adding all lines from current page of pdf
            document.add_page_break()

        document.save(file_name.split(".")[0] + ".docx")
