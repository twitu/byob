import xml.etree.ElementTree as tree
from docx import Document
import csv

class Rectangle:

    def __init__(self, values):
        self.x1 = values[0]
        self.y1 = values[1]
        self.x2 = values[2]
        self.y2 = values[3]

    # sort in vertically
    def __gt__(self, value):
        return self.y1 > value.y1

    # merge two rectangles to get largest possible rectangles
    def merge(self, value):
        self.x1 = min(self.x1, value.x1)
        self.y1 = min(self.y1, value.y1)
        self.x2 = max(self.x2, value.x2)
        self.y2 = max(self.y2, value.y2)

    def __str__(self):
        return " ".join(map(str, [x1, y1, x2, y2]))


class Word:

    def __init__(self, value, box):
        self.value = value
        self.box = box
        self.row_num = 0
        self.col_num = 0

    def __str__(self):
        return self.value

    # sort from left to right
    def __gt__(self, value):
        return self.box.x1 > self.box.x2

    # concatenate text and merge box
    def merge(self, other):
        self.value += " " + other.value
        self.box.merge(other.box)


class Line:

    def __init__(self, word):
        self.box = word.box
        self.words = [word]
        self.row_num = 0

    # add words to list and change bounding box accordingly
    def add_word(self, word):
        self.words.append(word)
        if word.box.y1 < self.box.y1:
            self.box.y1 = word.box.y1
        if self.box.y2 < word.box.y2:
            self.box.y2 = word.box.y2

    # get word from list of words
    def __getitem__(self, item):
        return self.words[item]

    # iterate over list of words
    def __iter__(self):
        return self.words.__iter__()

    # sort lines vertically
    def __gt__(self, value):
        return self.box.y1 > value.box.y1

    # debugging convenience will affect performance
    def __str__(self):
        return " ".join([word.__str__() for word in self.words])


class Column:

    def __init__(self, word):
        self.words = [word]
        self.box = word.box
        self.col_num = 0

    # add word to column and modify bounding box
    def add_word(self, word):
        self.words.append(word)
        if word.box.x1 < self.box.x1:
            self.box.x1 = word.box.x1
        if self.box.x2 < word.box.x2:
            self.box.x2 = word.box.x2

    # get item from list of words
    def __getitem__(self, item):
        return self.words[item]

    # iterate over words in a column
    def __iter__(self):
        return self.words.__iter__()

    # sort columns from left to right
    def __gt__(self, value):
        return self.box.x1 > value.box.x1

    # debugging convenience will affect performance
    def __str__(self):
        return "\n".join([word.__str__() for word in self.words])

class Paragraph:

    def __init__(self, line):
        self.lines = [line]
        self.box = line.box

    # add lines to paragraph and modify bounding box
    def add_line(self, line):
        self.lines.append(line)
        self.box.merge(line.box)

    # get line from list of lines
    def __getitem__(self, item):
        return self.lines[item]

    # iterate over lines in paragraph
    def __iter__(self):
        return self.lines.__iter__()

    # sort vertically
    def __gt__(self, value):
        return self.box.y1 > value.box.x1

# group words that are horizontally in the same line
def get_lines(page_element, margin=5):
    lines = []
    page_box = Rectangle(list(map(float, page_element.attrib["bbox"].split(","))))
    for text_box in page_element.getchildren():
        if not text_box.tag == "textbox": continue
        for text_line in text_box.getchildren():
            if not text_line.tag == "textline": continue
            bbox = Rectangle(list(map(float, text_line.attrib["bbox"].split(","))))
            value = ''.join([text_char.text if text_char.text else " " for text_char in text_line.getchildren()])
            value = value.strip()
            # TODO: filter and correct text value
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


# check if box passes centre line and check if it is greater than certain percentage of page width
def filter_centre_word(page_box, word):
    centre = page_box.x2/2
    width = 0.15
    if (word.box.x1 < centre < word.box.x2) and \
        (word.box.x2 - word.box.x1)/(page_box.x2 - page_box.x1) > width:
        return True
    else:
        return False


# take lines of words and create columns from them
def get_columns(lines, margin=10):
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
    for line in lines:
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


