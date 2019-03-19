import xml.etree.ElementTree as tree
import csv
import json
import spell_fixer
import sys

from docx import Document
from text_objects import Rectangle, Word, Line, LineType, Column
from text_objects import get_lines, get_columns
from text_objects import centre_aligned, merge_words, check_fix_spellings

triage_data = {
    "interest receivable and similar income": "Interest Receivable",
    "other interest receivable and similar income": "Interest Receivable",
    "interest payable and similar expenses": "Interest payable and similar charges",
    "interest payable and expenses": "Interest payable and similar charges",
    "profit before taxation": "Profit on ordinary activities before taxation",
    "loss before taxation": "Profit on ordinary activities before taxation",
    "profit before tax": "Profit on ordinary activities before taxation",
    "tax on profit": "Tax on profit on ordinary activities",
    "tax on loss": "Tax on profit on ordinary activities",
    "cost of raw material and consumables": "Distribution Costs",
    "cost of materials": "Distribution Costs",
    "staff costs": "Administrative Expenses",
    "tax": "Tax on profit on ordinary activities",
    "taxation": "Tax on profit on ordinary activities",
    "profit": "Profit for the financial year",
    "profit for the period": "Profit for the financial year",
    "loss for the period": "Profit for the financial year",
    "profit after tax": "Profit for the financial year",
    "profit for the financial year and total comprehensive income": "Profit for the financial year",
    "loss for the financial year and total comprehensive income": "Profit for the financial year",
    "loss for the financial year": "Profit for the financial year",
    "loss for the financial year after": "Profit for the financial year",
    "other charges": "Interest payable and similar charges",
    "profit or (loss) for period": "Profit for the financial year",
    "operating loss": "Operating Profit",
    "gross profit or (loss)": "Gross Profit",
    "operating profit or (loss)": "Operating Profit",
    "profit or (loss) before tax": "Profit on ordinary activities before taxation",
    "gross profit/(loss)": "Gross Profit",
    "profit/(loss)": "Profit for the financial year",
    "less cost of sales": "Cost of sales",
    "interest payable": "Interest payable and similar charges",
    "gross surplus or (deficit)": "Gross Profit",
    "surplus or (deficit) before tax": "Profit on ordinary activities before taxation",
    "tax on surplus": "Tax on profit on ordinary activities",
    "surplus or (deficit) for the period": "Profit for the financial year",
    "operating profit and profit for the financial year before members' remuneration and profit shares available for discretionary division among members ": "Profit for the financial year",
    "profit for the financial period before members' remuneration and profit shares available for discretionary division among members ": "Profit for the financial year",
    "profit after taxation being profit for the financial year": "Profit for the financial year"
}

# function to check for table headings
# table headings takes json file with example headings to compare


def detect_heading(lines, file):
    with open(file) as f:
        data = json.load(f)
    heading_list = data.keys()
    flag = False
    for line in lines:
        for word in line.words:
            for heading in heading_list:
                if word.value.lower() == heading.lower():
                    flag = True
                    break

    return flag


def filter_and_mark(lines, page_box, page_width, margin=20, cutoff=0.6):

    # get lines with multiple unmerged words
    # these have high chance of forming tables
    for line in lines:
        if line.type == -1 and len(line.words) > 1:
            line.type = LineType.TABLE

    # get centre text
    for line in lines:
        if line.type == -1 and centre_aligned(line, page_box):
            line.type = LineType.CENTRE

    # filter large lines that are likely to be part of paragraphs
    for line in lines:
        if line.type == -1 and (line.box.x2 - line.box.x1)/page_width > cutoff:
            line.type = LineType.PARA

    # get small lines adjacent to table lines even if they have one word
    # these can be empty entries in the table or headings of entries
    # add rest of small lines to paragraph lines
    for i, line in enumerate(lines):
        to_add = False

        # first check lower line and assign same type
        if i < len(lines) - 1 and \
            lines[i+1].box.x2 + margin > line.box.x1 and \
                line.type != -1 and lines[i+1].type != -1:
            line.type = lines[i+1].type

        # next check upper line and assign same type
        if i > 0 and lines[i-1].box.x1 - margin > line.box.x2 and \
                line.type != -1 and lines[i-1].type != -1:
            line.type = lines[i-1].type

        # if line is still not assigned a type make it a paragraph line
        if line.type == -1:
            line.type = LineType.TABLE


def process_csv(input_path, output_path, parse_mode):

    xml_file = tree.parse(input_path).getroot()
    for page in xml_file.getchildren():
        page_box = Rectangle(list(map(float, page.attrib["bbox"].split(","))))
        page_mid = (page_box.x1 + page_box.x2)/2
        page_width = page_box.x2 - page_box.x1
        lines = get_lines(page, parse_mode["line_margin"])
        lines = merge_words(lines, parse_mode["merge_margin"])
        lines.sort(reverse=True)

        # filter and mark names with appropriate types
        filter_and_mark(lines, page_box, page_width,
                        parse_mode["adj_margin"], parse_mode["large_cutoff"])

        # correct spellings and discard empty lines
        lines = check_fix_spellings(lines, (LineType.PARA, LineType.TABLE))

        # check if page contains table for profit and loss by checking header
        if spell_fixer.p_l_filter(lines):

            # get all tables lines
            table_lines = []
            for line in lines:
                if line.type == LineType.TABLE:
                    table_lines.append(line)

            # write to csv
            columns = get_columns(table_lines, parse_mode["column_margin"])
            columns.sort()
            for i, column in enumerate(columns):
                for word in column.words:
                    word.col_num = i
            max_col = len(columns)

            # make lower
            for line in table_lines:
                for word in line:
                    word.value = word.value.lower()

            # perform triaging using json file
            for line in table_lines:
                for word in line:
                    for key in triage_data.keys():
                        if word.value in key.lower():
                            word.value = triage_data[key]
                            break

            with open(output_path, "w") as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=',',
                                       quotechar='"', quoting=csv.QUOTE_ALL)
                for line in table_lines:
                    line.words.sort()
                    csv_line = [None]*(max_col)
                    for word in line.words:
                        csv_line[word.col_num] = word.value
                    csvwriter.writerow(csv_line)
