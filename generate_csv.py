import xml.etree.ElementTree as tree
from docx import Document
import csv
import json
from enum import Enum
from itertools import groupby
import spell_fixer
import sys
from text_objects import Rectangle, Word, Line, LineType, Column


# group words that are horizontally in the same line
def get_lines(page_element, margin=5):
    lines = []
    page_box = Rectangle(
        list(map(float, page_element.attrib["bbox"].split(","))))
    for text_box in page_element.getchildren():
        if not text_box.tag == "textbox":
            continue
        for text_line in text_box.getchildren():
            if not text_line.tag == "textline":
                continue
            bbox = Rectangle(
                list(map(float, text_line.attrib["bbox"].split(","))))
            value = ''.join(
                [text_char.text if text_char.text else " " for text_char in text_line.getchildren()])
            value = value.strip()
            if not spell_fixer.spelling_accept(value):
                continue
            value = spell_fixer.spelling_fixer(value)
            word = Word(value, bbox)
            added = False
            for line in lines:
                # check within a margin of error if the text_line can be added in an exisiting line
                if (line.box.y1 - margin < bbox.y1 < line.box.y1 + margin) and (line.box.y2 - margin < bbox.y2 < line.box.y2 + margin):
                    line.add_word(word)
                    added = True

            if not added:
                lines.append(Line(word))

    return lines


# take lines of words and create columns from them
def get_columns(lines, margin=20):
    columns = []
    for line in lines:
        for word in line:
            added = False
            for column in columns:
                if column.box.x1 - margin < word.box.x1 < column.box.x1 + margin \
                        or column.box.x2 - margin < word.box.x2 < column.box.x2 + margin \
                        or column.box.x1 + margin < word.box.x1 and word.box.x2 < column.box.x2:
                    column.words.append(word)
                    added = True
            if not added:
                columns.append(Column(word))
    return columns


# merge closely spaced words
def merge_words(lines, margin=15):
    new_lines = []
    for i, line in enumerate(lines):
        line.words.sort()
        merger = line.words[0]
        new_line = Line(merger)
        for i, word in enumerate(line.words[1:]):
            if merger.box.x2 + margin > word.box.x1:
                merger.merge(word)
            else:
                new_line.add_word(merger)
                merger = word
        # avoid adding starting word again
        # happens when line has only one word
        if merger != new_line.words[0]:
            new_line.add_word(merger)
        new_lines.append(new_line)
    return new_lines


def centre_aligned(line, page_box, margin=15, cutoff=0.8):
    mid = (page_box.x1 + page_box.x2)/2
    width = page_box.x2 - page_box.x1

    if line.box.x1 < mid < line.box.x2:
        left = mid - line.box.x1
        right = line.box.x2 - mid
        if (-margin < left - right < margin) and ((line.box.x2 - line.box.x1)/width < cutoff):
            return True

    return False


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


def filter_and_mark(lines, page_box):

    # get lines with multiple unmerged words
    # these have high chance of forming tables
    for line in lines:
        if line.type == -1 and len(line.words) > 1:
            line.type = LineType.TABLE

    # set headers
    spell_fixer.set_headers(lines)

    # set footers
    spell_fixer.set_footers(lines)

    # get centre text
    for line in lines:
        if line.type == -1 and centre_aligned(line, page_box):
            line.type = LineType.CENTRE

    # filter large lines that are likely to be part of paragraphs
    for line in lines:
        if line.type == -1 and (line.box.x2 - line.box.x1)/page_width > 0.6:
            line.type = LineType.PARA

    # get small lines adjacent to table lines even if they have one word
    # these can be empty entries in the table or headings of entries
    # add rest of small lines to paragraph lines
    for i, line in enumerate(lines):
        to_add = False
        margin = 15

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


if __name__ == "__main__":
    file_name = "00683982_ocr_10.xml"

    xml_file = tree.parse(file_name).getroot()
    for page in xml_file.getchildren():
        page_box = Rectangle(list(map(float, page.attrib["bbox"].split(","))))
        page_mid = (page_box.x1 + page_box.x2)/2
        page_width = page_box.x2 - page_box.x1
        lines = get_lines(page)
        lines = merge_words(lines)
        lines.sort(reverse=True)

        # filter and mark names with appropriate types
        filter_and_mark(lines, page_box)

        # check if page contains table for profit and loss by checking header
        if spell_fixer.p_l_filter(lines):

            # get all tables lines
            table_lines = filter(lambda x: x.type == LineType.TABLE, lines)

            # write to csv
            columns = get_columns(table_lines)
            columns.sort()
            for i, column in enumerate(columns):
                for word in column.words:
                    word.col_num = i
            max_col = len(columns)

            with open("table.csv", "w") as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='"', quoting=csv.QUOTE_ALL)
                for line in table_lines:
                    line.words.sort()
                    csv_line = [None]*(max_col)
                    for word in line.words:
                        csv_line[word.col_num] = word.value
                    print(csv_line)
                    csvwriter.writerow(csv_line)