def get_paragraphs(lines, margin=5):
    paras = []
    for line in lines:
        added = False
        for para in paras:
            if para.box.y1 - margin < line.box.y2 and line.box.y1 < para.box.y1 or \
                para.box.y2 + margin > line.box.y1 and line.box.y2 > para.box.y2:
                para.add_line(line)
                added = True

        if not added:
            paras.append(Paragraph(line))
        
    return paras


def write_to_doc(paras):

    document = Document()

    for para in paras:
        value = " ".join([" ".join([word.value for word in line]) for line in para])
        print(value)
        print()
        document.add_paragraph(value)
        
    document.save("demo.docx")

def write_to_csv(lines):

    columns = get_columns(lines)
    columns.sort()
    for i, column in enumerate(columns):
        for word in column.words:
            word.col_num = i

    with open("table.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for line in lines:
            line.words.sort()
            max_col = line.words[-1].col_num
            csv_line = [None]*(max_col + 1)
            for word in line.words:
                csv_line[word.col_num] = word.value
            print(csv_line)
            csvwriter.writerow(csv_line)


def centre_aligned(line, page_box, margin=15, cutoff=0.6):
    mid = (page_box.x1 + page_box.x2)/2
    width = page_box.x2 - page_box.x1

    if line.box.x1 < mid < line.box.x2:
        left = mid - line.box.x1
        right = line.box.x2 - mid
        if (-margin < left - right < margin) and ((line.box.x2 - line.box.x1)/width < cutoff):
            return True

    return False

    
if __name__ == "__main__":
    file_name = "para.xml"
    xml_file = tree.parse(file_name).getroot()
    page = xml_file.getchildren()[0]
    page_box = Rectangle(list(map(float, page.attrib["bbox"].split(","))))
    page_mid = (page_box.x1 + page_box.x2)/2
    page_width = page_box.x2 - page_box.x1
    lines = get_lines(page)
    lines = merge_words(lines)
    lines.sort(reverse=True)

    filter_lines = []
    centre_text = []
    table_lines = []
    paragraph_lines = []

    for line in lines:
        print(line)
    print()

    # get centre text
    for line in lines:
        if centre_aligned(line, page_box):
            centre_text.append(line)
        else:
            filter_lines.append(line)
    lines = filter_lines

    # get lines with multiple unmerged words
    # these have high chance of forming tables
    filter_lines = []
    for line in lines:
        if len(line.words) > 1:
            table_lines.append(line)
        else:
            filter_lines.append(line)
    lines = filter_lines

    # filter large lines that are likely to be part of paragraphs
    filter_lines = []
    for line in lines:
        if (line.box.x2 - line.box.x1)/page_width > 0.6:
            paragraph_lines.append(line)
        else:
            filter_lines.append(line)
    lines = filter_lines

    for line in lines:
        print(line)
    print()

    # get small lines adjacent to table lines even if they have one word
    # these can be empty entries in the table or headings of entries
    # add rest of small lines to paragraph lines
    for line in lines:
        to_add = False
        margin = 15
        for table_line in table_lines:
            if table_line.box.y1 - margin < line.box.y2 and line.box.y1 < table_line.box.y1 or \
                table_line.box.y2 + margin > line.box.y1 and line.box.y2 > table_line.box.y2:
                to_add = True

        if to_add:
            table_lines.append(line)
        else:
            paragraph_lines.append(line)

    # get paragraphs
    paragraphs = get_paragraphs(paragraph_lines, 10)

    # sort all types of lines
    paragraphs.sort(reverse=True)
    table_lines.sort(reverse=True)
    centre_text.sort(reverse=True)

    for line in table_lines:
        print(line)
    print()

    for paragraph in paragraphs:
        # first line should be bold if its width is less than paragraph width
        line = paragraph.lines[0]
        if (line.box.x2-line.box.x1)/(paragraph.box.x2-paragraph.box.x1) < 0.6:
            print(line)

        for line in paragraph.lines[1:]:
            print(line.__str__(), sep=" ")
        print()

    # lines.sort(reverse=True)
    # paras = get_paragraphs(lines)
    # write_to_doc(paras)
